"""
Asynchronous logging support for high-frequency operations.

This module provides queue-based asynchronous logging to minimize the impact
of logging on performance-critical code paths.
"""

import asyncio
import logging
import logging.handlers
import queue
import threading
import time
import sys
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import weakref


@dataclass
class AsyncLogRecord:
    """Asynchronous log record for queue-based logging."""
    logger_name: str
    level: int
    message: str
    args: tuple
    kwargs: dict
    timestamp: float
    thread_id: int
    
    def to_log_record(self) -> logging.LogRecord:
        """Convert to standard LogRecord."""
        record = logging.LogRecord(
            name=self.logger_name,
            level=self.level,
            pathname="",
            lineno=0,
            msg=self.message,
            args=self.args,
            exc_info=self.kwargs.get('exc_info')
        )
        
        # Add extra fields
        for key, value in self.kwargs.get('extra', {}).items():
            setattr(record, key, value)
        
        record.created = self.timestamp
        record.thread = self.thread_id
        
        return record


class AsyncLogHandler(logging.Handler):
    """
    Asynchronous log handler that queues log records for background processing.
    
    This handler immediately queues log records and processes them in a
    separate thread, minimizing the impact on the calling thread.
    """
    
    def __init__(self, target_handler: logging.Handler, queue_size: int = 10000, 
                 batch_size: int = 100, flush_interval: float = 1.0):
        """
        Initialize async log handler.
        
        Args:
            target_handler: The actual handler to process log records
            queue_size: Maximum size of the log queue
            batch_size: Number of records to process in each batch
            flush_interval: Maximum time between flushes (seconds)
        """
        super().__init__()
        self.target_handler = target_handler
        self.queue_size = queue_size
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Create queue and processing thread
        self._queue = queue.Queue(maxsize=queue_size)
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
        
        # Statistics
        self._records_queued = 0
        self._records_processed = 0
        self._records_dropped = 0
        self._last_flush = time.time()
        
        # Register cleanup
        weakref.finalize(self, self._cleanup)
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record by queuing it for asynchronous processing.
        
        Args:
            record: Log record to emit
        """
        try:
            # Create async log record
            async_record = AsyncLogRecord(
                logger_name=record.name,
                level=record.levelno,
                message=record.getMessage(),
                args=(),  # Already formatted
                kwargs={'extra': getattr(record, '__dict__', {})},
                timestamp=record.created,
                thread_id=record.thread
            )
            
            # Try to queue the record
            self._queue.put_nowait(async_record)
            self._records_queued += 1
            
        except queue.Full:
            # Queue is full, drop the record
            self._records_dropped += 1
            # Optionally, we could implement a fallback strategy here
    
    def _worker(self) -> None:
        """Worker thread that processes queued log records."""
        batch = []
        
        while not self._stop_event.is_set():
            try:
                # Try to get a record with timeout
                try:
                    async_record = self._queue.get(timeout=0.1)
                    batch.append(async_record)
                except queue.Empty:
                    # No records available, check if we should flush
                    if batch and (time.time() - self._last_flush) >= self.flush_interval:
                        self._process_batch(batch)
                        batch = []
                    continue
                
                # Process batch if it's full or flush interval exceeded
                if (len(batch) >= self.batch_size or 
                    (time.time() - self._last_flush) >= self.flush_interval):
                    self._process_batch(batch)
                    batch = []
                
            except Exception as e:
                # Log worker errors to stderr to avoid recursion
                print(f"AsyncLogHandler worker error: {e}", file=sys.stderr)
        
        # Process remaining records on shutdown
        if batch:
            self._process_batch(batch)
        
        # Process any remaining queued records
        remaining_batch = []
        try:
            while True:
                async_record = self._queue.get_nowait()
                remaining_batch.append(async_record)
                if len(remaining_batch) >= self.batch_size:
                    self._process_batch(remaining_batch)
                    remaining_batch = []
        except queue.Empty:
            pass
        
        if remaining_batch:
            self._process_batch(remaining_batch)
    
    def _process_batch(self, batch: list[AsyncLogRecord]) -> None:
        """
        Process a batch of log records.
        
        Args:
            batch: List of AsyncLogRecord instances to process
        """
        for async_record in batch:
            try:
                log_record = async_record.to_log_record()
                self.target_handler.emit(log_record)
                self._records_processed += 1
            except Exception as e:
                # Log processing errors to stderr
                print(f"AsyncLogHandler processing error: {e}", file=sys.stderr)
        
        # Flush the target handler
        try:
            self.target_handler.flush()
        except Exception as e:
            print(f"AsyncLogHandler flush error: {e}", file=sys.stderr)
        
        self._last_flush = time.time()
    
    def flush(self) -> None:
        """Flush all pending log records."""
        # Signal worker to process all remaining records
        batch = []
        try:
            while True:
                async_record = self._queue.get_nowait()
                batch.append(async_record)
        except queue.Empty:
            pass
        
        if batch:
            self._process_batch(batch)
        
        # Flush target handler
        self.target_handler.flush()
    
    def close(self) -> None:
        """Close the handler and clean up resources."""
        self._cleanup()
        super().close()
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, '_stop_event') and not self._stop_event.is_set():
            self._stop_event.set()
            if hasattr(self, '_worker_thread') and self._worker_thread.is_alive():
                self._worker_thread.join(timeout=5.0)
    
    def get_stats(self) -> Dict[str, int]:
        """Get handler statistics."""
        return {
            'records_queued': self._records_queued,
            'records_processed': self._records_processed,
            'records_dropped': self._records_dropped,
            'queue_size': self._queue.qsize(),
            'queue_capacity': self.queue_size
        }


class BufferedAsyncHandler(AsyncLogHandler):
    """
    Buffered asynchronous handler for batch operations.
    
    This handler buffers log records in memory and flushes them
    periodically or when the buffer is full.
    """
    
    def __init__(self, target_handler: logging.Handler, buffer_size: int = 1000,
                 flush_interval: float = 5.0, **kwargs):
        """
        Initialize buffered async handler.
        
        Args:
            target_handler: The actual handler to process log records
            buffer_size: Size of the memory buffer
            flush_interval: Time between automatic flushes
            **kwargs: Additional arguments for AsyncLogHandler
        """
        super().__init__(target_handler, batch_size=buffer_size, 
                        flush_interval=flush_interval, **kwargs)
        self.buffer_size = buffer_size


class AsyncFileHandler(AsyncLogHandler):
    """Asynchronous file handler optimized for file I/O."""
    
    def __init__(self, filename: str, mode: str = 'a', encoding: str = 'utf-8',
                 queue_size: int = 10000, batch_size: int = 50, **kwargs):
        """
        Initialize async file handler.
        
        Args:
            filename: Path to log file
            mode: File open mode
            encoding: File encoding
            queue_size: Size of the log queue
            batch_size: Records per batch
            **kwargs: Additional arguments
        """
        # Create the target file handler
        target_handler = logging.FileHandler(filename, mode, encoding)
        
        super().__init__(target_handler, queue_size=queue_size, 
                        batch_size=batch_size, **kwargs)


class AsyncRotatingFileHandler(AsyncLogHandler):
    """Asynchronous rotating file handler."""
    
    def __init__(self, filename: str, max_bytes: int = 10*1024*1024, 
                 backup_count: int = 5, encoding: str = 'utf-8',
                 queue_size: int = 10000, batch_size: int = 50, **kwargs):
        """
        Initialize async rotating file handler.
        
        Args:
            filename: Path to log file
            max_bytes: Maximum file size before rotation
            backup_count: Number of backup files to keep
            encoding: File encoding
            queue_size: Size of the log queue
            batch_size: Records per batch
            **kwargs: Additional arguments
        """
        # Create the target rotating file handler
        target_handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding
        )
        
        super().__init__(target_handler, queue_size=queue_size, 
                        batch_size=batch_size, **kwargs)


class AsyncLogger:
    """
    Asynchronous logger wrapper for high-frequency logging scenarios.
    
    This logger provides async/await interface for logging operations
    and integrates with asyncio event loops.
    """
    
    def __init__(self, logger: logging.Logger, executor: Optional[ThreadPoolExecutor] = None):
        """
        Initialize async logger.
        
        Args:
            logger: Underlying synchronous logger
            executor: Thread pool executor for async operations
        """
        self.logger = logger
        self.executor = executor or ThreadPoolExecutor(max_workers=2, thread_name_prefix="async_log")
        self._loop = None
    
    async def debug(self, message: str, *args, **kwargs) -> None:
        """Async debug logging."""
        await self._log_async(logging.DEBUG, message, *args, **kwargs)
    
    async def info(self, message: str, *args, **kwargs) -> None:
        """Async info logging."""
        await self._log_async(logging.INFO, message, *args, **kwargs)
    
    async def warning(self, message: str, *args, **kwargs) -> None:
        """Async warning logging."""
        await self._log_async(logging.WARNING, message, *args, **kwargs)
    
    async def error(self, message: str, *args, **kwargs) -> None:
        """Async error logging."""
        await self._log_async(logging.ERROR, message, *args, **kwargs)
    
    async def critical(self, message: str, *args, **kwargs) -> None:
        """Async critical logging."""
        await self._log_async(logging.CRITICAL, message, *args, **kwargs)
    
    async def _log_async(self, level: int, message: str, *args, **kwargs) -> None:
        """
        Perform asynchronous logging.
        
        Args:
            level: Log level
            message: Log message
            *args: Message arguments
            **kwargs: Additional keyword arguments
        """
        if not self.logger.isEnabledFor(level):
            return
        
        # Get current event loop
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                # No event loop running, use sync logging
                self.logger.log(level, message, *args, **kwargs)
                return
        
        # Run logging in thread pool
        await self._loop.run_in_executor(
            self.executor,
            lambda: self.logger.log(level, message, *args, **kwargs)
        )
    
    def sync_log(self, level: int, message: str, *args, **kwargs) -> None:
        """Synchronous logging fallback."""
        self.logger.log(level, message, *args, **kwargs)


# Convenience functions for creating async handlers
def create_async_file_handler(filename: str, **kwargs) -> AsyncFileHandler:
    """Create an asynchronous file handler."""
    return AsyncFileHandler(filename, **kwargs)


def create_async_rotating_handler(filename: str, **kwargs) -> AsyncRotatingFileHandler:
    """Create an asynchronous rotating file handler."""
    return AsyncRotatingFileHandler(filename, **kwargs)


def create_buffered_handler(target_handler: logging.Handler, **kwargs) -> BufferedAsyncHandler:
    """Create a buffered asynchronous handler."""
    return BufferedAsyncHandler(target_handler, **kwargs)


def wrap_logger_async(logger: logging.Logger, executor: Optional[ThreadPoolExecutor] = None) -> AsyncLogger:
    """Wrap a synchronous logger with async interface."""
    return AsyncLogger(logger, executor)


# Global async logging configuration
_async_enabled = False
_global_executor = None


def enable_async_logging(executor: Optional[ThreadPoolExecutor] = None) -> None:
    """Enable global asynchronous logging."""
    global _async_enabled, _global_executor
    _async_enabled = True
    _global_executor = executor or ThreadPoolExecutor(max_workers=4, thread_name_prefix="global_async_log")


def disable_async_logging() -> None:
    """Disable global asynchronous logging."""
    global _async_enabled, _global_executor
    _async_enabled = False
    if _global_executor:
        _global_executor.shutdown(wait=True)
        _global_executor = None


def is_async_logging_enabled() -> bool:
    """Check if async logging is enabled."""
    return _async_enabled


def get_global_executor() -> Optional[ThreadPoolExecutor]:
    """Get the global async logging executor."""
    return _global_executor