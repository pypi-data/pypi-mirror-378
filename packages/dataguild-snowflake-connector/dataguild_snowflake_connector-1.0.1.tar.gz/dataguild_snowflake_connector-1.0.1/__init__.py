"""
DataGuild Snowflake Connector
Enterprise-grade metadata extraction for Snowflake data warehouses.
"""

__version__ = "1.0.0"

# Import main classes for easy access
try:
    from dataguild.source.snowflake.main import SnowflakeV2Source
    from dataguild.source.snowflake.config import SnowflakeV2Config
except ImportError:
    # Handle missing modules gracefully during development
    pass

# Make main classes available at package level
__all__ = [
    '__version__',
    'SnowflakeV2Source',
    'SnowflakeV2Config'
]
