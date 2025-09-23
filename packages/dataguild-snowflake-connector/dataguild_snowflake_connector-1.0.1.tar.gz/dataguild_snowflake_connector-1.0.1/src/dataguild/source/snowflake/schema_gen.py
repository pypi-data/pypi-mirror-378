"""
DataGuild Snowflake Schema Generator

Comprehensive schema extraction and metadata generation for Snowflake databases.
This module handles extraction of databases, schemas, tables, views, streams, procedures,
columns, constraints, tags, and lineage information with full DataGuild integration.
"""

import itertools
import logging
import time
from typing import Any, Dict, Iterable, List, Optional, Union

from dataguild.configuration.common import AllowDenyPattern
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.api.report import Report
from dataguild.metadata.schemas import (
    ArrayType, BooleanType, BytesType, DateType, ForeignKeyConstraint,
    GlobalTags, MySqlDDL, NullType, NumberType, RecordType, SchemaField,
    SchemaFieldDataType, SchemaMetadata, Status, StringType, SubTypes,
    TagAssociation, TimeType, TimeStamp, ViewProperties, DatasetProperties
)
from dataguild.source.snowflake.constants import (
    GENERIC_PERMISSION_ERROR_KEY,
    SNOWFLAKE_DATABASE,
    SnowflakeObjectDomain,
)
from dataguild.source.snowflake.config import (
    SnowflakeV2Config,
    TagOption,
)
from dataguild.source.snowflake.connection import (
    SnowflakeConnection,
    SnowflakePermissionError,
)
from dataguild.source.snowflake.data_reader import SnowflakeDataReader
from dataguild.source.snowflake.profiler import SnowflakeProfiler
from dataguild.source.snowflake.query import SnowflakeQuery
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.snowflake.schema import (
    SCHEMA_PARALLELISM,
    BaseProcedure,
    SnowflakeColumn,
    SnowflakeDatabase,
    SnowflakeDataDictionary,
    SnowflakeDynamicTable,
    SnowflakeFK,
    SnowflakePK,
    SnowflakeSchema,
    SnowflakeStream,
    SnowflakeTable,
    SnowflakeTag,
    SnowflakeView,
)
from dataguild.source.snowflake.tag import SnowflakeTagExtractor
from dataguild.source.snowflake.utils import (
    SnowflakeFilter,
    SnowflakeIdentifierBuilder,
    SnowflakeStructuredReportMixin,
    SnowsightUrlBuilder,
    split_qualified_name,
)
from dataguild.sql_parsing.sql_parsing_aggregator import PreparsedQuery
from dataguild.sql_parsing.sqlglot_utils import extract_table_names as extract_table_names_generator
from dataguild.sql_parsing.schema_resolver import extract_table_names as extract_table_names_detailed
from dataguild.source.sql.sql_utils import (
    add_table_to_schema_container,
    gen_database_container,
    gen_schema_container,
    get_dataplatform_instance_aspect,
    get_domain_wu,
)
from dataguild.source.sql.stored_procedures.base import (
    generate_procedure_container_workunits,
    generate_procedure_workunits,
)
from dataguild.source.ingestion_stage import (
    EXTERNAL_TABLE_DDL_LINEAGE,
    LINEAGE_EXTRACTION,
    METADATA_EXTRACTION,
    PROFILING,
)
from dataguild.sql_parsing.sql_parsing_aggregator import (
    KnownLineageMapping,
    SqlParsingAggregator,
)
from dataguild.utilities.registries.domain_registry import DomainRegistry
from dataguild.utilities.threaded_iterator_executor import ThreadedIteratorExecutor
from dataguild.utilities.perf_timer import PerfTimer

logger = logging.getLogger(__name__)

# Snowflake data type mappings to DataGuild schema field types
# https://docs.snowflake.com/en/sql-reference/intro-summary-data-types.html
SNOWFLAKE_FIELD_TYPE_MAPPINGS = {
    "DATE": DateType,
    "BIGINT": NumberType,
    "BINARY": BytesType,
    "BOOLEAN": BooleanType,
    "CHAR": StringType,
    "CHARACTER": StringType,
    "DATETIME": TimeType,
    "DEC": NumberType,
    "DECIMAL": NumberType,
    "DOUBLE": NumberType,
    "FIXED": NumberType,
    "FLOAT": NumberType,
    "INT": NumberType,
    "INTEGER": NumberType,
    "NUMBER": NumberType,
    "REAL": NumberType,
    "BYTEINT": NumberType,
    "SMALLINT": NumberType,
    "STRING": StringType,
    "TEXT": StringType,
    "TIME": TimeType,
    "TIMESTAMP": TimeType,
    "TIMESTAMP_TZ": TimeType,
    "TIMESTAMP_LTZ": TimeType,
    "TIMESTAMP_NTZ": TimeType,
    "TINYINT": NumberType,
    "VARBINARY": BytesType,
    "VARCHAR": StringType,
    "VARIANT": RecordType,
    "OBJECT": NullType,
    "ARRAY": ArrayType,
    "GEOGRAPHY": NullType,
    "GEOMETRY": NullType,
}


class SnowflakeSchemaGenerator(SnowflakeStructuredReportMixin):
    """
    Comprehensive Snowflake schema generator for DataGuild.

    This class handles the extraction and generation of complete schema metadata
    from Snowflake databases, including:
    - Database and schema containers
    - Table, view, and stream metadata
    - Column definitions with data types
    - Primary and foreign key constraints
    - Tags and structured properties
    - Lineage information
    - Profiling integration
    """

    platform = "snowflake"

    def __init__(
        self,
        config: SnowflakeV2Config,
        report: SnowflakeV2Report,
        connection: SnowflakeConnection,
        filters: SnowflakeFilter,
        identifiers: SnowflakeIdentifierBuilder,
        domain_registry: Optional[DomainRegistry],
        profiler: Optional[SnowflakeProfiler],
        aggregator: Optional[SqlParsingAggregator],
        snowsight_url_builder: Optional[SnowsightUrlBuilder],
        fetch_views_from_information_schema: bool = False,
    ) -> None:
        """
        Initialize the Snowflake schema generator.

        Args:
            config: Snowflake configuration
            report: Structured report for tracking progress
            connection: Snowflake database connection
            filters: Dataset and object filters
            identifiers: URN and identifier builder
            domain_registry: Optional domain registry for data domains
            profiler: Optional profiler for data profiling
            aggregator: Optional SQL parsing aggregator for lineage
            snowsight_url_builder: Optional URL builder for Snowsight links
            fetch_views_from_information_schema: Whether to fetch views from information schema
        """
        self.config: SnowflakeV2Config = config
        self.report: SnowflakeV2Report = report
        self.connection: SnowflakeConnection = connection
        self.filters: SnowflakeFilter = filters
        self.identifiers: SnowflakeIdentifierBuilder = identifiers

        # Initialize data dictionary for metadata extraction
        self.data_dictionary: SnowflakeDataDictionary = SnowflakeDataDictionary(
            connection=self.connection,
            report=self.report,
            fetch_views_from_information_schema=fetch_views_from_information_schema,
        )
        self.report.data_dictionary_cache = self.data_dictionary

        # Optional components
        self.domain_registry: Optional[DomainRegistry] = domain_registry
        self.profiler: Optional[SnowflakeProfiler] = profiler
        self.snowsight_url_builder: Optional[SnowsightUrlBuilder] = snowsight_url_builder
        self.aggregator = aggregator
        
        # Initialize classification handler
        self.classification_handler: Optional[Any] = None
        if hasattr(config, 'classification') and getattr(config.classification, 'enabled', False):
            try:
                from dataguild.glossary.classification_mixin import ClassificationHandler
                self.classification_handler = ClassificationHandler(config, report)
            except ImportError:
                logger.warning("Classification handler not available")

        # Initialize tag extractor for tag processing
        self.tag_extractor = SnowflakeTagExtractor(
            config, self.data_dictionary, self.report, identifiers
        )

        # Runtime state populated during extraction
        self.databases: List[SnowflakeDatabase] = []

        # Performance tracking
        self.extraction_timer = PerfTimer("schema_extraction")

        logger.info(f"Initialized DataGuild SnowflakeSchemaGenerator for {self.platform}")

    def get_connection(self) -> SnowflakeConnection:
        """Get the Snowflake connection."""
        return self.connection

    @property
    def structured_reporter(self) -> Report:
        """Get the structured reporter for this generator."""
        return self.report

    def gen_dataset_urn(self, dataset_identifier: str) -> str:
        """Generate dataset URN from identifier."""
        return self.identifiers.gen_dataset_urn(dataset_identifier)

    def snowflake_identifier(self, identifier: str) -> str:
        """Normalize Snowflake identifier."""
        return self.identifiers.snowflake_identifier(identifier)

    def get_workunits_internal(self) -> Iterable[MetadataWorkUnit]:
        """
        Generate all metadata work units for Snowflake schema extraction.
        Following DataHub patterns for better maintainability and error handling.

        Returns:
            Iterator of MetadataWorkUnit instances
        """
        with self.extraction_timer:
            # Handle structured properties template creation if enabled
            if self.config.extract_tags_as_structured_properties:
                logger.info("Creating structured property templates for tags")
                yield from self.tag_extractor.create_structured_property_templates()

                # Wait for cache invalidation
                logger.info(
                    f"Waiting for {self.config.structured_properties_template_cache_invalidation_interval} seconds "
                    f"for structured properties cache to invalidate"
                )
                time.sleep(
                    self.config.structured_properties_template_cache_invalidation_interval
                )

            # Initialize and filter databases
            self.databases = []
            for database in self.get_databases() or []:
                self.report.report_entity_scanned(database.name, "database")
                if not self.filters.filter_config.database_pattern.allowed(database.name):
                    self.report.report_dropped(f"{database.name}.*")
                else:
                    self.databases.append(database)

            if len(self.databases) == 0:
                logger.warning("No databases found or allowed by configuration")
                return

            try:
                # Process each database
                for snowflake_db in self.databases:
                    with self.report.new_stage(f"{snowflake_db.name}: {METADATA_EXTRACTION}"):
                        yield from self._process_database(snowflake_db)

                # Handle external table DDL lineage
                with self.report.new_stage(f"*: {EXTERNAL_TABLE_DDL_LINEAGE}"):
                    discovered_tables: List[str] = [
                        self.identifiers.get_dataset_identifier(
                            table_name, schema.name, db.name
                        )
                        for db in self.databases
                        for schema in db.schemas
                        for table_name in schema.tables
                    ]
                    if self.aggregator:
                        for entry in self._external_tables_ddl_lineage(discovered_tables):
                            self.aggregator.add(entry)

            except SnowflakePermissionError as e:
                self.structured_reporter.failure(
                    GENERIC_PERMISSION_ERROR_KEY,
                    exc=e,
                )
                return

        logger.info(
            f"Schema extraction completed in {self.extraction_timer.elapsed_seconds():.2f}s "
            f"for {len(self.databases)} databases"
        )

    def get_databases(self) -> Optional[List[SnowflakeDatabase]]:
        """
        Get list of databases from Snowflake.

        Returns:
            List of SnowflakeDatabase objects or None if failed
        """
        try:
            # `show databases` is required to get databases for information_schema querying
            databases = self.data_dictionary.show_databases()
        except Exception as e:
            self.structured_reporter.failure(
                "Failed to list databases",
                exc=e,
            )
            return None
        else:
            ischema_databases: List[SnowflakeDatabase] = (
                self.get_databases_from_ischema(databases)
            )

            if len(ischema_databases) == 0:
                self.structured_reporter.failure(
                    GENERIC_PERMISSION_ERROR_KEY,
                    "No databases found. Please check permissions.",
                )
            return ischema_databases

    def get_databases_from_ischema(
        self, databases: List[SnowflakeDatabase]
    ) -> List[SnowflakeDatabase]:
        """
        Get databases from information_schema with permission handling and apply pattern filtering.

        Args:
            databases: List of databases from SHOW DATABASES

        Returns:
            List of accessible and filtered databases
        """
        # First, filter the input databases by pattern
        filtered_input_databases = []
        for database in databases:
            if self.config.database_pattern.allowed(database.name):
                logger.info(f"✅ Database {database.name} allowed by pattern")
                filtered_input_databases.append(database)
            else:
                logger.info(f"❌ Database {database.name} filtered out by pattern")
        
        logger.info(f"Input database filtering: {len(databases)} -> {len(filtered_input_databases)} databases")
        
        # Return the filtered input databases directly since they already match the pattern
        # The information schema query is not needed here as it returns all accessible databases
        logger.info(f"Final database filtering: {len(filtered_input_databases)} -> {len(filtered_input_databases)} databases")
        return filtered_input_databases

    def _process_database(
        self, snowflake_db: SnowflakeDatabase
    ) -> Iterable[MetadataWorkUnit]:
        """
        Process a single database and generate work units.

        Args:
            snowflake_db: Database to process

        Yields:
            MetadataWorkUnit instances
        """
        db_name = snowflake_db.name

        try:
            # Note: We don't need to explicitly USE database in DataGuild
            pass
        except Exception as e:
            if isinstance(e, SnowflakePermissionError):
                self.structured_reporter.warning(
                    "Insufficient privileges to operate on database, skipping. "
                    "Please grant USAGE permissions on database to extract its metadata.",
                    db_name,
                )
            else:
                logger.debug(
                    f"Failed to use database {db_name} due to error {e}",
                    exc_info=e,
                )
                self.structured_reporter.warning(
                    "Failed to get schemas for database", db_name, exc=e
                )
            return

        # Extract tags for database if enabled
        if self.config.extract_tags != TagOption.skip:
            snowflake_db.tags = self.tag_extractor.get_tags_on_object(
                domain="database", db_name=db_name
            )

        # Generate database containers if technical schema is included
        if self.config.include_technical_schema:
            yield from self.gen_database_containers(snowflake_db)

        # Fetch schemas for this database
        self.fetch_schemas_for_database(snowflake_db, db_name)

        # Process database tags
        if self.config.include_technical_schema and snowflake_db.tags:
            for tag in snowflake_db.tags:
                yield from self._process_tag(tag)

        # Cache tables for a single database (consider moving to disk/S3 for large databases)
        db_tables: Dict[str, List[SnowflakeTable]] = {}
        yield from self._process_db_schemas(snowflake_db, db_tables)

        # Run profiling if enabled
        if self.profiler and db_tables:
            with self.report.new_stage(f"{snowflake_db.name}: {PROFILING}"):
                yield from self.profiler.get_workunits(snowflake_db, db_tables)

    def _process_db_schemas(
        self,
        snowflake_db: SnowflakeDatabase,
        db_tables: Dict[str, List[SnowflakeTable]],
    ) -> Iterable[MetadataWorkUnit]:
        """
        Process all schemas in a database using parallel execution.

        Args:
            snowflake_db: Database containing schemas
            db_tables: Cache for tables by schema

        Yields:
            MetadataWorkUnit instances
        """
        def _process_schema_worker(
            schema_tuple: tuple,
        ) -> Iterable[MetadataWorkUnit]:
            """Worker function for parallel schema processing."""
            snowflake_schema = schema_tuple[0]  # Unpack the tuple
            for wu in self._process_schema(
                snowflake_schema, snowflake_db.name, db_tables
            ):
                yield wu

        # Process schemas in parallel for better performance
        for wu in ThreadedIteratorExecutor.process(
            worker_func=_process_schema_worker,
            args_list=[
                (snowflake_schema,) for snowflake_schema in snowflake_db.schemas
            ],
            max_workers=SCHEMA_PARALLELISM,
        ):
            yield wu

    def fetch_schemas_for_database(
        self, snowflake_db: SnowflakeDatabase, db_name: str
    ) -> None:
        """
        Fetch and filter schemas for a database.

        Args:
            snowflake_db: Database to populate with schemas
            db_name: Database name
        """
        logger.info(f"🔍 DEBUG: fetch_schemas_for_database called for {db_name}")
        schemas: List[SnowflakeSchema] = []
        try:
            raw_schemas = self.data_dictionary.get_schemas_for_database(db_name)
            logger.info(f"🔍 DEBUG: get_schemas_for_database returned {len(raw_schemas) if raw_schemas else 0} schemas")
            
            for schema in raw_schemas or []:
                logger.info(f"🔍 DEBUG: Processing schema: {schema.name}")
                self.report.report_entity_scanned(schema.name, "schema")
                if not self.filters.is_schema_allowed(
                    schema.name,
                    db_name,
                ):
                    logger.info(f"🔍 DEBUG: Schema {schema.name} was FILTERED OUT")
                    self.report.report_dropped(f"{db_name}.{schema.name}.*")
                else:
                    logger.info(f"🔍 DEBUG: Schema {schema.name} was ALLOWED")
                    schemas.append(schema)
        except Exception as e:
            if isinstance(e, SnowflakePermissionError):
                error_msg = (
                    f"Failed to get schemas for database {db_name}. "
                    f"Please check permissions."
                )
                raise SnowflakePermissionError(error_msg) from e.__cause__
            else:
                self.structured_reporter.warning(
                    "Failed to get schemas for database",
                    db_name,
                    exc=e,
                )

        if not schemas:
            self.structured_reporter.warning(
                "No schemas found in database. "
                "If schemas exist, please grant USAGE permissions on them.",
                db_name,
            )
        else:
            snowflake_db.schemas = schemas

    def _process_schema(
        self,
        snowflake_schema: SnowflakeSchema,
        db_name: str,
        db_tables: Dict[str, List[SnowflakeTable]],
    ) -> Iterable[MetadataWorkUnit]:
        """
        Process a single schema and its contents.

        Args:
            snowflake_schema: Schema to process
            db_name: Database name
            db_tables: Cache for tables by schema

        Yields:
            MetadataWorkUnit instances
        """
        schema_name = snowflake_schema.name

        # Extract schema tags
        if self.config.extract_tags != TagOption.skip:
            self._process_tags(snowflake_schema, schema_name, db_name, domain="schema")

        # Generate schema containers
        if self.config.include_technical_schema:
            yield from self.gen_schema_containers(snowflake_schema, db_name)

        tables, views, streams = [], [], []

        # Fetch tables if enabled
        if self.config.include_tables_bool:
            tables = self.fetch_tables_for_schema(
                snowflake_schema, db_name, schema_name
            )

        # Fetch views if enabled
        if self.config.include_views:
            views = self.fetch_views_for_schema(
                snowflake_schema, db_name, schema_name
            )

        # Process tables (filter out views to avoid duplicates)
        logger.info(f"🔍 DEBUG: include_tables_bool = {self.config.include_tables_bool}")
        if self.config.include_tables_bool:
            # Filter out views from tables list to avoid duplicate processing
            actual_tables = [table for table in tables if table.type and str(table.type).upper() not in ['VIEW', 'MATERIALIZED VIEW']]
            logger.info(f"🔍 DEBUG: Processing {len(actual_tables)} actual tables (filtered from {len(tables)} total objects) for schema {schema_name}")
            db_tables[schema_name] = actual_tables
            yield from self._process_tables(
                actual_tables, snowflake_schema, db_name, schema_name
            )
        else:
            logger.info(f"🔍 DEBUG: Skipping table processing - include_tables_bool is False")

        # Process views
        if self.config.include_views:
            # Add view definitions to aggregator for lineage
            self._add_views_to_aggregator(views, db_name, schema_name)
            
            # Generate work units for views
            if self.config.include_technical_schema:
                for view in views:
                    yield from self._process_view(view, snowflake_schema, db_name)

        # Process streams
        if self.config.include_streams:
            self.report.num_get_streams_for_schema_queries += 1
            streams = self.fetch_streams_for_schema(
                snowflake_schema,
                db_name,
            )
            yield from self._process_streams(streams, snowflake_schema, db_name)

        # Process procedures
        if self.config.include_procedures:
            procedures = self.fetch_procedures_for_schema(snowflake_schema, db_name)
            yield from self._process_procedures(procedures, snowflake_schema, db_name)

        # Process schema tags
        if self.config.include_technical_schema and snowflake_schema.tags:
            yield from self._process_tags_in_schema(snowflake_schema)

        # Report if no objects found
        if (
            not snowflake_schema.views
            and not snowflake_schema.tables
            and not snowflake_schema.streams
        ):
            self.structured_reporter.info(
                title="No tables/views/streams found in schema",
                message="If objects exist, please grant REFERENCES or SELECT permissions on them.",
                context=f"{db_name}.{schema_name}",
            )

    def _process_tags(
        self,
        snowflake_schema: SnowflakeSchema,
        schema_name: str,
        db_name: str,
        domain: str,
    ) -> None:
        """Extract and set tags for a schema."""
        snowflake_schema.tags = self.tag_extractor.get_tags_on_object(
            schema_name=schema_name, db_name=db_name, domain=domain
        )

    def _process_tables(
        self,
        tables: List[SnowflakeTable],
        snowflake_schema: SnowflakeSchema,
        db_name: str,
        schema_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """Process tables in a schema."""
        logger.info(f"🔍 DEBUG: _process_tables called with {len(tables)} tables for {db_name}.{schema_name}")
        if self.config.include_technical_schema:
            data_reader = self.make_data_reader()
            for table in tables:
                # Handle dynamic table definitions for lineage
                if (
                    isinstance(table, SnowflakeDynamicTable)
                    and table.definition
                    and self.aggregator
                ):
                    table_identifier = self.identifiers.get_dataset_identifier(
                        table.name, schema_name, db_name
                    )
                    
                    # Parse SQL to extract upstream tables
                    upstream_urns = self._extract_upstream_urns_from_sql(
                        table.definition, db_name, schema_name
                    )
                    
                    # Create PreparsedQuery for view definition
                    view_query = PreparsedQuery(
                        query_id=f"dynamic_table_{table.name}_{schema_name}_{db_name}",
                        query_text=table.definition,
                        upstreams=upstream_urns,  # Now populated with actual upstream tables
                        downstream=self.identifiers.gen_dataset_urn(table_identifier),
                        confidence_score=1.0,
                        query_type=None,
                        extra_info={
                            "object_type": "dynamic_table",
                            "database": db_name,
                            "schema": schema_name,
                            "table": table.name
                        }
                    )
                    self.aggregator.add(view_query)

                # Process table with classification
                logger.info(f"🔍 DEBUG: About to call _process_table for table {table.name}")
                table_wu_generator = self._process_table(
                    table, snowflake_schema, db_name
                )
                
                # Add table lineage processing for regular tables
                if (isinstance(table, SnowflakeTable) and 
                    table.type in ['TABLE', 'TRANSIENT'] and 
                    self.aggregator):
                    # Try to get table definition from access history or other sources
                    # For now, we'll rely on access history lineage extraction
                    pass

                # Apply classification if enabled
                if self.classification_handler and data_reader:
                    yield from self.classification_handler.process_workunits(
                        table_wu_generator,
                        data_reader,
                        [db_name, schema_name, table.name],
                    )
                else:
                    yield from table_wu_generator

    def _add_views_to_aggregator(
        self,
        views: List[SnowflakeView],
        db_name: str,
        schema_name: str,
    ) -> None:
        """Add view definitions to aggregator for lineage extraction."""
        logger.info(f"Adding {len(views)} views to aggregator")
        if self.aggregator:
            for view in views:
                logger.info(f"Processing view: {view.name}")
                view_identifier = self.identifiers.get_dataset_identifier(
                    view.name, schema_name, db_name
                )

                # Handle secure views
                if view.is_secure and not view.view_definition:
                    view.view_definition = self.fetch_secure_view_definition(
                        view.name, schema_name, db_name
                    )

                logger.info(f"View {view.name}: is_secure={view.is_secure}, has_definition={bool(view.view_definition)}")
                
                if view.view_definition:
                    logger.info(f"View {view.name} definition: {view.view_definition[:200]}...")
                    # Parse SQL to extract upstream tables
                    upstream_urns = self._extract_upstream_urns_from_sql(
                        view.view_definition, db_name, schema_name
                    )
                    
                    logger.info(f"View {view.name}: upstream_urns type: {type(upstream_urns)}")
                    logger.info(f"View {view.name}: upstream_urns is list: {isinstance(upstream_urns, list)}")
                    logger.info(f"View {view.name}: upstream_urns is generator: {isinstance(upstream_urns, type(iter([])))}")
                    logger.info(f"View {view.name}: Extracted {len(upstream_urns)} upstream URNs: {upstream_urns}")
                    
                    # Create PreparsedQuery for view definition
                    view_query = PreparsedQuery(
                        query_id=f"view_{view.name}_{schema_name}_{db_name}",
                        query_text=view.view_definition,
                        upstreams=upstream_urns,  # Now populated with actual upstream tables
                        downstream=self.identifiers.gen_dataset_urn(view_identifier),
                        confidence_score=1.0,
                        query_type=None,
                        extra_info={
                            "object_type": "view",
                            "database": db_name,
                            "schema": schema_name,
                            "view": view.name,
                            "is_secure": view.is_secure
                        }
                    )
                    
                    logger.info(f"Adding PreparsedQuery for view {view.name} with {len(upstream_urns)} upstreams")
                    self.aggregator.add(view_query)
                elif view.is_secure:
                    logger.warning(f"View {view.name} is secure but has no definition")
                    self.report.num_secure_views_missing_definition += 1
                else:
                    logger.warning(f"View {view.name} has no definition and is not secure")
        else:
            logger.warning("No aggregator available for view processing")

    def _process_views(
        self,
        views: List[SnowflakeView],
        snowflake_schema: SnowflakeSchema,
        db_name: str,
        schema_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """Process views in a schema."""
        # Generate work units for views
        if self.config.include_technical_schema:
            for view in views:
                yield from self._process_view(view, snowflake_schema, db_name)

    def _extract_upstream_urns_from_sql(self, sql_text: str, db_name: str, schema_name: str) -> List[str]:
        """Extract upstream dataset URNs from SQL query using DataHub's approach."""
        try:
            logger.info(f"Extracting upstream tables from SQL: {sql_text[:100]}...")
            
            # Use DataHub's approach: extract table names but exclude CTEs
            import sqlglot
            from dataguild.sql_parsing.sqlglot_utils import parse_sql_query
            
            # Parse the SQL statement
            statement = parse_sql_query(sql_text, dialect="snowflake")
            
            # Extract all table references
            all_tables = []
            for table in statement.find_all(sqlglot.exp.Table):
                if not isinstance(table.parent, sqlglot.exp.Drop):
                    table_name = table.alias_or_name
                    all_tables.append(table_name)
            
            # Extract CTE names to exclude them
            cte_names = set()
            for cte in statement.find_all(sqlglot.exp.CTE):
                cte_names.add(cte.alias_or_name)
            
            # Filter out CTEs and self-references
            actual_tables = []
            for table_name in all_tables:
                # Skip CTEs
                if table_name.lower() in cte_names:
                    logger.debug(f"Skipping CTE alias: {table_name}")
                    continue
                
                # Skip self-references (view referencing itself)
                if table_name.lower() in [db_name.lower(), schema_name.lower()]:
                    logger.debug(f"Skipping self-reference: {table_name}")
                    continue
                
                # Skip if the table name matches the view/table name (self-reference)
                # Extract the target object name from the SQL
                target_name = ""
                if 'view' in sql_text.lower():
                    # For views: extract view name
                    view_match = sql_text.lower().split('view')[1].split('(')[0].strip()
                    target_name = view_match.split('.')[-1].lower()
                elif 'table' in sql_text.lower() and 'create' in sql_text.lower():
                    # For tables: extract table name
                    table_match = sql_text.lower().split('table')[1].split('(')[0].strip()
                    target_name = table_match.split('.')[-1].lower()
                
                if table_name.lower() == target_name:
                    logger.debug(f"Skipping self-reference: {table_name} == {target_name}")
                    continue
                
                actual_tables.append(table_name)
            
            logger.info(f"Extracted table names: {actual_tables}")
            logger.info(f"Excluded CTEs: {list(cte_names)}")
            
            upstream_urns = []
            for table_name in actual_tables:
                # Convert table name to dataset identifier
                # Handle fully qualified names (database.schema.table)
                if '.' in table_name:
                    parts = table_name.split('.')
                    if len(parts) == 3:
                        table_db, table_schema, table_name_only = parts
                    elif len(parts) == 2:
                        table_db = db_name
                        table_schema, table_name_only = parts
                    else:
                        table_db = db_name
                        table_schema = schema_name
                        table_name_only = table_name
                else:
                    table_db = db_name
                    table_schema = schema_name
                    table_name_only = table_name
                
                # Create dataset identifier
                table_identifier = self.identifiers.get_dataset_identifier(
                    table_name_only, table_schema, table_db
                )
                
                # Generate URN
                urn = self.identifiers.gen_dataset_urn(table_identifier)
                upstream_urns.append(urn)
                
                logger.info(f"Extracted upstream table: {table_name} -> {urn}")
            
            logger.info(f"Extracted {len(upstream_urns)} upstream tables from SQL")
            return upstream_urns
            
        except Exception as e:
            logger.error(f"Error extracting upstream tables from SQL: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _process_streams(
        self,
        streams: List[SnowflakeStream],
        snowflake_schema: SnowflakeSchema,
        db_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """Process streams in a schema."""
        for stream in streams:
            yield from self._process_stream(stream, snowflake_schema, db_name)

    def _process_procedures(
        self,
        procedures: List[BaseProcedure],
        snowflake_schema: SnowflakeSchema,
        db_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """Process stored procedures in a schema."""
        if self.config.include_technical_schema:
            if procedures:
                yield from generate_procedure_container_workunits(
                    self.identifiers.gen_database_key(db_name),
                    self.identifiers.gen_schema_key(
                        db_name=db_name,
                        schema_name=snowflake_schema.name,
                    ),
                )
            for procedure in procedures:
                yield from self._process_procedure(procedure, snowflake_schema, db_name)

    def _process_tags_in_schema(
        self, snowflake_schema: SnowflakeSchema
    ) -> Iterable[MetadataWorkUnit]:
        """Process tags within a schema."""
        if snowflake_schema.tags:
            for tag in snowflake_schema.tags:
                yield from self._process_tag(tag)

    def fetch_secure_view_definition(
        self, table_name: str, schema_name: str, db_name: str
    ) -> Optional[str]:
        """
        Fetch definition for a secure view.

        Args:
            table_name: View name
            schema_name: Schema name
            db_name: Database name

        Returns:
            View definition SQL or None if not available
        """
        try:
            view_definitions = self.data_dictionary.get_secure_view_definitions()
            return view_definitions[db_name][schema_name][table_name]
        except KeyError:
            self.structured_reporter.info(
                title="Secure view definition not found",
                message="Lineage will be missing for the view.",
                context=f"{db_name}.{schema_name}.{table_name}",
            )
            return None
        except Exception as e:
            action_msg = (
                "Please check permissions."
                if isinstance(e, SnowflakePermissionError)
                else ""
            )

            self.structured_reporter.warning(
                title="Failed to get secure views definitions",
                message=f"Lineage will be missing for the view. {action_msg}",
                context=f"{db_name}.{schema_name}.{table_name}",
                exc=e,
            )
            return None

    def fetch_views_for_schema(
        self, snowflake_schema: SnowflakeSchema, db_name: str, schema_name: str
    ) -> List[SnowflakeView]:
        """Fetch and filter views for a schema."""
        try:
            views: List[SnowflakeView] = []
            for view in self.get_views_for_schema(schema_name, db_name):
                view_name = self.identifiers.get_dataset_identifier(
                    view.name, schema_name, db_name
                )

                self.report.report_entity_scanned(view_name, "view")

                if not self.filters.filter_config.view_pattern.allowed(view_name):
                    self.report.report_dropped(view_name)
                else:
                    views.append(view)

            snowflake_schema.views = [view.name for view in views]
            return views
        except Exception as e:
            if isinstance(e, SnowflakePermissionError):
                error_msg = (
                    f"Failed to get views for schema {db_name}.{schema_name}. "
                    f"Please check permissions."
                )
                raise SnowflakePermissionError(error_msg) from e.__cause__
            else:
                self.structured_reporter.warning(
                    "Failed to get views for schema",
                    f"{db_name}.{schema_name}",
                    exc=e,
                )
                return []

    def fetch_tables_for_schema(
        self, snowflake_schema: SnowflakeSchema, db_name: str, schema_name: str
    ) -> List[SnowflakeTable]:
        """Fetch and filter tables for a schema."""
        try:
            tables: List[SnowflakeTable] = []
            raw_tables = self.get_tables_for_schema(schema_name, db_name)
            logger.info(f"🔍 DEBUG: Found {len(raw_tables)} raw tables for {db_name}.{schema_name}")
            
            for table in raw_tables:
                table_identifier = self.identifiers.get_dataset_identifier(
                    table.name, schema_name, db_name
                )
                logger.info(f"🔍 DEBUG: Processing table: {table.name} -> identifier: {table_identifier}")
                
                self.report.report_entity_scanned(table_identifier)
                if not self.filters.filter_config.table_pattern.allowed(
                    table_identifier
                ):
                    logger.info(f"🔍 DEBUG: Table {table_identifier} was FILTERED OUT by pattern")
                    self.report.report_dropped(table_identifier)
                else:
                    logger.info(f"🔍 DEBUG: Table {table_identifier} was ALLOWED by pattern")
                    tables.append(table)

            snowflake_schema.tables = [table.name for table in tables]
            return tables
        except Exception as e:
            if isinstance(e, SnowflakePermissionError):
                error_msg = (
                    f"Failed to get tables for schema {db_name}.{schema_name}. "
                    f"Please check permissions."
                )
                raise SnowflakePermissionError(error_msg) from e.__cause__
            else:
                self.structured_reporter.warning(
                    "Failed to get tables for schema",
                    f"{db_name}.{schema_name}",
                    exc=e,
                )
                return []

    def make_data_reader(self) -> Optional[SnowflakeDataReader]:
        """Create data reader for classification if enabled."""
        if hasattr(self, 'classification_handler') and self.classification_handler and self.connection:
            return SnowflakeDataReader.create(
                self.connection, self.snowflake_identifier
            )
        return None

    def _process_table(
        self,
        table: SnowflakeTable,
        snowflake_schema: SnowflakeSchema,
        db_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """Process a single table with enhanced error handling and performance monitoring."""
        schema_name = snowflake_schema.name
        table_identifier = self.identifiers.get_dataset_identifier(
            table.name, schema_name, db_name
        )
        
        logger.info(f"🔍 Processing table {table.name} -> {table_identifier}")

        try:
            # Get columns for table with performance monitoring
            start_time = time.time()
            table.columns = self.get_columns_for_table(
                table.name, snowflake_schema, db_name
            )
            table.column_count = len(table.columns)
            column_extraction_time = time.time() - start_time
            
            logger.info(
                f"✅ Extracted {table.column_count} columns for {table.name} "
                f"in {column_extraction_time:.2f}s"
            )

            # Get column tags if enabled
            if self.config.extract_tags != TagOption.skip:
                try:
                    start_time = time.time()
                    table.column_tags = self.tag_extractor.get_column_tags_for_table(
                        table.name, schema_name, db_name
                    )
                    tag_extraction_time = time.time() - start_time
                    logger.info(
                        f"✅ Extracted {len(table.column_tags)} column tags for {table.name} "
                        f"in {tag_extraction_time:.2f}s"
                    )
                except Exception as tag_e:
                    logger.warning(
                        f"Failed to extract column tags for {table.name}: {tag_e}"
                    )
                    table.column_tags = []
                    
        except Exception as e:
            logger.error(f"❌ Failed to process table {table.name}: {e}")
            self.structured_reporter.warning(
                "Failed to get columns for table", table_identifier, exc=e
            )
            # Set defaults to prevent downstream errors
            table.columns = []
            table.column_count = 0
            table.column_tags = []

        # Get table tags if enabled
        logger.info(f"🔍 DEBUG: extract_tags = {self.config.extract_tags} (type: {type(self.config.extract_tags)}), TagOption.skip = {TagOption.skip}")
        if self.config.extract_tags != TagOption.skip:
            logger.info(f"🔍 DEBUG: Extracting tags for table {table.name} in {db_name}.{schema_name}")
            table.tags = self.tag_extractor.get_tags_on_object(
                table_name=table.name,
                schema_name=schema_name,
                db_name=db_name,
                domain="table",
            )
            logger.info(f"🔍 DEBUG: Found {len(table.tags) if table.tags else 0} tags for table {table.name}")
        else:
            logger.info(f"🔍 DEBUG: Skipping tag extraction - extract_tags is {self.config.extract_tags}")

        if self.config.include_technical_schema:
            # Get primary keys if enabled
            if self.config.include_primary_keys:
                self.fetch_pk_for_table(table, schema_name, db_name, table_identifier)

            # Get foreign keys if enabled
            if self.config.include_foreign_keys:
                self.fetch_foreign_keys_for_table(
                    table, schema_name, db_name, table_identifier
                )

            # Generate dataset work units
            yield from self.gen_dataset_workunits(table, schema_name, db_name)

    def fetch_foreign_keys_for_table(
        self,
        table: SnowflakeTable,
        schema_name: str,
        db_name: str,
        table_identifier: str,
    ) -> None:
        """Fetch foreign key constraints for a table."""
        try:
            table.foreign_keys = self.get_fk_constraints_for_table(
                table.name, schema_name, db_name
            )
        except Exception as e:
            self.structured_reporter.warning(
                "Failed to get foreign keys for table", table_identifier, exc=e
            )

    def fetch_pk_for_table(
        self,
        table: SnowflakeTable,
        schema_name: str,
        db_name: str,
        table_identifier: str,
    ) -> None:
        """Fetch primary key constraint for a table."""
        try:
            table.pk = self.get_pk_constraints_for_table(
                table.name, schema_name, db_name
            )
        except Exception as e:
            self.structured_reporter.warning(
                "Failed to get primary key for table", table_identifier, exc=e
            )

    def _process_view(
        self,
        view: SnowflakeView,
        snowflake_schema: SnowflakeSchema,
        db_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """Process a single view."""
        schema_name = snowflake_schema.name
        view_name = self.identifiers.get_dataset_identifier(
            view.name, schema_name, db_name
        )

        try:
            # Get columns for view
            view.columns = self.get_columns_for_table(
                view.name, snowflake_schema, db_name
            )

            # Get column tags if enabled
            if self.config.extract_tags != TagOption.skip:
                view.column_tags = self.tag_extractor.get_column_tags_for_table(
                    view.name, schema_name, db_name
                )
        except Exception as e:
            self.structured_reporter.warning(
                "Failed to get columns for view", view_name, exc=e
            )

        # Get view tags if enabled
        if self.config.extract_tags != TagOption.skip:
            view.tags = self.tag_extractor.get_tags_on_object(
                table_name=view.name,
                schema_name=schema_name,
                db_name=db_name,
                domain="table",
            )

        if self.config.include_technical_schema:
            yield from self.gen_dataset_workunits(view, schema_name, db_name)

    def _process_tag(self, tag: SnowflakeTag) -> Iterable[MetadataWorkUnit]:
        """Process a single tag."""
        try:
            logger.info(f"🔍 DEBUG: Processing tag: {tag}")
            use_sp = self.config.extract_tags_as_structured_properties

            identifier = (
                self.snowflake_identifier(tag.structured_property_identifier())
                if use_sp
                else tag.tag_identifier()
            )
            logger.info(f"🔍 DEBUG: Generated identifier: {identifier}")

            logger.info(f"🔍 DEBUG: Checking if tag is processed...")
            if self.report.is_tag_processed(identifier):
                logger.info(f"🔍 DEBUG: Tag already processed, skipping")
                return

            logger.info(f"🔍 DEBUG: Marking tag as processed...")
            self.report.report_tag_processed(identifier)

            if use_sp:
                logger.info(f"🔍 DEBUG: Using structured properties, skipping workunit generation")
                return

            logger.info(f"🔍 DEBUG: Generating tag workunits...")
            yield from self.gen_tag_workunits(tag)
            logger.info(f"🔍 DEBUG: Tag processing completed successfully")
        except Exception as e:
            logger.error(f"Error in _process_tag for {tag}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _format_tags_as_structured_properties(
        self, tags: List[SnowflakeTag]
    ) -> Dict[str, str]:
        """Format tags as structured properties."""
        return {
            self.snowflake_identifier(tag.structured_property_identifier()): tag.value
            for tag in tags
        }

    def _safe_to_dict(self, obj) -> Dict[str, Any]:
        """Safely convert object to dictionary, handling FieldInfo objects."""
        try:
            # Handle Pydantic models first
            if hasattr(obj, 'model_dump'):
                try:
                    return obj.model_dump()
                except Exception as e:
                    logger.debug(f"model_dump() failed for {type(obj)}: {e}")
                    # Fall back to dict() method
                    try:
                        return obj.dict()
                    except Exception as e2:
                        logger.debug(f"dict() failed for {type(obj)}: {e2}")
                        # Fall back to manual serialization
                        pass
            elif hasattr(obj, 'to_dict'):
                try:
                    return obj.to_dict()
                except Exception as e:
                    logger.warning(f"to_dict() failed for {type(obj)}: {e}")
                    # Fall back to manual serialization
                    pass
            
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    # Skip FieldInfo objects and other non-serializable items
                    if hasattr(value, '__class__') and 'FieldInfo' in str(value.__class__):
                        continue
                    # Skip private attributes
                    if key.startswith('_'):
                        continue
                    # Skip Pydantic internal fields
                    if key in ['__fields__', '__field_set__', '__field_defaults__', '__config__', '__validators__']:
                        continue
                    # Skip Field objects from Pydantic
                    if hasattr(value, '__class__') and 'Field' in str(value.__class__):
                        continue
                    # Skip any object that might contain FieldInfo
                    if hasattr(value, '__class__') and 'pydantic' in str(value.__class__.__module__):
                        try:
                            # Try to serialize Pydantic objects safely
                            if hasattr(value, 'model_dump'):
                                result[key] = value.model_dump()
                            elif hasattr(value, 'dict'):
                                result[key] = value.dict()
                            else:
                                result[key] = str(value)
                        except Exception as e:
                            logger.debug(f"Failed to serialize Pydantic object {key}: {e}")
                            result[key] = str(value)
                    # Handle nested objects
                    elif hasattr(value, '__dict__') or hasattr(value, 'to_dict') or hasattr(value, 'model_dump'):
                        try:
                            result[key] = self._safe_to_dict(value)
                        except Exception as e:
                            logger.debug(f"Failed to serialize nested object {key}: {e}")
                            result[key] = str(value)
                    else:
                        result[key] = value
                return result
            else:
                return str(obj)
        except Exception as e:
            logger.warning(f"Failed to serialize object to dict: {e}")
            return {"error": f"Serialization failed: {str(e)}"}

    def gen_dataset_workunits(
        self,
        table: Union[SnowflakeTable, SnowflakeView, SnowflakeStream],
        schema_name: str,
        db_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """
        Generate all work units for a dataset (table, view, or stream).

        Args:
            table: Table, view, or stream object
            schema_name: Schema name
            db_name: Database name

        Yields:
            MetadataWorkUnit instances
        """
        try:
            # Process all tags first
            try:
                logger.info(f"🔍 DEBUG: Processing table tags for {table.name}")
                if table.tags:
                    for tag in table.tags:
                        yield from self._process_tag(tag)
                logger.info(f"🔍 DEBUG: Table tags processed successfully for {table.name}")
            except Exception as e:
                logger.error(f"Error processing table tags for {table.name}: {e}")
                raise

            # Process column tags
            try:
                logger.info(f"🔍 DEBUG: Processing column tags for {table.name}")
                if hasattr(table, 'column_tags') and table.column_tags:
                    for column_name in table.column_tags:
                        for tag in table.column_tags[column_name]:
                            yield from self._process_tag(tag)
                logger.info(f"🔍 DEBUG: Column tags processed successfully for {table.name}")
            except Exception as e:
                logger.error(f"Error processing column tags for {table.name}: {e}")
                raise

            # Generate dataset URN
            try:
                logger.info(f"🔍 DEBUG: Generating dataset URN for {table.name}")
                dataset_name = self.identifiers.get_dataset_identifier(
                    table.name, schema_name, db_name
                )
                dataset_urn = self.identifiers.gen_dataset_urn(dataset_name)
                logger.info(f"🔍 DEBUG: Dataset URN generated successfully for {table.name}: {dataset_urn}")
            except Exception as e:
                logger.error(f"Error generating dataset URN for {table.name}: {e}")
                raise

            # Status aspect
            try:
                status = Status(removed=False)
                yield MetadataWorkUnit(
                    id=f"{dataset_urn}-status",
                    mcp_raw={
                        "entityUrn": dataset_urn,
                        "aspect": self._safe_to_dict(status),
                        "aspectName": "status"
                    }
                )
            except Exception as e:
                logger.error(f"Error creating status workunit for {dataset_urn}: {e}")
                raise

            # Schema metadata aspect
            try:
                logger.info(f"🔍 DEBUG: Creating schema metadata for {dataset_urn}")
                schema_metadata = self.gen_schema_metadata(table, schema_name, db_name)
                logger.info(f"🔍 DEBUG: Schema metadata created successfully for {dataset_urn}")
                logger.info(f"🔍 DEBUG: Converting schema metadata to dict for {dataset_urn}")
                schema_dict = self._safe_to_dict(schema_metadata)
                logger.info(f"🔍 DEBUG: Schema metadata converted to dict successfully for {dataset_urn}")
                yield MetadataWorkUnit(
                    id=f"{dataset_urn}-schemaMetadata",
                    mcp_raw={
                        "entityUrn": dataset_urn,
                        "aspect": schema_dict,
                        "aspectName": "schemaMetadata"
                    }
                )
                logger.info(f"🔍 DEBUG: Schema metadata workunit created successfully for {dataset_urn}")
            except Exception as e:
                logger.error(f"Error creating schema metadata workunit for {dataset_urn}: {e}")
                logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

            # Dataset properties aspect
            try:
                dataset_properties = self.get_dataset_properties(table, schema_name, db_name)
                yield MetadataWorkUnit(
                    id=f"{dataset_urn}-datasetProperties",
                    mcp_raw={
                        "entityUrn": dataset_urn,
                        "aspect": self._safe_to_dict(dataset_properties),
                        "aspectName": "datasetProperties"
                    }
                )
            except Exception as e:
                logger.error(f"Error creating dataset properties workunit for {dataset_urn}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error in gen_dataset_workunits for {table.name}: {e}")
            raise

        # SubTypes aspect
        subTypes = SubTypes(types=[table.get_subtype()])
        yield MetadataWorkUnit(
            id=f"{dataset_urn}-subTypes",
            mcp_raw={
                "entityUrn": dataset_urn,
                "aspect": self._safe_to_dict(subTypes),
                "aspectName": "subTypes"
            }
        )

        # Container membership
        schema_container_key = self.identifiers.gen_schema_key(db_name, schema_name)
        yield from add_table_to_schema_container(
            dataset_urn=dataset_urn,
            parent_container_key=schema_container_key,
        )

        # Data platform instance aspect
        dpi_aspect = get_dataplatform_instance_aspect(
            dataset_urn=dataset_urn,
            platform=self.platform,
            platform_instance=self.config.platform_instance,
        )
        if dpi_aspect:
            yield dpi_aspect

        # Domain assignment
        if self.domain_registry:
            yield from get_domain_wu(
                dataset_name=dataset_name,
                entity_urn=dataset_urn,
                domain_config=self.config.domain,
                domain_registry=self.domain_registry,
            )

        # Tags processing
        if table.tags:
            if self.config.extract_tags_as_structured_properties:
                # Handle structured properties for tags
                structured_props = self._format_tags_as_structured_properties(table.tags)
                if structured_props:
                    yield MetadataWorkUnit(
                        id=f"{dataset_urn}-structuredProperties",
                        mcp_raw={
                            "entityUrn": dataset_urn,
                            "aspect": {"properties": structured_props},
                            "aspectName": "structuredProperties"
                        }
                    )
            else:
                # Handle regular tags
                tag_urns = [
                    f"urn:li:tag:{self.snowflake_identifier(tag.tag_identifier())}"
                    for tag in table.tags
                ]
                global_tags = GlobalTags(tags=tag_urns)
                yield MetadataWorkUnit(
                    id=f"{dataset_urn}-globalTags",
                    mcp_raw={
                        "entityUrn": dataset_urn,
                        "aspect": self._safe_to_dict(global_tags),
                        "aspectName": "globalTags"
                    }
                )

        # View properties for views
        if isinstance(table, SnowflakeView) and table.view_definition is not None:
            view_properties_aspect = ViewProperties(
                materialized=table.materialized,
                view_language="SQL",
                view_definition=(
                    table.view_definition
                    if self.config.include_view_definitions
                    else ""
                ),
            )

            yield MetadataWorkUnit(
                id=f"{dataset_urn}-viewProperties",
                mcp_raw={
                    "entityUrn": dataset_urn,
                    "aspect": self._safe_to_dict(view_properties_aspect),
                    "aspectName": "viewProperties"
                }
            )

    def get_dataset_properties(
        self,
        table: Union[SnowflakeTable, SnowflakeView, SnowflakeStream],
        schema_name: str,
        db_name: str,
    ) -> DatasetProperties:
        """Generate dataset properties for a table, view, or stream."""
        custom_properties = {}

        if isinstance(table, SnowflakeTable):
            custom_properties.update(
                {
                    k: v
                    for k, v in {
                        "CLUSTERING_KEY": table.clustering_key,
                        "IS_HYBRID": "true" if table.is_hybrid else None,
                        "IS_DYNAMIC": "true" if table.is_dynamic else None,
                        "IS_ICEBERG": "true" if table.is_iceberg else None,
                    }.items()
                    if v
                }
            )

            if isinstance(table, SnowflakeDynamicTable):
                if table.target_lag:
                    custom_properties["TARGET_LAG"] = table.target_lag

        if isinstance(table, SnowflakeView) and table.is_secure:
            custom_properties["IS_SECURE"] = "true"

        elif isinstance(table, SnowflakeStream):
            custom_properties.update(
                {
                    k: v
                    for k, v in {
                        "SOURCE_TYPE": table.source_type,
                        "TYPE": table.type,
                        "STALE": table.stale,
                        "MODE": table.mode,
                        "INVALID_REASON": table.invalid_reason,
                        "OWNER_ROLE_TYPE": table.owner_role_type,
                        "TABLE_NAME": table.table_name,
                        "BASE_TABLES": table.base_tables,
                        "STALE_AFTER": (
                            table.stale_after.isoformat() if table.stale_after else None
                        ),
                    }.items()
                    if v
                }
            )

        return DatasetProperties(
            name=table.name,
            created=table.created_time,
            last_modified=table.last_modified_time,
            description=table.comment,
            custom_properties=custom_properties,
            external_url=(
                self.snowsight_url_builder.get_external_url_for_table(
                    table.name,
                    schema_name,
                    db_name,
                    (
                        SnowflakeObjectDomain.DYNAMIC_TABLE
                        if isinstance(table, SnowflakeTable) and table.is_dynamic
                        else SnowflakeObjectDomain.TABLE
                        if isinstance(table, SnowflakeTable)
                        else SnowflakeObjectDomain.VIEW
                    ),
                )
                if self.snowsight_url_builder
                else None
            ),
        )

    def gen_tag_workunits(self, tag: SnowflakeTag) -> Iterable[MetadataWorkUnit]:
        """Generate work units for a tag."""
        tag_urn = f"urn:li:tag:{self.snowflake_identifier(tag.tag_identifier())}"

        tag_properties = {
            "name": tag.tag_display_name(),
            "description": (
                f"Represents the Snowflake tag `{tag._id_prefix_as_str()}` "
                f"with value `{tag.value}`."
            ),
        }

        yield MetadataWorkUnit(
            id=f"{tag_urn}-tagProperties",
            mcp_raw={
                "entityUrn": tag_urn,
                "aspect": tag_properties,
                "aspectName": "tagProperties"
            }
        )

    def gen_schema_metadata(
        self,
        table: Union[SnowflakeTable, SnowflakeView, SnowflakeStream],
        schema_name: str,
        db_name: str,
    ) -> SchemaMetadata:
        """Generate schema metadata for a dataset."""
        dataset_name = self.identifiers.get_dataset_identifier(
            table.name, schema_name, db_name
        )
        dataset_urn = self.identifiers.gen_dataset_urn(dataset_name)

        # Build foreign key constraints
        foreign_keys: Optional[List[ForeignKeyConstraint]] = None
        if isinstance(table, SnowflakeTable) and len(table.foreign_keys) > 0:
            foreign_keys = self.build_foreign_keys(table, dataset_urn)

        # Build schema fields
        fields = []
        for col in table.columns:
            field_path = self.snowflake_identifier(col.name)

            # Map Snowflake data type to DataGuild type
            data_type_class = SNOWFLAKE_FIELD_TYPE_MAPPINGS.get(col.data_type, NullType)
            schema_field_data_type = SchemaFieldDataType(
                data_type_class()
            )

            # Handle column tags
            global_tags = None
            if (hasattr(table, 'column_tags') and
                col.name in table.column_tags and
                not self.config.extract_tags_as_structured_properties):
                tag_urns = [
                    f"urn:li:tag:{self.snowflake_identifier(tag.tag_identifier())}"
                    for tag in table.column_tags[col.name]
                ]
                global_tags = GlobalTags(tags=tag_urns)

            schema_field = SchemaField(
                name=field_path,
                type=schema_field_data_type,
                description=col.comment,
                nullable=col.is_nullable,
                is_primary_key=(
                    col.name in table.pk.column_names
                    if isinstance(table, SnowflakeTable) and table.pk is not None
                    else False
                ),
                tags=set(tag.tag_identifier() for tag in table.column_tags.get(col.name, [])) if hasattr(table, 'column_tags') and col.name in table.column_tags else set(),
            )
            fields.append(schema_field)

        schema_metadata = SchemaMetadata(
            name=dataset_name,
            platform=f"urn:li:dataPlatform:{self.platform}",
            version=0,
            hash="",
            fields=fields,
        )

        # Register with aggregator if available
        if self.aggregator and hasattr(self.aggregator, 'register_schema'):
            self.aggregator.register_schema(urn=dataset_urn, schema=schema_metadata)

        return schema_metadata

    def build_foreign_keys(
        self, table: SnowflakeTable, dataset_urn: str
    ) -> List[ForeignKeyConstraint]:
        """Build foreign key constraints for a table."""
        foreign_keys = []
        for fk in table.foreign_keys:
            foreign_dataset = self.identifiers.gen_dataset_urn(
                self.identifiers.get_dataset_identifier(
                    fk.referred_table, fk.referred_schema, fk.referred_database
                )
            )

            foreign_key_constraint = ForeignKeyConstraint(
                name=fk.name,
                column_names=fk.column_names,
                referenced_table=foreign_dataset,
                referenced_columns=fk.referred_column_names,
            )
            foreign_keys.append(foreign_key_constraint)

        return foreign_keys

    def gen_database_containers(
        self, database: SnowflakeDatabase
    ) -> Iterable[MetadataWorkUnit]:
        """Generate database container work units."""
        database_container_key = self.identifiers.gen_database_key(database.name)

        yield from gen_database_container(
            name=database.name,
            database=self.snowflake_identifier(database.name),
            database_container_key=database_container_key,
            sub_types=["Database"],
            domain_registry=self.domain_registry,
            domain_config=self.config.domain,
            external_url=(
                self.snowsight_url_builder.get_external_url_for_database(database.name)
                if self.snowsight_url_builder
                else None
            ),
            description=database.comment,
            created=(
                int(database.created.timestamp() * 1000)
                if database.created is not None
                else None
            ),
            last_modified=(
                int(database.last_altered.timestamp() * 1000)
                if database.last_altered is not None
                else (
                    int(database.created.timestamp() * 1000)
                    if database.created is not None
                    else None
                )
            ),
            tags=(
                [
                    self.snowflake_identifier(tag.tag_identifier())
                    for tag in database.tags
                ]
                if database.tags
                and not self.config.extract_tags_as_structured_properties
                else None
            ),
            structured_properties=(
                self._format_tags_as_structured_properties(database.tags)
                if database.tags and self.config.extract_tags_as_structured_properties
                else None
            ),
        )

    def gen_schema_containers(
        self, schema: SnowflakeSchema, db_name: str
    ) -> Iterable[MetadataWorkUnit]:
        """Generate schema container work units."""
        database_container_key = self.identifiers.gen_database_key(db_name)
        schema_container_key = self.identifiers.gen_schema_key(db_name, schema.name)

        yield from gen_schema_container(
            name=schema.name,
            schema=self.snowflake_identifier(schema.name),
            database=self.snowflake_identifier(db_name),
            database_container_key=database_container_key,
            domain_config=self.config.domain,
            schema_container_key=schema_container_key,
            sub_types=["Schema"],
            domain_registry=self.domain_registry,
            description=schema.comment,
            external_url=(
                self.snowsight_url_builder.get_external_url_for_schema(
                    schema.name, db_name
                )
                if self.snowsight_url_builder
                else None
            ),
            created=(
                int(schema.created.timestamp() * 1000)
                if schema.created is not None
                else None
            ),
            last_modified=(
                int(schema.last_altered.timestamp() * 1000)
                if schema.last_altered is not None
                else None
            ),
            tags=(
                [self.snowflake_identifier(tag.tag_identifier()) for tag in schema.tags]
                if schema.tags and not self.config.extract_tags_as_structured_properties
                else None
            ),
            structured_properties=(
                self._format_tags_as_structured_properties(schema.tags)
                if schema.tags and self.config.extract_tags_as_structured_properties
                else None
            ),
        )

    def get_tables_for_schema(
        self, schema_name: str, db_name: str
    ) -> List[SnowflakeTable]:
        """Get tables for a schema from data dictionary."""
        logger.info(f"🔍 DEBUG: get_tables_for_schema called for {db_name}.{schema_name}")
        
        tables = self.data_dictionary.get_tables_for_database(db_name)
        logger.info(f"🔍 DEBUG: get_tables_for_database returned {len(tables) if tables else 'None'} tables for {db_name}")

        if tables is None:
            logger.info(f"🔍 DEBUG: tables is None, calling get_tables_for_schema directly")
            self.report.num_get_tables_for_schema_queries += 1
            result = self.data_dictionary.get_tables_for_schema(
                db_name=db_name,
                schema_name=schema_name,
            )
            logger.info(f"🔍 DEBUG: get_tables_for_schema returned {len(result)} tables for {db_name}.{schema_name}")
            return result

        schema_tables = tables.get(schema_name, [])
        logger.info(f"🔍 DEBUG: Found {len(schema_tables)} tables for schema {schema_name} in cached database tables")
        return schema_tables

    def get_views_for_schema(
        self, schema_name: str, db_name: str
    ) -> List[SnowflakeView]:
        """Get views for a schema from data dictionary."""
        logger.info(f"🔍 DEBUG: get_views_for_schema called for {db_name}.{schema_name}")
        
        views = self.data_dictionary.get_views_for_database(db_name)
        logger.info(f"🔍 DEBUG: get_views_for_database returned {len(views) if views else 'None'} views for {db_name}")

        if views is not None:
            schema_views = views.get(schema_name, [])
            logger.info(f"🔍 DEBUG: Found {len(schema_views)} views for schema {schema_name} in cached database views")
            return schema_views

        logger.info(f"🔍 DEBUG: views is None, calling get_views_for_schema_using_show directly")
        self.report.num_get_views_for_schema_queries += 1
        result = self.data_dictionary.get_views_for_schema_using_show(
            db_name=db_name,
            schema_name=schema_name,
        )
        logger.info(f"🔍 DEBUG: get_views_for_schema_using_show returned {len(result)} views for {db_name}.{schema_name}")
        return result

    def get_columns_for_table(
        self, table_name: str, snowflake_schema: SnowflakeSchema, db_name: str
    ) -> List[SnowflakeColumn]:
        """Get columns for a table from data dictionary."""
        schema_name = snowflake_schema.name
        columns = self.data_dictionary.get_columns_for_schema(
            schema_name,
            db_name,
            cache_exclude_all_objects=itertools.chain(
                snowflake_schema.tables, snowflake_schema.views
            ),
        )

        return columns.get(table_name, [])

    def get_pk_constraints_for_table(
        self, table_name: str, schema_name: str, db_name: str
    ) -> Optional[SnowflakePK]:
        """Get primary key constraints for a table."""
        constraints = self.data_dictionary.get_pk_constraints_for_schema(
            schema_name, db_name
        )
        return constraints.get(table_name)

    def get_fk_constraints_for_table(
        self, table_name: str, schema_name: str, db_name: str
    ) -> List[SnowflakeFK]:
        """Get foreign key constraints for a table."""
        constraints = self.data_dictionary.get_fk_constraints_for_schema(
            schema_name, db_name
        )
        return constraints.get(table_name, [])

    def _external_tables_ddl_lineage(
        self, discovered_tables: List[str]
    ) -> Iterable[KnownLineageMapping]:
        """Handle external table DDL lineage extraction."""
        external_tables_query: str = SnowflakeQuery.show_external_tables()
        try:
            for db_row in self.connection.query(external_tables_query):
                key = self.identifiers.get_dataset_identifier(
                    db_row["name"], db_row["schema_name"], db_row["database_name"]
                )

                if key not in discovered_tables:
                    continue

                if db_row["location"].startswith("s3://"):
                    # Create S3 URN for lineage
                    s3_urn = f"urn:li:dataset:(urn:li:dataPlatform:s3,{db_row['location']},{self.config.env})"

                    yield KnownLineageMapping(
                        upstream_urn=s3_urn,
                        downstream_urn=self.identifiers.gen_dataset_urn(key),
                    )
                    self.report.num_external_table_edges_scanned += 1

        except Exception as e:
            self.structured_reporter.warning(
                "External table DDL lineage extraction failed",
                exc=e,
            )

    # Stream Processing Methods

    def fetch_streams_for_schema(
        self, snowflake_schema: SnowflakeSchema, db_name: str
    ) -> List[SnowflakeStream]:
        """Fetch and filter streams for a schema."""
        try:
            streams: List[SnowflakeStream] = []
            for stream in self.get_streams_for_schema(snowflake_schema.name, db_name):
                stream_identifier = self.identifiers.get_dataset_identifier(
                    stream.name, snowflake_schema.name, db_name
                )

                self.report.report_entity_scanned(stream_identifier, "stream")

                if not self.filters.is_dataset_pattern_allowed(
                    stream_identifier, SnowflakeObjectDomain.STREAM
                ):
                    self.report.report_dropped(stream_identifier)
                else:
                    streams.append(stream)

            snowflake_schema.streams = [stream.name for stream in streams]
            return streams
        except Exception as e:
            self.structured_reporter.warning(
                title="Failed to get streams for schema",
                message="Please check permissions"
                if isinstance(e, SnowflakePermissionError)
                else "",
                context=f"{db_name}.{snowflake_schema.name}",
                exc=e,
            )
            return []

    def get_streams_for_schema(
        self, schema_name: str, db_name: str
    ) -> List[SnowflakeStream]:
        """Get streams for a schema from data dictionary."""
        streams = self.data_dictionary.get_streams_for_database(db_name)
        return streams.get(schema_name, [])

    def _process_stream(
        self,
        stream: SnowflakeStream,
        snowflake_schema: SnowflakeSchema,
        db_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """Process a single stream."""
        schema_name = snowflake_schema.name

        try:
            # Get columns for stream (includes source columns + metadata columns)
            stream.columns = self.get_columns_for_stream(stream.table_name)
            yield from self.gen_dataset_workunits(stream, schema_name, db_name)

            # Add lineage for streams
            if self.config.include_column_lineage:
                with self.report.new_stage(f"*: {LINEAGE_EXTRACTION}"):
                    self.populate_stream_upstreams(stream, db_name, schema_name)

        except Exception as e:
            self.structured_reporter.warning(
                "Failed to get columns for stream:", stream.name, exc=e
            )

    def get_columns_for_stream(
        self,
        source_object: str,  # Qualified name of source table/view
    ) -> List[SnowflakeColumn]:
        """
        Get column information for a stream.

        Streams include all columns from source object plus metadata columns:
        - METADATA$ACTION
        - METADATA$ISUPDATE
        - METADATA$ROW_ID
        """
        columns: List[SnowflakeColumn] = []
        source_parts = split_qualified_name(source_object)
        source_db, source_schema, source_name = source_parts

        # Get columns from source object
        source_columns = self.data_dictionary.get_columns_for_schema(
            source_schema, source_db, itertools.chain([source_name])
        ).get(source_name, [])

        columns.extend(source_columns)

        # Add standard stream metadata columns
        metadata_columns = [
            SnowflakeColumn(
                name="METADATA$ACTION",
                ordinal_position=len(columns) + 1,
                is_nullable=False,
                data_type="VARCHAR",
                comment="Type of DML operation (INSERT/DELETE)",
                character_maximum_length=10,
                numeric_precision=None,
                numeric_scale=None,
            ),
            SnowflakeColumn(
                name="METADATA$ISUPDATE",
                ordinal_position=len(columns) + 2,
                is_nullable=False,
                data_type="BOOLEAN",
                comment="Whether row is from UPDATE operation",
                character_maximum_length=None,
                numeric_precision=None,
                numeric_scale=None,
            ),
            SnowflakeColumn(
                name="METADATA$ROW_ID",
                ordinal_position=len(columns) + 3,
                is_nullable=False,
                data_type="NUMBER",
                comment="Unique row identifier",
                character_maximum_length=None,
                numeric_precision=38,
                numeric_scale=0,
            ),
        ]

        columns.extend(metadata_columns)
        return columns

    def populate_stream_upstreams(
        self, stream: SnowflakeStream, db_name: str, schema_name: str
    ) -> None:
        """Populate stream upstream lineage information."""
        self.report.num_streams_with_known_upstreams += 1
        if self.aggregator:
            source_parts = split_qualified_name(stream.table_name)
            source_db, source_schema, source_name = source_parts

            dataset_identifier = self.identifiers.get_dataset_identifier(
                stream.name, schema_name, db_name
            )
            dataset_urn = self.identifiers.gen_dataset_urn(dataset_identifier)

            upstream_identifier = self.identifiers.get_dataset_identifier(
                source_name, source_schema, source_db
            )
            upstream_urn = self.identifiers.gen_dataset_urn(upstream_identifier)

            logger.debug(f"Stream lineage: {upstream_urn} -> {dataset_urn}")

            self.aggregator.add_known_lineage_mapping(
                upstream_urn=upstream_urn,
                downstream_urn=dataset_urn,
                lineage_type="COPY",  # Streams are typically copy operations
            )

    # Procedure Processing Methods

    def fetch_procedures_for_schema(
        self, snowflake_schema: SnowflakeSchema, db_name: str
    ) -> List[BaseProcedure]:
        """Fetch and filter procedures for a schema."""
        try:
            procedures: List[BaseProcedure] = []
            for procedure in self.get_procedures_for_schema(snowflake_schema, db_name):
                procedure_qualified_name = self.identifiers.get_dataset_identifier(
                    procedure.name, snowflake_schema.name, db_name
                )
                self.report.report_entity_scanned(procedure_qualified_name, "procedure")

                if self.filters.is_procedure_allowed(procedure_qualified_name):
                    procedures.append(procedure)
                else:
                    self.report.report_dropped(procedure_qualified_name)
            return procedures
        except Exception as e:
            self.structured_reporter.warning(
                title="Failed to get procedures for schema",
                message="Please check permissions"
                if isinstance(e, SnowflakePermissionError)
                else "",
                context=f"{db_name}.{snowflake_schema.name}",
                exc=e,
            )
            return []

    def get_procedures_for_schema(
        self,
        snowflake_schema: SnowflakeSchema,
        db_name: str,
    ) -> List[BaseProcedure]:
        """Get procedures for a schema from data dictionary."""
        procedures = self.data_dictionary.get_procedures_for_database(db_name)
        return procedures.get(snowflake_schema.name, [])

    def _process_procedure(
        self,
        procedure: BaseProcedure,
        snowflake_schema: SnowflakeSchema,
        db_name: str,
    ) -> Iterable[MetadataWorkUnit]:
        """Process a single stored procedure."""
        try:
            yield from generate_procedure_workunits(
                procedure,
                database_key=self.identifiers.gen_database_key(db_name),
                schema_key=self.identifiers.gen_schema_key(
                    db_name, snowflake_schema.name
                ),
                schema_resolver=(
                    self.aggregator.schema_resolver if self.aggregator else None
                ),
            )
        except Exception as e:
            self.structured_reporter.warning(
                title="Failed to ingest stored procedure",
                message="",
                context=procedure.name,
                exc=e,
            )


# Export the main class
__all__ = [
    'SnowflakeSchemaGenerator',
    'SNOWFLAKE_FIELD_TYPE_MAPPINGS',
]
