"""
DataGuild Snowflake Lineage Extractor v2.

This module provides comprehensive lineage extraction from Snowflake including:
1. External lineage (S3 to Table via COPY operations)
2. Table-to-Table and View-to-Table lineage via access_history
3. Column-level lineage tracking and analysis
4. Time-based lineage extraction with redundant run handling
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Collection, Iterable, List, Optional, Set, Tuple, Type, Union, Dict

from pydantic import BaseModel, Field, validator

from dataguild.configuration.datetimes import parse_absolute_time
from dataguild.api.closeable import Closeable
from dataguild.source.aws.s3_util import make_s3_urn_for_lineage
from dataguild.source.snowflake.constants import (
    LINEAGE_PERMISSION_ERROR,
    SnowflakeEdition,
)
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
    RedundantLineageRunSkipHandler,
)
from dataguild.metadata.schema_classes import DatasetLineageTypeClass, UpstreamClass
from dataguild.sql_parsing.sql_parsing_aggregator import (
    KnownLineageMapping,
    KnownQueryLineageInfo,
    SqlParsingAggregator,
    UrnStr,
)
from dataguild.source.snowflake.stored_proc_lineage import (
    StoredProcCall,
    StoredProcLineageTracker,
)
from dataguild.sql_parsing.sqlglot_lineage import (
    ColumnLineageInfo,
    ColumnRef,
    DownstreamColumnRef,
)
from dataguild.sql_parsing.sqlglot_utils import get_query_fingerprint
from dataguild.utilities.perf_timer import PerfTimer
from dataguild.utilities.time import ts_millis_to_datetime

logger: logging.Logger = logging.getLogger(__name__)

# Constants for lineage types
EXTERNAL_LINEAGE = "external_lineage"
TABLE_LINEAGE = "table_lineage"
VIEW_LINEAGE = "view_lineage"


def pydantic_parse_json(field: str) -> classmethod:
    """
    Create a Pydantic validator for parsing JSON fields.

    Args:
        field: Field name to create validator for

    Returns:
        Pydantic validator function
    """
    def _parse_from_json(cls: Type, v: Any) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v

    return validator(field, pre=True, allow_reuse=True)(_parse_from_json)


class UpstreamColumnNode(BaseModel):
    """Represents an upstream column reference in lineage."""

    object_name: str
    object_domain: str
    column_name: str


class ColumnUpstreamJob(BaseModel):
    """Represents a set of column upstreams for a specific query - DataHub compatible."""

    column_upstreams: List[Union[UpstreamColumnNode, Dict[str, Any]]] = Field(default_factory=list)
    query_id: str


class ColumnUpstreamLineage(BaseModel):
    """Represents column-level lineage information."""

    column_name: Optional[str] = None
    upstreams: List[ColumnUpstreamJob] = Field(default_factory=list)


class UpstreamTableNode(BaseModel):
    """Represents an upstream table in lineage."""

    upstream_object_domain: str
    upstream_object_name: str
    query_id: str


class Query(BaseModel):
    """Represents a SQL query with metadata."""

    query_id: str
    query_text: str
    start_time: str
    query_type: Optional[str] = None
    root_query_id: Optional[str] = None
    user: Optional[str] = None
    default_db: Optional[str] = None
    default_schema: Optional[str] = None


class UpstreamLineageEdge(BaseModel):
    """
    Represents a complete lineage edge with upstream and downstream information.

    This model handles JSON parsing for complex nested structures returned
    from Snowflake's access_history queries.
    """

    DOWNSTREAM_TABLE_NAME: str
    DOWNSTREAM_TABLE_DOMAIN: str
    UPSTREAM_TABLES: Optional[List[UpstreamTableNode]] = None
    UPSTREAM_COLUMNS: Optional[List[ColumnUpstreamLineage]] = None
    QUERIES: Optional[List[Query]] = None

    # JSON parsing validators for complex fields
    _json_upstream_tables = pydantic_parse_json("UPSTREAM_TABLES")
    _json_upstream_columns = pydantic_parse_json("UPSTREAM_COLUMNS")
    _json_queries = pydantic_parse_json("QUERIES")


@dataclass(frozen=True)
class SnowflakeColumnId:
    """
    Immutable identifier for a Snowflake column.

    Used for tracking column-level lineage relationships
    across different tables and views.
    """

    column_name: str
    object_name: str
    object_domain: Optional[str] = None


class SnowflakeLineageExtractor(SnowflakeCommonMixin, Closeable):
    """
    Extracts comprehensive lineage information from Snowflake.

    This extractor handles multiple types of lineage relationships:
    1. "Table to View" lineage via object_dependencies view + View definition SQL parsing
    2. "S3 to Table" lineage via external tables and copy_history view
    3. "View to Table" and "Table to Table" lineage via access_history view

    Edition Note: Snowflake Standard Edition does not have Access History Feature,
    so it does not support lineage extraction for access_history-based edges.

    Examples:
        >>> extractor = SnowflakeLineageExtractor(
        ...     config=config,
        ...     report=report,
        ...     connection=connection,
        ...     filters=filters,
        ...     identifiers=identifiers,
        ...     redundant_run_skip_handler=handler,
        ...     sql_aggregator=aggregator
        ... )
        >>> extractor.add_time_based_lineage_to_aggregator(
        ...     discovered_tables=tables,
        ...     discovered_views=views
        ... )
    """

    def __init__(
        self,
        config: SnowflakeV2Config,
        report: SnowflakeV2Report,
        connection: SnowflakeConnection,
        filters: SnowflakeFilter,
        identifiers: SnowflakeIdentifierBuilder,
        redundant_run_skip_handler: Optional[RedundantLineageRunSkipHandler],
        sql_aggregator: SqlParsingAggregator,
    ) -> None:
        """
        Initialize the Snowflake lineage extractor.

        Args:
            config: Snowflake configuration with lineage settings
            report: Report object for tracking extraction progress
            connection: Active Snowflake connection
            filters: Filters for datasets and objects
            identifiers: Builder for generating URNs and identifiers
            redundant_run_skip_handler: Handler for avoiding redundant runs
            sql_aggregator: Aggregator for processing SQL and lineage
        """
        self.config = config
        self.report = report
        self.connection = connection
        self.filters = filters
        self.identifiers = identifiers
        self.redundant_run_skip_handler = redundant_run_skip_handler
        self.sql_aggregator = sql_aggregator

        # Initialize stored procedure lineage tracker (will be created when needed)
        self.stored_proc_tracker: Optional[StoredProcLineageTracker] = None

        # Get time window for lineage extraction
        self.start_time, self.end_time = (
            self.report.lineage_start_time,
            self.report.lineage_end_time,
        ) = self.get_time_window()

        logger.info(
            f"Initialized SnowflakeLineageExtractor for time window: "
            f"{self.start_time} to {self.end_time}"
        )

    def get_time_window(self) -> Tuple[datetime, datetime]:
        """
        Determine the time window for lineage extraction.

        Uses redundant run skip handler to suggest optimal time windows
        if available, otherwise uses configuration defaults.

        Returns:
            Tuple of (start_time, end_time) for lineage extraction
        """
        if self.redundant_run_skip_handler:
            return self.redundant_run_skip_handler.suggest_run_time_window(
                (
                    self.config.start_time
                    if not self.config.ignore_start_time_lineage
                    else ts_millis_to_datetime(0)
                ),
                self.config.end_time,
            )
        else:
            return (
                (
                    self.config.start_time
                    if not self.config.ignore_start_time_lineage
                    else ts_millis_to_datetime(0)
                ),
                self.config.end_time,
            )

    def add_time_based_lineage_to_aggregator(
        self,
        discovered_tables: List[str],
        discovered_views: List[str],
    ) -> None:
        """
        Main entry point for adding time-based lineage to the SQL aggregator.

        This method orchestrates the extraction of both external and internal
        lineage relationships within the configured time window.

        Args:
            discovered_tables: List of discovered table identifiers
            discovered_views: List of discovered view identifiers
        """
        if not self._should_ingest_lineage():
            logger.info("Skipping lineage ingestion based on redundant run handler")
            return

        logger.info("Starting time-based lineage extraction")

        # Extract S3 dataset -> Snowflake table lineage
        self._populate_external_upstreams(discovered_tables)

        # Extract Snowflake view/table -> Snowflake table lineage
        self.populate_table_upstreams(discovered_tables, discovered_views)

        # Process stored procedure lineage
        self._process_stored_proc_lineage()

        logger.info("Completed time-based lineage extraction")

    def update_state(self):
        """
        Update the state for redundant run handling.

        This should be called after successful lineage extraction
        to mark the current time window as processed.
        """
        if self.redundant_run_skip_handler:
            # Update the checkpoint state for this run
            self.redundant_run_skip_handler.update_state(
                (
                    self.config.start_time
                    if not self.config.ignore_start_time_lineage
                    else ts_millis_to_datetime(0)
                ),
                self.config.end_time,
            )
            logger.info("Updated redundant run skip handler state")

    def populate_table_upstreams(self, discovered_tables: List[str], discovered_views: List[str] = None) -> None:
        """
        Populate table-to-table lineage from Snowflake's access_history.

        This method extracts lineage relationships between Snowflake objects
        using the access_history view, which requires Enterprise Edition or above.

        Args:
            discovered_tables: List of discovered table identifiers
            discovered_views: List of discovered view identifiers
        """
        if self.report.edition == SnowflakeEdition.STANDARD:
            logger.info(
                "Snowflake Account is Standard Edition. Table to Table and View to Table "
                "Lineage Feature is not supported."
            )
            # TODO: use sql_aggregator.add_observed_query to report queries from
            # snowflake.account_usage.query_history and let DataGuild generate lineage, usage and operations
            return

        logger.info("Extracting table-to-table lineage from access_history")

        # Combine tables and views into discovered_assets for comprehensive lineage
        discovered_assets = list(discovered_tables)
        if discovered_views:
            discovered_assets.extend(discovered_views)
            logger.info(f"Combined {len(discovered_tables)} tables and {len(discovered_views)} views into {len(discovered_assets)} discovered assets")
        else:
            logger.info(f"Using {len(discovered_tables)} tables as discovered assets")

        with PerfTimer() as timer:
            results = self._fetch_upstream_lineages_for_tables()
            if not results:
                logger.warning("No upstream lineage results found")
                return

            self.populate_known_query_lineage(discovered_assets, results)
            self.report.table_lineage_query_secs = timer.elapsed_seconds()

        logger.info(
            f"Upstream lineage detected for {self.report.num_tables_with_known_upstreams} tables. "
            f"Processing took {self.report.table_lineage_query_secs:.2f} seconds."
        )

    def populate_known_query_lineage(
        self,
        discovered_assets: Collection[str],
        results: Iterable[UpstreamLineageEdge],
    ) -> None:
        """
        Process upstream lineage results and add them to the SQL aggregator.
        Following DataHub's approach: only process lineage when QUERIES are present.

        Args:
            discovered_assets: Collection of discovered asset identifiers
            results: Iterable of upstream lineage edges from Snowflake
        """
        processed_count = 0

        for db_row in results:
            try:
                dataset_name = self.identifiers.get_dataset_identifier_from_qualified_name(
                    db_row.DOWNSTREAM_TABLE_NAME
                )

                # Debug logging for lineage matching
                logger.info(f"Processing lineage edge: {db_row.DOWNSTREAM_TABLE_NAME} -> {dataset_name}")
                logger.info(f"Discovered assets: {list(discovered_assets)}")
                logger.info(f"Dataset in discovered assets: {dataset_name in discovered_assets}")
                logger.info(f"Has queries: {bool(db_row.QUERIES)}")
                logger.info(f"QUERIES field type: {type(db_row.QUERIES)}")
                logger.info(f"QUERIES field value: {db_row.QUERIES}")
                logger.info(f"UPSTREAM_COLUMNS: {db_row.UPSTREAM_COLUMNS}")

                # Skip if dataset not discovered or no queries (following DataHub approach)
                if dataset_name not in discovered_assets or not db_row.QUERIES:
                    logger.warning(f"Skipping lineage edge for {dataset_name}: not discovered or no queries")
                    continue

                # Process each query (DataHub approach)
                for query in db_row.QUERIES:
                    # Check if this is a stored procedure call
                    if self._is_stored_proc_call(query):
                        self._process_stored_proc_call(query, dataset_name)
                        continue

                    known_lineage = self.get_known_query_lineage(
                        query, dataset_name, db_row
                    )

                    if known_lineage and known_lineage.upstreams:
                        self.report.num_tables_with_known_upstreams += 1
                        self.sql_aggregator.add(known_lineage)
                        processed_count += 1

                        logger.info(
                            f"Added lineage for {dataset_name}: "
                            f"{known_lineage.upstreams} -> {known_lineage.downstream}"
                        )
                        
                        # Log column-level lineage if available
                        if hasattr(known_lineage, 'column_lineage') and known_lineage.column_lineage:
                            column_lineage = known_lineage.column_lineage
                            logger.info(f"Added {len(column_lineage)} column-level lineage entries for {dataset_name}")
                            for col_lineage in column_lineage:
                                logger.info(f"Column lineage: {col_lineage.downstream.column} <- {[up.column for up in col_lineage.upstreams]}")
                    else:
                        logger.debug(f"No lineage found for {dataset_name}")

            except Exception as e:
                logger.error(f"Error processing lineage edge: {e}", exc_info=True)
                continue

        logger.info(f"Processed {processed_count} known query lineage entries")
        logger.info(f"SQL aggregator lineage map now has {len(self.sql_aggregator._lineage_map)} entries")

    def get_known_query_lineage(
        self, query: Query, dataset_name: str, db_row: UpstreamLineageEdge
    ) -> Optional[KnownQueryLineageInfo]:
        """
        Convert a query and lineage edge into a KnownQueryLineageInfo object.

        Args:
            query: Query information from Snowflake
            dataset_name: Downstream dataset identifier
            db_row: Upstream lineage edge data

        Returns:
            KnownQueryLineageInfo object or None if no upstreams
        """
        if not db_row.UPSTREAM_TABLES:
            return None

        try:
            downstream_table_urn = self.identifiers.gen_dataset_urn(dataset_name)

            # Get upstream URNs
            upstream_urns = self.map_query_result_upstreams(
                db_row.UPSTREAM_TABLES, query.query_id
            )
            
            if not upstream_urns:
                return None
                
            # Create KnownQueryLineageInfo matching DataHub structure
            known_lineage = KnownQueryLineageInfo(
                query_text=query.query_text,
                downstream=downstream_table_urn,
                upstreams=upstream_urns,
                column_lineage=(
                    self.map_query_result_fine_upstreams(
                        downstream_table_urn,
                        db_row.UPSTREAM_COLUMNS,
                        query.query_id,
                    )
                    if (self.config.include_column_lineage and db_row.UPSTREAM_COLUMNS)
                    else None
                ),
                timestamp=parse_absolute_time(query.start_time),
                query_id=get_query_fingerprint(
                    query.query_text, self.identifiers.platform
                ),
            )

            return known_lineage

        except Exception as e:
            logger.error(f"Error creating known query lineage: {e}")
            return None

    def _populate_external_upstreams(self, discovered_tables: List[str]) -> None:
        """
        Populate external lineage from S3 and other external sources.

        This method extracts lineage from COPY operations that load data
        from external sources like S3 into Snowflake tables.

        Args:
            discovered_tables: List of discovered table identifiers
        """
        logger.info("Extracting external lineage from copy history")

        with PerfTimer() as timer:
            self.report.num_external_table_edges_scanned = 0

            for entry in self._get_copy_history_lineage(discovered_tables):
                self.sql_aggregator.add(entry)

            self.report.external_lineage_queries_secs = timer.elapsed_seconds()

        logger.info(
            f"External lineage extraction completed. "
            f"Scanned {self.report.num_external_table_edges_scanned} edges in "
            f"{self.report.external_lineage_queries_secs:.2f} seconds."
        )

    def _get_copy_history_lineage(
        self, discovered_tables: List[str]
    ) -> Iterable[KnownLineageMapping]:
        """
        Extract lineage from Snowflake's copy_history view.

        Handles cases where tables are populated from external stages/S3 locations via COPY.
        Examples:
        - COPY INTO category_english FROM @external_s3_stage;
        - COPY INTO category_english FROM 's3://bucket/path/' CREDENTIALS=(...);

        Note: Snowflake does not log this information to the access_history table.

        Args:
            discovered_tables: List of discovered table identifiers

        Yields:
            KnownLineageMapping objects representing external lineage
        """
        query: str = SnowflakeQuery.copy_lineage_history(
            start_time_millis=int(self.start_time.timestamp() * 1000),
            end_time_millis=int(self.end_time.timestamp() * 1000),
            downstreams_deny_pattern=self.config.temporary_tables_pattern,
        )

        try:
            for db_row in self.connection.query(query):
                try:
                    known_lineage_mapping = self._process_external_lineage_result_row(
                        db_row, discovered_tables, identifiers=self.identifiers
                    )

                    if known_lineage_mapping:
                        self.report.num_external_table_edges_scanned += 1
                        yield known_lineage_mapping

                except Exception as e:
                    logger.error(f"Error processing external lineage row: {e}")
                    continue

        except Exception as e:
            if isinstance(e, SnowflakePermissionError):
                error_msg = (
                    "Failed to get external lineage. Please grant imported privileges "
                    "on SNOWFLAKE database."
                )
                self.warn_if_stateful_else_error(LINEAGE_PERMISSION_ERROR, error_msg)
            else:
                self.structured_reporter.warning(
                    "Error fetching external lineage from Snowflake",
                    exc=e,
                )
            self.report_status(EXTERNAL_LINEAGE, False)

    @classmethod
    def _process_external_lineage_result_row(
        cls,
        db_row: dict,
        discovered_tables: Optional[Collection[str]],
        identifiers: SnowflakeIdentifierBuilder,
    ) -> Optional[KnownLineageMapping]:
        """
        Process a single row from copy_history query into a lineage mapping.

        Args:
            db_row: Database row from copy_history query
            discovered_tables: Collection of discovered table identifiers
            identifiers: Identifier builder for generating URNs

        Returns:
            KnownLineageMapping or None if not applicable
        """
        # Extract downstream table identifier
        key: str = identifiers.get_dataset_identifier_from_qualified_name(
            db_row["DOWNSTREAM_TABLE_NAME"]
        )

        # Skip if table not discovered
        if discovered_tables is not None and key not in discovered_tables:
            return None

        # Process upstream locations
        if db_row["UPSTREAM_LOCATIONS"] is not None:
            try:
                external_locations = json.loads(db_row["UPSTREAM_LOCATIONS"])

                for loc in external_locations:
                    if loc.startswith("s3://"):
                        return KnownLineageMapping(
                            upstream_urn=make_s3_urn_for_lineage(
                                loc, identifiers.identifier_config.env
                            ),
                            downstream_urn=identifiers.gen_dataset_urn(key),
                        )

            except Exception as e:
                logger.error(f"Error parsing upstream locations: {e}")

        return None

    def _fetch_upstream_lineages_for_tables(self) -> Iterable[UpstreamLineageEdge]:
        """
        Fetch upstream lineage information from Snowflake's access_history.

        Returns:
            Iterable of UpstreamLineageEdge objects
        """
        # Use column-level lineage query if column lineage is enabled
        if self.config.include_column_lineage:
            query: str = SnowflakeQuery.table_upstreams_with_column_lineage(
                start_time_millis=int(self.start_time.timestamp() * 1000),
                end_time_millis=int(self.end_time.timestamp() * 1000),
                upstreams_deny_pattern=self.config.temporary_tables_pattern,
            )
            logger.info("Using column-level lineage query for comprehensive extraction")
        else:
            query: str = SnowflakeQuery.table_to_table_lineage_history_v2(
                start_time_millis=int(self.start_time.timestamp() * 1000),
                end_time_millis=int(self.end_time.timestamp() * 1000),
                upstreams_deny_pattern=self.config.temporary_tables_pattern,
                include_column_lineage=self.config.include_column_lineage,
            )
            logger.info("Using table-level lineage query")

        try:
            for db_row in self.connection.query(query):
                edge = self._process_upstream_lineage_row(db_row)
                if edge:
                    yield edge

        except Exception as e:
            if isinstance(e, SnowflakePermissionError):
                error_msg = (
                    "Failed to get table/view to table lineage. Please grant imported "
                    "privileges on SNOWFLAKE database."
                )
                self.warn_if_stateful_else_error(LINEAGE_PERMISSION_ERROR, error_msg)
            else:
                self.structured_reporter.warning(
                    "Failed to extract table/view -> table lineage from Snowflake",
                    exc=e,
                )
            self.report_status(TABLE_LINEAGE, False)

    def _process_upstream_lineage_row(
        self, db_row: dict
    ) -> Optional[UpstreamLineageEdge]:
        """
        Process a single upstream lineage row into an UpstreamLineageEdge.

        Args:
            db_row: Raw database row from access_history query

        Returns:
            UpstreamLineageEdge or None if parsing failed
        """
        try:
            # Handle empty queries array case
            _queries = db_row.get("QUERIES")
            if _queries == "[\n  {}\n]":
                # Snowflake sometimes returns an empty object in the array
                # Set to empty array to avoid Pydantic parsing errors
                db_row["QUERIES"] = "[]"

            return UpstreamLineageEdge.parse_obj(db_row)

        except Exception as e:
            self.report.num_upstream_lineage_edge_parsing_failed += 1

            # Extract key information for debugging
            upstream_tables = db_row.get("UPSTREAM_TABLES")
            downstream_table = db_row.get("DOWNSTREAM_TABLE_NAME")

            self.structured_reporter.warning(
                "Failed to parse lineage edge",
                context=(
                    f"Upstreams: {upstream_tables} "
                    f"Downstream: {downstream_table} "
                    f"Full row: {db_row}"
                ),
                exc=e,
            )
            return None

    def map_query_result_upstreams(
        self, upstream_tables: Optional[List[UpstreamTableNode]], query_id: str
    ) -> List[UrnStr]:
        """
        Map upstream table nodes to URN strings.

        Args:
            upstream_tables: List of upstream table nodes
            query_id: Query ID to match against

        Returns:
            List of upstream URN strings
        """
        if not upstream_tables:
            return []

        upstreams: List[UrnStr] = []

        for upstream_table in upstream_tables:
            if upstream_table and upstream_table.query_id == query_id:
                try:
                    upstream_name = (
                        self.identifiers.get_dataset_identifier_from_qualified_name(
                            upstream_table.upstream_object_name
                        )
                    )

                    # Validate upstream against patterns if configured
                    if upstream_name and (
                        not self.config.validate_upstreams_against_patterns
                        or self.filters.is_dataset_pattern_allowed(
                            upstream_name,
                            upstream_table.upstream_object_domain,
                        )
                    ):
                        upstreams.append(
                            self.identifiers.gen_dataset_urn(upstream_name)
                        )

                except Exception as e:
                    logger.debug(f"Error processing upstream table: {e}", exc_info=True)

        return upstreams

    def map_query_result_fine_upstreams(
        self,
        dataset_urn: str,
        column_wise_upstreams: Optional[List[ColumnUpstreamLineage]],
        query_id: str,
    ) -> List[ColumnLineageInfo]:
        """
        Map column-wise upstream information to ColumnLineageInfo objects.

        Args:
            dataset_urn: URN of the downstream dataset
            column_wise_upstreams: List of column upstream lineage information
            query_id: Query ID to match against

        Returns:
            List of ColumnLineageInfo objects
        """
        if not column_wise_upstreams:
            return []

        fine_upstreams: List[ColumnLineageInfo] = []

        for column_with_upstreams in column_wise_upstreams:
            if column_with_upstreams:
                try:
                    self._process_add_single_column_upstream(
                        dataset_urn, fine_upstreams, column_with_upstreams, query_id
                    )
                except Exception as e:
                    logger.debug(f"Error processing column upstream: {e}", exc_info=True)

        return fine_upstreams

    def _process_add_single_column_upstream(
        self,
        dataset_urn: str,
        fine_upstreams: List[ColumnLineageInfo],
        column_with_upstreams: ColumnUpstreamLineage,
        query_id: str,
    ) -> None:
        """
        Process a single column's upstream lineage information - DataHub compatible.

        Args:
            dataset_urn: URN of the downstream dataset
            fine_upstreams: List to append new ColumnLineageInfo to
            column_with_upstreams: Column upstream lineage data
            query_id: Query ID to match against
        """
        column_name = column_with_upstreams.column_name
        upstream_jobs = column_with_upstreams.upstreams

        if column_name and upstream_jobs:
            for upstream_job in upstream_jobs:
                if not upstream_job or upstream_job.query_id != query_id:
                    continue

                # Handle DataHub's new structure where column_upstreams is a list of objects
                upstream_columns = set()
                for col_upstream in upstream_job.column_upstreams:
                    if isinstance(col_upstream, dict):
                        # Handle DataHub's structure: {'object_name': ..., 'object_domain': ..., 'column_name': ...}
                        upstream_columns.add(SnowflakeColumnId(
                            column_name=col_upstream.get('column_name'),
                            object_name=col_upstream.get('object_name'),
                            object_domain=col_upstream.get('object_domain'),
                        ))
                    else:
                        # Handle our old structure
                        upstream_columns.add(SnowflakeColumnId(
                            column_name=col_upstream.column_name,
                            object_name=col_upstream.object_name,
                            object_domain=col_upstream.object_domain,
                        ))

                fine_upstream = self.build_finegrained_lineage(
                    dataset_urn=dataset_urn,
                    col=column_name,
                    upstream_columns=upstream_columns,
                )

                if fine_upstream:
                    fine_upstreams.append(fine_upstream)

    def build_finegrained_lineage(
        self,
        dataset_urn: str,
        col: str,
        upstream_columns: Set[SnowflakeColumnId],
    ) -> Optional[ColumnLineageInfo]:
        """
        Build fine-grained column lineage information.

        Args:
            dataset_urn: URN of the downstream dataset
            col: Downstream column name
            upstream_columns: Set of upstream column identifiers

        Returns:
            ColumnLineageInfo or None if no valid upstreams
        """
        column_upstreams = self.build_finegrained_lineage_upstreams(upstream_columns)

        if not column_upstreams:
            return None

        column_lineage = ColumnLineageInfo(
            downstream=DownstreamColumnRef(
                dataset=dataset_urn,
                column=self.identifiers.snowflake_identifier(col)
            ),
            upstreams=sorted(column_upstreams),
        )

        return column_lineage

    def build_finegrained_lineage_upstreams(
        self, upstream_columns: Set[SnowflakeColumnId]
    ) -> List[ColumnRef]:
        """
        Build list of upstream column references.

        Args:
            upstream_columns: Set of upstream column identifiers

        Returns:
            List of ColumnRef objects
        """
        column_upstreams = []

        for upstream_col in upstream_columns:
            if (
                upstream_col.object_name
                and upstream_col.column_name
                and (
                    not self.config.validate_upstreams_against_patterns
                    or self.filters.is_dataset_pattern_allowed(
                        upstream_col.object_name,
                        upstream_col.object_domain,
                    )
                )
            ):
                try:
                    upstream_dataset_name = (
                        self.identifiers.get_dataset_identifier_from_qualified_name(
                            upstream_col.object_name
                        )
                    )

                    column_upstreams.append(
                        ColumnRef(
                            table=self.identifiers.gen_dataset_urn(upstream_dataset_name),
                            column=self.identifiers.snowflake_identifier(
                                upstream_col.column_name
                            ),
                        )
                    )

                except Exception as e:
                    logger.debug(f"Error building upstream column ref: {e}")

        return column_upstreams

    def get_external_upstreams(self, external_lineage: Set[str]) -> List[UpstreamClass]:
        """
        Convert external lineage entries to UpstreamClass objects.

        Args:
            external_lineage: Set of external lineage URN strings

        Returns:
            List of UpstreamClass objects
        """
        external_upstreams = []

        for external_lineage_entry in sorted(external_lineage):
            # Currently only handle S3 external sources
            if external_lineage_entry.startswith("s3://"):
                external_upstream_table = UpstreamClass(
                    dataset=make_s3_urn_for_lineage(
                        external_lineage_entry, self.config.env
                    ),
                    type=DatasetLineageTypeClass.COPY,
                )
                external_upstreams.append(external_upstream_table)

        return external_upstreams

    def _should_ingest_lineage(self) -> bool:
        """
        Determine if lineage should be ingested for this run.

        Uses redundant run skip handler to avoid processing the same
        time window multiple times.

        Returns:
            True if lineage should be ingested, False otherwise
        """
        if (
            self.redundant_run_skip_handler
            and self.redundant_run_skip_handler.should_skip_this_run(
                cur_start_time=(
                    self.config.start_time
                    if not self.config.ignore_start_time_lineage
                    else ts_millis_to_datetime(0)
                ),
                cur_end_time=self.config.end_time,
            )
        ):
            # Skip this run - already processed
            self.report.report_warning(
                "lineage-extraction",
                "Skip this run as there was already a run for current ingestion window.",
            )
            return False

        return True

    def report_status(self, step: str, status: bool) -> None:
        """
        Report the status of a lineage extraction step.

        Args:
            step: Name of the step being reported
            status: Whether the step was successful
        """
        if self.redundant_run_skip_handler:
            self.redundant_run_skip_handler.report_current_run_status(step, status)

    def _is_stored_proc_call(self, query: Query) -> bool:
        """
        Check if a query is a stored procedure call.
        
        Args:
            query: Query object to check
            
        Returns:
            True if the query is a stored procedure call
        """
        if not query.query_text:
            return False
        
        query_text = query.query_text.strip().upper()
        return query_text.startswith('CALL ') and query.root_query_id is None

    def _process_stored_proc_call(self, query: Query, dataset_name: str) -> None:
        """
        Process a stored procedure call and add it to the stored procedure tracker.
        
        Args:
            query: Query object representing the stored procedure call
            dataset_name: Name of the dataset being processed
        """
        try:
            # Initialize stored procedure tracker if not already done
            if self.stored_proc_tracker is None:
                self.stored_proc_tracker = StoredProcLineageTracker(
                    platform=self.identifiers.platform,
                    shared_connection=None,
                )
            
            # Create a StoredProcCall object
            stored_proc_call = StoredProcCall(
                snowflake_root_query_id=query.query_id,
                query_text=query.query_text,
                timestamp=query.start_time,
                user=query.user,
                default_db=query.default_db,
                default_schema=query.default_schema,
            )
            
            # Add to stored procedure tracker
            self.stored_proc_tracker.add_stored_proc_call(stored_proc_call)
            
            logger.info(f"Added stored procedure call: {query.query_text[:50]}...")
            
        except Exception as e:
            logger.error(f"Error processing stored procedure call: {e}")

    def _process_stored_proc_lineage(self) -> None:
        """
        Process stored procedure lineage and add to SQL aggregator.
        This should be called after all queries have been processed.
        """
        try:
            # Skip if no stored procedure tracker was initialized
            if self.stored_proc_tracker is None:
                logger.info("No stored procedure calls found, skipping stored procedure lineage processing")
                return
            
            # Generate and add stored procedure lineage entries
            for lineage_entry in self.stored_proc_tracker.build_merged_lineage_entries():
                self.sql_aggregator.add(lineage_entry)
                logger.info(f"Added stored procedure lineage entry: {lineage_entry}")
                
        except Exception as e:
            logger.error(f"Error processing stored procedure lineage: {e}")

    def close(self) -> None:
        """Close the lineage extractor and clean up resources."""
        logger.info("Closing SnowflakeLineageExtractor")
        # No specific cleanup needed for this implementation


# Export all classes
__all__ = [
    'SnowflakeLineageExtractor',
    'UpstreamLineageEdge',
    'UpstreamTableNode',
    'UpstreamColumnNode',
    'ColumnUpstreamJob',
    'ColumnUpstreamLineage',
    'Query',
    'SnowflakeColumnId',
    'pydantic_parse_json',
]


# Example usage and testing
if __name__ == "__main__":
    print("=== DataGuild Snowflake Lineage Extractor Examples ===\n")

    # Example 1: Create Pydantic models
    upstream_table = UpstreamTableNode(
        upstream_object_domain="TABLE",
        upstream_object_name="RAW.CUSTOMERS",
        query_id="query123"
    )

    query = Query(
        query_id="query123",
        query_text="INSERT INTO analytics.customer_summary SELECT * FROM raw.customers",
        start_time="2024-01-15T10:30:00Z"
    )

    lineage_edge = UpstreamLineageEdge(
        DOWNSTREAM_TABLE_NAME="ANALYTICS.CUSTOMER_SUMMARY",
        DOWNSTREAM_TABLE_DOMAIN="TABLE",
        UPSTREAM_TABLES=[upstream_table],
        QUERIES=[query]
    )

    print("Example 1: Pydantic Models")
    print(f"Upstream Table: {upstream_table}")
    print(f"Query: {query}")
    print(f"Lineage Edge downstream: {lineage_edge.DOWNSTREAM_TABLE_NAME}")
    print(f"Lineage Edge upstreams: {len(lineage_edge.UPSTREAM_TABLES or [])}")
    print()

    # Example 2: Snowflake Column ID
    column_id = SnowflakeColumnId(
        column_name="customer_id",
        object_name="raw.customers",
        object_domain="TABLE"
    )

    print("Example 2: Snowflake Column ID")
    print(f"Column ID: {column_id}")
    print(f"Column name: {column_id.column_name}")
    print(f"Object name: {column_id.object_name}")
    print()

    # Example 3: JSON parsing validation
    print("Example 3: JSON Parsing")
    json_data = {
        "DOWNSTREAM_TABLE_NAME": "ANALYTICS.SUMMARY",
        "DOWNSTREAM_TABLE_DOMAIN": "TABLE",
        "UPSTREAM_TABLES": '[{"upstream_object_domain": "TABLE", "upstream_object_name": "RAW.DATA", "query_id": "q1"}]',
        "QUERIES": '[{"query_id": "q1", "query_text": "SELECT * FROM raw.data", "start_time": "2024-01-15T10:00:00Z"}]'
    }

    try:
        parsed_edge = UpstreamLineageEdge.parse_obj(json_data)
        print(f"Successfully parsed lineage edge: {parsed_edge.DOWNSTREAM_TABLE_NAME}")
        print(f"Upstream tables: {len(parsed_edge.UPSTREAM_TABLES or [])}")
        print(f"Queries: {len(parsed_edge.QUERIES or [])}")
    except Exception as e:
        print(f"Error parsing lineage edge: {e}")
