"""
Incremental lineage processing helper for DataGuild sources.

This module provides utilities to enable incremental lineage extraction,
allowing sources to process only changed lineage information between runs.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, Set
from functools import wraps

logger = logging.getLogger(__name__)


class LineageState:
    """Manages state for incremental lineage processing."""

    def __init__(self):
        self.processed_entities: Set[str] = set()
        self.last_run_timestamp: Optional[datetime] = None
        self.checkpoints: Dict[str, Any] = {}

    def mark_entity_processed(self, entity_urn: str) -> None:
        """Mark entity as processed in this run."""
        self.processed_entities.add(entity_urn)

    def is_entity_processed(self, entity_urn: str) -> bool:
        """Check if entity was processed in this run."""
        return entity_urn in self.processed_entities

    def set_checkpoint(self, key: str, value: Any) -> None:
        """Set a checkpoint value for incremental processing."""
        self.checkpoints[key] = value

    def get_checkpoint(self, key: str, default: Any = None) -> Any:
        """Get a checkpoint value."""
        return self.checkpoints.get(key, default)


def auto_incremental_lineage(
        enable_incremental: bool = True,
        state_provider: Optional[Any] = None
) -> Callable:
    """
    Decorator to enable incremental lineage processing for work units.

    This decorator wraps work unit generators to provide incremental
    lineage extraction capabilities, processing only changed lineage
    information between pipeline runs.

    Args:
        enable_incremental: Whether to enable incremental processing
        state_provider: Optional state provider for persistence

    Returns:
        Decorated function with incremental lineage support
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            """Enhanced work unit generator with incremental lineage."""

            if not enable_incremental:
                # Pass through without incremental processing
                logger.debug("Incremental lineage processing disabled")
                yield from func(self, *args, **kwargs)
                return

            logger.info("Starting incremental lineage processing")

            # Initialize lineage state
            lineage_state = LineageState()

            # Load previous state if available
            if hasattr(self, 'state_provider') and self.state_provider:
                try:
                    previous_state = self.state_provider.get_state('lineage')
                    if previous_state:
                        lineage_state.last_run_timestamp = previous_state.get('last_run_timestamp')
                        lineage_state.checkpoints = previous_state.get('checkpoints', {})
                        logger.info(f"Loaded previous lineage state: {len(lineage_state.checkpoints)} checkpoints")
                except Exception as e:
                    logger.warning(f"Failed to load previous lineage state: {e}")

            # Track processed work units for incremental logic
            processed_count = 0
            skipped_count = 0

            # Process work units with incremental logic
            for work_unit in func(self, *args, **kwargs):
                try:
                    # Extract entity URN from work unit
                    entity_urn = getattr(work_unit, 'id', str(work_unit))

                    # Check if incremental processing should skip this work unit
                    if should_skip_work_unit(work_unit, lineage_state):
                        skipped_count += 1
                        logger.debug(f"Skipping work unit {entity_urn} (no changes detected)")
                        continue

                    # Mark entity as processed
                    lineage_state.mark_entity_processed(entity_urn)
                    processed_count += 1

                    # Enhance work unit with incremental metadata
                    enhanced_work_unit = enhance_work_unit_with_incremental_info(
                        work_unit, lineage_state
                    )

                    yield enhanced_work_unit

                    # Update processing checkpoints periodically
                    if processed_count % 100 == 0:
                        update_processing_checkpoint(lineage_state, processed_count)
                        logger.debug(f"Updated checkpoint: {processed_count} work units processed")

                except Exception as e:
                    logger.error(f"Error in incremental lineage processing: {e}")
                    # Continue processing other work units
                    continue

            # Save final state
            try:
                if hasattr(self, 'state_provider') and self.state_provider:
                    final_state = {
                        'last_run_timestamp': datetime.now(),
                        'processed_entities': list(lineage_state.processed_entities),
                        'checkpoints': lineage_state.checkpoints
                    }
                    self.state_provider.set_state('lineage', final_state)
                    logger.info("Saved incremental lineage state")
            except Exception as e:
                logger.error(f"Failed to save lineage state: {e}")

            logger.info(
                f"Incremental lineage processing complete: "
                f"{processed_count} processed, {skipped_count} skipped"
            )

        return wrapper

    return decorator


def should_skip_work_unit(work_unit: Any, state: LineageState) -> bool:
    """
    Determine if a work unit should be skipped in incremental processing.

    Args:
        work_unit: Work unit to evaluate
        state: Current lineage state

    Returns:
        True if work unit should be skipped, False otherwise
    """
    try:
        # Extract lineage information from work unit
        lineage_info = extract_lineage_info(work_unit)

        if not lineage_info:
            return False

        # Check if lineage has changed since last run
        entity_urn = lineage_info.get('entity_urn')
        current_hash = lineage_info.get('lineage_hash')

        if not entity_urn or not current_hash:
            return False

        # Compare with previous hash
        previous_hash = state.get_checkpoint(f"lineage_hash_{entity_urn}")

        if previous_hash == current_hash:
            # No changes detected
            return True

        # Update hash for next run
        state.set_checkpoint(f"lineage_hash_{entity_urn}", current_hash)

        return False

    except Exception as e:
        logger.warning(f"Error checking work unit skip condition: {e}")
        # Default to not skipping on error
        return False


def extract_lineage_info(work_unit: Any) -> Optional[Dict[str, Any]]:
    """
    Extract lineage information from a work unit.

    Args:
        work_unit: Work unit to analyze

    Returns:
        Dictionary with lineage information or None
    """
    try:
        # Check if work unit contains lineage information
        if hasattr(work_unit, 'metadata'):
            metadata = work_unit.metadata

            if hasattr(metadata, 'aspects'):
                for aspect in metadata.aspects:
                    # Look for lineage aspects
                    if hasattr(aspect, 'upstreamLineage'):
                        upstream_lineage = aspect.upstreamLineage

                        # Generate hash of lineage information
                        import hashlib
                        import json

                        lineage_data = {
                            'upstreams': [u.dataset for u in
                                          upstream_lineage.upstreams] if upstream_lineage.upstreams else [],
                            'fine_grained': len(
                                upstream_lineage.fineGrainedLineages) if upstream_lineage.fineGrainedLineages else 0
                        }

                        lineage_json = json.dumps(lineage_data, sort_keys=True)
                        lineage_hash = hashlib.md5(lineage_json.encode()).hexdigest()

                        return {
                            'entity_urn': getattr(work_unit, 'id', 'unknown'),
                            'lineage_hash': lineage_hash,
                            'lineage_data': lineage_data
                        }

        return None

    except Exception as e:
        logger.debug(f"Failed to extract lineage info: {e}")
        return None


def enhance_work_unit_with_incremental_info(work_unit: Any, state: LineageState) -> Any:
    """
    Enhance work unit with incremental processing metadata.

    Args:
        work_unit: Original work unit
        state: Current lineage state

    Returns:
        Enhanced work unit
    """
    try:
        # Add incremental processing metadata
        if hasattr(work_unit, 'metadata'):
            # Add custom properties indicating incremental processing
            if hasattr(work_unit.metadata, 'customProperties'):
                work_unit.metadata.customProperties = work_unit.metadata.customProperties or {}
                work_unit.metadata.customProperties.update({
                    'incremental_lineage': 'true',
                    'processing_timestamp': datetime.now().isoformat()
                })

    except Exception as e:
        logger.debug(f"Failed to enhance work unit: {e}")

    return work_unit


def update_processing_checkpoint(state: LineageState, processed_count: int) -> None:
    """
    Update processing checkpoint with current progress.

    Args:
        state: Lineage state to update
        processed_count: Number of work units processed
    """
    state.set_checkpoint('processed_count', processed_count)
    state.set_checkpoint('last_checkpoint_time', datetime.now())


class IncrementalLineageConfig:
    """Configuration for incremental lineage processing."""

    def __init__(
            self,
            enabled: bool = True,
            checkpoint_interval: int = 100,
            max_checkpoint_age_hours: int = 24,
            force_full_refresh: bool = False
    ):
        self.enabled = enabled
        self.checkpoint_interval = checkpoint_interval
        self.max_checkpoint_age_hours = max_checkpoint_age_hours
        self.force_full_refresh = force_full_refresh


def create_incremental_lineage_processor(
        config: IncrementalLineageConfig
) -> Callable:
    """
    Create a configured incremental lineage processor.

    Args:
        config: Configuration for incremental processing

    Returns:
        Configured processor function
    """

    def processor(work_units: Iterable[Any]) -> Iterable[Any]:
        """Process work units with incremental lineage logic."""

        if not config.enabled or config.force_full_refresh:
            # Pass through all work units
            yield from work_units
            return

        state = LineageState()
        processed = 0

        for work_unit in work_units:
            if not should_skip_work_unit(work_unit, state):
                yield enhance_work_unit_with_incremental_info(work_unit, state)
                processed += 1

                if processed % config.checkpoint_interval == 0:
                    update_processing_checkpoint(state, processed)

    return processor
