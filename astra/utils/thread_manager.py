#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Thread Pool Manager
Centralized thread management using ThreadPoolExecutor.
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError as FutureTimeoutError
from typing import Callable, Any, Optional, Dict
from functools import wraps
import time

logger = logging.getLogger(__name__)


class ThreadPoolManager:
    """
    Manages thread pools for the ASTRA application.
    
    Benefits:
    - Controlled thread creation
    - Automatic cleanup
    - Timeout support
    - Better error handling
    - Thread naming for debugging
    """
    
    def __init__(self, max_workers: int = 10, thread_name_prefix: str = "ASTRA"):
        """
        Initialize thread pool manager.
        
        Args:
            max_workers: Maximum number of worker threads
            thread_name_prefix: Prefix for thread names
        """
        self.max_workers = max_workers
        self.thread_name_prefix = thread_name_prefix
        
        self._executor: Optional[ThreadPoolExecutor] = None
        self._futures: Dict[str, Future] = {}
        self._lock = threading.Lock()
        self._shutdown = False
        
        logger.info(f"🧵 Thread pool manager initialized (max_workers={max_workers})")
    
    @property
    def executor(self) -> ThreadPoolExecutor:
        """Get or create executor (lazy initialization)."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix=self.thread_name_prefix
            )
            logger.debug("Thread pool executor created")
        return self._executor
    
    def submit(
        self, 
        func: Callable, 
        *args, 
        task_name: Optional[str] = None,
        **kwargs
    ) -> Future:
        """
        Submit a task to the thread pool.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            task_name: Optional name for the task
            **kwargs: Keyword arguments
            
        Returns:
            Future object
        """
        if self._shutdown:
            raise RuntimeError("ThreadPoolManager is shut down")
        
        # Wrap function to add logging
        @wraps(func)
        def wrapped():
            task_id = task_name or func.__name__
            logger.debug(f"🏃 Starting task: {task_id}")
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"✅ Task completed: {task_id} ({elapsed:.2f}s)")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"❌ Task failed: {task_id} ({elapsed:.2f}s) - {e}")
                raise
        
        future = self.executor.submit(wrapped)
        
        # Store future for tracking
        if task_name:
            with self._lock:
                self._futures[task_name] = future
        
        return future
    
    def submit_with_timeout(
        self,
        func: Callable,
        timeout: float,
        *args,
        task_name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Submit a task with a timeout.
        
        Args:
            func: Function to execute
            timeout: Maximum time in seconds
            *args: Positional arguments
            task_name: Optional name for the task
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            TimeoutError: If execution exceeds timeout
        """
        future = self.submit(func, *args, task_name=task_name, **kwargs)
        
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError:
            logger.error(f"⏱️ Task timeout: {task_name or func.__name__} ({timeout}s)")
            future.cancel()
            raise TimeoutError(f"Task timed out after {timeout}s")
    
    def cancel_task(self, task_name: str) -> bool:
        """
        Cancel a named task.
        
        Args:
            task_name: Name of the task to cancel
            
        Returns:
            True if cancelled, False if not found or already done
        """
        with self._lock:
            future = self._futures.get(task_name)
            if future and not future.done():
                cancelled = future.cancel()
                if cancelled:
                    logger.info(f"🚫 Task cancelled: {task_name}")
                return cancelled
        return False
    
    def wait_for_task(self, task_name: str, timeout: Optional[float] = None) -> Any:
        """
        Wait for a named task to complete.
        
        Args:
            task_name: Name of the task
            timeout: Maximum time to wait (None = infinite)
            
        Returns:
            Task result
            
        Raises:
            KeyError: If task not found
            TimeoutError: If timeout exceeded
        """
        with self._lock:
            future = self._futures.get(task_name)
            if not future:
                raise KeyError(f"Task not found: {task_name}")
        
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError:
            raise TimeoutError(f"Timeout waiting for task: {task_name}")
    
    def shutdown(self, wait: bool = True, timeout: Optional[float] = 30.0):
        """
        Shutdown the thread pool.
        
        Args:
            wait: Whether to wait for tasks to complete
            timeout: Maximum time to wait (None = infinite)
        """
        if self._shutdown:
            return
        
        self._shutdown = True
        
        if self._executor:
            logger.info("🛑 Shutting down thread pool...")
            
            # Cancel pending tasks if not waiting
            if not wait:
                with self._lock:
                    for name, future in self._futures.items():
                        if not future.done():
                            future.cancel()
                            logger.debug(f"Cancelled pending task: {name}")
            
            # Shutdown executor
            self._executor.shutdown(wait=wait, cancel_futures=not wait)
            
            logger.info("✅ Thread pool shut down")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get thread pool statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_tasks = len(self._futures)
            completed = sum(1 for f in self._futures.values() if f.done())
            running = sum(1 for f in self._futures.values() if f.running())
            cancelled = sum(1 for f in self._futures.values() if f.cancelled())
            
        return {
            "max_workers": self.max_workers,
            "total_tasks": total_tasks,
            "completed": completed,
            "running": running,
            "cancelled": cancelled,
            "pending": total_tasks - completed - cancelled,
            "is_shutdown": self._shutdown
        }


# Global thread pool manager
_thread_pool_manager: Optional[ThreadPoolManager] = None


def get_thread_pool_manager() -> ThreadPoolManager:
    """
    Get global thread pool manager (singleton).
    
    Returns:
        ThreadPoolManager instance
    """
    global _thread_pool_manager
    if _thread_pool_manager is None:
        _thread_pool_manager = ThreadPoolManager()
    return _thread_pool_manager


def run_in_thread(func: Callable, *args, task_name: Optional[str] = None, **kwargs) -> Future:
    """
    Convenience function to run a function in a thread.
    
    Args:
        func: Function to run
        *args: Positional arguments
        task_name: Optional task name
        **kwargs: Keyword arguments
        
    Returns:
        Future object
    """
    return get_thread_pool_manager().submit(func, *args, task_name=task_name, **kwargs)


def run_with_timeout(func: Callable, timeout: float, *args, **kwargs) -> Any:
    """
    Run a function with a timeout.
    
    Args:
        func: Function to run
        timeout: Maximum time in seconds
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Function result
    """
    return get_thread_pool_manager().submit_with_timeout(func, timeout, *args, **kwargs)


# Decorator for running functions in threads
def threaded(task_name: Optional[str] = None):
    """
    Decorator to run a function in a thread pool.
    
    Args:
        task_name: Optional name for the task
        
    Example:
        @threaded("process_audio")
        def process_audio_data(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Future:
            name = task_name or func.__name__
            return run_in_thread(func, *args, task_name=name, **kwargs)
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get manager
    manager = get_thread_pool_manager()
    
    # Test function
    def slow_task(duration: int, name: str):
        print(f"Task {name} started (duration: {duration}s)")
        time.sleep(duration)
        print(f"Task {name} completed")
        return f"Result from {name}"
    
    # Submit tasks
    print("Submitting tasks...")
    future1 = manager.submit(slow_task, 2, "Task1", task_name="task1")
    future2 = manager.submit(slow_task, 1, "Task2", task_name="task2")
    future3 = manager.submit(slow_task, 3, "Task3", task_name="task3")
    
    # Wait for specific task
    print("\nWaiting for task2...")
    result2 = manager.wait_for_task("task2")
    print(f"Got result: {result2}")
    
    # Check stats
    print(f"\nStats: {manager.get_stats()}")
    
    # Wait for all
    print("\nWaiting for all tasks...")
    print(f"Result 1: {future1.result()}")
    print(f"Result 3: {future3.result()}")
    
    # Final stats
    print(f"\nFinal stats: {manager.get_stats()}")
    
    # Test timeout
    print("\n\nTesting timeout...")
    try:
        result = manager.submit_with_timeout(slow_task, 1.0, 5, "SlowTask")
    except TimeoutError as e:
        print(f"⏱️ Caught timeout: {e}")
    
    # Shutdown
    print("\nShutting down...")
    manager.shutdown()
    print("✅ Done!")
