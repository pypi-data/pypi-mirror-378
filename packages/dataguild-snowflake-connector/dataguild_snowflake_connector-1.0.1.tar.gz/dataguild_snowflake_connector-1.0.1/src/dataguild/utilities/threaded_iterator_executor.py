"""
DataGuild Advanced Threaded Iterator Executor

High-performance parallel processing system with intelligent load balancing,
error handling, resource management, and comprehensive monitoring.
"""

import concurrent.futures
import queue
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Iterator, List, Optional, Tuple, Dict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ExecutorState(Enum):
    """States of the executor."""
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    worker_id: Optional[str] = None

    def __post_init__(self):
        """Validate task result."""
        if not self.task_id:
            raise ValueError("Task ID cannot be empty")


@dataclass
class WorkerStats:
    """Statistics for a worker thread."""
    worker_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    last_activity: Optional[float] = None

    def update(self, task_result: TaskResult) -> None:
        """Update worker statistics with task result."""
        if task_result.success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1

        self.total_execution_time += task_result.execution_time
        total_tasks = self.tasks_completed + self.tasks_failed
        self.average_execution_time = self.total_execution_time / max(1, total_tasks)
        self.last_activity = time.time()


@dataclass
class ExecutorMetrics:
    """Comprehensive executor metrics."""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time: float = 0.0
    peak_memory_usage: int = 0
    worker_stats: Dict[str, WorkerStats] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100

    @property
    def average_execution_time(self) -> float:
        """Calculate average execution time per task."""
        if self.completed_tasks == 0:
            return 0.0
        return self.total_execution_time / self.completed_tasks

    @property
    def duration(self) -> float:
        """Get total execution duration."""
        end = self.end_time or time.time()
        return end - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": self.success_rate,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": self.average_execution_time,
            "peak_memory_usage": self.peak_memory_usage,
            "worker_count": len(self.worker_stats),
            "worker_stats": {
                worker_id: {
                    "tasks_completed": stats.tasks_completed,
                    "tasks_failed": stats.tasks_failed,
                    "total_execution_time": stats.total_execution_time,
                    "average_execution_time": stats.average_execution_time,
                    "last_activity": stats.last_activity
                }
                for worker_id, stats in self.worker_stats.items()
            }
        }


class ThreadedIteratorExecutor:
    """
    Advanced threaded executor with intelligent load balancing,
    comprehensive error handling, and performance monitoring.
    """

    def __init__(
            self,
            max_workers: int = 10,
            queue_size: Optional[int] = None,
            timeout: Optional[float] = None,
            enable_metrics: bool = True,
            thread_name_prefix: str = "DataGuildWorker"
    ):
        self.max_workers = max_workers
        self.queue_size = queue_size or max_workers * 2
        self.timeout = timeout
        self.enable_metrics = enable_metrics
        self.thread_name_prefix = thread_name_prefix

        # State management
        self.state = ExecutorState.IDLE
        self.executor: Optional[ThreadPoolExecutor] = None

        # Metrics and monitoring
        self.metrics = ExecutorMetrics() if enable_metrics else None
        self._task_counter = 0
        self._lock = threading.Lock()

        # Error handling
        self.max_retries = 3
        self.retry_delay = 1.0
        self.error_callbacks: List[Callable[[Exception, str], None]] = []

    @staticmethod
    def process(
            worker_func: Callable[[Any], Iterable[Any]],
            args_list: List[Tuple[Any, ...]],
            max_workers: int = 10,
            timeout: Optional[float] = None,
            preserve_order: bool = False
    ) -> Iterator[Any]:
        """
        Static method for simple parallel processing.

        Args:
            worker_func: Function to execute for each argument set
            args_list: List of argument tuples to process
            max_workers: Maximum number of worker threads
            timeout: Timeout for individual tasks
            preserve_order: Whether to preserve order of results

        Yields:
            Results from worker function executions
        """
        executor = ThreadedIteratorExecutor(
            max_workers=max_workers,
            timeout=timeout
        )

        try:
            yield from executor.execute_parallel(
                worker_func=worker_func,
                args_list=args_list,
                preserve_order=preserve_order
            )
        finally:
            executor.shutdown()

    def execute_parallel(
            self,
            worker_func: Callable[[Any], Iterable[Any]],
            args_list: List[Tuple[Any, ...]],
            preserve_order: bool = False,
            retry_failed: bool = True
    ) -> Iterator[Any]:
        """
        Execute function in parallel across argument sets.

        Args:
            worker_func: Function to execute
            args_list: List of argument tuples
            preserve_order: Whether to preserve result order
            retry_failed: Whether to retry failed tasks

        Yields:
            Results from successful executions
        """
        if not args_list:
            return

        self._start_execution()

        try:
            with ThreadPoolExecutor(
                    max_workers=self.max_workers,
                    thread_name_prefix=self.thread_name_prefix
            ) as executor:

                self.executor = executor

                # Submit all tasks
                future_to_args = {}
                for args in args_list:
                    task_id = self._get_next_task_id()
                    future = executor.submit(self._execute_with_monitoring, worker_func, args, task_id)
                    future_to_args[future] = (args, task_id)

                if self.metrics:
                    self.metrics.total_tasks = len(args_list)

                # Process results
                if preserve_order:
                    # Preserve order by waiting for futures in submission order
                    futures_list = list(future_to_args.keys())
                    for future in futures_list:
                        try:
                            results = future.result(timeout=self.timeout)
                            if results:
                                yield from results
                        except Exception as e:
                            args, task_id = future_to_args[future]
                            self._handle_task_error(e, task_id, args, retry_failed)
                else:
                    # Process results as they complete
                    for future in as_completed(future_to_args, timeout=self.timeout):
                        try:
                            results = future.result()
                            if results:
                                yield from results
                        except Exception as e:
                            args, task_id = future_to_args[future]
                            self._handle_task_error(e, task_id, args, retry_failed)

        except Exception as e:
            self.state = ExecutorState.ERROR
            logger.error(f"Executor error: {e}")
            raise
        finally:
            self._finish_execution()

    def execute_streaming(
            self,
            worker_func: Callable[[Any], Iterable[Any]],
            input_iterator: Iterator[Any],
            buffer_size: int = 100
    ) -> Iterator[Any]:
        """
        Execute function in streaming mode with dynamic task submission.

        Args:
            worker_func: Function to execute
            input_iterator: Iterator of input items
            buffer_size: Number of tasks to keep in buffer

        Yields:
            Results as they become available
        """
        self._start_execution()

        with ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix=self.thread_name_prefix
        ) as executor:

            self.executor = executor
            active_futures: Dict[concurrent.futures.Future, str] = {}
            input_exhausted = False

            try:
                input_iter = iter(input_iterator)

                # Fill initial buffer
                while len(active_futures) < buffer_size and not input_exhausted:
                    try:
                        item = next(input_iter)
                        task_id = self._get_next_task_id()
                        future = executor.submit(self._execute_with_monitoring, worker_func, item, task_id)
                        active_futures[future] = task_id

                        if self.metrics:
                            self.metrics.total_tasks += 1
                    except StopIteration:
                        input_exhausted = True

                # Process results and refill buffer
                while active_futures:
                    # Wait for at least one future to complete
                    completed_futures = set()
                    for future in as_completed(active_futures, timeout=1.0):
                        completed_futures.add(future)
                        break

                    # Process completed futures
                    for future in completed_futures:
                        task_id = active_futures.pop(future)
                        try:
                            results = future.result()
                            if results:
                                yield from results
                        except Exception as e:
                            self._handle_task_error(e, task_id, None, False)

                    # Refill buffer if input not exhausted
                    while len(active_futures) < buffer_size and not input_exhausted:
                        try:
                            item = next(input_iter)
                            task_id = self._get_next_task_id()
                            future = executor.submit(self._execute_with_monitoring, worker_func, item, task_id)
                            active_futures[future] = task_id

                            if self.metrics:
                                self.metrics.total_tasks += 1
                        except StopIteration:
                            input_exhausted = True

            finally:
                self._finish_execution()

    def _execute_with_monitoring(
            self,
            worker_func: Callable[[Any], Iterable[Any]],
            args: Any,
            task_id: str
    ) -> List[Any]:
        """Execute function with comprehensive monitoring."""
        start_time = time.time()
        worker_id = threading.current_thread().name
        results = []

        try:
            # Execute the worker function
            result_iterator = worker_func(args)

            # Collect all results
            if result_iterator:
                results = list(result_iterator)

            # Update metrics
            execution_time = time.time() - start_time
            if self.metrics:
                self._update_metrics(
                    TaskResult(
                        task_id=task_id,
                        success=True,
                        result=results,
                        execution_time=execution_time,
                        worker_id=worker_id
                    )
                )

            logger.debug(f"Task {task_id} completed successfully in {execution_time:.3f}s")
            return results

        except Exception as e:
            execution_time = time.time() - start_time

            # Update metrics
            if self.metrics:
                self._update_metrics(
                    TaskResult(
                        task_id=task_id,
                        success=False,
                        error=e,
                        execution_time=execution_time,
                        worker_id=worker_id
                    )
                )

            logger.error(f"Task {task_id} failed after {execution_time:.3f}s: {e}")
            logger.debug(f"Task {task_id} traceback: {traceback.format_exc()}")

            # Call error callbacks
            for callback in self.error_callbacks:
                try:
                    callback(e, task_id)
                except Exception as callback_error:
                    logger.error(f"Error callback failed: {callback_error}")

            raise

    def _update_metrics(self, task_result: TaskResult) -> None:
        """Update executor metrics with task result."""
        if not self.metrics:
            return

        with self._lock:
            if task_result.success:
                self.metrics.completed_tasks += 1
            else:
                self.metrics.failed_tasks += 1

            self.metrics.total_execution_time += task_result.execution_time

            # Update worker stats
            if task_result.worker_id:
                if task_result.worker_id not in self.metrics.worker_stats:
                    self.metrics.worker_stats[task_result.worker_id] = WorkerStats(
                        worker_id=task_result.worker_id
                    )

                self.metrics.worker_stats[task_result.worker_id].update(task_result)

    def _handle_task_error(
            self,
            error: Exception,
            task_id: str,
            args: Optional[Any],
            retry: bool
    ) -> None:
        """Handle task execution error."""
        logger.error(f"Task {task_id} error: {error}")

        # TODO: Implement retry logic if needed
        if retry and self.max_retries > 0:
            logger.info(f"Retry logic not yet implemented for task {task_id}")

    def _start_execution(self) -> None:
        """Initialize execution state."""
        self.state = ExecutorState.RUNNING
        if self.metrics:
            self.metrics.start_time = time.time()

    def _finish_execution(self) -> None:
        """Finalize execution state."""
        self.state = ExecutorState.STOPPED
        if self.metrics:
            self.metrics.end_time = time.time()
        self.executor = None

    def _get_next_task_id(self) -> str:
        """Get next unique task ID."""
        with self._lock:
            self._task_counter += 1
            return f"task_{self._task_counter:06d}"

    def add_error_callback(self, callback: Callable[[Exception, str], None]) -> None:
        """Add error callback function."""
        self.error_callbacks.append(callback)

    def remove_error_callback(self, callback: Callable[[Exception, str], None]) -> None:
        """Remove error callback function."""
        if callback in self.error_callbacks:
            self.error_callbacks.remove(callback)

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current execution metrics."""
        if not self.metrics:
            return None
        return self.metrics.to_dict()

    def shutdown(self, wait: bool = True, timeout: Optional[float] = None) -> None:
        """Shutdown the executor."""
        if self.executor:
            self.state = ExecutorState.STOPPING
            self.executor.shutdown(wait=wait, timeout=timeout)
            self.state = ExecutorState.STOPPED
            self.executor = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
