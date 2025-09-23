"""
DataGuild stale entity removal handler for stateful ingestion.

This module provides functionality to automatically detect and handle entities
that were present in previous ingestion runs but are missing in the current run.
It supports soft deletion of stale entities to maintain data catalog accuracy.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field

from dataguild.api.closeable import Closeable
from dataguild.api.common import PipelineContext
from dataguild.api.source import MetadataWorkUnitProcessor, SourceReport
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.state.checkpoint import (
    CheckpointStateBase,
    StatefulIngestionSourceBase,
)
from dataguild.metadata.schema_classes import StatusClass
from dataguild.metadata.com.linkedin.pegasus2avro.mxe import MetadataChangeProposalWrapper
from dataguild.utilities.urns import DatasetUrn

logger = logging.getLogger(__name__)


class StatefulStaleMetadataRemovalConfig(BaseModel):
    """
    Configuration for stale metadata removal in stateful ingestion.

    This configuration controls how stale entities (entities present in previous
    runs but missing in current runs) are handled during ingestion.
    """

    # Enable stale entity removal
    enabled: bool = Field(default=True, description="Enable stale entity removal")

    # Ignore entities matching these patterns for stale detection
    ignore_old_state: bool = Field(
        default=False,
        description="Ignore previous state and start fresh"
    )

    # Ignore entities newer than this threshold for removal
    ignore_new_state: bool = Field(
        default=False,
        description="Don't persist state after this run"
    )

    # Remove stale entities after this many runs
    remove_stale_metadata: bool = Field(
        default=True,
        description="Actually remove stale metadata vs just reporting"
    )

    # Fail the ingestion if stale entities are detected
    fail_safe_threshold: float = Field(
        default=1.0,
        description="Fail if more than this percentage of entities would be removed"
    )


class StaleEntityRemovalSourceReport(SourceReport):
    """
    Enhanced source report that includes stale entity removal statistics.

    This report tracks metrics related to stale entity detection and removal
    operations during stateful ingestion runs.
    """

    # Stale entity statistics
    soft_deleted_stale_entities: List[str] = field(default_factory=list)
    entities_scanned: int = 0
    entities_eligible_for_removal: List[str] = field(default_factory=list)

    # State management statistics
    state_size_bytes: int = 0
    state_entities_count: int = 0
    stateful_ingestion_enabled: bool = False

    def report_stale_entity_soft_deleted(self, urn: str) -> None:
        """Report that an entity was soft deleted as stale."""
        self.soft_deleted_stale_entities.append(urn)
        logger.info(f"Soft deleted stale entity: {urn}")

    def report_entity_scanned(self) -> None:
        """Report that an entity was scanned for staleness."""
        self.entities_scanned += 1

    def report_entity_eligible_for_removal(self, urn: str) -> None:
        """Report that an entity is eligible for stale removal."""
        self.entities_eligible_for_removal.append(urn)

    def get_stale_entity_removal_summary(self) -> Dict[str, Any]:
        """Get a summary of stale entity removal operations."""
        return {
            "stale_entities_soft_deleted": len(self.soft_deleted_stale_entities),
            "entities_scanned": self.entities_scanned,
            "entities_eligible_for_removal": len(self.entities_eligible_for_removal),
            "stale_removal_percentage": (
                    len(self.soft_deleted_stale_entities) / max(self.entities_scanned, 1) * 100
            ),
            "state_size_bytes": self.state_size_bytes,
            "state_entities_count": self.state_entities_count,
            "stateful_ingestion_enabled": self.stateful_ingestion_enabled,
        }


class StaleEntityCheckpointState(CheckpointStateBase):
    """
    Checkpoint state for tracking entity presence across ingestion runs.

    This state maintains a record of all entities seen in previous runs
    to enable detection of entities that have become stale.
    """

    # Set of entity URNs seen in the current/previous runs
    encoded_entity_urns: Set[str] = Field(default_factory=set)

    # Timestamp of when this state was last updated
    last_updated: Optional[datetime] = Field(default=None)

    # Pipeline information
    pipeline_name: Optional[str] = Field(default=None)
    run_id: Optional[str] = Field(default=None)

    # Performance tracking
    total_entities_in_last_run: int = Field(default=0)

    def add_entity_urn(self, urn: str) -> None:
        """Add an entity URN to the current state."""
        self.encoded_entity_urns.add(urn)

    def remove_entity_urn(self, urn: str) -> None:
        """Remove an entity URN from the current state."""
        self.encoded_entity_urns.discard(urn)

    def contains_entity_urn(self, urn: str) -> bool:
        """Check if an entity URN is in the current state."""
        return urn in self.encoded_entity_urns

    def get_entities_to_delete(self, current_entities: Set[str]) -> Set[str]:
        """Get entities that should be deleted (in previous state but not current)."""
        return self.encoded_entity_urns - current_entities

    def update_state(self, current_entities: Set[str]) -> None:
        """Update the state with current entities."""
        self.encoded_entity_urns = current_entities.copy()
        self.total_entities_in_last_run = len(current_entities)
        self.last_updated = datetime.now()

    def get_state_size(self) -> int:
        """Get approximate size of the state in bytes."""
        return sum(len(urn.encode('utf-8')) for urn in self.encoded_entity_urns)


class StaleEntityRemovalHandler(Closeable):
    """
    Handler for removing stale entities during stateful ingestion.

    This handler tracks entities across ingestion runs and identifies entities
    that were present in previous runs but are missing in the current run.
    It can automatically soft-delete these stale entities to keep the catalog clean.

    The handler works by:
    1. Loading previous state (set of entity URNs from last run)
    2. Tracking entities seen in current run
    3. Identifying entities in previous state but not current run (stale)
    4. Generating soft-delete work units for stale entities
    5. Saving current state for next run

    Examples:
        >>> handler = StaleEntityRemovalHandler.create(
        ...     source=source,
        ...     config=config,
        ...     ctx=pipeline_context
        ... )
        >>> # Process through workunit_processor
        >>> processors = [handler.workunit_processor]
    """

    def __init__(
            self,
            source: StatefulIngestionSourceBase,
            config: StatefulStaleMetadataRemovalConfig,
            ctx: PipelineContext,
    ):
        """
        Initialize the stale entity removal handler.

        Args:
            source: The stateful ingestion source
            config: Configuration for stale metadata removal
            ctx: Pipeline context with run information
        """
        self.source = source
        self.config = config
        self.ctx = ctx

        # Track entities in current run
        self.entities_in_current_run: Set[str] = set()

        # Load previous state
        self.state = self._get_or_create_state()

        # Track if we're in the middle of processing
        self.processing_started = False
        self.processing_completed = False

        logger.info(
            f"Initialized StaleEntityRemovalHandler for pipeline {ctx.pipeline_name}. "
            f"Previous state contains {len(self.state.encoded_entity_urns)} entities."
        )

    def _get_or_create_state(self) -> StaleEntityCheckpointState:
        """Get existing checkpoint state or create new state."""
        if hasattr(self.source, 'get_current_checkpoint') and not self.config.ignore_old_state:
            try:
                existing_state = self.source.get_current_checkpoint(StaleEntityCheckpointState)
                if existing_state:
                    logger.debug("Retrieved existing stale entity checkpoint state")
                    return existing_state
            except Exception as e:
                logger.warning(f"Failed to retrieve existing stale entity state: {e}")

        # Create new state
        new_state = StaleEntityCheckpointState(
            pipeline_name=self.ctx.pipeline_name,
            run_id=self.ctx.run_id
        )
        logger.debug("Created new stale entity checkpoint state")
        return new_state

    @classmethod
    def create(
            cls,
            source: StatefulIngestionSourceBase,
            config: StatefulStaleMetadataRemovalConfig,
            ctx: PipelineContext,
    ) -> "StaleEntityRemovalHandler":
        """
        Factory method to create a StaleEntityRemovalHandler.

        Args:
            source: The stateful ingestion source
            config: Configuration for stale metadata removal
            ctx: Pipeline context

        Returns:
            Configured StaleEntityRemovalHandler instance
        """
        return cls(source=source, config=config, ctx=ctx)

    @property
    def workunit_processor(self) -> MetadataWorkUnitProcessor:
        """Get the workunit processor for this handler."""
        return MetadataWorkUnitProcessor(
            processor_name="StaleEntityRemoval",
            process_workunit=self._process_workunit,
            finalize_processor=self._finalize_processor
        )

    def _process_workunit(self, workunit: MetadataWorkUnit) -> List[MetadataWorkUnit]:
        """
        Process a workunit and track entities for stale detection.

        Args:
            workunit: The workunit to process

        Returns:
            List containing the original workunit
        """
        if not self.config.enabled:
            return [workunit]

        self.processing_started = True

        # Extract entity URN from workunit
        entity_urn = self._extract_entity_urn(workunit)
        if entity_urn:
            self.entities_in_current_run.add(entity_urn)

            # Update report
            if hasattr(self.source, 'report') and hasattr(self.source.report, 'report_entity_scanned'):
                self.source.report.report_entity_scanned()

        return [workunit]

    def _extract_entity_urn(self, workunit: MetadataWorkUnit) -> Optional[str]:
        """
        Extract entity URN from a workunit.

        Args:
            workunit: The workunit to extract URN from

        Returns:
            Entity URN if found, None otherwise
        """
        try:
            if workunit.metadata and hasattr(workunit.metadata, 'entityUrn'):
                return workunit.metadata.entityUrn
            elif workunit.metadata and hasattr(workunit.metadata, 'aspect') and hasattr(workunit.metadata.aspect,
                                                                                        'urn'):
                return workunit.metadata.aspect.urn
            # Try to extract from workunit ID patterns
            elif workunit.id and '(' in workunit.id:
                # Parse URN-like patterns from workunit ID
                return self._parse_urn_from_id(workunit.id)
        except Exception as e:
            logger.debug(f"Failed to extract entity URN from workunit: {e}")

        return None

    def _parse_urn_from_id(self, workunit_id: str) -> Optional[str]:
        """
        Parse URN from workunit ID.

        Args:
            workunit_id: The workunit ID to parse

        Returns:
            Parsed URN if found, None otherwise
        """
        try:
            # Handle common patterns like "dataset-(urn:li:dataset:...)"
            if workunit_id.startswith('dataset-'):
                urn_part = workunit_id[8:]  # Remove 'dataset-' prefix
                if urn_part.startswith('(') and urn_part.endswith(')'):
                    return urn_part[1:-1]  # Remove parentheses
                return urn_part
            # Handle other entity type patterns
            elif '-(' in workunit_id:
                urn_part = workunit_id.split('-(', 1)[1]
                if urn_part.endswith(')'):
                    return urn_part[:-1]
        except Exception:
            pass

        return None

    def _finalize_processor(self) -> List[MetadataWorkUnit]:
        """
        Finalize processing and generate stale entity removal workunits.

        Returns:
            List of workunits for soft-deleting stale entities
        """
        if not self.config.enabled or not self.processing_started or self.processing_completed:
            return []

        self.processing_completed = True

        logger.info(
            f"Finalizing stale entity removal. "
            f"Current run: {len(self.entities_in_current_run)} entities, "
            f"Previous run: {len(self.state.encoded_entity_urns)} entities"
        )

        # Identify stale entities
        stale_entities = self.state.get_entities_to_delete(self.entities_in_current_run)

        # Apply fail-safe threshold
        if self._should_fail_safe(stale_entities):
            logger.error(
                f"Stale entity removal fail-safe triggered. "
                f"Would remove {len(stale_entities)} entities "
                f"({len(stale_entities) / max(len(self.entities_in_current_run), 1) * 100:.1f}% of current entities)"
            )
            return []

        # Generate removal workunits
        removal_workunits = []
        if self.config.remove_stale_metadata:
            removal_workunits = self._generate_stale_entity_removal_workunits(stale_entities)

        # Update state for next run
        if not self.config.ignore_new_state:
            self._update_state()

        # Update report
        self._update_report(stale_entities)

        logger.info(
            f"Stale entity removal completed. "
            f"Soft deleted {len(removal_workunits)} stale entities."
        )

        return removal_workunits

    def _should_fail_safe(self, stale_entities: Set[str]) -> bool:
        """
        Check if fail-safe threshold is exceeded.

        Args:
            stale_entities: Set of stale entity URNs

        Returns:
            True if fail-safe should be triggered
        """
        if not stale_entities:
            return False

        total_entities = len(self.entities_in_current_run) + len(stale_entities)
        stale_percentage = len(stale_entities) / max(total_entities, 1)

        return stale_percentage > self.config.fail_safe_threshold

    def _generate_stale_entity_removal_workunits(self, stale_entities: Set[str]) -> List[MetadataWorkUnit]:
        """
        Generate workunits to soft-delete stale entities.

        Args:
            stale_entities: Set of stale entity URNs

        Returns:
            List of workunits for soft deletion
        """
        removal_workunits = []

        for entity_urn in stale_entities:
            try:
                # Create soft deletion status
                status = StatusClass(removed=True)

                # Create workunit for soft deletion
                workunit = MetadataChangeProposalWrapper(
                    entityUrn=entity_urn,
                    aspect=status,
                ).as_workunit(f"stale-entity-removal-{entity_urn}")

                removal_workunits.append(workunit)

                logger.debug(f"Generated soft deletion workunit for stale entity: {entity_urn}")

            except Exception as e:
                logger.error(f"Failed to generate removal workunit for {entity_urn}: {e}")

        return removal_workunits

    def _update_state(self) -> None:
        """Update the checkpoint state with current entities."""
        try:
            self.state.update_state(self.entities_in_current_run)

            # Persist state
            if hasattr(self.source, 'set_current_checkpoint'):
                self.source.set_current_checkpoint(self.state)
                logger.debug("Persisted stale entity checkpoint state")
            else:
                logger.warning("Source does not support checkpoint persistence")
        except Exception as e:
            logger.error(f"Failed to update stale entity state: {e}")

    def _update_report(self, stale_entities: Set[str]) -> None:
        """
        Update the source report with stale entity statistics.

        Args:
            stale_entities: Set of stale entity URNs
        """
        if not hasattr(self.source, 'report'):
            return

        report = self.source.report

        # Update basic statistics
        if hasattr(report, 'entities_scanned'):
            report.entities_scanned = len(self.entities_in_current_run)

        if hasattr(report, 'state_size_bytes'):
            report.state_size_bytes = self.state.get_state_size()

        if hasattr(report, 'state_entities_count'):
            report.state_entities_count = len(self.state.encoded_entity_urns)

        if hasattr(report, 'stateful_ingestion_enabled'):
            report.stateful_ingestion_enabled = self.config.enabled

        # Report stale entities
        for entity_urn in stale_entities:
            if hasattr(report, 'report_entity_eligible_for_removal'):
                report.report_entity_eligible_for_removal(entity_urn)

            if self.config.remove_stale_metadata and hasattr(report, 'report_stale_entity_soft_deleted'):
                report.report_stale_entity_soft_deleted(entity_urn)

    def get_current_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current handler state."""
        return {
            "config_enabled": self.config.enabled,
            "entities_in_current_run": len(self.entities_in_current_run),
            "entities_in_previous_run": len(self.state.encoded_entity_urns),
            "processing_started": self.processing_started,
            "processing_completed": self.processing_completed,
            "pipeline_name": self.ctx.pipeline_name,
            "run_id": self.ctx.run_id,
            "state_last_updated": self.state.last_updated.isoformat() if self.state.last_updated else None,
        }

    def close(self) -> None:
        """Close the handler and clean up resources."""
        logger.info(f"Closing StaleEntityRemovalHandler. State: {self.get_current_state_summary()}")


# Export all classes
__all__ = [
    'StaleEntityRemovalHandler',
    'StatefulStaleMetadataRemovalConfig',
    'StaleEntityRemovalSourceReport',
    'StaleEntityCheckpointState',
]
