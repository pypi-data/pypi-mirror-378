"""
DataGuild Advanced Work Unit

Enterprise work unit system with batching, prioritization,
dependency management, comprehensive error handling, and event tracking.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

import logging

logger = logging.getLogger(__name__)


class WorkUnitType(Enum):
    """Types of work units."""
    METADATA = "metadata"
    LINEAGE = "lineage"
    USAGE = "usage"
    PROFILING = "profiling"
    CLASSIFICATION = "classification"
    CONTAINER = "container"


class WorkUnitStatus(Enum):
    """Work unit processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class WorkUnitPriority(Enum):
    """Work unit processing priority."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class MetadataEventType(Enum):
    """
    ✅ ADDED: Types of metadata events that can occur during processing.
    """
    # Work unit lifecycle events
    WORK_UNIT_CREATED = "work_unit_created"
    WORK_UNIT_STARTED = "work_unit_started"
    WORK_UNIT_COMPLETED = "work_unit_completed"
    WORK_UNIT_FAILED = "work_unit_failed"
    WORK_UNIT_RETRYING = "work_unit_retrying"
    WORK_UNIT_CANCELLED = "work_unit_cancelled"

    # Batch processing events
    BATCH_CREATED = "batch_created"
    BATCH_STARTED = "batch_started"
    BATCH_COMPLETED = "batch_completed"
    BATCH_FAILED = "batch_failed"

    # Data processing events
    ENTITY_DISCOVERED = "entity_discovered"
    ENTITY_UPDATED = "entity_updated"
    ENTITY_DELETED = "entity_deleted"
    LINEAGE_CREATED = "lineage_created"
    LINEAGE_UPDATED = "lineage_updated"

    # Schema events
    SCHEMA_CHANGED = "schema_changed"
    SCHEMA_DRIFT_DETECTED = "schema_drift_detected"

    # Quality and validation events
    DATA_QUALITY_CHECK = "data_quality_check"
    VALIDATION_ERROR = "validation_error"
    VALIDATION_WARNING = "validation_warning"

    # System events
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_LOST = "connection_lost"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"

    # Custom events
    CUSTOM = "custom"


class MetadataEventSeverity(Enum):
    """Severity levels for metadata events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetadataEvent:
    """
    ✅ ADDED: Represents a metadata processing event with comprehensive tracking.

    Captures events that occur during metadata ingestion, processing, and management,
    providing detailed audit trail, debugging information, and operational visibility.
    """

    # Required fields
    event_type: MetadataEventType
    timestamp: datetime
    source: str  # Source component/system that generated the event

    # Optional event details
    event_id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    severity: MetadataEventSeverity = MetadataEventSeverity.INFO
    message: Optional[str] = None

    # Context information
    work_unit_id: Optional[str] = None
    batch_id: Optional[str] = None
    entity_urn: Optional[str] = None
    platform: Optional[str] = None

    # Event payload and metadata
    payload: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    # Error information (for error events)
    error_code: Optional[str] = None
    error_details: Optional[str] = None
    stack_trace: Optional[str] = None

    # Processing context
    processing_node: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None

    # Metrics
    duration_ms: Optional[int] = None
    bytes_processed: Optional[int] = None
    records_processed: Optional[int] = None

    def __post_init__(self):
        """Post-initialization validation and normalization."""
        # Handle string-based event type input
        if isinstance(self.event_type, str):
            try:
                self.event_type = MetadataEventType(self.event_type.lower())
            except ValueError:
                logger.warning(f"Unknown event type: {self.event_type}, setting to CUSTOM")
                self.event_type = MetadataEventType.CUSTOM

        # Handle string-based severity input
        if isinstance(self.severity, str):
            try:
                self.severity = MetadataEventSeverity(self.severity.lower())
            except ValueError:
                logger.warning(f"Unknown severity: {self.severity}, setting to INFO")
                self.severity = MetadataEventSeverity.INFO

        # Validate required fields
        if not self.source:
            raise ValueError("Event source must be specified")

        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")

        # Set default event ID if not provided
        if not self.event_id:
            self.event_id = str(uuid4())

        # Validate URN format if provided
        if self.entity_urn and not self.entity_urn.startswith("urn:li:"):
            logger.warning(f"Invalid URN format: {self.entity_urn}")

    def is_error(self) -> bool:
        """Check if this is an error event."""
        return self.severity in {MetadataEventSeverity.ERROR, MetadataEventSeverity.CRITICAL}

    def is_warning(self) -> bool:
        """Check if this is a warning event."""
        return self.severity == MetadataEventSeverity.WARNING

    def is_lifecycle_event(self) -> bool:
        """Check if this is a work unit lifecycle event."""
        lifecycle_events = {
            MetadataEventType.WORK_UNIT_CREATED,
            MetadataEventType.WORK_UNIT_STARTED,
            MetadataEventType.WORK_UNIT_COMPLETED,
            MetadataEventType.WORK_UNIT_FAILED,
            MetadataEventType.WORK_UNIT_RETRYING,
            MetadataEventType.WORK_UNIT_CANCELLED
        }
        return self.event_type in lifecycle_events

    def is_batch_event(self) -> bool:
        """Check if this is a batch processing event."""
        batch_events = {
            MetadataEventType.BATCH_CREATED,
            MetadataEventType.BATCH_STARTED,
            MetadataEventType.BATCH_COMPLETED,
            MetadataEventType.BATCH_FAILED
        }
        return self.event_type in batch_events

    def is_data_event(self) -> bool:
        """Check if this is a data processing event."""
        data_events = {
            MetadataEventType.ENTITY_DISCOVERED,
            MetadataEventType.ENTITY_UPDATED,
            MetadataEventType.ENTITY_DELETED,
            MetadataEventType.LINEAGE_CREATED,
            MetadataEventType.LINEAGE_UPDATED
        }
        return self.event_type in data_events

    def add_payload_data(self, key: str, value: Any) -> None:
        """Add data to the event payload."""
        self.payload[key] = value

    def get_payload_data(self, key: str, default: Any = None) -> Any:
        """Get data from the event payload."""
        return self.payload.get(key, default)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the event."""
        self.tags.add(tag)

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the event."""
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check if event has a specific tag."""
        return tag in self.tags

    def set_error_info(self, error_code: str, error_details: str, stack_trace: Optional[str] = None) -> None:
        """Set error information for error events."""
        self.error_code = error_code
        self.error_details = error_details
        self.stack_trace = stack_trace

        # Automatically set severity to error if not already critical
        if self.severity not in {MetadataEventSeverity.ERROR, MetadataEventSeverity.CRITICAL}:
            self.severity = MetadataEventSeverity.ERROR

    def get_age_seconds(self) -> float:
        """Get age of the event in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()

    def get_duration_seconds(self) -> Optional[float]:
        """Get event duration in seconds."""
        if self.duration_ms is not None:
            return self.duration_ms / 1000.0
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "severity": self.severity.value,
            "message": self.message,

            # Context
            "work_unit_id": self.work_unit_id,
            "batch_id": self.batch_id,
            "entity_urn": self.entity_urn,
            "platform": self.platform,

            # Payload and metadata
            "payload": dict(self.payload),
            "tags": list(self.tags),

            # Error information
            "error_code": self.error_code,
            "error_details": self.error_details,
            "stack_trace": self.stack_trace,

            # Processing context
            "processing_node": self.processing_node,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,

            # Metrics
            "duration_ms": self.duration_ms,
            "duration_seconds": self.get_duration_seconds(),
            "bytes_processed": self.bytes_processed,
            "records_processed": self.records_processed,
            "age_seconds": self.get_age_seconds(),

            # Classification
            "is_error": self.is_error(),
            "is_warning": self.is_warning(),
            "is_lifecycle_event": self.is_lifecycle_event(),
            "is_batch_event": self.is_batch_event(),
            "is_data_event": self.is_data_event()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetadataEvent":
        """Create MetadataEvent from dictionary."""
        timestamp = datetime.fromisoformat(data["timestamp"])

        return cls(
            event_type=MetadataEventType(data["event_type"]),
            timestamp=timestamp,
            source=data["source"],
            event_id=data.get("event_id"),
            severity=MetadataEventSeverity(data.get("severity", "info")),
            message=data.get("message"),
            work_unit_id=data.get("work_unit_id"),
            batch_id=data.get("batch_id"),
            entity_urn=data.get("entity_urn"),
            platform=data.get("platform"),
            payload=data.get("payload", {}),
            tags=set(data.get("tags", [])),
            error_code=data.get("error_code"),
            error_details=data.get("error_details"),
            stack_trace=data.get("stack_trace"),
            processing_node=data.get("processing_node"),
            session_id=data.get("session_id"),
            correlation_id=data.get("correlation_id"),
            duration_ms=data.get("duration_ms"),
            bytes_processed=data.get("bytes_processed"),
            records_processed=data.get("records_processed")
        )

    @classmethod
    def create_work_unit_event(
        cls,
        event_type: MetadataEventType,
        work_unit_id: str,
        source: str,
        message: Optional[str] = None,
        **kwargs
    ) -> "MetadataEvent":
        """Create a work unit lifecycle event."""
        return cls(
            event_type=event_type,
            timestamp=datetime.now(),
            source=source,
            work_unit_id=work_unit_id,
            message=message,
            **kwargs
        )

    @classmethod
    def create_error_event(
        cls,
        source: str,
        error_code: str,
        error_details: str,
        work_unit_id: Optional[str] = None,
        entity_urn: Optional[str] = None,
        stack_trace: Optional[str] = None,
        **kwargs
    ) -> "MetadataEvent":
        """Create an error event."""
        event = cls(
            event_type=MetadataEventType.VALIDATION_ERROR,
            timestamp=datetime.now(),
            source=source,
            severity=MetadataEventSeverity.ERROR,
            work_unit_id=work_unit_id,
            entity_urn=entity_urn,
            **kwargs
        )
        event.set_error_info(error_code, error_details, stack_trace)
        return event

    @classmethod
    def create_entity_event(
        cls,
        event_type: MetadataEventType,
        entity_urn: str,
        source: str,
        platform: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ) -> "MetadataEvent":
        """Create an entity-related event."""
        return cls(
            event_type=event_type,
            timestamp=datetime.now(),
            source=source,
            entity_urn=entity_urn,
            platform=platform,
            message=message,
            **kwargs
        )

    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps(self.to_dict(), default=str, indent=2)

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (f"MetadataEvent(id={self.event_id}, type={self.event_type.value}, "
                f"severity={self.severity.value}, source={self.source})")


@dataclass
class WorkUnitMetrics:
    """Metrics for work unit processing."""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    retry_count: int = 0
    bytes_processed: int = 0
    records_processed: int = 0

    @property
    def total_time_ms(self) -> Optional[int]:
        """Get total processing time in milliseconds."""
        if self.created_at and self.completed_at:
            return int((self.completed_at - self.created_at).total_seconds() * 1000)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time_ms": self.processing_time_ms,
            "total_time_ms": self.total_time_ms,
            "retry_count": self.retry_count,
            "bytes_processed": self.bytes_processed,
            "records_processed": self.records_processed
        }


@dataclass
class ProcessorConfig:
    """
    Configuration object for the Advanced Work-Unit Processor.

    Tweak these knobs to balance throughput, resource usage
    and reliability for your specific workload.
    """

    # Concurrency & batching
    max_workers: int               = 10     # Worker threads / async tasks
    batch_size: int                = 100    # Work-units per batch
    batch_timeout_seconds: int     = 60     # Max wait before a not-full batch is processed

    # Queue & memory limits
    max_queue_size: int            = 10_000 # Safety cap on queued work-units
    memory_threshold_mb: int       = 1_024  # Soft memory ceiling per processor

    # Retry & back-off
    max_retries: int               = 3      # Retries allowed per work-unit
    retry_delay_seconds: int       = 5      # Sleep between retries

    # Processing guards
    max_processing_time_minutes: int = 30   # Kill switch for long-running units
    enable_deduplication: bool       = True # Skip identical content
    enable_async_processing: bool     = False# Switch to asyncio workers (future use)


class MetadataWorkUnit:
    """
    ✅ ENHANCED: Advanced metadata work unit with event tracking.
    """

    def __init__(
            self,
            id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            mcp: Optional[Any] = None,
            mcp_raw: Optional[Any] = None,
            work_unit_type: WorkUnitType = WorkUnitType.METADATA,
            priority: WorkUnitPriority = WorkUnitPriority.NORMAL,
            dependencies: Optional[List[str]] = None,
            max_retries: int = 3,
            timeout_minutes: int = 30,
            tags: Optional[Set[str]] = None
    ):
        self.id = id or str(uuid4())
        self.metadata = metadata or {}
        self.mcp = mcp
        self.mcp_raw = mcp_raw
        self.work_unit_type = work_unit_type
        self.priority = priority
        self.dependencies = dependencies or []
        self.max_retries = max_retries
        self.timeout_minutes = timeout_minutes
        self.tags = tags or set()

        # Processing state
        self.status = WorkUnitStatus.PENDING
        self.metrics = WorkUnitMetrics()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.processing_node: Optional[str] = None

        # ✅ ADDED: Event tracking
        self.events: List[MetadataEvent] = []

        # Callback functions
        self._success_callbacks: List[Callable[[Any], None]] = []
        self._failure_callbacks: List[Callable[[Exception], None]] = []

        # Content for processing
        self._content_hash: Optional[str] = None
        self._serialized_content: Optional[bytes] = None

        # ✅ ADDED: Create initial event
        self._add_event(MetadataEvent.create_work_unit_event(
            MetadataEventType.WORK_UNIT_CREATED,
            self.id,
            "work_unit",
            f"Work unit created with type {work_unit_type.value}"
        ))

    def _add_event(self, event: MetadataEvent) -> None:
        """Add event to work unit history."""
        self.events.append(event)

        # Log event based on severity
        if event.is_error():
            logger.error(f"Work unit {self.id}: {event.message}")
        elif event.is_warning():
            logger.warning(f"Work unit {self.id}: {event.message}")
        else:
            logger.debug(f"Work unit {self.id}: {event.message}")

    def set_content(self, content: Any) -> None:
        """Set work unit content with automatic serialization."""
        try:
            # Serialize content
            if hasattr(content, 'to_dict'):
                serializable = content.to_dict()
            elif hasattr(content, '__dict__'):
                serializable = content.__dict__
            else:
                serializable = content

            json_str = json.dumps(serializable, sort_keys=True, default=str)
            self._serialized_content = json_str.encode('utf-8')

            # Generate content hash for deduplication
            self._content_hash = hashlib.sha256(self._serialized_content).hexdigest()

            # Update metrics
            self.metrics.bytes_processed = len(self._serialized_content)

        except Exception as e:
            logger.error(f"Failed to serialize work unit content: {e}")
            self._add_event(MetadataEvent.create_error_event(
                "work_unit",
                "SERIALIZATION_ERROR",
                f"Failed to serialize content: {e}",
                work_unit_id=self.id
            ))
            raise

    def get_content_hash(self) -> Optional[str]:
        """Get content hash for deduplication."""
        return self._content_hash

    def add_dependency(self, dependency_id: str) -> None:
        """Add dependency on another work unit."""
        if dependency_id not in self.dependencies:
            self.dependencies.append(dependency_id)

    def add_success_callback(self, callback: Callable[[Any], None]) -> None:
        """Add success callback."""
        self._success_callbacks.append(callback)

    def add_failure_callback(self, callback: Callable[[Exception], None]) -> None:
        """Add failure callback."""
        self._failure_callbacks.append(callback)

    def start_processing(self, processing_node: Optional[str] = None) -> None:
        """✅ ENHANCED: Mark work unit as started with event tracking."""
        self.status = WorkUnitStatus.PROCESSING
        self.metrics.started_at = datetime.now()
        self.processing_node = processing_node

        # Add event
        self._add_event(MetadataEvent.create_work_unit_event(
            MetadataEventType.WORK_UNIT_STARTED,
            self.id,
            "work_unit",
            f"Started processing on node {processing_node}",
            processing_node=processing_node
        ))

        logger.debug(f"Started processing work unit {self.id} on {processing_node}")

    def mark_completed(self, result: Optional[Any] = None) -> None:
        """✅ ENHANCED: Mark work unit as completed with event tracking."""
        self.status = WorkUnitStatus.COMPLETED
        self.metrics.completed_at = datetime.now()

        if self.metrics.started_at:
            processing_time = self.metrics.completed_at - self.metrics.started_at
            self.metrics.processing_time_ms = int(processing_time.total_seconds() * 1000)

        # Add event
        self._add_event(MetadataEvent.create_work_unit_event(
            MetadataEventType.WORK_UNIT_COMPLETED,
            self.id,
            "work_unit",
            f"Completed in {self.metrics.processing_time_ms}ms",
            duration_ms=self.metrics.processing_time_ms,
            records_processed=self.metrics.records_processed
        ))

        # Execute success callbacks
        for callback in self._success_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.warning(f"Success callback failed for work unit {self.id}: {e}")

        logger.debug(f"Completed work unit {self.id} in {self.metrics.processing_time_ms}ms")

    def mark_failed(self, error: Exception, should_retry: bool = True) -> None:
        """✅ ENHANCED: Mark work unit as failed with event tracking."""
        self.errors.append(str(error))
        self.metrics.retry_count += 1

        if should_retry and self.metrics.retry_count <= self.max_retries:
            self.status = WorkUnitStatus.RETRYING
            event_type = MetadataEventType.WORK_UNIT_RETRYING
            message = f"Retry {self.metrics.retry_count}/{self.max_retries}: {error}"
        else:
            self.status = WorkUnitStatus.FAILED
            self.metrics.completed_at = datetime.now()
            event_type = MetadataEventType.WORK_UNIT_FAILED
            message = f"Failed after {self.metrics.retry_count} retries: {error}"

        # Add event
        self._add_event(MetadataEvent.create_error_event(
            "work_unit",
            "PROCESSING_ERROR",
            str(error),
            work_unit_id=self.id
        ))

        # Execute failure callbacks
        for callback in self._failure_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.warning(f"Failure callback failed for work unit {self.id}: {e}")

        logger.error(f"Work unit {self.id} failed: {error}")

    def add_warning(self, warning: str) -> None:
        """✅ ENHANCED: Add warning with event tracking."""
        self.warnings.append(warning)

        # Add event
        event = MetadataEvent(
            event_type=MetadataEventType.VALIDATION_WARNING,
            timestamp=datetime.now(),
            source="work_unit",
            severity=MetadataEventSeverity.WARNING,
            work_unit_id=self.id,
            message=warning
        )
        self._add_event(event)

        logger.warning(f"Work unit {self.id} warning: {warning}")

    def is_expired(self) -> bool:
        """Check if work unit has exceeded timeout."""
        if self.metrics.started_at:
            elapsed = datetime.now() - self.metrics.started_at
            return elapsed > timedelta(minutes=self.timeout_minutes)
        return False

    def can_process(self, completed_work_units: Set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep_id in completed_work_units for dep_id in self.dependencies)

    def get_events_by_type(self, event_type: MetadataEventType) -> List[MetadataEvent]:
        """✅ ADDED: Get events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]

    def get_error_events(self) -> List[MetadataEvent]:
        """✅ ADDED: Get all error events."""
        return [event for event in self.events if event.is_error()]

    def get_latest_event(self) -> Optional[MetadataEvent]:
        """✅ ADDED: Get the most recent event."""
        return self.events[-1] if self.events else None

    def get_metadata(self) -> Dict[str, Any]:
        """✅ ENHANCED: Get comprehensive work unit metadata including events."""
        return {
            "id": self.id,
            "type": self.work_unit_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "dependency_count": len(self.dependencies),
            "max_retries": self.max_retries,
            "timeout_minutes": self.timeout_minutes,
            "tags": list(self.tags),
            "processing_node": self.processing_node,
            "content_hash": self._content_hash,
            "metrics": self.metrics.to_dict(),
            "errors": self.errors,
            "warnings": self.warnings,
            "custom_metadata": self.metadata,

            # ✅ ADDED: Event information
            "event_count": len(self.events),
            "error_event_count": len(self.get_error_events()),
            "latest_event": self.get_latest_event().to_dict() if self.get_latest_event() else None,
            "events": [event.to_dict() for event in self.events]
        }

    def to_json(self) -> str:
        """Serialize work unit to JSON."""
        return json.dumps(self.get_metadata(), default=str, indent=2)

    def __str__(self) -> str:
        """String representation."""
        return f"WorkUnit(id={self.id}, type={self.work_unit_type.value}, status={self.status.value})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"MetadataWorkUnit(id='{self.id}', type={self.work_unit_type.value}, "
                f"priority={self.priority.value}, status={self.status.value})")


class WorkUnitBatch:
    """
    ✅ ENHANCED: Advanced batch container with event tracking.
    """

    def __init__(
            self,
            batch_id: Optional[str] = None,
            max_size: int = 100,
            max_wait_time_seconds: int = 60
    ):
        self.batch_id = batch_id or str(uuid4())
        self.max_size = max_size
        self.max_wait_time_seconds = max_wait_time_seconds

        self.work_units: Dict[str, MetadataWorkUnit] = {}
        self.created_at = datetime.now()
        self.completed_work_units: Set[str] = set()

        # Batch metrics
        self.total_processing_time_ms = 0
        self.total_bytes_processed = 0

        # ✅ ADDED: Event tracking
        self.events: List[MetadataEvent] = []

        # Create initial event
        self._add_event(MetadataEvent(
            event_type=MetadataEventType.BATCH_CREATED,
            timestamp=self.created_at,
            source="batch_processor",
            batch_id=self.batch_id,
            message=f"Batch created with max_size={max_size}"
        ))

    def _add_event(self, event: MetadataEvent) -> None:
        """Add event to batch history."""
        self.events.append(event)

    def add_work_unit(self, work_unit: MetadataWorkUnit) -> bool:
        """Add work unit to batch. Returns False if batch is full."""
        if len(self.work_units) >= self.max_size:
            return False

        self.work_units[work_unit.id] = work_unit
        return True

    def start_processing(self) -> None:
        """✅ ADDED: Mark batch as started processing."""
        self._add_event(MetadataEvent(
            event_type=MetadataEventType.BATCH_STARTED,
            timestamp=datetime.now(),
            source="batch_processor",
            batch_id=self.batch_id,
            message=f"Started processing batch with {len(self.work_units)} work units"
        ))

    def get_processable_work_units(self) -> List[MetadataWorkUnit]:
        """Get work units that can be processed (dependencies satisfied)."""
        processable = []

        for work_unit in self.work_units.values():
            if (work_unit.status == WorkUnitStatus.PENDING and
                    work_unit.can_process(self.completed_work_units)):
                processable.append(work_unit)

        # Sort by priority
        processable.sort(key=lambda wu: wu.priority.value)
        return processable

    def mark_work_unit_completed(self, work_unit_id: str) -> None:
        """Mark work unit as completed in batch context."""
        if work_unit_id in self.work_units:
            self.completed_work_units.add(work_unit_id)
            work_unit = self.work_units[work_unit_id]

            # Update batch metrics
            if work_unit.metrics.processing_time_ms:
                self.total_processing_time_ms += work_unit.metrics.processing_time_ms
            self.total_bytes_processed += work_unit.metrics.bytes_processed

    def mark_completed(self) -> None:
        """✅ ADDED: Mark batch as completed."""
        self._add_event(MetadataEvent(
            event_type=MetadataEventType.BATCH_COMPLETED,
            timestamp=datetime.now(),
            source="batch_processor",
            batch_id=self.batch_id,
            message=f"Batch completed. Processed {len(self.completed_work_units)} work units",
            duration_ms=self.total_processing_time_ms,
            bytes_processed=self.total_bytes_processed
        ))

    def mark_failed(self, error: str) -> None:
        """✅ ADDED: Mark batch as failed."""
        self._add_event(MetadataEvent.create_error_event(
            "batch_processor",
            "BATCH_PROCESSING_ERROR",
            error,
            batch_id=self.batch_id
        ))

    def is_complete(self) -> bool:
        """Check if all work units in batch are complete."""
        return len(self.completed_work_units) == len(self.work_units)

    def is_ready_for_processing(self) -> bool:
        """Check if batch is ready for processing (full or timeout reached)."""
        if len(self.work_units) >= self.max_size:
            return True

        elapsed = datetime.now() - self.created_at
        return elapsed.total_seconds() >= self.max_wait_time_seconds

    def get_batch_summary(self) -> Dict[str, Any]:
        """✅ ENHANCED: Get comprehensive batch summary with events."""
        status_counts = {}
        for status in WorkUnitStatus:
            count = sum(1 for wu in self.work_units.values() if wu.status == status)
            if count > 0:
                status_counts[status.value] = count

        return {
            "batch_id": self.batch_id,
            "created_at": self.created_at.isoformat(),
            "work_unit_count": len(self.work_units),
            "completed_count": len(self.completed_work_units),
            "status_distribution": status_counts,
            "total_processing_time_ms": self.total_processing_time_ms,
            "total_bytes_processed": self.total_bytes_processed,
            "is_complete": self.is_complete(),
            "completion_percentage": (
                        len(self.completed_work_units) / len(self.work_units) * 100) if self.work_units else 0,

            # ✅ ADDED: Event information
            "event_count": len(self.events),
            "events": [event.to_dict() for event in self.events]
        }


class WorkUnitProcessor:
    """
    ✅ ENHANCED: Advanced work unit processor with event tracking.
    """

    def __init__(self, max_workers: int = 10, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size

        self.work_unit_queue: List[MetadataWorkUnit] = []
        self.processing_work_units: Dict[str, MetadataWorkUnit] = {}
        self.completed_work_units: Set[str] = set()
        self.failed_work_units: Set[str] = set()

        # Deduplication
        self.content_hashes: Set[str] = set()

        # Metrics
        self.total_processed = 0
        self.total_failed = 0
        self.total_deduplicated = 0

        # ✅ ADDED: Event tracking
        self.events: List[MetadataEvent] = []

    def _add_event(self, event: MetadataEvent) -> None:
        """Add event to processor history."""
        self.events.append(event)

    def submit(self, work_unit: MetadataWorkUnit) -> bool:
        """Submit work unit for processing with deduplication."""
        # Check for duplicate content
        content_hash = work_unit.get_content_hash()
        if content_hash and content_hash in self.content_hashes:
            logger.debug(f"Deduplicated work unit {work_unit.id}")
            self.total_deduplicated += 1
            return False

        if content_hash:
            self.content_hashes.add(content_hash)

        self.work_unit_queue.append(work_unit)
        return True

    def process_batch(self) -> List[MetadataWorkUnit]:
        """✅ ENHANCED: Process batch with event tracking."""
        if not self.work_unit_queue:
            return []

        # Create batch
        batch_size = min(self.batch_size, len(self.work_unit_queue))
        batch_work_units = self.work_unit_queue[:batch_size]
        self.work_unit_queue = self.work_unit_queue[batch_size:]

        batch = WorkUnitBatch(max_size=batch_size)
        for wu in batch_work_units:
            batch.add_work_unit(wu)

        # Start batch processing
        batch.start_processing()

        # Process work units with dependency resolution
        processed_units = []

        try:
            while not batch.is_complete():
                processable = batch.get_processable_work_units()

                if not processable:
                    # Check for deadlocks or circular dependencies
                    remaining = [wu for wu in batch.work_units.values()
                                 if wu.status == WorkUnitStatus.PENDING]
                    if remaining:
                        error_msg = f"Potential dependency deadlock in batch {batch.batch_id}"
                        logger.warning(error_msg)
                        batch.mark_failed(error_msg)

                        for wu in remaining:
                            wu.mark_failed(Exception("Dependency deadlock"))
                    break

                # Process work units
                for work_unit in processable:
                    try:
                        work_unit.start_processing("local")

                        # Simulate processing (in real implementation, this would call platform APIs)
                        self._process_work_unit_content(work_unit)

                        work_unit.mark_completed()
                        batch.mark_work_unit_completed(work_unit.id)
                        self.completed_work_units.add(work_unit.id)
                        processed_units.append(work_unit)
                        self.total_processed += 1

                    except Exception as e:
                        work_unit.mark_failed(e, should_retry=False)
                        self.failed_work_units.add(work_unit.id)
                        self.total_failed += 1

            # Mark batch as completed
            batch.mark_completed()

        except Exception as e:
            batch.mark_failed(str(e))
            raise

        return processed_units

    def _process_work_unit_content(self, work_unit: MetadataWorkUnit) -> None:
        """Process work unit content (placeholder for actual implementation)."""
        # This would integrate with DataGuild platform APIs
        logger.debug(f"Processing work unit {work_unit.id} of type {work_unit.work_unit_type.value}")

        # Simulate processing time
        import time
        time.sleep(0.001)  # 1ms simulation

    def get_processing_stats(self) -> Dict[str, Any]:
        """✅ ENHANCED: Get comprehensive processing statistics with events."""
        return {
            "queued_count": len(self.work_unit_queue),
            "processing_count": len(self.processing_work_units),
            "completed_count": len(self.completed_work_units),
            "failed_count": len(self.failed_work_units),
            "total_processed": self.total_processed,
            "total_failed": self.total_failed,
            "total_deduplicated": self.total_deduplicated,
            "success_rate": (self.total_processed / (self.total_processed + self.total_failed)) * 100
            if (self.total_processed + self.total_failed) > 0 else 0,

            # ✅ ADDED: Event information
            "event_count": len(self.events),
            "recent_events": [event.to_dict() for event in self.events[-10:]]  # Last 10 events
        }

    def get_events_by_type(self, event_type: MetadataEventType) -> List[MetadataEvent]:
        """✅ ADDED: Get processor events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]

    def get_error_events(self) -> List[MetadataEvent]:
        """✅ ADDED: Get all error events from processor."""
        return [event for event in self.events if event.is_error()]


# Export all classes
__all__ = [
    # Enums
    'WorkUnitType',
    'WorkUnitStatus',
    'WorkUnitPriority',
    'MetadataEventType',        # ✅ ADDED
    'MetadataEventSeverity',    # ✅ ADDED

    # Main classes
    'MetadataEvent',            # ✅ ADDED
    'WorkUnitMetrics',
    'MetadataWorkUnit',
    'WorkUnitBatch',
    'WorkUnitProcessor',
]
