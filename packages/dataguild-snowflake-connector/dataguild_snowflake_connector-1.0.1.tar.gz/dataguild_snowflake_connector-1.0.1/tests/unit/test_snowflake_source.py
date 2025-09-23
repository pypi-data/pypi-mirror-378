"""
Unit tests for SnowflakeV2Source
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataguild.source.snowflake.main import SnowflakeV2Source
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.api.common import PipelineContext


class TestSnowflakeV2Source:
    """Test cases for SnowflakeV2Source"""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration"""
        return SnowflakeV2Config(
            account_id="test-account",
            username="test-user",
            password="test-password",
            warehouse="test-warehouse",
            database="test-database",
            schema="test-schema"
        )
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock pipeline context"""
        return PipelineContext(run_id="test_run")
    
    @pytest.fixture
    def mock_source(self, mock_config, mock_context):
        """Create a mock source with mocked dependencies"""
        with patch('dataguild.source.snowflake.main.SnowflakeConnection') as mock_conn, \
             patch('dataguild.source.snowflake.main.SnowflakeFilter') as mock_filter, \
             patch('dataguild.source.snowflake.main.SnowflakeIdentifierBuilder') as mock_identifiers, \
             patch('dataguild.source.snowflake.main.SqlParsingAggregator') as mock_aggregator, \
             patch('dataguild.source.snowflake.main.SnowflakeLineageExtractor') as mock_lineage, \
             patch('dataguild.source.snowflake.main.SnowflakeUsageExtractor') as mock_usage:
            
            source = SnowflakeV2Source(mock_context, mock_config)
            return source
    
    def test_source_initialization(self, mock_config, mock_context):
        """Test source initialization"""
        with patch('dataguild.source.snowflake.main.SnowflakeConnection'), \
             patch('dataguild.source.snowflake.main.SnowflakeFilter'), \
             patch('dataguild.source.snowflake.main.SnowflakeIdentifierBuilder'), \
             patch('dataguild.source.snowflake.main.SqlParsingAggregator'), \
             patch('dataguild.source.snowflake.main.SnowflakeLineageExtractor'), \
             patch('dataguild.source.snowflake.main.SnowflakeUsageExtractor'):
            
            source = SnowflakeV2Source(mock_context, mock_config)
            
            assert source.config == mock_config
            assert source.ctx == mock_context
            assert source.report is not None
    
    def test_get_workunits_internal(self, mock_source):
        """Test get_workunits_internal method"""
        # Mock the schema generator
        mock_schema_gen = Mock()
        mock_schema_gen.get_workunits_internal.return_value = [
            Mock(id="test-workunit-1"),
            Mock(id="test-workunit-2")
        ]
        mock_schema_gen.databases = []
        
        with patch('dataguild.source.snowflake.main.SnowflakeSchemaGenerator', return_value=mock_schema_gen):
            workunits = list(mock_source.get_workunits_internal())
            
            assert len(workunits) == 2
            assert workunits[0].id == "test-workunit-1"
            assert workunits[1].id == "test-workunit-2"
    
    def test_validate_warehouse_access(self, mock_source):
        """Test warehouse access validation"""
        # Mock the connection to return a valid warehouse
        mock_source.connection = Mock()
        mock_source.connection.execute_query.return_value = [("TEST_WAREHOUSE",)]
        
        result = mock_source._validate_warehouse_access()
        assert result is True
    
    def test_validate_warehouse_access_failure(self, mock_source):
        """Test warehouse access validation failure"""
        # Mock the connection to return no warehouse
        mock_source.connection = Mock()
        mock_source.connection.execute_query.return_value = []
        
        result = mock_source._validate_warehouse_access()
        assert result is False
    
    def test_discover_datasets(self, mock_source):
        """Test dataset discovery"""
        # Mock databases with schemas and tables
        mock_db = Mock()
        mock_db.name = "test_db"
        mock_schema = Mock()
        mock_schema.name = "test_schema"
        mock_schema.tables = ["table1", "table2"]
        mock_schema.views = ["view1"]
        mock_schema.streams = []
        mock_db.schemas = [mock_schema]
        
        mock_source.identifiers = Mock()
        mock_source.identifiers.get_dataset_identifier.side_effect = [
            "test_db.test_schema.table1",
            "test_db.test_schema.table2",
            "test_db.test_schema.view1"
        ]
        
        datasets = mock_source._discover_datasets([mock_db])
        
        assert len(datasets) == 3
        assert "test_db.test_schema.table1" in datasets
        assert "test_db.test_schema.table2" in datasets
        assert "test_db.test_schema.view1" in datasets
    
    def test_error_handling(self, mock_config, mock_context):
        """Test error handling during initialization"""
        with patch('dataguild.source.snowflake.main.SnowflakeConnection', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception):
                SnowflakeV2Source(mock_context, mock_config)
    
    def test_configuration_validation(self, mock_context):
        """Test configuration validation"""
        # Test missing required fields
        with pytest.raises(Exception):
            SnowflakeV2Config(
                account_id="test-account",
                # Missing required fields
            )
    
    def test_workunit_processing(self, mock_source):
        """Test workunit processing"""
        # Mock workunits
        mock_workunit1 = Mock()
        mock_workunit1.id = "test-1"
        mock_workunit1.mcp_raw = {"aspectName": "schemaMetadata"}
        
        mock_workunit2 = Mock()
        mock_workunit2.id = "test-2"
        mock_workunit2.mcp_raw = {"aspectName": "datasetProperties"}
        
        # Mock the schema generator to return these workunits
        mock_schema_gen = Mock()
        mock_schema_gen.get_workunits_internal.return_value = [mock_workunit1, mock_workunit2]
        mock_schema_gen.databases = []
        
        with patch('dataguild.source.snowflake.main.SnowflakeSchemaGenerator', return_value=mock_schema_gen):
            workunits = list(mock_source.get_workunits_internal())
            
            assert len(workunits) == 2
            assert workunits[0].id == "test-1"
            assert workunits[1].id == "test-2"
    
    def test_metadata_summary(self, mock_source):
        """Test metadata summary generation"""
        # Mock the report to return summary data
        mock_source.report = Mock()
        mock_source.report.get_summary.return_value = {
            "total_workunits": 100,
            "tables_processed": 50,
            "views_processed": 10,
            "errors": 0
        }
        
        summary = mock_source.get_metadata_summary()
        
        assert "total_workunits" in summary
        assert summary["total_workunits"] == 100
    
    def test_connection_testing(self, mock_source):
        """Test connection testing functionality"""
        # Mock successful connection
        mock_source.connection = Mock()
        mock_source.connection.execute_query.return_value = [("SUCCESS",)]
        
        result = mock_source.test_connection()
        assert result is True
        
        # Mock failed connection
        mock_source.connection.execute_query.side_effect = Exception("Connection failed")
        
        result = mock_source.test_connection()
        assert result is False


class TestSnowflakeV2Config:
    """Test cases for SnowflakeV2Config"""
    
    def test_config_creation(self):
        """Test configuration creation with required fields"""
        config = SnowflakeV2Config(
            account_id="test-account",
            username="test-user",
            password="test-password",
            warehouse="test-warehouse",
            database="test-database"
        )
        
        assert config.account_id == "test-account"
        assert config.username == "test-user"
        assert config.password == "test-password"
        assert config.warehouse == "test-warehouse"
        assert config.database == "test-database"
    
    def test_config_defaults(self):
        """Test configuration default values"""
        config = SnowflakeV2Config(
            account_id="test-account",
            username="test-user",
            password="test-password",
            warehouse="test-warehouse",
            database="test-database"
        )
        
        assert config.include_usage_stats is True
        assert config.include_table_lineage is True
        assert config.include_column_lineage is True
        assert config.include_tags is True
        assert config.max_workers == 4
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test missing required fields
        with pytest.raises(Exception):
            SnowflakeV2Config(
                account_id="test-account",
                # Missing required fields
            )
    
    def test_config_optional_fields(self):
        """Test optional configuration fields"""
        config = SnowflakeV2Config(
            account_id="test-account",
            username="test-user",
            password="test-password",
            warehouse="test-warehouse",
            database="test-database",
            schema="test-schema",
            role="test-role",
            max_workers=8,
            connection_timeout=600
        )
        
        assert config.schema == "test-schema"
        assert config.role == "test-role"
        assert config.max_workers == 8
        assert config.connection_timeout == 600


class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow with mocked dependencies"""
        config = SnowflakeV2Config(
            account_id="test-account",
            username="test-user",
            password="test-password",
            warehouse="test-warehouse",
            database="test-database"
        )
        
        ctx = PipelineContext(run_id="integration_test")
        
        with patch('dataguild.source.snowflake.main.SnowflakeConnection') as mock_conn, \
             patch('dataguild.source.snowflake.main.SnowflakeFilter') as mock_filter, \
             patch('dataguild.source.snowflake.main.SnowflakeIdentifierBuilder') as mock_identifiers, \
             patch('dataguild.source.snowflake.main.SqlParsingAggregator') as mock_aggregator, \
             patch('dataguild.source.snowflake.main.SnowflakeLineageExtractor') as mock_lineage, \
             patch('dataguild.source.snowflake.main.SnowflakeUsageExtractor') as mock_usage, \
             patch('dataguild.source.snowflake.main.SnowflakeSchemaGenerator') as mock_schema_gen:
            
            # Mock schema generator
            mock_workunit = Mock()
            mock_workunit.id = "test-workunit"
            mock_schema_gen.return_value.get_workunits_internal.return_value = [mock_workunit]
            mock_schema_gen.return_value.databases = []
            
            source = SnowflakeV2Source(ctx, config)
            workunits = list(source.get_workunits())
            
            assert len(workunits) == 1
            assert workunits[0].id == "test-workunit"
