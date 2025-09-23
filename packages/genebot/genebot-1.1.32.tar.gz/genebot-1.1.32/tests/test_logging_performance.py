"""
Performance and load tests for the logging system.

This module tests logging overhead, memory usage, concurrent logging,
and file I/O performance to ensure the logging system meets performance requirements.
"""

import gc
import logging
import os
import psutil
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import shutil
import statistics

from genebot.logging.factory import LoggerFactory
from genebot.logging.config import LoggingConfig
from genebot.logging.context import LogContext
from genebot.logging.formatters import StructuredJSONFormatter, PerformanceOptimizedFormatter
from genebot.logging.performance import LazyString, LazyFormat


class PerformanceTestBase(unittest.TestCase):
    """Base class for performance tests with common utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
        
        # Get initial memory usage
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
        gc.collect()  # Force garbage collection
    
    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return end_time - start_time, result
    
    def measure_memory_usage(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_increase(self):
        """Get memory increase since test start in MB."""
        current_memory = self.process.memory_info().rss
        return (current_memory - self.initial_memory) / 1024 / 1024


class TestLoggingOverhead(PerformanceTestBase):
    """Test logging overhead in high-frequency scenarios."""
    
    def test_basic_logging_overhead(self):
        """Test basic logging overhead without optimization."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=False,  # No file I/O for pure overhead test
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        logger = factory.get_logger("performance.test", enable_optimization=False)
        
        # Measure overhead of logging calls
        num_messages = 10000
        
        def log_messages():
            for i in range(num_messages):
                logger.info(f"Test message {i}")
        
        execution_time, _ = self.measure_time(log_messages)
        
        # Calculate messages per second
        messages_per_second = num_messages / execution_time
        
        print(f"Basic logging: {messages_per_second:.0f} messages/second")
        print(f"Average time per message: {(execution_time * 1000 / num_messages):.3f} ms")
        
        # Should be able to log at least 1000 messages per second
        self.assertGreater(messages_per_second, 1000)
    
    def test_optimized_logging_overhead(self):
        """Test logging overhead with performance optimizations."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=False,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        logger = factory.get_logger("performance.test", enable_optimization=True)
        
        num_messages = 10000
        
        def log_messages():
            for i in range(num_messages):
                logger.info(f"Test message {i}")
        
        execution_time, _ = self.measure_time(log_messages)
        messages_per_second = num_messages / execution_time
        
        print(f"Optimized logging: {messages_per_second:.0f} messages/second")
        
        # Optimized logging should be faster
        self.assertGreater(messages_per_second, 1500)
    
    def test_lazy_evaluation_performance(self):
        """Test performance benefit of lazy evaluation."""
        config = LoggingConfig(
            level="WARNING",  # DEBUG messages won't be processed
            console_output=False,
            file_output=False,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        logger = factory.get_logger("performance.test")
        
        num_messages = 50000
        
        # Test with regular string formatting (expensive)
        def log_with_regular_formatting():
            for i in range(num_messages):
                expensive_data = f"Complex calculation: {i * 123.456 / 789.012:.6f}"
                logger.debug(f"Debug message with expensive data: {expensive_data}")
        
        # Test with lazy formatting
        def log_with_lazy_formatting():
            for i in range(num_messages):
                logger.lazy_debug("Debug message with expensive data: Complex calculation: {:.6f}", 
                                i * 123.456 / 789.012)
        
        regular_time, _ = self.measure_time(log_with_regular_formatting)
        lazy_time, _ = self.measure_time(log_with_lazy_formatting)
        
        print(f"Regular formatting time: {regular_time:.3f}s")
        print(f"Lazy formatting time: {lazy_time:.3f}s")
        print(f"Speedup: {regular_time / lazy_time:.2f}x")
        
        # Lazy evaluation should be significantly faster when messages are filtered out
        self.assertLess(lazy_time, regular_time * 0.5)  # At least 2x faster
    
    def test_context_injection_overhead(self):
        """Test overhead of context injection."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=False,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        logger_no_context = factory.get_logger("performance.no_context")
        
        context = LogContext(
            component="performance_test",
            operation="context_overhead",
            symbol="BTCUSDT",
            exchange="binance"
        )
        logger_with_context = factory.get_logger("performance.with_context", context=context)
        
        num_messages = 5000
        
        def log_without_context():
            for i in range(num_messages):
                logger_no_context.info(f"Message {i}")
        
        def log_with_context():
            for i in range(num_messages):
                logger_with_context.info(f"Message {i}")
        
        no_context_time, _ = self.measure_time(log_without_context)
        with_context_time, _ = self.measure_time(log_with_context)
        
        overhead_percent = ((with_context_time - no_context_time) / no_context_time) * 100
        
        print(f"No context time: {no_context_time:.3f}s")
        print(f"With context time: {with_context_time:.3f}s")
        print(f"Context overhead: {overhead_percent:.1f}%")
        
        # Context overhead should be reasonable (less than 50%)
        self.assertLess(overhead_percent, 50)
    
    def test_formatter_performance_comparison(self):
        """Test performance of different formatters."""
        # Create test record
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/test.py",
            lineno=42,
            msg="Test message with some data: %s, %d",
            args=("test_string", 12345),
            exc_info=None
        )
        record.module = "test"
        record.funcName = "test_function"
        record.context = LogContext(
            component="performance_test",
            operation="formatter_test",
            symbol="BTCUSDT"
        )
        
        # Test different formatters
        structured_formatter = StructuredJSONFormatter()
        optimized_formatter = PerformanceOptimizedFormatter(cache_size=1000)
        
        num_formats = 10000
        
        def format_with_structured():
            for _ in range(num_formats):
                structured_formatter.format(record)
        
        def format_with_optimized():
            for _ in range(num_formats):
                optimized_formatter.format(record)
        
        structured_time, _ = self.measure_time(format_with_structured)
        optimized_time, _ = self.measure_time(format_with_optimized)
        
        print(f"Structured formatter: {structured_time:.3f}s ({num_formats/structured_time:.0f} formats/s)")
        print(f"Optimized formatter: {optimized_time:.3f}s ({num_formats/optimized_time:.0f} formats/s)")
        
        # Get cache stats for optimized formatter
        cache_stats = optimized_formatter.get_cache_stats()
        print(f"Cache hit rate: {cache_stats['hit_rate_percent']:.1f}%")
        
        # Optimized formatter should be faster due to caching
        self.assertLess(optimized_time, structured_time)


class TestMemoryUsage(PerformanceTestBase):
    """Test memory usage under sustained logging load."""
    
    def test_memory_usage_sustained_logging(self):
        """Test memory usage during sustained logging."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            max_file_size=1024 * 1024,  # 1MB for rotation testing
            backup_count=3
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        logger = factory.get_logger("memory.test")
        
        initial_memory = self.measure_memory_usage()
        memory_samples = [initial_memory]
        
        # Log messages in batches and measure memory
        batch_size = 1000
        num_batches = 20
        
        for batch in range(num_batches):
            for i in range(batch_size):
                logger.info(f"Batch {batch}, message {i}: Some test data with numbers {i * 123}")
            
            # Force garbage collection and measure memory
            gc.collect()
            current_memory = self.measure_memory_usage()
            memory_samples.append(current_memory)
            
            print(f"Batch {batch}: Memory usage: {current_memory:.1f} MB")
        
        final_memory = memory_samples[-1]
        memory_increase = final_memory - initial_memory
        
        print(f"Initial memory: {initial_memory:.1f} MB")
        print(f"Final memory: {final_memory:.1f} MB")
        print(f"Memory increase: {memory_increase:.1f} MB")
        
        # Memory increase should be reasonable (less than 50MB for this test)
        self.assertLess(memory_increase, 50)
        
        # Memory usage should stabilize (not continuously grow)
        # Check that memory doesn't grow significantly in the last few batches
        recent_samples = memory_samples[-5:]
        memory_variance = statistics.variance(recent_samples) if len(recent_samples) > 1 else 0
        print(f"Recent memory variance: {memory_variance:.2f}")
        
        # Low variance indicates stable memory usage
        self.assertLess(memory_variance, 10)
    
    def test_logger_cache_memory_usage(self):
        """Test memory usage of logger caching."""
        config = LoggingConfig(
            console_output=False,
            file_output=False,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        initial_memory = self.measure_memory_usage()
        
        # Create many loggers with different names
        loggers = []
        num_loggers = 1000
        
        for i in range(num_loggers):
            logger = factory.get_logger(f"test.logger.{i}")
            loggers.append(logger)
        
        after_creation_memory = self.measure_memory_usage()
        memory_per_logger = (after_creation_memory - initial_memory) * 1024 / num_loggers  # KB per logger
        
        print(f"Memory per logger: {memory_per_logger:.2f} KB")
        
        # Each logger should use reasonable memory (less than 10KB)
        self.assertLess(memory_per_logger, 10)
        
        # Test that getting existing loggers doesn't increase memory significantly
        before_reuse_memory = self.measure_memory_usage()
        
        # Get existing loggers (should be cached)
        for i in range(num_loggers):
            factory.get_logger(f"test.logger.{i}")
        
        after_reuse_memory = self.measure_memory_usage()
        reuse_memory_increase = after_reuse_memory - before_reuse_memory
        
        print(f"Memory increase from reuse: {reuse_memory_increase:.2f} MB")
        
        # Reusing cached loggers should not significantly increase memory
        self.assertLess(reuse_memory_increase, 1)  # Less than 1MB
    
    def test_context_memory_usage(self):
        """Test memory usage of context objects."""
        config = LoggingConfig(
            console_output=False,
            file_output=False,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        initial_memory = self.measure_memory_usage()
        
        # Create many contexts
        contexts = []
        num_contexts = 10000
        
        for i in range(num_contexts):
            context = LogContext(
                component=f"component_{i}",
                operation=f"operation_{i}",
                symbol=f"SYMBOL{i}",
                exchange=f"exchange_{i % 10}",  # Reuse some values
                strategy=f"strategy_{i % 5}"   # Reuse some values
            )
            contexts.append(context)
        
        after_creation_memory = self.measure_memory_usage()
        memory_per_context = (after_creation_memory - initial_memory) * 1024 / num_contexts  # KB per context
        
        print(f"Memory per context: {memory_per_context:.3f} KB")
        
        # Each context should use minimal memory (less than 1KB)
        self.assertLess(memory_per_context, 1)


class TestConcurrentLogging(PerformanceTestBase):
    """Test concurrent logging from multiple threads."""
    
    def test_concurrent_logging_performance(self):
        """Test performance of concurrent logging from multiple threads."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        num_threads = 10
        messages_per_thread = 1000
        results = []
        
        def log_from_thread(thread_id):
            logger = factory.get_logger(f"concurrent.thread_{thread_id}")
            
            start_time = time.perf_counter()
            
            for i in range(messages_per_thread):
                logger.info(f"Thread {thread_id}, message {i}")
            
            end_time = time.perf_counter()
            thread_time = end_time - start_time
            results.append((thread_id, thread_time))
        
        # Start all threads
        threads = []
        overall_start = time.perf_counter()
        
        for i in range(num_threads):
            thread = threading.Thread(target=log_from_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        overall_end = time.perf_counter()
        overall_time = overall_end - overall_start
        
        # Calculate statistics
        thread_times = [time for _, time in results]
        avg_thread_time = statistics.mean(thread_times)
        max_thread_time = max(thread_times)
        min_thread_time = min(thread_times)
        
        total_messages = num_threads * messages_per_thread
        overall_throughput = total_messages / overall_time
        
        print(f"Concurrent logging results:")
        print(f"  Threads: {num_threads}")
        print(f"  Messages per thread: {messages_per_thread}")
        print(f"  Total messages: {total_messages}")
        print(f"  Overall time: {overall_time:.3f}s")
        print(f"  Overall throughput: {overall_throughput:.0f} messages/s")
        print(f"  Average thread time: {avg_thread_time:.3f}s")
        print(f"  Min thread time: {min_thread_time:.3f}s")
        print(f"  Max thread time: {max_thread_time:.3f}s")
        
        # Verify all threads completed
        self.assertEqual(len(results), num_threads)
        
        # Overall throughput should be reasonable
        self.assertGreater(overall_throughput, 1000)  # At least 1000 messages/s total
        
        # Thread times should be reasonably consistent (no thread should take 3x longer than the fastest)
        time_ratio = max_thread_time / min_thread_time
        print(f"  Thread time ratio (max/min): {time_ratio:.2f}")
        self.assertLess(time_ratio, 3.0)
    
    def test_thread_safety_data_integrity(self):
        """Test that concurrent logging maintains data integrity."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            format_type="structured"  # Use structured format for easier parsing
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        num_threads = 5
        messages_per_thread = 200
        
        def log_from_thread(thread_id):
            logger = factory.get_logger("thread_safety.test")
            
            for i in range(messages_per_thread):
                logger.info(f"Thread_{thread_id}_Message_{i}", extra={
                    'thread_id': thread_id,
                    'message_id': i,
                    'test_data': f"data_{thread_id}_{i}"
                })
        
        # Start all threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=log_from_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify log file integrity
        log_file = self.log_dir / "genebot.log"
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Should have all messages
        expected_total = num_threads * messages_per_thread
        self.assertEqual(len(lines), expected_total)
        
        # Parse and verify each message
        thread_message_counts = {}
        
        for line in lines:
            try:
                import json
                log_data = json.loads(line.strip())
                
                # Verify structure
                self.assertIn('thread_id', log_data)
                self.assertIn('message_id', log_data)
                self.assertIn('test_data', log_data)
                
                thread_id = log_data['thread_id']
                message_id = log_data['message_id']
                
                # Count messages per thread
                if thread_id not in thread_message_counts:
                    thread_message_counts[thread_id] = 0
                thread_message_counts[thread_id] += 1
                
                # Verify data consistency
                expected_data = f"data_{thread_id}_{message_id}"
                self.assertEqual(log_data['test_data'], expected_data)
                
            except json.JSONDecodeError:
                self.fail(f"Invalid JSON in log line: {line}")
        
        # Verify each thread logged the correct number of messages
        for thread_id in range(num_threads):
            self.assertEqual(thread_message_counts[thread_id], messages_per_thread)


class TestFileIOPerformance(PerformanceTestBase):
    """Test file I/O performance and rotation efficiency."""
    
    def test_file_write_performance(self):
        """Test file writing performance."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            max_file_size=10 * 1024 * 1024,  # 10MB
            backup_count=5
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        logger = factory.get_logger("file_io.test")
        
        num_messages = 10000
        message_size = 200  # Approximate message size
        
        def write_messages():
            for i in range(num_messages):
                # Create message of approximately target size
                padding = "x" * (message_size - 50)  # Account for other content
                logger.info(f"Message {i:05d} with padding: {padding}")
        
        write_time, _ = self.measure_time(write_messages)
        
        # Calculate throughput
        total_bytes = num_messages * message_size
        throughput_mb_s = (total_bytes / (1024 * 1024)) / write_time
        messages_per_second = num_messages / write_time
        
        print(f"File I/O Performance:")
        print(f"  Messages: {num_messages}")
        print(f"  Total data: {total_bytes / (1024 * 1024):.1f} MB")
        print(f"  Write time: {write_time:.3f}s")
        print(f"  Throughput: {throughput_mb_s:.1f} MB/s")
        print(f"  Messages/second: {messages_per_second:.0f}")
        
        # Verify file was created and has expected size
        log_file = self.log_dir / "genebot.log"
        self.assertTrue(log_file.exists())
        
        file_size = log_file.stat().st_size
        expected_min_size = total_bytes * 0.8  # Allow some variance
        expected_max_size = total_bytes * 1.5  # JSON overhead
        
        print(f"  File size: {file_size / (1024 * 1024):.1f} MB")
        
        self.assertGreater(file_size, expected_min_size)
        self.assertLess(file_size, expected_max_size)
        
        # Performance should be reasonable
        self.assertGreater(messages_per_second, 500)  # At least 500 messages/s
    
    def test_log_rotation_performance(self):
        """Test performance impact of log rotation."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            max_file_size=1024 * 100,  # Small size (100KB) to trigger rotation
            backup_count=3
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        logger = factory.get_logger("rotation.test")
        
        # Log enough messages to trigger multiple rotations
        num_messages = 2000
        message_size = 100
        
        rotation_times = []
        
        def log_with_rotation_timing():
            for i in range(num_messages):
                start_time = time.perf_counter()
                
                padding = "x" * (message_size - 30)
                logger.info(f"Rotation test {i:04d}: {padding}")
                
                end_time = time.perf_counter()
                message_time = end_time - start_time
                rotation_times.append(message_time)
        
        total_time, _ = self.measure_time(log_with_rotation_timing)
        
        # Analyze timing to detect rotation events
        avg_time = statistics.mean(rotation_times)
        max_time = max(rotation_times)
        
        # Find messages that took significantly longer (likely rotation events)
        rotation_threshold = avg_time * 5  # 5x average time
        rotation_events = [t for t in rotation_times if t > rotation_threshold]
        
        print(f"Log Rotation Performance:")
        print(f"  Total messages: {num_messages}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average message time: {avg_time * 1000:.3f}ms")
        print(f"  Max message time: {max_time * 1000:.3f}ms")
        print(f"  Detected rotation events: {len(rotation_events)}")
        
        if rotation_events:
            avg_rotation_time = statistics.mean(rotation_events)
            print(f"  Average rotation time: {avg_rotation_time * 1000:.3f}ms")
        
        # Verify rotation occurred
        log_files = list(self.log_dir.glob("genebot.log*"))
        print(f"  Log files created: {len(log_files)}")
        
        self.assertGreater(len(log_files), 1)  # Should have rotated files
        
        # Rotation should not cause excessive delays
        if rotation_events:
            max_rotation_time = max(rotation_events)
            self.assertLess(max_rotation_time, 0.1)  # Less than 100ms per rotation
    
    def test_concurrent_file_access(self):
        """Test concurrent file access performance."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        num_threads = 5
        messages_per_thread = 500
        
        def concurrent_file_writer(thread_id):
            logger = factory.get_logger("concurrent_file.test")
            
            for i in range(messages_per_thread):
                logger.info(f"Concurrent file access from thread {thread_id}, message {i}")
        
        # Measure concurrent file access
        start_time = time.perf_counter()
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=concurrent_file_writer, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        total_messages = num_threads * messages_per_thread
        concurrent_throughput = total_messages / total_time
        
        print(f"Concurrent File Access:")
        print(f"  Threads: {num_threads}")
        print(f"  Total messages: {total_messages}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Throughput: {concurrent_throughput:.0f} messages/s")
        
        # Verify file integrity
        log_file = self.log_dir / "genebot.log"
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Should have all messages
        self.assertEqual(len(lines), total_messages)
        
        # Performance should be reasonable even with concurrent access
        self.assertGreater(concurrent_throughput, 200)  # At least 200 messages/s total


if __name__ == '__main__':
    # Run with verbose output to see performance metrics
    unittest.main(verbosity=2)