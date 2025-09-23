"""
DataGuild SQLGlot lineage classes for column-level lineage tracking.

This module provides comprehensive column-level lineage data structures
for tracking relationships between upstream and downstream columns in
SQL queries across various data platforms.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


@dataclass
class ColumnRef:
    """
    Represents a reference to a specific column in a table or dataset.

    This class is used to identify upstream columns that contribute to
    the lineage of a downstream column in SQL transformations.

    Examples:
        >>> col_ref = ColumnRef(table="users", column="email")
        >>> print(col_ref.qualified_name)
        'users.email'

        >>> col_ref = ColumnRef(
        ...     table="urn:li:dataset:(snowflake,db.schema.users,PROD)",
        ...     column="user_id"
        ... )
    """

    table: str  # Table name, qualified name, or dataset URN
    column: str  # Column name

    def __post_init__(self):
        """Validate column reference after initialization."""
        if not self.table:
            raise ValueError("table cannot be empty")
        if not self.column:
            raise ValueError("column cannot be empty")

    @property
    def qualified_name(self) -> str:
        """Get the fully qualified column name."""
        return f"{self.table}.{self.column}"

    def is_urn(self) -> bool:
        """Check if the table reference is a URN."""
        return self.table.startswith("urn:")

    def get_table_name(self) -> str:
        """
        Extract table name from URN or return table as-is.

        Returns:
            Simple table name extracted from URN or original table value
        """
        if self.is_urn():
            # Extract table name from URN format
            # Example: urn:li:dataset:(snowflake,db.schema.table,PROD) -> table
            try:
                parts = self.table.split(",")
                if len(parts) >= 2:
                    qualified_name = parts[1]
                    return qualified_name.split(".")[-1]  # Get table name
            except Exception as e:
                logger.debug(f"Failed to parse table name from URN {self.table}: {e}")

        # Return table name as-is (might be qualified like db.schema.table)
        return self.table.split(".")[-1] if "." in self.table else self.table

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "table": self.table,
            "column": self.column,
            "qualified_name": self.qualified_name,
            "is_urn": self.is_urn(),
        }

    def __str__(self) -> str:
        """String representation."""
        return self.qualified_name

    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash((self.table, self.column))

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, ColumnRef):
            return False
        return self.table == other.table and self.column == other.column


@dataclass
class DownstreamColumnRef:
    """
    Represents a reference to a downstream column in a dataset.

    This class identifies the target column that receives lineage from
    one or more upstream columns in SQL transformations.

    Examples:
        >>> downstream = DownstreamColumnRef(
        ...     dataset="urn:li:dataset:(snowflake,analytics.user_summary,PROD)",
        ...     column="total_orders"
        ... )
        >>> print(downstream.qualified_name)
        'analytics.user_summary.total_orders'
    """

    dataset: str  # Dataset name, qualified name, or dataset URN
    column: str  # Column name

    def __post_init__(self):
        """Validate downstream column reference after initialization."""
        if not self.dataset:
            raise ValueError("dataset cannot be empty")
        if not self.column:
            raise ValueError("column cannot be empty")

    @property
    def qualified_name(self) -> str:
        """Get the fully qualified column name."""
        return f"{self.dataset}.{self.column}"

    def is_urn(self) -> bool:
        """Check if the dataset reference is a URN."""
        return self.dataset.startswith("urn:")

    def get_dataset_name(self) -> str:
        """
        Extract dataset name from URN or return dataset as-is.

        Returns:
            Simple dataset name extracted from URN or original dataset value
        """
        if self.is_urn():
            # Extract dataset name from URN format
            try:
                parts = self.dataset.split(",")
                if len(parts) >= 2:
                    qualified_name = parts[1]
                    return qualified_name.split(".")[-1]  # Get dataset name
            except Exception as e:
                logger.debug(f"Failed to parse dataset name from URN {self.dataset}: {e}")

        # Return dataset name as-is
        return self.dataset.split(".")[-1] if "." in self.dataset else self.dataset

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "dataset": self.dataset,
            "column": self.column,
            "qualified_name": self.qualified_name,
            "is_urn": self.is_urn(),
        }

    def __str__(self) -> str:
        """String representation."""
        return self.qualified_name

    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash((self.dataset, self.column))

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, DownstreamColumnRef):
            return False
        return self.dataset == other.dataset and self.column == other.column


@dataclass
class ColumnLineageInfo:
    """
    Represents complete column-level lineage information.

    This class captures the relationship between a downstream column
    and all the upstream columns that contribute to its value through
    SQL transformations.

    Examples:
        >>> lineage = ColumnLineageInfo(
        ...     downstream=DownstreamColumnRef(
        ...         dataset="analytics.user_metrics",
        ...         column="total_spent"
        ...     ),
        ...     upstreams=[
        ...         ColumnRef(table="orders", column="amount"),
        ...         ColumnRef(table="orders", column="tax"),
        ...         ColumnRef(table="orders", column="shipping_cost")
        ...     ],
        ...     confidence_score=0.95
        ... )
    """

    downstream: DownstreamColumnRef  # Target column receiving lineage
    upstreams: List[ColumnRef]  # Source columns contributing to lineage
    confidence_score: float = 1.0  # Confidence in lineage accuracy (0.0-1.0)
    transformation_type: Optional[str] = None  # Type of transformation (e.g., "AGGREGATION", "JOIN")
    sql_expression: Optional[str] = None  # SQL expression that creates the lineage
    extra_info: Optional[Dict[str, Any]] = field(default_factory=dict)  # Additional metadata

    def __post_init__(self):
        """Validate column lineage info after initialization."""
        if not isinstance(self.downstream, DownstreamColumnRef):
            raise ValueError("downstream must be a DownstreamColumnRef instance")
        if not isinstance(self.upstreams, list):
            raise ValueError("upstreams must be a list")
        if not all(isinstance(upstream, ColumnRef) for upstream in self.upstreams):
            raise ValueError("all upstreams must be ColumnRef instances")
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")

    def get_upstream_tables(self) -> Set[str]:
        """Get all unique upstream tables referenced in this lineage."""
        return {upstream.table for upstream in self.upstreams}

    def get_upstream_columns_by_table(self) -> Dict[str, List[str]]:
        """Get upstream columns grouped by table."""
        columns_by_table = {}
        for upstream in self.upstreams:
            if upstream.table not in columns_by_table:
                columns_by_table[upstream.table] = []
            columns_by_table[upstream.table].append(upstream.column)
        return columns_by_table

    def has_upstream_table(self, table: str) -> bool:
        """Check if a specific table is in the upstream lineage."""
        return table in self.get_upstream_tables()

    def has_upstream_column(self, table: str, column: str) -> bool:
        """Check if a specific column from a table is in the upstream lineage."""
        return ColumnRef(table=table, column=column) in self.upstreams

    def get_lineage_complexity(self) -> str:
        """
        Get a simple classification of lineage complexity.

        Returns:
            String indicating complexity: "SIMPLE", "MODERATE", or "COMPLEX"
        """
        num_upstreams = len(self.upstreams)
        num_tables = len(self.get_upstream_tables())

        if num_upstreams <= 1 and num_tables <= 1:
            return "SIMPLE"
        elif num_upstreams <= 5 and num_tables <= 3:
            return "MODERATE"
        else:
            return "COMPLEX"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "downstream": self.downstream.to_dict(),
            "upstreams": [upstream.to_dict() for upstream in self.upstreams],
            "confidence_score": self.confidence_score,
            "transformation_type": self.transformation_type,
            "sql_expression": self.sql_expression,
            "extra_info": self.extra_info,
            "upstream_tables": list(self.get_upstream_tables()),
            "lineage_complexity": self.get_lineage_complexity(),
        }

    def to_summary(self) -> str:
        """Get a human-readable summary of the lineage."""
        upstream_summary = ", ".join(str(upstream) for upstream in self.upstreams[:3])
        if len(self.upstreams) > 3:
            upstream_summary += f" ... and {len(self.upstreams) - 3} more"

        return f"{self.downstream} <- [{upstream_summary}]"

    def __str__(self) -> str:
        """String representation."""
        return self.to_summary()


# Utility functions for working with column lineage
def create_column_lineage(
        downstream_dataset: str,
        downstream_column: str,
        upstream_references: List[tuple],
        confidence_score: float = 1.0,
        transformation_type: Optional[str] = None,
) -> ColumnLineageInfo:
    """
    Factory function to create column lineage information.

    Args:
        downstream_dataset: Target dataset name or URN
        downstream_column: Target column name
        upstream_references: List of (table, column) tuples for upstream references
        confidence_score: Confidence in the lineage accuracy
        transformation_type: Optional transformation type

    Returns:
        ColumnLineageInfo instance

    Examples:
        >>> lineage = create_column_lineage(
        ...     downstream_dataset="analytics.user_summary",
        ...     downstream_column="total_orders",
        ...     upstream_references=[
        ...         ("raw.orders", "order_id"),
        ...         ("raw.orders", "user_id")
        ...     ],
        ...     confidence_score=0.9,
        ...     transformation_type="AGGREGATION"
        ... )
    """
    downstream = DownstreamColumnRef(
        dataset=downstream_dataset,
        column=downstream_column
    )

    upstreams = [
        ColumnRef(table=table, column=column)
        for table, column in upstream_references
    ]

    return ColumnLineageInfo(
        downstream=downstream,
        upstreams=upstreams,
        confidence_score=confidence_score,
        transformation_type=transformation_type,
    )


def merge_column_lineage(lineage_infos: List[ColumnLineageInfo]) -> List[ColumnLineageInfo]:
    """
    Merge column lineage information with the same downstream column.

    Args:
        lineage_infos: List of ColumnLineageInfo to merge

    Returns:
        List of merged ColumnLineageInfo with deduplicated upstreams
    """
    # Group by downstream column
    lineage_by_downstream = {}

    for lineage in lineage_infos:
        downstream_key = (lineage.downstream.dataset, lineage.downstream.column)

        if downstream_key not in lineage_by_downstream:
            lineage_by_downstream[downstream_key] = lineage
        else:
            # Merge upstreams
            existing_lineage = lineage_by_downstream[downstream_key]
            existing_upstreams = set(existing_lineage.upstreams)
            new_upstreams = set(lineage.upstreams)

            merged_upstreams = list(existing_upstreams.union(new_upstreams))
            existing_lineage.upstreams = merged_upstreams

            # Update confidence score (use minimum for conservative estimate)
            existing_lineage.confidence_score = min(
                existing_lineage.confidence_score,
                lineage.confidence_score
            )

    return list(lineage_by_downstream.values())


def filter_lineage_by_confidence(
        lineage_infos: List[ColumnLineageInfo],
        min_confidence: float = 0.5
) -> List[ColumnLineageInfo]:
    """
    Filter column lineage by minimum confidence score.

    Args:
        lineage_infos: List of ColumnLineageInfo to filter
        min_confidence: Minimum confidence score threshold

    Returns:
        Filtered list of ColumnLineageInfo
    """
    return [
        lineage for lineage in lineage_infos
        if lineage.confidence_score >= min_confidence
    ]


def get_lineage_statistics(lineage_infos: List[ColumnLineageInfo]) -> Dict[str, Any]:
    """
    Calculate statistics for a collection of column lineage information.

    Args:
        lineage_infos: List of ColumnLineageInfo to analyze

    Returns:
        Dictionary with lineage statistics
    """
    if not lineage_infos:
        return {
            "total_lineage_edges": 0,
            "unique_downstream_columns": 0,
            "unique_upstream_tables": 0,
            "unique_upstream_columns": 0,
            "average_confidence": 0.0,
            "complexity_distribution": {},
        }

    all_upstream_tables = set()
    all_upstream_columns = set()
    all_downstream_columns = set()
    complexity_counts = {"SIMPLE": 0, "MODERATE": 0, "COMPLEX": 0}

    for lineage in lineage_infos:
        all_upstream_tables.update(lineage.get_upstream_tables())
        all_upstream_columns.update(
            (upstream.table, upstream.column) for upstream in lineage.upstreams
        )
        all_downstream_columns.add(lineage.downstream.qualified_name)
        complexity_counts[lineage.get_lineage_complexity()] += 1

    average_confidence = sum(l.confidence_score for l in lineage_infos) / len(lineage_infos)

    return {
        "total_lineage_edges": len(lineage_infos),
        "unique_downstream_columns": len(all_downstream_columns),
        "unique_upstream_tables": len(all_upstream_tables),
        "unique_upstream_columns": len(all_upstream_columns),
        "average_confidence": round(average_confidence, 3),
        "complexity_distribution": complexity_counts,
    }


# Export all classes and functions
__all__ = [
    'ColumnRef',
    'DownstreamColumnRef',
    'ColumnLineageInfo',
    'create_column_lineage',
    'merge_column_lineage',
    'filter_lineage_by_confidence',
    'get_lineage_statistics',
]

# Example usage and testing
if __name__ == "__main__":
    # Example: Create column lineage for a user summary table
    print("=== DataGuild SQLGlot Lineage Examples ===\n")

    # Example 1: Simple lineage
    simple_lineage = create_column_lineage(
        downstream_dataset="analytics.user_summary",
        downstream_column="user_name",
        upstream_references=[("raw.users", "first_name"), ("raw.users", "last_name")],
        confidence_score=0.95,
        transformation_type="CONCATENATION"
    )

    print("Example 1: Simple lineage")
    print(f"Lineage: {simple_lineage}")
    print(f"Complexity: {simple_lineage.get_lineage_complexity()}")
    print(f"Upstream tables: {simple_lineage.get_upstream_tables()}")
    print()

    # Example 2: Complex lineage with multiple tables
    complex_lineage = create_column_lineage(
        downstream_dataset="analytics.user_metrics",
        downstream_column="total_revenue",
        upstream_references=[
            ("raw.orders", "amount"),
            ("raw.orders", "tax"),
            ("raw.discounts", "discount_amount"),
            ("raw.payments", "processing_fee"),
            ("raw.refunds", "refund_amount"),
        ],
        confidence_score=0.85,
        transformation_type="AGGREGATION"
    )

    print("Example 2: Complex lineage")
    print(f"Lineage: {complex_lineage}")
    print(f"Complexity: {complex_lineage.get_lineage_complexity()}")
    print(f"Columns by table: {complex_lineage.get_upstream_columns_by_table()}")
    print()

    # Example 3: Statistics
    all_lineage = [simple_lineage, complex_lineage]
    stats = get_lineage_statistics(all_lineage)

    print("Example 3: Lineage statistics")
    for key, value in stats.items():
        print(f"{key}: {value}")
