"""
DataGuild SQL source configuration classes.

This module provides configuration classes for SQL-based data sources,
including common connection settings, filtering options, and advanced
configuration for various SQL databases and data warehouses.
"""

import logging
from typing import Any, Dict, List, Optional, Pattern, Set, Union
from enum import Enum
import re

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import SecretStr

logger = logging.getLogger(__name__)


class SQLDialect(str, Enum):
    """Supported SQL dialects for DataGuild ingestion."""

    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    POSTGRES = "postgres"  # Alias for postgresql
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    MSSQL = "mssql"
    ORACLE = "oracle"
    SQLITE = "sqlite"
    HIVE = "hive"
    SPARK = "spark"
    PRESTO = "presto"
    TRINO = "trino"
    DATABRICKS = "databricks"
    CLICKHOUSE = "clickhouse"


class SQLCommonConfig(BaseModel):
    """
    Common configuration for SQL-based data sources.

    This class provides the base configuration options that are shared
    across different SQL database connectors, including connection details,
    authentication, and basic query options.

    Examples:
        >>> config = SQLCommonConfig(
        ...     dialect="postgresql",
        ...     url="postgresql://user:pass@localhost:5432/mydb",
        ...     database="mydb",
        ...     schema_name="public"
        ... )
        >>> print(config.get_connection_url())
    """

    # Core connection settings
    dialect: Optional[SQLDialect] = Field(
        default=None,
        description="SQL dialect to use for this connection"
    )

    url: Optional[str] = Field(
        default=None,
        description="Complete database connection URL (if provided, overrides individual connection params)"
    )

    host: Optional[str] = Field(
        default="localhost",
        description="Database host address"
    )

    port: Optional[int] = Field(
        default=None,
        description="Database port number"
    )

    database: Optional[str] = Field(
        default=None,
        description="Name of the database to connect to"
    )

    schema_name: Optional[str] = Field(
        default=None,
        alias="schema",
        description="Default schema name to use"
    )

    # Authentication
    username: Optional[str] = Field(
        default=None,
        description="Database username"
    )

    password: Optional[SecretStr] = Field(
        default=None,
        description="Database password (will be hidden in logs)"
    )

    # Connection options
    connect_args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional connection arguments to pass to the database driver"
    )

    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional options for the database connection"
    )

    # Query execution settings
    query_timeout: Optional[int] = Field(
        default=300,
        description="Query timeout in seconds"
    )

    connection_timeout: Optional[int] = Field(
        default=30,
        description="Connection timeout in seconds"
    )

    # SSL/TLS settings
    use_ssl: bool = Field(
        default=False,
        description="Whether to use SSL/TLS for the connection"
    )

    ssl_ca: Optional[str] = Field(
        default=None,
        description="Path to SSL CA certificate file"
    )

    ssl_cert: Optional[str] = Field(
        default=None,
        description="Path to SSL client certificate file"
    )

    ssl_key: Optional[str] = Field(
        default=None,
        description="Path to SSL client key file"
    )

    # Advanced settings
    pool_size: int = Field(
        default=5,
        description="Database connection pool size"
    )

    max_overflow: int = Field(
        default=10,
        description="Maximum connection pool overflow"
    )

    pool_recycle: int = Field(
        default=3600,
        description="Connection pool recycle time in seconds"
    )

    class Config:
        """Pydantic configuration."""
        allow_population_by_field_name = True
        extra = "allow"

    @validator('port')
    def validate_port(cls, v):
        """Validate port number range."""
        if v is not None and (v < 1 or v > 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    @validator('query_timeout', 'connection_timeout')
    def validate_timeout(cls, v):
        """Validate timeout values."""
        if v is not None and v < 0:
            raise ValueError("Timeout must be non-negative")
        return v

    @root_validator
    def validate_connection_config(cls, values):
        """Validate that either url or individual connection params are provided."""
        url = values.get('url')
        host = values.get('host')
        database = values.get('database')

        if not url and not (host and database):
            raise ValueError(
                "Either 'url' must be provided, or both 'host' and 'database' must be specified"
            )

        return values

    def get_connection_url(self) -> str:
        """
        Get the complete connection URL for this configuration.

        Returns:
            Complete database connection URL
        """
        if self.url:
            return self.url

        # Build URL from individual components
        if not self.dialect:
            raise ValueError("Dialect must be specified to build connection URL")

        url_parts = [f"{self.dialect.value}://"]

        # Add authentication if provided
        if self.username:
            auth = self.username
            if self.password:
                auth += f":{self.password.get_secret_value()}"
            url_parts.append(f"{auth}@")

        # Add host and port
        url_parts.append(self.host or "localhost")
        if self.port:
            url_parts.append(f":{self.port}")

        # Add database
        if self.database:
            url_parts.append(f"/{self.database}")

        return "".join(url_parts)

    def get_safe_connection_url(self) -> str:
        """
        Get connection URL with password redacted for logging.

        Returns:
            Connection URL with password replaced by asterisks
        """
        url = self.get_connection_url()
        if self.password:
            # Replace password in URL with asterisks
            password_value = self.password.get_secret_value()
            if password_value in url:
                url = url.replace(password_value, "***")
        return url


class SQLFilterConfig(BaseModel):
    """
    Configuration for filtering SQL database objects during ingestion.

    This class provides options to include or exclude specific tables, schemas,
    and other database objects from the ingestion process.

    Examples:
        >>> filter_config = SQLFilterConfig(
        ...     schema_pattern=r"^(public|analytics)$",
        ...     table_pattern=r"^(?!temp_).*",
        ...     deny_list=["sensitive_table", "temp_*"]
        ... )
        >>> print(filter_config.should_include_table("public", "users"))
        True
    """

    # Schema filtering
    schema_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern for schema names to include"
    )

    schema_deny_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern for schema names to exclude"
    )

    allow_list: Optional[List[str]] = Field(
        default=None,
        description="List of schema names to explicitly include"
    )

    deny_list: Optional[List[str]] = Field(
        default_factory=list,
        description="List of schema names to explicitly exclude"
    )

    # Table filtering
    table_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern for table names to include"
    )

    table_deny_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern for table names to exclude"
    )

    table_allow_list: Optional[List[str]] = Field(
        default=None,
        description="List of table names to explicitly include"
    )

    table_deny_list: Optional[List[str]] = Field(
        default_factory=list,
        description="List of table names to explicitly exclude"
    )

    # Object type filtering
    include_views: bool = Field(
        default=True,
        description="Whether to include database views"
    )

    include_tables: bool = Field(
        default=True,
        description="Whether to include regular tables"
    )

    include_external_tables: bool = Field(
        default=True,
        description="Whether to include external tables"
    )

    include_materialized_views: bool = Field(
        default=True,
        description="Whether to include materialized views"
    )

    # Advanced filtering options
    min_table_size_bytes: Optional[int] = Field(
        default=None,
        description="Minimum table size in bytes to include"
    )

    max_table_size_bytes: Optional[int] = Field(
        default=None,
        description="Maximum table size in bytes to include"
    )

    min_column_count: Optional[int] = Field(
        default=None,
        description="Minimum number of columns required to include table"
    )

    max_column_count: Optional[int] = Field(
        default=None,
        description="Maximum number of columns allowed to include table"
    )

    # Performance settings
    sample_size: Optional[int] = Field(
        default=None,
        description="Maximum number of tables to sample for profiling"
    )

    def __post_init__(self):
        """Compile regex patterns after initialization."""
        self._schema_pattern = self._compile_pattern(self.schema_pattern)
        self._schema_deny_pattern = self._compile_pattern(self.schema_deny_pattern)
        self._table_pattern = self._compile_pattern(self.table_pattern)
        self._table_deny_pattern = self._compile_pattern(self.table_deny_pattern)

    def _compile_pattern(self, pattern: Optional[str]) -> Optional[Pattern]:
        """Compile a regex pattern string."""
        if not pattern:
            return None
        try:
            return re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
            return None

    def should_include_schema(self, schema_name: str) -> bool:
        """
        Check if a schema should be included based on filtering rules.

        Args:
            schema_name: Name of the schema to check

        Returns:
            True if schema should be included, False otherwise
        """
        # Check explicit deny list first
        if self.deny_list and schema_name in self.deny_list:
            return False

        # Check deny pattern
        if self._schema_deny_pattern and self._schema_deny_pattern.match(schema_name):
            return False

        # Check explicit allow list
        if self.allow_list:
            return schema_name in self.allow_list

        # Check allow pattern
        if self._schema_pattern:
            return bool(self._schema_pattern.match(schema_name))

        # Default to include if no filters specified
        return True

    def should_include_table(self, schema_name: str, table_name: str) -> bool:
        """
        Check if a table should be included based on filtering rules.

        Args:
            schema_name: Name of the schema containing the table
            table_name: Name of the table to check

        Returns:
            True if table should be included, False otherwise
        """
        # First check if schema should be included
        if not self.should_include_schema(schema_name):
            return False

        # Check explicit table deny list
        if self.table_deny_list and table_name in self.table_deny_list:
            return False

        # Check table deny pattern
        if self._table_deny_pattern and self._table_deny_pattern.match(table_name):
            return False

        # Check explicit table allow list
        if self.table_allow_list:
            return table_name in self.table_allow_list

        # Check table allow pattern
        if self._table_pattern:
            return bool(self._table_pattern.match(table_name))

        # Default to include if no table filters specified
        return True

    def should_include_table_type(self, table_type: str) -> bool:
        """
        Check if a table type should be included.

        Args:
            table_type: Type of the table (TABLE, VIEW, etc.)

        Returns:
            True if table type should be included, False otherwise
        """
        table_type_lower = table_type.lower()

        if table_type_lower in ["table", "base table"]:
            return self.include_tables
        elif table_type_lower in ["view"]:
            return self.include_views
        elif table_type_lower in ["materialized view"]:
            return self.include_materialized_views
        elif table_type_lower in ["external table"]:
            return self.include_external_tables

        # Default to include unknown types
        return True

    def get_filtered_schemas(self, all_schemas: List[str]) -> List[str]:
        """
        Filter a list of schemas based on the configuration.

        Args:
            all_schemas: List of all available schema names

        Returns:
            Filtered list of schema names
        """
        return [schema for schema in all_schemas if self.should_include_schema(schema)]

    def get_filtered_tables(self, schema_tables: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Filter a dictionary of schema->tables based on the configuration.

        Args:
            schema_tables: Dictionary mapping schema names to lists of table names

        Returns:
            Filtered dictionary of schema->tables
        """
        filtered = {}

        for schema_name, table_list in schema_tables.items():
            if self.should_include_schema(schema_name):
                filtered_tables = [
                    table for table in table_list
                    if self.should_include_table(schema_name, table)
                ]
                if filtered_tables:
                    filtered[schema_name] = filtered_tables

        return filtered


# Export classes
__all__ = [
    'SQLDialect',
    'SQLCommonConfig',
    'SQLFilterConfig',
]
