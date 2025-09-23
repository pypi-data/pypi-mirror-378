"""
Decorators for DataGuild ingestion sources.

This module provides decorators to annotate ingestion sources with
metadata about their capabilities, support status, and configuration.
"""

import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from functools import wraps

logger = logging.getLogger(__name__)


class SupportStatus(str, Enum):
    """Support status levels for ingestion sources."""
    CERTIFIED = "CERTIFIED"
    INCUBATING = "INCUBATING"
    TESTING = "TESTING"
    UNKNOWN = "UNKNOWN"
    DEPRECATED = "DEPRECATED"


def platform_name(name: str, doc_order: Optional[int] = None) -> Callable:
    """
    Decorator to specify the platform name for a source.

    Args:
        name: Human-readable platform name
        doc_order: Optional ordering for documentation

    Returns:
        Decorated class with platform name metadata
    """

    def decorator(cls: Type) -> Type:
        cls.platform_name = name
        if doc_order is not None:
            cls.doc_order = doc_order

        logger.debug(f"Registered platform name '{name}' for {cls.__name__}")
        return cls

    return decorator


def config_class(config_cls: Type) -> Callable:
    """
    Decorator to associate a configuration class with a source.

    Args:
        config_cls: Configuration class for the source

    Returns:
        Decorated class with config class metadata
    """

    def decorator(cls: Type) -> Type:
        cls.config_class = config_cls
        logger.debug(f"Registered config class {config_cls.__name__} for {cls.__name__}")
        return cls

    return decorator


def support_status(status: SupportStatus) -> Callable:
    """
    Decorator to specify support status for a source.

    Args:
        status: Support status level

    Returns:
        Decorated class with support status metadata
    """

    def decorator(cls: Type) -> Type:
        cls.support_status = status
        logger.debug(f"Set support status '{status}' for {cls.__name__}")
        return cls

    return decorator


def capability(
        capability_name: str,
        description: str,
        supported: bool = True,
        subtype_modifier: Optional[List[str]] = None
) -> Callable:
    """
    Decorator to declare a capability of a source.

    Args:
        capability_name: Name of the capability
        description: Description of the capability
        supported: Whether the capability is supported
        subtype_modifier: Optional list of subtype modifiers

    Returns:
        Decorated class with capability metadata
    """

    def decorator(cls: Type) -> Type:
        if not hasattr(cls, 'capabilities'):
            cls.capabilities = {}

        cls.capabilities[capability_name] = {
            'description': description,
            'supported': supported,
            'subtype_modifier': subtype_modifier or []
        }

        logger.debug(f"Added capability '{capability_name}' to {cls.__name__}")
        return cls

    return decorator


def source_capability(capability_name: str, **kwargs) -> Callable:
    """
    Simplified decorator for source capabilities.

    Args:
        capability_name: Name of the capability
        **kwargs: Additional capability metadata

    Returns:
        Decorated class with capability
    """

    def decorator(cls: Type) -> Type:
        if not hasattr(cls, 'source_capabilities'):
            cls.source_capabilities = set()

        cls.source_capabilities.add(capability_name)

        # Store additional metadata
        if not hasattr(cls, 'capability_metadata'):
            cls.capability_metadata = {}
        cls.capability_metadata[capability_name] = kwargs

        return cls

    return decorator


def requires_config(*required_fields: str) -> Callable:
    """
    Decorator to specify required configuration fields.

    Args:
        *required_fields: List of required field names

    Returns:
        Decorated class with required fields metadata
    """

    def decorator(cls: Type) -> Type:
        cls.required_config_fields = set(required_fields)
        return cls

    return decorator


def experimental(warning_message: Optional[str] = None) -> Callable:
    """
    Decorator to mark a source as experimental.

    Args:
        warning_message: Optional custom warning message

    Returns:
        Decorated class marked as experimental
    """

    def decorator(cls: Type) -> Type:
        cls.experimental = True
        cls.experimental_warning = (
                warning_message or
                f"{cls.__name__} is experimental and may change in future versions"
        )

        logger.warning(cls.experimental_warning)
        return cls

    return decorator


def deprecated(
        reason: str,
        alternative: Optional[str] = None,
        removal_version: Optional[str] = None
) -> Callable:
    """
    Decorator to mark a source as deprecated.

    Args:
        reason: Reason for deprecation
        alternative: Suggested alternative
        removal_version: Version when it will be removed

    Returns:
        Decorated class marked as deprecated
    """

    def decorator(cls: Type) -> Type:
        cls.deprecated = True
        cls.deprecation_reason = reason
        cls.deprecation_alternative = alternative
        cls.deprecation_removal_version = removal_version

        warning_msg = f"{cls.__name__} is deprecated: {reason}"
        if alternative:
            warning_msg += f" Use {alternative} instead."
        if removal_version:
            warning_msg += f" Will be removed in version {removal_version}."

        logger.warning(warning_msg)
        return cls

    return decorator


def metadata(**metadata_dict: Any) -> Callable:
    """
    Generic decorator to add metadata to a source class.

    Args:
        **metadata_dict: Key-value pairs of metadata

    Returns:
        Decorated class with additional metadata
    """

    def decorator(cls: Type) -> Type:
        if not hasattr(cls, '_metadata'):
            cls._metadata = {}

        cls._metadata.update(metadata_dict)
        return cls

    return decorator


def auto_work_unit_reporter(cls: Type) -> Type:
    """
    Decorator to automatically add work unit reporting capabilities.

    Args:
        cls: Source class to enhance

    Returns:
        Enhanced class with work unit reporting
    """
    original_get_workunits = getattr(cls, 'get_workunits_internal', None)

    if original_get_workunits:
        @wraps(original_get_workunits)
        def enhanced_get_workunits(self, *args, **kwargs):
            """Enhanced work unit generator with automatic reporting."""
            work_unit_count = 0

            for work_unit in original_get_workunits(self, *args, **kwargs):
                work_unit_count += 1

                # Report progress every 100 work units
                if work_unit_count % 100 == 0:
                    logger.info(f"Produced {work_unit_count} work units")

                yield work_unit

            logger.info(f"Total work units produced: {work_unit_count}")

        cls.get_workunits_internal = enhanced_get_workunits

    return cls


# Utility functions for working with decorated classes
def get_platform_name(cls: Type) -> Optional[str]:
    """Get platform name from decorated class."""
    return getattr(cls, 'platform_name', None)


def get_support_status(cls: Type) -> Optional[SupportStatus]:
    """Get support status from decorated class."""
    return getattr(cls, 'support_status', None)


def get_capabilities(cls: Type) -> Dict[str, Any]:
    """Get capabilities from decorated class."""
    return getattr(cls, 'capabilities', {})


def is_deprecated(cls: Type) -> bool:
    """Check if class is marked as deprecated."""
    return getattr(cls, 'deprecated', False)


def is_experimental(cls: Type) -> bool:
    """Check if class is marked as experimental."""
    return getattr(cls, 'experimental', False)


def get_config_class(cls: Type) -> Optional[Type]:
    """Get configuration class from decorated class."""
    return getattr(cls, 'config_class', None)


def validate_source_class(cls: Type) -> List[str]:
    """
    Validate a source class has required decorators and attributes.

    Args:
        cls: Source class to validate

    Returns:
        List of validation error messages
    """
    errors = []

    if not get_platform_name(cls):
        errors.append("Missing @platform_name decorator")

    if not get_config_class(cls):
        errors.append("Missing @config_class decorator")

    if not get_support_status(cls):
        errors.append("Missing @support_status decorator")

    if not hasattr(cls, 'get_workunits_internal'):
        errors.append("Missing get_workunits_internal method")

    return errors
