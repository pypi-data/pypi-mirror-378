"""
DataGuild Serialized LRU Cache

Advanced caching decorator with serialization support for complex arguments
and persistent storage capabilities. Essential for caching database queries
with complex parameter sets.
"""

import functools
import hashlib
import pickle
import sqlite3
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SerializedLRUCache:
    """
    Thread-safe LRU cache with serialization support for complex arguments.
    Supports both in-memory and persistent disk-based caching.
    """

    def __init__(
            self,
            maxsize: int = 128,
            typed: bool = False,
            persistent: bool = False,
            db_path: Optional[str] = None
    ):
        self.maxsize = maxsize
        self.typed = typed
        self.persistent = persistent
        self.db_path = db_path

        # In-memory cache
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.RLock()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._cache_gets = 0
        self._cache_sets = 0

        # Persistent storage
        self._db_connection: Optional[sqlite3.Connection] = None
        if persistent:
            self._init_persistent_storage()

    def _init_persistent_storage(self) -> None:
        """Initialize persistent SQLite storage for cache."""
        if not self.db_path:
            import tempfile
            self.db_path = tempfile.mktemp(suffix='.cache.db')

        self._db_connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=10.0
        )

        # Create cache table
        self._db_connection.execute('''
                                    CREATE TABLE IF NOT EXISTS cache_entries
                                    (
                                        key_hash
                                        TEXT
                                        PRIMARY
                                        KEY,
                                        value
                                        BLOB,
                                        timestamp
                                        REAL,
                                        access_count
                                        INTEGER
                                        DEFAULT
                                        0
                                    )
                                    ''')

        # Create index for performance
        self._db_connection.execute(
            'CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)'
        )

        self._db_connection.execute('PRAGMA journal_mode=WAL')
        self._db_connection.execute('PRAGMA synchronous=NORMAL')

        logger.info(f"Initialized persistent cache at {self.db_path}")

    def _serialize_key(self, args: Tuple, kwargs: Dict[str, Any]) -> str:
        """Create a serialized hash key from function arguments."""
        # Handle unhashable arguments by serializing them
        try:
            # Skip the first argument (self) for instance methods to avoid pickling unpickleable objects
            if len(args) > 0 and hasattr(args[0], '__class__'):
                # This is likely an instance method, skip the self parameter
                method_args = args[1:]
            else:
                method_args = args
                
            if self.typed:
                # Include type information in the key
                key_data = (
                    method_args,
                    tuple(sorted(kwargs.items())),
                    tuple(type(arg).__name__ for arg in method_args),
                    tuple(type(v).__name__ for v in kwargs.values())
                )
            else:
                key_data = (method_args, tuple(sorted(kwargs.items())))

            # Serialize and hash
            serialized = pickle.dumps(key_data, protocol=pickle.HIGHEST_PROTOCOL)
            return hashlib.sha256(serialized).hexdigest()

        except (TypeError, AttributeError, pickle.PicklingError) as e:
            logger.warning(f"Failed to serialize cache key: {e}")
            # Fallback to string representation, excluding self parameter
            if len(args) > 0 and hasattr(args[0], '__class__'):
                method_args = args[1:]
            else:
                method_args = args
            fallback_key = str((method_args, sorted(kwargs.items())))
            return hashlib.sha256(fallback_key.encode()).hexdigest()

    def get(self, key_hash: str) -> Tuple[bool, Any]:
        """
        Get value from cache.

        Returns:
            Tuple of (found, value) where found is True if key was in cache
        """
        current_time = time.time()

        with self._lock:
            self._cache_gets += 1

            # Check in-memory cache first
            if key_hash in self._cache:
                value, timestamp = self._cache[key_hash]
                # Move to end (most recently used)
                self._cache.move_to_end(key_hash)
                self._hits += 1
                return True, value

            # Check persistent storage if enabled
            if self.persistent and self._db_connection:
                try:
                    cursor = self._db_connection.execute(
                        'SELECT value, timestamp FROM cache_entries WHERE key_hash = ?',
                        (key_hash,)
                    )
                    row = cursor.fetchone()

                    if row:
                        value = pickle.loads(row[0])
                        timestamp = row[1]

                        # Update access count
                        self._db_connection.execute(
                            'UPDATE cache_entries SET access_count = access_count + 1 WHERE key_hash = ?',
                            (key_hash,)
                        )
                        self._db_connection.commit()

                        # Add back to memory cache
                        self._add_to_memory_cache(key_hash, value, timestamp)

                        self._hits += 1
                        return True, value

                except Exception as e:
                    logger.warning(f"Failed to read from persistent cache: {e}")

            self._misses += 1
            return False, None

    def set(self, key_hash: str, value: Any) -> None:
        """Set value in cache."""
        current_time = time.time()

        with self._lock:
            self._cache_sets += 1

            # Add to memory cache
            self._add_to_memory_cache(key_hash, value, current_time)

            # Add to persistent storage if enabled
            if self.persistent and self._db_connection:
                try:
                    serialized_value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                    self._db_connection.execute(
                        'INSERT OR REPLACE INTO cache_entries (key_hash, value, timestamp, access_count) VALUES (?, ?, ?, ?)',
                        (key_hash, serialized_value, current_time, 1)
                    )
                    self._db_connection.commit()
                except Exception as e:
                    logger.warning(f"Failed to write to persistent cache: {e}")

    def _add_to_memory_cache(self, key_hash: str, value: Any, timestamp: float) -> None:
        """Add item to in-memory cache with LRU eviction."""
        # Add to cache
        self._cache[key_hash] = (value, timestamp)

        # Evict oldest items if over capacity
        while len(self._cache) > self.maxsize:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

            if self.persistent and self._db_connection:
                try:
                    self._db_connection.execute('DELETE FROM cache_entries')
                    self._db_connection.commit()
                except Exception as e:
                    logger.warning(f"Failed to clear persistent cache: {e}")

            # Reset statistics
            self._hits = 0
            self._misses = 0
            self._cache_gets = 0
            self._cache_sets = 0

    def cache_info(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            info = {
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
                'current_size': len(self._cache),
                'max_size': self.maxsize,
                'cache_gets': self._cache_gets,
                'cache_sets': self._cache_sets,
                'persistent': self.persistent,
            }

            if self.persistent and self._db_connection:
                try:
                    cursor = self._db_connection.execute('SELECT COUNT(*) FROM cache_entries')
                    persistent_count = cursor.fetchone()[0]
                    info['persistent_entries'] = persistent_count
                except Exception:
                    info['persistent_entries'] = 'unknown'

            return info


def serialized_lru_cache(
        maxsize: int = 128,
        typed: bool = False,
        persistent: bool = False,
        db_path: Optional[str] = None
):
    """
    Decorator for caching function results with serialization support.

    Args:
        maxsize: Maximum number of entries to keep in memory
        typed: Include argument types in cache key
        persistent: Enable persistent disk-based caching
        db_path: Path for persistent cache database

    Example:
        @serialized_lru_cache(maxsize=256, persistent=True)
        def expensive_query(complex_args):
            return database.query(complex_args)
    """

    def decorator(func: Callable) -> Callable:
        cache = SerializedLRUCache(
            maxsize=maxsize,
            typed=typed,
            persistent=persistent,
            db_path=db_path
        )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key_hash = cache._serialize_key(args, kwargs)

            # Try to get from cache
            found, cached_value = cache.get(key_hash)
            if found:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key_hash, result)

            return result

        # Attach cache methods to wrapper
        wrapper.cache_clear = cache.clear
        wrapper.cache_info = cache.cache_info
        wrapper._cache = cache  # For debugging

        return wrapper

    return decorator


# Backward compatibility alias
lru_cache = serialized_lru_cache
