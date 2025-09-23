"""
DataGuild MCE Builder - Convenience functions for creating Metadata Change Events.

This module provides utility functions for constructing URNs (Uniform Resource Names)
and other metadata constructs used throughout DataGuild's ingestion and metadata
management systems.
"""

import hashlib
import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import quote

logger = logging.getLogger(__name__)

# Default values and constants
DEFAULT_ENV = "PROD"
DEFAULT_FLOW_CLUSTER = "prod"
UNKNOWN_USER = "urn:li:corpuser:unknown"

# URN validation patterns
URN_PATTERN = re.compile(r"^urn:li:[a-zA-Z][a-zA-Z0-9]*:")
PLATFORM_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
ASSERTION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")


def make_assertion_urn(assertion_id: str) -> str:
    """
    Construct an assertion URN from an assertion identifier.

    An assertion URN represents a data quality assertion or validation rule
    within the DataGuild metadata system.

    Args:
        assertion_id: Unique identifier for the assertion

    Returns:
        Properly formatted assertion URN

    Raises:
        ValueError: If assertion_id is invalid

    Examples:
        >>> make_assertion_urn("my_data_quality_check")
        'urn:li:assertion:my_data_quality_check'

        >>> make_assertion_urn("completeness_check_123")
        'urn:li:assertion:completeness_check_123'
    """
    if not assertion_id:
        raise ValueError("assertion_id cannot be empty")

    if not isinstance(assertion_id, str):
        raise TypeError(f"assertion_id must be a string, got {type(assertion_id)}")

    # Validate assertion ID format
    if not ASSERTION_ID_PATTERN.match(assertion_id):
        raise ValueError(
            f"Invalid assertion_id format: '{assertion_id}'. "
            "Must start with alphanumeric character and contain only alphanumeric, "
            "underscore, dot, and hyphen characters."
        )

    # URL encode to handle special characters safely
    encoded_id = quote(assertion_id, safe='_.-')

    urn = f"urn:li:assertion:{encoded_id}"
    logger.debug(f"Created assertion URN: {urn}")
    return urn


def make_data_platform_urn(platform: str) -> str:
    """
    Construct a data platform URN from a platform name.

    A data platform URN represents a data platform or data source type
    (e.g., Snowflake, BigQuery, MySQL) within the DataGuild metadata system.

    Args:
        platform: Name of the data platform

    Returns:
        Properly formatted data platform URN

    Raises:
        ValueError: If platform name is invalid

    Examples:
        >>> make_data_platform_urn("snowflake")
        'urn:li:dataPlatform:snowflake'

        >>> make_data_platform_urn("bigquery")
        'urn:li:dataPlatform:bigquery'

        >>> make_data_platform_urn("mysql")
        'urn:li:dataPlatform:mysql'
    """
    if not platform:
        raise ValueError("platform cannot be empty")

    if not isinstance(platform, str):
        raise TypeError(f"platform must be a string, got {type(platform)}")

    # Normalize platform name to lowercase
    platform = platform.lower().strip()

    # Validate platform name format
    if not PLATFORM_NAME_PATTERN.match(platform):
        raise ValueError(
            f"Invalid platform name format: '{platform}'. "
            "Must start with a letter and contain only alphanumeric, "
            "underscore, and hyphen characters."
        )

    urn = f"urn:li:dataPlatform:{platform}"
    logger.debug(f"Created data platform URN: {urn}")
    return urn


def make_dataplatform_instance_urn(platform: str, instance: str) -> str:
    """
    Construct a data platform instance URN from platform and instance names.

    A data platform instance URN represents a specific instance or deployment
    of a data platform (e.g., a specific Snowflake account, BigQuery project,
    or database cluster) within the DataGuild metadata system.

    Args:
        platform: Name of the data platform
        instance: Name or identifier of the platform instance

    Returns:
        Properly formatted data platform instance URN

    Raises:
        ValueError: If platform or instance name is invalid

    Examples:
        >>> make_dataplatform_instance_urn("snowflake", "prod_account")
        'urn:li:dataPlatformInstance:(snowflake,prod_account)'

        >>> make_dataplatform_instance_urn("bigquery", "my-gcp-project")
        'urn:li:dataPlatformInstance:(bigquery,my-gcp-project)'

        >>> make_dataplatform_instance_urn("mysql", "production_cluster")
        'urn:li:dataPlatformInstance:(mysql,production_cluster)'
    """
    if not platform:
        raise ValueError("platform cannot be empty")

    if not instance:
        raise ValueError("instance cannot be empty")

    if not isinstance(platform, str):
        raise TypeError(f"platform must be a string, got {type(platform)}")

    if not isinstance(instance, str):
        raise TypeError(f"instance must be a string, got {type(instance)}")

    # Normalize platform name to lowercase
    platform = platform.lower().strip()
    instance = instance.strip()

    # Validate platform name format
    if not PLATFORM_NAME_PATTERN.match(platform):
        raise ValueError(
            f"Invalid platform name format: '{platform}'. "
            "Must start with a letter and contain only alphanumeric, "
            "underscore, and hyphen characters."
        )

    # Validate instance name (allow more characters than platform name)
    if not instance or len(instance.strip()) == 0:
        raise ValueError("instance name cannot be empty or whitespace")

    # URL encode components to handle special characters safely
    encoded_platform = quote(platform, safe='_-')
    encoded_instance = quote(instance, safe='_.-')

    urn = f"urn:li:dataPlatformInstance:({encoded_platform},{encoded_instance})"
    logger.debug(f"Created data platform instance URN: {urn}")
    return urn


def make_dataset_urn(platform: str, name: str, env: str = DEFAULT_ENV) -> str:
    """
    Construct a dataset URN from platform, name, and environment.

    Args:
        platform: Name of the data platform
        name: Name/path of the dataset
        env: Environment (default: "PROD")

    Returns:
        Properly formatted dataset URN

    Examples:
        >>> make_dataset_urn("snowflake", "db.schema.table", "PROD")
        'urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)'
    """
    if not all([platform, name, env]):
        raise ValueError("platform, name, and env cannot be empty")

    platform_urn = make_data_platform_urn(platform)
    encoded_name = quote(name, safe='._-')

    urn = f"urn:li:dataset:({platform_urn},{encoded_name},{env.upper()})"
    logger.debug(f"Created dataset URN: {urn}")
    return urn


def make_dataset_urn_with_platform_instance(
    platform: str,
    name: str,
    platform_instance: Optional[str],
    env: str = DEFAULT_ENV
) -> str:
    """
    Construct a dataset URN with platform instance information.

    Args:
        platform: Name of the data platform
        name: Name/path of the dataset
        platform_instance: Platform instance identifier (optional)
        env: Environment (default: "PROD")

    Returns:
        Properly formatted dataset URN with platform instance

    Examples:
        >>> make_dataset_urn_with_platform_instance("bigquery", "project.dataset.table", "my-project")
        'urn:li:dataset:(urn:li:dataPlatform:bigquery,project.dataset.table,PROD)'
    """
    if platform_instance:
        # Include platform instance in the dataset name
        full_name = f"{platform_instance}.{name}" if not name.startswith(f"{platform_instance}.") else name
    else:
        full_name = name

    return make_dataset_urn(platform, full_name, env)


def make_user_urn(username: str) -> str:
    """
    Construct a user URN from a username.

    Args:
        username: Username or user identifier

    Returns:
        Properly formatted user URN

    Examples:
        >>> make_user_urn("john.doe")
        'urn:li:corpuser:john.doe'
    """
    if not username:
        raise ValueError("username cannot be empty")

    encoded_username = quote(username, safe='._-@')
    urn = f"urn:li:corpuser:{encoded_username}"
    logger.debug(f"Created user URN: {urn}")
    return urn


def make_group_urn(group_name: str) -> str:
    """
    Construct a group URN from a group name.

    Args:
        group_name: Name of the group

    Returns:
        Properly formatted group URN

    Examples:
        >>> make_group_urn("data-engineers")
        'urn:li:corpGroup:data-engineers'
    """
    if not group_name:
        raise ValueError("group_name cannot be empty")

    encoded_group = quote(group_name, safe='._-')
    urn = f"urn:li:corpGroup:{encoded_group}"
    logger.debug(f"Created group URN: {urn}")
    return urn


def make_tag_urn(tag_name: str) -> str:
    """
    Construct a tag URN from a tag name.

    Args:
        tag_name: Name of the tag

    Returns:
        Properly formatted tag URN

    Examples:
        >>> make_tag_urn("PII")
        'urn:li:tag:PII'
    """
    if not tag_name:
        raise ValueError("tag_name cannot be empty")

    encoded_tag = quote(tag_name, safe='._-')
    urn = f"urn:li:tag:{encoded_tag}"
    logger.debug(f"Created tag URN: {urn}")
    return urn


def make_domain_urn(domain_id: str) -> str:
    """
    Construct a domain URN from a domain identifier.

    Args:
        domain_id: Identifier of the domain

    Returns:
        Properly formatted domain URN

    Examples:
        >>> make_domain_urn("finance")
        'urn:li:domain:finance'
    """
    if not domain_id:
        raise ValueError("domain_id cannot be empty")

    encoded_domain = quote(domain_id, safe='._-')
    urn = f"urn:li:domain:{encoded_domain}"
    logger.debug(f"Created domain URN: {urn}")
    return urn


def make_container_urn(container_id: str) -> str:
    """
    Construct a container URN from a container identifier.

    Args:
        container_id: Identifier of the container

    Returns:
        Properly formatted container URN

    Examples:
        >>> make_container_urn("database_01")
        'urn:li:container:database_01'
    """
    if not container_id:
        raise ValueError("container_id cannot be empty")

    encoded_container = quote(container_id, safe='._-')
    urn = f"urn:li:container:{encoded_container}"
    logger.debug(f"Created container URN: {urn}")
    return urn


def get_sys_time() -> int:
    """
    Get current system time as milliseconds since epoch.

    Returns:
        Current timestamp in milliseconds

    Examples:
        >>> timestamp = get_sys_time()
        >>> print(f"Current time: {timestamp}")
    """
    return int(time.time() * 1000)


def validate_urn(urn: str) -> bool:
    """
    Validate that a string is a properly formatted URN.

    Args:
        urn: URN string to validate

    Returns:
        True if valid URN format, False otherwise

    Examples:
        >>> validate_urn("urn:li:dataset:(urn:li:dataPlatform:snowflake,db.table,PROD)")
        True
        >>> validate_urn("invalid_urn")
        False
    """
    if not isinstance(urn, str):
        return False

    return bool(URN_PATTERN.match(urn))


def extract_platform_from_dataset_urn(dataset_urn: str) -> Optional[str]:
    """
    Extract platform name from a dataset URN.

    Args:
        dataset_urn: Dataset URN to parse

    Returns:
        Platform name if found, None otherwise

    Examples:
        >>> urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.table,PROD)"
        >>> extract_platform_from_dataset_urn(urn)
        'snowflake'
    """
    if not validate_urn(dataset_urn):
        return None

    try:
        # Extract platform from dataset URN pattern
        # urn:li:dataset:(urn:li:dataPlatform:PLATFORM,name,env)
        if "urn:li:dataPlatform:" in dataset_urn:
            start = dataset_urn.find("urn:li:dataPlatform:") + len("urn:li:dataPlatform:")
            end = dataset_urn.find(",", start)
            if end > start:
                return dataset_urn[start:end]
    except Exception as e:
        logger.debug(f"Failed to extract platform from URN {dataset_urn}: {e}")

    return None


def generate_hash_id(*components: str) -> str:
    """
    Generate a deterministic hash ID from multiple string components.

    This is useful for creating consistent identifiers from multiple
    pieces of information.

    Args:
        *components: String components to hash together

    Returns:
        Hexadecimal hash string

    Examples:
        >>> generate_hash_id("platform", "dataset", "field")
        'a1b2c3d4e5f6...'
    """
    combined = "|".join(str(c) for c in components if c)
    return hashlib.md5(combined.encode('utf-8')).hexdigest()


# Utility function for creating audit stamps
def make_audit_stamp(actor: str = UNKNOWN_USER) -> Dict[str, Any]:
    """
    Create an audit stamp dictionary with current timestamp.

    Args:
        actor: URN of the actor performing the action

    Returns:
        Audit stamp dictionary

    Examples:
        >>> stamp = make_audit_stamp("urn:li:corpuser:john.doe")
        >>> print(stamp)
        {'time': 1234567890123, 'actor': 'urn:li:corpuser:john.doe'}
    """
    return {
        "time": get_sys_time(),
        "actor": actor or UNKNOWN_USER
    }


# Export all functions
__all__ = [
    'make_assertion_urn',
    'make_data_platform_urn',
    'make_dataplatform_instance_urn',
    'make_dataset_urn',
    'make_dataset_urn_with_platform_instance',
    'make_user_urn',
    'make_group_urn',
    'make_tag_urn',
    'make_domain_urn',
    'make_container_urn',
    'get_sys_time',
    'validate_urn',
    'extract_platform_from_dataset_urn',
    'generate_hash_id',
    'make_audit_stamp',
]
