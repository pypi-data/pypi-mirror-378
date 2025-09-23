# Logging Troubleshooting Guide

## Common Issues and Solutions

### 1. Duplicate Log Messages

**Symptoms:**
- Same log message appears multiple times
- Log files contain redundant entries
- Console output shows repeated messages

**Causes:**
- Multiple handlers attached to the same logger
- Incorrect logger propagation settings
- Multiple logging configurations being applied

**Solutions:**

#### Check Logger Propagation
```python
import logging

# Check current logger configuration
logger = logging.getLogger('your.logger.name')
print(f"Logger: {logger.name}")
print(f"Level: {logger.level}")
print(f"Propagate: {logger.propagate}")
print(f"Handlers: {[type(h).__name__ for h in logger.handlers]}")

# Fix propagation if needed
logger.propagate = False  # Prevent propagation to parent loggers
```

#### Remove Duplicate Handlers
```python
# Clear existing handlers before adding new ones
logger = logging.getLogger('your.logger.name')
logger.handlers.clear()

# Or check for existing handlers
if not logger.handlers:
    handler = logging.StreamHandler()
    logger.addHandler(handler)
```

#### Use Centralized Configuration
```python
# Instead of manual configuration, use centralized system
from genebot.logging.factory import get_logger

# This ensures no duplicates
logger = get_logger(__name__)
```

### 2. Missing Log Files

**Symptoms:**
- Expected log files are not created
- Logs appear in console but not in files
- File handlers seem to be ignored

**Causes:**
- Insufficient file permissions
- Log directory doesn't exist
- Disk space issues
- Incorrect file path configuration

**Solutions:**

#### Check File Permissions
```bash
# Check log directory permissions
ls -la logs/

# Fix permissions if needed
chmod 755 logs/
chmod 644 logs/*.log
```

#### Verify Directory Creation
```python
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Test file creation
test_file = log_dir / "test.log"
try:
    test_file.write_text("test")
    test_file.unlink()
    print("File creation successful")
except Exception as e:
    print(f"File creation failed: {e}")
```

#### Check Disk Space
```bash
# Check available disk space
df -h

# Check specific directory
du -sh logs/
```

#### Validate Configuration
```python
from genebot.logging.validation import validate_configuration_file
from pathlib import Path

report = validate_configuration_file(Path("config/logging_config.yaml"))
if report.overall_status != "passed":
    for error in report.errors:
        print(f"Error: {error.message}")
```

### 3. Performance Issues

**Symptoms:**
- Application slowdown when logging is enabled
- High CPU usage during logging operations
- Memory consumption increases over time
- Disk I/O bottlenecks

**Causes:**
- Synchronous logging in high-frequency operations
- Large log messages or complex formatting
- Inefficient file I/O operations
- Memory leaks in logging handlers

**Solutions:**

#### Enable Async Logging
```yaml
# config/logging_config.yaml
logging:
  enable_async_logging: true
  log_buffer_size: 1000
  async_queue_size: 10000
  async_batch_size: 100
  async_flush_interval: 1.0
```

#### Optimize Log Messages
```python
# Bad: Expensive string formatting
logger.debug(f"Complex data: {expensive_calculation()}")

# Good: Lazy evaluation
logger.debug("Complex data: %s", lambda: expensive_calculation())

# Better: Conditional logging
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Complex data: %s", expensive_calculation())
```

#### Use Appropriate Log Levels
```python
# Reduce log volume in production
import os

log_level = "DEBUG" if os.getenv("ENVIRONMENT") == "development" else "INFO"
```

#### Monitor Performance
```python
from genebot.logging.performance_logger import PerformanceLogger

perf_logger = PerformanceLogger()

# Monitor logging overhead
with perf_logger.measure_time("logging_operation"):
    logger.info("Some message")

# Check memory usage
perf_logger.log_memory_usage("after_logging")
```

### 4. Configuration Not Loading

**Symptoms:**
- Default configuration is used instead of custom config
- Environment variables are ignored
- Configuration changes don't take effect

**Causes:**
- Incorrect file path or name
- YAML/JSON syntax errors
- Environment variable naming issues
- Configuration loaded after logging setup

**Solutions:**

#### Verify File Path
```python
from pathlib import Path

config_path = Path("config/logging_config.yaml")
print(f"Config exists: {config_path.exists()}")
print(f"Config path: {config_path.absolute()}")
```

#### Validate YAML Syntax
```bash
# Use yamllint to check syntax
yamllint config/logging_config.yaml

# Or use Python
python -c "import yaml; yaml.safe_load(open('config/logging_config.yaml'))"
```

#### Check Environment Variables
```python
import os

# List all LOG_* environment variables
log_vars = {k: v for k, v in os.environ.items() if k.startswith('LOG_')}
print("Log environment variables:", log_vars)
```

#### Load Configuration Explicitly
```python
from genebot.logging.config import LoggingConfig
from genebot.logging.factory import setup_global_config

# Load and apply configuration
config = LoggingConfig.from_file("config/logging_config.yaml")
setup_global_config(config)
```

### 5. Structured Logging Issues

**Symptoms:**
- JSON format is malformed
- Extra fields are missing from log output
- Context information is not included

**Causes:**
- Incorrect formatter configuration
- Missing extra parameters in log calls
- Context not properly set

**Solutions:**

#### Verify Formatter Configuration
```yaml
logging:
  format_type: structured  # Ensure this is set to 'structured'
```

#### Use Extra Parameters Correctly
```python
# Correct way to add structured data
logger.info("Order placed", extra={
    "order_id": "12345",
    "symbol": "BTCUSDT",
    "quantity": 0.1
})

# Incorrect - data won't be structured
logger.info(f"Order 12345 placed for BTCUSDT quantity 0.1")
```

#### Set Context Properly
```python
from genebot.logging.context import LogContext
from genebot.logging.factory import get_logger

context = LogContext(
    component="trading",
    operation="place_order",
    symbol="BTCUSDT"
)

logger = get_logger(__name__, context)
logger.info("Order placed")  # Context automatically included
```

### 6. External Library Noise

**Symptoms:**
- Too many log messages from third-party libraries
- Irrelevant debug information clutters logs
- Performance impact from external library logging

**Causes:**
- External libraries using verbose logging
- Incorrect log level configuration for external libraries

**Solutions:**

#### Configure External Library Levels
```yaml
logging:
  external_lib_level: WARNING  # Reduce noise from external libraries
```

#### Set Specific Library Levels
```python
import logging

# Reduce noise from specific libraries
logging.getLogger('ccxt').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
```

#### Use Centralized Configuration
```python
from genebot.logging.factory import setup_global_config
from genebot.logging.config import LoggingConfig

config = LoggingConfig(external_lib_level="WARNING")
setup_global_config(config)
```

### 7. Log Rotation Issues

**Symptoms:**
- Log files grow too large
- Old log files are not cleaned up
- Disk space runs out
- Log rotation doesn't work

**Causes:**
- Incorrect rotation configuration
- File permission issues
- Process holding file handles

**Solutions:**

#### Configure Rotation Properly
```yaml
logging:
  max_file_size: 10485760  # 10MB
  backup_count: 5
  compress_rotated_files: true
  max_log_age_days: 30
```

#### Check File Handles
```bash
# Check which processes have log files open
lsof logs/*.log

# Check file sizes
ls -lh logs/
```

#### Manual Rotation Test
```python
import logging.handlers

# Test rotation manually
handler = logging.handlers.RotatingFileHandler(
    "test.log", 
    maxBytes=1024*1024,  # 1MB
    backupCount=3
)

# Generate large log to trigger rotation
for i in range(10000):
    handler.emit(logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg=f"Test message {i} " + "x" * 100, args=(), exc_info=None
    ))
```

### 8. Memory Leaks

**Symptoms:**
- Memory usage increases over time
- Application becomes slower
- Out of memory errors

**Causes:**
- Handlers not properly closed
- Large log buffers
- Circular references in loggers

**Solutions:**

#### Monitor Memory Usage
```python
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")

# Monitor before and after logging operations
log_memory_usage()
# ... logging operations ...
log_memory_usage()
```

#### Configure Buffer Sizes
```yaml
logging:
  log_buffer_size: 1000  # Reasonable buffer size
  async_queue_size: 10000  # Don't make this too large
```

#### Proper Handler Cleanup
```python
import logging
import atexit

def cleanup_logging():
    """Clean up logging handlers on exit."""
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)

atexit.register(cleanup_logging)
```

## Diagnostic Tools

### 1. Logging Configuration Inspector

```python
#!/usr/bin/env python3
"""
Logging configuration inspector tool.
"""

import logging
from genebot.logging.factory import get_logger

def inspect_logging_config():
    """Inspect current logging configuration."""
    
    print("=== Logging Configuration Inspector ===\n")
    
    # Root logger
    root = logging.getLogger()
    print(f"Root Logger:")
    print(f"  Level: {logging.getLevelName(root.level)}")
    print(f"  Handlers: {len(root.handlers)}")
    
    for i, handler in enumerate(root.handlers):
        print(f"    Handler {i}: {type(handler).__name__}")
        print(f"      Level: {logging.getLevelName(handler.level)}")
        if hasattr(handler, 'baseFilename'):
            print(f"      File: {handler.baseFilename}")
    
    print()
    
    # All loggers
    print("All Loggers:")
    for name in sorted(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(name)
        if logger.handlers or logger.level != logging.NOTSET:
            print(f"  {name}:")
            print(f"    Level: {logging.getLevelName(logger.level)}")
            print(f"    Propagate: {logger.propagate}")
            print(f"    Handlers: {len(logger.handlers)}")

if __name__ == "__main__":
    inspect_logging_config()
```

### 2. Log File Analyzer

```python
#!/usr/bin/env python3
"""
Log file analyzer tool.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

def analyze_log_file(log_path: Path):
    """Analyze log file for patterns and issues."""
    
    print(f"=== Analyzing {log_path} ===\n")
    
    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        return
    
    levels = Counter()
    loggers = Counter()
    errors = []
    timestamps = []
    
    with open(log_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Try to parse as JSON (structured logging)
                log_entry = json.loads(line)
                levels[log_entry.get('level', 'UNKNOWN')] += 1
                loggers[log_entry.get('logger', 'UNKNOWN')] += 1
                
                if 'timestamp' in log_entry:
                    timestamps.append(log_entry['timestamp'])
                
                if log_entry.get('level') in ['ERROR', 'CRITICAL']:
                    errors.append({
                        'line': line_num,
                        'message': log_entry.get('message', ''),
                        'timestamp': log_entry.get('timestamp', '')
                    })
                    
            except json.JSONDecodeError:
                # Try to parse as standard format
                parts = line.split(' - ')
                if len(parts) >= 3:
                    level_part = parts[2] if len(parts) > 2 else 'UNKNOWN'
                    levels[level_part] += 1
    
    # Print analysis results
    print(f"Total lines: {line_num}")
    print(f"File size: {log_path.stat().st_size / 1024:.2f} KB")
    print()
    
    print("Log Levels:")
    for level, count in levels.most_common():
        print(f"  {level}: {count}")
    print()
    
    print("Top Loggers:")
    for logger, count in loggers.most_common(10):
        print(f"  {logger}: {count}")
    print()
    
    if errors:
        print(f"Errors found: {len(errors)}")
        for error in errors[-5:]:  # Show last 5 errors
            print(f"  Line {error['line']}: {error['message'][:100]}...")
    
    if timestamps:
        print(f"\nTime range: {timestamps[0]} to {timestamps[-1]}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_log_file(Path(sys.argv[1]))
    else:
        print("Usage: python log_analyzer.py <log_file>")
```

### 3. Performance Monitor

```python
#!/usr/bin/env python3
"""
Logging performance monitor.
"""

import time
import logging
from genebot.logging.factory import get_logger, setup_global_config
from genebot.logging.config import LoggingConfig

def benchmark_logging_performance():
    """Benchmark logging performance."""
    
    print("=== Logging Performance Benchmark ===\n")
    
    # Test configurations
    configs = [
        ("Sync Simple", LoggingConfig(
            format_type="simple",
            enable_async_logging=False,
            console_output=False,
            file_output=True
        )),
        ("Sync Structured", LoggingConfig(
            format_type="structured",
            enable_async_logging=False,
            console_output=False,
            file_output=True
        )),
        ("Async Structured", LoggingConfig(
            format_type="structured",
            enable_async_logging=True,
            console_output=False,
            file_output=True
        ))
    ]
    
    message_counts = [100, 1000, 10000]
    
    for config_name, config in configs:
        print(f"Testing {config_name}:")
        
        setup_global_config(config)
        logger = get_logger("benchmark")
        
        for count in message_counts:
            start_time = time.time()
            
            for i in range(count):
                logger.info("Benchmark message", extra={
                    "iteration": i,
                    "timestamp": time.time(),
                    "data": {"key": "value", "number": i}
                })
            
            elapsed = time.time() - start_time
            rate = count / elapsed
            
            print(f"  {count:5d} messages: {elapsed:.3f}s ({rate:.0f} msg/s)")
        
        print()

if __name__ == "__main__":
    benchmark_logging_performance()
```

## Environment-Specific Troubleshooting

### Development Environment

**Common Issues:**
- Too much debug output
- Performance impact from verbose logging
- Configuration conflicts

**Solutions:**
```yaml
# config/logging_development.yaml
logging:
  level: INFO  # Use INFO instead of DEBUG for better performance
  format_type: simple
  console_output: true
  file_output: true
  enable_performance_logging: false  # Disable if not needed
```

### Testing Environment

**Common Issues:**
- Log output interfering with test results
- File handlers causing test isolation issues
- Performance impact on test execution

**Solutions:**
```yaml
# config/logging_testing.yaml
logging:
  level: WARNING  # Only log warnings and errors
  console_output: false
  file_output: false  # Disable file output for tests
  enable_performance_logging: false
```

```python
# In test fixtures
@pytest.fixture
def disable_logging():
    """Disable logging for tests."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
```

### Production Environment

**Common Issues:**
- Log files growing too large
- Performance impact from synchronous logging
- Insufficient monitoring of log health

**Solutions:**
```yaml
# config/logging_production.yaml
logging:
  level: INFO
  format_type: structured
  console_output: false
  file_output: true
  enable_async_logging: true
  max_file_size: 52428800  # 50MB
  backup_count: 10
  compress_rotated_files: true
  max_log_age_days: 30
```

## Monitoring and Alerting

### Log Health Monitoring

```python
#!/usr/bin/env python3
"""
Log health monitoring script.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta

def monitor_log_health(log_dir: Path):
    """Monitor log file health."""
    
    issues = []
    
    # Check if log directory exists
    if not log_dir.exists():
        issues.append(f"Log directory does not exist: {log_dir}")
        return issues
    
    # Check disk space
    stat = os.statvfs(log_dir)
    free_space_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
    
    if free_space_mb < 100:  # Less than 100MB
        issues.append(f"Low disk space: {free_space_mb:.1f}MB available")
    
    # Check log files
    log_files = list(log_dir.glob("*.log"))
    
    if not log_files:
        issues.append("No log files found")
        return issues
    
    now = datetime.now()
    
    for log_file in log_files:
        # Check file size
        size_mb = log_file.stat().st_size / (1024 * 1024)
        if size_mb > 100:  # Larger than 100MB
            issues.append(f"Large log file: {log_file.name} ({size_mb:.1f}MB)")
        
        # Check last modification time
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        if now - mtime > timedelta(hours=1):
            issues.append(f"Stale log file: {log_file.name} (last modified {mtime})")
    
    return issues

def setup_log_monitoring():
    """Set up automated log monitoring."""
    
    log_dir = Path("logs")
    
    while True:
        issues = monitor_log_health(log_dir)
        
        if issues:
            print(f"[{datetime.now()}] Log health issues detected:")
            for issue in issues:
                print(f"  - {issue}")
            
            # Here you could send alerts via email, Slack, etc.
            
        else:
            print(f"[{datetime.now()}] Log health OK")
        
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    setup_log_monitoring()
```

### Log Rotation Monitoring

```bash
#!/bin/bash
# log_rotation_monitor.sh

LOG_DIR="logs"
MAX_SIZE_MB=50
MAX_AGE_DAYS=30

# Check for oversized log files
find "$LOG_DIR" -name "*.log" -size +${MAX_SIZE_MB}M -exec echo "Oversized log file: {}" \;

# Check for old log files
find "$LOG_DIR" -name "*.log*" -mtime +$MAX_AGE_DAYS -exec echo "Old log file: {}" \;

# Check disk usage
DISK_USAGE=$(df "$LOG_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "High disk usage: ${DISK_USAGE}%"
fi
```

## Recovery Procedures

### Corrupted Log Files

```bash
# Backup corrupted file
cp logs/corrupted.log logs/corrupted.log.backup

# Try to recover readable lines
grep -v "^$" logs/corrupted.log > logs/recovered.log

# Validate JSON structure for structured logs
jq empty logs/recovered.log 2>/dev/null || echo "Invalid JSON found"
```

### Lost Log Configuration

```python
#!/usr/bin/env python3
"""
Emergency logging configuration recovery.
"""

from genebot.logging.config import LoggingConfig
from genebot.logging.factory import setup_global_config

def emergency_logging_setup():
    """Set up emergency logging configuration."""
    
    config = LoggingConfig(
        level="INFO",
        format_type="simple",
        console_output=True,
        file_output=True,
        log_directory="logs_emergency"
    )
    
    setup_global_config(config)
    
    # Save emergency configuration
    config.save_to_file("config/logging_emergency.yaml")
    
    print("Emergency logging configuration activated")

if __name__ == "__main__":
    emergency_logging_setup()
```

### Performance Recovery

```python
#!/usr/bin/env python3
"""
Logging performance recovery procedures.
"""

import logging
from genebot.logging.config import LoggingConfig
from genebot.logging.factory import setup_global_config

def reduce_logging_overhead():
    """Reduce logging overhead for performance recovery."""
    
    # Minimal configuration for performance
    config = LoggingConfig(
        level="ERROR",  # Only log errors
        format_type="simple",
        console_output=False,
        file_output=True,
        enable_async_logging=True,
        enable_performance_logging=False
    )
    
    setup_global_config(config)
    
    # Disable debug logging for all loggers
    logging.getLogger().setLevel(logging.ERROR)
    
    print("Logging overhead reduced for performance recovery")

if __name__ == "__main__":
    reduce_logging_overhead()
```

## Getting Help

### Validation Tools

Use the built-in validation tools to diagnose issues:

```bash
# Validate configuration
python scripts/logging_migration_tool.py validate config/logging_config.yaml --test-logging

# Scan for configuration issues
python scripts/logging_migration_tool.py scan .

# Generate diagnostic report
python -c "
from genebot.logging.validation import validate_configuration_file
from pathlib import Path
report = validate_configuration_file(Path('config/logging_config.yaml'), True)
report.save_to_file(Path('logging_diagnostic_report.json'))
print('Diagnostic report saved to logging_diagnostic_report.json')
"
```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT=simple
python your_application.py
```

### Support Information

When reporting logging issues, include:

1. **Configuration file** (`config/logging_config.yaml`)
2. **Environment variables** (LOG_* variables)
3. **Python version** and operating system
4. **Error messages** and stack traces
5. **Log file samples** (with sensitive data removed)
6. **System resource usage** (CPU, memory, disk)
7. **Validation report** from diagnostic tools

### Community Resources

- Check the project documentation for updates
- Search existing issues in the project repository
- Use the validation and diagnostic tools provided
- Test with minimal configuration to isolate issues