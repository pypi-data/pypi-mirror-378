"""
DataGuild SQL parsing aggregator for processing and analyzing SQL queries.

This module provides comprehensive SQL query processing, lineage extraction,
usage statistics aggregation, and metadata generation from parsed SQL queries
across various data platforms with enhanced type safety and lineage tracking.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Set, Union, NewType

from dataguild.configuration.time_window_config import BaseTimeWindowConfig
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.graph.client import DataGuildGraph
from dataguild.source.usage.usage_common import BaseUsageConfig
from dataguild.metadata.com.linkedin.pegasus2avro.dataset import (
    DatasetUsageStatistics,
    DatasetFieldUsageCounts,
    DatasetUserUsageCounts,
)
from dataguild.metadata.com.linkedin.pegasus2avro.timeseries import TimeWindowSize
from dataguild.metadata.urns import CorpUserUrn, DatasetUrn
from dataguild.metadata.schema_classes import DatasetLineageClass, UpstreamClass, DatasetLineageTypeClass
from dataguild.metadata.com.linkedin.pegasus2avro.mxe import MetadataChangeProposal, ChangeType
from dataguild.sql_parsing.schema_resolver import SchemaResolver
from dataguild.sql_parsing.sql_parsing_common import QueryType
from dataguild.sql_parsing.sqlglot_lineage import ColumnLineageInfo
from dataguild.utilities.perf_timer import PerfTimer

logger = logging.getLogger(__name__)

# ✅ ADDED: Type alias for URN strings to provide type safety
UrnStr = NewType('UrnStr', str)


@dataclass
class KnownQueryLineageInfo:
    """
    ✅ CORRECTED: Represents known query lineage information matching DataHub structure exactly.
    
    This class stores pre-computed lineage information for SQL queries,
    including upstream/downstream relationships, column-level lineage,
    and query metadata for ingestion into DataGuild.
    """
    query_text: str
    downstream: UrnStr
    upstreams: List[UrnStr]
    column_lineage: Optional[List[ColumnLineageInfo]] = None
    column_usage: Optional[Dict[UrnStr, Set[UrnStr]]] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    query_type: QueryType = QueryType.UNKNOWN
    query_id: Optional[str] = None




# ✅ ADDED: Helper functions for URN operations
def create_urn_str(urn: str) -> UrnStr:
    """
    Create a UrnStr with validation.

    Args:
        urn: URN string to validate and wrap

    Returns:
        UrnStr instance

    Raises:
        ValueError: If URN format is invalid
    """
    if not isinstance(urn, str) or not urn.startswith("urn:li:"):
        raise ValueError(f"Invalid URN format: {urn}")
    return UrnStr(urn)


def validate_urn_str(urn: UrnStr) -> bool:
    """
    Validate a UrnStr format.

    Args:
        urn: UrnStr to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        return isinstance(urn, str) and urn.startswith("urn:li:")
    except Exception:
        return False


def extract_platform_from_urn(urn: UrnStr) -> Optional[str]:
    """
    Extract platform name from a dataset URN.

    Args:
        urn: Dataset URN

    Returns:
        Platform name if extractable, None otherwise
    """
    try:
        if "dataPlatform:" in urn:
            # Extract platform from urn:li:dataset:(urn:li:dataPlatform:platform,...)
            parts = urn.split("dataPlatform:")
            if len(parts) > 1:
                platform_part = parts[1].split(",")[0]
                return platform_part
    except Exception as e:
        logger.debug(f"Failed to extract platform from URN {urn}: {e}")
    return None


@dataclass
class KnownLineageMapping:
    """
    Represents a known lineage relationship between upstream and downstream datasets.

    This is typically used for copy operations, external transformations,
    or other cases where lineage is explicitly known without SQL parsing.
    """

    upstream: UrnStr  # ✅ ENHANCED: Now using UrnStr for type safety
    downstream: UrnStr  # ✅ ENHANCED: Now using UrnStr for type safety
    columns: Optional[List[str]] = None  # Column names involved
    confidence_score: float = 1.0  # Confidence in this lineage (0.0-1.0)
    operation_type: str = "COPY"  # Type of operation that created this lineage
    timestamp: Optional[datetime] = None  # When this lineage was observed
    extra_info: Optional[Dict[str, Any]] = None  # Additional metadata

    def __post_init__(self):
        """Validate the lineage mapping after initialization."""
        if self.confidence_score < 0.0 or self.confidence_score > 1.0:
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        if not self.upstream or not self.downstream:
            raise ValueError("upstream and downstream must be non-empty")

        # Validate URN format
        if not validate_urn_str(self.upstream):
            raise ValueError(f"Invalid upstream URN: {self.upstream}")
        if not validate_urn_str(self.downstream):
            raise ValueError(f"Invalid downstream URN: {self.downstream}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "upstream": self.upstream,
            "downstream": self.downstream,
            "columns": self.columns,
            "confidence_score": self.confidence_score,
            "operation_type": self.operation_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "extra_info": self.extra_info,
        }

    def to_known_query_lineage(self) -> KnownQueryLineageInfo:
        """Convert to KnownQueryLineageInfo for compatibility."""
        return KnownQueryLineageInfo(
            upstream_urn=self.upstream,
            downstream_urn=self.downstream,
            columns=self.columns,
            operation_type=self.operation_type,
            confidence_score=self.confidence_score,
            timestamp=self.timestamp,
            extra_info=self.extra_info
        )


@dataclass
class ObservedQuery:
    """
    Represents a SQL query that was observed but requires full SQL parsing.

    This is used for complex queries, temporary views, or cases where
    Snowflake's metadata doesn't provide sufficient lineage information.
    """

    query: str  # SQL query text
    session_id: str  # Database session identifier
    timestamp: datetime  # When the query was executed
    user: Union[str, CorpUserUrn]  # User who executed the query
    default_db: Optional[str] = None  # Default database context
    default_schema: Optional[str] = None  # Default schema context
    query_hash: Optional[str] = None  # Hash for deduplication
    query_type: Optional[QueryType] = None  # Parsed query type
    extra_info: Optional[Dict[str, Any]] = None  # Additional metadata

    def __post_init__(self):
        """Validate the observed query after initialization."""
        if not self.query or not self.query.strip():
            raise ValueError("query cannot be empty")
        if not self.session_id:
            raise ValueError("session_id cannot be empty")

    def get_user_urn(self) -> str:
        """Get user URN as string."""
        if isinstance(self.user, CorpUserUrn):
            return str(self.user)
        return self.user

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "query": self.query,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "user": self.get_user_urn(),
            "default_db": self.default_db,
            "default_schema": self.default_schema,
            "query_hash": self.query_hash,
            "query_type": self.query_type.value if self.query_type else None,
            "extra_info": self.extra_info,
        }


@dataclass
class PreparsedQuery:
    """
    Represents a SQL query that has already been parsed with extracted metadata.

    This is the primary data structure for queries where lineage, usage,
    and other metadata have been extracted from the source system.
    """

    query_id: str  # Unique identifier for the query
    query_text: str  # SQL query text
    upstreams: List[UrnStr]  # ✅ ENHANCED: List of upstream dataset URNs (type-safe)
    downstream: Optional[UrnStr] = None  # ✅ ENHANCED: Downstream dataset URN (type-safe)
    column_lineage: Optional[List[ColumnLineageInfo]] = None  # Column-level lineage
    column_usage: Optional[Dict[str, Set[str]]] = None  # Column usage by dataset
    inferred_schema: Optional[Dict[str, Any]] = None  # Inferred schema information
    confidence_score: float = 1.0  # Confidence in the parsed metadata
    query_count: int = 1  # Number of times this query was observed
    user: Union[str, CorpUserUrn] = ""  # User who executed the query
    timestamp: Optional[datetime] = None  # When the query was executed
    session_id: str = ""  # Database session identifier
    query_type: Optional[QueryType] = None  # Type of SQL query
    extra_info: Optional[Dict[str, Any]] = None  # Additional metadata

    def __post_init__(self):
        """Validate the preparsed query after initialization."""
        if not self.query_id:
            raise ValueError("query_id cannot be empty")
        if not self.query_text:
            raise ValueError("query_text cannot be empty")
        if self.confidence_score < 0.0 or self.confidence_score > 1.0:
            raise ValueError("confidence_score must be between 0.0 and 1.0")

        # Validate URNs
        for upstream in self.upstreams:
            if not validate_urn_str(upstream):
                raise ValueError(f"Invalid upstream URN: {upstream}")

        if self.downstream and not validate_urn_str(self.downstream):
            raise ValueError(f"Invalid downstream URN: {self.downstream}")

    def get_user_urn(self) -> str:
        """Get user URN as string."""
        if isinstance(self.user, CorpUserUrn):
            return str(self.user)
        return self.user

    def get_all_datasets(self) -> Set[UrnStr]:
        """Get all datasets (upstream and downstream) referenced in this query."""
        datasets = set(self.upstreams)
        if self.downstream:
            datasets.add(self.downstream)
        return datasets

    def to_known_query_lineages(self) -> List[KnownQueryLineageInfo]:
        """Convert to list of KnownQueryLineageInfo objects."""
        lineages = []

        if self.downstream:
            for upstream in self.upstreams:
                lineage = KnownQueryLineageInfo(
                    upstream_urn=upstream,
                    downstream_urn=self.downstream,
                    operation_type=self.query_type.value if self.query_type else "SELECT",
                    confidence_score=self.confidence_score,
                    timestamp=self.timestamp,
                    query_id=self.query_id,
                    session_id=self.session_id,
                    user_urn=self.get_user_urn()
                )
                lineages.append(lineage)

        return lineages

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "upstreams": list(self.upstreams),
            "downstream": self.downstream,
            "column_lineage": [cl.to_dict() for cl in (self.column_lineage or [])],
            "column_usage": {k: list(v) for k, v in (self.column_usage or {}).items()},
            "confidence_score": self.confidence_score,
            "query_count": self.query_count,
            "user": self.get_user_urn(),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "session_id": self.session_id,
            "query_type": self.query_type.value if self.query_type else None,
            "extra_info": self.extra_info,
        }


@dataclass
class TableRename:
    """
    Represents a table rename operation.

    This captures DDL operations that rename tables, which is important
    for maintaining accurate lineage when table names change.
    """

    original_urn: UrnStr  # ✅ ENHANCED: Original table URN (type-safe)
    new_urn: UrnStr  # ✅ ENHANCED: New table URN after rename (type-safe)
    query: str  # SQL query that performed the rename
    session_id: str  # Database session identifier
    timestamp: datetime  # When the rename occurred
    extra_info: Optional[Dict[str, Any]] = None  # Additional metadata

    def __post_init__(self):
        """Validate the table rename after initialization."""
        if not self.original_urn or not self.new_urn:
            raise ValueError("original_urn and new_urn cannot be empty")
        if self.original_urn == self.new_urn:
            raise ValueError("original_urn and new_urn cannot be the same")

        # Validate URN format
        if not validate_urn_str(self.original_urn):
            raise ValueError(f"Invalid original URN: {self.original_urn}")
        if not validate_urn_str(self.new_urn):
            raise ValueError(f"Invalid new URN: {self.new_urn}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "original_urn": self.original_urn,
            "new_urn": self.new_urn,
            "query": self.query,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "extra_info": self.extra_info,
        }


@dataclass
class TableSwap:
    """
    Represents a table swap operation.

    This captures DDL operations that swap two tables, which can affect
    lineage tracking and requires special handling.
    """

    urn_a: UrnStr  # ✅ ENHANCED: First table URN (type-safe)
    urn_b: UrnStr  # ✅ ENHANCED: Second table URN (type-safe)
    query: str  # SQL query that performed the swap
    session_id: str  # Database session identifier
    timestamp: datetime  # When the swap occurred
    extra_info: Optional[Dict[str, Any]] = None  # Additional metadata

    def __post_init__(self):
        """Validate the table swap after initialization."""
        if not self.urn_a or not self.urn_b:
            raise ValueError("urn_a and urn_b cannot be empty")
        if self.urn_a == self.urn_b:
            raise ValueError("urn_a and urn_b cannot be the same")

        # Validate URN format
        if not validate_urn_str(self.urn_a):
            raise ValueError(f"Invalid URN A: {self.urn_a}")
        if not validate_urn_str(self.urn_b):
            raise ValueError(f"Invalid URN B: {self.urn_b}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "urn_a": self.urn_a,
            "urn_b": self.urn_b,
            "query": self.query,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "extra_info": self.extra_info,
        }


@dataclass
class SqlAggregatorReport:
    """
    Comprehensive report for SQL aggregator processing with detailed metrics.
    """

    # Processing counters
    num_queries_processed: int = 0
    num_known_lineage_processed: int = 0
    num_table_renames_processed: int = 0
    num_table_swaps_processed: int = 0
    num_observed_queries_processed: int = 0

    # ✅ ADDED: Enhanced counters for new lineage types
    num_known_query_lineages_processed: int = 0
    num_high_confidence_lineages: int = 0
    num_low_confidence_lineages: int = 0

    # Error counters
    num_parsing_errors: int = 0
    num_lineage_errors: int = 0
    num_usage_errors: int = 0
    num_urn_validation_errors: int = 0  # ✅ ADDED: URN validation errors

    # Generated outputs
    num_lineage_edges_generated: int = 0
    num_usage_statistics_generated: int = 0
    num_query_statistics_generated: int = 0
    num_operations_generated: int = 0
    column_lineage_count: int = 0  # ✅ ADDED: Column lineage counter

    # Performance metrics
    total_processing_time: PerfTimer = field(default_factory=PerfTimer)
    lineage_processing_time: PerfTimer = field(default_factory=PerfTimer)
    usage_processing_time: PerfTimer = field(default_factory=PerfTimer)

    # Dataset tracking (✅ ENHANCED: Now using UrnStr sets)
    datasets_with_lineage: Set[UrnStr] = field(default_factory=set)
    datasets_with_usage: Set[UrnStr] = field(default_factory=set)
    unique_users: Set[str] = field(default_factory=set)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the aggregator processing."""
        return {
            "processing": {
                "total_queries": self.num_queries_processed,
                "known_lineage": self.num_known_lineage_processed,
                "known_query_lineages": self.num_known_query_lineages_processed,
                "table_renames": self.num_table_renames_processed,
                "table_swaps": self.num_table_swaps_processed,
                "observed_queries": self.num_observed_queries_processed,
            },
            "lineage_quality": {
                "high_confidence": self.num_high_confidence_lineages,
                "low_confidence": self.num_low_confidence_lineages,
                "confidence_ratio": (
                    self.num_high_confidence_lineages /
                    max(self.num_high_confidence_lineages + self.num_low_confidence_lineages, 1)
                ),
            },
            "errors": {
                "parsing_errors": self.num_parsing_errors,
                "lineage_errors": self.num_lineage_errors,
                "usage_errors": self.num_usage_errors,
                "urn_validation_errors": self.num_urn_validation_errors,
            },
            "generated": {
                "lineage_edges": self.num_lineage_edges_generated,
                "usage_statistics": self.num_usage_statistics_generated,
                "query_statistics": self.num_query_statistics_generated,
                "operations": self.num_operations_generated,
                "column_lineage": self.column_lineage_count,
            },
            "datasets": {
                "with_lineage": len(self.datasets_with_lineage),
                "with_usage": len(self.datasets_with_usage),
                "unique_users": len(self.unique_users),
            },
            "performance": {
                "total_time_seconds": self.total_processing_time.elapsed_seconds(),
                "lineage_time_seconds": self.lineage_processing_time.elapsed_seconds(),
                "usage_time_seconds": self.usage_processing_time.elapsed_seconds(),
            },
        }


class SqlParsingAggregator:
    """
    ✅ ENHANCED: Main aggregator class with support for KnownQueryLineageInfo and UrnStr types.

    This class handles the aggregation of various SQL query types, extraction
    of lineage information, generation of usage statistics, and creation of
    metadata work units for ingestion into DataGuild.
    """

    def __init__(
        self,
        platform: str,
        platform_instance: Optional[str] = None,
        env: Optional[str] = None,
        schema_resolver: Optional[SchemaResolver] = None,
        graph: Optional[DataGuildGraph] = None,
        eager_graph_load: bool = False,
        generate_lineage: bool = True,
        generate_queries: bool = True,
        generate_usage_statistics: bool = True,
        generate_query_usage_statistics: bool = True,
        usage_config: Optional[BaseUsageConfig] = None,
        generate_operations: bool = True,
        is_temp_table: Optional[callable] = None,
        is_allowed_table: Optional[callable] = None,
        format_queries: bool = True,
    ):
        """
        Initialize the SQL parsing aggregator.

        Args:
            platform: Data platform identifier (e.g., 'snowflake', 'bigquery')
            platform_instance: Optional platform instance identifier
            env: Environment identifier (e.g., 'prod', 'dev')
            schema_resolver: Optional schema resolver for enhanced parsing
            graph: Optional DataGuild graph for context
            eager_graph_load: Whether to eagerly load graph data
            generate_lineage: Whether to generate lineage metadata
            generate_queries: Whether to generate query metadata
            generate_usage_statistics: Whether to generate usage statistics
            generate_query_usage_statistics: Whether to generate query-level usage
            usage_config: Configuration for usage statistics
            generate_operations: Whether to generate operation metadata
            is_temp_table: Function to check if a table is temporary
            is_allowed_table: Function to check if a table is allowed
            format_queries: Whether to format SQL queries for display
        """
        self.platform = platform
        self.platform_instance = platform_instance
        self.env = env
        self.schema_resolver = schema_resolver
        self.graph = graph
        self.eager_graph_load = eager_graph_load

        # Feature flags
        self.generate_lineage = generate_lineage
        self.generate_queries = generate_queries
        self.generate_usage_statistics = generate_usage_statistics
        self.generate_query_usage_statistics = generate_query_usage_statistics
        self.generate_operations = generate_operations
        self.format_queries = format_queries

        # Configuration
        self.usage_config = usage_config or BaseUsageConfig()
        self.is_temp_table = is_temp_table or (lambda x: False)
        self.is_allowed_table = is_allowed_table or (lambda x: True)

        # Internal state
        self.report = SqlAggregatorReport()
        self._entries: List[Union[
            KnownLineageMapping,
            KnownQueryLineageInfo,  # ✅ ADDED: Support for new lineage type
            PreparsedQuery,
            ObservedQuery,
            TableRename,
            TableSwap
        ]] = []

        # ✅ ENHANCED: Aggregated data structures with UrnStr support
        self._lineage_map: Dict[UrnStr, Set[UrnStr]] = defaultdict(set)  # downstream -> upstreams
        self._usage_data: Dict[UrnStr, Dict[str, Any]] = defaultdict(dict)  # dataset -> usage info
        self._query_lineages: List[KnownQueryLineageInfo] = []  # ✅ ADDED: Store query lineages

        logger.info(f"Initialized SqlParsingAggregator for platform: {platform}")

    def add(
        self,
        entry: Union[
            KnownLineageMapping,
            KnownQueryLineageInfo,  # ✅ ADDED: Support new lineage type
            PreparsedQuery,
            ObservedQuery,
            TableRename,
            TableSwap
        ]
    ) -> None:
        """
        ✅ ENHANCED: Add an entry to the aggregator for processing.

        Args:
            entry: SQL parsing entry to process (now supports KnownQueryLineageInfo)
        """
        try:
            with self.report.total_processing_time:
                self._entries.append(entry)
                self._process_entry(entry)
                self.report.num_queries_processed += 1

        except ValueError as e:
            self.report.num_urn_validation_errors += 1
            logger.error(f"URN validation error: {e}")
        except Exception as e:
            self.report.num_parsing_errors += 1
            logger.error(f"Error processing entry: {e}", exc_info=True)

    def _process_entry(
        self,
        entry: Union[
            KnownLineageMapping,
            KnownQueryLineageInfo,  # ✅ ADDED: Support new lineage type
            PreparsedQuery,
            ObservedQuery,
            TableRename,
            TableSwap
        ]
    ) -> None:
        """✅ ENHANCED: Process different types of entries including KnownQueryLineageInfo."""
        if isinstance(entry, KnownLineageMapping):
            self._process_known_lineage(entry)
        elif isinstance(entry, KnownQueryLineageInfo):  # ✅ ADDED: New processing branch
            self._process_known_query_lineage(entry)
        elif isinstance(entry, PreparsedQuery):
            self._process_preparsed_query(entry)
        elif isinstance(entry, ObservedQuery):
            self._process_observed_query(entry)
        elif isinstance(entry, TableRename):
            self._process_table_rename(entry)
        elif isinstance(entry, TableSwap):
            self._process_table_swap(entry)
        else:
            logger.warning(f"Unknown entry type: {type(entry)}")

    def _process_known_query_lineage(self, entry: KnownQueryLineageInfo) -> None:
        """
        ✅ CORRECTED: Process known query lineage information matching DataHub implementation.

        Args:
            entry: KnownQueryLineageInfo to process
        """
        try:
            with self.report.lineage_processing_time:
                # Store the query lineage
                self._query_lineages.append(entry)

                # Update lineage map (downstream -> upstreams)
                if self.generate_lineage:
                    for upstream in entry.upstreams:
                        self._lineage_map[entry.downstream].add(upstream)
                        self.report.datasets_with_lineage.add(upstream)
                    self.report.datasets_with_lineage.add(entry.downstream)
                    self.report.num_lineage_edges_generated += len(entry.upstreams)

                # Process column lineage if available
                if entry.column_lineage:
                    for col_lineage in entry.column_lineage:
                        self.report.column_lineage_count += 1

                # Process column usage if available
                if entry.column_usage:
                    for dataset, columns in entry.column_usage.items():
                        if dataset not in self._usage_data:
                            self._usage_data[dataset] = {}
                        self._usage_data[dataset]['columns'] = columns

                self.report.num_known_query_lineages_processed += 1
                logger.debug(f"Processed query lineage: {entry.query_id}")

        except Exception as e:
            self.report.num_lineage_errors += 1
            logger.error(f"Error processing known query lineage: {e}")

    def add_known_query_lineage(
        self, known_query_lineage: KnownQueryLineageInfo, merge_lineage: bool = False
    ) -> None:
        """Add a query and it's precomputed lineage to the aggregator.

        This is useful for cases where we have lineage information that was
        computed outside of the SQL parsing aggregator, e.g. from a data
        warehouse's system tables.

        Args:
            known_query_lineage: The known query lineage information.
            merge_lineage: Whether to merge the lineage with any existing lineage
                for the query ID.
        """
        self.report.num_known_query_lineage += 1
        
        # Add to entries for processing
        self.add(known_query_lineage)

    def _process_known_lineage(self, entry: KnownLineageMapping) -> None:
        """Process known lineage mapping."""
        try:
            logger.info(f"Processing known lineage: {entry.upstream} -> {entry.downstream}")
            with self.report.lineage_processing_time:
                if self.generate_lineage:
                    self._lineage_map[entry.downstream].add(entry.upstream)
                    self.report.datasets_with_lineage.add(entry.downstream)
                    self.report.datasets_with_lineage.add(entry.upstream)
                    self.report.num_lineage_edges_generated += 1
                    logger.info(f"Added lineage mapping: {entry.upstream} -> {entry.downstream}")

                self.report.num_known_lineage_processed += 1

        except Exception as e:
            self.report.num_lineage_errors += 1
            logger.error(f"Error processing known lineage: {e}")

    def _process_preparsed_query(self, entry: PreparsedQuery) -> None:
        """✅ ENHANCED: Process preparsed query with UrnStr support."""
        try:
            logger.info(f"Processing PreparsedQuery: {entry.query_id} with {len(entry.upstreams)} upstreams")
            logger.info(f"Downstream: {entry.downstream}")
            logger.info(f"Upstreams: {entry.upstreams}")
            
            # Process lineage
            if self.generate_lineage and entry.downstream:
                with self.report.lineage_processing_time:
                    for upstream in entry.upstreams:
                        self._lineage_map[entry.downstream].add(upstream)
                        self.report.num_lineage_edges_generated += 1
                        logger.info(f"Added lineage: {upstream} -> {entry.downstream}")

                    self.report.datasets_with_lineage.add(entry.downstream)
                    self.report.datasets_with_lineage.update(entry.upstreams)

            # Convert to KnownQueryLineageInfo objects for consistent processing
            known_lineages = entry.to_known_query_lineages()
            for lineage in known_lineages:
                self._query_lineages.append(lineage)

            # Process usage statistics
            if self.generate_usage_statistics:
                with self.report.usage_processing_time:
                    self._process_usage_from_query(entry)

            # Track user
            user_urn = entry.get_user_urn()
            if user_urn:
                self.report.unique_users.add(user_urn)

        except Exception as e:
            self.report.num_usage_errors += 1
            logger.error(f"Error processing preparsed query: {e}")

    def _process_observed_query(self, entry: ObservedQuery) -> None:
        """Process observed query that requires SQL parsing."""
        try:
            # TODO: Implement full SQL parsing for observed queries
            # This would use the schema resolver and SQL parsing utilities
            # to extract lineage and usage information

            self.report.num_observed_queries_processed += 1

            # Track user
            user_urn = entry.get_user_urn()
            if user_urn:
                self.report.unique_users.add(user_urn)

        except Exception as e:
            self.report.num_parsing_errors += 1
            logger.error(f"Error processing observed query: {e}")

    def _process_table_rename(self, entry: TableRename) -> None:
        """✅ ENHANCED: Process table rename operation with UrnStr support."""
        try:
            # Update lineage mappings to reflect the rename
            if entry.original_urn in self._lineage_map:
                # Move lineage from old URN to new URN
                upstreams = self._lineage_map.pop(entry.original_urn)
                self._lineage_map[entry.new_urn].update(upstreams)

            # Update any downstream references
            for downstream, upstreams in self._lineage_map.items():
                if entry.original_urn in upstreams:
                    upstreams.remove(entry.original_urn)
                    upstreams.add(entry.new_urn)

            # Update query lineages
            for lineage in self._query_lineages:
                if lineage.upstream_urn == entry.original_urn:
                    lineage.upstream_urn = entry.new_urn
                if lineage.downstream_urn == entry.original_urn:
                    lineage.downstream_urn = entry.new_urn

            self.report.num_table_renames_processed += 1

        except Exception as e:
            self.report.num_lineage_errors += 1
            logger.error(f"Error processing table rename: {e}")

    def _process_table_swap(self, entry: TableSwap) -> None:
        """✅ ENHANCED: Process table swap operation with UrnStr support."""
        try:
            # Swap lineage mappings
            lineage_a = self._lineage_map.get(entry.urn_a, set())
            lineage_b = self._lineage_map.get(entry.urn_b, set())

            self._lineage_map[entry.urn_a] = lineage_b
            self._lineage_map[entry.urn_b] = lineage_a

            # Update query lineages
            for lineage in self._query_lineages:
                if lineage.upstream_urn == entry.urn_a:
                    lineage.upstream_urn = entry.urn_b
                elif lineage.upstream_urn == entry.urn_b:
                    lineage.upstream_urn = entry.urn_a

                if lineage.downstream_urn == entry.urn_a:
                    lineage.downstream_urn = entry.urn_b
                elif lineage.downstream_urn == entry.urn_b:
                    lineage.downstream_urn = entry.urn_a

            self.report.num_table_swaps_processed += 1

        except Exception as e:
            self.report.num_lineage_errors += 1
            logger.error(f"Error processing table swap: {e}")

    def _process_usage_from_query(self, entry: PreparsedQuery) -> None:
        """✅ ENHANCED: Extract usage statistics with UrnStr support."""
        if not entry.timestamp:
            return

        # Process each upstream dataset for usage
        for dataset_urn in entry.upstreams:
            if not self.is_allowed_table(str(dataset_urn)):
                continue

            usage_info = self._usage_data[dataset_urn]

            # Initialize usage structure if needed
            if 'queries' not in usage_info:
                usage_info['queries'] = []
                usage_info['users'] = set()
                usage_info['column_usage'] = defaultdict(int)
                usage_info['timestamps'] = []

            # Add query information
            usage_info['queries'].append({
                'query_id': entry.query_id,
                'query_text': entry.query_text,
                'timestamp': entry.timestamp,
                'user': entry.get_user_urn(),
                'query_count': entry.query_count,
            })

            # Track user
            if entry.get_user_urn():
                usage_info['users'].add(entry.get_user_urn())

            # Track column usage
            if entry.column_usage and str(dataset_urn) in entry.column_usage:
                for column in entry.column_usage[str(dataset_urn)]:
                    usage_info['column_usage'][column] += entry.query_count

            # Track timestamp
            usage_info['timestamps'].append(entry.timestamp)

            self.report.datasets_with_usage.add(dataset_urn)

    def get_query_lineages(
        self,
        high_confidence_only: bool = False,
        recent_only: bool = False,
        hours_threshold: float = 24.0
    ) -> List[KnownQueryLineageInfo]:
        """
        ✅ ADDED: Get all query lineages with optional filtering.

        Args:
            high_confidence_only: Only return high confidence lineages
            recent_only: Only return recent lineages
            hours_threshold: Hours threshold for recent filter

        Returns:
            List of filtered KnownQueryLineageInfo objects
        """
        lineages = self._query_lineages.copy()

        if high_confidence_only:
            lineages = [l for l in lineages if l.is_high_confidence()]

        if recent_only:
            lineages = [l for l in lineages if l.is_recent(hours_threshold)]

        return lineages

    def get_lineage_summary(self) -> Dict[str, Any]:
        """
        ✅ ADDED: Get comprehensive lineage summary statistics.

        Returns:
            Dictionary with lineage statistics and quality metrics
        """
        total_lineages = len(self._query_lineages)
        high_confidence = len([l for l in self._query_lineages if l.is_high_confidence()])
        recent = len([l for l in self._query_lineages if l.is_recent()])

        # Operation type breakdown
        operation_counts = defaultdict(int)
        for lineage in self._query_lineages:
            operation_counts[lineage.operation_type] += 1

        # Platform breakdown
        platform_counts = defaultdict(int)
        for lineage in self._query_lineages:
            platform = extract_platform_from_urn(lineage.upstream_urn)
            if platform:
                platform_counts[platform] += 1

        return {
            "total_lineages": total_lineages,
            "high_confidence_count": high_confidence,
            "recent_count": recent,
            "confidence_percentage": (high_confidence / max(total_lineages, 1)) * 100,
            "recent_percentage": (recent / max(total_lineages, 1)) * 100,
            "operation_types": dict(operation_counts),
            "platforms": dict(platform_counts),
            "unique_upstream_urns": len(set(l.upstream_urn for l in self._query_lineages)),
            "unique_downstream_urns": len(set(l.downstream_urn for l in self._query_lineages)),
        }

    def gen_metadata(self) -> Iterable[MetadataWorkUnit]:
        """
        ✅ ENHANCED: Generate metadata work units from aggregated data.

        Returns:
            Iterator of MetadataWorkUnit instances
        """
        logger.info("Generating metadata work units from SQL aggregator")

        # ✅ CRITICAL FIX: Add comprehensive error handling to identify NoneType issues
        try:
            # Generate lineage metadata
            if self.generate_lineage:
                logger.debug("Generating lineage metadata")
                lineage_metadata = self._generate_lineage_metadata()
                if lineage_metadata is not None:
                    yield from lineage_metadata
                else:
                    logger.warning("Lineage metadata generation returned None")

            # Generate usage statistics
            if self.generate_usage_statistics:
                logger.debug("Generating usage metadata")
                usage_metadata = self._generate_usage_metadata()
                if usage_metadata is not None:
                    yield from usage_metadata
                else:
                    logger.warning("Usage metadata generation returned None")

            # Generate query metadata
            if self.generate_queries:
                logger.debug("Generating query metadata")
                query_metadata = self._generate_query_metadata()
                if query_metadata is not None:
                    yield from query_metadata
                else:
                    logger.warning("Query metadata generation returned None")

            # Generate operation metadata
            if self.generate_operations:
                logger.debug("Generating operation metadata")
                operation_metadata = self._generate_operation_metadata()
                if operation_metadata is not None:
                    yield from operation_metadata
                else:
                    logger.warning("Operation metadata generation returned None")

            logger.info(f"Generated metadata from {len(self._entries)} SQL entries")

        except Exception as e:
            logger.error(f"Error in gen_metadata: {e}")
            # Return empty iterator instead of failing
            return []

    def _generate_lineage_metadata(self) -> Iterable[MetadataWorkUnit]:
        """Generate lineage metadata work units."""
        logger.info(f"Generating lineage metadata from {len(self._lineage_map)} lineage relationships")
        logger.info(f"Lineage map contents: {dict(self._lineage_map)}")
        
        for downstream, upstreams in self._lineage_map.items():
            if upstreams is not None and upstreams:
                logger.info(f"Generating lineage: {list(upstreams)} -> {downstream}")
                
                # Create DatasetLineageClass with upstream relationships
                lineage = DatasetLineageClass()
                
                for upstream_urn in upstreams:
                    # Determine lineage type based on the URN
                    lineage_type = self._determine_lineage_type(upstream_urn)
                    
                    # Add upstream relationship
                    lineage.add_upstream(
                        urn=str(upstream_urn),
                        lineage_type=lineage_type,
                        confidence_score=1.0,
                        source_system="sql_parsing_aggregator",
                        properties={
                            "extraction_method": "sql_parsing",
                            "platform": self.platform
                        }
                    )
                
                # Create MetadataChangeProposal for lineage
                mcp = MetadataChangeProposal(
                    entity_urn=str(downstream),
                    aspect_name="upstreamLineage",
                    aspect=lineage,
                    change_type=ChangeType.UPSERT
                )
                
                # Create mcp_raw structure for proper serialization
                mcp_raw = {
                    "entityUrn": str(downstream),
                    "aspectName": "upstreamLineage",
                    "aspect": {
                        "upstreams": [
                            {
                                "urn": str(upstream_urn),
                                "type": str(lineage_type),
                                "confidence_score": 1.0,
                                "source_system": "sql_parsing_aggregator"
                            }
                            for upstream_urn, lineage_type in zip(upstreams, [
                                self._determine_lineage_type(up) for up in upstreams
                            ])
                        ],
                        "fineGrainedLineages": self._extract_column_lineage_for_dataset(downstream)
                    }
                }
                
                # Create MetadataWorkUnit with both mcp and mcp_raw
                workunit = MetadataWorkUnit(
                    id=f"lineage_{downstream}_{len(upstreams)}",
                    mcp=mcp,
                    mcp_raw=mcp_raw,
                    priority=1
                )
                
                logger.info(f"Generated lineage workunit for {downstream} with {len(upstreams)} upstreams")
                yield workunit
                
            else:
                logger.debug(f"No upstreams for {downstream}")

        self.report.num_lineage_edges_generated = len(self._lineage_map)
    
    def _determine_lineage_type(self, urn: str) -> DatasetLineageTypeClass:
        """Determine the lineage type based on the URN."""
        urn_lower = urn.lower()
        
        if "view" in urn_lower or "stg_" in urn_lower:
            return DatasetLineageTypeClass.VIEW
        elif "table" in urn_lower or "raw_" in urn_lower:
            return DatasetLineageTypeClass.TABLE
        elif "external" in urn_lower:
            return DatasetLineageTypeClass.EXTERNAL_TABLE
        elif "materialized" in urn_lower:
            return DatasetLineageTypeClass.MATERIALIZED_VIEW
        else:
            return DatasetLineageTypeClass.UNKNOWN

    def _extract_column_lineage_for_dataset(self, dataset_urn: str) -> List[Dict[str, Any]]:
        """Extract column-level lineage for a specific dataset."""
        column_lineages = []
        
        logger.debug(f"Extracting column lineage for dataset: {dataset_urn}")
        logger.debug(f"Total entries to check: {len(self._entries)}")
        
        # Look for column lineage in the entries (KnownQueryLineageInfo objects)
        for i, entry in enumerate(self._entries):
            if hasattr(entry, 'downstream'):
                logger.debug(f"Entry {i}: downstream={entry.downstream}, has_column_lineage={hasattr(entry, 'column_lineage')}")
                if hasattr(entry, 'column_lineage') and entry.column_lineage:
                    logger.debug(f"Entry {i}: column_lineage count={len(entry.column_lineage)}")
            
            if (hasattr(entry, 'downstream') and 
                str(entry.downstream) == str(dataset_urn) and 
                hasattr(entry, 'column_lineage') and 
                entry.column_lineage):
                
                logger.debug(f"Found column lineage for {dataset_urn}: {len(entry.column_lineage)} entries")
                
                for col_lineage in entry.column_lineage:
                    column_lineages.append({
                        "downstream": {
                            "table": str(dataset_urn),
                            "column": col_lineage.downstream.column
                        },
                        "upstreams": [
                            {
                                "table": str(up.table),
                                "column": up.column
                            }
                            for up in col_lineage.upstreams
                        ],
                        "confidence_score": getattr(col_lineage, 'confidence_score', 1.0),
                        "transformation_type": getattr(col_lineage, 'transformation_type', None),
                        "sql_expression": getattr(col_lineage, 'sql_expression', None)
                    })
        
        logger.debug(f"Extracted {len(column_lineages)} column lineage entries for {dataset_urn}")
        
        # Update counter
        self.report.column_lineage_count += len(column_lineages)
        
        return column_lineages

    def _generate_usage_metadata(self) -> Iterable[MetadataWorkUnit]:
        """Generate usage statistics metadata work units."""
        if not self.usage_config:
            return []

        for dataset_urn, usage_info in self._usage_data.items():
            try:
                # Create usage statistics
                usage_stats = self._create_usage_statistics(str(dataset_urn), usage_info)
                if usage_stats:
                    # TODO: Create actual MetadataWorkUnit with usage statistics
                    # This would wrap the usage_stats in a proper work unit
                    logger.debug(f"Generated usage statistics for {dataset_urn}")
                    self.report.num_usage_statistics_generated += 1

            except Exception as e:
                self.report.num_usage_errors += 1
                logger.error(f"Error generating usage statistics for {dataset_urn}: {e}")

    def _generate_query_metadata(self) -> Iterable[MetadataWorkUnit]:
        """Generate query metadata work units."""
        # TODO: Generate query metadata work units
        # This would include top queries, query patterns, etc.
        return []

    def _generate_operation_metadata(self) -> Iterable[MetadataWorkUnit]:
        """Generate operation metadata work units."""
        # TODO: Generate operation metadata work units
        # This would include DDL operations, data modifications, etc.
        return []

    def _create_usage_statistics(
        self,
        dataset_urn: str,
        usage_info: Dict[str, Any]
    ) -> Optional[DatasetUsageStatistics]:
        """Create usage statistics for a dataset."""
        if not usage_info.get('timestamps'):
            return None

        # Calculate time window
        timestamps = usage_info['timestamps']
        min_time = min(timestamps)
        bucket_start = self._get_bucket_start(min_time)

        # Create usage statistics
        return DatasetUsageStatistics(
            timestampMillis=int(bucket_start.timestamp() * 1000),
            eventGranularity=TimeWindowSize(
                unit=self.usage_config.bucket_duration,
                multiple=1
            ),
            totalSqlQueries=len(usage_info.get('queries', [])),
            uniqueUserCount=len(usage_info.get('users', set())),
            userCounts=self._create_user_counts(usage_info.get('users', set())),
            fieldCounts=self._create_field_counts(usage_info.get('column_usage', {})),
            topSqlQueries=self._get_top_queries(usage_info.get('queries', [])),
        )

    def _get_bucket_start(self, timestamp: datetime) -> datetime:
        """Get the bucket start time for a timestamp."""
        # TODO: Implement proper bucketing based on usage_config
        return timestamp.replace(minute=0, second=0, microsecond=0)

    def _create_user_counts(self, users: Set[str]) -> List[DatasetUserUsageCounts]:
        """Create user usage counts."""
        return [
            DatasetUserUsageCounts(
                user=user,
                count=1,  # TODO: Calculate actual usage count per user
                userEmail=None,  # TODO: Extract email if available
            )
            for user in users
        ]

    def _create_field_counts(self, column_usage: Dict[str, int]) -> List[DatasetFieldUsageCounts]:
        """Create field usage counts."""
        return [
            DatasetFieldUsageCounts(
                fieldPath=column,
                count=count,
            )
            for column, count in column_usage.items()
        ]

    def _get_top_queries(self, queries: List[Dict[str, Any]]) -> List[str]:
        """Get top queries by frequency."""
        # TODO: Implement proper query ranking and formatting
        return [q['query_text'] for q in queries[:10]]  # Top 10 queries

    def close(self) -> None:
        """Close the aggregator and clean up resources."""
        summary = self.report.get_summary()
        lineage_summary = self.get_lineage_summary()

        logger.info(f"Closing SqlParsingAggregator.")
        logger.info(f"Processing Report: {summary}")
        logger.info(f"Lineage Summary: {lineage_summary}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Export all classes and functions
__all__ = [
    # ✅ ADDED: New classes and types
    'UrnStr',
    'KnownQueryLineageInfo',

    # Enhanced existing classes
    'KnownLineageMapping',
    'ObservedQuery',
    'PreparsedQuery',
    'TableRename',
    'TableSwap',
    'SqlAggregatorReport',
    'SqlParsingAggregator',

    # ✅ ADDED: Utility functions
    'create_urn_str',
    'validate_urn_str',
    'extract_platform_from_urn',
]
