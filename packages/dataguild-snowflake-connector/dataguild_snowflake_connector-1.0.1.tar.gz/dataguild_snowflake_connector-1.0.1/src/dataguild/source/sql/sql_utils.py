"""
DataGuild SQL Utilities

This module provides utility functions for working with SQL databases,
including key generation, identifier normalization, container management,
domain assignment, and common SQL operations for metadata ingestion.
"""

import re
import logging
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from urllib.parse import quote, unquote
from dataclasses import dataclass
from datetime import datetime

from dataguild.api.source import MetadataWorkUnit
from dataguild.metadata.schemas import (
    Status, DatasetProperties, SubTypes, GlobalTags, TagAssociation
)
from dataguild.utilities.registries.domain_registry import DomainRegistry

logger = logging.getLogger(__name__)


# =============================================
# Container and Domain Management Functions
# =============================================

def add_table_to_schema_container(
    dataset_urn: str,
    parent_container_key: str,
    container_type: str = "SCHEMA"
) -> Iterable[MetadataWorkUnit]:
    """
    Add a dataset to a schema container, establishing the hierarchical relationship.

    Creates container membership work units that establish the relationship between
    a dataset (table, view, etc.) and its parent schema container in the metadata graph.

    Args:
        dataset_urn: URN of the dataset to add to container
        parent_container_key: Key of the parent container (schema)
        container_type: Type of container relationship

    Yields:
        MetadataWorkUnit for container membership

    Examples:
        >>> dataset_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)"
        >>> parent_key = "db.schema"
        >>> list(add_table_to_schema_container(dataset_urn, parent_key))
        [MetadataWorkUnit(...)]
    """
    if not dataset_urn or not parent_container_key:
        raise ValueError("Both dataset_urn and parent_container_key are required")

    # Generate container URN from key
    container_urn = f"urn:li:container:{parent_container_key}"

    # Container membership aspect
    container_membership = {
        "containers": [container_urn]
    }

    yield MetadataWorkUnit(
        id=f"container-membership-{parent_container_key}-{hash(dataset_urn)}",
        mcp_raw={
            "entityUrn": dataset_urn,
            "aspect": container_membership,
            "aspectName": "container"
        }
    )

    logger.debug(f"Added dataset {dataset_urn} to container {container_urn}")


def gen_database_container(
    name: str,
    database: str,
    database_container_key: str,
    platform: str = "snowflake",
    platform_instance: Optional[str] = None,
    sub_types: Optional[List[str]] = None,
    domain_registry: Optional[DomainRegistry] = None,
    domain_config: Optional[Any] = None,
    external_url: Optional[str] = None,
    description: Optional[str] = None,
    created: Optional[int] = None,
    last_modified: Optional[int] = None,
    tags: Optional[List[str]] = None,
    structured_properties: Optional[Dict[str, str]] = None,
) -> Iterable[MetadataWorkUnit]:
    """
    Generate work units for a database container entity.

    Creates comprehensive metadata work units for database containers including
    properties, status, subtypes, tags, and domain assignments.

    Args:
        name: Display name of the database
        database: Database identifier
        database_container_key: Unique key for the database container
        platform: Data platform name (e.g., 'snowflake', 'postgres')
        platform_instance: Optional platform instance identifier
        sub_types: List of container subtypes (e.g., ['Database'])
        domain_registry: Optional domain registry for domain assignment
        domain_config: Optional domain configuration
        external_url: Optional external URL for the database
        description: Optional database description
        created: Optional creation timestamp (epoch millis)
        last_modified: Optional last modified timestamp (epoch millis)
        tags: Optional list of tag names
        structured_properties: Optional structured properties

    Yields:
        MetadataWorkUnit instances for database container
    """
    if not name or not database or not database_container_key:
        raise ValueError("name, database, and database_container_key are required")

    container_urn = f"urn:li:container:{database_container_key}"

    # Container properties aspect
    container_properties = {
        "customProperties": structured_properties or {},
        "name": name,
        "description": description,
        "externalUrl": external_url,
        "platform": f"urn:li:dataPlatform:{platform}",
        "platformInstance": platform_instance,
        "created": created,
        "lastModified": last_modified,
        "type": "DATABASE",
        "subTypes": sub_types or ["Database"],
    }

    # Remove None values
    container_properties = {k: v for k, v in container_properties.items() if v is not None}

    yield MetadataWorkUnit(
        id=f"container-properties-{database_container_key}",
        mcp_raw={
            "entityUrn": container_urn,
            "aspect": container_properties,
            "aspectName": "containerProperties"
        }
    )

    # Status aspect
    status_aspect = Status(removed=False)
    yield MetadataWorkUnit(
        id=f"container-status-{database_container_key}",
        mcp_raw={
            "entityUrn": container_urn,
            "aspect": status_aspect.to_dict(),
            "aspectName": "status"
        }
    )

    # SubTypes aspect
    if sub_types:
        subtypes_aspect = SubTypes(types=sub_types)
        yield MetadataWorkUnit(
            id=f"container-subtypes-{database_container_key}",
            mcp_raw={
                "entityUrn": container_urn,
                "aspect": subtypes_aspect.to_dict(),
                "aspectName": "subTypes"
            }
        )

    # Global tags aspect
    if tags:
        tag_associations = [
            TagAssociation(tag=f"urn:li:tag:{tag}")
            for tag in tags
        ]
        global_tags = GlobalTags(tags=tag_associations)
        yield MetadataWorkUnit(
            id=f"container-tags-{database_container_key}",
            mcp_raw={
                "entityUrn": container_urn,
                "aspect": global_tags.to_dict(),
                "aspectName": "globalTags"
            }
        )

    # Domain assignment if available
    if domain_registry and domain_config:
        yield from get_domain_wu(
            dataset_name=database,
            entity_urn=container_urn,
            domain_config=domain_config,
            domain_registry=domain_registry,
        )

    logger.debug(f"Generated database container work units for {database}")


def gen_schema_container(
    name: str,
    schema: str,
    database: str,
    database_container_key: str,
    schema_container_key: str,
    platform: str = "snowflake",
    platform_instance: Optional[str] = None,
    sub_types: Optional[List[str]] = None,
    domain_config: Optional[Any] = None,
    domain_registry: Optional[DomainRegistry] = None,
    external_url: Optional[str] = None,
    description: Optional[str] = None,
    created: Optional[int] = None,
    last_modified: Optional[int] = None,
    tags: Optional[List[str]] = None,
    structured_properties: Optional[Dict[str, str]] = None,
) -> Iterable[MetadataWorkUnit]:
    """
    Generate work units for a schema container entity.

    Creates comprehensive metadata work units for schema containers including
    properties, status, container relationships, and domain assignments.

    Args:
        name: Display name of the schema
        schema: Schema identifier
        database: Database name containing this schema
        database_container_key: Key of the parent database container
        schema_container_key: Unique key for the schema container
        platform: Data platform name
        platform_instance: Optional platform instance identifier
        sub_types: List of container subtypes (e.g., ['Schema'])
        domain_config: Optional domain configuration
        domain_registry: Optional domain registry for domain assignment
        external_url: Optional external URL for the schema
        description: Optional schema description
        created: Optional creation timestamp (epoch millis)
        last_modified: Optional last modified timestamp (epoch millis)
        tags: Optional list of tag names
        structured_properties: Optional structured properties

    Yields:
        MetadataWorkUnit instances for schema container
    """
    if not all([name, schema, database, database_container_key, schema_container_key]):
        raise ValueError("name, schema, database, database_container_key, and schema_container_key are required")

    container_urn = f"urn:li:container:{schema_container_key}"
    database_container_urn = f"urn:li:container:{database_container_key}"

    # Container properties aspect
    container_properties = {
        "customProperties": structured_properties or {},
        "name": name,
        "description": description,
        "externalUrl": external_url,
        "platform": f"urn:li:dataPlatform:{platform}",
        "platformInstance": platform_instance,
        "created": created,
        "lastModified": last_modified,
        "type": "SCHEMA",
        "subTypes": sub_types or ["Schema"],
        "qualifiedName": f"{database}.{schema}",
        "parentContainer": database_container_urn,
    }

    # Remove None values
    container_properties = {k: v for k, v in container_properties.items() if v is not None}

    yield MetadataWorkUnit(
        id=f"container-properties-{schema_container_key}",
        mcp_raw={
            "entityUrn": container_urn,
            "aspect": container_properties,
            "aspectName": "containerProperties"
        }
    )

    # Status aspect
    status_aspect = Status(removed=False)
    yield MetadataWorkUnit(
        id=f"container-status-{schema_container_key}",
        mcp_raw={
            "entityUrn": container_urn,
            "aspect": status_aspect.to_dict(),
            "aspectName": "status"
        }
    )

    # Container membership (schema belongs to database)
    container_membership = {
        "containers": [database_container_urn]
    }
    yield MetadataWorkUnit(
        id=f"container-membership-{schema_container_key}",
        mcp_raw={
            "entityUrn": container_urn,
            "aspect": container_membership,
            "aspectName": "container"
        }
    )

    # SubTypes aspect
    if sub_types:
        subtypes_aspect = SubTypes(types=sub_types)
        yield MetadataWorkUnit(
            id=f"container-subtypes-{schema_container_key}",
            mcp_raw={
                "entityUrn": container_urn,
                "aspect": subtypes_aspect.to_dict(),
                "aspectName": "subTypes"
            }
        )

    # Global tags aspect
    if tags:
        tag_associations = [
            TagAssociation(tag=f"urn:li:tag:{tag}")
            for tag in tags
        ]
        global_tags = GlobalTags(tags=tag_associations)
        yield MetadataWorkUnit(
            id=f"container-tags-{schema_container_key}",
            mcp_raw={
                "entityUrn": container_urn,
                "aspect": global_tags.to_dict(),
                "aspectName": "globalTags"
            }
        )

    # Domain assignment if available
    if domain_registry and domain_config:
        yield from get_domain_wu(
            dataset_name=f"{database}.{schema}",
            entity_urn=container_urn,
            domain_config=domain_config,
            domain_registry=domain_registry,
        )

    logger.debug(f"Generated schema container work units for {database}.{schema}")


def get_dataplatform_instance_aspect(
    dataset_urn: str,
    platform: str,
    platform_instance: Optional[str] = None,
) -> Optional[MetadataWorkUnit]:
    """
    Generate data platform instance aspect for a dataset.

    Creates a work unit that associates a dataset with a specific platform instance,
    enabling multi-instance platform support in DataGuild.

    Args:
        dataset_urn: URN of the dataset
        platform: Platform name (e.g., 'snowflake', 'postgres')
        platform_instance: Optional platform instance identifier

    Returns:
        MetadataWorkUnit for platform instance aspect or None if no platform_instance

    Examples:
        >>> dataset_urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)"
        >>> get_dataplatform_instance_aspect(dataset_urn, "snowflake", "production")
        MetadataWorkUnit(...)
    """
    if not dataset_urn or not platform:
        raise ValueError("dataset_urn and platform are required")

    if not platform_instance:
        return None

    # Data platform instance aspect
    dpi_aspect = {
        "platform": f"urn:li:dataPlatform:{platform}",
        "instance": platform_instance,
    }

    return MetadataWorkUnit(
        id=f"dataplatform-instance-{hash(dataset_urn)}-{platform_instance}",
        mcp_raw={
            "entityUrn": dataset_urn,
            "aspect": dpi_aspect,
            "aspectName": "dataPlatformInstance"
        }
    )


def get_domain_wu(
    dataset_name: str,
    entity_urn: str,
    domain_config: Optional[Any] = None,
    domain_registry: Optional[DomainRegistry] = None,
) -> Iterable[MetadataWorkUnit]:
    """
    Generate domain assignment work units for an entity.

    Assigns entities to domains based on configured domain rules and registry,
    enabling data governance and organization by business domain.

    Args:
        dataset_name: Name/identifier of the dataset
        entity_urn: URN of the entity to assign to domain
        domain_config: Domain configuration with assignment rules
        domain_registry: Domain registry for domain resolution

    Yields:
        MetadataWorkUnit for domain assignment

    Examples:
        >>> dataset_name = "analytics.sales.customers"
        >>> entity_urn = "urn:li:dataset:(...)"
        >>> list(get_domain_wu(dataset_name, entity_urn, domain_config, domain_registry))
        [MetadataWorkUnit(...)]
    """
    if not dataset_name or not entity_urn:
        raise ValueError("dataset_name and entity_urn are required")

    if not domain_config or not domain_registry:
        logger.debug("No domain config or registry provided, skipping domain assignment")
        return

    try:
        # Get domain for the dataset using the registry
        domain_urn = domain_registry.get_domain_urn_for_dataset(
            dataset_name=dataset_name,
            domain_config=domain_config
        )

        if not domain_urn:
            logger.debug(f"No domain found for dataset {dataset_name}")
            return

        # Domain assignment aspect
        domains_aspect = {
            "domains": [domain_urn]
        }

        yield MetadataWorkUnit(
            id=f"domain-assignment-{hash(entity_urn)}-{hash(domain_urn)}",
            mcp_raw={
                "entityUrn": entity_urn,
                "aspect": domains_aspect,
                "aspectName": "domains"
            }
        )

        logger.debug(f"Assigned entity {entity_urn} to domain {domain_urn}")

    except Exception as e:
        logger.warning(f"Failed to assign domain for dataset {dataset_name}: {e}")


# =============================================
# Existing Key Generation Functions
# =============================================

def gen_database_key(database_name: str) -> str:
    """
    Generate a standardized database key from the given database name.

    Normalizes the database name by:
    - Converting to lowercase
    - Replacing special characters with underscores
    - Removing leading/trailing underscores

    Args:
        database_name: The database name to normalize

    Returns:
        Normalized database key

    Raises:
        ValueError: If database_name is empty or None

    Examples:
        >>> gen_database_key('MyDatabase1')
        'mydatabase1'
        >>> gen_database_key('my-database@123')
        'my_database_123'
        >>> gen_database_key('TEST_DB')
        'test_db'
    """
    if not database_name or not isinstance(database_name, str):
        raise ValueError("Database name must be a non-empty string")

    # Normalize to lowercase and strip whitespace
    key = database_name.strip().lower()

    # Replace any sequence of non-alphanumeric characters with single underscore
    key = re.sub(r'[^a-z0-9]+', '_', key)

    # Remove leading/trailing underscores
    key = key.strip('_')

    # Ensure we have a valid key
    if not key:
        raise ValueError(f"Database name '{database_name}' results in empty key after normalization")

    return key


def gen_schema_key(database_name: str, schema_name: str) -> str:
    """
    Generate a standardized schema key from the database and schema names.

    Creates a qualified schema key in the format 'database_key.schema_key'
    where both parts are normalized using the same rules as gen_database_key.

    Args:
        database_name: The database name
        schema_name: The schema name

    Returns:
        Normalized schema key in format 'database.schema'

    Raises:
        ValueError: If database_name or schema_name is empty or None

    Examples:
        >>> gen_schema_key('MyDatabase1', 'Public-Schema')
        'mydatabase1.public_schema'
        >>> gen_schema_key('ANALYTICS_DB', 'sales.data')
        'analytics_db.sales_data'
    """
    if not database_name or not isinstance(database_name, str):
        raise ValueError("Database name must be a non-empty string")
    if not schema_name or not isinstance(schema_name, str):
        raise ValueError("Schema name must be a non-empty string")

    # Generate normalized database key
    db_key = gen_database_key(database_name)

    # Generate normalized schema key using same logic
    schema_key = schema_name.strip().lower()
    schema_key = re.sub(r'[^a-z0-9]+', '_', schema_key)
    schema_key = schema_key.strip('_')

    if not schema_key:
        raise ValueError(f"Schema name '{schema_name}' results in empty key after normalization")

    return f"{db_key}.{schema_key}"


def gen_table_key(database_name: str, schema_name: str, table_name: str) -> str:
    """
    Generate a standardized table key from database, schema, and table names.

    Args:
        database_name: The database name
        schema_name: The schema name
        table_name: The table name

    Returns:
        Normalized table key in format 'database.schema.table'

    Examples:
        >>> gen_table_key('MyDB', 'public', 'customers')
        'mydb.public.customers'
    """
    if not table_name or not isinstance(table_name, str):
        raise ValueError("Table name must be a non-empty string")

    # Get the schema key first
    schema_key = gen_schema_key(database_name, schema_name)

    # Normalize table name
    table_key = table_name.strip().lower()
    table_key = re.sub(r'[^a-z0-9]+', '_', table_key)
    table_key = table_key.strip('_')

    if not table_key:
        raise ValueError(f"Table name '{table_name}' results in empty key after normalization")

    return f"{schema_key}.{table_key}"


# =============================================
# Identifier Utilities
# =============================================

def normalize_identifier(identifier: str) -> str:
    """
    Normalize a SQL identifier (database, schema, table, or column name).

    Args:
        identifier: The identifier to normalize

    Returns:
        Normalized identifier
    """
    if not identifier or not isinstance(identifier, str):
        raise ValueError("Identifier must be a non-empty string")

    # Remove quotes if present
    identifier = identifier.strip('"\'`[]')

    # Normalize to lowercase
    normalized = identifier.strip().lower()

    # Replace special characters with underscores
    normalized = re.sub(r'[^a-z0-9_]', '_', normalized)

    # Remove multiple consecutive underscores
    normalized = re.sub(r'_+', '_', normalized)

    # Remove leading/trailing underscores
    normalized = normalized.strip('_')

    return normalized


def quote_identifier(identifier: str, quote_char: str = '"') -> str:
    """
    Quote a SQL identifier if it contains special characters or keywords.

    Args:
        identifier: The identifier to quote
        quote_char: The quote character to use (default: double quote)

    Returns:
        Quoted identifier if necessary, otherwise original identifier
    """
    if not identifier:
        return identifier

    # Check if identifier needs quoting
    needs_quoting = (
            not identifier.isidentifier() or
            identifier.upper() in SQL_RESERVED_KEYWORDS or
            not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier)
    )

    if needs_quoting:
        # Escape any existing quote characters
        escaped = identifier.replace(quote_char, quote_char + quote_char)
        return f"{quote_char}{escaped}{quote_char}"

    return identifier


def parse_qualified_name(qualified_name: str) -> Tuple[Optional[str], Optional[str], str]:
    """
    Parse a qualified name into its components.

    Args:
        qualified_name: Fully qualified name (e.g., 'db.schema.table')

    Returns:
        Tuple of (database, schema, table) where database and schema may be None

    Examples:
        >>> parse_qualified_name('mydb.public.customers')
        ('mydb', 'public', 'customers')
        >>> parse_qualified_name('public.customers')
        (None, 'public', 'customers')
        >>> parse_qualified_name('customers')
        (None, None, 'customers')
    """
    if not qualified_name:
        raise ValueError("Qualified name cannot be empty")

    parts = qualified_name.split('.')

    if len(parts) == 1:
        return None, None, parts[0]
    elif len(parts) == 2:
        return None, parts[0], parts[1]
    elif len(parts) == 3:
        return parts[0], parts[1], parts[2]
    else:
        # Handle more than 3 parts by treating first as database,
        # second as schema, and joining rest as table name
        return parts[0], parts[1], '.'.join(parts[2:])


def build_qualified_name(
        table_name: str,
        schema_name: Optional[str] = None,
        database_name: Optional[str] = None
) -> str:
    """
    Build a qualified name from components.

    Args:
        table_name: The table name
        schema_name: Optional schema name
        database_name: Optional database name

    Returns:
        Qualified name string
    """
    if not table_name:
        raise ValueError("Table name is required")

    parts = []
    if database_name:
        parts.append(database_name)
    if schema_name:
        parts.append(schema_name)
    parts.append(table_name)

    return '.'.join(parts)


# =============================================
# SQL Utilities
# =============================================

def escape_sql_string(value: str) -> str:
    """
    Escape a string for safe use in SQL queries.

    Args:
        value: String to escape

    Returns:
        Escaped string
    """
    if value is None:
        return 'NULL'

    # Escape single quotes by doubling them
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def format_sql_value(value: Any) -> str:
    """
    Format a Python value for use in SQL queries.

    Args:
        value: Value to format

    Returns:
        SQL-formatted value
    """
    if value is None:
        return 'NULL'
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return escape_sql_string(value)
    else:
        return escape_sql_string(str(value))


def clean_sql_query(query: str) -> str:
    """
    Clean and normalize a SQL query.

    Args:
        query: SQL query string

    Returns:
        Cleaned query string
    """
    if not query:
        return ""

    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', query.strip())

    # Remove comments
    cleaned = re.sub(r'--.*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

    # Remove extra whitespace again after comment removal
    cleaned = re.sub(r'\s+', ' ', cleaned.strip())

    return cleaned


def is_valid_identifier(identifier: str) -> bool:
    """
    Check if a string is a valid SQL identifier.

    Args:
        identifier: String to validate

    Returns:
        True if valid identifier, False otherwise
    """
    if not identifier:
        return False

    # Check if it matches basic identifier pattern
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        return False

    # Check if it's a reserved keyword
    if identifier.upper() in SQL_RESERVED_KEYWORDS:
        return False

    return True


# =============================================
# Platform Utilities
# =============================================

def get_platform_from_url(connection_url: str) -> Optional[str]:
    """
    Extract platform/database type from connection URL.

    Args:
        connection_url: Database connection URL

    Returns:
        Platform name or None if not recognized
    """
    if not connection_url:
        return None

    url_lower = connection_url.lower()

    if 'snowflake' in url_lower:
        return 'snowflake'
    elif 'bigquery' in url_lower or 'googleapis.com' in url_lower:
        return 'bigquery'
    elif 'redshift' in url_lower:
        return 'redshift'
    elif 'postgresql' in url_lower or url_lower.startswith('postgres'):
        return 'postgres'
    elif 'mysql' in url_lower:
        return 'mysql'
    elif 'oracle' in url_lower:
        return 'oracle'
    elif 'sqlserver' in url_lower or 'mssql' in url_lower:
        return 'mssql'
    elif 'databricks' in url_lower:
        return 'databricks'
    else:
        return None


def get_quote_char(platform: str) -> str:
    """Get the appropriate quote character for a platform."""
    return PLATFORM_QUOTE_CHARS.get(platform.lower(), '"')


def quote_identifier_for_platform(identifier: str, platform: str) -> str:
    """Quote an identifier using platform-specific rules."""
    quote_char = get_quote_char(platform)

    # Special handling for SQL Server brackets
    if platform.lower() == 'mssql' and quote_char == '[':
        if not identifier.isidentifier() or identifier.upper() in SQL_RESERVED_KEYWORDS:
            escaped = identifier.replace(']', ']]')
            return f"[{escaped}]"
        return identifier

    return quote_identifier(identifier, quote_char)


# =============================================
# Query Generation Utilities
# =============================================

def generate_select_query(
        table_name: str,
        columns: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        limit: Optional[int] = None
) -> str:
    """
    Generate a simple SELECT query.

    Args:
        table_name: Table to query
        columns: Columns to select (default: *)
        where_clause: Optional WHERE clause
        limit: Optional LIMIT value

    Returns:
        Generated SQL query
    """
    if not table_name:
        raise ValueError("Table name is required")

    # Build column list
    if columns:
        column_list = ', '.join(columns)
    else:
        column_list = '*'

    # Build query
    query_parts = [f"SELECT {column_list}", f"FROM {table_name}"]

    if where_clause:
        query_parts.append(f"WHERE {where_clause}")

    if limit is not None:
        query_parts.append(f"LIMIT {limit}")

    return ' '.join(query_parts)


def generate_count_query(table_name: str, where_clause: Optional[str] = None) -> str:
    """
    Generate a COUNT query.

    Args:
        table_name: Table to count
        where_clause: Optional WHERE clause

    Returns:
        Generated COUNT query
    """
    query_parts = [f"SELECT COUNT(*) FROM {table_name}"]

    if where_clause:
        query_parts.append(f"WHERE {where_clause}")

    return ' '.join(query_parts)


# =============================================
# Constants and Configuration
# =============================================

# SQL Reserved Keywords (subset of common ones)
SQL_RESERVED_KEYWORDS = {
    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER',
    'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'ON',
    'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC', 'LIMIT', 'OFFSET',
    'UNION', 'ALL', 'DISTINCT', 'AS', 'AND', 'OR', 'NOT', 'IN', 'EXISTS',
    'BETWEEN', 'LIKE', 'IS', 'NULL', 'TRUE', 'FALSE', 'CASE', 'WHEN',
    'THEN', 'ELSE', 'END', 'IF', 'COALESCE', 'CAST', 'CONVERT',
    'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'SUBSTRING', 'TRIM', 'UPPER',
    'LOWER', 'LENGTH', 'ROUND', 'ABS', 'CURRENT_DATE', 'CURRENT_TIME',
    'CURRENT_TIMESTAMP', 'NOW', 'TODAY', 'YEAR', 'MONTH', 'DAY'
}

# Platform-specific identifier quoting
PLATFORM_QUOTE_CHARS = {
    'snowflake': '"',
    'bigquery': '`',
    'redshift': '"',
    'postgres': '"',
    'mysql': '`',
    'mssql': '[',  # Uses [identifier]
    'oracle': '"',
    'databricks': '`'
}


# Export all functions
__all__ = [
    # ✅ NEW: Container and domain management functions
    'add_table_to_schema_container',
    'gen_database_container',
    'gen_schema_container',
    'get_dataplatform_instance_aspect',
    'get_domain_wu',

    # Key generation functions
    'gen_database_key',
    'gen_schema_key',
    'gen_table_key',

    # Identifier utilities
    'normalize_identifier',
    'quote_identifier',
    'quote_identifier_for_platform',
    'is_valid_identifier',

    # Name parsing and building
    'parse_qualified_name',
    'build_qualified_name',

    # SQL utilities
    'escape_sql_string',
    'format_sql_value',
    'clean_sql_query',

    # Platform utilities
    'get_platform_from_url',
    'get_quote_char',

    # Query generation
    'generate_select_query',
    'generate_count_query',

    # Constants
    'SQL_RESERVED_KEYWORDS',
    'PLATFORM_QUOTE_CHARS',
]
