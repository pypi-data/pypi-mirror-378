"""
DataGuild Enhanced Snowflake Usage Extractor

Clean and enhanced usage extraction for Snowflake with improved error handling,
performance monitoring, and comprehensive reporting capabilities.

Key Improvements over DataHub:
1. Enhanced error handling and recovery
2. Better performance monitoring and timing
3. Simplified data processing pipeline
4. Comprehensive usage statistics tracking
5. Improved incremental ingestion support
6. Clean separation of concerns

Author: DataGuild Engineering Team
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pydantic

from dataguild.configuration.time_window_config import BaseTimeWindowConfig
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
from dataguild.metadata.com.linkedin.pegasus2avro.timeseries import TimeWindowSize
from dataguild.metadata.schema_classes import OperationClass, OperationTypeClass
from dataguild.sql_parsing.sqlglot_utils import try_format_query
from dataguild.utilities.perf_timer import PerfTimer
from dataguild.utilities.sql_formatter import trim_query

logger = logging.getLogger(__name__)

# Enhanced operation type mapping with more comprehensive coverage
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
    "UPSERT": OperationTypeClass.CUSTOM,
    "BULK_INSERT": OperationTypeClass.CUSTOM,
}


class PermissiveModel(pydantic.BaseModel):
    """Base model with permissive configuration for Snowflake data parsing."""

    class Config:
        extra = "allow"


class EnhancedSnowflakeColumnReference(PermissiveModel):
    """Enhanced column reference with validation and error handling."""
    columnName: str
    columnId: Optional[int] = None
    objectName: Optional[str] = None
    objectDomain: Optional[str] = None
    objectId: Optional[int] = None


class EnhancedSnowflakeObjectAccessEntry(PermissiveModel):
    """Enhanced object access entry with comprehensive metadata."""
    columns: Optional[List[EnhancedSnowflakeColumnReference]] = None
    objectDomain: str
    objectName: str
    objectId: Optional[int] = None
    stageKind: Optional[str] = None


class EnhancedSnowflakeJoinedAccessEvent(PermissiveModel):
    """Enhanced access event with comprehensive user and query information."""
    query_start_time: datetime
    query_text: str
    query_type: str
    rows_inserted: Optional[int] = None
    rows_updated: Optional[int] = None
    rows_deleted: Optional[int] = None
    base_objects_accessed: List[EnhancedSnowflakeObjectAccessEntry]
    direct_objects_accessed: List[EnhancedSnowflakeObjectAccessEntry]
    objects_modified: List[EnhancedSnowflakeObjectAccessEntry]
    user_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    role_name: str


class EnhancedSnowflakeUsageExtractor(SnowflakeCommonMixin, Closeable):
    """
    Enhanced Snowflake usage extractor with improved error handling,
    performance monitoring, and comprehensive usage statistics collection.
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
        self.config = config
        self.report = report
        self.filter = filter
        self.identifiers = identifiers
        self.connection = connection
        self.redundant_run_skip_handler = redundant_run_skip_handler

        # Enhanced initialization with error handling
        try:
            self.start_time, self.end_time = self._get_time_window()
            self.report.usage_start_time = self.start_time
            self.report.usage_end_time = self.end_time

            logger.info(
                f"Enhanced Snowflake Usage Extractor initialized for time window: "
                f"{self.start_time} to {self.end_time}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize usage extractor: {e}")
            raise

    def _get_time_window(self) -> Tuple[datetime, datetime]:
        """Get time window for usage extraction with enhanced logic."""
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
        Get usage work units with enhanced error handling and performance monitoring.
        """
        if not self._should_ingest_usage():
            logger.info("Skipping usage ingestion based on configuration or redundant run detection")
            return

        # Usage aggregation stage
        with self.report.new_stage(f"*: {USAGE_EXTRACTION_USAGE_AGGREGATION}"):
            if not self._validate_snowflake_edition():
                return

            logger.info("Checking usage date ranges")
            if not self._check_usage_date_ranges():
                logger.warning("Usage date range validation failed")
                return

            # Process usage statistics if enabled
            if self.config.include_usage_stats:
                try:
                    yield from auto_empty_dataset_usage_statistics(
                        self._get_usage_workunits_internal(discovered_datasets),
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
                except Exception as e:
                    logger.error(f"Failed to process usage statistics: {e}")
                    self.report.warning("usage-statistics", f"Usage statistics processing failed: {e}")

        # Operational statistics stage
        with self.report.new_stage(f"*: {USAGE_EXTRACTION_OPERATIONAL_STATS}"):
            if self.config.include_operational_stats:
                try:
                    access_events = self._get_snowflake_history()
                    for event in access_events:
                        yield from self._get_operation_aspect_work_unit(
                            event, discovered_datasets
                        )
                except Exception as e:
                    logger.error(f"Failed to process operational statistics: {e}")
                    self.report.warning("operational-statistics", f"Operational statistics processing failed: {e}")

            # Update checkpoint state for incremental ingestion
            if self.redundant_run_skip_handler:
                try:
                    self.redundant_run_skip_handler.update_state(
                        self.config.start_time,
                        self.config.end_time,
                        self.config.bucket_duration,
                    )
                except Exception as e:
                    logger.error(f"Failed to update checkpoint state: {e}")

    def _validate_snowflake_edition(self) -> bool:
        """Validate Snowflake edition supports usage extraction."""
        if self.report.edition == SnowflakeEdition.STANDARD.value:
            logger.info(
                "Snowflake Account is Standard Edition. Usage and Operation History Feature is not supported."
            )
            return False
        return True

    def _get_usage_workunits_internal(
            self, discovered_datasets: List[str]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Internal method to get usage work units with enhanced performance monitoring.
        """
        with PerfTimer() as timer:
            logger.info("Getting aggregated usage statistics")

            try:
                results = self.connection.query(
                    SnowflakeQuery.usage_per_object_per_time_bucket_for_time_window(
                        start_time_millis=int(self.start_time.timestamp() * 1000),
                        end_time_millis=int(self.end_time.timestamp() * 1000),
                        time_bucket_size=self.config.bucket_duration,
                        use_base_objects=self.config.apply_view_usage_to_tables,
                        top_n_queries=self.config.top_n_queries,
                        include_top_n_queries=self.config.include_top_n_queries,
                        email_domain=self.config.email_domain,
                        email_filter=self.config.user_email_pattern,
                        table_deny_pattern=self.config.temporary_tables_pattern,
                    ),
                )
            except Exception as e:
                logger.error(f"Usage statistics query failed: {e}")
                self.warn_if_stateful_else_error(
                    "usage-statistics",
                    f"Populating table usage statistics from Snowflake failed: {e}",
                )
                self._report_status(USAGE_EXTRACTION_USAGE_AGGREGATION, False)
                return

            # Update performance metrics
            self.report.usage_aggregation.query_secs = timer.elapsed_seconds()
            self.report.usage_aggregation.query_row_count = results.rowcount

        # Process results with enhanced monitoring
        with self.report.usage_aggregation.result_fetch_timer as fetch_timer:
            processed_count = 0

            for row in results:
                with (
                    fetch_timer.pause(),
                    self.report.usage_aggregation.result_skip_timer as skip_timer,
                ):
                    processed_count += 1

                    # Progress logging
                    if processed_count % 1000 == 0:
                        logger.info(f"Processed {processed_count} usage rows")
                        logger.debug(self.report.usage_aggregation.as_string())

                    # Enhanced filtering
                    if not self._is_usage_row_valid(row):
                        continue

                    dataset_identifier = (
                        self.identifiers.get_dataset_identifier_from_qualified_name(
                            row["OBJECT_NAME"]
                        )
                    )

                    if dataset_identifier not in discovered_datasets:
                        logger.debug(
                            f"Skipping usage for {dataset_identifier}, table not accessible"
                        )
                        continue

                    # Process the usage row
                    with (
                        skip_timer.pause(),
                        self.report.usage_aggregation.result_map_timer as map_timer,
                    ):
                        wu = self._build_usage_statistics_for_dataset(
                            dataset_identifier, row
                        )
                        if wu:
                            with map_timer.pause():
                                yield wu

    def _is_usage_row_valid(self, row: Dict[str, Any]) -> bool:
        """Enhanced validation for usage rows."""
        try:
            # Check if dataset is allowed by patterns
            if not self.filter.is_dataset_pattern_allowed(
                    row["OBJECT_NAME"],
                    row["OBJECT_DOMAIN"],
            ):
                logger.debug(
                    f"Skipping usage for {row['OBJECT_DOMAIN']} {row['OBJECT_NAME']}, "
                    f"not allowed by recipe patterns"
                )
                return False

            # Additional validation checks
            if not row.get("OBJECT_NAME") or not row.get("OBJECT_DOMAIN"):
                logger.debug("Skipping usage row with missing object name or domain")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating usage row: {e}")
            return False

    def _build_usage_statistics_for_dataset(
            self, dataset_identifier: str, row: Dict[str, Any]
    ) -> Optional[MetadataWorkUnit]:
        """
        Build usage statistics with enhanced error handling and validation.
        """
        try:
            stats = DatasetUsageStatistics(
                timestampMillis=int(row["BUCKET_START_TIME"].timestamp() * 1000),
                eventGranularity=TimeWindowSize(
                    unit=self.config.bucket_duration, multiple=1
                ),
                totalSqlQueries=row["TOTAL_QUERIES"],
                uniqueUserCount=row["TOTAL_USERS"],
                topSqlQueries=(
                    self._map_top_sql_queries(row["TOP_SQL_QUERIES"])
                    if self.config.include_top_n_queries and row.get("TOP_SQL_QUERIES")
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
            logger.error(
                f"Failed to build usage statistics for dataset {dataset_identifier}: {e}"
            )
            self.report.warning(
                "usage-statistics-build",
                f"Failed to build usage statistics for {dataset_identifier}",
            )
            return None

    def _map_top_sql_queries(self, top_sql_queries_str: str) -> List[str]:
        """Enhanced SQL query mapping with error handling."""
        try:
            with self.report.usage_aggregation.queries_map_timer:
                if not top_sql_queries_str:
                    return []

                top_sql_queries = json.loads(top_sql_queries_str)
                budget_per_query = max(
                    1, int(self.config.queries_character_limit / self.config.top_n_queries)
                )

                processed_queries = []
                for query in top_sql_queries:
                    try:
                        if self.config.format_sql_queries:
                            formatted_query = try_format_query(query, self.platform)
                            trimmed_query = trim_query(formatted_query, budget_per_query)
                        else:
                            trimmed_query = trim_query(query, budget_per_query)

                        processed_queries.append(trimmed_query)
                    except Exception as e:
                        logger.debug(f"Failed to process query: {e}")
                        # Fallback to original query trimmed
                        processed_queries.append(trim_query(query, budget_per_query))

                return sorted(processed_queries)

        except Exception as e:
            logger.error(f"Failed to map top SQL queries: {e}")
            return []

    def _map_user_counts(self, user_counts_str: str) -> List[DatasetUserUsageCounts]:
        """Enhanced user counts mapping with validation."""
        try:
            with self.report.usage_aggregation.users_map_timer:
                if not user_counts_str:
                    return []

                user_counts = json.loads(user_counts_str)
                filtered_user_counts = []

                for user_count in user_counts:
                    try:
                        user_email = user_count.get("email")
                        user_name = user_count.get("user_name")

                        # Enhanced email handling
                        if not user_email and self.config.email_domain and user_name:
                            user_email = f"{user_name}@{self.config.email_domain}".lower()

                        # Validate email against pattern
                        if not user_email or not self.config.user_email_pattern.allowed(user_email):
                            continue

                        filtered_user_counts.append(
                            DatasetUserUsageCounts(
                                user=make_user_urn(
                                    self.identifiers.get_user_identifier(user_name, user_email)
                                ),
                                count=user_count.get("total", 0),
                                userEmail=user_email,
                            )
                        )
                    except Exception as e:
                        logger.debug(f"Failed to process user count: {e}")
                        continue

                return sorted(filtered_user_counts, key=lambda v: v.user)

        except Exception as e:
            logger.error(f"Failed to map user counts: {e}")
            return []

    def _map_field_counts(self, field_counts_str: str) -> List[DatasetFieldUsageCounts]:
        """Enhanced field counts mapping with error handling."""
        try:
            with self.report.usage_aggregation.fields_map_timer:
                if not field_counts_str:
                    return []

                field_counts = json.loads(field_counts_str)
                processed_field_counts = []

                for field_count in field_counts:
                    try:
                        processed_field_counts.append(
                            DatasetFieldUsageCounts(
                                fieldPath=self.identifiers.snowflake_identifier(
                                    field_count["col"]
                                ),
                                count=field_count.get("total", 0),
                            )
                        )
                    except Exception as e:
                        logger.debug(f"Failed to process field count: {e}")
                        continue

                return sorted(processed_field_counts, key=lambda v: v.fieldPath)

        except Exception as e:
            logger.error(f"Failed to map field counts: {e}")
            return []

    def _get_snowflake_history(self) -> Iterable[EnhancedSnowflakeJoinedAccessEvent]:
        """Get Snowflake access history with enhanced error handling."""
        logger.info("Getting access history")

        with PerfTimer() as timer:
            try:
                query = self._make_operations_query()
                results = self.connection.query(query)
            except Exception as e:
                logger.error(f"Access history query failed: {e}")
                self.warn_if_stateful_else_error(
                    "operation",
                    f"Populating table operation history from Snowflake failed: {e}",
                )
                self._report_status(USAGE_EXTRACTION_OPERATIONAL_STATS, False)
                return

            self.report.access_history_query_secs = timer.elapsed_seconds(digits=2)

        processed_count = 0
        for row in results:
            processed_count += 1
            if processed_count % 1000 == 0:
                logger.info(f"Processed {processed_count} access history rows")

            yield from self._process_snowflake_history_row(row)

    def _make_operations_query(self) -> str:
        """Generate operations query with time window."""
        start_time = int(self.start_time.timestamp() * 1000)
        end_time = int(self.end_time.timestamp() * 1000)
        return SnowflakeQuery.operational_data_for_time_window(start_time, end_time)

    def _check_usage_date_ranges(self) -> bool:
        """Enhanced usage date range checking with better error handling."""
        with PerfTimer() as timer:
            try:
                results = self.connection.query(
                    SnowflakeQuery.get_access_history_date_range()
                )

                for db_row in results:
                    if (
                            len(db_row) < 2
                            or db_row["MIN_TIME"] is None
                            or db_row["MAX_TIME"] is None
                    ):
                        self.report.warning(
                            "check-usage-data",
                            f"Missing data for access_history: {db_row}",
                        )
                        return False

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
                        f"Usage date range: {self.report.min_access_history_time} to "
                        f"{self.report.max_access_history_time}"
                    )
                    return True

            except SnowflakePermissionError as e:
                error_msg = "Failed to get usage data. Please grant imported privileges on SNOWFLAKE database."
                logger.error(f"{error_msg}: {e}")
                self.warn_if_stateful_else_error("usage-permission-error", error_msg)
            except Exception as e:
                logger.error(f"Usage date range check failed: {e}")
                self.report.warning(
                    "usage-date-range",
                    f"Extracting the date range for usage data failed: {e}",
                )

            self._report_status("date-range-check", False)
            return False

    def _get_operation_aspect_work_unit(
            self, event: EnhancedSnowflakeJoinedAccessEvent, discovered_datasets: List[str]
    ) -> Iterable[MetadataWorkUnit]:
        """Generate operation aspect work units with enhanced processing."""
        if not (event.query_start_time and event.query_type):
            return

        try:
            start_time = event.query_start_time
            query_type = event.query_type
            user_email = event.email
            user_name = event.user_name

            operation_type = OPERATION_STATEMENT_TYPES.get(
                query_type, OperationTypeClass.CUSTOM
            )

            reported_time = int(time.time() * 1000)
            last_updated_timestamp = int(start_time.timestamp() * 1000)

            user_urn = make_user_urn(
                self.identifiers.get_user_identifier(user_name, user_email)
            )

            # Process modified objects
            for obj in event.objects_modified:
                try:
                    resource = obj.objectName
                    dataset_identifier = (
                        self.identifiers.get_dataset_identifier_from_qualified_name(resource)
                    )

                    if dataset_identifier not in discovered_datasets:
                        logger.debug(
                            f"Skipping operations for {dataset_identifier}, table not accessible"
                        )
                        continue

                    operation_aspect = OperationClass(
                        timestampMillis=reported_time,
                        lastUpdatedTimestamp=last_updated_timestamp,
                        actor=user_urn,
                        operationType=operation_type,
                        customOperationType=(
                            query_type if operation_type is OperationTypeClass.CUSTOM else None
                        ),
                    )

                    mcp = MetadataChangeProposalWrapper(
                        entityUrn=self.identifiers.gen_dataset_urn(dataset_identifier),
                        aspect=operation_aspect,
                    )

                    wu = MetadataWorkUnit(
                        id=f"{start_time.isoformat()}-operation-{resource}",
                        mcp=mcp,
                    )

                    yield wu

                except Exception as e:
                    logger.error(f"Failed to process operation for object {obj.objectName}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to generate operation work unit: {e}")

    def _process_snowflake_history_row(
            self, event_dict: Dict[str, Any]
    ) -> Iterable[EnhancedSnowflakeJoinedAccessEvent]:
        """Process Snowflake history row with enhanced error handling."""
        try:
            self.report.rows_processed += 1

            # Validate required fields
            if not event_dict.get("QUERY_TEXT"):
                self.report.rows_missing_query_text += 1
                return

            # Parse event objects with enhanced validation
            self._parse_event_objects(event_dict)

            # Create event object
            event = EnhancedSnowflakeJoinedAccessEvent(
                **{k.lower(): v for k, v in event_dict.items()}
            )

            yield event

        except Exception as e:
            self.report.rows_parsing_error += 1
            self.report.warning(
                "operation-parsing",
                f"Failed to parse operation history row: {e}",
            )

    def _parse_event_objects(self, event_dict: Dict[str, Any]) -> None:
        """Enhanced parsing of event objects with validation."""
        try:
            # Parse base objects accessed
            base_objects_raw = event_dict.get("BASE_OBJECTS_ACCESSED", "[]")
            event_dict["BASE_OBJECTS_ACCESSED"] = [
                obj for obj in json.loads(base_objects_raw) if self._is_object_valid(obj)
            ]

            if len(event_dict["BASE_OBJECTS_ACCESSED"]) == 0:
                self.report.rows_zero_base_objects_accessed += 1

            # Parse direct objects accessed
            direct_objects_raw = event_dict.get("DIRECT_OBJECTS_ACCESSED", "[]")
            event_dict["DIRECT_OBJECTS_ACCESSED"] = [
                obj for obj in json.loads(direct_objects_raw) if self._is_object_valid(obj)
            ]

            if len(event_dict["DIRECT_OBJECTS_ACCESSED"]) == 0:
                self.report.rows_zero_direct_objects_accessed += 1

            # Parse objects modified
            objects_modified_raw = event_dict.get("OBJECTS_MODIFIED", "[]")
            event_dict["OBJECTS_MODIFIED"] = [
                obj for obj in json.loads(objects_modified_raw) if self._is_object_valid(obj)
            ]

            if len(event_dict["OBJECTS_MODIFIED"]) == 0:
                self.report.rows_zero_objects_modified += 1

            # Parse query start time
            if "QUERY_START_TIME" in event_dict and event_dict["QUERY_START_TIME"]:
                event_dict["QUERY_START_TIME"] = event_dict["QUERY_START_TIME"].astimezone(
                    tz=timezone.utc
                )

            # Enhanced email handling
            if not event_dict.get("EMAIL") and self.config.email_domain and event_dict.get("USER_NAME"):
                event_dict["EMAIL"] = (
                    f"{event_dict['USER_NAME']}@{self.config.email_domain}".lower()
                )

            if not event_dict.get("EMAIL"):
                self.report.rows_missing_email += 1

        except Exception as e:
            logger.error(f"Failed to parse event objects: {e}")
            raise

    def _is_object_valid(self, obj: Dict[str, Any]) -> bool:
        """Enhanced object validation with comprehensive checks."""
        try:
            # Check for unsupported object types
            if self._is_unsupported_object_accessed(obj):
                return False

            # Check dataset patterns
            object_name = obj.get("objectName")
            object_domain = obj.get("objectDomain")

            if not object_name or not object_domain:
                return False

            if not self.filter.is_dataset_pattern_allowed(object_name, object_domain):
                return False

            return True

        except Exception as e:
            logger.debug(f"Error validating object: {e}")
            return False

    def _is_unsupported_object_accessed(self, obj: Dict[str, Any]) -> bool:
        """Check if object is of unsupported type."""
        unsupported_keys = ["locations"]
        unsupported_domains = ["Stage"]

        if obj.get("objectDomain") in unsupported_domains:
            return True

        return any(obj.get(key) is not None for key in unsupported_keys)

    def _should_ingest_usage(self) -> bool:
        """Enhanced check for whether usage ingestion should proceed."""
        if (
                self.redundant_run_skip_handler
                and self.redundant_run_skip_handler.should_skip_this_run(
            cur_start_time=self.config.start_time,
            cur_end_time=self.config.end_time,
        )
        ):
            self.report.report_warning(
                "usage-extraction",
                "Skipping run due to redundant run detection",
            )
            return False

        return True

    def _report_status(self, step: str, status: bool) -> None:
        """Report status to redundant run skip handler."""
        if self.redundant_run_skip_handler:
            self.redundant_run_skip_handler.report_current_run_status(step, status)

    def close(self) -> None:
        """Clean up resources."""
        logger.info("Closing Enhanced Snowflake Usage Extractor")
        # Any cleanup logic can be added here


# Utility functions for usage extraction

def create_usage_extractor(
        config: SnowflakeV2Config,
        report: SnowflakeV2Report,
        connection: SnowflakeConnection,
        filter: SnowflakeFilter,
        identifiers: SnowflakeIdentifierBuilder,
        enable_redundant_skip: bool = True
) -> EnhancedSnowflakeUsageExtractor:
    """Factory function to create usage extractor with standard configuration."""

    redundant_handler = None
    if enable_redundant_skip:
        redundant_handler = RedundantUsageRunSkipHandler()

    extractor = EnhancedSnowflakeUsageExtractor(
        config=config,
        report=report,
        connection=connection,
        filter=filter,
        identifiers=identifiers,
        redundant_run_skip_handler=redundant_handler
    )

    logger.info("Created Enhanced Snowflake Usage Extractor")
    return extractor


def validate_usage_config(config: SnowflakeV2Config) -> List[str]:
    """Validate usage extraction configuration."""
    issues = []

    if config.include_usage_stats and not config.start_time:
        issues.append("start_time is required when include_usage_stats is enabled")

    if config.include_usage_stats and not config.end_time:
        issues.append("end_time is required when include_usage_stats is enabled")

    if config.top_n_queries <= 0:
        issues.append("top_n_queries must be positive")

    if config.queries_character_limit <= 0:
        issues.append("queries_character_limit must be positive")

    return issues
