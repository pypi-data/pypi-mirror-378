"""
DataGuild Database Migration Script

Comprehensive migration script to move JSON metadata from DataGuild extraction
to both PostgreSQL (for structured data) and Neo4j (for lineage relationships).
"""

import json
import logging
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import traceback

# Add src path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dataguild.database.postgresql_client import PostgreSQLClient, create_postgresql_client_from_env
from dataguild.database.neo4j_client import Neo4jClient, create_neo4j_client_from_env

logger = logging.getLogger(__name__)


class DataGuildMigration:
    """
    Comprehensive migration tool for DataGuild metadata.
    
    Migrates JSON metadata to both PostgreSQL (structured data) and Neo4j (lineage).
    Handles entities, datasets, columns, usage statistics, and lineage relationships.
    """
    
    def __init__(self, postgres_config: Optional[Dict[str, Any]] = None, 
                 neo4j_config: Optional[Dict[str, Any]] = None):
        """
        Initialize migration tool.
        
        Args:
            postgres_config: PostgreSQL configuration
            neo4j_config: Neo4j configuration
        """
        self.postgres_client = None
        self.neo4j_client = None
        self.migration_stats = {
            'entities_processed': 0,
            'datasets_processed': 0,
            'columns_processed': 0,
            'lineage_relationships_created': 0,
            'usage_stats_processed': 0,
            'errors': []
        }
        
        # Initialize clients
        self._init_postgres_client(postgres_config)
        self._init_neo4j_client(neo4j_config)
    
    def _init_postgres_client(self, config: Optional[Dict[str, Any]]) -> None:
        """Initialize PostgreSQL client."""
        try:
            if config:
                self.postgres_client = PostgreSQLClient(config)
            else:
                self.postgres_client = create_postgresql_client_from_env()
            logger.info("PostgreSQL client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL client: {e}")
            raise
    
    def _init_neo4j_client(self, config: Optional[Dict[str, Any]]) -> None:
        """Initialize Neo4j client."""
        try:
            if config:
                self.neo4j_client = Neo4jClient(config)
            else:
                self.neo4j_client = create_neo4j_client_from_env()
            logger.info("Neo4j client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j client: {e}")
            raise
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """
        Migrate metadata from JSON file to both databases.
        
        Args:
            json_file_path: Path to JSON metadata file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting migration from {json_file_path}")
            
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Process different types of metadata
            self._migrate_entities(metadata)
            self._migrate_datasets(metadata)
            self._migrate_columns(metadata)
            self._migrate_lineage(metadata)
            self._migrate_usage_stats(metadata)
            self._migrate_operational_events(metadata)
            
            # Print migration summary
            self._print_migration_summary()
            
            logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _migrate_entities(self, metadata: Dict[str, Any]) -> None:
        """Migrate entity data to both databases."""
        logger.info("Migrating entities...")
        
        # Process databases
        for db_data in metadata.get('processed_metadata', {}).get('databases', []):
            try:
                entity_data = {
                    'urn': f"urn:li:container:{db_data.get('name', '').lower()}",
                    'entity_type': 'CONTAINER',
                    'name': db_data.get('name'),
                    'platform': 'snowflake',
                    'description': db_data.get('description'),
                    'metadata': {
                        'type': 'DATABASE',
                        'properties': db_data.get('properties', {}),
                        'created': db_data.get('created'),
                        'last_modified': db_data.get('last_modified')
                    },
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                
                # Store in PostgreSQL
                entity_id = self.postgres_client.store_entity(entity_data)
                
                # Store in Neo4j
                self.neo4j_client.create_entity_node(entity_data)
                
                self.migration_stats['entities_processed'] += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate database {db_data.get('name')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
        
        # Process schemas
        for schema_data in metadata.get('processed_metadata', {}).get('schemas', []):
            try:
                entity_data = {
                    'urn': f"urn:li:container:{schema_data.get('name', '').lower()}",
                    'entity_type': 'CONTAINER',
                    'name': schema_data.get('name'),
                    'platform': 'snowflake',
                    'description': schema_data.get('description'),
                    'metadata': {
                        'type': 'SCHEMA',
                        'database': schema_data.get('database'),
                        'schema': schema_data.get('schema'),
                        'properties': schema_data.get('properties', {})
                    },
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                
                # Store in PostgreSQL
                entity_id = self.postgres_client.store_entity(entity_data)
                
                # Store in Neo4j
                self.neo4j_client.create_entity_node(entity_data)
                
                self.migration_stats['entities_processed'] += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate schema {schema_data.get('name')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _migrate_datasets(self, metadata: Dict[str, Any]) -> None:
        """Migrate dataset data to both databases."""
        logger.info("Migrating datasets...")
        
        # Process tables
        for table_data in metadata.get('processed_metadata', {}).get('tables', []):
            try:
                # Create entity data
                entity_urn = self._extract_urn_from_dataset_data(table_data)
                entity_data = {
                    'urn': entity_urn,
                    'entity_type': 'DATASET',
                    'name': table_data.get('name'),
                    'platform': 'snowflake',
                    'description': table_data.get('description'),
                    'metadata': {
                        'type': 'TABLE',
                        'database': table_data.get('database'),
                        'schema': table_data.get('schema'),
                        'properties': table_data.get('properties', {}),
                        'custom_properties': table_data.get('custom_properties', {}),
                        'tags': table_data.get('tags', [])
                    },
                    'created_at': table_data.get('created'),
                    'updated_at': table_data.get('last_modified')
                }
                
                # Store entity in PostgreSQL
                entity_id = self.postgres_client.store_entity(entity_data)
                
                # Store dataset in PostgreSQL
                dataset_id = self.postgres_client.store_dataset(table_data, entity_id)
                
                # Store in Neo4j
                self.neo4j_client.create_entity_node(entity_data)
                self.neo4j_client.create_dataset_node(table_data, entity_urn)
                
                self.migration_stats['datasets_processed'] += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate table {table_data.get('name')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
        
        # Process views
        for view_data in metadata.get('processed_metadata', {}).get('views', []):
            try:
                # Create entity data
                entity_urn = self._extract_urn_from_dataset_data(view_data)
                entity_data = {
                    'urn': entity_urn,
                    'entity_type': 'DATASET',
                    'name': view_data.get('name'),
                    'platform': 'snowflake',
                    'description': view_data.get('description'),
                    'metadata': {
                        'type': 'VIEW',
                        'database': view_data.get('database'),
                        'schema': view_data.get('schema'),
                        'properties': view_data.get('properties', {}),
                        'custom_properties': view_data.get('custom_properties', {}),
                        'tags': view_data.get('tags', [])
                    },
                    'created_at': view_data.get('created'),
                    'updated_at': view_data.get('last_modified')
                }
                
                # Store entity in PostgreSQL
                entity_id = self.postgres_client.store_entity(entity_data)
                
                # Store dataset in PostgreSQL
                dataset_id = self.postgres_client.store_dataset(view_data, entity_id)
                
                # Store in Neo4j
                self.neo4j_client.create_entity_node(entity_data)
                self.neo4j_client.create_dataset_node(view_data, entity_urn)
                
                self.migration_stats['datasets_processed'] += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate view {view_data.get('name')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _migrate_columns(self, metadata: Dict[str, Any]) -> None:
        """Migrate column data to both databases."""
        logger.info("Migrating columns...")
        
        # Process columns from schema metadata
        for column_data in metadata.get('processed_metadata', {}).get('columns', []):
            try:
                # Find parent dataset
                dataset_urn = self._find_dataset_urn_for_column(column_data, metadata)
                if not dataset_urn:
                    continue
                
                # Store column in PostgreSQL
                # First, get the dataset ID
                dataset_entity = self.postgres_client.get_entity_by_urn(dataset_urn)
                if dataset_entity:
                    dataset_record = self.postgres_client.get_dataset_with_columns(dataset_urn)
                    if dataset_record:
                        # Store single column
                        self.postgres_client.store_columns([column_data], dataset_record['id'])
                
                # Store column in Neo4j
                column_urn = f"{dataset_urn}:{column_data.get('name')}"
                self.neo4j_client.create_column_nodes([column_data], dataset_urn)
                
                self.migration_stats['columns_processed'] += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate column {column_data.get('name')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _migrate_lineage(self, metadata: Dict[str, Any]) -> None:
        """Migrate lineage relationships to both databases."""
        logger.info("Migrating lineage relationships...")
        
        # Process lineage from processed metadata
        for lineage_data in metadata.get('processed_metadata', {}).get('lineage', []):
            try:
                source_urn = lineage_data.get('entity_urn')
                if not source_urn:
                    continue
                
                # Extract upstream and downstream relationships
                upstream = lineage_data.get('upstream', [])
                downstream = lineage_data.get('downstream', [])
                
                # Create upstream relationships
                for upstream_urn in upstream:
                    if isinstance(upstream_urn, str):
                        # Store in PostgreSQL
                        self.postgres_client.store_lineage_relationship(
                            upstream_urn, source_urn, "UPSTREAM_OF", "UPSTREAM"
                        )
                        
                        # Store in Neo4j
                        self.neo4j_client.create_lineage_relationship(
                            upstream_urn, source_urn, "UPSTREAM_OF"
                        )
                        
                        self.migration_stats['lineage_relationships_created'] += 1
                
                # Create downstream relationships
                for downstream_urn in downstream:
                    if isinstance(downstream_urn, str):
                        # Store in PostgreSQL
                        self.postgres_client.store_lineage_relationship(
                            source_urn, downstream_urn, "DOWNSTREAM_OF", "DOWNSTREAM"
                        )
                        
                        # Store in Neo4j
                        self.neo4j_client.create_lineage_relationship(
                            source_urn, downstream_urn, "DOWNSTREAM_OF"
                        )
                        
                        self.migration_stats['lineage_relationships_created'] += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate lineage for {lineage_data.get('entity_urn')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
        
        # Process lineage from raw workunits
        for workunit in metadata.get('raw_workunits', []):
            try:
                if 'lineage_' in workunit.get('workunit_id', ''):
                    # Extract lineage information from workunit
                    self._process_lineage_workunit(workunit)
                    
            except Exception as e:
                error_msg = f"Failed to process lineage workunit {workunit.get('workunit_id')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _migrate_usage_stats(self, metadata: Dict[str, Any]) -> None:
        """Migrate usage statistics to both databases."""
        logger.info("Migrating usage statistics...")
        
        for usage_data in metadata.get('processed_metadata', {}).get('usage_stats', []):
            try:
                entity_urn = usage_data.get('entity_urn')
                if not entity_urn:
                    continue
                
                # Get entity ID
                entity = self.postgres_client.get_entity_by_urn(entity_urn)
                if not entity:
                    continue
                
                # Store in PostgreSQL
                self.postgres_client.store_usage_stats(usage_data, entity['id'])
                
                self.migration_stats['usage_stats_processed'] += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate usage stats for {usage_data.get('entity_urn')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _migrate_operational_events(self, metadata: Dict[str, Any]) -> None:
        """Migrate operational events to PostgreSQL."""
        logger.info("Migrating operational events...")
        
        for event_data in metadata.get('processed_metadata', {}).get('operational_stats', []):
            try:
                entity_urn = event_data.get('entity_urn')
                if not entity_urn:
                    continue
                
                # Get entity ID
                entity = self.postgres_client.get_entity_by_urn(entity_urn)
                if not entity:
                    continue
                
                # Store operational event
                conn = self.postgres_client._get_connection()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO operational_events (
                                entity_id, event_type, operation_type, actor,
                                timestamp, duration_ms, status, error_message, metadata
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            entity['id'],
                            event_data.get('workunit_type', 'unknown'),
                            event_data.get('operational_data', {}).get('operationType'),
                            event_data.get('operational_data', {}).get('actor'),
                            event_data.get('extraction_timestamp'),
                            event_data.get('operational_data', {}).get('duration_ms'),
                            'completed',
                            None,
                            json.dumps(event_data.get('operational_data', {}))
                        ))
                        conn.commit()
                finally:
                    self.postgres_client._return_connection(conn)
                
            except Exception as e:
                error_msg = f"Failed to migrate operational event for {event_data.get('entity_urn')}: {e}"
                logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _extract_urn_from_dataset_data(self, dataset_data: Dict[str, Any]) -> str:
        """Extract URN from dataset data."""
        urn = dataset_data.get('entity_urn')
        if urn:
            return urn
        
        # Construct URN from dataset information
        database = dataset_data.get('database', 'unknown')
        schema = dataset_data.get('schema', 'unknown')
        name = dataset_data.get('name', 'unknown')
        
        return f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{database}.{schema}.{name},PROD)"
    
    def _find_dataset_urn_for_column(self, column_data: Dict[str, Any], metadata: Dict[str, Any]) -> Optional[str]:
        """Find the dataset URN for a column."""
        # Try to find from entity_urn in column data
        entity_urn = column_data.get('entity_urn')
        if entity_urn:
            return entity_urn
        
        # Try to match by workunit_id
        workunit_id = column_data.get('workunit_id')
        if workunit_id:
            # Look through raw workunits to find matching dataset
            for workunit in metadata.get('raw_workunits', []):
                if workunit.get('workunit_id') == workunit_id:
                    mcp_raw = workunit.get('mcp_raw', {})
                    if mcp_raw:
                        return mcp_raw.get('entityUrn')
        
        return None
    
    def _process_lineage_workunit(self, workunit: Dict[str, Any]) -> None:
        """Process lineage information from a workunit."""
        try:
            workunit_id = workunit.get('workunit_id', '')
            if 'lineage_' in workunit_id:
                # Extract entity URN from workunit ID
                entity_urn = workunit_id.replace('lineage_', '').split('_')[0]
                
                # Try to extract lineage details from workunit metadata
                mcp_raw = workunit.get('mcp_raw', {})
                if mcp_raw:
                    aspect_data = mcp_raw.get('aspect', {})
                    # Process lineage aspect data
                    self._process_lineage_aspect_data(entity_urn, aspect_data)
                
        except Exception as e:
            logger.warning(f"Failed to process lineage workunit: {e}")
    
    def _process_lineage_aspect_data(self, entity_urn: str, aspect_data: Dict[str, Any]) -> None:
        """Process lineage aspect data."""
        try:
            # Extract upstream and downstream relationships
            upstream = aspect_data.get('upstreams', [])
            downstream = aspect_data.get('downstreams', [])
            
            # Create relationships
            for upstream_urn in upstream:
                if isinstance(upstream_urn, str):
                    self.postgres_client.store_lineage_relationship(
                        upstream_urn, entity_urn, "UPSTREAM_OF", "UPSTREAM"
                    )
                    self.neo4j_client.create_lineage_relationship(
                        upstream_urn, entity_urn, "UPSTREAM_OF"
                    )
                    self.migration_stats['lineage_relationships_created'] += 1
            
            for downstream_urn in downstream:
                if isinstance(downstream_urn, str):
                    self.postgres_client.store_lineage_relationship(
                        entity_urn, downstream_urn, "DOWNSTREAM_OF", "DOWNSTREAM"
                    )
                    self.neo4j_client.create_lineage_relationship(
                        entity_urn, downstream_urn, "DOWNSTREAM_OF"
                    )
                    self.migration_stats['lineage_relationships_created'] += 1
                    
        except Exception as e:
            logger.warning(f"Failed to process lineage aspect data: {e}")
    
    def _print_migration_summary(self) -> None:
        """Print migration summary."""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Entities processed: {self.migration_stats['entities_processed']}")
        print(f"Datasets processed: {self.migration_stats['datasets_processed']}")
        print(f"Columns processed: {self.migration_stats['columns_processed']}")
        print(f"Lineage relationships created: {self.migration_stats['lineage_relationships_created']}")
        print(f"Usage stats processed: {self.migration_stats['usage_stats_processed']}")
        print(f"Errors encountered: {len(self.migration_stats['errors'])}")
        
        if self.migration_stats['errors']:
            print("\nERRORS:")
            for error in self.migration_stats['errors'][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.migration_stats['errors']) > 10:
                print(f"  ... and {len(self.migration_stats['errors']) - 10} more errors")
        
        print("="*60)
    
    def close(self) -> None:
        """Close database connections."""
        if self.postgres_client:
            self.postgres_client.close()
        if self.neo4j_client:
            self.neo4j_client.close()


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Migrate DataGuild JSON metadata to PostgreSQL and Neo4j',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic migration
  python migration_script.py --json-file metadata_final_usage_complete.json
  
  # Migration with custom database configs
  python migration_script.py --json-file metadata.json \\
    --postgres-host localhost --postgres-db dataguild \\
    --neo4j-uri bolt://localhost:7687 --neo4j-database neo4j
        """
    )
    
    parser.add_argument('--json-file', '-j', required=True,
                       help='Path to JSON metadata file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    # PostgreSQL options
    parser.add_argument('--postgres-host', default='localhost',
                       help='PostgreSQL host')
    parser.add_argument('--postgres-port', type=int, default=5432,
                       help='PostgreSQL port')
    parser.add_argument('--postgres-db', default='dataguild',
                       help='PostgreSQL database name')
    parser.add_argument('--postgres-user', default='dataguild',
                       help='PostgreSQL username')
    parser.add_argument('--postgres-password', default='dataguild',
                       help='PostgreSQL password')
    
    # Neo4j options
    parser.add_argument('--neo4j-uri', default='bolt://localhost:7687',
                       help='Neo4j URI')
    parser.add_argument('--neo4j-username', default='neo4j',
                       help='Neo4j username')
    parser.add_argument('--neo4j-password', default='neo4j',
                       help='Neo4j password')
    parser.add_argument('--neo4j-database', default='neo4j',
                       help='Neo4j database name')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create migration tool
        postgres_config = {
            'host': args.postgres_host,
            'port': args.postgres_port,
            'database': args.postgres_db,
            'username': args.postgres_user,
            'password': args.postgres_password
        }
        
        neo4j_config = {
            'uri': args.neo4j_uri,
            'username': args.neo4j_username,
            'password': args.neo4j_password,
            'database': args.neo4j_database
        }
        
        migration = DataGuildMigration(postgres_config, neo4j_config)
        
        # Run migration
        success = migration.migrate_from_json(args.json_file)
        
        # Close connections
        migration.close()
        
        if success:
            print("✅ Migration completed successfully!")
            return 0
        else:
            print("❌ Migration failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Migration interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())


