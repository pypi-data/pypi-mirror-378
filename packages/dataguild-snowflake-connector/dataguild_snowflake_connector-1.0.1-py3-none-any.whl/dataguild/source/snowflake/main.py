"""
DataGuild Snowflake Connector - Production-Ready Implementation
Enhanced with DataHub best practices and comprehensive error handling
"""

import contextlib
import functools
import json
import logging
import os
import os.path
import platform
import re
import threading
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Dict, Iterable, List, Optional, Union

from dataguild.configuration.time_window_config import BaseTimeWindowConfig
from dataguild.api.common import PipelineContext
from dataguild.api.decorators import (
    SupportStatus,
    capability,
    config_class,
    platform_name,
    support_status,
)
from dataguild.api.incremental_lineage_helper import auto_incremental_lineage
from dataguild.api.incremental_properties_helper import (
    auto_incremental_properties,
)
from dataguild.api.source import (
    CapabilityReport,
    MetadataWorkUnitProcessor,
    SourceCapability,
    SourceReport,
    TestableSource,
    TestConnectionReport,
)
from dataguild.api.source_helpers import auto_workunit
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.snowflake.constants import (
    GENERIC_PERMISSION_ERROR_KEY,
    SnowflakeEdition,
    SnowflakeObjectDomain,
)
from dataguild.source.snowflake.assertion import SnowflakeAssertionsHandler
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.source.snowflake.connection import (
    SnowflakeConnection,
    SnowflakeConnectionConfig,
)
from dataguild.source.snowflake.lineage import SnowflakeLineageExtractor
from dataguild.source.snowflake.profiler import SnowflakeProfiler
from dataguild.source.snowflake.query import SnowflakeQuery
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.snowflake.schema import SnowflakeDataDictionary
from dataguild.source.snowflake.schema_gen import SnowflakeSchemaGenerator
from dataguild.source.snowflake.snowflake_shares import SnowflakeSharesHandler
from dataguild.source.snowflake.usage import SnowflakeUsageExtractor
from dataguild.source.snowflake.utils import (
    SnowflakeCommonMixin,
    SnowflakeFilter,
    SnowflakeIdentifierBuilder,
    SnowsightUrlBuilder,
)
from dataguild.source.state.profiling_state_handler import ProfilingHandler
from dataguild.source.state.redundant_run_skip_handler import (
    RedundantLineageRunSkipHandler,
    RedundantUsageRunSkipHandler,
)
from dataguild.source.state.stale_entity_removal_handler import (
    StaleEntityRemovalHandler,
)
from dataguild.source.state.stateful_ingestion_base import (
    StatefulIngestionSourceBase,
)
from dataguild.configuration.common import AllowDenyPattern
from dataguild.source_report.ingestion_stage import (
    LINEAGE_EXTRACTION,
    METADATA_EXTRACTION,
    QUERIES_EXTRACTION,
    VIEW_PARSING,
)
from dataguild.sql_parsing.sql_parsing_aggregator import SqlParsingAggregator
from dataguild.utilities.registries.domain_registry import DomainRegistry

logger = logging.getLogger(__name__)

# Enhanced error handling following DataHub patterns
class SnowflakeConnectorError(Exception):
    """Base exception for Snowflake connector errors"""
    pass

class SnowflakePermissionError(SnowflakeConnectorError):
    """Permission-related errors in Snowflake connector"""
    pass

class SnowflakeConfigurationError(SnowflakeConnectorError):
    """Configuration-related errors in Snowflake connector"""
    pass

class SnowflakeConnectionError(SnowflakeConnectorError):
    """Connection-related errors in Snowflake connector"""
    pass

class SnowflakeQueryError(SnowflakeConnectorError):
    """Query execution errors in Snowflake connector"""
    pass

def safe_config_get(config, attr_name, default_value=None):
    """Safely get config attribute with default fallback to prevent AttributeError"""
    try:
        return getattr(config, attr_name, default_value)
    except AttributeError:
        logger.warning(f"Config attribute '{attr_name}' not found, using default: {default_value}")
        return default_value

def validate_snowflake_config(config) -> None:
    """Validate Snowflake configuration following DataHub patterns"""
    if not config.account_id:
        raise SnowflakeConfigurationError("account_id is required")
    if not config.username:
        raise SnowflakeConfigurationError("username is required")
    if not config.password:
        raise SnowflakeConfigurationError("password is required")
    if not config.warehouse:
        raise SnowflakeConfigurationError("warehouse is required")

def log_extraction_progress(stage: str, count: int, total: int = None) -> None:
    """Log extraction progress following DataHub patterns"""
    if total:
        logger.info(f"📊 {stage}: {count}/{total} ({count/total*100:.1f}%)")
    else:
        logger.info(f"📊 {stage}: {count} items processed")

# Enhanced SourceCapabilityModifier
class SourceCapabilityModifier:
    """Enhanced source capability modifiers for DataGuild Snowflake integration."""

    DATABASE = "DATABASE"
    SCHEMA = "SCHEMA"
    TABLE = "TABLE"
    VIEW = "VIEW"
    MATERIALIZED_VIEW = "MATERIALIZED_VIEW"
    EXTERNAL_TABLE = "EXTERNAL_TABLE"
    DYNAMIC_TABLE = "DYNAMIC_TABLE"
    STREAM = "STREAM"
    PROCEDURE = "PROCEDURE"
    FUNCTION = "FUNCTION"
    TASK = "TASK"
    STAGE = "STAGE"
    PIPE = "PIPE"
    SEQUENCE = "SEQUENCE"
    SHARE = "SHARE"
    TAG = "TAG"
    WAREHOUSE = "WAREHOUSE"

    _ALL_MODIFIERS = {
        DATABASE, SCHEMA, TABLE, VIEW, MATERIALIZED_VIEW, EXTERNAL_TABLE,
        DYNAMIC_TABLE, STREAM, PROCEDURE, FUNCTION, TASK, STAGE, PIPE,
        SEQUENCE, SHARE, TAG, WAREHOUSE
    }

    @classmethod
    def all_modifiers(cls) -> List[str]:
        return sorted(list(cls._ALL_MODIFIERS))

    @classmethod
    def container_modifiers(cls) -> List[str]:
        return [cls.DATABASE, cls.SCHEMA]

    @classmethod
    def dataset_modifiers(cls) -> List[str]:
        return [
            cls.TABLE, cls.VIEW, cls.MATERIALIZED_VIEW,
            cls.EXTERNAL_TABLE, cls.DYNAMIC_TABLE, cls.STREAM
        ]

    @classmethod
    def is_valid_modifier(cls, modifier: str) -> bool:
        return modifier in cls._ALL_MODIFIERS

# ✅ CRITICAL FIX: Safe config attribute accessor
def safe_config_get(config, attr_name, default_value=None):
    """Safely get config attribute with default fallback to prevent AttributeError"""
    return getattr(config, attr_name, default_value)

@platform_name("Snowflake", doc_order=1)
@config_class(SnowflakeV2Config)
@support_status(SupportStatus.CERTIFIED)
@capability(SourceCapability.PLATFORM_INSTANCE, "Enabled by default")
@capability(SourceCapability.DOMAINS, "Supported via the `domain` config field")
@capability(
    SourceCapability.CONTAINERS,
    "Enabled by default",
    subtype_modifier=[
        SourceCapabilityModifier.DATABASE,
        SourceCapabilityModifier.SCHEMA,
    ],
)
@capability(SourceCapability.SCHEMA_METADATA, "Enabled by default")
@capability(
    SourceCapability.DATA_PROFILING,
    "Optionally enabled via configuration `profiling.enabled`",
)
@capability(SourceCapability.DESCRIPTIONS, "Enabled by default")
@capability(
    SourceCapability.LINEAGE_COARSE,
    "Enabled by default, can be disabled via configuration `include_table_lineage`",
)
@capability(
    SourceCapability.LINEAGE_FINE,
    "Enabled by default, can be disabled via configuration `include_column_lineage`",
)
@capability(
    SourceCapability.USAGE_STATS,
    "Enabled by default, can be disabled via configuration `include_usage_stats`",
)
@capability(
    SourceCapability.DELETION_DETECTION,
    "Enabled by default via stateful ingestion",
    supported=True,
)
@capability(
    SourceCapability.TAGS,
    "Optionally enabled via `extract_tags`",
    supported=True,
)
@capability(
    SourceCapability.CLASSIFICATION,
    "Optionally enabled via `classification.enabled`",
    supported=True,
)
@capability(SourceCapability.TEST_CONNECTION, "Enabled by default")
class SnowflakeV2Source(
    SnowflakeCommonMixin,
    StatefulIngestionSourceBase,
    TestableSource,
):
    """
    CORRECTED: Enhanced DataGuild Snowflake V2 Source with comprehensive functionality,
    improved error handling, and production-ready features.
    """

    def __init__(self, ctx: PipelineContext, config: SnowflakeV2Config):
        """
        Initialize SnowflakeV2Source with comprehensive error handling and validation.
        Following DataHub patterns for better maintainability.
        """
        super().__init__(config, ctx)
        self.config: SnowflakeV2Config = config
        
        # Validate configuration following DataHub patterns
        validate_snowflake_config(config)
        
        # Initialize thread-safe query counter
        self._query_counter_lock = threading.Lock()
        self._query_counter = 0

        # Initialize report with proper error handling
        self._initialize_report(ctx)

        # Initialize core components
        self._initialize_filters()
        self._initialize_identifiers()
        self._initialize_domain_registry()
        self._initialize_connection()
        self._initialize_data_dictionary()
        self._initialize_sql_aggregator()
        self._initialize_lineage_extractor()
        self._initialize_usage_extractor()
        self._initialize_profiler()
        
        # Add configuration to report
        self.add_config_to_report()
        logger.info("✅ SnowflakeV2Source initialization completed successfully")

    def _initialize_report(self, ctx: PipelineContext) -> None:
        """Initialize the SnowflakeV2Report with proper error handling."""
        try:
            # Extract account information safely
            account_name = safe_config_get(self.config, 'account_id', 'unknown_account')
            region = safe_config_get(self.config, 'region', 'unknown_region')
            
            # Enhanced region detection
            if region == 'unknown_region' and '.' in str(account_name):
                parts = str(account_name).split('.')
                if len(parts) > 1:
                    region = parts[1]

            # Safe time extraction with proper defaults
            start_time = safe_config_get(self.config, 'start_time', datetime.now(UTC))
            end_time = safe_config_get(self.config, 'end_time', datetime.now(UTC))

            # Handle None values and ensure proper time ordering
            if start_time is None:
                start_time = datetime.now(UTC)
            if end_time is None:
                end_time = datetime.now(UTC)

            # Ensure end_time > start_time
            if end_time <= start_time:
                end_time = start_time.replace(hour=23, minute=59, second=59)

            self.report: SnowflakeV2Report = SnowflakeV2Report(
                name=f"snowflake_report_{ctx.pipeline_name}_{ctx.run_id}",
                account_name=str(account_name),
                region=str(region),
                report_period_start=start_time,
                report_period_end=end_time,
            )

            logger.info(f"✅ Created SnowflakeV2Report for account: {account_name}, region: {region}")

        except Exception as e:
            logger.error(f"Failed to create SnowflakeV2Report: {e}")
            # Fallback report
            now = datetime.now(UTC)
            self.report: SnowflakeV2Report = SnowflakeV2Report(
                name=f"snowflake_fallback_report_{ctx.run_id}",
                account_name="fallback_account",
                region="fallback_region",
                report_period_start=now,
                report_period_end=now,
            )
            logger.warning("Using fallback SnowflakeV2Report")

    def _initialize_filters(self) -> None:
        """Initialize SnowflakeFilter with error handling."""
        try:
            self.filters = SnowflakeFilter(
                filter_config=self.config, 
                structured_reporter=self.report
            )
            logger.debug("✅ SnowflakeFilter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SnowflakeFilter: {e}")
            raise SnowflakeConfigurationError(f"Filter initialization failed: {e}")

    def _initialize_identifiers(self) -> None:
        """Initialize SnowflakeIdentifierBuilder with error handling."""
        try:
            self.identifiers = SnowflakeIdentifierBuilder(
                identifier_config=self.config, 
                structured_reporter=self.report
            )
            logger.debug("✅ SnowflakeIdentifierBuilder initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SnowflakeIdentifierBuilder: {e}")
            raise SnowflakeConfigurationError(f"Identifier builder initialization failed: {e}")

    def _initialize_domain_registry(self) -> None:
        """Initialize domain registry with error handling."""
        self.domain_registry: Optional[DomainRegistry] = None
        try:
            domain_config = safe_config_get(self.config, 'domain', None)
            if domain_config:
                self.domain_registry = DomainRegistry(
                    cached_domains=[k for k in domain_config],
                    graph=self.ctx.graph
                )
                logger.debug("✅ Domain registry initialized")
        except Exception as e:
            logger.warning(f"Could not create domain registry: {e}")
            self.domain_registry = None

    def _initialize_connection(self) -> None:
        """Initialize Snowflake connection with proper error handling."""
        self._exit_stack = contextlib.ExitStack()
        
        try:
            logger.info("🔗 Establishing Snowflake connection")
            self.connection = self._exit_stack.enter_context(
                self.config.get_connection()
            )
            logger.info("✅ Snowflake connection established successfully")
        except Exception as e:
            logger.error(f"Failed to establish Snowflake connection: {e}")
            if "not granted to this user" in str(e):
                raise SnowflakePermissionError(f"Permission denied: {e}")
            raise SnowflakeConnectorError(f"Connection failed: {e}")

    def _initialize_data_dictionary(self) -> None:
        """Initialize SnowflakeDataDictionary with error handling."""
        try:
            self.data_dictionary = SnowflakeDataDictionary(
                connection=self.connection,
                report=self.report,
                fetch_views_from_information_schema=safe_config_get(
                    self.config, 'fetch_views_from_information_schema', True
                ),
            )
            logger.debug("✅ SnowflakeDataDictionary initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SnowflakeDataDictionary: {e}")
            raise SnowflakeConnectorError(f"Data dictionary initialization failed: {e}")

    def _initialize_sql_aggregator(self) -> None:
        """Initialize SQL parsing aggregator with error handling."""
        try:
            self.aggregator: SqlParsingAggregator = self._exit_stack.enter_context(
                SqlParsingAggregator(
                    platform=self.identifiers.platform,
                    platform_instance=safe_config_get(self.config, 'platform_instance', None),
                    env=safe_config_get(self.config, 'env', 'PROD'),
                    graph=self.ctx.graph,
                    eager_graph_load=(
                        not (
                            safe_config_get(self.config, 'include_technical_schema', True)
                            and safe_config_get(self.config, 'include_tables', True)
                            and safe_config_get(self.config, 'include_views', True)
                        )
                        and not safe_config_get(self.config, 'lazy_schema_resolver', False)
                    ),
                    generate_usage_statistics=False,
                    generate_operations=False,
                    generate_queries=safe_config_get(self.config, 'include_queries', True),
                    format_queries=safe_config_get(self.config, 'format_sql_queries', False),
                    is_temp_table=self._is_temp_table,
                    is_allowed_table=self._is_allowed_table,
                )
            )
            self.report.sql_aggregator = self.aggregator.report
            logger.debug("✅ SQL parsing aggregator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SQL parsing aggregator: {e}")
            raise SnowflakeConnectorError(f"SQL aggregator initialization failed: {e}")

    def _initialize_lineage_extractor(self) -> None:
        """Initialize lineage extractor with error handling."""
        self.lineage_extractor: Optional[SnowflakeLineageExtractor] = None
        self.discovered_datasets: Optional[List[str]] = None

        if safe_config_get(self.config, 'include_table_lineage', True):
            try:
                redundant_lineage_run_skip_handler: Optional[RedundantLineageRunSkipHandler] = None

                if safe_config_get(self.config, 'enable_stateful_lineage_ingestion', False):
                    redundant_lineage_run_skip_handler = RedundantLineageRunSkipHandler(
                        source=self,
                        config=self.config,
                        pipeline_name=self.ctx.pipeline_name,
                        run_id=self.ctx.run_id,
                    )

                self.lineage_extractor = self._exit_stack.enter_context(
                    SnowflakeLineageExtractor(
                        self.config,
                        self.report,
                        connection=self.connection,
                        filters=self.filters,
                        identifiers=self.identifiers,
                        redundant_run_skip_handler=redundant_lineage_run_skip_handler,
                        sql_aggregator=self.aggregator,
                    )
                )
                logger.debug("✅ Lineage extractor initialized")
            except Exception as e:
                logger.error(f"Failed to initialize lineage extractor: {e}")
                self.lineage_extractor = None

    def _initialize_usage_extractor(self) -> None:
        """Initialize usage extractor with error handling."""
        self.usage_extractor: Optional[SnowflakeUsageExtractor] = None
        if (safe_config_get(self.config, 'include_usage_stats', True) or
            safe_config_get(self.config, 'include_operational_stats', True)):

            try:
                redundant_usage_run_skip_handler: Optional[RedundantUsageRunSkipHandler] = None

                if safe_config_get(self.config, 'enable_stateful_usage_ingestion', False):
                    redundant_usage_run_skip_handler = RedundantUsageRunSkipHandler(
                        source=self,
                        config=self.config,
                        pipeline_name=self.ctx.pipeline_name,
                        run_id=self.ctx.run_id,
                    )

                self.usage_extractor = self._exit_stack.enter_context(
                    SnowflakeUsageExtractor(
                        self.config,
                        self.report,
                        connection=self.connection,
                        filter=self.filters,
                        identifiers=self.identifiers,
                        redundant_run_skip_handler=redundant_usage_run_skip_handler,
                    )
                )
                logger.debug("✅ Usage extractor initialized")
            except Exception as e:
                logger.error(f"Failed to initialize usage extractor: {e}")
                self.usage_extractor = None

    def _initialize_profiler(self) -> None:
        """Initialize profiler with error handling."""
        self.profiling_state_handler: Optional[ProfilingHandler] = None
        if safe_config_get(self.config, 'enable_stateful_profiling', False):
            try:
                self.profiling_state_handler = ProfilingHandler(
                    source=self,
                    config=self.config,
                    pipeline_name=self.ctx.pipeline_name,
                )
                logger.debug("✅ Profiling state handler initialized")
            except Exception as e:
                logger.warning(f"Could not create profiling state handler: {e}")

        self.profiler: Optional[SnowflakeProfiler] = None
        if safe_config_get(self.config, 'profiling', {}).get('enabled', False):
            try:
                self.profiler = SnowflakeProfiler(
                    self.config, self.report, self.profiling_state_handler
                )
                logger.debug("✅ Profiler initialized")
            except Exception as e:
                logger.error(f"Failed to initialize profiler: {e}")
                self.profiler = None

    @staticmethod
    def test_connection(config_dict: dict) -> TestConnectionReport:
        """Enhanced connection testing with comprehensive validation and error handling."""
        test_report = TestConnectionReport()

        try:
            logger.info("🔍 Testing Snowflake connection...")
            
            # Parse configuration with validation
            connection_conf = SnowflakeConnectionConfig.parse_obj_allow_extras(
                config_dict
            )
            
            # Test basic connectivity
            connection: SnowflakeConnection = connection_conf.get_connection()
            if not connection:
                raise SnowflakeConnectorError("Failed to establish connection")

            test_report.basic_connectivity = CapabilityReport(capable=True)
            logger.info("✅ Basic connectivity test passed")

            # Test capabilities
            try:
                test_report.capability_report = SnowflakeV2Source.check_capabilities(
                    connection, connection_conf
                )
                logger.info("✅ Capability check completed")
            except Exception as e:
                logger.warning(f"Capability check failed: {e}")
                test_report.internal_failure = True
                test_report.internal_failure_reason = f"Capability check failed: {e}"

            # Clean up connection
            try:
                connection.close()
                logger.info("✅ Connection closed successfully")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

            logger.info("✅ Connection test completed successfully")

        except SnowflakePermissionError as e:
            logger.error(f"Permission denied during connection test: {e}")
            test_report.basic_connectivity = CapabilityReport(
                capable=False, failure_reason=f"Permission denied: {e}"
            )
        except SnowflakeConfigurationError as e:
            logger.error(f"Configuration error during connection test: {e}")
            test_report.basic_connectivity = CapabilityReport(
                capable=False, failure_reason=f"Configuration error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}", exc_info=True)
            if test_report.basic_connectivity is None:
                test_report.basic_connectivity = CapabilityReport(
                    capable=False, failure_reason=f"Connection failed: {e}"
                )
            else:
                test_report.internal_failure = True
                test_report.internal_failure_reason = f"Unexpected error: {e}"

        return test_report

    @staticmethod
    def check_capabilities(
            conn: SnowflakeConnection, connection_conf: SnowflakeConnectionConfig
    ) -> Dict[Union[SourceCapability, str], CapabilityReport]:
        """Enhanced capability checking with detailed permission analysis."""

        @dataclass
        class SnowflakePrivilege:
            privilege: str
            object_name: str
            object_type: str

        _report: Dict[Union[SourceCapability, str], CapabilityReport] = dict()
        privileges: List[SnowflakePrivilege] = []

        capabilities: List[SourceCapability] = [
            c.capability
            for c in SnowflakeV2Source.get_capabilities()
            if c.capability not in (
                SourceCapability.PLATFORM_INSTANCE,
                SourceCapability.DOMAINS,
                SourceCapability.DELETION_DETECTION,
                SourceCapability.TEST_CONNECTION,
            )
        ]

        try:
            # Get current role and secondary roles
            cur = conn.query("select current_role()")
            current_role = [row["CURRENT_ROLE()"] for row in cur][0]

            cur = conn.query("select current_secondary_roles()")
            secondary_roles_str = json.loads(
                [row["CURRENT_SECONDARY_ROLES()"] for row in cur][0]
            )["roles"]

            secondary_roles = (
                [] if secondary_roles_str == "" else secondary_roles_str.split(",")
            )

            roles = [current_role] + secondary_roles

            if "PUBLIC" not in roles:
                roles.append("PUBLIC")

            # Enhanced privilege checking with better error handling
            i = 0
            while i < len(roles):
                role = roles[i]
                i = i + 1

                try:
                    cur = conn.query(f'show grants to role "{role}"')

                    for row in cur:
                        privilege = SnowflakePrivilege(
                            privilege=row["privilege"],
                            object_type=row["granted_on"],
                            object_name=row["name"],
                        )
                        privileges.append(privilege)

                        # Enhanced capability detection
                        if privilege.object_type in ("DATABASE", "SCHEMA") and privilege.privilege in ("OWNERSHIP", "USAGE"):
                            _report[SourceCapability.CONTAINERS] = CapabilityReport(capable=True)
                            _report[SourceCapability.TAGS] = CapabilityReport(capable=True)

                        elif privilege.object_type in ("TABLE", "VIEW", "MATERIALIZED_VIEW"):
                            _report[SourceCapability.SCHEMA_METADATA] = CapabilityReport(capable=True)
                            _report[SourceCapability.DESCRIPTIONS] = CapabilityReport(capable=True)
                            _report[SourceCapability.DATA_PROFILING] = CapabilityReport(capable=True)
                            _report[SourceCapability.CLASSIFICATION] = CapabilityReport(capable=True)

                            if privilege.object_name.startswith("SNOWFLAKE.ACCOUNT_USAGE."):
                                _report[SourceCapability.LINEAGE_COARSE] = CapabilityReport(capable=True)
                                _report[SourceCapability.LINEAGE_FINE] = CapabilityReport(capable=True)
                                _report[SourceCapability.USAGE_STATS] = CapabilityReport(capable=True)
                                _report[SourceCapability.TAGS] = CapabilityReport(capable=True)

                        if (privilege.object_type == "ROLE" and privilege.privilege == "USAGE"
                            and privilege.object_name not in roles):
                            roles.append(privilege.object_name)

                        if set(capabilities) == set(_report.keys()):
                            break

                except Exception as e:
                    logger.error(f"Error checking grants for role {role}: {e}")
                    continue

            # Enhanced warehouse checking
            cur = conn.query("select current_warehouse()")
            current_warehouse = [row["CURRENT_WAREHOUSE()"] for row in cur][0]

            # Enhanced failure message mapping
            default_failure_messages = {
                SourceCapability.SCHEMA_METADATA: "Either no tables exist or current role does not have permissions to access them",
                SourceCapability.DESCRIPTIONS: "Either no tables exist or current role does not have permissions to access them",
                SourceCapability.DATA_PROFILING: "Either no tables exist or current role does not have permissions to access them",
                SourceCapability.CLASSIFICATION: "Either no tables exist or current role does not have permissions to access them",
                SourceCapability.CONTAINERS: "Current role does not have permissions to use any database",
                SourceCapability.LINEAGE_COARSE: "Current role does not have permissions to snowflake account usage views",
                SourceCapability.LINEAGE_FINE: "Current role does not have permissions to snowflake account usage views",
                SourceCapability.USAGE_STATS: "Current role does not have permissions to snowflake account usage views",
                SourceCapability.TAGS: "Either no tags have been applied to objects, or the current role does not have permission to access the objects or to snowflake account usage views",
            }

            # Enhanced capability validation
            for c in capabilities:
                if current_warehouse is None and c in (
                        SourceCapability.SCHEMA_METADATA,
                        SourceCapability.DESCRIPTIONS,
                        SourceCapability.DATA_PROFILING,
                        SourceCapability.CLASSIFICATION,
                        SourceCapability.LINEAGE_COARSE,
                        SourceCapability.LINEAGE_FINE,
                        SourceCapability.USAGE_STATS,
                        SourceCapability.TAGS,
                ):
                    failure_message = (
                        f"Current role {current_role} does not have permissions to use warehouse {safe_config_get(connection_conf, 'warehouse', 'UNKNOWN')}"
                        if safe_config_get(connection_conf, 'warehouse', None) is not None
                        else "No default warehouse set for user. Either set default warehouse for user or configure warehouse in recipe"
                    )
                    _report[c] = CapabilityReport(
                        capable=False,
                        failure_reason=failure_message,
                    )

                if c in _report:
                    continue

                _report[c] = CapabilityReport(
                    capable=False,
                    failure_reason=default_failure_messages.get(c, "Unknown capability check failure"),
                )

        except Exception as e:
            logger.error(f"Error during capability checking: {e}")
            for c in capabilities:
                _report[c] = CapabilityReport(
                    capable=False,
                    failure_reason=f"Failed to check capabilities: {e}",
                )

        return _report

    def _is_temp_table(self, name: str) -> bool:
        """Enhanced temporary table detection."""
        temp_patterns = safe_config_get(self.config, 'temporary_tables_pattern', [])

        if any(re.match(pattern, name, flags=re.IGNORECASE) for pattern in temp_patterns):
            return True

        if (self.filters.is_dataset_pattern_allowed(name, SnowflakeObjectDomain.TABLE)
            and self.discovered_datasets
            and name not in self.discovered_datasets):
            return True

        return False

    def _is_allowed_table(self, name: str) -> bool:
        """Enhanced table filtering with comprehensive validation."""
        if self.discovered_datasets and name not in self.discovered_datasets:
            return False

        return self.filters.is_dataset_pattern_allowed(
            name, SnowflakeObjectDomain.TABLE
        )

    def get_workunit_processors(self) -> List[Optional[MetadataWorkUnitProcessor]]:
        """Enhanced work unit processors."""
        return [
            *super().get_workunit_processors(),
            functools.partial(
                auto_incremental_lineage,
                safe_config_get(self.config, 'incremental_lineage', None)
            ),
            functools.partial(
                auto_incremental_properties,
                safe_config_get(self.config, 'incremental_properties', None)
            ),
            StaleEntityRemovalHandler.create(
                self, self.config, self.ctx
            ).workunit_processor,
        ]

    def get_workunits_internal(self) -> Iterable[MetadataWorkUnit]:
        """Enhanced work unit generation following DataHub patterns for better maintainability."""
        
        # Clear OCSP cache for better connection stability
        self._snowflake_clear_ocsp_cache()
        
        # Inspect session metadata
        self.inspect_session_metadata(self.connection)
        
        # Build Snowsight URL builder if needed
        snowsight_url_builder = None
        if safe_config_get(self.config, 'include_external_url', False):
            snowsight_url_builder = self.get_snowsight_url_builder()
        
        # Validate warehouse access early
        if not self._validate_warehouse_access():
            logger.warning("Warehouse access validation failed")
            return
        
        # Create schema extractor with all dependencies
        schema_extractor = SnowflakeSchemaGenerator(
            config=self.config,
            report=self.report,
            connection=self.connection,
            domain_registry=self.domain_registry,
            profiler=self.profiler,
            aggregator=self.aggregator,
            snowsight_url_builder=snowsight_url_builder,
            filters=self.filters,
            identifiers=self.identifiers,
            fetch_views_from_information_schema=safe_config_get(
                self.config, 'fetch_views_from_information_schema', True
            ),
        )
        
        # Extract metadata using schema generator
        with self.report.new_stage(f"*: {METADATA_EXTRACTION}"):
            yield from schema_extractor.get_workunits_internal()
        
        # Get databases from extractor
        databases = schema_extractor.databases
        if not databases:
            logger.warning("No databases found for processing")
            return
        
        # Process shares if configured
        if safe_config_get(self.config, 'shares', None):
            yield from self._process_shares(databases)
        
        # Discover datasets using DataHub pattern
        discovered_datasets = self._discover_datasets(databases)
        self.discovered_datasets = discovered_datasets
        
        # Validate dataset discovery
        if not discovered_datasets:
            if safe_config_get(self.config, 'warn_no_datasets', False):
                self.structured_reporter.warning(
                    "No tables/views/streams found. Verify dataset permissions if Snowflake source is not empty.",
                )
            else:
                self.structured_reporter.failure(
                    GENERIC_PERMISSION_ERROR_KEY,
                    "No tables/views/streams found. Verify dataset permissions in Snowflake.",
                )
            return
        
        # Process based on configuration
        if safe_config_get(self.config, 'use_queries_v2', False):
            yield from self._process_queries_v2_path(discovered_datasets)
        else:
            yield from self._process_legacy_path(discovered_datasets)
        
        # Process assertions if enabled
        if safe_config_get(self.config, 'include_assertions', False):
            yield from self._process_assertions(discovered_datasets)
        
        logger.info("✅ Snowflake V2 Source processing completed successfully")

    def _preprocess_ingestion(self) -> None:
        """Pre-process ingestion setup including cache clearing and session inspection."""
        try:
            # Clear OCSP cache for better reliability
            self._snowflake_clear_ocsp_cache()
            
            # Inspect session metadata
            self.inspect_session_metadata(self.connection)
            
            logger.debug("✅ Pre-processing completed")
        except Exception as e:
            logger.warning(f"Pre-processing warning: {e}")

    def _validate_warehouse_access(self) -> bool:
        """Validate warehouse access and report failures."""
        if self.report.default_warehouse is None:
            self.report_warehouse_failure()
            return False
        return True

    def _extract_metadata(self) -> Iterable[MetadataWorkUnit]:
        """Extract metadata using schema generator."""
        try:
            # Build Snowsight URL builder if needed
            snowsight_url_builder = None
            if safe_config_get(self.config, 'include_external_url', False):
                snowsight_url_builder = self.get_snowsight_url_builder()

            # Create schema extractor
            schema_extractor = SnowflakeSchemaGenerator(
                config=self.config,
                report=self.report,
                connection=self.connection,
                domain_registry=self.domain_registry,
                profiler=self.profiler,
                aggregator=self.aggregator,
                snowsight_url_builder=snowsight_url_builder,
                filters=self.filters,
                identifiers=self.identifiers,
                fetch_views_from_information_schema=safe_config_get(
                    self.config, 'fetch_views_from_information_schema', True
                ),
            )

            # Extract metadata
            with self.report.new_stage(f"*: {METADATA_EXTRACTION}"):
                yield from schema_extractor.get_workunits_internal()

            # Store databases for later use
            self._extracted_databases = schema_extractor.databases
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            raise SnowflakeConnectorError(f"Metadata extraction failed: {e}")

    def _process_shares(self, databases: List) -> None:
        """Process shares if configured."""
        if safe_config_get(self.config, 'shares', None):
            try:
                yield from SnowflakeSharesHandler(
                    self.config, self.report
                ).get_shares_workunits(databases)
                logger.debug("✅ Shares processed")
            except Exception as e:
                logger.error(f"Error processing shares: {e}")

    def _discover_datasets(self, databases: List) -> List[str]:
        """Discover all datasets from databases."""
        try:
            discovered_tables = [
                self.identifiers.get_dataset_identifier(table_name, schema.name, db.name)
                for db in databases
                for schema in db.schemas
                for table_name in schema.tables
            ]

            discovered_views = [
                self.identifiers.get_dataset_identifier(table_name, schema.name, db.name)
                for db in databases
                for schema in db.schemas
                for table_name in schema.views
            ]

            discovered_streams = [
                self.identifiers.get_dataset_identifier(stream_name, schema.name, db.name)
                for db in databases
                for schema in db.schemas
                for stream_name in schema.streams
            ]

            total_datasets = len(discovered_tables) + len(discovered_views) + len(discovered_streams)
            
            if total_datasets == 0:
                if safe_config_get(self.config, 'warn_no_datasets', True):
                    self.structured_reporter.warning(
                        "No tables/views/streams found. Verify dataset permissions if Snowflake source is not empty.",
                    )
                else:
                    self.report.report_failure(
                        "No tables/views/streams found. Verify dataset permissions in Snowflake."
                    )

            logger.info(
                f"✅ Discovered {len(discovered_tables)} tables, {len(discovered_views)} views, "
                f"{len(discovered_streams)} streams"
            )

            return discovered_tables + discovered_views + discovered_streams
            
        except Exception as e:
            logger.error(f"Dataset discovery failed: {e}")
            raise SnowflakeConnectorError(f"Dataset discovery failed: {e}")

    def _process_queries_v2_path(self, discovered_datasets: List[str]) -> Iterable[MetadataWorkUnit]:
        """Process using queries v2 path."""
        try:
            # View parsing
            with self.report.new_stage(f"*: {VIEW_PARSING}"):
                if self.aggregator is not None:
                    yield from auto_workunit(self.aggregator.gen_metadata())
                else:
                    logger.warning("SQL aggregator is not initialized, skipping view parsing")

            # Lineage extraction
            if self.lineage_extractor:
                try:
                    with self.report.new_stage(f"*: {LINEAGE_EXTRACTION}"):
                        # Pass all discovered datasets - let lineage extractor handle filtering
                        self.lineage_extractor.add_time_based_lineage_to_aggregator(
                            discovered_tables=discovered_datasets,  # Include all datasets
                            discovered_views=discovered_datasets,   # Include all datasets
                        )
                except Exception as e:
                    logger.error(f"Error in lineage extraction: {e}")

            # Usage extraction
            if ((safe_config_get(self.config, 'include_usage_stats', True) or
                 safe_config_get(self.config, 'include_operational_stats', True))
                and self.usage_extractor):
                try:
                    with self.report.new_stage(f"*: Usage Extraction"):
                        yield from self.usage_extractor.get_usage_workunits(discovered_datasets)
                except Exception as e:
                    logger.error(f"Error in usage extraction: {e}")
                    
        except Exception as e:
            logger.error(f"Queries v2 processing failed: {e}")
            raise

    def _process_legacy_path(self, discovered_datasets: List[str]) -> Iterable[MetadataWorkUnit]:
        """Process using legacy path."""
        try:
            # Lineage extraction
            if self.lineage_extractor:
                try:
                    with self.report.new_stage(f"*: {LINEAGE_EXTRACTION}"):
                        # Pass all discovered datasets - let lineage extractor handle filtering
                        self.lineage_extractor.add_time_based_lineage_to_aggregator(
                            discovered_tables=discovered_datasets,  # Include all datasets
                            discovered_views=discovered_datasets,   # Include all datasets
                        )
                except Exception as e:
                    logger.error(f"Error in lineage extraction: {e}")

            # Aggregator metadata generation
            try:
                for mcp in self.aggregator.gen_metadata():
                    yield mcp.as_workunit()
            except Exception as e:
                logger.error(f"Error generating metadata from aggregator: {e}")

            # Update lineage state
            if self.lineage_extractor:
                try:
                    self.lineage_extractor.update_state()
                except Exception as e:
                    logger.error(f"Error updating lineage state: {e}")

            # Usage extraction
            if ((safe_config_get(self.config, 'include_usage_stats', True) or
                 safe_config_get(self.config, 'include_operational_stats', True))
                and self.usage_extractor):
                try:
                    yield from self.usage_extractor.get_usage_workunits(discovered_datasets)
                except Exception as e:
                    logger.error(f"Error in usage extraction: {e}")
                    
        except Exception as e:
            logger.error(f"Legacy processing failed: {e}")
            raise

    def _process_assertions(self, discovered_datasets: List[str]) -> None:
        """Process assertions if enabled."""
        if safe_config_get(self.config, 'include_assertion_results', False):
            try:
                yield from SnowflakeAssertionsHandler(
                    self.config, self.report, self.connection, self.identifiers
                ).get_assertion_workunits(discovered_datasets)
                logger.debug("✅ Assertions processed")
            except Exception as e:
                logger.error(f"Error in assertion extraction: {e}")

    def _cleanup_connection(self) -> None:
        """Clean up connection resources."""
        try:
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
                logger.info("✅ Snowflake connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

    def report_warehouse_failure(self) -> None:
        """Enhanced warehouse failure reporting."""
        warehouse = safe_config_get(self.config, 'warehouse', None)
        if warehouse is not None:
            self.report.report_failure(
                f"Current role does not have permissions to use warehouse {warehouse}. Please update permissions."
            )
        else:
            self.report.report_failure(
                "No default warehouse set for user. Either set a default warehouse for the user or configure a warehouse in the recipe."
            )

    def get_report(self) -> SourceReport:
        """Get the enhanced source report."""
        return self.report

    def add_config_to_report(self) -> None:
        """Enhanced configuration reporting with safe attribute access."""

        # ✅ FIXED: Safe assignment with hasattr checks
        if hasattr(self.report, 'cleaned_account_id'):
            self.report.cleaned_account_id = safe_config_get(self.config, 'account_id', 'unknown')

        if hasattr(self.report, 'ignore_start_time_lineage'):
            self.report.ignore_start_time_lineage = safe_config_get(self.config, 'ignore_start_time_lineage', False)

        if hasattr(self.report, 'upstream_lineage_in_report'):
            self.report.upstream_lineage_in_report = safe_config_get(self.config, 'upstream_lineage_in_report', False)

        if hasattr(self.report, 'include_technical_schema'):
            self.report.include_technical_schema = safe_config_get(self.config, 'include_technical_schema', True)

        if hasattr(self.report, 'include_usage_stats'):
            self.report.include_usage_stats = safe_config_get(self.config, 'include_usage_stats', True)

        if hasattr(self.report, 'include_operational_stats'):
            self.report.include_operational_stats = safe_config_get(self.config, 'include_operational_stats', True)

        if hasattr(self.report, 'include_column_lineage'):
            self.report.include_column_lineage = safe_config_get(self.config, 'include_column_lineage', True)

        if hasattr(self.report, 'stateful_lineage_ingestion_enabled'):
            self.report.stateful_lineage_ingestion_enabled = safe_config_get(self.config,
                                                                             'enable_stateful_lineage_ingestion', False)

        if hasattr(self.report, 'stateful_usage_ingestion_enabled'):
            self.report.stateful_usage_ingestion_enabled = safe_config_get(self.config,
                                                                           'enable_stateful_usage_ingestion', False)

        if hasattr(self.report, 'window_start_time') and hasattr(self.report, 'window_end_time'):
            self.report.window_start_time, self.report.window_end_time = (
                safe_config_get(self.config, 'start_time', datetime.now(UTC)),
                safe_config_get(self.config, 'end_time', datetime.now(UTC)),
            )

    def inspect_session_metadata(self, connection: SnowflakeConnection) -> None:
        """Enhanced session metadata inspection with safe assignments and error handling."""

        try:
            logger.info("Checking current version")
            for db_row in connection.query(SnowflakeQuery.current_version()):
                # ✅ FIXED: Safe assignment with hasattr check
                if hasattr(self.report, 'saas_version'):
                    self.report.saas_version = db_row["CURRENT_VERSION()"]
                else:
                    logger.debug(f"Snowflake version: {db_row['CURRENT_VERSION()']} (field not available in report)")
        except Exception as e:
            # ✅ FIXED: Safe error reporting with multiple fallbacks
            if (hasattr(self, 'structured_reporter') and
                    self.structured_reporter and
                    hasattr(self.structured_reporter, 'failure') and
                    callable(self.structured_reporter.failure)):
                self.report.report_failure("Could not determine the current Snowflake version")
            else:
                logger.error(f"Could not determine the current Snowflake version: {e}")

        try:
            logger.info("Checking current role")
            for db_row in connection.query(SnowflakeQuery.current_role()):
                # ✅ FIXED: Safe assignment with hasattr check
                if hasattr(self.report, 'role'):
                    self.report.role = db_row["CURRENT_ROLE()"]
                else:
                    logger.debug(f"Current role: {db_row['CURRENT_ROLE()']} (field not available in report)")
        except Exception as e:
            # ✅ FIXED: Safe error reporting
            if (hasattr(self, 'structured_reporter') and
                    self.structured_reporter and
                    hasattr(self.structured_reporter, 'failure') and
                    callable(self.structured_reporter.failure)):
                self.report.report_failure("Could not determine the current Snowflake role")
            else:
                logger.error(f"Could not determine the current Snowflake role: {e}")

        try:
            logger.info("Checking current warehouse")
            for db_row in connection.query(SnowflakeQuery.current_warehouse()):
                # ✅ FIXED: Safe assignment with hasattr check
                if hasattr(self.report, 'default_warehouse'):
                    self.report.default_warehouse = db_row["CURRENT_WAREHOUSE()"]
                else:
                    logger.debug(f"Current warehouse: {db_row['CURRENT_WAREHOUSE()']} (field not available in report)")
        except Exception as e:
            # ✅ FIXED: Safe error reporting
            if (hasattr(self, 'structured_reporter') and
                    self.structured_reporter and
                    hasattr(self.structured_reporter, 'failure') and
                    callable(self.structured_reporter.failure)):
                self.report.report_failure("Could not determine the current Snowflake warehouse")
            else:
                logger.error(f"Could not determine the current Snowflake warehouse: {e}")

        try:
            logger.info("Checking current edition")
            if self.is_standard_edition():
                if hasattr(self.report, 'edition'):
                    self.report.edition = SnowflakeEdition.STANDARD
                else:
                    logger.debug("Snowflake edition: STANDARD (field not available in report)")
            else:
                if hasattr(self.report, 'edition'):
                    self.report.edition = SnowflakeEdition.ENTERPRISE
                else:
                    logger.debug("Snowflake edition: ENTERPRISE (field not available in report)")
        except Exception as e:
            if hasattr(self.report, 'edition'):
                self.report.edition = None
            logger.warning(f"Could not determine Snowflake edition: {e}")

    def get_snowsight_url_builder(self) -> Optional[SnowsightUrlBuilder]:
        """Enhanced Snowsight URL builder with comprehensive error handling."""

        try:
            # Enhanced account and region detection
            for db_row in self.connection.query(SnowflakeQuery.current_account()):
                account_locator = db_row["CURRENT_ACCOUNT()"]

            for db_row in self.connection.query(SnowflakeQuery.current_region()):
                region = db_row["CURRENT_REGION()"]

            # ✅ FIXED: Safe assignment with hasattr check
            if hasattr(self.report, 'account_locator'):
                self.report.account_locator = account_locator

            if hasattr(self.report, 'region'):
                self.report.region = region

            # Enhanced region processing
            region = region.split(".")[-1].lower()
            account_locator = account_locator.lower()

            return SnowsightUrlBuilder(
                account_locator,
                region,
                privatelink=str(getattr(self.config, 'account_id', '')).endswith(".privatelink"),
                snowflake_domain=getattr(self.config, 'snowflake_domain', None),
            )

        except Exception as e:
            # ✅ FIXED: Safe error reporting with proper method checking
            try:
                if (hasattr(self.report, 'warning') and
                        callable(getattr(self.report, 'warning', None))):
                    self.report.warning(
                        title="External URL Generation Failed",
                        message="Unable to infer Snowsight base URL. External URLs will not be generated.",
                        exc=e,
                    )
                else:
                    logger.warning(f"External URL generation failed: {e}")
            except Exception as warning_error:
                logger.warning(f"External URL generation failed: {e} (could not report warning: {warning_error})")

            return None

    def is_standard_edition(self) -> bool:
        """Enhanced Snowflake edition detection."""
        known_edition = safe_config_get(self.config, 'known_snowflake_edition', None)
        if known_edition is not None:
            return known_edition == SnowflakeEdition.STANDARD

        try:
            self.connection.query(SnowflakeQuery.show_tags())
            return False
        except Exception as e:
            if "Unsupported feature 'TAG'" in str(e):
                return True
            raise

    def _snowflake_clear_ocsp_cache(self) -> None:
        """Enhanced OCSP cache clearing for improved reliability."""
        plat = platform.system().lower()

        if plat == "darwin":
            file_path = os.path.join(
                "~", "Library", "Caches", "Snowflake", "ocsp_response_validation_cache"
            )
        elif plat == "windows":
            file_path = os.path.join(
                "~", "AppData", "Local", "Snowflake", "Caches", "ocsp_response_validation_cache",
            )
        else:
            file_path = os.path.join(
                "~", ".cache", "snowflake", "ocsp_response_validation_cache"
            )

        file_path = os.path.expanduser(file_path)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f'Successfully removed OCSP cache file at "{file_path}"')
        except Exception as e:
            logger.debug(f'Failed to remove OCSP cache file at "{file_path}": {e}')

    def close(self) -> None:
        """Enhanced cleanup with comprehensive resource management."""
        logger.info("Closing Snowflake V2 Source")

        try:
            # Close parent class resources
            super().close()
            
            # Close exit stack (this will close all context managers)
            if hasattr(self, '_exit_stack'):
                self._exit_stack.close()
            
            # Additional cleanup
            self._cleanup_connection()
            
            logger.info("✅ Successfully closed Snowflake V2 Source")
        except Exception as e:
            logger.error(f"Error during Snowflake V2 Source cleanup: {e}")

    def get_query_counter(self) -> int:
        """Get thread-safe query counter."""
        with self._query_counter_lock:
            self._query_counter += 1
            return self._query_counter

    def validate_configuration(self) -> bool:
        """Validate the configuration before processing."""
        try:
            # Check required fields
            if not safe_config_get(self.config, 'account_id', None):
                raise SnowflakeConfigurationError("account_id is required")
            
            if not safe_config_get(self.config, 'user', None):
                raise SnowflakeConfigurationError("user is required")
            
            # Validate time windows
            start_time = safe_config_get(self.config, 'start_time', None)
            end_time = safe_config_get(self.config, 'end_time', None)
            
            if start_time and end_time and end_time <= start_time:
                raise SnowflakeConfigurationError("end_time must be after start_time")
            
            logger.debug("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def get_connection_info(self) -> Dict[str, str]:
        """Get connection information for debugging."""
        return {
            'account_id': safe_config_get(self.config, 'account_id', 'unknown'),
            'user': safe_config_get(self.config, 'user', 'unknown'),
            'warehouse': safe_config_get(self.config, 'warehouse', 'unknown'),
            'role': safe_config_get(self.config, 'role', 'unknown'),
            'region': safe_config_get(self.config, 'region', 'unknown'),
        }
