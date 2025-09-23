"""
DataGuild Closeable interface for resource management.

This module provides the Closeable interface and related utilities for proper
resource cleanup in DataGuild ingestion pipelines and data processing components.
"""

import logging
import threading
import weakref
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Set, Type, Union

logger = logging.getLogger(__name__)

# Global registry for tracking open resources (for debugging and monitoring)
_open_resources: Set[weakref.ReferenceType] = set()
_registry_lock = threading.Lock()


class Closeable(ABC):
    """
    Abstract base class for resources that can be closed.

    This interface defines a contract for releasing resources such as
    file handles, network connections, database connections, etc.

    All implementations should ensure:
    - The close() method is idempotent (safe to call multiple times)
    - Resources are properly released
    - The object is marked as closed after cleanup
    - Thread-safety if the resource may be accessed concurrently

    Examples:
        >>> class MyResource(Closeable):
        ...     def __init__(self):
        ...         self._closed = False
        ...         self._connection = create_connection()
        ...
        ...     def close(self) -> None:
        ...         if not self._closed:
        ...             self._connection.close()
        ...             self._closed = True
        ...
        ...     def is_closed(self) -> bool:
        ...         return self._closed

        >>> with MyResource() as resource:
        ...     # Use resource here
        ...     pass
        # Resource is automatically closed
    """

    def __init__(self):
        """Initialize the closeable resource."""
        self._register_resource()

    @abstractmethod
    def close(self) -> None:
        """
        Close this resource and release any system resources associated with it.

        This method should be idempotent - calling it multiple times should
        have no additional effect after the first call.

        Implementations should:
        1. Check if already closed to avoid duplicate work
        2. Release all held resources (files, connections, etc.)
        3. Mark the resource as closed
        4. Handle any cleanup exceptions gracefully

        Raises:
            Exception: May raise exceptions related to resource cleanup,
                      but should attempt to clean up as much as possible
        """
        pass

    def is_closed(self) -> bool:
        """
        Check if this resource has been closed.

        Returns:
            True if the resource is closed, False otherwise

        Note:
            Default implementation returns False. Subclasses should override
            this method to provide accurate closed state information.
        """
        return False

    def __enter__(self):
        """Context manager entry - return self for 'with' statements."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close the resource."""
        try:
            self.close()
        except Exception as e:
            logger.warning(f"Error closing resource {self.__class__.__name__}: {e}")
        return False  # Don't suppress exceptions

    def __del__(self):
        """Destructor - attempt to close resource if not already closed."""
        try:
            if not self.is_closed():
                logger.warning(
                    f"Resource {self.__class__.__name__} was not explicitly closed. "
                    f"Consider using a 'with' statement or calling close() explicitly."
                )
                self.close()
        except Exception as e:
            logger.error(f"Error in destructor for {self.__class__.__name__}: {e}")

    def _register_resource(self) -> None:
        """Register this resource for monitoring (debugging purposes)."""
        try:
            with _registry_lock:
                _open_resources.add(weakref.ref(self))
        except Exception as e:
            # Don't fail resource creation due to registry issues
            logger.debug(f"Failed to register resource: {e}")

    def _unregister_resource(self) -> None:
        """Unregister this resource from monitoring."""
        try:
            with _registry_lock:
                # Clean up dead references while we're here
                dead_refs = {ref for ref in _open_resources if ref() is None}
                _open_resources.difference_update(dead_refs)
        except Exception as e:
            logger.debug(f"Failed to unregister resource: {e}")


class CloseableGroup(Closeable):
    """
    A group of closeable resources that can be closed together.

    This class manages multiple Closeable resources and ensures they are
    all closed when the group is closed. Resources are closed in reverse
    order of addition (LIFO) to handle dependencies properly.

    Examples:
        >>> group = CloseableGroup()
        >>> group.add(connection1)
        >>> group.add(connection2)
        >>> group.close()  # Closes connection2, then connection1
    """

    def __init__(self):
        """Initialize an empty closeable group."""
        super().__init__()
        self._resources: List[Closeable] = []
        self._closed = False
        self._lock = threading.Lock()

    def add(self, resource: Closeable) -> None:
        """
        Add a resource to this group.

        Args:
            resource: Closeable resource to add

        Raises:
            ValueError: If the group is already closed
        """
        with self._lock:
            if self._closed:
                raise ValueError("Cannot add resources to a closed group")
            self._resources.append(resource)

    def remove(self, resource: Closeable) -> bool:
        """
        Remove a resource from this group.

        Args:
            resource: Closeable resource to remove

        Returns:
            True if the resource was found and removed, False otherwise
        """
        with self._lock:
            try:
                self._resources.remove(resource)
                return True
            except ValueError:
                return False

    def close(self) -> None:
        """Close all resources in reverse order (LIFO)."""
        with self._lock:
            if self._closed:
                return

            # Close in reverse order to handle dependencies
            errors = []
            for resource in reversed(self._resources):
                try:
                    if not resource.is_closed():
                        resource.close()
                except Exception as e:
                    logger.error(f"Error closing resource {resource.__class__.__name__}: {e}")
                    errors.append(e)

            self._resources.clear()
            self._closed = True
            self._unregister_resource()

            # If there were errors, raise the first one
            if errors:
                raise errors[0]

    def is_closed(self) -> bool:
        """Check if this group is closed."""
        return self._closed

    def __len__(self) -> int:
        """Get the number of resources in this group."""
        with self._lock:
            return len(self._resources)


class SafeCloseable(Closeable):
    """
    A thread-safe base implementation of Closeable with common functionality.

    This class provides:
    - Thread-safe close operations
    - Automatic state tracking
    - Error handling during closure
    - Resource cleanup verification

    Subclasses should implement the _do_close() method instead of close().
    """

    def __init__(self):
        """Initialize the safe closeable resource."""
        super().__init__()
        self._closed = False
        self._close_lock = threading.Lock()
        self._cleanup_errors: List[Exception] = []

    def close(self) -> None:
        """Thread-safe close implementation."""
        with self._close_lock:
            if self._closed:
                return

            try:
                self._do_close()
                logger.debug(f"Successfully closed {self.__class__.__name__}")
            except Exception as e:
                self._cleanup_errors.append(e)
                logger.error(f"Error closing {self.__class__.__name__}: {e}")
                raise
            finally:
                self._closed = True
                self._unregister_resource()

    @abstractmethod
    def _do_close(self) -> None:
        """
        Perform the actual resource cleanup.

        This method is called by close() and should implement the specific
        cleanup logic for the resource. It will only be called once and
        is protected by the close lock.

        Raises:
            Exception: Any exception related to resource cleanup
        """
        pass

    def is_closed(self) -> bool:
        """Check if this resource is closed."""
        return self._closed

    def get_cleanup_errors(self) -> List[Exception]:
        """Get any errors that occurred during cleanup."""
        return self._cleanup_errors.copy()


# Utility functions for resource management
def close_quietly(resource: Optional[Closeable], log_errors: bool = True) -> bool:
    """
    Close a resource without raising exceptions.

    Args:
        resource: Resource to close (may be None)
        log_errors: Whether to log any errors that occur

    Returns:
        True if closed successfully or resource was None, False if errors occurred
    """
    if resource is None:
        return True

    try:
        resource.close()
        return True
    except Exception as e:
        if log_errors:
            logger.error(f"Error closing resource {resource.__class__.__name__}: {e}")
        return False


def close_all(*resources: Optional[Closeable], reverse_order: bool = True,
              stop_on_error: bool = False) -> List[Exception]:
    """
    Close multiple resources, collecting any errors.

    Args:
        *resources: Resources to close (None values are ignored)
        reverse_order: Whether to close in reverse order (LIFO)
        stop_on_error: Whether to stop on first error

    Returns:
        List of exceptions that occurred during closure
    """
    errors = []
    resource_list = [r for r in resources if r is not None]

    if reverse_order:
        resource_list = list(reversed(resource_list))

    for resource in resource_list:
        try:
            if not resource.is_closed():
                resource.close()
        except Exception as e:
            errors.append(e)
            logger.error(f"Error closing resource {resource.__class__.__name__}: {e}")
            if stop_on_error:
                break

    return errors


@contextmanager
def managed_resource(resource: Closeable):
    """
    Context manager for ensuring a resource is properly closed.

    Args:
        resource: Closeable resource to manage

    Yields:
        The resource for use within the context

    Examples:
        >>> conn = create_connection()
        >>> with managed_resource(conn) as connection:
        ...     # Use connection here
        ...     pass
        # Connection is automatically closed
    """
    try:
        yield resource
    finally:
        close_quietly(resource)


def get_open_resource_count() -> int:
    """
    Get the number of currently tracked open resources.

    This is primarily for debugging and monitoring purposes.

    Returns:
        Number of open resources being tracked
    """
    with _registry_lock:
        # Clean up dead references
        dead_refs = {ref for ref in _open_resources if ref() is None}
        _open_resources.difference_update(dead_refs)
        return len(_open_resources)


def get_open_resource_types() -> Dict[str, int]:
    """
    Get a breakdown of open resources by type.

    Returns:
        Dictionary mapping class names to counts
    """
    type_counts: Dict[str, int] = {}

    with _registry_lock:
        # Clean up dead references and count by type
        dead_refs = set()
        for ref in _open_resources:
            resource = ref()
            if resource is None:
                dead_refs.add(ref)
            else:
                class_name = resource.__class__.__name__
                type_counts[class_name] = type_counts.get(class_name, 0) + 1

        _open_resources.difference_update(dead_refs)

    return type_counts


def cleanup_all_resources(force: bool = False) -> int:
    """
    Attempt to close all tracked resources.

    Args:
        force: If True, ignore errors and continue closing other resources

    Returns:
        Number of resources that were closed

    Warning:
        This is primarily for testing and emergency cleanup.
        Normal applications should manage their resources explicitly.
    """
    closed_count = 0

    with _registry_lock:
        resources_to_close = []
        dead_refs = set()

        for ref in _open_resources:
            resource = ref()
            if resource is None:
                dead_refs.add(ref)
            else:
                resources_to_close.append(resource)

        _open_resources.difference_update(dead_refs)

    for resource in resources_to_close:
        try:
            if not resource.is_closed():
                resource.close()
                closed_count += 1
        except Exception as e:
            logger.error(f"Error force-closing resource {resource.__class__.__name__}: {e}")
            if not force:
                break

    return closed_count


# Export public interface
__all__ = [
    'Closeable',
    'CloseableGroup',
    'SafeCloseable',
    'close_quietly',
    'close_all',
    'managed_resource',
    'get_open_resource_count',
    'get_open_resource_types',
    'cleanup_all_resources',
]

# Example implementations for documentation/testing
if __name__ == "__main__":
    # Example 1: Basic closeable resource
    class DatabaseConnection(SafeCloseable):
        def __init__(self, connection_string: str):
            super().__init__()
            self.connection_string = connection_string
            self._connection = f"Connected to {connection_string}"
            logger.info(f"Opened connection: {self._connection}")

        def _do_close(self) -> None:
            logger.info(f"Closing connection: {self._connection}")
            self._connection = None

        def query(self, sql: str) -> str:
            if self.is_closed():
                raise ValueError("Connection is closed")
            return f"Result of: {sql}"


    # Example 2: Using context manager
    print("=== DataGuild Closeable Examples ===\n")

    print("Example 1: Basic usage")
    conn = DatabaseConnection("localhost:5432/mydb")
    try:
        result = conn.query("SELECT * FROM users")
        print(f"Query result: {result}")
    finally:
        conn.close()

    print(f"Open resources: {get_open_resource_count()}")

    print("\nExample 2: Context manager")
    with DatabaseConnection("localhost:5432/testdb") as conn:
        result = conn.query("SELECT COUNT(*) FROM orders")
        print(f"Query result: {result}")
    # Connection automatically closed

    print(f"Open resources: {get_open_resource_count()}")

    print("\nExample 3: Resource group")
    group = CloseableGroup()
    group.add(DatabaseConnection("db1"))
    group.add(DatabaseConnection("db2"))
    group.close()  # Closes both connections

    print(f"Final open resources: {get_open_resource_count()}")
