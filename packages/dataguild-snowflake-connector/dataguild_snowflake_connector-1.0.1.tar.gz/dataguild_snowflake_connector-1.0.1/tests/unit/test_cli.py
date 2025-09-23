"""
Unit tests for CLI functionality
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from dataguild.cli import main, extract, quick_extract, test_connection, init_config, version


class TestCLI:
    """Test cases for CLI functionality"""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing"""
        return CliRunner()
    
    @pytest.fixture
    def sample_config_file(self):
        """Create a sample configuration file"""
        config_data = {
            "account_id": "test-account.snowflakecomputing.com",
            "username": "test-user",
            "password": "test-password",
            "warehouse": "test-warehouse",
            "database": "test-database",
            "schema": "test-schema"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            yield f.name
        
        # Cleanup
        os.unlink(f.name)
    
    def test_main_command(self, runner):
        """Test main command group"""
        result = runner.invoke(main)
        assert result.exit_code == 0
        assert "DataGuild Snowflake Connector CLI" in result.output
    
    def test_version_command(self, runner):
        """Test version command"""
        result = runner.invoke(version)
        assert result.exit_code == 0
        assert "DataGuild Snowflake Connector v1.0.0" in result.output
    
    def test_init_config_command(self, runner):
        """Test init-config command"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "test_config.yml")
            
            result = runner.invoke(init_config, ["--output", config_file])
            assert result.exit_code == 0
            assert "Sample configuration created" in result.output
            
            # Verify file was created
            assert os.path.exists(config_file)
            
            # Verify file contains expected content
            with open(config_file, 'r') as f:
                content = f.read()
                assert "account_id" in content
                assert "username" in content
                assert "warehouse" in content
    
    def test_init_config_default_output(self, runner):
        """Test init-config command with default output"""
        result = runner.invoke(init_config)
        assert result.exit_code == 0
        assert "Sample configuration created: snowflake_config.yml" in result.output
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_extract_command_success(self, mock_context, mock_config, mock_source, runner, sample_config_file):
        """Test extract command with successful execution"""
        # Mock the source and its methods
        mock_source_instance = Mock()
        mock_source_instance.get_workunits.return_value = [
            Mock(id="workunit-1"),
            Mock(id="workunit-2")
        ]
        mock_source_instance.get_metadata_summary.return_value = {
            "extraction_info": {"workunits_processed": 2}
        }
        mock_source.return_value = mock_source_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "output.json")
            
            result = runner.invoke(extract, [
                "--config", sample_config_file,
                "--output", output_file
            ])
            
            assert result.exit_code == 0
            assert "Metadata extraction completed" in result.output
            assert os.path.exists(output_file)
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_extract_command_validation_only(self, mock_context, mock_config, mock_source, runner, sample_config_file):
        """Test extract command with validation only"""
        # Mock the source
        mock_source_instance = Mock()
        mock_source_instance.test_connection.return_value = True
        mock_source.return_value = mock_source_instance
        
        result = runner.invoke(extract, [
            "--config", sample_config_file,
            "--output", "dummy.json",
            "--validate-only"
        ])
        
        assert result.exit_code == 0
        assert "Configuration and connection validation successful" in result.output
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_extract_command_dry_run(self, mock_context, mock_config, mock_source, runner, sample_config_file):
        """Test extract command with dry run"""
        result = runner.invoke(extract, [
            "--config", sample_config_file,
            "--output", "dummy.json",
            "--dry-run"
        ])
        
        assert result.exit_code == 0
        assert "Dry run completed successfully" in result.output
    
    def test_extract_command_missing_config(self, runner):
        """Test extract command with missing config file"""
        result = runner.invoke(extract, [
            "--config", "nonexistent.yml",
            "--output", "dummy.json"
        ])
        
        assert result.exit_code != 0
        assert "Error" in result.output
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_quick_extract_command(self, mock_context, mock_config, mock_source, runner):
        """Test quick-extract command"""
        # Mock the source
        mock_source_instance = Mock()
        mock_source_instance.get_workunits.return_value = [Mock(id="workunit-1")]
        mock_source_instance.get_metadata_summary.return_value = {
            "extraction_info": {"workunits_processed": 1}
        }
        mock_source.return_value = mock_source_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "output.json")
            
            result = runner.invoke(quick_extract, [
                "--account", "test-account",
                "--user", "test-user",
                "--password", "test-password",
                "--warehouse", "test-warehouse",
                "--database", "test-database",
                "--output", output_file
            ])
            
            assert result.exit_code == 0
            assert "Quick extraction completed" in result.output
            assert os.path.exists(output_file)
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_test_connection_command_with_config(self, mock_context, mock_config, mock_source, runner, sample_config_file):
        """Test test-connection command with config file"""
        # Mock the source
        mock_source_instance = Mock()
        mock_source_instance.test_connection.return_value = True
        mock_source.return_value = mock_source_instance
        
        result = runner.invoke(test_connection, [
            "--config", sample_config_file
        ])
        
        assert result.exit_code == 0
        assert "Snowflake connection test successful" in result.output
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_test_connection_command_with_params(self, mock_context, mock_config, mock_source, runner):
        """Test test-connection command with command-line parameters"""
        # Mock the source
        mock_source_instance = Mock()
        mock_source_instance.test_connection.return_value = True
        mock_source.return_value = mock_source_instance
        
        result = runner.invoke(test_connection, [
            "--account", "test-account",
            "--user", "test-user",
            "--password", "test-password",
            "--warehouse", "test-warehouse",
            "--database", "test-database"
        ])
        
        assert result.exit_code == 0
        assert "Snowflake connection test successful" in result.output
    
    def test_test_connection_command_missing_params(self, runner):
        """Test test-connection command with missing parameters"""
        result = runner.invoke(test_connection, [
            "--account", "test-account"
            # Missing other required parameters
        ])
        
        assert result.exit_code != 0
        assert "Missing required parameters" in result.output
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_extract_command_with_verbose_logging(self, mock_context, mock_config, mock_source, runner, sample_config_file):
        """Test extract command with verbose logging"""
        # Mock the source
        mock_source_instance = Mock()
        mock_source_instance.get_workunits.return_value = [Mock(id="workunit-1")]
        mock_source_instance.get_metadata_summary.return_value = {
            "extraction_info": {"workunits_processed": 1}
        }
        mock_source.return_value = mock_source_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "output.json")
            
            result = runner.invoke(extract, [
                "--config", sample_config_file,
                "--output", output_file,
                "--verbose"
            ])
            
            assert result.exit_code == 0
            assert "Metadata extraction completed" in result.output
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_extract_command_with_log_file(self, mock_context, mock_config, mock_source, runner, sample_config_file):
        """Test extract command with log file"""
        # Mock the source
        mock_source_instance = Mock()
        mock_source_instance.get_workunits.return_value = [Mock(id="workunit-1")]
        mock_source_instance.get_metadata_summary.return_value = {
            "extraction_info": {"workunits_processed": 1}
        }
        mock_source.return_value = mock_source_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "output.json")
            log_file = os.path.join(temp_dir, "test.log")
            
            result = runner.invoke(extract, [
                "--config", sample_config_file,
                "--output", output_file,
                "--log-file", log_file
            ])
            
            assert result.exit_code == 0
            assert "Metadata extraction completed" in result.output
            # Note: In a real test, we would verify the log file was created and contains expected content
    
    def test_extract_command_invalid_config(self, runner):
        """Test extract command with invalid configuration"""
        # Create an invalid config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            invalid_config_file = f.name
        
        try:
            result = runner.invoke(extract, [
                "--config", invalid_config_file,
                "--output", "dummy.json"
            ])
            
            assert result.exit_code != 0
            assert "Error" in result.output
        
        finally:
            os.unlink(invalid_config_file)
    
    @patch('dataguild.cli.SnowflakeV2Source')
    @patch('dataguild.cli.SnowflakeV2Config')
    @patch('dataguild.cli.PipelineContext')
    def test_extract_command_source_error(self, mock_context, mock_config, mock_source, runner, sample_config_file):
        """Test extract command when source raises an error"""
        # Mock the source to raise an error
        mock_source_instance = Mock()
        mock_source_instance.get_workunits.side_effect = Exception("Source error")
        mock_source.return_value = mock_source_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "output.json")
            
            result = runner.invoke(extract, [
                "--config", sample_config_file,
                "--output", output_file
            ])
            
            assert result.exit_code != 0
            assert "Error" in result.output
            assert "Source error" in result.output
