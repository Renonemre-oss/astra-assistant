#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Structured Logger
Enhanced logging with context, metrics, and structured data.
"""

import logging
import time
import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
import traceback


class StructuredLogger:
    """
    Wrapper around Python logger with structured logging capabilities.
    
    Features:
    - Contextual logging (request ID, user ID, etc.)
    - Performance tracking
    - Structured data (JSON-like)
    - Exception tracking
    """
    
    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            context: Default context to include in all logs
        """
        self.logger = logging.getLogger(name)
        self.context = context or {}
        self.default_context = {
            "logger": name,
            "timestamp": None,  # Will be set per log
        }
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format message with context."""
        full_context = {**self.default_context, **self.context}
        
        if extra:
            full_context.update(extra)
        
        # Add timestamp
        full_context["timestamp"] = datetime.now().isoformat()
        
        # Format as JSON if there's context
        if len(full_context) > 2:  # More than just logger and timestamp
            context_str = " | " + " | ".join(f"{k}={v}" for k, v in full_context.items() if k not in ["logger", "timestamp"])
            return f"{message}{context_str}"
        
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(self._format_message(message, kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(self._format_message(message, kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(self._format_message(message, kwargs))
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message with context and optional exception info."""
        self.logger.error(self._format_message(message, kwargs), exc_info=exc_info)
    
    def exception(self, message: str, **kwargs):
        """Log exception with full traceback."""
        # Add exception info to context
        kwargs["exception_type"] = type(kwargs.get("exc")).__name__ if "exc" in kwargs else "Unknown"
        self.logger.exception(self._format_message(message, kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.logger.critical(self._format_message(message, kwargs))
    
    def with_context(self, **additional_context) -> 'StructuredLogger':
        """
        Create a new logger with additional context.
        
        Args:
            **additional_context: Additional context to add
            
        Returns:
            New StructuredLogger with merged context
        """
        new_context = {**self.context, **additional_context}
        return StructuredLogger(self.logger.name, new_context)
    
    def measure_time(self, operation: str, **context):
        """
        Context manager to measure and log operation time.
        
        Args:
            operation: Name of the operation
            **context: Additional context
            
        Example:
            with logger.measure_time("database_query", query_id=123):
                result = db.query()
        """
        return TimedOperation(self, operation, context)
    
    def log_function_call(self, level: str = "DEBUG"):
        """
        Decorator to log function calls with arguments and timing.
        
        Args:
            level: Log level (DEBUG, INFO, etc.)
            
        Example:
            @logger.log_function_call("INFO")
            def process_data(data):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__
                
                # Log entry
                self.debug(
                    f"→ Calling {func_name}",
                    function=func_name,
                    args_count=len(args),
                    kwargs_count=len(kwargs)
                )
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    # Log success
                    self.debug(
                        f"✓ {func_name} completed",
                        function=func_name,
                        duration_ms=f"{elapsed*1000:.2f}"
                    )
                    
                    return result
                    
                except Exception as e:
                    elapsed = time.time() - start_time
                    
                    # Log failure
                    self.error(
                        f"✗ {func_name} failed",
                        function=func_name,
                        duration_ms=f"{elapsed*1000:.2f}",
                        error=str(e),
                        exc_info=True
                    )
                    raise
            
            return wrapper
        return decorator


class TimedOperation:
    """Context manager for timing operations."""
    
    def __init__(self, logger: StructuredLogger, operation: str, context: Dict[str, Any]):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"⏱️ Starting: {self.operation}", operation=self.operation, **self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"✅ Completed: {self.operation}",
                operation=self.operation,
                duration_ms=f"{elapsed*1000:.2f}",
                **self.context
            )
        else:
            self.logger.error(
                f"❌ Failed: {self.operation}",
                operation=self.operation,
                duration_ms=f"{elapsed*1000:.2f}",
                error=str(exc_val),
                **self.context
            )


def get_logger(name: str, **context) -> StructuredLogger:
    """
    Get a structured logger.
    
    Args:
        name: Logger name
        **context: Default context
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, context)


# Performance tracking decorator
def track_performance(operation_name: Optional[str] = None):
    """
    Decorator to track function performance.
    
    Args:
        operation_name: Name of the operation (defaults to function name)
        
    Example:
        @track_performance("data_processing")
        def process_large_dataset(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with logger.measure_time(op_name, function=func.__name__):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Exception logging decorator
def log_exceptions(logger_name: Optional[str] = None, re_raise: bool = True):
    """
    Decorator to automatically log exceptions.
    
    Args:
        logger_name: Logger name (defaults to function module)
        re_raise: Whether to re-raise the exception
        
    Example:
        @log_exceptions("my_module")
        def risky_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        name = logger_name or func.__module__
        logger = get_logger(name)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Exception in {func.__name__}",
                    function=func.__name__,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                
                if re_raise:
                    raise
                
                return None
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logger
    logger = get_logger("test_module", service="ASTRA", version="1.0")
    
    # Simple logging
    logger.info("Application started")
    logger.debug("Debug information", user_id=123, session_id="abc")
    logger.warning("Low memory", available_mb=100)
    
    # Contextual logger
    user_logger = logger.with_context(user_id=456, username="john")
    user_logger.info("User logged in")
    user_logger.info("User made a request", endpoint="/api/data")
    
    # Timed operation
    print("\n--- Timed operation ---")
    with logger.measure_time("database_query", query_id=789):
        time.sleep(0.5)  # Simulate work
    
    # Function decorator
    print("\n--- Function decorator ---")
    @logger.log_function_call("INFO")
    def process_data(data, multiplier=2):
        time.sleep(0.2)
        return data * multiplier
    
    result = process_data(10, multiplier=3)
    print(f"Result: {result}")
    
    # Performance tracking
    print("\n--- Performance tracking ---")
    @track_performance("heavy_computation")
    def heavy_computation(n):
        time.sleep(0.3)
        return sum(range(n))
    
    result = heavy_computation(1000)
    print(f"Computation result: {result}")
    
    # Exception logging
    print("\n--- Exception handling ---")
    @log_exceptions("error_test", re_raise=False)
    def failing_function():
        raise ValueError("Something went wrong!")
    
    failing_function()
    
    print("\n✅ Test completed!")
