"""
DataGuild Snowflake stored procedure lineage tracking.

This module provides comprehensive tracking and lineage extraction for
Snowflake stored procedures, aggregating queries executed within procedures
to build table-level lineage relationships for DataGuild ingestion pipelines.
"""

import dataclasses
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, List, Optional

from dataguild.api.closeable import Closeable
from dataguild.metadata.urns import CorpUserUrn
from dataguild.sql_parsing.sql_parsing_aggregator import (
    PreparsedQuery,
    UrnStr,
)
from dataguild.sql_parsing.sqlglot_utils import get_query_fingerprint
from dataguild.utilities.file_backed_collections import FileBackedDict

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class StoredProcCall:
    """
    Represents a stored procedure call in Snowflake.

    Snowflake assigns each stored procedure call a unique query_id which becomes
    the root_query_id for all subsequent queries executed within that procedure.
    This enables comprehensive lineage tracking across procedure executions.

    Examples:
        >>> call = StoredProcCall(
        ...     snowflake_root_query_id="01b2c3d4-e5f6-7890-abcd-ef1234567890",
        ...     query_text="CALL SALES_FORECASTING.CUSTOMER_ANALYSIS_PROC();",
        ...     timestamp=datetime.now(),
        ...     user=CorpUserUrn("analyst@company.com"),
        ...     default_db="SALES_DB",
        ...     default_schema="ANALYTICS"
        ... )
    """

    snowflake_root_query_id: str  # Unique identifier for the procedure call
    # Query text will typically be something like:
    # "CALL SALES_FORECASTING.CUSTOMER_ANALYSIS_PROC();"
    query_text: str  # SQL text of the CALL statement
    timestamp: datetime  # When the procedure was called
    user: CorpUserUrn  # User who executed the procedure
    default_db: str  # Default database context
    default_schema: str  # Default schema context

    def __post_init__(self):
        """Validate stored procedure call after initialization."""
        if not self.snowflake_root_query_id:
            raise ValueError("snowflake_root_query_id cannot be empty")
        if not self.query_text:
            raise ValueError("query_text cannot be empty")
        if not isinstance(self.user, CorpUserUrn):
            raise ValueError("user must be a CorpUserUrn instance")

    def get_procedure_name(self) -> Optional[str]:
        """
        Extract procedure name from the CALL statement.

        Returns:
            Procedure name if extractable, None otherwise
        """
        try:
            import re
            # Extract from "CALL schema.procedure_name()" format
            match = re.search(r'CALL\s+([^\s\(]+)', self.query_text, re.IGNORECASE)
            if match:
                return match.group(1)
        except Exception as e:
            logger.debug(f"Failed to extract procedure name from {self.query_text}: {e}")
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "snowflake_root_query_id": self.snowflake_root_query_id,
            "query_text": self.query_text,
            "timestamp": self.timestamp.isoformat(),
            "user": str(self.user),
            "default_db": self.default_db,
            "default_schema": self.default_schema,
            "procedure_name": self.get_procedure_name(),
        }


@dataclass
class StoredProcExecutionLineage:
    """
    Represents the aggregated lineage for a stored procedure execution.

    This class accumulates all input and output datasets from queries
    executed within a single stored procedure call, providing comprehensive
    lineage tracking for procedure-level transformations.
    """

    call: StoredProcCall  # The original procedure call
    inputs: List[UrnStr]  # All input datasets accessed by the procedure
    outputs: List[UrnStr]  # All output datasets modified by the procedure

    def __post_init__(self):
        """Initialize collections if needed."""
        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []

    def add_input(self, input_urn: UrnStr) -> None:
        """Add an input dataset URN if not already present."""
        if input_urn not in self.inputs:
            self.inputs.append(input_urn)

    def add_output(self, output_urn: UrnStr) -> None:
        """Add an output dataset URN if not already present."""
        if output_urn not in self.outputs:
            self.outputs.append(output_urn)

    def get_unique_inputs(self) -> List[UrnStr]:
        """Get deduplicated list of input URNs."""
        return list(dict.fromkeys(self.inputs))

    def get_unique_outputs(self) -> List[UrnStr]:
        """Get deduplicated list of output URNs."""
        return list(dict.fromkeys(self.outputs))

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "call": self.call.to_dict(),
            "inputs": self.get_unique_inputs(),
            "outputs": self.get_unique_outputs(),
            "input_count": len(self.get_unique_inputs()),
            "output_count": len(self.get_unique_outputs()),
        }


@dataclass
class StoredProcLineageReport:
    """
    Comprehensive report for stored procedure lineage tracking with detailed metrics.
    """

    # Core tracking metrics
    num_stored_proc_calls: int = 0  # Total procedure calls tracked
    num_related_queries: int = 0  # Queries associated with procedures
    num_related_queries_without_proc_call: int = 0  # Orphaned queries

    # Lineage generation metrics - incremented at generation/build time
    num_stored_proc_lineage_entries: int = 0  # Generated lineage entries
    num_stored_proc_calls_with_no_inputs: int = 0  # Procedures with no inputs
    num_stored_proc_calls_with_no_outputs: int = 0  # Procedures with no outputs

    # Additional quality metrics
    num_procedures_with_lineage: int = 0  # Procedures that generated lineage
    num_unique_procedures: int = 0  # Unique procedure names tracked

    def get_summary(self) -> dict:
        """Get a comprehensive summary of stored procedure tracking."""
        total_calls = self.num_stored_proc_calls
        calls_with_lineage = total_calls - self.num_stored_proc_calls_with_no_inputs

        return {
            "stored_procedures": {
                "total_calls": total_calls,
                "calls_with_inputs": total_calls - self.num_stored_proc_calls_with_no_inputs,
                "calls_with_outputs": total_calls - self.num_stored_proc_calls_with_no_outputs,
                "calls_generating_lineage": calls_with_lineage,
                "unique_procedures": self.num_unique_procedures,
            },
            "queries": {
                "related_queries": self.num_related_queries,
                "orphaned_queries": self.num_related_queries_without_proc_call,
            },
            "lineage": {
                "entries_generated": self.num_stored_proc_lineage_entries,
                "procedures_with_lineage": self.num_procedures_with_lineage,
            },
            "quality_metrics": {
                "lineage_coverage": calls_with_lineage / total_calls if total_calls > 0 else 0.0,
                "query_association_rate": (
                    self.num_related_queries /
                    (self.num_related_queries + self.num_related_queries_without_proc_call)
                    if (self.num_related_queries + self.num_related_queries_without_proc_call) > 0 else 0.0
                ),
            }
        }


class StoredProcLineageTracker(Closeable):
    """
    Tracks table-level lineage for Snowflake stored procedures.

    Stored procedures in Snowflake trigger multiple SQL queries during execution.
    Snowflake assigns each stored procedure call a unique query_id and uses this as the
    root_query_id for all subsequent queries executed within that procedure. This allows
    us to trace which queries belong to a specific stored procedure execution and build
    table-level lineage by aggregating inputs/outputs from all related queries.

    The tracker maintains a mapping of root_query_id to StoredProcExecutionLineage,
    accumulating lineage information as related queries are processed through the
    DataGuild ingestion pipeline.

    Examples:
        >>> with StoredProcLineageTracker(platform="snowflake") as tracker:
        ...     # Add procedure calls
        ...     tracker.add_stored_proc_call(call)
        ...
        ...     # Process related queries
        ...     for query in queries:
        ...         tracker.add_related_query(query)
        ...
        ...     # Generate lineage entries
        ...     for lineage in tracker.build_merged_lineage_entries():
        ...         yield lineage
    """

    def __init__(self, platform: str, shared_connection: Optional[Any] = None):
        """
        Initialize the stored procedure lineage tracker.

        Args:
            platform: Data platform identifier (e.g., 'snowflake')
            shared_connection: Optional shared database connection for file-backed storage
        """
        self.platform = platform
        self.report = StoredProcLineageReport()

        # Use file-backed storage for scalability with large datasets
        # { root_query_id -> StoredProcExecutionLineage }
        self._stored_proc_execution_lineage: FileBackedDict[StoredProcExecutionLineage] = (
            FileBackedDict(memory_threshold=1000, compress_values=True)
        )

        # Track unique procedure names for analytics
        self._procedure_names: set = set()

        logger.info(f"Initialized StoredProcLineageTracker for platform: {platform}")

    def add_stored_proc_call(self, call: StoredProcCall) -> None:
        """
        Add a stored procedure call to track.

        This creates an initial lineage record that will be populated
        as related queries are processed.

        Args:
            call: StoredProcCall instance representing the procedure execution
        """
        try:
            self._stored_proc_execution_lineage[call.snowflake_root_query_id] = (
                StoredProcExecutionLineage(
                    call=call,
                    # Will be populated by subsequent queries
                    inputs=[],
                    outputs=[],
                )
            )

            self.report.num_stored_proc_calls += 1

            # Track unique procedure names
            procedure_name = call.get_procedure_name()
            if procedure_name:
                self._procedure_names.add(procedure_name)
                self.report.num_unique_procedures = len(self._procedure_names)

            logger.debug(f"Added stored procedure call: {call.snowflake_root_query_id}")

        except Exception as e:
            logger.error(f"Failed to add stored procedure call: {e}")
            raise

    def add_related_query(self, query: PreparsedQuery) -> bool:
        """
        Add a query that might be related to a stored procedure execution.

        This method associates queries with stored procedures based on the
        snowflake_root_query_id, accumulating inputs and outputs for lineage.

        Args:
            query: PreparsedQuery that may belong to a stored procedure

        Returns:
            True if the query was added to a stored procedure execution, False otherwise
        """
        try:
            # Extract the root query ID from the query's extra info
            snowflake_root_query_id = (query.extra_info or {}).get(
                "snowflake_root_query_id"
            )

            if not snowflake_root_query_id:
                return False

            # Check if we have a stored procedure for this root query ID
            if snowflake_root_query_id not in self._stored_proc_execution_lineage:
                self.report.num_related_queries_without_proc_call += 1
                logger.debug(
                    f"Query {query.query_id} has root_query_id {snowflake_root_query_id} "
                    f"but no matching procedure call"
                )
                return False

            # Get the execution lineage for mutation (file-backed dict requirement)
            stored_proc_execution = self._stored_proc_execution_lineage.for_mutation(
                snowflake_root_query_id
            )

            # Add upstream datasets as inputs to the procedure
            stored_proc_execution.inputs.extend(query.upstreams)

            # Add downstream dataset as output from the procedure
            if query.downstream is not None:
                stored_proc_execution.outputs.append(query.downstream)

            self.report.num_related_queries += 1

            logger.debug(
                f"Associated query {query.query_id} with procedure {snowflake_root_query_id}. "
                f"Added {len(query.upstreams)} upstreams, "
                f"downstream: {query.downstream is not None}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to add related query {getattr(query, 'query_id', 'unknown')}: {e}")
            return False

    def build_merged_lineage_entries(self) -> Iterable[PreparsedQuery]:
        """
        Build merged lineage entries from stored procedure executions.

        For stored procedures, we can only get table-level lineage from the audit log.
        We represent these as PreparsedQuery objects for now. Eventually we'll want to
        create dataJobInputOutput lineage instead for more precise representation.

        This method processes all tracked procedures and generates lineage entries
        that represent the overall data transformation performed by each procedure.

        Yields:
            PreparsedQuery objects representing procedure-level lineage transformations
        """
        logger.info("Building merged lineage entries for stored procedures")

        for stored_proc_execution in self._stored_proc_execution_lineage.values():
            try:
                # Skip procedures with no inputs (can't generate meaningful lineage)
                if not stored_proc_execution.inputs:
                    self.report.num_stored_proc_calls_with_no_inputs += 1
                    logger.debug(
                        f"Procedure {stored_proc_execution.call.snowflake_root_query_id} "
                        f"has no inputs, skipping lineage generation"
                    )
                    continue

                # Track procedures with no outputs (still generate lineage for audit)
                if not stored_proc_execution.outputs:
                    self.report.num_stored_proc_calls_with_no_outputs += 1
                    logger.debug(
                        f"Procedure {stored_proc_execution.call.snowflake_root_query_id} "
                        f"has no outputs, but continuing with lineage generation"
                    )
                    # Still continue to generate lineage for cases where we have inputs but no outputs

                # Generate a lineage entry for each output dataset
                has_generated_lineage = False
                for downstream in stored_proc_execution.outputs:
                    # Create a unique query ID for this procedure-output combination
                    stored_proc_query_id = get_query_fingerprint(
                        stored_proc_execution.call.query_text,
                        self.platform,
                        fast=True,
                        secondary_id=downstream,
                    )

                    # Create the lineage entry as a PreparsedQuery for pipeline compatibility
                    lineage_entry = PreparsedQuery(
                        query_id=stored_proc_query_id,
                        query_text=stored_proc_execution.call.query_text,
                        upstreams=stored_proc_execution.inputs,
                        downstream=downstream,
                        column_lineage=None,  # Procedures don't provide column-level lineage
                        column_usage=None,
                        inferred_schema=None,
                        confidence_score=0.8,  # Lower confidence for procedure-derived lineage
                        query_count=0,  # Procedure calls are not counted as regular queries
                        user=stored_proc_execution.call.user,
                        timestamp=stored_proc_execution.call.timestamp,
                        session_id="",  # Procedures don't have traditional session IDs
                        query_type=None,  # Will be determined by downstream processing
                        extra_info={
                            "is_stored_procedure_lineage": True,
                            "snowflake_root_query_id": stored_proc_execution.call.snowflake_root_query_id,
                            "procedure_name": stored_proc_execution.call.get_procedure_name(),
                            "input_count": len(stored_proc_execution.inputs),
                            "output_count": len(stored_proc_execution.outputs),
                        }
                    )

                    self.report.num_stored_proc_lineage_entries += 1
                    has_generated_lineage = True

                    logger.debug(
                        f"Generated lineage entry for procedure "
                        f"{stored_proc_execution.call.get_procedure_name()}: "
                        f"{len(stored_proc_execution.inputs)} inputs -> {downstream}"
                    )

                    yield lineage_entry

                # Track procedures that successfully generated lineage
                if has_generated_lineage:
                    self.report.num_procedures_with_lineage += 1

            except Exception as e:
                logger.error(
                    f"Failed to build lineage for procedure "
                    f"{stored_proc_execution.call.snowflake_root_query_id}: {e}"
                )
                continue

        logger.info(
            f"Completed stored procedure lineage generation: "
            f"{self.report.num_stored_proc_lineage_entries} entries from "
            f"{self.report.num_procedures_with_lineage} procedures"
        )

    def get_procedure_summary(self, root_query_id: str) -> Optional[dict]:
        """
        Get summary information for a specific procedure execution.

        Args:
            root_query_id: Snowflake root query ID

        Returns:
            Dictionary with procedure execution summary or None if not found
        """
        if root_query_id not in self._stored_proc_execution_lineage:
            return None

        execution = self._stored_proc_execution_lineage[root_query_id]
        return execution.to_dict()

    def get_all_procedure_names(self) -> List[str]:
        """Get all unique procedure names that have been tracked."""
        return sorted(list(self._procedure_names))

    def close(self) -> None:
        """
        Close the tracker and clean up resources.

        This method ensures proper cleanup of file-backed storage and
        logs final tracking statistics.
        """
        try:
            self._stored_proc_execution_lineage.close()
            self._procedure_names.clear()

            logger.info(
                f"Closed StoredProcLineageTracker. Final report: {self.report.get_summary()}"
            )

        except Exception as e:
            logger.error(f"Error closing StoredProcLineageTracker: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.close()


# Export all classes
__all__ = [
    'StoredProcCall',
    'StoredProcExecutionLineage',
    'StoredProcLineageReport',
    'StoredProcLineageTracker',
]


# Example usage and testing
if __name__ == "__main__":
    from dataguild.metadata.urns import CorpUserUrn

    print("=== DataGuild Stored Procedure Lineage Examples ===\n")

    # Example 1: Create a stored procedure call
    call = StoredProcCall(
        snowflake_root_query_id="01b2c3d4-e5f6-7890-abcd-ef1234567890",
        query_text="CALL ANALYTICS.CUSTOMER_ANALYSIS_PROC('2024-01-01', '2024-12-31');",
        timestamp=datetime.now(),
        user=CorpUserUrn("data_analyst@company.com"),
        default_db="ANALYTICS_DB",
        default_schema="PROCEDURES"
    )

    print("Example 1: Stored Procedure Call")
    print(f"Call: {call}")
    print(f"Procedure name: {call.get_procedure_name()}")
    print(f"Dictionary representation:")
    for k, v in call.to_dict().items():
        print(f"  {k}: {v}")
    print()

    # Example 2: Track procedure with simulated queries
    print("Example 2: Procedure Tracking with Lineage")
    with StoredProcLineageTracker(platform="snowflake") as tracker:
        tracker.add_stored_proc_call(call)

        # Simulate related queries (would normally come from query processing)
        class MockQuery:
            def __init__(self, query_id, upstreams, downstream, root_query_id):
                self.query_id = query_id
                self.upstreams = upstreams
                self.downstream = downstream
                self.extra_info = {"snowflake_root_query_id": root_query_id}
                self.user = call.user
                self.timestamp = call.timestamp

        # Add mock related queries
        query1 = MockQuery(
            "query1",
            ["urn:li:dataset:(snowflake,raw.customers,PROD)"],
            "urn:li:dataset:(snowflake,analytics.customer_summary,PROD)",
            call.snowflake_root_query_id
        )

        query2 = MockQuery(
            "query2",
            ["urn:li:dataset:(snowflake,raw.orders,PROD)", "urn:li:dataset:(snowflake,raw.products,PROD)"],
            "urn:li:dataset:(snowflake,analytics.customer_orders,PROD)",
            call.snowflake_root_query_id
        )

        # Associate queries with the procedure
        success1 = tracker.add_related_query(query1)
        success2 = tracker.add_related_query(query2)

        print(f"Query association results: {success1}, {success2}")
        print(f"Tracked procedure names: {tracker.get_all_procedure_names()}")

        # Generate lineage entries
        lineage_entries = list(tracker.build_merged_lineage_entries())

        print(f"Generated {len(lineage_entries)} lineage entries:")
        for i, entry in enumerate(lineage_entries, 1):
            print(f"  Entry {i}: {len(entry.upstreams)} upstreams -> {entry.downstream}")
            print(f"    Upstreams: {entry.upstreams}")
            print(f"    Confidence: {entry.confidence_score}")
        print()

        # Show comprehensive tracking report
        print("Example 3: Comprehensive Tracking Report")
        summary = tracker.report.get_summary()
        for section, data in summary.items():
            print(f"{section}:")
            for key, value in data.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")
            print()
