#!/usr/bin/env python3
"""
Advanced usage example for DataGuild Snowflake Connector

This example demonstrates advanced features including custom filtering,
error handling, and performance optimization.
"""

import json
import logging
from typing import Dict, Any, List
from dataguild_snowflake_connector import SnowflakeV2Source, SnowflakeV2Config
from dataguild.api.common import PipelineContext


def setup_logging(verbose: bool = True):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('snowflake_extraction.log')
        ]
    )


def create_advanced_config() -> SnowflakeV2Config:
    """Create an advanced configuration with custom settings"""
    return SnowflakeV2Config(
        # Basic connection parameters
        account_id="your-account.snowflakecomputing.com",
        username="your-username",
        password="your-password",
        warehouse="your-warehouse",
        database="your-database",
        schema="your-schema",
        role="your-role",
        
        # Extraction settings
        include_usage_stats=True,
        include_table_lineage=True,
        include_column_lineage=True,
        include_tags=True,
        include_views=True,
        include_tables_bool=True,
        include_streams=True,
        include_procedures=True,
        
        # Performance settings
        max_workers=8,
        connection_timeout=300,
        query_timeout=600,
        
        # Custom filtering
        database_pattern={
            "allow": ["PROD_DATABASE", "STAGING_DATABASE"],
            "deny": ["TEMP_*", "TEST_*"],
            "ignoreCase": True
        },
        schema_pattern={
            "allow": ["PUBLIC", "ANALYTICS", "REPORTING"],
            "deny": ["INFORMATION_SCHEMA", "TEMP_*"],
            "ignoreCase": True
        },
        
        # Time window for usage and lineage
        start_time="2020-01-01T00:00:00Z",
        end_time="2025-12-31T23:59:59Z",
        
        # Additional options
        warn_no_datasets=False,
        skip_empty_tables=True,
        lazy_schema_resolver=True,
        convert_urns_to_lowercase=True
    )


def process_workunit(workunit, metadata: Dict[str, Any]) -> None:
    """Process a single workunit and extract relevant information"""
    if not workunit.mcp_raw:
        return
    
    aspect_name = workunit.mcp_raw.get("aspectName")
    entity_urn = workunit.mcp_raw.get("entityUrn")
    aspect_data = workunit.mcp_raw.get("aspect", {})
    
    # Extract entity information
    if "dataset" in entity_urn:
        # Parse dataset URN to get database, schema, table info
        parts = entity_urn.split(",")
        if len(parts) >= 2:
            dataset_name = parts[1].replace(")", "")
            db_schema_table = dataset_name.split(".")
            if len(db_schema_table) >= 3:
                database, schema, table = db_schema_table[0], db_schema_table[1], db_schema_table[2]
                
                # Store in organized structure
                if database not in metadata:
                    metadata[database] = {}
                if schema not in metadata[database]:
                    metadata[database][schema] = {}
                if table not in metadata[database][schema]:
                    metadata[database][schema][table] = {
                        "name": table,
                        "database": database,
                        "schema": schema,
                        "aspects": {}
                    }
                
                metadata[database][schema][table]["aspects"][aspect_name] = aspect_data


def extract_metadata_with_retry(source: SnowflakeV2Source, max_retries: int = 3) -> Dict[str, Any]:
    """Extract metadata with retry logic"""
    metadata = {}
    workunit_count = 0
    
    for attempt in range(max_retries):
        try:
            logging.info(f"🔄 Attempt {attempt + 1} of {max_retries}")
            
            for workunit in source.get_workunits():
                workunit_count += 1
                process_workunit(workunit, metadata)
                
                # Progress indicator
                if workunit_count % 50 == 0:
                    logging.info(f"📊 Processed {workunit_count} workunits...")
            
            logging.info(f"✅ Successfully extracted {workunit_count} workunits!")
            break
            
        except Exception as e:
            logging.error(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            else:
                logging.info(f"🔄 Retrying in 5 seconds...")
                import time
                time.sleep(5)
    
    return metadata


def analyze_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze extracted metadata and generate insights"""
    analysis = {
        "total_databases": 0,
        "total_schemas": 0,
        "total_tables": 0,
        "total_views": 0,
        "tables_with_descriptions": 0,
        "tables_with_tags": 0,
        "lineage_relationships": 0,
        "usage_records": 0
    }
    
    for database, schemas in metadata.items():
        if isinstance(schemas, dict):
            analysis["total_databases"] += 1
            
            for schema, tables in schemas.items():
                if isinstance(tables, dict):
                    analysis["total_schemas"] += 1
                    
                    for table, table_info in tables.items():
                        if isinstance(table_info, dict) and "aspects" in table_info:
                            analysis["total_tables"] += 1
                            
                            # Check for descriptions
                            if "datasetProperties" in table_info["aspects"]:
                                props = table_info["aspects"]["datasetProperties"]
                                if props.get("description"):
                                    analysis["tables_with_descriptions"] += 1
                            
                            # Check for tags
                            if "globalTags" in table_info["aspects"]:
                                analysis["tables_with_tags"] += 1
                            
                            # Check for lineage
                            if "upstreamLineage" in table_info["aspects"]:
                                analysis["lineage_relationships"] += 1
                            
                            # Check for usage
                            if "datasetUsageStatistics" in table_info["aspects"]:
                                analysis["usage_records"] += 1
    
    return analysis


def main():
    """Main function demonstrating advanced usage"""
    
    # Setup logging
    setup_logging(verbose=True)
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Create advanced configuration
        logger.info("🔧 Creating advanced configuration...")
        config = create_advanced_config()
        
        # 2. Create pipeline context
        ctx = PipelineContext(run_id="advanced_example")
        
        # 3. Create and configure the source
        logger.info("🚀 Initializing Snowflake source...")
        source = SnowflakeV2Source(ctx, config)
        
        # 4. Test connection
        logger.info("🔍 Testing Snowflake connection...")
        if not source.test_connection():
            logger.error("❌ Connection test failed!")
            return
        logger.info("✅ Connection successful!")
        
        # 5. Extract metadata with retry logic
        logger.info("📊 Starting metadata extraction...")
        metadata = extract_metadata_with_retry(source, max_retries=3)
        
        # 6. Analyze metadata
        logger.info("🔍 Analyzing metadata...")
        analysis = analyze_metadata(metadata)
        
        # 7. Save results
        output_file = "advanced_snowflake_metadata.json"
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        analysis_file = "metadata_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # 8. Display results
        logger.info("📊 Extraction Results:")
        logger.info(f"  - Databases: {analysis['total_databases']}")
        logger.info(f"  - Schemas: {analysis['total_schemas']}")
        logger.info(f"  - Tables: {analysis['total_tables']}")
        logger.info(f"  - Tables with descriptions: {analysis['tables_with_descriptions']}")
        logger.info(f"  - Tables with tags: {analysis['tables_with_tags']}")
        logger.info(f"  - Lineage relationships: {analysis['lineage_relationships']}")
        logger.info(f"  - Usage records: {analysis['usage_records']}")
        
        logger.info(f"💾 Metadata saved to {output_file}")
        logger.info(f"📈 Analysis saved to {analysis_file}")
        
        # 9. Performance metrics
        if hasattr(source, 'get_metadata_summary'):
            summary = source.get_metadata_summary()
            logger.info(f"⏱️  Extraction completed in {summary.get('duration_seconds', 'unknown')} seconds")
        
    except Exception as e:
        logger.error(f"❌ Error during advanced extraction: {e}")
        raise


if __name__ == "__main__":
    main()
