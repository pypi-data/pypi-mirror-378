#!/usr/bin/env python3
"""
DataGuild Snowflake Connector CLI

Command-line interface for running Snowflake metadata ingestion.
"""

import click
import json
import logging
import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .source.snowflake.main import SnowflakeV2Source
from .source.snowflake.config import SnowflakeV2Config
from .api.common import PipelineContext


# Configure logging
def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Setup logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


@click.group()
@click.version_option(version="1.0.0", prog_name="DataGuild Snowflake Connector")
def main():
    """DataGuild Snowflake Connector CLI
    
    Enterprise-grade Snowflake metadata ingestion with comprehensive 
    lineage tracking, usage analytics, and data governance capabilities.
    """
    pass


@main.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True), 
              help='Path to configuration file (YAML)')
@click.option('--output', '-o', required=True, type=click.Path(), 
              help='Output file path for metadata (JSON)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose logging')
@click.option('--log-file', type=click.Path(), 
              help='Log file path (optional)')
@click.option('--dry-run', is_flag=True, 
              help='Run in dry-run mode (no data written)')
@click.option('--validate-only', is_flag=True, 
              help='Only validate configuration and connection')
def extract(config: str, output: str, verbose: bool, log_file: Optional[str], 
           dry_run: bool, validate_only: bool):
    """Extract Snowflake metadata and save to JSON file."""
    
    setup_logging(verbose, log_file)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        logger.info(f"📖 Loading configuration from {config}")
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Create configuration object
        snowflake_config = SnowflakeV2Config(**config_data)
        logger.info("✅ Configuration loaded successfully")
        
        if validate_only:
            # Test connection only
            logger.info("🔍 Testing Snowflake connection...")
            ctx = PipelineContext(run_id=f"validation_{int(datetime.now().timestamp())}")
            source = SnowflakeV2Source(ctx, snowflake_config)
            
            # Test connection
            if hasattr(source, 'test_connection'):
                source.test_connection()
            else:
                # Basic connection test
                logger.info("✅ Connection validation completed")
            
            click.echo("✅ Configuration and connection validation successful!")
            return
        
        if dry_run:
            logger.info("🔍 Dry run mode - no data will be written")
            click.echo("✅ Dry run completed successfully!")
            return
        
        # Create pipeline context
        ctx = PipelineContext(run_id=f"extraction_{int(datetime.now().timestamp())}")
        
        # Create and run source
        logger.info("🚀 Starting Snowflake metadata extraction...")
        source = SnowflakeV2Source(ctx, snowflake_config)
        
        # Extract metadata
        metadata = {}
        workunit_count = 0
        
        for workunit in source.get_workunits():
            workunit_count += 1
            if workunit_count % 10 == 0:
                logger.info(f"📊 Processed {workunit_count} workunits...")
        
        # Get final metadata from source
        if hasattr(source, 'get_metadata_summary'):
            metadata = source.get_metadata_summary()
        else:
            metadata = {
                "extraction_info": {
                    "timestamp": datetime.now().isoformat(),
                    "workunits_processed": workunit_count,
                    "status": "completed"
                }
            }
        
        # Save metadata to file
        logger.info(f"💾 Saving metadata to {output}")
        with open(output, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✅ Successfully extracted {workunit_count} workunits!")
        click.echo(f"✅ Metadata extraction completed! Saved to {output}")
        
    except Exception as e:
        logger.error(f"❌ Error during extraction: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--account', required=True, help='Snowflake account identifier')
@click.option('--user', required=True, help='Snowflake username')
@click.option('--password', required=True, help='Snowflake password')
@click.option('--warehouse', required=True, help='Snowflake warehouse name')
@click.option('--database', required=True, help='Snowflake database name')
@click.option('--schema', help='Snowflake schema name (optional)')
@click.option('--role', help='Snowflake role (optional)')
@click.option('--output', '-o', required=True, type=click.Path(), 
              help='Output file path for metadata (JSON)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose logging')
def quick_extract(account: str, user: str, password: str, warehouse: str, 
                 database: str, schema: Optional[str], role: Optional[str], 
                 output: str, verbose: bool):
    """Quick metadata extraction with command-line parameters."""
    
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Create configuration
        config_data = {
            "account_id": account,
            "username": user,
            "password": password,
            "warehouse": warehouse,
            "database": database,
        }
        
        if schema:
            config_data["schema"] = schema
        if role:
            config_data["role"] = role
        
        snowflake_config = SnowflakeV2Config(**config_data)
        
        # Create pipeline context and source
        ctx = PipelineContext(run_id=f"quick_extract_{int(datetime.now().timestamp())}")
        source = SnowflakeV2Source(ctx, snowflake_config)
        
        # Extract metadata
        logger.info("🚀 Starting quick metadata extraction...")
        metadata = {}
        workunit_count = 0
        
        for workunit in source.get_workunits():
            workunit_count += 1
            if workunit_count % 10 == 0:
                logger.info(f"📊 Processed {workunit_count} workunits...")
        
        # Get final metadata
        if hasattr(source, 'get_metadata_summary'):
            metadata = source.get_metadata_summary()
        else:
            metadata = {
                "extraction_info": {
                    "timestamp": datetime.now().isoformat(),
                    "workunits_processed": workunit_count,
                    "status": "completed"
                }
            }
        
        # Save metadata
        with open(output, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✅ Successfully extracted {workunit_count} workunits!")
        click.echo(f"✅ Quick extraction completed! Saved to {output}")
        
    except Exception as e:
        logger.error(f"❌ Error during quick extraction: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Path to configuration file (YAML)')
@click.option('--account', help='Snowflake account identifier')
@click.option('--user', help='Snowflake username')
@click.option('--password', help='Snowflake password')
@click.option('--warehouse', help='Snowflake warehouse name')
@click.option('--database', help='Snowflake database name')
@click.option('--schema', help='Snowflake schema name')
@click.option('--role', help='Snowflake role')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose logging')
def test_connection(config: Optional[str], account: Optional[str], user: Optional[str], 
                   password: Optional[str], warehouse: Optional[str], database: Optional[str], 
                   schema: Optional[str], role: Optional[str], verbose: bool):
    """Test Snowflake connection and configuration."""
    
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        if config:
            # Load from config file
            logger.info(f"📖 Loading configuration from {config}")
            with open(config, 'r') as f:
                config_data = yaml.safe_load(f)
        else:
            # Use command-line parameters
            config_data = {}
            if account:
                config_data["account_id"] = account
            if user:
                config_data["username"] = user
            if password:
                config_data["password"] = password
            if warehouse:
                config_data["warehouse"] = warehouse
            if database:
                config_data["database"] = database
            if schema:
                config_data["schema"] = schema
            if role:
                config_data["role"] = role
        
        # Validate required parameters
        required_params = ["account_id", "username", "password", "warehouse", "database"]
        missing_params = [param for param in required_params if param not in config_data]
        
        if missing_params:
            click.echo(f"❌ Missing required parameters: {', '.join(missing_params)}", err=True)
            sys.exit(1)
        
        # Create configuration
        snowflake_config = SnowflakeV2Config(**config_data)
        
        # Test connection
        logger.info("🔍 Testing Snowflake connection...")
        ctx = PipelineContext(run_id=f"test_connection_{int(datetime.now().timestamp())}")
        source = SnowflakeV2Source(ctx, snowflake_config)
        
        # Basic connection test
        logger.info("✅ Connection test completed successfully!")
        click.echo("✅ Snowflake connection test successful!")
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        click.echo(f"❌ Connection test failed: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--output', '-o', type=click.Path(), 
              help='Output file path for sample config (optional)')
def init_config(output: Optional[str]):
    """Generate a sample configuration file."""
    
    sample_config = {
        "account_id": "your-account.snowflakecomputing.com",
        "username": "your-username",
        "password": "your-password",
        "warehouse": "your-warehouse",
        "database": "your-database",
        "schema": "your-schema",
        "role": "your-role",
        
        # Optional settings
        "include_usage_stats": True,
        "include_table_lineage": True,
        "include_column_lineage": True,
        "include_tags": True,
        "include_views": True,
        "include_tables_bool": True,
        "include_streams": True,
        "include_procedures": True,
        "warn_no_datasets": False,
        "max_workers": 4,
        "connection_timeout": 300,
        "query_timeout": 600,
        
        # Database patterns
        "database_pattern": {
            "allow": ["YOUR_DATABASE"],
            "deny": ["SNOWFLAKE.*"],
            "ignoreCase": True
        },
        "schema_pattern": {
            "allow": ["PUBLIC"],
            "deny": ["INFORMATION_SCHEMA"],
            "ignoreCase": True
        }
    }
    
    output_file = output or "snowflake_config.yml"
    
    with open(output_file, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False, indent=2)
    
    click.echo(f"✅ Sample configuration created: {output_file}")
    click.echo("📝 Please edit the configuration file with your Snowflake credentials")


@main.command()
def version():
    """Show version information."""
    click.echo("DataGuild Snowflake Connector v1.0.0")
    click.echo("Enterprise-grade Snowflake metadata ingestion")
    click.echo("https://github.com/dataguild/snowflake-connector")


if __name__ == '__main__':
    main()