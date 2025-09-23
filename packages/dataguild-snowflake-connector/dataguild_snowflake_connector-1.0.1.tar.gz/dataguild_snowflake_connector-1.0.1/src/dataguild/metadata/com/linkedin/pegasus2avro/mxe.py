"""
DataGuild Metadata Exchange (MXE) classes.

This module provides classes for creating and managing metadata change
proposals in the DataGuild system, compatible with LinkedIn's Pegasus/Avro format.
"""
import logging
import json
import hashlib
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of metadata changes."""
    UPSERT = "UPSERT"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    PATCH = "PATCH"
    RESTATE = "RESTATE"


class AspectName(Enum):
    """Known aspect names in the metadata model."""
    STATUS = "status"
    OWNERSHIP = "ownership"
    DATASET_PROPERTIES = "datasetProperties"
    SCHEMA_METADATA = "schemaMetadata"
    GLOBAL_TAGS = "globalTags"
    GLOSSARY_TERMS = "glossaryTerms"
    INSTITUTIONAL_MEMORY = "institutionalMemory"
    DATA_PLATFORM_INSTANCE = "dataPlatformInstance"


@dataclass
class SystemMetadata:
    """System metadata for change proposals."""

    last_observed: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    run_id: Optional[str] = None
    registry_name: Optional[str] = None
    registry_version: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)


class MetadataChangeProposal:
    """
    Core metadata change proposal class.

    Represents a proposed change to metadata for a specific entity,
    including the entity URN, aspect data, and change type.
    """

    def __init__(
            self,
            entity_urn: str,
            aspect_name: str,
            aspect: Any,
            change_type: Union[ChangeType, str] = ChangeType.UPSERT,
            system_metadata: Optional[SystemMetadata] = None
    ):
        self.entity_urn = entity_urn
        self.aspect_name = aspect_name
        self.aspect = aspect
        self.change_type = ChangeType(change_type) if isinstance(change_type, str) else change_type
        self.system_metadata = system_metadata or SystemMetadata()

    def to_dict(self) -> Dict[str, Any]:
        """Convert MCP to dictionary representation."""
        return {
            "entityUrn": self.entity_urn,
            "aspectName": self.aspect_name,
            "aspect": self._serialize_aspect(self.aspect),
            "changeType": self.change_type.value,
            "systemMetadata": self._serialize_system_metadata()
        }

    def _serialize_aspect(self, aspect: Any) -> Dict[str, Any]:
        """Serialize aspect to dictionary."""
        if hasattr(aspect, 'to_dict'):
            return aspect.to_dict()
        elif hasattr(aspect, '__dict__'):
            return aspect.__dict__
        else:
            return {"value": aspect}

    def _serialize_system_metadata(self) -> Dict[str, Any]:
        """Serialize system metadata."""
        return {
            "lastObserved": self.system_metadata.last_observed,
            "runId": self.system_metadata.run_id,
            "registryName": self.system_metadata.registry_name,
            "registryVersion": self.system_metadata.registry_version,
            "properties": self.system_metadata.properties
        }

    def get_hash(self) -> str:
        """Get content hash for deduplication."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


class MetadataWorkUnit:
    """
    Work unit representing a metadata change operation.

    Wraps a MetadataChangeProposal with additional processing metadata
    such as priority, batch information, and execution tracking.
    """

    def __init__(
            self,
            id: str,
            mcp: MetadataChangeProposal,
            priority: int = 1,
            batch_id: Optional[str] = None
    ):
        self.id = id
        self.mcp = mcp
        self.priority = priority
        self.batch_id = batch_id
        self.created_at = datetime.now()
        self.processed_at: Optional[datetime] = None
        self.attempts = 0
        self.last_error: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    def mark_processed(self) -> None:
        """Mark the work unit as processed."""
        self.processed_at = datetime.now()

    def record_attempt(self, error: Optional[str] = None) -> None:
        """Record a processing attempt."""
        self.attempts += 1
        if error:
            self.last_error = error

    def is_processed(self) -> bool:
        """Check if work unit has been processed."""
        return self.processed_at is not None

    def get_metadata(self) -> Dict[str, Any]:
        """Get work unit metadata."""
        return {
            "id": self.id,
            "entityUrn": self.mcp.entity_urn,
            "aspectName": self.mcp.aspect_name,
            "changeType": self.mcp.change_type.value,
            "priority": self.priority,
            "batchId": self.batch_id,
            "createdAt": self.created_at.isoformat(),
            "processedAt": self.processed_at.isoformat() if self.processed_at else None,
            "attempts": self.attempts,
            "lastError": self.last_error,
            "contentHash": self.mcp.get_hash()
        }


class MetadataChangeProposalWrapper:
    """
    Wrapper for MetadataChangeProposal with enhanced functionality.

    Provides a high-level interface for creating metadata change proposals
    with automatic aspect name detection and work unit generation.
    """

    def __init__(
            self,
            entity_urn: str,
            aspect: Any,
            change_type: Union[ChangeType, str] = ChangeType.UPSERT,
            aspect_name: Optional[str] = None
    ):
        self.entity_urn = entity_urn
        self.aspect = aspect
        self.change_type = ChangeType(change_type) if isinstance(change_type, str) else change_type
        self.aspect_name = aspect_name or self._detect_aspect_name(aspect)

        # Create the underlying MCP
        self.mcp = MetadataChangeProposal(
            entity_urn=entity_urn,
            aspect_name=self.aspect_name,
            aspect=aspect,
            change_type=self.change_type
        )

    def _detect_aspect_name(self, aspect: Any) -> str:
        """Automatically detect aspect name from aspect object."""
        class_name = aspect.__class__.__name__

        # Map common class names to aspect names
        aspect_mapping = {
            "StatusClass": "status",
            "OwnershipClass": "ownership",
            "DatasetPropertiesClass": "datasetProperties",
            "SchemaMetadataClass": "schemaMetadata",
            "GlobalTagsClass": "globalTags",
            "GlossaryTermsClass": "glossaryTerms",
        }

        return aspect_mapping.get(class_name, class_name.lower().replace("class", ""))

    def as_workunit(
            self,
            priority: int = 1,
            batch_id: Optional[str] = None,
            work_unit_id: Optional[str] = None
    ) -> MetadataWorkUnit:
        """
        Convert wrapper to a work unit for processing.

        Args:
            priority: Processing priority (higher = more important)
            batch_id: Optional batch identifier for grouping
            work_unit_id: Optional custom work unit ID

        Returns:
            MetadataWorkUnit ready for processing
        """
        if work_unit_id is None:
            work_unit_id = self._generate_work_unit_id()

        return MetadataWorkUnit(
            id=work_unit_id,
            mcp=self.mcp,
            priority=priority,
            batch_id=batch_id
        )

    def _generate_work_unit_id(self) -> str:
        """Generate a unique work unit ID."""
        content = f"{self.entity_urn}:{self.aspect_name}:{datetime.now().isoformat()}"
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"wu-{hash_suffix}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert wrapper to dictionary."""
        return self.mcp.to_dict()

    @classmethod
    def create_status_change(
            cls,
            entity_urn: str,
            removed: bool = False,
            actor: Optional[str] = None
    ) -> "MetadataChangeProposalWrapper":
        """
        Create a status change proposal.

        Args:
            entity_urn: URN of the entity to update
            removed: Whether to mark entity as removed
            actor: Actor performing the change

        Returns:
            MetadataChangeProposalWrapper for status change
        """
        status = StatusClass(removed=removed, actor=actor)
        return cls(entity_urn=entity_urn, aspect=status)

    @classmethod
    def create_property_change(
            cls,
            entity_urn: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            tags: Optional[List[str]] = None,
            custom_properties: Optional[Dict[str, str]] = None
    ) -> "MetadataChangeProposalWrapper":
        """
        Create a dataset properties change proposal.

        Args:
            entity_urn: URN of the entity to update
            name: Dataset name
            description: Dataset description
            tags: List of tags
            custom_properties: Custom properties dictionary

        Returns:
            MetadataChangeProposalWrapper for properties change
        """
        properties = DatasetPropertiesClass(
            name=name,
            description=description,
            tags=tags or [],
            custom_properties=custom_properties or {}
        )
        return cls(entity_urn=entity_urn, aspect=properties)


# Utility functions for common operations
def create_entity_urn(platform: str, name: str, env: str = "PROD") -> str:
    """
    Create a standard entity URN.

    Args:
        platform: Data platform name (e.g., 'snowflake', 'bigquery')
        name: Entity name (e.g., 'database.schema.table')
        env: Environment (default: 'PROD')

    Returns:
        Properly formatted entity URN
    """
    return f"urn:li:dataset:(urn:li:dataPlatform:{platform},{name},{env})"


def create_batch_work_units(
        mcps: List[MetadataChangeProposalWrapper],
        batch_id: Optional[str] = None,
        base_priority: int = 1
) -> List[MetadataWorkUnit]:
    """
    Create a batch of work units from multiple MCPs.

    Args:
        mcps: List of MetadataChangeProposalWrapper instances
        batch_id: Optional batch identifier
        base_priority: Base priority for all work units

    Returns:
        List of MetadataWorkUnit instances
    """
    if batch_id is None:
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"

    work_units = []
    for i, mcp in enumerate(mcps):
        wu = mcp.as_workunit(
            priority=base_priority + i,
            batch_id=batch_id
        )
        work_units.append(wu)

    return work_units
