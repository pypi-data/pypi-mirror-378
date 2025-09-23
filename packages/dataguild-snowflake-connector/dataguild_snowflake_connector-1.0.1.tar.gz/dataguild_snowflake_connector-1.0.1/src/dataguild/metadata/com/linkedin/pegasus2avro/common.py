"""
Common metadata models and base classes for DataGuild.

This module provides foundational metadata structures that are shared across
different entity types in the DataGuild metadata management system.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class FabricType(str, Enum):
    """Enumeration of fabric types for data environments."""
    DEV = "DEV"
    TEST = "TEST"
    STAGING = "STAGING"
    EI = "EI"
    PRE = "PRE"
    PROD = "PROD"
    CORP = "CORP"


class OwnershipType(str, Enum):
    """Enumeration of ownership types."""
    TECHNICAL_OWNER = "TECHNICAL_OWNER"
    BUSINESS_OWNER = "BUSINESS_OWNER"
    DATA_STEWARD = "DATA_STEWARD"
    NONE = "NONE"


class DatasetLineageType(str, Enum):
    """Types of dataset lineage relationships."""
    COPY = "COPY"
    TRANSFORMED = "TRANSFORMED"
    VIEW = "VIEW"


class LineageDirection(str, Enum):
    """Direction of lineage relationships."""
    UPSTREAM = "UPSTREAM"
    DOWNSTREAM = "DOWNSTREAM"


class Status(str, Enum):
    """General status enumeration."""
    OK = "OK"
    FAILED = "FAILED"
    REMOVED = "REMOVED"


class AuditStamp(BaseModel):
    """
    Audit information for tracking changes to metadata.

    Records who made changes and when they occurred.
    """

    time: int = Field(description="Timestamp in milliseconds when the change occurred")
    actor: str = Field(description="URN of the actor who made the change")
    impersonator: Optional[str] = Field(
        default=None,
        description="URN of the impersonator if applicable"
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional message describing the change"
    )

    @classmethod
    def create_now(cls, actor: str, message: Optional[str] = None) -> "AuditStamp":
        """Create audit stamp with current timestamp."""
        return cls(
            time=int(datetime.now().timestamp() * 1000),
            actor=actor,
            message=message
        )


class DataPlatformInstance(BaseModel):
    """
    Information about a specific data platform instance.

    Enables support for multiple instances of the same platform type.
    """

    platform: str = Field(description="URN of the data platform")
    instance: Optional[str] = Field(
        default=None,
        description="Optional instance identifier for multi-instance platforms"
    )


class Owner(BaseModel):
    """Individual owner information."""

    owner: str = Field(description="URN of the owner (user or group)")
    type: OwnershipType = Field(description="Type of ownership")
    source: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Source information for the ownership"
    )


class Ownership(BaseModel):
    """
    Ownership information for an entity.

    Tracks who owns, manages, or is responsible for a data asset.
    """

    owners: List[Owner] = Field(description="List of owners")
    lastModified: AuditStamp = Field(description="Audit stamp for last modification")

    def add_owner(self, owner_urn: str, ownership_type: OwnershipType) -> None:
        """Add a new owner to the ownership list."""
        owner = Owner(owner=owner_urn, type=ownership_type)
        self.owners.append(owner)

    def get_owners_by_type(self, ownership_type: OwnershipType) -> List[Owner]:
        """Get all owners of a specific type."""
        return [owner for owner in self.owners if owner.type == ownership_type]


class TagAssociation(BaseModel):
    """Association between an entity and a tag."""

    tag: str = Field(description="URN of the tag")
    context: Optional[str] = Field(
        default=None,
        description="Optional context for the tag association"
    )
    attribution: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Attribution information for the tag"
    )


class GlobalTags(BaseModel):
    """
    Global tags applied to an entity.

    Provides a way to categorize and label entities with business-relevant tags.
    """

    tags: List[TagAssociation] = Field(description="List of tag associations")

    def add_tag(self, tag_urn: str, context: Optional[str] = None) -> None:
        """Add a tag to the entity."""
        tag_association = TagAssociation(tag=tag_urn, context=context)
        self.tags.append(tag_association)

    def has_tag(self, tag_urn: str) -> bool:
        """Check if entity has a specific tag."""
        return any(tag.tag == tag_urn for tag in self.tags)

    def remove_tag(self, tag_urn: str) -> None:
        """Remove a tag from the entity."""
        self.tags = [tag for tag in self.tags if tag.tag != tag_urn]


class GlossaryTermAssociation(BaseModel):
    """Association between an entity and a glossary term."""

    urn: str = Field(description="URN of the glossary term")
    context: Optional[str] = Field(
        default=None,
        description="Optional context for the term association"
    )
    attribution: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Attribution information for the term"
    )


class GlossaryTerms(BaseModel):
    """
    Glossary terms associated with an entity.

    Links entities to business glossary terms for better understanding
    and governance of data assets.
    """

    terms: List[GlossaryTermAssociation] = Field(description="List of glossary term associations")
    auditStamp: AuditStamp = Field(description="Audit stamp for the associations")

    def add_term(self, term_urn: str, context: Optional[str] = None) -> None:
        """Add a glossary term to the entity."""
        term_association = GlossaryTermAssociation(urn=term_urn, context=context)
        self.terms.append(term_association)

    def has_term(self, term_urn: str) -> bool:
        """Check if entity has a specific glossary term."""
        return any(term.urn == term_urn for term in self.terms)


class StringMapEntry(BaseModel):
    """Entry in a string-to-string map."""

    key: str = Field(description="Map key")
    value: str = Field(description="Map value")


class StringMap(BaseModel):
    """String-to-string map representation."""

    entries: List[StringMapEntry] = Field(description="Map entries")

    def to_dict(self) -> Dict[str, str]:
        """Convert to Python dictionary."""
        return {entry.key: entry.value for entry in self.entries}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "StringMap":
        """Create from Python dictionary."""
        entries = [StringMapEntry(key=k, value=v) for k, v in data.items()]
        return cls(entries=entries)


class ChangeAuditStamps(BaseModel):
    """Comprehensive audit information for entity changes."""

    created: AuditStamp = Field(description="Audit stamp for entity creation")
    lastModified: AuditStamp = Field(description="Audit stamp for last modification")
    deleted: Optional[AuditStamp] = Field(
        default=None,
        description="Audit stamp for entity deletion"
    )


class Cost(BaseModel):
    """Cost information for a data asset."""

    costType: str = Field(description="Type of cost (e.g., 'COMPUTE', 'STORAGE')")
    cost: float = Field(description="Cost amount")
    unit: str = Field(description="Cost unit (e.g., 'USD', 'CREDITS')")


class CostInfo(BaseModel):
    """Comprehensive cost information."""

    costs: List[Cost] = Field(description="List of cost breakdowns")
    totalCost: Optional[float] = Field(
        default=None,
        description="Total cost across all cost types"
    )


class DatasetUrn(BaseModel):
    """URN for a dataset entity."""

    urn: str = Field(description="Dataset URN")

    def __str__(self) -> str:
        return self.urn


class AssertionUrn(BaseModel):
    """URN for an assertion entity."""

    urn: str = Field(description="Assertion URN")

    def __str__(self) -> str:
        return self.urn


class TagUrn(BaseModel):
    """URN for a tag entity."""

    urn: str = Field(description="Tag URN")

    def __str__(self) -> str:
        return self.urn


# Utility functions for common operations

def create_audit_stamp(actor: str, message: Optional[str] = None) -> AuditStamp:
    """Create an audit stamp with current timestamp."""
    return AuditStamp.create_now(actor, message)


def create_data_platform_instance(
        platform: str,
        instance: Optional[str] = None
) -> DataPlatformInstance:
    """Create a data platform instance."""
    return DataPlatformInstance(platform=platform, instance=instance)


def create_ownership(owners: List[tuple], actor: str) -> Ownership:
    """
    Create ownership with list of (owner_urn, ownership_type) tuples.

    Args:
        owners: List of (owner_urn, ownership_type) tuples
        actor: Actor making the ownership assignment

    Returns:
        Ownership instance
    """
    owner_objects = [
        Owner(owner=owner_urn, type=ownership_type)
        for owner_urn, ownership_type in owners
    ]

    return Ownership(
        owners=owner_objects,
        lastModified=create_audit_stamp(actor)
    )


def create_global_tags(tag_urns: List[str]) -> GlobalTags:
    """Create global tags from list of tag URNs."""
    tag_associations = [TagAssociation(tag=tag_urn) for tag_urn in tag_urns]
    return GlobalTags(tags=tag_associations)


def create_glossary_terms(term_urns: List[str], actor: str) -> GlossaryTerms:
    """Create glossary terms from list of term URNs."""
    term_associations = [
        GlossaryTermAssociation(urn=term_urn)
        for term_urn in term_urns
    ]

    return GlossaryTerms(
        terms=term_associations,
        auditStamp=create_audit_stamp(actor)
    )
