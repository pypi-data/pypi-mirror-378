"""
DataGuild profiling state handler for managing data profiling operations.

This module provides comprehensive state management for data profiling workflows,
including tracking profiled datasets, managing profiling schedules, and handling
incremental profiling updates across DataGuild ingestion pipelines.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from dataguild.api.closeable import Closeable
from dataguild.source.state.checkpoint import (
    CheckpointStateBase,
    StatefulIngestionSourceBase,
)
from dataguild.configuration.time_window_config import BaseTimeWindowConfig
from dataguild.utilities.time import datetime_to_ts_millis, ts_millis_to_datetime

logger = logging.getLogger(__name__)


@dataclass
class ProfilingResult:
    """
    Represents the result of a data profiling operation.

    Contains comprehensive information about what was profiled,
    when it was profiled, and the quality of the profiling results.
    """

    dataset_urn: str  # URN of the profiled dataset
    profile_timestamp: datetime  # When profiling was performed
    rows_profiled: int  # Number of rows included in profiling
    columns_profiled: int  # Number of columns profiled
    profiling_duration_seconds: float  # Time taken for profiling
    profile_quality_score: float  # Quality score (0.0-1.0) of the profiling
    profile_version: str  # Version identifier for the profile

    # Statistical summaries
    null_percentage: Optional[float] = None  # Overall null percentage
    duplicate_percentage: Optional[float] = None  # Duplicate row percentage
    data_types_detected: Optional[Dict[str, int]] = None  # Column type distribution

    # Profiling metadata
    profiling_method: str = "FULL"  # FULL, SAMPLE, INCREMENTAL
    sample_size: Optional[int] = None  # If sampling was used
    profiling_errors: List[str] = field(default_factory=list)  # Any errors encountered

    def __post_init__(self):
        """Validate profiling result after initialization."""
        if self.profile_quality_score < 0.0 or self.profile_quality_score > 1.0:
            raise ValueError("profile_quality_score must be between 0.0 and 1.0")
        if self.rows_profiled < 0:
            raise ValueError("rows_profiled cannot be negative")
        if self.columns_profiled < 0:
            raise ValueError("columns_profiled cannot be negative")

    def is_high_quality(self, threshold: float = 0.8) -> bool:
        """Check if this profiling result meets quality standards."""
        return self.profile_quality_score >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "dataset_urn": self.dataset_urn,
            "profile_timestamp": self.profile_timestamp.isoformat(),
            "rows_profiled": self.rows_profiled,
            "columns_profiled": self.columns_profiled,
            "profiling_duration_seconds": self.profiling_duration_seconds,
            "profile_quality_score": self.profile_quality_score,
            "profile_version": self.profile_version,
            "null_percentage": self.null_percentage,
            "duplicate_percentage": self.duplicate_percentage,
            "data_types_detected": self.data_types_detected,
            "profiling_method": self.profiling_method,
            "sample_size": self.sample_size,
            "profiling_errors": self.profiling_errors,
        }


class ProfilingCheckpointState(CheckpointStateBase):
    """
    Checkpoint state for data profiling operations.

    Tracks which datasets have been profiled, when they were profiled,
    and manages incremental profiling schedules.
    """

    # Core profiling state
    profiled_datasets: Dict[str, ProfilingResult] = Field(default_factory=dict)

    # Profiling schedule management
    profiling_schedule: Dict[str, datetime] = Field(default_factory=dict)  # dataset -> next_profile_time
    profiling_frequency_days: int = Field(default=7)  # Default weekly profiling

    # Quality and performance tracking
    failed_profiles: Dict[str, List[str]] = Field(default_factory=dict)  # dataset -> error_messages
    profiling_performance_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Configuration
    min_profile_quality_threshold: float = Field(default=0.7)
    max_profiling_retries: int = Field(default=3)
    incremental_profiling_enabled: bool = Field(default=True)

    def add_profiling_result(self, result: ProfilingResult) -> None:
        """
        Add a profiling result to the state.

        Args:
            result: ProfilingResult to add to the state
        """
        self.profiled_datasets[result.dataset_urn] = result

        # Schedule next profiling
        next_profile_time = result.profile_timestamp + timedelta(days=self.profiling_frequency_days)
        self.profiling_schedule[result.dataset_urn] = next_profile_time

        # Clear any previous failures
        if result.dataset_urn in self.failed_profiles:
            del self.failed_profiles[result.dataset_urn]

        # Track performance
        self.profiling_performance_history.append({
            "dataset_urn": result.dataset_urn,
            "timestamp": result.profile_timestamp.isoformat(),
            "duration_seconds": result.profiling_duration_seconds,
            "rows_profiled": result.rows_profiled,
            "quality_score": result.profile_quality_score,
        })

        # Keep only recent performance history
        cutoff_time = datetime.now() - timedelta(days=30)
        self.profiling_performance_history = [
            perf for perf in self.profiling_performance_history
            if datetime.fromisoformat(perf["timestamp"]) > cutoff_time
        ]

        logger.info(
            f"Added profiling result for {result.dataset_urn} with quality score {result.profile_quality_score}")

    def is_dataset_profiled(self, dataset_urn: str) -> bool:
        """Check if a dataset has been profiled."""
        return dataset_urn in self.profiled_datasets

    def needs_profiling(self, dataset_urn: str, current_time: Optional[datetime] = None) -> bool:
        """
        Check if a dataset needs profiling.

        Args:
            dataset_urn: URN of the dataset to check
            current_time: Current time (defaults to now)

        Returns:
            True if the dataset needs profiling
        """
        if current_time is None:
            current_time = datetime.now()

        # Never profiled - needs profiling
        if not self.is_dataset_profiled(dataset_urn):
            return True

        # Check if scheduled for profiling
        if dataset_urn in self.profiling_schedule:
            next_profile_time = self.profiling_schedule[dataset_urn]
            if current_time >= next_profile_time:
                return True

        # Check if previous profiling was low quality
        result = self.profiled_datasets.get(dataset_urn)
        if result and not result.is_high_quality(self.min_profile_quality_threshold):
            return True

        # Check if there were failures that need retry
        if dataset_urn in self.failed_profiles:
            failure_count = len(self.failed_profiles[dataset_urn])
            if failure_count < self.max_profiling_retries:
                return True

        return False

    def add_profiling_failure(self, dataset_urn: str, error_message: str) -> None:
        """
        Record a profiling failure.

        Args:
            dataset_urn: URN of the dataset that failed profiling
            error_message: Error message from the failure
        """
        if dataset_urn not in self.failed_profiles:
            self.failed_profiles[dataset_urn] = []

        self.failed_profiles[dataset_urn].append(error_message)

        # If we've exceeded max retries, schedule for later
        if len(self.failed_profiles[dataset_urn]) >= self.max_profiling_retries:
            # Schedule retry after extended delay
            retry_time = datetime.now() + timedelta(days=self.profiling_frequency_days * 2)
            self.profiling_schedule[dataset_urn] = retry_time
            logger.warning(f"Max profiling retries exceeded for {dataset_urn}, scheduled retry for {retry_time}")

    def get_profiling_summary(self) -> Dict[str, Any]:
        """Get a summary of the profiling state."""
        total_datasets = len(self.profiled_datasets)
        high_quality_profiles = sum(
            1 for result in self.profiled_datasets.values()
            if result.is_high_quality(self.min_profile_quality_threshold)
        )
        failed_datasets = len(self.failed_profiles)

        return {
            "total_profiled_datasets": total_datasets,
            "high_quality_profiles": high_quality_profiles,
            "failed_datasets": failed_datasets,
            "quality_percentage": (high_quality_profiles / total_datasets * 100) if total_datasets > 0 else 0.0,
            "average_profiling_duration": self._calculate_average_duration(),
            "next_scheduled_profiles": len([
                urn for urn, next_time in self.profiling_schedule.items()
                if next_time <= datetime.now() + timedelta(days=1)
            ]),
        }

    def _calculate_average_duration(self) -> float:
        """Calculate average profiling duration from performance history."""
        if not self.profiling_performance_history:
            return 0.0

        total_duration = sum(perf["duration_seconds"] for perf in self.profiling_performance_history)
        return total_duration / len(self.profiling_performance_history)

    def cleanup_old_state(self, retention_days: int = 90) -> int:
        """
        Clean up old profiling state data.

        Args:
            retention_days: Number of days to retain profiling data

        Returns:
            Number of items cleaned up
        """
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        cleaned_count = 0

        # Clean up old profiling results
        to_remove = [
            urn for urn, result in self.profiled_datasets.items()
            if result.profile_timestamp < cutoff_time
        ]

        for urn in to_remove:
            del self.profiled_datasets[urn]
            if urn in self.profiling_schedule:
                del self.profiling_schedule[urn]
            if urn in self.failed_profiles:
                del self.failed_profiles[urn]
            cleaned_count += 1

        # Clean up old performance history
        old_performance_count = len(self.profiling_performance_history)
        self.profiling_performance_history = [
            perf for perf in self.profiling_performance_history
            if datetime.fromisoformat(perf["timestamp"]) > cutoff_time
        ]
        cleaned_count += old_performance_count - len(self.profiling_performance_history)

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old profiling state items")

        return cleaned_count


class ProfilingHandler(Closeable):
    """
    Comprehensive handler for managing data profiling state across DataGuild ingestion.

    This handler manages the complete lifecycle of data profiling operations:
    - Tracking which datasets have been profiled and when
    - Managing profiling schedules and frequencies
    - Handling profiling failures and retries
    - Providing intelligent profiling recommendations
    - Maintaining profiling quality metrics and performance history

    Examples:
        >>> handler = ProfilingHandler(
        ...     source=source,
        ...     config=config,
        ...     pipeline_name="snowflake_ingestion"
        ... )
        >>>
        >>> # Check if dataset needs profiling
        >>> if handler.should_profile_dataset("urn:li:dataset:(snowflake,db.table,PROD)"):
        ...     result = profile_dataset(dataset)
        ...     handler.record_profiling_result(result)
    """

    def __init__(
            self,
            source: StatefulIngestionSourceBase,
            config: BaseTimeWindowConfig,
            pipeline_name: Optional[str] = None,
            profiling_frequency_days: int = 7,
            min_quality_threshold: float = 0.7,
            max_retries: int = 3,
    ):
        """
        Initialize the profiling handler.

        Args:
            source: Source instance implementing stateful ingestion
            config: Time window configuration for profiling operations
            pipeline_name: Name of the ingestion pipeline
            profiling_frequency_days: How often to profile datasets (default 7 days)
            min_quality_threshold: Minimum acceptable quality score (0.0-1.0)
            max_retries: Maximum number of retry attempts for failed profiling
        """
        self.source = source
        self.config = config
        self.pipeline_name = pipeline_name

        # Get or create checkpoint state
        self.state = self._get_or_create_state()

        # Update configuration
        self.state.profiling_frequency_days = profiling_frequency_days
        self.state.min_profile_quality_threshold = min_quality_threshold
        self.state.max_profiling_retries = max_retries

        logger.info(
            f"Initialized ProfilingHandler for pipeline: {pipeline_name}. "
            f"Tracking {len(self.state.profiled_datasets)} profiled datasets."
        )

    def _get_or_create_state(self) -> ProfilingCheckpointState:
        """Get existing profiling state or create new state."""
        if hasattr(self.source, 'get_current_checkpoint'):
            try:
                existing_state = self.source.get_current_checkpoint(ProfilingCheckpointState)
                if existing_state:
                    logger.info("Retrieved existing profiling checkpoint state")
                    return existing_state
            except Exception as e:
                logger.warning(f"Failed to retrieve existing profiling state: {e}")

        # Create new state
        new_state = ProfilingCheckpointState()
        logger.info("Created new profiling checkpoint state")
        return new_state

    def should_profile_dataset(
            self,
            dataset_urn: str,
            force_profiling: bool = False,
            current_time: Optional[datetime] = None
    ) -> bool:
        """
        Determine if a dataset should be profiled.

        Args:
            dataset_urn: URN of the dataset to check
            force_profiling: Force profiling even if not scheduled
            current_time: Current time (defaults to now)

        Returns:
            True if the dataset should be profiled
        """
        if force_profiling:
            logger.info(f"Force profiling requested for {dataset_urn}")
            return True

        return self.state.needs_profiling(dataset_urn, current_time)

    def record_profiling_result(self, result: ProfilingResult) -> None:
        """
        Record the result of a profiling operation.

        Args:
            result: ProfilingResult containing profiling outcome
        """
        try:
            self.state.add_profiling_result(result)
            self._persist_state()

            logger.info(
                f"Recorded profiling result for {result.dataset_urn}: "
                f"{result.rows_profiled} rows, quality score {result.profile_quality_score:.3f}"
            )

        except Exception as e:
            logger.error(f"Failed to record profiling result: {e}")
            raise

    def record_profiling_failure(self, dataset_urn: str, error_message: str) -> None:
        """
        Record a profiling failure.

        Args:
            dataset_urn: URN of the dataset that failed profiling
            error_message: Error message describing the failure
        """
        try:
            self.state.add_profiling_failure(dataset_urn, error_message)
            self._persist_state()

            failure_count = len(self.state.failed_profiles.get(dataset_urn, []))
            logger.warning(
                f"Recorded profiling failure for {dataset_urn} (attempt {failure_count}): {error_message}"
            )

        except Exception as e:
            logger.error(f"Failed to record profiling failure: {e}")

    def get_datasets_needing_profiling(
            self,
            dataset_urns: List[str],
            max_datasets: Optional[int] = None
    ) -> List[str]:
        """
        Get list of datasets that need profiling.

        Args:
            dataset_urns: List of dataset URNs to check
            max_datasets: Maximum number of datasets to return

        Returns:
            List of dataset URNs that need profiling
        """
        needing_profiling = [
            urn for urn in dataset_urns
            if self.should_profile_dataset(urn)
        ]

        # Sort by priority (never profiled first, then by schedule)
        def priority_score(urn: str) -> tuple:
            if not self.state.is_dataset_profiled(urn):
                return (0, 0)  # Highest priority - never profiled

            # Get scheduled time (default to now if not scheduled)
            scheduled_time = self.state.profiling_schedule.get(urn, datetime.now())
            return (1, scheduled_time.timestamp())  # Lower priority, sort by schedule

        needing_profiling.sort(key=priority_score)

        if max_datasets:
            needing_profiling = needing_profiling[:max_datasets]

        logger.info(f"Found {len(needing_profiling)} datasets needing profiling")
        return needing_profiling

    def get_profiling_recommendations(self, dataset_urns: List[str]) -> Dict[str, Any]:
        """
        Get profiling recommendations for a set of datasets.

        Args:
            dataset_urns: List of dataset URNs to analyze

        Returns:
            Dictionary with profiling recommendations
        """
        recommendations = {
            "immediate_profiling": [],  # Never profiled or overdue
            "scheduled_profiling": [],  # Scheduled for profiling soon
            "retry_profiling": [],  # Previously failed, ready for retry
            "up_to_date": [],  # Recently profiled and high quality
            "low_quality": [],  # Profiled but low quality
        }

        current_time = datetime.now()

        for urn in dataset_urns:
            if not self.state.is_dataset_profiled(urn):
                recommendations["immediate_profiling"].append(urn)
            elif urn in self.state.failed_profiles:
                if len(self.state.failed_profiles[urn]) < self.state.max_profiling_retries:
                    recommendations["retry_profiling"].append(urn)
            elif self.state.needs_profiling(urn, current_time):
                if urn in self.state.profiling_schedule:
                    scheduled_time = self.state.profiling_schedule[urn]
                    if scheduled_time <= current_time:
                        recommendations["immediate_profiling"].append(urn)
                    else:
                        recommendations["scheduled_profiling"].append(urn)
                else:
                    recommendations["immediate_profiling"].append(urn)
            else:
                result = self.state.profiled_datasets.get(urn)
                if result and result.is_high_quality(self.state.min_profile_quality_threshold):
                    recommendations["up_to_date"].append(urn)
                else:
                    recommendations["low_quality"].append(urn)

        # Add summary statistics
        recommendations["summary"] = {
            "total_datasets": len(dataset_urns),
            "immediate_action_needed": len(recommendations["immediate_profiling"]) + len(
                recommendations["retry_profiling"]),
            "profiling_coverage": len([urn for urn in dataset_urns if self.state.is_dataset_profiled(urn)]) / len(
                dataset_urns) if dataset_urns else 0.0,
        }

        return recommendations

    def get_profiling_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for profiling operations."""
        if not self.state.profiling_performance_history:
            return {"message": "No profiling performance data available"}

        durations = [perf["duration_seconds"] for perf in self.state.profiling_performance_history]
        quality_scores = [perf["quality_score"] for perf in self.state.profiling_performance_history]
        row_counts = [perf["rows_profiled"] for perf in self.state.profiling_performance_history]

        return {
            "total_profiling_operations": len(self.state.profiling_performance_history),
            "average_duration_seconds": sum(durations) / len(durations),
            "median_duration_seconds": sorted(durations)[len(durations) // 2],
            "average_quality_score": sum(quality_scores) / len(quality_scores),
            "average_rows_profiled": sum(row_counts) / len(row_counts),
            "duration_percentiles": {
                "p50": sorted(durations)[int(len(durations) * 0.5)],
                "p90": sorted(durations)[int(len(durations) * 0.9)],
                "p95": sorted(durations)[int(len(durations) * 0.95)],
            }
        }

    def update_profiling_schedule(self, dataset_urn: str, next_profile_time: datetime) -> None:
        """
        Update the profiling schedule for a specific dataset.

        Args:
            dataset_urn: URN of the dataset
            next_profile_time: When the dataset should next be profiled
        """
        self.state.profiling_schedule[dataset_urn] = next_profile_time
        self._persist_state()
        logger.info(f"Updated profiling schedule for {dataset_urn}: {next_profile_time}")

    def _persist_state(self) -> None:
        """Persist the current profiling state."""
        try:
            if hasattr(self.source, 'set_current_checkpoint'):
                self.source.set_current_checkpoint(self.state)
                logger.debug("Persisted profiling checkpoint state")
            else:
                logger.warning("Source does not support checkpoint persistence")
        except Exception as e:
            logger.error(f"Failed to persist profiling checkpoint state: {e}")

    def cleanup_old_profiling_data(self, retention_days: int = 90) -> None:
        """
        Clean up old profiling data to prevent unlimited growth.

        Args:
            retention_days: Number of days to retain profiling data
        """
        removed_count = self.state.cleanup_old_state(retention_days)

        if removed_count > 0:
            self._persist_state()
            logger.info(f"Cleaned up {removed_count} old profiling data items")

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the profiling state."""
        base_summary = self.state.get_profiling_summary()

        return {
            **base_summary,
            "pipeline_name": self.pipeline_name,
            "profiling_frequency_days": self.state.profiling_frequency_days,
            "min_quality_threshold": self.state.min_profile_quality_threshold,
            "max_retries": self.state.max_profiling_retries,
            "incremental_profiling_enabled": self.state.incremental_profiling_enabled,
        }

    def reset_profiling_state(self, dataset_urn: Optional[str] = None) -> None:
        """
        Reset profiling state (use with caution in production).

        Args:
            dataset_urn: Specific dataset to reset, or None for all datasets
        """
        if dataset_urn:
            # Reset specific dataset
            if dataset_urn in self.state.profiled_datasets:
                del self.state.profiled_datasets[dataset_urn]
            if dataset_urn in self.state.profiling_schedule:
                del self.state.profiling_schedule[dataset_urn]
            if dataset_urn in self.state.failed_profiles:
                del self.state.failed_profiles[dataset_urn]

            logger.warning(f"Reset profiling state for dataset: {dataset_urn}")
        else:
            # Reset all profiling state
            logger.warning("Resetting ALL profiling state")
            self.state = ProfilingCheckpointState()

        self._persist_state()

    def close(self) -> None:
        """Close the profiling handler and clean up resources."""
        logger.info(f"Closing ProfilingHandler. Final state: {self.get_state_summary()}")


# Factory function for creating handlers
def create_profiling_handler(
        source: StatefulIngestionSourceBase,
        config: BaseTimeWindowConfig,
        pipeline_name: Optional[str] = None,
        **kwargs
) -> ProfilingHandler:
    """
    Factory function to create a ProfilingHandler.

    Args:
        source: Source instance
        config: Time window configuration
        pipeline_name: Pipeline name
        **kwargs: Additional configuration options

    Returns:
        Configured ProfilingHandler instance
    """
    return ProfilingHandler(
        source=source,
        config=config,
        pipeline_name=pipeline_name,
        **kwargs
    )


# Export all classes and functions
__all__ = [
    'ProfilingResult',
    'ProfilingCheckpointState',
    'ProfilingHandler',
    'create_profiling_handler',
]

# Example usage and testing
if __name__ == "__main__":
    print("=== DataGuild Profiling Handler Examples ===\n")

    # Example 1: Create a profiling result
    profiling_result = ProfilingResult(
        dataset_urn="urn:li:dataset:(snowflake,analytics.customer_data,PROD)",
        profile_timestamp=datetime.now(),
        rows_profiled=1000000,
        columns_profiled=25,
        profiling_duration_seconds=45.7,
        profile_quality_score=0.92,
        profile_version="v1.2.3",
        null_percentage=2.1,
        duplicate_percentage=0.5,
        data_types_detected={"STRING": 12, "INTEGER": 8, "FLOAT": 3, "BOOLEAN": 2},
        profiling_method="SAMPLE",
        sample_size=100000
    )

    print("Example 1: Profiling Result")
    print(f"Dataset: {profiling_result.dataset_urn}")
    print(f"Quality Score: {profiling_result.profile_quality_score}")
    print(f"Is High Quality: {profiling_result.is_high_quality()}")
    print(f"Rows Profiled: {profiling_result.rows_profiled:,}")
    print()

    # Example 2: Profiling state management
    state = ProfilingCheckpointState()
    state.add_profiling_result(profiling_result)

    print("Example 2: State Management")
    print(f"Dataset profiled: {state.is_dataset_profiled(profiling_result.dataset_urn)}")
    print(f"Needs profiling: {state.needs_profiling(profiling_result.dataset_urn)}")
    print(f"State summary: {state.get_profiling_summary()}")
    print()

    # Example 3: Profiling recommendations
    dataset_urns = [
        "urn:li:dataset:(snowflake,raw.users,PROD)",
        "urn:li:dataset:(snowflake,raw.orders,PROD)",
        "urn:li:dataset:(snowflake,analytics.customer_data,PROD)",
    ]


    # Mock handler for demonstration
    class MockSource:
        def get_current_checkpoint(self, cls):
            return state

        def set_current_checkpoint(self, state):
            pass


    mock_config = type('Config', (), {})()
    handler = ProfilingHandler(MockSource(), mock_config, "test_pipeline")
    handler.state = state

    recommendations = handler.get_profiling_recommendations(dataset_urns)

    print("Example 3: Profiling Recommendations")
    for category, datasets in recommendations.items():
        if category != "summary" and datasets:
            print(f"{category}: {len(datasets)} datasets")
    print(f"Summary: {recommendations['summary']}")
