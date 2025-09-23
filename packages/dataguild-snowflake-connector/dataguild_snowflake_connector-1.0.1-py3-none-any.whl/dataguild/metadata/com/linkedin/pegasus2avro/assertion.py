"""
DataGuild assertion metadata schema classes.

This module provides the core data structures for representing data quality assertions
and their execution results within the DataGuild metadata system, following the
LinkedIn Pegasus2Avro schema patterns.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AssertionResultType(str, Enum):
    """
    Enumeration of possible assertion result types.

    This enum represents the outcome of executing a data quality assertion,
    indicating whether the assertion passed, failed, or encountered issues.
    """

    SUCCESS = "SUCCESS"
    """The assertion passed successfully - data meets the specified criteria."""

    FAILURE = "FAILURE"
    """The assertion failed - data does not meet the specified criteria."""

    WARNING = "WARNING"
    """The assertion completed with warnings - data may have minor issues."""

    ERROR = "ERROR"
    """The assertion encountered an error during execution."""

    UNKNOWN = "UNKNOWN"
    """The assertion result is unknown or could not be determined."""


class AssertionRunStatus(str, Enum):
    """
    Enumeration of possible assertion run statuses.

    This enum represents the execution state of an assertion run,
    tracking the lifecycle from initiation to completion.
    """

    RUNNING = "RUNNING"
    """The assertion is currently being executed."""

    COMPLETE = "COMPLETE"
    """The assertion execution has completed successfully."""

    FAILED = "FAILED"
    """The assertion execution failed due to system errors."""

    ABORTED = "ABORTED"
    """The assertion execution was aborted or cancelled."""

    SKIPPED = "SKIPPED"
    """The assertion execution was skipped."""

    PENDING = "PENDING"
    """The assertion is pending execution."""


class AssertionType(str, Enum):
    """
    Enumeration of assertion types supported by DataGuild.
    """

    DATASET = "DATASET"
    """Dataset-level assertion (e.g., row count, schema validation)."""

    FIELD = "FIELD"
    """Field/column-level assertion (e.g., null checks, value ranges)."""

    CUSTOM = "CUSTOM"
    """Custom assertion with user-defined logic."""

    SQL = "SQL"
    """SQL-based assertion using custom queries."""


@dataclass
class AssertionResult:
    """
    Represents the result of executing a data quality assertion.

    This class contains comprehensive information about the outcome of an assertion,
    including the result type, actual vs expected values, and any additional context.

    Attributes:
        type: The type of assertion result (SUCCESS, FAILURE, etc.)
        externalUrl: Optional URL to external system showing detailed results
        actualValue: The actual value observed during assertion execution
        expectedValue: The expected value or criteria for the assertion
        nativeResults: Platform-specific result details as key-value pairs
        context: Additional context information about the assertion execution

    Examples:
        >>> result = AssertionResult(
        ...     type=AssertionResultType.SUCCESS,
        ...     actualValue=1000,
        ...     expectedValue="between 900 and 1100",
        ...     externalUrl="https://dq-tool.example.com/result/123"
        ... )
        >>> print(result.type)
        AssertionResultType.SUCCESS
    """

    type: AssertionResultType
    """The type/outcome of the assertion result."""

    externalUrl: Optional[str] = None
    """URL to external system where detailed results can be viewed."""

    actualValue: Optional[Union[str, int, float, bool]] = None
    """The actual value observed during assertion execution."""

    expectedValue: Optional[Union[str, int, float, bool]] = None
    """The expected value or criteria that was being tested."""

    nativeResults: Optional[Dict[str, Any]] = None
    """Platform-specific result details (e.g., from Great Expectations, dbt, etc.)."""

    context: Optional[Dict[str, Any]] = None
    """Additional context information about the assertion execution."""

    rowCount: Optional[int] = None
    """Number of rows that were evaluated (for dataset assertions)."""

    missingCount: Optional[int] = None
    """Number of missing/null values found (for completeness checks)."""

    unexpectedCount: Optional[int] = None
    """Number of values that didn't meet expectations (for validation checks)."""

    def __post_init__(self):
        """Validate assertion result after initialization."""
        if not isinstance(self.type, AssertionResultType):
            if isinstance(self.type, str):
                try:
                    self.type = AssertionResultType(self.type)
                except ValueError:
                    raise ValueError(f"Invalid assertion result type: {self.type}")
            else:
                raise TypeError(f"type must be AssertionResultType, got {type(self.type)}")

    def is_success(self) -> bool:
        """Check if the assertion result indicates success."""
        return self.type == AssertionResultType.SUCCESS

    def is_failure(self) -> bool:
        """Check if the assertion result indicates failure."""
        return self.type == AssertionResultType.FAILURE

    def to_dict(self) -> Dict[str, Any]:
        """Convert assertion result to dictionary representation."""
        result_dict = {
            "type": self.type.value,
            "externalUrl": self.externalUrl,
            "actualValue": self.actualValue,
            "expectedValue": self.expectedValue,
            "nativeResults": self.nativeResults,
            "context": self.context,
            "rowCount": self.rowCount,
            "missingCount": self.missingCount,
            "unexpectedCount": self.unexpectedCount,
        }

        # Remove None values for cleaner serialization
        return {k: v for k, v in result_dict.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssertionResult":
        """Create AssertionResult from dictionary representation."""
        return cls(
            type=AssertionResultType(data["type"]),
            externalUrl=data.get("externalUrl"),
            actualValue=data.get("actualValue"),
            expectedValue=data.get("expectedValue"),
            nativeResults=data.get("nativeResults"),
            context=data.get("context"),
            rowCount=data.get("rowCount"),
            missingCount=data.get("missingCount"),
            unexpectedCount=data.get("unexpectedCount"),
        )


@dataclass
class AssertionRunEvent:
    """
    Represents an event that occurs when a data quality assertion is executed.

    This class captures comprehensive information about an assertion execution,
    including timing, context, results, and relationships to datasets and assertions.

    Attributes:
        timestampMillis: Timestamp when the assertion was executed (in milliseconds)
        assertionUrn: URN of the assertion that was executed
        asserteeUrn: URN of the entity (dataset, field) that was asserted against
        runId: Unique identifier for this specific assertion run
        status: Current status of the assertion run
        result: Detailed result of the assertion execution
        message: Optional human-readable message about the assertion run

    Examples:
        >>> import time
        >>> from dataguild.emitter.mce_builder import make_assertion_urn, make_dataset_urn
        >>>
        >>> result = AssertionResult(
        ...     type=AssertionResultType.SUCCESS,
        ...     actualValue=1000,
        ...     expectedValue=1000
        ... )
        >>>
        >>> event = AssertionRunEvent(
        ...     timestampMillis=int(time.time() * 1000),
        ...     assertionUrn=make_assertion_urn("completeness_check"),
        ...     asserteeUrn=make_dataset_urn("snowflake", "db.schema.table"),
        ...     runId="run_20231201_001",
        ...     status=AssertionRunStatus.COMPLETE,
        ...     result=result,
        ...     message="Row count assertion passed"
        ... )
    """

    timestampMillis: int
    """Timestamp when the assertion was executed, in milliseconds since Unix epoch."""

    assertionUrn: str
    """URN of the assertion that was executed."""

    asserteeUrn: str
    """URN of the entity (dataset, schema field, etc.) that was asserted against."""

    runId: str
    """Unique identifier for this specific assertion run."""

    status: AssertionRunStatus
    """Current status of the assertion run execution."""

    result: AssertionResult
    """Detailed result of the assertion execution."""

    message: Optional[str] = None
    """Optional human-readable message providing additional context."""

    partitionSpec: Optional[str] = None
    """Specification of the data partition that was asserted (JSON string)."""

    batchId: Optional[str] = None
    """Identifier for the data batch that was processed."""

    executionRequestId: Optional[str] = None
    """Identifier for the execution request that triggered this assertion."""

    def __post_init__(self):
        """Validate assertion run event after initialization."""
        if not isinstance(self.status, AssertionRunStatus):
            if isinstance(self.status, str):
                try:
                    self.status = AssertionRunStatus(self.status)
                except ValueError:
                    raise ValueError(f"Invalid assertion run status: {self.status}")
            else:
                raise TypeError(f"status must be AssertionRunStatus, got {type(self.status)}")

        if not isinstance(self.result, AssertionResult):
            raise TypeError(f"result must be AssertionResult, got {type(self.result)}")

        if self.timestampMillis <= 0:
            raise ValueError("timestampMillis must be positive")

        if not self.assertionUrn or not self.assertionUrn.startswith("urn:li:assertion:"):
            raise ValueError("assertionUrn must be a valid assertion URN")

        if not self.runId:
            raise ValueError("runId cannot be empty")

    def is_completed(self) -> bool:
        """Check if the assertion run has completed (successfully or with failure)."""
        return self.status in [AssertionRunStatus.COMPLETE, AssertionRunStatus.FAILED]

    def is_successful_completion(self) -> bool:
        """Check if the assertion run completed successfully with a success result."""
        return (
                self.status == AssertionRunStatus.COMPLETE
                and self.result.is_success()
        )

    def get_execution_time_iso(self) -> str:
        """Get the execution timestamp as an ISO format string."""
        dt = datetime.fromtimestamp(self.timestampMillis / 1000, tz=timezone.utc)
        return dt.isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert assertion run event to dictionary representation."""
        event_dict = {
            "timestampMillis": self.timestampMillis,
            "assertionUrn": self.assertionUrn,
            "asserteeUrn": self.asserteeUrn,
            "runId": self.runId,
            "status": self.status.value,
            "result": self.result.to_dict(),
            "message": self.message,
            "partitionSpec": self.partitionSpec,
            "batchId": self.batchId,
            "executionRequestId": self.executionRequestId,
        }

        # Remove None values for cleaner serialization
        return {k: v for k, v in event_dict.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssertionRunEvent":
        """Create AssertionRunEvent from dictionary representation."""
        return cls(
            timestampMillis=data["timestampMillis"],
            assertionUrn=data["assertionUrn"],
            asserteeUrn=data["asserteeUrn"],
            runId=data["runId"],
            status=AssertionRunStatus(data["status"]),
            result=AssertionResult.from_dict(data["result"]),
            message=data.get("message"),
            partitionSpec=data.get("partitionSpec"),
            batchId=data.get("batchId"),
            executionRequestId=data.get("executionRequestId"),
        )

    def to_json(self) -> str:
        """Convert assertion run event to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "AssertionRunEvent":
        """Create AssertionRunEvent from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# Utility functions for creating assertion objects
def create_success_result(
        actual_value: Optional[Any] = None,
        expected_value: Optional[Any] = None,
        external_url: Optional[str] = None,
        **kwargs
) -> AssertionResult:
    """
    Create a successful assertion result.

    Args:
        actual_value: The actual value observed
        expected_value: The expected value or criteria
        external_url: URL to external system with detailed results
        **kwargs: Additional result attributes

    Returns:
        AssertionResult with SUCCESS type
    """
    return AssertionResult(
        type=AssertionResultType.SUCCESS,
        actualValue=actual_value,
        expectedValue=expected_value,
        externalUrl=external_url,
        **kwargs
    )


def create_failure_result(
        actual_value: Optional[Any] = None,
        expected_value: Optional[Any] = None,
        external_url: Optional[str] = None,
        **kwargs
) -> AssertionResult:
    """
    Create a failed assertion result.

    Args:
        actual_value: The actual value observed
        expected_value: The expected value or criteria
        external_url: URL to external system with detailed results
        **kwargs: Additional result attributes

    Returns:
        AssertionResult with FAILURE type
    """
    return AssertionResult(
        type=AssertionResultType.FAILURE,
        actualValue=actual_value,
        expectedValue=expected_value,
        externalUrl=external_url,
        **kwargs
    )


def create_assertion_run_event(
        assertion_urn: str,
        assertee_urn: str,
        run_id: str,
        result: AssertionResult,
        timestamp_millis: Optional[int] = None,
        message: Optional[str] = None,
        **kwargs
) -> AssertionRunEvent:
    """
    Create an assertion run event.

    Args:
        assertion_urn: URN of the assertion
        assertee_urn: URN of the entity being asserted
        run_id: Unique identifier for the run
        result: Result of the assertion execution
        timestamp_millis: Timestamp in milliseconds (defaults to current time)
        message: Optional message about the run
        **kwargs: Additional event attributes

    Returns:
        AssertionRunEvent instance
    """
    if timestamp_millis is None:
        timestamp_millis = int(datetime.now(timezone.utc).timestamp() * 1000)

    status = AssertionRunStatus.COMPLETE if result.is_success() or result.is_failure() else AssertionRunStatus.FAILED

    return AssertionRunEvent(
        timestampMillis=timestamp_millis,
        assertionUrn=assertion_urn,
        asserteeUrn=assertee_urn,
        runId=run_id,
        status=status,
        result=result,
        message=message,
        **kwargs
    )


# Export all classes and functions
__all__ = [
    'AssertionResult',
    'AssertionResultType',
    'AssertionRunEvent',
    'AssertionRunStatus',
    'AssertionType',
    'create_success_result',
    'create_failure_result',
    'create_assertion_run_event',
]

# Example usage and testing (for development/testing purposes)
if __name__ == "__main__":
    print("=== DataGuild Assertion Schema Examples ===\n")

    # Example 1: Create a successful assertion result
    print("Example 1: Successful assertion result")
    success_result = create_success_result(
        actual_value=1000,
        expected_value="between 900 and 1100",
        external_url="https://dq-tool.example.com/result/123",
        row_count=1000,
        context={"check_type": "row_count"}
    )
    print(f"Result type: {success_result.type}")
    print(f"Success: {success_result.is_success()}")
    print(f"Result dict: {success_result.to_dict()}")
    print()

    # Example 2: Create a failed assertion result
    print("Example 2: Failed assertion result")
    failure_result = create_failure_result(
        actual_value=50,
        expected_value="greater than 100",
        missing_count=50,
        context={"check_type": "completeness"}
    )
    print(f"Result type: {failure_result.type}")
    print(f"Failure: {failure_result.is_failure()}")
    print()

    # Example 3: Create assertion run events
    print("Example 3: Assertion run events")

    success_event = create_assertion_run_event(
        assertion_urn="urn:li:assertion:completeness_check_001",
        assertee_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)",
        run_id="run_20231201_001",
        result=success_result,
        message="Row count assertion passed successfully",
        batch_id="batch_001"
    )

    failure_event = create_assertion_run_event(
        assertion_urn="urn:li:assertion:completeness_check_002",
        assertee_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table2,PROD)",
        run_id="run_20231201_002",
        result=failure_result,
        message="Completeness assertion failed - too many missing values"
    )

    print(f"Success event completed: {success_event.is_completed()}")
    print(f"Success event successful: {success_event.is_successful_completion()}")
    print(f"Execution time: {success_event.get_execution_time_iso()}")
    print()

    print(f"Failure event completed: {failure_event.is_completed()}")
    print(f"Failure event successful: {failure_event.is_successful_completion()}")
    print()

    # Example 4: JSON serialization
    print("Example 4: JSON serialization")
    json_str = success_event.to_json()
    print("Serialized to JSON:")
    print(json_str)

    # Deserialize from JSON
    deserialized_event = AssertionRunEvent.from_json(json_str)
    print(f"Deserialized event run ID: {deserialized_event.runId}")
    print(f"Deserialized result type: {deserialized_event.result.type}")
