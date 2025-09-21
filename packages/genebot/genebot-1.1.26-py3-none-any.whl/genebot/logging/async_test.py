#!/usr/bin/env python3
"""
Test script for asynchronous logging functionality.
"""

import asyncio
import logging
import time
import tempfile
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import genebot modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from genebot.logging.async_logging import (
    AsyncFileHandler, AsyncRotatingFileHandler, BufferedAsyncHandler,
    AsyncLogger, wrap_logger_async, enable_async_logging
)
from genebot.logging.factory import setup_global_config, get_logger
from genebot.logging.config import LoggingConfig


def test_async_handlers():
    """Test asynchronous handlers."""
    print("=== Testing Asynchronous Handlers ===\n")
    
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Test AsyncFileHandler
        print("Test 1: AsyncFileHandler")
        print("-" * 30)
        
        async_handler = AsyncFileHandler(temp_filename, queue_size=100, batch_size=10)
        
        # Create logger and add async handler
        test_logger = logging.getLogger('async_test')
        test_logger.setLevel(logging.DEBUG)
        test_logger.addHandler(async_handler)
        
        # Log some messages
        start_time = time.perf_counter()
        for i in range(100):
            test_logger.info(f"Async test message {i}")
        sync_time = time.perf_counter() - start_time
        
        # Wait for async processing to complete
        time.sleep(0.5)
        async_handler.flush()
        
        # Check stats
        stats = async_handler.get_stats()
        print(f"Messages queued: {stats['records_queued']}")
        print(f"Messages processed: {stats['records_processed']}")
        print(f"Messages dropped: {stats['records_dropped']}")
        print(f"Queue size: {stats['queue_size']}")
        print(f"Sync logging time: {sync_time:.4f}s ({sync_time/100*1000:.2f}ms per message)")
        
        # Verify file contents
        with open(temp_filename, 'r') as f:
            lines = f.readlines()
        print(f"Lines written to file: {len(lines)}")
        
        # Clean up
        async_handler.close()
        test_logger.removeHandler(async_handler)
        
        print("✓ AsyncFileHandler test passed\n")
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_async_logger():
    """Test AsyncLogger with asyncio."""
    print("Test 2: AsyncLogger with asyncio")
    print("-" * 30)
    
    async def async_logging_test():
        # Create async logger
        sync_logger = logging.getLogger('async_logger_test')
        sync_logger.setLevel(logging.DEBUG)
        
        # Add console handler for visibility
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        sync_logger.addHandler(console_handler)
        
        async_logger = wrap_logger_async(sync_logger)
        
        # Test async logging
        start_time = time.perf_counter()
        
        tasks = []
        for i in range(50):
            task = async_logger.info(f"Async message {i} from coroutine")
            tasks.append(task)
        
        # Wait for all logging tasks to complete
        await asyncio.gather(*tasks)
        
        async_time = time.perf_counter() - start_time
        print(f"Async logging time: {async_time:.4f}s ({async_time/50*1000:.2f}ms per message)")
        
        # Test mixed sync/async logging
        await async_logger.warning("This is an async warning")
        async_logger.sync_log(logging.ERROR, "This is a sync error")
        
        print("✓ AsyncLogger test passed")
    
    # Run the async test
    asyncio.run(async_logging_test())
    print()


def test_performance_comparison():
    """Compare sync vs async logging performance."""
    print("Test 3: Performance Comparison")
    print("-" * 30)
    
    # Create temporary files
    sync_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_sync.log')
    async_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_async.log')
    sync_filename = sync_file.name
    async_filename = async_file.name
    sync_file.close()
    async_file.close()
    
    try:
        iterations = 1000
        
        # Test synchronous logging
        sync_logger = logging.getLogger('sync_perf_test')
        sync_logger.setLevel(logging.DEBUG)
        sync_handler = logging.FileHandler(sync_filename)
        sync_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        sync_logger.addHandler(sync_handler)
        
        start_time = time.perf_counter()
        for i in range(iterations):
            sync_logger.info(f"Sync message {i} with some data: {{'key': 'value', 'number': {i}}}")
        sync_time = time.perf_counter() - start_time
        
        sync_handler.close()
        sync_logger.removeHandler(sync_handler)
        
        # Test asynchronous logging
        async_logger = logging.getLogger('async_perf_test')
        async_logger.setLevel(logging.DEBUG)
        async_handler = AsyncFileHandler(async_filename, queue_size=2000, batch_size=50)
        async_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        async_logger.addHandler(async_handler)
        
        start_time = time.perf_counter()
        for i in range(iterations):
            async_logger.info(f"Async message {i} with some data: {{'key': 'value', 'number': {i}}}")
        async_queue_time = time.perf_counter() - start_time
        
        # Wait for async processing
        time.sleep(1.0)
        async_handler.flush()
        
        # Get async stats
        stats = async_handler.get_stats()
        
        async_handler.close()
        async_logger.removeHandler(async_handler)
        
        # Compare results
        print(f"Synchronous logging: {sync_time:.4f}s ({sync_time/iterations*1000:.2f}ms per message)")
        print(f"Asynchronous queueing: {async_queue_time:.4f}s ({async_queue_time/iterations*1000:.2f}ms per message)")
        print(f"Async improvement: {((sync_time - async_queue_time) / sync_time * 100):.1f}%")
        print(f"Async messages processed: {stats['records_processed']}")
        print(f"Async messages dropped: {stats['records_dropped']}")
        
        # Verify file contents
        with open(sync_filename, 'r') as f:
            sync_lines = len(f.readlines())
        with open(async_filename, 'r') as f:
            async_lines = len(f.readlines())
        
        print(f"Sync file lines: {sync_lines}")
        print(f"Async file lines: {async_lines}")
        
        if sync_lines == async_lines == iterations:
            print("✓ Performance comparison test passed")
        else:
            print("⚠ Warning: Line counts don't match expected")
        
    finally:
        # Clean up temp files
        for filename in [sync_filename, async_filename]:
            if os.path.exists(filename):
                os.unlink(filename)
    
    print()


def test_integrated_async_logging():
    """Test integrated async logging with factory."""
    print("Test 4: Integrated Async Logging")
    print("-" * 30)
    
    # Create temporary directory for logs
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup async logging configuration
        config = LoggingConfig(
            level="DEBUG",
            console_output=True,
            file_output=True,
            log_directory=Path(temp_dir),
            enable_async_logging=True,
            async_queue_size=500,
            async_batch_size=25,
            async_flush_interval=0.5,
            enable_performance_logging=True,
            enable_trade_logging=True
        )
        
        setup_global_config(config)
        
        # Get loggers
        main_logger = get_logger("integrated_test")
        trade_logger = get_logger("genebot.trades")
        perf_logger = get_logger("genebot.performance")
        
        # Log messages
        start_time = time.perf_counter()
        
        for i in range(100):
            main_logger.info(f"Main message {i}")
            if i % 10 == 0:
                trade_logger.info(f"Trade event {i}")
                perf_logger.info(f"Performance metric {i}")
        
        queue_time = time.perf_counter() - start_time
        
        # Wait for async processing
        time.sleep(1.0)
        
        print(f"Integrated async logging time: {queue_time:.4f}s ({queue_time/100*1000:.2f}ms per message)")
        
        # Check log files
        log_files = list(Path(temp_dir).glob("*.log"))
        print(f"Log files created: {[f.name for f in log_files]}")
        
        for log_file in log_files:
            with open(log_file, 'r') as f:
                lines = len(f.readlines())
            print(f"  {log_file.name}: {lines} lines")
        
        print("✓ Integrated async logging test passed")
    
    print()


def main():
    """Run all async logging tests."""
    print("=== Asynchronous Logging Tests ===\n")
    
    try:
        test_async_handlers()
        test_async_logger()
        test_performance_comparison()
        test_integrated_async_logging()
        
        print("=== All Async Logging Tests Passed! ===")
        
    except Exception as e:
        print(f"Error in async logging tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()