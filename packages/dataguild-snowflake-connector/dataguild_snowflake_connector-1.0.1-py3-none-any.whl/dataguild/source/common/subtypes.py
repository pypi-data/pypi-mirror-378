"""
DataGuild Dataset Subtypes

Comprehensive enumeration of dataset subtypes across different data platforms
to enable precise classification and handling of various data object types.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class DatasetSubTypes(Enum):
    """
    Enumeration of dataset subtypes supported across DataGuild connectors.

    This classification system enables:
    - Precise object type identification
    - Platform-specific handling logic
    - UI rendering customization
    - Governance policy application
    - Metadata processing optimization
    """

    # Generic table types
    TABLE = "table"
    VIEW = "view"
    MATERIALIZED_VIEW = "materialized_view"
    EXTERNAL_TABLE = "external_table"

    # Snowflake-specific types
    DYNAMIC_TABLE = "dynamic_table"
    ICEBERG_TABLE = "iceberg_table"
    HYBRID_TABLE = "hybrid_table"
    SNOWFLAKE_STREAM = "snowflake_stream"

    # BigQuery-specific types
    BIGQUERY_TABLE = "bigquery_table"
    BIGQUERY_VIEW = "bigquery_view"
    BIGQUERY_MATERIALIZED_VIEW = "bigquery_materialized_view"
    BIGQUERY_EXTERNAL_TABLE = "bigquery_external_table"
    BIGQUERY_SNAPSHOT = "bigquery_snapshot"

    # Databricks-specific types
    DATABRICKS_TABLE = "databricks_table"
    DATABRICKS_VIEW = "databricks_view"
    DELTA_TABLE = "delta_table"

    # Redshift-specific types
    REDSHIFT_TABLE = "redshift_table"
    REDSHIFT_VIEW = "redshift_view"
    REDSHIFT_EXTERNAL_TABLE = "redshift_external_table"
    REDSHIFT_MATERIALIZED_VIEW = "redshift_materialized_view"

    # PostgreSQL-specific types
    POSTGRES_TABLE = "postgres_table"
    POSTGRES_VIEW = "postgres_view"
    POSTGRES_MATERIALIZED_VIEW = "postgres_materialized_view"
    POSTGRES_FOREIGN_TABLE = "postgres_foreign_table"

    # MySQL-specific types
    MYSQL_TABLE = "mysql_table"
    MYSQL_VIEW = "mysql_view"

    # Oracle-specific types
    ORACLE_TABLE = "oracle_table"
    ORACLE_VIEW = "oracle_view"
    ORACLE_MATERIALIZED_VIEW = "oracle_materialized_view"

    # File-based types
    PARQUET_FILE = "parquet_file"
    CSV_FILE = "csv_file"
    JSON_FILE = "json_file"
    AVRO_FILE = "avro_file"
    ORC_FILE = "orc_file"

    # Cloud storage types
    S3_OBJECT = "s3_object"
    GCS_OBJECT = "gcs_object"
    AZURE_BLOB = "azure_blob"

    # Streaming types
    KAFKA_TOPIC = "kafka_topic"
    KINESIS_STREAM = "kinesis_stream"
    PUBSUB_TOPIC = "pubsub_topic"

    # NoSQL types
    MONGODB_COLLECTION = "mongodb_collection"
    CASSANDRA_TABLE = "cassandra_table"
    DYNAMODB_TABLE = "dynamodb_table"
    HBASE_TABLE = "hbase_table"

    # Time-series types
    INFLUXDB_MEASUREMENT = "influxdb_measurement"
    PROMETHEUS_METRIC = "prometheus_metric"

    # Graph database types (Neo4j support removed)

    # Search engine types
    ELASTICSEARCH_INDEX = "elasticsearch_index"
    SOLR_COLLECTION = "solr_collection"

    # API types
    REST_API_ENDPOINT = "rest_api_endpoint"
    GRAPHQL_SCHEMA = "graphql_schema"

    # Unknown or generic types
    UNKNOWN = "unknown"
    GENERIC_DATASET = "generic_dataset"

    @classmethod
    def get_snowflake_types(cls) -> List['DatasetSubTypes']:
        """Get all Snowflake-specific dataset subtypes."""
        return [
            cls.TABLE,
            cls.VIEW,
            cls.MATERIALIZED_VIEW,
            cls.EXTERNAL_TABLE,
            cls.DYNAMIC_TABLE,
            cls.ICEBERG_TABLE,
            cls.HYBRID_TABLE,
            cls.SNOWFLAKE_STREAM
        ]

    @classmethod
    def get_table_like_types(cls) -> List['DatasetSubTypes']:
        """Get all subtypes that are table-like (contain structured data)."""
        return [
            cls.TABLE,
            cls.EXTERNAL_TABLE,
            cls.DYNAMIC_TABLE,
            cls.ICEBERG_TABLE,
            cls.HYBRID_TABLE,
            cls.BIGQUERY_TABLE,
            cls.DATABRICKS_TABLE,
            cls.DELTA_TABLE,
            cls.REDSHIFT_TABLE,
            cls.POSTGRES_TABLE,
            cls.MYSQL_TABLE,
            cls.ORACLE_TABLE,
        ]

    @classmethod
    def get_view_like_types(cls) -> List['DatasetSubTypes']:
        """Get all subtypes that are view-like (virtual datasets)."""
        return [
            cls.VIEW,
            cls.MATERIALIZED_VIEW,
            cls.BIGQUERY_VIEW,
            cls.BIGQUERY_MATERIALIZED_VIEW,
            cls.DATABRICKS_VIEW,
            cls.REDSHIFT_VIEW,
            cls.REDSHIFT_MATERIALIZED_VIEW,
            cls.POSTGRES_VIEW,
            cls.POSTGRES_MATERIALIZED_VIEW,
            cls.MYSQL_VIEW,
            cls.ORACLE_VIEW,
            cls.ORACLE_MATERIALIZED_VIEW,
        ]

    @classmethod
    def get_streaming_types(cls) -> List['DatasetSubTypes']:
        """Get all subtypes that represent streaming data sources."""
        return [
            cls.SNOWFLAKE_STREAM,
            cls.KAFKA_TOPIC,
            cls.KINESIS_STREAM,
            cls.PUBSUB_TOPIC,
        ]

    @classmethod
    def get_file_types(cls) -> List['DatasetSubTypes']:
        """Get all subtypes that represent file-based datasets."""
        return [
            cls.PARQUET_FILE,
            cls.CSV_FILE,
            cls.JSON_FILE,
            cls.AVRO_FILE,
            cls.ORC_FILE,
        ]

    def is_table_like(self) -> bool:
        """Check if this subtype represents a table-like object."""
        return self in self.get_table_like_types()

    def is_view_like(self) -> bool:
        """Check if this subtype represents a view-like object."""
        return self in self.get_view_like_types()

    def is_streaming(self) -> bool:
        """Check if this subtype represents a streaming data source."""
        return self in self.get_streaming_types()

    def is_file_based(self) -> bool:
        """Check if this subtype represents a file-based dataset."""
        return self in self.get_file_types()

    def get_platform(self) -> Optional[str]:
        """Get the platform name for this subtype."""
        platform_mapping = {
            # Snowflake
            self.DYNAMIC_TABLE: "snowflake",
            self.ICEBERG_TABLE: "snowflake",
            self.HYBRID_TABLE: "snowflake",
            self.SNOWFLAKE_STREAM: "snowflake",

            # BigQuery
            self.BIGQUERY_TABLE: "bigquery",
            self.BIGQUERY_VIEW: "bigquery",
            self.BIGQUERY_MATERIALIZED_VIEW: "bigquery",
            self.BIGQUERY_EXTERNAL_TABLE: "bigquery",
            self.BIGQUERY_SNAPSHOT: "bigquery",

            # Databricks
            self.DATABRICKS_TABLE: "databricks",
            self.DATABRICKS_VIEW: "databricks",
            self.DELTA_TABLE: "databricks",

            # Redshift
            self.REDSHIFT_TABLE: "redshift",
            self.REDSHIFT_VIEW: "redshift",
            self.REDSHIFT_EXTERNAL_TABLE: "redshift",
            self.REDSHIFT_MATERIALIZED_VIEW: "redshift",

            # PostgreSQL
            self.POSTGRES_TABLE: "postgres",
            self.POSTGRES_VIEW: "postgres",
            self.POSTGRES_MATERIALIZED_VIEW: "postgres",
            self.POSTGRES_FOREIGN_TABLE: "postgres",

            # MySQL
            self.MYSQL_TABLE: "mysql",
            self.MYSQL_VIEW: "mysql",

            # Oracle
            self.ORACLE_TABLE: "oracle",
            self.ORACLE_VIEW: "oracle",
            self.ORACLE_MATERIALIZED_VIEW: "oracle",
        }

        return platform_mapping.get(self)

    def supports_columns(self) -> bool:
        """Check if this subtype supports column-level metadata."""
        # Most structured data types support columns
        non_column_types = {
            self.S3_OBJECT,
            self.GCS_OBJECT,
            self.AZURE_BLOB,
            self.REST_API_ENDPOINT,
            self.GRAPHQL_SCHEMA,
            self.UNKNOWN
        }
        return self not in non_column_types

    def supports_lineage(self) -> bool:
        """Check if this subtype supports lineage tracking."""
        # Most data processing objects support lineage
        non_lineage_types = {
            self.REST_API_ENDPOINT,
            self.GRAPHQL_SCHEMA,
            self.UNKNOWN
        }
        return self not in non_lineage_types

    def __str__(self) -> str:
        """String representation using the enum value."""
        return self.value

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"DatasetSubTypes.{self.name}('{self.value}')"


@dataclass
class SourceCapabilityModifier:
    """
    Represents capability modifiers for DataGuild ingestion sources.

    This class encapsulates boolean flags that modify or extend the base
    capabilities of a data source, enabling fine-grained control over
    ingestion behavior and feature availability.
    """

    # Core ingestion capabilities
    supports_deletion_detection: bool = False
    supports_incremental_extraction: bool = False
    supports_metadata_changes: bool = False
    supports_stateful_ingestion: bool = False

    # Advanced feature capabilities
    supports_column_lineage: bool = False
    supports_table_lineage: bool = False
    supports_usage_statistics: bool = False
    supports_profiling: bool = False
    supports_data_quality: bool = False

    # Performance and optimization
    supports_parallel_processing: bool = False
    supports_batch_processing: bool = False
    supports_streaming_ingestion: bool = False
    supports_caching: bool = False

    # Platform-specific features
    supports_tags: bool = False
    supports_glossary_terms: bool = False
    supports_custom_properties: bool = False
    supports_ownership: bool = False
    supports_domains: bool = False

    # Security and compliance
    supports_classification: bool = False
    supports_encryption_metadata: bool = False
    supports_access_control: bool = False
    supports_audit_logs: bool = False

    # Data quality and monitoring
    supports_assertions: bool = False
    supports_tests: bool = False
    supports_monitoring: bool = False
    supports_alerts: bool = False

    # Schema evolution and management
    supports_schema_evolution: bool = False
    supports_backward_compatibility: bool = False
    supports_schema_validation: bool = False

    def __post_init__(self):
        """Validate capability combinations and log configuration."""
        self._validate_capability_combinations()
        logger.debug(f"Initialized SourceCapabilityModifier with {self.get_enabled_count()} enabled capabilities")

    def _validate_capability_combinations(self) -> None:
        """Validate logical capability combinations."""
        # Column lineage requires table lineage
        if self.supports_column_lineage and not self.supports_table_lineage:
            logger.warning("Column lineage support requires table lineage support")
            self.supports_table_lineage = True

        # Data quality features often require profiling
        if self.supports_data_quality and not self.supports_profiling:
            logger.info("Data quality support typically benefits from profiling capabilities")

        # Stateful ingestion requires deletion detection for completeness
        if self.supports_stateful_ingestion and not self.supports_deletion_detection:
            logger.info("Stateful ingestion works best with deletion detection enabled")

    def get_enabled_capabilities(self) -> List[str]:
        """Get list of enabled capability names."""
        enabled = []
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                if attr_name.startswith('supports_') and getattr(self, attr_name):
                    enabled.append(attr_name)
        return enabled

    def get_enabled_count(self) -> int:
        """Get count of enabled capabilities."""
        return len(self.get_enabled_capabilities())

    def get_capability_groups(self) -> Dict[str, List[str]]:
        """Get capabilities organized by functional groups."""
        groups = {
            "core_ingestion": [
                "supports_deletion_detection",
                "supports_incremental_extraction",
                "supports_metadata_changes",
                "supports_stateful_ingestion"
            ],
            "lineage_and_usage": [
                "supports_column_lineage",
                "supports_table_lineage",
                "supports_usage_statistics"
            ],
            "data_quality": [
                "supports_profiling",
                "supports_data_quality",
                "supports_assertions",
                "supports_tests",
                "supports_monitoring",
                "supports_alerts"
            ],
            "governance": [
                "supports_tags",
                "supports_glossary_terms",
                "supports_custom_properties",
                "supports_ownership",
                "supports_domains",
                "supports_classification"
            ],
            "performance": [
                "supports_parallel_processing",
                "supports_batch_processing",
                "supports_streaming_ingestion",
                "supports_caching"
            ],
            "security": [
                "supports_encryption_metadata",
                "supports_access_control",
                "supports_audit_logs"
            ],
            "schema_management": [
                "supports_schema_evolution",
                "supports_backward_compatibility",
                "supports_schema_validation"
            ]
        }

        # Filter to only include enabled capabilities
        enabled_groups = {}
        for group_name, capabilities in groups.items():
            enabled_in_group = [cap for cap in capabilities if getattr(self, cap, False)]
            if enabled_in_group:
                enabled_groups[group_name] = enabled_in_group

        return enabled_groups

    def enable_capability(self, capability_name: str) -> bool:
        """Enable a specific capability."""
        if hasattr(self, capability_name) and capability_name.startswith('supports_'):
            setattr(self, capability_name, True)
            logger.debug(f"Enabled capability: {capability_name}")
            return True
        else:
            logger.warning(f"Unknown capability: {capability_name}")
            return False

    def disable_capability(self, capability_name: str) -> bool:
        """Disable a specific capability."""
        if hasattr(self, capability_name) and capability_name.startswith('supports_'):
            setattr(self, capability_name, False)
            logger.debug(f"Disabled capability: {capability_name}")
            return True
        else:
            logger.warning(f"Unknown capability: {capability_name}")
            return False

    def enable_group(self, group_name: str) -> int:
        """Enable all capabilities in a functional group."""
        groups = {
            "basic": ["supports_metadata_changes", "supports_tags"],
            "lineage": ["supports_table_lineage", "supports_column_lineage"],
            "advanced": ["supports_usage_statistics", "supports_profiling", "supports_data_quality"],
            "governance": ["supports_tags", "supports_glossary_terms", "supports_ownership"],
            "performance": ["supports_parallel_processing", "supports_caching"],
            "all": [attr for attr in dir(self)
                   if attr.startswith('supports_') and not callable(getattr(self, attr))]
        }

        if group_name not in groups:
            logger.warning(f"Unknown capability group: {group_name}")
            return 0

        enabled_count = 0
        for capability in groups[group_name]:
            if self.enable_capability(capability):
                enabled_count += 1

        logger.info(f"Enabled {enabled_count} capabilities in group '{group_name}'")
        return enabled_count

    def copy(self) -> 'SourceCapabilityModifier':
        """Create a deep copy of this modifier."""
        return SourceCapabilityModifier(**self.to_dict())

    def merge(self, other: 'SourceCapabilityModifier') -> 'SourceCapabilityModifier':
        """Merge with another modifier (OR operation)."""
        merged_dict = {}

        for attr_name in dir(self):
            if attr_name.startswith('supports_') and not callable(getattr(self, attr_name)):
                self_value = getattr(self, attr_name)
                other_value = getattr(other, attr_name, False)
                merged_dict[attr_name] = self_value or other_value

        return SourceCapabilityModifier(**merged_dict)

    def intersect(self, other: 'SourceCapabilityModifier') -> 'SourceCapabilityModifier':
        """Intersect with another modifier (AND operation)."""
        intersected_dict = {}

        for attr_name in dir(self):
            if attr_name.startswith('supports_') and not callable(getattr(self, attr_name)):
                self_value = getattr(self, attr_name)
                other_value = getattr(other, attr_name, False)
                intersected_dict[attr_name] = self_value and other_value

        return SourceCapabilityModifier(**intersected_dict)

    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary representation."""
        result = {}
        for attr_name in dir(self):
            if attr_name.startswith('supports_') and not callable(getattr(self, attr_name)):
                result[attr_name] = getattr(self, attr_name)
        return result

    def from_dict(self, capability_dict: Dict[str, bool]) -> 'SourceCapabilityModifier':
        """Create modifier from dictionary."""
        for capability, enabled in capability_dict.items():
            if hasattr(self, capability):
                setattr(self, capability, enabled)
        return self

    def to_summary_string(self) -> str:
        """Get a human-readable summary of enabled capabilities."""
        enabled = self.get_enabled_capabilities()
        if not enabled:
            return "No capabilities enabled"

        groups = self.get_capability_groups()
        group_summaries = []

        for group_name, capabilities in groups.items():
            count = len(capabilities)
            group_summaries.append(f"{group_name}: {count}")

        return f"Enabled: {len(enabled)} total ({', '.join(group_summaries)})"

    def __str__(self) -> str:
        """String representation."""
        return f"SourceCapabilityModifier({self.get_enabled_count()} capabilities enabled)"

    def __repr__(self) -> str:
        """Detailed string representation."""
        enabled = self.get_enabled_capabilities()
        return f"SourceCapabilityModifier(enabled={enabled})"


# Factory functions for common capability configurations
def create_basic_capabilities() -> SourceCapabilityModifier:
    """Create modifier with basic ingestion capabilities."""
    return SourceCapabilityModifier(
        supports_metadata_changes=True,
        supports_tags=True,
        supports_custom_properties=True
    )


def create_advanced_capabilities() -> SourceCapabilityModifier:
    """Create modifier with advanced ingestion capabilities."""
    return SourceCapabilityModifier(
        supports_deletion_detection=True,
        supports_incremental_extraction=True,
        supports_metadata_changes=True,
        supports_stateful_ingestion=True,
        supports_table_lineage=True,
        supports_column_lineage=True,
        supports_usage_statistics=True,
        supports_profiling=True,
        supports_tags=True,
        supports_glossary_terms=True,
        supports_custom_properties=True,
        supports_ownership=True,
        supports_parallel_processing=True,
        supports_caching=True
    )


def create_snowflake_capabilities() -> SourceCapabilityModifier:
    """Create modifier with Snowflake-specific capabilities."""
    return SourceCapabilityModifier(
        supports_deletion_detection=True,
        supports_incremental_extraction=True,
        supports_metadata_changes=True,
        supports_stateful_ingestion=True,
        supports_column_lineage=True,
        supports_table_lineage=True,
        supports_usage_statistics=True,
        supports_profiling=True,
        supports_data_quality=True,
        supports_tags=True,
        supports_glossary_terms=True,
        supports_custom_properties=True,
        supports_ownership=True,
        supports_domains=True,
        supports_classification=True,
        supports_parallel_processing=True,
        supports_batch_processing=True,
        supports_caching=True,
        supports_assertions=True,
        supports_monitoring=True,
        supports_schema_evolution=True
    )


def create_bigquery_capabilities() -> SourceCapabilityModifier:
    """Create modifier with BigQuery-specific capabilities."""
    return SourceCapabilityModifier(
        supports_deletion_detection=True,
        supports_incremental_extraction=True,
        supports_metadata_changes=True,
        supports_stateful_ingestion=True,
        supports_table_lineage=True,
        supports_usage_statistics=True,
        supports_profiling=True,
        supports_tags=True,
        supports_custom_properties=True,
        supports_parallel_processing=True,
        supports_caching=True,
        supports_schema_evolution=True
    )


def create_file_based_capabilities() -> SourceCapabilityModifier:
    """Create modifier for file-based sources."""
    return SourceCapabilityModifier(
        supports_metadata_changes=True,
        supports_custom_properties=True,
        supports_tags=True,
        supports_profiling=True,
        supports_schema_validation=True,
        supports_parallel_processing=True
    )


# ✅ FIXED: Backward compatibility aliases
# Instead of enum inheritance (which Python doesn't allow), use simple alias
DatasetSubType = DatasetSubTypes  # Simple alias for backward compatibility


# Helper functions
def get_subtype_from_string(subtype_str: str) -> Optional[DatasetSubTypes]:
    """Get DatasetSubTypes enum from string value."""
    try:
        return DatasetSubTypes(subtype_str.lower())
    except ValueError:
        return None


def is_supported_subtype(subtype_str: str) -> bool:
    """Check if a string represents a supported dataset subtype."""
    return get_subtype_from_string(subtype_str) is not None


"""
DataGuild Advanced Dataset Container SubTypes

Comprehensive type system for dataset containers across all supported
data platforms with hierarchical relationships and metadata capabilities.
"""


class DatasetContainerSubTypes(Enum):
    """
    Comprehensive enumeration of dataset container subtypes across
    all supported data platforms in the DataGuild ecosystem.
    """

    # Core container types
    DATABASE = "database"
    SCHEMA = "schema"
    CATALOG = "catalog"
    NAMESPACE = "namespace"
    PROJECT = "project"

    # Cloud-specific containers
    # AWS
    S3_BUCKET = "s3_bucket"
    GLUE_CATALOG = "glue_catalog"
    GLUE_DATABASE = "glue_database"
    REDSHIFT_DATABASE = "redshift_database"
    REDSHIFT_SCHEMA = "redshift_schema"

    # Google Cloud
    BIGQUERY_PROJECT = "bigquery_project"
    BIGQUERY_DATASET = "bigquery_dataset"
    GCS_BUCKET = "gcs_bucket"

    # Azure
    SYNAPSE_WORKSPACE = "synapse_workspace"
    SYNAPSE_DATABASE = "synapse_database"
    SYNAPSE_SCHEMA = "synapse_schema"
    ADLS_ACCOUNT = "adls_account"
    ADLS_CONTAINER = "adls_container"

    # Snowflake-specific
    SNOWFLAKE_ACCOUNT = "snowflake_account"
    SNOWFLAKE_DATABASE = "snowflake_database"
    SNOWFLAKE_SCHEMA = "snowflake_schema"

    # Databricks
    DATABRICKS_WORKSPACE = "databricks_workspace"
    DATABRICKS_CATALOG = "databricks_catalog"
    DATABRICKS_DATABASE = "databricks_database"
    DATABRICKS_SCHEMA = "databricks_schema"

    # Traditional databases
    POSTGRES_DATABASE = "postgres_database"
    POSTGRES_SCHEMA = "postgres_schema"
    MYSQL_DATABASE = "mysql_database"
    ORACLE_DATABASE = "oracle_database"
    ORACLE_SCHEMA = "oracle_schema"

    # NoSQL
    MONGODB_DATABASE = "mongodb_database"
    MONGODB_COLLECTION_GROUP = "mongodb_collection_group"
    CASSANDRA_KEYSPACE = "cassandra_keyspace"
    DYNAMODB_TABLE_GROUP = "dynamodb_table_group"

    # Streaming
    KAFKA_CLUSTER = "kafka_cluster"
    KAFKA_TOPIC_GROUP = "kafka_topic_group"
    KINESIS_STREAM_GROUP = "kinesis_stream_group"
    PUBSUB_PROJECT = "pubsub_project"
    PUBSUB_TOPIC_GROUP = "pubsub_topic_group"

    # File systems
    HDFS_DIRECTORY = "hdfs_directory"
    NFS_DIRECTORY = "nfs_directory"

    # Data lakes
    DELTA_LAKE_CATALOG = "delta_lake_catalog"
    DELTA_LAKE_SCHEMA = "delta_lake_schema"
    ICEBERG_CATALOG = "iceberg_catalog"
    ICEBERG_NAMESPACE = "iceberg_namespace"

    # Business Intelligence
    TABLEAU_WORKBOOK = "tableau_workbook"
    TABLEAU_PROJECT = "tableau_project"
    POWERBI_WORKSPACE = "powerbi_workspace"
    POWERBI_DATASET_GROUP = "powerbi_dataset_group"

    # Generic containers
    FOLDER = "folder"
    DIRECTORY = "directory"
    COLLECTION = "collection"

    def get_platform(self) -> Optional[str]:
        """Get the platform associated with this container type."""
        platform_mapping = {
            # Snowflake
            self.SNOWFLAKE_ACCOUNT: "snowflake",
            self.SNOWFLAKE_DATABASE: "snowflake",
            self.SNOWFLAKE_SCHEMA: "snowflake",

            # BigQuery
            self.BIGQUERY_PROJECT: "bigquery",
            self.BIGQUERY_DATASET: "bigquery",

            # AWS
            self.S3_BUCKET: "s3",
            self.GLUE_CATALOG: "glue",
            self.GLUE_DATABASE: "glue",
            self.REDSHIFT_DATABASE: "redshift",
            self.REDSHIFT_SCHEMA: "redshift",

            # Databricks
            self.DATABRICKS_WORKSPACE: "databricks",
            self.DATABRICKS_CATALOG: "databricks",
            self.DATABRICKS_DATABASE: "databricks",
            self.DATABRICKS_SCHEMA: "databricks",

            # Traditional databases
            self.POSTGRES_DATABASE: "postgres",
            self.POSTGRES_SCHEMA: "postgres",
            self.MYSQL_DATABASE: "mysql",
            self.ORACLE_DATABASE: "oracle",
            self.ORACLE_SCHEMA: "oracle",
        }

        return platform_mapping.get(self)

    def get_hierarchy_level(self) -> int:
        """Get the hierarchy level (0 = top level, higher = deeper)."""
        level_mapping = {
            # Level 0 - Top level
            self.SNOWFLAKE_ACCOUNT: 0,
            self.BIGQUERY_PROJECT: 0,
            self.DATABRICKS_WORKSPACE: 0,
            self.S3_BUCKET: 0,
            self.GCS_BUCKET: 0,

            # Level 1 - Database/Catalog level
            self.DATABASE: 1,
            self.CATALOG: 1,
            self.SNOWFLAKE_DATABASE: 1,
            self.BIGQUERY_DATASET: 1,
            self.DATABRICKS_CATALOG: 1,
            self.POSTGRES_DATABASE: 1,
            self.MYSQL_DATABASE: 1,

            # Level 2 - Schema level
            self.SCHEMA: 2,
            self.SNOWFLAKE_SCHEMA: 2,
            self.DATABRICKS_SCHEMA: 2,
            self.POSTGRES_SCHEMA: 2,
            self.ORACLE_SCHEMA: 2,

            # Level 3 - Collection level
            self.COLLECTION: 3,
            self.FOLDER: 3,
            self.DIRECTORY: 3,
        }

        return level_mapping.get(self, 1)  # Default to level 1

    def get_child_types(self) -> Set['DatasetContainerSubTypes']:
        """Get valid child container types."""
        child_mapping = {
            # Snowflake hierarchy
            self.SNOWFLAKE_ACCOUNT: {self.SNOWFLAKE_DATABASE},
            self.SNOWFLAKE_DATABASE: {self.SNOWFLAKE_SCHEMA},
            self.SNOWFLAKE_SCHEMA: set(),  # Contains tables, not containers

            # BigQuery hierarchy
            self.BIGQUERY_PROJECT: {self.BIGQUERY_DATASET},
            self.BIGQUERY_DATASET: set(),  # Contains tables

            # Databricks hierarchy
            self.DATABRICKS_WORKSPACE: {self.DATABRICKS_CATALOG},
            self.DATABRICKS_CATALOG: {self.DATABRICKS_DATABASE},
            self.DATABRICKS_DATABASE: {self.DATABRICKS_SCHEMA},
            self.DATABRICKS_SCHEMA: set(),  # Contains tables

            # Generic hierarchy
            self.DATABASE: {self.SCHEMA},
            self.SCHEMA: set(),
            self.CATALOG: {self.DATABASE, self.SCHEMA},
        }

        return child_mapping.get(self, set())

    def can_contain(self, child_type: 'DatasetContainerSubTypes') -> bool:
        """Check if this container type can contain the specified child type."""
        return child_type in self.get_child_types()

    def is_leaf_container(self) -> bool:
        """Check if this is a leaf container (contains datasets, not other containers)."""
        return len(self.get_child_types()) == 0


@dataclass
class ContainerHierarchy:
    """Represents a container hierarchy path."""
    levels: List[Tuple[str, DatasetContainerSubTypes]]  # (name, type) pairs

    def __post_init__(self):
        """Validate hierarchy consistency."""
        if not self._validate_hierarchy():
            raise ValueError(f"Invalid container hierarchy: {self.levels}")

    def _validate_hierarchy(self) -> bool:
        """Validate that the hierarchy is consistent."""
        if len(self.levels) < 2:
            return True

        for i in range(len(self.levels) - 1):
            parent_type = self.levels[i][1]
            child_type = self.levels[i + 1][1]

            if not parent_type.can_contain(child_type):
                logger.warning(f"Invalid hierarchy: {parent_type.value} cannot contain {child_type.value}")
                return False

        return True

    def get_parent_path(self) -> Optional['ContainerHierarchy']:
        """Get parent container hierarchy."""
        if len(self.levels) <= 1:
            return None

        return ContainerHierarchy(levels=self.levels[:-1])

    def get_full_path(self, separator: str = ".") -> str:
        """Get full hierarchical path as string."""
        return separator.join(name for name, _ in self.levels)

    def get_urn_components(self) -> Dict[str, str]:
        """Get URN components for container hierarchy."""
        if not self.levels:
            return {}

        # Use the most specific (last) level as primary
        primary_name, primary_type = self.levels[-1]
        platform = primary_type.get_platform()

        return {
            "platform": platform or "generic",
            "name": self.get_full_path(),
            "primary_type": primary_type.value,
            "hierarchy_depth": len(self.levels)
        }


class DatasetContainerTypes:
    """
    Advanced factory class for creating and managing dataset containers
    with proper hierarchy validation and URN generation.
    """

    @staticmethod
    def create_hierarchy(
            platform: str,
            path_components: List[Tuple[str, str]]  # (name, container_type) pairs
    ) -> ContainerHierarchy:
        """
        Create a validated container hierarchy for a platform.

        Args:
            platform: Platform name (e.g., 'snowflake', 'bigquery')
            path_components: List of (name, container_type) tuples

        Returns:
            Validated ContainerHierarchy
        """
        # Convert string types to enums
        typed_components = []
        for name, type_str in path_components:
            try:
                container_type = DatasetContainerSubTypes(type_str.lower())
                typed_components.append((name, container_type))
            except ValueError:
                logger.warning(f"Unknown container type: {type_str}")
                # Use generic type as fallback
                if "database" in type_str.lower():
                    container_type = DatasetContainerSubTypes.DATABASE
                elif "schema" in type_str.lower():
                    container_type = DatasetContainerSubTypes.SCHEMA
                else:
                    container_type = DatasetContainerSubTypes.COLLECTION
                typed_components.append((name, container_type))

        return ContainerHierarchy(levels=typed_components)

    @staticmethod
    def get_platform_hierarchy_template(platform: str) -> List[DatasetContainerSubTypes]:
        """Get standard hierarchy template for a platform."""
        templates = {
            "snowflake": [
                DatasetContainerSubTypes.SNOWFLAKE_ACCOUNT,
                DatasetContainerSubTypes.SNOWFLAKE_DATABASE,
                DatasetContainerSubTypes.SNOWFLAKE_SCHEMA
            ],
            "bigquery": [
                DatasetContainerSubTypes.BIGQUERY_PROJECT,
                DatasetContainerSubTypes.BIGQUERY_DATASET
            ],
            "databricks": [
                DatasetContainerSubTypes.DATABRICKS_WORKSPACE,
                DatasetContainerSubTypes.DATABRICKS_CATALOG,
                DatasetContainerSubTypes.DATABRICKS_DATABASE,
                DatasetContainerSubTypes.DATABRICKS_SCHEMA
            ],
            "postgres": [
                DatasetContainerSubTypes.POSTGRES_DATABASE,
                DatasetContainerSubTypes.POSTGRES_SCHEMA
            ],
            "s3": [
                DatasetContainerSubTypes.S3_BUCKET
            ]
        }

        return templates.get(platform.lower(), [
            DatasetContainerSubTypes.DATABASE,
            DatasetContainerSubTypes.SCHEMA
        ])

    @staticmethod
    def generate_database_container(
            database_name: str,
            database_urn: str,
            platform_urn: str,
            tags: Optional[List[str]] = None,
            description: Optional[str] = None,
            created_timestamp: Optional[float] = None,
            updated_timestamp: Optional[float] = None,
            platform_instance: Optional[str] = None,
            custom_properties: Optional[Dict[str, str]] = None
    ) -> List[Any]:
        """Generate database container workunit."""
        from dataguild.emitter.mcp import MetadataChangeProposalWrapper
        from dataguild.metadata.schemas import ContainerProperties, Status

        workunits = []

        # Status aspect
        status = Status(removed=False)
        workunits.append(
            MetadataChangeProposalWrapper(entityUrn=database_urn, aspect=status).as_workunit()
        )

        # Container properties
        properties = ContainerProperties(
            name=database_name,
            description=description,
            customProperties=custom_properties or {},
            created=int(created_timestamp * 1000) if created_timestamp else None,
            lastModified=int(updated_timestamp * 1000) if updated_timestamp else None
        )

        workunits.append(
            MetadataChangeProposalWrapper(entityUrn=database_urn, aspect=properties).as_workunit()
        )

        # Tags if provided
        if tags:
            from dataguild.metadata.schemas import GlobalTags, TagAssociation
            tag_associations = [TagAssociation(tag=tag) for tag in tags]
            global_tags = GlobalTags(tags=tag_associations)
            workunits.append(
                MetadataChangeProposalWrapper(entityUrn=database_urn, aspect=global_tags).as_workunit()
            )

        return workunits

    @staticmethod
    def generate_schema_container(
            schema_name: str,
            schema_urn: str,
            database_urn: str,
            platform_urn: str,
            tags: Optional[List[str]] = None,
            description: Optional[str] = None,
            created_timestamp: Optional[float] = None,
            updated_timestamp: Optional[float] = None,
            platform_instance: Optional[str] = None,
            custom_properties: Optional[Dict[str, str]] = None
    ) -> List[Any]:
        """Generate schema container workunit."""
        from dataguild.emitter.mcp import MetadataChangeProposalWrapper
        from dataguild.metadata.schemas import ContainerProperties, Status, Container

        workunits = []

        # Status aspect
        status = Status(removed=False)
        workunits.append(
            MetadataChangeProposalWrapper(entityUrn=schema_urn, aspect=status).as_workunit()
        )

        # Container properties
        properties = ContainerProperties(
            name=schema_name,
            description=description,
            customProperties=custom_properties or {},
            created=int(created_timestamp * 1000) if created_timestamp else None,
            lastModified=int(updated_timestamp * 1000) if updated_timestamp else None
        )

        workunits.append(
            MetadataChangeProposalWrapper(entityUrn=schema_urn, aspect=properties).as_workunit()
        )

        # Parent container relationship
        container = Container(container=database_urn)
        workunits.append(
            MetadataChangeProposalWrapper(entityUrn=schema_urn, aspect=container).as_workunit()
        )

        # Tags if provided
        if tags:
            from dataguild.metadata.schemas import GlobalTags, TagAssociation
            tag_associations = [TagAssociation(tag=tag) for tag in tags]
            global_tags = GlobalTags(tags=tag_associations)
            workunits.append(
                MetadataChangeProposalWrapper(entityUrn=schema_urn, aspect=global_tags).as_workunit()
            )

        return workunits

    @staticmethod
    def add_dataset_to_container(dataset_urn: str, container_urn: str) -> List[Any]:
        """Add dataset to container relationship."""
        from dataguild.emitter.mcp import MetadataChangeProposalWrapper
        from dataguild.metadata.schemas import Container

        container = Container(container=container_urn)
        return [MetadataChangeProposalWrapper(entityUrn=dataset_urn, aspect=container).as_workunit()]

    @staticmethod
    def validate_container_hierarchy(hierarchy: List[Tuple[str, DatasetContainerSubTypes]]) -> bool:
        """Validate a container hierarchy."""
        if len(hierarchy) < 2:
            return True

        for i in range(len(hierarchy) - 1):
            parent_type = hierarchy[i][1]
            child_type = hierarchy[i + 1][1]

            if not parent_type.can_contain(child_type):
                return False

        return True

    @staticmethod
    def get_container_stats() -> Dict[str, Any]:
        """Get statistics about available container types."""
        platform_counts = {}
        level_counts = {}

        for container_type in DatasetContainerSubTypes:
            # Count by platform
            platform = container_type.get_platform()
            if platform:
                platform_counts[platform] = platform_counts.get(platform, 0) + 1

            # Count by hierarchy level
            level = container_type.get_hierarchy_level()
            level_counts[f"level_{level}"] = level_counts.get(f"level_{level}", 0) + 1

        return {
            "total_container_types": len(DatasetContainerSubTypes),
            "platforms_supported": len(platform_counts),
            "platform_distribution": platform_counts,
            "hierarchy_level_distribution": level_counts,
            "leaf_containers": sum(1 for ct in DatasetContainerSubTypes if ct.is_leaf_container())
        }
