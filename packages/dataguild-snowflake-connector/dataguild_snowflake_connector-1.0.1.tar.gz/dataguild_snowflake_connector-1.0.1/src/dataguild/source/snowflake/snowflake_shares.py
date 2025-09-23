"""
DataGuild Snowflake Shares Handler

Handles inbound and outbound Snowflake shares, generating appropriate
sibling relationships and upstream lineage for shared databases.

Author: DataGuild Engineering Team
"""

import logging
from typing import Iterable, List

from dataguild.emitter.mce_builder import make_dataset_urn_with_platform_instance
from dataguild.emitter.mcp import MetadataChangeProposalWrapper
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.snowflake.config import (
    DatabaseId,
    SnowflakeV2Config,
)
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.snowflake.schema import SnowflakeDatabase
from dataguild.source.snowflake.utils import SnowflakeCommonMixin
from dataguild.schemas.common import Siblings
from dataguild.schemas.dataset import (
    DatasetLineageType,
    Upstream,
    UpstreamLineage,
)

logger: logging.Logger = logging.getLogger(__name__)


class SnowflakeSharesHandler(SnowflakeCommonMixin):
    """
    Handler for managing Snowflake database shares in DataGuild.

    Processes inbound and outbound share configurations to generate:
    - Sibling relationships between shared databases
    - Upstream lineage for inbound shares
    - Comprehensive share metadata tracking
    """

    def __init__(
            self,
            config: SnowflakeV2Config,
            report: SnowflakeV2Report,
    ) -> None:
        """
        Initialize the shares handler.

        Args:
            config: Snowflake configuration with share settings
            report: Report instance for tracking operations
        """
        self.config = config
        self.report = report
        logger.info("SnowflakeSharesHandler initialized for DataGuild")

    def get_shares_workunits(
            self, databases: List[SnowflakeDatabase]
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate work units for shared databases.

        Args:
            databases: List of Snowflake databases to process

        Yields:
            MetadataWorkUnit: Work units for share relationships and lineage
        """
        inbounds = self.config.inbounds()
        outbounds = self.config.outbounds()

        # Early return if no shares configured
        if not (inbounds or outbounds):
            logger.debug("No inbound or outbound shares configured")
            return

        logger.info(f"Processing shares for {len(databases)} databases")
        logger.debug("Checking databases for inbound or outbound shares")

        processed_shares = 0

        for db in databases:
            is_inbound = db.name in inbounds
            is_outbound = db.name in outbounds

            if not (is_inbound or is_outbound):
                logger.debug(f"Database {db.name} is not shared")
                continue

            logger.info(f"Processing shared database: {db.name} (inbound: {is_inbound}, outbound: {is_outbound})")

            # Determine sibling databases
            sibling_dbs = (
                list(outbounds[db.name]) if is_outbound else [inbounds[db.name]]
            )

            # Process each schema and table/view
            for schema in db.schemas:
                schema_objects_processed = 0

                for table_name in schema.tables + schema.views:
                    # TODO: Enhanced share processing for outbound databases:
                    # 1. Query `SHOW SHARES` to identify shares associated with database
                    # 2. Run `SHOW GRANTS TO SHARE <share_name>` for exact object permissions
                    # 3. Only emit siblings for objects actually included in shares
                    # 4. Requires ACCOUNTADMIN role or share ownership
                    # This prevents ghost nodes in "Composed Of" sections

                    yield from self.gen_siblings(
                        db.name,
                        schema.name,
                        table_name,
                        is_outbound,
                        sibling_dbs,
                    )

                    # Generate upstream lineage for inbound shares
                    if is_inbound:
                        assert len(sibling_dbs) == 1, "Inbound share must have exactly one sibling"
                        # Note: SnowflakeLineageExtractor is unaware of database->schema->table hierarchy
                        # This lineage generation is specific to shares and not governed by include_table_lineage config
                        yield self.get_upstream_lineage_with_primary_sibling(
                            db.name, schema.name, table_name, sibling_dbs[0]
                        )

                    schema_objects_processed += 1

                if schema_objects_processed > 0:
                    logger.debug(f"Processed {schema_objects_processed} objects in schema {schema.name}")

            processed_shares += 1

        logger.info(f"Successfully processed {processed_shares} shared databases")

        # Report any missing database configurations
        self.report_missing_databases(
            databases, list(inbounds.keys()), list(outbounds.keys())
        )

    def report_missing_databases(
            self,
            databases: List[SnowflakeDatabase],
            inbounds: List[str],
            outbounds: List[str],
    ) -> None:
        """
        Report databases referenced in share configs but not found during ingestion.

        Args:
            databases: List of ingested databases
            inbounds: List of configured inbound share databases
            outbounds: List of configured outbound share databases
        """
        db_names = [db.name for db in databases]
        missing_dbs = [db for db in inbounds + outbounds if db not in db_names]

        if not missing_dbs:
            return

        if self.config.platform_instance:
            self.report.warning(
                title="Extra Snowflake share configurations",
                message="Some databases referenced by share configs were not ingested. "
                        "Siblings/lineage will not be set for these databases.",
                context=f"Missing databases: {missing_dbs}",
            )
            logger.warning(f"Missing share databases with platform instance: {missing_dbs}")
        else:
            logger.debug(f"Databases {missing_dbs} were not ingested in this recipe")

    def gen_siblings(
            self,
            database_name: str,
            schema_name: str,
            table_name: str,
            primary: bool,
            sibling_databases: List[DatabaseId],
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate sibling relationships for shared tables/views.

        Args:
            database_name: Source database name
            schema_name: Source schema name
            table_name: Source table/view name
            primary: Whether this is the primary sibling (True for outbound shares)
            sibling_databases: List of sibling database identifiers

        Yields:
            MetadataWorkUnit: Sibling relationship metadata
        """
        if not sibling_databases:
            logger.debug(f"No sibling databases for {database_name}.{schema_name}.{table_name}")
            return

        try:
            # Get dataset identifier and URN for source
            dataset_identifier = self.identifiers.get_dataset_identifier(
                table_name, schema_name, database_name
            )
            urn = self.identifiers.gen_dataset_urn(dataset_identifier)

            # Generate sibling URNs
            sibling_urns = []
            for sibling_db in sibling_databases:
                sibling_urn = make_dataset_urn_with_platform_instance(
                    self.identifiers.platform,
                    self.identifiers.get_dataset_identifier(
                        table_name, schema_name, sibling_db.database
                    ),
                    sibling_db.platform_instance,
                )
                sibling_urns.append(sibling_urn)

            # Create siblings aspect
            siblings_aspect = Siblings(
                primary=primary,
                siblings=sorted(sibling_urns)
            )

            logger.debug(f"Generated {len(sibling_urns)} siblings for {urn} (primary: {primary})")

            yield MetadataChangeProposalWrapper(
                entityUrn=urn,
                aspect=siblings_aspect,
            ).as_workunit()

        except Exception as e:
            logger.error(f"Failed to generate siblings for {database_name}.{schema_name}.{table_name}: {e}")
            self.report.report_failure(
                key=f"{database_name}.{schema_name}.{table_name}",
                reason=f"Failed to generate siblings: {str(e)}"
            )

    def get_upstream_lineage_with_primary_sibling(
            self,
            database_name: str,
            schema_name: str,
            table_name: str,
            primary_sibling_db: DatabaseId,
    ) -> MetadataWorkUnit:
        """
        Generate upstream lineage from primary sibling for inbound shares.

        Args:
            database_name: Target database name (inbound share)
            schema_name: Target schema name
            table_name: Target table/view name
            primary_sibling_db: Source database identifier (primary sibling)

        Returns:
            MetadataWorkUnit: Upstream lineage metadata
        """
        try:
            # Get target dataset URN
            dataset_identifier = self.identifiers.get_dataset_identifier(
                table_name, schema_name, database_name
            )
            urn = self.identifiers.gen_dataset_urn(dataset_identifier)

            # Get upstream (source) dataset URN
            upstream_urn = make_dataset_urn_with_platform_instance(
                self.identifiers.platform,
                self.identifiers.get_dataset_identifier(
                    table_name, schema_name, primary_sibling_db.database
                ),
                primary_sibling_db.platform_instance,
            )

            # Create upstream lineage aspect
            upstream_lineage = UpstreamLineage(
                upstreams=[
                    Upstream(
                        dataset=upstream_urn,
                        type=DatasetLineageType.COPY
                    )
                ]
            )

            logger.debug(f"Generated upstream lineage: {upstream_urn} -> {urn}")

            return MetadataChangeProposalWrapper(
                entityUrn=urn,
                aspect=upstream_lineage,
            ).as_workunit()

        except Exception as e:
            logger.error(f"Failed to generate upstream lineage for {database_name}.{schema_name}.{table_name}: {e}")
            self.report.report_failure(
                key=f"{database_name}.{schema_name}.{table_name}",
                reason=f"Failed to generate upstream lineage: {str(e)}"
            )
            # Return empty workunit on error
            return MetadataChangeProposalWrapper(
                entityUrn="",
                aspect=None,
            ).as_workunit()

    def get_share_statistics(self) -> dict:
        """
        Get statistics about configured shares.

        Returns:
            dict: Share configuration statistics
        """
        inbounds = self.config.inbounds()
        outbounds = self.config.outbounds()

        return {
            "inbound_shares": len(inbounds),
            "outbound_shares": len(outbounds),
            "total_share_databases": len(set(list(inbounds.keys()) + list(outbounds.keys()))),
            "inbound_databases": list(inbounds.keys()),
            "outbound_databases": list(outbounds.keys()),
        }

    def validate_share_configuration(self) -> List[str]:
        """
        Validate share configuration for common issues.

        Returns:
            List[str]: List of validation warnings/errors
        """
        issues = []

        try:
            inbounds = self.config.inbounds()
            outbounds = self.config.outbounds()

            # Check for overlapping inbound/outbound databases
            inbound_dbs = set(inbounds.keys())
            outbound_dbs = set(outbounds.keys())
            overlap = inbound_dbs.intersection(outbound_dbs)

            if overlap:
                issues.append(f"Databases configured as both inbound and outbound: {list(overlap)}")

            # Check for empty configurations
            if not inbounds and not outbounds:
                issues.append("No share configurations found")

            # Validate database identifiers
            all_dbs = list(inbounds.values()) + [db for db_list in outbounds.values() for db in db_list]
            for db in all_dbs:
                if not hasattr(db, 'database') or not db.database:
                    issues.append(f"Invalid database identifier: {db}")
                if not hasattr(db, 'platform_instance'):
                    issues.append(f"Missing platform_instance for database: {db}")

        except Exception as e:
            issues.append(f"Error validating share configuration: {str(e)}")

        return issues


# Utility functions for share management

def validate_share_permissions(config: SnowflakeV2Config) -> bool:
    """
    Validate that the configured role has necessary permissions for share operations.

    Args:
        config: Snowflake configuration

    Returns:
        bool: True if permissions are adequate
    """
    # This would typically query Snowflake to check role permissions
    # For now, return True with a warning
    logger.warning("Share permission validation not implemented - ensure role has ACCOUNTADMIN or share ownership")
    return True


def get_share_grants_query(share_name: str) -> str:
    """
    Generate SQL query to get grants for a specific share.

    Args:
        share_name: Name of the share

    Returns:
        str: SQL query to retrieve share grants
    """
    return f"SHOW GRANTS TO SHARE {share_name}"


def get_shares_list_query() -> str:
    """
    Generate SQL query to list all shares.

    Returns:
        str: SQL query to list shares
    """
    return "SHOW SHARES"


# Export classes and functions
__all__ = [
    'SnowflakeSharesHandler',
    'validate_share_permissions',
    'get_share_grants_query',
    'get_shares_list_query',
]
