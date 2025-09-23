"""
DataGuild lossy collections utilities.

This module provides memory-efficient collections that automatically
evict old entries when size limits are reached.
"""

import logging
from collections import OrderedDict
from typing import Any, Dict, Iterator, KeysView, Optional, ValuesView, ItemsView, Union, Callable, Tuple, List
from threading import Lock
from datetime import datetime

logger = logging.getLogger(__name__)


class EvictionPolicy:
    """Eviction policy enum for lossy collections."""
    LRU = "lru"  # Least Recently Used
    FIFO = "fifo"  # First In, First Out
    CUSTOM = "custom"  # Custom callback-based


class LossyDict(OrderedDict):
    """
    A dictionary with a maximum size that evicts entries when limit is exceeded.

    This collection is useful for caches and buffers where memory usage needs
    to be bounded and older entries can be safely discarded.
    """

    def __init__(
            self,
            max_size: int,
            eviction_callback: Optional[Callable[[Any, Any], None]] = None,
            eviction_policy: str = EvictionPolicy.LRU
    ):
        """
        Initialize LossyDict.

        Args:
            max_size: Maximum number of entries to store
            eviction_callback: Optional callback function called when items are evicted
            eviction_policy: Eviction strategy ('lru', 'fifo', 'custom')
        """
        super().__init__()
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self.max_size = max_size
        self.eviction_callback = eviction_callback
        self.eviction_policy = eviction_policy
        self._lock = Lock()  # Thread safety
        self._evicted_count = 0
        self._access_count = 0
        self._creation_time = datetime.now()

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set item with automatic eviction if size limit exceeded."""
        with self._lock:
            # If key already exists, just update it
            if key in self:
                super().__setitem__(key, value)
                # Move to end if LRU policy
                if self.eviction_policy == EvictionPolicy.LRU:
                    self.move_to_end(key)
                return

            # Check if we need to evict items
            while len(self) >= self.max_size:
                self._evict_one()

            # Add the new item
            super().__setitem__(key, value)

    def __getitem__(self, key: Any) -> Any:
        """Get item and optionally move to end (mark as recently used)."""
        with self._lock:
            self._access_count += 1
            value = super().__getitem__(key)

            # Move to end if LRU policy
            if self.eviction_policy == EvictionPolicy.LRU:
                self.move_to_end(key)

            return value

    def __delitem__(self, key: Any) -> None:
        """Delete item."""
        with self._lock:
            super().__delitem__(key)

    def __contains__(self, key: Any) -> bool:
        """Check if key exists."""
        with self._lock:
            return super().__contains__(key)

    def __len__(self) -> int:
        """Get current size."""
        with self._lock:
            return super().__len__()

    def __repr__(self) -> str:
        """String representation."""
        with self._lock:
            items_preview = dict(list(self.items())[:3])  # Show first 3 items
            suffix = f", ...+{len(self) - 3}" if len(self) > 3 else ""
            return (f"LossyDict(max_size={self.max_size}, size={len(self)}, "
                    f"evicted={self._evicted_count}, policy={self.eviction_policy}, "
                    f"items={items_preview}{suffix})")

    def _evict_one(self) -> Optional[Tuple[Any, Any]]:
        """Evict one item based on the eviction policy."""
        if not self:
            return None

        if self.eviction_policy == EvictionPolicy.FIFO:
            # Remove the first (oldest) item
            key = next(iter(self))
        elif self.eviction_policy == EvictionPolicy.LRU:
            # Remove the first (least recently used) item
            key = next(iter(self))
        else:
            # Default to FIFO
            key = next(iter(self))

        value = self[key]
        del self[key]
        self._evicted_count += 1

        # Call eviction callback if provided
        if self.eviction_callback:
            try:
                self.eviction_callback(key, value)
            except Exception as e:
                logger.warning(f"Eviction callback failed: {e}")

        return (key, value)

    def get(self, key: Any, default: Any = None, mark_accessed: bool = True) -> Any:
        """
        Get value with optional access tracking.

        Args:
            key: Key to lookup
            default: Default value if key not found
            mark_accessed: Whether to mark key as recently accessed (for LRU)

        Returns:
            Value for key or default
        """
        with self._lock:
            if key not in self:
                return default

            self._access_count += 1
            value = super().__getitem__(key)

            if mark_accessed and self.eviction_policy == EvictionPolicy.LRU:
                self.move_to_end(key)

            return value

    def put(self, key: Any, value: Any) -> Optional[Tuple[Any, Any]]:
        """
        Put key-value pair and return evicted item if any.

        Args:
            key: Key to store
            value: Value to store

        Returns:
            Tuple of (evicted_key, evicted_value) if eviction occurred, None otherwise
        """
        with self._lock:
            evicted = None

            # Check if we need to evict (and key is new)
            if key not in self and len(self) >= self.max_size:
                evicted = self._evict_one()

            # Add/update the item
            super().__setitem__(key, value)
            if self.eviction_policy == EvictionPolicy.LRU:
                self.move_to_end(key)

            return evicted

    def peek(self, key: Any, default: Any = None) -> Any:
        """Get value without marking as accessed."""
        return self.get(key, default, mark_accessed=False)

    def peek_oldest(self) -> Optional[Tuple[Any, Any]]:
        """Peek at the oldest key-value pair without removing it."""
        with self._lock:
            if not self:
                return None
            oldest_key = next(iter(self))
            return (oldest_key, super().__getitem__(oldest_key))

    def peek_newest(self) -> Optional[Tuple[Any, Any]]:
        """Peek at the newest key-value pair without removing it."""
        with self._lock:
            if not self:
                return None
            newest_key = next(reversed(self))
            return (newest_key, super().__getitem__(newest_key))

    def evict(self, count: int = 1) -> List[Tuple[Any, Any]]:
        """
        Manually evict specified number of entries.

        Args:
            count: Number of entries to evict

        Returns:
            List of (key, value) tuples that were evicted
        """
        evicted = []
        with self._lock:
            for _ in range(min(count, len(self))):
                result = self._evict_one()
                if result:
                    evicted.append(result)

        return evicted

    def clear_with_callback(self) -> int:
        """Clear all items, calling eviction callback for each."""
        with self._lock:
            count = len(self)
            if self.eviction_callback:
                for key, value in list(self.items()):
                    try:
                        self.eviction_callback(key, value)
                    except Exception as e:
                        logger.warning(f"Eviction callback failed during clear: {e}")

            self.clear()
            self._evicted_count += count
            return count

    def resize(self, new_max_size: int) -> List[Tuple[Any, Any]]:
        """
        Resize the dictionary and evict items if necessary.

        Args:
            new_max_size: New maximum size

        Returns:
            List of (key, value) tuples that were evicted due to resize
        """
        if new_max_size <= 0:
            raise ValueError("new_max_size must be positive")

        with self._lock:
            old_max_size = self.max_size
            self.max_size = new_max_size

            evicted = []
            # Evict excess items if new size is smaller
            while len(self) > new_max_size:
                result = self._evict_one()
                if result:
                    evicted.append(result)

            logger.info(f"Resized LossyDict from {old_max_size} to {new_max_size}, evicted {len(evicted)} items")
            return evicted

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the dictionary usage."""
        with self._lock:
            uptime = (datetime.now() - self._creation_time).total_seconds()

            return {
                "max_size": self.max_size,
                "current_size": len(self),
                "utilization_percent": (len(self) / self.max_size) * 100 if self.max_size > 0 else 0,
                "total_evicted": self._evicted_count,
                "total_accesses": self._access_count,
                "eviction_policy": self.eviction_policy,
                "has_eviction_callback": self.eviction_callback is not None,
                "is_full": len(self) >= self.max_size,
                "uptime_seconds": uptime,
                "accesses_per_second": self._access_count / uptime if uptime > 0 else 0,
            }

    def copy(self) -> "LossyDict":
        """Create a copy of the LossyDict."""
        with self._lock:
            new_dict = LossyDict(
                self.max_size,
                self.eviction_callback,
                self.eviction_policy
            )
            new_dict.update(self)
            new_dict._evicted_count = self._evicted_count
            new_dict._access_count = self._access_count
            return new_dict


# Specialized lossy collections
class LossyList:
    """A list with maximum size that evicts oldest entries."""

    def __init__(self, max_size: int):
        """Initialize LossyList with maximum size."""
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self.max_size = max_size
        self._items = []
        self._lock = Lock()

    def append(self, item: Any) -> Optional[Any]:
        """
        Append item and return evicted item if any.

        Args:
            item: Item to append

        Returns:
            Evicted item if list was full, None otherwise
        """
        with self._lock:
            evicted = None
            if len(self._items) >= self.max_size:
                evicted = self._items.pop(0)

            self._items.append(item)
            return evicted

    def __len__(self) -> int:
        """Get current length."""
        with self._lock:
            return len(self._items)

    def __getitem__(self, index: int) -> Any:
        """Get item by index."""
        with self._lock:
            return self._items[index]

    def __repr__(self) -> str:
        """String representation."""
        with self._lock:
            return f"LossyList(max_size={self.max_size}, size={len(self._items)})"


# Export all classes
__all__ = [
    'LossyDict',
    'LossyList',
    'EvictionPolicy',
]
