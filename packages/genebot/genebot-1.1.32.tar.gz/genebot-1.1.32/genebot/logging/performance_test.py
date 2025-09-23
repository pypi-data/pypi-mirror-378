#!/usr/bin/env python3
"""
Performance testing script for logging optimizations.

This script benchmarks the performance improvements from lazy evaluation
and other logging optimizations.
"""

import logging
import time
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import genebot modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from genebot.logging.factory import setup_global_config, get_logger
from genebot.logging.config import LoggingConfig
from genebot.logging.performance import (
    LazyString, LazyFormat, LoggingBenchmark, 
    lazy_json_dump, lazy_repr, get_performance_monitor
)


def expensive_operation():
    """Simulate an expensive operation for lazy evaluation testing."""
    time.sleep(0.001)  # 1ms delay
    return "Expensive result: " + json.dumps({
        'data': list(range(100)),
        'timestamp': time.time(),
        'nested': {'key': 'value', 'numbers': list(range(50))}
    })


def run_performance_tests():
    """Run comprehensive performance tests for logging optimizations."""
    print("=== Logging Performance Tests ===\n")
    
    # Setup logging configuration for testing
    config = LoggingConfig(
        level="DEBUG",
        console_output=True,  # Enable console for testing
        file_output=False,
        enable_performance_logging=True
    )
    setup_global_config(config)
    
    # Create test logger
    logger = get_logger("performance_test")
    
    # Test 1: Regular vs Lazy String Evaluation
    print("Test 1: Regular vs Lazy String Evaluation")
    print("-" * 50)
    
    iterations = 1000
    
    # Regular logging with expensive operation
    start_time = time.perf_counter()
    for i in range(iterations):
        logger.debug(f"Regular: {expensive_operation()}")
    regular_time = time.perf_counter() - start_time
    
    # Lazy logging with expensive operation
    start_time = time.perf_counter()
    for i in range(iterations):
        logger.debug(LazyString(expensive_operation))
    lazy_time = time.perf_counter() - start_time
    
    print(f"Regular logging: {regular_time:.4f}s ({regular_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy logging: {lazy_time:.4f}s ({lazy_time/iterations*1000:.2f}ms per call)")
    print(f"Performance improvement: {((regular_time - lazy_time) / regular_time * 100):.1f}%")
    print()
    
    # Test 2: String Formatting Performance
    print("Test 2: String Formatting Performance")
    print("-" * 50)
    
    # Regular string formatting
    start_time = time.perf_counter()
    for i in range(iterations):
        logger.debug(f"Message {i} with data: {{'key': 'value', 'number': {i}, 'list': {list(range(10))}}}")
    regular_format_time = time.perf_counter() - start_time
    
    # Lazy string formatting
    start_time = time.perf_counter()
    for i in range(iterations):
        logger.debug(LazyFormat("Message {} with data: {}", i, {'key': 'value', 'number': i, 'list': list(range(10))}))
    lazy_format_time = time.perf_counter() - start_time
    
    print(f"Regular formatting: {regular_format_time:.4f}s ({regular_format_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy formatting: {lazy_format_time:.4f}s ({lazy_format_time/iterations*1000:.2f}ms per call)")
    print(f"Performance improvement: {((regular_format_time - lazy_format_time) / regular_format_time * 100):.1f}%")
    print()
    
    # Test 3: JSON Serialization Performance
    print("Test 3: JSON Serialization Performance")
    print("-" * 50)
    
    test_data = {
        'users': [{'id': i, 'name': f'user_{i}', 'data': list(range(20))} for i in range(50)],
        'metadata': {'timestamp': time.time(), 'version': '1.0'},
        'config': {'settings': {f'key_{i}': f'value_{i}' for i in range(20)}}
    }
    
    # Regular JSON serialization
    start_time = time.perf_counter()
    for i in range(iterations):
        logger.debug(f"Data: {json.dumps(test_data)}")
    regular_json_time = time.perf_counter() - start_time
    
    # Lazy JSON serialization
    start_time = time.perf_counter()
    for i in range(iterations):
        logger.debug(lazy_json_dump(test_data))
    lazy_json_time = time.perf_counter() - start_time
    
    print(f"Regular JSON: {regular_json_time:.4f}s ({regular_json_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy JSON: {lazy_json_time:.4f}s ({lazy_json_time/iterations*1000:.2f}ms per call)")
    print(f"Performance improvement: {((regular_json_time - lazy_json_time) / regular_json_time * 100):.1f}%")
    print()
    
    # Test 4: Disabled Logging Performance
    print("Test 4: Disabled Logging Performance")
    print("-" * 50)
    
    # Disable debug logging
    logging.getLogger("performance_test").setLevel(logging.INFO)
    
    # Regular logging when disabled
    start_time = time.perf_counter()
    for i in range(iterations):
        logger.debug(f"Disabled: {expensive_operation()}")
    disabled_regular_time = time.perf_counter() - start_time
    
    # Lazy logging when disabled
    start_time = time.perf_counter()
    for i in range(iterations):
        logger.debug(LazyString(expensive_operation))
    disabled_lazy_time = time.perf_counter() - start_time
    
    print(f"Regular (disabled): {disabled_regular_time:.4f}s ({disabled_regular_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy (disabled): {disabled_lazy_time:.4f}s ({disabled_lazy_time/iterations*1000:.2f}ms per call)")
    print(f"Performance improvement: {((disabled_regular_time - disabled_lazy_time) / disabled_regular_time * 100):.1f}%")
    print()
    
    # Test 5: Comprehensive Benchmark
    print("Test 5: Comprehensive Benchmark Suite")
    print("-" * 50)
    
    # Re-enable debug logging for benchmark
    logging.getLogger("performance_test").setLevel(logging.DEBUG)
    
    benchmark = LoggingBenchmark(logging.getLogger("performance_test"))
    results = benchmark.run_full_benchmark()
    
    print("Benchmark Results:")
    for test_name, metrics in results.items():
        print(f"  {test_name}:")
        print(f"    Total time: {metrics['total_time_s']:.4f}s")
        print(f"    Avg time per message: {metrics['avg_time_ms']:.4f}ms")
        print(f"    Messages per second: {metrics['messages_per_second']:.0f}")
    print()
    
    # Test 6: Performance Monitoring
    print("Test 6: Performance Monitoring")
    print("-" * 50)
    
    monitor = get_performance_monitor()
    
    # Generate some logging activity
    for i in range(100):
        logger.debug(LazyFormat("Test message {} with data {}", i, {'test': True}))
        logger.info(f"Info message {i}")
        if i % 10 == 0:
            logger.warning(f"Warning message {i}")
    
    # Get metrics
    metrics = monitor.get_metrics("performance_test")
    system_metrics = monitor.get_system_metrics()
    
    print("Logger Metrics:")
    print(f"  Total calls: {metrics.total_calls}")
    print(f"  Debug calls: {metrics.debug_calls}")
    print(f"  Debug skipped: {metrics.debug_skipped}")
    print(f"  Average time: {metrics.avg_time_ms:.4f}ms")
    print(f"  Total time: {metrics.total_time_ms:.4f}ms")
    
    print("\nSystem Metrics:")
    print(f"  Memory usage: {system_metrics['memory_mb']:.2f}MB")
    print(f"  CPU usage: {system_metrics['cpu_percent']:.1f}%")
    print(f"  Uptime: {system_metrics['uptime_seconds']:.1f}s")
    print()
    
    # Summary
    print("=== Performance Test Summary ===")
    print(f"Lazy evaluation provides significant performance benefits:")
    print(f"- String evaluation: {((regular_time - lazy_time) / regular_time * 100):.1f}% improvement")
    print(f"- String formatting: {((regular_format_time - lazy_format_time) / regular_format_time * 100):.1f}% improvement")
    print(f"- JSON serialization: {((regular_json_time - lazy_json_time) / regular_json_time * 100):.1f}% improvement")
    print(f"- Disabled logging: {((disabled_regular_time - disabled_lazy_time) / disabled_regular_time * 100):.1f}% improvement")
    print("\nLazy evaluation is especially beneficial when:")
    print("- Debug logging is disabled in production")
    print("- Log messages involve expensive operations")
    print("- High-frequency logging is required")


def test_lazy_evaluation_correctness():
    """Test that lazy evaluation produces correct results."""
    print("\n=== Lazy Evaluation Correctness Tests ===\n")
    
    # Test LazyString
    def get_test_string():
        return "Test string from function"
    
    lazy_str = LazyString(get_test_string)
    assert str(lazy_str) == "Test string from function"
    print("✓ LazyString correctness test passed")
    
    # Test LazyFormat
    lazy_fmt = LazyFormat("Hello {}, you have {} messages", "Alice", 5)
    assert str(lazy_fmt) == "Hello Alice, you have 5 messages"
    print("✓ LazyFormat correctness test passed")
    
    # Test LazyFormat with kwargs
    lazy_fmt_kwargs = LazyFormat("User {name} has {count} items", name="Bob", count=10)
    assert str(lazy_fmt_kwargs) == "User Bob has 10 items"
    print("✓ LazyFormat with kwargs correctness test passed")
    
    # Test lazy JSON
    test_obj = {'key': 'value', 'number': 42}
    lazy_json = lazy_json_dump(test_obj)
    expected_json = json.dumps(test_obj, default=str, separators=(',', ':'))
    assert str(lazy_json) == expected_json
    print("✓ Lazy JSON correctness test passed")
    
    # Test lazy repr
    test_obj = [1, 2, 3, {'nested': True}]
    lazy_repr_str = lazy_repr(test_obj)
    assert str(lazy_repr_str) == repr(test_obj)
    print("✓ Lazy repr correctness test passed")
    
    print("\nAll correctness tests passed! ✓")


if __name__ == "__main__":
    try:
        test_lazy_evaluation_correctness()
        run_performance_tests()
    except Exception as e:
        print(f"Error running performance tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)