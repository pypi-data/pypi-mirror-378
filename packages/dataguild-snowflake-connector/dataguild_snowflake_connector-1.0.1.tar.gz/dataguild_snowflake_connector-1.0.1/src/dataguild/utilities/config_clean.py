"""
DataGuild configuration cleaning utilities.

This module provides comprehensive utilities for cleaning and normalizing
configuration values, URLs, paths, and other string-based configuration
parameters commonly used in DataGuild ingestion pipelines.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def remove_protocol(url: Optional[str]) -> Optional[str]:
    """
    Remove protocol scheme from URL string.

    Removes common protocol prefixes like 'http://', 'https://', 'ftp://',
    'jdbc:', etc. from the beginning of URL strings for normalization.

    Args:
        url: URL string that may contain a protocol prefix

    Returns:
        URL string with protocol removed, or None if input is None

    Examples:
        >>> remove_protocol("https://example.com/path")
        'example.com/path'

        >>> remove_protocol("jdbc:snowflake://account.snowflakecomputing.com")
        'account.snowflakecomputing.com'

        >>> remove_protocol("ftp://files.example.com/data")
        'files.example.com/data'

        >>> remove_protocol("example.com")  # No protocol
        'example.com'
    """
    if not url:
        return url

    # Remove protocol schemes (handles multiple common protocols)
    # Pattern matches: protocol:// or protocol: followed by any characters
    cleaned_url = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', '', url)

    # Handle special cases like jdbc: without //
    cleaned_url = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', '', cleaned_url)

    logger.debug(f"Removed protocol from '{url}' -> '{cleaned_url}'")
    return cleaned_url


def remove_suffix(
        text: Optional[str],
        suffixes: Union[str, List[str]]
) -> Optional[str]:
    """
    Remove specified suffixes from the end of text string.

    Removes any of the provided suffixes from the end of the input text.
    Processes suffixes in the order provided and only removes the first
    matching suffix found.

    Args:
        text: Input string to process
        suffixes: Single suffix string or list of suffix strings to remove

    Returns:
        String with suffix removed, or None if input is None

    Examples:
        >>> remove_suffix("database.schema.table", [".table", ".view"])
        'database.schema'

        >>> remove_suffix("config.yaml", ".yaml")
        'config'

        >>> remove_suffix("api_endpoint/", "/")
        'api_endpoint'

        >>> remove_suffix("no_suffix", [".txt", ".json"])
        'no_suffix'
    """
    if not text:
        return text

    # Convert single suffix to list for uniform processing
    if isinstance(suffixes, str):
        suffixes = [suffixes]

    original_text = text

    # Try to remove each suffix (only removes the first match)
    for suffix in suffixes:
        if suffix and text.endswith(suffix):
            text = text[:-len(suffix)]
            logger.debug(f"Removed suffix '{suffix}' from '{original_text}' -> '{text}'")
            break

    return text


def remove_trailing_slashes(path: Optional[str]) -> Optional[str]:
    """
    Remove trailing slashes from path string.

    Removes one or more trailing forward slashes from paths while preserving
    single root slash for absolute paths.

    Args:
        path: Path string that may have trailing slashes

    Returns:
        Path string with trailing slashes removed, or None if input is None

    Examples:
        >>> remove_trailing_slashes("/api/v1/data/")
        '/api/v1/data'

        >>> remove_trailing_slashes("relative/path///")
        'relative/path'

        >>> remove_trailing_slashes("/")
        '/'

        >>> remove_trailing_slashes("")
        ''
    """
    if not path:
        return path

    original_path = path

    # Special case: preserve single root slash
    if path == "/":
        return path

    # Remove trailing slashes
    cleaned_path = path.rstrip('/')

    if cleaned_path != original_path:
        logger.debug(f"Removed trailing slashes from '{original_path}' -> '{cleaned_path}'")

    return cleaned_path


def remove_leading_slashes(path: Optional[str]) -> Optional[str]:
    """
    Remove leading slashes from path string.

    Args:
        path: Path string that may have leading slashes

    Returns:
        Path string with leading slashes removed

    Examples:
        >>> remove_leading_slashes("//path/to/file")
        'path/to/file'

        >>> remove_leading_slashes("/single/slash")
        'single/slash'
    """
    if not path:
        return path

    original_path = path
    cleaned_path = path.lstrip('/')

    if cleaned_path != original_path:
        logger.debug(f"Removed leading slashes from '{original_path}' -> '{cleaned_path}'")

    return cleaned_path


def normalize_whitespace(text: Optional[str]) -> Optional[str]:
    """
    Normalize whitespace in text string.

    Removes leading/trailing whitespace and replaces multiple consecutive
    whitespace characters with single spaces.

    Args:
        text: Input text to normalize

    Returns:
        Text with normalized whitespace

    Examples:
        >>> normalize_whitespace("  multiple   spaces   here  ")
        'multiple spaces here'

        >>> normalize_whitespace("line1\\n\\nline2\\t\\tvalue")
        'line1 line2 value'
    """
    if not text:
        return text

    # Replace multiple whitespace characters with single space
    normalized = re.sub(r'\s+', ' ', text.strip())

    logger.debug(f"Normalized whitespace: '{text}' -> '{normalized}'")
    return normalized


def clean_url(url: Optional[str]) -> Optional[str]:
    """
    Comprehensive URL cleaning and normalization.

    Combines multiple cleaning operations for URLs including protocol removal,
    trailing slash removal, and basic normalization.

    Args:
        url: URL string to clean

    Returns:
        Cleaned and normalized URL string

    Examples:
        >>> clean_url("https://api.example.com/v1/data/")
        'api.example.com/v1/data'

        >>> clean_url("jdbc:snowflake://account.snowflakecomputing.com:443/")
        'account.snowflakecomputing.com:443'
    """
    if not url:
        return url

    cleaned = url

    # Remove protocol
    cleaned = remove_protocol(cleaned)

    # Remove trailing slashes
    cleaned = remove_trailing_slashes(cleaned)

    # Normalize whitespace
    cleaned = normalize_whitespace(cleaned)

    logger.debug(f"Cleaned URL: '{url}' -> '{cleaned}'")
    return cleaned


def clean_identifier(identifier: Optional[str]) -> Optional[str]:
    """
    Clean and normalize identifier strings.

    Removes common problematic characters and normalizes identifiers
    for use in configurations, database names, etc.

    Args:
        identifier: Identifier string to clean

    Returns:
        Cleaned identifier string

    Examples:
        >>> clean_identifier("  my-database_name  ")
        'my-database_name'

        >>> clean_identifier("schema.table@version")
        'schema.table_version'
    """
    if not identifier:
        return identifier

    # Normalize whitespace first
    cleaned = normalize_whitespace(identifier)

    if not cleaned:
        return cleaned

    # Replace problematic characters commonly found in identifiers
    cleaned = re.sub(r'[@#$%^&*()+=\[\]{}|\\:";\'<>?,./]', '_', cleaned)

    # Remove multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)

    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')

    logger.debug(f"Cleaned identifier: '{identifier}' -> '{cleaned}'")
    return cleaned


def remove_comments(text: Optional[str], comment_chars: Optional[List[str]] = None) -> Optional[str]:
    """
    Remove comments from configuration text.

    Removes lines or portions of lines that start with comment characters.
    Supports multiple comment character types.

    Args:
        text: Text that may contain comments
        comment_chars: List of comment prefixes (default: ['#'])

    Returns:
        Text with comments removed

    Examples:
        >>> remove_comments("line1\\n# This is a comment\\nline2")
        'line1\\n\\nline2'

        >>> remove_comments("config=value # inline comment", ['#'])
        'config=value '

        >>> remove_comments("// JS comment\\ncode", ['//'])
        '\\ncode'
    """
    if not text:
        return text

    if comment_chars is None:
        comment_chars = ['#']

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        cleaned_line = line

        # Find the earliest comment character in the line
        earliest_pos = len(line)
        for comment_char in comment_chars:
            pos = line.find(comment_char)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos

        # Remove comment portion if found
        if earliest_pos < len(line):
            cleaned_line = line[:earliest_pos].rstrip()

        cleaned_lines.append(cleaned_line)

    result = '\n'.join(cleaned_lines)
    logger.debug(f"Removed comments from {len(lines)} lines")
    return result


def sanitize_config_value(value: Any) -> Any:
    """
    Sanitize configuration values for safe processing.

    Cleans string values and handles various data types commonly found
    in configuration files.

    Args:
        value: Configuration value to sanitize

    Returns:
        Sanitized configuration value
    """
    if isinstance(value, str):
        # Apply basic string cleaning
        sanitized = normalize_whitespace(value)

        # Remove quotes if they wrap the entire value
        if len(sanitized) >= 2:
            if (sanitized.startswith('"') and sanitized.endswith('"')) or \
               (sanitized.startswith("'") and sanitized.endswith("'")):
                sanitized = sanitized[1:-1]

        return sanitized

    elif isinstance(value, dict):
        # Recursively sanitize dictionary values
        return {k: sanitize_config_value(v) for k, v in value.items()}

    elif isinstance(value, list):
        # Recursively sanitize list items
        return [sanitize_config_value(item) for item in value]

    else:
        # Return non-string values as-is
        return value


def validate_identifier(identifier: str, allow_dots: bool = True) -> bool:
    """
    Validate that an identifier follows naming conventions.

    Args:
        identifier: Identifier string to validate
        allow_dots: Whether to allow dots in identifiers

    Returns:
        True if identifier is valid, False otherwise

    Examples:
        >>> validate_identifier("valid_name")
        True

        >>> validate_identifier("schema.table", allow_dots=True)
        True

        >>> validate_identifier("invalid@name")
        False
    """
    if not identifier or not isinstance(identifier, str):
        return False

    # Basic pattern for identifiers
    if allow_dots:
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_\.]*$'
    else:
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'

    return bool(re.match(pattern, identifier))


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain/hostname from URL string.

    Args:
        url: URL string

    Returns:
        Domain name or None if extraction fails

    Examples:
        >>> extract_domain_from_url("https://api.example.com:8080/path")
        'api.example.com'

        >>> extract_domain_from_url("jdbc:snowflake://account.snowflakecomputing.com")
        'account.snowflakecomputing.com'
    """
    try:
        # Handle special URL schemes like jdbc:
        if url.startswith('jdbc:'):
            url = url.replace('jdbc:', 'http:', 1)

        parsed = urlparse(url)
        return parsed.hostname
    except Exception:
        logger.warning(f"Failed to extract domain from URL: {url}")
        return None


def merge_config_strings(base: str, override: str, separator: str = ",") -> str:
    """
    Merge two configuration strings with deduplication.

    Args:
        base: Base configuration string
        override: Override configuration string
        separator: String separator (default: comma)

    Returns:
        Merged configuration string

    Examples:
        >>> merge_config_strings("a,b,c", "c,d,e")
        'a,b,c,d,e'

        >>> merge_config_strings("db1;db2", "db2;db3", separator=";")
        'db1;db2;db3'
    """
    if not base:
        return override or ""

    if not override:
        return base

    base_items = [item.strip() for item in base.split(separator) if item.strip()]
    override_items = [item.strip() for item in override.split(separator) if item.strip()]

    # Merge with deduplication while preserving order
    seen = set()
    merged = []

    for item in base_items + override_items:
        if item not in seen:
            seen.add(item)
            merged.append(item)

    return separator.join(merged)
