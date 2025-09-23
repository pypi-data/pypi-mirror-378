"""
Snowflake data dictionary for DataGuild metadata extraction.

This module provides comprehensive data structures and extraction logic for
Snowflake metadata including databases, schemas, tables, views, columns,
tags, procedures, and other governance information with optimized parallel processing.
"""

import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, MutableMapping, Optional, Tuple

from dataguild.configuration.common import AllowDenyPattern
from dataguild.api.common import PipelineContext
from dataguild.source.snowflake.constants import SnowflakeObjectDomain
from dataguild.source.sql.sql_generic import BaseTable, BaseView
from dataguild.source.snowflake.connection import SnowflakeConnection
from dataguild.source.snowflake.query import (
    SHOW_COMMAND_MAX_PAGE_SIZE,
    SnowflakeQuery,
)
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.utilities.file_backed_collections import FileBackedDict
from dataguild.utilities.prefix_batch_builder import PrefixGroup, build_prefix_batches
from dataguild.utilities.serialized_lru_cache import serialized_lru_cache

logger: logging.Logger = logging.getLogger(__name__)

# =============================================
# Parallelism Configuration
# =============================================

# Controls parallel processing of schema operations
SCHEMA_PARALLELISM = int(os.getenv("DATAGUILD_SNOWFLAKE_SCHEMA_PARALLELISM", 20))


def get_schema_parallelism() -> int:
    """
    Get the current schema parallelism setting.

    Returns:
        Number of parallel workers for schema processing
    """
    return SCHEMA_PARALLELISM


def set_schema_parallelism(parallelism: int) -> None:
    """
    Set the schema parallelism level.

    Args:
        parallelism: Number of parallel workers (1-100)

    Raises:
        ValueError: If parallelism is not between 1 and 100
    """
    global SCHEMA_PARALLELISM
    if not (1 <= parallelism <= 100):
        raise ValueError("Schema parallelism must be between 1 and 100")
    SCHEMA_PARALLELISM = parallelism
    logger.info(f"Schema parallelism set to {SCHEMA_PARALLELISM}")


def get_optimal_parallelism(schema_count: int) -> int:
    """
    Calculate optimal parallelism based on schema count.

    Args:
        schema_count: Number of schemas to process

    Returns:
        Optimal parallelism level
    """
    if schema_count <= 5:
        return min(schema_count, 5)
    elif schema_count <= 50:
        return min(schema_count // 2, SCHEMA_PARALLELISM)
    else:
        return SCHEMA_PARALLELISM


# =============================================
# Change Type Classification
# =============================================

class ChangeTypeClass:
    """
    Change Type Enumeration for DataGuild metadata change tracking.

    Provides standardized change type constants for tracking metadata
    modifications across Snowflake objects and schema evolution.
    """

    # Core change types
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    UPSERT = "UPSERT"
    DELETE = "DELETE"

    # Extended change types for comprehensive tracking
    ADDITION = "ADDITION"
    REMOVAL = "REMOVAL"
    MODIFICATION = "MODIFICATION"
    MOVED = "MOVED"
    ALTERED = "ALTERED"
    SCHEMA_CHANGE = "SCHEMA_CHANGE"
    DATA_TYPE_CHANGE = "DATA_TYPE_CHANGE"
    CONSTRAINT_CHANGE = "CONSTRAINT_CHANGE"
    TAG_CHANGE = "TAG_CHANGE"
    PROCEDURE_CHANGE = "PROCEDURE_CHANGE"
    VIEW_DEFINITION_CHANGE = "VIEW_DEFINITION_CHANGE"
    PERMISSION_CHANGE = "PERMISSION_CHANGE"

    # All allowed change types
    allowed_types = {
        CREATE, UPDATE, UPSERT, DELETE, ADDITION, REMOVAL,
        MODIFICATION, MOVED, ALTERED, SCHEMA_CHANGE, DATA_TYPE_CHANGE,
        CONSTRAINT_CHANGE, TAG_CHANGE, PROCEDURE_CHANGE,
        VIEW_DEFINITION_CHANGE, PERMISSION_CHANGE
    }

    def __init__(self, change_type: str):
        """
        Initialize change type.

        Args:
            change_type: Change type string

        Raises:
            ValueError: If change_type is not valid
        """
        if change_type not in self.allowed_types:
            raise ValueError(f"Invalid change_type: {change_type}. Allowed types: {self.allowed_types}")
        self.change_type = change_type

    def __str__(self) -> str:
        """String representation of the change type."""
        return self.change_type

    def __eq__(self, other) -> bool:
        """Check equality with another ChangeTypeClass instance."""
        return isinstance(other, ChangeTypeClass) and self.change_type == other.change_type

    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.change_type)

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ChangeTypeClass({self.change_type})"

    @classmethod
    def all_types(cls) -> List[str]:
        """Get all allowed change types."""
        return sorted(list(cls.allowed_types))

    @classmethod
    def core_types(cls) -> List[str]:
        """Get core change types."""
        return [cls.CREATE, cls.UPDATE, cls.UPSERT, cls.DELETE]

    @classmethod
    def extended_types(cls) -> List[str]:
        """Get extended change types."""
        return [
            cls.ADDITION, cls.REMOVAL, cls.MODIFICATION, cls.MOVED, cls.ALTERED,
            cls.SCHEMA_CHANGE, cls.DATA_TYPE_CHANGE, cls.CONSTRAINT_CHANGE,
            cls.TAG_CHANGE, cls.PROCEDURE_CHANGE, cls.VIEW_DEFINITION_CHANGE,
            cls.PERMISSION_CHANGE
        ]

    def is_destructive(self) -> bool:
        """Check if this change type is potentially destructive."""
        destructive_types = {
            self.DELETE, self.REMOVAL, self.ALTERED,
            self.DATA_TYPE_CHANGE, self.CONSTRAINT_CHANGE
        }
        return self.change_type in destructive_types

    def is_additive(self) -> bool:
        """Check if this change type is purely additive."""
        additive_types = {
            self.CREATE, self.ADDITION, self.TAG_CHANGE, self.UPSERT
        }
        return self.change_type in additive_types

    def get_severity(self) -> str:
        """Get the severity level of this change type."""
        if self.change_type in {self.DELETE, self.REMOVAL, self.DATA_TYPE_CHANGE}:
            return "HIGH"
        elif self.change_type in {self.ALTERED, self.CONSTRAINT_CHANGE, self.PROCEDURE_CHANGE, self.MODIFICATION}:
            return "MEDIUM"
        elif self.change_type in {self.CREATE, self.ADDITION, self.TAG_CHANGE, self.UPDATE, self.UPSERT}:
            return "LOW"
        else:
            return "UNKNOWN"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.change_type,
            "severity": self.get_severity(),
            "is_destructive": self.is_destructive(),
            "is_additive": self.is_additive()
        }


# =============================================
# Core Data Structures
# =============================================

@dataclass
class SnowflakePK:
    """Represents a primary key constraint in Snowflake."""

    name: str
    column_names: List[str]


@dataclass
class SnowflakeFK:
    """Represents a foreign key constraint in Snowflake."""

    name: str
    column_names: List[str]
    referred_database: str
    referred_schema: str
    referred_table: str
    referred_column_names: List[str]


@dataclass
class SnowflakeTag:
    """Represents a Snowflake tag with comprehensive metadata."""

    database: str
    schema: str
    name: str
    value: str

    def tag_display_name(self) -> str:
        """Get human-readable tag display name."""
        return f"{self.name}: {self.value}"

    def tag_identifier(self) -> str:
        """Get unique tag identifier with value."""
        return f"{self._id_prefix_as_str()}:{self.value}"

    def _id_prefix_as_str(self) -> str:
        """Get tag prefix without value."""
        return f"{self.database}.{self.schema}.{self.name}"

    def structured_property_identifier(self) -> str:
        """Get structured property identifier for DataGuild."""
        return f"snowflake.{self.database}.{self.schema}.{self.name}"

    def to_urn(self) -> str:
        """Convert tag to DataGuild URN format."""
        return f"urn:li:tag:snowflake.{self.database}.{self.schema}.{self.name}"


@dataclass
class ProcedureParameter:
    """Represents a parameter in a Snowflake stored procedure."""

    name: str
    data_type: str
    mode: str = "IN"  # IN, OUT, INOUT
    default_value: Optional[str] = None
    description: Optional[str] = None
    ordinal_position: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameter to dictionary representation."""
        return {
            "name": self.name,
            "data_type": self.data_type,
            "mode": self.mode,
            "default_value": self.default_value,
            "description": self.description,
            "ordinal_position": self.ordinal_position,
        }


@dataclass
class BaseProcedure:
    """Represents a Snowflake stored procedure with comprehensive metadata."""

    name: str
    database: str
    schema: str
    language: str
    definition: Optional[str] = None
    parameters: List[ProcedureParameter] = field(default_factory=list)
    return_type: Optional[str] = None
    description: Optional[str] = None
    created: Optional[datetime] = None
    last_altered: Optional[datetime] = None
    owner: Optional[str] = None
    security_type: Optional[str] = None  # DEFINER, INVOKER
    comment: Optional[str] = None
    tags: List[SnowflakeTag] = field(default_factory=list)
    is_secure: bool = False
    external_access_integrations: Optional[str] = None
    secrets: Optional[str] = None
    imports: Optional[str] = None
    handler: Optional[str] = None
    runtime_version: Optional[str] = None
    packages: Optional[str] = None

    def get_full_name(self) -> str:
        """Get fully qualified procedure name."""
        return f"{self.database}.{self.schema}.{self.name}"

    def get_signature(self) -> str:
        """Get procedure signature with parameters."""
        param_strs = []
        for param in self.parameters:
            param_str = f"{param.mode} {param.name} {param.data_type}"
            if param.default_value:
                param_str += f" DEFAULT {param.default_value}"
            param_strs.append(param_str)

        signature = f"{self.name}({', '.join(param_strs)})"
        if self.return_type:
            signature += f" RETURNS {self.return_type}"

        return signature

    def get_subtype(self) -> str:
        """Get dataset subtype for procedure."""
        if self.is_secure:
            return "SECURE_PROCEDURE"
        elif self.language.upper() == "SQL":
            return "SQL_PROCEDURE"
        elif self.language.upper() == "JAVASCRIPT":
            return "JAVASCRIPT_PROCEDURE"
        elif self.language.upper() == "PYTHON":
            return "PYTHON_PROCEDURE"
        elif self.language.upper() == "JAVA":
            return "JAVA_PROCEDURE"
        elif self.language.upper() == "SCALA":
            return "SCALA_PROCEDURE"
        else:
            return "PROCEDURE"

    def to_dict(self) -> Dict[str, Any]:
        """Convert procedure to dictionary representation."""
        return {
            "name": self.name,
            "database": self.database,
            "schema": self.schema,
            "full_name": self.get_full_name(),
            "signature": self.get_signature(),
            "subtype": self.get_subtype(),
            "language": self.language,
            "return_type": self.return_type,
            "description": self.description,
            "created": self.created.isoformat() if self.created else None,
            "last_altered": self.last_altered.isoformat() if self.last_altered else None,
            "owner": self.owner,
            "security_type": self.security_type,
            "comment": self.comment,
            "is_secure": self.is_secure,
            "parameter_count": len(self.parameters),
            "parameters": [param.to_dict() for param in self.parameters],
            "tags": [tag.tag_identifier() for tag in self.tags],
            "external_access_integrations": self.external_access_integrations,
            "secrets": self.secrets,
            "imports": self.imports,
            "handler": self.handler,
            "runtime_version": self.runtime_version,
            "packages": self.packages,
        }


@dataclass
class SnowflakeColumn:
    """Represents a Snowflake column with comprehensive metadata."""

    name: str
    data_type: str
    ordinal_position: Optional[int] = None
    is_nullable: bool = True
    comment: Optional[str] = None
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    column_default: Optional[str] = None
    is_identity: bool = False
    tags: List[SnowflakeTag] = field(default_factory=list)
    # Enhanced metadata fields
    type_details: Optional[str] = None
    classification: Optional[str] = None

    def get_precise_native_type(self) -> str:
        """Get precise native data type with precision/scale information."""
        precise_native_type = self.data_type

        # Handle numeric types with precision/scale
        if (
            self.data_type in ("NUMBER", "NUMERIC", "DECIMAL")
            and self.numeric_precision is not None
            and self.numeric_scale is not None
        ):
            precise_native_type = f"NUMBER({self.numeric_precision},{self.numeric_scale})"

        # Handle string types with length
        elif (
            self.data_type in ("TEXT", "STRING", "VARCHAR")
            and self.character_maximum_length is not None
        ):
            precise_native_type = f"VARCHAR({self.character_maximum_length})"

        return precise_native_type
    
    def get_enhanced_type_info(self) -> Dict[str, Any]:
        """Get enhanced type information including classification and details."""
        return {
            "base_type": self.data_type,
            "precise_type": self.get_precise_native_type(),
            "type_details": self.type_details,
            "classification": self.classification,
            "is_identity": self.is_identity,
            "is_nullable": self.is_nullable,
            "has_default": self.column_default is not None,
            "precision": self.numeric_precision,
            "scale": self.numeric_scale,
            "max_length": self.character_maximum_length,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert column to dictionary representation."""
        return {
            "name": self.name,
            "data_type": self.data_type,
            "precise_native_type": self.get_precise_native_type(),
            "ordinal_position": self.ordinal_position,
            "is_nullable": self.is_nullable,
            "comment": self.comment,
            "character_maximum_length": self.character_maximum_length,
            "numeric_precision": self.numeric_precision,
            "numeric_scale": self.numeric_scale,
            "column_default": self.column_default,
            "is_identity": self.is_identity,
            "tags": [tag.tag_identifier() for tag in self.tags],
        }


class SnowflakeTable(BaseTable):
    """Represents a Snowflake table with comprehensive metadata."""

    type: Optional[str] = None
    size_in_bytes: Optional[int] = None
    rows_count: Optional[int] = None
    comment: Optional[str] = None
    clustering_key: Optional[str] = None
    pk: Optional[SnowflakePK] = None
    columns: List[SnowflakeColumn] = field(default_factory=list)
    foreign_keys: List[SnowflakeFK] = field(default_factory=list)
    tags: List[SnowflakeTag] = field(default_factory=list)
    column_tags: Dict[str, List[SnowflakeTag]] = field(default_factory=dict)
    is_dynamic: bool = False
    is_iceberg: bool = False
    is_hybrid: bool = False

    def get_full_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.database}.{self.schema}.{self.name}"

    def get_subtype(self) -> str:
        """Get dataset subtype."""
        if self.is_dynamic:
            return "DYNAMIC_TABLE"
        elif self.is_iceberg:
            return "ICEBERG_TABLE"
        elif self.type == "EXTERNAL TABLE":
            return "EXTERNAL_TABLE"
        else:
            return "TABLE"

    def to_dict(self) -> Dict[str, Any]:
        """Convert table to dictionary representation."""
        return {
            "name": self.name,
            "database": self.database,
            "schema": self.schema,
            "full_name": self.get_full_name(),
            "type": self.type,
            "subtype": self.get_subtype(),
            "created": self.created.isoformat() if self.created else None,
            "last_altered": self.last_altered.isoformat() if self.last_altered else None,
            "size_in_bytes": self.size_in_bytes,
            "rows_count": self.rows_count,
            "comment": self.comment,
            "clustering_key": self.clustering_key,
            "is_dynamic": self.is_dynamic,
            "is_iceberg": self.is_iceberg,
            "is_hybrid": self.is_hybrid,
            "column_count": len(self.columns),
            "tags": [tag.tag_identifier() for tag in self.tags],
        }


class SnowflakeDynamicTable(SnowflakeTable):
    """Represents a Snowflake dynamic table with additional metadata."""

    definition: Optional[str] = None
    target_lag: Optional[str] = None

    def get_subtype(self) -> str:
        """Get dataset subtype for dynamic table."""
        return "DYNAMIC_TABLE"

    def to_dict(self) -> Dict[str, Any]:
        """Convert dynamic table to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "definition": self.definition,
            "target_lag": self.target_lag,
        })
        return base_dict


@dataclass
class SnowflakeView(BaseView):
    """Represents a Snowflake view with comprehensive metadata."""

    view_definition: Optional[str] = None
    materialized: bool = False
    is_secure: bool = False
    columns: List[SnowflakeColumn] = field(default_factory=list)
    tags: List[SnowflakeTag] = field(default_factory=list)
    column_tags: Dict[str, List[SnowflakeTag]] = field(default_factory=dict)

    def get_full_name(self) -> str:
        """Get fully qualified view name."""
        return f"{self.database}.{self.schema}.{self.name}"

    def get_subtype(self) -> str:
        """Get dataset subtype."""
        if self.materialized:
            return "MATERIALIZED_VIEW"
        elif self.is_secure:
            return "SECURE_VIEW"
        else:
            return "VIEW"

    def to_dict(self) -> Dict[str, Any]:
        """Convert view to dictionary representation."""
        return {
            "name": self.name,
            "database": self.database,
            "schema": self.schema,
            "full_name": self.get_full_name(),
            "subtype": self.get_subtype(),
            "created": self.created.isoformat() if self.created else None,
            "last_altered": self.last_altered.isoformat() if self.last_altered else None,
            "comment": self.comment,
            "view_definition": self.view_definition,
            "materialized": self.materialized,
            "is_secure": self.is_secure,
            "column_count": len(self.columns),
            "tags": [tag.tag_identifier() for tag in self.tags],
        }


@dataclass
class SnowflakeSchema:
    """Represents a Snowflake schema with comprehensive metadata."""

    name: str
    database: str
    created: Optional[datetime] = None
    last_altered: Optional[datetime] = None
    comment: Optional[str] = None
    tables: List[str] = field(default_factory=list)
    views: List[str] = field(default_factory=list)
    streams: List[str] = field(default_factory=list)
    procedures: List[str] = field(default_factory=list)
    tags: List[SnowflakeTag] = field(default_factory=list)

    def get_full_name(self) -> str:
        """Get fully qualified schema name."""
        return f"{self.database}.{self.name}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary representation."""
        return {
            "name": self.name,
            "database": self.database,
            "full_name": self.get_full_name(),
            "created": self.created.isoformat() if self.created else None,
            "last_altered": self.last_altered.isoformat() if self.last_altered else None,
            "comment": self.comment,
            "table_count": len(self.tables),
            "view_count": len(self.views),
            "stream_count": len(self.streams),
            "procedure_count": len(self.procedures),
            "tags": [tag.tag_identifier() for tag in self.tags],
        }


@dataclass
class SnowflakeDatabase:
    """Represents a Snowflake database with comprehensive metadata."""

    name: str
    created: Optional[datetime] = None
    comment: Optional[str] = None
    last_altered: Optional[datetime] = None
    schemas: List[SnowflakeSchema] = field(default_factory=list)
    tags: List[SnowflakeTag] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert database to dictionary representation."""
        return {
            "name": self.name,
            "created": self.created.isoformat() if self.created else None,
            "last_altered": self.last_altered.isoformat() if self.last_altered else None,
            "comment": self.comment,
            "schema_count": len(self.schemas),
            "tags": [tag.tag_identifier() for tag in self.tags],
        }


@dataclass
class SnowflakeStream:
    """Represents a Snowflake stream with comprehensive metadata."""

    name: str
    database: str
    schema: str
    created: datetime
    owner: str
    source_type: str
    type: str
    stale: str
    mode: str
    invalid_reason: str
    owner_role_type: str
    table_name: str
    comment: Optional[str] = None
    columns: List[SnowflakeColumn] = field(default_factory=list)
    stale_after: Optional[datetime] = None
    base_tables: Optional[str] = None
    tags: List[SnowflakeTag] = field(default_factory=list)
    column_tags: Dict[str, List[SnowflakeTag]] = field(default_factory=dict)
    last_altered: Optional[datetime] = None

    def get_full_name(self) -> str:
        """Get fully qualified stream name."""
        return f"{self.database}.{self.schema}.{self.name}"

    def get_subtype(self) -> str:
        """Get dataset subtype for stream."""
        return "STREAM"

    def to_dict(self) -> Dict[str, Any]:
        """Convert stream to dictionary representation."""
        return {
            "name": self.name,
            "database": self.database,
            "schema": self.schema,
            "full_name": self.get_full_name(),
            "subtype": self.get_subtype(),
            "created": self.created.isoformat() if self.created else None,
            "last_altered": self.last_altered.isoformat() if self.last_altered else None,
            "owner": self.owner,
            "source_type": self.source_type,
            "type": self.type,
            "stale": self.stale,
            "mode": self.mode,
            "table_name": self.table_name,
            "comment": self.comment,
            "tags": [tag.tag_identifier() for tag in self.tags],
        }


@dataclass
class SnowflakeProcedure:
    """Represents a Snowflake procedure with comprehensive metadata."""

    name: str
    database: str
    schema: str
    created: datetime
    owner: str
    comment: Optional[str] = None
    is_secure: bool = False
    tags: List[SnowflakeTag] = field(default_factory=list)
    last_altered: Optional[datetime] = None

    def get_full_name(self) -> str:
        """Get fully qualified procedure name."""
        return f"{self.database}.{self.schema}.{self.name}"

    def get_subtype(self) -> str:
        """Get dataset subtype for procedure."""
        return "PROCEDURE"

    def to_dict(self) -> Dict[str, Any]:
        """Convert procedure to dictionary representation."""
        return {
            "name": self.name,
            "database": self.database,
            "schema": self.schema,
            "full_name": self.get_full_name(),
            "subtype": self.get_subtype(),
            "created": self.created.isoformat() if self.created else None,
            "last_altered": self.last_altered.isoformat() if self.last_altered else None,
            "owner": self.owner,
            "comment": self.comment,
            "is_secure": self.is_secure,
            "tags": [tag.tag_identifier() for tag in self.tags],
        }


# =============================================
# Enhanced Tag Cache System
# =============================================

class _SnowflakeTagCache:
    """Cache for managing Snowflake tags across different object types including procedures."""

    def __init__(self) -> None:
        # Database tags: database_name -> [tags]
        self._database_tags: Dict[str, List[SnowflakeTag]] = defaultdict(list)

        # Schema tags: database_name -> schema_name -> [tags]
        self._schema_tags: Dict[str, Dict[str, List[SnowflakeTag]]] = defaultdict(
            lambda: defaultdict(list)
        )

        # Table tags: database_name -> schema_name -> table_name -> [tags]
        self._table_tags: Dict[str, Dict[str, Dict[str, List[SnowflakeTag]]]] = (
            defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        )

        # Column tags: database_name -> schema_name -> table_name -> column_name -> [tags]
        self._column_tags: Dict[
            str, Dict[str, Dict[str, Dict[str, List[SnowflakeTag]]]]
        ] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        )

        # Procedure tags: database_name -> schema_name -> procedure_name -> [tags]
        self._procedure_tags: Dict[str, Dict[str, Dict[str, List[SnowflakeTag]]]] = (
            defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        )

        # View tags: database_name -> schema_name -> view_name -> [tags]
        self._view_tags: Dict[str, Dict[str, Dict[str, List[SnowflakeTag]]]] = (
            defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        )

        # Stream tags: database_name -> schema_name -> stream_name -> [tags]
        self._stream_tags: Dict[str, Dict[str, Dict[str, List[SnowflakeTag]]]] = (
            defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        )

    # Database tag methods
    def add_database_tag(self, db_name: str, tag: SnowflakeTag) -> None:
        """Add tag to database."""
        self._database_tags[db_name].append(tag)

    def get_database_tags(self, db_name: str) -> List[SnowflakeTag]:
        """Get tags for database."""
        return self._database_tags[db_name]

    # Schema tag methods
    def add_schema_tag(self, schema_name: str, db_name: str, tag: SnowflakeTag) -> None:
        """Add tag to schema."""
        self._schema_tags[db_name][schema_name].append(tag)

    def get_schema_tags(self, schema_name: str, db_name: str) -> List[SnowflakeTag]:
        """Get tags for schema."""
        return self._schema_tags.get(db_name, {}).get(schema_name, [])

    # Table tag methods
    def add_table_tag(
        self, table_name: str, schema_name: str, db_name: str, tag: SnowflakeTag
    ) -> None:
        """Add tag to table."""
        self._table_tags[db_name][schema_name][table_name].append(tag)

    def get_table_tags(
        self, table_name: str, schema_name: str, db_name: str
    ) -> List[SnowflakeTag]:
        """Get tags for table."""
        return self._table_tags[db_name][schema_name][table_name]

    # Column tag methods
    def add_column_tag(
        self,
        column_name: str,
        table_name: str,
        schema_name: str,
        db_name: str,
        tag: SnowflakeTag,
    ) -> None:
        """Add tag to column."""
        self._column_tags[db_name][schema_name][table_name][column_name].append(tag)

    def get_column_tags_for_table(
        self, table_name: str, schema_name: str, db_name: str
    ) -> Dict[str, List[SnowflakeTag]]:
        """Get all column tags for a table."""
        return (
            self._column_tags.get(db_name, {}).get(schema_name, {}).get(table_name, {})
        )

    def get_column_tags(
        self, column_name: str, table_name: str, schema_name: str, db_name: str
    ) -> List[SnowflakeTag]:
        """Get tags for a specific column."""
        return self._column_tags[db_name][schema_name][table_name][column_name]

    # Procedure tag methods
    def add_procedure_tag(
        self, procedure_name: str, schema_name: str, db_name: str, tag: SnowflakeTag
    ) -> None:
        """
        Add tag to stored procedure.

        Args:
            procedure_name: Name of the stored procedure
            schema_name: Schema containing the procedure
            db_name: Database containing the schema
            tag: SnowflakeTag to add to the procedure
        """
        self._procedure_tags[db_name][schema_name][procedure_name].append(tag)

    def get_procedure_tags(
        self, procedure_name: str, schema_name: str, db_name: str
    ) -> List[SnowflakeTag]:
        """Get tags for a specific procedure."""
        return self._procedure_tags[db_name][schema_name][procedure_name]

    def get_all_procedure_tags_for_schema(
        self, schema_name: str, db_name: str
    ) -> Dict[str, List[SnowflakeTag]]:
        """Get all procedure tags for a schema."""
        return self._procedure_tags.get(db_name, {}).get(schema_name, {})

    # View tag methods
    def add_view_tag(
        self, view_name: str, schema_name: str, db_name: str, tag: SnowflakeTag
    ) -> None:
        """Add tag to view."""
        self._view_tags[db_name][schema_name][view_name].append(tag)

    def get_view_tags(
        self, view_name: str, schema_name: str, db_name: str
    ) -> List[SnowflakeTag]:
        """Get tags for view."""
        return self._view_tags[db_name][schema_name][view_name]

    # Stream tag methods
    def add_stream_tag(
        self, stream_name: str, schema_name: str, db_name: str, tag: SnowflakeTag
    ) -> None:
        """Add tag to stream."""
        self._stream_tags[db_name][schema_name][stream_name].append(tag)

    def get_stream_tags(
        self, stream_name: str, schema_name: str, db_name: str
    ) -> List[SnowflakeTag]:
        """Get tags for stream."""
        return self._stream_tags[db_name][schema_name][stream_name]

    def get_all_tags(self) -> List[SnowflakeTag]:
        """Get all tags from all categories."""
        all_tags = []
        
        # Add database tags
        for db_tags in self._database_tags.values():
            all_tags.extend(db_tags)
        
        # Add schema tags
        for schema_dict in self._schema_tags.values():
            for schema_tags in schema_dict.values():
                all_tags.extend(schema_tags)
        
        # Add table tags
        for table_dict in self._table_tags.values():
            for schema_dict in table_dict.values():
                for table_tags in schema_dict.values():
                    all_tags.extend(table_tags)
        
        # Add column tags
        for col_dict in self._column_tags.values():
            for schema_dict in col_dict.values():
                for table_dict in schema_dict.values():
                    for column_tags in table_dict.values():
                        all_tags.extend(column_tags)
        
        # Add procedure tags
        for proc_dict in self._procedure_tags.values():
            for schema_dict in proc_dict.values():
                for proc_tags in schema_dict.values():
                    all_tags.extend(proc_tags)
        
        # Add view tags
        for view_dict in self._view_tags.values():
            for schema_dict in view_dict.values():
                for view_tags in schema_dict.values():
                    all_tags.extend(view_tags)
        
        # Add stream tags
        for stream_dict in self._stream_tags.values():
            for schema_dict in stream_dict.values():
                for stream_tags in schema_dict.values():
                    all_tags.extend(stream_tags)
        
        return all_tags

    # Batch and utility methods
    def add_procedure_tags_batch(
        self, procedure_tags: List[Tuple[str, str, str, SnowflakeTag]]
    ) -> None:
        """Add multiple procedure tags in batch."""
        for procedure_name, schema_name, db_name, tag in procedure_tags:
            self.add_procedure_tag(procedure_name, schema_name, db_name, tag)

    def find_procedures_with_tag(
        self, tag_name: str, db_name: Optional[str] = None
    ) -> List[Tuple[str, str, str]]:
        """Find all procedures that have a specific tag."""
        results = []
        databases = [db_name] if db_name else self._procedure_tags.keys()

        for db in databases:
            for schema_name, procedures in self._procedure_tags[db].items():
                for procedure_name, tags in procedures.items():
                    if any(tag.name == tag_name for tag in tags):
                        results.append((db, schema_name, procedure_name))

        return results

    def clear_procedure_tags(
        self, procedure_name: str, schema_name: str, db_name: str
    ) -> None:
        """Clear all tags for a specific procedure."""
        if db_name in self._procedure_tags:
            if schema_name in self._procedure_tags[db_name]:
                if procedure_name in self._procedure_tags[db_name][schema_name]:
                    self._procedure_tags[db_name][schema_name][procedure_name] = []

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            "database_tags": sum(len(tags) for tags in self._database_tags.values()),
            "schema_tags": sum(
                sum(len(schema_tags) for schema_tags in db_schemas.values())
                for db_schemas in self._schema_tags.values()
            ),
            "table_tags": sum(
                sum(
                    sum(len(table_tags) for table_tags in schema_tables.values())
                    for schema_tables in db_schemas.values()
                )
                for db_schemas in self._table_tags.values()
            ),
            "column_tags": sum(
                sum(
                    sum(
                        sum(len(column_tags) for column_tags in table_columns.values())
                        for table_columns in schema_tables.values()
                    )
                    for schema_tables in db_schemas.values()
                )
                for db_schemas in self._column_tags.values()
            ),
            "procedure_tags": sum(
                sum(
                    sum(len(proc_tags) for proc_tags in schema_procs.values())
                    for schema_procs in db_schemas.values()
                )
                for db_schemas in self._procedure_tags.values()
            ),
            "view_tags": sum(
                sum(
                    sum(len(view_tags) for view_tags in schema_views.values())
                    for schema_views in db_schemas.values()
                )
                for db_schemas in self._view_tags.values()
            ),
            "stream_tags": sum(
                sum(
                    sum(len(stream_tags) for stream_tags in schema_streams.values())
                    for schema_streams in db_schemas.values()
                )
                for db_schemas in self._stream_tags.values()
            ),
        }

        stats["total_tags"] = sum(stats.values())
        return stats

    def __len__(self) -> int:
        """Get total number of tags in cache."""
        return self.get_statistics()["total_tags"]


# =============================================
# Main Data Dictionary Class
# =============================================

class SnowflakeDataDictionary:
    """
    Comprehensive data dictionary for Snowflake metadata extraction.

    This class provides methods to extract all types of metadata from Snowflake
    including databases, schemas, tables, views, columns, constraints, tags,
    procedures, and other governance information with optimized parallel processing.
    """

    def __init__(
        self,
        connection: SnowflakeConnection,
        report: SnowflakeV2Report,
        fetch_views_from_information_schema: bool = False,
    ) -> None:
        self.connection = connection
        self.report = report
        self._fetch_views_from_information_schema = fetch_views_from_information_schema
        self._tag_cache: Optional[_SnowflakeTagCache] = None

    def as_obj(self) -> Dict[str, Any]:
        """Get object representation for reporting."""
        lru_cache_functions: List[Callable] = [
            self.get_tables_for_database,
            self.get_views_for_database,
            self.get_columns_for_schema,
            self.get_streams_for_database,
            self.get_pk_constraints_for_schema,
            self.get_fk_constraints_for_schema,
            self.get_procedures_for_database,
        ]

        report: Dict[str, Any] = {
            "fetch_views_from_information_schema": self._fetch_views_from_information_schema,
            "schema_parallelism": SCHEMA_PARALLELISM,
        }

        for func in lru_cache_functions:
            if hasattr(func, 'cache_info'):
                report[func.__name__] = func.cache_info()._asdict()

        if self._tag_cache:
            report["tag_cache_statistics"] = self._tag_cache.get_statistics()

        return report

    # Database operations
    def show_databases(self) -> List[SnowflakeDatabase]:
        """Get all databases using SHOW DATABASES command."""
        databases: List[SnowflakeDatabase] = []

        cur = self.connection.query(SnowflakeQuery.show_databases())

        for database in cur:
            snowflake_db = SnowflakeDatabase(
                name=database["name"],
                created=database["created_on"],
                comment=database["comment"],
            )
            databases.append(snowflake_db)

        logger.info(f"Found {len(databases)} databases")
        return databases

    def get_databases(self, db_name: Optional[str] = None) -> List[SnowflakeDatabase]:
        """Get databases from information schema."""
        databases: List[SnowflakeDatabase] = []

        cur = self.connection.query(SnowflakeQuery.get_databases(db_name))

        for database in cur:
            snowflake_db = SnowflakeDatabase(
                name=database["DATABASE_NAME"],
                created=database["CREATED"],
                last_altered=database["LAST_ALTERED"],
                comment=database["COMMENT"],
            )
            databases.append(snowflake_db)

        logger.info(f"Found {len(databases)} databases")
        return databases

    # Schema operations
    def get_schemas_for_database(self, db_name: str) -> List[SnowflakeSchema]:
        """Get all schemas for a database."""
        snowflake_schemas = []

        # Set database context before querying INFORMATION_SCHEMA
        try:
            self.connection.query(f'USE DATABASE "{db_name}"')
            logger.debug(f"Set database context to {db_name}")
        except Exception as e:
            logger.warning(f"Failed to set database context to {db_name}: {e}")

        cur = self.connection.query(SnowflakeQuery.schemas_for_database(db_name))

        for schema in cur:
            # Handle different result formats (dict vs tuple)
            if isinstance(schema, dict):
                schema_name = schema.get("SCHEMA_NAME")
                created = schema.get("CREATED")
                last_altered = schema.get("LAST_ALTERED")
                comment = schema.get("COMMENT")
            else:
                # Assume tuple format: (SCHEMA_NAME, CREATED, LAST_ALTERED, COMMENT)
                schema_name = schema[0] if len(schema) > 0 else None
                created = schema[1] if len(schema) > 1 else None
                last_altered = schema[2] if len(schema) > 2 else None
                comment = schema[3] if len(schema) > 3 else None
            
            if schema_name:
                snowflake_schema = SnowflakeSchema(
                    name=schema_name,
                    database=db_name,
                    created=created,
                    last_altered=last_altered,
                    comment=comment,
                )
                snowflake_schemas.append(snowflake_schema)

        logger.info(f"Found {len(snowflake_schemas)} schemas in database {db_name}")
        return snowflake_schemas

    # Table operations
    @serialized_lru_cache(maxsize=1)
    def get_tables_for_database(
        self, db_name: str
    ) -> Optional[Dict[str, List[SnowflakeTable]]]:
        """Get all tables for a database organized by schema."""
        logger.info(f"🔍 DEBUG: get_tables_for_database called for {db_name}")
        
        try:
            # Set database context before querying INFORMATION_SCHEMA
            self.connection.query(f'USE DATABASE "{db_name}"')
            logger.debug(f"Set database context to {db_name}")

            query = SnowflakeQuery.tables_for_database(db_name)
            logger.info(f"🔍 DEBUG: Executing query: {query}")
            
            cur = self.connection.query(query)
            logger.info(f"🔍 DEBUG: Query executed successfully")
            
            # Convert cursor to list to avoid consumption issue
            rows = list(cur)
            logger.info(f"🔍 DEBUG: Query returned {len(rows)} rows")
            
            if len(rows) == 0:
                logger.warning(f"🔍 DEBUG: No tables found for database {db_name}")
                return {}

            tables: Dict[str, List[SnowflakeTable]] = {}

            for table in rows:
                logger.info(f"🔍 DEBUG: Processing table row: {table}")
                # SHOW TABLES returns 'schema_name', not 'TABLE_SCHEMA'
                schema_name = table.get("schema_name") or table.get("SCHEMA_NAME")
                table_name = table.get("name") or table.get("NAME")
                logger.info(f"🔍 DEBUG: Extracted schema_name={schema_name}, table_name={table_name}")
                
                if schema_name not in tables:
                    tables[schema_name] = []
                
                # Create SnowflakeTable object with correct field mapping
                snowflake_table = SnowflakeTable(
                    name=table_name,
                    database=db_name,
                    schema=schema_name,
                    type=table.get("kind") or table.get("KIND"),
                    created_time=table.get("created_on") or table.get("CREATED_ON"),
                    last_modified_time=table.get("created_on") or table.get("CREATED_ON"),  # SHOW TABLES doesn't have last_altered
                    size_in_bytes=table.get("bytes") or table.get("BYTES"),
                    rows_count=table.get("rows") or table.get("ROWS"),
                    comment=table.get("comment") or table.get("COMMENT"),
                )
                
                # Set additional fields after instantiation
                snowflake_table.clustering_key = table.get("cluster_by") or table.get("CLUSTER_BY")
                snowflake_table.is_dynamic = table.get("is_dynamic") == "Y" or table.get("IS_DYNAMIC") == "Y"
                snowflake_table.is_iceberg = table.get("is_iceberg") == "Y" or table.get("IS_ICEBERG") == "Y"
                snowflake_table.is_hybrid = table.get("is_hybrid") == "Y" or table.get("IS_HYBRID") == "Y"
                
                tables[schema_name].append(snowflake_table)
                logger.info(f"🔍 DEBUG: Added table {table_name} to schema {schema_name}")

            # Populate dynamic table definitions
            self.populate_dynamic_table_definitions(tables, db_name)

            total_tables = sum(len(schema_tables) for schema_tables in tables.values())
            logger.info(f"Found {total_tables} tables across {len(tables)} schemas in database {db_name}")
            return tables
        except Exception as e:
            logger.warning(f"Failed to get tables for database {db_name}: {e}")
            return {}

    def get_tables_for_schema(
        self, schema_name: str, db_name: str
    ) -> List[SnowflakeTable]:
        """Get all tables for a specific schema using SHOW TABLES command."""
        try:
            logger.info(f"🔍 DEBUG: get_tables_for_schema called for {db_name}.{schema_name}")
            # Set database and schema context before querying
            self.connection.query(f'USE DATABASE "{db_name}"')
            self.connection.query(f'USE SCHEMA "{schema_name}"')
            
            # Use SHOW TABLES command for better permission compatibility
            query = SnowflakeQuery.tables_for_schema(schema_name, db_name)
            logger.info(f"🔍 DEBUG: Executing query: {query}")
            cur = self.connection.query(query)
            
            tables = []
            for row in cur:
                logger.info(f"🔍 DEBUG: Found table row: {row}")
                # SHOW TABLES returns tuples with specific column positions:
                # created_on, name, database_name, schema_name, kind, comment, cluster_by, rows, bytes, owner, retention_time, ...
                table = SnowflakeTable(
                    name=row[1],  # name
                    schema=schema_name,
                    database=db_name,
                    type=row[4],  # kind
                    created_time=row[0],  # created_on
                    last_modified_time=None,  # Not available in SHOW TABLES
                    size_in_bytes=row[8] if len(row) > 8 else None,  # bytes
                    rows_count=row[7] if len(row) > 7 else None,  # rows
                    comment=row[5] if len(row) > 5 else None,  # comment
                )
                
                # Set additional fields after instantiation
                table.clustering_key = row[6] if len(row) > 6 else None  # cluster_by
                table.is_dynamic = (row[15] if len(row) > 15 else 'NO').upper() == 'YES'
                table.is_iceberg = (row[13] if len(row) > 13 else 'NO').upper() == 'YES'
                table.is_hybrid = (row[12] if len(row) > 12 else 'NO').upper() == 'YES'
                tables.append(table)
            
            logger.info(f"🔍 DEBUG: get_tables_for_schema returning {len(tables)} tables")
            return tables
        except Exception as e:
            logger.warning(f"Failed to get tables for schema {db_name}.{schema_name}: {e}")
            return []

    # View operations (implementation would include pagination and caching)
    @serialized_lru_cache(maxsize=1)
    def get_views_for_database(
        self, db_name: str
    ) -> Optional[Dict[str, List[SnowflakeView]]]:
        """Get all views for a database organized by schema."""
        logger.info(f"🔍 DEBUG: get_views_for_database called for {db_name}")
        try:
            # Set database context before querying
            self.connection.query(f'USE DATABASE "{db_name}"')
            logger.debug(f"Set database context to {db_name}")

            # Get all schemas for this database
            schemas = self.get_schemas_for_database(db_name)
            if not schemas:
                logger.warning(f"No schemas found for database {db_name}")
                return {}

            views: Dict[str, List[SnowflakeView]] = {}
            
            # Get views for each schema
            for schema in schemas:
                schema_name = schema.name
                schema_views = self.get_views_for_schema_using_show(db_name, schema_name)
                if schema_views:
                    views[schema_name] = schema_views

            logger.info(f"Found {len(views)} schemas with views in database {db_name}")
            return views
        except Exception as e:
            logger.warning(f"Failed to get views for database {db_name}: {e}")
            return {}

    def get_views_for_schema_using_show(
        self, db_name: str, schema_name: str
    ) -> List[SnowflakeView]:
        """Get views for a specific schema using SHOW VIEWS command."""
        try:
            # Query SHOW VIEWS to get view metadata
            query = f'SHOW VIEWS IN SCHEMA {db_name}.{schema_name}'
            logger.debug(f"Executing query: {query}")
            
            results = self.connection.execute(query)
            views = []
            
            # Properly iterate over cursor results
            for row in results:
                # Handle different result formats (dict vs tuple)
                if isinstance(row, dict):
                    name = row.get("name")
                    database_name = row.get("database_name")
                    schema_name_result = row.get("schema_name")
                    is_secure = row.get("is_secure", "NO").upper() == "YES"
                    comment = row.get("comment")
                    text = row.get("text")  # View definition
                else:
                    # SHOW VIEWS returns columns in specific order
                    # Format: created_on, name, database_name, schema_name, kind, comment, text, is_secure
                    name = row[1] if len(row) > 1 else None
                    database_name = row[2] if len(row) > 2 else None
                    schema_name_result = row[3] if len(row) > 3 else None
                    is_secure = (row[7] if len(row) > 7 else 'NO').upper() == 'YES'
                    comment = row[5] if len(row) > 5 else None
                    text = row[6] if len(row) > 6 else None  # View definition
                
                if name:
                    view = SnowflakeView(
                        name=name,
                        schema=schema_name,
                        database=db_name,
                        view_definition=text,
                        is_secure=is_secure,
                        comment=comment
                    )
                    views.append(view)
            
            logger.debug(f"Found {len(views)} views in schema {db_name}.{schema_name}")
            return views
        except Exception as e:
            logger.warning(f"Failed to get views for schema {db_name}.{schema_name} using SHOW VIEWS: {e}")
            return []

    # Stream operations
    @serialized_lru_cache(maxsize=1)
    def get_streams_for_database(
        self, db_name: str
    ) -> Optional[Dict[str, List[SnowflakeStream]]]:
        """Get all streams for a database organized by schema."""
        logger.info(f"🔍 DEBUG: get_streams_for_database called for {db_name}")
        try:
            # Set database context before querying
            self.connection.query(f'USE DATABASE "{db_name}"')
            logger.debug(f"Set database context to {db_name}")

            # Get all schemas for this database
            schemas = self.get_schemas_for_database(db_name)
            if not schemas:
                logger.warning(f"No schemas found for database {db_name}")
                return {}

            streams: Dict[str, List[SnowflakeStream]] = {}
            
            # Get streams for each schema
            for schema in schemas:
                schema_name = schema.name
                schema_streams = self.get_streams_for_schema(schema_name, db_name)
                if schema_streams:
                    streams[schema_name] = schema_streams

            logger.info(f"Found {len(streams)} schemas with streams in database {db_name}")
            return streams
        except Exception as e:
            logger.warning(f"Failed to get streams for database {db_name}: {e}")
            return {}

    def get_streams_for_schema(
        self, schema_name: str, db_name: str
    ) -> List[SnowflakeStream]:
        """Get all streams for a specific schema using SHOW STREAMS command."""
        try:
            logger.info(f"🔍 DEBUG: get_streams_for_schema called for {db_name}.{schema_name}")
            # Set database and schema context before querying
            self.connection.query(f'USE DATABASE "{db_name}"')
            self.connection.query(f'USE SCHEMA "{schema_name}"')
            
            query = f'SHOW STREAMS IN SCHEMA {db_name}.{schema_name}'
            logger.debug(f"Executing query: {query}")
            
            results = self.connection.execute(query)
            streams = []
            
            # Properly iterate over cursor results
            for row in results:
                # Handle different result formats (dict vs tuple)
                if isinstance(row, dict):
                    name = row.get("name")
                    database_name = row.get("database_name")
                    schema_name_result = row.get("schema_name")
                    table_name = row.get("table_name")
                    comment = row.get("comment")
                    is_stale = row.get("is_stale", "NO").upper() == "YES"
                else:
                    # SHOW STREAMS returns columns in specific order
                    # Format: created_on, name, database_name, schema_name, owner, comment, table_name, source_type, is_stale
                    name = row[1] if len(row) > 1 else None
                    database_name = row[2] if len(row) > 2 else None
                    schema_name_result = row[3] if len(row) > 3 else None
                    table_name = row[6] if len(row) > 6 else None
                    comment = row[5] if len(row) > 5 else None
                    is_stale = (row[8] if len(row) > 8 else 'NO').upper() == 'YES'
                
                if name:
                    stream = SnowflakeStream(
                        name=name,
                        schema=schema_name,
                        database=db_name,
                        table_name=table_name,
                        comment=comment,
                        is_stale=is_stale
                    )
                    streams.append(stream)
            
            logger.debug(f"Found {len(streams)} streams in schema {db_name}.{schema_name}")
            return streams
        except Exception as e:
            logger.warning(f"Failed to get streams for schema {db_name}.{schema_name}: {e}")
            return []

    # Procedure operations
    @serialized_lru_cache(maxsize=1)
    def get_procedures_for_database(
        self, db_name: str
    ) -> Optional[Dict[str, List[SnowflakeProcedure]]]:
        """Get all procedures for a database organized by schema."""
        logger.info(f"🔍 DEBUG: get_procedures_for_database called for {db_name}")
        try:
            # Set database context before querying
            self.connection.query(f'USE DATABASE "{db_name}"')
            logger.debug(f"Set database context to {db_name}")

            # Get all schemas for this database
            schemas = self.get_schemas_for_database(db_name)
            if not schemas:
                logger.warning(f"No schemas found for database {db_name}")
                return {}

            procedures: Dict[str, List[SnowflakeProcedure]] = {}
            
            # Get procedures for each schema
            for schema in schemas:
                schema_name = schema.name
                schema_procedures = self.get_procedures_for_schema(schema_name, db_name)
                if schema_procedures:
                    procedures[schema_name] = schema_procedures

            logger.info(f"Found {len(procedures)} schemas with procedures in database {db_name}")
            return procedures
        except Exception as e:
            logger.warning(f"Failed to get procedures for database {db_name}: {e}")
            return {}

    def get_procedures_for_schema(
        self, schema_name: str, db_name: str
    ) -> List[SnowflakeProcedure]:
        """Get all procedures for a specific schema using SHOW PROCEDURES command."""
        try:
            logger.info(f"🔍 DEBUG: get_procedures_for_schema called for {db_name}.{schema_name}")
            # Set database and schema context before querying
            self.connection.query(f'USE DATABASE "{db_name}"')
            self.connection.query(f'USE SCHEMA "{schema_name}"')
            
            query = f'SHOW PROCEDURES IN SCHEMA {db_name}.{schema_name}'
            logger.debug(f"Executing query: {query}")
            
            results = self.connection.execute(query)
            procedures = []
            
            # Properly iterate over cursor results
            for row in results:
                # Handle different result formats (dict vs tuple)
                if isinstance(row, dict):
                    name = row.get("name")
                    database_name = row.get("database_name")
                    schema_name_result = row.get("schema_name")
                    comment = row.get("comment")
                    is_secure = row.get("is_secure", "NO").upper() == "YES"
                else:
                    # SHOW PROCEDURES returns columns in specific order
                    # Format: created_on, name, database_name, schema_name, owner, comment, is_secure
                    name = row[1] if len(row) > 1 else None
                    database_name = row[2] if len(row) > 2 else None
                    schema_name_result = row[3] if len(row) > 3 else None
                    comment = row[5] if len(row) > 5 else None
                    is_secure = (row[6] if len(row) > 6 else 'NO').upper() == 'YES'
                
                if name:
                    procedure = SnowflakeProcedure(
                        name=name,
                        schema=schema_name,
                        database=db_name,
                        comment=comment,
                        is_secure=is_secure
                    )
                    procedures.append(procedure)
            
            logger.debug(f"Found {len(procedures)} procedures in schema {db_name}.{schema_name}")
            return procedures
        except Exception as e:
            logger.warning(f"Failed to get procedures for schema {db_name}.{schema_name}: {e}")
            return []

    # Column operations with enhanced parallelism
    @serialized_lru_cache(maxsize=SCHEMA_PARALLELISM)
    def get_columns_for_schema(
        self,
        schema_name: str,
        db_name: str,
        cache_exclude_all_objects: Iterable[str],
    ) -> MutableMapping[str, List[SnowflakeColumn]]:
        """Get all columns for tables/views in a schema using optimized parallelism."""
        all_objects = list(cache_exclude_all_objects)
        columns: MutableMapping[str, List[SnowflakeColumn]] = {}

        if len(all_objects) > 10000:
            columns = FileBackedDict()
            logger.info(f"Using FileBackedDict for {len(all_objects)} objects in {db_name}.{schema_name}")

        # Build object batches for processing with optimal parallelism
        if len(all_objects) == 1:
            object_batches = [
                [PrefixGroup(prefix=all_objects[0], names=[], exact_match=True)]
            ]
        else:
            optimal_batch_size = max(1000, len(all_objects) // SCHEMA_PARALLELISM)
            object_batches = build_prefix_batches(
                all_objects,
                max_batch_size=optimal_batch_size,
                max_groups_in_batch=min(5, SCHEMA_PARALLELISM)
            )

        logger.info(
            f"🚀 Processing {len(all_objects)} objects in {len(object_batches)} batches "
            f"for {db_name}.{schema_name} (parallelism: {SCHEMA_PARALLELISM})"
        )
        
        # Performance tracking
        total_start_time = time.time()
        processed_objects = 0
        failed_objects = 0

        # Process batches
        for batch_index, object_batch in enumerate(object_batches):
            if batch_index > 0:
                logger.info(
                    f"Still fetching columns for {db_name}.{schema_name} - "
                    f"batch {batch_index + 1} of {len(object_batches)}"
                )

            query = SnowflakeQuery.columns_for_schema(schema_name, db_name, object_batch)
            cur = self.connection.query(query)

            for column in cur:
                try:
                    table_name = column["TABLE_NAME"]
                    if table_name not in columns:
                        columns[table_name] = []

                    # Enhanced column creation with better error handling
                    column_obj = SnowflakeColumn(
                        name=column["COLUMN_NAME"],
                        ordinal_position=column["ORDINAL_POSITION"],
                        is_nullable=column["IS_NULLABLE"] == "YES",
                        data_type=column["DATA_TYPE"],
                        comment=column["COMMENT"],
                        character_maximum_length=column["CHARACTER_MAXIMUM_LENGTH"],
                        numeric_precision=column["NUMERIC_PRECISION"],
                        numeric_scale=column["NUMERIC_SCALE"],
                    )
                    
                    # Add enhanced metadata if available
                    if "TYPE_DETAILS" in column and column["TYPE_DETAILS"]:
                        column_obj.type_details = column["TYPE_DETAILS"]
                    elif column["DATA_TYPE"] in ('NUMBER', 'DECIMAL', 'NUMERIC'):
                        # Handle numeric types by constructing type details from precision and scale
                        if column["NUMERIC_PRECISION"] is not None and column["NUMERIC_SCALE"] is not None:
                            column_obj.type_details = f"{column['NUMERIC_PRECISION']},{column['NUMERIC_SCALE']}"
                        elif column["NUMERIC_PRECISION"] is not None:
                            column_obj.type_details = str(column["NUMERIC_PRECISION"])
                    
                    if "COLUMN_CLASSIFICATION" in column and column["COLUMN_CLASSIFICATION"]:
                        column_obj.classification = column["COLUMN_CLASSIFICATION"]
                    
                    columns[table_name].append(column_obj)
                    
                except Exception as e:
                    logger.warning(
                        f"Failed to process column {column.get('COLUMN_NAME', 'unknown')} "
                        f"for table {column.get('TABLE_NAME', 'unknown')}: {e}"
                    )
                    continue

        total_columns = sum(len(table_columns) for table_columns in columns.values())
        total_time = time.time() - total_start_time
        
        logger.info(
            f"✅ Column extraction completed: {total_columns} columns across {len(columns)} objects "
            f"in {db_name}.{schema_name} (processed: {processed_objects}, failed: {failed_objects}) "
            f"in {total_time:.2f}s"
        )
        
        if failed_objects > 0:
            logger.warning(f"⚠️  {failed_objects} objects failed column extraction")
            
        return columns

    # Constraint operations with enhanced parallelism
    @serialized_lru_cache(maxsize=SCHEMA_PARALLELISM)
    def get_pk_constraints_for_schema(
        self, schema_name: str, db_name: str
    ) -> Dict[str, SnowflakePK]:
        """Get primary key constraints for a schema with parallel processing."""
        constraints: Dict[str, SnowflakePK] = {}

        cur = self.connection.query(
            SnowflakeQuery.show_primary_keys_for_schema(schema_name, db_name)
        )

        for row in cur:
            table_name = row["table_name"]
            if table_name not in constraints:
                constraints[table_name] = SnowflakePK(
                    name=row["constraint_name"],
                    column_names=[]
                )
            constraints[table_name].column_names.append(row["column_name"])

        logger.info(f"Found {len(constraints)} primary key constraints in {db_name}.{schema_name}")
        return constraints

    @serialized_lru_cache(maxsize=SCHEMA_PARALLELISM)
    def get_fk_constraints_for_schema(
        self, schema_name: str, db_name: str
    ) -> Dict[str, List[SnowflakeFK]]:
        """Get foreign key constraints for a schema with parallel processing."""
        constraints: Dict[str, List[SnowflakeFK]] = {}
        fk_constraints_map: Dict[str, SnowflakeFK] = {}

        cur = self.connection.query(
            SnowflakeQuery.show_foreign_keys_for_schema(schema_name, db_name)
        )

        for row in cur:
            fk_name = row["fk_name"]
            table_name = row["fk_table_name"]

            if fk_name not in fk_constraints_map:
                fk_constraints_map[fk_name] = SnowflakeFK(
                    name=fk_name,
                    column_names=[],
                    referred_database=row["pk_database_name"],
                    referred_schema=row["pk_schema_name"],
                    referred_table=row["pk_table_name"],
                    referred_column_names=[],
                )

            if table_name not in constraints:
                constraints[table_name] = []

            fk_constraints_map[fk_name].column_names.append(row["fk_column_name"])
            fk_constraints_map[fk_name].referred_column_names.append(row["pk_column_name"])
            constraints[table_name].append(fk_constraints_map[fk_name])

        total_constraints = sum(len(table_fks) for table_fks in constraints.values())
        logger.info(f"Found {total_constraints} foreign key constraints in {db_name}.{schema_name}")
        return constraints

    # Procedure operations
    @serialized_lru_cache(maxsize=1)
    def get_procedures_for_database(self, db_name: str) -> Dict[str, List[BaseProcedure]]:
        """Get all stored procedures for a database organized by schema."""
        procedures: Dict[str, List[BaseProcedure]] = {}

        try:
            cur = self.connection.query(SnowflakeQuery.procedures_for_database(db_name))
        except Exception as e:
            logger.debug(f"Failed to get procedures for database {db_name}", exc_info=e)
            return procedures

        for proc in cur:
            schema_name = proc["PROCEDURE_SCHEMA"]
            if schema_name not in procedures:
                procedures[schema_name] = []

            # Parse procedure arguments if available
            parameters = []
            if proc.get("ARGUMENTS"):
                try:
                    # Custom parsing logic for procedure arguments would go here
                    args_str = proc["ARGUMENTS"]
                    # Implementation would parse Snowflake's argument format
                    pass
                except Exception as e:
                    logger.debug(f"Failed to parse arguments for procedure {proc['PROCEDURE_NAME']}: {e}")

            procedures[schema_name].append(
                BaseProcedure(
                    name=proc["PROCEDURE_NAME"],
                    database=db_name,
                    schema=schema_name,
                    language=proc.get("PROCEDURE_LANGUAGE", "SQL"),
                    definition=proc.get("PROCEDURE_DEFINITION"),
                    description=proc.get("PROCEDURE_COMMENT"),
                    comment=proc.get("PROCEDURE_COMMENT"),
                    created=proc.get("CREATED"),
                    last_altered=proc.get("LAST_ALTERED"),
                    owner=proc.get("PROCEDURE_OWNER"),
                    security_type=proc.get("SECURITY_TYPE"),
                    return_type=proc.get("DATA_TYPE"),
                    is_secure=proc.get("IS_SECURE", "NO").upper() == "YES",
                    external_access_integrations=proc.get("EXTERNAL_ACCESS_INTEGRATIONS"),
                    secrets=proc.get("SECRETS"),
                    imports=proc.get("IMPORTS"),
                    handler=proc.get("HANDLER"),
                    runtime_version=proc.get("RUNTIME_VERSION"),
                    packages=proc.get("PACKAGES"),
                    parameters=parameters,
                )
            )

        total_procedures = sum(len(schema_procs) for schema_procs in procedures.values())
        logger.info(f"Found {total_procedures} procedures across {len(procedures)} schemas in database {db_name}")
        return procedures

    # Stream operations (implementation would be similar to other object types)
    @serialized_lru_cache(maxsize=1)
    def get_streams_for_database(self, db_name: str) -> Dict[str, List[SnowflakeStream]]:
        """Get all streams for a database."""
        try:
            # Query SHOW STREAMS to get stream metadata
            query = f"SHOW STREAMS IN DATABASE {db_name}"
            results = self.connection.execute(query)
            
            streams_by_schema = {}
            
            for row in results:
                # Handle different result formats (dict vs tuple)
                if isinstance(row, dict):
                    schema_name = row.get("schema_name")
                    stream_name = row.get("name")
                    table_name = row.get("table_name")
                    comment = row.get("comment")
                else:
                    # SHOW STREAMS returns columns in specific order
                    # Format: created_on, name, database_name, schema_name, owner, comment, table_name, ...
                    schema_name = row[3] if len(row) > 3 else None
                    stream_name = row[1] if len(row) > 1 else None
                    table_name = row[6] if len(row) > 6 else None
                    comment = row[5] if len(row) > 5 else None
                
                if schema_name and stream_name:
                    if schema_name not in streams_by_schema:
                        streams_by_schema[schema_name] = []
                    
                    stream = SnowflakeStream(
                        name=stream_name,
                        schema=schema_name,
                        database=db_name,
                        table_name=table_name,
                        comment=comment
                    )
                    
                    streams_by_schema[schema_name].append(stream)
            
            return streams_by_schema
        except Exception as e:
            logger.warning(f"Failed to get streams for database {db_name}: {e}")
            return {}

    # Tag operations
    def get_tags_for_database_without_propagation(self, db_name: str) -> _SnowflakeTagCache:
        """Get all tags for a database without propagation."""
        # Use direct information_schema query instead of account_usage due to delay
        logger.info(f"🔍 DEBUG: Loading tags for database {db_name} using direct query")
        cur = self.connection.query(
            SnowflakeQuery.get_all_tags_in_database_without_propagation(db_name)
        )

        tags = _SnowflakeTagCache()

        for tag in cur:
            snowflake_tag = SnowflakeTag(
                database=tag["TAG_DATABASE"],
                schema=tag["TAG_SCHEMA"],
                name=tag["TAG_NAME"],
                value=tag["TAG_VALUE"],
            )

            object_name = tag["OBJECT_NAME"]
            object_schema = tag["OBJECT_SCHEMA"]
            object_database = tag["OBJECT_DATABASE"]
            domain = tag["DOMAIN"].lower()

            if domain == SnowflakeObjectDomain.DATABASE:
                tags.add_database_tag(object_name, snowflake_tag)
            elif domain == SnowflakeObjectDomain.SCHEMA:
                tags.add_schema_tag(object_name, object_database, snowflake_tag)
            elif domain == SnowflakeObjectDomain.TABLE:
                tags.add_table_tag(object_name, object_schema, object_database, snowflake_tag)
            elif domain == SnowflakeObjectDomain.COLUMN:
                column_name = tag["COLUMN_NAME"]
                tags.add_column_tag(
                    column_name, object_name, object_schema, object_database, snowflake_tag
                )
            elif domain == "procedure":
                tags.add_procedure_tag(object_name, object_schema, object_database, snowflake_tag)
            elif domain == "view":
                tags.add_view_tag(object_name, object_schema, object_database, snowflake_tag)
            elif domain == "stream":
                tags.add_stream_tag(object_name, object_schema, object_database, snowflake_tag)
            else:
                logger.warning(f"Encountered unexpected domain: {domain}")
                continue

        stats = tags.get_statistics()
        logger.info(f"Loaded tags for database {db_name}: {stats}")
        self._tag_cache = tags
        return tags

    # Change tracking with ChangeTypeClass
    def track_schema_changes(
        self,
        old_schema: SnowflakeSchema,
        new_schema: SnowflakeSchema
    ) -> List[Tuple[ChangeTypeClass, str]]:
        """
        Track changes between schema versions using ChangeTypeClass.

        Args:
            old_schema: Previous schema version
            new_schema: Current schema version

        Returns:
            List of changes with change types and descriptions
        """
        changes = []

        # Check for schema metadata changes
        if old_schema.comment != new_schema.comment:
            changes.append((
                ChangeTypeClass(ChangeTypeClass.MODIFICATION),
                f"Schema comment changed from '{old_schema.comment}' to '{new_schema.comment}'"
            ))

        # Check for table additions/removals
        old_tables = set(old_schema.tables)
        new_tables = set(new_schema.tables)

        for added_table in new_tables - old_tables:
            changes.append((
                ChangeTypeClass(ChangeTypeClass.ADDITION),
                f"Table '{added_table}' added to schema"
            ))

        for removed_table in old_tables - new_tables:
            changes.append((
                ChangeTypeClass(ChangeTypeClass.REMOVAL),
                f"Table '{removed_table}' removed from schema"
            ))

        # Check for procedure changes
        old_procedures = set(old_schema.procedures)
        new_procedures = set(new_schema.procedures)

        for added_proc in new_procedures - old_procedures:
            changes.append((
                ChangeTypeClass(ChangeTypeClass.PROCEDURE_CHANGE),
                f"Procedure '{added_proc}' added to schema"
            ))

        for removed_proc in old_procedures - new_procedures:
            changes.append((
                ChangeTypeClass(ChangeTypeClass.PROCEDURE_CHANGE),
                f"Procedure '{removed_proc}' removed from schema"
            ))

        return changes

    # Dynamic table operations (implementation would handle definitions and lag info)
    def populate_dynamic_table_definitions(
        self, tables: Dict[str, List[SnowflakeTable]], db_name: str
    ) -> None:
        """Populate dynamic table definitions for tables marked as dynamic."""
        # Implementation would use SHOW DYNAMIC TABLES to get definitions
        pass

    # Utility methods
    def get_schema_summary(self, db_name: str, schema_name: str) -> Dict[str, Any]:
        """Get comprehensive summary for a schema including procedures."""
        summary = {
            "database": db_name,
            "schema": schema_name,
            "full_name": f"{db_name}.{schema_name}",
        }

        try:
            # Get tables
            tables = self.get_tables_for_schema(schema_name, db_name)
            summary["table_count"] = len(tables)
            summary["tables"] = [table.to_dict() for table in tables]

            # Get views from database-level cache
            all_views = self.get_views_for_database(db_name)
            schema_views = all_views.get(schema_name, []) if all_views else []
            summary["view_count"] = len(schema_views)
            summary["views"] = [view.to_dict() for view in schema_views]

            # Get streams from database-level cache
            all_streams = self.get_streams_for_database(db_name)
            schema_streams = all_streams.get(schema_name, []) if all_streams else []
            summary["stream_count"] = len(schema_streams)
            summary["streams"] = [stream.to_dict() for stream in schema_streams]

            # Get procedures from database-level cache
            all_procedures = self.get_procedures_for_database(db_name)
            schema_procedures = all_procedures.get(schema_name, []) if all_procedures else []
            summary["procedure_count"] = len(schema_procedures)
            summary["procedures"] = [proc.to_dict() for proc in schema_procedures]

            # Get columns for all objects
            all_object_names = (
                [t.name for t in tables] +
                [v.name for v in schema_views] +
                [s.name for s in schema_streams]
            )
            if all_object_names:
                columns = self.get_columns_for_schema(schema_name, db_name, all_object_names)
                total_columns = sum(len(table_columns) for table_columns in columns.values())
                summary["total_columns"] = total_columns
                summary["objects_with_columns"] = len(columns)

        except Exception as e:
            logger.error(f"Failed to get complete schema summary for {db_name}.{schema_name}: {e}")
            summary["error"] = str(e)

        return summary

    def clear_cache(self) -> None:
        """Clear all cached data including procedures."""
        cache_functions = [
            self.get_tables_for_database,
            self.get_views_for_database,
            self.get_columns_for_schema,
            self.get_streams_for_database,
            self.get_pk_constraints_for_schema,
            self.get_fk_constraints_for_schema,
            self.get_procedures_for_database,
        ]

        for func in cache_functions:
            if hasattr(func, 'cache_clear'):
                func.cache_clear()

        # Clear tag cache
        self._tag_cache = None

        logger.info(f"Cleared all data dictionary caches (parallelism: {SCHEMA_PARALLELISM})")

    def get_tags_for_object_with_propagation(
        self,
        domain: str,
        quoted_identifier: str,
        db_name: str,
        schema_name: Optional[str] = None,
        table_name: Optional[str] = None,
    ) -> List[Any]:
        """
        Get tags for a Snowflake object with propagation support.

        Args:
            domain: Object domain (TABLE, VIEW, SCHEMA, DATABASE, etc.)
            quoted_identifier: Quoted identifier for the object
            db_name: Database name
            schema_name: Optional schema name
            table_name: Optional table name

        Returns:
            List of tags with propagation information
        """
        try:
            logger.info(f"🔍 DEBUG: Getting tags for object: {domain}.{quoted_identifier} in {db_name}")
            
            # Query for tags on the specific object
            query = SnowflakeQuery.get_all_tags_on_object_with_propagation(
                db_name, quoted_identifier, domain
            )
            logger.info(f"🔍 DEBUG: Executing tag query: {query}")
            
            cur = self.connection.query(query)
            
            tags = []
            for tag in cur:
                logger.info(f"🔍 DEBUG: Processing tag: {tag}")
                snowflake_tag = SnowflakeTag(
                    database=tag["TAG_DATABASE"],
                    schema=tag["TAG_SCHEMA"],
                    name=tag["TAG_NAME"],
                    value=tag["TAG_VALUE"],
                )
                tags.append(snowflake_tag)
            
            logger.info(f"🔍 DEBUG: Found {len(tags)} tags for {domain}.{quoted_identifier}")
            return tags
            
        except Exception as e:
            logger.error(f"Failed to get tags for object {domain}.{quoted_identifier}: {e}")
            return []

    def get_parallelism_info(self) -> Dict[str, Any]:
        """Get information about current parallelism settings."""
        return {
            "current_parallelism": SCHEMA_PARALLELISM,
            "optimal_for_schemas": get_optimal_parallelism,
            "environment_variable": "DATAGUILD_SNOWFLAKE_SCHEMA_PARALLELISM",
            "cache_sizes": {
                "columns": SCHEMA_PARALLELISM,
                "pk_constraints": SCHEMA_PARALLELISM,
                "fk_constraints": SCHEMA_PARALLELISM,
            }
        }


# =============================================
# Factory Function
# =============================================

def create_snowflake_data_dictionary(
    connection: SnowflakeConnection,
    report: SnowflakeV2Report,
    fetch_views_from_information_schema: bool = False,
    schema_parallelism: Optional[int] = None,
) -> SnowflakeDataDictionary:
    """
    Factory function to create SnowflakeDataDictionary instance with parallelism control.

    Args:
        connection: Snowflake connection instance
        report: Report instance for tracking operations
        fetch_views_from_information_schema: Whether to use information schema for views
        schema_parallelism: Optional custom parallelism level

    Returns:
        Configured SnowflakeDataDictionary instance
    """
    if schema_parallelism is not None:
        set_schema_parallelism(schema_parallelism)

    return SnowflakeDataDictionary(
        connection=connection,
        report=report,
        fetch_views_from_information_schema=fetch_views_from_information_schema,
    )


# =============================================
# Exports
# =============================================

__all__ = [
    # Core data structures
    'SnowflakeDatabase',
    'SnowflakeSchema',
    'SnowflakeTable',
    'SnowflakeDynamicTable',
    'SnowflakeView',
    'SnowflakeColumn',
    'SnowflakeStream',
    'SnowflakeTag',
    'SnowflakePK',
    'SnowflakeFK',

    # Procedure structures
    'BaseProcedure',
    'ProcedureParameter',

    # Change management
    'ChangeTypeClass',

    # Data dictionary and utilities
    'SnowflakeDataDictionary',
    'create_snowflake_data_dictionary',

    # Parallelism utilities
    'SCHEMA_PARALLELISM',
    'get_schema_parallelism',
    'set_schema_parallelism',
    'get_optimal_parallelism',
]
