"""
Snowflake data dictionary for DataGuild metadata extraction.

This module provides comprehensive data structures and extraction logic for
Snowflake metadata including databases, schemas, tables, views, columns,
tags, procedures, and other governance information with optimized parallel processing.
"""

import logging
import os
import json
import hashlib
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, MutableMapping, Optional, Tuple, Union, Set, Type
from enum import Enum

from dataguild.configuration.common import AllowDenyPattern
from dataguild.api.common import PipelineContext
from dataguild.source.snowflake.constants import SnowflakeObjectDomain
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

SCHEMA_PARALLELISM = int(os.getenv("DATAGUILD_SNOWFLAKE_SCHEMA_PARALLELISM", 20))


def get_schema_parallelism() -> int:
    """Get the current schema parallelism setting."""
    return SCHEMA_PARALLELISM


def set_schema_parallelism(parallelism: int) -> None:
    """Set the schema parallelism level."""
    global SCHEMA_PARALLELISM
    if not (1 <= parallelism <= 100):
        raise ValueError("Schema parallelism must be between 1 and 100")
    SCHEMA_PARALLELISM = parallelism
    logger.info(f"Schema parallelism set to {SCHEMA_PARALLELISM}")


def get_optimal_parallelism(schema_count: int) -> int:
    """Calculate optimal parallelism based on schema count."""
    if schema_count <= 5:
        return min(schema_count, 5)
    elif schema_count <= 50:
        return min(schema_count // 2, SCHEMA_PARALLELISM)
    else:
        return SCHEMA_PARALLELISM


# =============================================
# ChangeTypeClass - DataGuild Change Management
# =============================================

class ChangeTypeClass:
    """
    Comprehensive change type classification for DataGuild metadata changes.

    Provides standardized change type categorization for tracking metadata
    modifications across all Snowflake objects and schema evolution.
    """

    # Core change types
    UNKNOWN = 'unknown'
    METADATA = 'metadata'
    ADDITION = 'addition'
    REMOVAL = 'removal'
    MODIFICATION = 'modification'
    MOVED = 'moved'
    ALTERED = 'altered'

    # Extended change types for comprehensive tracking
    SCHEMA_CHANGE = 'schema_change'
    DATA_TYPE_CHANGE = 'data_type_change'
    CONSTRAINT_CHANGE = 'constraint_change'
    TAG_CHANGE = 'tag_change'
    PROCEDURE_CHANGE = 'procedure_change'
    VIEW_DEFINITION_CHANGE = 'view_definition_change'
    PERMISSION_CHANGE = 'permission_change'

    TYPES = [
        UNKNOWN, METADATA, ADDITION, REMOVAL, MODIFICATION,
        MOVED, ALTERED, SCHEMA_CHANGE, DATA_TYPE_CHANGE,
        CONSTRAINT_CHANGE, TAG_CHANGE, PROCEDURE_CHANGE,
        VIEW_DEFINITION_CHANGE, PERMISSION_CHANGE
    ]

    def __init__(self, type_: str):
        """
        Initialize change type.

        Args:
            type_: Change type string

        Raises:
            ValueError: If type is not a valid change type
        """
        if type_ not in self.TYPES:
            raise ValueError(f'Invalid change type: {type_}. Valid types: {self.TYPES}')
        self.type = type_

    def __str__(self) -> str:
        """String representation of the change type."""
        return self.type

    def __eq__(self, other) -> bool:
        """Check equality with another ChangeTypeClass instance."""
        return isinstance(other, ChangeTypeClass) and self.type == other.type

    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.type)

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f'ChangeTypeClass({self.type})'

    @classmethod
    def all_types(cls) -> List[str]:
        """Get all available change types."""
        return cls.TYPES.copy()

    @classmethod
    def core_types(cls) -> List[str]:
        """Get core change types."""
        return [cls.UNKNOWN, cls.METADATA, cls.ADDITION, cls.REMOVAL,
                cls.MODIFICATION, cls.MOVED, cls.ALTERED]

    @classmethod
    def extended_types(cls) -> List[str]:
        """Get extended change types."""
        return [cls.SCHEMA_CHANGE, cls.DATA_TYPE_CHANGE, cls.CONSTRAINT_CHANGE,
                cls.TAG_CHANGE, cls.PROCEDURE_CHANGE, cls.VIEW_DEFINITION_CHANGE,
                cls.PERMISSION_CHANGE]

    def is_destructive(self) -> bool:
        """Check if this change type is potentially destructive."""
        destructive_types = {self.REMOVAL, self.ALTERED, self.DATA_TYPE_CHANGE,
                           self.CONSTRAINT_CHANGE}
        return self.type in destructive_types

    def is_additive(self) -> bool:
        """Check if this change type is purely additive."""
        additive_types = {self.ADDITION, self.TAG_CHANGE}
        return self.type in additive_types

    def get_severity(self) -> str:
        """Get the severity level of this change type."""
        if self.type in {self.REMOVAL, self.DATA_TYPE_CHANGE}:
            return "HIGH"
        elif self.type in {self.ALTERED, self.CONSTRAINT_CHANGE, self.PROCEDURE_CHANGE}:
            return "MEDIUM"
        elif self.type in {self.ADDITION, self.METADATA, self.TAG_CHANGE}:
            return "LOW"
        else:
            return "UNKNOWN"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.type,
            "severity": self.get_severity(),
            "is_destructive": self.is_destructive(),
            "is_additive": self.is_additive()
        }


# =============================================
# DataGuild Advanced Metadata Schemas
# =============================================

class SchemaFieldDataType(Enum):
    """Enumeration of supported schema field data types."""
    ARRAY = "array"
    BOOLEAN = "boolean"
    BYTES = "bytes"
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    NULL = "null"
    NUMBER = "number"
    STRING = "string"
    RECORD = "record"
    UNION = "union"


@dataclass(frozen=True)
class BaseDataType(ABC):
    """Abstract base class for all data types."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        pass

    @abstractmethod
    def validate_value(self, value: Any) -> bool:
        """Validate if a value matches this data type."""
        pass

    def get_type_name(self) -> str:
        """Get the type name."""
        return self.__class__.__name__.replace("Type", "").lower()


@dataclass(frozen=True)
class ArrayType(BaseDataType):
    """Array data type with element type specification."""
    element_type: 'BaseDataType'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "array",
            "elementType": self.element_type.to_dict()
        }

    def validate_value(self, value: Any) -> bool:
        if not isinstance(value, (list, tuple)):
            return False
        return all(self.element_type.validate_value(item) for item in value)


@dataclass(frozen=True)
class StringType(BaseDataType):
    """String data type with length constraints."""
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    charset: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": "string"}
        if self.max_length is not None:
            result["maxLength"] = self.max_length
        if self.min_length is not None:
            result["minLength"] = self.min_length
        if self.charset:
            result["charset"] = self.charset
        return result

    def validate_value(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        if self.min_length is not None and len(value) < self.min_length:
            return False
        if self.max_length is not None and len(value) > self.max_length:
            return False
        return True


@dataclass(frozen=True)
class NumberType(BaseDataType):
    """Numeric data type with precision and scale."""
    precision: Optional[int] = None
    scale: Optional[int] = None
    signed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": "number"}
        if self.precision is not None:
            result["precision"] = self.precision
        if self.scale is not None:
            result["scale"] = self.scale
        result["signed"] = self.signed
        return result

    def validate_value(self, value: Any) -> bool:
        return isinstance(value, (int, float)) and (self.signed or value >= 0)


@dataclass(frozen=True)
class BooleanType(BaseDataType):
    """Boolean data type."""

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "boolean"}

    def validate_value(self, value: Any) -> bool:
        return isinstance(value, bool)


@dataclass(frozen=True)
class TagAssociation:
    """Association between an entity and a tag."""
    tag: str  # Tag URN
    context: Optional[str] = None
    propagate: bool = True

    def to_dict(self) -> Dict[str, Any]:
        result = {"tag": self.tag}
        if self.context:
            result["context"] = self.context
        result["propagate"] = self.propagate
        return result


@dataclass(frozen=True)
class GlobalTags:
    """Global tags applied to an entity."""
    tags: List[TagAssociation]

    def __post_init__(self):
        """Validate tags."""
        if not isinstance(self.tags, list):
            raise ValueError("Tags must be a list")
        for tag in self.tags:
            if not isinstance(tag, TagAssociation):
                raise ValueError(f"Invalid tag association: {tag}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tags": [tag.to_dict() for tag in self.tags]
        }

    def get_tag_urns(self) -> Set[str]:
        """Get set of all tag URNs."""
        return {tag.tag for tag in self.tags}


@dataclass(frozen=True)
class Status:
    """Entity status metadata."""
    removed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"removed": self.removed}


@dataclass(frozen=True)
class SubTypes:
    """Entity subtype information."""
    typeNames: List[str]

    def __post_init__(self):
        """Validate subtypes."""
        if not isinstance(self.typeNames, list):
            raise ValueError("Type names must be a list")
        if not self.typeNames:
            raise ValueError("Must have at least one type name")

    def to_dict(self) -> Dict[str, Any]:
        return {"typeNames": self.typeNames}


@dataclass(frozen=True)
class TimeStamp:
    """Timestamp representation."""
    time: int  # Unix timestamp in milliseconds
    actor: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"time": self.time}
        if self.actor:
            result["actor"] = self.actor
        return result

    @classmethod
    def now(cls, actor: Optional[str] = None) -> 'TimeStamp':
        """Create timestamp for current time."""
        return cls(time=int(datetime.now().timestamp() * 1000), actor=actor)


@dataclass(frozen=True)
class DatasetProperties:
    """Dataset properties and metadata."""
    name: str
    qualifiedName: Optional[str] = None
    description: Optional[str] = None
    customProperties: Optional[Dict[str, str]] = None
    externalUrl: Optional[str] = None
    created: Optional[TimeStamp] = None
    lastModified: Optional[TimeStamp] = None

    def __post_init__(self):
        """Validate dataset properties."""
        if not self.name:
            raise ValueError("Dataset name cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"name": self.name}

        if self.qualifiedName:
            result["qualifiedName"] = self.qualifiedName
        if self.description:
            result["description"] = self.description
        if self.customProperties:
            result["customProperties"] = self.customProperties
        if self.externalUrl:
            result["externalUrl"] = self.externalUrl
        if self.created:
            result["created"] = self.created.to_dict()
        if self.lastModified:
            result["lastModified"] = self.lastModified.to_dict()

        return result


# =============================================
# Core Snowflake Data Structures
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


@dataclass
class SnowflakeTable:
    """Represents a Snowflake table with comprehensive metadata."""
    name: str
    database: str
    schema: str
    type: Optional[str] = None
    created: Optional[datetime] = None
    last_altered: Optional[datetime] = None
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


@dataclass
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
class SnowflakeView:
    """Represents a Snowflake view with comprehensive metadata."""
    name: str
    database: str
    schema: str
    created: Optional[datetime] = None
    last_altered: Optional[datetime] = None
    comment: Optional[str] = None
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

        cur = self.connection.query(SnowflakeQuery.schemas_for_database(db_name))

        for schema in cur:
            snowflake_schema = SnowflakeSchema(
                name=schema["SCHEMA_NAME"],
                database=db_name,
                created=schema["CREATED"],
                last_altered=schema["LAST_ALTERED"],
                comment=schema["COMMENT"],
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
        tables: Dict[str, List[SnowflakeTable]] = {}

        try:
            cur = self.connection.query(SnowflakeQuery.tables_for_database(db_name))
        except Exception as e:
            logger.debug(f"Failed to get all tables for database - {db_name}", exc_info=e)
            return None

        for table in cur:
            schema_name = table["TABLE_SCHEMA"]
            if schema_name not in tables:
                tables[schema_name] = []

            is_dynamic = table.get("IS_DYNAMIC", "NO").upper() == "YES"
            table_cls = SnowflakeDynamicTable if is_dynamic else SnowflakeTable

            tables[schema_name].append(
                table_cls(
                    name=table["TABLE_NAME"],
                    database=db_name,
                    schema=schema_name,
                    type=table["TABLE_TYPE"],
                    created=table["CREATED"],
                    last_altered=table["LAST_ALTERED"],
                    size_in_bytes=table["BYTES"],
                    rows_count=table["ROW_COUNT"],
                    comment=table["COMMENT"],
                    clustering_key=table["CLUSTERING_KEY"],
                    is_dynamic=is_dynamic,
                    is_iceberg=table.get("IS_ICEBERG", "NO").upper() == "YES",
                    is_hybrid=table.get("IS_HYBRID", "NO").upper() == "YES",
                )
            )

        # Populate dynamic table definitions
        self.populate_dynamic_table_definitions(tables, db_name)

        total_tables = sum(len(schema_tables) for schema_tables in tables.values())
        logger.info(f"Found {total_tables} tables across {len(tables)} schemas in database {db_name}")
        return tables

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
            f"Processing {len(all_objects)} objects in {len(object_batches)} batches "
            f"for {db_name}.{schema_name} (parallelism: {SCHEMA_PARALLELISM})"
        )

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
                table_name = column["TABLE_NAME"]
                if table_name not in columns:
                    columns[table_name] = []

                columns[table_name].append(
                    SnowflakeColumn(
                        name=column["COLUMN_NAME"],
                        ordinal_position=column["ORDINAL_POSITION"],
                        is_nullable=column["IS_NULLABLE"] == "YES",
                        data_type=column["DATA_TYPE"],
                        comment=column["COMMENT"],
                        character_maximum_length=column["CHARACTER_MAXIMUM_LENGTH"],
                        numeric_precision=column["NUMERIC_PRECISION"],
                        numeric_scale=column["NUMERIC_SCALE"],
                    )
                )

        total_columns = sum(len(table_columns) for table_columns in columns.values())
        logger.info(f"Found {total_columns} columns across {len(columns)} objects in {db_name}.{schema_name}")
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

    # View and Stream operations would follow similar patterns...

    # Tag operations with ChangeTypeClass integration
    def get_tags_for_database_without_propagation(self, db_name: str) -> _SnowflakeTagCache:
        """Get all tags for a database without propagation."""
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
                ChangeTypeClass(ChangeTypeClass.METADATA),
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

    # Utility methods
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

        self._tag_cache = None
        logger.info(f"Cleared all data dictionary caches (parallelism: {SCHEMA_PARALLELISM})")

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

    # Additional methods would be implemented following similar patterns...
    def populate_dynamic_table_definitions(
        self, tables: Dict[str, List[SnowflakeTable]], db_name: str
    ) -> None:
        """Populate dynamic table definitions for tables marked as dynamic."""
        pass  # Implementation would handle dynamic table definitions


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
# Utility Functions
# =============================================

def create_string_type(max_length: Optional[int] = None) -> 'SchemaFieldDataType':
    """Create a string type for schema fields."""
    return StringType(max_length=max_length)


def create_number_type(precision: Optional[int] = None, scale: Optional[int] = None) -> NumberType:
    """Create a number type for schema fields."""
    return NumberType(precision=precision, scale=scale)


def create_boolean_type() -> BooleanType:
    """Create a boolean type for schema fields."""
    return BooleanType()


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

    # Advanced schema types
    'BaseDataType',
    'ArrayType',
    'StringType',
    'NumberType',
    'BooleanType',
    'TagAssociation',
    'GlobalTags',
    'Status',
    'SubTypes',
    'TimeStamp',
    'DatasetProperties',

    # Data dictionary and utilities
    'SnowflakeDataDictionary',
    'create_snowflake_data_dictionary',

    # Parallelism utilities
    'SCHEMA_PARALLELISM',
    'get_schema_parallelism',
    'set_schema_parallelism',
    'get_optimal_parallelism',

    # Utility functions
    'create_string_type',
    'create_number_type',
    'create_boolean_type',
]
