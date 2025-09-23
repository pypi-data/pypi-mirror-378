"""
DataGuild Advanced Domain Registry

Enterprise domain management system with hierarchical domains,
pattern matching, governance rules, and comprehensive validation.
"""

import re
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DomainMatchType(Enum):
    """Types of domain matching strategies."""
    PREFIX = "prefix"
    REGEX = "regex"
    EXACT = "exact"
    GLOB = "glob"
    CUSTOM = "custom"


@dataclass
class DomainRule:
    """Rule for domain assignment."""
    name: str
    match_type: DomainMatchType
    pattern: str
    priority: int = 1
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate rule after initialization."""
        if self.priority < 0:
            raise ValueError("Priority must be non-negative")

        # Compile regex pattern if applicable
        if self.match_type == DomainMatchType.REGEX:
            try:
                re.compile(self.pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{self.pattern}': {e}")

    def matches(self, entity_identifier: str) -> bool:
        """Check if rule matches entity identifier."""
        if not self.enabled:
            return False

        try:
            if self.match_type == DomainMatchType.PREFIX:
                return entity_identifier.startswith(self.pattern)

            elif self.match_type == DomainMatchType.EXACT:
                return entity_identifier == self.pattern

            elif self.match_type == DomainMatchType.REGEX:
                return bool(re.match(self.pattern, entity_identifier))

            elif self.match_type == DomainMatchType.GLOB:
                import fnmatch
                return fnmatch.fnmatch(entity_identifier, self.pattern)

            else:
                return False

        except Exception as e:
            logger.error(f"Error matching rule {self.name} against {entity_identifier}: {e}")
            return False


@dataclass
class Domain:
    """Domain with metadata and governance rules."""
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    rules: List[DomainRule] = field(default_factory=list)
    parent_domain: Optional[str] = None
    child_domains: Set[str] = field(default_factory=set)
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    governance_policies: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Validate domain after initialization."""
        if not self.name:
            raise ValueError("Domain name cannot be empty")

        # Validate domain name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', self.name):
            raise ValueError(f"Invalid domain name format: {self.name}")

    def add_rule(self, rule: DomainRule) -> None:
        """Add rule to domain."""
        # Check for duplicate rule names
        existing_names = {r.name for r in self.rules}
        if rule.name in existing_names:
            raise ValueError(f"Rule with name '{rule.name}' already exists")

        self.rules.append(rule)

        # Sort rules by priority (higher priority first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove rule by name."""
        initial_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        return len(self.rules) < initial_count

    def matches_entity(self, entity_identifier: str) -> Tuple[bool, Optional[DomainRule]]:
        """Check if domain matches entity, return matching rule."""
        for rule in self.rules:
            if rule.matches(entity_identifier):
                return True, rule
        return False, None

    def get_effective_properties(self) -> Dict[str, Any]:
        """Get effective properties including inherited ones."""
        # In a real implementation, this would merge with parent domain properties
        return self.properties.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "owner": self.owner,
            "rules": [
                {
                    "name": rule.name,
                    "match_type": rule.match_type.value,
                    "pattern": rule.pattern,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "metadata": rule.metadata
                }
                for rule in self.rules
            ],
            "parent_domain": self.parent_domain,
            "child_domains": list(self.child_domains),
            "properties": self.properties,
            "tags": list(self.tags),
            "governance_policies": self.governance_policies,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class DomainRegistry:
    """
    Advanced domain registry with hierarchical domains,
    pattern matching, and governance integration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.domains: Dict[str, Domain] = {}
        self.config = config or {}

        # Domain hierarchy tracking
        self.hierarchy: Dict[str, Set[str]] = {}  # parent -> children
        self.reverse_hierarchy: Dict[str, str] = {}  # child -> parent

        # Caching for performance
        self._match_cache: Dict[str, Optional[str]] = {}
        self._cache_enabled = self.config.get("enable_cache", True)
        self._max_cache_size = self.config.get("max_cache_size", 10000)

        # Statistics
        self.stats = {
            "domains_registered": 0,
            "entity_lookups": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "hierarchy_violations": 0
        }

        # Load initial configuration
        if "domains" in self.config:
            self._load_from_config(self.config["domains"])

    def register_domain(
            self,
            name: str,
            description: Optional[str] = None,
            owner: Optional[str] = None,
            parent_domain: Optional[str] = None,
            properties: Optional[Dict[str, Any]] = None
    ) -> Domain:
        """Register a new domain."""
        if name in self.domains:
            raise ValueError(f"Domain '{name}' already exists")

        # Validate parent domain exists
        if parent_domain and parent_domain not in self.domains:
            raise ValueError(f"Parent domain '{parent_domain}' does not exist")

        domain = Domain(
            name=name,
            description=description,
            owner=owner,
            parent_domain=parent_domain,
            properties=properties or {}
        )

        self.domains[name] = domain
        self.stats["domains_registered"] += 1

        # Update hierarchy
        if parent_domain:
            self.hierarchy.setdefault(parent_domain, set()).add(name)
            self.reverse_hierarchy[name] = parent_domain
            self.domains[parent_domain].child_domains.add(name)

        # Clear cache since domain structure changed
        self._clear_cache()

        logger.info(f"Registered domain: {name}")
        return domain

    def add_domain_rule(
            self,
            domain_name: str,
            rule_name: str,
            match_type: Union[DomainMatchType, str],
            pattern: str,
            priority: int = 1,
            metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add rule to domain."""
        if domain_name not in self.domains:
            raise ValueError(f"Domain '{domain_name}' does not exist")

        if isinstance(match_type, str):
            match_type = DomainMatchType(match_type.lower())

        rule = DomainRule(
            name=rule_name,
            match_type=match_type,
            pattern=pattern,
            priority=priority,
            metadata=metadata
        )

        self.domains[domain_name].add_rule(rule)

        # Clear cache since rules changed
        self._clear_cache()

        logger.info(f"Added rule '{rule_name}' to domain '{domain_name}'")

    def get_domain_for_entity(self, entity_identifier: str) -> Optional[str]:
        """Get domain for entity identifier."""
        self.stats["entity_lookups"] += 1

        # Check cache first
        if self._cache_enabled and entity_identifier in self._match_cache:
            self.stats["cache_hits"] += 1
            return self._match_cache[entity_identifier]

        self.stats["cache_misses"] += 1

        # Find matching domain
        best_match: Optional[Tuple[str, DomainRule]] = None

        for domain_name, domain in self.domains.items():
            matches, rule = domain.matches_entity(entity_identifier)
            if matches and rule:
                if best_match is None or rule.priority > best_match[1].priority:
                    best_match = (domain_name, rule)

        result = best_match[0] if best_match else None

        # Cache result
        if self._cache_enabled:
            self._cache_result(entity_identifier, result)

        if result:
            logger.debug(f"Matched entity '{entity_identifier}' to domain '{result}'")

        return result

    def get_domain(self, domain_name: str) -> Optional[Domain]:
        """Get domain by name."""
        return self.domains.get(domain_name)

    def list_domains(self) -> List[str]:
        """List all domain names."""
        return list(self.domains.keys())

    def get_domain_hierarchy(self) -> Dict[str, Any]:
        """Get complete domain hierarchy."""

        def build_tree(domain_name: str) -> Dict[str, Any]:
            domain = self.domains[domain_name]
            children = {}

            for child_name in domain.child_domains:
                children[child_name] = build_tree(child_name)

            return {
                "name": domain_name,
                "description": domain.description,
                "owner": domain.owner,
                "rule_count": len(domain.rules),
                "children": children
            }

        # Find root domains (no parent)
        root_domains = [name for name, domain in self.domains.items() if not domain.parent_domain]

        hierarchy = {}
        for root_name in root_domains:
            hierarchy[root_name] = build_tree(root_name)

        return hierarchy

    def validate_hierarchy(self) -> List[str]:
        """Validate domain hierarchy for cycles and orphans."""
        violations = []

        # Check for cycles
        visited = set()
        rec_stack = set()

        def has_cycle(domain_name: str) -> bool:
            if domain_name in rec_stack:
                return True
            if domain_name in visited:
                return False

            visited.add(domain_name)
            rec_stack.add(domain_name)

            domain = self.domains[domain_name]
            if domain.parent_domain and has_cycle(domain.parent_domain):
                return True

            rec_stack.remove(domain_name)
            return False

        for domain_name in self.domains:
            if domain_name not in visited and has_cycle(domain_name):
                violations.append(f"Cycle detected involving domain: {domain_name}")
                self.stats["hierarchy_violations"] += 1

        # Check for orphaned parent references
        for domain_name, domain in self.domains.items():
            if domain.parent_domain and domain.parent_domain not in self.domains:
                violations.append(f"Domain '{domain_name}' references non-existent parent '{domain.parent_domain}'")
                self.stats["hierarchy_violations"] += 1

        return violations

    def search_domains(
            self,
            query: Optional[str] = None,
            owner: Optional[str] = None,
            tags: Optional[Set[str]] = None
    ) -> List[Domain]:
        """Search domains by various criteria."""
        results = []

        for domain in self.domains.values():
            # Query match (name or description)
            if query:
                query_lower = query.lower()
                if (query_lower not in domain.name.lower() and
                        (not domain.description or query_lower not in domain.description.lower())):
                    continue

            # Owner match
            if owner and domain.owner != owner:
                continue

            # Tags match
            if tags and not tags.issubset(domain.tags):
                continue

            results.append(domain)

        return results

    def export_configuration(self) -> Dict[str, Any]:
        """Export domain configuration."""
        return {
            "version": "1.0",
            "domains": {
                name: domain.to_dict()
                for name, domain in self.domains.items()
            },
            "hierarchy": self.hierarchy,
            "statistics": self.get_statistics()
        }

    def import_configuration(self, config: Dict[str, Any]) -> None:
        """Import domain configuration."""
        if "domains" not in config:
            raise ValueError("Configuration must contain 'domains' section")

        # Clear existing domains
        self.domains.clear()
        self.hierarchy.clear()
        self.reverse_hierarchy.clear()
        self._clear_cache()

        # Load domains
        self._load_from_config(config["domains"])

        logger.info(f"Imported {len(self.domains)} domains from configuration")

    def _load_from_config(self, domains_config: Dict[str, Any]) -> None:
        """Load domains from configuration dictionary."""
        # First pass: create domains without parent relationships
        for domain_name, domain_config in domains_config.items():
            domain = Domain(
                name=domain_name,
                description=domain_config.get("description"),
                owner=domain_config.get("owner"),
                properties=domain_config.get("properties", {}),
                tags=set(domain_config.get("tags", [])),
                governance_policies=domain_config.get("governance_policies", {}),
                created_at=domain_config.get("created_at"),
                updated_at=domain_config.get("updated_at")
            )

            # Add rules
            for rule_config in domain_config.get("rules", []):
                rule = DomainRule(
                    name=rule_config["name"],
                    match_type=DomainMatchType(rule_config["match_type"]),
                    pattern=rule_config["pattern"],
                    priority=rule_config.get("priority", 1),
                    enabled=rule_config.get("enabled", True),
                    metadata=rule_config.get("metadata")
                )
                domain.add_rule(rule)

            self.domains[domain_name] = domain
            self.stats["domains_registered"] += 1

        # Second pass: establish parent-child relationships
        for domain_name, domain_config in domains_config.items():
            parent_domain = domain_config.get("parent_domain")
            if parent_domain:
                if parent_domain not in self.domains:
                    logger.warning(f"Parent domain '{parent_domain}' not found for '{domain_name}'")
                    continue

                self.domains[domain_name].parent_domain = parent_domain
                self.hierarchy.setdefault(parent_domain, set()).add(domain_name)
                self.reverse_hierarchy[domain_name] = parent_domain
                self.domains[parent_domain].child_domains.add(domain_name)

    def _cache_result(self, entity_identifier: str, domain: Optional[str]) -> None:
        """Cache domain lookup result."""
        if len(self._match_cache) >= self._max_cache_size:
            # Simple LRU: remove 10% of entries
            items_to_remove = list(self._match_cache.keys())[:self._max_cache_size // 10]
            for key in items_to_remove:
                del self._match_cache[key]

        self._match_cache[entity_identifier] = domain

    def _clear_cache(self) -> None:
        """Clear domain match cache."""
        self._match_cache.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_rules = sum(len(domain.rules) for domain in self.domains.values())
        enabled_rules = sum(
            sum(1 for rule in domain.rules if rule.enabled)
            for domain in self.domains.values()
        )

        return {
            **self.stats,
            "total_domains": len(self.domains),
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "cache_size": len(self._match_cache),
            "cache_hit_rate": (
                                      self.stats["cache_hits"] / max(1, self.stats["entity_lookups"])
                              ) * 100
        }
