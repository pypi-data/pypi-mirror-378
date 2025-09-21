"""
Logging context management for structured logging.

This module provides context information that can be attached to log messages
for better traceability and debugging.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import threading
import uuid
from contextlib import contextmanager


@dataclass
class LogContext:
    """
    Context information for structured logging.
    
    This class holds contextual information that gets attached to log messages
    to provide better traceability and debugging capabilities.
    """
    
    component: str
    operation: str
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    strategy: Optional[str] = None
    order_id: Optional[str] = None
    trade_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize context with auto-generated IDs if not provided."""
        if self.session_id is None:
            self.session_id = getattr(threading.current_thread(), 'session_id', None)
        
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def update(self, **kwargs) -> 'LogContext':
        """Create new context with updated values."""
        current_values = asdict(self)
        current_values.update(kwargs)
        return LogContext(**current_values)
    
    def with_operation(self, operation: str) -> 'LogContext':
        """Create new context with different operation."""
        return self.update(operation=operation)
    
    def with_symbol(self, symbol: str) -> 'LogContext':
        """Create new context with symbol information."""
        return self.update(symbol=symbol)
    
    def with_exchange(self, exchange: str) -> 'LogContext':
        """Create new context with exchange information."""
        return self.update(exchange=exchange)
    
    def with_strategy(self, strategy: str) -> 'LogContext':
        """Create new context with strategy information."""
        return self.update(strategy=strategy)
    
    def with_trade_info(self, order_id: str = None, trade_id: str = None) -> 'LogContext':
        """Create new context with trade information."""
        return self.update(order_id=order_id, trade_id=trade_id)


class ContextManager:
    """
    Thread-local context manager for maintaining logging context.
    
    This class manages logging context in a thread-safe manner, allowing
    context to be set and retrieved throughout the execution flow.
    """
    
    def __init__(self):
        self._local = threading.local()
    
    def set_context(self, context: LogContext) -> None:
        """Set the current logging context for this thread."""
        self._local.context = context
    
    def get_context(self) -> Optional[LogContext]:
        """Get the current logging context for this thread."""
        return getattr(self._local, 'context', None)
    
    def clear_context(self) -> None:
        """Clear the current logging context for this thread."""
        if hasattr(self._local, 'context'):
            delattr(self._local, 'context')
    
    def update_context(self, **kwargs) -> None:
        """Update the current context with new values."""
        current_context = self.get_context()
        if current_context:
            self.set_context(current_context.update(**kwargs))
        else:
            # Create new context if none exists
            self.set_context(LogContext(
                component=kwargs.get('component', 'unknown'),
                operation=kwargs.get('operation', 'unknown'),
                **{k: v for k, v in kwargs.items() if k not in ['component', 'operation']}
            ))
    
    @contextmanager
    def context_scope(self, context: LogContext):
        """
        Context manager for temporary context changes.
        
        Args:
            context: Context to use within the scope
            
        Usage:
            with context_manager.context_scope(LogContext(...)):
                # Logging within this scope will use the provided context
                logger.info("This will include the context")
        """
        previous_context = self.get_context()
        try:
            self.set_context(context)
            yield context
        finally:
            if previous_context:
                self.set_context(previous_context)
            else:
                self.clear_context()


# Global context manager instance
_context_manager = ContextManager()


def set_context(context: LogContext) -> None:
    """Set the current logging context."""
    _context_manager.set_context(context)


def get_context() -> Optional[LogContext]:
    """Get the current logging context."""
    return _context_manager.get_context()


def clear_context() -> None:
    """Clear the current logging context."""
    _context_manager.clear_context()


def update_context(**kwargs) -> None:
    """Update the current context with new values."""
    _context_manager.update_context(**kwargs)


def context_scope(context: LogContext):
    """Context manager for temporary context changes."""
    return _context_manager.context_scope(context)


# Convenience functions for common context types
def trading_context(symbol: str, exchange: str, strategy: str = None) -> LogContext:
    """Create context for trading operations."""
    return LogContext(
        component="trading",
        operation="execution",
        symbol=symbol,
        exchange=exchange,
        strategy=strategy
    )


def cli_context(command: str, subcommand: str = None) -> LogContext:
    """Create context for CLI operations."""
    operation = f"{command}.{subcommand}" if subcommand else command
    return LogContext(
        component="cli",
        operation=operation
    )


def monitoring_context(metric_type: str) -> LogContext:
    """Create context for monitoring operations."""
    return LogContext(
        component="monitoring",
        operation=metric_type
    )


def error_context(error_type: str, component: str = "unknown") -> LogContext:
    """Create context for error tracking."""
    return LogContext(
        component=component,
        operation=f"error.{error_type}"
    )