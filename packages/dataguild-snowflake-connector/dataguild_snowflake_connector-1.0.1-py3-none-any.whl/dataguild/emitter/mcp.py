"""
DataGuild Advanced Metadata Change Proposal

Enterprise metadata change management with validation, batching,
and performance optimization.
"""

import json
from enum import Enum
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod

import logging

logger = logging.getLogger(__name__)


class AspectType(Enum):
    """Supported metadata aspects."""
    STATUS = "status"
    DATASET_PROPERTIES = "datasetProperties"
    SCHEMA_METADATA = "schemaMetadata"
    GLOBAL_TAGS = "globalTags"
    STRUCTURED_PROPERTIES = "structuredProperties"
    SUB_TYPES = "subTypes"
    VIEW_PROPERTIES = "viewProperties"
    CONTAINER = "container"
    OWNERSHIP = "ownership"
    DOMAINS = "domains"


@dataclass
class MetadataAspect(ABC):
    """Base class for all metadata aspects."""

    @abstractmethod
    def aspect_name(self) -> str:
        """Get the aspect name."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate the aspect."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert aspect to dictionary."""
        return asdict(self)


@dataclass
class MetadataChangeProposal:
    """
    Advanced metadata change proposal with validation and optimization.
    """
    entityUrn: str
    aspect: MetadataAspect
    changeType: str = "UPSERT"
    systemMetadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate the MCP after initialization."""
        if not self.entityUrn:
            raise ValueError("EntityUrn cannot be empty")

        if not self.aspect.validate():
            raise ValueError(f"Invalid aspect: {self.aspect}")

        # Add system metadata
        if not self.systemMetadata:
            self.systemMetadata = {
                "lastObserved": int(datetime.now().timestamp() * 1000),
                "runId": self._generate_run_id(),
                "version": "1.0"
            }

    def _generate_run_id(self) -> str:
        """Generate unique run ID."""
        content = f"{self.entityUrn}:{self.aspect.aspect_name}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def get_hash(self) -> str:
        """Get content hash for deduplication."""
        content = json.dumps({
            "entityUrn": self.entityUrn,
            "aspect": self.aspect.to_dict(),
            "changeType": self.changeType
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


class MetadataWorkUnit:
    """
    Advanced work unit with batching, validation, and performance tracking.
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
        self.attempts = 0
        self.last_error: Optional[str] = None

    def get_metadata(self) -> Dict[str, Any]:
        """Get workunit metadata."""
        return {
            "id": self.id,
            "entityUrn": self.mcp.entityUrn,
            "aspectName": self.mcp.aspect.aspect_name(),
            "changeType": self.mcp.changeType,
            "priority": self.priority,
            "batchId": self.batch_id,
            "createdAt": self.created_at.isoformat(),
            "attempts": self.attempts,
            "contentHash": self.mcp.get_hash()
        }


class MetadataChangeProposalWrapper:
    """
    Advanced wrapper for MCPs with batching, validation, and error handling.
    """

    def __init__(
            self,
            entityUrn: str,
            aspect: MetadataAspect,
            changeType: str = "UPSERT"
    ):
        self.mcp = MetadataChangeProposal(
            entityUrn=entityUrn,
            aspect=aspect,
            changeType=changeType
        )
        self._workunit_id = self._generate_workunit_id()

    def _generate_workunit_id(self) -> str:
        """Generate unique workunit ID."""
        content = f"{self.mcp.entityUrn}:{self.mcp.aspect.aspect_name}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()

    def as_workunit(self, priority: int = 1, batch_id: Optional[str] = None) -> MetadataWorkUnit:
        """Convert to workunit with advanced features."""
        return MetadataWorkUnit(
            id=self._workunit_id,
            mcp=self.mcp,
            priority=priority,
            batch_id=batch_id
        )


class BatchedMCPEmitter:
    """
    Advanced batched emitter for high-performance metadata ingestion.
    """

    def __init__(self, batch_size: int = 100, max_workers: int = 10):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self._current_batch: List[MetadataWorkUnit] = []
        self._processed_count = 0
        self._error_count = 0
        self._dedup_cache: Set[str] = set()

    def emit(self, workunit: MetadataWorkUnit) -> None:
        """Emit workunit with batching and deduplication."""
        content_hash = workunit.mcp.get_hash()

        # Deduplication
        if content_hash in self._dedup_cache:
            logger.debug(f"Skipping duplicate workunit: {workunit.id}")
            return

        self._dedup_cache.add(content_hash)
        self._current_batch.append(workunit)

        # Process batch if full
        if len(self._current_batch) >= self.batch_size:
            self._process_batch()

    def _process_batch(self) -> None:
        """Process current batch of workunits."""
        if not self._current_batch:
            return

        logger.info(f"Processing batch of {len(self._current_batch)} workunits")

        # Sort by priority
        self._current_batch.sort(key=lambda wu: wu.priority, reverse=True)

        # Process workunits
        for workunit in self._current_batch:
            try:
                self._process_workunit(workunit)
                self._processed_count += 1
            except Exception as e:
                logger.error(f"Failed to process workunit {workunit.id}: {e}")
                workunit.attempts += 1
                workunit.last_error = str(e)
                self._error_count += 1

        # Clear batch
        self._current_batch.clear()

    def _process_workunit(self, workunit: MetadataWorkUnit) -> None:
        """Process individual workunit."""
        # This would integrate with the actual DataGuild platform
        logger.debug(f"Processing workunit: {workunit.get_metadata()}")

    def flush(self) -> None:
        """Flush remaining workunits."""
        if self._current_batch:
            self._process_batch()

    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            "processed_count": self._processed_count,
            "error_count": self._error_count,
            "pending_count": len(self._current_batch),
            "dedup_cache_size": len(self._dedup_cache)
        }
