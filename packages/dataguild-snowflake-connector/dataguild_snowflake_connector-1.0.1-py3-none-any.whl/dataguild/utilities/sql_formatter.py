"""
DataGuild SQL formatting utilities.

This module provides comprehensive SQL formatting and manipulation utilities
for query processing, logging, and display purposes in DataGuild ingestion pipelines.
"""

import logging
import re
from typing import List, Optional, Union

logger = logging.getLogger(__name__)

# SQL keyword patterns for formatting
SQL_KEYWORDS = {
    "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "JOIN",
    "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN", "FULL JOIN",
    "ON", "AS", "AND", "OR", "IN", "EXISTS", "UNION", "INTERSECT", "EXCEPT",
    "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "WITH", "CASE",
    "WHEN", "THEN", "ELSE", "END", "LIMIT", "OFFSET", "DISTINCT", "ALL"
}

# SQL comment patterns
COMMENT_PATTERNS = [
    re.compile(r'--[^\n]*'),  # Single line comments
    re.compile(r'/\*.*?\*/', re.DOTALL),  # Multi-line comments
]


def trim_query(
        query: str,
        budget: int,
        placeholder: str = "...",
        preserve_newlines: bool = False,
        word_boundary: bool = True,
) -> str:
    """
    Trim a SQL query string to fit within the specified character budget.

    This function intelligently trims SQL queries while maintaining readability
    and avoiding cuts in the middle of SQL tokens when possible.

    Args:
        query: The original SQL query string to trim
        budget: The maximum allowed length of the returned string
        placeholder: String to append when query is truncated (default: "...")
        preserve_newlines: Whether to preserve line breaks in the output
        word_boundary: Whether to respect word boundaries when trimming

    Returns:
        The trimmed and optionally formatted SQL query string

    Examples:
        >>> trim_query("SELECT * FROM users WHERE id = 1", 20)
        'SELECT * FROM users...'

        >>> trim_query("SELECT\\n  *\\nFROM users", 15, preserve_newlines=True)
        'SELECT\\n  *\\nFROM...'
    """
    if not query:
        return ""

    # Handle empty or whitespace-only queries
    if not query.strip():
        return ""

    # Normalize whitespace unless preserving newlines
    if not preserve_newlines:
        # Replace multiple whitespace characters with single space
        normalized_query = re.sub(r'\s+', ' ', query.strip())
    else:
        # Just strip leading/trailing whitespace but preserve internal structure
        normalized_query = query.strip()

    # If query already fits within budget, return as-is
    if len(normalized_query) <= budget:
        return normalized_query

    # Account for placeholder length in budget
    effective_budget = max(1, budget - len(placeholder))

    # Trim to effective budget
    trimmed = normalized_query[:effective_budget]

    # Try to respect word boundaries if requested
    if word_boundary and ' ' in trimmed:
        # Find the last space to avoid cutting words
        last_space = trimmed.rfind(' ')

        # Only use word boundary if it doesn't cut too much
        # (at least half the budget should be preserved)
        if last_space > effective_budget // 2:
            trimmed = trimmed[:last_space].rstrip()

    return trimmed + placeholder


def clean_query(query: str, remove_comments: bool = True, normalize_whitespace: bool = True) -> str:
    """
    Clean and normalize a SQL query string.

    Args:
        query: The SQL query string to clean
        remove_comments: Whether to remove SQL comments
        normalize_whitespace: Whether to normalize whitespace characters

    Returns:
        Cleaned SQL query string

    Examples:
        >>> clean_query("SELECT * FROM users -- Get all users")
        'SELECT * FROM users'

        >>> clean_query("SELECT\\n  *\\n  FROM    users")
        'SELECT * FROM users'
    """
    if not query:
        return ""

    cleaned = query

    # Remove comments if requested
    if remove_comments:
        for pattern in COMMENT_PATTERNS:
            cleaned = pattern.sub('', cleaned)

    # Normalize whitespace if requested
    if normalize_whitespace:
        # Replace multiple whitespace characters with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()

    return cleaned


def format_query_for_logging(
        query: str,
        max_length: int = 200,
        single_line: bool = True,
        include_ellipsis: bool = True,
) -> str:
    """
    Format a SQL query for logging purposes.

    Args:
        query: The SQL query to format
        max_length: Maximum length for the formatted query
        single_line: Whether to format as a single line
        include_ellipsis: Whether to add ellipsis when truncated

    Returns:
        Formatted query string suitable for logging

    Examples:
        >>> format_query_for_logging("SELECT * FROM users WHERE active = 1")
        'SELECT * FROM users WHERE active = 1'

        >>> format_query_for_logging("SELECT * FROM users WHERE active = 1" * 10, 50)
        'SELECT * FROM users WHERE active = 1SELECT * ...'
    """
    if not query:
        return ""

    # Clean the query first
    formatted = clean_query(query, remove_comments=True, normalize_whitespace=single_line)

    # Trim if necessary
    if len(formatted) > max_length:
        placeholder = "..." if include_ellipsis else ""
        formatted = trim_query(
            formatted,
            max_length,
            placeholder=placeholder,
            preserve_newlines=not single_line
        )

    return formatted


def extract_table_names(query: str) -> List[str]:
    """
    Extract table names from a SQL query using simple pattern matching.

    Note: This is a basic implementation that works for simple queries.
    For complex queries, consider using a proper SQL parser.

    Args:
        query: SQL query string

    Returns:
        List of table names found in the query

    Examples:
        >>> extract_table_names("SELECT * FROM users JOIN orders ON users.id = orders.user_id")
        ['users', 'orders']
    """
    if not query:
        return []

    # Clean the query first
    cleaned = clean_query(query, remove_comments=True, normalize_whitespace=True)

    # Simple pattern to find table names after FROM, JOIN, INTO, UPDATE
    table_patterns = [
        r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
        r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
        r'\bINTO\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
        r'\bUPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
    ]

    table_names = set()

    for pattern in table_patterns:
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        for match in matches:
            # Handle qualified names (schema.table)
            table_name = match.split('.')[-1]  # Get the table name part
            if table_name and not table_name.upper() in SQL_KEYWORDS:
                table_names.add(table_name)

    return sorted(list(table_names))


def mask_sensitive_data(
        query: str,
        mask_values: bool = True,
        mask_char: str = "*",
        preserve_structure: bool = True,
) -> str:
    """
    Mask sensitive data in SQL queries for logging or display.

    Args:
        query: SQL query string to mask
        mask_values: Whether to mask string and numeric literals
        mask_char: Character to use for masking
        preserve_structure: Whether to preserve the original structure/length

    Returns:
        SQL query with sensitive data masked

    Examples:
        >>> mask_sensitive_data("SELECT * FROM users WHERE name = 'John' AND age = 25")
        "SELECT * FROM users WHERE name = '****' AND age = **"
    """
    if not query:
        return ""

    masked = query

    if mask_values:
        # Mask string literals
        def mask_string(match):
            original = match.group(0)
            quote_char = original[0]  # ' or "
            content = original[1:-1]  # Remove quotes

            if preserve_structure:
                # Replace with same length of mask characters
                masked_content = mask_char * len(content)
            else:
                # Use fixed length mask
                masked_content = mask_char * 4

            return f"{quote_char}{masked_content}{quote_char}"

        # Mask quoted strings
        masked = re.sub(r"'[^']*'", mask_string, masked)
        masked = re.sub(r'"[^"]*"', mask_string, masked)

        # Mask numeric literals
        def mask_number(match):
            original = match.group(0)
            if preserve_structure:
                # Replace digits with mask character, preserve structure
                return re.sub(r'\d', mask_char, original)
            else:
                return mask_char * 2

        # Mask numbers (including decimals)
        masked = re.sub(r'\b\d+(?:\.\d+)?\b', mask_number, masked)

    return masked


def split_sql_statements(sql_text: str) -> List[str]:
    """
    Split a SQL text containing multiple statements into individual statements.

    Args:
        sql_text: Text containing one or more SQL statements

    Returns:
        List of individual SQL statements

    Examples:
        >>> split_sql_statements("SELECT 1; SELECT 2; SELECT 3;")
        ['SELECT 1', 'SELECT 2', 'SELECT 3']
    """
    if not sql_text:
        return []

    # Simple split by semicolon (doesn't handle semicolons in strings perfectly)
    # For production use, consider a proper SQL parser
    statements = []

    # Remove comments first
    cleaned = clean_query(sql_text, remove_comments=True, normalize_whitespace=False)

    # Split by semicolon
    parts = cleaned.split(';')

    for part in parts:
        statement = part.strip()
        if statement:  # Skip empty statements
            statements.append(statement)

    return statements


def is_select_query(query: str) -> bool:
    """
    Check if a query is a SELECT statement.

    Args:
        query: SQL query string

    Returns:
        True if the query is a SELECT statement, False otherwise

    Examples:
        >>> is_select_query("SELECT * FROM users")
        True

        >>> is_select_query("INSERT INTO users VALUES (1, 'John')")
        False
    """
    if not query:
        return False

    cleaned = clean_query(query, remove_comments=True, normalize_whitespace=True)
    return cleaned.upper().strip().startswith('SELECT')


def is_dml_query(query: str) -> bool:
    """
    Check if a query is a DML (Data Manipulation Language) statement.

    Args:
        query: SQL query string

    Returns:
        True if the query is INSERT, UPDATE, DELETE, or MERGE

    Examples:
        >>> is_dml_query("INSERT INTO users VALUES (1, 'John')")
        True

        >>> is_dml_query("CREATE TABLE users (id INT)")
        False
    """
    if not query:
        return False

    cleaned = clean_query(query, remove_comments=True, normalize_whitespace=True)
    first_word = cleaned.upper().split()[0] if cleaned else ""

    return first_word in ('INSERT', 'UPDATE', 'DELETE', 'MERGE')


def is_ddl_query(query: str) -> bool:
    """
    Check if a query is a DDL (Data Definition Language) statement.

    Args:
        query: SQL query string

    Returns:
        True if the query is CREATE, ALTER, DROP, or similar DDL statement

    Examples:
        >>> is_ddl_query("CREATE TABLE users (id INT)")
        True

        >>> is_ddl_query("SELECT * FROM users")
        False
    """
    if not query:
        return False

    cleaned = clean_query(query, remove_comments=True, normalize_whitespace=True)
    first_word = cleaned.upper().split()[0] if cleaned else ""

    return first_word in ('CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'COMMENT')


def get_query_type(query: str) -> str:
    """
    Determine the type of a SQL query.

    Args:
        query: SQL query string

    Returns:
        String representing the query type (SELECT, INSERT, CREATE, etc.)

    Examples:
        >>> get_query_type("SELECT * FROM users")
        'SELECT'

        >>> get_query_type("CREATE TABLE users (id INT)")
        'CREATE'
    """
    if not query:
        return "UNKNOWN"

    cleaned = clean_query(query, remove_comments=True, normalize_whitespace=True)
    first_word = cleaned.upper().split()[0] if cleaned else ""

    return first_word if first_word else "UNKNOWN"


def format_sql_for_display(
        query: str,
        max_width: int = 80,
        indent_size: int = 2,
        uppercase_keywords: bool = True,
) -> str:
    """
    Format SQL query for pretty display with basic indentation.

    Args:
        query: SQL query string to format
        max_width: Maximum line width (not strictly enforced)
        indent_size: Number of spaces for each indentation level
        uppercase_keywords: Whether to convert keywords to uppercase

    Returns:
        Formatted SQL query string

    Note:
        This is a basic formatter. For production use, consider a dedicated SQL formatter.
    """
    if not query:
        return ""

    # Clean the query
    formatted = clean_query(query, remove_comments=False, normalize_whitespace=True)

    if uppercase_keywords:
        # Convert keywords to uppercase (basic implementation)
        for keyword in SQL_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            formatted = re.sub(pattern, keyword.upper(), formatted, flags=re.IGNORECASE)

    # Basic formatting: add newlines after major clauses
    major_clauses = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING']

    for clause in major_clauses:
        pattern = r'\b' + clause + r'\b'
        formatted = re.sub(
            pattern,
            f'\n{clause}',
            formatted,
            flags=re.IGNORECASE
        )

    # Clean up extra newlines and add basic indentation
    lines = [line.strip() for line in formatted.split('\n') if line.strip()]

    indented_lines = []
    indent_level = 0

    for line in lines:
        # Simple indentation logic
        if line.upper().startswith(('SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING')):
            indent_level = 0
        elif line.upper().startswith(('AND', 'OR')):
            indent_level = 1
        elif line.upper().startswith(('JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN')):
            indent_level = 0

        indent = ' ' * (indent_level * indent_size)
        indented_lines.append(f"{indent}{line}")

    return '\n'.join(indented_lines)


# Utility functions for query analysis
def count_query_complexity(query: str) -> dict:
    """
    Analyze query complexity by counting various SQL elements.

    Args:
        query: SQL query string

    Returns:
        Dictionary with complexity metrics

    Examples:
        >>> count_query_complexity("SELECT * FROM users WHERE id = 1")
        {'tables': 1, 'joins': 0, 'conditions': 1, 'subqueries': 0}
    """
    if not query:
        return {'tables': 0, 'joins': 0, 'conditions': 0, 'subqueries': 0}

    cleaned = clean_query(query, remove_comments=True, normalize_whitespace=True)
    upper_query = cleaned.upper()

    # Count tables (approximate)
    tables = len(extract_table_names(query))

    # Count joins
    join_patterns = ['JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'OUTER JOIN', 'FULL JOIN']
    joins = sum(upper_query.count(pattern) for pattern in join_patterns)

    # Count WHERE conditions (approximate)
    where_conditions = upper_query.count(' AND ') + upper_query.count(' OR ') + (1 if ' WHERE ' in upper_query else 0)

    # Count subqueries (approximate)
    subqueries = upper_query.count('SELECT') - 1  # Subtract main SELECT

    return {
        'tables': tables,
        'joins': joins,
        'conditions': max(0, where_conditions),
        'subqueries': max(0, subqueries)
    }


# Export main functions
__all__ = [
    'trim_query',
    'clean_query',
    'format_query_for_logging',
    'extract_table_names',
    'mask_sensitive_data',
    'split_sql_statements',
    'is_select_query',
    'is_dml_query',
    'is_ddl_query',
    'get_query_type',
    'format_sql_for_display',
    'count_query_complexity',
]

if __name__ == "__main__":
    # Example usage and testing
    sample_queries = [
        "SELECT * FROM users WHERE active = 1 AND name = 'John Doe'",
        "INSERT INTO orders (user_id, total) VALUES (123, 45.67)",
        "CREATE TABLE products (id SERIAL PRIMARY KEY, name VARCHAR(100))",
        """
        SELECT u.name, COUNT(o.id) as order_count
        FROM users u
                 LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.active = 1
        GROUP BY u.name
        ORDER BY order_count DESC
        """,
    ]

    print("=== DataGuild SQL Formatter Examples ===\n")

    for i, query in enumerate(sample_queries, 1):
        print(f"Query {i}:")
        print(f"Original: {query}")
        print(f"Trimmed (50 chars): {trim_query(query, 50)}")
        print(f"For logging: {format_query_for_logging(query, 60)}")
        print(f"Query type: {get_query_type(query)}")
        print(f"Tables: {extract_table_names(query)}")
        print(f"Complexity: {count_query_complexity(query)}")
        print("-" * 50)
