"""
DataGuild Metadata Classes - Common and Structured Property Definitions

Clean and simple implementations of core metadata classes for DataGuild's
Snowflake integration, following KISS principles.

Author: DataGuild Engineering Team
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class AuditStamp:
    """Represents when and by whom a metadata change was made."""
    time: int
    actor: str

    def __init__(self, time: Optional[int] = None, actor: str = "urn:li:corpuser:datahub"):
        """Initialize audit stamp with current time if not provided."""
        self.time = time if time is not None else int(datetime.now(timezone.utc).timestamp() * 1000)
        self.actor = actor


@dataclass
class StructuredPropertyDefinition:
    """Defines a structured property that can be applied to entities."""
    qualifiedName: str
    displayName: str
    valueType: str
    entityTypes: List[str]
    lastModified: AuditStamp
    description: Optional[str] = None

    def __post_init__(self):
        """Validate required fields."""
        if not self.qualifiedName:
            raise ValueError("qualifiedName is required")
        if not self.displayName:
            raise ValueError("displayName is required")
        if not self.valueType:
            raise ValueError("valueType is required")
        if not self.entityTypes:
            raise ValueError("entityTypes list cannot be empty")


# Utility functions for creating common metadata objects

def create_audit_stamp(actor: str = "urn:li:corpuser:datahub") -> AuditStamp:
    """Create an audit stamp with current timestamp."""
    return AuditStamp(actor=actor)


def create_string_property_definition(
        qualified_name: str,
        display_name: str,
        entity_types: List[str],
        description: Optional[str] = None
) -> StructuredPropertyDefinition:
    """Create a structured property definition for string values."""
    return StructuredPropertyDefinition(
        qualifiedName=qualified_name,
        displayName=display_name,
        valueType="urn:li:dataType:string",
        entityTypes=entity_types,
        lastModified=create_audit_stamp(),
        description=description
    )


def create_tag_property_definition(
        tag_name: str,
        tag_display_name: str
) -> StructuredPropertyDefinition:
    """Create a structured property definition for Snowflake tags."""
    return create_string_property_definition(
        qualified_name=f"snowflake.tag.{tag_name}",
        display_name=f"Snowflake Tag: {tag_display_name}",
        entity_types=[
            "urn:li:entityType:container",
            "urn:li:entityType:dataset",
            "urn:li:entityType:schemaField"
        ],
        description=f"Snowflake tag property for {tag_display_name}"
    )


# Common data types for value types
class DataTypes:
    """Common data type URNs for structured properties."""
    STRING = "urn:li:dataType:string"
    NUMBER = "urn:li:dataType:number"
    BOOLEAN = "urn:li:dataType:boolean"
    DATE = "urn:li:dataType:date"
    URN = "urn:li:dataType:urn"


# Common entity types
class EntityTypes:
    """Common entity type URNs."""
    CONTAINER = "urn:li:entityType:container"
    DATASET = "urn:li:entityType:dataset"
    SCHEMA_FIELD = "urn:li:entityType:schemaField"
    DASHBOARD = "urn:li:entityType:dashboard"
    CHART = "urn:li:entityType:chart"


# Validation helpers

def validate_urn_format(urn: str) -> bool:
    """Validate basic URN format."""
    return urn.startswith("urn:li:") and len(urn.split(":")) >= 3


def validate_qualified_name(name: str) -> bool:
    """Validate qualified name format."""
    return bool(name and len(name.strip()) > 0 and not name.startswith(" "))


def validate_entity_types(entity_types: List[str]) -> bool:
    """Validate that all entity types are properly formatted URNs."""
    if not entity_types:
        return False

    return all(validate_urn_format(et) for et in entity_types)
