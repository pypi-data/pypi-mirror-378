"""
Common utilities and classes for DataGuild ingestion API.

This module provides foundational classes and utilities used across
the DataGuild ingestion framework.
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PipelineContext:
    """
    Runtime context for an ingestion pipeline execution.

    Contains metadata about the current pipeline run, including
    execution details, state management, and runtime configuration.
    """

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pipeline_name: str = field(default="dataguild-pipeline")

    # Execution metadata
    start_time: datetime = field(default_factory=datetime.now)
    dry_run: bool = field(default=False)
    preview_mode: bool = field(default=False)

    # State and configuration
    state: Dict[str, Any] = field(default_factory=dict)
    graph: Optional[Any] = field(default=None)

    # Runtime tracking
    work_units_produced: int = field(default=0)
    work_units_processed: int = field(default=0)
    errors_encountered: int = field(default=0)
    warnings_encountered: int = field(default=0)

    # Pipeline metadata
    pipeline_config: Dict[str, Any] = field(default_factory=dict)
    source_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize pipeline context after creation."""
        if not self.run_id:
            self.run_id = f"run-{int(time.time())}-{str(uuid.uuid4())[:8]}"

        logger.info(f"Initialized pipeline context: {self.run_id}")

    def get_elapsed_time(self) -> float:
        """Get elapsed time since pipeline start in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    def increment_work_units_produced(self, count: int = 1) -> None:
        """Increment work units produced counter."""
        self.work_units_produced += count

    def increment_work_units_processed(self, count: int = 1) -> None:
        """Increment work units processed counter."""
        self.work_units_processed += count

    def increment_errors(self, count: int = 1) -> None:
        """Increment error counter."""
        self.errors_encountered += count

    def increment_warnings(self, count: int = 1) -> None:
        """Increment warning counter."""
        self.warnings_encountered += count

    def set_state(self, key: str, value: Any) -> None:
        """Set pipeline state value."""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get pipeline state value."""
        return self.state.get(key, default)

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline execution."""
        return {
            "run_id": self.run_id,
            "pipeline_name": self.pipeline_name,
            "elapsed_time": self.get_elapsed_time(),
            "work_units_produced": self.work_units_produced,
            "work_units_processed": self.work_units_processed,
            "errors": self.errors_encountered,
            "warnings": self.warnings_encountered,
            "dry_run": self.dry_run,
            "preview_mode": self.preview_mode
        }


class WorkunitId:
    """Identifier for work units in the pipeline."""

    def __init__(self, id_str: str):
        self.id = id_str

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"WorkunitId({self.id})"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, WorkunitId):
            return self.id == other.id
        return False


def make_dataplatform_instance_urn(platform: str, instance: str) -> str:
    """
    Create a data platform instance URN.

    Args:
        platform: Platform name
        instance: Instance identifier

    Returns:
        Data platform instance URN
    """
    return f"urn:li:dataPlatformInstance:({platform},{instance})"


def make_dataset_urn(platform: str, name: str, env: str = "PROD") -> str:
    """
    Create a dataset URN.

    Args:
        platform: Platform name
        name: Dataset name
        env: Environment (default: PROD)

    Returns:
        Dataset URN
    """
    return f"urn:li:dataset:({platform},{name},{env})"


def make_data_platform_urn(platform: str) -> str:
    """
    Create a data platform URN.

    Args:
        platform: Platform name

    Returns:
        Data platform URN
    """
    return f"urn:li:dataPlatform:{platform}"


def make_tag_urn(tag: str) -> str:
    """
    Create a tag URN.

    Args:
        tag: Tag name

    Returns:
        Tag URN
    """
    return f"urn:li:tag:{tag}"


def make_user_urn(username: str) -> str:
    """
    Create a user URN.

    Args:
        username: Username

    Returns:
        User URN
    """
    return f"urn:li:corpuser:{username}"


def make_assertion_urn(assertion_id: str) -> str:
    """
    Create an assertion URN.

    Args:
        assertion_id: Assertion identifier

    Returns:
        Assertion URN
    """
    return f"urn:li:assertion:{assertion_id}"
