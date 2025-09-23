"""
DataGuild SQL Generic Profiler

Base profiler class for SQL-based data sources with comprehensive
profiling capabilities, sampling strategies, and performance monitoring.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, Set
from dataclasses import dataclass

from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.sql.sql_generic import BaseTable, Database, DatabaseSchema
from dataguild.source.state.profiling_state_handler import ProfilingHandler
from dataguild.metadata.schemas import MetadataEvent, MetadataEventType, MetadataEventSeverity
from dataguild.utilities.perf_timer import PerfTimer

logger = logging.getLogger(__name__)


@dataclass
class ProfileRequest:
    """Request for profiling a specific table."""
    table: BaseTable
    schema_name: str
    database_name: str
    pretty_name: str
    profile_options: Dict[str, Any]

    def __post_init__(self):
        """Validate profile request."""
        if not self.table:
            raise ValueError("Table is required for profile request")
        if not self.schema_name:
            raise ValueError("Schema name is required")
        if not self.database_name:
            raise ValueError("Database name is required")


@dataclass
class ProfilingConfig:
    """Configuration for data profiling operations."""
    enabled: bool = True
    max_workers: int = 5
    sample_size: int = 10000
    use_sampling: bool = True
    timeout_seconds: int = 300

    # Field-level profiling options
    include_field_null_count: bool = True
    include_field_min_value: bool = True
    include_field_max_value: bool = True
    include_field_mean_value: bool = True
    include_field_median_value: bool = False
    include_field_stddev_value: bool = False
    include_field_quantiles: bool = False
    include_field_distinct_value_frequencies: bool = False
    include_field_histogram: bool = False
    include_field_sample_values: bool = True

    # Table-level options
    profile_external_tables: bool = False
    max_table_size_gb: Optional[float] = None
    max_table_rows: Optional[int] = None

    # Sampling options
    sampling_method: str = "RANDOM"  # RANDOM, BLOCK, SYSTEM
    confidence_level: float = 0.95


class GenericProfiler(ABC):
    """
    Abstract base class for SQL-based data profilers.

    This class provides the foundation for profiling data across different
    SQL databases and data warehouses in the DataGuild system.
    """

    def __init__(
            self,
            config: Any,
            report: Any,
            platform: str,
            state_handler: Optional[ProfilingHandler] = None,
    ):
        """
        Initialize the generic profiler.

        Args:
            config: Platform-specific configuration
            report: Profiling report instance
            platform: Platform identifier (e.g., 'snowflake', 'postgres')
            state_handler: Optional state handler for profiling
        """
        self.config = config
        self.report = report
        self.platform = platform
        self.state_handler = state_handler

        # Performance tracking
        self.profiling_timer = PerfTimer(f"{platform}_profiling")
        self.events: List[MetadataEvent] = []

        # Profiling state
        self.tables_profiled = 0
        self.tables_skipped = 0
        self.total_processing_time = 0.0

        logger.info(f"Initialized {self.__class__.__name__} for platform {platform}")

    def _emit_event(self, event: MetadataEvent) -> None:
        """Emit profiling event for monitoring."""
        self.events.append(event)

        if event.severity == MetadataEventSeverity.ERROR:
            logger.error(f"Profiling error: {event.message}")
        elif event.severity == MetadataEventSeverity.WARNING:
            logger.warning(f"Profiling warning: {event.message}")
        else:
            logger.debug(f"Profiling event: {event.message}")

    @abstractmethod
    def get_workunits(
            self, database: Database, db_tables: Dict[str, List[BaseTable]]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate profiling work units for database tables.

        Args:
            database: Database metadata
            db_tables: Dictionary mapping schema names to table lists

        Yields:
            MetadataWorkUnit instances for profiling operations
        """
        raise NotImplementedError("Subclasses must implement get_workunits")

    @abstractmethod
    def get_profiler_instance(self, db_name: Optional[str] = None) -> Any:
        """
        Create profiler instance for database connection.

        Args:
            db_name: Database name to connect to

        Returns:
            Platform-specific profiler instance
        """
        raise NotImplementedError("Subclasses must implement get_profiler_instance")

    @abstractmethod
    def get_batch_kwargs(
            self, table: BaseTable, schema_name: str, db_name: str
    ) -> Dict[str, Any]:
        """
        Generate batch kwargs for profiling execution.

        Args:
            table: Table to profile
            schema_name: Schema name
            db_name: Database name

        Returns:
            Dictionary of batch execution parameters
        """
        raise NotImplementedError("Subclasses must implement get_batch_kwargs")

    def should_profile_table(
            self, table: BaseTable, schema_name: str, db_name: str
    ) -> bool:
        """
        Determine if a table should be profiled.

        Args:
            table: Table metadata
            schema_name: Schema name
            db_name: Database name

        Returns:
            True if table should be profiled
        """
        # Check if profiling is enabled
        if not getattr(self.config, 'is_profiling_enabled', lambda: True)():
            return False

        # Skip external tables if configured
        profiling_config = getattr(self.config, 'profiling', None)
        if (
                profiling_config
                and hasattr(profiling_config, 'profile_external_tables')
                and not profiling_config.profile_external_tables
                and table.is_external_table()
        ):
            logger.debug(f"Skipping external table {table.get_fully_qualified_name()}")
            return False

        # Check table size limits
        if (
                profiling_config
                and hasattr(profiling_config, 'max_table_size_gb')
                and profiling_config.max_table_size_gb
                and table.size_in_bytes
        ):
            size_gb = table.get_size_gb()
            if size_gb and size_gb > profiling_config.max_table_size_gb:
                logger.info(
                    f"Skipping large table {table.get_fully_qualified_name()} "
                    f"({size_gb:.2f} GB > {profiling_config.max_table_size_gb} GB limit)"
                )
                return False

        # Check row count limits
        if (
                profiling_config
                and hasattr(profiling_config, 'max_table_rows')
                and profiling_config.max_table_rows
                and table.rows_count
                and table.rows_count > profiling_config.max_table_rows
        ):
            logger.info(
                f"Skipping table with many rows {table.get_fully_qualified_name()} "
                f"({table.rows_count:,} rows > {profiling_config.max_table_rows:,} limit)"
            )
            return False

        return True

    def get_profile_request(
            self, table: BaseTable, schema_name: str, db_name: str
    ) -> Optional[ProfileRequest]:
        """
        Create profile request for a table.

        Args:
            table: Table to profile
            schema_name: Schema name
            db_name: Database name

        Returns:
            ProfileRequest instance or None if profiling should be skipped
        """
        if not self.should_profile_table(table, schema_name, db_name):
            return None

        try:
            pretty_name = f"{db_name}.{schema_name}.{table.name}"

            profile_request = ProfileRequest(
                table=table,
                schema_name=schema_name,
                database_name=db_name,
                pretty_name=pretty_name,
                profile_options=self.get_profile_args()
            )

            logger.debug(f"Created profile request for {pretty_name}")
            return profile_request

        except Exception as e:
            error_msg = f"Error creating profile request for {db_name}.{schema_name}.{table.name}: {e}"

            error_event = MetadataEvent(
                event_type=MetadataEventType.VALIDATION_ERROR,
                timestamp=datetime.now(),
                source=f"{self.platform}_profiler",
                severity=MetadataEventSeverity.ERROR,
                message=error_msg,
                platform=self.platform
            )
            error_event.add_tag("profile_request_error")
            self._emit_event(error_event)

            logger.error(error_msg)
            return None

    def generate_profile_workunits(
            self,
            profile_requests: List[ProfileRequest],
            max_workers: int,
            db_name: str,
            platform: str,
            profiler_args: Dict[str, Any],
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate profiling work units from profile requests.

        Args:
            profile_requests: List of profiling requests
            max_workers: Maximum number of worker threads
            db_name: Database name
            platform: Platform identifier
            profiler_args: Additional profiling arguments

        Yields:
            MetadataWorkUnit instances for profiling
        """
        logger.info(
            f"Generating profiling work units for {len(profile_requests)} tables "
            f"in database {db_name}"
        )

        try:
            # Get profiler instance
            profiler = self.get_profiler_instance(db_name)
            if not profiler:
                logger.error(f"Failed to create profiler instance for database {db_name}")
                return

            # Process each profile request
            for i, request in enumerate(profile_requests):
                try:
                    logger.debug(
                        f"Processing profile request {i + 1}/{len(profile_requests)}: "
                        f"{request.pretty_name}"
                    )

                    # Generate batch kwargs
                    batch_kwargs = self.get_batch_kwargs(
                        request.table, request.schema_name, request.database_name
                    )

                    # Create work unit (placeholder - actual implementation would
                    # integrate with Great Expectations or similar profiling library)
                    work_unit = self._create_profiling_work_unit(
                        request, batch_kwargs, profiler_args
                    )

                    if work_unit:
                        yield work_unit
                        self.tables_profiled += 1
                    else:
                        self.tables_skipped += 1

                except Exception as e:
                    error_msg = f"Error processing profile request for {request.pretty_name}: {e}"

                    error_event = MetadataEvent(
                        event_type=MetadataEventType.VALIDATION_ERROR,
                        timestamp=datetime.now(),
                        source=f"{self.platform}_profiler",
                        severity=MetadataEventSeverity.ERROR,
                        message=error_msg,
                        platform=self.platform
                    )
                    error_event.add_tag("work_unit_error")
                    self._emit_event(error_event)

                    logger.error(error_msg)
                    self.tables_skipped += 1

            logger.info(
                f"Completed profiling work unit generation: "
                f"{self.tables_profiled} profiled, {self.tables_skipped} skipped"
            )

        except Exception as e:
            error_msg = f"Critical error generating profile work units for database {db_name}: {e}"

            error_event = MetadataEvent(
                event_type=MetadataEventType.VALIDATION_ERROR,
                timestamp=datetime.now(),
                source=f"{self.platform}_profiler",
                severity=MetadataEventSeverity.CRITICAL,
                message=error_msg,
                platform=self.platform
            )
            error_event.add_tag("critical_error")
            self._emit_event(error_event)

            logger.error(error_msg, exc_info=True)
            raise

    def _create_profiling_work_unit(
            self,
            request: ProfileRequest,
            batch_kwargs: Dict[str, Any],
            profiler_args: Dict[str, Any]
    ) -> Optional[MetadataWorkUnit]:
        """
        Create profiling work unit for a table.

        This is a placeholder method that would be implemented by subclasses
        to integrate with specific profiling libraries.

        Args:
            request: Profile request
            batch_kwargs: Batch execution parameters
            profiler_args: Profiling arguments

        Returns:
            MetadataWorkUnit or None if creation failed
        """
        # Placeholder implementation
        logger.debug(f"Creating work unit for {request.pretty_name}")

        # In a real implementation, this would:
        # 1. Create Great Expectations batch
        # 2. Execute profiling expectations
        # 3. Generate DataGuild metadata work unit
        # 4. Return the work unit

        return None

    def get_profile_args(self) -> Dict[str, Any]:
        """
        Get profiling arguments from configuration.

        Returns:
            Dictionary of profiling configuration
        """
        profiling_config = getattr(self.config, 'profiling', None)

        if not profiling_config:
            return {
                "include_field_null_count": True,
                "include_field_min_value": True,
                "include_field_max_value": True,
                "include_field_sample_values": True,
            }

        return {
            "include_field_null_count": getattr(profiling_config, 'include_field_null_count', True),
            "include_field_min_value": getattr(profiling_config, 'include_field_min_value', True),
            "include_field_max_value": getattr(profiling_config, 'include_field_max_value', True),
            "include_field_mean_value": getattr(profiling_config, 'include_field_mean_value', False),
            "include_field_median_value": getattr(profiling_config, 'include_field_median_value', False),
            "include_field_stddev_value": getattr(profiling_config, 'include_field_stddev_value', False),
            "include_field_quantiles": getattr(profiling_config, 'include_field_quantiles', False),
            "include_field_distinct_value_frequencies": getattr(profiling_config,
                                                                'include_field_distinct_value_frequencies', False),
            "include_field_histogram": getattr(profiling_config, 'include_field_histogram', False),
            "include_field_sample_values": getattr(profiling_config, 'include_field_sample_values', True),
        }

    def get_profiling_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive profiling summary.

        Returns:
            Dictionary with profiling statistics
        """
        return {
            "platform": self.platform,
            "tables_profiled": self.tables_profiled,
            "tables_skipped": self.tables_skipped,
            "total_processing_time_seconds": self.profiling_timer.elapsed_seconds(),
            "events_generated": len(self.events),
            "error_events": len([e for e in self.events if e.severity == MetadataEventSeverity.ERROR]),
            "warning_events": len([e for e in self.events if e.severity == MetadataEventSeverity.WARNING]),
        }

    def get_events(self) -> List[MetadataEvent]:
        """Get all profiling events."""
        return self.events.copy()

    def clear_events(self) -> None:
        """Clear profiling events to free memory."""
        self.events.clear()


# Export main classes
__all__ = [
    'ProfileRequest',
    'ProfilingConfig',
    'GenericProfiler'
]
