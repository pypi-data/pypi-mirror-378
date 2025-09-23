"""
DataGuild time window reporting utilities.

This module provides time-based reporting capabilities with configurable
time windows and aggregation functions for data analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class TimeWindowUnit(str, Enum):
    """Time window unit types."""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class AggregationType(str, Enum):
    """Types of aggregation for time window data."""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    FIRST = "first"
    LAST = "last"


@dataclass
class TimeWindowDataPoint:
    """Data point within a time window."""
    timestamp: datetime
    value: Union[int, float, str, Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "metadata": self.metadata,
        }


class BaseTimeWindowReport(BaseModel):
    """
    Base class for time window-based reporting.

    Provides functionality for collecting, aggregating, and analyzing
    data within configurable time windows.
    """

    report_name: str = Field(description="Name of the time window report")
    start_time: datetime = Field(description="Start time of the reporting window")
    end_time: datetime = Field(description="End time of the reporting window")
    window_size: int = Field(description="Size of individual time windows", gt=0)
    window_unit: TimeWindowUnit = Field(description="Unit for time window size")

    # Data storage
    data_points: List[TimeWindowDataPoint] = Field(
        default_factory=list,
        description="Raw data points"
    )
    aggregated_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Aggregated data by time window"
    )

    # Configuration
    max_data_points: int = Field(
        default=10000,
        description="Maximum data points to store",
        gt=0
    )
    auto_aggregate: bool = Field(
        default=True,
        description="Automatically aggregate data as points are added"
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    @validator('end_time')
    def validate_end_time(cls, v, values):
        """Validate that end_time is after start_time."""
        start_time = values.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('end_time must be after start_time')
        return v

    def get_window_duration(self) -> timedelta:
        """Get duration of individual time windows."""
        unit_mapping = {
            TimeWindowUnit.SECOND: timedelta(seconds=self.window_size),
            TimeWindowUnit.MINUTE: timedelta(minutes=self.window_size),
            TimeWindowUnit.HOUR: timedelta(hours=self.window_size),
            TimeWindowUnit.DAY: timedelta(days=self.window_size),
            TimeWindowUnit.WEEK: timedelta(weeks=self.window_size),
            TimeWindowUnit.MONTH: timedelta(days=self.window_size * 30),  # Approximate
        }
        return unit_mapping.get(self.window_unit, timedelta(hours=1))

    def get_total_duration(self) -> timedelta:
        """Get total duration of the reporting window."""
        return self.end_time - self.start_time

    def add_data_point(
            self,
            timestamp: datetime,
            value: Union[int, float, str, Dict[str, Any]],
            metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a data point to the report.

        Args:
            timestamp: When the data point occurred
            value: The data value
            metadata: Optional metadata about the data point
        """
        # Validate timestamp is within reporting window
        if not (self.start_time <= timestamp <= self.end_time):
            logger.warning(f"Data point timestamp {timestamp} outside reporting window")
            return

        # Create data point
        data_point = TimeWindowDataPoint(
            timestamp=timestamp,
            value=value,
            metadata=metadata or {}
        )

        # Add to collection (with size limit)
        if len(self.data_points) >= self.max_data_points:
            # Remove oldest data point
            self.data_points.pop(0)
            logger.warning("Reached max data points, removing oldest entry")

        self.data_points.append(data_point)

        # Auto-aggregate if enabled
        if self.auto_aggregate:
            self._update_aggregation(data_point)

    def _get_window_key(self, timestamp: datetime) -> str:
        """Get window key for a given timestamp."""
        window_duration = self.get_window_duration()

        # Calculate which window this timestamp belongs to
        time_offset = timestamp - self.start_time
        window_index = int(time_offset.total_seconds() / window_duration.total_seconds())

        # Calculate window start time
        window_start = self.start_time + (window_index * window_duration)

        return window_start.isoformat()

    def _update_aggregation(self, data_point: TimeWindowDataPoint) -> None:
        """Update aggregated data with new data point."""
        window_key = self._get_window_key(data_point.timestamp)

        if window_key not in self.aggregated_data:
            self.aggregated_data[window_key] = {
                'count': 0,
                'values': [],
                'first_timestamp': data_point.timestamp,
                'last_timestamp': data_point.timestamp,
            }

        window_data = self.aggregated_data[window_key]
        window_data['count'] += 1
        window_data['values'].append(data_point.value)
        window_data['last_timestamp'] = data_point.timestamp

    def aggregate_by_window(
            self,
            aggregation_type: Union[AggregationType, str] = AggregationType.COUNT,
            value_key: Optional[str] = None
    ) -> Dict[str, Union[int, float]]:
        """
        Aggregate data by time windows.

        Args:
            aggregation_type: How to aggregate the data
            value_key: Key to extract from dict values (if values are dicts)

        Returns:
            Dictionary mapping window keys to aggregated values
        """
        if isinstance(aggregation_type, str):
            aggregation_type = AggregationType(aggregation_type.lower())

        result = {}

        for window_key, window_data in self.aggregated_data.items():
            values = window_data['values']

            # Extract specific key from dict values if specified
            if value_key and values and isinstance(values[0], dict):
                values = [v.get(value_key, 0) for v in values if isinstance(v, dict)]

            # Filter out non-numeric values for numeric aggregations
            numeric_agg_types = {AggregationType.SUM, AggregationType.AVERAGE,
                                 AggregationType.MIN, AggregationType.MAX}
            if aggregation_type in numeric_agg_types:
                values = [v for v in values if isinstance(v, (int, float))]

            # Perform aggregation
            if aggregation_type == AggregationType.COUNT:
                result[window_key] = window_data['count']
            elif aggregation_type == AggregationType.SUM:
                result[window_key] = sum(values) if values else 0
            elif aggregation_type == AggregationType.AVERAGE:
                result[window_key] = sum(values) / len(values) if values else 0
            elif aggregation_type == AggregationType.MIN:
                result[window_key] = min(values) if values else 0
            elif aggregation_type == AggregationType.MAX:
                result[window_key] = max(values) if values else 0
            elif aggregation_type == AggregationType.FIRST:
                result[window_key] = values[0] if values else None
            elif aggregation_type == AggregationType.LAST:
                result[window_key] = values[-1] if values else None

        return result

    def get_data_in_window(
            self,
            window_start: datetime,
            window_end: datetime
    ) -> List[TimeWindowDataPoint]:
        """Get all data points within a specific time window."""
        return [
            dp for dp in self.data_points
            if window_start <= dp.timestamp <= window_end
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistical summary of the report data."""
        if not self.data_points:
            return {"error": "No data points available"}

        # Extract numeric values
        numeric_values = []
        for dp in self.data_points:
            if isinstance(dp.value, (int, float)):
                numeric_values.append(dp.value)

        stats = {
            "total_data_points": len(self.data_points),
            "numeric_data_points": len(numeric_values),
            "window_count": len(self.aggregated_data),
            "reporting_duration_seconds": self.get_total_duration().total_seconds(),
            "window_duration_seconds": self.get_window_duration().total_seconds(),
        }

        if numeric_values:
            stats.update({
                "min_value": min(numeric_values),
                "max_value": max(numeric_values),
                "average_value": sum(numeric_values) / len(numeric_values),
                "total_value": sum(numeric_values),
            })

        return stats

    def export_data(self, include_metadata: bool = True) -> List[Dict[str, Any]]:
        """Export all data points as list of dictionaries."""
        return [
            dp.to_dict() if include_metadata else {
                "timestamp": dp.timestamp.isoformat(),
                "value": dp.value
            }
            for dp in self.data_points
        ]

    def __repr__(self) -> str:
        """String representation of the report."""
        return f"BaseTimeWindowReport(name={self.report_name}, data_points={len(self.data_points)}, windows={len(self.aggregated_data)})"
