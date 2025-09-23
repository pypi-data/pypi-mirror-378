"""
DataGuild Snowflake Assertions Handler

Clean and enhanced assertions processing for Snowflake data quality monitoring.
Handles assertion results extraction and processing with improved error handling
and performance monitoring.

Author: DataGuild Engineering Team
"""

import logging
from datetime import datetime
from typing import Iterable, List, Optional

from pydantic import BaseModel

from dataguild.emitter.mce_builder import (
    make_assertion_urn,
    make_data_platform_urn,
    make_dataplatform_instance_urn,
)
from dataguild.emitter.mcp import MetadataChangeProposalWrapper
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.source.snowflake.connection import SnowflakeConnection
from dataguild.source.snowflake.query import SnowflakeQuery
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.snowflake.utils import (
    SnowflakeIdentifierBuilder,
)
from dataguild.metadata.com.linkedin.pegasus2avro.assertion import (
    AssertionResult,
    AssertionResultType,
    AssertionRunEvent,
    AssertionRunStatus,
)
from dataguild.metadata.com.linkedin.pegasus2avro.common import DataPlatformInstance
from dataguild.utilities.time import datetime_to_ts_millis

logger = logging.getLogger(__name__)


class DataQualityMonitoringResult(BaseModel):
    """Data model for Snowflake data quality monitoring results."""
    MEASUREMENT_TIME: datetime
    METRIC_NAME: str
    TABLE_NAME: str
    TABLE_SCHEMA: str
    TABLE_DATABASE: str
    VALUE: int

    class Config:
        """Pydantic configuration for parsing flexibility."""
        extra = "allow"  # Allow additional fields from Snowflake


class SnowflakeAssertionsHandler:
    """
    Enhanced handler for processing Snowflake assertion results with improved
    error handling, performance monitoring, and comprehensive logging.
    """

    def __init__(
            self,
            config: SnowflakeV2Config,
            report: SnowflakeV2Report,
            connection: SnowflakeConnection,
            identifiers: SnowflakeIdentifierBuilder,
    ) -> None:
        self.config = config
        self.report = report
        self.connection = connection
        self.identifiers = identifiers
        self._urns_processed: List[str] = []

        # Enhanced tracking
        self._assertions_processed = 0
        self._assertions_failed = 0
        self._processing_errors = 0

        logger.info("Enhanced Snowflake Assertions Handler initialized")

    def get_assertion_workunits(
            self, discovered_datasets: List[str]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Extract assertion work units from Snowflake with enhanced error handling
        and performance monitoring.
        """
        if not self.config.include_assertion_results:
            logger.info("Assertion results extraction disabled, skipping")
            return

        try:
            logger.info("Starting assertion results extraction from Snowflake")

            # Execute DMF assertion results query
            cur = self.connection.query(
                SnowflakeQuery.dmf_assertion_results(
                    datetime_to_ts_millis(self.config.start_time),
                    datetime_to_ts_millis(self.config.end_time),
                )
            )

            logger.info(f"Found {cur.rowcount if cur.rowcount else 0} assertion result rows")

            processed_count = 0

            for db_row in cur:
                try:
                    processed_count += 1

                    # Progress logging every 100 rows
                    if processed_count % 100 == 0:
                        logger.debug(f"Processed {processed_count} assertion rows")

                    mcp = self._process_result_row(db_row, discovered_datasets)

                    if mcp:
                        # Yield assertion result work unit
                        yield mcp.as_workunit(is_primary_source=False)
                        self._assertions_processed += 1

                        # Generate platform instance work unit if needed
                        if mcp.entityUrn and mcp.entityUrn not in self._urns_processed:
                            self._urns_processed.append(mcp.entityUrn)
                            yield self._gen_platform_instance_wu(mcp.entityUrn)

                except Exception as e:
                    self._processing_errors += 1
                    logger.error(f"Error processing assertion row {processed_count}: {e}")
                    self.report.report_warning(
                        "assertion-row-processing-error",
                        f"Failed to process assertion row: {e}"
                    )
                    continue

            # Final summary logging
            logger.info(
                f"Assertion processing complete: {self._assertions_processed} processed, "
                f"{self._assertions_failed} failed, {self._processing_errors} errors"
            )

        except Exception as e:
            logger.error(f"Failed to extract assertion results: {e}")
            self.report.report_warning(
                "assertion-extraction-error",
                f"Assertion results extraction failed: {e}"
            )

    def _gen_platform_instance_wu(self, urn: str) -> MetadataWorkUnit:
        """
        Generate platform instance work unit for assertion with enhanced validation.
        """
        try:
            # Construct platform instance metadata
            platform_aspect = DataPlatformInstance(
                platform=make_data_platform_urn(self.identifiers.platform),
                instance=(
                    make_dataplatform_instance_urn(
                        self.identifiers.platform, self.config.platform_instance
                    )
                    if self.config.platform_instance
                    else None
                ),
            )

            return MetadataChangeProposalWrapper(
                entityUrn=urn,
                aspect=platform_aspect,
            ).as_workunit(is_primary_source=False)

        except Exception as e:
            logger.error(f"Failed to generate platform instance work unit for {urn}: {e}")
            raise

    def _process_result_row(
            self, result_row: dict, discovered_datasets: List[str]
    ) -> Optional[MetadataChangeProposalWrapper]:
        """
        Process individual assertion result row with enhanced validation and error handling.
        """
        try:
            # Parse the result using Pydantic model for validation
            result = DataQualityMonitoringResult.parse_obj(result_row)

            # Enhanced assertion GUID extraction with validation
            assertion_guid = self._extract_assertion_guid(result.METRIC_NAME)
            if not assertion_guid:
                logger.debug(f"Could not extract assertion GUID from metric: {result.METRIC_NAME}")
                return None

            # Determine assertion status (1 = PASS, 0 = FAIL)
            status = bool(result.VALUE)

            # Build dataset identifier
            assertee = self.identifiers.get_dataset_identifier(
                result.TABLE_NAME, result.TABLE_SCHEMA, result.TABLE_DATABASE
            )

            # Check if dataset was discovered (only process known datasets)
            if assertee not in discovered_datasets:
                logger.debug(f"Skipping assertion for undiscovered dataset: {assertee}")
                return None

            # Track assertion status for reporting
            if not status:
                self._assertions_failed += 1

            # Create assertion run event
            assertion_run_event = AssertionRunEvent(
                timestampMillis=datetime_to_ts_millis(result.MEASUREMENT_TIME),
                runId=result.MEASUREMENT_TIME.strftime("%Y-%m-%dT%H:%M:%SZ"),
                asserteeUrn=self.identifiers.gen_dataset_urn(assertee),
                status=AssertionRunStatus.COMPLETE,
                assertionUrn=make_assertion_urn(assertion_guid),
                result=AssertionResult(
                    type=(
                        AssertionResultType.SUCCESS
                        if status
                        else AssertionResultType.FAILURE
                    )
                ),
            )

            # Create metadata change proposal
            return MetadataChangeProposalWrapper(
                entityUrn=make_assertion_urn(assertion_guid),
                aspect=assertion_run_event,
            )

        except Exception as e:
            logger.error(f"Failed to process assertion result row: {e}")
            self.report.report_warning(
                "assertion-result-parse-failure",
                f"Failed to parse assertion result: {e}"
            )
            return None

    def _extract_assertion_guid(self, metric_name: str) -> Optional[str]:
        """
        Extract assertion GUID from metric name with enhanced validation.

        Args:
            metric_name: The metric name from Snowflake (e.g., "dq_check__assertion_guid")

        Returns:
            Extracted GUID or None if extraction fails
        """
        try:
            # Handle different metric name formats
            parts = metric_name.split("__")

            if len(parts) >= 2:
                # Standard format: prefix__guid
                guid = parts[-1].lower().strip()

                # Validate GUID format (basic validation)
                if len(guid) > 0 and not guid.isspace():
                    return guid

            # Fallback: try splitting on different delimiters
            for delimiter in ["_", "-"]:
                if delimiter in metric_name:
                    parts = metric_name.split(delimiter)
                    if len(parts) >= 2:
                        potential_guid = parts[-1].lower().strip()
                        if len(potential_guid) > 0:
                            return potential_guid

            # If all else fails, use the entire metric name as GUID
            return metric_name.lower().strip()

        except Exception as e:
            logger.error(f"Error extracting GUID from metric name {metric_name}: {e}")
            return None

    def get_processing_stats(self) -> dict:
        """
        Get processing statistics for monitoring and reporting.

        Returns:
            Dictionary with processing metrics
        """
        return {
            "assertions_processed": self._assertions_processed,
            "assertions_failed": self._assertions_failed,
            "processing_errors": self._processing_errors,
            "unique_urns_processed": len(self._urns_processed),
            "success_rate": (
                                    (self._assertions_processed - self._assertions_failed) /
                                    max(self._assertions_processed, 1)
                            ) * 100
        }

    def reset_stats(self) -> None:
        """Reset processing statistics for new ingestion run."""
        self._assertions_processed = 0
        self._assertions_failed = 0
        self._processing_errors = 0
        self._urns_processed.clear()
        logger.debug("Assertion handler statistics reset")


# Utility functions for assertion processing

def validate_assertion_config(config: SnowflakeV2Config) -> List[str]:
    """
    Validate assertion-related configuration.

    Args:
        config: Snowflake V2 configuration

    Returns:
        List of validation issues (empty if valid)
    """
    issues = []

    if config.include_assertion_results:
        if not config.start_time:
            issues.append("start_time is required when include_assertion_results is enabled")

        if not config.end_time:
            issues.append("end_time is required when include_assertion_results is enabled")

        # Check time window is reasonable (not too large)
        if config.start_time and config.end_time:
            time_diff = config.end_time - config.start_time
            if time_diff.days > 30:
                issues.append("Time window for assertion results should not exceed 30 days")

    return issues


def create_assertions_handler(
        config: SnowflakeV2Config,
        report: SnowflakeV2Report,
        connection: SnowflakeConnection,
        identifiers: SnowflakeIdentifierBuilder
) -> SnowflakeAssertionsHandler:
    """
    Factory function to create assertions handler with validation.

    Args:
        config: Snowflake configuration
        report: Snowflake report instance
        connection: Snowflake connection
        identifiers: Identifier builder

    Returns:
        Configured assertions handler
    """
    # Validate configuration
    issues = validate_assertion_config(config)
    if issues:
        raise ValueError(f"Invalid assertion configuration: {'; '.join(issues)}")

    handler = SnowflakeAssertionsHandler(
        config=config,
        report=report,
        connection=connection,
        identifiers=identifiers
    )

    logger.info("Created Snowflake assertions handler")
    return handler
