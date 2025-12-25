#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA/Astra - Performance Monitor
Real-time performance monitoring and profiling.
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Real-time performance monitoring system."""
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize performance monitor.
        
        Args:
            history_size: Number of samples to keep in history
        """
        self.history_size = history_size
        self.cpu_history: deque = deque(maxlen=history_size)
        self.memory_history: deque = deque(maxlen=history_size)
        self.response_times: deque = deque(maxlen=history_size)
        
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.interval = 1.0  # seconds
        
        self.process = psutil.Process()
        
    def start_monitoring(self):
        """Start background monitoring."""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Performance monitoring started")
            
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("Performance monitoring stopped")
        
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                # Collect metrics
                cpu_percent = self.process.cpu_percent(interval=0.1)
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                timestamp = datetime.now()
                
                self.cpu_history.append({
                    'timestamp': timestamp,
                    'value': cpu_percent
                })
                
                self.memory_history.append({
                    'timestamp': timestamp,
                    'value': memory_mb
                })
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                
    def record_response_time(self, duration: float, endpoint: str = "unknown"):
        """Record API response time."""
        self.response_times.append({
            'timestamp': datetime.now(),
            'duration': duration,
            'endpoint': endpoint
        })
        
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = self.process.memory_percent()
            
            num_threads = self.process.num_threads()
            
            return {
                'cpu_percent': round(cpu_percent, 2),
                'memory_mb': round(memory_mb, 2),
                'memory_percent': round(memory_percent, 2),
                'num_threads': num_threads,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}
            
    def get_statistics(self, window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get performance statistics for a time window.
        
        Args:
            window_minutes: Time window in minutes
            
        Returns:
            Dict with statistics
        """
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        # Filter recent data
        recent_cpu = [s for s in self.cpu_history if s['timestamp'] > cutoff_time]
        recent_memory = [s for s in self.memory_history if s['timestamp'] > cutoff_time]
        recent_responses = [s for s in self.response_times if s['timestamp'] > cutoff_time]
        
        stats = {
            'window_minutes': window_minutes,
            'cpu': self._calculate_stats([s['value'] for s in recent_cpu]),
            'memory_mb': self._calculate_stats([s['value'] for s in recent_memory]),
            'response_time_ms': self._calculate_stats([s['duration'] * 1000 for s in recent_responses]),
            'sample_count': {
                'cpu': len(recent_cpu),
                'memory': len(recent_memory),
                'responses': len(recent_responses)
            }
        }
        
        return stats
        
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistics for a list of values."""
        if not values:
            return {'min': 0, 'max': 0, 'avg': 0, 'median': 0}
            
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            'min': round(min(values), 2),
            'max': round(max(values), 2),
            'avg': round(sum(values) / n, 2),
            'median': round(sorted_values[n // 2], 2),
            'p95': round(sorted_values[int(n * 0.95)] if n > 0 else 0, 2),
            'p99': round(sorted_values[int(n * 0.99)] if n > 0 else 0, 2)
        }
        
    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile function execution."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = self.process.memory_info().rss / 1024 / 1024
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                end_memory = self.process.memory_info().rss / 1024 / 1024
                
                duration = end_time - start_time
                memory_delta = end_memory - start_memory
                
                logger.info(
                    f"Profile [{func.__name__}]: "
                    f"Time={duration:.3f}s, Memory={memory_delta:+.2f}MB"
                )
                
                self.record_response_time(duration, func.__name__)
                
        return wrapper
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            'memory_total_gb': round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
            'memory_available_gb': round(psutil.virtual_memory().available / 1024 / 1024 / 1024, 2),
            'disk_usage': psutil.disk_usage('/')._asdict()
        }


# Global instance
performance_monitor = PerformanceMonitor()


def profile(func: Callable) -> Callable:
    """Global profiling decorator."""
    return performance_monitor.profile_function(func)


