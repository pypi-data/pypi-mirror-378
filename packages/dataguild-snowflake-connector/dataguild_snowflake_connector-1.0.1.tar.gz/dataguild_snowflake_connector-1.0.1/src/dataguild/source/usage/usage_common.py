"""
DataGuild usage configuration base class.

This module provides base configuration for usage tracking, monitoring,
and analytics across DataGuild sources and pipelines.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass

import pydantic
from pydantic import Field, validator

from dataguild.configuration.common import ConfigModel, MetaError

logger = logging.getLogger(__name__)


class UsageAggregationLevel(Enum):
    """Levels of usage data aggregation."""
    RAW = "raw"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class UsageMetricType(Enum):
    """Types of usage metrics to collect."""
    QUERIES = "queries"
    ROWS_READ = "rows_read"
    BYTES_READ = "bytes_read"
    EXECUTION_TIME = "execution_time"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    COST = "cost"
    USER_COUNT = "user_count"
    TABLE_ACCESS = "table_access"


@dataclass
class UsageWindow:
    """Time window for usage data collection."""
    start_time: datetime
    end_time: datetime

    def __post_init__(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")

    @property
    def duration(self) -> timedelta:
        """Get the duration of the usage window."""
        return self.end_time - self.start_time

    def contains(self, timestamp: datetime) -> bool:
        """Check if timestamp falls within this window."""
        return self.start_time <= timestamp <= self.end_time


class BaseUsageConfig(ConfigModel):
    """
    Base configuration class for usage tracking and analytics.

    Provides common configuration options for collecting, processing,
    and storing usage statistics across DataGuild sources.
    """

    # Basic usage collection settings
    enabled: bool = Field(
        default=True,
        description="Enable usage data collection"
    )

    collection_interval_minutes: int = Field(
        default=60,
        description="Interval between usage data collection in minutes",
        ge=1,
        le=1440  # Max 24 hours
    )

    # Time window configuration
    lookback_days: int = Field(
        default=7,
        description="Number of days to look back for usage data",
        ge=1,
        le=90
    )

    start_time: Optional[datetime] = Field(
        default=None,
        description="Explicit start time for usage collection (overrides lookback_days)"
    )

    end_time: Optional[datetime] = Field(
        default=None,
        description="Explicit end time for usage collection (defaults to now)"
    )

    # Aggregation settings
    aggregation_level: UsageAggregationLevel = Field(
        default=UsageAggregationLevel.DAILY,
        description="Level of aggregation for usage data"
    )

    metrics_to_collect: Set[UsageMetricType] = Field(
        default_factory=lambda: {
            UsageMetricType.QUERIES,
            UsageMetricType.ROWS_READ,
            UsageMetricType.EXECUTION_TIME
        },
        description="Set of usage metrics to collect"
    )

    # Filtering and sampling
    include_system_queries: bool = Field(
        default=False,
        description="Include system/internal queries in usage data"
    )

    include_failed_queries: bool = Field(
        default=True,
        description="Include failed queries in usage statistics"
    )

    min_query_duration_ms: Optional[int] = Field(
        default=None,
        description="Minimum query duration in milliseconds to include (filters out very fast queries)",
        ge=0
    )

    user_filter_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern to filter users (None includes all)"
    )

    database_filter_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern to filter databases (None includes all)"
    )

    # Resource limits and performance
    max_concurrent_requests: int = Field(
        default=5,
        description="Maximum concurrent usage API requests",
        ge=1,
        le=50
    )

    request_timeout_seconds: int = Field(
        default=300,
        description="Timeout for usage API requests in seconds",
        ge=30,
        le=3600
    )

    max_results_per_request: int = Field(
        default=10000,
        description="Maximum number of results per API request",
        ge=100,
        le=100000
    )

    # Caching and storage
    enable_caching: bool = Field(
        default=True,
        description="Enable caching of usage data"
    )

    cache_ttl_minutes: int = Field(
        default=60,
        description="Cache TTL in minutes",
        ge=1,
        le=1440
    )

    # Error handling and retries
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests",
        ge=0,
        le=10
    )

    retry_delay_seconds: int = Field(
        default=30,
        description="Delay between retries in seconds",
        ge=1,
        le=300
    )

    ignore_errors: bool = Field(
        default=False,
        description="Continue processing even if some usage data collection fails"
    )

    # Output and formatting
    include_metadata: bool = Field(
        default=True,
        description="Include metadata in usage reports"
    )

    format_timestamps: bool = Field(
        default=True,
        description="Format timestamps in human-readable format"
    )

    group_by_user: bool = Field(
        default=True,
        description="Group usage statistics by user"
    )

    group_by_database: bool = Field(
        default=True,
        description="Group usage statistics by database"
    )

    # Advanced settings
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom fields for usage data collection"
    )

    @validator("end_time")
    def validate_time_window(cls, v, values):
        """Validate that end_time is after start_time if both are provided."""
        start_time = values.get("start_time")
        if start_time and v and v <= start_time:
            raise ValueError("end_time must be after start_time")
        return v

    def get_usage_window(self) -> UsageWindow:
        """
        Get the time window for usage data collection.

        Returns:
            UsageWindow object defining the collection period
        """
        if self.start_time and self.end_time:
            return UsageWindow(self.start_time, self.end_time)

        end = self.end_time or datetime.now()
        start = self.start_time or (end - timedelta(days=self.lookback_days))

        return UsageWindow(start, end)

    def should_collect_metric(self, metric_type: UsageMetricType) -> bool:
        """
        Check if a specific metric should be collected.

        Args:
            metric_type: Type of metric to check

        Returns:
            True if metric should be collected
        """
        return metric_type in self.metrics_to_collect

    def get_collection_config(self) -> Dict[str, Any]:
        """
        Get configuration dictionary for usage collection.

        Returns:
            Dictionary of collection parameters
        """
        window = self.get_usage_window()

        return {
            "enabled": self.enabled,
            "start_time": window.start_time,
            "end_time": window.end_time,
            "aggregation_level": self.aggregation_level.value,
            "metrics": [metric.value for metric in self.metrics_to_collect],
            "include_system": self.include_system_queries,
            "include_failed": self.include_failed_queries,
            "max_concurrent": self.max_concurrent_requests,
            "timeout": self.request_timeout_seconds,
            "cache_enabled": self.enable_caching,
            "cache_ttl": self.cache_ttl_minutes * 60,  # Convert to seconds
        }

    @classmethod
    def create_minimal_config(cls) -> "BaseUsageConfig":
        """
        Create a minimal usage configuration for basic monitoring.

        Returns:
            BaseUsageConfig with minimal settings
        """
        return cls(
            lookback_days=1,
            aggregation_level=UsageAggregationLevel.HOURLY,
            metrics_to_collect={UsageMetricType.QUERIES, UsageMetricType.ROWS_READ},
            max_concurrent_requests=2,
            enable_caching=False
        )

    @classmethod
    def create_comprehensive_config(cls) -> "BaseUsageConfig":
        """
        Create a comprehensive usage configuration for detailed analytics.

        Returns:
            BaseUsageConfig with comprehensive settings
        """
        return cls(
            lookback_days=30,
            aggregation_level=UsageAggregationLevel.DAILY,
            metrics_to_collect=set(UsageMetricType),  # All metrics
            include_system_queries=True,
            include_failed_queries=True,
            max_concurrent_requests=10,
            enable_caching=True,
            cache_ttl_minutes=120,
            include_metadata=True,
            group_by_user=True,
            group_by_database=True
        )
