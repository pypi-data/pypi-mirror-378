"""
DataGuild SQL source reporting utilities.

This module provides comprehensive reporting capabilities for SQL-based data sources
including query tracking, performance metrics, and error reporting.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SQLOperationType(Enum):
    """Types of SQL operations tracked in reports."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    DESCRIBE = "DESCRIBE"
    SHOW = "SHOW"


class SQLExecutionStatus(Enum):
    """Status of SQL execution."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


@dataclass
class SQLQueryMetrics:
    """Metrics for a single SQL query execution."""

    query: str
    operation_type: SQLOperationType
    status: SQLExecutionStatus
    execution_time_ms: int
    rows_affected: Optional[int] = None
    rows_returned: Optional[int] = None
    bytes_processed: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "query": self.query,
            "operation_type": self.operation_type.value,
            "status": self.status.value,
            "execution_time_ms": self.execution_time_ms,
            "rows_affected": self.rows_affected,
            "rows_returned": self.rows_returned,
            "bytes_processed": self.bytes_processed,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


class SQLSourceReport(BaseModel):
    """
    Comprehensive reporting for SQL-based data sources.

    Tracks query executions, performance metrics, errors, and provides
    summary statistics for SQL source operations.
    """

    source_name: str = Field(description="Name of the SQL data source")
    start_time: datetime = Field(default_factory=datetime.now, description="Report start time")
    end_time: Optional[datetime] = Field(default=None, description="Report end time")

    # Query tracking
    total_queries: int = Field(default=0, description="Total number of queries executed")
    successful_queries: int = Field(default=0, description="Number of successful queries")
    failed_queries: int = Field(default=0, description="Number of failed queries")

    # Performance metrics
    total_execution_time_ms: int = Field(default=0, description="Total execution time in milliseconds")
    average_execution_time_ms: float = Field(default=0.0, description="Average execution time")
    max_execution_time_ms: int = Field(default=0, description="Maximum execution time")
    min_execution_time_ms: int = Field(default=0, description="Minimum execution time")

    # Data metrics
    total_rows_processed: int = Field(default=0, description="Total rows processed")
    total_bytes_processed: int = Field(default=0, description="Total bytes processed")

    # Collections for detailed tracking
    query_metrics: List[SQLQueryMetrics] = Field(default_factory=list, description="Individual query metrics")
    error_messages: List[str] = Field(default_factory=list, description="Collection of error messages")
    slow_queries: List[SQLQueryMetrics] = Field(default_factory=list, description="Queries exceeding threshold")

    # Configuration
    slow_query_threshold_ms: int = Field(default=5000, description="Threshold for slow query detection")
    max_stored_queries: int = Field(default=1000, description="Maximum queries to store in detail")

    class Config:
        arbitrary_types_allowed = True

    def add_query_execution(
            self,
            query: str,
            operation_type: Union[SQLOperationType, str],
            execution_time_ms: int,
            status: Union[SQLExecutionStatus, str] = SQLExecutionStatus.SUCCESS,
            rows_affected: Optional[int] = None,
            rows_returned: Optional[int] = None,
            bytes_processed: Optional[int] = None,
            error_message: Optional[str] = None
    ) -> None:
        """
        Record a SQL query execution in the report.

        Args:
            query: SQL query text
            operation_type: Type of SQL operation
            execution_time_ms: Execution time in milliseconds
            status: Execution status
            rows_affected: Number of rows affected (for DML operations)
            rows_returned: Number of rows returned (for SELECT operations)
            bytes_processed: Bytes processed during execution
            error_message: Error message if execution failed
        """
        # Convert string enums to enum instances
        if isinstance(operation_type, str):
            operation_type = SQLOperationType(operation_type.upper())
        if isinstance(status, str):
            status = SQLExecutionStatus(status.upper())

        # Create query metrics
        metrics = SQLQueryMetrics(
            query=query,
            operation_type=operation_type,
            status=status,
            execution_time_ms=execution_time_ms,
            rows_affected=rows_affected,
            rows_returned=rows_returned,
            bytes_processed=bytes_processed,
            error_message=error_message
        )

        # Update counters
        self.total_queries += 1
        if status == SQLExecutionStatus.SUCCESS:
            self.successful_queries += 1
        else:
            self.failed_queries += 1
            if error_message:
                self.error_messages.append(error_message)

        # Update performance metrics
        self.total_execution_time_ms += execution_time_ms
        if self.total_queries > 0:
            self.average_execution_time_ms = self.total_execution_time_ms / self.total_queries

        if execution_time_ms > self.max_execution_time_ms:
            self.max_execution_time_ms = execution_time_ms

        if self.min_execution_time_ms == 0 or execution_time_ms < self.min_execution_time_ms:
            self.min_execution_time_ms = execution_time_ms

        # Update data metrics
        if rows_affected:
            self.total_rows_processed += rows_affected
        if rows_returned:
            self.total_rows_processed += rows_returned
        if bytes_processed:
            self.total_bytes_processed += bytes_processed

        # Store detailed metrics (with size limit)
        if len(self.query_metrics) < self.max_stored_queries:
            self.query_metrics.append(metrics)

        # Track slow queries
        if execution_time_ms >= self.slow_query_threshold_ms:
            self.slow_queries.append(metrics)

    def get_success_rate(self) -> float:
        """Calculate query success rate as percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100.0

    def get_failure_rate(self) -> float:
        """Calculate query failure rate as percentage."""
        return 100.0 - self.get_success_rate()

    def get_queries_per_second(self) -> float:
        """Calculate average queries per second."""
        if not self.end_time:
            duration = datetime.now() - self.start_time
        else:
            duration = self.end_time - self.start_time

        duration_seconds = duration.total_seconds()
        if duration_seconds == 0:
            return 0.0

        return self.total_queries / duration_seconds

    def get_operation_breakdown(self) -> Dict[str, int]:
        """Get breakdown of queries by operation type."""
        breakdown = {}
        for metrics in self.query_metrics:
            op_type = metrics.operation_type.value
            breakdown[op_type] = breakdown.get(op_type, 0) + 1
        return breakdown

    def get_top_errors(self, limit: int = 10) -> List[str]:
        """Get most common error messages."""
        from collections import Counter
        error_counts = Counter(self.error_messages)
        return [error for error, _ in error_counts.most_common(limit)]

    def finalize_report(self) -> None:
        """Mark report as complete and set end time."""
        self.end_time = datetime.now()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the report."""
        duration = (self.end_time or datetime.now()) - self.start_time

        return {
            "source_name": self.source_name,
            "duration_seconds": duration.total_seconds(),
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "success_rate_percent": round(self.get_success_rate(), 2),
            "failure_rate_percent": round(self.get_failure_rate(), 2),
            "queries_per_second": round(self.get_queries_per_second(), 2),
            "average_execution_time_ms": round(self.average_execution_time_ms, 2),
            "max_execution_time_ms": self.max_execution_time_ms,
            "min_execution_time_ms": self.min_execution_time_ms,
            "total_rows_processed": self.total_rows_processed,
            "total_bytes_processed": self.total_bytes_processed,
            "slow_queries_count": len(self.slow_queries),
            "unique_errors_count": len(set(self.error_messages)),
            "operation_breakdown": self.get_operation_breakdown(),
        }

    def __repr__(self) -> str:
        """String representation of the report."""
        return f"SQLSourceReport(source={self.source_name}, queries={self.total_queries}, success_rate={self.get_success_rate():.1f}%)"
