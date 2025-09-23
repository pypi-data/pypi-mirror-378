"""
DataGuild Snowflake connection management.

This module provides simplified connection handling for Snowflake instances
with basic username/password authentication and comprehensive error handling.
"""

import logging
import threading
from typing import Any, Dict, Optional, List
from urllib.parse import quote_plus

import pydantic
import snowflake.connector
from snowflake.connector import SnowflakeConnection as NativeSnowflakeConnection
from snowflake.connector.cursor import DictCursor
from snowflake.connector.errors import ProgrammingError, DatabaseError
# from snowflake.connector.network import DEFAULT_AUTHENTICATOR  # Removed to prevent AWS metadata service calls

from dataguild.configuration.common import ConfigModel, ConfigurationError, MetaError
from dataguild.api.closeable import Closeable
from dataguild.source.snowflake.constants import (
    CLIENT_PREFETCH_THREADS,
    CLIENT_SESSION_KEEP_ALIVE,
    DEFAULT_SNOWFLAKE_DOMAIN,
)
from dataguild.utilities.config_clean import (
    remove_protocol,
    remove_suffix,
    remove_trailing_slashes,
)

logger = logging.getLogger(__name__)

_APPLICATION_NAME: str = "dataguild"


class SnowflakePermissionError(MetaError):
    """A permission error has occurred when accessing Snowflake."""
    pass


class SnowflakeConnectionError(ConfigurationError):
    """A connection error has occurred when connecting to Snowflake."""
    pass


class SnowflakeConnectionConfig(ConfigModel):
    """
    Configuration for Snowflake database connections.

    This simplified configuration supports basic username/password authentication
    with optional warehouse and role specification.
    """

    # Basic connection parameters
    scheme: str = pydantic.Field(
        default="snowflake",
        description="Database scheme (always 'snowflake')"
    )

    username: str = pydantic.Field(
        description="Snowflake username for authentication"
    )

    password: pydantic.SecretStr = pydantic.Field(
        description="Snowflake password for authentication"
    )

    account_id: str = pydantic.Field(
        description=(
            "Snowflake account identifier. Examples: xy12345, xy12345.us-east-2.aws, "
            "xy12345.us-central1.gcp, xy12345.central-us.azure. "
            "See Snowflake documentation for Account Identifiers."
        )
    )

    # Optional connection parameters
    warehouse: Optional[str] = pydantic.Field(
        default=None,
        description="Default warehouse to use for queries"
    )

    role: Optional[str] = pydantic.Field(
        default=None,
        description="Default role to assume when connecting"
    )

    database: Optional[str] = pydantic.Field(
        default=None,
        description="Default database to connect to"
    )

    # ✅ FIXED: Use alias to avoid BaseModel attribute shadowing
    schema_: Optional[str] = pydantic.Field(
        default=None,
        alias='schema',
        description="Default schema to use"
    )

    snowflake_domain: str = pydantic.Field(
        default=DEFAULT_SNOWFLAKE_DOMAIN,
        description=(
            "Snowflake domain. Use 'snowflakecomputing.com' for most regions "
            "or 'snowflakecomputing.cn' for China (cn-northwest-1) region."
        )
    )

    # Connection options
    connect_args: Optional[Dict[str, Any]] = pydantic.Field(
        default=None,
        description="Additional connection arguments to pass to Snowflake connector"
    )

    options: Dict[str, Any] = pydantic.Field(
        default_factory=dict,
        description="Additional connection options"
    )

    # Connection timeouts and settings
    login_timeout: Optional[int] = pydantic.Field(
        default=60,
        description="Login timeout in seconds"
    )

    network_timeout: Optional[int] = pydantic.Field(
        default=300,
        description="Network timeout in seconds"
    )

    class Config:
        """Pydantic configuration for enhanced functionality."""
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = "forbid"
        use_enum_values = True
        validate_all = True
        allow_population_by_field_name = True  # ✅ ADDED: Enable alias usage

    @pydantic.validator("account_id")
    def validate_account_id(cls, account_id: str, values: Dict) -> str:
        """Clean and validate the account ID."""
        account_id = remove_protocol(account_id)
        account_id = remove_trailing_slashes(account_id)

        # Get the domain from config, fallback to default
        domain = values.get("snowflake_domain", DEFAULT_SNOWFLAKE_DOMAIN)
        snowflake_host_suffix = f".{domain}"
        account_id = remove_suffix(account_id, snowflake_host_suffix)

        if not account_id:
            raise ValueError("account_id cannot be empty after processing")

        return account_id

    def get_account(self) -> str:
        """Get the processed account identifier."""
        return self.account_id

    def get_host(self) -> str:
        """Get the full Snowflake host name."""
        return f"{self.account_id}.{self.snowflake_domain}"

    def get_connect_args(self) -> Dict[str, Any]:
        """
        Get connection arguments for the Snowflake connector.

        Returns:
            Dictionary of connection arguments with performance optimizations
        """
        connect_args: Dict[str, Any] = {
            # Performance optimizations
            CLIENT_PREFETCH_THREADS: 10,
            CLIENT_SESSION_KEEP_ALIVE: True,

            # Timeouts
            "login_timeout": self.login_timeout,
            "network_timeout": self.network_timeout,

            # Application identification
            "application": _APPLICATION_NAME,

            # User-provided overrides
            **(self.connect_args or {}),
        }

        return connect_args

    def get_connection_params(self) -> Dict[str, Any]:
        """
        Get all connection parameters for Snowflake connector.

        Returns:
            Dictionary of connection parameters
        """
        params = {
            "user": self.username,
            "password": self.password.get_secret_value(),
            "account": self.account_id,
            "host": self.get_host(),
            "authenticator": "snowflake",  # Explicitly use username/password authentication
        }

        # Add optional parameters
        if self.warehouse:
            params["warehouse"] = self.warehouse
        if self.role:
            params["role"] = self.role
        if self.database:
            params["database"] = self.database
        if self.schema_:  # ✅ FIXED: Changed from self.schema
            params["schema"] = self.schema_  # ✅ FIXED: Changed from self.schema

        # Add connection arguments
        params.update(self.get_connect_args())

        return params

    def get_native_connection(self) -> NativeSnowflakeConnection:
        """
        Create and return a native Snowflake connection.

        Returns:
            Native Snowflake connection instance

        Raises:
            SnowflakeConnectionError: If connection fails
            SnowflakePermissionError: If authentication fails
        """
        try:
            connection_params = self.get_connection_params()
            logger.info(f"Connecting to Snowflake account: {self.account_id}")

            connection = snowflake.connector.connect(**connection_params)

            logger.info(f"Successfully connected to Snowflake as {self.username}")
            return connection

        except ProgrammingError as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in [
                "insufficient privileges",
                "not authorized",
                "access denied",
                "permission denied"
            ]):
                raise SnowflakePermissionError(
                    f"Permission denied when connecting to Snowflake: {e}"
                ) from e
            else:
                raise SnowflakeConnectionError(
                    f"Failed to connect to Snowflake: {e}"
                ) from e

        except DatabaseError as e:
            raise SnowflakeConnectionError(
                f"Database error when connecting to Snowflake: {e}"
            ) from e

        except Exception as e:
            logger.debug(f"Connection error details: {e}", exc_info=True)
            raise SnowflakeConnectionError(
                f"Unexpected error when connecting to Snowflake: {e}"
            ) from e

    def get_connection(self) -> "SnowflakeConnection":
        """
        Get a wrapped Snowflake connection with additional functionality.

        Returns:
            SnowflakeConnection wrapper instance
        """
        native_conn = self.get_native_connection()
        return SnowflakeConnection(native_conn)

    def test_connection(self) -> bool:
        """
        Test the Snowflake connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            conn = self.get_connection()
            # Execute a simple query to verify connection
            result = conn.query("SELECT 1 as test")
            conn.close()
            return result is not None
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            return False

    def get_sqlalchemy_url(self, database: Optional[str] = None) -> str:
        """
        Generate SQLAlchemy connection URL.

        Args:
            database: Optional database name to include in URL

        Returns:
            SQLAlchemy connection URL string
        """
        # Build the basic URL
        password = quote_plus(self.password.get_secret_value())
        url = f"snowflake://{self.username}:{password}@{self.account_id}"

        if database:
            url += f"/{database}"

        # Add query parameters
        params = []
        if self.warehouse:
            params.append(f"warehouse={quote_plus(self.warehouse)}")
        if self.role:
            params.append(f"role={quote_plus(self.role)}")
        if self.schema_:  # ✅ FIXED: Changed from self.schema
            params.append(f"schema={quote_plus(self.schema_)}")  # ✅ FIXED

        params.append(f"application={quote_plus(_APPLICATION_NAME)}")

        if params:
            url += "?" + "&".join(params)

        return url


class SnowflakeConnection(Closeable):
    """
    Wrapper around native Snowflake connection with additional functionality.

    This class provides query execution, error handling, logging, and
    thread-safe operation management for Snowflake connections.
    """

    def __init__(self, connection: NativeSnowflakeConnection):
        """
        Initialize the connection wrapper.

        Args:
            connection: Native Snowflake connection instance
        """
        self._connection = connection
        self._query_num_lock = threading.Lock()
        self._query_num = 1
        self._is_closed = False

        logger.debug("Initialized SnowflakeConnection wrapper")

    def native_connection(self) -> NativeSnowflakeConnection:
        """
        Get the underlying native Snowflake connection.

        Returns:
            Native Snowflake connection instance
        """
        return self._connection

    def get_query_number(self) -> int:
        """
        Get a unique query number for logging purposes.

        Returns:
            Unique query number (thread-safe)
        """
        with self._query_num_lock:
            query_num = self._query_num
            self._query_num += 1
            return query_num

    def query(self, query: str, timeout: Optional[int] = None) -> Any:
        """
        Execute a SQL query on the Snowflake connection.

        Args:
            query: SQL query string to execute
            timeout: Optional query timeout in seconds

        Returns:
            Query result cursor

        Raises:
            SnowflakePermissionError: If insufficient permissions
            Exception: For other query execution errors
        """
        if self._is_closed:
            raise SnowflakeConnectionError("Connection is closed")

        query_num = self.get_query_number()

        try:
            cleaned_query = query.strip()

            logger.info(f"Query #{query_num}: {cleaned_query[:100]}{'...' if len(cleaned_query) > 100 else ''}")

            # Create cursor with dictionary format for easier result handling
            cursor = self._connection.cursor(DictCursor)

            # Set timeout if provided
            if timeout:
                cursor.execute(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = {timeout}")

            # Execute the query
            result = cursor.execute(query)

            # Log result information
            if result is not None and hasattr(result, 'rowcount') and result.rowcount is not None:
                logger.info(f"Query #{query_num} returned {result.rowcount} rows")
            else:
                logger.info(f"Query #{query_num} executed successfully")

            return result

        except Exception as e:
            logger.error(f"Query #{query_num} failed: {str(e)}")

            if _is_permission_error(e):
                raise SnowflakePermissionError(f"Permission error executing query: {e}") from e

            # Re-raise other exceptions as-is
            raise

    def execute(self, query: str, timeout: Optional[int] = None) -> Any:
        """
        Execute a SQL query on the Snowflake connection - alias for query method.

        Args:
            query: SQL query string to execute
            timeout: Optional query timeout in seconds

        Returns:
            Query result cursor

        Raises:
            SnowflakePermissionError: If insufficient permissions
            Exception: For other query execution errors
        """
        return self.query(query, timeout)

    def execute_batch(self, queries: List[str], stop_on_error: bool = True) -> List[Any]:
        """
        Execute multiple queries in sequence.

        Args:
            queries: List of SQL query strings
            stop_on_error: Whether to stop execution on first error

        Returns:
            List of query results
        """
        results = []

        for i, query in enumerate(queries):
            try:
                result = self.query(query)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch query {i+1} failed: {e}")
                if stop_on_error:
                    raise
                results.append(None)

        return results

    def get_current_warehouse(self) -> Optional[str]:
        """Get the current warehouse name."""
        try:
            result = self.query("SELECT CURRENT_WAREHOUSE() as warehouse")
            row = result.fetchone()
            return row['WAREHOUSE'] if row else None
        except Exception as e:
            logger.warning(f"Failed to get current warehouse: {e}")
            return None

    def get_current_role(self) -> Optional[str]:
        """Get the current role name."""
        try:
            result = self.query("SELECT CURRENT_ROLE() as role")
            row = result.fetchone()
            return row['ROLE'] if row else None
        except Exception as e:
            logger.warning(f"Failed to get current role: {e}")
            return None

    def get_current_database(self) -> Optional[str]:
        """Get the current database name."""
        try:
            result = self.query("SELECT CURRENT_DATABASE() as database")
            row = result.fetchone()
            return row['DATABASE'] if row else None
        except Exception as e:
            logger.warning(f"Failed to get current database: {e}")
            return None

    def get_current_schema(self) -> Optional[str]:
        """Get the current schema name."""
        try:
            result = self.query("SELECT CURRENT_SCHEMA() as schema")
            row = result.fetchone()
            return row['SCHEMA'] if row else None
        except Exception as e:
            logger.warning(f"Failed to get current schema: {e}")
            return None

    def use_warehouse(self, warehouse: str) -> None:
        """Switch to a different warehouse."""
        self.query(f'USE WAREHOUSE "{warehouse}"')
        logger.info(f"Switched to warehouse: {warehouse}")

    def use_role(self, role: str) -> None:
        """Switch to a different role."""
        self.query(f'USE ROLE "{role}"')
        logger.info(f"Switched to role: {role}")

    def use_database(self, database: str) -> None:
        """Switch to a different database."""
        self.query(f'USE DATABASE "{database}"')
        logger.info(f"Switched to database: {database}")

    def use_schema(self, schema: str) -> None:
        """Switch to a different schema."""
        self.query(f'USE SCHEMA "{schema}"')
        logger.info(f"Switched to schema: {schema}")

    def is_closed(self) -> bool:
        """
        Check if the connection is closed.

        Returns:
            True if connection is closed, False otherwise
        """
        return self._is_closed or self._connection.is_closed()

    def close(self) -> None:
        """Close the Snowflake connection."""
        if not self._is_closed:
            try:
                self._connection.close()
                logger.info("Snowflake connection closed successfully")
            except Exception as e:
                logger.warning(f"Error closing Snowflake connection: {e}")
            finally:
                self._is_closed = True

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def _is_permission_error(e: Exception) -> bool:
    """
    Check if an exception represents a permission error.

    Args:
        e: Exception to check

    Returns:
        True if the exception indicates a permission error
    """
    msg = str(e).lower()

    permission_indicators = [
        "insufficient privileges",
        "not authorized",
        "access denied",
        "permission denied",
        "does not exist or not authorized",
        "not granted to this user",
        "unauthorized",
    ]

    return any(indicator in msg for indicator in permission_indicators)


# Factory functions and utilities
def create_snowflake_connection(
    username: str,
    password: str,
    account_id: str,
    warehouse: Optional[str] = None,
    role: Optional[str] = None,
    database: Optional[str] = None,
    schema: Optional[str] = None,  # External API still uses 'schema'
    **kwargs
) -> SnowflakeConnection:
    """
    Factory function to create a Snowflake connection.

    Args:
        username: Snowflake username
        password: Snowflake password
        account_id: Snowflake account identifier
        warehouse: Optional warehouse name
        role: Optional role name
        database: Optional database name
        schema: Optional schema name
        **kwargs: Additional connection parameters

    Returns:
        SnowflakeConnection instance
    """
    config = SnowflakeConnectionConfig(
        username=username,
        password=password,
        account_id=account_id,
        warehouse=warehouse,
        role=role,
        database=database,
        schema=schema,  # This maps to schema_ via alias
        **kwargs
    )

    return config.get_connection()


def test_snowflake_connection(config: SnowflakeConnectionConfig) -> Dict[str, Any]:
    """
    Test a Snowflake connection and return diagnostic information.

    Args:
        config: Snowflake connection configuration

    Returns:
        Dictionary with connection test results
    """
    test_result = {
        "success": False,
        "error": None,
        "connection_info": {},
        "permissions": {},
    }

    try:
        with config.get_connection() as conn:
            # Test basic connection
            conn.query("SELECT 1")
            test_result["success"] = True

            # Get connection information
            test_result["connection_info"] = {
                "current_warehouse": conn.get_current_warehouse(),
                "current_role": conn.get_current_role(),
                "current_database": conn.get_current_database(),
                "current_schema": conn.get_current_schema(),
            }

            # Test basic permissions
            try:
                conn.query("SHOW DATABASES")
                test_result["permissions"]["show_databases"] = True
            except:
                test_result["permissions"]["show_databases"] = False

            try:
                conn.query("SELECT CURRENT_ACCOUNT()")
                test_result["permissions"]["account_info"] = True
            except:
                test_result["permissions"]["account_info"] = False

    except Exception as e:
        test_result["error"] = str(e)
        test_result["error_type"] = type(e).__name__

    return test_result


# Connection pool management (basic implementation)
class SnowflakeConnectionPool:
    """Simple connection pool for Snowflake connections."""

    def __init__(self, config: SnowflakeConnectionConfig, max_connections: int = 5):
        self.config = config
        self.max_connections = max_connections
        self._pool: List[SnowflakeConnection] = []
        self._pool_lock = threading.Lock()

    def get_connection(self) -> SnowflakeConnection:
        """Get a connection from the pool or create a new one."""
        with self._pool_lock:
            if self._pool:
                return self._pool.pop()

        return self.config.get_connection()

    def return_connection(self, conn: SnowflakeConnection) -> None:
        """Return a connection to the pool."""
        if not conn.is_closed():
            with self._pool_lock:
                if len(self._pool) < self.max_connections:
                    self._pool.append(conn)
                    return

        # Close the connection if pool is full
        conn.close()

    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._pool_lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()
