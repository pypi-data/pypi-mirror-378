"""
DataGuild Prefix Batch Builder

Intelligent batching system for organizing large numbers of object names
into efficient SQL query batches based on common prefixes. Critical for
performance when dealing with massive Snowflake schemas.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


@dataclass
class PrefixGroup:
    """
    Represents a group of names sharing a common prefix.

    Args:
        prefix: The common prefix string
        names: List of full names in this group
        exact_match: Whether to use exact matching instead of LIKE patterns
    """
    prefix: str
    names: List[str]
    exact_match: bool = False

    def __post_init__(self):
        """Validate the prefix group after initialization."""
        if not self.prefix:
            raise ValueError("Prefix cannot be empty")

        # Verify all names actually start with the prefix (unless exact match)
        if not self.exact_match:
            for name in self.names:
                if not name.startswith(self.prefix):
                    logger.warning(f"Name '{name}' does not start with prefix '{self.prefix}'")


def build_prefix_batches(
        names: List[str],
        max_batch_size: int = 1000,
        max_groups_in_batch: int = 5,
        min_prefix_length: int = 2,
        max_prefix_length: int = 20
) -> List[List[PrefixGroup]]:
    """
    Build intelligent batches of names grouped by common prefixes.

    This function analyzes a list of names and groups them by common prefixes,
    then organizes these groups into batches suitable for efficient SQL queries.

    Args:
        names: List of names to batch
        max_batch_size: Maximum number of total names per batch
        max_groups_in_batch: Maximum number of prefix groups per batch
        min_prefix_length: Minimum length of a prefix to consider
        max_prefix_length: Maximum length of a prefix to consider

    Returns:
        List of batches, where each batch is a list of PrefixGroups

    Example:
        names = ['table_a1', 'table_a2', 'table_b1', 'view_x', 'view_y']
        batches = build_prefix_batches(names, max_batch_size=3)
        # Result: [[PrefixGroup('table_a', ['table_a1', 'table_a2'])],
        #          [PrefixGroup('table_b', ['table_b1']), PrefixGroup('view_', ['view_x', 'view_y'])]]
    """
    if not names:
        return []

    logger.info(f"Building prefix batches for {len(names)} names")

    # Step 1: Find optimal prefixes using a trie-based approach
    prefix_groups = _find_optimal_prefixes(
        names, min_prefix_length, max_prefix_length
    )

    logger.info(f"Found {len(prefix_groups)} prefix groups")

    # Step 2: Organize groups into batches
    batches = _organize_into_batches(
        prefix_groups, max_batch_size, max_groups_in_batch
    )

    logger.info(f"Created {len(batches)} batches")

    return batches


def _find_optimal_prefixes(
        names: List[str],
        min_length: int,
        max_length: int
) -> List[PrefixGroup]:
    """
    Find optimal prefixes using a trie-based algorithm that maximizes
    the number of names covered by each prefix while minimizing overlaps.
    """
    # Build a trie of all names
    trie = _build_trie(names)

    # Find optimal cut points in the trie
    prefix_groups = []
    used_names: Set[str] = set()

    for length in range(min_length, min(max_length + 1, max(len(name) for name in names) + 1)):
        # Find prefixes of this length that cover multiple unused names
        length_prefixes = _find_prefixes_at_length(trie, length, names, used_names)

        for prefix, matching_names in length_prefixes.items():
            if len(matching_names) >= 2:  # Only create groups with multiple names
                available_names = [name for name in matching_names if name not in used_names]
                if len(available_names) >= 2:
                    prefix_groups.append(PrefixGroup(
                        prefix=prefix,
                        names=available_names,
                        exact_match=False
                    ))
                    used_names.update(available_names)

    # Handle remaining single names as exact matches
    remaining_names = [name for name in names if name not in used_names]
    for name in remaining_names:
        prefix_groups.append(PrefixGroup(
            prefix=name,
            names=[name],
            exact_match=True
        ))

    return prefix_groups


def _build_trie(names: List[str]) -> Dict:
    """Build a trie (prefix tree) from the list of names."""
    trie = {}

    for name in names:
        current = trie
        for char in name:
            if char not in current:
                current[char] = {}
            current = current[char]
        current['$END'] = name  # Mark end of word

    return trie


def _find_prefixes_at_length(
        trie: Dict,
        length: int,
        all_names: List[str],
        used_names: Set[str]
) -> Dict[str, List[str]]:
    """Find all prefixes of a specific length and their matching names."""
    prefixes = {}

    def traverse(node: Dict, current_prefix: str, depth: int):
        if depth == length:
            # We've reached the desired prefix length
            matching_names = []
            for name in all_names:
                if name.startswith(current_prefix) and name not in used_names:
                    matching_names.append(name)

            if len(matching_names) >= 2:
                prefixes[current_prefix] = matching_names
            return

        # Continue traversing
        for char, child_node in node.items():
            if char != '$END':
                traverse(child_node, current_prefix + char, depth + 1)

    traverse(trie, '', 0)
    return prefixes


def _organize_into_batches(
        prefix_groups: List[PrefixGroup],
        max_batch_size: int,
        max_groups_in_batch: int
) -> List[List[PrefixGroup]]:
    """
    Organize prefix groups into batches with size constraints.
    Uses a bin-packing-like algorithm to optimize batch utilization.
    """
    # Sort groups by size (largest first) for better bin packing
    sorted_groups = sorted(prefix_groups, key=lambda g: len(g.names), reverse=True)

    batches = []
    current_batch = []
    current_batch_size = 0

    for group in sorted_groups:
        group_size = len(group.names)

        # Check if we can add this group to the current batch
        if (len(current_batch) < max_groups_in_batch and
                current_batch_size + group_size <= max_batch_size):

            current_batch.append(group)
            current_batch_size += group_size
        else:
            # Start a new batch
            if current_batch:
                batches.append(current_batch)

            current_batch = [group]
            current_batch_size = group_size

    # Add the last batch if it's not empty
    if current_batch:
        batches.append(current_batch)

    return batches


def analyze_name_patterns(names: List[str]) -> Dict[str, any]:
    """
    Analyze naming patterns in a list of names to provide insights
    for optimization and debugging.

    Returns:
        Dictionary with analysis results including common patterns,
        average lengths, character distributions, etc.
    """
    if not names:
        return {}

    # Basic statistics
    lengths = [len(name) for name in names]

    # Find common patterns
    patterns = {}
    for name in names:
        # Extract patterns like prefixes ending with underscore
        match = re.match(r'^([a-zA-Z_]+[_])', name)
        if match:
            pattern = match.group(1)
            patterns[pattern] = patterns.get(pattern, 0) + 1

    # Character analysis
    all_chars = ''.join(names)
    char_freq = {}
    for char in all_chars:
        char_freq[char] = char_freq.get(char, 0) + 1

    return {
        'total_names': len(names),
        'avg_length': sum(lengths) / len(lengths),
        'min_length': min(lengths),
        'max_length': max(lengths),
        'common_patterns': dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]),
        'most_common_chars': dict(sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:10]),
        'has_underscores': sum(1 for name in names if '_' in name),
        'has_numbers': sum(1 for name in names if any(c.isdigit() for c in name)),
    }
