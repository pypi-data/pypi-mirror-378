"""
Unit tests for core logging components.

This module tests the LoggerFactory, LoggingConfig, LogContext, and formatters
to ensure they work correctly and meet all requirements.
"""

import json
import logging
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Import the logging components to test
from genebot.logging.factory import (
    LoggerFactory, ContextualLogger, TradeLogger, PerformanceLogger, 
    ErrorLogger, CLILogger
)
from genebot.logging.config import LoggingConfig, get_default_config, LogLevel, LogFormat, Environment
from genebot.logging.context import (
    LogContext, ContextManager, set_context, get_context, clear_context,
    trading_context, cli_context, monitoring_context, error_context
)
from genebot.logging.formatters import (
    StructuredJSONFormatter, SimpleFormatter, PerformanceOptimizedFormatter, CompactFormatter
)


class TestLoggingConfig(unittest.TestCase):
    """Test LoggingConfig validation and loading."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.yaml"
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config_creation(self):
        """Test creating default configuration."""
        config = LoggingConfig()
        
        # Test default values
        self.assertEqual(config.level, "INFO")
        self.assertEqual(config.format_type, "structured")
        self.assertTrue(config.console_output)
        self.assertTrue(config.file_output)
        self.assertEqual(config.log_directory, Path("logs"))
        self.assertEqual(config.max_file_size, 10 * 1024 * 1024)
        self.assertEqual(config.backup_count, 5)
        self.assertEqual(config.environment, "development")
    
    def test_config_validation_valid_values(self):
        """Test configuration validation with valid values."""
        config = LoggingConfig(
            level="DEBUG",
            format_type="simple",
            environment="production",
            max_file_size=1024,
            backup_count=3
        )
        
        # Should not raise any exceptions
        self.assertEqual(config.level, "DEBUG")
        self.assertEqual(config.format_type, "simple")
        self.assertEqual(config.environment, "production")
    
    def test_config_validation_invalid_level(self):
        """Test configuration validation with invalid log level."""
        with self.assertRaises(ValueError) as context:
            LoggingConfig(level="INVALID")
        
        self.assertIn("Invalid log level", str(context.exception))
    
    def test_config_validation_invalid_format(self):
        """Test configuration validation with invalid format type."""
        with self.assertRaises(ValueError) as context:
            LoggingConfig(format_type="invalid")
        
        self.assertIn("Invalid format type", str(context.exception))
    
    def test_config_validation_invalid_environment(self):
        """Test configuration validation with invalid environment."""
        with self.assertRaises(ValueError) as context:
            LoggingConfig(environment="invalid")
        
        self.assertIn("Invalid environment", str(context.exception))
    
    def test_config_validation_invalid_file_size(self):
        """Test configuration validation with invalid file size."""
        with self.assertRaises(ValueError) as context:
            LoggingConfig(max_file_size=0)
        
        self.assertIn("max_file_size must be positive", str(context.exception))
    
    def test_config_validation_invalid_backup_count(self):
        """Test configuration validation with invalid backup count."""
        with self.assertRaises(ValueError) as context:
            LoggingConfig(backup_count=-1)
        
        self.assertIn("backup_count must be non-negative", str(context.exception))
    
    def test_environment_variable_overrides(self):
        """Test environment variable overrides."""
        with patch.dict(os.environ, {
            'LOG_LEVEL': 'ERROR',
            'LOG_FORMAT': 'simple',
            'LOG_CONSOLE': 'false',
            'LOG_FILE': 'true',
            'LOG_MAX_SIZE': '5242880',
            'LOG_BACKUP_COUNT': '10'
        }):
            config = LoggingConfig()
            
            self.assertEqual(config.level, "ERROR")
            self.assertEqual(config.format_type, "simple")
            self.assertFalse(config.console_output)
            self.assertTrue(config.file_output)
            self.assertEqual(config.max_file_size, 5242880)
            self.assertEqual(config.backup_count, 10)
    
    def test_config_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
logging:
  level: WARNING
  format_type: simple
  console_output: false
  file_output: true
  max_file_size: 20971520
  backup_count: 7
  environment: production
"""
        
        with open(self.config_file, 'w') as f:
            f.write(yaml_content)
        
        config = LoggingConfig.from_file(self.config_file)
        
        self.assertEqual(config.level, "WARNING")
        self.assertEqual(config.format_type, "simple")
        self.assertFalse(config.console_output)
        self.assertTrue(config.file_output)
        self.assertEqual(config.max_file_size, 20971520)
        self.assertEqual(config.backup_count, 7)
        self.assertEqual(config.environment, "production")
    
    def test_config_from_json_file(self):
        """Test loading configuration from JSON file."""
        json_file = Path(self.temp_dir) / "test_config.json"
        json_content = {
            "logging": {
                "level": "DEBUG",
                "format_type": "structured",
                "console_output": True,
                "file_output": False,
                "environment": "testing"
            }
        }
        
        with open(json_file, 'w') as f:
            json.dump(json_content, f)
        
        config = LoggingConfig.from_file(json_file)
        
        self.assertEqual(config.level, "DEBUG")
        self.assertEqual(config.format_type, "structured")
        self.assertTrue(config.console_output)
        self.assertFalse(config.file_output)
        self.assertEqual(config.environment, "testing")
    
    def test_config_file_not_found(self):
        """Test handling of missing configuration file."""
        non_existent_file = Path(self.temp_dir) / "missing.yaml"
        
        with self.assertRaises(FileNotFoundError):
            LoggingConfig.from_file(non_existent_file)
    
    def test_config_for_environment_development(self):
        """Test environment-specific configuration for development."""
        config = LoggingConfig.for_environment("development")
        
        self.assertEqual(config.level, "DEBUG")
        self.assertEqual(config.format_type, "simple")
        self.assertTrue(config.console_output)
        self.assertTrue(config.file_output)
        self.assertTrue(config.enable_performance_logging)
        self.assertFalse(config.enable_async_logging)
    
    def test_config_for_environment_testing(self):
        """Test environment-specific configuration for testing."""
        config = LoggingConfig.for_environment("testing")
        
        self.assertEqual(config.level, "WARNING")
        self.assertEqual(config.format_type, "simple")
        self.assertFalse(config.console_output)
        self.assertFalse(config.file_output)
        self.assertFalse(config.enable_performance_logging)
        self.assertFalse(config.enable_async_logging)
    
    def test_config_for_environment_production(self):
        """Test environment-specific configuration for production."""
        config = LoggingConfig.for_environment("production")
        
        self.assertEqual(config.level, "INFO")
        self.assertEqual(config.format_type, "structured")
        self.assertFalse(config.console_output)
        self.assertTrue(config.file_output)
        self.assertTrue(config.enable_performance_logging)
        self.assertTrue(config.enable_async_logging)
        self.assertEqual(config.max_file_size, 50 * 1024 * 1024)
        self.assertEqual(config.backup_count, 10)
    
    def test_config_to_dict(self):
        """Test converting configuration to dictionary."""
        config = LoggingConfig(
            level="INFO",
            format_type="structured",
            log_directory=Path("/tmp/logs")
        )
        
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict['level'], "INFO")
        self.assertEqual(config_dict['format_type'], "structured")
        self.assertEqual(config_dict['log_directory'], "/tmp/logs")  # Path converted to string
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            config = get_default_config()
            self.assertEqual(config.environment, "production")
            self.assertEqual(config.level, "INFO")


class TestLogContext(unittest.TestCase):
    """Test LogContext and context management."""
    
    def setUp(self):
        """Set up test environment."""
        clear_context()  # Clear any existing context
    
    def tearDown(self):
        """Clean up test environment."""
        clear_context()
    
    def test_log_context_creation(self):
        """Test creating LogContext with required fields."""
        context = LogContext(
            component="trading",
            operation="buy_order",
            symbol="BTCUSDT",
            exchange="binance"
        )
        
        self.assertEqual(context.component, "trading")
        self.assertEqual(context.operation, "buy_order")
        self.assertEqual(context.symbol, "BTCUSDT")
        self.assertEqual(context.exchange, "binance")
        self.assertIsNotNone(context.request_id)  # Auto-generated
    
    def test_log_context_to_dict(self):
        """Test converting LogContext to dictionary."""
        context = LogContext(
            component="cli",
            operation="start",
            symbol="ETHUSDT"
        )
        
        context_dict = context.to_dict()
        
        self.assertEqual(context_dict['component'], "cli")
        self.assertEqual(context_dict['operation'], "start")
        self.assertEqual(context_dict['symbol'], "ETHUSDT")
        self.assertIn('request_id', context_dict)
        # None values should be excluded
        self.assertNotIn('exchange', context_dict)
    
    def test_log_context_update(self):
        """Test updating LogContext with new values."""
        original_context = LogContext(
            component="trading",
            operation="buy_order"
        )
        
        updated_context = original_context.update(
            symbol="BTCUSDT",
            exchange="binance"
        )
        
        # Original should be unchanged
        self.assertIsNone(original_context.symbol)
        self.assertIsNone(original_context.exchange)
        
        # Updated should have new values
        self.assertEqual(updated_context.symbol, "BTCUSDT")
        self.assertEqual(updated_context.exchange, "binance")
        self.assertEqual(updated_context.component, "trading")  # Preserved
        self.assertEqual(updated_context.operation, "buy_order")  # Preserved
    
    def test_log_context_convenience_methods(self):
        """Test LogContext convenience methods."""
        context = LogContext(component="trading", operation="order")
        
        # Test with_operation
        new_context = context.with_operation("cancel")
        self.assertEqual(new_context.operation, "cancel")
        self.assertEqual(new_context.component, "trading")
        
        # Test with_symbol
        new_context = context.with_symbol("ETHUSDT")
        self.assertEqual(new_context.symbol, "ETHUSDT")
        
        # Test with_exchange
        new_context = context.with_exchange("coinbase")
        self.assertEqual(new_context.exchange, "coinbase")
        
        # Test with_strategy
        new_context = context.with_strategy("momentum")
        self.assertEqual(new_context.strategy, "momentum")
        
        # Test with_trade_info
        new_context = context.with_trade_info(order_id="12345", trade_id="67890")
        self.assertEqual(new_context.order_id, "12345")
        self.assertEqual(new_context.trade_id, "67890")
    
    def test_context_manager_set_get_clear(self):
        """Test ContextManager set, get, and clear operations."""
        context = LogContext(component="test", operation="unit_test")
        
        # Initially no context
        self.assertIsNone(get_context())
        
        # Set context
        set_context(context)
        retrieved_context = get_context()
        self.assertIsNotNone(retrieved_context)
        self.assertEqual(retrieved_context.component, "test")
        self.assertEqual(retrieved_context.operation, "unit_test")
        
        # Clear context
        clear_context()
        self.assertIsNone(get_context())
    
    def test_context_manager_thread_safety(self):
        """Test that context is thread-local."""
        results = {}
        
        def set_context_in_thread(thread_id):
            context = LogContext(component=f"thread_{thread_id}", operation="test")
            set_context(context)
            time.sleep(0.1)  # Allow other threads to run
            retrieved_context = get_context()
            results[thread_id] = retrieved_context.component if retrieved_context else None
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=set_context_in_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Each thread should have its own context
        self.assertEqual(results[0], "thread_0")
        self.assertEqual(results[1], "thread_1")
        self.assertEqual(results[2], "thread_2")
    
    def test_context_scope_manager(self):
        """Test context scope manager."""
        from genebot.logging.context import context_scope
        
        # Set initial context
        initial_context = LogContext(component="initial", operation="setup")
        set_context(initial_context)
        
        # Use scope manager
        scope_context = LogContext(component="scope", operation="test")
        with context_scope(scope_context):
            current_context = get_context()
            self.assertEqual(current_context.component, "scope")
            self.assertEqual(current_context.operation, "test")
        
        # Should restore previous context
        restored_context = get_context()
        self.assertEqual(restored_context.component, "initial")
        self.assertEqual(restored_context.operation, "setup")
    
    def test_convenience_context_functions(self):
        """Test convenience functions for creating contexts."""
        # Test trading_context
        trading_ctx = trading_context("BTCUSDT", "binance", "momentum")
        self.assertEqual(trading_ctx.component, "trading")
        self.assertEqual(trading_ctx.operation, "execution")
        self.assertEqual(trading_ctx.symbol, "BTCUSDT")
        self.assertEqual(trading_ctx.exchange, "binance")
        self.assertEqual(trading_ctx.strategy, "momentum")
        
        # Test cli_context
        cli_ctx = cli_context("start", "bot")
        self.assertEqual(cli_ctx.component, "cli")
        self.assertEqual(cli_ctx.operation, "start.bot")
        
        cli_ctx_simple = cli_context("status")
        self.assertEqual(cli_ctx_simple.component, "cli")
        self.assertEqual(cli_ctx_simple.operation, "status")
        
        # Test monitoring_context
        monitoring_ctx = monitoring_context("performance")
        self.assertEqual(monitoring_ctx.component, "monitoring")
        self.assertEqual(monitoring_ctx.operation, "performance")
        
        # Test error_context
        error_ctx = error_context("validation", "config")
        self.assertEqual(error_ctx.component, "config")
        self.assertEqual(error_ctx.operation, "error.validation")


class TestLoggerFactory(unittest.TestCase):
    """Test LoggerFactory creation and caching."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset factory singleton for testing
        LoggerFactory._instance = None
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        # Reset factory singleton
        LoggerFactory._instance = None
    
    def test_factory_singleton_pattern(self):
        """Test that LoggerFactory implements singleton pattern."""
        factory1 = LoggerFactory()
        factory2 = LoggerFactory()
        
        self.assertIs(factory1, factory2)
    
    def test_factory_setup_global_config(self):
        """Test setting up global configuration."""
        factory = LoggerFactory()
        config = LoggingConfig(
            level="DEBUG",
            console_output=False,
            file_output=False,  # Disable file output for testing
            log_directory=Path(self.temp_dir)
        )
        
        # Should not raise any exceptions
        factory.setup_global_config(config)
        self.assertTrue(factory._configured)
        self.assertEqual(factory._config, config)
    
    def test_factory_get_logger_basic(self):
        """Test getting basic logger from factory."""
        factory = LoggerFactory()
        config = LoggingConfig(
            console_output=False,
            file_output=False,  # Disable file output for testing
            log_directory=Path(self.temp_dir)
        )
        factory.setup_global_config(config)
        
        logger = factory.get_logger("test.logger")
        
        self.assertIsInstance(logger, ContextualLogger)
        self.assertEqual(logger.logger.name, "test.logger")
    
    def test_factory_get_logger_with_context(self):
        """Test getting logger with default context."""
        factory = LoggerFactory()
        config = LoggingConfig(
            console_output=False,
            file_output=False,
            log_directory=Path(self.temp_dir)
        )
        factory.setup_global_config(config)
        
        context = LogContext(component="test", operation="unit_test")
        logger = factory.get_logger("test.logger", context=context)
        
        self.assertIsInstance(logger, ContextualLogger)
        self.assertEqual(logger.default_context, context)
    
    def test_factory_logger_caching(self):
        """Test that factory caches loggers properly."""
        factory = LoggerFactory()
        config = LoggingConfig(
            console_output=False,
            file_output=False,
            log_directory=Path(self.temp_dir)
        )
        factory.setup_global_config(config)
        
        logger1 = factory.get_logger("test.logger")
        logger2 = factory.get_logger("test.logger")
        
        # Should return the same cached instance
        self.assertIs(logger1, logger2)
    
    def test_factory_logger_caching_with_different_contexts(self):
        """Test that factory creates different instances for different contexts."""
        factory = LoggerFactory()
        config = LoggingConfig(
            console_output=False,
            file_output=False,
            log_directory=Path(self.temp_dir)
        )
        factory.setup_global_config(config)
        
        context1 = LogContext(component="test1", operation="op1")
        context2 = LogContext(component="test2", operation="op2")
        
        logger1 = factory.get_logger("test.logger", context=context1)
        logger2 = factory.get_logger("test.logger", context=context2)
        
        # Should be different instances due to different contexts
        self.assertIsNot(logger1, logger2)
    
    def test_factory_get_specialized_loggers(self):
        """Test getting specialized loggers from factory."""
        factory = LoggerFactory()
        config = LoggingConfig(
            console_output=False,
            file_output=False,
            log_directory=Path(self.temp_dir)
        )
        factory.setup_global_config(config)
        
        # Test TradeLogger
        trade_logger = factory.get_trade_logger()
        self.assertIsInstance(trade_logger, TradeLogger)
        self.assertEqual(trade_logger.logger.name, "genebot.trades")
        
        # Test PerformanceLogger
        perf_logger = factory.get_performance_logger()
        self.assertIsInstance(perf_logger, PerformanceLogger)
        self.assertEqual(perf_logger.logger.name, "genebot.performance")
        
        # Test ErrorLogger
        error_logger = factory.get_error_logger()
        self.assertIsInstance(error_logger, ErrorLogger)
        self.assertEqual(error_logger.logger.name, "genebot.errors")
        
        # Test CLILogger
        cli_logger = factory.get_cli_logger(verbose=True)
        self.assertIsInstance(cli_logger, CLILogger)
        self.assertEqual(cli_logger.logger.name, "genebot.cli")
        self.assertTrue(cli_logger.verbose)
    
    def test_factory_auto_configuration(self):
        """Test that factory auto-configures with default config if not configured."""
        factory = LoggerFactory()
        
        # Should auto-configure when getting logger
        logger = factory.get_logger("test.logger")
        
        self.assertIsInstance(logger, ContextualLogger)
        self.assertTrue(factory._configured)
        self.assertIsNotNone(factory._config)


class TestContextualLogger(unittest.TestCase):
    """Test ContextualLogger functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_logger.name = "test.logger"
        self.mock_logger.isEnabledFor.return_value = True
        self.context = LogContext(component="test", operation="unit_test")
    
    def test_contextual_logger_creation(self):
        """Test creating ContextualLogger."""
        logger = ContextualLogger(self.mock_logger, self.context)
        
        self.assertEqual(logger.logger, self.mock_logger)
        self.assertEqual(logger.default_context, self.context)
    
    def test_contextual_logger_log_methods(self):
        """Test ContextualLogger log methods."""
        logger = ContextualLogger(self.mock_logger, enable_optimization=False)
        
        # Test each log level
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Verify calls were made
        self.assertEqual(self.mock_logger.log.call_count, 5)
        
        # Check the calls
        calls = self.mock_logger.log.call_args_list
        self.assertEqual(calls[0][0], (logging.DEBUG, "Debug message"))
        self.assertEqual(calls[1][0], (logging.INFO, "Info message"))
        self.assertEqual(calls[2][0], (logging.WARNING, "Warning message"))
        self.assertEqual(calls[3][0], (logging.ERROR, "Error message"))
        self.assertEqual(calls[4][0], (logging.CRITICAL, "Critical message"))
    
    def test_contextual_logger_with_context(self):
        """Test logging with context information."""
        logger = ContextualLogger(self.mock_logger, enable_optimization=False)
        
        context = LogContext(component="trading", operation="buy")
        logger.info("Trade executed", context=context)
        
        # Verify context was added to extra
        call_args = self.mock_logger.log.call_args
        self.assertIn('extra', call_args[1])
        self.assertIn('context', call_args[1]['extra'])
        self.assertEqual(call_args[1]['extra']['context'], context)
    
    def test_contextual_logger_exception_logging(self):
        """Test exception logging."""
        logger = ContextualLogger(self.mock_logger, enable_optimization=False)
        
        logger.exception("An error occurred")
        
        # Verify exception logging
        call_args = self.mock_logger.log.call_args
        self.assertEqual(call_args[0][0], logging.ERROR)
        self.assertEqual(call_args[1]['exc_info'], True)
    
    def test_contextual_logger_with_context_method(self):
        """Test creating logger with specific context."""
        logger = ContextualLogger(self.mock_logger)
        context = LogContext(component="test", operation="specific")
        
        context_logger = logger.with_context(context)
        
        self.assertIsInstance(context_logger, ContextualLogger)
        self.assertEqual(context_logger.default_context, context)
        self.assertEqual(context_logger.logger, self.mock_logger)


class TestSpecializedLoggers(unittest.TestCase):
    """Test specialized logger classes."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_logger = Mock(spec=logging.Logger)
        self.mock_logger.name = "test.logger"
    
    def test_trade_logger_methods(self):
        """Test TradeLogger specialized methods."""
        trade_logger = TradeLogger(self.mock_logger)
        
        # Test trade_opened
        trade_logger.trade_opened("BTCUSDT", "BUY", 1.0, 50000.0)
        
        # Verify call
        call_args = trade_logger.logger.info.call_args
        self.assertIn("Trade opened", call_args[0][0])
        self.assertIn('extra', call_args[1])
        extra = call_args[1]['extra']
        self.assertEqual(extra['trade_event'], 'opened')
        self.assertEqual(extra['symbol'], 'BTCUSDT')
        self.assertEqual(extra['side'], 'BUY')
        self.assertEqual(extra['quantity'], 1.0)
        self.assertEqual(extra['price'], 50000.0)
        
        # Test trade_closed
        trade_logger.trade_closed("BTCUSDT", "SELL", 1.0, 51000.0, pnl=1000.0)
        
        call_args = trade_logger.logger.info.call_args
        self.assertIn("Trade closed", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['trade_event'], 'closed')
        self.assertEqual(extra['pnl'], 1000.0)
        
        # Test order_placed
        trade_logger.order_placed("12345", "ETHUSDT", "BUY", 2.0, "LIMIT")
        
        call_args = trade_logger.logger.info.call_args
        self.assertIn("Order placed", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['trade_event'], 'order_placed')
        self.assertEqual(extra['order_id'], '12345')
        
        # Test order_filled
        trade_logger.order_filled("12345", "ETHUSDT", 2.0, 3000.0)
        
        call_args = trade_logger.logger.info.call_args
        self.assertIn("Order filled", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['trade_event'], 'order_filled')
        self.assertEqual(extra['filled_quantity'], 2.0)
    
    def test_performance_logger_methods(self):
        """Test PerformanceLogger specialized methods."""
        perf_logger = PerformanceLogger(self.mock_logger)
        
        # Test execution_time
        perf_logger.execution_time("database_query", 150.5)
        
        call_args = perf_logger.logger.info.call_args
        self.assertIn("Performance", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['metric_type'], 'execution_time')
        self.assertEqual(extra['operation'], 'database_query')
        self.assertEqual(extra['duration_ms'], 150.5)
        
        # Test memory_usage
        perf_logger.memory_usage("trading_engine", 256.7)
        
        call_args = perf_logger.logger.info.call_args
        self.assertIn("Memory", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['metric_type'], 'memory_usage')
        self.assertEqual(extra['component'], 'trading_engine')
        self.assertEqual(extra['memory_mb'], 256.7)
        
        # Test throughput
        perf_logger.throughput("order_processing", 1000, 60.0)
        
        call_args = perf_logger.logger.info.call_args
        self.assertIn("Throughput", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['metric_type'], 'throughput')
        self.assertEqual(extra['count'], 1000)
        self.assertEqual(extra['duration_s'], 60.0)
        self.assertAlmostEqual(extra['rate'], 16.67, places=2)
        
        # Test resource_usage
        perf_logger.resource_usage(cpu_percent=75.5, memory_mb=512.0)
        
        call_args = perf_logger.logger.info.call_args
        self.assertIn("Resources", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['metric_type'], 'resource_usage')
        self.assertEqual(extra['cpu_percent'], 75.5)
        self.assertEqual(extra['memory_mb'], 512.0)
    
    def test_error_logger_methods(self):
        """Test ErrorLogger specialized methods."""
        error_logger = ErrorLogger(self.mock_logger)
        
        # Test error_occurred
        error_logger.error_occurred("ValidationError", "Invalid symbol", "trading")
        
        call_args = error_logger.logger.error.call_args
        self.assertIn("Error in trading", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['error_type'], 'ValidationError')
        self.assertEqual(extra['error_message'], 'Invalid symbol')
        self.assertEqual(extra['component'], 'trading')
        
        # Test exception_caught
        test_exception = ValueError("Test error")
        error_logger.exception_caught(test_exception, "config", "load_settings")
        
        call_args = error_logger.logger.exception.call_args
        self.assertIn("Exception in config.load_settings", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['exception_type'], 'ValueError')
        self.assertEqual(extra['exception_message'], 'Test error')
        self.assertEqual(extra['component'], 'config')
        self.assertEqual(extra['operation'], 'load_settings')
        
        # Test validation_error
        error_logger.validation_error("symbol", "INVALID", "Symbol not supported")
        
        call_args = error_logger.logger.error.call_args
        self.assertIn("Validation error", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['error_type'], 'validation')
        self.assertEqual(extra['field'], 'symbol')
        self.assertEqual(extra['value'], 'INVALID')
        self.assertEqual(extra['reason'], 'Symbol not supported')
    
    def test_cli_logger_methods(self):
        """Test CLILogger specialized methods."""
        cli_logger = CLILogger(self.mock_logger, verbose=True)
        
        # Test command_start
        cli_logger.command_start("start", {"symbol": "BTCUSDT"})
        
        call_args = cli_logger.logger.info.call_args
        self.assertIn("Executing command: start", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['cli_event'], 'command_start')
        self.assertEqual(extra['command'], 'start')
        self.assertEqual(extra['command_args'], {"symbol": "BTCUSDT"})
        
        # Test command_success
        cli_logger.command_success("start", "Bot started successfully")
        
        call_args = cli_logger.logger.info.call_args
        self.assertIn("Command completed successfully", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['cli_event'], 'command_success')
        self.assertEqual(extra['result'], 'Bot started successfully')
        
        # Test command_error
        cli_logger.command_error("start", "Configuration not found")
        
        call_args = cli_logger.logger.error.call_args
        self.assertIn("Command failed", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['cli_event'], 'command_error')
        self.assertEqual(extra['error'], 'Configuration not found')
        
        # Test progress
        cli_logger.progress("Processing orders", 50, 100)
        
        call_args = cli_logger.logger.info.call_args
        self.assertIn("Progress: Processing orders", call_args[0][0])
        self.assertIn("(50/100 - 50.0%)", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['cli_event'], 'progress')
        self.assertEqual(extra['current'], 50)
        self.assertEqual(extra['total'], 100)
        
        # Test user_info with verbose
        cli_logger.user_info("System ready")
        
        call_args = cli_logger.logger.info.call_args
        self.assertIn("Info: System ready", call_args[0][0])
        extra = call_args[1]['extra']
        self.assertEqual(extra['cli_event'], 'user_info')


if __name__ == '__main__':
    unittest.main()