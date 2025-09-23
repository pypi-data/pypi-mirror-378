# Contributing to DataGuild Snowflake Connector

Thank you for your interest in contributing to the DataGuild Snowflake Connector! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Snowflake account (for testing)
- Docker (optional, for containerized testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/dataguild-snowflake-connector.git
   cd dataguild-snowflake-connector
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## 🧪 Testing

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests (requires Snowflake connection)
pytest tests/integration/

# All tests
pytest

# With coverage
pytest --cov=dataguild --cov-report=html
```

### Test Configuration

Create a test configuration file for integration tests:

```yaml
# tests/test_config.yml
account_id: "your-test-account.snowflakecomputing.com"
username: "test-user"
password: "test-password"
warehouse: "TEST_WH"
database: "TEST_DB"
schema: "PUBLIC"
```

## 📝 Code Style

We follow these coding standards:

- **Python**: PEP 8 with Black formatting
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Follow Google docstring format
- **Imports**: Use isort for import organization

### Formatting

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only src/ tests/
```

## 🔧 Development Guidelines

### Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement Changes**
   - Add new functionality
   - Include comprehensive tests
   - Update documentation
   - Add type hints

3. **Test Your Changes**
   ```bash
   pytest tests/
   ```

4. **Update Documentation**
   - Update README.md if needed
   - Add docstrings to new functions
   - Update CHANGELOG.md

### Bug Fixes

1. **Create Bug Branch**
   ```bash
   git checkout -b bugfix/issue-description
   ```

2. **Fix the Issue**
   - Identify and fix the root cause
   - Add tests to prevent regression
   - Update documentation if needed

3. **Test the Fix**
   ```bash
   pytest tests/
   ```

## 📋 Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] No merge conflicts

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Operating system
   - Package version

2. **Steps to Reproduce**
   - Clear, minimal steps
   - Sample configuration
   - Expected vs actual behavior

3. **Error Information**
   - Full error traceback
   - Log files (if applicable)

### Feature Requests

For feature requests, please include:

1. **Use Case**
   - Why is this feature needed?
   - How would it be used?

2. **Proposed Solution**
   - High-level approach
   - Any design considerations

3. **Alternatives Considered**
   - Other approaches you've considered

## 🏗️ Architecture Guidelines

### Code Organization

- **Single Responsibility**: Each module should have a clear purpose
- **Separation of Concerns**: Separate data access, business logic, and presentation
- **Error Handling**: Use appropriate exception types and error messages
- **Logging**: Use structured logging with appropriate levels

### Performance Considerations

- **Database Queries**: Optimize SQL queries for performance
- **Memory Usage**: Be mindful of memory consumption for large datasets
- **Parallel Processing**: Use appropriate concurrency patterns
- **Caching**: Implement caching where appropriate

## 📚 Documentation

### Code Documentation

- **Docstrings**: All public functions and classes need docstrings
- **Type Hints**: Use type hints for better code clarity
- **Comments**: Add comments for complex logic
- **Examples**: Include usage examples in docstrings

### API Documentation

- **README**: Keep README.md up to date
- **Examples**: Provide clear usage examples
- **Configuration**: Document all configuration options
- **Changelog**: Maintain detailed changelog

## 🔒 Security

### Security Guidelines

- **Credentials**: Never commit credentials or sensitive data
- **Input Validation**: Validate all inputs
- **SQL Injection**: Use parameterized queries
- **Dependencies**: Keep dependencies updated

### Reporting Security Issues

For security issues, please email security@dataguild.com instead of creating a public issue.

## 🎯 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Tag created
- [ ] PyPI package published

## 🤝 Community

### Getting Help

- **GitHub Discussions**: For questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Email**: support@dataguild.com

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to DataGuild Snowflake Connector! 🎉
