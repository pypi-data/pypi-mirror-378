#!/usr/bin/env python3
"""
Basic usage example for DataGuild Snowflake Connector

This example demonstrates how to use the connector to extract metadata
from a Snowflake database.
"""

import json
from dataguild_snowflake_connector import SnowflakeV2Source, SnowflakeV2Config
from dataguild.api.common import PipelineContext


def main():
    """Main function demonstrating basic usage"""
    
    # 1. Configure your Snowflake connection
    config = SnowflakeV2Config(
        account_id="your-account.snowflakecomputing.com",
        username="your-username",
        password="your-password",
        warehouse="your-warehouse",
        database="your-database",
        schema="your-schema",
        role="your-role"  # Optional
    )
    
    # 2. Create pipeline context
    ctx = PipelineContext(run_id="basic_example")
    
    # 3. Create and configure the source
    source = SnowflakeV2Source(ctx, config)
    
    # 4. Test connection (optional but recommended)
    print("🔍 Testing Snowflake connection...")
    if source.test_connection():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed!")
        return
    
    # 5. Extract metadata
    print("🚀 Starting metadata extraction...")
    metadata = {}
    workunit_count = 0
    
    try:
        for workunit in source.get_workunits():
            workunit_count += 1
            
            # Process each workunit
            if workunit.mcp_raw:
                aspect_name = workunit.mcp_raw.get("aspectName")
                entity_urn = workunit.mcp_raw.get("entityUrn")
                
                print(f"📊 Processed workunit {workunit_count}: {aspect_name} for {entity_urn}")
                
                # Store workunit data
                if aspect_name not in metadata:
                    metadata[aspect_name] = []
                metadata[aspect_name].append(workunit.mcp_raw)
            
            # Progress indicator
            if workunit_count % 10 == 0:
                print(f"📈 Processed {workunit_count} workunits...")
        
        # 6. Get summary information
        if hasattr(source, 'get_metadata_summary'):
            summary = source.get_metadata_summary()
            metadata["summary"] = summary
        
        # 7. Save metadata to file
        output_file = "snowflake_metadata.json"
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print(f"✅ Successfully extracted {workunit_count} workunits!")
        print(f"💾 Metadata saved to {output_file}")
        
        # 8. Display summary
        print("\n📊 Extraction Summary:")
        print(f"  - Total workunits: {workunit_count}")
        print(f"  - Schema metadata: {len(metadata.get('schemaMetadata', []))}")
        print(f"  - Dataset properties: {len(metadata.get('datasetProperties', []))}")
        print(f"  - Lineage relationships: {len(metadata.get('upstreamLineage', []))}")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
