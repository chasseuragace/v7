"""
Metrics collection utilities for performance monitoring.
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict, deque
import threading

from src.core.logging import LoggerMixin
from src.interfaces.base import MetricsCollector


class InMemoryMetricsCollector(MetricsCollector, LoggerMixin):
    """In-memory metrics collector for development and testing."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.counters = defaultdict(int)
        self.gauges = {}
        self.timings = defaultdict(lambda: deque(maxlen=max_history))
        self.lock = threading.Lock()
    
    def record_processing_time(self, operation: str, duration: float) -> None:
        """Record processing time for an operation."""
        with self.lock:
            self.timings[operation].append({
                'duration': duration,
                'timestamp': datetime.now()
            })
    
    def increment_counter(self, metric: str, tags: Dict[str, str] = None) -> None:
        """Increment a counter metric."""
        with self.lock:
            key = self._create_metric_key(metric, tags)
            self.counters[key] += 1
    
    def record_gauge(self, metric: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a gauge metric."""
        with self.lock:
            key = self._create_metric_key(metric, tags)
            self.gauges[key] = {
                'value': value,
                'timestamp': datetime.now()
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        with self.lock:
            summary = {
                'counters': dict(self.counters),
                'gauges': {k: v['value'] for k, v in self.gauges.items()},
                'timing_stats': {}
            }
            
            # Calculate timing statistics
            for operation, timings in self.timings.items():
                if timings:
                    durations = [t['duration'] for t in timings]
                    summary['timing_stats'][operation] = {
                        'count': len(durations),
                        'avg': sum(durations) / len(durations),
                        'min': min(durations),
                        'max': max(durations)
                    }
            
            return summary
    
    def _create_metric_key(self, metric: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a metric key with tags."""
        if not tags:
            return metric
        
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric}[{tag_str}]"


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, metrics_collector: MetricsCollector, operation: str):
        self.metrics_collector = metrics_collector
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics_collector.record_processing_time(self.operation, duration)


def timed_operation(metrics_collector: MetricsCollector, operation_name: str = None):
    """Decorator for timing function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            with PerformanceTimer(metrics_collector, op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
