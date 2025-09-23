"""
DataGuild Common Data Reader

Base class for all data readers in the DataGuild ingestion framework.
Provides common interfaces and functionality for reading sample data
from various data sources for classification, profiling, and analysis.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Set
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from dataguild.api.report import Report
from dataguild.utilities.perf_timer import PerfTimer

logger = logging.getLogger(__name__)


@dataclass
class SamplingConfig:
    """Configuration for data sampling operations."""
    sample_size: int = 1000
    sample_method: str = "RANDOM"
    max_column_length: int = 1000
    include_nulls: bool = True
    distinct_only: bool = False
    timeout_seconds: int = 300


@dataclass
class SamplingResult:
    """Result from a data sampling operation."""
    table_id: List[str]
    data: Dict[str, List[Any]]
    row_count: int
    column_count: int
    sampling_time_seconds: float
    sampling_method: str
    metadata: Dict[str, Any]


class DataReaderError(Exception):
    """Base exception for DataReader errors."""
    pass


class DataReader(ABC):
    """
    Abstract base class for all DataGuild data readers.

    Provides common interfaces and functionality for reading sample data
    from various data sources including databases, data warehouses, and files.
    Used primarily for data classification, profiling, and quality assessment.
    """

    def __init__(
            self,
            connection: Any,
            report: Optional[Report] = None,
            config: Optional[SamplingConfig] = None
    ):
        """
        Initialize the data reader.

        Args:
            connection: Connection object to the data source
            report: Optional report for tracking operations
            config: Optional sampling configuration
        """
        self.connection = connection
        self.report = report
        self.config = config or SamplingConfig()

        # Statistics tracking
        self._samples_collected = 0
        self._total_sampling_time = 0.0
        self._errors_encountered = 0
        self._start_time = datetime.now()

        logger.debug(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def get_sample_data_for_table(
            self,
            table_id: List[str],
            sample_size: int,
            **kwargs: Any
    ) -> Dict[str, List[Any]]:
        """
        Get sample data for a specified table.

        This is the main method that must be implemented by all subclasses
        to provide table sampling functionality specific to their data source.

        Args:
            table_id: Identifier for the table (format varies by source)
            sample_size: Number of rows to sample
            **kwargs: Additional source-specific arguments

        Returns:
            Dictionary with column names as keys and lists of values as values

        Raises:
            DataReaderError: If sampling fails
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_sample_data_for_table"
        )

    def get_sample_data_for_column(
            self,
            table_id: List[str],
            column_name: str,
            sample_size: int,
            **kwargs: Any
    ) -> List[Any]:
        """
        Get sample data for a specific column.

        Default implementation calls get_sample_data_for_table and extracts
        the specified column. Subclasses can override for more efficient
        column-specific sampling.

        Args:
            table_id: Identifier for the table
            column_name: Name of the column to sample
            sample_size: Number of values to sample
            **kwargs: Additional arguments

        Returns:
            List of sampled column values
        """
        try:
            table_data = self.get_sample_data_for_table(
                table_id, sample_size, **kwargs
            )

            if column_name in table_data:
                return table_data[column_name]
            else:
                available_columns = list(table_data.keys())
                raise DataReaderError(
                    f"Column '{column_name}' not found. "
                    f"Available columns: {available_columns}"
                )

        except Exception as e:
            self._handle_error(f"Column sampling failed for {column_name}", e)
            raise DataReaderError(f"Failed to sample column {column_name}: {e}") from e

    def get_table_schema(self, table_id: List[str]) -> Dict[str, str]:
        """
        Get schema information for a table.

        Default implementation returns empty dict. Subclasses should override
        to provide actual schema information when available.

        Args:
            table_id: Identifier for the table

        Returns:
            Dictionary mapping column names to data types
        """
        logger.debug(f"Schema information not available for {table_id}")
        return {}

    def validate_table_access(self, table_id: List[str]) -> bool:
        """
        Validate that the table can be accessed for sampling.

        Default implementation returns True. Subclasses can override
        to implement actual access validation.

        Args:
            table_id: Identifier for the table

        Returns:
            True if table can be accessed, False otherwise
        """
        return True

    def get_table_row_count(self, table_id: List[str]) -> Optional[int]:
        """
        Get the total number of rows in a table.

        Default implementation returns None. Subclasses should override
        to provide actual row count when efficient methods are available.

        Args:
            table_id: Identifier for the table

        Returns:
            Number of rows or None if not available
        """
        return None

    def test_connection(self) -> bool:
        """
        Test if the connection to the data source is working.

        Default implementation returns True. Subclasses should override
        to implement actual connection testing.

        Returns:
            True if connection is working, False otherwise
        """
        return True

    def get_available_tables(self) -> List[List[str]]:
        """
        Get list of available tables for sampling.

        Default implementation returns empty list. Subclasses should override
        to provide actual table discovery when supported.

        Returns:
            List of table identifiers
        """
        return []

    def sample_multiple_tables(
            self,
            table_ids: List[List[str]],
            sample_size: int,
            **kwargs: Any
    ) -> Dict[str, Dict[str, List[Any]]]:
        """
        Sample data from multiple tables in batch.

        Default implementation calls get_sample_data_for_table for each table.
        Subclasses can override for more efficient batch processing.

        Args:
            table_ids: List of table identifiers
            sample_size: Number of rows to sample per table
            **kwargs: Additional arguments

        Returns:
            Dictionary mapping table names to sample data
        """
        results = {}

        for table_id in table_ids:
            try:
                table_key = self._format_table_key(table_id)
                sample_data = self.get_sample_data_for_table(
                    table_id, sample_size, **kwargs
                )
                results[table_key] = sample_data

            except Exception as e:
                error_msg = f"Failed to sample table {table_id}: {e}"
                logger.warning(error_msg)
                if self.report:
                    self.report.report_failure("table_sampling", table_id, exc=e)

        return results

    @contextmanager
    def batch_sampling_context(self, batch_size: int = 10):
        """
        Context manager for batch sampling operations.

        Args:
            batch_size: Suggested batch size for operations
        """
        batch_timer = PerfTimer()
        batch_timer.__enter__()

        try:
            logger.info(f"Starting batch sampling context (batch_size={batch_size})")
            yield self

        except Exception as e:
            logger.error(f"Error in batch sampling context: {e}")
            raise

        finally:
            elapsed = batch_timer.elapsed_seconds()
            logger.info(f"Completed batch sampling context in {elapsed:.2f} seconds")
            batch_timer.__exit__(None, None, None)

    def get_sampling_result(
            self,
            table_id: List[str],
            sample_size: int,
            **kwargs: Any
    ) -> SamplingResult:
        """
        Get comprehensive sampling result with metadata.

        Args:
            table_id: Identifier for the table
            sample_size: Number of rows to sample
            **kwargs: Additional arguments

        Returns:
            SamplingResult with data and metadata
        """
        with PerfTimer() as timer:
            try:
                # Get sample data
                data = self.get_sample_data_for_table(table_id, sample_size, **kwargs)

                # Calculate metrics
                row_count = len(next(iter(data.values()))) if data else 0
                column_count = len(data)
                sampling_time = timer.elapsed_seconds()

                # Update statistics
                self._samples_collected += 1
                self._total_sampling_time += sampling_time

                return SamplingResult(
                    table_id=table_id,
                    data=data,
                    row_count=row_count,
                    column_count=column_count,
                    sampling_time_seconds=sampling_time,
                    sampling_method=kwargs.get('sample_method', 'DEFAULT'),
                    metadata={
                        'reader_type': self.__class__.__name__,
                        'config': self.config.__dict__,
                        'timestamp': datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                self._handle_error(f"Sampling failed for table {table_id}", e)
                raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the data reader's operations.

        Returns:
            Dictionary containing various statistics and metrics
        """
        uptime = (datetime.now() - self._start_time).total_seconds()

        return {
            "reader_type": self.__class__.__name__,
            "samples_collected": self._samples_collected,
            "total_sampling_time_seconds": self._total_sampling_time,
            "average_sampling_time_seconds": (
                self._total_sampling_time / self._samples_collected
                if self._samples_collected > 0 else 0.0
            ),
            "errors_encountered": self._errors_encountered,
            "uptime_seconds": uptime,
            "samples_per_minute": (
                self._samples_collected / (uptime / 60)
                if uptime > 0 else 0.0
            ),
            "connection_active": self.test_connection(),
            "config": self.config.__dict__,
        }

    def reset_statistics(self) -> None:
        """Reset internal statistics counters."""
        self._samples_collected = 0
        self._total_sampling_time = 0.0
        self._errors_encountered = 0
        self._start_time = datetime.now()
        logger.debug("Reset data reader statistics")

    def _handle_error(self, message: str, exception: Exception) -> None:
        """
        Handle and log errors consistently.

        Args:
            message: Error message
            exception: The exception that occurred
        """
        self._errors_encountered += 1
        logger.error(f"{message}: {exception}", exc_info=True)

        if self.report:
            self.report.report_failure("data_reader_error", message, exc=exception)

    def _format_table_key(self, table_id: List[str]) -> str:
        """
        Format a table identifier as a string key.

        Args:
            table_id: Table identifier

        Returns:
            String representation of the table identifier
        """
        return ".".join(str(part) for part in table_id)

    def _validate_sample_size(self, sample_size: int) -> int:
        """
        Validate and normalize sample size.

        Args:
            sample_size: Requested sample size

        Returns:
            Validated sample size

        Raises:
            ValueError: If sample size is invalid
        """
        if sample_size <= 0:
            raise ValueError(f"Sample size must be positive, got {sample_size}")

        max_sample_size = getattr(self.config, 'max_sample_size', 100000)
        if sample_size > max_sample_size:
            logger.warning(
                f"Sample size {sample_size} exceeds maximum {max_sample_size}, "
                f"capping at maximum"
            )
            return max_sample_size

        return sample_size

    def close(self) -> None:
        """
        Close the data reader and clean up resources.

        Default implementation logs statistics. Subclasses should override
        to implement actual resource cleanup.
        """
        stats = self.get_statistics()
        logger.info(
            f"Closing {self.__class__.__name__}. "
            f"Final statistics: {stats['samples_collected']} samples, "
            f"{stats['total_sampling_time_seconds']:.2f}s total time, "
            f"{stats['errors_encountered']} errors"
        )

    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()

        if exc_type is not None:
            logger.error(
                f"Exception in {self.__class__.__name__} context: "
                f"{exc_type.__name__}: {exc_val}"
            )

    def __repr__(self) -> str:
        """String representation of the data reader."""
        stats = self.get_statistics()
        return (
            f"{self.__class__.__name__}("
            f"samples_collected={stats['samples_collected']}, "
            f"uptime={stats['uptime_seconds']:.1f}s, "
            f"connection_active={stats['connection_active']}"
            f")"
        )


# Utility functions for data readers

def validate_table_id_format(table_id: List[str], expected_parts: int) -> None:
    """
    Validate table ID format.

    Args:
        table_id: Table identifier to validate
        expected_parts: Expected number of parts in the identifier

    Raises:
        ValueError: If format is invalid
    """
    if not table_id or len(table_id) != expected_parts:
        raise ValueError(
            f"table_id must have exactly {expected_parts} parts, "
            f"got {len(table_id) if table_id else 0}: {table_id}"
        )


def normalize_column_name(column_name: str) -> str:
    """
    Normalize column name for consistent handling.

    Args:
        column_name: Original column name

    Returns:
        Normalized column name
    """
    if not column_name:
        return column_name

    # Convert to lowercase and replace special characters
    import re
    normalized = re.sub(r'[^\w]', '_', column_name.lower())
    normalized = re.sub(r'_+', '_', normalized)
    normalized = normalized.strip('_')

    return normalized


def create_sampling_config(**kwargs) -> SamplingConfig:
    """
    Create a sampling configuration with custom parameters.

    Args:
        **kwargs: Configuration parameters

    Returns:
        SamplingConfig instance
    """
    return SamplingConfig(**kwargs)


# Export all classes and functions
__all__ = [
    'DataReader',
    'DataReaderError',
    'SamplingConfig',
    'SamplingResult',
    'validate_table_id_format',
    'normalize_column_name',
    'create_sampling_config',
]
