"""
DataGuild string enumeration utility.

This module provides a string-based enumeration class that combines the
benefits of Python enums with string compatibility and serialization.
"""

import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union


class StrEnum(str, Enum):
    """
    String enumeration that can be used as both string and enum.

    This class provides enumeration functionality while maintaining
    string compatibility for serialization and comparison operations.
    """

    def __new__(cls, value: str) -> "StrEnum":
        """Create a new StrEnum instance."""
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj

    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value

    def __repr__(self) -> str:
        """Return a detailed representation of the enum."""
        return f"{self.__class__.__name__}.{self.name}"

    def __eq__(self, other: Any) -> bool:
        """Compare enum with other values (supports string comparison)."""
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        """Return hash of the enum value."""
        return hash(self.value)

    def __format__(self, format_spec: str) -> str:
        """Format the enum as a string."""
        return format(str(self), format_spec)

    @classmethod
    def _missing_(cls, value: Any) -> Optional["StrEnum"]:
        """Handle missing enum values gracefully."""
        if isinstance(value, str):
            # Try case-insensitive lookup
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None

    @classmethod
    def values(cls) -> List[str]:
        """
        Get all enum values as a list of strings.

        Returns:
            List of enum values
        """
        return [member.value for member in cls]

    @classmethod
    def names(cls) -> List[str]:
        """
        Get all enum names as a list of strings.

        Returns:
            List of enum names
        """
        return [member.name for member in cls]

    @classmethod
    def items(cls) -> List[tuple]:
        """
        Get all enum items as (name, value) tuples.

        Returns:
            List of (name, value) tuples
        """
        return [(member.name, member.value) for member in cls]

    @classmethod
    def from_string(cls, value: str, default: Optional["StrEnum"] = None) -> Optional["StrEnum"]:
        """
        Create enum from string value with optional default.

        Args:
            value: String value to convert
            default: Default enum to return if value not found

        Returns:
            Enum member or default
        """
        try:
            return cls(value)
        except ValueError:
            return default

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """
        Check if a string value is valid for this enum.

        Args:
            value: String value to check

        Returns:
            True if value is valid for this enum
        """
        try:
            cls(value)
            return True
        except ValueError:
            return False

    @classmethod
    def to_dict(cls) -> Dict[str, str]:
        """
        Convert enum to dictionary mapping names to values.

        Returns:
            Dictionary of name -> value mappings
        """
        return {member.name: member.value for member in cls}

    @classmethod
    def choices(cls) -> List[tuple]:
        """
        Get choices suitable for form fields (Django/Flask style).

        Returns:
            List of (value, display_name) tuples
        """
        return [(member.value, member.value.replace('_', ' ').title()) for member in cls]


# Compatibility function for Python < 3.11
if sys.version_info < (3, 11):
    # For older Python versions, we need to ensure proper MRO
    class StrEnum(str, Enum):
        """String enumeration for Python < 3.11."""

        def __new__(cls, value: str) -> "StrEnum":
            obj = str.__new__(cls, value)
            obj._value_ = value
            return obj

        def __str__(self) -> str:
            return self.value

        def __repr__(self) -> str:
            return f"{self.__class__.__name__}.{self.name}"

        @classmethod
        def values(cls) -> List[str]:
            return [member.value for member in cls]

        @classmethod
        def names(cls) -> List[str]:
            return [member.name for member in cls]

        @classmethod
        def items(cls) -> List[tuple]:
            return [(member.name, member.value) for member in cls]

        @classmethod
        def from_string(cls, value: str, default: Optional["StrEnum"] = None) -> Optional["StrEnum"]:
            try:
                return cls(value)
            except ValueError:
                return default

        @classmethod
        def is_valid(cls, value: str) -> bool:
            try:
                cls(value)
                return True
            except ValueError:
                return False

        @classmethod
        def to_dict(cls) -> Dict[str, str]:
            return {member.name: member.value for member in cls}

        @classmethod
        def choices(cls) -> List[tuple]:
            return [(member.value, member.value.replace('_', ' ').title()) for member in cls]


# Utility functions for working with StrEnum classes
def create_str_enum(name: str, values: Union[List[str], Dict[str, str]]) -> Type[StrEnum]:
    """
    Dynamically create a StrEnum class.

    Args:
        name: Name of the enum class
        values: List of values or dict of name->value mappings

    Returns:
        StrEnum class

    Example:
        >>> StatusEnum = create_str_enum('Status', ['ACTIVE', 'INACTIVE', 'PENDING'])
        >>> print(StatusEnum.ACTIVE)  # 'ACTIVE'
    """
    if isinstance(values, list):
        enum_dict = {value.upper().replace(' ', '_'): value for value in values}
    elif isinstance(values, dict):
        enum_dict = values
    else:
        raise ValueError("Values must be a list or dictionary")

    return StrEnum(name, enum_dict)


def enum_to_json_schema(enum_class: Type[StrEnum]) -> Dict[str, Any]:
    """
    Convert StrEnum to JSON schema definition.

    Args:
        enum_class: StrEnum class to convert

    Returns:
        JSON schema dictionary
    """
    return {
        "type": "string",
        "enum": enum_class.values(),
        "description": f"Valid values for {enum_class.__name__}"
    }


def validate_enum_value(enum_class: Type[StrEnum], value: Any, field_name: str = "value") -> str:
    """
    Validate and convert a value to enum string.

    Args:
        enum_class: StrEnum class to validate against
        value: Value to validate
        field_name: Name of field being validated (for error messages)

    Returns:
        Validated enum value as string

    Raises:
        ValueError: If value is not valid for the enum
    """
    if isinstance(value, enum_class):
        return value.value
    elif isinstance(value, str) and enum_class.is_valid(value):
        return value
    else:
        valid_values = ', '.join(enum_class.values())
        raise ValueError(f"Invalid {field_name}: '{value}'. Must be one of: {valid_values}")
