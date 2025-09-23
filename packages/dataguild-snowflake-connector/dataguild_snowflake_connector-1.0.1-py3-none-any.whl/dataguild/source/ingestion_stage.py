"""
DataGuild Ingestion Stage Constants and Utilities

This module provides stage constants and utilities for tracking ingestion progress,
performance monitoring, and structured reporting across different extraction stages.
Extends the existing ingestion stage system with additional constants and utilities.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger(__name__)

# =============================================
# Extended Ingestion Stage Constants
# =============================================

# Core extraction stages (existing)
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

# ✅ ADDED: Extended lineage and DDL stages
EXTERNAL_TABLE_DDL_LINEAGE = "External Table DDL Lineage"
VIEW_LINEAGE_EXTRACTION = "View Lineage Extraction"
PROCEDURE_LINEAGE_EXTRACTION = "Procedure Lineage Extraction"
COLUMN_LINEAGE_EXTRACTION = "Column Lineage Extraction"

# Data quality and validation stages
DATA_QUALITY_ASSESSMENT = "Data Quality Assessment"
SCHEMA_VALIDATION = "Schema Validation"
CONSTRAINT_VALIDATION = "Constraint Validation"

# Security and governance stages
PERMISSION_EXTRACTION = "Permission Extraction"
COMPLIANCE_SCANNING = "Compliance Scanning"
SENSITIVE_DATA_DETECTION = "Sensitive Data Detection"

# Platform-specific stages
SNOWFLAKE_SPECIFIC = "Snowflake Specific Processing"
BIGQUERY_SPECIFIC = "BigQuery Specific Processing"
DATABRICKS_SPECIFIC = "Databricks Specific Processing"
POSTGRES_SPECIFIC = "PostgreSQL Specific Processing"

# State management stages
STATE_INITIALIZATION = "State Initialization"
STATE_PERSISTENCE = "State Persistence"
STATE_RECOVERY = "State Recovery"
CHECKPOINT_CREATION = "Checkpoint Creation"

# Work unit processing stages
WORKUNIT_PROCESSING = "Work Unit Processing"
WORKUNIT_VALIDATION = "Work Unit Validation"
WORKUNIT_TRANSFORMATION = "Work Unit Transformation"
WORKUNIT_EMISSION = "Work Unit Emission"

# Performance and monitoring stages
PERFORMANCE_MONITORING = "Performance Monitoring"
RESOURCE_MONITORING = "Resource Monitoring"
ERROR_HANDLING = "Error Handling"
RETRY_LOGIC = "Retry Logic"

# Cleanup and finalization stages
CACHE_CLEANUP = "Cache Cleanup"
CONNECTION_CLEANUP = "Connection Cleanup"
FINALIZATION = "Finalization"


class IngestionStageCategory(Enum):
    """Categories for grouping ingestion stages."""
    INITIALIZATION = "initialization"
    DISCOVERY = "discovery"
    EXTRACTION = "extraction"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    PROCESSING = "processing"
    LINEAGE = "lineage"
    QUALITY = "quality"
    SECURITY = "security"
    CLEANUP = "cleanup"
    MONITORING = "monitoring"


class StageExecutionStatus(Enum):
    """Execution status for ingestion stages."""
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class IngestionStageDefinition:
    """Definition of an ingestion stage with metadata."""
    name: str
    category: IngestionStageCategory
    description: str
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False
    timeout_seconds: Optional[int] = None
    retry_attempts: int = 3
    parallel_execution: bool = False


# =============================================
# Stage Registry and Definitions
# =============================================

STAGE_REGISTRY: Dict[str, IngestionStageDefinition] = {
    # Core extraction stages
    METADATA_EXTRACTION: IngestionStageDefinition(
        name=METADATA_EXTRACTION,
        category=IngestionStageCategory.EXTRACTION,
        description="Extract basic metadata about datasets, schemas, and databases",
        timeout_seconds=1800,  # 30 minutes
    ),

    SCHEMA_EXTRACTION: IngestionStageDefinition(
        name=SCHEMA_EXTRACTION,
        category=IngestionStageCategory.EXTRACTION,
        description="Extract detailed schema information including columns and types",
        dependencies=[METADATA_EXTRACTION],
        timeout_seconds=1200,  # 20 minutes
    ),

    LINEAGE_EXTRACTION: IngestionStageDefinition(
        name=LINEAGE_EXTRACTION,
        category=IngestionStageCategory.LINEAGE,
        description="Extract data lineage relationships between datasets",
        dependencies=[SCHEMA_EXTRACTION],
        timeout_seconds=2400,  # 40 minutes
    ),

    EXTERNAL_TABLE_DDL_LINEAGE: IngestionStageDefinition(
        name=EXTERNAL_TABLE_DDL_LINEAGE,
        category=IngestionStageCategory.LINEAGE,
        description="Extract lineage for external tables from DDL definitions",
        dependencies=[METADATA_EXTRACTION],
        optional=True,
        timeout_seconds=600,  # 10 minutes
    ),

    VIEW_LINEAGE_EXTRACTION: IngestionStageDefinition(
        name=VIEW_LINEAGE_EXTRACTION,
        category=IngestionStageCategory.LINEAGE,
        description="Extract lineage relationships from view definitions",
        dependencies=[SCHEMA_EXTRACTION, VIEW_PARSING],
        timeout_seconds=1800,  # 30 minutes
    ),

    PROCEDURE_LINEAGE_EXTRACTION: IngestionStageDefinition(
        name=PROCEDURE_LINEAGE_EXTRACTION,
        category=IngestionStageCategory.LINEAGE,
        description="Extract lineage from stored procedure definitions",
        optional=True,
        timeout_seconds=1200,  # 20 minutes
    ),

    COLUMN_LINEAGE_EXTRACTION: IngestionStageDefinition(
        name=COLUMN_LINEAGE_EXTRACTION,
        category=IngestionStageCategory.LINEAGE,
        description="Extract fine-grained column-level lineage",
        dependencies=[LINEAGE_EXTRACTION],
        optional=True,
        timeout_seconds=3600,  # 1 hour
    ),

    # Query and view processing
    QUERIES_EXTRACTION: IngestionStageDefinition(
        name=QUERIES_EXTRACTION,
        category=IngestionStageCategory.EXTRACTION,
        description="Extract query logs and execution history",
        optional=True,
        timeout_seconds=2400,  # 40 minutes
    ),

    VIEW_PARSING: IngestionStageDefinition(
        name=VIEW_PARSING,
        category=IngestionStageCategory.PROCESSING,
        description="Parse view definitions for schema and lineage extraction",
        dependencies=[SCHEMA_EXTRACTION],
        timeout_seconds=900,  # 15 minutes
    ),

    # Data quality and profiling
    PROFILING: IngestionStageDefinition(
        name=PROFILING,
        category=IngestionStageCategory.QUALITY,
        description="Profile data for statistics and quality metrics",
        dependencies=[SCHEMA_EXTRACTION],
        optional=True,
        timeout_seconds=7200,  # 2 hours
        parallel_execution=True,
    ),

    DATA_QUALITY_ASSESSMENT: IngestionStageDefinition(
        name=DATA_QUALITY_ASSESSMENT,
        category=IngestionStageCategory.QUALITY,
        description="Assess data quality using predefined rules and metrics",
        dependencies=[PROFILING],
        optional=True,
        timeout_seconds=1800,  # 30 minutes
    ),

    # Security and classification
    CLASSIFICATION: IngestionStageDefinition(
        name=CLASSIFICATION,
        category=IngestionStageCategory.SECURITY,
        description="Classify data for PII and sensitive information",
        dependencies=[SCHEMA_EXTRACTION],
        optional=True,
        timeout_seconds=1800,  # 30 minutes
        parallel_execution=True,
    ),

    SENSITIVE_DATA_DETECTION: IngestionStageDefinition(
        name=SENSITIVE_DATA_DETECTION,
        category=IngestionStageCategory.SECURITY,
        description="Detect sensitive data patterns and PII",
        dependencies=[CLASSIFICATION],
        optional=True,
        timeout_seconds=1200,  # 20 minutes
    ),

    PERMISSION_EXTRACTION: IngestionStageDefinition(
        name=PERMISSION_EXTRACTION,
        category=IngestionStageCategory.SECURITY,
        description="Extract access permissions and security policies",
        dependencies=[METADATA_EXTRACTION],
        optional=True,
        timeout_seconds=600,  # 10 minutes
    ),

    # Processing stages
    WORKUNIT_PROCESSING: IngestionStageDefinition(
        name=WORKUNIT_PROCESSING,
        category=IngestionStageCategory.PROCESSING,
        description="Process and transform extracted metadata into work units",
        dependencies=[METADATA_EXTRACTION, SCHEMA_EXTRACTION],
        timeout_seconds=1200,  # 20 minutes
    ),

    WORKUNIT_VALIDATION: IngestionStageDefinition(
        name=WORKUNIT_VALIDATION,
        category=IngestionStageCategory.VALIDATION,
        description="Validate work units for correctness and completeness",
        dependencies=[WORKUNIT_PROCESSING],
        timeout_seconds=300,  # 5 minutes
    ),

    # State management
    STATE_INITIALIZATION: IngestionStageDefinition(
        name=STATE_INITIALIZATION,
        category=IngestionStageCategory.INITIALIZATION,
        description="Initialize ingestion state and prepare environment",
        timeout_seconds=300,  # 5 minutes
    ),

    STATE_PERSISTENCE: IngestionStageDefinition(
        name=STATE_PERSISTENCE,
        category=IngestionStageCategory.CLEANUP,
        description="Persist ingestion state and checkpoints",
        timeout_seconds=600,  # 10 minutes
    ),

    # Cleanup stages
    CACHE_CLEANUP: IngestionStageDefinition(
        name=CACHE_CLEANUP,
        category=IngestionStageCategory.CLEANUP,
        description="Clean up temporary caches and intermediate files",
        optional=True,
        timeout_seconds=300,  # 5 minutes
    ),

    CONNECTION_CLEANUP: IngestionStageDefinition(
        name=CONNECTION_CLEANUP,
        category=IngestionStageCategory.CLEANUP,
        description="Clean up database connections and resources",
        timeout_seconds=120,  # 2 minutes
    ),

    FINALIZATION: IngestionStageDefinition(
        name=FINALIZATION,
        category=IngestionStageCategory.CLEANUP,
        description="Finalize ingestion process and generate reports",
        timeout_seconds=300,  # 5 minutes
    ),
}


# =============================================
# Stage Execution Utilities
# =============================================

@dataclass
class StageExecutionContext:
    """Context for stage execution with timing and metrics."""
    stage_name: str
    status: StageExecutionStatus = StageExecutionStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        """Mark stage as started."""
        self.status = StageExecutionStatus.IN_PROGRESS
        self.start_time = datetime.now()
        logger.info(f"Started stage: {self.stage_name}")

    def complete(self) -> None:
        """Mark stage as completed."""
        self.status = StageExecutionStatus.COMPLETED
        self.end_time = datetime.now()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Completed stage: {self.stage_name} in {self.duration_seconds:.2f}s")

    def fail(self, error_message: str) -> None:
        """Mark stage as failed."""
        self.status = StageExecutionStatus.FAILED
        self.end_time = datetime.now()
        self.error_message = error_message
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        logger.error(f"Failed stage: {self.stage_name} - {error_message}")

    def skip(self, reason: str = "") -> None:
        """Mark stage as skipped."""
        self.status = StageExecutionStatus.SKIPPED
        self.end_time = datetime.now()
        self.error_message = f"Skipped: {reason}"
        logger.info(f"Skipped stage: {self.stage_name} - {reason}")


class IngestionStageManager:
    """Manager for ingestion stage execution and tracking."""

    def __init__(self, enabled_stages: Optional[List[str]] = None):
        """
        Initialize stage manager.

        Args:
            enabled_stages: Optional list of enabled stage names
        """
        self.enabled_stages = set(enabled_stages) if enabled_stages else set(STAGE_REGISTRY.keys())
        self.stage_contexts: Dict[str, StageExecutionContext] = {}
        self._lock = Lock()

        # Initialize contexts for enabled stages
        for stage_name in self.enabled_stages:
            if stage_name in STAGE_REGISTRY:
                self.stage_contexts[stage_name] = StageExecutionContext(stage_name)

    def is_stage_enabled(self, stage_name: str) -> bool:
        """Check if a stage is enabled."""
        return stage_name in self.enabled_stages

    def get_stage_definition(self, stage_name: str) -> Optional[IngestionStageDefinition]:
        """Get stage definition by name."""
        return STAGE_REGISTRY.get(stage_name)

    def get_stage_context(self, stage_name: str) -> Optional[StageExecutionContext]:
        """Get execution context for a stage."""
        return self.stage_contexts.get(stage_name)

    def start_stage(self, stage_name: str) -> bool:
        """
        Start execution of a stage.

        Args:
            stage_name: Name of stage to start

        Returns:
            True if stage was started successfully
        """
        with self._lock:
            if stage_name not in self.stage_contexts:
                logger.warning(f"Stage {stage_name} not found in contexts")
                return False

            context = self.stage_contexts[stage_name]
            if context.status != StageExecutionStatus.NOT_STARTED:
                logger.warning(f"Stage {stage_name} already started")
                return False

            context.start()
            return True

    def complete_stage(self, stage_name: str, metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Mark a stage as completed.

        Args:
            stage_name: Name of stage to complete
            metrics: Optional metrics to record

        Returns:
            True if stage was completed successfully
        """
        with self._lock:
            if stage_name not in self.stage_contexts:
                return False

            context = self.stage_contexts[stage_name]
            context.complete()

            if metrics:
                context.metrics.update(metrics)

            return True

    def fail_stage(self, stage_name: str, error_message: str) -> bool:
        """
        Mark a stage as failed.

        Args:
            stage_name: Name of stage that failed
            error_message: Error message describing failure

        Returns:
            True if stage failure was recorded
        """
        with self._lock:
            if stage_name not in self.stage_contexts:
                return False

            context = self.stage_contexts[stage_name]
            context.fail(error_message)
            return True

    def skip_stage(self, stage_name: str, reason: str = "") -> bool:
        """
        Mark a stage as skipped.

        Args:
            stage_name: Name of stage to skip
            reason: Reason for skipping

        Returns:
            True if stage was skipped successfully
        """
        with self._lock:
            if stage_name not in self.stage_contexts:
                return False

            context = self.stage_contexts[stage_name]
            context.skip(reason)
            return True

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of stage execution."""
        with self._lock:
            summary = {
                "total_stages": len(self.stage_contexts),
                "completed": 0,
                "failed": 0,
                "skipped": 0,
                "in_progress": 0,
                "not_started": 0,
                "total_duration": 0.0,
                "stages": {}
            }

            for stage_name, context in self.stage_contexts.items():
                summary["stages"][stage_name] = {
                    "status": context.status.value,
                    "duration_seconds": context.duration_seconds,
                    "error_message": context.error_message,
                    "retry_count": context.retry_count,
                    "metrics": context.metrics,
                }

                if context.status == StageExecutionStatus.COMPLETED:
                    summary["completed"] += 1
                    if context.duration_seconds:
                        summary["total_duration"] += context.duration_seconds
                elif context.status == StageExecutionStatus.FAILED:
                    summary["failed"] += 1
                elif context.status == StageExecutionStatus.SKIPPED:
                    summary["skipped"] += 1
                elif context.status == StageExecutionStatus.IN_PROGRESS:
                    summary["in_progress"] += 1
                else:
                    summary["not_started"] += 1

            return summary


# =============================================
# Utility Functions
# =============================================

def get_stage_dependencies(stage_name: str) -> List[str]:
    """Get dependencies for a stage."""
    definition = STAGE_REGISTRY.get(stage_name)
    return definition.dependencies if definition else []


def is_stage_optional(stage_name: str) -> bool:
    """Check if a stage is optional."""
    definition = STAGE_REGISTRY.get(stage_name)
    return definition.optional if definition else False


def get_stages_by_category(category: IngestionStageCategory) -> List[str]:
    """Get all stages in a category."""
    return [
        stage_name for stage_name, definition in STAGE_REGISTRY.items()
        if definition.category == category
    ]


def validate_stage_order(stage_names: List[str]) -> List[str]:
    """
    Validate and reorder stages based on dependencies.

    Args:
        stage_names: List of stage names to validate

    Returns:
        Reordered list of stages respecting dependencies
    """
    # Simple topological sort based on dependencies
    ordered_stages = []
    remaining_stages = set(stage_names)

    while remaining_stages:
        # Find stages with no remaining dependencies
        ready_stages = []
        for stage_name in remaining_stages:
            dependencies = get_stage_dependencies(stage_name)
            if not dependencies or all(dep in ordered_stages for dep in dependencies):
                ready_stages.append(stage_name)

        if not ready_stages:
            # Circular dependency or missing dependency
            logger.warning(f"Circular dependency detected in stages: {remaining_stages}")
            # Add remaining stages anyway
            ordered_stages.extend(list(remaining_stages))
            break

        # Add ready stages to ordered list
        for stage_name in ready_stages:
            ordered_stages.append(stage_name)
            remaining_stages.remove(stage_name)

    return ordered_stages


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
    'QUERIES_EXTRACTION',
    'VIEW_PARSING',

    # Extended lineage stages
    'EXTERNAL_TABLE_DDL_LINEAGE',
    'VIEW_LINEAGE_EXTRACTION',
    'PROCEDURE_LINEAGE_EXTRACTION',
    'COLUMN_LINEAGE_EXTRACTION',

    # Quality and validation stages
    'DATA_QUALITY_ASSESSMENT',
    'SCHEMA_VALIDATION',
    'CONSTRAINT_VALIDATION',

    # Security stages
    'PERMISSION_EXTRACTION',
    'COMPLIANCE_SCANNING',
    'SENSITIVE_DATA_DETECTION',

    # Platform-specific stages
    'SNOWFLAKE_SPECIFIC',
    'BIGQUERY_SPECIFIC',
    'DATABRICKS_SPECIFIC',
    'POSTGRES_SPECIFIC',

    # State management
    'STATE_INITIALIZATION',
    'STATE_PERSISTENCE',
    'STATE_RECOVERY',
    'CHECKPOINT_CREATION',

    # Processing stages
    'WORKUNIT_PROCESSING',
    'WORKUNIT_VALIDATION',
    'WORKUNIT_TRANSFORMATION',
    'WORKUNIT_EMISSION',

    # Monitoring stages
    'PERFORMANCE_MONITORING',
    'RESOURCE_MONITORING',
    'ERROR_HANDLING',
    'RETRY_LOGIC',

    # Cleanup stages
    'CACHE_CLEANUP',
    'CONNECTION_CLEANUP',
    'FINALIZATION',

    # Classes and enums
    'IngestionStageCategory',
    'StageExecutionStatus',
    'IngestionStageDefinition',
    'StageExecutionContext',
    'IngestionStageManager',
    'STAGE_REGISTRY',

    # Utility functions
    'get_stage_dependencies',
    'is_stage_optional',
    'get_stages_by_category',
    'validate_stage_order',
]
