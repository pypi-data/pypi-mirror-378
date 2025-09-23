"""
Incremental properties processing helper for DataGuild sources.
This module provides utilities to enable incremental property extraction,
allowing sources to process only changed property information between runs.
"""
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from functools import wraps

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PropertiesState:
    """Manages state for incremental properties processing."""

    def __init__(self):
        self.processed_entities: Set[str] = set()
        self.entity_hashes: Dict[str, str] = {}
        self.last_run_timestamp: Optional[datetime] = None
        self.checkpoints: Dict[str, Any] = {}

    def set_entity_hash(self, entity_urn: str, properties_hash: str) -> None:
        """Set properties hash for an entity."""
        self.entity_hashes[entity_urn] = properties_hash

    def get_entity_hash(self, entity_urn: str) -> Optional[str]:
        """Get stored properties hash for an entity."""
        return self.entity_hashes.get(entity_urn)

    def mark_entity_processed(self, entity_urn: str) -> None:
        """Mark entity as processed in this run."""
        self.processed_entities.add(entity_urn)

    def is_entity_processed(self, entity_urn: str) -> bool:
        """Check if entity was processed in this run."""
        return entity_urn in self.processed_entities


def auto_incremental_properties(
        enable_incremental: bool = True,
        state_provider: Optional[Any] = None
) -> Callable:
    """
    Decorator to enable incremental properties processing for work units.
    This decorator wraps work unit generators to provide incremental
    property extraction capabilities, processing only entities with
    changed properties between pipeline runs.
    Args:
        enable_incremental: Whether to enable incremental processing
        state_provider: Optional state provider for persistence
    Returns:
        Decorated function with incremental properties support
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            """Enhanced work unit generator with incremental properties."""
            if not enable_incremental:
                logger.debug("Incremental properties processing disabled")
                yield from func(self, *args, **kwargs)
                return

            logger.info("Starting incremental properties processing")

            # Initialize properties state
            properties_state = PropertiesState()

            # Load previous state if available
            if hasattr(self, 'state_provider') and self.state_provider:
                try:
                    previous_state = self.state_provider.get_state('properties')
                    if previous_state:
                        properties_state.last_run_timestamp = previous_state.get('last_run_timestamp')
                        properties_state.entity_hashes = previous_state.get('entity_hashes', {})
                        properties_state.checkpoints = previous_state.get('checkpoints', {})
                        logger.info(f"Loaded previous properties state: {len(properties_state.entity_hashes)} entities")
                except Exception as e:
                    logger.warning(f"Failed to load previous properties state: {e}")

            processed_count = 0
            skipped_count = 0

            # Process work units with incremental properties logic
            for work_unit in func(self, *args, **kwargs):
                try:
                    entity_urn = getattr(work_unit, 'id', str(work_unit))

                    # Check if properties have changed
                    if should_skip_properties_work_unit(work_unit, properties_state):
                        skipped_count += 1
                        logger.debug(f"Skipping work unit {entity_urn} (no property changes)")
                        continue

                    # Mark as processed and update hash
                    properties_state.mark_entity_processed(entity_urn)
                    update_entity_properties_hash(work_unit, properties_state)
                    processed_count += 1

                    # Enhance work unit with incremental metadata
                    enhanced_work_unit = enhance_work_unit_with_properties_info(
                        work_unit, properties_state
                    )
                    yield enhanced_work_unit

                    # Checkpoint progress
                    if processed_count % 100 == 0:
                        properties_state.checkpoints['processed_count'] = processed_count
                        logger.debug(f"Checkpoint: {processed_count} work units processed")

                except Exception as e:
                    logger.error(f"Error in incremental properties processing: {e}")
                    continue

            # Save final state
            try:
                if hasattr(self, 'state_provider') and self.state_provider:
                    final_state = {
                        'last_run_timestamp': datetime.now(),
                        'entity_hashes': properties_state.entity_hashes,
                        'processed_entities': list(properties_state.processed_entities),
                        'checkpoints': properties_state.checkpoints
                    }
                    self.state_provider.set_state('properties', final_state)
                    logger.info("Saved incremental properties state")
            except Exception as e:
                logger.error(f"Failed to save properties state: {e}")

            logger.info(
                f"Incremental properties processing complete: "
                f"{processed_count} processed, {skipped_count} skipped"
            )
        return wrapper
    return decorator


def should_skip_properties_work_unit(work_unit: Any, state: PropertiesState) -> bool:
    """
    Determine if a work unit should be skipped based on property changes.
    Args:
        work_unit: Work unit to evaluate
        state: Current properties state
    Returns:
        True if work unit should be skipped, False otherwise
    """
    try:
        entity_urn = getattr(work_unit, 'id', 'unknown')
        current_hash = compute_properties_hash(work_unit)

        if not current_hash:
            # No properties to compare, don't skip
            return False

        previous_hash = state.get_entity_hash(entity_urn)
        if previous_hash == current_hash:
            # Properties haven't changed
            return True

        return False
    except Exception as e:
        logger.warning(f"Error checking properties skip condition: {e}")
        return False


def compute_properties_hash(work_unit: Any) -> Optional[str]:
    """
    Compute hash of properties in a work unit.
    Args:
        work_unit: Work unit to analyze
    Returns:
        Hash string or None if no properties found
    """
    try:
        import hashlib
        import json

        properties_data = {}

        # Extract properties from work unit metadata
        if hasattr(work_unit, 'metadata'):
            metadata = work_unit.metadata

            # Check for dataset properties
            if hasattr(metadata, 'aspects'):
                for aspect in metadata.aspects:
                    if hasattr(aspect, 'datasetProperties'):
                        props = aspect.datasetProperties
                        properties_data.update({
                            'name': getattr(props, 'name', None),
                            'description': getattr(props, 'description', None),
                            'customProperties': getattr(props, 'customProperties', None)
                        })

                    # Check for structured properties
                    if hasattr(aspect, 'structuredProperties'):
                        struct_props = aspect.structuredProperties
                        if hasattr(struct_props, 'properties'):
                            properties_data['structuredProperties'] = [
                                {
                                    'propertyUrn': prop.propertyUrn,
                                    'values': [val.value for val in prop.values]
                                }
                                for prop in struct_props.properties
                            ]

                    # Check for global tags
                    if hasattr(aspect, 'globalTags'):
                        tags = aspect.globalTags
                        if hasattr(tags, 'tags'):
                            properties_data['globalTags'] = [tag.tag for tag in tags.tags]

        if not properties_data:
            return None

        # Generate stable hash
        properties_json = json.dumps(properties_data, sort_keys=True, default=str)
        return hashlib.md5(properties_json.encode()).hexdigest()

    except Exception as e:
        logger.debug(f"Failed to compute properties hash: {e}")
        return None


def update_entity_properties_hash(work_unit: Any, state: PropertiesState) -> None:
    """
    Update stored properties hash for an entity.
    Args:
        work_unit: Work unit to process
        state: Properties state to update
    """
    try:
        entity_urn = getattr(work_unit, 'id', 'unknown')
        properties_hash = compute_properties_hash(work_unit)
        if properties_hash:
            state.set_entity_hash(entity_urn, properties_hash)
    except Exception as e:
        logger.debug(f"Failed to update entity properties hash: {e}")


def enhance_work_unit_with_properties_info(work_unit: Any, state: PropertiesState) -> Any:
    """
    Enhance work unit with incremental properties metadata.
    Args:
        work_unit: Original work unit
        state: Current properties state
    Returns:
        Enhanced work unit
    """
    try:
        # Add incremental processing metadata
        if hasattr(work_unit, 'metadata') and hasattr(work_unit.metadata, 'customProperties'):
            if not work_unit.metadata.customProperties:
                work_unit.metadata.customProperties = {}
            work_unit.metadata.customProperties.update({
                'incremental_properties': 'true',
                'properties_processing_timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.debug(f"Failed to enhance work unit with properties info: {e}")

    return work_unit


class IncrementalPropertiesConfig(BaseModel):
    """
    Configuration for incremental properties processing.

    This configuration class controls which types of properties are included
    in the incremental processing and how the incremental logic behaves.

    Attributes:
        enabled: Enable incremental properties processing
        include_custom_properties: Include custom properties in change detection
        include_structured_properties: Include structured properties in change detection
        include_tags: Include tags in change detection
        include_glossary_terms: Include glossary terms in change detection
        force_full_refresh: Force full refresh ignoring previous state
        hash_algorithm: Algorithm to use for property change detection (default: md5)
        checkpoint_interval: Number of entities to process before checkpointing (default: 100)

    Examples:
        >>> config = IncrementalPropertiesConfig(
        ...     enabled=True,
        ...     include_custom_properties=True,
        ...     include_tags=False,
        ...     checkpoint_interval=50
        ... )
    """

    enabled: bool = Field(
        default=True,
        description="Enable incremental properties processing"
    )

    include_custom_properties: bool = Field(
        default=True,
        description="Include custom properties in change detection"
    )

    include_structured_properties: bool = Field(
        default=True,
        description="Include structured properties in change detection"
    )

    include_tags: bool = Field(
        default=True,
        description="Include tags in change detection"
    )

    include_glossary_terms: bool = Field(
        default=True,
        description="Include glossary terms in change detection"
    )

    include_ownership: bool = Field(
        default=True,
        description="Include ownership information in change detection"
    )

    force_full_refresh: bool = Field(
        default=False,
        description="Force full refresh ignoring previous state"
    )

    hash_algorithm: str = Field(
        default="md5",
        description="Hash algorithm to use for change detection (md5, sha1, sha256)"
    )

    checkpoint_interval: int = Field(
        default=100,
        description="Number of entities to process before checkpointing state"
    )

    max_state_size: int = Field(
        default=10000,
        description="Maximum number of entity hashes to keep in state"
    )

    state_cleanup_threshold: float = Field(
        default=0.8,
        description="Threshold for cleaning up old state (0.0-1.0)"
    )

    def is_incremental_enabled(self) -> bool:
        """Check if incremental processing is enabled and not forced full refresh."""
        return self.enabled and not self.force_full_refresh

    def get_included_property_types(self) -> List[str]:
        """Get list of property types included in change detection."""
        included = []
        if self.include_custom_properties:
            included.append("custom_properties")
        if self.include_structured_properties:
            included.append("structured_properties")
        if self.include_tags:
            included.append("tags")
        if self.include_glossary_terms:
            included.append("glossary_terms")
        if self.include_ownership:
            included.append("ownership")
        return included


class IncrementalPropertiesConfigMixin(BaseModel):
    """
    Mixin class that adds incremental properties configuration to source configs.

    This mixin provides a standard way to add incremental properties configuration
    to any DataGuild source configuration class, enabling sources to opt into
    incremental property extraction with customizable behavior.

    The mixin adds an `incremental_properties` field that contains all the
    configuration options for controlling incremental properties processing.

    Examples:
        >>> class MySourceConfig(IncrementalPropertiesConfigMixin):
        ...     # Other source-specific config fields
        ...     source_type: str = "my_source"
        ...     connection_url: str = "https://api.example.com"
        >>>
        >>> config = MySourceConfig(
        ...     incremental_properties=IncrementalPropertiesConfig(
        ...         enabled=True,
        ...         include_tags=False,
        ...         checkpoint_interval=50
        ...     )
        ... )
        >>>
        >>> print(f"Incremental enabled: {config.is_incremental_properties_enabled()}")
        >>> print(f"Included types: {config.get_incremental_property_types()}")
    """

    incremental_properties: Optional[IncrementalPropertiesConfig] = Field(
        default=None,
        description="Configuration for incremental properties processing"
    )

    def is_incremental_properties_enabled(self) -> bool:
        """
        Check if incremental properties processing is enabled.

        Returns:
            True if incremental properties is enabled and configured
        """
        return (
            self.incremental_properties is not None
            and self.incremental_properties.is_incremental_enabled()
        )

    def get_incremental_property_types(self) -> List[str]:
        """
        Get the list of property types included in incremental processing.

        Returns:
            List of property type names that are included in change detection
        """
        if not self.is_incremental_properties_enabled():
            return []

        return self.incremental_properties.get_included_property_types()

    def get_incremental_checkpoint_interval(self) -> int:
        """
        Get the checkpoint interval for incremental processing.

        Returns:
            Number of entities to process before checkpointing (default: 100)
        """
        if not self.is_incremental_properties_enabled():
            return 100

        return self.incremental_properties.checkpoint_interval

    def should_force_full_refresh(self) -> bool:
        """
        Check if a full refresh should be forced.

        Returns:
            True if full refresh is forced, ignoring incremental state
        """
        return (
            self.incremental_properties is not None
            and self.incremental_properties.force_full_refresh
        )

    def get_incremental_hash_algorithm(self) -> str:
        """
        Get the hash algorithm to use for change detection.

        Returns:
            Hash algorithm name (default: "md5")
        """
        if not self.is_incremental_properties_enabled():
            return "md5"

        return self.incremental_properties.hash_algorithm

    def create_default_incremental_config(self) -> IncrementalPropertiesConfig:
        """
        Create a default incremental properties configuration.

        Returns:
            Default IncrementalPropertiesConfig instance
        """
        if self.incremental_properties is None:
            self.incremental_properties = IncrementalPropertiesConfig()

        return self.incremental_properties


def extract_entity_properties(work_unit: Any, config: IncrementalPropertiesConfig) -> Dict[str, Any]:
    """
    Extract properties from a work unit based on configuration.

    This function extracts only the property types that are configured
    to be included in incremental processing, allowing for fine-grained
    control over what triggers property change detection.

    Args:
        work_unit: Work unit to extract properties from
        config: Incremental properties configuration

    Returns:
        Dictionary containing extracted properties

    Examples:
        >>> config = IncrementalPropertiesConfig(
        ...     include_tags=False,
        ...     include_custom_properties=True
        ... )
        >>> properties = extract_entity_properties(work_unit, config)
        >>> print(properties.keys())  # Won't include 'tags'
    """
    properties = {}

    if not hasattr(work_unit, 'metadata'):
        return properties

    metadata = work_unit.metadata

    # Extract based on configuration
    if config.include_custom_properties and hasattr(metadata, 'customProperties'):
        properties['custom_properties'] = metadata.customProperties

    if config.include_structured_properties and hasattr(metadata, 'structuredProperties'):
        properties['structured_properties'] = metadata.structuredProperties

    if config.include_tags and hasattr(metadata, 'globalTags'):
        properties['tags'] = [tag.tag for tag in metadata.globalTags.tags] if metadata.globalTags.tags else []

    if config.include_glossary_terms and hasattr(metadata, 'glossaryTerms'):
        properties['glossary_terms'] = [term.urn for term in metadata.glossaryTerms.terms] if metadata.glossaryTerms.terms else []

    if config.include_ownership and hasattr(metadata, 'ownership'):
        properties['ownership'] = [
            {'owner': owner.owner, 'type': owner.type}
            for owner in metadata.ownership.owners
        ] if metadata.ownership.owners else []

    return properties


def create_incremental_properties_hash(properties: Dict[str, Any], algorithm: str = "md5") -> str:
    """
    Create a hash from extracted properties using the specified algorithm.

    Args:
        properties: Extracted properties dictionary
        algorithm: Hash algorithm to use (md5, sha1, sha256)

    Returns:
        Hash string

    Raises:
        ValueError: If unsupported hash algorithm is specified
    """
    import hashlib
    import json

    # Supported algorithms
    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256
    }

    if algorithm not in algorithms:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    # Create stable JSON representation
    properties_json = json.dumps(properties, sort_keys=True, default=str)

    # Generate hash
    hash_func = algorithms[algorithm]()
    hash_func.update(properties_json.encode('utf-8'))

    return hash_func.hexdigest()


# Export all classes and functions
__all__ = [
    'PropertiesState',
    'IncrementalPropertiesConfig',
    'IncrementalPropertiesConfigMixin',
    'auto_incremental_properties',
    'should_skip_properties_work_unit',
    'compute_properties_hash',
    'update_entity_properties_hash',
    'enhance_work_unit_with_properties_info',
    'extract_entity_properties',
    'create_incremental_properties_hash',
]


# Example usage and testing (for development purposes)
if __name__ == "__main__":
    print("=== DataGuild Incremental Properties Processing Examples ===\n")

    # Example 1: Configuration mixin usage
    print("Example 1: Configuration mixin usage")

    class ExampleSourceConfig(IncrementalPropertiesConfigMixin):
        source_type: str = "example"
        connection_url: str = "https://api.example.com"

    config = ExampleSourceConfig(
        source_type="example",
        connection_url="https://api.example.com",
        incremental_properties=IncrementalPropertiesConfig(
            enabled=True,
            include_tags=False,
            checkpoint_interval=50
        )
    )

    print(f"Incremental enabled: {config.is_incremental_properties_enabled()}")
    print(f"Property types included: {config.get_incremental_property_types()}")
    print(f"Checkpoint interval: {config.get_incremental_checkpoint_interval()}")
    print(f"Hash algorithm: {config.get_incremental_hash_algorithm()}")
    print()

    # Example 2: Property extraction and hashing
    print("Example 2: Property extraction and hashing")

    # Mock work unit
    class MockWorkUnit:
        def __init__(self):
            self.id = "test_entity"
            self.metadata = MockMetadata()

    class MockMetadata:
        def __init__(self):
            self.customProperties = {"key1": "value1", "key2": "value2"}

    work_unit = MockWorkUnit()

    # Extract properties
    properties = extract_entity_properties(work_unit, config.incremental_properties)
    print(f"Extracted properties: {properties}")

    # Create hash
    hash_value = create_incremental_properties_hash(properties, "md5")
    print(f"Properties hash: {hash_value}")
    print()

    # Example 3: State management
    print("Example 3: State management")

    state = PropertiesState()
    state.set_entity_hash("test_entity", hash_value)
    state.mark_entity_processed("test_entity")

    print(f"Entity processed: {state.is_entity_processed('test_entity')}")
    print(f"Stored hash: {state.get_entity_hash('test_entity')}")
    print(f"Total entities in state: {len(state.entity_hashes)}")
