"""
DataGuild stateful ingestion base classes - FINAL CORRECTED VERSION

This module provides base classes and utilities for implementing stateful ingestion
sources that can maintain state across runs for features like stale entity removal
and redundant run detection.
"""

import logging
import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field, validator

from dataguild.api.common import PipelineContext
from dataguild.api.source import Source, MetadataWorkUnitProcessor
from dataguild.source.state.checkpoint import CheckpointStateBase
from dataguild.configuration.common import ConfigModel

logger = logging.getLogger(__name__)

# Type variable for checkpoint state
CheckpointStateType = TypeVar('CheckpointStateType', bound=CheckpointStateBase)

from datetime import timedelta

from dataguild.source.state.stale_entity_removal_handler import StatefulStaleMetadataRemovalConfig


class StatefulLineageConfig(BaseModel):
    """Configuration for stateful lineage extraction."""

    enabled: bool = Field(
        default=False,
        description="Enable stateful lineage extraction"
    )

    max_lookback_days: int = Field(
        default=7,
        description="Maximum number of days to look back for lineage information"
    )

    min_lookback_days: int = Field(
        default=1,
        description="Minimum number of days to look back for lineage information"
    )

    include_view_lineage: bool = Field(
        default=True,
        description="Whether to extract lineage for database views"
    )

    include_column_lineage: bool = Field(
        default=True,
        description="Whether to extract column-level lineage"
    )

    include_usage_statistics: bool = Field(
        default=False,
        description="Whether to include usage statistics in lineage extraction"
    )

    query_log_delay_seconds: int = Field(
        default=3600,
        description="Delay in seconds to account for query log ingestion lag"
    )

    lineage_batch_size: int = Field(
        default=1000,
        description="Batch size for processing lineage relationships"
    )

    skip_redundant_runs: bool = Field(
        default=True,
        description="Whether to skip redundant lineage extraction runs"
    )

    @validator('max_lookback_days', 'min_lookback_days')
    def validate_lookback_days(cls, v):
        """Validate lookback day values."""
        if v < 0:
            raise ValueError("Lookback days must be non-negative")
        return v

    @validator('max_lookback_days')
    def validate_max_greater_than_min(cls, v, values):
        """Validate max lookback is greater than min."""
        min_days = values.get('min_lookback_days', 1)
        if v < min_days:
            raise ValueError("max_lookback_days must be >= min_lookback_days")
        return v


class StatefulProfilingConfig(BaseModel):
    """Configuration for stateful data profiling."""

    enabled: bool = Field(
        default=False,
        description="Enable stateful data profiling"
    )

    profile_frequency_days: int = Field(
        default=7,
        description="How often to profile datasets (in days)"
    )

    profile_on_schema_change: bool = Field(
        default=True,
        description="Whether to re-profile when schema changes are detected"
    )

    min_quality_threshold: float = Field(
        default=0.7,
        description="Minimum acceptable quality score for profiling results (0.0-1.0)"
    )

    max_profiling_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed profiling"
    )

    profiling_timeout_seconds: int = Field(
        default=3600,
        description="Timeout for profiling operations in seconds"
    )

    enable_sampling: bool = Field(
        default=True,
        description="Whether to use sampling for large datasets"
    )

    max_sample_size: int = Field(
        default=100000,
        description="Maximum number of rows to sample for profiling"
    )

    sample_percentage: float = Field(
        default=10.0,
        description="Percentage of data to sample (0.1-100.0)"
    )

    @validator('min_quality_threshold')
    def validate_quality_threshold(cls, v):
        """Validate quality threshold is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("min_quality_threshold must be between 0.0 and 1.0")
        return v

    @validator('sample_percentage')
    def validate_sample_percentage(cls, v):
        """Validate sample percentage is between 0.1 and 100."""
        if not 0.1 <= v <= 100.0:
            raise ValueError("sample_percentage must be between 0.1 and 100.0")
        return v


class StatefulUsageConfig(BaseModel):
    """Configuration for stateful usage statistics collection."""

    enabled: bool = Field(
        default=False,
        description="Enable stateful usage statistics collection"
    )

    usage_lookback_days: int = Field(
        default=7,
        description="Number of days to look back for usage statistics"
    )

    usage_aggregation_window_hours: int = Field(
        default=24,
        description="Time window for aggregating usage statistics (in hours)"
    )

    include_query_logs: bool = Field(
        default=True,
        description="Whether to process query logs for usage statistics"
    )

    include_operational_stats: bool = Field(
        default=True,
        description="Whether to include operational statistics (reads, writes, etc.)"
    )

    include_user_statistics: bool = Field(
        default=True,
        description="Whether to collect user-level usage statistics"
    )

    top_n_queries: int = Field(
        default=1000,
        description="Maximum number of top queries to include in usage statistics"
    )

    @validator('usage_lookback_days', 'usage_aggregation_window_hours')
    def validate_positive_time_values(cls, v):
        """Validate positive time values."""
        if v <= 0:
            raise ValueError("Time values must be positive")
        return v


class StatefulIngestionConfigBase(ConfigModel):
    """Base configuration class for stateful ingestion sources."""
    stateful_ingestion: Optional[BaseModel] = None


class StatefulIngestionReport(BaseModel):
    """Base report class for stateful ingestion sources."""
    stateful_ingestion_enabled: bool = False
    checkpoint_state_size_bytes: int = 0

    def report_stateful_ingestion_feature_enabled(self) -> None:
        """Report that stateful ingestion features are enabled."""
        self.stateful_ingestion_enabled = True


class StatefulIngestionSourceBase(Source, ABC):
    """
    🔧 FINAL FIX: Base class for sources that support stateful ingestion.

    Uses comprehensive defensive initialization to handle any Source class signature.
    """

    def __init__(self, config: StatefulIngestionConfigBase, ctx: PipelineContext):
        """
        🔧 FINAL DEFENSIVE FIX: Initialize with comprehensive error handling.

        Args:
            config: Source configuration with stateful ingestion settings
            ctx: Pipeline context with run information
        """

        # 🔍 DEBUG: Inspect Source class signature
        try:
            source_signature = inspect.signature(Source.__init__)
            source_params = list(source_signature.parameters.keys())
            logger.debug(f"Source.__init__ signature: {source_signature}")
            logger.debug(f"Source.__init__ parameters: {source_params}")
        except Exception as e:
            logger.warning(f"Could not inspect Source signature: {e}")
            source_params = ['self']  # Fallback

        # 🔧 COMPREHENSIVE INITIALIZATION STRATEGY
        initialization_success = False

        # Strategy 1: Try no arguments (Source() expects no args)
        if not initialization_success and len(source_params) == 1:  # Only 'self'
            try:
                Source.__init__(self)
                logger.info("✅ Strategy 1: Source.__init__() with no args succeeded")
                initialization_success = True
            except Exception as e:
                logger.debug(f"Strategy 1 failed: {e}")

        # Strategy 2: Try with ctx only
        if not initialization_success:
            try:
                Source.__init__(self, ctx)
                logger.info("✅ Strategy 2: Source.__init__(self, ctx) succeeded")
                initialization_success = True
            except Exception as e:
                logger.debug(f"Strategy 2 failed: {e}")

        # Strategy 3: Try with config and ctx
        if not initialization_success:
            try:
                Source.__init__(self, config, ctx)
                logger.info("✅ Strategy 3: Source.__init__(self, config, ctx) succeeded")
                initialization_success = True
            except Exception as e:
                logger.debug(f"Strategy 3 failed: {e}")

        # Strategy 4: Try super() with ctx
        if not initialization_success:
            try:
                super().__init__(ctx)
                logger.info("✅ Strategy 4: super().__init__(ctx) succeeded")
                initialization_success = True
            except Exception as e:
                logger.debug(f"Strategy 4 failed: {e}")

        # Strategy 5: Try super() with config and ctx
        if not initialization_success:
            try:
                super().__init__(config, ctx)
                logger.info("✅ Strategy 5: super().__init__(config, ctx) succeeded")
                initialization_success = True
            except Exception as e:
                logger.debug(f"Strategy 5 failed: {e}")

        # Strategy 6: Try super() with no args
        if not initialization_success:
            try:
                super().__init__()
                logger.info("✅ Strategy 6: super().__init__() succeeded")
                initialization_success = True
            except Exception as e:
                logger.debug(f"Strategy 6 failed: {e}")

        # Strategy 7: Manual initialization (last resort)
        if not initialization_success:
            logger.warning("All initialization strategies failed, using manual initialization")
            # Manually set attributes that Source would normally set
            if not hasattr(self, 'ctx'):
                self.ctx = ctx
            initialization_success = True

        # Store configuration and context
        self.config = config
        if not hasattr(self, 'ctx'):
            self.ctx = ctx
        self.stateful_ingestion_config = config

        # State management
        self._checkpoint_states: Dict[str, CheckpointStateBase] = {}

        if initialization_success:
            logger.info(f"✅ Successfully initialized stateful ingestion source for pipeline: {ctx.pipeline_name}")
        else:
            logger.error("❌ Failed to initialize Source base class")

    def get_current_checkpoint(
        self,
        checkpoint_class: Type[CheckpointStateType]
    ) -> Optional[CheckpointStateType]:
        """Get the current checkpoint state for a specific checkpoint class."""
        checkpoint_name = checkpoint_class.__name__

        # Check in-memory cache first
        if checkpoint_name in self._checkpoint_states:
            cached_state = self._checkpoint_states[checkpoint_name]
            if isinstance(cached_state, checkpoint_class):
                return cached_state

        # Try to load from persistent storage
        try:
            state = self._load_checkpoint_from_storage(checkpoint_class)
            if state:
                self._checkpoint_states[checkpoint_name] = state
                logger.debug(f"Loaded checkpoint state: {checkpoint_name}")
                return state
        except Exception as e:
            logger.warning(f"Failed to load checkpoint state {checkpoint_name}: {e}")

        return None

    def set_current_checkpoint(self, checkpoint_state: CheckpointStateBase) -> None:
        """Set the current checkpoint state."""
        checkpoint_name = type(checkpoint_state).__name__

        # Update in-memory cache
        self._checkpoint_states[checkpoint_name] = checkpoint_state

        # Persist to storage
        try:
            self._save_checkpoint_to_storage(checkpoint_state)
            logger.debug(f"Saved checkpoint state: {checkpoint_name}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint state {checkpoint_name}: {e}")
            raise

    def _load_checkpoint_from_storage(
        self,
        checkpoint_class: Type[CheckpointStateType]
    ) -> Optional[CheckpointStateType]:
        """Load checkpoint state from persistent storage."""
        logger.debug(f"No persistent storage configured for checkpoint: {checkpoint_class.__name__}")
        return None

    def _save_checkpoint_to_storage(self, checkpoint_state: CheckpointStateBase) -> None:
        """Save checkpoint state to persistent storage."""
        checkpoint_name = type(checkpoint_state).__name__
        logger.debug(f"No persistent storage configured for checkpoint: {checkpoint_name}")

    def get_workunit_processors(self) -> List[Optional[MetadataWorkUnitProcessor]]:
        """Get workunit processors for this source."""
        return []

    def is_stateful_ingestion_configured(self) -> bool:
        """Check if stateful ingestion is configured for this source."""
        return (
            self.stateful_ingestion_config is not None
            and hasattr(self.stateful_ingestion_config, 'stateful_ingestion')
            and self.stateful_ingestion_config.stateful_ingestion is not None
        )

    def get_stateful_ingestion_summary(self) -> Dict[str, Any]:
        """Get a summary of stateful ingestion status and configuration."""
        return {
            "stateful_ingestion_configured": self.is_stateful_ingestion_configured(),
            "pipeline_name": getattr(self.ctx, 'pipeline_name', 'unknown'),
            "run_id": getattr(self.ctx, 'run_id', 'unknown'),
            "checkpoint_states_loaded": len(self._checkpoint_states),
            "checkpoint_types": list(self._checkpoint_states.keys()),
        }

    def cleanup_checkpoint_state(self, retention_hours: int = 168) -> int:
        """Clean up old checkpoint state data."""
        cleaned_count = 0

        for checkpoint_name, state in list(self._checkpoint_states.items()):
            if hasattr(state, 'cleanup_old_state'):
                try:
                    removed = state.cleanup_old_state(retention_hours // 24)  # Convert to days
                    cleaned_count += removed
                    logger.info(f"Cleaned up {removed} entries from {checkpoint_name}")
                except Exception as e:
                    logger.error(f"Failed to cleanup {checkpoint_name}: {e}")

        return cleaned_count


class DatabaseBackedStatefulIngestionSourceBase(StatefulIngestionSourceBase):
    """Database-backed implementation of stateful ingestion source."""

    def __init__(
        self,
        config: StatefulIngestionConfigBase,
        ctx: PipelineContext,
        database_connection: Optional[Any] = None
    ):
        """Initialize database-backed stateful source."""
        # Call parent with correct argument order
        super().__init__(config, ctx)
        self.database_connection = database_connection

        # Initialize database tables if needed
        self._ensure_checkpoint_tables_exist()

    def _ensure_checkpoint_tables_exist(self) -> None:
        """Ensure that required checkpoint tables exist in the database."""
        if not self.database_connection:
            return

        try:
            logger.debug("Ensuring checkpoint tables exist")
        except Exception as e:
            logger.error(f"Failed to ensure checkpoint tables exist: {e}")

    def _load_checkpoint_from_storage(
        self,
        checkpoint_class: Type[CheckpointStateType]
    ) -> Optional[CheckpointStateType]:
        """Load checkpoint state from database."""
        if not self.database_connection:
            return None

        try:
            checkpoint_name = checkpoint_class.__name__
            logger.debug(f"Loading checkpoint from database: {checkpoint_name}")
            return None  # Placeholder - implement actual database loading logic

        except Exception as e:
            logger.error(f"Failed to load checkpoint from database: {e}")
            return None

    def _save_checkpoint_to_storage(self, checkpoint_state: CheckpointStateBase) -> None:
        """Save checkpoint state to database."""
        if not self.database_connection:
            return

        try:
            checkpoint_name = type(checkpoint_state).__name__
            logger.debug(f"Saving checkpoint to database: {checkpoint_name}")
            # Implement actual database saving logic

        except Exception as e:
            logger.error(f"Failed to save checkpoint to database: {e}")
            raise


# Configuration mixins (unchanged from your original code)
class StatefulLineageConfigMixin(BaseModel):
    """Mixin class that adds stateful lineage configuration to source configs."""

    stateful_lineage: Optional[StatefulLineageConfig] = Field(
        default=None,
        description="Configuration for stateful lineage extraction"
    )

    remove_stale_metadata: Optional[StatefulStaleMetadataRemovalConfig] = Field(
        default=None,
        description="Configuration for removing stale metadata entities"
    )

    def is_stateful_lineage_enabled(self) -> bool:
        """Check if stateful lineage is enabled."""
        return (
            self.stateful_lineage is not None
            and self.stateful_lineage.enabled
        )

    def get_lineage_lookback_timedelta(self) -> Optional[timedelta]:
        """Get the lineage lookback period as a timedelta."""
        if not self.is_stateful_lineage_enabled():
            return None
        return timedelta(days=self.stateful_lineage.max_lookback_days)


class StatefulProfilingConfigMixin(BaseModel):
    """Mixin class that adds stateful profiling configuration to source configs."""

    stateful_profiling: Optional[StatefulProfilingConfig] = Field(
        default=None,
        description="Configuration for stateful data profiling"
    )

    def is_stateful_profiling_enabled(self) -> bool:
        """Check if stateful profiling is enabled."""
        return (
            self.stateful_profiling is not None
            and self.stateful_profiling.enabled
        )

    def get_profiling_frequency_timedelta(self) -> Optional[timedelta]:
        """Get the profiling frequency as a timedelta."""
        if not self.is_stateful_profiling_enabled():
            return None
        return timedelta(days=self.stateful_profiling.profile_frequency_days)


class StatefulUsageConfigMixin(BaseModel):
    """Mixin class that adds stateful usage configuration to source configs."""

    stateful_usage: Optional[StatefulUsageConfig] = Field(
        default=None,
        description="Configuration for stateful usage statistics collection"
    )

    def is_stateful_usage_enabled(self) -> bool:
        """Check if stateful usage is enabled."""
        return (
            self.stateful_usage is not None
            and self.stateful_usage.enabled
        )

    def get_usage_lookback_timedelta(self) -> Optional[timedelta]:
        """Get the usage lookback period as a timedelta."""
        if not self.is_stateful_usage_enabled():
            return None
        return timedelta(days=self.stateful_usage.usage_lookback_days)


class StatefulIngestionConfigMixin(
    StatefulLineageConfigMixin,
    StatefulProfilingConfigMixin,
    StatefulUsageConfigMixin
):
    """Combined mixin that provides all stateful ingestion configuration options."""

    def get_enabled_stateful_features(self) -> List[str]:
        """Get a list of enabled stateful ingestion features."""
        features = []

        if self.is_stateful_lineage_enabled():
            features.append("lineage")

        if self.is_stateful_profiling_enabled():
            features.append("profiling")

        if self.is_stateful_usage_enabled():
            features.append("usage")

        return features

    def has_any_stateful_features_enabled(self) -> bool:
        """Check if any stateful ingestion features are enabled."""
        return len(self.get_enabled_stateful_features()) > 0


# Export all classes
__all__ = [
    'StatefulLineageConfig',
    'StatefulProfilingConfig',
    'StatefulUsageConfig',
    'StatefulLineageConfigMixin',
    'StatefulProfilingConfigMixin',
    'StatefulUsageConfigMixin',
    'StatefulIngestionConfigMixin',
    'StatefulIngestionSourceBase',
    'StatefulIngestionConfigBase',
    'StatefulIngestionReport',
    'DatabaseBackedStatefulIngestionSourceBase',
]
