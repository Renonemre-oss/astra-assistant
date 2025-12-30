#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Exception Handler
Advanced exception handling with categorization, recovery strategies, and logging.
"""

import logging
import functools
from typing import Callable, Optional, Any, Dict, Type, List
from enum import Enum
import traceback
import time


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"  # Pode ser ignorado, não afeta funcionalidade
    MEDIUM = "medium"  # Afeta funcionalidade mas tem fallback
    HIGH = "high"  # Afeta funcionalidade crítica
    CRITICAL = "critical"  # Sistema não pode continuar


class ErrorCategory(Enum):
    """Categories of errors."""
    NETWORK = "network"  # Problemas de rede/API
    DATABASE = "database"  # Erros de base de dados
    FILE_SYSTEM = "file_system"  # Erros de ficheiros
    AUTHENTICATION = "authentication"  # Erros de autenticação
    VALIDATION = "validation"  # Erros de validação
    RESOURCE = "resource"  # Falta de recursos (memória, etc.)
    EXTERNAL_SERVICE = "external_service"  # Serviços externos (Ollama, APIs)
    CONFIGURATION = "configuration"  # Erros de configuração
    USER_INPUT = "user_input"  # Problemas com input do utilizador
    UNKNOWN = "unknown"  # Erro desconhecido


class RecoveryStrategy(Enum):
    """Recovery strategies for errors."""
    RETRY = "retry"  # Tentar novamente
    FALLBACK = "fallback"  # Usar alternativa
    IGNORE = "ignore"  # Ignorar e continuar
    FAIL = "fail"  # Falhar imediatamente
    ASK_USER = "ask_user"  # Pedir input ao utilizador


class AstraException(Exception):
    """Base exception for ASTRA errors."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.FAIL,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.recovery_strategy = recovery_strategy
        self.original_error = original_error
        self.context = context or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "recovery_strategy": self.recovery_strategy.value,
            "original_error": str(self.original_error) if self.original_error else None,
            "context": self.context,
            "timestamp": self.timestamp
        }


class NetworkError(AstraException):
    """Network/API related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=kwargs.get('severity', ErrorSeverity.MEDIUM),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.RETRY),
            **{k: v for k, v in kwargs.items() if k not in ['severity', 'recovery_strategy']}
        )


class DatabaseError(AstraException):
    """Database related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=kwargs.get('severity', ErrorSeverity.HIGH),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.FALLBACK),
            **{k: v for k, v in kwargs.items() if k not in ['severity', 'recovery_strategy']}
        )


class ConfigurationError(AstraException):
    """Configuration related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=kwargs.get('severity', ErrorSeverity.CRITICAL),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.FAIL),
            **{k: v for k, v in kwargs.items() if k not in ['severity', 'recovery_strategy']}
        )


class ExternalServiceError(AstraException):
    """External service errors (Ollama, APIs, etc.)."""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=kwargs.get('severity', ErrorSeverity.MEDIUM),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.RETRY),
            **{k: v for k, v in kwargs.items() if k not in ['severity', 'recovery_strategy']}
        )


class ExceptionHandler:
    """
    Centralized exception handler with recovery strategies.
    """
    
    def __init__(self):
        self._error_counts: Dict[str, int] = {}
        self._last_errors: List[Dict[str, Any]] = []
        self._max_history = 100
    
    def handle_exception(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        log_traceback: bool = True
    ) -> Optional[Any]:
        """
        Handle an exception with appropriate logging and recovery.
        
        Args:
            error: The exception to handle
            context: Additional context information
            log_traceback: Whether to log full traceback
            
        Returns:
            Recovery result if applicable
        """
        # Convert to AstraException if needed
        if not isinstance(error, AstraException):
            error = self._categorize_exception(error, context)
        
        # Log the error
        self._log_error(error, log_traceback)
        
        # Track error
        self._track_error(error)
        
        # Apply recovery strategy
        return self._apply_recovery(error)
    
    def _categorize_exception(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> AstraException:
        """Categorize a generic exception."""
        error_type = type(error).__name__
        
        # Network errors
        if any(keyword in error_type.lower() for keyword in ['connection', 'timeout', 'network', 'http']):
            return NetworkError(str(error), original_error=error, context=context)
        
        # Database errors
        if any(keyword in error_type.lower() for keyword in ['database', 'sql', 'query']):
            return DatabaseError(str(error), original_error=error, context=context)
        
        # File system errors
        if any(keyword in error_type.lower() for keyword in ['file', 'io', 'permission']):
            return AstraException(
                str(error),
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                recovery_strategy=RecoveryStrategy.FALLBACK,
                original_error=error,
                context=context
            )
        
        # Configuration errors
        if any(keyword in error_type.lower() for keyword in ['config', 'setting']):
            return ConfigurationError(str(error), original_error=error, context=context)
        
        # Default to unknown
        return AstraException(
            str(error),
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.FAIL,
            original_error=error,
            context=context
        )
    
    def _log_error(self, error: AstraException, log_traceback: bool = True):
        """Log error with appropriate level."""
        error_dict = error.to_dict()
        
        # Format message
        log_msg = (
            f"[{error.category.value.upper()}] {error.message} | "
            f"Severity: {error.severity.value} | "
            f"Recovery: {error.recovery_strategy.value}"
        )
        
        # Add context if present
        if error.context:
            context_str = ", ".join(f"{k}={v}" for k, v in error.context.items())
            log_msg += f" | Context: {context_str}"
        
        # Choose log level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_msg, exc_info=log_traceback)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_msg, exc_info=log_traceback)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        # Log original traceback if available
        if log_traceback and error.original_error:
            logger.debug(f"Original error: {type(error.original_error).__name__}")
            logger.debug(traceback.format_exc())
    
    def _track_error(self, error: AstraException):
        """Track error for statistics."""
        error_key = f"{error.category.value}:{error.severity.value}"
        self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1
        
        # Store in history
        self._last_errors.append(error.to_dict())
        
        # Trim history
        if len(self._last_errors) > self._max_history:
            self._last_errors = self._last_errors[-self._max_history:]
    
    def _apply_recovery(self, error: AstraException) -> Optional[Any]:
        """Apply recovery strategy."""
        strategy = error.recovery_strategy
        
        if strategy == RecoveryStrategy.IGNORE:
            logger.info(f"Ignoring error: {error.message}")
            return None
        
        elif strategy == RecoveryStrategy.FAIL:
            raise error
        
        # Other strategies would be implemented by caller
        return None
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": sum(self._error_counts.values()),
            "errors_by_category": self._error_counts.copy(),
            "recent_errors": self._last_errors[-10:]  # Last 10
        }
    
    def clear_history(self):
        """Clear error history."""
        self._last_errors.clear()
        self._error_counts.clear()


# Global exception handler
_exception_handler = ExceptionHandler()


def handle_exceptions(
    fallback_value: Any = None,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    log_traceback: bool = True,
    category: Optional[ErrorCategory] = None,
    severity: Optional[ErrorSeverity] = None
):
    """
    Decorator for automatic exception handling.
    
    Args:
        fallback_value: Value to return on error
        retry_count: Number of retries
        retry_delay: Delay between retries in seconds
        log_traceback: Whether to log full traceback
        category: Error category override
        severity: Error severity override
        
    Example:
        @handle_exceptions(fallback_value="Error occurred", retry_count=3)
        def risky_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(retry_count + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    # Convert to AstraException if needed
                    if not isinstance(e, AstraException):
                        context = {
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_attempts": retry_count + 1
                        }
                        
                        if category:
                            e = AstraException(
                                str(e),
                                category=category,
                                severity=severity or ErrorSeverity.MEDIUM,
                                original_error=e,
                                context=context
                            )
                        else:
                            e = _exception_handler._categorize_exception(e, context)
                    
                    # Handle the error
                    _exception_handler.handle_exception(e, log_traceback=log_traceback)
                    
                    # If not last attempt, wait and retry
                    if attempt < retry_count:
                        logger.info(f"Retrying {func.__name__} in {retry_delay}s... (attempt {attempt + 1}/{retry_count + 1})")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"All retry attempts failed for {func.__name__}")
            
            # All retries failed, return fallback
            logger.warning(f"Returning fallback value for {func.__name__}: {fallback_value}")
            return fallback_value
        
        return wrapper
    return decorator


def get_exception_handler() -> ExceptionHandler:
    """Get global exception handler."""
    return _exception_handler


def log_and_raise(
    error_class: Type[AstraException],
    message: str,
    **kwargs
):
    """
    Log and raise an error in one call.
    
    Args:
        error_class: Exception class to raise
        message: Error message
        **kwargs: Additional kwargs for exception
        
    Example:
        log_and_raise(NetworkError, "API request failed", context={"url": url})
    """
    error = error_class(message, **kwargs)
    _exception_handler._log_error(error, log_traceback=False)
    raise error


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=== Testing Exception Handler ===\n")
    
    # Test 1: Basic exception handling
    print("1. Testing basic exception handling:")
    
    @handle_exceptions(fallback_value="Fallback result")
    def failing_function():
        raise ValueError("Something went wrong!")
    
    result = failing_function()
    print(f"   Result: {result}\n")
    
    # Test 2: Network error with retry
    print("2. Testing retry logic:")
    
    attempt_count = [0]
    
    @handle_exceptions(retry_count=2, retry_delay=0.5, fallback_value="Failed after retries")
    def unstable_network_call():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ConnectionError(f"Network error (attempt {attempt_count[0]})")
        return "Success!"
    
    result = unstable_network_call()
    print(f"   Result: {result}\n")
    
    # Test 3: Custom ASTRA exceptions
    print("3. Testing custom exceptions:")
    
    try:
        raise NetworkError(
            "Failed to connect to API",
            context={"url": "https://api.example.com", "timeout": 30}
        )
    except AstraException as e:
        handler = get_exception_handler()
        handler.handle_exception(e)
        print(f"   Handled: {e.message}\n")
    
    # Test 4: Error statistics
    print("4. Error statistics:")
    stats = get_exception_handler().get_error_stats()
    print(f"   Total errors: {stats['total_errors']}")
    print(f"   By category: {stats['errors_by_category']}")
    
    print("\n✅ All tests completed!")
