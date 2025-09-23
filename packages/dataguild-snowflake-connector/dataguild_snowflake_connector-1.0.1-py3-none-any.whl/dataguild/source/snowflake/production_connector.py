"""
Production-ready DataGuild Snowflake Connector
"""

import logging
import sys
import traceback
from typing import Any, Dict, List, Optional, Iterator
from datetime import datetime, timedelta
from pathlib import Path
import json
import yaml
from contextlib import contextmanager

from dataguild.api.common import PipelineContext
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.source.snowflake.main import SnowflakeV2Source
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.snowflake.production_config import ConfigManager, ProductionConfig
from dataguild.source.snowflake.monitoring import (
    MetricsCollector, HealthChecker, SystemMonitor, PerformanceMonitor,
    MonitoringDashboard, check_snowflake_connection, check_memory_usage, check_disk_space
)

logger = logging.getLogger(__name__)


class ProductionSnowflakeConnector:
    """
    Production-ready Snowflake connector with comprehensive monitoring,
    error handling, and observability features.
    """
    
    def __init__(self, config_path: Optional[str] = None, 
                 config_overrides: Optional[Dict[str, Any]] = None):
        """
        Initialize the production connector.
        
        Args:
            config_path: Path to configuration file
            config_overrides: Configuration overrides
        """
        self.config_manager = ConfigManager(config_path)
        self.production_config = self.config_manager.config
        
        # Apply overrides if provided
        if config_overrides:
            for key, value in config_overrides.items():
                if hasattr(self.production_config, key):
                    setattr(self.production_config, key, value)
                else:
                    self.production_config.custom_settings[key] = value
        
        # Initialize monitoring
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker()
        self.system_monitor = SystemMonitor(self.metrics_collector)
        self.performance_monitor = PerformanceMonitor(self.metrics_collector)
        self.monitoring_dashboard = None
        
        # Initialize connector components
        self.connector = None
        self.report = None
        self.context = None
        
        # State tracking
        self.is_initialized = False
        self.is_running = False
        self.start_time = None
        self.end_time = None
        
        # Setup logging
        self._setup_logging()
        
        # Setup health checks
        self._setup_health_checks()
        
        # Setup monitoring
        if self.production_config.enable_metrics:
            self._setup_monitoring()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.production_config.log_level.upper())
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('dataguild_snowflake.log')
            ]
        )
        
        # Set specific logger levels
        if self.production_config.debug:
            logging.getLogger('dataguild').setLevel(logging.DEBUG)
        else:
            logging.getLogger('dataguild').setLevel(logging.INFO)
    
    def _setup_health_checks(self) -> None:
        """Setup health check functions."""
        self.health_checker.add_check(check_memory_usage)
        self.health_checker.add_check(check_disk_space)
    
    def _setup_monitoring(self) -> None:
        """Setup monitoring systems."""
        # Start system monitoring
        self.system_monitor.start(interval=30)
        
        # Setup monitoring dashboard
        if self.production_config.metrics_port:
            self.monitoring_dashboard = MonitoringDashboard(
                self.metrics_collector,
                self.health_checker,
                port=self.production_config.metrics_port
            )
    
    def initialize(self) -> bool:
        """
        Initialize the connector.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing production Snowflake connector...")
            
            # Get Snowflake configuration
            snowflake_config = self.config_manager.get_snowflake_config()
            
            # Create pipeline context
            self.context = PipelineContext(
                pipeline_name="production_snowflake_ingestion",
                run_id=f"prod_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                dry_run=False,
                pipeline_config={
                    "report_period_start": (datetime.now() - timedelta(days=30)).isoformat(),
                    "report_period_end": datetime.now().isoformat()
                }
            )
            
            # Initialize the connector
            with self.performance_monitor.time_operation("connector_initialization"):
                self.connector = SnowflakeV2Source(ctx=self.context, config=snowflake_config)
            
            # Add Snowflake connection health check
            self.health_checker.add_check(
                lambda: check_snowflake_connection(self.connector)
            )
            
            # Initialize report with required fields
            self.report = SnowflakeV2Report(
                name="production_snowflake_ingestion",
                account_name=snowflake_config.account_id,
                region="us-east-1",  # Default region
                report_period_start=datetime.now() - timedelta(days=30),
                report_period_end=datetime.now()
            )
            self.report.ingestion_start_time = datetime.now()
            self.report.ingestion_status = "IN_PROGRESS"
            
            self.is_initialized = True
            self.start_time = datetime.now()
            
            # Record initialization metrics
            self.metrics_collector.add_metric(
                "connector_initialized_total", 1, "counter"
            )
            
            logger.info("✅ Production Snowflake connector initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize connector: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Record error metrics
            self.performance_monitor.record_error("initialization_error", error_msg)
            
            return False
    
    def extract_metadata(self, max_workunits: Optional[int] = None) -> Iterator[MetadataWorkUnit]:
        """
        Extract metadata from Snowflake.
        
        Args:
            max_workunits: Maximum number of workunits to extract
            
        Yields:
            MetadataWorkUnit objects
        """
        if not self.is_initialized:
            raise RuntimeError("Connector not initialized. Call initialize() first.")
        
        if self.is_running:
            raise RuntimeError("Extraction already in progress")
        
        self.is_running = True
        workunit_count = 0
        
        try:
            logger.info("Starting metadata extraction...")
            
            with self.performance_monitor.time_operation("metadata_extraction"):
                for workunit in self.connector.get_workunits():
                    try:
                        workunit_count += 1
                        
                        # Record workunit metrics
                        workunit_type = type(workunit).__name__
                        self.performance_monitor.record_workunit_processed(workunit_type)
                        
                        # Update report
                        if self.report:
                            self.report.add_workunit(workunit_type)
                        
                        yield workunit
                        
                        # Check limits
                        if max_workunits and workunit_count >= max_workunits:
                            logger.info(f"Reached maximum workunits limit: {max_workunits}")
                            break
                        
                        # Log progress
                        if workunit_count % 100 == 0:
                            logger.info(f"Processed {workunit_count} workunits...")
                    
                    except Exception as e:
                        error_msg = f"Error processing workunit {workunit_count}: {str(e)}"
                        logger.error(error_msg)
                        self.performance_monitor.record_error("workunit_processing_error", error_msg)
                        continue
            
            # Record extraction completion metrics
            self.metrics_collector.add_metric(
                "workunits_extracted_total", workunit_count, "counter"
            )
            
            logger.info(f"✅ Metadata extraction completed. Processed {workunit_count} workunits")
            
        except Exception as e:
            error_msg = f"Metadata extraction failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Record error metrics
            self.performance_monitor.record_error("extraction_error", error_msg)
            
            # Update report
            if self.report:
                self.report.report_failure(error_msg)
            
            raise
        
        finally:
            self.is_running = False
    
    def extract_and_save(self, output_path: str, max_workunits: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract metadata and save to file.
        
        Args:
            output_path: Path to save extracted data
            max_workunits: Maximum number of workunits to extract
            
        Returns:
            Dictionary with extraction summary
        """
        try:
            logger.info(f"Starting extraction to {output_path}...")
            
            extracted_data = []
            workunit_count = 0
            
            # Extract metadata
            for workunit in self.extract_metadata(max_workunits):
                workunit_count += 1
                
                # Convert workunit to serializable format
                workunit_data = self._serialize_workunit(workunit, workunit_count)
                extracted_data.append(workunit_data)
            
            # Save data
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(extracted_data, f, indent=2, default=str)
            
            # Create summary
            summary = {
                "extraction_summary": {
                    "total_workunits": workunit_count,
                    "extraction_time": datetime.now().isoformat(),
                    "output_file": str(output_file),
                    "connector_config": {
                        "database": self.config_manager.get_snowflake_config().database,
                        "schema": self.config_manager.get_snowflake_config().schema,
                        "warehouse": self.config_manager.get_snowflake_config().warehouse
                    }
                },
                "metrics": self.metrics_collector.get_metric_summary(),
                "health_checks": [
                    {
                        "name": check.name,
                        "status": check.status,
                        "message": check.message
                    }
                    for check in self.health_checker.run_checks()
                ]
            }
            
            # Save summary
            summary_file = output_file.with_suffix('.summary.json')
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            # Update report
            if self.report:
                self.report.report_success()
                self.report.ingestion_completed_at = datetime.now()
            
            logger.info(f"✅ Extraction completed successfully. Saved {workunit_count} workunits to {output_file}")
            
            return summary
            
        except Exception as e:
            error_msg = f"Extraction and save failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Record error metrics
            self.performance_monitor.record_error("extraction_save_error", error_msg)
            
            # Update report
            if self.report:
                self.report.report_failure(error_msg)
            
            raise
    
    def _serialize_workunit(self, workunit: MetadataWorkUnit, index: int) -> Dict[str, Any]:
        """Serialize a workunit to a dictionary, extracting relevant metadata."""
        workunit_data = {
            'index': index,
            'type': type(workunit).__name__,
            'extraction_time': datetime.now().isoformat(),
            'metadata_type': 'Unknown',
            'entity_urn': 'Unknown',
            'aspect_name': 'Unknown',
            'value_summary': 'Unknown',
            'data': {}  # To store the actual metadata content
        }

        try:
            # Check for mcp_raw data first (DataGuild workunits use this)
            if hasattr(workunit, 'mcp_raw') and workunit.mcp_raw:
                mcp_data = workunit.mcp_raw
                workunit_data['metadata_type'] = 'MCP_Raw'
                workunit_data['data'] = mcp_data
                
                # Extract entity URN and aspect name from mcp_raw
                if isinstance(mcp_data, dict):
                    if 'entityUrn' in mcp_data:
                        workunit_data['entity_urn'] = str(mcp_data['entityUrn'])
                    if 'aspectName' in mcp_data:
                        workunit_data['aspect_name'] = str(mcp_data['aspectName'])
                    
                    # Create a meaningful summary
                    if 'aspect' in mcp_data and isinstance(mcp_data['aspect'], dict):
                        aspect = mcp_data['aspect']
                        if 'name' in aspect:
                            workunit_data['value_summary'] = f"Name: {aspect['name']}"
                        elif 'description' in aspect:
                            workunit_data['value_summary'] = f"Description: {aspect['description'][:100]}..."
                        elif 'removed' in aspect:
                            workunit_data['value_summary'] = f"Status: {'Removed' if aspect['removed'] else 'Active'}"
                        else:
                            workunit_data['value_summary'] = f"Aspect: {workunit_data['aspect_name']}"
                    else:
                        workunit_data['value_summary'] = f"MCP data for {workunit_data['aspect_name']}"
                else:
                    workunit_data['value_summary'] = f"MCP raw data: {type(mcp_data).__name__}"
            
            # Check for metadata attribute as fallback
            elif hasattr(workunit, 'metadata') and workunit.metadata:
                metadata = workunit.metadata
                workunit_data['metadata_type'] = type(metadata).__name__
                
                # Common attributes for many metadata types
                if hasattr(metadata, 'entityUrn') and metadata.entityUrn:
                    workunit_data['entity_urn'] = str(metadata.entityUrn)
                elif hasattr(metadata, 'urn') and metadata.urn:
                    workunit_data['entity_urn'] = str(metadata.urn)
                
                if hasattr(metadata, 'aspectName') and metadata.aspectName:
                    workunit_data['aspect_name'] = str(metadata.aspectName)
                
                # Attempt to serialize the actual metadata content
                # Pydantic models have .dict() or .json() methods
                if hasattr(metadata, 'dict'):
                    workunit_data['data'] = metadata.dict()
                elif hasattr(metadata, 'to_dict'):  # Some older DataGuild models might use this
                    workunit_data['data'] = metadata.to_dict()
                else:
                    # Fallback for non-Pydantic or custom objects
                    workunit_data['data'] = str(metadata)  # Represent as string if not serializable
                
                # Add a summary if available (e.g., for dataset properties)
                if hasattr(metadata, 'name') and metadata.name:
                    workunit_data['value_summary'] = f"Name: {metadata.name}"
                elif hasattr(metadata, 'description') and metadata.description:
                    workunit_data['value_summary'] = f"Description: {metadata.description[:100]}..."
                elif workunit_data['data']:
                    workunit_data['value_summary'] = f"Contains data for {workunit_data['metadata_type']}"
            
            return workunit_data
        except Exception as e:
            logger.error(f"Error serializing workunit {index}: {e}", exc_info=True)
            workunit_data['error'] = str(e)
            return workunit_data
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        health_checks = self.health_checker.run_checks()
        
        overall_status = "healthy"
        for check in health_checks:
            if check.status == "unhealthy":
                overall_status = "unhealthy"
                break
            elif check.status == "degraded" and overall_status == "healthy":
                overall_status = "degraded"
        
        return {
            "status": overall_status,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "message": check.message,
                    "duration_ms": check.duration_ms
                }
                for check in health_checks
            ],
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "is_initialized": self.is_initialized,
            "is_running": self.is_running
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return {
            "metrics": self.metrics_collector.get_metric_summary(),
            "system_metrics": self.metrics_collector.get_metrics(since=datetime.now() - timedelta(minutes=5))
        }
    
    def start_monitoring_dashboard(self) -> None:
        """Start the monitoring dashboard."""
        if self.monitoring_dashboard:
            self.monitoring_dashboard.start()
        else:
            logger.warning("Monitoring dashboard not configured")
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            logger.info("Cleaning up connector resources...")
            
            # Stop monitoring
            if self.system_monitor:
                self.system_monitor.stop()
            
            if self.monitoring_dashboard:
                self.monitoring_dashboard.stop()
            
            # Close connector
            if self.connector and hasattr(self.connector, 'close'):
                self.connector.close()
            
            # Update report
            if self.report:
                self.report.ingestion_completed_at = datetime.now()
                if self.report.ingestion_status == "IN_PROGRESS":
                    self.report.ingestion_status = "COMPLETED"
            
            self.end_time = datetime.now()
            
            # Record cleanup metrics
            if self.start_time and self.end_time:
                duration = (self.end_time - self.start_time).total_seconds()
                self.metrics_collector.add_metric(
                    "connector_duration_seconds", duration, "histogram"
                )
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        if not self.initialize():
            raise RuntimeError("Failed to initialize connector")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


# Convenience functions
def create_production_connector(config_path: Optional[str] = None, 
                               **overrides) -> ProductionSnowflakeConnector:
    """Create a production connector with overrides."""
    return ProductionSnowflakeConnector(config_path, overrides)


def run_production_extraction(config_path: Optional[str] = None,
                            output_path: str = "extracted_data.json",
                            max_workunits: Optional[int] = None,
                            **overrides) -> Dict[str, Any]:
    """Run a production extraction."""
    with create_production_connector(config_path, **overrides) as connector:
        return connector.extract_and_save(output_path, max_workunits)
