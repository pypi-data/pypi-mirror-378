"""
Enhanced performance logger for system metrics and monitoring.

This module provides comprehensive performance logging with:
- System performance metrics tracking
- Execution time monitoring
- Memory usage logging
- Structured format for performance data
- Integration with monitoring systems
"""

import time
import psutil
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from functools import wraps
import gc

from .factory import get_performance_logger, PerformanceLogger as BasePerformanceLogger
from .context import LogContext, monitoring_context


@dataclass
class PerformanceMetric:
    """Container for performance metric data."""
    timestamp: datetime
    metric_type: str
    component: str
    operation: str
    value: float
    unit: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionProfile:
    """Container for execution profiling data."""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    memory_before_mb: Optional[float] = None
    memory_after_mb: Optional[float] = None
    memory_delta_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedPerformanceLogger:
    """
    Enhanced performance logger with comprehensive metrics tracking.
    
    This logger provides:
    - System resource monitoring
    - Execution time tracking with decorators
    - Memory usage profiling
    - CPU utilization monitoring
    - Structured performance data logging
    - Integration with external monitoring systems
    """
    
    def __init__(self, enable_system_monitoring: bool = True, 
                 monitoring_interval: float = 30.0):
        """
        Initialize enhanced performance logger.
        
        Args:
            enable_system_monitoring: Enable background system monitoring
            monitoring_interval: Interval for system monitoring in seconds
        """
        self._logger = get_performance_logger()
        self._metrics: List[PerformanceMetric] = []
        self._active_profiles: Dict[str, ExecutionProfile] = {}
        self._lock = threading.RLock()
        
        # System monitoring
        self._enable_system_monitoring = enable_system_monitoring
        self._monitoring_interval = monitoring_interval
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        if enable_system_monitoring:
            self._start_system_monitoring()
    
    def _start_system_monitoring(self) -> None:
        """Start background system monitoring thread."""
        self._monitoring_thread = threading.Thread(
            target=self._system_monitoring_loop, 
            daemon=True
        )
        self._monitoring_thread.start()
    
    def _system_monitoring_loop(self) -> None:
        """Background system monitoring loop."""
        while not self._stop_monitoring.wait(self._monitoring_interval):
            try:
                self._collect_system_metrics()
            except Exception as e:
                self._logger.error(
                    f"Error collecting system metrics: {str(e)}",
                    extra={'error_type': 'system_monitoring', 'component': 'performance_logger'},
                    exc_info=True
                )
    
    def _collect_system_metrics(self) -> None:
        """Collect and log system performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.log_cpu_usage(cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.log_memory_usage(
                total_mb=memory.total / 1024 / 1024,
                used_mb=memory.used / 1024 / 1024,
                available_mb=memory.available / 1024 / 1024,
                percent=memory.percent
            )
            
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.log_disk_io(
                    read_bytes=disk_io.read_bytes,
                    write_bytes=disk_io.write_bytes,
                    read_count=disk_io.read_count,
                    write_count=disk_io.write_count
                )
            
            # Network I/O metrics
            net_io = psutil.net_io_counters()
            if net_io:
                self.log_network_io(
                    bytes_sent=net_io.bytes_sent,
                    bytes_recv=net_io.bytes_recv,
                    packets_sent=net_io.packets_sent,
                    packets_recv=net_io.packets_recv
                )
                
        except Exception as e:
            self._logger.error(
                f"Failed to collect system metrics: {str(e)}",
                extra={'error_type': 'metrics_collection'},
                exc_info=True
            )
    
    def log_execution_time(self, operation: str, duration_ms: float, 
                          component: str = "unknown", **metadata) -> None:
        """
        Log execution time metric.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            component: Component name
            **metadata: Additional metadata
        """
        context = monitoring_context("execution_time")
        
        self._logger.execution_time(
            operation=operation,
            duration_ms=duration_ms,
            context=context,
            component=component,
            **metadata
        )
        
        # Store metric for analysis
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_type="execution_time",
            component=component,
            operation=operation,
            value=duration_ms,
            unit="milliseconds",
            metadata=metadata
        )
        
        with self._lock:
            self._metrics.append(metric)
    
    def log_memory_usage(self, total_mb: float = None, used_mb: float = None,
                        available_mb: float = None, percent: float = None,
                        component: str = "system", **metadata) -> None:
        """
        Log memory usage metrics.
        
        Args:
            total_mb: Total memory in MB
            used_mb: Used memory in MB
            available_mb: Available memory in MB
            percent: Memory usage percentage
            component: Component name
            **metadata: Additional metadata
        """
        context = monitoring_context("memory_usage")
        
        if used_mb is not None:
            self._logger.memory_usage(
                component=component,
                memory_mb=used_mb,
                context=context,
                total_mb=total_mb,
                available_mb=available_mb,
                percent=percent,
                **metadata
            )
        
        # Store metrics for analysis
        if used_mb is not None:
            metric = PerformanceMetric(
                timestamp=datetime.utcnow(),
                metric_type="memory_usage",
                component=component,
                operation="memory_monitoring",
                value=used_mb,
                unit="megabytes",
                metadata={
                    'total_mb': total_mb,
                    'available_mb': available_mb,
                    'percent': percent,
                    **metadata
                }
            )
            
            with self._lock:
                self._metrics.append(metric)
    
    def log_cpu_usage(self, cpu_percent: float, component: str = "system", **metadata) -> None:
        """
        Log CPU usage metric.
        
        Args:
            cpu_percent: CPU usage percentage
            component: Component name
            **metadata: Additional metadata
        """
        context = monitoring_context("cpu_usage")
        
        self._logger.info(
            f"CPU usage: {cpu_percent:.1f}%",
            context=context,
            extra={
                'metric_type': 'cpu_usage',
                'component': component,
                'cpu_percent': cpu_percent,
                **metadata
            }
        )
        
        # Store metric for analysis
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_type="cpu_usage",
            component=component,
            operation="cpu_monitoring",
            value=cpu_percent,
            unit="percent",
            metadata=metadata
        )
        
        with self._lock:
            self._metrics.append(metric)
    
    def log_throughput(self, operation: str, count: int, duration_s: float,
                      component: str = "unknown", **metadata) -> None:
        """
        Log throughput metric.
        
        Args:
            operation: Operation name
            count: Number of operations
            duration_s: Duration in seconds
            component: Component name
            **metadata: Additional metadata
        """
        context = monitoring_context("throughput")
        
        self._logger.throughput(
            operation=operation,
            count=count,
            duration_s=duration_s,
            context=context,
            component=component,
            **metadata
        )
        
        # Store metric for analysis
        rate = count / duration_s if duration_s > 0 else 0
        metric = PerformanceMetric(
            timestamp=datetime.utcnow(),
            metric_type="throughput",
            component=component,
            operation=operation,
            value=rate,
            unit="operations_per_second",
            metadata={
                'count': count,
                'duration_s': duration_s,
                **metadata
            }
        )
        
        with self._lock:
            self._metrics.append(metric)
    
    def log_disk_io(self, read_bytes: int = None, write_bytes: int = None,
                   read_count: int = None, write_count: int = None,
                   component: str = "system", **metadata) -> None:
        """
        Log disk I/O metrics.
        
        Args:
            read_bytes: Bytes read
            write_bytes: Bytes written
            read_count: Number of read operations
            write_count: Number of write operations
            component: Component name
            **metadata: Additional metadata
        """
        context = monitoring_context("disk_io")
        
        self._logger.info(
            f"Disk I/O - Read: {read_bytes or 0} bytes ({read_count or 0} ops), "
            f"Write: {write_bytes or 0} bytes ({write_count or 0} ops)",
            context=context,
            extra={
                'metric_type': 'disk_io',
                'component': component,
                'read_bytes': read_bytes,
                'write_bytes': write_bytes,
                'read_count': read_count,
                'write_count': write_count,
                **metadata
            }
        )
    
    def log_network_io(self, bytes_sent: int = None, bytes_recv: int = None,
                      packets_sent: int = None, packets_recv: int = None,
                      component: str = "system", **metadata) -> None:
        """
        Log network I/O metrics.
        
        Args:
            bytes_sent: Bytes sent
            bytes_recv: Bytes received
            packets_sent: Packets sent
            packets_recv: Packets received
            component: Component name
            **metadata: Additional metadata
        """
        context = monitoring_context("network_io")
        
        self._logger.info(
            f"Network I/O - Sent: {bytes_sent or 0} bytes ({packets_sent or 0} packets), "
            f"Recv: {bytes_recv or 0} bytes ({packets_recv or 0} packets)",
            context=context,
            extra={
                'metric_type': 'network_io',
                'component': component,
                'bytes_sent': bytes_sent,
                'bytes_recv': bytes_recv,
                'packets_sent': packets_sent,
                'packets_recv': packets_recv,
                **metadata
            }
        )
    
    @contextmanager
    def profile_execution(self, operation: str, component: str = "unknown", **metadata):
        """
        Context manager for profiling code execution.
        
        Args:
            operation: Operation name
            component: Component name
            **metadata: Additional metadata
            
        Usage:
            with performance_logger.profile_execution("database_query"):
                # Code to profile
                result = database.query(...)
        """
        profile_id = f"{component}:{operation}:{id(threading.current_thread())}"
        
        # Start profiling
        start_time = time.perf_counter()
        memory_before = self._get_memory_usage()
        
        profile = ExecutionProfile(
            operation=operation,
            start_time=start_time,
            memory_before_mb=memory_before,
            metadata=metadata
        )
        
        with self._lock:
            self._active_profiles[profile_id] = profile
        
        try:
            yield profile
        finally:
            # End profiling
            end_time = time.perf_counter()
            memory_after = self._get_memory_usage()
            
            profile.end_time = end_time
            profile.duration_ms = (end_time - start_time) * 1000
            profile.memory_after_mb = memory_after
            profile.memory_delta_mb = memory_after - memory_before if memory_before else None
            
            # Log the execution profile
            self.log_execution_time(
                operation=operation,
                duration_ms=profile.duration_ms,
                component=component,
                memory_before_mb=memory_before,
                memory_after_mb=memory_after,
                memory_delta_mb=profile.memory_delta_mb,
                **metadata
            )
            
            # Clean up
            with self._lock:
                self._active_profiles.pop(profile_id, None)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def performance_decorator(self, operation: str = None, component: str = "unknown"):
        """
        Decorator for automatic performance profiling.
        
        Args:
            operation: Operation name (defaults to function name)
            component: Component name
            
        Usage:
            @performance_logger.performance_decorator(component="trading")
            def execute_trade(symbol, quantity):
                # Function implementation
                pass
        """
        def decorator(func: Callable) -> Callable:
            op_name = operation or func.__name__
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.profile_execution(op_name, component):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """
        Get performance summary for the specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing performance summary
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            recent_metrics = [m for m in self._metrics if m.timestamp >= cutoff]
        
        if not recent_metrics:
            return {'message': 'No metrics available for the specified period'}
        
        # Group metrics by type
        metrics_by_type = {}
        for metric in recent_metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)
        
        summary = {
            'period_hours': hours,
            'total_metrics': len(recent_metrics),
            'metric_types': list(metrics_by_type.keys()),
            'analysis': {}
        }
        
        # Analyze each metric type
        for metric_type, metrics in metrics_by_type.items():
            values = [m.value for m in metrics]
            summary['analysis'][metric_type] = {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'unit': metrics[0].unit if metrics else 'unknown'
            }
        
        return summary
    
    def get_slow_operations(self, threshold_ms: float = 1000, hours: int = 1) -> List[Dict[str, Any]]:
        """
        Get operations that exceeded the performance threshold.
        
        Args:
            threshold_ms: Threshold in milliseconds
            hours: Number of hours to analyze
            
        Returns:
            List of slow operations
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            execution_metrics = [
                m for m in self._metrics 
                if (m.timestamp >= cutoff and 
                    m.metric_type == "execution_time" and 
                    m.value > threshold_ms)
            ]
        
        slow_ops = []
        for metric in execution_metrics:
            slow_ops.append({
                'timestamp': metric.timestamp.isoformat(),
                'operation': metric.operation,
                'component': metric.component,
                'duration_ms': metric.value,
                'threshold_ms': threshold_ms,
                'metadata': metric.metadata
            })
        
        return sorted(slow_ops, key=lambda x: x['duration_ms'], reverse=True)
    
    def clear_metrics(self) -> None:
        """Clear stored metrics (useful for testing or memory management)."""
        with self._lock:
            self._metrics.clear()
    
    def stop_monitoring(self) -> None:
        """Stop background system monitoring."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=5)


# Global performance logger instance
_performance_logger = None


def get_enhanced_performance_logger() -> EnhancedPerformanceLogger:
    """Get global enhanced performance logger instance."""
    global _performance_logger
    if _performance_logger is None:
        _performance_logger = EnhancedPerformanceLogger()
    return _performance_logger