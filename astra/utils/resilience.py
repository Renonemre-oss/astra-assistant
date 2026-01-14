#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Resilience Utilities
Circuit breaker and rate limiting for external services.
"""

import time
import threading
import logging
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 2          # Successes to close from half-open
    timeout: float = 60.0               # Seconds before half-open attempt
    expected_exception: type = Exception  # Exception type to catch


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by stopping requests to a failing service.
    After a timeout, allows test requests to check if service recovered.
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            name: Name of the service being protected
            config: Configuration (uses defaults if None)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.Lock()
        
        logger.info(f"🔒 Circuit breaker initialized for: {name}")
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: If function raises
        """
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    logger.info(f"🔄 {self.name}: Circuit HALF_OPEN, attempting reset")
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker is OPEN for {self.name}"
                    )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return False
        return time.time() - self._last_failure_time >= self.config.timeout
    
    def _on_success(self):
        """Handle successful call."""
        with self._lock:
            self._failure_count = 0
            
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._success_count = 0
                    logger.info(f"✅ {self.name}: Circuit CLOSED (recovered)")
    
    def _on_failure(self):
        """Handle failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning(f"⚠️ {self.name}: Circuit OPEN (half-open test failed)")
            elif self._failure_count >= self.config.failure_threshold:
                self._state = CircuitState.OPEN
                logger.error(f"❌ {self.name}: Circuit OPEN ({self._failure_count} failures)")
    
    def reset(self):
        """Manually reset the circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            logger.info(f"🔄 {self.name}: Circuit manually reset")


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


@dataclass
class RateLimiterConfig:
    """Configuration for rate limiter."""
    max_calls: int = 10         # Maximum calls per period
    period: float = 60.0        # Period in seconds
    burst: int = 0              # Additional burst capacity (0 = disabled)


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Limits the rate of operations to prevent overwhelming external services.
    Supports burst capacity for handling short spikes.
    """
    
    def __init__(self, name: str, config: Optional[RateLimiterConfig] = None):
        """
        Initialize rate limiter.
        
        Args:
            name: Name of the rate limiter
            config: Configuration (uses defaults if None)
        """
        self.name = name
        self.config = config or RateLimiterConfig()
        
        # Token bucket parameters
        self._max_tokens = self.config.max_calls + self.config.burst
        self._tokens = self._max_tokens
        self._last_update = time.time()
        self._refill_rate = self.config.max_calls / self.config.period
        
        self._lock = threading.Lock()
        
        # Statistics
        self._total_requests = 0
        self._rejected_requests = 0
        
        logger.info(f"⏱️ Rate limiter initialized for: {name}")
        logger.info(f"   Max calls: {self.config.max_calls}/{self.config.period}s")
    
    def acquire(self, tokens: int = 1, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from the rate limiter.
        
        Args:
            tokens: Number of tokens to acquire
            blocking: If True, wait for tokens to become available
            timeout: Maximum time to wait (None = infinite)
            
        Returns:
            True if tokens acquired, False otherwise
        """
        start_time = time.time()
        
        while True:
            with self._lock:
                self._refill_tokens()
                self._total_requests += 1
                
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                else:
                    self._rejected_requests += 1
                    
                    if not blocking:
                        logger.warning(f"⏱️ {self.name}: Rate limit exceeded (non-blocking)")
                        return False
                    
                    # Calculate wait time
                    tokens_needed = tokens - self._tokens
                    wait_time = tokens_needed / self._refill_rate
                    
                    # Check timeout
                    if timeout is not None:
                        elapsed = time.time() - start_time
                        if elapsed + wait_time > timeout:
                            logger.warning(f"⏱️ {self.name}: Rate limit timeout")
                            return False
            
            # Wait outside the lock
            time.sleep(min(wait_time, 0.1))
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_update
        self._last_update = now
        
        # Add tokens based on refill rate
        self._tokens = min(
            self._max_tokens,
            self._tokens + elapsed * self._refill_rate
        )
    
    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            rejection_rate = (
                self._rejected_requests / self._total_requests * 100
                if self._total_requests > 0 else 0
            )
            
            return {
                "name": self.name,
                "total_requests": self._total_requests,
                "rejected_requests": self._rejected_requests,
                "rejection_rate": f"{rejection_rate:.2f}%",
                "current_tokens": int(self._tokens),
                "max_tokens": self._max_tokens
            }
    
    def reset_stats(self):
        """Reset statistics counters."""
        with self._lock:
            self._total_requests = 0
            self._rejected_requests = 0


def with_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    Decorator to apply circuit breaker to a function.
    
    Args:
        name: Name for the circuit breaker
        config: Configuration (uses defaults if None)
        
    Example:
        @with_circuit_breaker("ollama_api")
        def call_ollama():
            ...
    """
    breaker = CircuitBreaker(name, config)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


def with_rate_limit(name: str, config: Optional[RateLimiterConfig] = None):
    """
    Decorator to apply rate limiting to a function.
    
    Args:
        name: Name for the rate limiter
        config: Configuration (uses defaults if None)
        
    Example:
        @with_rate_limit("ollama_api", RateLimiterConfig(max_calls=10, period=60))
        def call_ollama():
            ...
    """
    limiter = RateLimiter(name, config)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            if limiter.acquire():
                return func(*args, **kwargs)
            else:
                raise RateLimitExceeded(f"Rate limit exceeded for {name}")
        return wrapper
    return decorator


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("🧪 Testing Circuit Breaker")
    print("=" * 60)
    
    # Test circuit breaker
    breaker = CircuitBreaker(
        "test_service",
        CircuitBreakerConfig(failure_threshold=3, timeout=2.0)
    )
    
    def failing_service():
        raise Exception("Service failed!")
    
    def healthy_service():
        return "Success!"
    
    # Simulate failures
    for i in range(5):
        try:
            result = breaker.call(failing_service)
        except (CircuitBreakerError, Exception) as e:
            print(f"Attempt {i+1}: {type(e).__name__} - {e}")
        print(f"State: {breaker.state.value}")
    
    print("\n" + "=" * 60)
    print("🧪 Testing Rate Limiter")
    print("=" * 60)
    
    # Test rate limiter
    limiter = RateLimiter(
        "test_api",
        RateLimiterConfig(max_calls=5, period=10.0)
    )
    
    print("Making 10 rapid requests...")
    for i in range(10):
        if limiter.acquire(blocking=False):
            print(f"Request {i+1}: ✅ Allowed")
        else:
            print(f"Request {i+1}: ❌ Rate limited")
    
    print(f"\nStatistics: {limiter.get_stats()}")
