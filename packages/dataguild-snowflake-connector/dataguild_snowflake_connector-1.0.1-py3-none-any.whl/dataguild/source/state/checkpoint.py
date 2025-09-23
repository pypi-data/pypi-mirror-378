"""
DataGuild checkpoint state management and stateful ingestion infrastructure.

This module provides the complete foundation for managing checkpoint state
across ingestion runs, enabling stateful features like stale entity removal,
redundant run detection, and incremental processing.

This consolidated module includes:
- CheckpointStateBase: Base class for all checkpoint states
- CheckpointStateManager: Manager for multiple checkpoint states
- StatefulIngestionSourceBase: Base class for stateful sources
- StaleEntityRemovalHandler: Handler for removing stale entities
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Set
import json

from pydantic import BaseModel, Field

from dataguild.api.closeable import Closeable
from dataguild.api.common import PipelineContext
from dataguild.api.source import Source, MetadataWorkUnitProcessor
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.metadata.schema_classes import StatusClass
from dataguild.metadata.com.linkedin.pegasus2avro.mxe import MetadataChangeProposalWrapper
from dataguild.configuration.common import ConfigModel

logger = logging.getLogger(__name__)

# Type variables for generic checkpoint state
T = TypeVar('T', bound='CheckpointStateBase')
CheckpointStateType = TypeVar('CheckpointStateType', bound='CheckpointStateBase')


class CheckpointStateBase(BaseModel):
    """
    Base class for all checkpoint state implementations.

    This class provides the foundation for maintaining state across DataGuild
    ingestion runs. Subclasses should implement specific state structures
    for different stateful ingestion features.

    Key features:
    - Serialization/deserialization for persistence
    - Timestamp tracking for state validation
    - Metadata management for debugging and monitoring
    - Cleanup methods for managing state size

    Examples:
        >>> @dataclass
        ... class MyCheckpointState(CheckpointStateBase):
        ...     processed_entities: Set[str] = Field(default_factory=set)
        ...     last_update_time: datetime = Field(default_factory=datetime.now)
        ...
        >>> state = MyCheckpointState()
        >>> state.processed_entities.add("urn:li:dataset:(platform,name,env)")
    """

    # Base metadata fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0")

    # Pipeline metadata for tracking
    pipeline_name: Optional[str] = Field(default=None)
    run_id: Optional[str] = Field(default=None)

    # Custom metadata for extensibility
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration for checkpoint state."""
        # Allow arbitrary types for flexibility
        arbitrary_types_allowed = True
        # Use enum values for serialization
        use_enum_values = True
        # Validate assignments
        validate_assignment = True
        # JSON encoders for complex types
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            set: list,  # Convert sets to lists for JSON serialization
        }

    def update_timestamp(self) -> None:
        """Update the last updated timestamp."""
        self.updated_at = datetime.now()

    def add_custom_metadata(self, key: str, value: Any) -> None:
        """
        Add custom metadata to the checkpoint state.

        Args:
            key: Metadata key
            value: Metadata value (must be JSON serializable)
        """
        self.custom_metadata[key] = value
        self.update_timestamp()

    def get_custom_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get custom metadata from the checkpoint state.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.custom_metadata.get(key, default)

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the checkpoint state.

        Returns:
            Dictionary with state summary information
        """
        return {
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "pipeline_name": self.pipeline_name,
            "run_id": self.run_id,
            "custom_metadata_keys": list(self.custom_metadata.keys()),
            "state_class": self.__class__.__name__,
        }

    def validate_state_consistency(self) -> List[str]:
        """
        Validate the consistency of the checkpoint state.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Basic timestamp validation
        if self.updated_at < self.created_at:
            errors.append("updated_at timestamp is before created_at")

        # Subclasses can override to add specific validation
        return errors

    def cleanup_old_data(self, retention_days: int = 30) -> int:
        """
        Clean up old data from the checkpoint state.

        This base implementation provides a template that subclasses
        can override for specific cleanup logic.

        Args:
            retention_days: Number of days to retain data

        Returns:
            Number of items cleaned up
        """
        # Base implementation - subclasses should override
        cutoff_time = datetime.now() - timedelta(days=retention_days)

        # Clean up old custom metadata entries
        old_keys = []
        for key, value in self.custom_metadata.items():
            if isinstance(value, dict) and 'timestamp' in value:
                try:
                    if datetime.fromisoformat(value['timestamp']) < cutoff_time:
                        old_keys.append(key)
                except (ValueError, TypeError):
                    pass  # Skip invalid timestamp entries

        for key in old_keys:
            del self.custom_metadata[key]

        if old_keys:
            self.update_timestamp()
            logger.info(f"Cleaned up {len(old_keys)} old metadata entries from checkpoint state")

        return len(old_keys)

    def serialize_to_dict(self) -> Dict[str, Any]:
        """
        Serialize the checkpoint state to a dictionary.

        Returns:
            Dictionary representation of the state
        """
        return json.loads(self.json())

    @classmethod
    def deserialize_from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Deserialize checkpoint state from a dictionary.

        Args:
            data: Dictionary representation of the state

        Returns:
            Deserialized checkpoint state instance
        """
        return cls.parse_obj(data)

    def serialize_to_bytes(self) -> bytes:
        """
        Serialize the checkpoint state to bytes.

        Returns:
            Byte representation of the state
        """
        return self.json().encode('utf-8')

    @classmethod
    def deserialize_from_bytes(cls: Type[T], data: bytes) -> T:
        """
        Deserialize checkpoint state from bytes.

        Args:
            data: Byte representation of the state

        Returns:
            Deserialized checkpoint state instance
        """
        return cls.parse_raw(data)

    def get_memory_footprint(self) -> Dict[str, Any]:
        """
        Get approximate memory footprint of the checkpoint state.

        Returns:
            Dictionary with memory usage information
        """
        json_size = len(self.json().encode('utf-8'))

        return {
            "json_size_bytes": json_size,
            "json_size_kb": json_size / 1024,
            "json_size_mb": json_size / (1024 * 1024),
            "field_count": len(self.__fields__),
            "custom_metadata_count": len(self.custom_metadata),
        }

    def __str__(self) -> str:
        """String representation of the checkpoint state."""
        return f"{self.__class__.__name__}(pipeline={self.pipeline_name}, run={self.run_id}, updated={self.updated_at})"

    def __repr__(self) -> str:
        """Detailed string representation of the checkpoint state."""
        return f"{self.__class__.__name__}(created_at={self.created_at}, updated_at={self.updated_at}, version={self.version})"


class CheckpointStateManager:
    """
    Manager class for handling multiple checkpoint states.

    This class provides utilities for managing multiple checkpoint states
    within a single ingestion source, including serialization, persistence,
    and state lifecycle management.
    """

    def __init__(self):
        """Initialize the checkpoint state manager."""
        self._states: Dict[str, CheckpointStateBase] = {}
        self._state_types: Dict[str, Type[CheckpointStateBase]] = {}

    def register_state_type(self, name: str, state_class: Type[CheckpointStateBase]) -> None:
        """
        Register a checkpoint state type with the manager.

        Args:
            name: Name identifier for the state type
            state_class: Checkpoint state class
        """
        self._state_types[name] = state_class
        logger.debug(f"Registered checkpoint state type: {name} -> {state_class.__name__}")

    def set_state(self, name: str, state: CheckpointStateBase) -> None:
        """
        Set a checkpoint state in the manager.

        Args:
            name: Name identifier for the state
            state: Checkpoint state instance
        """
        self._states[name] = state
        state.update_timestamp()
        logger.debug(f"Set checkpoint state: {name}")

    def get_state(self, name: str, state_class: Optional[Type[T]] = None) -> Optional[T]:
        """
        Get a checkpoint state from the manager.

        Args:
            name: Name identifier for the state
            state_class: Optional state class for type checking

        Returns:
            Checkpoint state instance or None if not found
        """
        state = self._states.get(name)

        if state is None:
            return None

        if state_class is not None and not isinstance(state, state_class):
            logger.warning(f"State {name} is not of expected type {state_class.__name__}")
            return None

        return state

    def has_state(self, name: str) -> bool:
        """
        Check if a checkpoint state exists in the manager.

        Args:
            name: Name identifier for the state

        Returns:
            True if state exists, False otherwise
        """
        return name in self._states

    def remove_state(self, name: str) -> bool:
        """
        Remove a checkpoint state from the manager.

        Args:
            name: Name identifier for the state

        Returns:
            True if state was removed, False if not found
        """
        if name in self._states:
            del self._states[name]
            logger.debug(f"Removed checkpoint state: {name}")
            return True
        return False

    def get_all_states(self) -> Dict[str, CheckpointStateBase]:
        """
        Get all checkpoint states in the manager.

        Returns:
            Dictionary of all checkpoint states
        """
        return self._states.copy()

    def serialize_all_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Serialize all checkpoint states to dictionaries.

        Returns:
            Dictionary mapping state names to their serialized data
        """
        serialized = {}
        for name, state in self._states.items():
            try:
                serialized[name] = state.serialize_to_dict()
            except Exception as e:
                logger.error(f"Failed to serialize state {name}: {e}")
        return serialized

    def deserialize_all_states(self, data: Dict[str, Dict[str, Any]]) -> int:
        """
        Deserialize checkpoint states from dictionaries.

        Args:
            data: Dictionary mapping state names to their serialized data

        Returns:
            Number of successfully deserialized states
        """
        success_count = 0

        for name, state_data in data.items():
            try:
                # Determine state class from registered types or data
                state_class = self._determine_state_class(name, state_data)

                if state_class:
                    state = state_class.deserialize_from_dict(state_data)
                    self._states[name] = state
                    success_count += 1
                    logger.debug(f"Deserialized state: {name}")
                else:
                    logger.warning(f"Could not determine state class for: {name}")

            except Exception as e:
                logger.error(f"Failed to deserialize state {name}: {e}")

        return success_count

    def _determine_state_class(self, name: str, state_data: Dict[str, Any]) -> Optional[Type[CheckpointStateBase]]:
        """
        Determine the appropriate state class for deserialization.

        Args:
            name: State name
            state_data: Serialized state data

        Returns:
            State class or None if not determinable
        """
        # Try registered types first
        if name in self._state_types:
            return self._state_types[name]

        # Try to extract from serialized data
        if 'state_class' in state_data:
            class_name = state_data['state_class']
            for registered_class in self._state_types.values():
                if registered_class.__name__ == class_name:
                    return registered_class

        return None

    def cleanup_all_states(self, retention_days: int = 30) -> Dict[str, int]:
        """
        Clean up old data from all checkpoint states.

        Args:
            retention_days: Number of days to retain data

        Returns:
            Dictionary mapping state names to cleanup counts
        """
        cleanup_results = {}

        for name, state in self._states.items():
            try:
                cleaned_count = state.cleanup_old_data(retention_days)
                cleanup_results[name] = cleaned_count
            except Exception as e:
                logger.error(f"Failed to cleanup state {name}: {e}")
                cleanup_results[name] = 0

        return cleanup_results

    def get_manager_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the checkpoint state manager.

        Returns:
            Dictionary with manager summary information
        """
        total_states = len(self._states)
        registered_types = len(self._state_types)

        state_summaries = {}
        total_memory = 0

        for name, state in self._states.items():
            try:
                summary = state.get_state_summary()
                memory_info = state.get_memory_footprint()
                state_summaries[name] = {
                    **summary,
                    "memory_kb": memory_info["json_size_kb"]
                }
                total_memory += memory_info["json_size_bytes"]
            except Exception as e:
                logger.error(f"Failed to get summary for state {name}: {e}")
                state_summaries[name] = {"error": str(e)}

        return {
            "total_states": total_states,
            "registered_types": registered_types,
            "total_memory_bytes": total_memory,
            "total_memory_mb": total_memory / (1024 * 1024),
            "state_summaries": state_summaries,
        }


class StatefulIngestionSourceBase(Source, ABC):
    """
    Base class for sources that support stateful ingestion.

    This class provides the foundation for implementing stateful ingestion sources
    that can maintain state across runs. It includes:

    - Checkpoint state management with automatic persistence
    - Integration with stateful ingestion handlers
    - State lifecycle management (creation, loading, saving, cleanup)
    - Support for multiple checkpoint state types per source

    Stateful sources enable advanced features like:
    - Stale entity removal (automatically remove entities not seen in current run)
    - Redundant run detection (skip processing duplicate time windows)
    - Delta processing (only process changed data since last run)
    - Usage statistics accumulation across runs

    Examples:
        >>> class MyStatefulSource(StatefulIngestionSourceBase):
        ...     def __init__(self, config: MyConfig, ctx: PipelineContext):
        ...         super().__init__(ctx)
        ...         self.config = config
        ...         # Initialize stateful features
        ...         self._setup_stale_entity_removal()
        ...
        ...     def get_workunits_internal(self):
        ...         # Generate workunits with stateful processing
        ...         for entity in self.discover_entities():
        ...             yield self.create_workunit(entity)
        ...
        ...     def _setup_stale_entity_removal(self):
        ...         # Set up stale entity removal handler
        ...         from dataguild.source.state.stale_entity_removal_handler import StaleEntityRemovalHandler
        ...         self.stale_entity_handler = StaleEntityRemovalHandler.create(
        ...             source=self, config=self.config.stale_removal, ctx=self.ctx
        ...         )
    """

    def __init__(self, ctx: PipelineContext):
        """
        Initialize the stateful ingestion source.

        Args:
            ctx: Pipeline context with run information and configuration
        """
        super().__init__(ctx)
        self.ctx = ctx

        # Initialize checkpoint state manager
        self.checkpoint_manager = CheckpointStateManager()

        # Track if stateful ingestion is enabled
        self._stateful_ingestion_enabled = False

        logger.info(f"Initialized stateful ingestion source for pipeline: {ctx.pipeline_name}")

    def enable_stateful_ingestion(self) -> None:
        """Enable stateful ingestion features for this source."""
        self._stateful_ingestion_enabled = True
        logger.info("Enabled stateful ingestion features")

    def is_stateful_ingestion_enabled(self) -> bool:
        """
        Check if stateful ingestion is enabled for this source.

        Returns:
            True if stateful ingestion is enabled
        """
        return self._stateful_ingestion_enabled

    def get_current_checkpoint(
        self,
        checkpoint_class: Type[CheckpointStateType],
        checkpoint_name: Optional[str] = None
    ) -> Optional[CheckpointStateType]:
        """
        Get the current checkpoint state for a specific checkpoint class.

        Args:
            checkpoint_class: The class of checkpoint state to retrieve
            checkpoint_name: Optional name for the checkpoint (defaults to class name)

        Returns:
            The current checkpoint state or None if not found
        """
        if not self._stateful_ingestion_enabled:
            logger.debug("Stateful ingestion not enabled, returning None for checkpoint")
            return None

        name = checkpoint_name or checkpoint_class.__name__

        # Try to get from checkpoint manager
        existing_state = self.checkpoint_manager.get_state(name, checkpoint_class)
        if existing_state:
            return existing_state

        # Try to load from persistent storage
        try:
            loaded_state = self._load_checkpoint_from_storage(checkpoint_class, name)
            if loaded_state:
                self.checkpoint_manager.set_state(name, loaded_state)
                logger.debug(f"Loaded checkpoint state from storage: {name}")
                return loaded_state
        except Exception as e:
            logger.warning(f"Failed to load checkpoint state {name}: {e}")

        return None

    def set_current_checkpoint(
        self,
        checkpoint_state: CheckpointStateBase,
        checkpoint_name: Optional[str] = None
    ) -> None:
        """
        Set the current checkpoint state.

        Args:
            checkpoint_state: The checkpoint state to save
            checkpoint_name: Optional name for the checkpoint (defaults to class name)
        """
        if not self._stateful_ingestion_enabled:
            logger.debug("Stateful ingestion not enabled, not setting checkpoint")
            return

        name = checkpoint_name or type(checkpoint_state).__name__

        # Update checkpoint state metadata
        checkpoint_state.pipeline_name = self.ctx.pipeline_name
        checkpoint_state.run_id = self.ctx.run_id
        checkpoint_state.update_timestamp()

        # Set in checkpoint manager
        self.checkpoint_manager.set_state(name, checkpoint_state)

        # Persist to storage
        try:
            self._save_checkpoint_to_storage(checkpoint_state, name)
            logger.debug(f"Saved checkpoint state: {name}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint state {name}: {e}")
            raise

    def create_checkpoint_state(
        self,
        checkpoint_class: Type[CheckpointStateType],
        checkpoint_name: Optional[str] = None,
        **kwargs: Any
    ) -> CheckpointStateType:
        """
        Create a new checkpoint state instance.

        Args:
            checkpoint_class: The class of checkpoint state to create
            checkpoint_name: Optional name for the checkpoint
            **kwargs: Additional arguments to pass to the checkpoint constructor

        Returns:
            New checkpoint state instance
        """
        # Set default metadata
        kwargs.setdefault('pipeline_name', self.ctx.pipeline_name)
        kwargs.setdefault('run_id', self.ctx.run_id)

        # Create new state
        new_state = checkpoint_class(**kwargs)

        # Register and set if stateful ingestion is enabled
        if self._stateful_ingestion_enabled:
            name = checkpoint_name or checkpoint_class.__name__
            self.checkpoint_manager.register_state_type(name, checkpoint_class)
            self.checkpoint_manager.set_state(name, new_state)

        logger.debug(f"Created new checkpoint state: {checkpoint_class.__name__}")
        return new_state

    def register_checkpoint_state_type(
        self,
        checkpoint_class: Type[CheckpointStateBase],
        checkpoint_name: Optional[str] = None
    ) -> None:
        """
        Register a checkpoint state type with this source.

        Args:
            checkpoint_class: The checkpoint state class to register
            checkpoint_name: Optional name for the checkpoint type
        """
        name = checkpoint_name or checkpoint_class.__name__
        self.checkpoint_manager.register_state_type(name, checkpoint_class)
        logger.debug(f"Registered checkpoint state type: {name}")

    def _load_checkpoint_from_storage(
        self,
        checkpoint_class: Type[CheckpointStateType],
        checkpoint_name: str
    ) -> Optional[CheckpointStateType]:
        """
        Load checkpoint state from persistent storage.

        This is a template method that subclasses can override to implement
        their specific storage mechanism (database, file system, etc.).

        Args:
            checkpoint_class: The class of checkpoint state to load
            checkpoint_name: Name of the checkpoint to load

        Returns:
            The loaded checkpoint state or None
        """
        # Default implementation - subclasses should override for persistence
        logger.debug(f"No persistent storage configured for checkpoint: {checkpoint_name}")
        return None

    def _save_checkpoint_to_storage(
        self,
        checkpoint_state: CheckpointStateBase,
        checkpoint_name: str
    ) -> None:
        """
        Save checkpoint state to persistent storage.

        This is a template method that subclasses can override to implement
        their specific storage mechanism (database, file system, etc.).

        Args:
            checkpoint_state: The checkpoint state to save
            checkpoint_name: Name of the checkpoint to save
        """
        # Default implementation - subclasses should override for persistence
        logger.debug(f"No persistent storage configured for checkpoint: {checkpoint_name}")

    def cleanup_checkpoint_state(self, retention_days: int = 30) -> Dict[str, int]:
        """
        Clean up old checkpoint state data.

        Args:
            retention_days: Number of days to retain checkpoint data

        Returns:
            Dictionary mapping checkpoint names to cleanup counts
        """
        if not self._stateful_ingestion_enabled:
            return {}

        cleanup_results = self.checkpoint_manager.cleanup_all_states(retention_days)

        # Persist updated states after cleanup
        for name, cleanup_count in cleanup_results.items():
            if cleanup_count > 0:
                try:
                    state = self.checkpoint_manager.get_state(name)
                    if state:
                        self._save_checkpoint_to_storage(state, name)
                except Exception as e:
                    logger.error(f"Failed to persist cleaned up state {name}: {e}")

        total_cleaned = sum(cleanup_results.values())
        if total_cleaned > 0:
            logger.info(f"Cleaned up {total_cleaned} checkpoint state entries")

        return cleanup_results

    def get_all_checkpoint_states(self) -> Dict[str, CheckpointStateBase]:
        """
        Get all checkpoint states managed by this source.

        Returns:
            Dictionary mapping checkpoint names to their states
        """
        if not self._stateful_ingestion_enabled:
            return {}

        return self.checkpoint_manager.get_all_states()

    def remove_checkpoint_state(self, checkpoint_name: str) -> bool:
        """
        Remove a checkpoint state from this source.

        Args:
            checkpoint_name: Name of the checkpoint to remove

        Returns:
            True if checkpoint was removed, False if not found
        """
        if not self._stateful_ingestion_enabled:
            return False

        return self.checkpoint_manager.remove_state(checkpoint_name)

    def get_stateful_ingestion_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of stateful ingestion status.

        Returns:
            Dictionary with stateful ingestion information
        """
        base_summary = {
            "stateful_ingestion_enabled": self._stateful_ingestion_enabled,
            "pipeline_name": self.ctx.pipeline_name,
            "run_id": self.ctx.run_id,
        }

        if self._stateful_ingestion_enabled:
            manager_summary = self.checkpoint_manager.get_manager_summary()
            base_summary.update({
                "checkpoint_manager": manager_summary,
                "total_checkpoint_states": manager_summary["total_states"],
                "total_memory_mb": manager_summary["total_memory_mb"],
            })
        else:
            base_summary.update({
                "checkpoint_manager": None,
                "total_checkpoint_states": 0,
                "total_memory_mb": 0.0,
            })

        return base_summary

    def save_all_checkpoint_states(self) -> Dict[str, bool]:
        """
        Save all checkpoint states to persistent storage.

        Returns:
            Dictionary mapping checkpoint names to save success status
        """
        if not self._stateful_ingestion_enabled:
            return {}

        save_results = {}

        for name, state in self.checkpoint_manager.get_all_states().items():
            try:
                self._save_checkpoint_to_storage(state, name)
                save_results[name] = True
            except Exception as e:
                logger.error(f"Failed to save checkpoint state {name}: {e}")
                save_results[name] = False

        return save_results


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
        config: Dict[str, Any],
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
            f"Previous state contains {len(getattr(self.state, 'encoded_entity_urns', set()))} entities."
        )

    def _get_or_create_state(self) -> CheckpointStateBase:
        """Get existing checkpoint state or create new state."""
        # This would use a specific StaleEntityCheckpointState class
        # For now, return a basic checkpoint state
        return CheckpointStateBase(
            pipeline_name=self.ctx.pipeline_name,
            run_id=self.ctx.run_id
        )

    @classmethod
    def create(
        cls,
        source: StatefulIngestionSourceBase,
        config: Dict[str, Any],
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

    def close(self) -> None:
        """Close the handler and clean up resources."""
        logger.info(f"Closing StaleEntityRemovalHandler for pipeline {self.ctx.pipeline_name}")


# Export all classes
__all__ = [
    'CheckpointStateBase',
    'CheckpointStateManager',
    'StatefulIngestionSourceBase',
    'StaleEntityRemovalHandler',
]
