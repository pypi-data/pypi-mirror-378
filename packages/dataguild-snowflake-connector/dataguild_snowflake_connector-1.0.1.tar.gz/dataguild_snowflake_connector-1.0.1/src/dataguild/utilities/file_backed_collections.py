"""
DataGuild File-Backed Collections

Memory-efficient collections that automatically spill to disk when dealing
with large datasets that cannot fit in memory. Essential for enterprise-scale
data processing where schemas may contain hundreds of thousands of objects.
"""

import os
import pickle
import sqlite3
import tempfile
import threading
import weakref
from collections.abc import MutableMapping
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class FileBackedDict(MutableMapping):
    """
    A dictionary-like object that automatically spills to SQLite when memory usage
    becomes too large. Provides transparent disk backing for massive datasets.

    Features:
    - Automatic memory to disk spillover
    - Thread-safe operations
    - Transparent dict-like interface
    - Automatic cleanup on deletion
    - Compression support for large values
    """

    def __init__(
            self,
            memory_threshold: int = 10000,
            temp_dir: Optional[str] = None,
            compress_values: bool = True
    ):
        self._memory_threshold = memory_threshold
        self._compress_values = compress_values
        self._memory_dict: Dict[str, Any] = {}
        self._spilled_to_disk = False
        self._db_path: Optional[str] = None
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()

        # Create temp directory if not specified
        if temp_dir:
            os.makedirs(temp_dir, exist_ok=True)
            self._temp_dir = temp_dir
        else:
            self._temp_dir = tempfile.gettempdir()

        # Register cleanup on deletion
        self._finalizer = weakref.finalize(self, self._cleanup_files, self._db_path)

    def _should_spill_to_disk(self) -> bool:
        """Check if we should spill data to disk."""
        return len(self._memory_dict) >= self._memory_threshold

    def _init_disk_storage(self) -> None:
        """Initialize SQLite database for disk storage."""
        if self._spilled_to_disk:
            return

        # Create temporary SQLite database
        fd, self._db_path = tempfile.mkstemp(
            suffix='.db',
            prefix='dataguild_cache_',
            dir=self._temp_dir
        )
        os.close(fd)  # Close file descriptor, SQLite will handle the file

        self._connection = sqlite3.connect(
            self._db_path,
            check_same_thread=False,
            timeout=30.0
        )

        # Create table with optimized schema
        self._connection.execute('''
                                 CREATE TABLE cache
                                 (
                                     key   TEXT PRIMARY KEY,
                                     value BLOB,
                                     size  INTEGER
                                 )
                                 ''')

        # Create index for performance
        self._connection.execute('CREATE INDEX idx_key ON cache(key)')
        self._connection.execute('PRAGMA journal_mode=WAL')
        self._connection.execute('PRAGMA synchronous=NORMAL')
        self._connection.execute('PRAGMA cache_size=10000')

        # Move existing memory data to disk
        for key, value in self._memory_dict.items():
            self._store_to_disk(key, value)

        self._memory_dict.clear()
        self._spilled_to_disk = True

        logger.info(f"Spilled FileBackedDict to disk: {self._db_path}")

    def _store_to_disk(self, key: str, value: Any) -> None:
        """Store a key-value pair to disk."""
        if self._compress_values:
            import gzip
            serialized = gzip.compress(pickle.dumps(value))
        else:
            serialized = pickle.dumps(value)

        size = len(serialized)

        self._connection.execute(
            'INSERT OR REPLACE INTO cache (key, value, size) VALUES (?, ?, ?)',
            (key, serialized, size)
        )
        self._connection.commit()

    def _load_from_disk(self, key: str) -> Any:
        """Load a value from disk."""
        cursor = self._connection.execute(
            'SELECT value FROM cache WHERE key = ?', (key,)
        )
        row = cursor.fetchone()

        if row is None:
            raise KeyError(key)

        serialized_value = row[0]

        if self._compress_values:
            import gzip
            return pickle.loads(gzip.decompress(serialized_value))
        else:
            return pickle.loads(serialized_value)

    def __setitem__(self, key: str, value: Any) -> None:
        with self._lock:
            if not self._spilled_to_disk:
                if self._should_spill_to_disk():
                    self._init_disk_storage()
                    self._store_to_disk(key, value)
                else:
                    self._memory_dict[key] = value
            else:
                self._store_to_disk(key, value)

    def __getitem__(self, key: str) -> Any:
        with self._lock:
            if not self._spilled_to_disk:
                return self._memory_dict[key]
            else:
                return self._load_from_disk(key)

    def __delitem__(self, key: str) -> None:
        with self._lock:
            if not self._spilled_to_disk:
                del self._memory_dict[key]
            else:
                cursor = self._connection.execute(
                    'DELETE FROM cache WHERE key = ?', (key,)
                )
                if cursor.rowcount == 0:
                    raise KeyError(key)
                self._connection.commit()

    def __contains__(self, key: object) -> bool:
        with self._lock:
            if not self._spilled_to_disk:
                return key in self._memory_dict
            else:
                cursor = self._connection.execute(
                    'SELECT 1 FROM cache WHERE key = ? LIMIT 1', (str(key),)
                )
                return cursor.fetchone() is not None

    def __iter__(self) -> Iterator[str]:
        with self._lock:
            if not self._spilled_to_disk:
                return iter(self._memory_dict)
            else:
                cursor = self._connection.execute('SELECT key FROM cache')
                return iter(row[0] for row in cursor.fetchall())

    def __len__(self) -> int:
        with self._lock:
            if not self._spilled_to_disk:
                return len(self._memory_dict)
            else:
                cursor = self._connection.execute('SELECT COUNT(*) FROM cache')
                return cursor.fetchone()[0]

    def keys(self):
        """Return a view of the dictionary's keys."""
        return self.__iter__()

    def items(self):
        """Return a view of the dictionary's (key, value) pairs."""
        with self._lock:
            if not self._spilled_to_disk:
                return self._memory_dict.items()
            else:
                cursor = self._connection.execute('SELECT key, value FROM cache')
                for key, serialized_value in cursor.fetchall():
                    if self._compress_values:
                        import gzip
                        value = pickle.loads(gzip.decompress(serialized_value))
                    else:
                        value = pickle.loads(serialized_value)
                    yield key, value

    def get_disk_usage(self) -> int:
        """Get disk usage in bytes."""
        if not self._spilled_to_disk or not self._db_path:
            return 0
        try:
            return os.path.getsize(self._db_path)
        except OSError:
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return {
            'spilled_to_disk': self._spilled_to_disk,
            'memory_threshold': self._memory_threshold,
            'total_items': len(self),
            'disk_usage_bytes': self.get_disk_usage(),
            'db_path': self._db_path
        }

    @staticmethod
    def _cleanup_files(db_path: Optional[str]) -> None:
        """Clean up temporary files."""
        if db_path and os.path.exists(db_path):
            try:
                os.unlink(db_path)
                # Also try to clean up WAL and SHM files
                for suffix in ['-wal', '-shm']:
                    wal_file = db_path + suffix
                    if os.path.exists(wal_file):
                        os.unlink(wal_file)
            except OSError:
                pass

    def close(self) -> None:
        """Explicitly close and clean up resources."""
        with self._lock:
            if self._connection:
                self._connection.close()
                self._connection = None

            if self._db_path:
                self._cleanup_files(self._db_path)
                self._db_path = None

            self._memory_dict.clear()
            self._spilled_to_disk = False


class ConnectionWrapper:
    """Wrapper for database connections with automatic resource management."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None

    def __enter__(self):
        self._connection = sqlite3.connect(self.db_path)
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            self._connection.close()


class FileBackedList:
    """A list-like object that spills to disk when memory usage becomes large."""

    def __init__(self, connection_wrapper: ConnectionWrapper):
        self._connection_wrapper = connection_wrapper
        self._memory_list: List[Any] = []
        self._spilled = False
        self._table_created = False

    def _ensure_table(self, connection):
        """Ensure the storage table exists."""
        if not self._table_created:
            connection.execute('''
                               CREATE TABLE IF NOT EXISTS list_storage
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   value
                                   BLOB
                               )
                               ''')
            self._table_created = True

    def append(self, item: Any) -> None:
        """Add an item to the list."""
        if not self._spilled and len(self._memory_list) < 10000:
            self._memory_list.append(item)
        else:
            # Spill to disk
            with self._connection_wrapper as conn:
                self._ensure_table(conn)

                if not self._spilled:
                    # Move existing items to disk
                    for existing_item in self._memory_list:
                        serialized = pickle.dumps(existing_item)
                        conn.execute('INSERT INTO list_storage (value) VALUES (?)', (serialized,))
                    self._memory_list.clear()
                    self._spilled = True

                # Add new item
                serialized = pickle.dumps(item)
                conn.execute('INSERT INTO list_storage (value) VALUES (?)', (serialized,))
                conn.commit()

    def __iter__(self):
        """Iterate over all items."""
        if not self._spilled:
            return iter(self._memory_list)
        else:
            return self._disk_iterator()

    def _disk_iterator(self):
        """Iterator for disk-backed items."""
        with self._connection_wrapper as conn:
            cursor = conn.execute('SELECT value FROM list_storage ORDER BY id')
            for row in cursor:
                yield pickle.loads(row[0])
