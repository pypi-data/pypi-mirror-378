"""
Enhanced error logger for centralized error tracking and reporting.

This module provides comprehensive error logging with:
- Centralized error collection and categorization
- Exception context capture and stack trace logging
- Error reporting with structured metadata
- Integration with error tracking systems
- Error pattern analysis and alerting
"""

import sys
import traceback
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Type, Union
from collections import defaultdict, deque
from enum import Enum
import hashlib
import json

from .factory import get_error_logger, ErrorLogger as BaseErrorLogger
from .context import LogContext, error_context


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_API = "external_api"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    UNKNOWN = "unknown"


@dataclass
class ErrorEvent:
    """Container for error event information."""
    timestamp: datetime
    error_id: str
    error_type: str
    error_message: str
    component: str
    operation: str
    severity: ErrorSeverity
    category: ErrorCategory
    stack_trace: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_notes: Optional[str] = None


@dataclass
class ErrorPattern:
    """Container for error pattern analysis."""
    error_signature: str
    count: int
    first_seen: datetime
    last_seen: datetime
    components: List[str]
    operations: List[str]
    severity: ErrorSeverity
    category: ErrorCategory
    sample_error: ErrorEvent


class EnhancedErrorLogger:
    """
    Enhanced error logger with comprehensive error tracking and analysis.
    
    This logger provides:
    - Centralized error collection with categorization
    - Exception context capture and stack trace logging
    - Error pattern detection and analysis
    - Structured error reporting with metadata
    - Integration with external error tracking systems
    - Error alerting and notification capabilities
    """
    
    def __init__(self, max_errors: int = 10000, enable_pattern_analysis: bool = True):
        """
        Initialize enhanced error logger.
        
        Args:
            max_errors: Maximum number of errors to keep in memory
            enable_pattern_analysis: Enable error pattern detection
        """
        self._logger = get_error_logger()
        self._errors: deque = deque(maxlen=max_errors)
        self._error_patterns: Dict[str, ErrorPattern] = {}
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._lock = threading.RLock()
        
        self._enable_pattern_analysis = enable_pattern_analysis
        self._session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    def _generate_error_id(self, error_type: str, error_message: str, 
                          component: str, operation: str) -> str:
        """Generate unique error ID for tracking."""
        error_data = f"{error_type}:{error_message}:{component}:{operation}"
        return hashlib.md5(error_data.encode()).hexdigest()[:12]
    
    def _generate_error_signature(self, error_type: str, component: str, 
                                 operation: str) -> str:
        """Generate error signature for pattern analysis."""
        return f"{error_type}:{component}:{operation}"
    
    def _categorize_error(self, error_type: str, error_message: str, 
                         component: str) -> ErrorCategory:
        """Automatically categorize error based on type and context."""
        error_type_lower = error_type.lower()
        error_message_lower = error_message.lower()
        component_lower = component.lower()
        
        # Network-related errors
        if any(keyword in error_type_lower for keyword in 
               ['connection', 'timeout', 'network', 'socket', 'http']):
            return ErrorCategory.NETWORK
        
        # Database-related errors
        if any(keyword in component_lower for keyword in 
               ['database', 'db', 'sql', 'mongo', 'redis']):
            return ErrorCategory.DATABASE
        
        # Validation errors
        if any(keyword in error_type_lower for keyword in 
               ['validation', 'invalid', 'format', 'parse']):
            return ErrorCategory.VALIDATION
        
        # Configuration errors
        if any(keyword in error_message_lower for keyword in 
               ['config', 'setting', 'parameter', 'environment']):
            return ErrorCategory.CONFIGURATION
        
        # Security errors
        if any(keyword in error_type_lower for keyword in 
               ['permission', 'auth', 'security', 'access', 'forbidden']):
            return ErrorCategory.SECURITY
        
        # Performance errors
        if any(keyword in error_message_lower for keyword in 
               ['memory', 'timeout', 'slow', 'performance']):
            return ErrorCategory.PERFORMANCE
        
        # External API errors
        if any(keyword in component_lower for keyword in 
               ['api', 'external', 'service', 'client']):
            return ErrorCategory.EXTERNAL_API
        
        # System errors
        if any(keyword in error_type_lower for keyword in 
               ['system', 'os', 'file', 'disk', 'memory']):
            return ErrorCategory.SYSTEM
        
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error_type: str, error_message: str, 
                           category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on type and category."""
        error_type_lower = error_type.lower()
        error_message_lower = error_message.lower()
        
        # Critical errors
        if any(keyword in error_type_lower for keyword in 
               ['critical', 'fatal', 'crash', 'abort']):
            return ErrorSeverity.CRITICAL
        
        if category == ErrorCategory.SECURITY:
            return ErrorSeverity.HIGH
        
        # High severity errors
        if any(keyword in error_message_lower for keyword in 
               ['failed to start', 'cannot connect', 'out of memory']):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.DATABASE, ErrorCategory.EXTERNAL_API]:
            return ErrorSeverity.MEDIUM
        
        if any(keyword in error_type_lower for keyword in 
               ['warning', 'deprecated']):
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM
    
    def log_error(self, error_type: str, error_message: str, 
                  component: str = "unknown", operation: str = "unknown",
                  severity: Optional[ErrorSeverity] = None,
                  category: Optional[ErrorCategory] = None,
                  **metadata) -> str:
        """
        Log an error with comprehensive tracking.
        
        Args:
            error_type: Type of error
            error_message: Error message
            component: Component where error occurred
            operation: Operation being performed
            severity: Error severity (auto-determined if not provided)
            category: Error category (auto-determined if not provided)
            **metadata: Additional metadata
            
        Returns:
            Error ID for tracking
        """
        # Auto-categorize if not provided
        if category is None:
            category = self._categorize_error(error_type, error_message, component)
        
        if severity is None:
            severity = self._determine_severity(error_type, error_message, category)
        
        # Generate error ID
        error_id = self._generate_error_id(error_type, error_message, component, operation)
        
        # Create error event
        error_event = ErrorEvent(
            timestamp=datetime.utcnow(),
            error_id=error_id,
            error_type=error_type,
            error_message=error_message,
            component=component,
            operation=operation,
            severity=severity,
            category=category,
            context_data=metadata.get('context_data', {}),
            metadata=metadata
        )
        
        # Store error
        with self._lock:
            self._errors.append(error_event)
            self._error_counts[error_id] += 1
        
        # Pattern analysis
        if self._enable_pattern_analysis:
            self._analyze_error_pattern(error_event)
        
        # Create logging context
        context = error_context(error_type, component)
        
        # Log using centralized logger
        self._logger.error_occurred(
            error_type=error_type,
            error_message=error_message,
            component=component,
            context=context,
            operation=operation,
            error_id=error_id,
            severity=severity.value,
            category=category.value,
            session_id=self._session_id,
            **metadata
        )
        
        return error_id
    
    def log_exception(self, exception: Exception, component: str = "unknown", 
                     operation: str = "unknown", 
                     severity: Optional[ErrorSeverity] = None,
                     category: Optional[ErrorCategory] = None,
                     **metadata) -> str:
        """
        Log an exception with full context and stack trace.
        
        Args:
            exception: Exception instance
            component: Component where exception occurred
            operation: Operation being performed
            severity: Error severity (auto-determined if not provided)
            category: Error category (auto-determined if not provided)
            **metadata: Additional metadata
            
        Returns:
            Error ID for tracking
        """
        error_type = type(exception).__name__
        error_message = str(exception)
        
        # Capture stack trace
        stack_trace = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        
        # Auto-categorize if not provided
        if category is None:
            category = self._categorize_error(error_type, error_message, component)
        
        if severity is None:
            severity = self._determine_severity(error_type, error_message, category)
        
        # Generate error ID
        error_id = self._generate_error_id(error_type, error_message, component, operation)
        
        # Create error event
        error_event = ErrorEvent(
            timestamp=datetime.utcnow(),
            error_id=error_id,
            error_type=error_type,
            error_message=error_message,
            component=component,
            operation=operation,
            severity=severity,
            category=category,
            stack_trace=stack_trace,
            context_data=metadata.get('context_data', {}),
            metadata=metadata
        )
        
        # Store error
        with self._lock:
            self._errors.append(error_event)
            self._error_counts[error_id] += 1
        
        # Pattern analysis
        if self._enable_pattern_analysis:
            self._analyze_error_pattern(error_event)
        
        # Create logging context
        context = error_context(error_type, component)
        
        # Log using centralized logger
        self._logger.exception_caught(
            exception=exception,
            component=component,
            operation=operation,
            context=context,
            error_id=error_id,
            severity=severity.value,
            category=category.value,
            session_id=self._session_id,
            stack_trace=stack_trace,
            **metadata
        )
        
        return error_id
    
    def log_validation_error(self, field: str, value: str, reason: str,
                           component: str = "validation", **metadata) -> str:
        """
        Log a validation error with structured information.
        
        Args:
            field: Field that failed validation
            value: Value that was invalid
            reason: Reason for validation failure
            component: Component performing validation
            **metadata: Additional metadata
            
        Returns:
            Error ID for tracking
        """
        error_type = "ValidationError"
        error_message = f"Field '{field}' validation failed: {reason}"
        
        # Create logging context
        context = error_context("validation", component)
        
        # Log using centralized logger
        self._logger.validation_error(
            field=field,
            value=value,
            reason=reason,
            context=context,
            component=component,
            session_id=self._session_id,
            **metadata
        )
        
        # Also log as regular error for tracking
        return self.log_error(
            error_type=error_type,
            error_message=error_message,
            component=component,
            operation="validation",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            field=field,
            value=value,
            reason=reason,
            **metadata
        )
    
    def _analyze_error_pattern(self, error_event: ErrorEvent) -> None:
        """Analyze error patterns for trend detection."""
        signature = self._generate_error_signature(
            error_event.error_type, 
            error_event.component, 
            error_event.operation
        )
        
        with self._lock:
            if signature in self._error_patterns:
                pattern = self._error_patterns[signature]
                pattern.count += 1
                pattern.last_seen = error_event.timestamp
                
                # Update components and operations lists
                if error_event.component not in pattern.components:
                    pattern.components.append(error_event.component)
                if error_event.operation not in pattern.operations:
                    pattern.operations.append(error_event.operation)
                
                # Update severity if current error is more severe
                if error_event.severity.value > pattern.severity.value:
                    pattern.severity = error_event.severity
            else:
                # Create new pattern
                self._error_patterns[signature] = ErrorPattern(
                    error_signature=signature,
                    count=1,
                    first_seen=error_event.timestamp,
                    last_seen=error_event.timestamp,
                    components=[error_event.component],
                    operations=[error_event.operation],
                    severity=error_event.severity,
                    category=error_event.category,
                    sample_error=error_event
                )
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get error summary for the specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing error summary
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            recent_errors = [e for e in self._errors if e.timestamp >= cutoff]
        
        if not recent_errors:
            return {'message': 'No errors in the specified period'}
        
        # Count by severity
        severity_counts = defaultdict(int)
        for error in recent_errors:
            severity_counts[error.severity.value] += 1
        
        # Count by category
        category_counts = defaultdict(int)
        for error in recent_errors:
            category_counts[error.category.value] += 1
        
        # Count by component
        component_counts = defaultdict(int)
        for error in recent_errors:
            component_counts[error.component] += 1
        
        # Top error types
        error_type_counts = defaultdict(int)
        for error in recent_errors:
            error_type_counts[error.error_type] += 1
        
        return {
            'period_hours': hours,
            'total_errors': len(recent_errors),
            'severity_distribution': dict(severity_counts),
            'category_distribution': dict(category_counts),
            'top_components': dict(sorted(component_counts.items(), 
                                        key=lambda x: x[1], reverse=True)[:10]),
            'top_error_types': dict(sorted(error_type_counts.items(), 
                                         key=lambda x: x[1], reverse=True)[:10]),
            'session_id': self._session_id
        }
    
    def get_error_patterns(self, min_count: int = 2) -> List[Dict[str, Any]]:
        """
        Get detected error patterns.
        
        Args:
            min_count: Minimum occurrence count to include pattern
            
        Returns:
            List of error patterns
        """
        with self._lock:
            patterns = []
            for signature, pattern in self._error_patterns.items():
                if pattern.count >= min_count:
                    patterns.append({
                        'signature': signature,
                        'count': pattern.count,
                        'first_seen': pattern.first_seen.isoformat(),
                        'last_seen': pattern.last_seen.isoformat(),
                        'components': pattern.components,
                        'operations': pattern.operations,
                        'severity': pattern.severity.value,
                        'category': pattern.category.value,
                        'sample_error_id': pattern.sample_error.error_id
                    })
            
            return sorted(patterns, key=lambda x: x['count'], reverse=True)
    
    def get_critical_errors(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get critical errors from the specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            List of critical errors
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            critical_errors = [
                e for e in self._errors 
                if (e.timestamp >= cutoff and 
                    e.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH])
            ]
        
        return [
            {
                'error_id': error.error_id,
                'timestamp': error.timestamp.isoformat(),
                'error_type': error.error_type,
                'error_message': error.error_message,
                'component': error.component,
                'operation': error.operation,
                'severity': error.severity.value,
                'category': error.category.value,
                'metadata': error.metadata
            }
            for error in critical_errors
        ]
    
    def resolve_error(self, error_id: str, resolution_notes: str) -> bool:
        """
        Mark an error as resolved.
        
        Args:
            error_id: Error ID to resolve
            resolution_notes: Notes about the resolution
            
        Returns:
            True if error was found and resolved, False otherwise
        """
        with self._lock:
            for error in self._errors:
                if error.error_id == error_id:
                    error.resolved = True
                    error.resolution_notes = resolution_notes
                    
                    # Log resolution
                    self._logger.info(
                        f"Error resolved: {error_id} - {resolution_notes}",
                        extra={
                            'error_resolution': True,
                            'error_id': error_id,
                            'resolution_notes': resolution_notes,
                            'session_id': self._session_id
                        }
                    )
                    return True
        
        return False
    
    def export_errors(self, hours: int = 24, include_resolved: bool = False) -> str:
        """
        Export errors to JSON format for external analysis.
        
        Args:
            hours: Number of hours to export
            include_resolved: Include resolved errors
            
        Returns:
            JSON string containing error data
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            errors_to_export = []
            for error in self._errors:
                if error.timestamp >= cutoff:
                    if include_resolved or not error.resolved:
                        error_data = {
                            'error_id': error.error_id,
                            'timestamp': error.timestamp.isoformat(),
                            'error_type': error.error_type,
                            'error_message': error.error_message,
                            'component': error.component,
                            'operation': error.operation,
                            'severity': error.severity.value,
                            'category': error.category.value,
                            'stack_trace': error.stack_trace,
                            'context_data': error.context_data,
                            'metadata': error.metadata,
                            'resolved': error.resolved,
                            'resolution_notes': error.resolution_notes
                        }
                        errors_to_export.append(error_data)
        
        export_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'period_hours': hours,
            'session_id': self._session_id,
            'total_errors': len(errors_to_export),
            'errors': errors_to_export
        }
        
        return json.dumps(export_data, indent=2)
    
    def clear_errors(self) -> None:
        """Clear stored errors (useful for testing or memory management)."""
        with self._lock:
            self._errors.clear()
            self._error_patterns.clear()
            self._error_counts.clear()


# Global error logger instance
_error_logger = None


def get_enhanced_error_logger() -> EnhancedErrorLogger:
    """Get global enhanced error logger instance."""
    global _error_logger
    if _error_logger is None:
        _error_logger = EnhancedErrorLogger()
    return _error_logger