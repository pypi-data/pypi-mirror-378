"""
DataGuild profiling state handler and redundant run skip handler for stateful ingestion.

This module provides comprehensive state management for data profiling workflows
and functionality to prevent redundant runs of expensive ingestion operations
by tracking state and checking if a run for the same time period has already
been completed successfully.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field

from dataguild.api.closeable import Closeable
from dataguild.api.common import PipelineContext
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


class BaseUsageCheckpointState(CheckpointStateBase):
    """
    Base checkpoint state for usage extraction with redundant run detection.

    This state tracks completed time windows to prevent redundant processing
    of the same time periods in subsequent runs.
    """

    # Set of completed time windows (start_time_millis, end_time_millis)
    completed_windows: Set[Tuple[int, int]] = Field(default_factory=set)

    # Last successful run metadata
    last_successful_run: Optional[Dict[str, Any]] = Field(default=None)

    # Bucket duration used for time windows (in milliseconds)
    bucket_duration_ms: Optional[int] = Field(default=None)

    # Pipeline run metadata
    pipeline_name: Optional[str] = Field(default=None)
    run_id: Optional[str] = Field(default=None)

    def add_completed_window(
            self,
            start_time: datetime,
            end_time: datetime,
            bucket_duration: Optional[timedelta] = None
    ) -> None:
        """
        Add a completed time window to the state.

        Args:
            start_time: Start time of the completed window
            end_time: End time of the completed window
            bucket_duration: Optional bucket duration for the window
        """
        start_millis = datetime_to_ts_millis(start_time)
        end_millis = datetime_to_ts_millis(end_time)

        self.completed_windows.add((start_millis, end_millis))

        if bucket_duration:
            self.bucket_duration_ms = int(bucket_duration.total_seconds() * 1000)

        logger.debug(f"Added completed window: {start_time} to {end_time}")

    def is_window_completed(self, start_time: datetime, end_time: datetime) -> bool:
        """
        Check if a time window has already been completed.

        Args:
            start_time: Start time of the window to check
            end_time: End time of the window to check

        Returns:
            True if the window has been completed, False otherwise
        """
        start_millis = datetime_to_ts_millis(start_time)
        end_millis = datetime_to_ts_millis(end_time)

        return (start_millis, end_millis) in self.completed_windows

    def get_completed_windows(self) -> List[Tuple[datetime, datetime]]:
        """
        Get all completed windows as datetime tuples.

        Returns:
            List of (start_time, end_time) tuples for completed windows
        """
        return [
            (ts_millis_to_datetime(start_ms), ts_millis_to_datetime(end_ms))
            for start_ms, end_ms in self.completed_windows
        ]

    def cleanup_old_windows(self, cutoff_time: datetime) -> int:
        """
        Remove completed windows older than the cutoff time.

        Args:
            cutoff_time: Remove windows ending before this time

        Returns:
            Number of windows removed
        """
        cutoff_millis = datetime_to_ts_millis(cutoff_time)
        old_windows = {
            (start_ms, end_ms) for start_ms, end_ms in self.completed_windows
            if end_ms < cutoff_millis
        }

        self.completed_windows -= old_windows
        removed_count = len(old_windows)

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old completed windows")

        return removed_count


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

        logger.info(f"Added profiling result for {result.dataset_urn} with quality score {result.profile_quality_score}")

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


class RedundantLineageRunSkipHandler:
    """
    Handler for skipping redundant lineage extraction runs.

    This handler tracks completed time windows and prevents redundant processing
    of the same time periods. It's designed for expensive operations like
    lineage and usage statistics extraction that should not be repeated unnecessarily.
    """

    def __init__(
            self,
            source: StatefulIngestionSourceBase,
            config: BaseTimeWindowConfig,
            pipeline_name: Optional[str] = None,
            run_id: Optional[str] = None,
            state_provider: Optional[Any] = None,
    ):
        """
        Initialize the redundant run skip handler.

        Args:
            source: Source instance implementing stateful ingestion
            config: Time window configuration
            pipeline_name: Name of the ingestion pipeline
            run_id: Unique identifier for this run
            state_provider: Optional custom state provider
        """
        self.source = source
        self.config = config
        self.pipeline_name = pipeline_name
        self.run_id = run_id
        self.state_provider = state_provider

        # Initialize or retrieve checkpoint state
        self.state = self._get_or_create_state()

        logger.info(
            f"Initialized RedundantLineageRunSkipHandler for pipeline: {pipeline_name}, "
            f"run: {run_id}"
        )

    def _get_or_create_state(self) -> BaseUsageCheckpointState:
        """Get existing state or create new state."""
        if hasattr(self.source, 'get_current_checkpoint'):
            try:
                existing_state = self.source.get_current_checkpoint(
                    BaseUsageCheckpointState
                )
                if existing_state:
                    logger.debug("Retrieved existing checkpoint state")
                    return existing_state
            except Exception as e:
                logger.warning(f"Failed to retrieve existing state: {e}")

        # Create new state
        new_state = BaseUsageCheckpointState(
            pipeline_name=self.pipeline_name,
            run_id=self.run_id
        )
        logger.debug("Created new checkpoint state")
        return new_state

    def should_skip_this_run(
            self,
            cur_start_time: datetime,
            cur_end_time: datetime,
            force_refresh: bool = False
    ) -> bool:
        """
        Determine if the current run should be skipped.

        Args:
            cur_start_time: Start time of the current run
            cur_end_time: End time of the current run
            force_refresh: Force refresh even if window was completed

        Returns:
            True if the run should be skipped, False otherwise
        """
        if force_refresh:
            logger.info("Force refresh requested, not skipping run")
            return False

        # Check if this exact time window has been completed
        if self.state.is_window_completed(cur_start_time, cur_end_time):
            logger.info(
                f"Skipping redundant run for time window: {cur_start_time} to {cur_end_time}"
            )
            return True

        # Check for overlapping completed windows
        overlapping = self._find_overlapping_windows(cur_start_time, cur_end_time)
        if overlapping:
            logger.info(
                f"Skipping run due to {len(overlapping)} overlapping completed windows"
            )
            return True

        logger.info(f"Proceeding with run for time window: {cur_start_time} to {cur_end_time}")
        return False

    def suggest_run_time_window(
            self,
            requested_start: datetime,
            requested_end: datetime
    ) -> Tuple[datetime, datetime]:
        """
        Suggest an optimal time window for the run, avoiding completed windows.

        Args:
            requested_start: Requested start time
            requested_end: Requested end time

        Returns:
            Tuple of (suggested_start_time, suggested_end_time)
        """
        # If no overlap with completed windows, use requested window
        if not self._find_overlapping_windows(requested_start, requested_end):
            return requested_start, requested_end

        # Find the next available window after completed ones
        completed_windows = self.state.get_completed_windows()
        if not completed_windows:
            return requested_start, requested_end

        # Sort completed windows by end time
        sorted_windows = sorted(completed_windows, key=lambda w: w[1])

        # Find gap after the latest completed window
        latest_end = sorted_windows[-1][1]
        if latest_end >= requested_start:
            suggested_start = latest_end + timedelta(seconds=1)
            duration = requested_end - requested_start
            suggested_end = suggested_start + duration

            logger.info(
                f"Suggesting adjusted time window: {suggested_start} to {suggested_end}"
            )
            return suggested_start, suggested_end

        return requested_start, requested_end

    def _find_overlapping_windows(
            self,
            start_time: datetime,
            end_time: datetime
    ) -> List[Tuple[datetime, datetime]]:
        """
        Find completed windows that overlap with the given time range.

        Args:
            start_time: Start time to check
            end_time: End time to check

        Returns:
            List of overlapping completed windows
        """
        overlapping = []

        for completed_start, completed_end in self.state.get_completed_windows():
            # Check for overlap: windows overlap if start1 < end2 and start2 < end1
            if start_time < completed_end and completed_start < end_time:
                overlapping.append((completed_start, completed_end))

        return overlapping

    def update_state(
            self,
            start_time: datetime,
            end_time: datetime,
            bucket_duration: Optional[timedelta] = None,
            run_status: str = "completed"
    ) -> None:
        """
        Update the state with information about the current run.

        Args:
            start_time: Start time of the completed run
            end_time: End time of the completed run
            bucket_duration: Bucket duration used in the run
            run_status: Status of the run (completed, failed, etc.)
        """
        if run_status == "completed":
            # Add completed window to state
            self.state.add_completed_window(start_time, end_time, bucket_duration)

            # Update last successful run metadata
            self.state.last_successful_run = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "run_id": self.run_id,
                "pipeline_name": self.pipeline_name,
                "timestamp": datetime.now().isoformat(),
                "bucket_duration_ms": int(bucket_duration.total_seconds() * 1000) if bucket_duration else None
            }

            logger.info(f"Updated state with completed run: {start_time} to {end_time}")
        else:
            logger.warning(f"Run completed with status: {run_status}")

        # Persist state
        self._persist_state()

    def report_current_run_status(self, step: str, success: bool) -> None:
        """
        Report the status of the current run step.

        Args:
            step: Name of the step being reported
            success: Whether the step was successful
        """
        if not hasattr(self.state, 'run_steps'):
            self.state.run_steps = {}

        self.state.run_steps[step] = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "run_id": self.run_id
        }

        logger.debug(f"Reported step status - {step}: {'success' if success else 'failure'}")

    def _persist_state(self) -> None:
        """Persist the current state."""
        try:
            if hasattr(self.source, 'set_current_checkpoint'):
                self.source.set_current_checkpoint(self.state)
                logger.debug("Persisted checkpoint state")
            else:
                logger.warning("Source does not support checkpoint persistence")
        except Exception as e:
            logger.error(f"Failed to persist checkpoint state: {e}")

    def cleanup_old_state(self, retention_days: int = 30) -> None:
        """
        Clean up old state data to prevent unlimited growth.

        Args:
            retention_days: Number of days to retain completed windows
        """
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        removed_count = self.state.cleanup_old_windows(cutoff_time)

        if removed_count > 0:
            self._persist_state()
            logger.info(f"Cleaned up {removed_count} old state entries")

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state.

        Returns:
            Dictionary containing state summary information
        """
        completed_windows = self.state.get_completed_windows()

        return {
            "pipeline_name": self.state.pipeline_name,
            "run_id": self.state.run_id,
            "completed_windows_count": len(completed_windows),
            "earliest_window": min(completed_windows)[0].isoformat() if completed_windows else None,
            "latest_window": max(completed_windows, key=lambda w: w[1])[1].isoformat() if completed_windows else None,
            "last_successful_run": self.state.last_successful_run,
            "bucket_duration_ms": self.state.bucket_duration_ms,
        }

    def reset_state(self) -> None:
        """Reset the state (use with caution in production)."""
        logger.warning("Resetting redundant run skip handler state")
        self.state = BaseUsageCheckpointState(
            pipeline_name=self.pipeline_name,
            run_id=self.run_id
        )
        self._persist_state()


class RedundantUsageRunSkipHandler:
    """
    Handler for skipping redundant usage statistics extraction runs.

    This handler specifically tracks completed time windows for usage statistics
    processing and prevents redundant processing of the same time periods.
    It's optimized for usage-specific operations like query log analysis,
    user activity tracking, and dataset usage metrics extraction.

    Examples:
        >>> handler = RedundantUsageRunSkipHandler(
        ...     source=source,
        ...     config=config,
        ...     pipeline_name="snowflake_usage",
        ...     run_id="usage_123"
        ... )
        >>> if not handler.should_skip_this_run(start_time, end_time):
        ...     # Process usage statistics extraction
        ...     handler.update_state(start_time, end_time, "completed")
    """

    def __init__(
            self,
            source: StatefulIngestionSourceBase,
            config: BaseTimeWindowConfig,
            pipeline_name: Optional[str] = None,
            run_id: Optional[str] = None,
            state_provider: Optional[Any] = None,
    ):
        """
        Initialize the redundant usage run skip handler.

        Args:
            source: Source instance implementing stateful ingestion
            config: Time window configuration for usage extraction
            pipeline_name: Name of the usage ingestion pipeline
            run_id: Unique identifier for this usage run
            state_provider: Optional custom state provider
        """
        self.source = source
        self.config = config
        self.pipeline_name = pipeline_name
        self.run_id = run_id
        self.state_provider = state_provider

        # Initialize or retrieve checkpoint state for usage operations
        self.state = self._get_or_create_usage_state()

        logger.info(
            f"Initialized RedundantUsageRunSkipHandler for pipeline: {pipeline_name}, "
            f"run: {run_id}"
        )

    def _get_or_create_usage_state(self) -> BaseUsageCheckpointState:
        """Get existing usage state or create new state."""
        if hasattr(self.source, 'get_current_checkpoint'):
            try:
                # Try to get existing usage checkpoint state
                existing_state = self.source.get_current_checkpoint(
                    BaseUsageCheckpointState
                )
                if existing_state and existing_state.pipeline_name == self.pipeline_name:
                    logger.debug("Retrieved existing usage checkpoint state")
                    return existing_state
            except Exception as e:
                logger.warning(f"Failed to retrieve existing usage state: {e}")

        # Create new usage-specific state
        new_state = BaseUsageCheckpointState(
            pipeline_name=self.pipeline_name,
            run_id=self.run_id
        )
        logger.debug("Created new usage checkpoint state")
        return new_state

    def should_skip_this_run(
            self,
            cur_start_time: datetime,
            cur_end_time: datetime,
            force_refresh: bool = False
    ) -> bool:
        """
        Determine if the current usage run should be skipped.

        Args:
            cur_start_time: Start time of the current usage run
            cur_end_time: End time of the current usage run
            force_refresh: Force refresh even if usage window was completed

        Returns:
            True if the usage run should be skipped, False otherwise
        """
        if force_refresh:
            logger.info("Force refresh requested for usage extraction, not skipping run")
            return False

        # Check if this exact usage time window has been completed
        if self.state.is_window_completed(cur_start_time, cur_end_time):
            logger.info(
                f"Skipping redundant usage run for time window: {cur_start_time} to {cur_end_time}"
            )
            return True

        # Check for overlapping completed usage windows
        overlapping = self._find_overlapping_windows(cur_start_time, cur_end_time)
        if overlapping:
            logger.info(
                f"Skipping usage run due to {len(overlapping)} overlapping completed windows"
            )
            return True

        logger.info(f"Proceeding with usage run for time window: {cur_start_time} to {cur_end_time}")
        return False

    def suggest_run_time_window(
            self,
            requested_start: datetime,
            requested_end: datetime
    ) -> Tuple[datetime, datetime]:
        """
        Suggest an optimal time window for usage extraction, avoiding completed windows.

        Args:
            requested_start: Requested start time for usage extraction
            requested_end: Requested end time for usage extraction

        Returns:
            Tuple of (suggested_start_time, suggested_end_time) for usage processing
        """
        # If no overlap with completed usage windows, use requested window
        if not self._find_overlapping_windows(requested_start, requested_end):
            return requested_start, requested_end

        # Find the next available window after completed usage processing
        completed_windows = self.state.get_completed_windows()
        if not completed_windows:
            return requested_start, requested_end

        # Sort completed usage windows by end time
        sorted_windows = sorted(completed_windows, key=lambda w: w[1])

        # Find gap after the latest completed usage window
        latest_end = sorted_windows[-1][1]
        if latest_end >= requested_start:
            suggested_start = latest_end + timedelta(seconds=1)
            duration = requested_end - requested_start
            suggested_end = suggested_start + duration

            logger.info(
                f"Suggesting adjusted usage time window: {suggested_start} to {suggested_end}"
            )
            return suggested_start, suggested_end

        return requested_start, requested_end

    def _find_overlapping_windows(
            self,
            start_time: datetime,
            end_time: datetime
    ) -> List[Tuple[datetime, datetime]]:
        """
        Find completed usage windows that overlap with the given time range.

        Args:
            start_time: Start time to check for usage overlap
            end_time: End time to check for usage overlap

        Returns:
            List of overlapping completed usage windows
        """
        overlapping = []

        for completed_start, completed_end in self.state.get_completed_windows():
            # Check for overlap: windows overlap if start1 < end2 and start2 < end1
            if start_time < completed_end and completed_start < end_time:
                overlapping.append((completed_start, completed_end))

        return overlapping

    def update_state(
            self,
            start_time: datetime,
            end_time: datetime,
            bucket_duration: Optional[timedelta] = None,
            run_status: str = "completed"
    ) -> None:
        """
        Update the usage state with information about the current run.

        Args:
            start_time: Start time of the completed usage run
            end_time: End time of the completed usage run
            bucket_duration: Bucket duration used in the usage run
            run_status: Status of the usage run (completed, failed, etc.)
        """
        if run_status == "completed":
            # Add completed usage window to state
            self.state.add_completed_window(start_time, end_time, bucket_duration)

            # Update last successful usage run metadata
            self.state.last_successful_run = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "run_id": self.run_id,
                "pipeline_name": self.pipeline_name,
                "timestamp": datetime.now().isoformat(),
                "bucket_duration_ms": int(bucket_duration.total_seconds() * 1000) if bucket_duration else None,
                "run_type": "usage_extraction"
            }

            logger.info(f"Updated usage state with completed run: {start_time} to {end_time}")
        else:
            logger.warning(f"Usage run completed with status: {run_status}")

        # Persist usage state
        self._persist_state()

    def report_current_run_status(self, step: str, success: bool) -> None:
        """
        Report the status of the current usage run step.

        Args:
            step: Name of the usage step being reported
            success: Whether the usage step was successful
        """
        if not hasattr(self.state, 'run_steps'):
            self.state.run_steps = {}

        self.state.run_steps[step] = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "run_id": self.run_id,
            "step_type": "usage_extraction"
        }

        logger.debug(f"Reported usage step status - {step}: {'success' if success else 'failure'}")

    def _persist_state(self) -> None:
        """Persist the current usage state."""
        try:
            if hasattr(self.source, 'set_current_checkpoint'):
                self.source.set_current_checkpoint(self.state)
                logger.debug("Persisted usage checkpoint state")
            else:
                logger.warning("Source does not support usage checkpoint persistence")
        except Exception as e:
            logger.error(f"Failed to persist usage checkpoint state: {e}")

    def cleanup_old_state(self, retention_days: int = 30) -> None:
        """
        Clean up old usage state data to prevent unlimited growth.

        Args:
            retention_days: Number of days to retain completed usage windows
        """
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        removed_count = self.state.cleanup_old_windows(cutoff_time)

        if removed_count > 0:
            self._persist_state()
            logger.info(f"Cleaned up {removed_count} old usage state entries")

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current usage state.

        Returns:
            Dictionary containing usage state summary information
        """
        completed_windows = self.state.get_completed_windows()

        return {
            "pipeline_name": self.state.pipeline_name,
            "run_id": self.state.run_id,
            "pipeline_type": "usage_extraction",
            "completed_windows_count": len(completed_windows),
            "earliest_window": min(completed_windows)[0].isoformat() if completed_windows else None,
            "latest_window": max(completed_windows, key=lambda w: w[1])[1].isoformat() if completed_windows else None,
            "last_successful_run": self.state.last_successful_run,
            "bucket_duration_ms": self.state.bucket_duration_ms,
        }

    def reset_state(self) -> None:
        """Reset the usage state (use with caution in production)."""
        logger.warning("Resetting redundant usage run skip handler state")
        self.state = BaseUsageCheckpointState(
            pipeline_name=self.pipeline_name,
            run_id=self.run_id
        )
        self._persist_state()


class ProfilingHandler(Closeable):
    """
    Comprehensive handler for managing data profiling state across DataGuild ingestion.

    This handler manages the complete lifecycle of data profiling operations:
    - Tracking which datasets have been profiled and when
    - Managing profiling schedules and frequencies
    - Handling profiling failures and retries
    - Providing intelligent profiling recommendations
    - Maintaining profiling quality metrics and performance history
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
            "retry_profiling": [],     # Previously failed, ready for retry
            "up_to_date": [],          # Recently profiled and high quality
            "low_quality": [],         # Profiled but low quality
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
            "immediate_action_needed": len(recommendations["immediate_profiling"]) + len(recommendations["retry_profiling"]),
            "profiling_coverage": len([urn for urn in dataset_urns if self.state.is_dataset_profiled(urn)]) / len(dataset_urns) if dataset_urns else 0.0,
        }

        return recommendations

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

    def close(self) -> None:
        """Close the profiling handler and clean up resources."""
        logger.info(f"Closing ProfilingHandler. Final state: {self.get_state_summary()}")


# Factory functions for creating handlers
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


def create_redundant_lineage_run_skip_handler(
        source: StatefulIngestionSourceBase,
        config: BaseTimeWindowConfig,
        pipeline_name: Optional[str] = None,
        run_id: Optional[str] = None,
) -> RedundantLineageRunSkipHandler:
    """
    Factory function to create a RedundantLineageRunSkipHandler.

    Args:
        source: Source instance
        config: Time window configuration
        pipeline_name: Pipeline name
        run_id: Run ID

    Returns:
        Configured RedundantLineageRunSkipHandler instance
    """
    return RedundantLineageRunSkipHandler(
        source=source,
        config=config,
        pipeline_name=pipeline_name,
        run_id=run_id,
    )


def create_redundant_usage_run_skip_handler(
        source: StatefulIngestionSourceBase,
        config: BaseTimeWindowConfig,
        pipeline_name: Optional[str] = None,
        run_id: Optional[str] = None,
) -> RedundantUsageRunSkipHandler:
    """
    Factory function to create a RedundantUsageRunSkipHandler.

    Args:
        source: Source instance
        config: Time window configuration for usage extraction
        pipeline_name: Pipeline name for usage processing
        run_id: Run ID for usage extraction

    Returns:
        Configured RedundantUsageRunSkipHandler instance
    """
    return RedundantUsageRunSkipHandler(
        source=source,
        config=config,
        pipeline_name=pipeline_name,
        run_id=run_id,
    )


# Export all classes and functions
__all__ = [
    'ProfilingResult',
    'ProfilingCheckpointState',
    'ProfilingHandler',
    'BaseUsageCheckpointState',
    'RedundantLineageRunSkipHandler',
    'RedundantUsageRunSkipHandler',
    'create_profiling_handler',
    'create_redundant_lineage_run_skip_handler',
    'create_redundant_usage_run_skip_handler',
]
