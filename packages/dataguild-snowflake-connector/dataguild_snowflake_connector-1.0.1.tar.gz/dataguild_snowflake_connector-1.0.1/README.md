# DataGuild Snowflake Connector

[![PyPI version](https://badge.fury.io/py/dataguild-snowflake-connector.svg)](https://badge.fury.io/py/dataguild-snowflake-connector)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Enterprise-grade Snowflake metadata ingestion with comprehensive lineage tracking, usage analytics, and data governance capabilities.

## 🚀 Features

- **Comprehensive Metadata Extraction**: Tables, views, schemas, columns, and relationships
- **Advanced Lineage Tracking**: Table-to-table and column-level lineage from SQL queries
- **Usage Analytics**: Query patterns, access patterns, and operational statistics
- **Data Governance**: Tag management, data classification, and ownership tracking
- **Production Ready**: Robust error handling, monitoring, and performance optimization
- **CLI Interface**: Easy-to-use command-line tools for extraction and management
- **DataHub Compatible**: Follows DataHub patterns for seamless integration

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install dataguild-snowflake-connector
```

### From Source

```bash
git clone https://github.com/your-org/dataguild-snowflake-connector.git
cd dataguild-snowflake-connector
pip install -e .
```

## 🚀 Quick Start

### Basic Usage

```python
from dataguild.source.snowflake.main import SnowflakeV2Source, SnowflakeV2Config
from dataguild.api.common import PipelineContext

# Configure your Snowflake connection
config = SnowflakeV2Config(
    account_id="your-account.snowflakecomputing.com",
    username="your-username",
    password="your-password",
    warehouse="your-warehouse",
    database="your-database",
    schema="your-schema"  # Optional
)

# Create and run the source
ctx = PipelineContext(run_id="my_extraction")
source = SnowflakeV2Source(ctx, config)

# Extract metadata workunits
all_workunits = []
for workunit in source.get_workunits():
    all_workunits.append(workunit)
    print(f"Processed workunit: {workunit.id}")

print(f"Extracted {len(all_workunits)} workunits.")
```

### CLI Usage

```bash
# Test connection
dataguild test-connection --config config.yml

# Extract metadata
dataguild extract --config config.yml --output metadata.json

# Generate sample configuration
dataguild init-config --output config.yml
```

## 📋 Configuration

Create a configuration file (`config.yml`):

```yaml
# Snowflake Connection
account_id: "your-account.snowflakecomputing.com"
username: "your-username"
password: "your-password"
warehouse: "your-warehouse"
database: "your-database"
schema: "your-schema"  # Optional
role: "your-role"      # Optional

# Extraction Settings
include_usage_stats: true
include_lineage: true
include_tags: true
include_view_definitions: true
include_primary_keys: true
include_foreign_keys: true

# Performance Settings
max_workers: 4
connection_timeout: 300
query_timeout: 600

# Logging
log_level: "INFO"
```

## 🏗️ Architecture

The DataGuild Snowflake Connector follows a modular architecture inspired by DataHub:

```
dataguild_snowflake/
├── src/dataguild/
│   ├── source/snowflake/
│   │   ├── main.py              # Main source class
│   │   ├── config.py            # Configuration management
│   │   ├── connection.py        # Snowflake connection handling
│   │   ├── schema_gen.py        # Schema metadata generation
│   │   ├── lineage.py           # Lineage extraction
│   │   ├── usage.py             # Usage analytics
│   │   ├── tag.py               # Tag management
│   │   └── ...                  # Additional modules
│   └── cli.py                   # Command-line interface
├── tests/                       # Test suite
├── examples/                    # Usage examples
└── docs/                        # Documentation
```

## 🔧 Advanced Usage

### Custom Extraction Patterns

```python
config = SnowflakeV2Config(
    # ... connection settings ...
    
    # Database filtering
    database_pattern={"allow": ["PROD_DB", "STAGING_DB"]},
    schema_pattern={"allow": ["PUBLIC", "ANALYTICS"]},
    
    # Table filtering
    table_pattern={"allow": ["FACT_%", "DIM_%"]},
    
    # Lineage settings
    include_column_lineage=True,
    include_view_lineage=True,
    
    # Usage analytics
    include_usage_stats=True,
    usage_lookback_days=30,
)
```

### Programmatic Configuration

```python
from dataguild.source.snowflake.config import SnowflakeV2Config

# Create config programmatically
config = SnowflakeV2Config(
    account_id="my-account.snowflakecomputing.com",
    username="my-user",
    password="my-password",
    warehouse="COMPUTE_WH",
    database="MY_DATABASE",
    include_usage_stats=True,
    include_lineage=True,
    max_workers=8
)
```

## 📊 Extracted Metadata

The connector extracts comprehensive metadata including:

- **Database & Schema Information**: Names, descriptions, creation dates
- **Table & View Metadata**: Structure, types, comments, ownership
- **Column Details**: Data types, constraints, descriptions, tags
- **Lineage Relationships**: Table-to-table and column-level dependencies
- **Usage Statistics**: Query patterns, access frequency, performance metrics
- **Data Governance**: Tags, classifications, ownership, data quality metrics

## 🧪 Testing

Run the test suite:

```bash
# Unit tests
pytest tests/unit/

# Integration tests (requires Snowflake connection)
pytest tests/integration/

# All tests
pytest
```

## 📈 Performance

The connector is optimized for performance:

- **Parallel Processing**: Multi-threaded extraction for large datasets
- **Incremental Updates**: Stateful ingestion for efficient updates
- **Query Optimization**: Optimized SQL queries for metadata extraction
- **Memory Management**: Efficient memory usage for large-scale extractions

## 🔒 Security

- **Credential Management**: Secure handling of Snowflake credentials
- **Network Security**: Encrypted connections to Snowflake
- **Data Privacy**: No sensitive data stored in logs or outputs
- **Access Control**: Role-based access following Snowflake permissions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full Documentation](https://dataguild.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/your-org/dataguild-snowflake-connector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/dataguild-snowflake-connector/discussions)
- **Email**: support@dataguild.com

## 🗺️ Roadmap

- [ ] Support for additional Snowflake features (streams, tasks, etc.)
- [ ] Enhanced lineage visualization
- [ ] Real-time metadata updates
- [ ] Integration with additional data platforms
- [ ] Advanced data quality metrics

## 🙏 Acknowledgments

- Inspired by [DataHub](https://datahubproject.io/) architecture and patterns
- Built on top of [Snowflake Connector for Python](https://docs.snowflake.com/en/user-guide/python-connector.html)
- Community feedback and contributions

---

**DataGuild Snowflake Connector** - Enterprise metadata management made simple.