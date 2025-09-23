"""
DataGuild SQL source configuration.

This module provides configuration classes for SQL database sources including
connection management, filtering, and common SQL operations.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse

import pydantic
from pydantic import Field, validator

from dataguild.configuration.common import ConfigModel, AllowDenyPattern, MetaError

logger = logging.getLogger(__name__)


class SQLDialect(Enum):
    """Supported SQL database dialects."""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    DATABRICKS = "databricks"
    UNKNOWN = "unknown"


class SQLCommonConfig(ConfigModel):
    """
    Common SQL configuration for database connections and operations.

    Provides shared configuration options for SQL-based data sources including
    connection parameters, query limits, and performance settings.
    """

    # Connection configuration
    connection_string: Optional[str] = Field(
        default=None,
        description="Complete database connection string (overrides individual parameters)"
    )

    host: Optional[str] = Field(
        default=None,
        description="Database host address"
    )

    port: Optional[int] = Field(
        default=None,
        description="Database port number"
    )

    database: Optional[str] = Field(
        default=None,
        description="Database name to connect to"
    )

    username: Optional[str] = Field(
        default=None,
        description="Database username for authentication"
    )

    password: Optional[pydantic.SecretStr] = Field(
        default=None,
        description="Database password for authentication"
    )

    # SQL dialect and driver configuration
    dialect: SQLDialect = Field(
        default=SQLDialect.UNKNOWN,
        description="SQL dialect/database type"
    )

    driver: Optional[str] = Field(
        default=None,
        description="Database driver name (e.g., 'psycopg2', 'pymysql')"
    )

    # Query execution configuration
    query_timeout: int = Field(
        default=300,
        description="Query timeout in seconds",
        ge=1,
        le=7200
    )

    max_rows: Optional[int] = Field(
        default=None,
        description="Maximum number of rows to fetch per query (None for unlimited)",
        ge=1
    )

    batch_size: int = Field(
        default=1000,
        description="Number of rows to fetch per batch",
        ge=1,
        le=100000
    )

    # Connection pool settings
    pool_size: int = Field(
        default=5,
        description="Connection pool size",
        ge=1,
        le=50
    )

    max_overflow: int = Field(
        default=10,
        description="Maximum connection overflow",
        ge=0,
        le=100
    )

    pool_pre_ping: bool = Field(
        default=True,
        description="Enable connection health checks before use"
    )

    # Performance and optimization settings
    enable_query_cache: bool = Field(
        default=True,
        description="Enable query result caching"
    )

    cache_ttl: int = Field(
        default=300,
        description="Cache TTL in seconds",
        ge=60,
        le=86400
    )

    enable_parallel_queries: bool = Field(
        default=False,
        description="Enable parallel query execution"
    )

    max_parallel_queries: int = Field(
        default=3,
        description="Maximum number of parallel queries",
        ge=1,
        le=20
    )

    # SSL/TLS configuration
    ssl_mode: Optional[str] = Field(
        default=None,
        description="SSL mode (e.g., 'require', 'prefer', 'disable')"
    )

    ssl_cert: Optional[str] = Field(
        default=None,
        description="Path to SSL certificate file"
    )

    ssl_key: Optional[str] = Field(
        default=None,
        description="Path to SSL key file"
    )

    ssl_ca: Optional[str] = Field(
        default=None,
        description="Path to SSL CA certificate file"
    )

    # Additional connection options
    connect_args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional connection arguments passed to SQLAlchemy"
    )

    # Logging and debugging
    enable_sql_logging: bool = Field(
        default=False,
        description="Enable SQL query logging (for debugging)"
    )

    log_slow_queries: bool = Field(
        default=True,
        description="Log queries that exceed slow query threshold"
    )

    slow_query_threshold: float = Field(
        default=5.0,
        description="Slow query threshold in seconds",
        ge=0.1
    )

    @validator("dialect", pre=True)
    def validate_dialect(cls, v):
        """Validate and normalize SQL dialect."""
        if isinstance(v, str):
            try:
                return SQLDialect(v.lower())
            except ValueError:
                return SQLDialect.UNKNOWN
        return v

    @validator("connection_string")
    def validate_connection_string(cls, v):
        """Validate connection string format."""
        if v:
            try:
                parsed = urlparse(v)
                if not parsed.scheme:
                    raise ValueError("Connection string must include a scheme")
                return v
            except Exception as e:
                raise ValueError(f"Invalid connection string format: {e}")
        return v

    def get_connection_params(self) -> Dict[str, Any]:
        """
        Get connection parameters as a dictionary.

        Returns:
            Dictionary of connection parameters
        """
        params = {}

        if self.host:
            params["host"] = self.host
        if self.port:
            params["port"] = self.port
        if self.database:
            params["database"] = self.database
        if self.username:
            params["username"] = self.username
        if self.password:
            params["password"] = self.password.get_secret_value()

        # Add SSL parameters
        if self.ssl_mode:
            params["sslmode"] = self.ssl_mode
        if self.ssl_cert:
            params["sslcert"] = self.ssl_cert
        if self.ssl_key:
            params["sslkey"] = self.ssl_key
        if self.ssl_ca:
            params["sslrootcert"] = self.ssl_ca

        # Add connect_args
        params.update(self.connect_args)

        return params

    def get_sqlalchemy_url(self) -> str:
        """
        Generate SQLAlchemy connection URL.

        Returns:
            SQLAlchemy connection URL
        """
        if self.connection_string:
            return self.connection_string

        if not all([self.dialect, self.host, self.database]):
            raise MetaError("Insufficient connection parameters for URL generation")

        # Build URL components
        scheme = self.dialect.value
        if self.driver:
            scheme += f"+{self.driver}"

        auth = ""
        if self.username:
            auth = self.username
            if self.password:
                auth += f":{self.password.get_secret_value()}"
            auth += "@"

        netloc = f"{auth}{self.host}"
        if self.port:
            netloc += f":{self.port}"

        url = f"{scheme}://{netloc}/{self.database}"

        return url


class SQLFilterConfig(ConfigModel):
    """
    Configuration for filtering SQL database objects during ingestion.

    Provides comprehensive filtering capabilities for tables, schemas,
    columns, and data based on patterns and conditions.
    """

    # Schema filtering
    schema_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern.allow_all,
        description="Pattern for including/excluding schemas"
    )

    include_schemas: Optional[List[str]] = Field(
        default=None,
        description="List of schema names to include (overrides schema_pattern)"
    )

    exclude_schemas: Optional[List[str]] = Field(
        default=None,
        description="List of schema names to exclude"
    )

    # Table filtering
    table_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern.allow_all,
        description="Pattern for including/excluding tables"
    )

    # View filtering
    view_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern.allow_all,
        description="Pattern for including/excluding views"
    )

    include_tables: Optional[List[str]] = Field(
        default=None,
        description="List of table names to include (schema.table format supported)"
    )

    exclude_tables: Optional[List[str]] = Field(
        default=None,
        description="List of table names to exclude (schema.table format supported)"
    )

    # Table type filtering
    include_table_types: Set[str] = Field(
        default_factory=lambda: {"BASE TABLE", "TABLE"},
        description="Set of table types to include (e.g., 'BASE TABLE', 'VIEW', 'MATERIALIZED VIEW')"
    )

    exclude_table_types: Set[str] = Field(
        default_factory=lambda: {"SYSTEM TABLE", "INFORMATION_SCHEMA"},
        description="Set of table types to exclude"
    )

    # Column filtering
    column_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern.allow_all,
        description="Pattern for including/excluding columns"
    )

    include_columns: Optional[List[str]] = Field(
        default=None,
        description="List of column names to include"
    )

    exclude_columns: Optional[List[str]] = Field(
        default=None,
        description="List of column names to exclude (e.g., sensitive columns)"
    )

    # Data filtering
    where_clause_suffix: Optional[str] = Field(
        default=None,
        description="WHERE clause to append to data extraction queries"
    )

    custom_sql_filters: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom SQL filters per table (table_name -> WHERE clause)"
    )

    # Size and sampling filters
    max_table_size_mb: Optional[float] = Field(
        default=None,
        description="Maximum table size in MB to process (None for unlimited)",
        ge=0.1
    )

    sample_percentage: Optional[float] = Field(
        default=None,
        description="Percentage of data to sample (1-100)",
        ge=0.01,
        le=100.0
    )

    sample_method: str = Field(
        default="TABLESAMPLE",
        description="Sampling method ('TABLESAMPLE', 'RANDOM', 'TOP')"
    )

    # Performance filtering
    skip_empty_tables: bool = Field(
        default=True,
        description="Skip tables with zero rows"
    )

    skip_large_tables: bool = Field(
        default=False,
        description="Skip tables exceeding max_table_size_mb"
    )

    max_rows_per_table: Optional[int] = Field(
        default=None,
        description="Maximum rows to extract per table",
        ge=1
    )

    # Metadata filtering
    include_system_schemas: bool = Field(
        default=False,
        description="Include system/internal schemas"
    )

    include_temporary_tables: bool = Field(
        default=False,
        description="Include temporary tables"
    )

    include_external_tables: bool = Field(
        default=True,
        description="Include external/federated tables"
    )

    @validator("include_schemas", "exclude_schemas", "include_tables", "exclude_tables")
    def validate_schema_table_names(cls, v):
        """Validate schema and table name formats."""
        if v:
            for name in v:
                if not isinstance(name, str) or not name.strip():
                    raise ValueError(f"Invalid schema/table name: {name}")
        return v

    @validator("sample_percentage")
    def validate_sample_percentage(cls, v):
        """Validate sample percentage is within valid range."""
        if v is not None and not (0.01 <= v <= 100.0):
            raise ValueError("Sample percentage must be between 0.01 and 100.0")
        return v

    def is_schema_allowed(self, schema_name: str) -> bool:
        """
        Check if a schema should be included based on filtering rules.

        Args:
            schema_name: Name of the schema to check

        Returns:
            True if schema should be included
        """
        # Check explicit include/exclude lists first
        if self.exclude_schemas and schema_name in self.exclude_schemas:
            return False

        if self.include_schemas:
            return schema_name in self.include_schemas

        # Check pattern-based filtering
        return self.schema_pattern.allowed(schema_name)

    def is_table_allowed(self, table_name: str, schema_name: Optional[str] = None) -> bool:
        """
        Check if a table should be included based on filtering rules.

        Args:
            table_name: Name of the table to check
            schema_name: Optional schema name for qualified table names

        Returns:
            True if table should be included
        """
        # Create fully qualified name if schema provided
        full_name = f"{schema_name}.{table_name}" if schema_name else table_name

        # Check explicit include/exclude lists
        if self.exclude_tables:
            if table_name in self.exclude_tables or full_name in self.exclude_tables:
                return False

        if self.include_tables:
            return table_name in self.include_tables or full_name in self.include_tables

        # Check pattern-based filtering
        return self.table_pattern.allowed(table_name)

    def is_table_type_allowed(self, table_type: str) -> bool:
        """
        Check if a table type should be included.

        Args:
            table_type: Type of the table (e.g., 'BASE TABLE', 'VIEW')

        Returns:
            True if table type should be included
        """
        table_type = table_type.upper()

        if table_type in self.exclude_table_types:
            return False

        return table_type in self.include_table_types

    def is_column_allowed(self, column_name: str) -> bool:
        """
        Check if a column should be included based on filtering rules.

        Args:
            column_name: Name of the column to check

        Returns:
            True if column should be included
        """
        # Check explicit include/exclude lists
        if self.exclude_columns and column_name in self.exclude_columns:
            return False

        if self.include_columns:
            return column_name in self.include_columns

        # Check pattern-based filtering
        return self.column_pattern.allowed(column_name)

    def get_table_filter_sql(self, table_name: str, schema_name: Optional[str] = None) -> Optional[str]:
        """
        Get custom SQL filter for a specific table.

        Args:
            table_name: Name of the table
            schema_name: Optional schema name

        Returns:
            SQL WHERE clause or None
        """
        full_name = f"{schema_name}.{table_name}" if schema_name else table_name

        # Check for table-specific filter first
        custom_filter = self.custom_sql_filters.get(full_name) or self.custom_sql_filters.get(table_name)

        if custom_filter:
            return custom_filter

        # Return global filter
        return self.where_clause_suffix

    def get_sampling_clause(self, dialect: SQLDialect) -> Optional[str]:
        """
        Generate sampling clause based on SQL dialect.

        Args:
            dialect: SQL dialect to generate clause for

        Returns:
            SQL sampling clause or None
        """
        if not self.sample_percentage:
            return None

        if dialect == SQLDialect.POSTGRESQL:
            return f"TABLESAMPLE BERNOULLI ({self.sample_percentage})"
        elif dialect == SQLDialect.MSSQL:
            return f"TABLESAMPLE ({self.sample_percentage} PERCENT)"
        elif dialect == SQLDialect.MYSQL:
            # MySQL doesn't have native sampling, use RAND()
            return f"ORDER BY RAND() LIMIT {int(self.sample_percentage * 1000)}"
        elif dialect == SQLDialect.SNOWFLAKE:
            return f"SAMPLE ({self.sample_percentage})"

        return None

    @classmethod
    def create_minimal_filter(
            cls,
            include_tables: Optional[List[str]] = None,
            exclude_tables: Optional[List[str]] = None
    ) -> "SQLFilterConfig":
        """
        Create a minimal filter configuration with basic table filtering.

        Args:
            include_tables: Tables to include
            exclude_tables: Tables to exclude

        Returns:
            SQLFilterConfig instance
        """
        return cls(
            include_tables=include_tables,
            exclude_tables=exclude_tables,
            skip_empty_tables=True,
            include_system_schemas=False
        )

    @classmethod
    def create_production_filter(cls) -> "SQLFilterConfig":
        """
        Create a production-ready filter configuration.

        Returns:
            SQLFilterConfig instance optimized for production
        """
        return cls(
            exclude_schemas=["information_schema", "sys", "mysql", "performance_schema"],
            exclude_table_types={"SYSTEM TABLE", "INFORMATION_SCHEMA", "SYSTEM VIEW"},
            exclude_columns=["password", "secret", "token", "key", "hash"],
            skip_empty_tables=True,
            skip_large_tables=True,
            max_table_size_mb=1000.0,
            max_rows_per_table=1000000,
            include_system_schemas=False,
            include_temporary_tables=False
        )


# Utility functions
def create_sql_config_from_url(
        connection_string: str,
        **filter_options
) -> tuple[SQLCommonConfig, SQLFilterConfig]:
    """
    Create SQL configuration objects from connection string.

    Args:
        connection_string: Database connection string
        **filter_options: Additional filtering options

    Returns:
        Tuple of (SQLCommonConfig, SQLFilterConfig)
    """
    # Parse connection string to determine dialect
    parsed = urlparse(connection_string)
    dialect = SQLDialect.UNKNOWN

    scheme_mapping = {
        "postgresql": SQLDialect.POSTGRESQL,
        "mysql": SQLDialect.MYSQL,
        "sqlite": SQLDialect.SQLITE,
        "mssql": SQLDialect.MSSQL,
        "oracle": SQLDialect.ORACLE,
        "snowflake": SQLDialect.SNOWFLAKE,
        "bigquery": SQLDialect.BIGQUERY,
        "redshift": SQLDialect.REDSHIFT,
    }

    base_scheme = parsed.scheme.split('+')[0]
    dialect = scheme_mapping.get(base_scheme, SQLDialect.UNKNOWN)

    common_config = SQLCommonConfig(
        connection_string=connection_string,
        dialect=dialect
    )

    filter_config = SQLFilterConfig(**filter_options)

    return common_config, filter_config


def validate_sql_configs(
        common_config: SQLCommonConfig,
        filter_config: SQLFilterConfig
) -> List[str]:
    """
    Validate SQL configuration objects for compatibility and completeness.

    Args:
        common_config: Common SQL configuration
        filter_config: SQL filter configuration

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Validate connection parameters
    if not common_config.connection_string:
        if not all([common_config.host, common_config.database]):
            errors.append("Either connection_string or host+database must be provided")

    # Validate filter compatibility
    if filter_config.sample_percentage and common_config.dialect == SQLDialect.SQLITE:
        errors.append("Sampling is not supported for SQLite databases")

    if filter_config.max_parallel_queries and not common_config.enable_parallel_queries:
        errors.append("max_parallel_queries specified but parallel queries are disabled")

    return errors
