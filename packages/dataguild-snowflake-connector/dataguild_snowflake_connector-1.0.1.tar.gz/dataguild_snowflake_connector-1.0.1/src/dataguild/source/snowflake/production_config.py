"""
Production-ready configuration management for DataGuild Snowflake Connector
"""

import os
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
import yaml
from dataclasses import dataclass, field
from enum import Enum

from .config import SnowflakeV2Config

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Supported deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class ProductionConfig:
    """Production configuration container."""
    
    # Environment settings
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_level: str = "INFO"
    
    # Snowflake connection settings
    snowflake_config: Optional[SnowflakeV2Config] = None
    
    # Performance settings
    max_workers: int = 4
    batch_size: int = 1000
    timeout_seconds: int = 300
    
    # Monitoring settings
    enable_metrics: bool = True
    metrics_port: int = 8080
    health_check_interval: int = 30
    
    # Data quality settings
    enable_data_validation: bool = True
    validation_timeout: int = 60
    max_retries: int = 3
    
    # Security settings
    encrypt_credentials: bool = True
    credential_vault: Optional[str] = None
    
    # Output settings
    output_format: str = "json"
    output_compression: bool = True
    output_directory: str = "./output"
    
    # State management
    state_backend: str = "file"  # file, redis, s3
    state_directory: str = "./state"
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Production configuration manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
    
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        possible_paths = [
            "config/snowflake_config.yml",
            "snowflake_config.yml",
            "config/production.yml",
            "production.yml",
            os.path.expanduser("~/.dataguild/snowflake.yml"),
            "/etc/dataguild/snowflake.yml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found configuration file: {path}")
                return path
        
        # Create default config if none found
        default_path = "snowflake_config.yml"
        self._create_default_config(default_path)
        return default_path
    
    def _create_default_config(self, path: str) -> None:
        """Create a default configuration file."""
        default_config = {
            "environment": "development",
            "debug": True,
            "log_level": "INFO",
            "snowflake": {
                "username": "${SNOWFLAKE_USERNAME}",
                "password": "${SNOWFLAKE_PASSWORD}",
                "account_id": "${SNOWFLAKE_ACCOUNT_ID}",
                "database": "${SNOWFLAKE_DATABASE}",
                "schema": "${SNOWFLAKE_SCHEMA}",
                "warehouse": "${SNOWFLAKE_WAREHOUSE}",
                "role": "${SNOWFLAKE_ROLE}"
            },
            "performance": {
                "max_workers": 4,
                "batch_size": 1000,
                "timeout_seconds": 300
            },
            "monitoring": {
                "enable_metrics": True,
                "metrics_port": 8080,
                "health_check_interval": 30
            },
            "data_quality": {
                "enable_data_validation": True,
                "validation_timeout": 60,
                "max_retries": 3
            },
            "security": {
                "encrypt_credentials": True,
                "credential_vault": None
            },
            "output": {
                "format": "json",
                "compression": True,
                "directory": "./output"
            },
            "state": {
                "backend": "file",
                "directory": "./state"
            }
        }
        
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(path)
        if dir_path:  # Only create directory if path has a directory component
            os.makedirs(dir_path, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        logger.info(f"Created default configuration file: {path}")
    
    def _load_config(self) -> ProductionConfig:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Resolve environment variables
            config_data = self._resolve_env_vars(config_data)
            
            # Create Snowflake config
            snowflake_config = None
            if 'snowflake' in config_data:
                snowflake_data = config_data['snowflake']
                snowflake_config = SnowflakeV2Config(**snowflake_data)
            
            # Create production config
            return ProductionConfig(
                environment=Environment(config_data.get('environment', 'development')),
                debug=config_data.get('debug', False),
                log_level=config_data.get('log_level', 'INFO'),
                snowflake_config=snowflake_config,
                max_workers=config_data.get('performance', {}).get('max_workers', 4),
                batch_size=config_data.get('performance', {}).get('batch_size', 1000),
                timeout_seconds=config_data.get('performance', {}).get('timeout_seconds', 300),
                enable_metrics=config_data.get('monitoring', {}).get('enable_metrics', True),
                metrics_port=config_data.get('monitoring', {}).get('metrics_port', 8080),
                health_check_interval=config_data.get('monitoring', {}).get('health_check_interval', 30),
                enable_data_validation=config_data.get('data_quality', {}).get('enable_data_validation', True),
                validation_timeout=config_data.get('data_quality', {}).get('validation_timeout', 60),
                max_retries=config_data.get('data_quality', {}).get('max_retries', 3),
                encrypt_credentials=config_data.get('security', {}).get('encrypt_credentials', True),
                credential_vault=config_data.get('security', {}).get('credential_vault'),
                output_format=config_data.get('output', {}).get('format', 'json'),
                output_compression=config_data.get('output', {}).get('compression', True),
                output_directory=config_data.get('output', {}).get('directory', './output'),
                state_backend=config_data.get('state', {}).get('backend', 'file'),
                state_directory=config_data.get('state', {}).get('directory', './state'),
                custom_settings=config_data.get('custom', {})
            )
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _resolve_env_vars(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve environment variables in configuration."""
        def resolve_value(value):
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                return os.getenv(env_var, value)
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(v) for v in value]
            else:
                return value
        
        return resolve_value(config_data)
    
    def get_snowflake_config(self) -> SnowflakeV2Config:
        """Get Snowflake configuration."""
        if self.config.snowflake_config is None:
            raise ValueError("Snowflake configuration not found")
        return self.config.snowflake_config
    
    def get_log_level(self) -> str:
        """Get logging level."""
        return self.config.log_level
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.config.environment == Environment.PRODUCTION
    
    def get_output_directory(self) -> str:
        """Get output directory."""
        return self.config.output_directory
    
    def get_state_directory(self) -> str:
        """Get state directory."""
        return self.config.state_directory


def create_production_config(
    config_path: Optional[str] = None,
    environment: Optional[Environment] = None,
    **overrides
) -> ProductionConfig:
    """Create a production configuration with overrides."""
    manager = ConfigManager(config_path)
    config = manager.config
    
    if environment:
        config.environment = environment
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            config.custom_settings[key] = value
    
    return config


# Environment-specific configurations
def get_development_config() -> ProductionConfig:
    """Get development configuration."""
    return create_production_config(
        environment=Environment.DEVELOPMENT,
        debug=True,
        log_level="DEBUG",
        max_workers=2,
        batch_size=100
    )


def get_staging_config() -> ProductionConfig:
    """Get staging configuration."""
    return create_production_config(
        environment=Environment.STAGING,
        debug=False,
        log_level="INFO",
        max_workers=4,
        batch_size=500
    )


def get_production_config() -> ProductionConfig:
    """Get production configuration."""
    return create_production_config(
        environment=Environment.PRODUCTION,
        debug=False,
        log_level="WARNING",
        max_workers=8,
        batch_size=2000,
        enable_metrics=True,
        encrypt_credentials=True
    )
