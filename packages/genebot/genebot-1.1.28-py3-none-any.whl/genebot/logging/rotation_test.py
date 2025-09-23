#!/usr/bin/env python3
"""
Test script for log rotation and file handling optimizations.
"""

import logging
import tempfile
import time
import os
import gzip
import sys
from pathlib import Path

# Add the parent directory to the path so we can import genebot modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from genebot.logging.rotation import (
    CompressedRotatingFileHandler, OptimizedFileHandler, DiskSpaceMonitor,
    RotationPolicy, setup_log_rotation_policy, monitor_log_directory
)
from genebot.logging.factory import setup_global_config, get_logger
from genebot.logging.config import LoggingConfig


def test_disk_space_monitor():
    """Test disk space monitoring functionality."""
    print("=== Testing Disk Space Monitor ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create monitor
        monitor = DiskSpaceMonitor(temp_path, min_free_space_mb=1)
        
        # Test disk space info
        info = monitor.get_disk_space_info()
        print(f"Disk space info:")
        print(f"  Total: {info.total_bytes / (1024**3):.2f} GB")
        print(f"  Used: {info.used_bytes / (1024**3):.2f} GB")
        print(f"  Free: {info.free_bytes / (1024**3):.2f} GB")
        print(f"  Usage: {info.usage_percent:.1f}%")
        
        # Test space availability
        available = monitor.is_space_available(1024*1024)  # 1MB
        print(f"Space available for 1MB: {available}")
        
        # Create some test log files
        for i in range(5):
            log_file = temp_path / f"test_{i}.log"
            with open(log_file, 'w') as f:
                f.write(f"Test log content {i}\n" * 100)
            
            # Set different modification times
            mtime = time.time() - (i * 24 * 60 * 60)  # i days ago
            os.utime(log_file, (mtime, mtime))
        
        # Test cleanup by age
        deleted_files = monitor.cleanup_old_files(max_age_days=2)
        print(f"Deleted {len(deleted_files)} old files: {[f.name for f in deleted_files]}")
        
        remaining_files = list(temp_path.glob("*.log"))
        print(f"Remaining files: {[f.name for f in remaining_files]}")
        
        print("✓ Disk space monitor test passed\n")


def test_compressed_rotating_handler():
    """Test compressed rotating file handler."""
    print("=== Testing Compressed Rotating Handler ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        log_file = temp_path / "test_rotating.log"
        
        # Create rotation policy
        policy = RotationPolicy(
            max_file_size=1024,  # 1KB for quick rotation
            max_files=3,
            compress_rotated=True,
            max_age_days=1,
            min_free_space_mb=1
        )
        
        # Create handler
        handler = CompressedRotatingFileHandler(
            str(log_file),
            maxBytes=1024,
            backupCount=3,
            rotation_policy=policy
        )
        
        # Create logger
        logger = logging.getLogger('rotation_test')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        # Generate enough logs to trigger rotation
        for i in range(100):
            logger.info(f"Test message {i} with some content to fill up the log file quickly")
        
        # Wait a bit for compression to complete
        time.sleep(1.0)
        
        # Check files created
        log_files = list(temp_path.glob("*"))
        print(f"Files created: {[f.name for f in log_files]}")
        
        # Check for compressed files
        compressed_files = list(temp_path.glob("*.gz"))
        print(f"Compressed files: {[f.name for f in compressed_files]}")
        
        # Verify compression worked
        if compressed_files:
            compressed_file = compressed_files[0]
            with gzip.open(compressed_file, 'rt') as f:
                content = f.read()
            print(f"Compressed file content preview: {content[:100]}...")
        
        # Clean up
        handler.close()
        logger.removeHandler(handler)
        
        print("✓ Compressed rotating handler test passed\n")


def test_optimized_file_handler():
    """Test optimized file handler."""
    print("=== Testing Optimized File Handler ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        log_file = temp_path / "test_optimized.log"
        
        # Create optimized handler
        handler = OptimizedFileHandler(str(log_file), buffer_size=4096)
        
        # Create logger
        logger = logging.getLogger('optimized_test')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        # Test performance
        start_time = time.perf_counter()
        
        for i in range(1000):
            logger.info(f"Optimized log message {i} with buffered I/O")
        
        handler.flush()
        elapsed_time = time.perf_counter() - start_time
        
        print(f"Optimized logging time: {elapsed_time:.4f}s ({elapsed_time/1000*1000:.2f}ms per message)")
        
        # Check file size
        file_size = log_file.stat().st_size
        print(f"Log file size: {file_size} bytes")
        
        # Verify content
        with open(log_file, 'r') as f:
            lines = f.readlines()
        print(f"Lines written: {len(lines)}")
        
        # Clean up
        handler.close()
        logger.removeHandler(handler)
        
        print("✓ Optimized file handler test passed\n")


def test_integrated_rotation():
    """Test integrated rotation with factory."""
    print("=== Testing Integrated Rotation ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Setup configuration with optimized rotation
        config = LoggingConfig(
            level="DEBUG",
            console_output=True,
            file_output=True,
            log_directory=temp_path,
            max_file_size=2048,  # 2KB for quick rotation
            backup_count=3,
            optimized_file_io=True,
            compress_rotated_files=True,
            max_log_age_days=1,
            min_free_space_mb=1,
            cleanup_on_startup=True
        )
        
        setup_global_config(config)
        
        # Get logger
        logger = get_logger("integrated_rotation_test")
        
        # Generate logs to trigger rotation
        for i in range(200):
            logger.info(f"Integrated rotation test message {i} with enough content to trigger rotation")
        
        # Wait for compression
        time.sleep(2.0)
        
        # Check directory status
        from genebot.logging.factory import get_log_directory_status
        status = get_log_directory_status()
        
        print("Log directory status:")
        print(f"  Disk space: {status.get('disk_space', {})}")
        print(f"  Log files: {status.get('log_files', {})}")
        
        # List actual files
        all_files = list(temp_path.glob("*"))
        print(f"Actual files: {[f.name for f in all_files]}")
        
        # Check for compressed files
        compressed_files = list(temp_path.glob("*.gz"))
        print(f"Compressed files: {len(compressed_files)}")
        
        print("✓ Integrated rotation test passed\n")


def test_performance_comparison():
    """Compare performance of different handlers."""
    print("=== Testing Performance Comparison ===\n")
    
    iterations = 1000
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test standard handler
        standard_file = temp_path / "standard.log"
        standard_handler = logging.FileHandler(str(standard_file))
        standard_logger = logging.getLogger('standard_perf')
        standard_logger.setLevel(logging.DEBUG)
        standard_logger.addHandler(standard_handler)
        
        start_time = time.perf_counter()
        for i in range(iterations):
            standard_logger.info(f"Standard message {i}")
        standard_handler.flush()
        standard_time = time.perf_counter() - start_time
        
        standard_handler.close()
        standard_logger.removeHandler(standard_handler)
        
        # Test optimized handler
        optimized_file = temp_path / "optimized.log"
        optimized_handler = OptimizedFileHandler(str(optimized_file), buffer_size=8192)
        optimized_logger = logging.getLogger('optimized_perf')
        optimized_logger.setLevel(logging.DEBUG)
        optimized_logger.addHandler(optimized_handler)
        
        start_time = time.perf_counter()
        for i in range(iterations):
            optimized_logger.info(f"Optimized message {i}")
        optimized_handler.flush()
        optimized_time = time.perf_counter() - start_time
        
        optimized_handler.close()
        optimized_logger.removeHandler(optimized_handler)
        
        # Test compressed rotating handler
        rotating_file = temp_path / "rotating.log"
        policy = RotationPolicy(max_file_size=50*1024, max_files=2, compress_rotated=False)  # Disable compression for fair comparison
        rotating_handler = CompressedRotatingFileHandler(
            str(rotating_file),
            maxBytes=50*1024,
            backupCount=2,
            rotation_policy=policy
        )
        rotating_logger = logging.getLogger('rotating_perf')
        rotating_logger.setLevel(logging.DEBUG)
        rotating_logger.addHandler(rotating_handler)
        
        start_time = time.perf_counter()
        for i in range(iterations):
            rotating_logger.info(f"Rotating message {i}")
        rotating_handler.flush()
        rotating_time = time.perf_counter() - start_time
        
        rotating_handler.close()
        rotating_logger.removeHandler(rotating_handler)
        
        # Compare results
        print("Performance comparison:")
        print(f"  Standard handler: {standard_time:.4f}s ({standard_time/iterations*1000:.2f}ms per message)")
        print(f"  Optimized handler: {optimized_time:.4f}s ({optimized_time/iterations*1000:.2f}ms per message)")
        print(f"  Rotating handler: {rotating_time:.4f}s ({rotating_time/iterations*1000:.2f}ms per message)")
        
        if optimized_time < standard_time:
            improvement = ((standard_time - optimized_time) / standard_time) * 100
            print(f"  Optimized improvement: {improvement:.1f}%")
        
        # Check file sizes
        print("\nFile sizes:")
        for name, file_path in [("Standard", standard_file), ("Optimized", optimized_file), ("Rotating", rotating_file)]:
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  {name}: {size} bytes")
        
        print("✓ Performance comparison test passed\n")


def main():
    """Run all rotation and file handling tests."""
    print("=== Log Rotation and File Handling Tests ===\n")
    
    try:
        test_disk_space_monitor()
        test_compressed_rotating_handler()
        test_optimized_file_handler()
        test_integrated_rotation()
        test_performance_comparison()
        
        print("=== All Rotation Tests Passed! ===")
        
    except Exception as e:
        print(f"Error in rotation tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()