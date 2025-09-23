"""
Performance optimization utilities for the logging system.

This module provides lazy evaluation, performance monitoring, and optimization
techniques to minimize logging overhead in performance-critical scenarios.
"""

import functools
import logging
import time
import threading
import weakref
from typing import Callable, Any, Dict, Optional, Union
from collections import defaultdict
from dataclasses import dataclass
import psutil
import os


@dataclass
class LoggingMetrics:
    """Metrics for logging performance monitoring."""
    total_calls: int = 0
    debug_calls: int = 0
    debug_skipped: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0


class LazyString:
    """
    Lazy string evaluation for expensive log message construction.
    
    This class defers string construction until the message is actually needed,
    which can significantly improve performance when debug logging is disabled.
    """
    
    def __init__(self, func: Callable[[], str], *args, **kwargs):
        """
        Initialize lazy string with function and arguments.
        
        Args:
            func: Function that returns the string when called
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._cached_result = None
        self._evaluated = False
    
    def __str__(self) -> str:
        """Evaluate and return the string."""
        if not self._evaluated:
            self._cached_result = self.func(*self.args, **self.kwargs)
            self._evaluated = True
        return self._cached_result
    
    def __repr__(self) -> str:
        """Return representation of lazy string."""
        return f"LazyString({self.func.__name__})"


class LazyFormat:
    """
    Lazy string formatting for log messages.
    
    This class defers string formatting until the message is actually logged,
    avoiding expensive string operations when logging is disabled.
    """
    
    def __init__(self, template: str, *args, **kwargs):
        """
        Initialize lazy format with template and arguments.
        
        Args:
            template: Format string template
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting
        """
        self.template = template
        self.args = args
        self.kwargs = kwargs
        self._cached_result = None
        self._evaluated = False
    
    def __str__(self) -> str:
        """Evaluate and return the formatted string."""
        if not self._evaluated:
            try:
                if self.args and self.kwargs:
                    self._cached_result = self.template.format(*self.args, **self.kwargs)
                elif self.args:
                    self._cached_result = self.template.format(*self.args)
                elif self.kwargs:
                    self._cached_result = self.template.format(**self.kwargs)
                else:
                    self._cached_result = self.template
            except (KeyError, IndexError, ValueError) as e:
                # Fallback to safe formatting
                self._cached_result = f"[Format Error: {e}] {self.template}"
            self._evaluated = True
        return self._cached_result
    
    def __repr__(self) -> str:
        """Return representation of lazy format."""
        return f"LazyFormat('{self.template[:50]}...')"


class PerformanceMonitor:
    """
    Monitor logging performance and collect metrics.
    
    This class tracks logging performance metrics to identify bottlenecks
    and optimize logging configuration.
    """
    
    def __init__(self):
        self._metrics = defaultdict(LoggingMetrics)
        self._lock = threading.Lock()
        self._start_time = time.time()
        self._process = psutil.Process(os.getpid())
    
    def record_log_call(self, logger_name: str, level: int, duration_ms: float, was_skipped: bool = False):
        """
        Record a logging call for performance tracking.
        
        Args:
            logger_name: Name of the logger
            level: Log level
            duration_ms: Time taken for the log call in milliseconds
            was_skipped: Whether the log call was skipped due to level filtering
        """
        with self._lock:
            metrics = self._metrics[logger_name]
            metrics.total_calls += 1
            
            if level == logging.DEBUG:
                metrics.debug_calls += 1
                if was_skipped:
                    metrics.debug_skipped += 1
            
            if not was_skipped:
                metrics.total_time_ms += duration_ms
                metrics.avg_time_ms = metrics.total_time_ms / (metrics.total_calls - metrics.debug_skipped)
    
    def get_metrics(self, logger_name: str = None) -> Union[LoggingMetrics, Dict[str, LoggingMetrics]]:
        """
        Get performance metrics for logger(s).
        
        Args:
            logger_name: Specific logger name, or None for all loggers
            
        Returns:
            LoggingMetrics for specific logger or dict of all metrics
        """
        with self._lock:
            if logger_name:
                return self._metrics.get(logger_name, LoggingMetrics())
            else:
                return dict(self._metrics)
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource usage."""
        try:
            memory_info = self._process.memory_info()
            cpu_percent = self._process.cpu_percent()
            
            return {
                'memory_mb': memory_info.rss / 1024 / 1024,
                'cpu_percent': cpu_percent,
                'uptime_seconds': time.time() - self._start_time
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {
                'memory_mb': 0.0,
                'cpu_percent': 0.0,
                'uptime_seconds': time.time() - self._start_time
            }
    
    def reset_metrics(self, logger_name: str = None):
        """
        Reset performance metrics.
        
        Args:
            logger_name: Specific logger to reset, or None for all loggers
        """
        with self._lock:
            if logger_name:
                if logger_name in self._metrics:
                    del self._metrics[logger_name]
            else:
                self._metrics.clear()


class OptimizedLogger:
    """
    Performance-optimized logger wrapper with lazy evaluation support.
    
    This wrapper adds performance optimizations including:
    - Lazy message evaluation
    - Level-based filtering before expensive operations
    - Performance monitoring
    - Memory-efficient caching
    """
    
    def __init__(self, logger: logging.Logger, monitor: Optional[PerformanceMonitor] = None):
        """
        Initialize optimized logger.
        
        Args:
            logger: Underlying Python logger
            monitor: Optional performance monitor
        """
        self.logger = logger
        self.monitor = monitor or PerformanceMonitor()
        self._level_cache = {}
        self._cache_lock = threading.Lock()
    
    def _is_enabled_for(self, level: int) -> bool:
        """
        Check if logging is enabled for level with caching.
        
        Args:
            level: Log level to check
            
        Returns:
            True if logging is enabled for this level
        """
        # Use cached result if available
        cache_key = (self.logger.name, level)
        if cache_key in self._level_cache:
            return self._level_cache[cache_key]
        
        # Check and cache result
        with self._cache_lock:
            enabled = self.logger.isEnabledFor(level)
            self._level_cache[cache_key] = enabled
            return enabled
    
    def _log_with_timing(self, level: int, message: Union[str, LazyString, LazyFormat], *args, **kwargs):
        """
        Log message with performance timing.
        
        Args:
            level: Log level
            message: Message to log (can be lazy)
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        start_time = time.perf_counter()
        
        # Check if logging is enabled for this level
        if not self._is_enabled_for(level):
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.monitor.record_log_call(self.logger.name, level, duration_ms, was_skipped=True)
            return
        
        # Evaluate lazy message if needed
        if isinstance(message, (LazyString, LazyFormat)):
            message = str(message)
        
        # Perform the actual logging
        self.logger.log(level, message, *args, **kwargs)
        
        # Record performance metrics
        duration_ms = (time.perf_counter() - start_time) * 1000
        self.monitor.record_log_call(self.logger.name, level, duration_ms, was_skipped=False)
    
    def debug(self, message: Union[str, LazyString, LazyFormat], *args, **kwargs):
        """Log debug message with lazy evaluation."""
        self._log_with_timing(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: Union[str, LazyString, LazyFormat], *args, **kwargs):
        """Log info message with lazy evaluation."""
        self._log_with_timing(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: Union[str, LazyString, LazyFormat], *args, **kwargs):
        """Log warning message with lazy evaluation."""
        self._log_with_timing(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: Union[str, LazyString, LazyFormat], *args, **kwargs):
        """Log error message with lazy evaluation."""
        self._log_with_timing(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: Union[str, LazyString, LazyFormat], *args, **kwargs):
        """Log critical message with lazy evaluation."""
        self._log_with_timing(logging.CRITICAL, message, *args, **kwargs)
    
    def exception(self, message: Union[str, LazyString, LazyFormat], *args, **kwargs):
        """Log exception with lazy evaluation."""
        kwargs['exc_info'] = True
        self._log_with_timing(logging.ERROR, message, *args, **kwargs)
    
    def clear_cache(self):
        """Clear the level cache (useful when log levels change)."""
        with self._cache_lock:
            self._level_cache.clear()


# Global performance monitor instance
_global_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _global_monitor


def lazy_string(func: Callable[[], str]) -> Callable[..., LazyString]:
    """
    Decorator to create lazy string functions.
    
    Args:
        func: Function that returns a string
        
    Returns:
        Decorated function that returns LazyString
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return LazyString(func, *args, **kwargs)
    return wrapper


def lazy_format(template: str) -> Callable[..., LazyFormat]:
    """
    Create a lazy format function for a template.
    
    Args:
        template: Format string template
        
    Returns:
        Function that creates LazyFormat instances
    """
    def formatter(*args, **kwargs):
        return LazyFormat(template, *args, **kwargs)
    return formatter


def optimize_logger(logger: logging.Logger, monitor: Optional[PerformanceMonitor] = None) -> OptimizedLogger:
    """
    Wrap a logger with performance optimizations.
    
    Args:
        logger: Logger to optimize
        monitor: Optional performance monitor
        
    Returns:
        OptimizedLogger instance
    """
    return OptimizedLogger(logger, monitor or _global_monitor)


# Convenience functions for common lazy logging patterns
def lazy_debug_format(template: str):
    """Create lazy format function optimized for debug logging."""
    return lazy_format(template)


def lazy_json_dump(obj: Any) -> LazyString:
    """Create lazy JSON serialization for logging."""
    import json
    return LazyString(lambda: json.dumps(obj, default=str, separators=(',', ':')))


def lazy_repr(obj: Any) -> LazyString:
    """Create lazy repr() for logging."""
    return LazyString(lambda: repr(obj))


def lazy_str_join(separator: str, items) -> LazyString:
    """Create lazy string join for logging."""
    return LazyString(lambda: separator.join(str(item) for item in items))


# Performance benchmarking utilities
class LoggingBenchmark:
    """Benchmark logging performance under different scenarios."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.optimized_logger = optimize_logger(logger)
    
    def benchmark_regular_logging(self, iterations: int = 10000) -> Dict[str, float]:
        """Benchmark regular logging performance."""
        start_time = time.perf_counter()
        
        for i in range(iterations):
            self.logger.debug(f"Debug message {i} with data: {{'key': 'value', 'number': {i}}}")
        
        duration = time.perf_counter() - start_time
        return {
            'total_time_s': duration,
            'avg_time_ms': (duration / iterations) * 1000,
            'messages_per_second': iterations / duration
        }
    
    def benchmark_lazy_logging(self, iterations: int = 10000) -> Dict[str, float]:
        """Benchmark lazy logging performance."""
        start_time = time.perf_counter()
        
        for i in range(iterations):
            self.optimized_logger.debug(
                LazyFormat("Debug message {} with data: {}", i, {'key': 'value', 'number': i})
            )
        
        duration = time.perf_counter() - start_time
        return {
            'total_time_s': duration,
            'avg_time_ms': (duration / iterations) * 1000,
            'messages_per_second': iterations / duration
        }
    
    def benchmark_disabled_logging(self, iterations: int = 10000) -> Dict[str, float]:
        """Benchmark performance when logging is disabled."""
        # Temporarily disable debug logging
        original_level = self.logger.level
        self.logger.setLevel(logging.INFO)
        
        try:
            start_time = time.perf_counter()
            
            for i in range(iterations):
                self.optimized_logger.debug(
                    LazyFormat("Debug message {} with data: {}", i, {'key': 'value', 'number': i})
                )
            
            duration = time.perf_counter() - start_time
            return {
                'total_time_s': duration,
                'avg_time_ms': (duration / iterations) * 1000,
                'messages_per_second': iterations / duration
            }
        finally:
            self.logger.setLevel(original_level)
    
    def run_full_benchmark(self) -> Dict[str, Dict[str, float]]:
        """Run complete benchmark suite."""
        return {
            'regular_logging': self.benchmark_regular_logging(),
            'lazy_logging': self.benchmark_lazy_logging(),
            'disabled_logging': self.benchmark_disabled_logging()
        }