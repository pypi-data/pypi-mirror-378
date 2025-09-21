# Logging Developer Guide

## Quick Start

### Basic Setup

```python
from genebot.logging.factory import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Start logging
logger.info("Application started")
```

### Configuration

Create or update `config/logging_config.yaml`:

```yaml
logging:
  level: INFO
  format_type: structured
  console_output: true
  file_output: true
  log_directory: logs
```

## Core Concepts

### Logger Factory

The centralized logger factory provides consistent logger instances:

```python
from genebot.logging.factory import (
    get_logger,           # General purpose logger
    get_trade_logger,     # Trade-specific logger
    get_performance_logger, # Performance metrics logger
    get_error_logger,     # Error tracking logger
    get_cli_logger        # CLI operations logger
)
```

### Context-Aware Logging

Add context to your logs for better traceability:

```python
from genebot.logging.context import LogContext
from genebot.logging.factory import get_logger

# Create context
context = LogContext(
    component="trading",
    operation="place_order",
    symbol="BTCUSDT",
    exchange="binance"
)

# Get logger with context
logger = get_logger("trading.orders", context)

# All messages will include context
logger.info("Order placed successfully")
```

### Structured Logging

Use structured data for better log analysis:

```python
logger.info("Trade executed", extra={
    "trade_id": "T123456",
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 0.1,
    "price": 45000.0,
    "commission": 0.45,
    "timestamp": "2025-09-20T12:34:56Z"
})
```

## Common Patterns

### Module-Level Logger

```python
# At the top of your module
from genebot.logging.factory import get_logger

logger = get_logger(__name__)

class TradingStrategy:
    def __init__(self):
        # Use module logger or create specific logger
        self.logger = logger.with_context(
            component="strategy",
            operation="initialization"
        )
    
    def execute(self):
        self.logger.info("Executing strategy")
```

### Class-Level Logger

```python
from genebot.logging.factory import get_logger
from genebot.logging.context import LogContext

class OrderManager:
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        
        # Create logger with class context
        context = LogContext(
            component="order_management",
            exchange=exchange_name
        )
        self.logger = get_logger(f"{__name__}.OrderManager", context)
    
    def place_order(self, symbol: str, side: str, quantity: float):
        # Update context for this operation
        order_logger = self.logger.with_context(
            operation="place_order",
            symbol=symbol
        )
        
        order_logger.info("Placing order", extra={
            "side": side,
            "quantity": quantity
        })
        
        try:
            # Place order logic
            order_id = self._execute_order(symbol, side, quantity)
            
            order_logger.info("Order placed successfully", extra={
                "order_id": order_id
            })
            
            return order_id
            
        except Exception as e:
            order_logger.exception("Failed to place order", extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            raise
```

### Function-Level Logging

```python
from genebot.logging.factory import get_logger

logger = get_logger(__name__)

def calculate_position_size(balance: float, risk_percent: float, price: float) -> float:
    """Calculate position size based on risk management rules."""
    
    # Log function entry with parameters
    logger.debug("Calculating position size", extra={
        "balance": balance,
        "risk_percent": risk_percent,
        "price": price
    })
    
    try:
        # Calculation logic
        risk_amount = balance * (risk_percent / 100)
        position_size = risk_amount / price
        
        # Log successful calculation
        logger.info("Position size calculated", extra={
            "position_size": position_size,
            "risk_amount": risk_amount
        })
        
        return position_size
        
    except Exception as e:
        # Log calculation error
        logger.exception("Position size calculation failed", extra={
            "balance": balance,
            "risk_percent": risk_percent,
            "price": price
        })
        raise
```

## Specialized Loggers

### Trade Logger

Use for all trade-related events:

```python
from genebot.logging.factory import get_trade_logger

trade_logger = get_trade_logger()

# Log trade execution
trade_logger.info("Trade executed", extra={
    "trade_id": "T123456",
    "symbol": "BTCUSDT",
    "side": "buy",
    "quantity": 0.1,
    "entry_price": 45000.0,
    "exit_price": 45500.0,
    "profit_loss": 50.0,
    "commission": 0.45,
    "strategy": "momentum_v2",
    "execution_time_ms": 150
})

# Log trade signals
trade_logger.info("Trade signal generated", extra={
    "signal_type": "buy",
    "symbol": "BTCUSDT",
    "confidence": 0.85,
    "indicators": {
        "rsi": 35.2,
        "macd": 0.15,
        "volume_ratio": 1.8
    }
})
```

### Performance Logger

Use for system performance metrics:

```python
from genebot.logging.factory import get_performance_logger

perf_logger = get_performance_logger()

# Log system metrics
perf_logger.info("System performance", extra={
    "cpu_usage_percent": 45.2,
    "memory_usage_mb": 512.8,
    "disk_usage_percent": 78.5,
    "network_latency_ms": 25.3
})

# Log strategy performance
perf_logger.info("Strategy performance", extra={
    "strategy_name": "momentum_v2",
    "total_trades": 150,
    "winning_trades": 98,
    "win_rate": 0.653,
    "total_profit": 2450.75,
    "max_drawdown": -125.30,
    "sharpe_ratio": 1.85
})
```

### Error Logger

Use for centralized error tracking:

```python
from genebot.logging.factory import get_error_logger

error_logger = get_error_logger()

# Log application errors
try:
    connect_to_exchange()
except ConnectionError as e:
    error_logger.error("Exchange connection failed", extra={
        "exchange": "binance",
        "error_type": "ConnectionError",
        "error_message": str(e),
        "retry_count": 3,
        "last_successful_connection": "2025-09-20T10:30:00Z"
    })

# Log business logic errors
if insufficient_balance:
    error_logger.warning("Insufficient balance for trade", extra={
        "required_balance": 1000.0,
        "available_balance": 750.0,
        "symbol": "BTCUSDT",
        "operation": "place_order"
    })
```

### CLI Logger

Use for command-line interface operations:

```python
from genebot.logging.factory import get_cli_logger

cli_logger = get_cli_logger(verbose=True)

# Log CLI commands
cli_logger.info("Command executed", extra={
    "command": "start-bot",
    "arguments": ["--config", "production.yaml"],
    "user": "trader01",
    "execution_time_ms": 1250
})

# Log user interactions
cli_logger.info("User action", extra={
    "action": "view_positions",
    "user": "trader01",
    "filters": {"symbol": "BTC*"},
    "results_count": 5
})
```

## Performance Optimization

### Lazy Evaluation

Use lazy evaluation for expensive log message construction:

```python
# Good: Lazy evaluation
logger.debug("Complex calculation result: %s", 
             lambda: expensive_calculation())

# Better: Check log level first
if logger.isEnabledFor(logging.DEBUG):
    result = expensive_calculation()
    logger.debug("Complex calculation result: %s", result)

# Best: Use structured logging with conditional data
logger.debug("Complex calculation completed", extra={
    "result": expensive_calculation() if logger.isEnabledFor(logging.DEBUG) else None
})
```

### Async Logging

Enable async logging for high-frequency operations:

```yaml
logging:
  enable_async_logging: true
  log_buffer_size: 1000
  async_queue_size: 10000
  async_batch_size: 100
  async_flush_interval: 1.0
```

```python
# High-frequency logging (automatically async if enabled)
for tick in market_data_stream:
    logger.debug("Market tick", extra={
        "symbol": tick.symbol,
        "price": tick.price,
        "volume": tick.volume,
        "timestamp": tick.timestamp
    })
```

### Performance Measurement

Use the performance logger to measure execution times:

```python
from genebot.logging.performance_logger import PerformanceLogger

perf_logger = PerformanceLogger()

# Measure function execution time
@perf_logger.measure_execution_time
def calculate_indicators(data):
    # Your calculation logic
    return indicators

# Measure code block execution time
with perf_logger.measure_time("strategy_execution"):
    signals = strategy.generate_signals(market_data)
    orders = strategy.create_orders(signals)

# Log custom performance metrics
perf_logger.log_metric("orders_per_second", orders_count / elapsed_time)
perf_logger.log_memory_usage("after_data_processing")
```

## Error Handling

### Exception Logging

Always use `logger.exception()` for proper stack traces:

```python
try:
    result = risky_operation()
except SpecificException as e:
    # Log with context and continue
    logger.warning("Operation failed, retrying", extra={
        "operation": "risky_operation",
        "attempt": retry_count,
        "error": str(e)
    })
    
except Exception as e:
    # Log with full stack trace
    logger.exception("Unexpected error in risky_operation", extra={
        "operation": "risky_operation",
        "input_data": input_data,
        "error_type": type(e).__name__
    })
    raise
```

### Error Context

Provide rich context for error investigation:

```python
def process_market_data(symbol: str, data: dict):
    try:
        # Processing logic
        pass
    except Exception as e:
        logger.exception("Market data processing failed", extra={
            "symbol": symbol,
            "data_size": len(data),
            "data_keys": list(data.keys()),
            "processing_stage": "validation",
            "error_type": type(e).__name__,
            "timestamp": datetime.utcnow().isoformat()
        })
        raise
```

## Testing with Logging

### Test Logger Configuration

```python
import pytest
from genebot.logging.config import LoggingConfig
from genebot.logging.factory import setup_global_config, get_logger

@pytest.fixture
def test_logging_config():
    """Configure logging for tests."""
    config = LoggingConfig(
        level="DEBUG",
        console_output=False,
        file_output=False,
        enable_performance_logging=False
    )
    setup_global_config(config)
    return config

def test_trading_strategy(test_logging_config):
    """Test trading strategy with logging."""
    logger = get_logger("test.strategy")
    
    # Your test logic with logging
    strategy = TradingStrategy()
    result = strategy.execute()
    
    # Verify logging behavior if needed
    assert result is not None
```

### Capturing Log Output

```python
import logging
from io import StringIO

def test_log_output():
    """Test that correct log messages are generated."""
    
    # Capture log output
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    
    logger = get_logger("test.module")
    logger.logger.addHandler(handler)
    
    # Execute code that should log
    logger.info("Test message", extra={"key": "value"})
    
    # Verify log output
    log_output = log_capture.getvalue()
    assert "Test message" in log_output
    assert "key" in log_output
```

### Mock Logging

```python
from unittest.mock import patch, MagicMock

def test_with_mocked_logger():
    """Test with mocked logger to verify log calls."""
    
    with patch('genebot.logging.factory.get_logger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Execute code that should log
        function_that_logs()
        
        # Verify logging calls
        mock_logger.info.assert_called_once()
        mock_logger.error.assert_not_called()
```

## Configuration Management

### Environment-Specific Configurations

Create different configurations for each environment:

```yaml
# config/logging_development.yaml
logging:
  level: DEBUG
  format_type: simple
  console_output: true
  file_output: true
  enable_performance_logging: true

# config/logging_production.yaml
logging:
  level: INFO
  format_type: structured
  console_output: false
  file_output: true
  enable_async_logging: true
  max_file_size: 52428800  # 50MB
  backup_count: 10
```

### Dynamic Configuration

```python
from genebot.logging.config import LoggingConfig
from genebot.logging.factory import setup_global_config

def configure_logging_for_environment(env: str):
    """Configure logging based on environment."""
    
    if env == "development":
        config = LoggingConfig.for_environment("development")
    elif env == "production":
        config = LoggingConfig.for_environment("production")
    else:
        config = LoggingConfig()  # Default configuration
    
    setup_global_config(config)
```

### Configuration Validation

```python
from genebot.logging.validation import validate_configuration_file

# Validate configuration before using
report = validate_configuration_file(
    Path("config/logging_config.yaml"),
    run_functionality_tests=True
)

if report.overall_status != "passed":
    print("Configuration validation failed:")
    for error in report.errors:
        print(f"  - {error.message}")
```

## Integration Patterns

### Dependency Injection

```python
from typing import Protocol
from genebot.logging.factory import get_logger

class Logger(Protocol):
    def info(self, message: str, **kwargs): ...
    def error(self, message: str, **kwargs): ...
    def exception(self, message: str, **kwargs): ...

class TradingService:
    def __init__(self, logger: Logger = None):
        self.logger = logger or get_logger(__name__)
    
    def execute_trade(self):
        self.logger.info("Executing trade")
```

### Decorator Pattern

```python
from functools import wraps
from genebot.logging.factory import get_logger

def log_execution(operation_name: str = None):
    """Decorator to log function execution."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            op_name = operation_name or func.__name__
            
            logger.info(f"Starting {op_name}", extra={
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            })
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {op_name}", extra={
                    "function": func.__name__,
                    "success": True
                })
                return result
                
            except Exception as e:
                logger.exception(f"Failed {op_name}", extra={
                    "function": func.__name__,
                    "error_type": type(e).__name__
                })
                raise
        
        return wrapper
    return decorator

# Usage
@log_execution("order_placement")
def place_order(symbol: str, quantity: float):
    # Order placement logic
    pass
```

### Context Manager Pattern

```python
from contextlib import contextmanager
from genebot.logging.factory import get_logger

@contextmanager
def log_operation(operation_name: str, logger=None, **context):
    """Context manager for logging operations."""
    
    if logger is None:
        logger = get_logger(__name__)
    
    logger.info(f"Starting {operation_name}", extra=context)
    
    try:
        yield logger
        logger.info(f"Completed {operation_name}", extra=context)
        
    except Exception as e:
        logger.exception(f"Failed {operation_name}", extra={
            **context,
            "error_type": type(e).__name__
        })
        raise

# Usage
with log_operation("data_processing", symbol="BTCUSDT") as logger:
    # Processing logic
    data = process_market_data()
    logger.info("Data processed", extra={"records": len(data)})
```

## Best Practices Summary

### Do's

1. **Use structured logging** with consistent field names
2. **Include relevant context** in log messages
3. **Use appropriate log levels** for different message types
4. **Log exceptions with full stack traces** using `logger.exception()`
5. **Use lazy evaluation** for expensive log message construction
6. **Configure different settings** for different environments
7. **Validate configurations** before deployment
8. **Use specialized loggers** for specific purposes (trade, performance, error)
9. **Include timing information** for performance-critical operations
10. **Mask sensitive data** in production logs

### Don'ts

1. **Don't use print statements** - use proper logging instead
2. **Don't log sensitive information** like API keys or passwords
3. **Don't create duplicate loggers** - use the centralized factory
4. **Don't ignore log levels** - respect the configured level
5. **Don't log in tight loops** without considering performance
6. **Don't use string formatting** in log calls - use structured data
7. **Don't catch and ignore exceptions** without logging them
8. **Don't use generic error messages** - provide specific context
9. **Don't forget to configure log rotation** for production
10. **Don't mix logging configurations** - use centralized system

### Performance Tips

1. **Enable async logging** for high-frequency operations
2. **Use appropriate buffer sizes** for your workload
3. **Configure log rotation** to prevent large files
4. **Monitor logging overhead** with performance metrics
5. **Use conditional logging** for debug messages in hot paths
6. **Optimize log message construction** with lazy evaluation
7. **Consider log sampling** for very high-frequency events
8. **Use structured logging** instead of string concatenation
9. **Configure external library log levels** to reduce noise
10. **Monitor disk space usage** and configure cleanup policies