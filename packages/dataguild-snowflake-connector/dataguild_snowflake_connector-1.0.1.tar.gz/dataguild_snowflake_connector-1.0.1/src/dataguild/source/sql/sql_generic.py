"""
DataGuild SQL Generic Base Classes

Base classes for SQL-based data source ingestion with comprehensive
table metadata, column information, and constraint tracking.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from dataguild.metadata.schemas import MetadataEvent, MetadataEventType

logger = logging.getLogger(__name__)


class TableType(Enum):
    """Enumeration of supported table types."""
    TABLE = "TABLE"
    VIEW = "VIEW"
    MATERIALIZED_VIEW = "MATERIALIZED_VIEW"
    EXTERNAL_TABLE = "EXTERNAL_TABLE"
    TEMPORARY_TABLE = "TEMPORARY_TABLE"
    SYSTEM_TABLE = "SYSTEM_TABLE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "TableType":
        """Create TableType from string value."""
        if not value:
            return cls.UNKNOWN
        try:
            return cls(value.upper().replace(" ", "_"))
        except ValueError:
            logger.warning(f"Unknown table type: {value}, defaulting to UNKNOWN")
            return cls.UNKNOWN


@dataclass
class ColumnInfo:
    """Column metadata information."""
    name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    default_value: Optional[str] = None
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    ordinal_position: Optional[int] = None
    comment: Optional[str] = None

    def __post_init__(self):
        """Validate column information."""
        if not self.name:
            raise ValueError("Column name is required")
        if not self.data_type:
            raise ValueError("Column data_type is required")


@dataclass
class ConstraintInfo:
    """Table constraint information."""
    name: str
    constraint_type: str  # PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK
    column_names: List[str] = field(default_factory=list)
    referenced_table: Optional[str] = None
    referenced_columns: Optional[List[str]] = None
    definition: Optional[str] = None


@dataclass
class IndexInfo:
    """Table index information."""
    name: str
    column_names: List[str]
    is_unique: bool = False
    is_clustered: bool = False
    index_type: Optional[str] = None


@dataclass
class BaseTable:
    """
    Base table metadata with comprehensive information for profiling and lineage.

    This class provides a unified interface for table metadata across different
    SQL databases and data warehouses in the DataGuild system.
    """

    # Required fields
    name: str
    schema: str
    database: str

    # Table characteristics
    type: TableType = TableType.UNKNOWN
    rows_count: Optional[int] = None
    size_in_bytes: Optional[int] = None

    # Metadata
    created_time: Optional[datetime] = None
    last_modified_time: Optional[datetime] = None
    comment: Optional[str] = None

    # Column and constraint information
    columns: List[ColumnInfo] = field(default_factory=list)
    constraints: List[ConstraintInfo] = field(default_factory=list)
    indexes: List[IndexInfo] = field(default_factory=list)

    # Additional properties
    owner: Optional[str] = None
    location: Optional[str] = None  # For external tables
    storage_format: Optional[str] = None  # PARQUET, AVRO, etc.
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    # Processing metadata
    last_analyzed: Optional[datetime] = None
    is_partitioned: bool = False
    partition_keys: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate table information after initialization."""
        if not self.name:
            raise ValueError("Table name is required")
        if not self.schema:
            raise ValueError("Schema name is required")
        if not self.database:
            raise ValueError("Database name is required")

        # Convert string type to enum if needed
        if isinstance(self.type, str):
            self.type = TableType.from_string(self.type)

    def get_fully_qualified_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.database}.{self.schema}.{self.name}"

    def get_column_by_name(self, column_name: str) -> Optional[ColumnInfo]:
        """Get column information by name."""
        for column in self.columns:
            if column.name.lower() == column_name.lower():
                return column
        return None

    def get_primary_key_columns(self) -> List[ColumnInfo]:
        """Get all primary key columns."""
        return [col for col in self.columns if col.is_primary_key]

    def get_foreign_key_columns(self) -> List[ColumnInfo]:
        """Get all foreign key columns."""
        return [col for col in self.columns if col.is_foreign_key]

    def is_external_table(self) -> bool:
        """Check if this is an external table."""
        return self.type == TableType.EXTERNAL_TABLE

    def is_view(self) -> bool:
        """Check if this is a view or materialized view."""
        return self.type in {TableType.VIEW, TableType.MATERIALIZED_VIEW}

    def is_temporary(self) -> bool:
        """Check if this is a temporary table."""
        return self.type == TableType.TEMPORARY_TABLE

    def get_size_mb(self) -> Optional[float]:
        """Get table size in megabytes."""
        if self.size_in_bytes is not None:
            return self.size_in_bytes / (1024 * 1024)
        return None

    def get_size_gb(self) -> Optional[float]:
        """Get table size in gigabytes."""
        if self.size_in_bytes is not None:
            return self.size_in_bytes / (1024 * 1024 * 1024)
        return None

    def add_column(self, column: ColumnInfo) -> None:
        """Add column to table metadata."""
        # Check for duplicate columns
        existing = self.get_column_by_name(column.name)
        if existing:
            logger.warning(f"Column {column.name} already exists in table {self.name}")
            return

        self.columns.append(column)

    def add_constraint(self, constraint: ConstraintInfo) -> None:
        """Add constraint to table metadata."""
        self.constraints.append(constraint)

    def add_index(self, index: IndexInfo) -> None:
        """Add index to table metadata."""
        self.indexes.append(index)

    def add_tag(self, tag: str) -> None:
        """Add tag to table."""
        self.tags.add(tag)

    def has_tag(self, tag: str) -> bool:
        """Check if table has specific tag."""
        return tag in self.tags

    def set_property(self, key: str, value: Any) -> None:
        """Set custom property."""
        self.properties[key] = value

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get custom property value."""
        return self.properties.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert table metadata to dictionary."""
        return {
            "name": self.name,
            "schema": self.schema,
            "database": self.database,
            "fully_qualified_name": self.get_fully_qualified_name(),
            "type": self.type.value,
            "rows_count": self.rows_count,
            "size_in_bytes": self.size_in_bytes,
            "size_mb": self.get_size_mb(),
            "size_gb": self.get_size_gb(),
            "created_time": self.created_time.isoformat() if self.created_time else None,
            "last_modified_time": self.last_modified_time.isoformat() if self.last_modified_time else None,
            "comment": self.comment,
            "columns": [col.__dict__ for col in self.columns],
            "column_count": len(self.columns),
            "constraints": [cons.__dict__ for cons in self.constraints],
            "indexes": [idx.__dict__ for idx in self.indexes],
            "owner": self.owner,
            "location": self.location,
            "storage_format": self.storage_format,
            "properties": dict(self.properties),
            "tags": list(self.tags),
            "last_analyzed": self.last_analyzed.isoformat() if self.last_analyzed else None,
            "is_partitioned": self.is_partitioned,
            "partition_keys": self.partition_keys,
            "is_external": self.is_external_table(),
            "is_view": self.is_view(),
            "is_temporary": self.is_temporary(),
            "primary_key_columns": [col.name for col in self.get_primary_key_columns()],
            "foreign_key_columns": [col.name for col in self.get_foreign_key_columns()]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseTable":
        """Create BaseTable from dictionary."""
        table = cls(
            name=data["name"],
            schema=data["schema"],
            database=data["database"],
            type=TableType.from_string(data.get("type", "UNKNOWN")),
            rows_count=data.get("rows_count"),
            size_in_bytes=data.get("size_in_bytes"),
            comment=data.get("comment"),
            owner=data.get("owner"),
            location=data.get("location"),
            storage_format=data.get("storage_format"),
            properties=data.get("properties", {}),
            tags=set(data.get("tags", [])),
            is_partitioned=data.get("is_partitioned", False),
            partition_keys=data.get("partition_keys", [])
        )

        # Parse timestamps
        if data.get("created_time"):
            table.created_time = datetime.fromisoformat(data["created_time"])
        if data.get("last_modified_time"):
            table.last_modified_time = datetime.fromisoformat(data["last_modified_time"])
        if data.get("last_analyzed"):
            table.last_analyzed = datetime.fromisoformat(data["last_analyzed"])

        # Parse columns
        for col_data in data.get("columns", []):
            column = ColumnInfo(**col_data)
            table.add_column(column)

        # Parse constraints
        for cons_data in data.get("constraints", []):
            constraint = ConstraintInfo(**cons_data)
            table.add_constraint(constraint)

        # Parse indexes
        for idx_data in data.get("indexes", []):
            index = IndexInfo(**idx_data)
            table.add_index(index)

        return table

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (f"BaseTable(name={self.name}, schema={self.schema}, "
                f"database={self.database}, type={self.type.value}, "
                f"rows={self.rows_count}, columns={len(self.columns)})")


@dataclass
class BaseView:
    """
    Base view metadata with comprehensive information for profiling and lineage.
    
    This class provides a unified interface for view metadata across different
    SQL databases and data warehouses in the DataGuild system.
    """
    
    # Required fields
    name: str
    schema: str
    database: str
    
    # View characteristics
    view_definition: Optional[str] = None
    rows_count: Optional[int] = None
    size_in_bytes: Optional[int] = None
    
    # Metadata
    created_time: Optional[datetime] = None
    last_modified_time: Optional[datetime] = None
    comment: Optional[str] = None
    
    # Column information
    columns: List[ColumnInfo] = field(default_factory=list)
    
    # Additional properties
    owner: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    # Processing metadata
    last_analyzed: Optional[datetime] = None
    is_materialized: bool = False
    is_secure: bool = False
    
    def __post_init__(self):
        """Validate view information after initialization."""
        if not self.name:
            raise ValueError("View name is required")
        if not self.schema:
            raise ValueError("Schema name is required")
        if not self.database:
            raise ValueError("Database name is required")
    
    def get_full_name(self) -> str:
        """Get fully qualified view name."""
        return f"{self.database}.{self.schema}.{self.name}"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (f"BaseView(name={self.name}, schema={self.schema}, "
                f"database={self.database}, rows={self.rows_count}, "
                f"columns={len(self.columns)})")


@dataclass
class DatabaseSchema:
    """Database schema metadata."""
    name: str
    database: str
    tables: List[BaseTable] = field(default_factory=list)
    comment: Optional[str] = None
    owner: Optional[str] = None
    created_time: Optional[datetime] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def get_table_by_name(self, table_name: str) -> Optional[BaseTable]:
        """Get table by name."""
        for table in self.tables:
            if table.name.lower() == table_name.lower():
                return table
        return None

    def add_table(self, table: BaseTable) -> None:
        """Add table to schema."""
        if table.schema != self.name:
            raise ValueError(f"Table schema {table.schema} doesn't match schema name {self.name}")

        existing = self.get_table_by_name(table.name)
        if existing:
            logger.warning(f"Table {table.name} already exists in schema {self.name}")
            return

        self.tables.append(table)

    def get_fully_qualified_name(self) -> str:
        """Get fully qualified schema name."""
        return f"{self.database}.{self.name}"


@dataclass
class Database:
    """Database metadata."""
    name: str
    schemas: List[DatabaseSchema] = field(default_factory=list)
    comment: Optional[str] = None
    owner: Optional[str] = None
    created_time: Optional[datetime] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def get_schema_by_name(self, schema_name: str) -> Optional[DatabaseSchema]:
        """Get schema by name."""
        for schema in self.schemas:
            if schema.name.lower() == schema_name.lower():
                return schema
        return None

    def add_schema(self, schema: DatabaseSchema) -> None:
        """Add schema to database."""
        if schema.database != self.name:
            raise ValueError(f"Schema database {schema.database} doesn't match database name {self.name}")

        existing = self.get_schema_by_name(schema.name)
        if existing:
            logger.warning(f"Schema {schema.name} already exists in database {self.name}")
            return

        self.schemas.append(schema)


# Export all classes
__all__ = [
    'TableType',
    'ColumnInfo',
    'ConstraintInfo',
    'IndexInfo',
    'BaseTable',
    'BaseView',
    'DatabaseSchema',
    'Database'
]
