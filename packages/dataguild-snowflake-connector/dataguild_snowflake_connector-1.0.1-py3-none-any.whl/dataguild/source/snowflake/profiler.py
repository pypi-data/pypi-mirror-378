"""
DataGuild Snowflake Profiler

Enterprise-grade data profiling for Snowflake with comprehensive
statistics generation, sampling strategies, and performance optimization.
"""

import logging
from typing import Callable, Dict, Iterable, List, Optional
from datetime import datetime

from snowflake.sqlalchemy import snowdialect
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql import sqltypes

# DataGuild imports
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.ge_data_profiler import DataGuildGEProfiler
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.source.snowflake.query import SnowflakeQuery
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.snowflake.schema import (
    SnowflakeDatabase,
    SnowflakeTable,
)
from dataguild.source.snowflake.utils import SnowflakeCommonMixin
from dataguild.source.sql.sql_generic import BaseTable
from dataguild.source.sql.sql_generic_profiler import GenericProfiler
from dataguild.source.state.profiling_state_handler import ProfilingHandler

# DataGuild metadata and event system
from dataguild.metadata.schemas import MetadataEvent, MetadataEventType, MetadataEventSeverity
from dataguild.utilities.perf_timer import PerfTimer

# Configure Snowflake dialect for unsupported types
snowdialect.ischema_names["GEOGRAPHY"] = sqltypes.NullType
snowdialect.ischema_names["GEOMETRY"] = sqltypes.NullType

logger = logging.getLogger(__name__)

PUBLIC_SCHEMA = "PUBLIC"


class SnowflakeProfiler(GenericProfiler, SnowflakeCommonMixin):
    """
    DataGuild Snowflake Profiler with advanced sampling strategies,
    performance optimization, and comprehensive error handling.

    Features:
    - Intelligent two-stage sampling for large tables
    - Comprehensive event tracking and monitoring
    - Performance metrics and timing
    - Robust error handling with graceful degradation
    - Support for external tables and mixed-case identifiers
    """

    def __init__(
        self,
        config: SnowflakeV2Config,
        report: SnowflakeV2Report,
        state_handler: Optional[ProfilingHandler] = None,
    ) -> None:
        super().__init__(config, report, self.platform, state_handler)
        self.config: SnowflakeV2Config = config
        self.report: SnowflakeV2Report = report
        self.database_default_schema: Dict[str, str] = dict()

        # Performance and event tracking
        self.profiling_timer = PerfTimer("snowflake_profiling")
        self.events: List[MetadataEvent] = []

        logger.info(
            f"Initialized DataGuild SnowflakeProfiler for platform {self.platform} "
            f"with profiling_enabled={self.config.is_profiling_enabled()}"
        )

    def _emit_event(self, event: MetadataEvent) -> None:
        """Emit a profiling event for monitoring and debugging."""
        self.events.append(event)

        if event.severity == MetadataEventSeverity.ERROR:
            logger.error(f"Profiling error: {event.message}")
        elif event.severity == MetadataEventSeverity.WARNING:
            logger.warning(f"Profiling warning: {event.message}")
        else:
            logger.debug(f"Profiling event: {event.message}")

    def get_workunits(
        self, database: SnowflakeDatabase, db_tables: Dict[str, List[SnowflakeTable]]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate profiling work units for all tables in the database.

        This method handles:
        - Connection pool optimization for multi-threaded profiling
        - Default schema detection when PUBLIC schema is missing
        - External table filtering based on configuration
        - Comprehensive error handling and event emission

        Args:
            database: SnowflakeDatabase instance containing schema metadata
            db_tables: Dictionary mapping schema names to lists of tables

        Yields:
            MetadataWorkUnit instances for profiling operations
        """
        with self.profiling_timer:
            # Emit profiling start event
            start_event = MetadataEvent(
                event_type=MetadataEventType.DATA_QUALITY_CHECK,
                timestamp=datetime.now(),
                source="snowflake_profiler",
                severity=MetadataEventSeverity.INFO,
                message=f"Starting profiling for database {database.name}",
                platform="snowflake",
                payload={
                    "database": database.name,
                    "schema_count": len(db_tables),
                    "total_tables": sum(len(tables) for tables in db_tables.values())
                }
            )
            start_event.add_tag("profiling_start")
            self._emit_event(start_event)

            try:
                # Configure connection pool for better performance with threading
                # Extra default SQLAlchemy option for better connection pooling and threading.
                # https://docs.sqlalchemy.org/en/14/core/pooling.html#sqlalchemy.pool.QueuePool.params.max_overflow
                if self.config.is_profiling_enabled():
                    self.config.options.setdefault(
                        "max_overflow", self.config.profiling.max_workers
                    )

                # Handle databases without PUBLIC schema
                if PUBLIC_SCHEMA not in db_tables:
                    if db_tables:
                        # If PUBLIC schema is absent, we use any one of schemas as default schema
                        default_schema = list(db_tables.keys())[0]
                        self.database_default_schema[database.name] = default_schema

                        warning_event = MetadataEvent(
                            event_type=MetadataEventType.VALIDATION_WARNING,
                            timestamp=datetime.now(),
                            source="snowflake_profiler",
                            severity=MetadataEventSeverity.WARNING,
                            message=f"PUBLIC schema not found in {database.name}, using {default_schema} as default",
                            platform="snowflake"
                        )
                        warning_event.add_tag("schema_fallback")
                        self._emit_event(warning_event)

                # Collect profiling requests
                profile_requests = []
                skipped_count = 0

                for schema in database.schemas:
                    if schema.name not in db_tables:
                        continue

                    for table in db_tables[schema.name]:
                        try:
                            # Check if we should skip external tables
                            if (
                                not self.config.profiling.profile_external_tables
                                and table.type == "EXTERNAL TABLE"
                            ):
                                logger.info(
                                    f"Skipping profiling of external table "
                                    f"{database.name}.{schema.name}.{table.name}"
                                )
                                self.report.profiling_skipped_other[schema.name] += 1
                                skipped_count += 1
                                continue

                            # Generate profile request
                            profile_request = self.get_profile_request(
                                table, schema.name, database.name
                            )

                            if profile_request is not None:
                                self.report.report_entity_profiled(profile_request.pretty_name)
                                profile_requests.append(profile_request)

                                logger.debug(
                                    f"Created profile request for "
                                    f"{database.name}.{schema.name}.{table.name}"
                                )

                        except Exception as e:
                            error_msg = (
                                f"Error creating profile request for "
                                f"{database.name}.{schema.name}.{table.name}: {e}"
                            )

                            error_event = MetadataEvent(
                                event_type=MetadataEventType.VALIDATION_ERROR,
                                timestamp=datetime.now(),
                                source="snowflake_profiler",
                                severity=MetadataEventSeverity.ERROR,
                                message=error_msg,
                                platform="snowflake",
                                entity_urn=self._get_dataset_urn(table.name, schema.name, database.name)
                            )
                            error_event.add_tag("profile_request_error")
                            self._emit_event(error_event)

                logger.info(
                    f"Generated {len(profile_requests)} profiling requests "
                    f"for database {database.name}, skipped {skipped_count} tables"
                )

                # Generate work units if we have requests
                if len(profile_requests) == 0:
                    logger.warning(f"No tables to profile in database {database.name}")
                    return

                # Generate profiling work units using DataGuild's profiling system
                yield from self.generate_profile_workunits(
                    profile_requests,
                    max_workers=self.config.profiling.max_workers,
                    db_name=database.name,
                    platform=self.platform,
                    profiler_args=self.get_profile_args(),
                )

                # Emit completion event
                completion_event = MetadataEvent(
                    event_type=MetadataEventType.DATA_QUALITY_CHECK,
                    timestamp=datetime.now(),
                    source="snowflake_profiler",
                    severity=MetadataEventSeverity.INFO,
                    message=f"Completed profiling for database {database.name}",
                    platform="snowflake",
                    duration_ms=int(self.profiling_timer.elapsed_seconds() * 1000),
                    records_processed=len(profile_requests)
                )
                completion_event.add_tag("profiling_complete")
                self._emit_event(completion_event)

                logger.info(
                    f"Completed profiling for database {database.name} "
                    f"in {self.profiling_timer.elapsed_seconds():.2f}s"
                )

            except Exception as e:
                error_msg = f"Critical error profiling database {database.name}: {e}"

                error_event = MetadataEvent(
                    event_type=MetadataEventType.VALIDATION_ERROR,
                    timestamp=datetime.now(),
                    source="snowflake_profiler",
                    severity=MetadataEventSeverity.CRITICAL,
                    message=error_msg,
                    platform="snowflake"
                )
                error_event.add_tag("critical_error")
                self._emit_event(error_event)

                logger.error(error_msg, exc_info=True)
                raise

    def get_dataset_name(self, table_name: str, schema_name: str, db_name: str) -> str:
        """
        Generate standardized dataset name for DataGuild.

        Args:
            table_name: Name of the table
            schema_name: Name of the schema
            db_name: Name of the database

        Returns:
            Standardized dataset identifier
        """
        return self.identifiers.get_dataset_identifier(table_name, schema_name, db_name)

    def _get_dataset_urn(self, table_name: str, schema_name: str, db_name: str) -> str:
        """Generate dataset URN for event tracking."""
        dataset_name = self.get_dataset_name(table_name, schema_name, db_name)
        return f"urn:li:dataset:(urn:li:dataPlatform:{self.platform},{dataset_name},PROD)"

    def get_batch_kwargs(
        self, table: BaseTable, schema_name: str, db_name: str
    ) -> dict:
        """
        Generate batch kwargs for Great Expectations with optimized Snowflake sampling.

        This method implements intelligent sampling strategies:
        1. No sampling for small tables (< sample_size rows)
        2. Single-stage BERNOULLI sampling for medium tables
        3. Two-stage sampling (BLOCK + BERNOULLI) for very large tables

        The two-stage approach improves performance on massive tables by:
        - First using BLOCK sampling to create an intermediate result set
        - Then using BERNOULLI sampling for final size reduction

        Args:
            table: Table metadata including row count
            schema_name: Schema name
            db_name: Database name

        Returns:
            Dictionary of batch kwargs for Great Expectations
        """
        custom_sql = None

        if (
            not self.config.profiling.limit
            and self.config.profiling.use_sampling
            and table.rows_count
            and table.rows_count > self.config.profiling.sample_size
        ):
            logger.debug(
                f"Applying sampling to {db_name}.{schema_name}.{table.name} "
                f"({table.rows_count:,} rows -> {self.config.profiling.sample_size:,} sample)"
            )

            # GX creates a temporary table from query if query is passed as batch kwargs.
            # We are using fraction-based sampling here, instead of fixed-size sampling because
            # Fixed-size sampling can be slower than equivalent fraction-based sampling
            # as per https://docs.snowflake.com/en/sql-reference/constructs/sample#performance-considerations

            estimated_block_row_count = 500_000
            block_profiling_min_rows = 100 * estimated_block_row_count
            tablename = f'"{db_name}"."{schema_name}"."{table.name}"'
            sample_pc = self.config.profiling.sample_size / table.rows_count
            overgeneration_factor = 1000

            if (
                table.rows_count > block_profiling_min_rows
                and table.rows_count > self.config.profiling.sample_size * overgeneration_factor
            ):
                # Two-stage sampling for extremely large tables
                # If the table is significantly larger than the sample size, do a first pass
                # using block sampling to improve performance. We generate a table 1000 times
                # larger than the target sample size, and then use normal sampling for the
                # final size reduction.

                logger.debug(
                    f"Using two-stage sampling for large table {table.name} "
                    f"({table.rows_count:,} rows)"
                )

                block_sample_pc = 100 * overgeneration_factor * sample_pc
                tablename = (
                    f"(SELECT * FROM {tablename} "
                    f"TABLESAMPLE BLOCK ({block_sample_pc:.8f}))"
                )
                sample_pc = 1 / overgeneration_factor

            # Final BERNOULLI sampling
            custom_sql = (
                f"select * from {tablename} "
                f"TABLESAMPLE BERNOULLI ({100 * sample_pc:.8f})"
            )

            logger.debug(f"Generated sampling SQL: {custom_sql}")

        return {
            **super().get_batch_kwargs(table, schema_name, db_name),
            # Lowercase/Mixedcase table names in Snowflake do not work by default.
            # We need to pass `use_quoted_name=True` for such tables as mentioned here -
            # https://github.com/great-expectations/great_expectations/pull/2023
            "use_quoted_name": (table.name != table.name.upper()),
            "custom_sql": custom_sql,
        }

    def get_profiler_instance(
        self, db_name: Optional[str] = None
    ) -> "DataGuildGEProfiler":
        """
        Create DataGuild Great Expectations profiler instance.

        Args:
            db_name: Database name to connect to

        Returns:
            Configured DataGuildGEProfiler instance

        Raises:
            AssertionError: If db_name is not provided
            Exception: If connection or profiler creation fails
        """
        assert db_name, "Database name is required for profiler instance"

        try:
            # Generate SQLAlchemy connection URL
            url = self.config.get_sql_alchemy_url(database=db_name)
            logger.debug(f"sql_alchemy_url={url}")

            # Create SQLAlchemy engine with custom connection creator
            engine = create_engine(
                url,
                creator=self.callable_for_db_connection(db_name),
                **self.config.get_options(),
            )

            # Establish connection and create inspector
            conn = engine.connect()
            inspector = inspect(conn)

            # Create DataGuild profiler instance
            profiler = DataGuildGEProfiler(
                conn=inspector.bind,
                report=self.report,
                config=self.config.profiling,
                platform=self.platform,
            )

            logger.debug(f"Successfully created profiler instance for database {db_name}")
            return profiler

        except Exception as e:
            error_msg = f"Failed to create profiler instance for database {db_name}: {e}"

            error_event = MetadataEvent(
                event_type=MetadataEventType.CONNECTION_LOST,
                timestamp=datetime.now(),
                source="snowflake_profiler",
                severity=MetadataEventSeverity.ERROR,
                message=error_msg,
                platform="snowflake"
            )
            error_event.add_tag("profiler_creation_error")
            self._emit_event(error_event)

            logger.error(error_msg, exc_info=True)
            raise

    def callable_for_db_connection(self, db_name: str) -> Callable:
        """
        Create callable that returns configured database connection.

        This method handles database and schema context setup, including
        fallback to default schema when PUBLIC schema is not available.

        Args:
            db_name: Database name to connect to

        Returns:
            Callable that returns configured Snowflake connection
        """
        schema_name = self.database_default_schema.get(db_name)

        def get_db_connection():
            """
            Create and configure database connection with proper context.

            This function:
            1. Gets a native Snowflake connection from the config
            2. Sets the database context using USE DATABASE
            3. Sets the schema context if needed (when PUBLIC is missing)

            Returns:
                Configured Snowflake connection
            """
            try:
                conn = self.config.get_native_connection()
                cursor = conn.cursor()

                # Set database context
                cursor.execute(SnowflakeQuery.use_database(db_name))

                # As mentioned here - https://docs.snowflake.com/en/sql-reference/sql/use-database#usage-notes
                # no schema is selected if PUBLIC schema is absent. We need to explicitly call `USE SCHEMA <schema>`
                if schema_name:
                    cursor.execute(SnowflakeQuery.use_schema(schema_name))
                    logger.debug(
                        f"Set database context to {db_name} and schema context to {schema_name}"
                    )
                else:
                    logger.debug(f"Set database context to {db_name}")

                return conn

            except Exception as e:
                error_msg = f"Failed to configure database connection for {db_name}: {e}"

                error_event = MetadataEvent(
                    event_type=MetadataEventType.CONNECTION_LOST,
                    timestamp=datetime.now(),
                    source="snowflake_profiler",
                    severity=MetadataEventSeverity.ERROR,
                    message=error_msg,
                    platform="snowflake"
                )
                error_event.add_tag("connection_error")
                self._emit_event(error_event)

                logger.error(error_msg, exc_info=True)
                raise

        return get_db_connection

    def get_profile_args(self) -> Dict[str, any]:
        """
        Get additional arguments for profiling operations.

        Returns:
            Dictionary of profiling configuration arguments
        """
        return {
            "catch_exceptions": True,
            "profiling_enabled": self.config.is_profiling_enabled(),
            "include_field_null_count": self.config.profiling.include_field_null_count,
            "include_field_min_value": self.config.profiling.include_field_min_value,
            "include_field_max_value": self.config.profiling.include_field_max_value,
            "include_field_mean_value": self.config.profiling.include_field_mean_value,
            "include_field_median_value": self.config.profiling.include_field_median_value,
            "include_field_stddev_value": self.config.profiling.include_field_stddev_value,
            "include_field_quantiles": self.config.profiling.include_field_quantiles,
            "include_field_distinct_value_frequencies": self.config.profiling.include_field_distinct_value_frequencies,
            "include_field_histogram": self.config.profiling.include_field_histogram,
            "include_field_sample_values": self.config.profiling.include_field_sample_values,
        }

    def get_profiling_summary(self) -> Dict[str, any]:
        """
        Get comprehensive summary of profiling operations.

        Returns:
            Dictionary containing profiling statistics and metrics
        """
        return {
            "total_time_seconds": self.profiling_timer.elapsed_seconds(),
            "databases_with_default_schema": len(self.database_default_schema),
            "profiling_enabled": self.config.is_profiling_enabled(),
            "sampling_enabled": self.config.profiling.use_sampling,
            "sample_size": self.config.profiling.sample_size,
            "max_workers": self.config.profiling.max_workers,
            "profile_external_tables": self.config.profiling.profile_external_tables,
            "events_generated": len(self.events),
            "error_events": len([e for e in self.events if e.severity == MetadataEventSeverity.ERROR]),
            "warning_events": len([e for e in self.events if e.severity == MetadataEventSeverity.WARNING]),
        }

    def get_events(self) -> List[MetadataEvent]:
        """Get all profiling events for debugging and monitoring."""
        return self.events.copy()

    def clear_events(self) -> None:
        """Clear profiling events to free memory."""
        self.events.clear()


# Export the main profiler class
__all__ = [
    'SnowflakeProfiler',
]
