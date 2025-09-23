"""
DataGuild SQL parsing common utilities and constants.

This module provides common data structures, enums, and utilities used
across DataGuild's SQL parsing and analysis components for consistent
query classification and processing.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """
    Enumeration of SQL query types for classification and processing.

    This enum provides comprehensive classification of SQL query types
    to support lineage extraction, usage analysis, and operational
    metadata generation across different data platforms.
    """

    # Unknown or unclassified queries
    UNKNOWN = "UNKNOWN"

    # Data Query Language (DQL) - Read operations
    SELECT = "SELECT"
    WITH = "WITH"  # Common Table Expressions

    # Data Manipulation Language (DML) - Write operations
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    MERGE = "MERGE"
    UPSERT = "UPSERT"

    # Data Definition Language (DDL) - Schema operations
    CREATE_TABLE = "CREATE_TABLE"
    CREATE_VIEW = "CREATE_VIEW"
    CREATE_MATERIALIZED_VIEW = "CREATE_MATERIALIZED_VIEW"
    CREATE_SCHEMA = "CREATE_SCHEMA"
    CREATE_DATABASE = "CREATE_DATABASE"
    CREATE_INDEX = "CREATE_INDEX"
    CREATE_FUNCTION = "CREATE_FUNCTION"
    CREATE_PROCEDURE = "CREATE_PROCEDURE"

    ALTER_TABLE = "ALTER_TABLE"
    ALTER_VIEW = "ALTER_VIEW"
    ALTER_SCHEMA = "ALTER_SCHEMA"
    ALTER_DATABASE = "ALTER_DATABASE"

    DROP_TABLE = "DROP_TABLE"
    DROP_VIEW = "DROP_VIEW"
    DROP_SCHEMA = "DROP_SCHEMA"
    DROP_DATABASE = "DROP_DATABASE"
    DROP_INDEX = "DROP_INDEX"
    DROP_FUNCTION = "DROP_FUNCTION"
    DROP_PROCEDURE = "DROP_PROCEDURE"

    TRUNCATE_TABLE = "TRUNCATE_TABLE"
    RENAME_TABLE = "RENAME_TABLE"

    # Special CREATE operations that combine DDL and DML
    CREATE_TABLE_AS_SELECT = "CREATE_TABLE_AS_SELECT"  # CTAS
    CREATE_VIEW_AS_SELECT = "CREATE_VIEW_AS_SELECT"  # CVAS

    # Data Control Language (DCL) - Security operations
    GRANT = "GRANT"
    REVOKE = "REVOKE"

    # Transaction Control Language (TCL)
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"
    SAVEPOINT = "SAVEPOINT"

    # Platform-specific operations
    COPY = "COPY"  # Snowflake, Redshift data loading
    LOAD = "LOAD"  # BigQuery, Spark data loading
    EXPORT = "EXPORT"  # Data export operations

    # Utility and maintenance operations
    ANALYZE = "ANALYZE"  # Statistics gathering
    VACUUM = "VACUUM"  # Table maintenance
    DESCRIBE = "DESCRIBE"  # Schema introspection
    SHOW = "SHOW"  # Metadata queries
    EXPLAIN = "EXPLAIN"  # Query plan analysis

    # Stored procedure and function calls
    CALL = "CALL"
    EXECUTE = "EXECUTE"

    # Temporary table operations
    CREATE_TEMP_TABLE = "CREATE_TEMP_TABLE"
    CREATE_TEMPORARY_VIEW = "CREATE_TEMPORARY_VIEW"

    def __str__(self) -> str:
        """String representation of the query type."""
        return self.value

    def is_read_operation(self) -> bool:
        """Check if this is a read-only operation."""
        read_operations = {
            QueryType.SELECT,
            QueryType.WITH,
            QueryType.DESCRIBE,
            QueryType.SHOW,
            QueryType.EXPLAIN,
        }
        return self in read_operations

    def is_write_operation(self) -> bool:
        """Check if this is a write operation that modifies data."""
        write_operations = {
            QueryType.INSERT,
            QueryType.UPDATE,
            QueryType.DELETE,
            QueryType.MERGE,
            QueryType.UPSERT,
            QueryType.COPY,
            QueryType.LOAD,
        }
        return self in write_operations

    def is_ddl_operation(self) -> bool:
        """Check if this is a DDL operation that modifies schema."""
        ddl_operations = {
            QueryType.CREATE_TABLE,
            QueryType.CREATE_VIEW,
            QueryType.CREATE_MATERIALIZED_VIEW,
            QueryType.CREATE_SCHEMA,
            QueryType.CREATE_DATABASE,
            QueryType.CREATE_INDEX,
            QueryType.CREATE_FUNCTION,
            QueryType.CREATE_PROCEDURE,
            QueryType.ALTER_TABLE,
            QueryType.ALTER_VIEW,
            QueryType.ALTER_SCHEMA,
            QueryType.ALTER_DATABASE,
            QueryType.DROP_TABLE,
            QueryType.DROP_VIEW,
            QueryType.DROP_SCHEMA,
            QueryType.DROP_DATABASE,
            QueryType.DROP_INDEX,
            QueryType.DROP_FUNCTION,
            QueryType.DROP_PROCEDURE,
            QueryType.TRUNCATE_TABLE,
            QueryType.RENAME_TABLE,
            QueryType.CREATE_TABLE_AS_SELECT,
            QueryType.CREATE_VIEW_AS_SELECT,
            QueryType.CREATE_TEMP_TABLE,
            QueryType.CREATE_TEMPORARY_VIEW,
        }
        return self in ddl_operations

    def is_create_operation(self) -> bool:
        """Check if this is a CREATE operation."""
        return self.value.startswith("CREATE")

    def is_drop_operation(self) -> bool:
        """Check if this is a DROP operation."""
        return self.value.startswith("DROP")

    def is_alter_operation(self) -> bool:
        """Check if this is an ALTER operation."""
        return self.value.startswith("ALTER")

    def creates_lineage(self) -> bool:
        """Check if this query type typically creates lineage relationships."""
        lineage_creating_operations = {
            QueryType.INSERT,
            QueryType.UPDATE,
            QueryType.CREATE_TABLE_AS_SELECT,
            QueryType.CREATE_VIEW,
            QueryType.CREATE_VIEW_AS_SELECT,
            QueryType.CREATE_MATERIALIZED_VIEW,
            QueryType.MERGE,
            QueryType.COPY,
            QueryType.LOAD,
        }
        return self in lineage_creating_operations

    def affects_usage_stats(self) -> bool:
        """Check if this query type should be included in usage statistics."""
        usage_affecting_operations = {
            QueryType.SELECT,
            QueryType.WITH,
            QueryType.INSERT,
            QueryType.UPDATE,
            QueryType.DELETE,
            QueryType.MERGE,
            QueryType.CREATE_TABLE_AS_SELECT,
            QueryType.CREATE_VIEW_AS_SELECT,
        }
        return self in usage_affecting_operations

    @classmethod
    def from_sql_text(cls, sql_text: str) -> "QueryType":
        """
        Attempt to determine query type from SQL text.

        Args:
            sql_text: Raw SQL query text

        Returns:
            QueryType enum value, UNKNOWN if cannot be determined
        """
        if not sql_text or not sql_text.strip():
            return cls.UNKNOWN

        # Normalize SQL text
        normalized_sql = sql_text.strip().upper()

        # Remove comments and leading whitespace
        lines = []
        for line in normalized_sql.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                lines.append(line)

        if not lines:
            return cls.UNKNOWN

        first_statement = ' '.join(lines)

        # Extract first meaningful keyword(s)
        tokens = first_statement.split()
        if not tokens:
            return cls.UNKNOWN

        first_token = tokens[0]
        second_token = tokens[1] if len(tokens) > 1 else ""
        third_token = tokens[2] if len(tokens) > 2 else ""

        # Map SQL keywords to query types
        if first_token == "SELECT":
            return cls.SELECT
        elif first_token == "WITH":
            return cls.WITH
        elif first_token == "INSERT":
            return cls.INSERT
        elif first_token == "UPDATE":
            return cls.UPDATE
        elif first_token == "DELETE":
            return cls.DELETE
        elif first_token == "MERGE":
            return cls.MERGE
        elif first_token == "CREATE":
            if second_token == "TABLE":
                if "AS" in tokens and "SELECT" in tokens:
                    return cls.CREATE_TABLE_AS_SELECT
                elif "TEMPORARY" in tokens or "TEMP" in tokens:
                    return cls.CREATE_TEMP_TABLE
                else:
                    return cls.CREATE_TABLE
            elif second_token == "VIEW":
                if "TEMPORARY" in tokens or "TEMP" in tokens:
                    return cls.CREATE_TEMPORARY_VIEW
                else:
                    return cls.CREATE_VIEW
            elif second_token == "MATERIALIZED" and third_token == "VIEW":
                return cls.CREATE_MATERIALIZED_VIEW
            elif second_token == "SCHEMA":
                return cls.CREATE_SCHEMA
            elif second_token == "DATABASE":
                return cls.CREATE_DATABASE
            elif second_token == "INDEX":
                return cls.CREATE_INDEX
            elif second_token == "FUNCTION":
                return cls.CREATE_FUNCTION
            elif second_token == "PROCEDURE":
                return cls.CREATE_PROCEDURE
            else:
                return cls.UNKNOWN
        elif first_token == "ALTER":
            if second_token == "TABLE":
                return cls.ALTER_TABLE
            elif second_token == "VIEW":
                return cls.ALTER_VIEW
            elif second_token == "SCHEMA":
                return cls.ALTER_SCHEMA
            elif second_token == "DATABASE":
                return cls.ALTER_DATABASE
            else:
                return cls.UNKNOWN
        elif first_token == "DROP":
            if second_token == "TABLE":
                return cls.DROP_TABLE
            elif second_token == "VIEW":
                return cls.DROP_VIEW
            elif second_token == "SCHEMA":
                return cls.DROP_SCHEMA
            elif second_token == "DATABASE":
                return cls.DROP_DATABASE
            elif second_token == "INDEX":
                return cls.DROP_INDEX
            elif second_token == "FUNCTION":
                return cls.DROP_FUNCTION
            elif second_token == "PROCEDURE":
                return cls.DROP_PROCEDURE
            else:
                return cls.UNKNOWN
        elif first_token == "TRUNCATE":
            return cls.TRUNCATE_TABLE
        elif first_token == "COPY":
            return cls.COPY
        elif first_token == "LOAD":
            return cls.LOAD
        elif first_token == "GRANT":
            return cls.GRANT
        elif first_token == "REVOKE":
            return cls.REVOKE
        elif first_token == "CALL":
            return cls.CALL
        elif first_token == "EXECUTE":
            return cls.EXECUTE
        elif first_token == "DESCRIBE" or first_token == "DESC":
            return cls.DESCRIBE
        elif first_token == "SHOW":
            return cls.SHOW
        elif first_token == "EXPLAIN":
            return cls.EXPLAIN
        elif first_token == "ANALYZE" or first_token == "ANALYSE":
            return cls.ANALYZE
        elif first_token == "VACUUM":
            return cls.VACUUM
        else:
            return cls.UNKNOWN


# Query type categories for grouping and analysis
QUERY_TYPE_CATEGORIES = {
    "READ_OPERATIONS": {
        QueryType.SELECT,
        QueryType.WITH,
        QueryType.DESCRIBE,
        QueryType.SHOW,
        QueryType.EXPLAIN,
    },
    "WRITE_OPERATIONS": {
        QueryType.INSERT,
        QueryType.UPDATE,
        QueryType.DELETE,
        QueryType.MERGE,
        QueryType.UPSERT,
        QueryType.COPY,
        QueryType.LOAD,
    },
    "DDL_OPERATIONS": {
        QueryType.CREATE_TABLE,
        QueryType.CREATE_VIEW,
        QueryType.CREATE_MATERIALIZED_VIEW,
        QueryType.ALTER_TABLE,
        QueryType.ALTER_VIEW,
        QueryType.DROP_TABLE,
        QueryType.DROP_VIEW,
        QueryType.TRUNCATE_TABLE,
        QueryType.RENAME_TABLE,
    },
    "HYBRID_OPERATIONS": {
        QueryType.CREATE_TABLE_AS_SELECT,
        QueryType.CREATE_VIEW_AS_SELECT,
    },
    "MAINTENANCE_OPERATIONS": {
        QueryType.ANALYZE,
        QueryType.VACUUM,
    },
    "SECURITY_OPERATIONS": {
        QueryType.GRANT,
        QueryType.REVOKE,
    }
}

# Platform-specific query type mappings
PLATFORM_QUERY_TYPE_MAPPINGS = {
    "snowflake": {
        "COPY": QueryType.COPY,
        "COPY INTO": QueryType.COPY,
        "CREATE OR REPLACE": QueryType.CREATE_TABLE,  # Snowflake-specific syntax
    },
    "bigquery": {
        "LOAD DATA": QueryType.LOAD,
        "EXPORT DATA": QueryType.EXPORT,
    },
    "databricks": {
        "OPTIMIZE": QueryType.ANALYZE,
        "DELTA": QueryType.UPDATE,  # Delta Lake operations
    },
    "redshift": {
        "COPY": QueryType.COPY,
        "UNLOAD": QueryType.EXPORT,
    }
}


def get_query_types_by_category(category: str) -> Set[QueryType]:
    """
    Get query types belonging to a specific category.

    Args:
        category: Category name from QUERY_TYPE_CATEGORIES

    Returns:
        Set of QueryType enum values in that category
    """
    return QUERY_TYPE_CATEGORIES.get(category, set())


def is_query_type_in_category(query_type: QueryType, category: str) -> bool:
    """
    Check if a query type belongs to a specific category.

    Args:
        query_type: QueryType to check
        category: Category name to check against

    Returns:
        True if query type is in the category
    """
    category_types = get_query_types_by_category(category)
    return query_type in category_types


def get_platform_specific_query_type(
        platform: str,
        query_keyword: str
) -> Optional[QueryType]:
    """
    Get platform-specific query type mapping.

    Args:
        platform: Data platform name (e.g., 'snowflake', 'bigquery')
        query_keyword: SQL keyword or phrase

    Returns:
        QueryType if mapping exists, None otherwise
    """
    platform_mappings = PLATFORM_QUERY_TYPE_MAPPINGS.get(platform.lower(), {})
    return platform_mappings.get(query_keyword.upper())


def classify_query_impact(query_type: QueryType) -> Dict[str, bool]:
    """
    Classify the impact of a query type on different aspects.

    Args:
        query_type: QueryType to classify

    Returns:
        Dictionary with impact classifications
    """
    return {
        "creates_lineage": query_type.creates_lineage(),
        "affects_usage": query_type.affects_usage_stats(),
        "modifies_data": query_type.is_write_operation(),
        "modifies_schema": query_type.is_ddl_operation(),
        "read_only": query_type.is_read_operation(),
    }


# Export all classes and functions
__all__ = [
    'QueryType',
    'QUERY_TYPE_CATEGORIES',
    'PLATFORM_QUERY_TYPE_MAPPINGS',
    'get_query_types_by_category',
    'is_query_type_in_category',
    'get_platform_specific_query_type',
    'classify_query_impact',
]

# Example usage and testing
if __name__ == "__main__":
    # Example usage of QueryType enum
    print("=== DataGuild QueryType Examples ===\n")

    # Example 1: Query type classification
    sample_queries = [
        "SELECT * FROM users",
        "INSERT INTO orders (user_id, amount) VALUES (1, 100)",
        "CREATE TABLE analytics.user_summary AS SELECT * FROM users",
        "DROP TABLE temp_staging",
        "MERGE INTO target USING source ON target.id = source.id",
    ]

    for query in sample_queries:
        query_type = QueryType.from_sql_text(query)
        impact = classify_query_impact(query_type)

        print(f"Query: {query}")
        print(f"Type: {query_type}")
        print(f"Impact: {impact}")
        print()

    # Example 2: Category analysis
    print("Query type categories:")
    for category, types in QUERY_TYPE_CATEGORIES.items():
        print(f"{category}: {len(types)} types")
        for qt in sorted(types, key=lambda x: x.value):
            print(f"  - {qt}")
        print()
