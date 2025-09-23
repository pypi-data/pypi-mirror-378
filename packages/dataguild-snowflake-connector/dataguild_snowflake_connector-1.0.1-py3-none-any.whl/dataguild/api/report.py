"""
DataGuild API reporting base classes.

This module provides the foundational report classes used throughout
the DataGuild system for tracking operations, errors, and metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ReportStatus(str, Enum):
    """Status values for reports."""
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"
    WARNING = "WARNING"
    IN_PROGRESS = "IN_PROGRESS"


class ReportLevel(str, Enum):
    """Severity levels for report messages."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ReportMessage:
    """Individual message within a report."""
    message: str
    level: ReportLevel = ReportLevel.INFO
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message": self.message,
            "level": self.level.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }


class Report(BaseModel):
    """
    Base report class for DataGuild operations.

    Provides comprehensive tracking of operations including success/failure status,
    timing information, error messages, and performance metrics.
    """

    name: str = Field(description="Name of the report")
    start_time: datetime = Field(
        default_factory=datetime.now,
        description="When the reported operation started"
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="When the reported operation ended"
    )
    status: ReportStatus = Field(
        default=ReportStatus.IN_PROGRESS,
        description="Current status of the operation"
    )

    # Message tracking
    messages: List[ReportMessage] = Field(
        default_factory=list,
        description="Collection of report messages"
    )

    # Error tracking
    errors: List[str] = Field(
        default_factory=list,
        description="Collection of error messages"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Collection of warning messages"
    )

    # Metrics
    processed_count: int = Field(default=0, description="Number of items processed")
    success_count: int = Field(default=0, description="Number of successful operations")
    failure_count: int = Field(default=0, description="Number of failed operations")

    # Custom data
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the report"
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def add_message(
        self,
        message: str,
        level: Union[ReportLevel, str] = ReportLevel.INFO,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to the report.

        Args:
            message: Message text
            level: Message severity level
            context: Additional context information
        """
        if isinstance(level, str):
            level = ReportLevel(level.upper())

        report_message = ReportMessage(
            message=message,
            level=level,
            context=context or {}
        )

        self.messages.append(report_message)

        # Also add to appropriate collections for easy access
        if level == ReportLevel.ERROR:
            self.errors.append(message)
        elif level == ReportLevel.WARNING:
            self.warnings.append(message)

    def add_error(self, error: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add an error message to the report."""
        self.add_message(error, ReportLevel.ERROR, context)
        self.failure_count += 1

    def add_warning(self, warning: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add a warning message to the report."""
        self.add_message(warning, ReportLevel.WARNING, context)

    def add_info(self, info: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add an info message to the report."""
        self.add_message(info, ReportLevel.INFO, context)

    def increment_processed(self, count: int = 1) -> None:
        """Increment the processed count."""
        self.processed_count += count

    def increment_success(self, count: int = 1) -> None:
        """Increment the success count."""
        self.success_count += count

    def increment_failure(self, count: int = 1) -> None:
        """Increment the failure count."""
        self.failure_count += count

    def finalize(self, status: Optional[ReportStatus] = None) -> None:
        """
        Finalize the report by setting end time and determining final status.

        Args:
            status: Override status, otherwise determined automatically
        """
        self.end_time = datetime.now()

        if status:
            self.status = status
        else:
            # Auto-determine status based on errors and warnings
            if self.errors:
                self.status = ReportStatus.FAILURE
            elif self.warnings:
                self.status = ReportStatus.PARTIAL_SUCCESS
            else:
                self.status = ReportStatus.SUCCESS

    def get_duration(self) -> Optional[timedelta]:
        """Get the duration of the reported operation."""
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def get_duration_seconds(self) -> Optional[float]:
        """Get duration in seconds."""
        duration = self.get_duration()
        return duration.total_seconds() if duration else None

    def has_errors(self) -> bool:
        """Check if report has any errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if report has any warnings."""
        return len(self.warnings) > 0

    def is_successful(self) -> bool:
        """Check if operation was successful."""
        return self.status == ReportStatus.SUCCESS

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the report."""
        duration = self.get_duration_seconds()

        return {
            "name": self.name,
            "status": self.status.value,
            "duration_seconds": duration,
            "processed_count": self.processed_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "message_count": len(self.messages),
            "success_rate": self.get_success_rate(),
        }

    def get_success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 100.0
        return (self.success_count / total) * 100.0

    def get_messages_by_level(self, level: ReportLevel) -> List[ReportMessage]:
        """Get all messages of a specific level."""
        return [msg for msg in self.messages if msg.level == level]

    def export_messages(self) -> List[Dict[str, Any]]:
        """Export all messages as dictionaries."""
        return [msg.to_dict() for msg in self.messages]

    def to_json(self) -> str:
        """Export report as JSON string."""
        data = {
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "summary": self.get_summary(),
            "messages": self.export_messages(),
            "metadata": self.metadata,
        }
        return json.dumps(data, indent=2)

    def __repr__(self) -> str:
        """String representation of the report."""
        duration = f", duration={self.get_duration_seconds():.2f}s" if self.end_time else ""
        return f"Report(name={self.name}, status={self.status.value}, errors={len(self.errors)}{duration})"
