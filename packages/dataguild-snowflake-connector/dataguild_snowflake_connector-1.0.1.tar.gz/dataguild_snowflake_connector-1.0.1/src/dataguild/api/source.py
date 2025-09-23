"""
Base classes and interfaces for DataGuild ingestion sources.

This module provides the foundational classes and interfaces that all
DataGuild ingestion sources must implement.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class SourceCapability(str, Enum):
    """Enumeration of source capabilities."""
    PLATFORM_INSTANCE = "PLATFORM_INSTANCE"
    DOMAINS = "DOMAINS"
    CONTAINERS = "CONTAINERS"
    SCHEMA_METADATA = "SCHEMA_METADATA"
    DATA_PROFILING = "DATA_PROFILING"
    DESCRIPTIONS = "DESCRIPTIONS"
    LINEAGE_COARSE = "LINEAGE_COARSE"
    LINEAGE_FINE = "LINEAGE_FINE"
    USAGE_STATS = "USAGE_STATS"
    DELETION_DETECTION = "DELETION_DETECTION"
    TAGS = "TAGS"
    CLASSIFICATION = "CLASSIFICATION"
    TEST_CONNECTION = "TEST_CONNECTION"
    BROWSE_PATHS = "BROWSE_PATHS"
    OWNERSHIP = "OWNERSHIP"


@dataclass
class CapabilityReport:
    """Report on source capability status."""

    capable: bool = field(default=True)
    failure_reason: Optional[str] = field(default=None)
    mitigation_message: Optional[str] = field(default=None)

    @classmethod
    def success(cls) -> "CapabilityReport":
        """Create successful capability report."""
        return cls(capable=True)

    @classmethod
    def failure(cls, reason: str, mitigation: Optional[str] = None) -> "CapabilityReport":
        """Create failed capability report."""
        return cls(capable=False, failure_reason=reason, mitigation_message=mitigation)


@dataclass
class TestConnectionReport:
    """Report on connection test results."""

    basic_connectivity: Optional[CapabilityReport] = field(default=None)
    capability_report: Optional[Dict[Union[SourceCapability, str], CapabilityReport]] = field(default=None)
    internal_failure: bool = field(default=False)
    internal_failure_reason: Optional[str] = field(default=None)

    @classmethod
    def success(
        cls,
        capabilities: Optional[Dict[SourceCapability, CapabilityReport]] = None
    ) -> "TestConnectionReport":
        """Create successful test connection report."""
        return cls(
            basic_connectivity=CapabilityReport.success(),
            capability_report=capabilities or {}
        )

    @classmethod
    def failure(cls, reason: str) -> "TestConnectionReport":
        """Create failed test connection report."""
        return cls(
            basic_connectivity=CapabilityReport.failure(reason),
            internal_failure=True,
            internal_failure_reason=reason
        )


class MetadataWorkUnit:
    """Represents a unit of metadata work to be processed."""

    def __init__(
        self,
        id: str,
        mcp: Optional[Any] = None,
        mcp_raw: Optional[Any] = None,
        metadata: Optional[Any] = None,
        treat_errors_as_warnings: bool = False
    ):
        self.id = id
        self.mcp = mcp  # MetadataChangeProposal
        self.mcp_raw = mcp_raw  # Raw MCP data
        self.metadata = metadata
        self.treat_errors_as_warnings = treat_errors_as_warnings
        self.created_timestamp = datetime.now()

    def __str__(self) -> str:
        return f"WorkUnit(id={self.id})"

    def __repr__(self) -> str:
        return self.__str__()


class MetadataWorkUnitProcessor:
    """Base processor for metadata work units."""

    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.start_time = datetime.now()

    def process(self, work_unit: MetadataWorkUnit) -> None:
        """
        Process a single work unit.

        Args:
            work_unit: Work unit to process
        """
        try:
            self._process_work_unit(work_unit)
            self.processed_count += 1
        except Exception as e:
            self.error_count += 1
            if not work_unit.treat_errors_as_warnings:
                raise
            else:
                logger.warning(f"Error processing work unit {work_unit.id}: {e}")

    def _process_work_unit(self, work_unit: MetadataWorkUnit) -> None:
        """
        Internal method to process work unit. Override in subclasses.

        Args:
            work_unit: Work unit to process
        """
        logger.debug(f"Processing work unit: {work_unit.id}")

    def get_report(self) -> Dict[str, Any]:
        """Get processing report."""
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'elapsed_time_seconds': elapsed_time,
            'processing_rate': self.processed_count / max(elapsed_time, 0.001)
        }


class SourceReport:
    """Base report class for ingestion sources."""

    def __init__(self):
        # Entity counts
        self.tables_scanned: int = 0
        self.views_scanned: int = 0
        self.schemas_scanned: int = 0
        self.databases_scanned: int = 0
        self.containers_scanned: int = 0

        # Processing metrics
        self.work_units_produced: int = 0
        self.work_units_processed: int = 0

        # Error tracking
        self.warnings: List[str] = []
        self.failures: List[str] = []

        # Timing information
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None

        # Additional metadata
        self.metadata: Dict[str, Any] = {}

    def report_warning(self, key: str, reason: str) -> None:
        """Report a warning."""
        warning_msg = f"{key}: {reason}"
        self.warnings.append(warning_msg)
        logger.warning(warning_msg)

    def report_failure(self, key: str, reason: str) -> None:
        """Report a failure."""
        failure_msg = f"{key}: {reason}"
        self.failures.append(failure_msg)
        logger.error(failure_msg)

    def set_ingestion_stage(self, stage: str) -> None:
        """Set current ingestion stage."""
        self.metadata['current_stage'] = stage
        logger.info(f"Ingestion stage: {stage}")

    def compute_stats(self) -> Dict[str, Any]:
        """Compute and return summary statistics."""
        if not self.end_time:
            self.end_time = datetime.now()

        elapsed_time = (self.end_time - self.start_time).total_seconds()

        return {
            'entities_scanned': {
                'tables': self.tables_scanned,
                'views': self.views_scanned,
                'schemas': self.schemas_scanned,
                'databases': self.databases_scanned,
                'containers': self.containers_scanned
            },
            'work_units': {
                'produced': self.work_units_produced,
                'processed': self.work_units_processed
            },
            'errors': {
                'warnings': len(self.warnings),
                'failures': len(self.failures)
            },
            'timing': {
                'elapsed_time_seconds': elapsed_time,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat() if self.end_time else None
            },
            'metadata': self.metadata
        }


class TestableSource(ABC):
    """Interface for sources that support connection testing."""

    @staticmethod
    @abstractmethod
    def test_connection(config_dict: dict) -> TestConnectionReport:
        """
        Test connection to the source system.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Test connection report
        """
        pass


class Source(ABC):
    """Base class for all DataGuild ingestion sources."""

    def __init__(self, config: Any, ctx: Any):
        self.config = config
        self.ctx = ctx
        self.report = SourceReport()

    @abstractmethod
    def get_workunits_internal(self) -> Iterable[MetadataWorkUnit]:
        """
        Generate metadata work units.

        Returns:
            Iterator of metadata work units
        """
        pass

    def get_workunits(self) -> Iterable[MetadataWorkUnit]:
        """
        Public interface for getting work units.

        Returns:
            Iterator of metadata work units
        """
        self.report.set_ingestion_stage("METADATA_EXTRACTION")

        try:
            for work_unit in self.get_workunits_internal():
                self.report.work_units_produced += 1
                yield work_unit

                # Log progress
                if self.report.work_units_produced % 1000 == 0:
                    logger.info(f"Produced {self.report.work_units_produced} work units")

        except Exception as e:
            self.report.report_failure("INGESTION_ERROR")
            raise
        finally:
            self.report.end_time = datetime.now()

    def get_report(self) -> SourceReport:
        """Get ingestion report."""
        return self.report

    def close(self) -> None:
        """Clean up resources."""
        logger.info(f"Closing source: {self.__class__.__name__}")

    def get_workunit_processors(self) -> List[Optional[MetadataWorkUnitProcessor]]:
        """
        Get list of work unit processors for this source.

        Returns:
            List of work unit processors
        """
        return []


class StatelessIngestionSourceBase(Source):
    """Base class for stateless ingestion sources."""

    def __init__(self, config: Any, ctx: Any):
        super().__init__(config, ctx)


class StatefulIngestionSourceBase(Source):
    """Base class for stateful ingestion sources with checkpointing."""

    def __init__(self, config: Any, ctx: Any):
        super().__init__(config, ctx)
        self.state_provider = getattr(config, 'state_provider', None)

    def get_previous_run_state(self, key: str) -> Optional[Any]:
        """Get state from previous run."""
        if self.state_provider:
            return self.state_provider.get_state(key)
        return None

    def set_current_run_state(self, key: str, value: Any) -> None:
        """Set state for current run."""
        if self.state_provider:
            self.state_provider.set_state(key, value)


# Factory functions and utilities

def create_test_connection_report(
    connectivity_passed: bool,
    connectivity_failure_reason: Optional[str] = None,
    capability_results: Optional[Dict[SourceCapability, CapabilityReport]] = None
) -> TestConnectionReport:
    """
    Create a test connection report.

    Args:
        connectivity_passed: Whether basic connectivity passed
        connectivity_failure_reason: Reason for connectivity failure
        capability_results: Results of capability testing

    Returns:
        Test connection report
    """
    basic_connectivity = CapabilityReport.success() if connectivity_passed else CapabilityReport.failure(connectivity_failure_reason or "Unknown error")

    return TestConnectionReport(
        basic_connectivity=basic_connectivity,
        capability_report=capability_results or {}
    )


def validate_source_config(source_class: type, config_dict: Dict[str, Any]) -> List[str]:
    """
    Validate source configuration.

    Args:
        source_class: Source class to validate
        config_dict: Configuration dictionary

    Returns:
        List of validation errors
    """
    errors = []

    # Check required fields if defined
    required_fields = getattr(source_class, 'required_config_fields', set())
    for field in required_fields:
        if field not in config_dict:
            errors.append(f"Missing required field: {field}")

    # Check config class validation if available
    config_class = getattr(source_class, 'config_class', None)
    if config_class:
        try:
            config_class.parse_obj(config_dict)
        except Exception as e:
            errors.append(f"Config validation failed: {e}")

    return errors


def get_source_capabilities(source_class: type) -> Dict[str, Any]:
    """
    Get capabilities of a source class.

    Args:
        source_class: Source class to inspect

    Returns:
        Dictionary of capabilities
    """
    return getattr(source_class, 'capabilities', {})


def is_source_capability_supported(
    source_class: type,
    capability: SourceCapability
) -> bool:
    """
    Check if a source supports a specific capability.

    Args:
        source_class: Source class to check
        capability: Capability to verify

    Returns:
        True if capability is supported
    """
    capabilities = get_source_capabilities(source_class)
    capability_info = capabilities.get(capability.value, {})
    return capability_info.get('supported', False)


def auto_work_unit(work_units: Iterable[MetadataWorkUnit]) -> Iterable[MetadataWorkUnit]:
    """
    Auto-process work units with standard enhancements.

    Args:
        work_units: Iterator of work units

    Returns:
        Enhanced work units
    """
    count = 0
    for work_unit in work_units:
        count += 1

        # Add processing metadata
        if hasattr(work_unit, 'metadata'):
            if not hasattr(work_unit.metadata, 'customProperties'):
                work_unit.metadata.customProperties = {}

            work_unit.metadata.customProperties.update({
                'processing_order': str(count),
                'processed_timestamp': datetime.now().isoformat()
            })

        yield work_unit
