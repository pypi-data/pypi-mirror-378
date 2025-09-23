"""
DataGuild Snowflake Data Reader

Provides efficient data sampling and reading capabilities for Snowflake databases
with integrated performance monitoring, error handling, and column preprocessing
for data classification and profiling workflows.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union
import pandas as pd
from contextlib import contextmanager

from dataguild.source.common.data_reader import DataReader
from dataguild.source.snowflake.connection import SnowflakeConnection
from dataguild.utilities.perf_timer import PerfTimer
from dataguild.api.report import Report

logger = logging.getLogger(__name__)


class SnowflakeDataReader(DataReader):
    """
    DataGuild Snowflake data reader for sampling and data extraction.

    Provides efficient data sampling capabilities for Snowflake tables with
    integrated performance monitoring, error handling, and column preprocessing
    support for data classification and profiling workflows.
    """

    @staticmethod
    def create(
            conn: SnowflakeConnection,
            col_name_preprocessor: Callable[[str], str],
            report: Optional[Report] = None
    ) -> "SnowflakeDataReader":
        """
        Create a SnowflakeDataReader instance.

        Args:
            conn: SnowflakeConnection instance
            col_name_preprocessor: Function to preprocess column names
            report: Optional report for tracking operations

        Returns:
            SnowflakeDataReader instance
        """
        return SnowflakeDataReader(conn, col_name_preprocessor, report)

    def __init__(
            self,
            conn: SnowflakeConnection,
            col_name_preprocessor: Callable[[str], str],
            report: Optional[Report] = None
    ) -> None:
        """
        Initialize the Snowflake data reader.

        Args:
            conn: SnowflakeConnection instance (lifecycle managed externally)
            col_name_preprocessor: Function to normalize column names
            report: Optional report for tracking operations
        """
        super().__init__()
        self.conn = conn
        self.col_name_preprocessor = col_name_preprocessor
        self.report = report
        self._samples_collected = 0
        self._total_time_seconds = 0.0

        logger.info("Initialized DataGuild SnowflakeDataReader")

    def get_sample_data_for_table(
            self,
            table_id: List[str],
            sample_size: int,
            sample_method: str = "SYSTEM",
            where_clause: Optional[str] = None,
            **kwargs: Any
    ) -> Dict[str, List[Any]]:
        """
        Get sample data for a Snowflake table.

        For Snowflake, table_id should be in the form [db_name, schema_name, table_name].

        Args:
            table_id: List containing [database, schema, table] names
            sample_size: Number of rows to sample
            sample_method: Sampling method ('SYSTEM' or 'BERNOULLI')
            where_clause: Optional WHERE clause to filter data
            **kwargs: Additional arguments

        Returns:
            Dictionary with column names as keys and lists of values

        Raises:
            ValueError: If table_id format is invalid
            Exception: If data sampling fails

        Examples:
            >>> reader = SnowflakeDataReader.create(conn, lambda x: x.lower())
            >>> sample = reader.get_sample_data_for_table(
            ...     ['ANALYTICS_DB', 'PUBLIC', 'CUSTOMERS'],
            ...     100
            ... )
            >>> print(f"Sampled {len(sample['customer_id'])} customers")
        """
        if not table_id or len(table_id) != 3:
            raise ValueError("table_id must be a list of [database, schema, table] names")

        db_name, schema_name, table_name = table_id
        qualified_name = f"{db_name}.{schema_name}.{table_name}"

        logger.debug(
            f"Collecting sample data for table {qualified_name} "
            f"(sample_size={sample_size}, method={sample_method})"
        )

        try:
            with PerfTimer() as timer:
                # Build sampling query
                quoted_table = f'"{db_name}"."{schema_name}"."{table_name}"'

                if sample_method.upper() == "SYSTEM":
                    sample_clause = f"SAMPLE SYSTEM ({sample_size} ROWS)"
                elif sample_method.upper() == "BERNOULLI":
                    # Calculate percentage for Bernoulli sampling
                    sample_percentage = min(100, max(0.1, sample_size / 1000))
                    sample_clause = f"SAMPLE BERNOULLI ({sample_percentage})"
                else:
                    # Fallback to LIMIT for simple sampling
                    sample_clause = f"LIMIT {sample_size}"

                # Construct the complete query
                base_query = f"SELECT * FROM {quoted_table}"
                if where_clause:
                    base_query += f" WHERE {where_clause}"

                sql_query = f"{base_query} {sample_clause}"

                # Execute query and fetch data
                result_data = self._execute_sampling_query(sql_query, qualified_name)

                # Process results
                if result_data:
                    # Convert to DataFrame for easier processing
                    df = pd.DataFrame(
                        result_data['data'],
                        columns=result_data['columns']
                    )

                    # Apply column name preprocessing
                    df.columns = [
                        self.col_name_preprocessor(col) for col in df.columns
                    ]

                    # Convert back to dictionary format
                    sample_dict = df.to_dict(orient="list")

                    # Update statistics
                    elapsed_time = timer.elapsed_seconds()
                    self._samples_collected += 1
                    self._total_time_seconds += elapsed_time

                    # Log results
                    logger.debug(
                        f"Successfully collected sample data for {qualified_name}: "
                        f"{len(df)} rows, {len(df.columns)} columns, "
                        f"took {elapsed_time:.3f} seconds"
                    )

                    # Report to structured reporter if available
                    if self.report:
                        self.report.report_entity_scanned(
                            qualified_name,
                            "table_sample",
                            {"rows": len(df), "columns": len(df.columns)}
                        )

                    return sample_dict
                else:
                    logger.warning(f"No data returned for table {qualified_name}")
                    return {}

        except Exception as e:
            error_msg = f"Failed to collect sample data for table {qualified_name}: {e}"
            logger.error(error_msg, exc_info=True)

            if self.report:
                self.report.report_failure(
                    "table_sampling_failed",
                    qualified_name,
                    exc=e
                )

            raise Exception(error_msg) from e

    def _execute_sampling_query(
            self,
            sql_query: str,
            table_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Execute the sampling query against Snowflake.

        Args:
            sql_query: SQL query to execute
            table_name: Table name for logging

        Returns:
            Dictionary with 'data' and 'columns' keys, or None if no results
        """
        try:
            with self.conn.get_cursor() as cursor:
                logger.debug(f"Executing sampling query for {table_name}: {sql_query}")

                cursor.execute(sql_query)
                rows = cursor.fetchall()

                if not rows:
                    logger.warning(f"No rows returned from sampling query for {table_name}")
                    return None

                # Extract column names from cursor description
                column_names = [desc[0] for desc in cursor.description]

                return {
                    'data': rows,
                    'columns': column_names
                }

        except Exception as e:
            logger.error(f"Query execution failed for {table_name}: {e}")
            raise

    def get_sample_data_for_column(
            self,
            table_id: List[str],
            column_name: str,
            sample_size: int,
            distinct_only: bool = False,
            **kwargs: Any
    ) -> List[Any]:
        """
        Get sample data for a specific column.

        Args:
            table_id: List containing [database, schema, table] names
            column_name: Name of the column to sample
            sample_size: Number of values to sample
            distinct_only: Whether to return only distinct values
            **kwargs: Additional arguments

        Returns:
            List of sampled column values
        """
        if not table_id or len(table_id) != 3:
            raise ValueError("table_id must be a list of [database, schema, table] names")

        db_name, schema_name, table_name = table_id
        qualified_name = f"{db_name}.{schema_name}.{table_name}"

        logger.debug(
            f"Collecting sample data for column {column_name} "
            f"in table {qualified_name} (sample_size={sample_size})"
        )

        try:
            with PerfTimer() as timer:
                # Build column-specific sampling query
                quoted_table = f'"{db_name}"."{schema_name}"."{table_name}"'
                quoted_column = f'"{column_name}"'

                distinct_clause = "DISTINCT " if distinct_only else ""
                base_query = f"SELECT {distinct_clause}{quoted_column} FROM {quoted_table}"

                # Add sampling and limits
                sql_query = f"{base_query} SAMPLE SYSTEM ({sample_size * 2} ROWS) LIMIT {sample_size}"

                # Execute query
                with self.conn.get_cursor() as cursor:
                    cursor.execute(sql_query)
                    rows = cursor.fetchall()

                    # Extract column values
                    values = [row[0] for row in rows if row[0] is not None]

                    elapsed_time = timer.elapsed_seconds()
                    logger.debug(
                        f"Collected {len(values)} values for column {column_name} "
                        f"in {elapsed_time:.3f} seconds"
                    )

                    return values

        except Exception as e:
            error_msg = f"Failed to collect column sample for {column_name} in {qualified_name}: {e}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e

    def test_connection(self) -> bool:
        """
        Test the Snowflake connection.

        Returns:
            True if connection is working, False otherwise
        """
        try:
            with self.conn.get_cursor() as cursor:
                cursor.execute("SELECT 1 as test_value")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_table_row_count(self, table_id: List[str]) -> Optional[int]:
        """
        Get approximate row count for a table.

        Args:
            table_id: List containing [database, schema, table] names

        Returns:
            Approximate row count or None if failed
        """
        if not table_id or len(table_id) != 3:
            raise ValueError("table_id must be a list of [database, schema, table] names")

        db_name, schema_name, table_name = table_id
        qualified_name = f"{db_name}.{schema_name}.{table_name}"

        try:
            quoted_table = f'"{db_name}"."{schema_name}"."{table_name}"'
            sql_query = f"SELECT COUNT(*) FROM {quoted_table}"

            with self.conn.get_cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchone()
                return result[0] if result else None

        except Exception as e:
            logger.warning(f"Failed to get row count for {qualified_name}: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get reader statistics.

        Returns:
            Dictionary with reader statistics
        """
        return {
            "samples_collected": self._samples_collected,
            "total_time_seconds": self._total_time_seconds,
            "average_time_per_sample": (
                self._total_time_seconds / self._samples_collected
                if self._samples_collected > 0 else 0.0
            ),
            "connection_active": self.test_connection(),
        }

    @contextmanager
    def batch_sampling_context(self, batch_size: int = 10):
        """
        Context manager for batch sampling operations.

        Args:
            batch_size: Number of tables to sample in batch
        """
        batch_start_time = PerfTimer()
        batch_start_time.__enter__()

        try:
            logger.info(f"Starting batch sampling context (batch_size={batch_size})")
            yield self

        finally:
            elapsed = batch_start_time.elapsed_seconds()
            logger.info(f"Completed batch sampling in {elapsed:.2f} seconds")
            batch_start_time.__exit__(None, None, None)

    def close(self) -> None:
        """
        Close the data reader and clean up resources.

        Note: The SnowflakeConnection lifecycle is managed externally,
        so we don't close it here.
        """
        logger.debug(
            f"Closing SnowflakeDataReader. "
            f"Statistics: {self.get_statistics()}"
        )

        # Reset internal counters
        self._samples_collected = 0
        self._total_time_seconds = 0.0

        logger.info("Closed DataGuild SnowflakeDataReader")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the data reader."""
        stats = self.get_statistics()
        return (
            f"SnowflakeDataReader("
            f"samples_collected={stats['samples_collected']}, "
            f"total_time={stats['total_time_seconds']:.2f}s, "
            f"connection_active={stats['connection_active']}"
            f")"
        )


# Export the main class
__all__ = ['SnowflakeDataReader']
