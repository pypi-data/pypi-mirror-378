"""
DataGuild global warning utility.

This module provides centralized warning management for DataGuild operations,
allowing components to register and track warnings across the system.
"""

import logging
import threading
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class WarningLevel(Enum):
    """Severity levels for warnings."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class WarningCategory(Enum):
    """Categories of warnings."""
    CONFIGURATION = "configuration"
    CONNECTION = "connection"
    DATA_QUALITY = "data_quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DEPRECATION = "deprecation"
    COMPATIBILITY = "compatibility"
    RESOURCE = "resource"
    GENERAL = "general"


@dataclass
class GlobalWarning:
    """Represents a global warning in the DataGuild system."""
    message: str
    level: WarningLevel = WarningLevel.WARNING
    category: WarningCategory = WarningCategory.GENERAL
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    count: int = 1

    def __str__(self) -> str:
        """String representation of the warning."""
        prefix = f"[{self.level.value.upper()}]"
        if self.source:
            prefix += f"[{self.source}]"
        suffix = f" (count: {self.count})" if self.count > 1 else ""
        return f"{prefix} {self.message}{suffix}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert warning to dictionary representation."""
        return {
            "message": self.message,
            "level": self.level.value,
            "category": self.category.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "count": self.count
        }


class GlobalWarningManager:
    """Thread-safe manager for global warnings."""

    def __init__(self):
        self._warnings: List[GlobalWarning] = []
        self._warning_counts: Dict[str, int] = {}
        self._lock = threading.Lock()
        self._max_warnings = 1000
        self._deduplicate = True

    def add_warning(
            self,
            message: str,
            level: WarningLevel = WarningLevel.WARNING,
            category: WarningCategory = WarningCategory.GENERAL,
            source: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a new warning to the global warning system.

        Args:
            message: Warning message
            level: Severity level of the warning
            category: Category of the warning
            source: Source component that generated the warning
            details: Additional details about the warning
        """
        with self._lock:
            # Create warning key for deduplication
            warning_key = f"{message}|{level.value}|{category.value}|{source}"

            # Check for existing warning if deduplication is enabled
            if self._deduplicate:
                for existing_warning in self._warnings:
                    existing_key = f"{existing_warning.message}|{existing_warning.level.value}|{existing_warning.category.value}|{existing_warning.source}"
                    if existing_key == warning_key:
                        existing_warning.count += 1
                        existing_warning.timestamp = datetime.now()
                        if details:
                            existing_warning.details.update(details)
                        return

            # Create new warning
            warning = GlobalWarning(
                message=message,
                level=level,
                category=category,
                source=source,
                details=details or {},
            )

            # Add to warnings list
            self._warnings.append(warning)
            self._warning_counts[warning_key] = self._warning_counts.get(warning_key, 0) + 1

            # Trim warnings list if it exceeds maximum
            if len(self._warnings) > self._max_warnings:
                self._warnings = self._warnings[-self._max_warnings:]

            # Log the warning
            log_level = {
                WarningLevel.INFO: logging.INFO,
                WarningLevel.WARNING: logging.WARNING,
                WarningLevel.ERROR: logging.ERROR,
                WarningLevel.CRITICAL: logging.CRITICAL
            }.get(level, logging.WARNING)

            logger.log(log_level, str(warning))

    def get_warnings(
            self,
            level: Optional[WarningLevel] = None,
            category: Optional[WarningCategory] = None,
            source: Optional[str] = None,
            limit: Optional[int] = None
    ) -> List[GlobalWarning]:
        """
        Get warnings matching the specified criteria.

        Args:
            level: Filter by warning level
            category: Filter by warning category
            source: Filter by source component
            limit: Maximum number of warnings to return

        Returns:
            List of matching warnings
        """
        with self._lock:
            filtered_warnings = []

            for warning in self._warnings:
                if level and warning.level != level:
                    continue
                if category and warning.category != category:
                    continue
                if source and warning.source != source:
                    continue

                filtered_warnings.append(warning)

            # Sort by timestamp (most recent first)
            filtered_warnings.sort(key=lambda w: w.timestamp, reverse=True)

            if limit:
                filtered_warnings = filtered_warnings[:limit]

            return filtered_warnings

    def clear_warnings(
            self,
            level: Optional[WarningLevel] = None,
            category: Optional[WarningCategory] = None,
            source: Optional[str] = None
    ) -> int:
        """
        Clear warnings matching the specified criteria.

        Args:
            level: Clear warnings with this level
            category: Clear warnings in this category
            source: Clear warnings from this source

        Returns:
            Number of warnings cleared
        """
        with self._lock:
            initial_count = len(self._warnings)

            self._warnings = [
                warning for warning in self._warnings
                if not (
                        (level is None or warning.level == level) and
                        (category is None or warning.category == category) and
                        (source is None or warning.source == source)
                )
            ]

            cleared_count = initial_count - len(self._warnings)

            if cleared_count > 0:
                logger.info(f"Cleared {cleared_count} global warnings")

            return cleared_count

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current warnings.

        Returns:
            Dictionary with warning statistics
        """
        with self._lock:
            summary = {
                "total_warnings": len(self._warnings),
                "by_level": {},
                "by_category": {},
                "by_source": {},
                "most_recent": None
            }

            for warning in self._warnings:
                # Count by level
                level_key = warning.level.value
                summary["by_level"][level_key] = summary["by_level"].get(level_key, 0) + 1

                # Count by category
                category_key = warning.category.value
                summary["by_category"][category_key] = summary["by_category"].get(category_key, 0) + 1

                # Count by source
                source_key = warning.source or "unknown"
                summary["by_source"][source_key] = summary["by_source"].get(source_key, 0) + 1

            # Get most recent warning
            if self._warnings:
                most_recent = max(self._warnings, key=lambda w: w.timestamp)
                summary["most_recent"] = most_recent.to_dict()

            return summary

    def has_errors(self) -> bool:
        """Check if there are any error-level or critical warnings."""
        with self._lock:
            return any(
                warning.level in {WarningLevel.ERROR, WarningLevel.CRITICAL}
                for warning in self._warnings
            )

    def configure(
            self,
            max_warnings: int = 1000,
            deduplicate: bool = True
    ) -> None:
        """
        Configure the warning manager.

        Args:
            max_warnings: Maximum number of warnings to keep
            deduplicate: Whether to deduplicate identical warnings
        """
        with self._lock:
            self._max_warnings = max_warnings
            self._deduplicate = deduplicate


# Global instance
_global_warning_manager = GlobalWarningManager()


def add_global_warning(
        message: str,
        level: WarningLevel = WarningLevel.WARNING,
        category: WarningCategory = WarningCategory.GENERAL,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Add a global warning to the DataGuild system.

    Args:
        message: Warning message
        level: Severity level (default: WARNING)
        category: Warning category (default: GENERAL)
        source: Source component name
        details: Additional warning details

    Example:
        >>> add_global_warning("Configuration file not found",
        ...                   level=WarningLevel.ERROR,
        ...                   category=WarningCategory.CONFIGURATION,
        ...                   source="snowflake_connector")
    """
    _global_warning_manager.add_warning(message, level, category, source, details)


def get_global_warnings(
        level: Optional[WarningLevel] = None,
        category: Optional[WarningCategory] = None,
        source: Optional[str] = None,
        limit: Optional[int] = None
) -> List[GlobalWarning]:
    """
    Get global warnings matching the specified criteria.

    Args:
        level: Filter by warning level
        category: Filter by category
        source: Filter by source
        limit: Maximum number of warnings

    Returns:
        List of matching warnings
    """
    return _global_warning_manager.get_warnings(level, category, source, limit)


def clear_global_warnings(
        level: Optional[WarningLevel] = None,
        category: Optional[WarningCategory] = None,
        source: Optional[str] = None
) -> int:
    """
    Clear global warnings matching criteria.

    Args:
        level: Clear warnings with this level
        category: Clear warnings in this category
        source: Clear warnings from this source

    Returns:
        Number of warnings cleared
    """
    return _global_warning_manager.clear_warnings(level, category, source)


def get_warning_summary() -> Dict[str, Any]:
    """
    Get summary of current global warnings.

    Returns:
        Dictionary with warning statistics
    """
    return _global_warning_manager.get_summary()


def has_error_warnings() -> bool:
    """
    Check if there are any error or critical warnings.

    Returns:
        True if there are error-level warnings
    """
    return _global_warning_manager.has_errors()


# Convenience functions for different warning levels
def add_info(message: str, source: Optional[str] = None, **kwargs) -> None:
    """Add an info-level global warning."""
    add_global_warning(message, WarningLevel.INFO, source=source, **kwargs)


def add_warning(message: str, source: Optional[str] = None, **kwargs) -> None:
    """Add a warning-level global warning."""
    add_global_warning(message, WarningLevel.WARNING, source=source, **kwargs)


def add_error(message: str, source: Optional[str] = None, **kwargs) -> None:
    """Add an error-level global warning."""
    add_global_warning(message, WarningLevel.ERROR, source=source, **kwargs)


def add_critical(message: str, source: Optional[str] = None, **kwargs) -> None:
    """Add a critical-level global warning."""
    add_global_warning(message, WarningLevel.CRITICAL, source=source, **kwargs)
