#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/Astra - Cache Manager
Intelligent caching system with multiple strategies.
"""

import hashlib
import time
import json
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Intelligent cache manager with TTL, LRU, and persistence.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default TTL in seconds
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.access_times: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.miss_count += 1
            return None
            
        entry = self.cache[key]
        
        # Check TTL
        if entry['expires_at'] < time.time():
            del self.cache[key]
            self.miss_count += 1
            return None
            
        # Update access time
        self.access_times[key] = time.time()
        self.hit_count += 1
        
        return entry['value']
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if set successfully
        """
        # Evict if at max size
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
            
        ttl = ttl or self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'created_at': time.time(),
            'expires_at': time.time() + ttl
        }
        
        self.access_times[key] = time.time()
        
        return True
        
    def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return True
        return False
        
    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.access_times.clear()
        self.hit_count = 0
        self.miss_count = 0
        
    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self.access_times:
            return
            
        lru_key = min(self.access_times, key=self.access_times.get)
        self.delete(lru_key)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total
        }
        
    def cached(self, ttl: Optional[int] = None):
        """
        Decorator for caching function results.
        
        Args:
            ttl: Time to live in seconds
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                key = self._make_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                result = self.get(key)
                if result is not None:
                    return result
                    
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                
                return result
            return wrapper
        return decorator
        
    def _make_key(self, prefix: str, args: tuple, kwargs: dict) -> str:
        """Create cache key from prefix and arguments."""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()


# Global cache instance
cache_manager = CacheManager()


def cached(ttl: Optional[int] = None):
    """Global cache decorator."""
    return cache_manager.cached(ttl)

