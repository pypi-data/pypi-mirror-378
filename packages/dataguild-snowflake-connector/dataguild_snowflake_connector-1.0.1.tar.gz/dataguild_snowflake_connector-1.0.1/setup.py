#!/usr/bin/env python3
"""
Setup script for DataGuild Snowflake Connector
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read version
def read_version():
    with open("src/dataguild/__init__.py", "r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="dataguild-snowflake-connector",
    version=read_version(),
    author="DataGuild Engineering Team",
    author_email="engineering@dataguild.com",
    description="Enterprise-grade Snowflake metadata ingestion connector for DataGuild platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/dataguild/snowflake-connector",
    project_urls={
        "Bug Tracker": "https://github.com/dataguild/snowflake-connector/issues",
        "Documentation": "https://dataguild-snowflake.readthedocs.io",
        "Source Code": "https://github.com/dataguild/snowflake-connector",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Backup",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=1.10.0,<2.0.0",
        "snowflake-connector-python>=3.0.0",
        "sqlparse>=0.4.0",
        "PyYAML>=6.0",
        "click>=8.0.0",
        "typing-extensions>=4.0.0",
        "sqlalchemy>=1.4.0",
        "pandas>=1.3.0",
        "structlog>=22.0.0",
        "psutil>=5.8.0",
        "snowflake-sqlalchemy>=1.4.0",
        "prometheus-client>=0.15.0",
        "psycopg2-binary>=2.9.0",
        "neo4j>=5.0.0",
        "sqlglot>=10.0.0",
        "networkx>=2.6.0",
        "requests>=2.25.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.6.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "isort>=5.10.0",
            "pre-commit>=2.17.0",
            "tox>=3.24.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.12.0",
            "myst-parser>=0.18.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.6.0",
            "pytest-asyncio>=0.21.0",
            "coverage>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dataguild-snowflake=dataguild.cli:main",
        ],
        "dataguild.sources": [
            "snowflake=dataguild.source.snowflake.main:SnowflakeV2Source",
        ],
    },
    include_package_data=True,
    package_data={
        "dataguild": [
            "config/*.yml",
            "config/*.yaml",
            "config/*.conf",
            "*.pyi",
        ],
    },
    zip_safe=False,
    keywords=[
        "snowflake",
        "metadata",
        "data-catalog",
        "lineage",
        "dataguild",
        "etl",
        "data-engineering",
        "data-governance",
        "data-quality",
    ],
)
