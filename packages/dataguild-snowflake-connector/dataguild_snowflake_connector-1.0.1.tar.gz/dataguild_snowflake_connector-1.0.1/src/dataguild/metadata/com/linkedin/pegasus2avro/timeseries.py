"""
DataGuild timeseries metadata classes.

This module provides classes for representing time-based metadata aspects
and time window specifications for usage statistics and other temporal data.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TimeWindowUnit(Enum):
    """Enumeration of supported time window units."""

    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"

    def to_seconds(self) -> int:
        """Convert time unit to seconds."""
        unit_to_seconds = {
            self.MINUTE: 60,
            self.HOUR: 3600,
            self.DAY: 86400,
            self.WEEK: 604800,
            self.MONTH: 2592000,  # 30 days
            self.YEAR: 31536000,  # 365 days
        }
        return unit_to_seconds[self]

    def __str__(self) -> str:
        return self.value


@dataclass
class TimeWindowSize:
    """
    Represents the size of a time window for aggregating usage statistics.

    This class defines the granularity at which usage statistics are collected
    and aggregated, such as hourly, daily, or weekly intervals.
    """

    unit: TimeWindowUnit
    multiple: int = 1

    def __post_init__(self):
        """Validate time window size after initialization."""
        if self.multiple <= 0:
            raise ValueError("multiple must be positive")
        if not isinstance(self.unit, TimeWindowUnit):
            raise ValueError("unit must be a TimeWindowUnit enum")

    def get_duration_seconds(self) -> int:
        """Get the duration of this time window in seconds."""
        return self.unit.to_seconds() * self.multiple

    def get_duration_milliseconds(self) -> int:
        """Get the duration of this time window in milliseconds."""
        return self.get_duration_seconds() * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "unit": self.unit.value,
            "multiple": self.multiple,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeWindowSize":
        """Create instance from dictionary."""
        unit_str = data["unit"]
        unit = TimeWindowUnit(unit_str) if isinstance(unit_str, str) else unit_str
        return cls(
            unit=unit,
            multiple=data.get("multiple", 1),
        )

    def __str__(self) -> str:
        """String representation."""
        if self.multiple == 1:
            return self.unit.value.lower()
        else:
            return f"{self.multiple}_{self.unit.value.lower()}s"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"TimeWindowSize(unit={self.unit}, multiple={self.multiple})"


# Factory functions for common time windows
def hourly_window() -> TimeWindowSize:
    """Create an hourly time window."""
    return TimeWindowSize(unit=TimeWindowUnit.HOUR, multiple=1)


def daily_window() -> TimeWindowSize:
    """Create a daily time window."""
    return TimeWindowSize(unit=TimeWindowUnit.DAY, multiple=1)


def weekly_window() -> TimeWindowSize:
    """Create a weekly time window."""
    return TimeWindowSize(unit=TimeWindowUnit.WEEK, multiple=1)


def monthly_window() -> TimeWindowSize:
    """Create a monthly time window."""
    return TimeWindowSize(unit=TimeWindowUnit.MONTH, multiple=1)


def custom_window(unit: TimeWindowUnit, multiple: int) -> TimeWindowSize:
    """Create a custom time window."""
    return TimeWindowSize(unit=unit, multiple=multiple)


# Export all classes and functions
__all__ = [
    'TimeWindowUnit',
    'TimeWindowSize',
    'hourly_window',
    'daily_window',
    'weekly_window',
    'monthly_window',
    'custom_window',
]
