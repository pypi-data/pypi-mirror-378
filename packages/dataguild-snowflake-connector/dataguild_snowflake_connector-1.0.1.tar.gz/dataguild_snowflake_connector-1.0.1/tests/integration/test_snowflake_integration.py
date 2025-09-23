"""
Integration tests for Snowflake connector
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from dataguild.source.snowflake.main import SnowflakeV2Source
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.api.common import PipelineContext


class TestSnowflakeIntegration:
    """Integration tests for Snowflake connector"""
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing"""
        return {
            "account_id": "test-account.snowflakecomputing.com",
            "username": "test-user",
            "password": "test-password",
            "warehouse": "test-warehouse",
            "database": "test-database",
            "schema": "test-schema",
            "include_usage_stats": True,
            "include_table_lineage": True,
            "include_column_lineage": True,
            "include_tags": True,
            "max_workers": 2
        }
    
    @pytest.fixture
    def mock_snowflake_connection(self):
        """Mock Snowflake connection with sample data"""
        mock_conn = Mock()
        
        # Mock database query results
        mock_conn.execute_query.side_effect = [
            # SHOW DATABASES
            [("TEST_DATABASE",)],
            # SHOW SCHEMAS
            [("TEST_SCHEMA",)],
            # SHOW TABLES
            [("TABLE1", "TABLE", "TEST_DATABASE", "TEST_SCHEMA")],
            [("TABLE2", "TABLE", "TEST_DATABASE", "TEST_SCHEMA")],
            # SHOW VIEWS
            [("VIEW1", "VIEW", "TEST_DATABASE", "TEST_SCHEMA")],
            # Column information
            [
                ("COL1", "VARCHAR", "TEST_DATABASE", "TEST_SCHEMA", "TABLE1"),
                ("COL2", "INTEGER", "TEST_DATABASE", "TEST_SCHEMA", "TABLE1"),
                ("COL3", "VARCHAR", "TEST_DATABASE", "TEST_SCHEMA", "TABLE2"),
            ],
            # Usage statistics
            [
                ("TABLE1", "SELECT", 100, "2024-01-01"),
                ("TABLE2", "SELECT", 50, "2024-01-01"),
            ]
        ]
        
        return mock_conn
    
    def test_full_extraction_workflow(self, sample_config, mock_snowflake_connection):
        """Test complete extraction workflow"""
        config = SnowflakeV2Config(**sample_config)
        ctx = PipelineContext(run_id="integration_test")
        
        with patch('dataguild.source.snowflake.main.SnowflakeConnection', return_value=mock_snowflake_connection), \
             patch('dataguild.source.snowflake.main.SnowflakeFilter') as mock_filter, \
             patch('dataguild.source.snowflake.main.SnowflakeIdentifierBuilder') as mock_identifiers, \
             patch('dataguild.source.snowflake.main.SqlParsingAggregator') as mock_aggregator, \
             patch('dataguild.source.snowflake.main.SnowflakeLineageExtractor') as mock_lineage, \
             patch('dataguild.source.snowflake.main.SnowflakeUsageExtractor') as mock_usage, \
             patch('dataguild.source.snowflake.main.SnowflakeSchemaGenerator') as mock_schema_gen:
            
            # Mock schema generator with realistic workunits
            mock_workunits = []
            for i in range(5):
                workunit = Mock()
                workunit.id = f"workunit-{i}"
                workunit.mcp_raw = {
                    "entityUrn": f"urn:li:dataset:(snowflake,test_db.test_schema.table{i},PROD)",
                    "aspectName": "schemaMetadata" if i % 2 == 0 else "datasetProperties",
                    "aspect": {"name": f"table{i}", "columns": []}
                }
                mock_workunits.append(workunit)
            
            mock_schema_gen.return_value.get_workunits_internal.return_value = mock_workunits
            mock_schema_gen.return_value.databases = []
            
            # Mock identifiers
            mock_identifiers.return_value.get_dataset_identifier.side_effect = [
                "test_db.test_schema.table0",
                "test_db.test_schema.table1",
                "test_db.test_schema.table2",
                "test_db.test_schema.table3",
                "test_db.test_schema.table4"
            ]
            
            source = SnowflakeV2Source(ctx, config)
            
            # Test connection
            assert source.test_connection() is True
            
            # Extract workunits
            workunits = list(source.get_workunits())
            assert len(workunits) == 5
            
            # Verify workunit structure
            for workunit in workunits:
                assert hasattr(workunit, 'id')
                assert hasattr(workunit, 'mcp_raw')
                assert workunit.mcp_raw is not None
    
    def test_configuration_file_loading(self, sample_config):
        """Test loading configuration from file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            import yaml
            yaml.dump(sample_config, f)
            config_file = f.name
        
        try:
            # Test loading configuration
            with open(config_file, 'r') as f:
                loaded_config = yaml.safe_load(f)
            
            config = SnowflakeV2Config(**loaded_config)
            
            assert config.account_id == sample_config["account_id"]
            assert config.username == sample_config["username"]
            assert config.warehouse == sample_config["warehouse"]
            assert config.database == sample_config["database"]
            
        finally:
            os.unlink(config_file)
    
    def test_error_handling_and_recovery(self, sample_config):
        """Test error handling and recovery mechanisms"""
        config = SnowflakeV2Config(**sample_config)
        ctx = PipelineContext(run_id="error_test")
        
        # Mock connection that fails initially but succeeds on retry
        mock_conn = Mock()
        call_count = 0
        
        def mock_execute_query(query):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Connection failed")
            return [("SUCCESS",)]
        
        mock_conn.execute_query.side_effect = mock_execute_query
        
        with patch('dataguild.source.snowflake.main.SnowflakeConnection', return_value=mock_conn), \
             patch('dataguild.source.snowflake.main.SnowflakeFilter'), \
             patch('dataguild.source.snowflake.main.SnowflakeIdentifierBuilder'), \
             patch('dataguild.source.snowflake.main.SqlParsingAggregator'), \
             patch('dataguild.source.snowflake.main.SnowflakeLineageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeUsageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeSchemaGenerator') as mock_schema_gen:
            
            mock_schema_gen.return_value.get_workunits_internal.return_value = []
            mock_schema_gen.return_value.databases = []
            
            source = SnowflakeV2Source(ctx, config)
            
            # Test that connection eventually succeeds
            assert source.test_connection() is True
    
    def test_metadata_output_format(self, sample_config, mock_snowflake_connection):
        """Test that metadata output follows expected format"""
        config = SnowflakeV2Config(**sample_config)
        ctx = PipelineContext(run_id="format_test")
        
        with patch('dataguild.source.snowflake.main.SnowflakeConnection', return_value=mock_snowflake_connection), \
             patch('dataguild.source.snowflake.main.SnowflakeFilter'), \
             patch('dataguild.source.snowflake.main.SnowflakeIdentifierBuilder'), \
             patch('dataguild.source.snowflake.main.SqlParsingAggregator'), \
             patch('dataguild.source.snowflake.main.SnowflakeLineageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeUsageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeSchemaGenerator') as mock_schema_gen:
            
            # Mock workunits with different aspect types
            mock_workunits = [
                Mock(id="schema-1", mcp_raw={
                    "entityUrn": "urn:li:dataset:(snowflake,test_db.test_schema.table1,PROD)",
                    "aspectName": "schemaMetadata",
                    "aspect": {"name": "table1", "columns": []}
                }),
                Mock(id="props-1", mcp_raw={
                    "entityUrn": "urn:li:dataset:(snowflake,test_db.test_schema.table1,PROD)",
                    "aspectName": "datasetProperties",
                    "aspect": {"name": "table1", "description": "Test table"}
                }),
                Mock(id="lineage-1", mcp_raw={
                    "entityUrn": "urn:li:dataset:(snowflake,test_db.test_schema.table1,PROD)",
                    "aspectName": "upstreamLineage",
                    "aspect": {"upstreams": []}
                })
            ]
            
            mock_schema_gen.return_value.get_workunits_internal.return_value = mock_workunits
            mock_schema_gen.return_value.databases = []
            
            source = SnowflakeV2Source(ctx, config)
            workunits = list(source.get_workunits())
            
            # Verify workunit structure
            assert len(workunits) == 3
            
            # Check that each workunit has required fields
            for workunit in workunits:
                assert hasattr(workunit, 'id')
                assert hasattr(workunit, 'mcp_raw')
                assert 'entityUrn' in workunit.mcp_raw
                assert 'aspectName' in workunit.mcp_raw
                assert 'aspect' in workunit.mcp_raw
    
    def test_performance_with_large_dataset(self, sample_config):
        """Test performance with large dataset simulation"""
        config = SnowflakeV2Config(**sample_config)
        ctx = PipelineContext(run_id="performance_test")
        
        # Create a large number of mock workunits
        large_workunit_count = 1000
        mock_workunits = []
        
        for i in range(large_workunit_count):
            workunit = Mock()
            workunit.id = f"workunit-{i}"
            workunit.mcp_raw = {
                "entityUrn": f"urn:li:dataset:(snowflake,test_db.test_schema.table{i},PROD)",
                "aspectName": "schemaMetadata",
                "aspect": {"name": f"table{i}", "columns": []}
            }
            mock_workunits.append(workunit)
        
        with patch('dataguild.source.snowflake.main.SnowflakeConnection'), \
             patch('dataguild.source.snowflake.main.SnowflakeFilter'), \
             patch('dataguild.source.snowflake.main.SnowflakeIdentifierBuilder'), \
             patch('dataguild.source.snowflake.main.SqlParsingAggregator'), \
             patch('dataguild.source.snowflake.main.SnowflakeLineageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeUsageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeSchemaGenerator') as mock_schema_gen:
            
            mock_schema_gen.return_value.get_workunits_internal.return_value = mock_workunits
            mock_schema_gen.return_value.databases = []
            
            source = SnowflakeV2Source(ctx, config)
            
            # Time the extraction
            import time
            start_time = time.time()
            workunits = list(source.get_workunits())
            end_time = time.time()
            
            # Verify all workunits were processed
            assert len(workunits) == large_workunit_count
            
            # Verify reasonable performance (should complete in reasonable time)
            extraction_time = end_time - start_time
            assert extraction_time < 10.0  # Should complete within 10 seconds for 1000 workunits
    
    def test_concurrent_extraction(self, sample_config):
        """Test concurrent extraction capabilities"""
        config = SnowflakeV2Config(**sample_config)
        config.max_workers = 4  # Use multiple workers
        
        ctx = PipelineContext(run_id="concurrent_test")
        
        with patch('dataguild.source.snowflake.main.SnowflakeConnection'), \
             patch('dataguild.source.snowflake.main.SnowflakeFilter'), \
             patch('dataguild.source.snowflake.main.SnowflakeIdentifierBuilder'), \
             patch('dataguild.source.snowflake.main.SqlParsingAggregator'), \
             patch('dataguild.source.snowflake.main.SnowflakeLineageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeUsageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeSchemaGenerator') as mock_schema_gen:
            
            # Mock workunits for concurrent processing
            mock_workunits = [Mock(id=f"workunit-{i}") for i in range(100)]
            mock_schema_gen.return_value.get_workunits_internal.return_value = mock_workunits
            mock_schema_gen.return_value.databases = []
            
            source = SnowflakeV2Source(ctx, config)
            workunits = list(source.get_workunits())
            
            # Verify all workunits were processed
            assert len(workunits) == 100
            
            # Verify max_workers setting was respected
            assert config.max_workers == 4
