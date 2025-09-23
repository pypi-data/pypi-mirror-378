"""
Structured logging formatters for consistent log output.

This module provides formatters for both machine-readable JSON logs and
human-readable console output, with context injection and performance optimization.
"""

import json
import logging
import os
import threading
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
import re

from .context import LogContext


class StructuredJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for machine-readable structured logging.
    
    This formatter creates consistent JSON log entries with:
    - Standardized field names and structure
    - Context information injection
    - Performance metadata
    - Exception handling
    - Sensitive data masking
    """
    
    def __init__(self, mask_sensitive: bool = True, include_performance: bool = True):
        super().__init__()
        self.mask_sensitive = mask_sensitive
        self.include_performance = include_performance
        self._sensitive_patterns = [
            re.compile(r'(api[_-]?key|secret|password|token|auth)', re.IGNORECASE),
            re.compile(r'(\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b)'),  # Credit card numbers
            re.compile(r'(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)'),  # Email addresses
        ]
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log entry structure
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': self._mask_sensitive_data(record.getMessage()) if self.mask_sensitive else record.getMessage()
        }
        
        # Add metadata
        metadata = {
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': threading.current_thread().name,
            'process': os.getpid()
        }
        log_entry['metadata'] = metadata
        
        # Add context information if available
        context_data = self._extract_context(record)
        if context_data:
            log_entry['context'] = context_data
        
        # Add performance information if enabled
        if self.include_performance:
            performance_data = self._extract_performance(record)
            if performance_data:
                log_entry['performance'] = performance_data
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self._format_exception(record.exc_info)
        
        # Add extra fields from the record
        extra_fields = self._extract_extra_fields(record)
        if extra_fields:
            log_entry.update(extra_fields)
        
        return json.dumps(log_entry, default=self._json_serializer, separators=(',', ':'))
    
    def _extract_context(self, record: logging.LogRecord) -> Optional[Dict[str, Any]]:
        """Extract context information from log record."""
        context_data = {}
        
        # Check for LogContext object
        if hasattr(record, 'context') and record.context:
            if isinstance(record.context, LogContext):
                context_data.update(record.context.to_dict())
            elif isinstance(record.context, dict):
                context_data.update(record.context)
        
        # Check for individual context fields
        context_fields = ['component', 'operation', 'symbol', 'exchange', 'strategy', 
                         'order_id', 'trade_id', 'user_id', 'session_id', 'request_id']
        
        for field in context_fields:
            if hasattr(record, field) and getattr(record, field):
                context_data[field] = getattr(record, field)
        
        return context_data if context_data else None
    
    def _extract_performance(self, record: logging.LogRecord) -> Optional[Dict[str, Any]]:
        """Extract performance information from log record."""
        performance_data = {}
        
        # Check for performance fields
        performance_fields = ['execution_time_ms', 'memory_usage_mb', 'cpu_percent', 
                            'duration_ms', 'throughput', 'latency_ms']
        
        for field in performance_fields:
            if hasattr(record, field) and getattr(record, field) is not None:
                performance_data[field] = getattr(record, field)
        
        return performance_data if performance_data else None
    
    def _extract_extra_fields(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract extra fields from log record."""
        # Standard fields to exclude
        standard_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process', 'getMessage',
            'exc_info', 'exc_text', 'stack_info', 'context'
        }
        
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in standard_fields and not key.startswith('_'):
                if self.mask_sensitive and isinstance(value, str):
                    value = self._mask_sensitive_data(value)
                extra_fields[key] = value
        
        return extra_fields
    
    def _format_exception(self, exc_info) -> Dict[str, Any]:
        """Format exception information."""
        exc_type, exc_value, exc_traceback = exc_info
        
        return {
            'type': exc_type.__name__ if exc_type else 'Unknown',
            'message': str(exc_value) if exc_value else 'No message',
            'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback)
        }
    
    def _mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in log messages."""
        if not isinstance(text, str):
            return text
        
        masked_text = text
        for pattern in self._sensitive_patterns:
            masked_text = pattern.sub(lambda m: self._mask_match(m.group()), masked_text)
        
        return masked_text
    
    def _mask_match(self, match: str) -> str:
        """Mask a matched sensitive string."""
        if len(match) <= 4:
            return '*' * len(match)
        else:
            return match[:2] + '*' * (len(match) - 4) + match[-2:]
    
    def _json_serializer(self, obj) -> str:
        """Custom JSON serializer for non-standard types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)


class SimpleFormatter(logging.Formatter):
    """
    Human-readable formatter for console output and development.
    
    This formatter provides clean, readable log output for development
    and console display while still including essential context information.
    """
    
    def __init__(self, include_context: bool = True, colorize: bool = None):
        super().__init__()
        self.include_context = include_context
        self.colorize = colorize if colorize is not None else self._should_colorize()
        
        # Color codes for different log levels
        self.colors = {
            'DEBUG': '\033[36m',     # Cyan
            'INFO': '\033[32m',      # Green
            'WARNING': '\033[33m',   # Yellow
            'ERROR': '\033[31m',     # Red
            'CRITICAL': '\033[35m',  # Magenta
            'RESET': '\033[0m'       # Reset
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for human-readable output."""
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format level with optional color
        level = record.levelname
        if self.colorize and level in self.colors:
            level = f"{self.colors[level]}{level}{self.colors['RESET']}"
        
        # Format logger name (shortened for readability)
        logger_name = self._shorten_logger_name(record.name)
        
        # Format location info
        location = f"{record.module}:{record.funcName}:{record.lineno}"
        
        # Base message
        message = record.getMessage()
        
        # Build the log line
        parts = [timestamp, level.ljust(8), logger_name.ljust(20), f"[{location}]", message]
        log_line = " - ".join(parts)
        
        # Add context information if available and enabled
        if self.include_context:
            context_info = self._format_context(record)
            if context_info:
                log_line += f" | {context_info}"
        
        # Add exception information if present
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)
        
        return log_line
    
    def _shorten_logger_name(self, name: str) -> str:
        """Shorten logger name for better readability."""
        if len(name) <= 20:
            return name
        
        parts = name.split('.')
        if len(parts) > 2:
            return f"{parts[0]}...{parts[-1]}"
        else:
            return name[:17] + "..."
    
    def _format_context(self, record: logging.LogRecord) -> Optional[str]:
        """Format context information for display."""
        context_parts = []
        
        # Extract context from LogContext object
        if hasattr(record, 'context') and record.context:
            if isinstance(record.context, LogContext):
                context_dict = record.context.to_dict()
                for key, value in context_dict.items():
                    if value and key in ['symbol', 'exchange', 'strategy', 'operation']:
                        context_parts.append(f"{key}={value}")
            elif isinstance(record.context, dict):
                for key, value in record.context.items():
                    if value and key in ['symbol', 'exchange', 'strategy', 'operation']:
                        context_parts.append(f"{key}={value}")
        
        # Extract individual context fields
        context_fields = ['symbol', 'exchange', 'strategy', 'operation', 'order_id', 'trade_id']
        for field in context_fields:
            if hasattr(record, field) and getattr(record, field):
                value = getattr(record, field)
                if field not in [part.split('=')[0] for part in context_parts]:  # Avoid duplicates
                    context_parts.append(f"{field}={value}")
        
        return " ".join(context_parts) if context_parts else None
    
    def _should_colorize(self) -> bool:
        """Determine if output should be colorized."""
        # Check if we're in a terminal that supports colors
        return (
            hasattr(os, 'isatty') and 
            os.isatty(2) and  # stderr
            os.getenv('TERM') != 'dumb' and
            os.getenv('NO_COLOR') is None
        )


class PerformanceOptimizedFormatter(StructuredJSONFormatter):
    """
    Performance-optimized formatter for high-frequency logging.
    
    This formatter reduces overhead for high-frequency logging scenarios
    by caching formatted strings and minimizing object creation.
    """
    
    def __init__(self, cache_size: int = 1000, **kwargs):
        super().__init__(**kwargs)
        self.cache_size = cache_size
        self._format_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with caching for performance."""
        # Create cache key from record essentials
        cache_key = (
            record.levelname,
            record.name,
            record.module,
            record.funcName,
            record.lineno,
            record.getMessage()
        )
        
        # Check cache first
        if cache_key in self._format_cache:
            self._cache_hits += 1
            cached_entry = self._format_cache[cache_key].copy()
            # Update timestamp for cached entry
            cached_entry['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            return json.dumps(cached_entry, default=self._json_serializer, separators=(',', ':'))
        
        # Format normally and cache result
        self._cache_misses += 1
        formatted = super().format(record)
        
        # Cache management
        if len(self._format_cache) >= self.cache_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._format_cache.keys())[:self.cache_size // 4]
            for key in keys_to_remove:
                del self._format_cache[key]
        
        # Parse and cache the formatted JSON
        try:
            parsed = json.loads(formatted)
            self._format_cache[cache_key] = parsed
        except json.JSONDecodeError:
            pass  # Don't cache if we can't parse
        
        return formatted
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate_percent': round(hit_rate, 2),
            'cache_size': len(self._format_cache)
        }


class CompactFormatter(logging.Formatter):
    """
    Compact formatter for space-constrained environments.
    
    This formatter produces minimal log output while retaining
    essential information for debugging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format record in compact form."""
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        level_short = record.levelname[0]  # Just first letter
        logger_short = record.name.split('.')[-1][:8]  # Last component, max 8 chars
        
        message = record.getMessage()
        if len(message) > 80:
            message = message[:77] + "..."
        
        return f"{timestamp} {level_short} {logger_short}: {message}"