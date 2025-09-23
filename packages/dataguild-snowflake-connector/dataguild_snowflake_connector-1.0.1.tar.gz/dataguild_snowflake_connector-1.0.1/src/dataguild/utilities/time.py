"""
DataGuild time utilities for working with datetime objects and timestamps.

This module provides utility functions for converting between datetime objects
and Unix timestamps in milliseconds, with proper timezone handling and
error management for DataGuild ingestion workflows.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Union
import time

logger = logging.getLogger(__name__)


def datetime_to_ts_millis(dt: datetime) -> int:
    """
    Convert a datetime object to milliseconds since Unix epoch.

    This function converts a Python datetime object to the number of milliseconds
    that have elapsed since January 1, 1970, 00:00:00 UTC (Unix epoch).

    Args:
        dt: The datetime object to convert. Can be timezone-aware or naive.
            If naive, it will be treated as local time.

    Returns:
        Integer representing milliseconds since Unix epoch

    Raises:
        TypeError: If dt is not a datetime object
        ValueError: If datetime is invalid or cannot be converted
        OverflowError: If datetime is too far in the future/past

    Examples:
        >>> from datetime import datetime, timezone
        >>> dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> ts = datetime_to_ts_millis(dt)
        >>> print(ts)
        1672574400000

        >>> # Current time
        >>> now = datetime.now()
        >>> current_ts = datetime_to_ts_millis(now)
        >>> print(f"Current timestamp: {current_ts}")
    """
    if not isinstance(dt, datetime):
        raise TypeError(f"Expected datetime object, got {type(dt).__name__}")

    try:
        # Get timestamp in seconds (float) and convert to milliseconds (int)
        timestamp_seconds = dt.timestamp()
        timestamp_millis = int(timestamp_seconds * 1000)

        logger.debug(f"Converted datetime {dt} to timestamp {timestamp_millis}ms")
        return timestamp_millis

    except (ValueError, OverflowError, OSError) as e:
        logger.error(f"Failed to convert datetime {dt} to timestamp: {e}")
        raise ValueError(f"Cannot convert datetime to timestamp: {e}") from e


def ts_millis_to_datetime(ts_millis: Union[int, float]) -> datetime:
    """
    Convert milliseconds since Unix epoch to a datetime object.

    This function converts a Unix timestamp in milliseconds back to a Python
    datetime object in UTC timezone.

    Args:
        ts_millis: Timestamp in milliseconds since Unix epoch.
                  Can be int or float.

    Returns:
        Timezone-aware datetime object in UTC

    Raises:
        TypeError: If ts_millis is not a number
        ValueError: If timestamp is invalid or out of range
        OverflowError: If timestamp is too large

    Examples:
        >>> ts = 1672574400000  # Jan 1, 2023 12:00:00 UTC
        >>> dt = ts_millis_to_datetime(ts)
        >>> print(dt)
        2023-01-01 12:00:00+00:00

        >>> # Convert current timestamp back to datetime
        >>> current_ts = int(time.time() * 1000)
        >>> current_dt = ts_millis_to_datetime(current_ts)
        >>> print(f"Current time: {current_dt}")
    """
    if not isinstance(ts_millis, (int, float)):
        raise TypeError(f"Expected int or float, got {type(ts_millis).__name__}")

    try:
        # Convert milliseconds to seconds
        timestamp_seconds = ts_millis / 1000.0

        # Create timezone-aware datetime object in UTC
        dt = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)

        logger.debug(f"Converted timestamp {ts_millis}ms to datetime {dt}")
        return dt

    except (ValueError, OverflowError, OSError) as e:
        logger.error(f"Failed to convert timestamp {ts_millis}ms to datetime: {e}")
        raise ValueError(f"Cannot convert timestamp to datetime: {e}") from e


def current_time_millis() -> int:
    """
    Get the current time as milliseconds since Unix epoch.

    This is a convenience function that returns the current time
    as a Unix timestamp in milliseconds.

    Returns:
        Current timestamp in milliseconds

    Examples:
        >>> current_ts = current_time_millis()
        >>> print(f"Current timestamp: {current_ts}")
        >>>
        >>> # Convert back to datetime to verify
        >>> current_dt = ts_millis_to_datetime(current_ts)
        >>> print(f"Current time: {current_dt}")
    """
    return datetime_to_ts_millis(datetime.now(timezone.utc))


def parse_absolute_time(time_str: str) -> datetime:
    """
    Parse various time string formats into a datetime object.

    This function attempts to parse common timestamp formats including
    ISO 8601, Unix timestamps, and other standard formats.

    Args:
        time_str: Time string to parse

    Returns:
        Parsed datetime object (timezone-aware when possible)

    Raises:
        ValueError: If time string cannot be parsed

    Examples:
        >>> # ISO 8601 format
        >>> dt1 = parse_absolute_time("2023-01-01T12:00:00Z")
        >>> print(dt1)
        2023-01-01 12:00:00+00:00

        >>> # Unix timestamp in seconds
        >>> dt2 = parse_absolute_time("1672574400")
        >>> print(dt2)
        2023-01-01 12:00:00+00:00

        >>> # Unix timestamp in milliseconds
        >>> dt3 = parse_absolute_time("1672574400000")
        >>> print(dt3)
        2023-01-01 12:00:00+00:00
    """
    if not isinstance(time_str, str):
        raise TypeError(f"Expected string, got {type(time_str).__name__}")

    time_str = time_str.strip()
    if not time_str:
        raise ValueError("Empty time string")

    # Try to parse as Unix timestamp (numeric string)
    if time_str.isdigit():
        try:
            timestamp = int(time_str)

            # Determine if it's seconds or milliseconds based on magnitude
            # Timestamps after year 2001 in seconds: > 1000000000
            # Timestamps before year 2286 in milliseconds: < 10000000000000
            if timestamp > 1000000000 and timestamp < 10000000000:
                # Likely seconds, convert to milliseconds
                return ts_millis_to_datetime(timestamp * 1000)
            elif timestamp >= 10000000000:
                # Likely milliseconds
                return ts_millis_to_datetime(timestamp)
            else:
                raise ValueError(f"Timestamp {timestamp} appears to be too small")

        except (ValueError, OverflowError) as e:
            logger.debug(f"Failed to parse as timestamp: {e}")

    # Try to parse as ISO 8601 format
    try:
        # Handle common ISO 8601 variants
        if time_str.endswith('Z'):
            # UTC timezone indicator
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        elif '+' in time_str or time_str.count('-') > 2:
            # Already has timezone info
            dt = datetime.fromisoformat(time_str)
        else:
            # No timezone info, assume UTC
            dt = datetime.fromisoformat(time_str).replace(tzinfo=timezone.utc)

        logger.debug(f"Parsed time string '{time_str}' as {dt}")
        return dt

    except ValueError as e:
        logger.debug(f"Failed to parse as ISO format: {e}")

    # Try other common formats
    common_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in common_formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            # Assume UTC if no timezone info
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            logger.debug(f"Parsed time string '{time_str}' using format '{fmt}' as {dt}")
            return dt
        except ValueError:
            continue

    # If nothing worked, raise an error
    raise ValueError(f"Unable to parse time string: '{time_str}'")


def format_timestamp_millis(ts_millis: Union[int, float], fmt: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """
    Format a timestamp in milliseconds as a human-readable string.

    Args:
        ts_millis: Timestamp in milliseconds since Unix epoch
        fmt: strftime format string (default: "%Y-%m-%d %H:%M:%S UTC")

    Returns:
        Formatted time string

    Examples:
        >>> ts = 1672574400000  # Jan 1, 2023 12:00:00 UTC
        >>> formatted = format_timestamp_millis(ts)
        >>> print(formatted)
        2023-01-01 12:00:00 UTC

        >>> # Custom format
        >>> custom = format_timestamp_millis(ts, "%B %d, %Y at %I:%M %p")
        >>> print(custom)
        January 01, 2023 at 12:00 PM
    """
    dt = ts_millis_to_datetime(ts_millis)
    return dt.strftime(fmt)


def time_diff_millis(start_dt: datetime, end_dt: datetime) -> int:
    """
    Calculate the difference between two datetime objects in milliseconds.

    Args:
        start_dt: Start datetime
        end_dt: End datetime

    Returns:
        Difference in milliseconds (positive if end_dt > start_dt)

    Examples:
        >>> from datetime import timedelta
        >>> start = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> end = start + timedelta(hours=1)
        >>> diff = time_diff_millis(start, end)
        >>> print(diff)
        3600000  # 1 hour in milliseconds
    """
    if not isinstance(start_dt, datetime) or not isinstance(end_dt, datetime):
        raise TypeError("Both arguments must be datetime objects")

    # Calculate difference as timedelta
    diff = end_dt - start_dt

    # Convert to milliseconds
    diff_millis = int(diff.total_seconds() * 1000)

    return diff_millis


def is_valid_timestamp_millis(ts_millis: Union[int, float]) -> bool:
    """
    Check if a timestamp in milliseconds is valid and reasonable.

    This function validates that the timestamp is within a reasonable range
    (between year 1970 and 2100) and can be converted to a datetime.

    Args:
        ts_millis: Timestamp in milliseconds to validate

    Returns:
        True if timestamp is valid, False otherwise

    Examples:
        >>> is_valid_timestamp_millis(1672574400000)  # Valid timestamp
        True
        >>> is_valid_timestamp_millis(-1)  # Before epoch
        False
        >>> is_valid_timestamp_millis(4102444800000)  # Year 2100
        True
        >>> is_valid_timestamp_millis(9999999999999)  # Too far in future
        False
    """
    if not isinstance(ts_millis, (int, float)):
        return False

    try:
        # Check reasonable bounds
        # January 1, 1970 00:00:00 UTC = 0
        # January 1, 2100 00:00:00 UTC = 4102444800000
        min_timestamp = 0
        max_timestamp = 4102444800000  # Year 2100

        if ts_millis < min_timestamp or ts_millis > max_timestamp:
            return False

        # Try to convert to datetime
        ts_millis_to_datetime(ts_millis)
        return True

    except (ValueError, OverflowError, TypeError):
        return False


# Export all functions
__all__ = [
    'datetime_to_ts_millis',
    'ts_millis_to_datetime',
    'current_time_millis',
    'parse_absolute_time',
    'format_timestamp_millis',
    'time_diff_millis',
    'is_valid_timestamp_millis',
]

# Example usage and testing (for development/testing purposes)
if __name__ == "__main__":
    print("=== DataGuild Time Utilities Examples ===\n")

    # Example 1: Basic conversion
    print("Example 1: Basic datetime to timestamp conversion")
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    ts = datetime_to_ts_millis(dt)
    dt_back = ts_millis_to_datetime(ts)

    print(f"Original datetime: {dt}")
    print(f"Timestamp (ms): {ts}")
    print(f"Converted back: {dt_back}")
    print(f"Round trip successful: {dt == dt_back}")
    print()

    # Example 2: Current time
    print("Example 2: Current time operations")
    current_ts = current_time_millis()
    current_dt = ts_millis_to_datetime(current_ts)
    formatted = format_timestamp_millis(current_ts)

    print(f"Current timestamp: {current_ts}")
    print(f"Current datetime: {current_dt}")
    print(f"Formatted: {formatted}")
    print()

    # Example 3: Time parsing
    print("Example 3: Time string parsing")
    test_strings = [
        "2023-01-01T12:00:00Z",
        "1672574400",  # seconds
        "1672574400000",  # milliseconds
        "2023-01-01 12:00:00",
    ]

    for time_str in test_strings:
        try:
            parsed_dt = parse_absolute_time(time_str)
            print(f"'{time_str}' -> {parsed_dt}")
        except ValueError as e:
            print(f"'{time_str}' -> ERROR: {e}")
    print()

    # Example 4: Time difference calculation
    print("Example 4: Time difference calculation")
    start = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    end = datetime(2023, 1, 1, 13, 30, 0, tzinfo=timezone.utc)
    diff_ms = time_diff_millis(start, end)

    print(f"Start: {start}")
    print(f"End: {end}")
    print(f"Difference: {diff_ms}ms ({diff_ms / 1000 / 60:.1f} minutes)")
    print()

    # Example 5: Validation
    print("Example 5: Timestamp validation")
    test_timestamps = [
        1672574400000,  # Valid
        -1,  # Invalid (before epoch)
        9999999999999,  # Invalid (too far in future)
        "not_a_number",  # Invalid type
    ]

    for ts in test_timestamps:
        valid = is_valid_timestamp_millis(ts)
        print(f"{ts} -> Valid: {valid}")
