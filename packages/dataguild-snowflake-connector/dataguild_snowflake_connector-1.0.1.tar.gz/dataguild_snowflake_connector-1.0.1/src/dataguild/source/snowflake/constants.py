"""
DataGuild Snowflake Constants

Clean and comprehensive constants definitions for Snowflake integration in DataGuild.
Provides standardized enumerations, mappings, and configuration values used across
the Snowflake connector components.

Author: DataGuild Engineering Team
"""

import enum
from typing import Tuple, List


class StrEnum(str, enum.Enum):
    """String enumeration base class for consistent string-based enums."""

    def __str__(self) -> str:
        return self.value


class SnowflakeCloudProvider(StrEnum):
    """Supported Snowflake cloud providers."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class SnowflakeEdition(StrEnum):
    """Snowflake account editions with different feature capabilities."""
    STANDARD = "Standard"
    ENTERPRISE = "Enterprise or above"


class SnowflakeObjectDomain(StrEnum):
    """Snowflake object domains for access history and metadata extraction."""
    TABLE = "table"
    EXTERNAL_TABLE = "external table"
    VIEW = "view"
    MATERIALIZED_VIEW = "materialized view"
    DATABASE = "database"
    SCHEMA = "schema"
    COLUMN = "column"
    ICEBERG_TABLE = "iceberg table"
    STREAM = "stream"
    PROCEDURE = "procedure"
    DYNAMIC_TABLE = "dynamic table"


# Default configurations
SNOWFLAKE_DEFAULT_CLOUD = SnowflakeCloudProvider.AWS
DEFAULT_SNOWFLAKE_DOMAIN = "snowflakecomputing.com"

# Standard Snowflake system database
SNOWFLAKE_DATABASE = "SNOWFLAKE"

# Region mapping for special cases where standard format doesn't apply
# Format: region_identifier -> (cloud_provider, normalized_region)
# See: https://docs.snowflake.com/en/user-guide/admin-account-identifier#non-vps-account-locator-formats-by-cloud-platform-and-region
SNOWFLAKE_REGION_CLOUD_REGION_MAPPING = {
    # AWS special cases
    "aws_us_east_1_gov": (SnowflakeCloudProvider.AWS, "us-east-1"),

    # Azure region mappings
    "azure_westus2": (SnowflakeCloudProvider.AZURE, "west-us-2"),
    "azure_centralus": (SnowflakeCloudProvider.AZURE, "central-us"),
    "azure_southcentralus": (SnowflakeCloudProvider.AZURE, "south-central-us"),
    "azure_eastus2": (SnowflakeCloudProvider.AZURE, "east-us-2"),
    "azure_usgovvirginia": (SnowflakeCloudProvider.AZURE, "us-gov-virginia"),
    "azure_canadacentral": (SnowflakeCloudProvider.AZURE, "canada-central"),
    "azure_uksouth": (SnowflakeCloudProvider.AZURE, "uk-south"),
    "azure_northeurope": (SnowflakeCloudProvider.AZURE, "north-europe"),
    "azure_westeurope": (SnowflakeCloudProvider.AZURE, "west-europe"),
    "azure_switzerlandnorth": (SnowflakeCloudProvider.AZURE, "switzerland-north"),
    "azure_uaenorth": (SnowflakeCloudProvider.AZURE, "uae-north"),
    "azure_centralindia": (SnowflakeCloudProvider.AZURE, "central-india"),
    "azure_japaneast": (SnowflakeCloudProvider.AZURE, "japan-east"),
    "azure_southeastasia": (SnowflakeCloudProvider.AZURE, "southeast-asia"),
    "azure_australiaeast": (SnowflakeCloudProvider.AZURE, "australia-east"),
}

# Error handling constants
GENERIC_PERMISSION_ERROR_KEY = "permission-error"
LINEAGE_PERMISSION_ERROR = "lineage-permission-error"

# Snowflake connection configuration parameters
# See: https://docs.snowflake.com/en/user-guide/python-connector-api.html#connect
CLIENT_PREFETCH_THREADS = "client_prefetch_threads"
CLIENT_SESSION_KEEP_ALIVE = "client_session_keep_alive"


# Utility functions for working with constants

def get_cloud_provider_from_region(region: str) -> Tuple[SnowflakeCloudProvider, str]:
    """
    Extract cloud provider and normalized region from Snowflake region identifier.

    Args:
        region: Snowflake region identifier (e.g., "aws_us_west_2", "azure_westus2")

    Returns:
        Tuple of (cloud_provider, normalized_region)

    Raises:
        ValueError: If region format is not recognized
    """
    # Check special mappings first
    if region in SNOWFLAKE_REGION_CLOUD_REGION_MAPPING:
        return SNOWFLAKE_REGION_CLOUD_REGION_MAPPING[region]

    # Handle standard format: {provider}_{region_with_underscores}
    if region.startswith(("aws_", "gcp_", "azure_")):
        parts = region.split("_", 1)
        if len(parts) == 2:
            cloud_provider = SnowflakeCloudProvider(parts[0])
            normalized_region = parts[1].replace("_", "-")
            return cloud_provider, normalized_region

    raise ValueError(f"Unknown or invalid Snowflake region format: {region}")


def is_system_object_domain(domain: str) -> bool:
    """
    Check if an object domain represents a system/metadata object.

    Args:
        domain: Object domain string

    Returns:
        True if domain represents system objects
    """
    system_domains = {
        SnowflakeObjectDomain.DATABASE,
        SnowflakeObjectDomain.SCHEMA,
        SnowflakeObjectDomain.COLUMN
    }

    return domain.lower() in {d.value.lower() for d in system_domains}


def is_data_object_domain(domain: str) -> bool:
    """
    Check if an object domain represents a data object (table, view, etc.).

    Args:
        domain: Object domain string

    Returns:
        True if domain represents data objects
    """
    data_domains = {
        SnowflakeObjectDomain.TABLE,
        SnowflakeObjectDomain.EXTERNAL_TABLE,
        SnowflakeObjectDomain.VIEW,
        SnowflakeObjectDomain.MATERIALIZED_VIEW,
        SnowflakeObjectDomain.ICEBERG_TABLE,
        SnowflakeObjectDomain.DYNAMIC_TABLE,
        SnowflakeObjectDomain.STREAM
    }

    return domain.lower() in {d.value.lower() for d in data_domains}


def get_supported_object_domains() -> List[str]:
    """
    Get list of all supported Snowflake object domains.

    Returns:
        List of supported object domain strings
    """
    return [domain.value for domain in SnowflakeObjectDomain]


def validate_cloud_provider(provider: str) -> bool:
    """
    Validate if a cloud provider string is supported.

    Args:
        provider: Cloud provider string

    Returns:
        True if provider is supported
    """
    try:
        SnowflakeCloudProvider(provider.lower())
        return True
    except ValueError:
        return False


def get_default_domain_for_cloud(cloud_provider: SnowflakeCloudProvider) -> str:
    """
    Get default Snowflake domain for a cloud provider.

    Args:
        cloud_provider: Cloud provider enum

    Returns:
        Default domain string for the cloud provider
    """
    # Most regions use the standard domain
    # Special cases can be added here if needed
    if cloud_provider == SnowflakeCloudProvider.AWS:
        return DEFAULT_SNOWFLAKE_DOMAIN
    elif cloud_provider == SnowflakeCloudProvider.GCP:
        return DEFAULT_SNOWFLAKE_DOMAIN
    elif cloud_provider == SnowflakeCloudProvider.AZURE:
        return DEFAULT_SNOWFLAKE_DOMAIN
    else:
        return DEFAULT_SNOWFLAKE_DOMAIN


# Connection parameter defaults
DEFAULT_CONNECTION_PARAMS = {
    CLIENT_PREFETCH_THREADS: 4,
    CLIENT_SESSION_KEEP_ALIVE: True,
}
