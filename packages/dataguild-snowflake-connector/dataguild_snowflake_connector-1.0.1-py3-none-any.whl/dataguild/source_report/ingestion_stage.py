"""
DataGuild ingestion stage constants and utilities with enhanced reporting.

This module provides constants, utilities, and comprehensive reporting capabilities
for tracking different stages of the ingestion process for monitoring, reporting,
and debugging purposes.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger(__name__)

# =============================================
# Core ingestion stage constants
# =============================================

METADATA_EXTRACTION = "Metadata Extraction"
SCHEMA_EXTRACTION = "Schema Extraction"
LINEAGE_EXTRACTION = "Lineage Extraction"
USAGE_EXTRACTION = "Usage Extraction"
PROFILING = "Data Profiling"
CLASSIFICATION = "Data Classification"
CONTAINER_EXTRACTION = "Container Extraction"
ASSERTION_EXTRACTION = "Assertion Extraction"

# ✅ ADDED: New extraction stages
QUERIES_EXTRACTION = "Queries Extraction"
VIEW_PARSING = "View Parsing"

# Usage extraction substages
USAGE_EXTRACTION_USAGE_AGGREGATION = "Usage Extraction - Usage Aggregation"
USAGE_EXTRACTION_OPERATIONAL_STATS = "Usage Extraction - Operational Statistics"
USAGE_EXTRACTION_QUERY_LOG = "Usage Extraction - Query Log Processing"
USAGE_EXTRACTION_USER_ACTIVITY = "Usage Extraction - User Activity Analysis"

# Metadata extraction substages
METADATA_EXTRACTION_DATABASE_DISCOVERY = "Metadata Extraction - Database Discovery"
METADATA_EXTRACTION_SCHEMA_DISCOVERY = "Metadata Extraction - Schema Discovery"
METADATA_EXTRACTION_TABLE_DISCOVERY = "Metadata Extraction - Table Discovery"
METADATA_EXTRACTION_VIEW_DISCOVERY = "Metadata Extraction - View Discovery"
METADATA_EXTRACTION_COLUMN_DISCOVERY = "Metadata Extraction - Column Discovery"

# Schema extraction substages
SCHEMA_EXTRACTION_COLUMN_TYPES = "Schema Extraction - Column Types"
SCHEMA_EXTRACTION_CONSTRAINTS = "Schema Extraction - Constraints"
SCHEMA_EXTRACTION_INDEXES = "Schema Extraction - Indexes"
SCHEMA_EXTRACTION_RELATIONSHIPS = "Schema Extraction - Relationships"

# Lineage extraction substages
LINEAGE_EXTRACTION_TABLE_LINEAGE = "Lineage Extraction - Table Lineage"
LINEAGE_EXTRACTION_COLUMN_LINEAGE = "Lineage Extraction - Column Lineage"
LINEAGE_EXTRACTION_SQL_PARSING = "Lineage Extraction - SQL Parsing"
LINEAGE_EXTRACTION_VIEW_LINEAGE = "Lineage Extraction - View Lineage"

# ✅ ADDED: Queries extraction substages
QUERIES_EXTRACTION_QUERY_HISTORY = "Queries Extraction - Query History"
QUERIES_EXTRACTION_EXECUTION_PLANS = "Queries Extraction - Execution Plans"
QUERIES_EXTRACTION_PERFORMANCE_METRICS = "Queries Extraction - Performance Metrics"
QUERIES_EXTRACTION_SQL_ANALYSIS = "Queries Extraction - SQL Analysis"

# ✅ ADDED: View parsing substages
VIEW_PARSING_SQL_PARSING = "View Parsing - SQL Parsing"
VIEW_PARSING_DEPENDENCY_ANALYSIS = "View Parsing - Dependency Analysis"
VIEW_PARSING_COLUMN_MAPPING = "View Parsing - Column Mapping"
VIEW_PARSING_MATERIALIZATION_CHECK = "View Parsing - Materialization Check"

# Profiling substages
PROFILING_COLUMN_STATS = "Data Profiling - Column Statistics"
PROFILING_DATA_QUALITY = "Data Profiling - Data Quality Metrics"
PROFILING_NULL_ANALYSIS = "Data Profiling - Null Analysis"
PROFILING_UNIQUENESS_ANALYSIS = "Data Profiling - Uniqueness Analysis"
PROFILING_PATTERN_ANALYSIS = "Data Profiling - Pattern Analysis"

# Classification substages
CLASSIFICATION_PII_DETECTION = "Data Classification - PII Detection"
CLASSIFICATION_SENSITIVE_DATA = "Data Classification - Sensitive Data Detection"
CLASSIFICATION_BUSINESS_GLOSSARY = "Data Classification - Business Glossary Mapping"
CLASSIFICATION_TAG_ASSIGNMENT = "Data Classification - Tag Assignment"

# Container extraction substages
CONTAINER_EXTRACTION_DATABASE_CONTAINERS = "Container Extraction - Database Containers"
CONTAINER_EXTRACTION_SCHEMA_CONTAINERS = "Container Extraction - Schema Containers"
CONTAINER_EXTRACTION_CATALOG_CONTAINERS = "Container Extraction - Catalog Containers"

# Work unit processing stages
WORKUNIT_PROCESSING = "Work Unit Processing"
WORKUNIT_VALIDATION = "Work Unit Validation"
WORKUNIT_TRANSFORMATION = "Work Unit Transformation"
WORKUNIT_EMISSION = "Work Unit Emission"

# Error handling and recovery stages
ERROR_HANDLING = "Error Handling"
RETRY_LOGIC = "Retry Logic"
GRACEFUL_DEGRADATION = "Graceful Degradation"

# State management stages
STATE_INITIALIZATION = "State Initialization"
STATE_PERSISTENCE = "State Persistence"
STATE_RECOVERY = "State Recovery"
CHECKPOINT_CREATION = "Checkpoint Creation"

# Platform-specific stages
SNOWFLAKE_CONNECTION = "Snowflake - Connection"
SNOWFLAKE_WAREHOUSE_SETUP = "Snowflake - Warehouse Setup"
SNOWFLAKE_QUERY_EXECUTION = "Snowflake - Query Execution"

BIGQUERY_AUTHENTICATION = "BigQuery - Authentication"
BIGQUERY_PROJECT_DISCOVERY = "BigQuery - Project Discovery"
BIGQUERY_DATASET_DISCOVERY = "BigQuery - Dataset Discovery"

DATABRICKS_CLUSTER_SETUP = "Databricks - Cluster Setup"
DATABRICKS_CATALOG_DISCOVERY = "Databricks - Catalog Discovery"
DATABRICKS_SCHEMA_DISCOVERY = "Databricks - Schema Discovery"


# =============================================
# Enhanced Enums and Classes
# =============================================

class IngestionStageType(Enum):
    """Enumeration of ingestion stage types for categorization."""
    SETUP = "setup"
    DISCOVERY = "discovery"
    EXTRACTION = "extraction"
    PROCESSING = "processing"
    VALIDATION = "validation"
    PERSISTENCE = "persistence"
    CLEANUP = "cleanup"
    ERROR_HANDLING = "error_handling"


class StageStatus(Enum):
    """Status values for ingestion stage execution."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class StagePriority(Enum):
    """Priority levels for stage execution."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class StageMetrics:
    """Comprehensive metrics for stage execution."""
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    bytes_processed: int = 0
    duration_seconds: float = 0.0
    memory_peak_mb: float = 0.0
    cpu_usage_percent: float = 0.0

    # Additional performance metrics
    throughput_records_per_sec: float = 0.0
    throughput_mb_per_sec: float = 0.0
    error_rate_percent: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary representation."""
        return {
            "records_processed": self.records_processed,
            "records_successful": self.records_successful,
            "records_failed": self.records_failed,
            "bytes_processed": self.bytes_processed,
            "duration_seconds": self.duration_seconds,
            "memory_peak_mb": self.memory_peak_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "throughput_records_per_sec": self.throughput_records_per_sec,
            "throughput_mb_per_sec": self.throughput_mb_per_sec,
            "error_rate_percent": self.error_rate_percent,
        }

    def calculate_derived_metrics(self) -> None:
        """Calculate derived performance metrics."""
        if self.duration_seconds > 0:
            self.throughput_records_per_sec = self.records_processed / self.duration_seconds
            self.throughput_mb_per_sec = (self.bytes_processed / 1024 / 1024) / self.duration_seconds

        if self.records_processed > 0:
            self.error_rate_percent = (self.records_failed / self.records_processed) * 100


class IngestionStage:
    """
    Enhanced ingestion stage with metadata and tracking capabilities.

    This class provides a structured way to represent ingestion stages
    with timing, status tracking, and hierarchical organization.
    """

    def __init__(
            self,
            name: str,
            stage_type: IngestionStageType = IngestionStageType.EXTRACTION,
            parent_stage: Optional[str] = None,
            description: Optional[str] = None,
            priority: StagePriority = StagePriority.NORMAL,
            timeout_seconds: Optional[int] = None,
    ):
        """
        Initialize an ingestion stage.

        Args:
            name: Name of the stage
            stage_type: Type of the stage
            parent_stage: Parent stage name for hierarchical organization
            description: Optional description of the stage
            priority: Execution priority
            timeout_seconds: Optional timeout for stage execution
        """
        self.name = name
        self.stage_type = stage_type
        self.parent_stage = parent_stage
        self.description = description
        self.priority = priority
        self.timeout_seconds = timeout_seconds
        self.substages: List[str] = []

    def add_substage(self, substage_name: str) -> None:
        """Add a substage to this stage."""
        if substage_name not in self.substages:
            self.substages.append(substage_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert stage to dictionary representation."""
        return {
            "name": self.name,
            "stage_type": self.stage_type.value,
            "parent_stage": self.parent_stage,
            "description": self.description,
            "priority": self.priority.value,
            "timeout_seconds": self.timeout_seconds,
            "substages": self.substages,
        }


@dataclass
class IngestionStageReport:
    """
    Comprehensive reporting for individual ingestion stages.

    Tracks the progress, performance, issues, and detailed metrics
    for each stage of the data ingestion pipeline with thread-safe operations.
    """

    stage_name: str
    stage_type: IngestionStageType = IngestionStageType.EXTRACTION
    status: StageStatus = StageStatus.NOT_STARTED
    priority: StagePriority = StagePriority.NORMAL

    # Timing information
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timeout_seconds: Optional[int] = None

    # Progress tracking
    total_items: Optional[int] = None
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0

    # Error and warning tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    # Performance metrics
    metrics: StageMetrics = field(default_factory=StageMetrics)

    # Stage-specific data and configuration
    stage_config: Dict[str, Any] = field(default_factory=dict)
    stage_metadata: Dict[str, Any] = field(default_factory=dict)

    # Sub-stages for complex operations
    sub_stage_reports: List["IngestionStageReport"] = field(default_factory=list)

    # Thread safety
    _lock: Lock = field(default_factory=Lock, repr=False, compare=False)

    def start_stage(self, total_items: Optional[int] = None) -> None:
        """
        Mark the stage as started and initialize timing.

        Args:
            total_items: Optional total number of items to process
        """
        with self._lock:
            self.status = StageStatus.IN_PROGRESS
            self.start_time = datetime.now()
            if total_items is not None:
                self.total_items = total_items

            logger.info(
                f"Started ingestion stage '{self.stage_name}' "
                f"(type: {self.stage_type.value}, priority: {self.priority.value})"
            )

    def complete_stage(self) -> None:
        """Mark the stage as completed successfully."""
        with self._lock:
            self.status = StageStatus.COMPLETED
            self.end_time = datetime.now()

            # Update metrics
            if self.start_time and self.end_time:
                duration = self.end_time - self.start_time
                self.metrics.duration_seconds = duration.total_seconds()
                self.metrics.records_processed = self.processed_items
                self.metrics.records_successful = self.successful_items
                self.metrics.records_failed = self.failed_items
                self.metrics.calculate_derived_metrics()

            logger.info(
                f"Completed ingestion stage '{self.stage_name}' in "
                f"{self.metrics.duration_seconds:.2f}s "
                f"(processed: {self.processed_items}, success: {self.successful_items}, "
                f"failed: {self.failed_items})"
            )

    def fail_stage(self, error_message: str, can_retry: bool = True) -> None:
        """
        Mark the stage as failed with an error message.

        Args:
            error_message: Description of the failure
            can_retry: Whether this stage can be retried
        """
        with self._lock:
            self.errors.append(error_message)
            self.end_time = datetime.now()

            # Determine if we should retry
            if can_retry and self.retry_count < self.max_retries:
                self.status = StageStatus.RETRYING
                self.retry_count += 1
                logger.warning(
                    f"Retrying ingestion stage '{self.stage_name}' "
                    f"(attempt {self.retry_count}/{self.max_retries}): {error_message}"
                )
            else:
                self.status = StageStatus.FAILED
                logger.error(
                    f"Failed ingestion stage '{self.stage_name}' "
                    f"after {self.retry_count} retries: {error_message}"
                )

    def skip_stage(self, reason: str) -> None:
        """
        Mark the stage as skipped with a reason.

        Args:
            reason: Reason why the stage was skipped
        """
        with self._lock:
            self.status = StageStatus.SKIPPED
            self.end_time = datetime.now()
            self.warnings.append(f"Stage skipped: {reason}")
            self.stage_metadata["skip_reason"] = reason

            logger.info(f"Skipped ingestion stage '{self.stage_name}': {reason}")

    def cancel_stage(self, reason: str) -> None:
        """
        Mark the stage as cancelled.

        Args:
            reason: Reason for cancellation
        """
        with self._lock:
            self.status = StageStatus.CANCELLED
            self.end_time = datetime.now()
            self.warnings.append(f"Stage cancelled: {reason}")
            self.stage_metadata["cancel_reason"] = reason

            logger.warning(f"Cancelled ingestion stage '{self.stage_name}': {reason}")

    def add_error(self, error: str) -> None:
        """Add an error message to the stage."""
        with self._lock:
            self.errors.append(error)
            self.failed_items += 1

    def add_warning(self, warning: str) -> None:
        """Add a warning message to the stage."""
        with self._lock:
            self.warnings.append(warning)

    def update_progress(
        self,
        processed: Optional[int] = None,
        successful: Optional[int] = None,
        failed: Optional[int] = None,
        skipped: Optional[int] = None,
        total: Optional[int] = None
    ) -> None:
        """
        Update progress counters atomically.

        Args:
            processed: Increment processed counter
            successful: Increment successful counter
            failed: Increment failed counter
            skipped: Increment skipped counter
            total: Set total items (if known)
        """
        with self._lock:
            if processed is not None:
                self.processed_items += processed
            if successful is not None:
                self.successful_items += successful
            if failed is not None:
                self.failed_items += failed
            if skipped is not None:
                self.skipped_items += skipped
            if total is not None:
                self.total_items = total

    def set_total_items(self, total: int) -> None:
        """Set the total number of items for this stage."""
        with self._lock:
            self.total_items = total

    def add_sub_stage(self, sub_stage: "IngestionStageReport") -> None:
        """Add a sub-stage report to this stage."""
        with self._lock:
            self.sub_stage_reports.append(sub_stage)

    def update_metrics(
        self,
        bytes_processed: Optional[int] = None,
        memory_peak_mb: Optional[float] = None,
        cpu_usage_percent: Optional[float] = None
    ) -> None:
        """
        Update performance metrics.

        Args:
            bytes_processed: Bytes processed during this stage
            memory_peak_mb: Peak memory usage in MB
            cpu_usage_percent: CPU usage percentage
        """
        with self._lock:
            if bytes_processed is not None:
                self.metrics.bytes_processed += bytes_processed
            if memory_peak_mb is not None:
                self.metrics.memory_peak_mb = max(self.metrics.memory_peak_mb, memory_peak_mb)
            if cpu_usage_percent is not None:
                self.metrics.cpu_usage_percent = cpu_usage_percent

    def get_progress_percentage(self) -> Optional[float]:
        """Get progress as percentage (0.0-100.0)."""
        with self._lock:
            if self.total_items is None or self.total_items == 0:
                return None
            return (self.processed_items / self.total_items) * 100.0

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        with self._lock:
            if self.processed_items == 0:
                return 100.0
            return (self.successful_items / self.processed_items) * 100.0

    def get_error_rate(self) -> float:
        """Get error rate as percentage."""
        with self._lock:
            if self.processed_items == 0:
                return 0.0
            return (self.failed_items / self.processed_items) * 100.0

    def get_duration(self) -> Optional[timedelta]:
        """Get duration of the stage."""
        with self._lock:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            elif self.start_time:
                return datetime.now() - self.start_time
            return None

    def get_duration_seconds(self) -> Optional[float]:
        """Get duration in seconds."""
        duration = self.get_duration()
        return duration.total_seconds() if duration else None

    def is_timeout_exceeded(self) -> bool:
        """Check if the stage has exceeded its timeout."""
        if not self.timeout_seconds or not self.start_time:
            return False

        current_duration = (datetime.now() - self.start_time).total_seconds()
        return current_duration > self.timeout_seconds

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary information for the stage."""
        with self._lock:
            progress_pct = self.get_progress_percentage()
            duration_seconds = self.get_duration_seconds()

            return {
                "stage_name": self.stage_name,
                "stage_type": self.stage_type.value,
                "status": self.status.value,
                "priority": self.priority.value,
                "duration_seconds": duration_seconds,
                "progress_percentage": progress_pct,
                "success_rate": round(self.get_success_rate(), 2),
                "error_rate": round(self.get_error_rate(), 2),
                "total_items": self.total_items,
                "processed_items": self.processed_items,
                "successful_items": self.successful_items,
                "failed_items": self.failed_items,
                "skipped_items": self.skipped_items,
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
                "retry_count": self.retry_count,
                "max_retries": self.max_retries,
                "metrics": self.metrics.to_dict(),
                "sub_stages": len(self.sub_stage_reports),
                "timeout_seconds": self.timeout_seconds,
                "timeout_exceeded": self.is_timeout_exceeded(),
            }

    def is_completed(self) -> bool:
        """Check if stage is completed."""
        return self.status == StageStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if stage failed."""
        return self.status == StageStatus.FAILED

    def is_in_progress(self) -> bool:
        """Check if stage is in progress."""
        return self.status == StageStatus.IN_PROGRESS

    def is_retrying(self) -> bool:
        """Check if stage is retrying."""
        return self.status == StageStatus.RETRYING

    def has_errors(self) -> bool:
        """Check if stage has any errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if stage has any warnings."""
        return len(self.warnings) > 0

    def can_retry(self) -> bool:
        """Check if stage can be retried."""
        return self.retry_count < self.max_retries

    def get_aggregated_sub_stage_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all sub-stages."""
        if not self.sub_stage_reports:
            return {}

        total_duration = 0.0
        total_processed = 0
        total_successful = 0
        total_failed = 0
        total_errors = 0
        total_warnings = 0

        for sub_stage in self.sub_stage_reports:
            summary = sub_stage.get_summary()
            total_duration += summary.get("duration_seconds", 0) or 0
            total_processed += summary.get("processed_items", 0)
            total_successful += summary.get("successful_items", 0)
            total_failed += summary.get("failed_items", 0)
            total_errors += summary.get("error_count", 0)
            total_warnings += summary.get("warning_count", 0)

        return {
            "sub_stage_count": len(self.sub_stage_reports),
            "total_duration_seconds": total_duration,
            "total_processed_items": total_processed,
            "total_successful_items": total_successful,
            "total_failed_items": total_failed,
            "total_error_count": total_errors,
            "total_warning_count": total_warnings,
            "average_success_rate": (total_successful / total_processed * 100) if total_processed > 0 else 0,
        }

    def __repr__(self) -> str:
        """String representation of the stage report."""
        with self._lock:
            progress = f", {self.get_progress_percentage():.1f}%" if self.get_progress_percentage() else ""
            duration = f", {self.get_duration_seconds():.2f}s" if self.get_duration_seconds() else ""
            return (
                f"IngestionStageReport(stage={self.stage_name}, "
                f"status={self.status.value}{progress}{duration})"
            )


# =============================================
# Predefined Stage Definitions (Enhanced)
# =============================================

# Predefined stage definitions
STAGE_DEFINITIONS = {
    # Core stages
    METADATA_EXTRACTION: IngestionStage(
        METADATA_EXTRACTION,
        IngestionStageType.EXTRACTION,
        description="Extract metadata about datasets, tables, and schemas",
        priority=StagePriority.HIGH,
        timeout_seconds=1800  # 30 minutes
    ),

    USAGE_EXTRACTION: IngestionStage(
        USAGE_EXTRACTION,
        IngestionStageType.EXTRACTION,
        description="Extract usage statistics and operational data",
        priority=StagePriority.NORMAL,
        timeout_seconds=3600  # 1 hour
    ),

    LINEAGE_EXTRACTION: IngestionStage(
        LINEAGE_EXTRACTION,
        IngestionStageType.EXTRACTION,
        description="Extract data lineage information",
        priority=StagePriority.NORMAL,
        timeout_seconds=2400  # 40 minutes
    ),

    PROFILING: IngestionStage(
        PROFILING,
        IngestionStageType.PROCESSING,
        description="Profile data for quality and statistical analysis",
        priority=StagePriority.LOW,
        timeout_seconds=7200  # 2 hours
    ),

    CLASSIFICATION: IngestionStage(
        CLASSIFICATION,
        IngestionStageType.PROCESSING,
        description="Classify data for PII and sensitive data detection",
        priority=StagePriority.NORMAL,
        timeout_seconds=1800  # 30 minutes
    ),

    # ✅ ADDED: New stage definitions
    QUERIES_EXTRACTION: IngestionStage(
        QUERIES_EXTRACTION,
        IngestionStageType.EXTRACTION,
        description="Extract query history, execution plans, and performance metrics",
        priority=StagePriority.NORMAL,
        timeout_seconds=2400  # 40 minutes
    ),

    VIEW_PARSING: IngestionStage(
        VIEW_PARSING,
        IngestionStageType.PROCESSING,
        description="Parse view definitions and analyze dependencies",
        priority=StagePriority.NORMAL,
        timeout_seconds=1200  # 20 minutes
    ),

    # Usage extraction substages
    USAGE_EXTRACTION_USAGE_AGGREGATION: IngestionStage(
        USAGE_EXTRACTION_USAGE_AGGREGATION,
        IngestionStageType.PROCESSING,
        parent_stage=USAGE_EXTRACTION,
        description="Aggregate usage statistics from raw data",
        priority=StagePriority.NORMAL
    ),

    USAGE_EXTRACTION_OPERATIONAL_STATS: IngestionStage(
        USAGE_EXTRACTION_OPERATIONAL_STATS,
        IngestionStageType.PROCESSING,
        parent_stage=USAGE_EXTRACTION,
        description="Extract operational statistics and performance metrics",
        priority=StagePriority.NORMAL
    ),

    # ✅ ADDED: Queries extraction substages
    QUERIES_EXTRACTION_QUERY_HISTORY: IngestionStage(
        QUERIES_EXTRACTION_QUERY_HISTORY,
        IngestionStageType.EXTRACTION,
        parent_stage=QUERIES_EXTRACTION,
        description="Extract historical query information and patterns",
        priority=StagePriority.NORMAL
    ),

    QUERIES_EXTRACTION_EXECUTION_PLANS: IngestionStage(
        QUERIES_EXTRACTION_EXECUTION_PLANS,
        IngestionStageType.EXTRACTION,
        parent_stage=QUERIES_EXTRACTION,
        description="Extract and analyze query execution plans",
        priority=StagePriority.NORMAL
    ),

    QUERIES_EXTRACTION_PERFORMANCE_METRICS: IngestionStage(
        QUERIES_EXTRACTION_PERFORMANCE_METRICS,
        IngestionStageType.EXTRACTION,
        parent_stage=QUERIES_EXTRACTION,
        description="Extract query performance and optimization metrics",
        priority=StagePriority.NORMAL
    ),

    QUERIES_EXTRACTION_SQL_ANALYSIS: IngestionStage(
        QUERIES_EXTRACTION_SQL_ANALYSIS,
        IngestionStageType.PROCESSING,
        parent_stage=QUERIES_EXTRACTION,
        description="Analyze SQL queries for patterns and complexity",
        priority=StagePriority.NORMAL
    ),

    # ✅ ADDED: View parsing substages
    VIEW_PARSING_SQL_PARSING: IngestionStage(
        VIEW_PARSING_SQL_PARSING,
        IngestionStageType.PROCESSING,
        parent_stage=VIEW_PARSING,
        description="Parse SQL definitions of views for structure analysis",
        priority=StagePriority.NORMAL
    ),

    VIEW_PARSING_DEPENDENCY_ANALYSIS: IngestionStage(
        VIEW_PARSING_DEPENDENCY_ANALYSIS,
        IngestionStageType.PROCESSING,
        parent_stage=VIEW_PARSING,
        description="Analyze dependencies between views and base tables",
        priority=StagePriority.HIGH
    ),

    VIEW_PARSING_COLUMN_MAPPING: IngestionStage(
        VIEW_PARSING_COLUMN_MAPPING,
        IngestionStageType.PROCESSING,
        parent_stage=VIEW_PARSING,
        description="Map view columns to source table columns",
        priority=StagePriority.NORMAL
    ),

    VIEW_PARSING_MATERIALIZATION_CHECK: IngestionStage(
        VIEW_PARSING_MATERIALIZATION_CHECK,
        IngestionStageType.VALIDATION,
        parent_stage=VIEW_PARSING,
        description="Check view materialization status and refresh patterns",
        priority=StagePriority.NORMAL
    ),

    # Metadata extraction substages
    METADATA_EXTRACTION_DATABASE_DISCOVERY: IngestionStage(
        METADATA_EXTRACTION_DATABASE_DISCOVERY,
        IngestionStageType.DISCOVERY,
        parent_stage=METADATA_EXTRACTION,
        description="Discover databases in the data source",
        priority=StagePriority.HIGH
    ),

    METADATA_EXTRACTION_SCHEMA_DISCOVERY: IngestionStage(
        METADATA_EXTRACTION_SCHEMA_DISCOVERY,
        IngestionStageType.DISCOVERY,
        parent_stage=METADATA_EXTRACTION,
        description="Discover schemas within databases",
        priority=StagePriority.HIGH
    ),

    METADATA_EXTRACTION_TABLE_DISCOVERY: IngestionStage(
        METADATA_EXTRACTION_TABLE_DISCOVERY,
        IngestionStageType.DISCOVERY,
        parent_stage=METADATA_EXTRACTION,
        description="Discover tables within schemas",
        priority=StagePriority.HIGH
    ),

    # Platform-specific stages
    SNOWFLAKE_CONNECTION: IngestionStage(
        SNOWFLAKE_CONNECTION,
        IngestionStageType.SETUP,
        description="Establish connection to Snowflake",
        priority=StagePriority.CRITICAL,
        timeout_seconds=300  # 5 minutes
    ),

    SNOWFLAKE_WAREHOUSE_SETUP: IngestionStage(
        SNOWFLAKE_WAREHOUSE_SETUP,
        IngestionStageType.SETUP,
        description="Configure Snowflake warehouse for queries",
        priority=StagePriority.HIGH,
        timeout_seconds=180  # 3 minutes
    ),
}

# Populate parent-child relationships
for stage_name, stage in STAGE_DEFINITIONS.items():
    if stage.parent_stage and stage.parent_stage in STAGE_DEFINITIONS:
        STAGE_DEFINITIONS[stage.parent_stage].add_substage(stage_name)


# =============================================
# Utility Functions (Enhanced)
# =============================================

def get_stage_hierarchy() -> Dict[str, List[str]]:
    """
    Get the stage hierarchy mapping parent stages to their substages.

    Returns:
        Dictionary mapping parent stage names to lists of substage names
    """
    hierarchy = {}
    for stage_name, stage in STAGE_DEFINITIONS.items():
        if stage.substages:
            hierarchy[stage_name] = stage.substages.copy()
    return hierarchy


def get_all_stages() -> List[str]:
    """Get all available ingestion stage names."""
    return list(STAGE_DEFINITIONS.keys())


def get_stages_by_type(stage_type: IngestionStageType) -> List[str]:
    """Get all stages of a specific type."""
    return [
        stage_name for stage_name, stage in STAGE_DEFINITIONS.items()
        if stage.stage_type == stage_type
    ]


def get_stages_by_priority(priority: StagePriority) -> List[str]:
    """Get all stages of a specific priority."""
    return [
        stage_name for stage_name, stage in STAGE_DEFINITIONS.items()
        if stage.priority == priority
    ]


def create_stage_report(
    stage_name: str,
    total_items: Optional[int] = None,
    priority: Optional[StagePriority] = None,
    timeout_seconds: Optional[int] = None
) -> IngestionStageReport:
    """
    Create an IngestionStageReport for a given stage name.

    Args:
        stage_name: Name of the stage
        total_items: Optional total number of items to process
        priority: Optional priority override
        timeout_seconds: Optional timeout override

    Returns:
        Configured IngestionStageReport instance
    """
    stage_def = STAGE_DEFINITIONS.get(stage_name)
    if not stage_def:
        # Create a generic stage if not found in definitions
        stage_type = IngestionStageType.PROCESSING
        stage_priority = priority or StagePriority.NORMAL
        stage_timeout = timeout_seconds
    else:
        stage_type = stage_def.stage_type
        stage_priority = priority or stage_def.priority
        stage_timeout = timeout_seconds or stage_def.timeout_seconds

    return IngestionStageReport(
        stage_name=stage_name,
        stage_type=stage_type,
        priority=stage_priority,
        timeout_seconds=stage_timeout,
        total_items=total_items
    )


def create_stage_pipeline(stage_names: List[str]) -> List[IngestionStageReport]:
    """Create a pipeline of ingestion stage reports."""
    return [create_stage_report(stage_name) for stage_name in stage_names]


def get_default_ingestion_pipeline() -> List[IngestionStageReport]:
    """Get the default ingestion pipeline with stage reports."""
    default_stages = [
        STATE_INITIALIZATION,
        METADATA_EXTRACTION,
        SCHEMA_EXTRACTION,
        USAGE_EXTRACTION,
        QUERIES_EXTRACTION,  # ✅ ADDED
        LINEAGE_EXTRACTION,
        VIEW_PARSING,  # ✅ ADDED
        PROFILING,
        CLASSIFICATION,
        WORKUNIT_PROCESSING,
        STATE_PERSISTENCE,
    ]
    return create_stage_pipeline(default_stages)


def get_snowflake_pipeline() -> List[IngestionStageReport]:
    """Get Snowflake-specific ingestion pipeline."""
    snowflake_stages = [
        SNOWFLAKE_CONNECTION,
        SNOWFLAKE_WAREHOUSE_SETUP,
        METADATA_EXTRACTION_DATABASE_DISCOVERY,
        METADATA_EXTRACTION_SCHEMA_DISCOVERY,
        METADATA_EXTRACTION_TABLE_DISCOVERY,
        QUERIES_EXTRACTION_QUERY_HISTORY,  # ✅ ADDED
        USAGE_EXTRACTION_USAGE_AGGREGATION,
        USAGE_EXTRACTION_OPERATIONAL_STATS,
        VIEW_PARSING_SQL_PARSING,  # ✅ ADDED
        CLASSIFICATION,
        WORKUNIT_PROCESSING,
    ]
    return create_stage_pipeline(snowflake_stages)


# ✅ ADDED: New pipeline functions for queries and view parsing
def get_queries_extraction_pipeline() -> List[IngestionStageReport]:
    """Get queries extraction specific pipeline."""
    queries_stages = [
        QUERIES_EXTRACTION_QUERY_HISTORY,
        QUERIES_EXTRACTION_EXECUTION_PLANS,
        QUERIES_EXTRACTION_PERFORMANCE_METRICS,
        QUERIES_EXTRACTION_SQL_ANALYSIS,
    ]
    return create_stage_pipeline(queries_stages)


def get_view_parsing_pipeline() -> List[IngestionStageReport]:
    """Get view parsing specific pipeline."""
    view_stages = [
        VIEW_PARSING_SQL_PARSING,
        VIEW_PARSING_DEPENDENCY_ANALYSIS,
        VIEW_PARSING_COLUMN_MAPPING,
        VIEW_PARSING_MATERIALIZATION_CHECK,
    ]
    return create_stage_pipeline(view_stages)


def validate_stage_name(stage_name: str) -> bool:
    """Validate that a stage name exists in the definitions."""
    return stage_name in STAGE_DEFINITIONS


def get_stage_description(stage_name: str) -> Optional[str]:
    """Get the description of a stage."""
    stage = STAGE_DEFINITIONS.get(stage_name)
    return stage.description if stage else None


def is_substage_of(substage: str, parent_stage: str) -> bool:
    """Check if a stage is a substage of another stage."""
    if parent_stage not in STAGE_DEFINITIONS:
        return False
    return substage in STAGE_DEFINITIONS[parent_stage].substages


# =============================================
# Stage Collections (Enhanced)
# =============================================

# Platform-specific stage collections
SNOWFLAKE_STAGES = [
    SNOWFLAKE_CONNECTION,
    SNOWFLAKE_WAREHOUSE_SETUP,
    SNOWFLAKE_QUERY_EXECUTION,
    METADATA_EXTRACTION_DATABASE_DISCOVERY,
    METADATA_EXTRACTION_SCHEMA_DISCOVERY,
    METADATA_EXTRACTION_TABLE_DISCOVERY,
    QUERIES_EXTRACTION_QUERY_HISTORY,  # ✅ ADDED
    USAGE_EXTRACTION_USAGE_AGGREGATION,
    USAGE_EXTRACTION_OPERATIONAL_STATS,
    VIEW_PARSING_SQL_PARSING,  # ✅ ADDED
]

BIGQUERY_STAGES = [
    BIGQUERY_AUTHENTICATION,
    BIGQUERY_PROJECT_DISCOVERY,
    BIGQUERY_DATASET_DISCOVERY,
    METADATA_EXTRACTION,
    USAGE_EXTRACTION,
    QUERIES_EXTRACTION,  # ✅ ADDED
    LINEAGE_EXTRACTION,
    VIEW_PARSING,  # ✅ ADDED
]

DATABRICKS_STAGES = [
    DATABRICKS_CLUSTER_SETUP,
    DATABRICKS_CATALOG_DISCOVERY,
    DATABRICKS_SCHEMA_DISCOVERY,
    METADATA_EXTRACTION,
    QUERIES_EXTRACTION,  # ✅ ADDED
    LINEAGE_EXTRACTION,
    VIEW_PARSING,  # ✅ ADDED
]

# Stage collections by category
EXTRACTION_STAGES = [
    METADATA_EXTRACTION,
    SCHEMA_EXTRACTION,
    LINEAGE_EXTRACTION,
    USAGE_EXTRACTION,
    QUERIES_EXTRACTION,  # ✅ ADDED
    CONTAINER_EXTRACTION,
    ASSERTION_EXTRACTION,
]

PROCESSING_STAGES = [
    PROFILING,
    CLASSIFICATION,
    VIEW_PARSING,  # ✅ ADDED
    WORKUNIT_PROCESSING,
    WORKUNIT_VALIDATION,
    WORKUNIT_TRANSFORMATION,
]

ERROR_RECOVERY_STAGES = [
    ERROR_HANDLING,
    RETRY_LOGIC,
    GRACEFUL_DEGRADATION,
]

STATE_MANAGEMENT_STAGES = [
    STATE_INITIALIZATION,
    STATE_PERSISTENCE,
    STATE_RECOVERY,
    CHECKPOINT_CREATION,
]

# ✅ ADDED: New stage collections
QUERIES_STAGES = [
    QUERIES_EXTRACTION,
    QUERIES_EXTRACTION_QUERY_HISTORY,
    QUERIES_EXTRACTION_EXECUTION_PLANS,
    QUERIES_EXTRACTION_PERFORMANCE_METRICS,
    QUERIES_EXTRACTION_SQL_ANALYSIS,
]

VIEW_STAGES = [
    VIEW_PARSING,
    VIEW_PARSING_SQL_PARSING,
    VIEW_PARSING_DEPENDENCY_ANALYSIS,
    VIEW_PARSING_COLUMN_MAPPING,
    VIEW_PARSING_MATERIALIZATION_CHECK,
]

CRITICAL_STAGES = get_stages_by_priority(StagePriority.CRITICAL)
HIGH_PRIORITY_STAGES = get_stages_by_priority(StagePriority.HIGH)


# =============================================
# Export All Constants and Classes
# =============================================

__all__ = [
    # Core stage constants
    'METADATA_EXTRACTION',
    'SCHEMA_EXTRACTION',
    'LINEAGE_EXTRACTION',
    'USAGE_EXTRACTION',
    'PROFILING',
    'CLASSIFICATION',
    'CONTAINER_EXTRACTION',
    'ASSERTION_EXTRACTION',

    # ✅ ADDED: New stage constants
    'QUERIES_EXTRACTION',
    'VIEW_PARSING',

    # Usage extraction substages
    'USAGE_EXTRACTION_USAGE_AGGREGATION',
    'USAGE_EXTRACTION_OPERATIONAL_STATS',
    'USAGE_EXTRACTION_QUERY_LOG',
    'USAGE_EXTRACTION_USER_ACTIVITY',

    # ✅ ADDED: Queries extraction substages
    'QUERIES_EXTRACTION_QUERY_HISTORY',
    'QUERIES_EXTRACTION_EXECUTION_PLANS',
    'QUERIES_EXTRACTION_PERFORMANCE_METRICS',
    'QUERIES_EXTRACTION_SQL_ANALYSIS',

    # ✅ ADDED: View parsing substages
    'VIEW_PARSING_SQL_PARSING',
    'VIEW_PARSING_DEPENDENCY_ANALYSIS',
    'VIEW_PARSING_COLUMN_MAPPING',
    'VIEW_PARSING_MATERIALIZATION_CHECK',

    # Other substages
    'METADATA_EXTRACTION_DATABASE_DISCOVERY',
    'METADATA_EXTRACTION_SCHEMA_DISCOVERY',
    'METADATA_EXTRACTION_TABLE_DISCOVERY',
    'METADATA_EXTRACTION_VIEW_DISCOVERY',
    'METADATA_EXTRACTION_COLUMN_DISCOVERY',

    # Work unit and state management stages
    'WORKUNIT_PROCESSING',
    'WORKUNIT_VALIDATION',
    'STATE_INITIALIZATION',
    'STATE_PERSISTENCE',

    # Platform-specific stages
    'SNOWFLAKE_CONNECTION',
    'SNOWFLAKE_WAREHOUSE_SETUP',
    'BIGQUERY_AUTHENTICATION',
    'DATABRICKS_CLUSTER_SETUP',

    # Enhanced classes and enums
    'IngestionStageType',
    'StageStatus',
    'StagePriority',
    'StageMetrics',
    'IngestionStage',
    'IngestionStageReport',
    'STAGE_DEFINITIONS',

    # Utility functions
    'get_stage_hierarchy',
    'get_all_stages',
    'get_stages_by_type',
    'get_stages_by_priority',
    'create_stage_report',
    'create_stage_pipeline',
    'get_default_ingestion_pipeline',
    'get_snowflake_pipeline',

    # ✅ ADDED: New pipeline functions
    'get_queries_extraction_pipeline',
    'get_view_parsing_pipeline',

    'validate_stage_name',
    'get_stage_description',
    'is_substage_of',

    # Platform-specific collections
    'SNOWFLAKE_STAGES',
    'BIGQUERY_STAGES',
    'DATABRICKS_STAGES',

    # Category collections
    'EXTRACTION_STAGES',
    'PROCESSING_STAGES',
    'ERROR_RECOVERY_STAGES',
    'STATE_MANAGEMENT_STAGES',

    # ✅ ADDED: New stage collections
    'QUERIES_STAGES',
    'VIEW_STAGES',

    'CRITICAL_STAGES',
    'HIGH_PRIORITY_STAGES',
]
