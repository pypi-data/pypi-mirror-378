# Centralized Logging Infrastructure

This module provides a unified logging system for the GeneBot trading bot that consolidates all logging configurations, eliminates duplicates, and provides consistent structured logging across the entire application.

## Features

- **Unified Configuration**: Single source of truth for all logging settings
- **Environment Awareness**: Automatic configuration based on development/testing/production environments
- **Structured Logging**: JSON-formatted logs for machine processing
- **Context Injection**: Automatic context information in all log messages
- **Specialized Loggers**: Purpose-built loggers for trades, CLI, performance, and errors
- **Performance Optimization**: Lazy evaluation and caching for high-frequency logging
- **Security**: Automatic masking of sensitive data in logs

## Quick Start

```python
from genebot.logging import LoggingConfig, LoggerFactory
from genebot.logging.factory import setup_global_config, get_logger

# Set up logging configuration
config = LoggingConfig.for_environment('development')
setup_global_config(config)

# Get a logger
logger = get_logger('my_module')
logger.info("Hello, world!")
```

## Configuration

### From Environment Variables

```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT=structured
export LOG_DIRECTORY=logs
export ENVIRONMENT=development
```

### From Configuration File

```yaml
logging:
  level: INFO
  format_type: structured
  console_output: true
  file_output: true
  log_directory: logs
  environment: production
```

### Programmatic Configuration

```python
from genebot.logging import LoggingConfig

config = LoggingConfig(
    level="INFO",
    format_type="structured",
    console_output=True,
    file_output=True,
    environment="production"
)
```

## Specialized Loggers

### Trade Logger

```python
from genebot.logging.factory import get_trade_logger

trade_logger = get_trade_logger()
trade_logger.trade_opened("BTCUSDT", "BUY", 0.1, 45000.0)
trade_logger.order_placed("order_123", "BTCUSDT", "BUY", 0.1, "MARKET")
```

### Performance Logger

```python
from genebot.logging.factory import get_performance_logger

perf_logger = get_performance_logger()
perf_logger.execution_time("strategy_calculation", 15.5)
perf_logger.memory_usage("trading_engine", 128.5)
```

### CLI Logger

```python
from genebot.logging.factory import get_cli_logger

cli_logger = get_cli_logger(verbose=True)
cli_logger.command_start("backtest", {"symbol": "BTCUSDT"})
cli_logger.progress("Processing data", 50, 100)
```

### Error Logger

```python
from genebot.logging.factory import get_error_logger

error_logger = get_error_logger()
error_logger.error_occurred("ValidationError", "Invalid symbol", "trading")

try:
    # Some operation
    pass
except Exception as e:
    error_logger.exception_caught(e, "trading", "position_open")
```

## Context Management

### Automatic Context

```python
from genebot.logging.context import set_context, trading_context

# Set global context
set_context(trading_context("BTCUSDT", "binance", "momentum"))

# All subsequent logs will include this context
logger = get_logger('trading')
logger.info("This message includes trading context")
```

### Logger-Specific Context

```python
from genebot.logging import LogContext

context = LogContext(
    component="trading",
    operation="position_open",
    symbol="BTCUSDT",
    exchange="binance"
)

logger = get_logger('trading', context)
logger.info("This message has specific context")
```

### Temporary Context

```python
from genebot.logging.context import context_scope, LogContext

with context_scope(LogContext(component="backtest", operation="run")):
    logger.info("This message uses temporary context")
```

## Log Formats

### Structured JSON (Machine-Readable)

```json
{
  "timestamp": "2025-09-20T15:06:00.720617Z",
  "level": "INFO",
  "logger": "genebot.trades",
  "message": "Trade opened: BUY 0.1 BTCUSDT @ 45000.0",
  "metadata": {
    "module": "trading_bot",
    "function": "open_position",
    "line": 245,
    "thread": "MainThread",
    "process": 12345
  },
  "context": {
    "component": "trading",
    "operation": "execution",
    "symbol": "BTCUSDT",
    "exchange": "binance",
    "strategy": "momentum"
  }
}
```

### Simple Format (Human-Readable)

```
2025-09-20 15:06:00 - INFO - genebot.trades - [trading_bot:open_position:245] - Trade opened: BUY 0.1 BTCUSDT @ 45000.0 | symbol=BTCUSDT exchange=binance strategy=momentum
```

## File Organization

The logging system creates separate log files for different purposes:

- `genebot.log` - Main application logs
- `trades.log` - Trade execution events
- `performance.log` - Performance metrics
- `cli.log` - CLI operations
- `errors.log` - Error and exception logs

## Environment-Specific Behavior

### Development
- Log level: DEBUG
- Console output: Enabled
- Format: Simple (human-readable)
- File output: Enabled

### Testing
- Log level: WARNING
- Console output: Disabled
- File output: Disabled
- Minimal overhead

### Production
- Log level: INFO
- Console output: Disabled
- Format: Structured JSON
- Async logging: Enabled
- Larger file sizes and more backups

## Migration from Existing Logging

The new system is designed to be backward compatible. To migrate:

1. Replace existing logger creation:
   ```python
   # Old way
   import logging
   logger = logging.getLogger(__name__)
   
   # New way
   from genebot.logging.factory import get_logger
   logger = get_logger(__name__)
   ```

2. Replace print statements:
   ```python
   # Old way
   print("Processing order...")
   
   # New way
   logger.info("Processing order...")
   ```

3. Update configuration:
   ```python
   # Old way
   logging.basicConfig(level=logging.INFO)
   
   # New way
   from genebot.logging import LoggingConfig
   from genebot.logging.factory import setup_global_config
   
   config = LoggingConfig.for_environment('development')
   setup_global_config(config)
   ```

## Performance Considerations

- Use lazy evaluation for debug messages
- Structured logging has minimal overhead in production
- File rotation prevents disk space issues
- Async logging available for high-frequency scenarios
- Caching reduces logger creation overhead

## Security Features

- Automatic masking of sensitive data (API keys, passwords, etc.)
- Configurable data redaction patterns
- Secure file permissions for log files
- No sensitive data in structured log fields