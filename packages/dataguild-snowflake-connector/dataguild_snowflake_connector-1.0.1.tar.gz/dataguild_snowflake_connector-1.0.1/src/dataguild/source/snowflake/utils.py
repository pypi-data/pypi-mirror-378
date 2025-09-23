"""
DataGuild Snowflake utilities for URL building, filtering, and identifier management.

This module provides comprehensive utilities for Snowflake ingestion including
URL construction for Snowsight, dataset filtering, identifier building, and
common functionality mixins.
"""

import abc
import logging
from functools import cached_property
from typing import ClassVar, List, Literal, Optional, Tuple

from dataguild.configuration.pattern_utils import is_schema_allowed as is_schema_allowed_pattern
from dataguild.emitter.mce_builder import (
    make_dataset_urn_with_platform_instance,
)
from dataguild.emitter.mcp_builder import DatabaseKey, SchemaKey
from dataguild.api.source import SourceReport
from dataguild.source.snowflake.constants import (
    DEFAULT_SNOWFLAKE_DOMAIN,
    SNOWFLAKE_REGION_CLOUD_REGION_MAPPING,
    SnowflakeCloudProvider,
    SnowflakeObjectDomain,
)
from dataguild.source.snowflake.config import (
    SnowflakeFilterConfig,
    SnowflakeIdentifierConfig,
    SnowflakeV2Config,
)
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.sql.sql_utils import gen_database_key, gen_schema_key

logger = logging.getLogger(__name__)


class SnowflakeStructuredReportMixin(abc.ABC):
    """
    Abstract mixin for classes that provide structured reporting capabilities.

    This mixin ensures that implementing classes provide access to a structured
    reporter for consistent logging and error reporting across Snowflake operations.
    """

    @property
    @abc.abstractmethod
    def structured_reporter(self) -> SourceReport:
        """Get the structured reporter instance for this class."""
        ...


class SnowsightUrlBuilder:
    """
    Builder class for constructing Snowsight URLs for Snowflake objects.

    This class handles the complex logic of building proper Snowsight URLs
    for different cloud providers, regions, and account configurations.
    """

    CLOUD_REGION_IDS_WITHOUT_CLOUD_SUFFIX: ClassVar = [
        "us-west-2",
        "us-east-1",
        "eu-west-1",
        "eu-central-1",
        "ap-southeast-2",
    ]

    def __init__(
        self,
        account_locator: str,
        region: str,
        privatelink: bool = False,
        snowflake_domain: str = DEFAULT_SNOWFLAKE_DOMAIN,
    ):
        """
        Initialize the URL builder with account and region information.

        Args:
            account_locator: Snowflake account locator
            region: Snowflake region identifier
            privatelink: Whether to use private link URLs
            snowflake_domain: Base Snowflake domain
        """
        cloud, cloud_region_id = self.get_cloud_region_from_snowflake_region_id(region)
        self.snowsight_base_url = self.create_snowsight_base_url(
            account_locator, cloud_region_id, cloud, privatelink, snowflake_domain
        )
        logger.debug(f"Initialized SnowsightUrlBuilder with base URL: {self.snowsight_base_url}")

    @staticmethod
    def create_snowsight_base_url(
        account_locator: str,
        cloud_region_id: str,
        cloud: str,
        privatelink: bool = False,
        snowflake_domain: str = DEFAULT_SNOWFLAKE_DOMAIN,
    ) -> str:
        """
        Create the base Snowsight URL for the given account and region.

        Args:
            account_locator: Snowflake account locator
            cloud_region_id: Cloud region identifier
            cloud: Cloud provider name
            privatelink: Whether to use private link
            snowflake_domain: Base Snowflake domain

        Returns:
            Base Snowsight URL string
        """
        url_cloud_provider_suffix = ""

        if cloud:
            url_cloud_provider_suffix = f".{cloud}"

        if cloud == SnowflakeCloudProvider.AWS:
            # Some AWS regions do not have cloud suffix
            # https://docs.snowflake.com/en/user-guide/admin-account-identifier#non-vps-account-locator-formats-by-cloud-platform-and-region
            if (
                cloud_region_id
                in SnowsightUrlBuilder.CLOUD_REGION_IDS_WITHOUT_CLOUD_SUFFIX
            ):
                url_cloud_provider_suffix = ""
            else:
                url_cloud_provider_suffix = f".{cloud}"

        if privatelink:
            url = f"https://app.{account_locator}.{cloud_region_id}.privatelink.{snowflake_domain}/"
        else:
            # Standard Snowsight URL format - works for most regions
            # China region may use app.snowflake.cn instead of app.snowflake.com
            if snowflake_domain == "snowflakecomputing.cn":
                url = f"https://app.snowflake.cn/{cloud_region_id}{url_cloud_provider_suffix}/{account_locator}/"
            else:
                url = f"https://app.snowflake.com/{cloud_region_id}{url_cloud_provider_suffix}/{account_locator}/"

        return url

    @staticmethod
    def get_cloud_region_from_snowflake_region_id(region: str) -> Tuple[str, str]:
        """
        Extract cloud provider and region from Snowflake region identifier.

        Args:
            region: Snowflake region identifier

        Returns:
            Tuple of (cloud_provider, cloud_region_id)

        Raises:
            ValueError: If the region format is not recognized
        """
        if region in SNOWFLAKE_REGION_CLOUD_REGION_MAPPING:
            cloud, cloud_region_id = SNOWFLAKE_REGION_CLOUD_REGION_MAPPING[region]
        elif region.startswith(("aws_", "gcp_", "azure_")):
            # e.g. aws_us_west_2, gcp_us_central1, azure_northeurope
            cloud, cloud_region_id = region.split("_", 1)
            cloud_region_id = cloud_region_id.replace("_", "-")
        else:
            raise ValueError(f"Unknown Snowflake region: {region}")

        return cloud, cloud_region_id

    def get_external_url_for_table(
        self,
        table_name: str,
        schema_name: str,
        db_name: str,
        domain: Literal[
            SnowflakeObjectDomain.TABLE,
            SnowflakeObjectDomain.VIEW,
            SnowflakeObjectDomain.DYNAMIC_TABLE,
        ],
    ) -> Optional[str]:
        """
        Generate Snowsight URL for a table, view, or dynamic table.

        Args:
            table_name: Name of the table/view
            schema_name: Name of the schema
            db_name: Name of the database
            domain: Type of object (table, view, dynamic_table)

        Returns:
            Snowsight URL for the object
        """
        # For dynamic tables, use the dynamic-table domain in the URL path
        url_domain = (
            "dynamic-table"
            if domain == SnowflakeObjectDomain.DYNAMIC_TABLE
            else str(domain)
        )

        url = f"{self.snowsight_base_url}#/data/databases/{db_name}/schemas/{schema_name}/{url_domain}/{table_name}/"
        logger.debug(f"Generated table URL: {url}")
        return url

    def get_external_url_for_schema(
        self, schema_name: str, db_name: str
    ) -> Optional[str]:
        """
        Generate Snowsight URL for a schema.

        Args:
            schema_name: Name of the schema
            db_name: Name of the database

        Returns:
            Snowsight URL for the schema
        """
        url = f"{self.snowsight_base_url}#/data/databases/{db_name}/schemas/{schema_name}/"
        logger.debug(f"Generated schema URL: {url}")
        return url

    def get_external_url_for_database(self, db_name: str) -> Optional[str]:
        """
        Generate Snowsight URL for a database.

        Args:
            db_name: Name of the database

        Returns:
            Snowsight URL for the database
        """
        url = f"{self.snowsight_base_url}#/data/databases/{db_name}/"
        logger.debug(f"Generated database URL: {url}")
        return url


class SnowflakeFilter:
    """
    Filter class for determining which Snowflake objects should be ingested.

    This class implements the filtering logic based on configuration patterns
    for databases, schemas, tables, views, streams, and procedures.
    """

    def __init__(
        self, filter_config: SnowflakeFilterConfig, structured_reporter: SourceReport
    ) -> None:
        """
        Initialize the filter with configuration and reporter.

        Args:
            filter_config: Filter configuration with patterns
            structured_reporter: Reporter for logging filter decisions
        """
        self.filter_config = filter_config
        self.structured_reporter = structured_reporter
        logger.debug(f"Initialized SnowflakeFilter with config: {filter_config}")

    def is_dataset_pattern_allowed(
        self,
        dataset_name: Optional[str],
        dataset_type: Optional[str],
    ) -> bool:
        """
        Check if a dataset should be included based on filter patterns.

        Args:
            dataset_name: Fully qualified dataset name
            dataset_type: Type of dataset (table, view, etc.)

        Returns:
            True if the dataset should be included, False otherwise
        """
        if not dataset_type or not dataset_name:
            return True

        # Check if dataset type is supported
        if dataset_type.lower() not in (
            SnowflakeObjectDomain.TABLE,
            SnowflakeObjectDomain.EXTERNAL_TABLE,
            SnowflakeObjectDomain.VIEW,
            SnowflakeObjectDomain.MATERIALIZED_VIEW,
            SnowflakeObjectDomain.ICEBERG_TABLE,
            SnowflakeObjectDomain.STREAM,
            SnowflakeObjectDomain.DYNAMIC_TABLE,
        ):
            logger.debug(f"Unsupported dataset type: {dataset_type}")
            return False

        # Skip system tables
        if _is_sys_table(dataset_name):
            logger.debug(f"Skipping system table: {dataset_name}")
            return False

        # Parse qualified name
        dataset_params = split_qualified_name(dataset_name)
        if len(dataset_params) != 3:
            self.structured_reporter.report_warning(
                "UNEXPECTED_DATASET_PATTERN",
                f"Found a {dataset_type} with an unexpected number of parts. "
                f"Database and schema filtering will not work as expected, "
                f"but table filtering will still work. Dataset: {dataset_name}"
            )

        # Check database pattern
        if (
            len(dataset_params) >= 1
            and not self.filter_config.database_pattern.allowed(
                dataset_params[0].strip('"')
            )
        ):
            logger.debug(f"Database pattern filtered out: {dataset_params[0]}")
            return False

        # Check schema pattern
        if (
            len(dataset_params) >= 2
            and not is_schema_allowed_pattern(
                self.filter_config.schema_pattern,
                dataset_params[1].strip('"'),
                dataset_params[0].strip('"'),
                self.filter_config.match_fully_qualified_names,
            )
        ):
            logger.debug(f"Schema pattern filtered out: {dataset_params[1]}")
            return False

        # Check table pattern
        if dataset_type.lower() in {
            SnowflakeObjectDomain.TABLE,
            SnowflakeObjectDomain.DYNAMIC_TABLE,
        } and not self.filter_config.table_pattern.allowed(
            _cleanup_qualified_name(dataset_name, self.structured_reporter)
        ):
            logger.debug(f"Table pattern filtered out: {dataset_name}")
            return False

        # Check view pattern
        if dataset_type.lower() in {
            SnowflakeObjectDomain.VIEW,
            SnowflakeObjectDomain.MATERIALIZED_VIEW,
        } and not self.filter_config.view_pattern.allowed(
            _cleanup_qualified_name(dataset_name, self.structured_reporter)
        ):
            logger.debug(f"View pattern filtered out: {dataset_name}")
            return False

        # Check stream pattern
        if (
            dataset_type.lower() == SnowflakeObjectDomain.STREAM
            and not self.filter_config.stream_pattern.allowed(
                _cleanup_qualified_name(dataset_name, self.structured_reporter)
            )
        ):
            logger.debug(f"Stream pattern filtered out: {dataset_name}")
            return False

        return True

    def is_procedure_allowed(self, procedure_name: str) -> bool:
        """
        Check if a procedure should be included based on filter patterns.

        Args:
            procedure_name: Name of the procedure

        Returns:
            True if the procedure should be included, False otherwise
        """
        allowed = self.filter_config.procedure_pattern.allowed(procedure_name)
        logger.debug(f"Procedure {procedure_name} allowed: {allowed}")
        return allowed

    def is_schema_allowed(self, schema_name: str, db_name: str) -> bool:
        """
        Check if a schema should be included based on filter patterns.

        Args:
            schema_name: Name of the schema
            db_name: Name of the database

        Returns:
            True if the schema should be included, False otherwise
        """
        try:
            # Use the imported is_schema_allowed function from pattern_utils
            allowed = is_schema_allowed_pattern(
                self.filter_config.schema_pattern,
                schema_name,
                db_name,
                self.filter_config.match_fully_qualified_names,
            )
            logger.info(f"Schema filtering check: {db_name}.{schema_name} -> allowed: {allowed}")
            logger.debug(f"Schema {db_name}.{schema_name} allowed: {allowed}")
            return allowed
        except Exception as e:
            logger.error(f"Error checking schema allowance for {db_name}.{schema_name}: {e}")
            return False


class SnowflakeIdentifierBuilder:
    """
    Builder class for constructing DataGuild identifiers and URNs for Snowflake objects.

    This class handles identifier normalization, URN generation, and manages
    platform-specific identifier rules.
    """

    platform = "snowflake"

    def __init__(
        self,
        identifier_config: SnowflakeIdentifierConfig,
        structured_reporter: SourceReport,
    ) -> None:
        """
        Initialize the identifier builder with configuration and reporter.

        Args:
            identifier_config: Configuration for identifier handling
            structured_reporter: Reporter for logging identifier operations
        """
        self.identifier_config = identifier_config
        self.structured_reporter = structured_reporter
        logger.debug(f"Initialized SnowflakeIdentifierBuilder with config: {identifier_config}")

    def snowflake_identifier(self, identifier: str) -> str:
        """
        Normalize a Snowflake identifier according to configuration.

        Args:
            identifier: Raw identifier string

        Returns:
            Normalized identifier
        """
        # Convert to lowercase for consistency with older connector behavior
        if self.identifier_config.convert_urns_to_lowercase:
            return identifier.lower()
        return identifier

    def get_dataset_identifier(
        self, table_name: str, schema_name: str, db_name: str
    ) -> str:
        """
        Generate a dataset identifier from table, schema, and database names.

        Args:
            table_name: Name of the table
            schema_name: Name of the schema
            db_name: Name of the database

        Returns:
            Formatted dataset identifier
        """
        identifier = self.snowflake_identifier(
            _combine_identifier_parts(
                table_name=table_name, schema_name=schema_name, db_name=db_name
            )
        )
        logger.debug(f"Generated dataset identifier: {identifier}")
        return identifier

    def gen_dataset_urn(self, dataset_identifier: str) -> str:
        """
        Generate a DataGuild URN for a dataset.

        Args:
            dataset_identifier: Dataset identifier

        Returns:
            DataGuild URN for the dataset
        """
        urn = make_dataset_urn_with_platform_instance(
            platform=self.platform,
            name=dataset_identifier,
            platform_instance=self.identifier_config.platform_instance,
            env=self.identifier_config.env,
        )
        logger.debug(f"Generated dataset URN: {urn}")
        return urn

    def get_dataset_identifier_from_qualified_name(self, qualified_name: str) -> str:
        """
        Generate dataset identifier from a qualified name.

        Args:
            qualified_name: Fully qualified object name

        Returns:
            Normalized dataset identifier
        """
        identifier = self.snowflake_identifier(
            _cleanup_qualified_name(qualified_name, self.structured_reporter)
        )
        logger.debug(f"Generated identifier from qualified name {qualified_name}: {identifier}")
        return identifier

    @staticmethod
    def get_quoted_identifier_for_database(db_name: str) -> str:
        """
        Generate quoted identifier for database.

        Args:
            db_name: Database name

        Returns:
            Quoted database identifier
        """
        return f'"{db_name}"'

    @staticmethod
    def get_quoted_identifier_for_schema(db_name: str, schema_name: str) -> str:
        """
        Generate quoted identifier for schema.

        Args:
            db_name: Database name
            schema_name: Schema name

        Returns:
            Quoted schema identifier
        """
        return f'"{db_name}"."{schema_name}"'

    @staticmethod
    def get_quoted_identifier_for_table(
        db_name: str, schema_name: str, table_name: str
    ) -> str:
        """
        Generate quoted identifier for table.

        Args:
            db_name: Database name
            schema_name: Schema name
            table_name: Table name

        Returns:
            Quoted table identifier
        """
        return f'"{db_name}"."{schema_name}"."{table_name}"'

    def get_user_identifier(
        self,
        user_name: str,
        user_email: Optional[str],
    ) -> str:
        """
        Generate user identifier for Snowflake user.

        Args:
            user_name: Snowflake user name
            user_email: User email address (optional)

        Returns:
            User identifier for URN generation
        """
        if user_email:
            identifier = self.snowflake_identifier(user_email)
        else:
            if self.identifier_config.email_domain is not None:
                identifier = self.snowflake_identifier(
                    f"{user_name}@{self.identifier_config.email_domain}"
                )
            else:
                identifier = self.snowflake_identifier(user_name)

        logger.debug(f"Generated user identifier for {user_name}: {identifier}")
        return identifier

    def gen_schema_key(self, db_name: str, schema_name: str) -> SchemaKey:
        """
        Generate schema key for DataGuild.

        Args:
            db_name: Database name
            schema_name: Schema name

        Returns:
            Schema key object
        """
        return SchemaKey(
            database_name=self.snowflake_identifier(db_name),
            schema_name=self.snowflake_identifier(schema_name)
        )

    def gen_database_key(self, db_name: str) -> DatabaseKey:
        """
        Generate database key for DataGuild.

        Args:
            db_name: Database name

        Returns:
            Database key object
        """
        return gen_database_key(
            self.snowflake_identifier(db_name)
        )


class SnowflakeCommonMixin(SnowflakeStructuredReportMixin):
    """
    Common mixin for Snowflake ingestion classes.

    This mixin provides shared functionality for Snowflake sources including
    identifier building, reporting, and common configuration access.
    """

    platform = "snowflake"
    config: SnowflakeV2Config
    report: SnowflakeV2Report

    @property
    def structured_reporter(self) -> SourceReport:
        """Get the structured reporter instance."""
        return self.report

    @cached_property
    def identifiers(self) -> SnowflakeIdentifierBuilder:
        """Get the identifier builder instance."""
        return SnowflakeIdentifierBuilder(self.config, self.report)

    @cached_property
    def snowsight_url_builder(self) -> Optional[SnowsightUrlBuilder]:
        """Get the Snowsight URL builder instance."""
        try:
            if hasattr(self.config, 'account_locator') and hasattr(self.config, 'region'):
                return SnowsightUrlBuilder(
                    account_locator=self.config.account_locator,
                    region=self.config.region,
                    privatelink=getattr(self.config, 'privatelink', False),
                    snowflake_domain=getattr(self.config, 'snowflake_domain', DEFAULT_SNOWFLAKE_DOMAIN),
                )
        except Exception as e:
            logger.warning(f"Failed to create SnowsightUrlBuilder: {e}")
            return None
        return None

    @cached_property
    def snowflake_filter(self) -> SnowflakeFilter:
        """Get the Snowflake filter instance."""
        return SnowflakeFilter(self.config.filter_config, self.report)

    def warn_if_stateful_else_error(self, key: str, reason: str) -> None:
        """
        Log a warning if stateful ingestion is enabled, otherwise log an error.

        This method provides different error handling behavior based on whether
        stateful ingestion is enabled, allowing for more graceful degradation
        when stateful checkpoints can handle partial failures.

        Args:
            key: Error/warning key for categorization
            reason: Description of the issue
        """
        # Check if any stateful features are enabled
        stateful_enabled = (
            (hasattr(self.config, 'stateful_usage') and self.config.stateful_usage and self.config.stateful_usage.enabled) or
            (hasattr(self.config, 'stateful_lineage') and self.config.stateful_lineage and self.config.stateful_lineage.enabled) or
            (hasattr(self.config, 'stateful_profiling') and self.config.stateful_profiling and self.config.stateful_profiling.enabled)
        )
        
        if stateful_enabled:
            self.structured_reporter.report_warning(key, reason)
            logger.warning(f"Stateful ingestion warning [{key}]: {reason}")
        else:
            # Use the correct method signature for report_failure
            if hasattr(self.structured_reporter, 'report_failure'):
                # Try the 2-parameter version first
                try:
                    self.structured_reporter.report_failure(key, reason)
                except TypeError:
                    # Fallback to 1-parameter version
                    self.structured_reporter.report_failure(f"{key}: {reason}")
            else:
                logger.error(f"Ingestion error [{key}]: {reason}")

    def get_dataset_urn(self, table_name: str, schema_name: str, db_name: str) -> str:
        """
        Generate dataset URN for a Snowflake object.

        Args:
            table_name: Name of the table
            schema_name: Name of the schema
            db_name: Name of the database

        Returns:
            DataGuild URN for the dataset
        """
        dataset_identifier = self.identifiers.get_dataset_identifier(
            table_name, schema_name, db_name
        )
        return self.identifiers.gen_dataset_urn(dataset_identifier)

    def get_external_url(
        self,
        table_name: str,
        schema_name: str,
        db_name: str,
        domain: str = SnowflakeObjectDomain.TABLE
    ) -> Optional[str]:
        """
        Generate external URL for a Snowflake object.

        Args:
            table_name: Name of the table
            schema_name: Name of the schema
            db_name: Name of the database
            domain: Type of object

        Returns:
            External URL if URL builder is available, None otherwise
        """
        if self.snowsight_url_builder:
            return self.snowsight_url_builder.get_external_url_for_table(
                table_name, schema_name, db_name, domain
            )
        return None


# Helper functions
def _combine_identifier_parts(*, table_name: str, schema_name: str, db_name: str) -> str:
    """
    Combine database, schema, and table names into a qualified identifier.

    Args:
        table_name: Name of the table
        schema_name: Name of the schema
        db_name: Name of the database

    Returns:
        Fully qualified identifier
    """
    return f"{db_name}.{schema_name}.{table_name}"


def _is_sys_table(table_name: str) -> bool:
    """
    Check if a table name represents a system table.

    System tables often look like `SYS$_UNPIVOT_VIEW1737` or `sys$_pivot_view19`.

    Args:
        table_name: Name of the table to check

    Returns:
        True if the table is a system table, False otherwise
    """
    return table_name.lower().startswith("sys$")


def split_qualified_name(qualified_name: str) -> List[str]:
    """
    Split a qualified name into its constituent parts, handling quoted identifiers.

    Examples:
        >>> split_qualified_name("db.my_schema.my_table")
        ['db', 'my_schema', 'my_table']
        >>> split_qualified_name('"db"."my_schema"."my_table"')
        ['db', 'my_schema', 'my_table']
        >>> split_qualified_name('TEST_DB.TEST_SCHEMA."TABLE.WITH.DOTS"')
        ['TEST_DB', 'TEST_SCHEMA', 'TABLE.WITH.DOTS']
        >>> split_qualified_name('TEST_DB."SCHEMA.WITH.DOTS".MY_TABLE')
        ['TEST_DB', 'SCHEMA.WITH.DOTS', 'MY_TABLE']

    Args:
        qualified_name: Qualified name to split

    Returns:
        List of name parts without quotes
    """
    # Fast path - no quotes
    if '"' not in qualified_name:
        return qualified_name.split(".")

    # First pass - split on dots that are not inside quotes
    in_quote = False
    parts: List[List[str]] = [[]]

    for char in qualified_name:
        if char == '"':
            in_quote = not in_quote
        elif char == "." and not in_quote:
            parts.append([])
        else:
            parts[-1].append(char)

    # Second pass - remove outer pairs of quotes
    result = []
    for part in parts:
        if len(part) > 2 and part[0] == '"' and part[-1] == '"':
            part = part[1:-1]
        result.append("".join(part))

    return result


def _cleanup_qualified_name(
    qualified_name: str, structured_reporter: SourceReport
) -> str:
    """
    Clean up qualified name by removing quotes and validating format.

    Qualified object names from Snowflake audit logs have quotes for quoted identifiers,
    e.g., "test-database"."test-schema".test_table whereas we generate URNs without
    quotes even for quoted identifiers for backward compatibility.

    Args:
        qualified_name: Qualified name to clean up
        structured_reporter: Reporter for logging issues

    Returns:
        Cleaned up qualified name
    """
    name_parts = split_qualified_name(qualified_name)

    if len(name_parts) != 3:
        if not _is_sys_table(qualified_name):
            structured_reporter.report_warning(
                "UNEXPECTED_DATASET_PATTERN",
                f"Failed to parse Snowflake qualified name into constituent parts. "
                f"DB/schema/table filtering may not work as expected. "
                f"Name: {qualified_name}, Parts: {len(name_parts)}"
            )
        return qualified_name.replace('"', "")

    return _combine_identifier_parts(
        db_name=name_parts[0],
        schema_name=name_parts[1],
        table_name=name_parts[2],
    )


# Utility functions for common operations
def create_snowflake_identifier_builder(
    config: SnowflakeV2Config,
    report: SnowflakeV2Report
) -> SnowflakeIdentifierBuilder:
    """
    Factory function to create SnowflakeIdentifierBuilder.

    Args:
        config: Snowflake V2 configuration
        report: Snowflake V2 report

    Returns:
        Configured SnowflakeIdentifierBuilder instance
    """
    return SnowflakeIdentifierBuilder(config, report)


def create_snowflake_filter(
    config: SnowflakeV2Config,
    report: SnowflakeV2Report
) -> SnowflakeFilter:
    """
    Factory function to create SnowflakeFilter.

    Args:
        config: Snowflake V2 configuration
        report: Snowflake V2 report

    Returns:
        Configured SnowflakeFilter instance
    """
    return SnowflakeFilter(config.filter_config, report)


def create_snowsight_url_builder(
    account_locator: str,
    region: str,
    privatelink: bool = False,
    snowflake_domain: str = DEFAULT_SNOWFLAKE_DOMAIN,
) -> SnowsightUrlBuilder:
    """
    Factory function to create SnowsightUrlBuilder.

    Args:
        account_locator: Snowflake account locator
        region: Snowflake region
        privatelink: Whether to use private link
        snowflake_domain: Snowflake domain

    Returns:
        Configured SnowsightUrlBuilder instance
    """
    return SnowsightUrlBuilder(
        account_locator=account_locator,
        region=region,
        privatelink=privatelink,
        snowflake_domain=snowflake_domain,
    )


def validate_qualified_name(qualified_name: str) -> bool:
    """
    Validate that a qualified name has the expected format.

    Args:
        qualified_name: Name to validate

    Returns:
        True if name has expected 3-part format, False otherwise
    """
    try:
        parts = split_qualified_name(qualified_name)
        return len(parts) == 3 and all(part.strip() for part in parts)
    except Exception:
        return False


def normalize_snowflake_identifier(
    identifier: str,
    convert_to_lowercase: bool = True
) -> str:
    """
    Normalize Snowflake identifier according to conventions.

    Args:
        identifier: Identifier to normalize
        convert_to_lowercase: Whether to convert to lowercase

    Returns:
        Normalized identifier
    """
    if convert_to_lowercase:
        return identifier.lower()
    return identifier
