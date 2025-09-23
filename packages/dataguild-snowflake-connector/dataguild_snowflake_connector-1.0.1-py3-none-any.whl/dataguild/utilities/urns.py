"""
DataGuild URN utilities.

This module provides utilities for creating, parsing, and manipulating
Uniform Resource Names (URNs) used in DataGuild for entity identification.
"""

import re
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import quote, unquote

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Supported entity types in DataGuild URNs."""
    DATASET = "dataset"
    DATA_PLATFORM = "dataPlatform"
    DATA_JOB = "dataJob"
    DATA_FLOW = "dataFlow"
    DASHBOARD = "dashboard"
    CHART = "chart"
    CONTAINER = "container"
    DOMAIN = "domain"
    TAG = "tag"
    GLOSSARY_TERM = "glossaryTerm"
    CORPUSER = "corpuser"
    CORPGROUP = "corpgroup"


class UrnValidationError(Exception):
    """Exception raised when URN validation fails."""
    pass


class BaseUrn:
    """
    Base class for all URN types in DataGuild.

    Provides common functionality for URN parsing, validation, and manipulation.
    """

    # URN pattern: urn:li:entityType:(key)
    URN_PATTERN = re.compile(r'^urn:li:([^:]+):\((.+)\)$')

    def __init__(self, urn_str: str):
        """
        Initialize URN from string.

        Args:
            urn_str: URN string to parse

        Raises:
            UrnValidationError: If URN format is invalid
        """
        self._urn_str = urn_str.strip()
        self._entity_type, self._key = self._parse_urn(self._urn_str)
        self._validate()

    def _parse_urn(self, urn_str: str) -> Tuple[str, str]:
        """
        Parse URN string into entity type and key.

        Args:
            urn_str: URN string to parse

        Returns:
            Tuple of (entity_type, key)

        Raises:
            UrnValidationError: If URN format is invalid
        """
        match = self.URN_PATTERN.match(urn_str)
        if not match:
            raise UrnValidationError(f"Invalid URN format: {urn_str}")

        entity_type = match.group(1)
        key = match.group(2)

        return entity_type, key

    def _validate(self) -> None:
        """Validate the URN. Override in subclasses for specific validation."""
        pass

    @property
    def entity_type(self) -> str:
        """Get the entity type."""
        return self._entity_type

    @property
    def key(self) -> str:
        """Get the entity key."""
        return self._key

    def __str__(self) -> str:
        """String representation of the URN."""
        return self._urn_str

    def __repr__(self) -> str:
        """Detailed representation of the URN."""
        return f"{self.__class__.__name__}('{self._urn_str}')"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another URN."""
        if not isinstance(other, BaseUrn):
            return False
        return self._urn_str == other._urn_str

    def __hash__(self) -> int:
        """Hash for using URN as dictionary key."""
        return hash(self._urn_str)

    def to_dict(self) -> Dict[str, str]:
        """Convert URN to dictionary representation."""
        return {
            "urn": self._urn_str,
            "entity_type": self._entity_type,
            "key": self._key
        }


class DataPlatformUrn(BaseUrn):
    """
    URN for data platforms.

    Format: urn:li:dataPlatform:platform_name
    Example: urn:li:dataPlatform:snowflake
    """

    def __init__(self, platform_name: str):
        """
        Initialize DataPlatform URN.

        Args:
            platform_name: Name of the data platform
        """
        if isinstance(platform_name, str) and platform_name.startswith('urn:li:dataPlatform:'):
            # Already a URN string
            super().__init__(platform_name)
        else:
            # Platform name, construct URN
            urn_str = f"urn:li:dataPlatform:{platform_name}"
            super().__init__(urn_str)

    @property
    def platform_name(self) -> str:
        """Get the platform name."""
        return self._key

    def _validate(self) -> None:
        """Validate DataPlatform URN."""
        if self._entity_type != "dataPlatform":
            raise UrnValidationError(f"Expected dataPlatform, got {self._entity_type}")

        if not self._key or not self._key.strip():
            raise UrnValidationError("Platform name cannot be empty")

    @classmethod
    def create(cls, platform_name: str) -> "DataPlatformUrn":
        """
        Create DataPlatform URN from platform name.

        Args:
            platform_name: Name of the platform

        Returns:
            DataPlatformUrn instance
        """
        return cls(platform_name)


class DatasetUrn(BaseUrn):
    """
    URN for datasets.

    Format: urn:li:dataset:(urn:li:dataPlatform:platform,name,env)
    Example: urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)
    """

    # Dataset key pattern: (platform_urn,name,env)
    DATASET_KEY_PATTERN = re.compile(r'^(urn:li:dataPlatform:[^,]+),([^,]+),([^,]+)$')

    def __init__(self, urn_str: str):
        """
        Initialize Dataset URN from string.

        Args:
            urn_str: Complete dataset URN string
        """
        super().__init__(urn_str)
        self._platform_urn, self._name, self._env = self._parse_dataset_key()

    def _parse_dataset_key(self) -> Tuple[str, str, str]:
        """
        Parse dataset key into components.

        Returns:
            Tuple of (platform_urn, name, env)

        Raises:
            UrnValidationError: If key format is invalid
        """
        match = self.DATASET_KEY_PATTERN.match(self._key)
        if not match:
            raise UrnValidationError(f"Invalid dataset key format: {self._key}")

        platform_urn = match.group(1)
        name = unquote(match.group(2))  # URL decode the name
        env = match.group(3)

        return platform_urn, name, env

    def _validate(self) -> None:
        """Validate Dataset URN."""
        if self._entity_type != "dataset":
            raise UrnValidationError(f"Expected dataset, got {self._entity_type}")

        # Validate platform URN
        try:
            DataPlatformUrn(self._platform_urn)
        except UrnValidationError as e:
            raise UrnValidationError(f"Invalid platform URN: {e}")

        if not self._name or not self._name.strip():
            raise UrnValidationError("Dataset name cannot be empty")

        if not self._env or not self._env.strip():
            raise UrnValidationError("Environment cannot be empty")

    @property
    def platform(self) -> str:
        """Get the platform name."""
        return DataPlatformUrn(self._platform_urn).platform_name

    @property
    def platform_urn(self) -> str:
        """Get the platform URN."""
        return self._platform_urn

    @property
    def name(self) -> str:
        """Get the dataset name."""
        return self._name

    @property
    def env(self) -> str:
        """Get the environment."""
        return self._env

    def get_database(self) -> Optional[str]:
        """Extract database from dataset name (first part before first dot)."""
        parts = self._name.split('.')
        return parts[0] if parts else None

    def get_schema(self) -> Optional[str]:
        """Extract schema from dataset name (second part)."""
        parts = self._name.split('.')
        return parts[1] if len(parts) >= 2 else None

    def get_table(self) -> Optional[str]:
        """Extract table from dataset name (third part)."""
        parts = self._name.split('.')
        return parts[2] if len(parts) >= 3 else parts[-1] if parts else None

    def get_name_parts(self) -> List[str]:
        """Get all parts of the dataset name split by dots."""
        return self._name.split('.')

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary with dataset-specific fields."""
        base_dict = super().to_dict()
        base_dict.update({
            "platform": self.platform,
            "platform_urn": self._platform_urn,
            "name": self._name,
            "env": self._env,
            "database": self.get_database(),
            "schema": self.get_schema(),
            "table": self.get_table(),
        })
        return base_dict

    @classmethod
    def create(
            cls,
            platform: str,
            name: str,
            env: str = "PROD"
    ) -> "DatasetUrn":
        """
        Create Dataset URN from components.

        Args:
            platform: Platform name (e.g., 'snowflake', 'bigquery')
            name: Dataset name (e.g., 'db.schema.table')
            env: Environment (default: 'PROD')

        Returns:
            DatasetUrn instance

        Example:
            >>> urn = DatasetUrn.create("snowflake", "db.schema.table", "PROD")
            >>> str(urn)
            'urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)'
        """
        platform_urn = f"urn:li:dataPlatform:{platform}"
        encoded_name = quote(name, safe='.')  # URL encode, but keep dots
        dataset_key = f"{platform_urn},{encoded_name},{env}"
        urn_str = f"urn:li:dataset:({dataset_key})"

        return cls(urn_str)

    @classmethod
    def create_from_parts(
            cls,
            platform: str,
            database: str,
            schema: Optional[str] = None,
            table: Optional[str] = None,
            env: str = "PROD"
    ) -> "DatasetUrn":
        """
        Create Dataset URN from database parts.

        Args:
            platform: Platform name
            database: Database name
            schema: Schema name (optional)
            table: Table name (optional)
            env: Environment

        Returns:
            DatasetUrn instance
        """
        name_parts = [database]
        if schema:
            name_parts.append(schema)
        if table:
            name_parts.append(table)

        name = '.'.join(name_parts)
        return cls.create(platform, name, env)

    @classmethod
    def parse(cls, urn_str: str) -> "DatasetUrn":
        """
        Parse URN string into DatasetUrn.

        Args:
            urn_str: URN string to parse

        Returns:
            DatasetUrn instance
        """
        return cls(urn_str)


# Utility functions
def create_dataset_urn(
        platform: str,
        name: str,
        env: str = "PROD"
) -> DatasetUrn:
    """
    Create a dataset URN from components.

    Args:
        platform: Data platform name
        name: Dataset name
        env: Environment

    Returns:
        DatasetUrn instance
    """
    return DatasetUrn.create(platform, name, env)


def create_snowflake_dataset_urn(
        database: str,
        schema: str,
        table: str,
        env: str = "PROD"
) -> DatasetUrn:
    """
    Create a Snowflake dataset URN.

    Args:
        database: Snowflake database name
        schema: Snowflake schema name
        table: Snowflake table name
        env: Environment

    Returns:
        DatasetUrn for Snowflake dataset
    """
    return DatasetUrn.create_from_parts("snowflake", database, schema, table, env)


def create_bigquery_dataset_urn(
        project: str,
        dataset: str,
        table: str,
        env: str = "PROD"
) -> DatasetUrn:
    """
    Create a BigQuery dataset URN.

    Args:
        project: GCP project name
        dataset: BigQuery dataset name
        table: BigQuery table name
        env: Environment

    Returns:
        DatasetUrn for BigQuery dataset
    """
    return DatasetUrn.create_from_parts("bigquery", project, dataset, table, env)


def parse_urn(urn_str: str) -> BaseUrn:
    """
    Parse a URN string into the appropriate URN type.

    Args:
        urn_str: URN string to parse

    Returns:
        Appropriate URN instance based on entity type

    Raises:
        UrnValidationError: If URN cannot be parsed or entity type is unsupported
    """
    try:
        # Try to determine entity type
        match = BaseUrn.URN_PATTERN.match(urn_str.strip())
        if not match:
            raise UrnValidationError(f"Invalid URN format: {urn_str}")

        entity_type = match.group(1)

        # Route to appropriate URN class
        if entity_type == "dataset":
            return DatasetUrn(urn_str)
        elif entity_type == "dataPlatform":
            return DataPlatformUrn(urn_str)
        else:
            # For unsupported types, return generic BaseUrn
            return BaseUrn(urn_str)

    except Exception as e:
        raise UrnValidationError(f"Failed to parse URN '{urn_str}': {e}")


def is_valid_urn(urn_str: str) -> bool:
    """
    Check if a string is a valid URN.

    Args:
        urn_str: String to validate

    Returns:
        True if valid URN, False otherwise
    """
    try:
        parse_urn(urn_str)
        return True
    except UrnValidationError:
        return False


def normalize_urn(urn_str: str) -> str:
    """
    Normalize a URN string (parse and reconstruct).

    Args:
        urn_str: URN string to normalize

    Returns:
        Normalized URN string

    Raises:
        UrnValidationError: If URN is invalid
    """
    urn = parse_urn(urn_str)
    return str(urn)


# Export all classes and functions
__all__ = [
    'BaseUrn',
    'DatasetUrn',
    'DataPlatformUrn',
    'EntityType',
    'UrnValidationError',
    'create_dataset_urn',
    'create_snowflake_dataset_urn',
    'create_bigquery_dataset_urn',
    'parse_urn',
    'is_valid_urn',
    'normalize_urn',
]
