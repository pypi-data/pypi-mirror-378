"""
DataGuild SQLGlot utilities for SQL parsing, formatting, and analysis.

This module provides comprehensive SQL parsing and formatting capabilities
using the SQLGlot library, with robust error handling and DataGuild-specific
optimizations for various SQL dialects, including advanced query fingerprinting.
"""

import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)

try:
    import sqlglot
    from sqlglot import expressions as exp
    from sqlglot.errors import ParseError, TokenError, UnsupportedError

    SQLGLOT_AVAILABLE = True
except ImportError:
    logger.warning(
        "SQLGlot is not available. Install with: pip install sqlglot. "
        "SQL formatting and parsing features will be limited."
    )
    SQLGLOT_AVAILABLE = False


    # Create dummy classes to prevent import errors
    class ParseError(Exception):
        pass


    class TokenError(Exception):
        pass


    class UnsupportedError(Exception):
        pass

# Supported SQL dialects in DataGuild
SUPPORTED_DIALECTS = {
    "snowflake", "bigquery", "postgres", "mysql", "redshift", "spark",
    "hive", "presto", "trino", "databricks", "duckdb", "clickhouse",
    "sqlite", "oracle", "teradata", "tsql"
}

# Default dialect for formatting
DEFAULT_DIALECT = "snowflake"


def get_query_fingerprint(
    query: str,
    dialect: str = DEFAULT_DIALECT,
    normalize_literals: bool = True,
    normalize_identifiers: bool = False,
    ignore_comments: bool = True,
    algorithm: str = "sha256"
) -> Dict[str, Any]:
    """
    ✅ ADDED: Generate a unique fingerprint for a SQL query to identify structurally similar queries.

    This function creates a normalized fingerprint of SQL queries by:
    - Replacing literal values with placeholders
    - Optionally normalizing identifiers (table/column names)
    - Removing comments and extra whitespace
    - Generating a hash of the normalized structure

    This is useful for:
    - Query performance monitoring and caching
    - Identifying similar query patterns
    - Query template detection
    - Usage analytics and optimization

    Args:
        query: SQL query string to fingerprint
        dialect: SQL dialect for parsing
        normalize_literals: Whether to replace literal values with placeholders
        normalize_identifiers: Whether to normalize table/column names
        ignore_comments: Whether to ignore SQL comments
        algorithm: Hash algorithm to use (md5, sha1, sha256, sha512)

    Returns:
        Dictionary containing fingerprint information:
        {
            'fingerprint': str,           # Hash of normalized query
            'normalized_query': str,      # Normalized query string
            'query_type': str,           # Type of query (SELECT, INSERT, etc.)
            'table_count': int,          # Number of tables referenced
            'complexity_score': float,   # Query complexity metric
            'has_subqueries': bool,      # Whether query contains subqueries
            'has_joins': bool,           # Whether query contains joins
            'literal_count': int,        # Number of literals found
            'success': bool,             # Whether fingerprinting succeeded
            'error': Optional[str]       # Error message if failed
        }

    Examples:
        >>> get_query_fingerprint("SELECT * FROM users WHERE id = 123")
        {
            'fingerprint': 'a1b2c3d4...',
            'normalized_query': 'SELECT * FROM users WHERE id = ?',
            'query_type': 'SELECT',
            'table_count': 1,
            'success': True,
            'error': None
        }

        >>> get_query_fingerprint("SELECT name FROM customers WHERE city = 'NYC' AND age > 25")
        {
            'fingerprint': 'e5f6g7h8...',
            'normalized_query': 'SELECT name FROM customers WHERE city = ? AND age > ?',
            'query_type': 'SELECT',
            'table_count': 1,
            'success': True,
            'error': None
        }
    """
    result = {
        'fingerprint': None,
        'normalized_query': None,
        'query_type': 'UNKNOWN',
        'table_count': 0,
        'complexity_score': 0.0,
        'has_subqueries': False,
        'has_joins': False,
        'literal_count': 0,
        'success': False,
        'error': None
    }

    if not query or not query.strip():
        result['error'] = "Empty query provided"
        return result

    # Validate hash algorithm
    if algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:
        logger.warning(f"Unsupported hash algorithm '{algorithm}', using 'sha256'")
        algorithm = 'sha256'

    try:
        # Step 1: Basic query cleaning
        normalized = query.strip()

        # Remove comments if requested
        if ignore_comments:
            normalized = _remove_sql_comments(normalized)

        # Step 2: Try SQLGlot-based normalization (preferred)
        if SQLGLOT_AVAILABLE:
            try:
                parsed = sqlglot.parse_one(normalized, read=dialect)
                if parsed:
                    result.update(_extract_query_metadata(parsed))
                    normalized = _normalize_with_sqlglot(
                        parsed,
                        normalize_literals=normalize_literals,
                        normalize_identifiers=normalize_identifiers,
                        dialect=dialect
                    )
                else:
                    # Fallback to regex-based normalization
                    normalized, literal_count = _normalize_with_regex(
                        normalized,
                        normalize_literals=normalize_literals
                    )
                    result['literal_count'] = literal_count

            except (ParseError, TokenError, UnsupportedError) as e:
                logger.debug(f"SQLGlot parsing failed, using regex fallback: {e}")
                normalized, literal_count = _normalize_with_regex(
                    normalized,
                    normalize_literals=normalize_literals
                )
                result['literal_count'] = literal_count
                result['query_type'] = _get_query_type_regex(query)
        else:
            # Pure regex-based normalization
            normalized, literal_count = _normalize_with_regex(
                normalized,
                normalize_literals=normalize_literals
            )
            result['literal_count'] = literal_count
            result['query_type'] = _get_query_type_regex(query)

        # Step 3: Final normalization steps
        normalized = _final_normalize(normalized)

        # Step 4: Generate fingerprint hash
        fingerprint = _generate_hash(normalized, algorithm)

        # Step 5: Update result
        result.update({
            'fingerprint': fingerprint,
            'normalized_query': normalized,
            'success': True,
            'error': None
        })

        logger.debug(f"Generated fingerprint for query type '{result['query_type']}': {fingerprint[:16]}...")
        return result

    except Exception as e:
        logger.error(f"Error generating query fingerprint: {e}")
        result['error'] = str(e)
        return result


def _remove_sql_comments(query: str) -> str:
    """Remove SQL comments from query string."""
    # Remove single-line comments (-- comment)
    query = re.sub(r'--.*?$', '', query, flags=re.MULTILINE)

    # Remove multi-line comments (/* comment */)
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)

    return query


def _extract_query_metadata(parsed_query) -> Dict[str, Any]:
    """Extract metadata from parsed SQLGlot query."""
    metadata = {
        'query_type': 'UNKNOWN',
        'table_count': 0,
        'has_subqueries': False,
        'has_joins': False,
        'complexity_score': 0.0
    }

    try:
        # Determine query type
        if isinstance(parsed_query, exp.Select):
            metadata['query_type'] = 'SELECT'
        elif isinstance(parsed_query, exp.Insert):
            metadata['query_type'] = 'INSERT'
        elif isinstance(parsed_query, exp.Update):
            metadata['query_type'] = 'UPDATE'
        elif isinstance(parsed_query, exp.Delete):
            metadata['query_type'] = 'DELETE'
        elif isinstance(parsed_query, exp.Create):
            metadata['query_type'] = 'CREATE'
        elif isinstance(parsed_query, exp.Drop):
            metadata['query_type'] = 'DROP'
        elif isinstance(parsed_query, exp.Alter):
            metadata['query_type'] = 'ALTER'
        else:
            metadata['query_type'] = type(parsed_query).__name__.upper()

        # Count tables
        tables = list(parsed_query.find_all(exp.Table))
        metadata['table_count'] = len(tables)

        # Check for subqueries
        subqueries = list(parsed_query.find_all(exp.Subquery))
        metadata['has_subqueries'] = len(subqueries) > 0

        # Check for joins
        join_types = [exp.Join, exp.LeftJoin, exp.RightJoin, exp.FullJoin, exp.InnerJoin]
        joins = sum(len(list(parsed_query.find_all(join_type))) for join_type in join_types)
        metadata['has_joins'] = joins > 0

        # Calculate complexity score
        functions = len(list(parsed_query.find_all(exp.Function)))
        conditions = len(list(parsed_query.find_all(exp.Where))) + len(list(parsed_query.find_all(exp.Having)))

        metadata['complexity_score'] = (
            metadata['table_count'] * 1.0 +
            joins * 2.0 +
            len(subqueries) * 3.0 +
            functions * 0.5 +
            conditions * 1.5
        )

    except Exception as e:
        logger.debug(f"Error extracting query metadata: {e}")

    return metadata


def _normalize_with_sqlglot(
    parsed_query,
    normalize_literals: bool = True,
    normalize_identifiers: bool = False,
    dialect: str = DEFAULT_DIALECT
) -> str:
    """Normalize query using SQLGlot AST manipulation."""
    try:
        # Create a copy to avoid modifying original
        normalized = parsed_query.copy()

        if normalize_literals:
            # Replace all literal values with placeholders
            for literal in normalized.find_all(exp.Literal):
                if literal.is_string:
                    literal.replace(exp.Placeholder(this="?"))
                elif literal.is_number:
                    literal.replace(exp.Placeholder(this="?"))
                elif literal.is_datetime:
                    literal.replace(exp.Placeholder(this="?"))

        if normalize_identifiers:
            # Normalize table and column names
            for table in normalized.find_all(exp.Table):
                if table.name:
                    table.args["this"] = "TABLE"

            for column in normalized.find_all(exp.Column):
                if column.name and column.name != "*":
                    column.args["this"] = "COLUMN"

        # Generate normalized SQL
        return normalized.sql(dialect=dialect, pretty=False, normalize=True)

    except Exception as e:
        logger.debug(f"Error normalizing with SQLGlot: {e}")
        raise


def _normalize_with_regex(query: str, normalize_literals: bool = True) -> tuple[str, int]:
    """Normalize query using regex patterns (fallback method)."""
    normalized = query
    literal_count = 0

    if normalize_literals:
        # Replace string literals
        string_pattern = r"'(?:[^'\\]|\\.)*'"
        string_matches = re.findall(string_pattern, normalized)
        literal_count += len(string_matches)
        normalized = re.sub(string_pattern, '?', normalized)

        # Replace numeric literals (integers and decimals)
        number_pattern = r'\b\d+\.?\d*\b'
        number_matches = re.findall(number_pattern, normalized)
        literal_count += len(number_matches)
        normalized = re.sub(number_pattern, '?', normalized)

        # Replace quoted identifiers but be careful not to affect keywords
        quoted_pattern = r'"[^"]*"'
        quoted_matches = re.findall(quoted_pattern, normalized)
        literal_count += len(quoted_matches)
        # Only replace if it's likely a string value, not an identifier

        # Replace date/time literals
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b',  # YYYY-MM-DD HH:MM:SS
            r'TIMESTAMP\s*\'\d{4}-\d{2}-\d{2}[^\']*\'',  # TIMESTAMP 'YYYY-MM-DD...'
        ]

        for pattern in date_patterns:
            date_matches = re.findall(pattern, normalized, re.IGNORECASE)
            literal_count += len(date_matches)
            normalized = re.sub(pattern, '?', normalized, flags=re.IGNORECASE)

    return normalized, literal_count


def _get_query_type_regex(query: str) -> str:
    """Extract query type using regex (fallback method)."""
    query_upper = query.strip().upper()

    # Common SQL statement types
    patterns = [
        (r'^\s*SELECT\b', 'SELECT'),
        (r'^\s*INSERT\b', 'INSERT'),
        (r'^\s*UPDATE\b', 'UPDATE'),
        (r'^\s*DELETE\b', 'DELETE'),
        (r'^\s*CREATE\b', 'CREATE'),
        (r'^\s*DROP\b', 'DROP'),
        (r'^\s*ALTER\b', 'ALTER'),
        (r'^\s*WITH\b', 'WITH'),
        (r'^\s*MERGE\b', 'MERGE'),
        (r'^\s*TRUNCATE\b', 'TRUNCATE'),
    ]

    for pattern, query_type in patterns:
        if re.match(pattern, query_upper):
            return query_type

    return 'UNKNOWN'


def _final_normalize(query: str) -> str:
    """Apply final normalization steps."""
    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', query)

    # Remove leading/trailing whitespace
    normalized = normalized.strip()

    # Convert to uppercase for consistency (optional)
    # normalized = normalized.upper()

    return normalized


def _generate_hash(text: str, algorithm: str) -> str:
    """Generate hash using specified algorithm."""
    text_bytes = text.encode('utf-8')

    if algorithm == 'md5':
        return hashlib.md5(text_bytes).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(text_bytes).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text_bytes).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(text_bytes).hexdigest()
    else:
        # Default to SHA256
        return hashlib.sha256(text_bytes).hexdigest()


def try_format_query(
        query: str,
        dialect: str = DEFAULT_DIALECT,
        pretty: bool = True,
        identify: bool = False,
        normalize: bool = True,
        fallback_to_original: bool = True,
) -> str:
    """
    Attempt to format a SQL query using SQLGlot with error handling.

    This function safely formats SQL queries with comprehensive error handling,
    falling back to the original query if parsing or formatting fails.

    Args:
        query: The SQL query string to format
        dialect: Target SQL dialect for formatting
        pretty: Whether to apply pretty formatting
        identify: Whether to quote/identify all identifiers
        normalize: Whether to normalize the query structure
        fallback_to_original: Whether to return original query on errors

    Returns:
        Formatted SQL query string, or original query if formatting fails

    Examples:
        >>> try_format_query("select * from users where id=1")
        'SELECT\\n  *\\nFROM users\\nWHERE\\n  id = 1'

        >>> try_format_query("invalid sql", fallback_to_original=True)
        'invalid sql'
    """
    if not query or not query.strip():
        return query

    if not SQLGLOT_AVAILABLE:
        logger.debug("SQLGlot not available, returning original query")
        return query

    # Validate dialect
    if dialect not in SUPPORTED_DIALECTS:
        logger.warning(f"Unsupported dialect '{dialect}', using default '{DEFAULT_DIALECT}'")
        dialect = DEFAULT_DIALECT

    try:
        # Parse the query
        parsed = sqlglot.parse_one(query, read=dialect)

        if parsed is None:
            logger.debug("Failed to parse query, returning original")
            return query if fallback_to_original else query

        # Format the query
        formatted = parsed.sql(
            dialect=dialect,
            pretty=pretty,
            identify=identify,
            normalize=normalize
        )

        if not formatted or not formatted.strip():
            logger.debug("Formatting produced empty result, returning original")
            return query if fallback_to_original else query

        logger.debug(f"Successfully formatted query using dialect '{dialect}'")
        return formatted

    except (ParseError, TokenError) as e:
        logger.debug(f"Parse error formatting query: {e}")
        return query if fallback_to_original else query

    except UnsupportedError as e:
        logger.debug(f"Unsupported SQL feature: {e}")
        return query if fallback_to_original else query

    except Exception as e:
        logger.warning(f"Unexpected error formatting query: {e}")
        return query if fallback_to_original else query


def parse_sql_query(
        query: str,
        dialect: str = DEFAULT_DIALECT,
        raise_on_error: bool = False
) -> Optional[Any]:
    """
    Parse a SQL query into an AST using SQLGlot.

    Args:
        query: SQL query string to parse
        dialect: Source SQL dialect
        raise_on_error: Whether to raise exceptions on parse errors

    Returns:
        Parsed SQL expression or None if parsing fails

    Raises:
        ParseError: If raise_on_error is True and parsing fails
    """
    if not query or not query.strip():
        return None

    if not SQLGLOT_AVAILABLE:
        if raise_on_error:
            raise ImportError("SQLGlot is not available")
        return None

    try:
        return sqlglot.parse_one(query, read=dialect)
    except (ParseError, TokenError) as e:
        if raise_on_error:
            raise
        logger.debug(f"Failed to parse SQL query: {e}")
        return None
    except Exception as e:
        if raise_on_error:
            raise
        logger.warning(f"Unexpected error parsing SQL query: {e}")
        return None


def extract_table_names(
        query: str,
        dialect: str = DEFAULT_DIALECT,
        include_ctes: bool = True
) -> List[str]:
    """
    Extract table names referenced in a SQL query.

    Args:
        query: SQL query string
        dialect: SQL dialect for parsing
        include_ctes: Whether to include CTE names in results

    Returns:
        List of table names found in the query

    Examples:
        >>> extract_table_names("SELECT * FROM users u JOIN orders o ON u.id = o.user_id")
        ['users', 'orders']
    """
    if not SQLGLOT_AVAILABLE:
        return []

    parsed = parse_sql_query(query, dialect=dialect)
    if not parsed:
        return []

    table_names = set()

    try:
        # Find all table references
        for table in parsed.find_all(exp.Table):
            if table.name:
                table_names.add(table.name)

        # Include CTE names if requested
        if include_ctes:
            for cte in parsed.find_all(exp.CTE):
                if cte.alias:
                    table_names.add(cte.alias)

    except Exception as e:
        logger.debug(f"Error extracting table names: {e}")
        return []

    return sorted(list(table_names))


def extract_column_names(
        query: str,
        dialect: str = DEFAULT_DIALECT,
        include_aliases: bool = True
) -> List[str]:
    """
    Extract column names referenced in a SQL query.

    Args:
        query: SQL query string
        dialect: SQL dialect for parsing
        include_aliases: Whether to include column aliases

    Returns:
        List of column names found in the query

    Examples:
        >>> extract_column_names("SELECT u.name, u.email as user_email FROM users u")
        ['name', 'email', 'user_email']
    """
    if not SQLGLOT_AVAILABLE:
        return []

    parsed = parse_sql_query(query, dialect=dialect)
    if not parsed:
        return []

    column_names = set()

    try:
        # Find all column references
        for column in parsed.find_all(exp.Column):
            if column.name and column.name != "*":
                column_names.add(column.name)

        # Include aliases if requested
        if include_aliases:
            for alias in parsed.find_all(exp.Alias):
                if alias.alias and isinstance(alias.this, exp.Column):
                    column_names.add(alias.alias)

    except Exception as e:
        logger.debug(f"Error extracting column names: {e}")
        return []

    return sorted(list(column_names))


def transpile_query(
        query: str,
        source_dialect: str,
        target_dialect: str,
        pretty: bool = True,
        identify: bool = False
) -> Optional[str]:
    """
    Transpile a SQL query from one dialect to another.

    Args:
        query: SQL query string to transpile
        source_dialect: Source SQL dialect
        target_dialect: Target SQL dialect
        pretty: Whether to apply pretty formatting
        identify: Whether to quote identifiers

    Returns:
        Transpiled SQL query string or None if transpilation fails

    Examples:
        >>> transpile_query("SELECT TOP 10 * FROM users", "tsql", "postgres")
        'SELECT\\n  *\\nFROM users\\nLIMIT 10'
    """
    if not SQLGLOT_AVAILABLE:
        return None

    if source_dialect not in SUPPORTED_DIALECTS:
        logger.warning(f"Unsupported source dialect: {source_dialect}")
        return None

    if target_dialect not in SUPPORTED_DIALECTS:
        logger.warning(f"Unsupported target dialect: {target_dialect}")
        return None

    try:
        result = sqlglot.transpile(
            query,
            read=source_dialect,
            write=target_dialect,
            pretty=pretty,
            identify=identify
        )

        if result and len(result) > 0:
            return result[0]
        return None

    except Exception as e:
        logger.debug(f"Error transpiling query: {e}")
        return None


def get_query_type(query: str, dialect: str = DEFAULT_DIALECT) -> str:
    """
    Determine the type of SQL query (SELECT, INSERT, UPDATE, etc.).

    Args:
        query: SQL query string
        dialect: SQL dialect for parsing

    Returns:
        Query type string or "UNKNOWN" if cannot be determined

    Examples:
        >>> get_query_type("SELECT * FROM users")
        'SELECT'
        >>> get_query_type("INSERT INTO users VALUES (1, 'John')")
        'INSERT'
    """
    if not SQLGLOT_AVAILABLE:
        # Fallback to simple string analysis
        return _get_query_type_regex(query)

    parsed = parse_sql_query(query, dialect=dialect)
    if not parsed:
        return "UNKNOWN"

    try:
        if isinstance(parsed, exp.Select):
            return "SELECT"
        elif isinstance(parsed, exp.Insert):
            return "INSERT"
        elif isinstance(parsed, exp.Update):
            return "UPDATE"
        elif isinstance(parsed, exp.Delete):
            return "DELETE"
        elif isinstance(parsed, exp.Create):
            return "CREATE"
        elif isinstance(parsed, exp.Drop):
            return "DROP"
        elif isinstance(parsed, exp.Alter):
            return "ALTER"
        else:
            return type(parsed).__name__.upper()

    except Exception as e:
        logger.debug(f"Error determining query type: {e}")
        return "UNKNOWN"


def validate_sql_syntax(
        query: str,
        dialect: str = DEFAULT_DIALECT,
        return_errors: bool = False
) -> Union[bool, Dict[str, Any]]:
    """
    Validate SQL syntax using SQLGlot parser.

    Args:
        query: SQL query string to validate
        dialect: SQL dialect for validation
        return_errors: Whether to return detailed error information

    Returns:
        Boolean indicating validity, or dict with validation details

    Examples:
        >>> validate_sql_syntax("SELECT * FROM users")
        True
        >>> validate_sql_syntax("SELECT * FROM", return_errors=True)
        {'valid': False, 'error': 'Parse error...', 'error_type': 'ParseError'}
    """
    if not SQLGLOT_AVAILABLE:
        result = {"valid": False, "error": "SQLGlot not available", "error_type": "ImportError"}
        return result if return_errors else False

    try:
        parsed = sqlglot.parse_one(query, read=dialect)
        result = {"valid": True, "error": None, "error_type": None}
        return result if return_errors else True

    except (ParseError, TokenError) as e:
        result = {"valid": False, "error": str(e), "error_type": type(e).__name__}
        return result if return_errors else False

    except Exception as e:
        result = {"valid": False, "error": str(e), "error_type": type(e).__name__}
        return result if return_errors else False


def optimize_query(
        query: str,
        dialect: str = DEFAULT_DIALECT,
        schema: Optional[Dict[str, Dict[str, str]]] = None
) -> Optional[str]:
    """
    Optimize a SQL query using SQLGlot optimizer.

    Args:
        query: SQL query string to optimize
        dialect: SQL dialect
        schema: Optional schema information for optimization

    Returns:
        Optimized SQL query string or None if optimization fails

    Examples:
        >>> optimize_query("SELECT * FROM (SELECT * FROM users) t WHERE t.id = 1")
        'SELECT\\n  users.id,\\n  users.name\\nFROM users\\nWHERE\\n  users.id = 1'
    """
    if not SQLGLOT_AVAILABLE:
        return None

    try:
        from sqlglot.optimizer import optimize

        parsed = sqlglot.parse_one(query, read=dialect)
        if not parsed:
            return None

        optimized = optimize(parsed, schema=schema or {})
        return optimized.sql(dialect=dialect, pretty=True)

    except ImportError:
        logger.debug("SQLGlot optimizer not available")
        return None
    except Exception as e:
        logger.debug(f"Error optimizing query: {e}")
        return None


def get_query_complexity_score(
        query: str,
        dialect: str = DEFAULT_DIALECT
) -> Dict[str, Union[int, float]]:
    """
    Calculate complexity metrics for a SQL query.

    Args:
        query: SQL query string
        dialect: SQL dialect for parsing

    Returns:
        Dictionary with complexity metrics

    Examples:
        >>> get_query_complexity_score("SELECT * FROM users WHERE id = 1")
        {'tables': 1, 'joins': 0, 'subqueries': 0, 'functions': 0, 'complexity_score': 1.0}
    """
    default_metrics = {
        'tables': 0, 'joins': 0, 'subqueries': 0, 'functions': 0,
        'conditions': 0, 'complexity_score': 0.0
    }

    if not SQLGLOT_AVAILABLE:
        return default_metrics

    parsed = parse_sql_query(query, dialect=dialect)
    if not parsed:
        return default_metrics

    try:
        metrics = default_metrics.copy()

        # Count tables
        metrics['tables'] = len(list(parsed.find_all(exp.Table)))

        # Count joins
        join_types = [exp.Join, exp.LeftJoin, exp.RightJoin, exp.FullJoin, exp.InnerJoin]
        metrics['joins'] = sum(len(list(parsed.find_all(join_type))) for join_type in join_types)

        # Count subqueries
        metrics['subqueries'] = len(list(parsed.find_all(exp.Subquery)))

        # Count functions
        metrics['functions'] = len(list(parsed.find_all(exp.Function)))

        # Count conditions (WHERE, HAVING clauses)
        metrics['conditions'] = len(list(parsed.find_all(exp.Where))) + len(list(parsed.find_all(exp.Having)))

        # Calculate complexity score
        metrics['complexity_score'] = (
                metrics['tables'] * 1.0 +
                metrics['joins'] * 2.0 +
                metrics['subqueries'] * 3.0 +
                metrics['functions'] * 0.5 +
                metrics['conditions'] * 1.5
        )

        return metrics

    except Exception as e:
        logger.debug(f"Error calculating query complexity: {e}")
        return default_metrics


def is_select_query(query: str, dialect: str = DEFAULT_DIALECT) -> bool:
    """Check if a query is a SELECT statement."""
    return get_query_type(query, dialect) == "SELECT"


def is_dml_query(query: str, dialect: str = DEFAULT_DIALECT) -> bool:
    """Check if a query is a DML (INSERT, UPDATE, DELETE) statement."""
    query_type = get_query_type(query, dialect)
    return query_type in ["INSERT", "UPDATE", "DELETE"]


def is_ddl_query(query: str, dialect: str = DEFAULT_DIALECT) -> bool:
    """Check if a query is a DDL (CREATE, ALTER, DROP) statement."""
    query_type = get_query_type(query, dialect)
    return query_type in ["CREATE", "ALTER", "DROP"]


def clean_sql_query(query: str, remove_comments: bool = True) -> str:
    """
    Clean and normalize a SQL query string.

    Args:
        query: SQL query string to clean
        remove_comments: Whether to remove SQL comments

    Returns:
        Cleaned SQL query string
    """
    if not query:
        return ""

    cleaned = query.strip()

    if remove_comments and SQLGLOT_AVAILABLE:
        try:
            # Use SQLGlot to parse and regenerate without comments
            parsed = sqlglot.parse_one(cleaned)
            if parsed:
                cleaned = parsed.sql(comments=False)
        except:
            pass  # Fall back to original if parsing fails

    return cleaned


# Export main functions
__all__ = [
    # ✅ ADDED: Query fingerprinting
    'get_query_fingerprint',

    # Existing functions
    'try_format_query',
    'parse_sql_query',
    'extract_table_names',
    'extract_column_names',
    'transpile_query',
    'get_query_type',
    'validate_sql_syntax',
    'optimize_query',
    'get_query_complexity_score',
    'is_select_query',
    'is_dml_query',
    'is_ddl_query',
    'clean_sql_query',
    'SUPPORTED_DIALECTS',
    'DEFAULT_DIALECT',
]

# Utility functions for testing and debugging
if __name__ == "__main__":
    # Example usage and testing
    sample_queries = [
        "SELECT * FROM users WHERE active = 1",
        "INSERT INTO orders (user_id, total) VALUES (123, 45.67)",
        "UPDATE users SET last_login = NOW() WHERE id = 1",
        """
        WITH active_users AS (SELECT id, name
                              FROM users
                              WHERE active = 1)
        SELECT u.name, COUNT(o.id) as order_count
        FROM active_users u
                 LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.name
        ORDER BY order_count DESC LIMIT 10
        """,
    ]

    print("=== DataGuild SQLGlot Utilities Examples ===\n")

    for i, query in enumerate(sample_queries, 1):
        print(f"Query {i}:")
        print(f"Original: {query.strip()}")
        print(f"Formatted: {try_format_query(query)}")
        print(f"Type: {get_query_type(query)}")
        print(f"Tables: {extract_table_names(query)}")
        print(f"Columns: {extract_column_names(query)}")
        print(f"Valid: {validate_sql_syntax(query)}")
        print(f"Complexity: {get_query_complexity_score(query)}")

        # ✅ NEW: Demonstrate fingerprinting
        fingerprint_result = get_query_fingerprint(query)
        if fingerprint_result['success']:
            print(f"Fingerprint: {fingerprint_result['fingerprint'][:16]}...")
            print(f"Normalized: {fingerprint_result['normalized_query']}")
            print(f"Literal Count: {fingerprint_result['literal_count']}")
        else:
            print(f"Fingerprint Error: {fingerprint_result['error']}")

        print("-" * 60)
