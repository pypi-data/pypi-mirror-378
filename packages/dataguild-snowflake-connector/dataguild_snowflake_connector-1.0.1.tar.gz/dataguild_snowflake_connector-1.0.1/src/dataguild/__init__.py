"""
DataGuild Snowflake Connector

Enterprise-grade Snowflake metadata ingestion connector with comprehensive 
lineage tracking, usage analytics, and data governance capabilities.
"""

__version__ = "1.0.1"
__author__ = "DataGuild Engineering Team"
__email__ = "engineering@dataguild.com"
__license__ = "Apache-2.0"

# Core imports
from .source.snowflake.main import SnowflakeV2Source
from .source.snowflake.config import SnowflakeV2Config
from .source.snowflake.report import SnowflakeV2Report

# Utility imports
from .api.workunit import MetadataWorkUnit
from .api.common import PipelineContext

# Version info
__version_info__ = tuple(map(int, __version__.split(".")))

# Package metadata
__all__ = [
    "SnowflakeV2Source",
    "SnowflakeV2Config", 
    "SnowflakeV2Report",
    "MetadataWorkUnit",
    "PipelineContext",
    "__version__",
    "__version_info__",
]