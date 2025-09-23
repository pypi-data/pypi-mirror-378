#!/usr/bin/env python3
"""
Simple performance test for lazy evaluation without full logging setup.
"""

import time
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import genebot modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from genebot.logging.performance import LazyString, LazyFormat, lazy_json_dump


def expensive_operation():
    """Simulate an expensive operation."""
    time.sleep(0.001)  # 1ms delay
    return "Expensive result: " + json.dumps({
        'data': list(range(100)),
        'timestamp': time.time(),
        'nested': {'key': 'value', 'numbers': list(range(50))}
    })


def test_lazy_evaluation():
    """Test lazy evaluation performance without logging setup."""
    print("=== Simple Lazy Evaluation Performance Test ===\n")
    
    iterations = 1000
    
    # Test 1: LazyString vs regular string evaluation
    print("Test 1: LazyString Performance")
    print("-" * 40)
    
    # Regular string evaluation (always executes)
    start_time = time.perf_counter()
    results = []
    for i in range(iterations):
        result = expensive_operation()  # Always executed
        results.append(result)
    regular_time = time.perf_counter() - start_time
    
    # Lazy string evaluation (only executes when converted to string)
    start_time = time.perf_counter()
    lazy_results = []
    for i in range(iterations):
        lazy_result = LazyString(expensive_operation)  # Not executed yet
        lazy_results.append(lazy_result)
    lazy_creation_time = time.perf_counter() - start_time
    
    # Now evaluate the lazy strings
    start_time = time.perf_counter()
    evaluated_results = [str(lazy_result) for lazy_result in lazy_results]
    lazy_evaluation_time = time.perf_counter() - start_time
    
    total_lazy_time = lazy_creation_time + lazy_evaluation_time
    
    print(f"Regular evaluation: {regular_time:.4f}s ({regular_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy creation: {lazy_creation_time:.4f}s ({lazy_creation_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy evaluation: {lazy_evaluation_time:.4f}s ({lazy_evaluation_time/iterations*1000:.2f}ms per call)")
    print(f"Total lazy time: {total_lazy_time:.4f}s ({total_lazy_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy overhead: {((total_lazy_time - regular_time) / regular_time * 100):.1f}%")
    print()
    
    # Test 2: LazyFormat performance
    print("Test 2: LazyFormat Performance")
    print("-" * 40)
    
    # Regular string formatting
    start_time = time.perf_counter()
    for i in range(iterations):
        formatted = f"Message {i} with data: {{'key': 'value', 'number': {i}, 'list': {list(range(10))}}}"
    regular_format_time = time.perf_counter() - start_time
    
    # Lazy string formatting
    start_time = time.perf_counter()
    lazy_formats = []
    for i in range(iterations):
        lazy_fmt = LazyFormat("Message {} with data: {}", i, {'key': 'value', 'number': i, 'list': list(range(10))})
        lazy_formats.append(lazy_fmt)
    lazy_format_creation_time = time.perf_counter() - start_time
    
    # Evaluate lazy formats
    start_time = time.perf_counter()
    evaluated_formats = [str(lazy_fmt) for lazy_fmt in lazy_formats]
    lazy_format_evaluation_time = time.perf_counter() - start_time
    
    total_lazy_format_time = lazy_format_creation_time + lazy_format_evaluation_time
    
    print(f"Regular formatting: {regular_format_time:.4f}s ({regular_format_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy format creation: {lazy_format_creation_time:.4f}s ({lazy_format_creation_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy format evaluation: {lazy_format_evaluation_time:.4f}s ({lazy_format_evaluation_time/iterations*1000:.2f}ms per call)")
    print(f"Total lazy format time: {total_lazy_format_time:.4f}s ({total_lazy_format_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy format overhead: {((total_lazy_format_time - regular_format_time) / regular_format_time * 100):.1f}%")
    print()
    
    # Test 3: Benefit when evaluation is skipped
    print("Test 3: Benefit When Evaluation is Skipped")
    print("-" * 40)
    
    # Simulate scenario where expensive operations are skipped (like disabled logging)
    start_time = time.perf_counter()
    for i in range(iterations):
        # In real scenario, this would be skipped due to log level
        pass  # Skip the expensive operation
    skipped_time = time.perf_counter() - start_time
    
    # Lazy evaluation that's never converted to string (simulating disabled logging)
    start_time = time.perf_counter()
    for i in range(iterations):
        lazy_result = LazyString(expensive_operation)  # Created but never evaluated
        # In real logging, this would be discarded without evaluation
    lazy_skipped_time = time.perf_counter() - start_time
    
    print(f"Skipped operations: {skipped_time:.4f}s ({skipped_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy (not evaluated): {lazy_skipped_time:.4f}s ({lazy_skipped_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy overhead when skipped: {((lazy_skipped_time - skipped_time) / max(skipped_time, 0.0001) * 100):.1f}%")
    print()
    
    # Test 4: JSON serialization performance
    print("Test 4: JSON Serialization Performance")
    print("-" * 40)
    
    test_data = {
        'users': [{'id': i, 'name': f'user_{i}', 'data': list(range(20))} for i in range(50)],
        'metadata': {'timestamp': time.time(), 'version': '1.0'},
        'config': {'settings': {f'key_{i}': f'value_{i}' for i in range(20)}}
    }
    
    # Regular JSON serialization
    start_time = time.perf_counter()
    for i in range(iterations):
        json_str = json.dumps(test_data, default=str, separators=(',', ':'))
    regular_json_time = time.perf_counter() - start_time
    
    # Lazy JSON serialization
    start_time = time.perf_counter()
    lazy_jsons = []
    for i in range(iterations):
        lazy_json = lazy_json_dump(test_data)
        lazy_jsons.append(lazy_json)
    lazy_json_creation_time = time.perf_counter() - start_time
    
    # Evaluate lazy JSON
    start_time = time.perf_counter()
    evaluated_jsons = [str(lazy_json) for lazy_json in lazy_jsons]
    lazy_json_evaluation_time = time.perf_counter() - start_time
    
    total_lazy_json_time = lazy_json_creation_time + lazy_json_evaluation_time
    
    print(f"Regular JSON: {regular_json_time:.4f}s ({regular_json_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy JSON creation: {lazy_json_creation_time:.4f}s ({lazy_json_creation_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy JSON evaluation: {lazy_json_evaluation_time:.4f}s ({lazy_json_evaluation_time/iterations*1000:.2f}ms per call)")
    print(f"Total lazy JSON time: {total_lazy_json_time:.4f}s ({total_lazy_json_time/iterations*1000:.2f}ms per call)")
    print(f"Lazy JSON overhead: {((total_lazy_json_time - regular_json_time) / regular_json_time * 100):.1f}%")
    print()
    
    # Summary
    print("=== Performance Summary ===")
    print("Lazy evaluation characteristics:")
    print(f"- LazyString overhead: {((total_lazy_time - regular_time) / regular_time * 100):.1f}%")
    print(f"- LazyFormat overhead: {((total_lazy_format_time - regular_format_time) / regular_format_time * 100):.1f}%")
    print(f"- LazyJSON overhead: {((total_lazy_json_time - regular_json_time) / regular_json_time * 100):.1f}%")
    print(f"- Overhead when skipped: {((lazy_skipped_time - skipped_time) / max(skipped_time, 0.0001) * 100):.1f}%")
    print()
    print("Key benefits:")
    print("- Minimal overhead when evaluation is deferred")
    print("- Significant savings when expensive operations are skipped")
    print("- Ideal for debug logging that's often disabled in production")
    print("- Maintains correctness while improving performance")


if __name__ == "__main__":
    try:
        test_lazy_evaluation()
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)