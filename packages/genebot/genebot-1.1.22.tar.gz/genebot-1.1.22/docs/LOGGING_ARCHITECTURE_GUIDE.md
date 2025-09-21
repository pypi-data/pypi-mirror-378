# Logging Architecture Guide

## Overview

The trading bot uses a centralized logging system that provides consistent, structured logging across all modules. This system eliminates duplicate logging configurations, replaces print statements with proper logging, and offers specialized loggers for different operational contexts.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Logging Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │  Application    │    │      Centralized Logger         │ │
│  │   Modules       │───▶│         Factory                 │ │
│  │                 │    │                                 │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                        │                    │
│                                        ▼                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Unified Configuration                      │ │
│  │  • Environment-aware settings                          │ │
│  │  • Single source of truth                              │ │
│  │  • Structured JSON formatting                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                        │                    │
│                                        ▼                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Specialized Loggers                        │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │ │
│  │  │    Trade    │ │     CLI     │ │   Performance   │   │ │
│  │  │   Logger    │ │   Logger    │ │     Logger      │   │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                        │                    │
│                                        ▼                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Output Handlers                          │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │ │
│  │  │   Console   │ │    File     │ │    Rotating     │   │ │
│  │  │   Handler   │ │   Handler   │ │   File Handler  │   │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Logger Hierarchy

```
root
├── genebot
│   ├── cli
│   │   ├── commands
│   │   ├── utils
│   │   └── main
│   ├── core
│   │   ├── trading_bot
│   │   └── orchestrator
│   ├── strategies
│   ├── exchanges
│   └── monitoring
├── trading_bot
│   ├── trades
│   ├── performance
│   ├── errors
│   └── audit
└── external_libs (controlled noise level)
    ├── ccxt (WARNING)
    ├── urllib3 (WARNING)
    └── requests (WARNING)
```

## Key Features

### 1. Centralized Configuration
- Single configuration file for all logging settings
- Environment-aware defaults (development, testing, production)
- Environment variable overrides
- YAML and JSON configuration support

### 2. Structured Logging
- Consistent JSON format for machine processing
- Context-aware logging with metadata
- Standardized field names across all modules
- Performance metrics integration

### 3. Specialized Loggers
- **Trade Logger**: Dedicated to trade execution events
- **Performance Logger**: System metrics and monitoring
- **Error Logger**: Centralized error collection
- **CLI Logger**: User-friendly console output

### 4. Performance Optimization
- Lazy evaluation for debug messages
- Asynchronous logging for high-frequency operations
- Optimized file I/O and rotation
- Memory usage monitoring

### 5. Security Features
- Sensitive data masking
- Secure file permissions
- PII redaction capabilities
- Audit trail support

## Configuration

### Basic Configuration

```yaml
logging:
  level: INFO
  format_type: structured  # structured or simple
  console_output: true
  file_output: true
  log_directory: logs
  max_file_size: 10485760  # 10MB
  backup_count: 5
  environment: development
```

### Environment-Specific Settings

#### Development
```yaml
logging:
  level: DEBUG
  format_type: simple
  console_output: true
  file_output: true
  enable_performance_logging: true
  enable_async_logging: false
```

#### Production
```yaml
logging:
  level: INFO
  format_type: structured
  console_output: false
  file_output: true
  enable_performance_logging: true
  enable_async_logging: true
  max_file_size: 52428800  # 50MB
  backup_count: 10
```

#### Testing
```yaml
logging:
  level: WARNING
  format_type: simple
  console_output: false
  file_output: false
  enable_performance_logging: false
```

### Environment Variables

Override any configuration setting using environment variables:

```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT=structured
export LOG_DIRECTORY=/var/log/trading-bot
export LOG_ASYNC=true
export LOG_MASK_SENSITIVE=true
```

## Usage Examples

### Basic Logging

```python
from genebot.logging.factory import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Context-Aware Logging

```python
from genebot.logging.factory import get_logger
from genebot.logging.context import LogContext

# Create context for structured logging
context = LogContext(
    component="trading",
    operation="position_open",
    symbol="BTCUSDT",
    exchange="binance",
    strategy="momentum_v2"
)

# Get logger with context
logger = get_logger("trading.positions", context)

# All log messages will include context information
logger.info("Opening position", extra={
    "quantity": 0.1,
    "price": 45000.0,
    "side": "buy"
})
```

### Specialized Loggers

```python
from genebot.logging.factory import (
    get_trade_logger, 
    get_performance_logger, 
    get_error_logger
)

# Trade logging
trade_logger = get_trade_logger()
trade_logger.info("Trade executed", extra={
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 0.1,
    "price": 45000.0,
    "commission": 0.45
})

# Performance logging
perf_logger = get_performance_logger()
perf_logger.info("Strategy performance", extra={
    "strategy": "momentum_v2",
    "win_rate": 0.65,
    "profit_loss": 1250.50,
    "trades_count": 100
})

# Error logging
error_logger = get_error_logger()
try:
    # Some operation that might fail
    pass
except Exception as e:
    error_logger.exception("Operation failed", extra={
        "operation": "place_order",
        "symbol": "BTCUSDT",
        "error_code": "INSUFFICIENT_BALANCE"
    })
```

### Performance Measurement

```python
from genebot.logging.performance_logger import PerformanceLogger

perf_logger = PerformanceLogger()

# Measure execution time
with perf_logger.measure_time("strategy_calculation"):
    # Your strategy calculation code
    result = calculate_signals()

# Log memory usage
perf_logger.log_memory_usage("after_data_processing")

# Log custom metrics
perf_logger.log_metric("orders_per_second", 15.2)
```

## Log Output Formats

### Structured JSON Format

```json
{
  "timestamp": "2025-09-20T12:34:56.789Z",
  "level": "INFO",
  "logger": "genebot.core.trading_bot",
  "message": "Position opened for BTCUSDT",
  "context": {
    "component": "trading",
    "operation": "position_open",
    "symbol": "BTCUSDT",
    "exchange": "binance",
    "strategy": "momentum_v2",
    "session_id": "sess_123456"
  },
  "metadata": {
    "module": "trading_bot",
    "function": "open_position",
    "line": 245,
    "thread": "MainThread",
    "process": 12345
  },
  "performance": {
    "execution_time_ms": 15.2,
    "memory_usage_mb": 128.5
  }
}
```

### Simple Format

```
2025-09-20 12:34:56,789 - genebot.core.trading_bot - INFO - [trading_bot:open_position:245] - Position opened for BTCUSDT
```

## File Organization

### Log Directory Structure

```
logs/
├── genebot.log              # Main application log
├── trades.log               # Trade execution logs
├── performance.log          # Performance metrics
├── errors.log               # Error and exception logs
├── cli.log                  # CLI operation logs
├── instances/               # Instance-specific logs
│   ├── bot_001.log
│   └── bot_002.log
├── trades/                  # Detailed trade logs
│   ├── 2025-09-20_trades.log
│   └── 2025-09-19_trades.log
└── metrics/                 # Performance metrics
    ├── 2025-09-20_metrics.log
    └── 2025-09-19_metrics.log
```

### Log Rotation

- **File Size**: Rotate when files exceed configured size (default: 10MB)
- **Backup Count**: Keep specified number of backup files (default: 5)
- **Compression**: Optionally compress rotated files
- **Age-based**: Automatically clean up old log files

## Integration with External Systems

### Log Aggregation

The structured JSON format is designed for easy integration with log aggregation systems:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Fluentd**
- **Splunk**
- **Datadog**
- **New Relic**

### Monitoring and Alerting

Set up alerts based on log patterns:

```python
# Error rate monitoring
if error_count > threshold:
    send_alert("High error rate detected")

# Performance monitoring
if response_time > sla_threshold:
    send_alert("Performance degradation detected")

# Trade monitoring
if failed_trades_ratio > 0.1:
    send_alert("High trade failure rate")
```

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational information
- **WARNING**: Something unexpected happened but the system continues
- **ERROR**: A serious problem occurred
- **CRITICAL**: The system cannot continue

### 2. Include Relevant Context

```python
# Good: Include relevant context
logger.info("Order placed", extra={
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 0.1,
    "order_id": "12345"
})

# Bad: Vague message without context
logger.info("Order placed")
```

### 3. Use Structured Data

```python
# Good: Structured data for analysis
logger.info("Trade completed", extra={
    "trade_id": "T123456",
    "symbol": "BTCUSDT",
    "profit_loss": 125.50,
    "duration_seconds": 3600
})

# Bad: Unstructured string
logger.info("Trade T123456 for BTCUSDT completed with P&L 125.50 after 1 hour")
```

### 4. Avoid Logging Sensitive Information

```python
# Good: Mask sensitive data
logger.info("API request", extra={
    "endpoint": "/api/orders",
    "api_key": "***masked***"
})

# Bad: Expose sensitive data
logger.info("API request", extra={
    "endpoint": "/api/orders",
    "api_key": "actual_api_key_here"
})
```

### 5. Use Exception Logging

```python
# Good: Use exception() for proper stack traces
try:
    place_order()
except Exception as e:
    logger.exception("Failed to place order", extra={
        "symbol": "BTCUSDT",
        "error_type": type(e).__name__
    })

# Bad: Lose stack trace information
try:
    place_order()
except Exception as e:
    logger.error(f"Failed to place order: {e}")
```

## Troubleshooting

### Common Issues

1. **Duplicate Log Messages**
   - Check logger propagation settings
   - Ensure no duplicate handlers
   - Verify centralized configuration is used

2. **Missing Log Files**
   - Check file permissions
   - Verify log directory exists and is writable
   - Check disk space availability

3. **Performance Issues**
   - Enable async logging for high-frequency operations
   - Adjust buffer sizes
   - Use appropriate log levels

4. **Configuration Not Loading**
   - Check file path and permissions
   - Validate YAML/JSON syntax
   - Check environment variable overrides

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT=simple
```

### Validation Tools

Use the built-in validation tools:

```bash
# Validate configuration
python scripts/logging_migration_tool.py validate config/logging_config.yaml

# Test logging functionality
python scripts/logging_migration_tool.py validate config/logging_config.yaml --test-logging
```

## Migration from Legacy Systems

### Automatic Migration

Use the migration tool to automatically convert legacy configurations:

```bash
# Scan for legacy configurations
python scripts/logging_migration_tool.py scan /path/to/project

# Migrate all configurations
python scripts/logging_migration_tool.py migrate /path/to/project --output new_config.yaml

# Create backups before migration
python scripts/logging_migration_tool.py backup /path/to/project
```

### Manual Migration Steps

1. **Backup existing configurations**
2. **Install centralized logging system**
3. **Create new configuration file**
4. **Update import statements**
5. **Replace print statements**
6. **Test and validate**

See the [Migration Guide](LOGGING_MIGRATION_GUIDE.md) for detailed instructions.

## Performance Considerations

### Optimization Techniques

1. **Lazy Evaluation**: Debug messages are only formatted when debug level is enabled
2. **Async Logging**: High-frequency logs are processed asynchronously
3. **Buffered I/O**: File writes are buffered for better performance
4. **Log Rotation**: Prevents large files that impact performance

### Memory Management

- Configure appropriate buffer sizes
- Monitor memory usage with performance logger
- Set up automatic cleanup of old log files
- Use compression for archived logs

### CPU Usage

- Minimize string formatting in hot paths
- Use structured logging instead of string concatenation
- Enable async logging for high-throughput scenarios
- Monitor logging overhead with performance metrics

## Security Considerations

### Data Protection

- Enable sensitive data masking in production
- Use secure file permissions (600 or 640)
- Implement log rotation to prevent information leakage
- Consider log encryption for sensitive environments

### Access Control

- Restrict log file access to authorized users
- Use separate log directories for different security levels
- Implement audit trails for log access
- Consider centralized log storage with access controls

### Compliance

- Configure retention policies according to regulations
- Implement data anonymization where required
- Ensure audit trail completeness
- Document logging practices for compliance reviews