"""
DataGuild Snowflake usage and operational statistics extractor.

This module provides comprehensive usage statistics extraction and operational
history processing for Snowflake data sources, including query analysis,
user activity tracking, and dataset usage patterns.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pydantic
from pydantic import BaseModel

from dataguild.configuration.time_window_config import BaseTimeWindowConfig, BucketDuration
from dataguild.configuration.common import AllowDenyPattern
from dataguild.emitter.mce_builder import make_user_urn
from dataguild.emitter.mcp import MetadataChangeProposalWrapper
from dataguild.api.closeable import Closeable
from dataguild.api.source_helpers import auto_empty_dataset_usage_statistics
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.snowflake.constants import SnowflakeEdition
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.source.snowflake.connection import (
    SnowflakeConnection,
    SnowflakePermissionError,
)
from dataguild.source.snowflake.query import SnowflakeQuery
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.snowflake.utils import (
    SnowflakeCommonMixin,
    SnowflakeFilter,
    SnowflakeIdentifierBuilder,
)
from dataguild.source.state.redundant_run_skip_handler import (
    RedundantUsageRunSkipHandler,
)
from dataguild.source_report.ingestion_stage import (
    USAGE_EXTRACTION_OPERATIONAL_STATS,
    USAGE_EXTRACTION_USAGE_AGGREGATION,
)
from dataguild.metadata.com.linkedin.pegasus2avro.dataset import (
    DatasetFieldUsageCounts,
    DatasetUsageStatistics,
    DatasetUserUsageCounts,
)
from dataguild.metadata.com.linkedin.pegasus2avro.timeseries import TimeWindowSize, TimeWindowUnit
from dataguild.metadata.schema_classes import OperationClass, OperationTypeClass
from dataguild.sql_parsing.sqlglot_utils import try_format_query
from dataguild.utilities.perf_timer import PerfTimer
from dataguild.utilities.sql_formatter import trim_query

logger: logging.Logger = logging.getLogger(__name__)

# Operation statement type mappings for Snowflake queries
OPERATION_STATEMENT_TYPES = {
    "INSERT": OperationTypeClass.INSERT,
    "UPDATE": OperationTypeClass.UPDATE,
    "DELETE": OperationTypeClass.DELETE,
    "CREATE": OperationTypeClass.CREATE,
    "CREATE_TABLE": OperationTypeClass.CREATE,
    "CREATE_TABLE_AS_SELECT": OperationTypeClass.CREATE,
    "MERGE": OperationTypeClass.CUSTOM,
    "COPY": OperationTypeClass.CUSTOM,
    "TRUNCATE_TABLE": OperationTypeClass.CUSTOM,
    # TODO: Dataset for below query types are not detected by Snowflake in access_history.objects_modified.
    # However it seems possible to support these using SQL parsing in future.
    # When this support is added, snowflake_query.operational_data_for_time_window needs to be updated.
    # "CREATE_VIEW": OperationTypeClass.CREATE,
    # "CREATE_EXTERNAL_TABLE": OperationTypeClass.CREATE,
    # "ALTER_TABLE_MODIFY_COLUMN": OperationTypeClass.ALTER,
    # "ALTER_TABLE_ADD_COLUMN": OperationTypeClass.ALTER,
    # "RENAME_COLUMN": OperationTypeClass.ALTER,
    # "ALTER_SET_TAG": OperationTypeClass.ALTER,
    # "ALTER_TABLE_DROP_COLUMN": OperationTypeClass.ALTER,
    # "ALTER": OperationTypeClass.ALTER,
}


class PermissiveModel(BaseModel):
    """Base model that allows extra fields for flexible parsing."""

    class Config:
        extra = "allow"
        validate_assignment = True
        use_enum_values = True


class SnowflakeColumnReference(PermissiveModel):
    """Represents a column reference in Snowflake access history."""

    columnName: str
    columnId: Optional[int] = None
    objectName: Optional[str] = None
    objectDomain: Optional[str] = None
    objectId: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "columnName": self.columnName,
            "columnId": self.columnId,
            "objectName": self.objectName,
            "objectDomain": self.objectDomain,
            "objectId": self.objectId,
        }


class SnowflakeObjectAccessEntry(PermissiveModel):
    """Represents an object access entry in Snowflake access history."""

    columns: Optional[List[SnowflakeColumnReference]] = None
    objectDomain: str
    objectName: str
    # Seems like it should never be null, but in practice have seen null objectIds
    objectId: Optional[int] = None
    stageKind: Optional[str] = None

    def get_qualified_name(self) -> str:
        """Get the qualified name for this object."""
        return self.objectName

    def is_valid_object(self) -> bool:
        """Check if this is a valid object for processing."""
        return bool(self.objectName and self.objectDomain)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "objectName": self.objectName,
            "objectDomain": self.objectDomain,
            "objectId": self.objectId,
            "stageKind": self.stageKind,
            "columns": [col.to_dict() for col in (self.columns or [])],
        }


class SnowflakeJoinedAccessEvent(PermissiveModel):
    """Represents a joined access event from Snowflake access history and query history."""

    query_start_time: datetime
    query_text: str
    query_type: str
    rows_inserted: Optional[int] = None
    rows_updated: Optional[int] = None
    rows_deleted: Optional[int] = None
    base_objects_accessed: List[SnowflakeObjectAccessEntry]
    direct_objects_accessed: List[SnowflakeObjectAccessEntry]
    objects_modified: List[SnowflakeObjectAccessEntry]
    user_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    role_name: str

    def get_operation_type(self) -> OperationTypeClass:
        """Get the operation type for this event."""
        return OPERATION_STATEMENT_TYPES.get(
            self.query_type, OperationTypeClass.CUSTOM
        )

    def has_valid_user_info(self) -> bool:
        """Check if the event has valid user information."""
        return bool(self.user_name)

    def get_affected_datasets(self) -> List[str]:
        """Get list of datasets affected by this event."""
        datasets = []
        for obj in self.objects_modified:
            if obj.is_valid_object():
                datasets.append(obj.get_qualified_name())
        return datasets

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "query_start_time": self.query_start_time.isoformat(),
            "query_text": self.query_text,
            "query_type": self.query_type,
            "rows_inserted": self.rows_inserted,
            "rows_updated": self.rows_updated,
            "rows_deleted": self.rows_deleted,
            "user_name": self.user_name,
            "email": self.email,
            "role_name": self.role_name,
            "base_objects_accessed": [obj.to_dict() for obj in self.base_objects_accessed],
            "direct_objects_accessed": [obj.to_dict() for obj in self.direct_objects_accessed],
            "objects_modified": [obj.to_dict() for obj in self.objects_modified],
        }


class SnowflakeUsageExtractor(SnowflakeCommonMixin, Closeable):
    """
    Comprehensive usage statistics and operational history extractor for Snowflake.

    This class handles:
    - Usage statistics extraction and aggregation
    - Operational history processing
    - Query analysis and user activity tracking
    - Time window management for incremental processing
    """

    def __init__(
            self,
            config: SnowflakeV2Config,
            report: SnowflakeV2Report,
            connection: SnowflakeConnection,
            filter: SnowflakeFilter,
            identifiers: SnowflakeIdentifierBuilder,
            redundant_run_skip_handler: Optional[RedundantUsageRunSkipHandler] = None,
    ) -> None:
        """
        Initialize the usage extractor with required dependencies.

        Args:
            config: Snowflake V2 configuration
            report: Snowflake V2 report for tracking progress
            connection: Snowflake database connection
            filter: Filter for determining which objects to include
            identifiers: Builder for generating identifiers and URNs
            redundant_run_skip_handler: Handler for skipping redundant runs
        """
        self.config: SnowflakeV2Config = config
        self.report: SnowflakeV2Report = report
        self.filter = filter
        self.identifiers = identifiers
        self.connection = connection
        self.redundant_run_skip_handler = redundant_run_skip_handler

        # Get the time window for this extraction run
        self.start_time, self.end_time = (
            self.report.usage_start_time,
            self.report.usage_end_time,
        ) = self.get_time_window()
        
        # Initialize usage aggregation report with PerfTimer objects
        if not hasattr(self.report, 'usage_aggregation') or self.report.usage_aggregation is None:
            from dataguild.utilities.perf_timer import PerfTimer
            
            # Create a simple object with the required attributes
            self.report.usage_aggregation = type('UsageAggregation', (), {})()
            self.report.usage_aggregation.query_secs = 0.0
            self.report.usage_aggregation.query_row_count = 0
            self.report.usage_aggregation.result_fetch_timer = PerfTimer()
            self.report.usage_aggregation.result_skip_timer = PerfTimer()
            self.report.usage_aggregation.result_map_timer = PerfTimer()
            self.report.usage_aggregation.queries_map_timer = PerfTimer()
            self.report.usage_aggregation.users_map_timer = PerfTimer()
            self.report.usage_aggregation.fields_map_timer = PerfTimer()
            
            def as_string(self):
                return f"UsageAggregation(query_secs={self.query_secs}, query_row_count={self.query_row_count})"
            
            self.report.usage_aggregation.as_string = as_string.__get__(self.report.usage_aggregation)

        logger.info(
            f"Initialized SnowflakeUsageExtractor for time window: "
            f"{self.start_time} to {self.end_time}"
        )

    def get_time_window(self) -> Tuple[datetime, datetime]:
        """
        Get the time window for usage extraction.

        Returns:
            Tuple of (start_time, end_time) for the extraction window
        """
        if self.redundant_run_skip_handler:
            return self.redundant_run_skip_handler.suggest_run_time_window(
                self.config.start_time, self.config.end_time
            )
        else:
            return self.config.start_time, self.config.end_time

    def get_usage_workunits(
            self, discovered_datasets: List[str]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate usage work units for discovered datasets.

        Args:
            discovered_datasets: List of discovered dataset identifiers

        Yields:
            MetadataWorkUnit objects containing usage statistics and operations
        """
        if not self._should_ingest_usage():
            logger.info("Skipping usage ingestion based on configuration or state")
            return

        # Extract usage aggregation statistics
        with self.report.new_stage(f"*: {USAGE_EXTRACTION_USAGE_AGGREGATION}"):
            if self.report.edition == SnowflakeEdition.STANDARD:
                logger.warning(
                    "Snowflake Account is Standard Edition. "
                    "Usage and Operation History Feature is not supported."
                )
                return

            logger.info("Checking usage date ranges")
            self._check_usage_date_ranges()

            # If permission error, execution returns from here
            if (
                    self.report.min_access_history_time is None
                    or self.report.max_access_history_time is None
            ):
                logger.warning("No access history time range available")
                return

            # Generate usage statistics
            if self.config.include_usage_stats:
                logger.info("Extracting usage statistics")
                yield from auto_empty_dataset_usage_statistics(
                    self._get_workunits_internal(discovered_datasets),
                    config=BaseTimeWindowConfig(
                        start_time=self.start_time,
                        end_time=self.end_time,
                        bucket_duration=self.config.bucket_duration,
                    ),
                    dataset_urns={
                        self.identifiers.gen_dataset_urn(dataset_identifier)
                        for dataset_identifier in discovered_datasets
                    },
                )

        # Extract operational statistics
        with self.report.new_stage(f"*: {USAGE_EXTRACTION_OPERATIONAL_STATS}"):
            if getattr(self.config.stateful_usage, 'include_operational_stats', True) if self.config.stateful_usage else True:
                logger.info("Extracting operational statistics")
                # Generate the operation work units
                access_events = self._get_snowflake_history()
                for event in access_events:
                    yield from self._get_operation_aspect_work_unit(
                        event, discovered_datasets
                    )

            if self.redundant_run_skip_handler:
                # Update the checkpoint state for this run
                self.redundant_run_skip_handler.update_state(
                    self.config.start_time,
                    self.config.end_time,
                    self.config.bucket_duration,
                )

    def _get_workunits_internal(
            self, discovered_datasets: List[str]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Internal method to get usage work units with performance tracking.

        Args:
            discovered_datasets: List of discovered dataset identifiers

        Yields:
            MetadataWorkUnit objects containing usage statistics
        """
        with PerfTimer() as timer:
            logger.info("Getting aggregated usage statistics from Snowflake")

            try:
                results = self.connection.query(
                    SnowflakeQuery.usage_per_object_per_time_bucket_for_time_window(
                        start_time_millis=int(self.start_time.timestamp() * 1000),
                        end_time_millis=int(self.end_time.timestamp() * 1000),
                        time_bucket_size=self.config.bucket_duration,
                        use_base_objects=self.config.apply_view_usage_to_tables,
                        top_n_queries=getattr(self.config.stateful_usage, 'top_n_queries', 1000) if self.config.stateful_usage else 1000,
                        include_top_n_queries=getattr(self.config.stateful_usage, 'include_operational_stats', True) if self.config.stateful_usage else True,
                        email_domain=self.config.email_domain,
                        email_filter=getattr(self.config, 'user_email_pattern', AllowDenyPattern(allow=[".*"], deny=[])),
                        table_deny_pattern=self.config.temporary_tables_pattern,
                    ),
                )
            except Exception as e:
                logger.debug(e, exc_info=e)
                self.warn_if_stateful_else_error(
                    "usage-statistics",
                    f"Populating table usage statistics from Snowflake failed due to error {e}.",
                )
                self.report_status(USAGE_EXTRACTION_USAGE_AGGREGATION, False)
                return

            self.report.usage_aggregation.query_secs = timer.elapsed_seconds()
            self.report.usage_aggregation.query_row_count = results.rowcount

        # Process results 
        for row in results:
            # Log progress periodically
            if results.rownumber is not None and results.rownumber % 1000 == 0:
                logger.debug(f"Processing usage row number {results.rownumber}")
                logger.debug(f"Processing usage row {results.rownumber}")

            # Apply filtering
            if not self.filter.is_dataset_pattern_allowed(
                    row["OBJECT_NAME"],
                    row["OBJECT_DOMAIN"],
            ):
                logger.debug(
                    f"Skipping usage for {row['OBJECT_DOMAIN']} {row['OBJECT_NAME']}, "
                    f"as table is not allowed by recipe."
                )
                continue

            # Check if dataset was discovered
            dataset_identifier = (
                self.identifiers.get_dataset_identifier_from_qualified_name(
                    row["OBJECT_NAME"]
                )
            )
            if dataset_identifier not in discovered_datasets:
                logger.debug(
                    f"Skipping usage for {row['OBJECT_DOMAIN']} {dataset_identifier}, "
                    f"as table is not accessible."
                )
                continue

            # Build and yield usage statistics
            wu = self.build_usage_statistics_for_dataset(
                dataset_identifier, row
            )
            
            if wu:
                yield wu

    def build_usage_statistics_for_dataset(
            self, dataset_identifier: str, row: dict
    ) -> Optional[MetadataWorkUnit]:
        """
        Build usage statistics work unit for a dataset.

        Args:
            dataset_identifier: Dataset identifier
            row: Row from usage statistics query

        Returns:
            MetadataWorkUnit with usage statistics or None if parsing fails
        """
        try:
            # Convert BucketDuration to TimeWindowUnit
            bucket_to_time_unit = {
                "MINUTE": TimeWindowUnit.MINUTE,
                "HOUR": TimeWindowUnit.HOUR,
                "DAY": TimeWindowUnit.DAY,
                "WEEK": TimeWindowUnit.WEEK,
                "MONTH": TimeWindowUnit.MONTH,
                "QUARTER": TimeWindowUnit.MONTH,  # Map QUARTER to MONTH
                "YEAR": TimeWindowUnit.YEAR,
            }
            
            time_unit = bucket_to_time_unit.get(self.config.bucket_duration, TimeWindowUnit.DAY)
            
            stats = DatasetUsageStatistics(
                timestampMillis=int(row["BUCKET_START_TIME"].timestamp() * 1000),
                eventGranularity=TimeWindowSize(
                    unit=time_unit, multiple=1
                ),
                totalSqlQueries=row["TOTAL_QUERIES"],
                uniqueUserCount=row["TOTAL_USERS"],
                topSqlQueries=(
                    self._map_top_sql_queries(row["TOP_SQL_QUERIES"])
                    if (getattr(self.config.stateful_usage, 'include_operational_stats', True) if self.config.stateful_usage else True)
                    else None
                ),
                userCounts=self._map_user_counts(row["USER_COUNTS"]),
                fieldCounts=self._map_field_counts(row["FIELD_COUNTS"]),
            )

            return MetadataChangeProposalWrapper(
                entityUrn=self.identifiers.gen_dataset_urn(dataset_identifier),
                aspect=stats,
            ).as_workunit()

        except Exception as e:
            logger.debug(
                f"Failed to parse usage statistics for dataset {dataset_identifier} "
                f"due to error {e}.",
                exc_info=e,
            )
            self.report.report_warning(
                "FAILED_USAGE_STATISTICS_PARSING",
                f"Failed to parse usage statistics for dataset {dataset_identifier}"
            )
        return None

    def _map_top_sql_queries(self, top_sql_queries_data) -> List[str]:
        """
        Map and format top SQL queries from array data.

        Args:
            top_sql_queries_data: Array or JSON string containing top SQL queries

        Returns:
            List of formatted and trimmed SQL queries
        """
        # Handle both array data from ARRAY_UNIQUE_AGG and JSON strings
        if isinstance(top_sql_queries_data, str):
            top_sql_queries = json.loads(top_sql_queries_data)
        else:
            top_sql_queries = top_sql_queries_data or []
        # Use a reasonable default for query character limit
        queries_character_limit = getattr(self.config, 'queries_character_limit', 10000)
        top_n_queries = getattr(self.config.stateful_usage, 'top_n_queries', 1000) if self.config.stateful_usage else 1000
        budget_per_query: int = max(1, int(queries_character_limit / top_n_queries))

        formatted_queries = []
        for query in top_sql_queries:
            if getattr(self.config, 'format_sql_queries', False):
                formatted_query = trim_query(
                    try_format_query(query, self.platform), budget_per_query
                )
            else:
                formatted_query = trim_query(query, budget_per_query)
            formatted_queries.append(formatted_query)

        return sorted(formatted_queries)

    def _map_user_counts(
            self,
            user_counts_data,
    ) -> List[DatasetUserUsageCounts]:
        """
        Map user counts from array data to structured format.

        Args:
            user_counts_data: Array or JSON string containing user count data

        Returns:
            List of DatasetUserUsageCounts objects
        """
        # Handle both array data from ARRAY_UNIQUE_AGG and JSON strings
        if isinstance(user_counts_data, str):
            user_counts = json.loads(user_counts_data)
        else:
            user_counts = user_counts_data or []
        filtered_user_counts = []

        for user_count in user_counts:
            user_email = user_count.get("email")

            # Generate email if not provided
            if (
                    not user_email
                    and self.config.email_domain
                    and user_count["user_name"]
            ):
                user_email = "{}@{}".format(
                    user_count["user_name"], self.config.email_domain
                ).lower()

            # Filter by email pattern - use the same pattern as in the query call
            email_pattern = getattr(self.config, 'user_email_pattern', AllowDenyPattern(allow=[".*"], deny=[]))
            if not user_email or not email_pattern.allowed(user_email):
                continue

            filtered_user_counts.append(
                DatasetUserUsageCounts(
                    user=make_user_urn(
                        self.identifiers.get_user_identifier(
                            user_count["user_name"],
                            user_email,
                        )
                    ),
                    count=user_count["total"],
                    # NOTE: Generated emails may be incorrect, as email may be different than
                    # username@email_domain
                    userEmail=user_email,
                )
            )

        return sorted(filtered_user_counts, key=lambda v: v.user)
# Timer removed

    def _map_field_counts(self, field_counts_data) -> List[DatasetFieldUsageCounts]:
        """
        Map field counts from array data to structured format.

        Args:
            field_counts_data: Array or JSON string containing field count data

        Returns:
            List of DatasetFieldUsageCounts objects
        """
        # Handle both array data from ARRAY_UNIQUE_AGG and JSON strings
        if isinstance(field_counts_data, str):
            field_counts = json.loads(field_counts_data)
        else:
            field_counts = field_counts_data or []

        mapped_counts = []
        for field_count in field_counts:
            mapped_counts.append(
                DatasetFieldUsageCounts(
                    fieldPath=self.identifiers.snowflake_identifier(
                        field_count["col"]
                    ),
                    count=field_count["total"],
                )
            )

        return sorted(mapped_counts, key=lambda v: v.fieldPath)
# Timer removed

    def _get_snowflake_history(self) -> Iterable[SnowflakeJoinedAccessEvent]:
        """
        Get Snowflake access history for operational statistics.

        Yields:
            SnowflakeJoinedAccessEvent objects containing access history data
        """
        logger.info("Getting Snowflake access history")

        with PerfTimer() as timer:
            query = self._make_operations_query()

            try:
                assert self.connection is not None
                results = self.connection.query(query)
            except Exception as e:
                logger.debug(e, exc_info=e)
                self.warn_if_stateful_else_error(
                    "operation",
                    f"Populating table operation history from Snowflake failed due to error {e}.",
                )
                self.report_status(USAGE_EXTRACTION_OPERATIONAL_STATS, False)
                return

            # Update performance metrics
            if hasattr(self.report, 'access_history_query_secs'):
                self.report.access_history_query_secs = timer.elapsed_seconds(digits=2)

        # Process each row from the results
        for row in results:
            yield from self._process_snowflake_history_row(row)

    def _make_operations_query(self) -> str:
        """
        Create the operations query for the configured time window.

        Returns:
            SQL query string for operational data extraction
        """
        start_time = int(self.start_time.timestamp() * 1000)
        end_time = int(self.end_time.timestamp() * 1000)

        query = SnowflakeQuery.operational_data_for_time_window(start_time, end_time)
        logger.debug(f"Generated operations query for time window: {start_time} to {end_time}")
        return query

    def _check_usage_date_ranges(self) -> None:
        """
        Check the available date ranges in Snowflake access history.

        This method queries Snowflake to determine the min/max available
        access history dates and updates the report accordingly.
        """
        with PerfTimer() as timer:
            try:
                assert self.connection is not None
                results = self.connection.query(
                    SnowflakeQuery.get_access_history_date_range()
                )
            except Exception as e:
                if isinstance(e, SnowflakePermissionError):
                    error_msg = (
                        "Failed to get usage. Please grant imported privileges on "
                        "SNOWFLAKE database."
                    )
                    self.warn_if_stateful_else_error(
                        "usage-permission-error", error_msg
                    )
                else:
                    logger.debug(e, exc_info=e)
                    self.report.report_warning(
                        "USAGE_DATE_RANGE_ERROR",
                        f"Extracting the date range for usage data from Snowflake "
                        f"failed due to error {e}.",
                    )
                self.report_status("date-range-check", False)
            else:
                for db_row in results:
                    if (
                            len(db_row) < 2
                            or db_row["MIN_TIME"] is None
                            or db_row["MAX_TIME"] is None
                    ):
                        self.report.report_warning(
                            "MISSING_USAGE_DATA",
                            f"Missing data for access_history {db_row}.",
                        )
                        break

                    self.report.min_access_history_time = db_row["MIN_TIME"].astimezone(
                        tz=timezone.utc
                    )
                    self.report.max_access_history_time = db_row["MAX_TIME"].astimezone(
                        tz=timezone.utc
                    )
                    self.report.access_history_range_query_secs = timer.elapsed_seconds(
                        digits=2
                    )

                    logger.info(
                        f"Access history available from {self.report.min_access_history_time} "
                        f"to {self.report.max_access_history_time}"
                    )

    def _get_operation_aspect_work_unit(
            self, event: SnowflakeJoinedAccessEvent, discovered_datasets: List[str]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate operation aspect work units from access events.

        Args:
            event: Snowflake access event
            discovered_datasets: List of discovered dataset identifiers

        Yields:
            MetadataWorkUnit objects containing operation aspects
        """
        if not (event.query_start_time and event.query_type):
            return

        start_time = event.query_start_time
        query_type = event.query_type
        user_email = event.email
        user_name = event.user_name

        try:
            operation_type = event.get_operation_type()
        except Exception as e:
            logger.error(f"Error getting operation type: {e}")
            logger.debug(f"Exception details:", exc_info=True)
            return
            
        reported_time: int = int(time.time() * 1000)
        last_updated_timestamp: int = int(start_time.timestamp() * 1000)

        try:
            user_urn = make_user_urn(
                self.identifiers.get_user_identifier(user_name, user_email)
            )
        except Exception as e:
            logger.error(f"Error creating user URN: {e}")
            logger.debug(f"Exception details:", exc_info=True)
            return

        # Process each modified object
        for obj in event.objects_modified:
            resource = obj.objectName
            dataset_identifier = (
                self.identifiers.get_dataset_identifier_from_qualified_name(
                    resource
                )
            )

            if dataset_identifier not in discovered_datasets:
                logger.debug(
                    f"Skipping operations for table {dataset_identifier}, "
                    f"as table schema is not accessible"
                )
                continue

            try:
                operation_aspect = OperationClass(
                    timestamp=datetime.fromtimestamp(reported_time / 1000),
                    actor=user_urn,
                    operation_type=operation_type,
                    sql_statement=event.query_text,
                    affected_rows=event.rows_inserted + event.rows_updated + event.rows_deleted,
                    query_id=getattr(event, 'query_id', None),
                )

                mcp = MetadataChangeProposalWrapper(
                    entityUrn=self.identifiers.gen_dataset_urn(dataset_identifier),
                    aspect=operation_aspect,
                )

                wu = MetadataWorkUnit(
                    id=f"{start_time.isoformat()}-operation-aspect-{resource}",
                    mcp=mcp,
                )
                yield wu
                
            except Exception as e:
                logger.error(f"Error creating operation work unit for {resource}: {e}")
                logger.debug(f"Exception details:", exc_info=True)
                continue

    def _process_snowflake_history_row(
            self, event_dict: dict
    ) -> Iterable[SnowflakeJoinedAccessEvent]:
        """
        Process a single row from Snowflake access history.

        Args:
            event_dict: Dictionary containing access history row data

        Yields:
            SnowflakeJoinedAccessEvent objects
        """
        try:
            self.report.rows_processed += 1

            # Skip events without query text
            if not event_dict["QUERY_TEXT"]:
                self.report.rows_missing_query_text += 1
                return

            # Parse object references
            self.parse_event_objects(event_dict)

            # Create event object
            event = SnowflakeJoinedAccessEvent(
                **{k.lower(): v for k, v in event_dict.items()}
            )

            yield event

        except Exception as e:
            if hasattr(self.report, 'rows_parsing_error'):
                if self.report.rows_parsing_error is None:
                    self.report.rows_parsing_error = 0
                self.report.rows_parsing_error += 1
            self.report.report_warning(
                "OPERATION_PARSING_ERROR",
                f"Failed to parse operation history row {event_dict}, {e}",
            )

    def parse_event_objects(self, event_dict: Dict) -> None:
        """
        Parse object references from access history event.

        Args:
            event_dict: Event dictionary to modify with parsed objects
        """
        # Parse base objects accessed
        event_dict["BASE_OBJECTS_ACCESSED"] = [
            obj
            for obj in json.loads(event_dict["BASE_OBJECTS_ACCESSED"])
            if self._is_object_valid(obj)
        ]
        if len(event_dict["BASE_OBJECTS_ACCESSED"]) == 0:
            self.report.rows_zero_base_objects_accessed += 1

        # Parse direct objects accessed
        event_dict["DIRECT_OBJECTS_ACCESSED"] = [
            obj
            for obj in json.loads(event_dict["DIRECT_OBJECTS_ACCESSED"])
            if self._is_object_valid(obj)
        ]
        if len(event_dict["DIRECT_OBJECTS_ACCESSED"]) == 0:
            self.report.rows_zero_direct_objects_accessed += 1

        # Parse objects modified
        event_dict["OBJECTS_MODIFIED"] = [
            obj
            for obj in json.loads(event_dict["OBJECTS_MODIFIED"])
            if self._is_object_valid(obj)
        ]
        if len(event_dict["OBJECTS_MODIFIED"]) == 0:
            self.report.rows_zero_objects_modified += 1

        # Convert timestamp to UTC
        event_dict["QUERY_START_TIME"] = (event_dict["QUERY_START_TIME"]).astimezone(
            tz=timezone.utc
        )

        # Generate email if missing
        if (
                not event_dict["EMAIL"]
                and self.config.email_domain
                and event_dict["USER_NAME"]
        ):
            # NOTE: Generated emails may be incorrect, as email may be different than
            # username@email_domain
            event_dict["EMAIL"] = (
                f"{event_dict['USER_NAME']}@{self.config.email_domain}".lower()
            )

        if not event_dict["EMAIL"]:
            self.report.rows_missing_email += 1

    def _is_unsupported_object_accessed(self, obj: Dict[str, Any]) -> bool:
        """
        Check if an object access represents an unsupported object type.

        Args:
            obj: Object access dictionary

        Returns:
            True if the object type is unsupported, False otherwise
        """
        unsupported_keys = ["locations"]

        # Skip stage objects
        if obj.get("objectDomain") in ["Stage"]:
            return True

        # Skip objects with unsupported keys
        return any([obj.get(key) is not None for key in unsupported_keys])

    def _is_object_valid(self, obj: Dict[str, Any]) -> bool:
        """
        Check if an object is valid for processing.

        Args:
            obj: Object dictionary to validate

        Returns:
            True if the object should be processed, False otherwise
        """
        if self._is_unsupported_object_accessed(obj):
            return False

        if not self.filter.is_dataset_pattern_allowed(
                obj.get("objectName"), obj.get("objectDomain")
        ):
            return False

        return True

    def _should_ingest_usage(self) -> bool:
        """
        Determine if usage should be ingested for this run.

        Returns:
            True if usage should be ingested, False otherwise
        """
        if (
                self.redundant_run_skip_handler
                and self.redundant_run_skip_handler.should_skip_this_run(
            cur_start_time=self.config.start_time,
            cur_end_time=self.config.end_time,
        )
        ):
            # Skip this run
            self.report.report_warning(
                "USAGE_EXTRACTION_SKIPPED",
                "Skip this run as there was already a run for current ingestion window.",
            )
            return False
        return True

    def report_status(self, step: str, status: bool) -> None:
        """
        Report the status of a processing step.

        Args:
            step: Name of the processing step
            status: Success status of the step
        """
        if self.redundant_run_skip_handler:
            self.redundant_run_skip_handler.report_current_run_status(step, status)

    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Get a summary of usage extraction statistics.

        Returns:
            Dictionary containing usage extraction summary
        """
        return {
            "time_window": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_hours": (self.end_time - self.start_time).total_seconds() / 3600,
            },
            "extraction_stats": {
                "rows_processed": getattr(self.report, 'rows_processed', 0),
                "rows_missing_query_text": getattr(self.report, 'rows_missing_query_text', 0),
                "rows_parsing_error": getattr(self.report, 'rows_parsing_error', 0),
                "rows_missing_email": getattr(self.report, 'rows_missing_email', 0),
            },
            "access_history": {
                "min_time": self.report.min_access_history_time.isoformat() if self.report.min_access_history_time else None,
                "max_time": self.report.max_access_history_time.isoformat() if self.report.max_access_history_time else None,
                "query_time_secs": getattr(self.report, 'access_history_query_secs', 0),
            },
            "configuration": {
                "include_usage_stats": self.config.include_usage_stats,
                "include_operational_stats": getattr(self.config.stateful_usage, 'include_operational_stats', True) if self.config.stateful_usage else True,
                "bucket_duration": str(self.config.bucket_duration),
                "top_n_queries": getattr(self.config.stateful_usage, 'top_n_queries', 1000) if self.config.stateful_usage else 1000,
            },
        }

    def close(self) -> None:
        """Clean up resources used by the usage extractor."""
        logger.info("Closing SnowflakeUsageExtractor")
        # No specific cleanup needed for this implementation


# Factory functions for creating usage extractors
def create_snowflake_usage_extractor(
        config: SnowflakeV2Config,
        report: SnowflakeV2Report,
        connection: SnowflakeConnection,
        filter: SnowflakeFilter,
        identifiers: SnowflakeIdentifierBuilder,
        redundant_run_skip_handler: Optional[RedundantUsageRunSkipHandler] = None,
) -> SnowflakeUsageExtractor:
    """
    Factory function to create a SnowflakeUsageExtractor.

    Args:
        config: Snowflake V2 configuration
        report: Snowflake V2 report
        connection: Snowflake connection
        filter: Snowflake filter
        identifiers: Identifier builder
        redundant_run_skip_handler: Optional redundant run skip handler

    Returns:
        Configured SnowflakeUsageExtractor instance
    """
    return SnowflakeUsageExtractor(
        config=config,
        report=report,
        connection=connection,
        filter=filter,
        identifiers=identifiers,
        redundant_run_skip_handler=redundant_run_skip_handler,
    )


# Utility functions
def validate_usage_config(config: SnowflakeV2Config) -> List[str]:
    """
    Validate usage extraction configuration.

    Args:
        config: Configuration to validate

    Returns:
        List of validation error messages
    """
    errors = []

    if config.include_usage_stats or (getattr(config.stateful_usage, 'include_operational_stats', True) if config.stateful_usage else True):
        if not hasattr(config, 'start_time') or not config.start_time:
            errors.append("start_time is required for usage extraction")

        if not hasattr(config, 'end_time') or not config.end_time:
            errors.append("end_time is required for usage extraction")

        if (
                config.start_time
                and config.end_time
                and config.start_time >= config.end_time
        ):
            errors.append("start_time must be before end_time")

    if config.include_usage_stats:
        if not hasattr(config, 'bucket_duration') or not config.bucket_duration:
            errors.append("bucket_duration is required for usage statistics")

    return errors


def format_time_window_summary(start_time: datetime, end_time: datetime) -> str:
    """
    Format time window for human-readable summary.

    Args:
        start_time: Start of time window
        end_time: End of time window

    Returns:
        Formatted time window string
    """
    duration = end_time - start_time
    hours = duration.total_seconds() / 3600

    return (
        f"Time window: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to "
        f"{end_time.strftime('%Y-%m-%d %H:%M:%S')} ({hours:.1f} hours)"
    )
