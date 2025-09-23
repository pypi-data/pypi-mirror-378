"""
Dataset metadata models for DataGuild.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from dataguild.emitter.mcp import MetadataAspect

logger = logging.getLogger(__name__)


# Enum definitions
class DatasetSubTypes(str, Enum):
    """Subtypes for datasets."""
    TABLE = "Table"
    VIEW = "View"
    MATERIALIZED_VIEW = "Materialized View"
    EXTERNAL_TABLE = "External Table"
    TEMPORARY_TABLE = "Temporary Table"
    STREAM = "Stream"
    TOPIC = "Topic"


class TimeWindowSize(str, Enum):
    """Time window granularities for usage statistics."""
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


@dataclass
class DatasetProperties:
    """Properties of a dataset including name, description, and custom metadata."""

    # ✅ All required fields first (no defaults)
    # No required fields in this case

    # ✅ All optional fields with defaults
    name: Optional[str] = None
    description: Optional[str] = None
    qualifiedName: Optional[str] = None
    customProperties: Dict[str, str] = field(default_factory=dict)
    externalUrl: Optional[str] = None
    origin: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created: Optional[datetime] = None
    lastModified: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "qualifiedName": self.qualifiedName,
            "customProperties": self.customProperties,
            "externalUrl": self.externalUrl,
            "origin": self.origin,
            "tags": self.tags,
            "created": self.created.isoformat() if self.created else None,
            "lastModified": self.lastModified.isoformat() if self.lastModified else None,
        }


@dataclass
class DatasetFieldUsageCounts:
    """Usage statistics for dataset fields."""

    # ✅ Required field first
    fieldPath: str

    # ✅ Optional fields with defaults
    count: int = 0

    def __post_init__(self):
        if not self.fieldPath:
            raise ValueError("fieldPath cannot be empty")
        if self.count < 0:
            raise ValueError("count must be non-negative")


@dataclass
class DatasetUserUsageCounts:
    """Usage statistics for dataset users."""

    # ✅ Required field first
    user: str

    # ✅ Optional fields with defaults
    count: int = 0
    userEmail: Optional[str] = None

    def __post_init__(self):
        if not self.user:
            raise ValueError("user cannot be empty")
        if self.count < 0:
            raise ValueError("count must be non-negative")


@dataclass
class DatasetUsageStatistics(MetadataAspect):
    """Comprehensive usage statistics for a dataset."""

    # ✅ Required fields first
    timestampMillis: int
    eventGranularity: TimeWindowSize

    # ✅ Optional fields with defaults
    totalSqlQueries: int = 0
    uniqueUserCount: int = 0
    userCounts: List[DatasetUserUsageCounts] = field(default_factory=list)
    fieldCounts: List[DatasetFieldUsageCounts] = field(default_factory=list)
    topSqlQueries: Optional[List[str]] = None

    def __post_init__(self):
        if self.timestampMillis <= 0:
            raise ValueError("timestampMillis must be positive")
    
    def validate(self) -> bool:
        """Validate the usage statistics data."""
        try:
            if self.timestampMillis <= 0:
                return False
            if self.totalSqlQueries < 0:
                return False
            if self.uniqueUserCount < 0:
                return False
            return True
        except Exception:
            return False
    
    @property
    def aspect_name(self) -> str:
        """Return the aspect name for this class."""
        return "datasetUsageStatistics"


@dataclass
class SchemaFieldDataType:
    """Data type information for schema fields."""

    # ✅ Required field first
    type_info: Union[str, Dict[str, Any]]  # Renamed from 'type' (Python keyword)


@dataclass
class SchemaField:
    """Schema field definition."""

    # ✅ FIXED: Required fields first (no defaults)
    fieldPath: str
    type_info: SchemaFieldDataType  # Renamed from 'type' to avoid keyword conflict

    # ✅ Optional fields with defaults come after
    nullable: bool = True
    description: Optional[str] = None
    nativeDataType: Optional[str] = None
    recursive: bool = False

    def __post_init__(self):
        if not self.fieldPath:
            raise ValueError("fieldPath cannot be empty")


@dataclass
class SchemaMetadata:
    """Schema metadata for datasets."""

    # ✅ Required fields first
    schemaName: str
    platform: str

    # ✅ Optional fields with defaults
    version: int = 0
    fields: List[SchemaField] = field(default_factory=list)
    primaryKeys: List[str] = field(default_factory=list)
    foreignKeys: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.schemaName:
            raise ValueError("schemaName cannot be empty")
        if not self.platform:
            raise ValueError("platform cannot be empty")


@dataclass
class DatasetDeprecation:
    """Dataset deprecation information."""

    # ✅ All fields have defaults
    deprecated: bool = False
    decommissionTime: Optional[int] = None
    note: Optional[str] = None


@dataclass
class EditableDatasetProperties:
    """Editable dataset properties."""

    # ✅ All fields have defaults
    created: Optional[datetime] = None
    lastModified: Optional[datetime] = None
    deleted: Optional[datetime] = None
    description: Optional[str] = None


@dataclass
class ViewProperties:
    """Properties specific to database views."""

    # ✅ All fields have defaults
    materialized: bool = False
    viewLogic: Optional[str] = None
    viewLanguage: str = "SQL"


@dataclass
class UpstreamLineage:
    """Upstream lineage information for datasets."""

    # ✅ All fields have defaults
    upstreams: List[Dict[str, Any]] = field(default_factory=list)


# Export all classes
__all__ = [
    'DatasetProperties',
    'DatasetFieldUsageCounts',
    'DatasetUserUsageCounts',
    'DatasetUsageStatistics',
    'DatasetSubTypes',
    'TimeWindowSize',
    'SchemaFieldDataType',
    'SchemaField',
    'SchemaMetadata',
    'DatasetDeprecation',
    'EditableDatasetProperties',
    'ViewProperties',
    'UpstreamLineage',
]
