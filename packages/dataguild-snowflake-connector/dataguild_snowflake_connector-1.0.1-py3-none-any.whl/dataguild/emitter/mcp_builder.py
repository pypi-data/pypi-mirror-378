"""
DataGuild Advanced Metadata Change Proposal Builder

Enterprise-grade utilities for building metadata change proposals with
comprehensive validation, optimization, and advanced features.
"""

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Set, Iterable
from dataclasses import dataclass, asdict
from enum import Enum

import logging

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Supported entity types in DataGuild."""
    DATASET = "dataset"
    DATA_PLATFORM = "dataPlatform"
    TAG = "tag"
    DOMAIN = "domain"
    SCHEMA_FIELD = "schemaField"
    CONTAINER = "container"
    CHART = "chart"
    DASHBOARD = "dashboard"
    DATA_JOB = "dataJob"
    DATA_FLOW = "dataFlow"


class PlatformType(Enum):
    """Supported data platforms."""
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    DATABRICKS = "databricks"
    S3 = "s3"
    POSTGRES = "postgres"
    MYSQL = "mysql"


class DatabaseKey:
    """
    Standardized database key generator for consistent identifier normalization.

    Provides a consistent way to generate database keys by normalizing
    database names to lowercase, alphanumeric identifiers.
    """

    def __init__(self, database_name: str):
        """
        Initialize DatabaseKey with validation.

        Args:
            database_name: Name of the database to normalize

        Raises:
            ValueError: If database_name is empty or None
        """
        if not database_name or not isinstance(database_name, str):
            raise ValueError("Database name must be a non-empty string")
        self.database_name = database_name

    def key(self) -> str:
        """
        Generate a standardized database key.

        Normalizes the database name by:
        - Converting to lowercase
        - Replacing non-alphanumeric characters with underscores
        - Removing leading/trailing underscores

        Returns:
            Normalized database key

        Raises:
            ValueError: If normalization results in empty key

        Examples:
            >>> DatabaseKey("MyDatabase1").key()
            'mydatabase1'
            >>> DatabaseKey("my-database@123").key()
            'my_database_123'
        """
        key = self.database_name.strip().lower()
        key = re.sub(r'[^a-z0-9]+', '_', key)
        key = key.strip('_')

        if not key:
            raise ValueError(f"Invalid database key for name: {self.database_name}")

        return key

    def __str__(self) -> str:
        """String representation returns the key."""
        return self.key()

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"DatabaseKey(database_name='{self.database_name}')"

    def __eq__(self, other) -> bool:
        """Check equality with another DatabaseKey."""
        if not isinstance(other, DatabaseKey):
            return False
        return self.key() == other.key()

    def __hash__(self) -> int:
        """Hash for using as dictionary key."""
        return hash(self.key())


class SchemaKey:
    """
    Standardized schema key generator for consistent qualified schema identifiers.

    Provides a consistent way to generate schema keys in the format
    'database_key.schema_key' where both parts are normalized.
    """

    def __init__(self, database_name: str, schema_name: str):
        """
        Initialize SchemaKey with validation.

        Args:
            database_name: Name of the database
            schema_name: Name of the schema

        Raises:
            ValueError: If database_name or schema_name is empty or None
        """
        if not database_name or not isinstance(database_name, str):
            raise ValueError("Database name must be a non-empty string")
        if not schema_name or not isinstance(schema_name, str):
            raise ValueError("Schema name must be a non-empty string")

        self.database_name = database_name
        self.schema_name = schema_name

    def key(self) -> str:
        """
        Generate a standardized schema key.

        Creates a qualified schema key in the format 'database_key.schema_key'
        where both parts are normalized using the same rules as DatabaseKey.

        Returns:
            Normalized schema key in format 'database.schema'

        Raises:
            ValueError: If normalization results in empty key parts

        Examples:
            >>> SchemaKey("MyDatabase1", "PublicSchema").key()
            'mydatabase1.publicschema'
            >>> SchemaKey("ANALYTICS_DB", "sales.data").key()
            'analytics_db.sales_data'
        """
        # Generate normalized database key
        db_key = DatabaseKey(self.database_name).key()

        # Generate normalized schema key using same logic
        schema_key = self.schema_name.strip().lower()
        schema_key = re.sub(r'[^a-z0-9]+', '_', schema_key)
        schema_key = schema_key.strip('_')

        if not schema_key:
            raise ValueError(f"Invalid schema key for name: {self.schema_name}")

        return f"{db_key}.{schema_key}"

    def get_database_key(self) -> str:
        """Get just the database part of the schema key."""
        return DatabaseKey(self.database_name).key()

    def get_schema_part(self) -> str:
        """Get just the schema part of the key (without database prefix)."""
        schema_key = self.schema_name.strip().lower()
        schema_key = re.sub(r'[^a-z0-9]+', '_', schema_key)
        return schema_key.strip('_')

    def __str__(self) -> str:
        """String representation returns the key."""
        return self.key()

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"SchemaKey(database_name='{self.database_name}', schema_name='{self.schema_name}')"

    def __eq__(self, other) -> bool:
        """Check equality with another SchemaKey."""
        if not isinstance(other, SchemaKey):
            return False
        return self.key() == other.key()

    def __hash__(self) -> int:
        """Hash for using as dictionary key."""
        return hash(self.key())


@dataclass
class StructuredPropertyUrn:
    """URN for structured properties."""
    property_id: str

    def urn(self) -> str:
        return f"urn:li:structuredProperty:{self.property_id}"


@dataclass
class DataPlatformUrn:
    """URN for data platforms."""
    platform: str

    def urn(self) -> str:
        return f"urn:li:dataPlatform:{self.platform}"


@dataclass
class DatasetUrn:
    """URN for datasets with platform instance support."""
    platform: str
    name: str
    origin: str = "PROD"
    platform_instance: Optional[str] = None

    def urn(self) -> str:
        if self.platform_instance:
            return f"urn:li:dataset:(urn:li:dataPlatform:{self.platform},{self.name},{self.origin},urn:li:dataPlatformInstance:({self.platform_instance}))"
        return f"urn:li:dataset:(urn:li:dataPlatform:{self.platform},{self.name},{self.origin})"


@dataclass
class TagUrn:
    """URN for tags."""
    name: str

    def urn(self) -> str:
        return f"urn:li:tag:{self.name}"


@dataclass
class SchemaFieldUrn:
    """URN for schema fields."""
    dataset_urn: str
    field_path: str

    def urn(self) -> str:
        return f"urn:li:schemaField:({self.dataset_urn},{self.field_path})"


@dataclass
class ContainerUrn:
    """URN for containers."""
    platform: str
    name: str
    origin: str = "PROD"

    def urn(self) -> str:
        return f"urn:li:container:{self.platform}.{self.name}.{self.origin}"


class AdvancedMCPBuilder:
    """
    Advanced Metadata Change Proposal builder with validation,
    caching, and performance optimization.
    """

    def __init__(self):
        self._urn_cache: Dict[str, str] = {}
        self._validation_cache: Set[str] = set()
        self._key_cache: Dict[str, Union[DatabaseKey, SchemaKey]] = {}
        self._performance_metrics = {
            'urn_generations': 0,
            'cache_hits': 0,
            'validations': 0,
            'key_generations': 0
        }

    def make_database_key(self, database_name: str) -> DatabaseKey:
        """
        Create a DatabaseKey with caching for performance.

        Args:
            database_name: Name of the database

        Returns:
            DatabaseKey instance
        """
        cache_key = f"db_key:{database_name}"
        if cache_key in self._key_cache:
            self._performance_metrics['cache_hits'] += 1
            return self._key_cache[cache_key]

        db_key = DatabaseKey(database_name)
        self._key_cache[cache_key] = db_key
        self._performance_metrics['key_generations'] += 1
        return db_key

    def make_schema_key(self, database_name: str, schema_name: str) -> SchemaKey:
        """
        Create a SchemaKey with caching for performance.

        Args:
            database_name: Name of the database
            schema_name: Name of the schema

        Returns:
            SchemaKey instance
        """
        cache_key = f"schema_key:{database_name}:{schema_name}"
        if cache_key in self._key_cache:
            self._performance_metrics['cache_hits'] += 1
            return self._key_cache[cache_key]

        schema_key = SchemaKey(database_name, schema_name)
        self._key_cache[cache_key] = schema_key
        self._performance_metrics['key_generations'] += 1
        return schema_key

    def make_data_platform_urn(self, platform: str) -> str:
        """Create data platform URN with caching."""
        cache_key = f"platform:{platform}"
        if cache_key in self._urn_cache:
            self._performance_metrics['cache_hits'] += 1
            return self._urn_cache[cache_key]

        if platform not in [p.value for p in PlatformType]:
            logger.warning(f"Unknown platform type: {platform}")

        urn = DataPlatformUrn(platform=platform).urn()
        self._urn_cache[cache_key] = urn
        self._performance_metrics['urn_generations'] += 1
        return urn

    def make_dataset_urn_with_platform_instance(
            self,
            platform: str,
            name: str,
            env: str = "PROD",
            platform_instance: Optional[str] = None
    ) -> str:
        """Create dataset URN with platform instance support."""
        cache_key = f"dataset:{platform}:{name}:{env}:{platform_instance}"
        if cache_key in self._urn_cache:
            self._performance_metrics['cache_hits'] += 1
            return self._urn_cache[cache_key]

        # Validate dataset name
        if not self._is_valid_dataset_name(name):
            raise ValueError(f"Invalid dataset name: {name}")

        urn = DatasetUrn(
            platform=platform,
            name=name,
            origin=env,
            platform_instance=platform_instance
        ).urn()

        self._urn_cache[cache_key] = urn
        self._performance_metrics['urn_generations'] += 1
        return urn

    def make_dataset_urn_from_keys(
            self,
            platform: str,
            database_key: DatabaseKey,
            schema_key: SchemaKey,
            table_name: str,
            env: str = "PROD"
    ) -> str:
        """
        Create dataset URN using DatabaseKey and SchemaKey for consistent naming.

        Args:
            platform: Data platform name
            database_key: DatabaseKey instance
            schema_key: SchemaKey instance
            table_name: Name of the table
            env: Environment (default: PROD)

        Returns:
            Dataset URN string
        """
        # Use normalized keys to build dataset name
        dataset_name = f"{schema_key.key()}.{table_name.lower()}"

        return self.make_dataset_urn_with_platform_instance(
            platform=platform,
            name=dataset_name,
            env=env
        )

    def make_schema_field_urn(self, dataset_urn: str, field_path: str) -> str:
        """Create schema field URN."""
        cache_key = f"field:{dataset_urn}:{field_path}"
        if cache_key in self._urn_cache:
            self._performance_metrics['cache_hits'] += 1
            return self._urn_cache[cache_key]

        urn = SchemaFieldUrn(dataset_urn=dataset_urn, field_path=field_path).urn()
        self._urn_cache[cache_key] = urn
        self._performance_metrics['urn_generations'] += 1
        return urn

    def make_tag_urn(self, tag_name: str) -> str:
        """Create tag URN with validation."""
        cache_key = f"tag:{tag_name}"
        if cache_key in self._urn_cache:
            self._performance_metrics['cache_hits'] += 1
            return self._urn_cache[cache_key]

        # Sanitize tag name
        sanitized_name = self._sanitize_tag_name(tag_name)
        urn = TagUrn(name=sanitized_name).urn()

        self._urn_cache[cache_key] = urn
        self._performance_metrics['urn_generations'] += 1
        return urn

    def make_container_urn(
            self,
            platform: str,
            container_name: str,
            env: str = "PROD"
    ) -> str:
        """Create container URN."""
        cache_key = f"container:{platform}:{container_name}:{env}"
        if cache_key in self._urn_cache:
            self._performance_metrics['cache_hits'] += 1
            return self._urn_cache[cache_key]

        urn = ContainerUrn(platform=platform, name=container_name, origin=env).urn()
        self._urn_cache[cache_key] = urn
        self._performance_metrics['urn_generations'] += 1
        return urn

    def make_container_urn_from_schema_key(
            self,
            platform: str,
            schema_key: SchemaKey,
            env: str = "PROD"
    ) -> str:
        """
        Create container URN using SchemaKey for consistent naming.

        Args:
            platform: Data platform name
            schema_key: SchemaKey instance
            env: Environment

        Returns:
            Container URN string
        """
        return self.make_container_urn(
            platform=platform,
            container_name=schema_key.key(),
            env=env
        )

    def _is_valid_dataset_name(self, name: str) -> bool:
        """Validate dataset name format."""
        if not name or len(name) == 0:
            return False

        # Check for valid characters (alphanumeric, dots, underscores, hyphens)
        pattern = r'^[a-zA-Z0-9._-]+$'
        return bool(re.match(pattern, name))

    def _sanitize_tag_name(self, tag_name: str) -> str:
        """Sanitize tag name for URN compliance."""
        # Replace spaces with underscores, remove special characters
        sanitized = re.sub(r'[^\w\-_.]', '_', tag_name)
        sanitized = re.sub(r'_+', '_', sanitized)  # Collapse multiple underscores
        return sanitized.strip('_')

    def get_performance_metrics(self) -> Dict[str, int]:
        """Get performance metrics for monitoring."""
        return self._performance_metrics.copy()

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._urn_cache.clear()
        self._validation_cache.clear()
        self._key_cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "urn_cache_size": len(self._urn_cache),
            "key_cache_size": len(self._key_cache),
            "validation_cache_size": len(self._validation_cache),
            "performance_metrics": self._performance_metrics
        }


# Global builder instance
_builder = AdvancedMCPBuilder()


# Convenience functions for key generation
def make_database_key(database_name: str) -> DatabaseKey:
    """Create a DatabaseKey using the global builder instance."""
    return _builder.make_database_key(database_name)


def make_schema_key(database_name: str, schema_name: str) -> SchemaKey:
    """Create a SchemaKey using the global builder instance."""
    return _builder.make_schema_key(database_name, schema_name)


# Existing convenience functions
def make_data_platform_urn(platform: str) -> str:
    return _builder.make_data_platform_urn(platform)


def make_dataset_urn_with_platform_instance(
        platform: str, name: str, env: str = "PROD", platform_instance: Optional[str] = None
) -> str:
    return _builder.make_dataset_urn_with_platform_instance(platform, name, env, platform_instance)


def make_dataset_urn_from_keys(
        platform: str,
        database_key: DatabaseKey,
        schema_key: SchemaKey,
        table_name: str,
        env: str = "PROD"
) -> str:
    """Create dataset URN using DatabaseKey and SchemaKey."""
    return _builder.make_dataset_urn_from_keys(platform, database_key, schema_key, table_name, env)


def make_schema_field_urn(dataset_urn: str, field_path: str) -> str:
    return _builder.make_schema_field_urn(dataset_urn, field_path)


def make_tag_urn(tag_name: str) -> str:
    return _builder.make_tag_urn(tag_name)


def make_container_urn(platform: str, container_name: str, env: str = "PROD") -> str:
    return _builder.make_container_urn(platform, container_name, env)


def make_container_urn_from_schema_key(
        platform: str,
        schema_key: SchemaKey,
        env: str = "PROD"
) -> str:
    """Create container URN using SchemaKey."""
    return _builder.make_container_urn_from_schema_key(platform, schema_key, env)


# Advanced structured properties builder
def add_structured_properties_to_entity_wu(
        entity_urn: str,
        structured_properties: Dict[StructuredPropertyUrn, str]
) -> Iterable[Any]:
    """Add structured properties to entity with validation."""
    from dataguild.emitter.mcp import MetadataChangeProposalWrapper
    from dataguild.metadata.schemas import StructuredProperties

    if not structured_properties:
        return

    # Validate structured properties
    validated_properties = {}
    for prop_urn, value in structured_properties.items():
        if not isinstance(prop_urn, StructuredPropertyUrn):
            logger.warning(f"Invalid structured property URN: {prop_urn}")
            continue

        # Validate value is serializable
        try:
            json.dumps(value)
            validated_properties[prop_urn.urn()] = value
        except TypeError:
            logger.warning(f"Non-serializable value for property {prop_urn.urn()}: {value}")

    if validated_properties:
        structured_props = StructuredProperties(properties=validated_properties)
        yield MetadataChangeProposalWrapper(
            entityUrn=entity_urn,
            aspect=structured_props
        ).as_workunit()


# Export all classes and functions
__all__ = [
    # Key classes
    'DatabaseKey',
    'SchemaKey',

    # Enum classes
    'EntityType',
    'PlatformType',

    # URN classes
    'StructuredPropertyUrn',
    'DataPlatformUrn',
    'DatasetUrn',
    'TagUrn',
    'SchemaFieldUrn',
    'ContainerUrn',

    # Builder classes
    'AdvancedMCPBuilder',

    # Convenience functions
    'make_database_key',
    'make_schema_key',
    'make_data_platform_urn',
    'make_dataset_urn_with_platform_instance',
    'make_dataset_urn_from_keys',
    'make_schema_field_urn',
    'make_tag_urn',
    'make_container_urn',
    'make_container_urn_from_schema_key',
    'add_structured_properties_to_entity_wu',
]
