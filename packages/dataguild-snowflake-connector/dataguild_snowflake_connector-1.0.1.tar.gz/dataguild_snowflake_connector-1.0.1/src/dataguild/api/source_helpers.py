"""
Source helpers and utilities for DataGuild ingestion API.

This module provides helper functions and utilities to streamline
the creation and processing of metadata work units in DataGuild sources.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Union
from functools import wraps

from dataguild.api.source import MetadataWorkUnit
from dataguild.api.common import WorkunitId
from dataguild.configuration.time_window_config import BaseTimeWindowConfig

logger = logging.getLogger(__name__)


def auto_workunit(
        work_units: Iterable[Any],
        stream: bool = True,
        auto_id: bool = True,
        treat_errors_as_warnings: bool = False
) -> Iterable[MetadataWorkUnit]:
    """
    Automatically convert objects to MetadataWorkUnit instances with enhanced capabilities.

    This function wraps any iterable of objects and converts them into proper
    MetadataWorkUnit instances with automatic ID generation, error handling,
    and metadata enhancement.

    Args:
        work_units: Iterable of objects to convert to work units
        stream: Whether to stream work units (True) or collect them first (False)
        auto_id: Whether to automatically generate IDs for work units
        treat_errors_as_warnings: Whether to treat processing errors as warnings

    Returns:
        Iterator of MetadataWorkUnit instances

    Example:
        ```
        # Convert raw metadata objects to work units
        datasets = extract_datasets_from_source()
        work_units = auto_workunit(datasets, auto_id=True)

        for wu in work_units:
            yield wu
        ```
    """
    logger.debug(f"Processing work units with auto_workunit (stream={stream}, auto_id={auto_id})")

    work_unit_count = 0
    error_count = 0

    def _process_work_unit(item: Any, index: int) -> Optional[MetadataWorkUnit]:
        """Process individual work unit item."""
        nonlocal work_unit_count, error_count

        try:
            # If already a MetadataWorkUnit, enhance it
            if isinstance(item, MetadataWorkUnit):
                work_unit = item
            else:
                # Convert to MetadataWorkUnit
                work_unit = _convert_to_work_unit(
                    item,
                    index=index,
                    auto_id=auto_id,
                    treat_errors_as_warnings=treat_errors_as_warnings
                )

            # Enhance work unit with metadata
            enhanced_work_unit = _enhance_work_unit(work_unit, index)

            work_unit_count += 1
            return enhanced_work_unit

        except Exception as e:
            error_count += 1
            error_msg = f"Error processing work unit at index {index}: {e}"

            if treat_errors_as_warnings:
                logger.warning(error_msg)
                return None
            else:
                logger.error(error_msg)
                raise

    # Process work units
    if stream:
        # Stream processing - process one at a time
        for index, item in enumerate(work_units):
            processed_wu = _process_work_unit(item, index)
            if processed_wu:
                yield processed_wu
    else:
        # Batch processing - collect all first, then yield
        collected_items = list(work_units)
        for index, item in enumerate(collected_items):
            processed_wu = _process_work_unit(item, index)
            if processed_wu:
                yield processed_wu

    logger.info(f"auto_workunit completed: {work_unit_count} work units processed, {error_count} errors")


def auto_empty_dataset_usage_statistics(
        work_units: Iterable[MetadataWorkUnit],
        config: BaseTimeWindowConfig,
        dataset_urns: Set[str]
) -> Iterable[MetadataWorkUnit]:
    """
    Automatically generate empty usage statistics for datasets with no recorded usage.

    This function wraps a work units iterator and ensures that all discovered datasets
    have usage statistics, even if they have zero usage. This provides complete
    coverage for usage analytics and prevents missing data in reports.

    Args:
        work_units: Iterator of MetadataWorkUnit instances containing usage statistics
        config: Time window configuration with start_time, end_time, and bucket_duration
        dataset_urns: Set of all dataset URNs that should have usage statistics

    Returns:
        Iterator of MetadataWorkUnit instances including empty usage for missing datasets

    Example:
        ```
        # Ensure all discovered datasets have usage statistics
        usage_work_units = extract_usage_statistics()
        complete_usage = auto_empty_dataset_usage_statistics(
            usage_work_units,
            config=BaseTimeWindowConfig(
                start_time=start_time,
                end_time=end_time,
                bucket_duration=bucket_duration
            ),
            dataset_urns=discovered_dataset_urns
        )

        for wu in complete_usage:
            yield wu
        ```
    """
    logger.debug(f"Generating empty usage statistics for {len(dataset_urns)} datasets")

    # Track which datasets we've seen usage statistics for
    seen_dataset_urns = set()
    yielded_count = 0
    empty_count = 0

    # First, yield all existing usage work units and track URNs
    for work_unit in work_units:
        yielded_count += 1

        # Extract dataset URN from the work unit
        dataset_urn = _extract_dataset_urn_from_workunit(work_unit)
        if dataset_urn:
            seen_dataset_urns.add(dataset_urn)

        yield work_unit

    # Generate empty usage statistics for datasets without usage
    missing_dataset_urns = dataset_urns - seen_dataset_urns

    logger.info(
        f"Found {len(seen_dataset_urns)} datasets with usage, "
        f"{len(missing_dataset_urns)} datasets need empty usage statistics"
    )

    for dataset_urn in missing_dataset_urns:
        try:
            empty_usage_wu = _create_empty_usage_workunit(dataset_urn, config)
            empty_count += 1
            yield empty_usage_wu

        except Exception as e:
            logger.error(f"Failed to create empty usage statistics for {dataset_urn}: {e}")

    logger.info(
        f"auto_empty_dataset_usage_statistics completed: "
        f"{yielded_count} original work units, {empty_count} empty usage work units generated"
    )


def _extract_dataset_urn_from_workunit(work_unit: MetadataWorkUnit) -> Optional[str]:
    """
    Extract dataset URN from a usage statistics work unit.

    Args:
        work_unit: MetadataWorkUnit containing usage statistics

    Returns:
        Dataset URN if found, None otherwise
    """
    try:
        # Check if work unit ID contains dataset URN
        if work_unit.id and "urn:li:dataset:" in work_unit.id:
            # Extract URN from work unit ID (common pattern)
            parts = work_unit.id.split("urn:li:dataset:")
            if len(parts) > 1:
                # Take everything after the first occurrence
                return "urn:li:dataset:" + parts[1].split("|")[0]  # Handle potential suffixes

        # Check in MCP if available
        if hasattr(work_unit, 'mcp') and work_unit.mcp:
            if hasattr(work_unit.mcp, 'entityUrn'):
                return work_unit.mcp.entityUrn
            if hasattr(work_unit.mcp, 'entity_urn'):
                return work_unit.mcp.entity_urn

        # Check in metadata
        if hasattr(work_unit, 'metadata') and work_unit.metadata:
            if hasattr(work_unit.metadata, 'urn'):
                return work_unit.metadata.urn

        # Check work unit attributes for URN-like values
        if hasattr(work_unit, '_dataset_urn'):
            return work_unit._dataset_urn

        return None

    except Exception as e:
        logger.debug(f"Error extracting dataset URN from work unit {work_unit.id}: {e}")
        return None


def _create_empty_usage_workunit(
        dataset_urn: str,
        config: BaseTimeWindowConfig
    ) -> MetadataWorkUnit:
    """
    Create a MetadataWorkUnit with empty usage statistics for a dataset.

    Args:
        dataset_urn: URN of the dataset
        config: Time window configuration

    Returns:
        MetadataWorkUnit with empty usage statistics
    """
    try:
        from dataguild.metadata.com.linkedin.pegasus2avro.dataset import DatasetUsageStatistics
        from dataguild.metadata.com.linkedin.pegasus2avro.timeseries import TimeWindowSize, TimeWindowUnit
        from dataguild.emitter.mcp import MetadataChangeProposalWrapper

        # Calculate timestamp for the usage statistics
        timestamp_millis = int(config.start_time.timestamp() * 1000)

        # Convert BucketDuration to TimeWindowUnit
        bucket_to_time_unit = {
            "MINUTE": TimeWindowUnit.MINUTE,
            "HOUR": TimeWindowUnit.HOUR,
            "DAY": TimeWindowUnit.DAY,
            "MONTH": TimeWindowUnit.MONTH,
            "QUARTER": TimeWindowUnit.MONTH,  # Map QUARTER to MONTH
            "YEAR": TimeWindowUnit.YEAR,
        }
        
        bucket_duration = getattr(config, 'bucket_duration', 'DAY')
        time_unit = bucket_to_time_unit.get(bucket_duration, TimeWindowUnit.DAY)
        
        # Create time window size from bucket duration
        time_window = TimeWindowSize(
            unit=time_unit,
            multiple=1
        )

        # Create empty usage statistics
        empty_usage_stats = DatasetUsageStatistics(
            timestampMillis=timestamp_millis,
            eventGranularity=time_window,
            totalSqlQueries=0,
            uniqueUserCount=0,
            userCounts=[],
            fieldCounts=[],
            topSqlQueries=None,
        )

        # Create metadata change proposal
        mcp = MetadataChangeProposalWrapper(
            entityUrn=dataset_urn,
            aspect=empty_usage_stats,
        )

        # Create work unit
        work_unit_id = f"empty-usage-{dataset_urn}-{timestamp_millis}"

        work_unit = MetadataWorkUnit(
            id=work_unit_id,
            mcp=mcp,
            treat_errors_as_warnings=False
        )

        # Add metadata for tracking
        work_unit._dataset_urn = dataset_urn
        work_unit._is_empty_usage = True
        work_unit._generated_timestamp = datetime.now().isoformat()

        logger.debug(f"Created empty usage work unit for dataset: {dataset_urn}")
        return work_unit
        
    except Exception as e:
        logger.error(f"Failed to create empty usage statistics for {dataset_urn}: {e}")
        logger.debug(f"Exception details:", exc_info=True)
        raise


def _convert_to_work_unit(
        item: Any,
        index: int,
        auto_id: bool = True,
        treat_errors_as_warnings: bool = False
) -> MetadataWorkUnit:
    """
    Convert an arbitrary item to a MetadataWorkUnit.

    Args:
        item: Item to convert
        index: Index of the item in the sequence
        auto_id: Whether to automatically generate an ID
        treat_errors_as_warnings: Error handling preference

    Returns:
        MetadataWorkUnit instance
    """
    # Generate work unit ID
    if auto_id:
        if hasattr(item, 'id'):
            work_unit_id = str(item.id)
        elif hasattr(item, 'urn'):
            work_unit_id = str(item.urn)
        elif hasattr(item, 'name'):
            work_unit_id = f"workunit-{item.name}-{index}"
        else:
            work_unit_id = f"workunit-{index}-{int(datetime.now().timestamp())}"
    else:
        work_unit_id = f"workunit-{index}"

    # Extract metadata if available
    metadata = None
    if hasattr(item, 'metadata'):
        metadata = item.metadata
    elif hasattr(item, 'to_metadata'):
        try:
            metadata = item.to_metadata()
        except Exception as e:
            logger.debug(f"Failed to extract metadata using to_metadata(): {e}")

    # Create MetadataWorkUnit
    work_unit = MetadataWorkUnit(
        id=work_unit_id,
        mcp=getattr(item, 'mcp', None),
        metadata=metadata,
        treat_errors_as_warnings=treat_errors_as_warnings
    )

    # Store original item reference
    work_unit._original_item = item

    return work_unit


def _enhance_work_unit(work_unit: MetadataWorkUnit, index: int) -> MetadataWorkUnit:
    """
    Enhance work unit with additional metadata and capabilities.

    Args:
        work_unit: Work unit to enhance
        index: Index of the work unit

    Returns:
        Enhanced work unit
    """
    # Add processing metadata
    processing_metadata = {
        'processing_index': index,
        'processed_timestamp': datetime.now().isoformat(),
        'processor': 'auto_workunit',
        'dataguild_version': '1.0.0'
    }

    # Add metadata to work unit if it has metadata attribute
    if hasattr(work_unit, 'metadata') and work_unit.metadata:
        if hasattr(work_unit.metadata, 'customProperties'):
            if not work_unit.metadata.customProperties:
                work_unit.metadata.customProperties = {}
            work_unit.metadata.customProperties.update(processing_metadata)

    # Add processing metadata as work unit attribute
    work_unit._processing_metadata = processing_metadata

    return work_unit


def make_dataset_workunit(
        dataset_urn: str,
        dataset_snapshot: Any,
        treat_errors_as_warnings: bool = False
) -> MetadataWorkUnit:
    """
    Create a MetadataWorkUnit for a dataset.

    Args:
        dataset_urn: URN of the dataset
        dataset_snapshot: Dataset snapshot containing metadata
        treat_errors_as_warnings: Error handling preference

    Returns:
        MetadataWorkUnit for the dataset
    """
    work_unit_id = f"dataset-{dataset_urn}"

    return MetadataWorkUnit(
        id=work_unit_id,
        metadata=dataset_snapshot,
        treat_errors_as_warnings=treat_errors_as_warnings
    )


def make_container_workunit(
        container_urn: str,
        container_snapshot: Any,
        treat_errors_as_warnings: bool = False
) -> MetadataWorkUnit:
    """
    Create a MetadataWorkUnit for a container (database, schema, etc.).

    Args:
        container_urn: URN of the container
        container_snapshot: Container snapshot containing metadata
        treat_errors_as_warnings: Error handling preference

    Returns:
        MetadataWorkUnit for the container
    """
    work_unit_id = f"container-{container_urn}"

    return MetadataWorkUnit(
        id=work_unit_id,
        metadata=container_snapshot,
        treat_errors_as_warnings=treat_errors_as_warnings
    )


def make_assertion_workunit(
        assertion_urn: str,
        assertion_info: Any,
        treat_errors_as_warnings: bool = False
) -> MetadataWorkUnit:
    """
    Create a MetadataWorkUnit for an assertion.

    Args:
        assertion_urn: URN of the assertion
        assertion_info: Assertion information
        treat_errors_as_warnings: Error handling preference

    Returns:
        MetadataWorkUnit for the assertion
    """
    work_unit_id = f"assertion-{assertion_urn}"

    return MetadataWorkUnit(
        id=work_unit_id,
        metadata=assertion_info,
        treat_errors_as_warnings=treat_errors_as_warnings
    )


def batch_workunits(
        work_units: Iterable[MetadataWorkUnit],
        batch_size: int = 100
) -> Iterable[List[MetadataWorkUnit]]:
    """
    Batch work units into groups for efficient processing.

    Args:
        work_units: Iterator of work units to batch
        batch_size: Size of each batch

    Returns:
        Iterator of work unit batches

    Example:
        ```
        work_units = auto_workunit(datasets)
        for batch in batch_workunits(work_units, batch_size=50):
            process_batch(batch)
        ```
    """
    batch = []

    for work_unit in work_units:
        batch.append(work_unit)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    # Yield remaining work units
    if batch:
        yield batch


def filter_workunits(
        work_units: Iterable[MetadataWorkUnit],
        filter_func: Callable[[MetadataWorkUnit], bool]
) -> Iterable[MetadataWorkUnit]:
    """
    Filter work units based on a predicate function.

    Args:
        work_units: Iterator of work units to filter
        filter_func: Function that returns True for work units to keep

    Returns:
        Filtered iterator of work units

    Example:
        ```
        # Only process table work units
        table_units = filter_workunits(
            work_units,
            lambda wu: 'table' in wu.id.lower()
        )
        ```
    """
    filtered_count = 0
    total_count = 0

    for work_unit in work_units:
        total_count += 1

        try:
            if filter_func(work_unit):
                filtered_count += 1
                yield work_unit
        except Exception as e:
            logger.warning(f"Error filtering work unit {work_unit.id}: {e}")

    logger.debug(f"Filtered {filtered_count}/{total_count} work units")


def transform_workunits(
        work_units: Iterable[MetadataWorkUnit],
        transform_func: Callable[[MetadataWorkUnit], MetadataWorkUnit]
) -> Iterable[MetadataWorkUnit]:
    """
    Transform work units using a transformation function.

    Args:
        work_units: Iterator of work units to transform
        transform_func: Function to transform each work unit

    Returns:
        Iterator of transformed work units

    Example:
        ```
        # Add custom properties to all work units
        def add_custom_props(wu):
            if hasattr(wu.metadata, 'customProperties'):
                wu.metadata.customProperties['source'] = 'snowflake'
            return wu

        transformed = transform_workunits(work_units, add_custom_props)
        ```
    """
    transformed_count = 0

    for work_unit in work_units:
        try:
            transformed_unit = transform_func(work_unit)
            transformed_count += 1
            yield transformed_unit
        except Exception as e:
            logger.error(f"Error transforming work unit {work_unit.id}: {e}")
            # Re-raise to maintain error handling behavior
            raise

    logger.debug(f"Transformed {transformed_count} work units")


def deduplicate_workunits(
        work_units: Iterable[MetadataWorkUnit],
        key_func: Optional[Callable[[MetadataWorkUnit], str]] = None
) -> Iterable[MetadataWorkUnit]:
    """
    Remove duplicate work units based on a key function.

    Args:
        work_units: Iterator of work units to deduplicate
        key_func: Function to extract deduplication key (defaults to work unit ID)

    Returns:
        Iterator of deduplicated work units
    """
    if key_func is None:
        key_func = lambda wu: wu.id

    seen_keys = set()
    unique_count = 0
    duplicate_count = 0

    for work_unit in work_units:
        try:
            key = key_func(work_unit)

            if key not in seen_keys:
                seen_keys.add(key)
                unique_count += 1
                yield work_unit
            else:
                duplicate_count += 1
                logger.debug(f"Skipping duplicate work unit with key: {key}")

        except Exception as e:
            logger.warning(f"Error extracting key from work unit {work_unit.id}: {e}")
            # Yield the work unit anyway to avoid losing data
            yield work_unit

    logger.debug(f"Deduplication complete: {unique_count} unique, {duplicate_count} duplicates removed")


def count_workunits(work_units: Iterable[MetadataWorkUnit]) -> Iterable[MetadataWorkUnit]:
    """
    Count work units as they pass through (useful for debugging).

    Args:
        work_units: Iterator of work units to count

    Returns:
        Iterator of work units (unchanged)
    """
    count = 0

    for work_unit in work_units:
        count += 1

        if count % 100 == 0:
            logger.info(f"Processed {count} work units")

        yield work_unit

    logger.info(f"Total work units processed: {count}")


# Utility decorators for work unit processing
def workunit_processor(
        auto_id: bool = True,
        treat_errors_as_warnings: bool = False,
        batch_size: Optional[int] = None
):
    """
    Decorator to automatically process function output as work units.

    Args:
        auto_id: Whether to automatically generate work unit IDs
        treat_errors_as_warnings: Error handling preference
        batch_size: Optional batch size for processing

    Returns:
        Decorated function that outputs MetadataWorkUnit instances

    Example:
        ```
        @workunit_processor(auto_id=True, batch_size=50)
        def extract_datasets():
            for dataset in get_datasets():
                yield dataset
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get original results
            results = func(*args, **kwargs)

            # Convert to work units
            work_units = auto_workunit(
                results,
                auto_id=auto_id,
                treat_errors_as_warnings=treat_errors_as_warnings
            )

            # Apply batching if requested
            if batch_size:
                work_units = batch_workunits(work_units, batch_size)

            return work_units

        return wrapper

    return decorator


# Helper functions for common work unit operations
def extract_urns_from_workunits(work_units: Iterable[MetadataWorkUnit]) -> List[str]:
    """Extract all URNs from work units."""
    urns = []

    for work_unit in work_units:
        if hasattr(work_unit, 'metadata') and work_unit.metadata:
            if hasattr(work_unit.metadata, 'urn'):
                urns.append(work_unit.metadata.urn)

        # Also check in work unit ID if it looks like a URN
        if work_unit.id.startswith('urn:'):
            urns.append(work_unit.id)

    return urns


def get_workunit_summary(work_units: Iterable[MetadataWorkUnit]) -> Dict[str, Any]:
    """Get summary statistics for work units."""
    summary = {
        'total_count': 0,
        'error_count': 0,
        'types': {},
        'urns': []
    }

    for work_unit in work_units:
        summary['total_count'] += 1

        if work_unit.treat_errors_as_warnings:
            summary['error_count'] += 1

        # Track work unit types
        wu_type = work_unit.id.split('-')[0] if '-' in work_unit.id else 'unknown'
        summary['types'][wu_type] = summary['types'].get(wu_type, 0) + 1

        # Collect URNs
        if work_unit.id.startswith('urn:'):
            summary['urns'].append(work_unit.id)

    return summary


# Export all functions
__all__ = [
    'auto_workunit',
    'auto_empty_dataset_usage_statistics',
    'make_dataset_workunit',
    'make_container_workunit',
    'make_assertion_workunit',
    'batch_workunits',
    'filter_workunits',
    'transform_workunits',
    'deduplicate_workunits',
    'count_workunits',
    'workunit_processor',
    'extract_urns_from_workunits',
    'get_workunit_summary',
]
