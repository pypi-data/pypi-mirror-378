# DataGuild Snowflake Connector - Usage Guide

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install dataguild-snowflake-connector

# Or install from local wheel
pip install dist/dataguild_snowflake_connector-1.0.0-py3-none-any.whl

# Or install in development mode
pip install -e .
```

### Basic Usage

#### 1. Command Line Interface

```bash
# Generate sample configuration
dataguild-snowflake init-config --output my_config.yml

# Extract metadata using configuration file
dataguild-snowflake extract --config my_config.yml --output metadata.json

# Quick extraction with command-line parameters
dataguild-snowflake quick-extract \
  --account your-account.snowflakecomputing.com \
  --user your-username \
  --password your-password \
  --warehouse your-warehouse \
  --database your-database \
  --output metadata.json

# Test connection
dataguild-snowflake test-connection --config my_config.yml
```

#### 2. Python API

```python
from dataguild.source.snowflake.main import SnowflakeV2Source
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.api.common import PipelineContext

# Configure connection
config = SnowflakeV2Config(
    account_id="your-account.snowflakecomputing.com",
    username="your-username",
    password="your-password",
    warehouse="your-warehouse",
    database="your-database",
    schema="your-schema"
)

# Create pipeline context
ctx = PipelineContext(run_id="my_extraction")

# Create and run source
source = SnowflakeV2Source(ctx, config)

# Extract metadata
for workunit in source.get_workunits():
    print(f"Processed workunit: {workunit.id}")
```

## 📋 Configuration

### Sample Configuration File

```yaml
# Required connection parameters
account_id: "your-account.snowflakecomputing.com"
username: "your-username"
password: "your-password"
warehouse: "your-warehouse"
database: "your-database"
schema: "your-schema"
role: "your-role"

# Optional extraction settings
include_usage_stats: true
include_table_lineage: true
include_column_lineage: true
include_tags: true
include_views: true
include_tables_bool: true
include_streams: true
include_procedures: true
warn_no_datasets: false

# Performance settings
max_workers: 4
connection_timeout: 300
query_timeout: 600

# Database filtering
database_pattern:
  allow: ["YOUR_DATABASE"]
  deny: ["SNOWFLAKE.*"]
  ignoreCase: true

schema_pattern:
  allow: ["PUBLIC"]
  deny: ["INFORMATION_SCHEMA"]
  ignoreCase: true
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `account_id` | string | Required | Snowflake account identifier |
| `username` | string | Required | Snowflake username |
| `password` | string | Required | Snowflake password |
| `warehouse` | string | Required | Snowflake warehouse name |
| `database` | string | Required | Snowflake database name |
| `schema` | string | Optional | Snowflake schema name |
| `role` | string | Optional | Snowflake role |
| `include_usage_stats` | boolean | true | Include usage statistics |
| `include_table_lineage` | boolean | true | Include table lineage |
| `include_column_lineage` | boolean | true | Include column lineage |
| `include_tags` | boolean | true | Include tag information |
| `include_views` | boolean | true | Include views |
| `include_tables_bool` | boolean | true | Include tables |
| `include_streams` | boolean | true | Include streams |
| `include_procedures` | boolean | true | Include procedures |
| `max_workers` | integer | 4 | Number of parallel workers |
| `connection_timeout` | integer | 300 | Connection timeout in seconds |
| `query_timeout` | integer | 600 | Query timeout in seconds |

## 🔧 Advanced Usage

### Custom Filtering

```python
config = SnowflakeV2Config(
    account_id="your-account",
    username="your-user",
    password="your-password",
    warehouse="your-warehouse",
    database="your-database",
    
    # Custom filtering
    database_pattern={
        "allow": ["PROD_DATABASE", "STAGING_DATABASE"],
        "deny": ["TEMP_*", "TEST_*"],
        "ignoreCase": True
    },
    schema_pattern={
        "allow": ["PUBLIC", "ANALYTICS"],
        "deny": ["INFORMATION_SCHEMA"],
        "ignoreCase": True
    }
)
```

### Error Handling

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    config = SnowflakeV2Config(...)
    ctx = PipelineContext(run_id="error_handling_test")
    source = SnowflakeV2Source(ctx, config)
    
    # Test connection first
    if source.test_connection():
        print("✅ Connection successful")
    else:
        print("❌ Connection failed")
        sys.exit(1)
    
    # Extract metadata
    workunit_count = 0
    for workunit in source.get_workunits():
        workunit_count += 1
        if workunit_count % 100 == 0:
            print(f"Processed {workunit_count} workunits...")
    
    print(f"✅ Successfully extracted {workunit_count} workunits")
    
except Exception as e:
    logging.error(f"Failed to extract metadata: {e}")
    sys.exit(1)
```

### Performance Optimization

```python
# For large datasets, increase workers
config = SnowflakeV2Config(
    # ... other settings ...
    max_workers=8,
    connection_timeout=600,
    query_timeout=1200
)

# Use time windows for usage and lineage
config = SnowflakeV2Config(
    # ... other settings ...
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-12-31T23:59:59Z"
)
```

## 📊 Output Format

The connector outputs structured metadata in JSON format:

```json
{
  "extraction_info": {
    "timestamp": "2024-01-01T12:00:00Z",
    "extractor_version": "1.0.0",
    "extraction_id": "extract_1704110400"
  },
  "processed_metadata": {
    "databases": [...],
    "schemas": [...],
    "tables": [...],
    "views": [...],
    "columns": [...],
    "lineage": [...],
    "usage_stats": [...],
    "operational_stats": [...],
    "custom_metadata": [...]
  },
  "summary": {
    "total_workunits_processed": 150,
    "metadata_counts": {
      "databases": 1,
      "schemas": 5,
      "tables": 25,
      "views": 10,
      "columns": 200,
      "lineage_relationships": 15,
      "usage_records": 50
    }
  }
}
```

## 🧪 Testing

### Run Tests

```bash
# Install development dependencies
pip install -e ".[dev,test]"

# Run all tests
pytest

# Run with coverage
pytest --cov=dataguild --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

### Test Configuration

```bash
# Test with sample configuration
dataguild-snowflake test-connection --config examples/sample_config.yml

# Test with command-line parameters
dataguild-snowflake test-connection \
  --account your-account \
  --user your-username \
  --password your-password \
  --warehouse your-warehouse \
  --database your-database
```

## 🔍 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify account ID format (should include `.snowflakecomputing.com`)
   - Check username and password
   - Ensure warehouse is running
   - Verify network connectivity

2. **No Tables Found**
   - Check database and schema names
   - Verify user has access to the database
   - Check filtering patterns in configuration

3. **Permission Errors**
   - Ensure user has necessary privileges
   - Check role assignments
   - Verify warehouse access

4. **Timeout Errors**
   - Increase `connection_timeout` and `query_timeout`
   - Reduce `max_workers` for stability
   - Check network latency

### Debug Mode

```bash
# Enable verbose logging
dataguild-snowflake extract --config my_config.yml --output metadata.json --verbose

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Examples

### Basic Extraction

```python
from dataguild.source.snowflake.main import SnowflakeV2Source
from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.api.common import PipelineContext

# Basic configuration
config = SnowflakeV2Config(
    account_id="your-account.snowflakecomputing.com",
    username="your-username",
    password="your-password",
    warehouse="your-warehouse",
    database="your-database"
)

ctx = PipelineContext(run_id="basic_example")
source = SnowflakeV2Source(ctx, config)

# Extract and save metadata
metadata = {}
for workunit in source.get_workunits():
    if workunit.mcp_raw:
        aspect_name = workunit.mcp_raw.get("aspectName")
        if aspect_name not in metadata:
            metadata[aspect_name] = []
        metadata[aspect_name].append(workunit.mcp_raw)

# Save to file
import json
with open("metadata.json", "w") as f:
    json.dump(metadata, f, indent=2, default=str)
```

### Advanced Extraction with Filtering

```python
# Advanced configuration with filtering
config = SnowflakeV2Config(
    account_id="your-account.snowflakecomputing.com",
    username="your-username",
    password="your-password",
    warehouse="your-warehouse",
    database="your-database",
    schema="your-schema",
    
    # Advanced options
    include_usage_stats=True,
    include_table_lineage=True,
    include_column_lineage=True,
    include_tags=True,
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
    }
)

ctx = PipelineContext(run_id="advanced_example")
source = SnowflakeV2Source(ctx, config)

# Test connection first
if not source.test_connection():
    print("❌ Connection failed!")
    sys.exit(1)

# Extract with progress tracking
workunit_count = 0
for workunit in source.get_workunits():
    workunit_count += 1
    if workunit_count % 50 == 0:
        print(f"Processed {workunit_count} workunits...")

print(f"✅ Successfully extracted {workunit_count} workunits")
```

## 📞 Support

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/dataguild/snowflake-connector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dataguild/snowflake-connector/discussions)
- **Email**: engineering@dataguild.com

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
