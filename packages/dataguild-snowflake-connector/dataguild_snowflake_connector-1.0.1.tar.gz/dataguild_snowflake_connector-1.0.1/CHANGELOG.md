# Changelog

All notable changes to the DataGuild Snowflake Connector will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-09-23

### Fixed
- Updated package metadata and version information
- Improved PyPI package description and classifiers
- Enhanced documentation and examples
- Fixed minor configuration issues

### Changed
- Version bump to 1.0.1 for improved package management
- Updated internal version references

## [1.0.0] - 2024-01-23

### Added
- **Initial Release** - Enterprise-grade Snowflake metadata ingestion connector
- **Complete Metadata Extraction** - Tables, views, streams, procedures, functions, and more
- **Advanced Lineage Tracking** - Table-to-table and column-level lineage with SQL parsing
- **Usage Analytics** - Comprehensive usage statistics and operational metrics
- **Data Governance** - Tag extraction and classification support
- **Production Ready** - Enhanced error handling, monitoring, and structured logging
- **CLI Support** - Easy-to-use command-line interface with multiple commands
- **Flexible Configuration** - YAML-based configuration system with extensive options
- **DataHub Compatible** - Built with DataHub best practices and patterns

### Features
- **SnowflakeV2Source** - Main source class for metadata extraction
- **SnowflakeV2Config** - Comprehensive configuration management
- **SnowflakeV2Report** - Detailed reporting and monitoring
- **Command Line Interface** - Full CLI with extract, quick-extract, test-connection, and init-config commands
- **Configuration Management** - Support for YAML configuration files and command-line parameters
- **Error Handling** - Robust error handling with retry logic and detailed logging
- **Performance Optimization** - Multi-threaded processing and connection pooling
- **Metadata Processing** - Comprehensive workunit processing with deduplication
- **Lineage Extraction** - Advanced SQL parsing for lineage relationships
- **Usage Statistics** - Detailed usage analytics and operational metrics
- **Tag Processing** - Complete tag extraction and classification
- **Database Filtering** - Flexible database and schema filtering patterns
- **Time Window Support** - Configurable time windows for usage and lineage extraction
- **Stateful Ingestion** - Support for incremental and stateful metadata extraction

### Technical Details
- **Python 3.8+ Support** - Compatible with Python 3.8, 3.9, 3.10, 3.11, and 3.12
- **Dependencies** - Snowflake Connector, SQLGlot, Pydantic, Click, and more
- **Architecture** - Modular design with clear separation of concerns
- **Testing** - Comprehensive test suite with unit, integration, and performance tests
- **Documentation** - Complete documentation with examples and API reference
- **Packaging** - Proper pip package with setup.py and pyproject.toml

### CLI Commands
- `dataguild-snowflake extract` - Extract metadata using configuration file
- `dataguild-snowflake quick-extract` - Quick extraction with command-line parameters
- `dataguild-snowflake test-connection` - Test Snowflake connection
- `dataguild-snowflake init-config` - Generate sample configuration file
- `dataguild-snowflake version` - Show version information

### Configuration Options
- **Connection Settings** - Account, username, password, warehouse, database, schema, role
- **Extraction Settings** - Usage stats, lineage, tags, views, tables, streams, procedures
- **Performance Settings** - Max workers, timeouts, connection pooling
- **Filtering** - Database and schema patterns with allow/deny lists
- **Time Windows** - Start and end times for usage and lineage extraction
- **Stateful Ingestion** - Incremental extraction with state management
- **Security** - SSL/TLS, OAuth, and other security options

### Output Format
- **Structured JSON** - Well-organized metadata output with extraction summary
- **Workunit Processing** - Individual workunits with aspect information
- **Metadata Organization** - Hierarchical organization by database, schema, and table
- **Summary Statistics** - Comprehensive extraction summary with counts and metrics
- **Error Reporting** - Detailed error reporting and logging

### Examples
- **Basic Usage** - Simple extraction example with minimal configuration
- **Advanced Usage** - Complex extraction with custom filtering and error handling
- **Configuration Examples** - Sample configuration files with all options
- **CLI Examples** - Command-line usage examples for all commands

### Documentation
- **README.md** - Comprehensive documentation with installation and usage instructions
- **API Reference** - Complete API documentation for all classes and methods
- **Examples** - Multiple example scripts demonstrating different use cases
- **Configuration Guide** - Detailed configuration options and examples
- **CLI Reference** - Complete command-line interface documentation

### Testing
- **Unit Tests** - Comprehensive unit tests for all components
- **Integration Tests** - End-to-end integration tests with mocked dependencies
- **Performance Tests** - Performance testing with large datasets
- **CLI Tests** - Complete CLI functionality testing
- **Error Handling Tests** - Error handling and recovery testing

### Dependencies
- **Core Dependencies** - Snowflake Connector, SQLGlot, Pydantic, Click
- **Database Dependencies** - PostgreSQL, Neo4j support
- **Development Dependencies** - Pytest, Black, Flake8, MyPy, Sphinx
- **Optional Dependencies** - Additional features and integrations

### Installation
- **PyPI Package** - `pip install dataguild-snowflake-connector`
- **Source Installation** - `pip install -e .`
- **Development Installation** - `pip install -e ".[dev,test]"`
- **Documentation Installation** - `pip install -e ".[docs]"`

### License
- **Apache 2.0** - Open source license with commercial use allowed

### Support
- **GitHub Issues** - Issue tracking and bug reports
- **GitHub Discussions** - Community discussions and Q&A
- **Documentation** - Comprehensive online documentation
- **Email Support** - engineering@dataguild.com

## [Unreleased]

### Planned Features
- Support for additional Snowflake object types (external tables, stages, etc.)
- Enhanced lineage visualization tools
- Real-time metadata streaming
- Integration with additional data catalogs (Collibra, Alation, etc.)
- Advanced data quality metrics and profiling
- GraphQL API for metadata querying
- Webhook support for real-time updates
- Enhanced security features (OAuth, SSO)
- Docker containerization
- Kubernetes deployment support
- Cloud-native monitoring and observability
- Advanced caching mechanisms
- Incremental metadata updates
- Data lineage visualization
- Data quality scoring
- Automated data profiling
- Custom metadata extraction rules
- Multi-tenant support
- Advanced security and compliance features

### Known Issues
- None at this time

### Breaking Changes
- None in this release

### Deprecations
- None in this release

---

## Version History

- **1.0.0** - Initial release with comprehensive Snowflake metadata extraction capabilities
- **0.1.0** - Pre-release development version (internal use only)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Support

- **Documentation**: [https://dataguild-snowflake.readthedocs.io](https://dataguild-snowflake.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/dataguild/snowflake-connector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dataguild/snowflake-connector/discussions)
- **Email**: engineering@dataguild.com