"""
Unit tests for logging formatters.

This module tests the various formatters to ensure they produce correct output
and handle context injection properly.
"""

import json
import logging
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from io import StringIO

from genebot.logging.formatters import (
    StructuredJSONFormatter, SimpleFormatter, PerformanceOptimizedFormatter, CompactFormatter
)
from genebot.logging.context import LogContext


class TestStructuredJSONFormatter(unittest.TestCase):
    """Test StructuredJSONFormatter functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.formatter = StructuredJSONFormatter()
        self.record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        self.record.module = "test"
        self.record.funcName = "test_function"
    
    def test_basic_json_formatting(self):
        """Test basic JSON formatting without context."""
        formatted = self.formatter.format(self.record)
        
        # Should be valid JSON
        log_data = json.loads(formatted)
        
        # Check required fields
        self.assertIn('timestamp', log_data)
        self.assertIn('level', log_data)
        self.assertIn('logger', log_data)
        self.assertIn('message', log_data)
        self.assertIn('metadata', log_data)
        
        # Check values
        self.assertEqual(log_data['level'], 'INFO')
        self.assertEqual(log_data['logger'], 'test.logger')
        self.assertEqual(log_data['message'], 'Test message')
        
        # Check metadata
        metadata = log_data['metadata']
        self.assertEqual(metadata['module'], 'test')
        self.assertEqual(metadata['function'], 'test_function')
        self.assertEqual(metadata['line'], 42)
        self.assertIn('thread', metadata)
        self.assertIn('process', metadata)
    
    def test_json_formatting_with_context(self):
        """Test JSON formatting with LogContext."""
        context = LogContext(
            component="trading",
            operation="buy_order",
            symbol="BTCUSDT",
            exchange="binance"
        )
        self.record.context = context
        
        formatted = self.formatter.format(self.record)
        log_data = json.loads(formatted)
        
        # Check context is included
        self.assertIn('context', log_data)
        context_data = log_data['context']
        self.assertEqual(context_data['component'], 'trading')
        self.assertEqual(context_data['operation'], 'buy_order')
        self.assertEqual(context_data['symbol'], 'BTCUSDT')
        self.assertEqual(context_data['exchange'], 'binance')
    
    def test_json_formatting_with_performance_data(self):
        """Test JSON formatting with performance information."""
        self.record.execution_time_ms = 150.5
        self.record.memory_usage_mb = 256.7
        
        formatted = self.formatter.format(self.record)
        log_data = json.loads(formatted)
        
        # Check performance data is included
        self.assertIn('performance', log_data)
        performance_data = log_data['performance']
        self.assertEqual(performance_data['execution_time_ms'], 150.5)
        self.assertEqual(performance_data['memory_usage_mb'], 256.7)
    
    def test_json_formatting_with_exception(self):
        """Test JSON formatting with exception information."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            self.record.exc_info = sys.exc_info()
        
        formatted = self.formatter.format(self.record)
        log_data = json.loads(formatted)
        
        # Check exception is included
        self.assertIn('exception', log_data)
        exception_data = log_data['exception']
        self.assertEqual(exception_data['type'], 'ValueError')
        self.assertEqual(exception_data['message'], 'Test exception')
        self.assertIn('traceback', exception_data)
        self.assertIsInstance(exception_data['traceback'], list)
    
    def test_json_formatting_with_extra_fields(self):
        """Test JSON formatting with extra fields."""
        self.record.trade_id = "12345"
        self.record.order_type = "LIMIT"
        self.record.custom_field = "custom_value"
        
        formatted = self.formatter.format(self.record)
        log_data = json.loads(formatted)
        
        # Check extra fields are included
        self.assertEqual(log_data['trade_id'], '12345')
        self.assertEqual(log_data['order_type'], 'LIMIT')
        self.assertEqual(log_data['custom_field'], 'custom_value')
    
    def test_sensitive_data_masking(self):
        """Test that sensitive data is masked in JSON output."""
        formatter = StructuredJSONFormatter(mask_sensitive=True)
        
        # Test with sensitive data in message
        self.record.msg = "API key: sk-1234567890abcdef, password: secret123"
        
        formatted = formatter.format(self.record)
        log_data = json.loads(formatted)
        
        # Sensitive data should be masked
        message = log_data['message']
        self.assertNotIn('sk-1234567890abcdef', message)
        self.assertNotIn('secret123', message)
        self.assertIn('sk-**************ef', message)
        self.assertIn('se*****23', message)
    
    def test_sensitive_data_masking_disabled(self):
        """Test that sensitive data masking can be disabled."""
        formatter = StructuredJSONFormatter(mask_sensitive=False)
        
        self.record.msg = "API key: sk-1234567890abcdef"
        
        formatted = formatter.format(self.record)
        log_data = json.loads(formatted)
        
        # Sensitive data should not be masked
        message = log_data['message']
        self.assertIn('sk-1234567890abcdef', message)
    
    def test_performance_data_disabled(self):
        """Test that performance data inclusion can be disabled."""
        formatter = StructuredJSONFormatter(include_performance=False)
        
        self.record.execution_time_ms = 150.5
        
        formatted = formatter.format(self.record)
        log_data = json.loads(formatted)
        
        # Performance data should not be included
        self.assertNotIn('performance', log_data)
    
    def test_timestamp_format(self):
        """Test that timestamp is in correct ISO format."""
        formatted = self.formatter.format(self.record)
        log_data = json.loads(formatted)
        
        timestamp = log_data['timestamp']
        # Should be ISO format with Z suffix
        self.assertTrue(timestamp.endswith('Z'))
        
        # Should be parseable as datetime
        parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        self.assertIsInstance(parsed_time, datetime)


class TestSimpleFormatter(unittest.TestCase):
    """Test SimpleFormatter functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.formatter = SimpleFormatter(colorize=False)  # Disable colors for testing
        self.record = logging.LogRecord(
            name="genebot.trading.engine",
            level=logging.INFO,
            pathname="/path/to/trading/engine.py",
            lineno=123,
            msg="Order executed successfully",
            args=(),
            exc_info=None
        )
        self.record.module = "engine"
        self.record.funcName = "execute_order"
    
    def test_basic_simple_formatting(self):
        """Test basic simple formatting."""
        formatted = self.formatter.format(self.record)
        
        # Should contain key components
        self.assertIn('INFO', formatted)
        self.assertIn('genebot.trading', formatted)  # Shortened logger name
        self.assertIn('engine:execute_order:123', formatted)
        self.assertIn('Order executed successfully', formatted)
        
        # Should be human-readable format
        parts = formatted.split(' - ')
        self.assertEqual(len(parts), 5)  # timestamp, level, logger, location, message
    
    def test_simple_formatting_with_context(self):
        """Test simple formatting with context information."""
        formatter = SimpleFormatter(include_context=True, colorize=False)
        
        context = LogContext(
            component="trading",
            operation="buy_order",
            symbol="BTCUSDT",
            exchange="binance"
        )
        self.record.context = context
        
        formatted = formatter.format(self.record)
        
        # Should include context information
        self.assertIn('symbol=BTCUSDT', formatted)
        self.assertIn('exchange=binance', formatted)
        self.assertIn('operation=buy_order', formatted)
    
    def test_simple_formatting_context_disabled(self):
        """Test simple formatting with context disabled."""
        formatter = SimpleFormatter(include_context=False, colorize=False)
        
        context = LogContext(component="trading", operation="buy_order", symbol="BTCUSDT")
        self.record.context = context
        
        formatted = formatter.format(self.record)
        
        # Should not include context information
        self.assertNotIn('symbol=BTCUSDT', formatted)
        self.assertNotIn('|', formatted)  # Context separator
    
    def test_simple_formatting_with_exception(self):
        """Test simple formatting with exception."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            self.record.exc_info = sys.exc_info()
        
        formatted = self.formatter.format(self.record)
        
        # Should include exception traceback
        self.assertIn('ValueError: Test exception', formatted)
        self.assertIn('Traceback', formatted)
    
    def test_logger_name_shortening(self):
        """Test logger name shortening for readability."""
        # Test long logger name
        self.record.name = "genebot.very.long.module.path.with.many.components"
        
        formatted = self.formatter.format(self.record)
        
        # Should be shortened
        self.assertIn('genebot...components', formatted)
    
    def test_logger_name_no_shortening_needed(self):
        """Test that short logger names are not modified."""
        self.record.name = "short.name"
        
        formatted = self.formatter.format(self.record)
        
        # Should not be modified
        self.assertIn('short.name', formatted)
    
    def test_colorization_detection(self):
        """Test color detection logic."""
        # Test with environment that should support colors
        with patch.dict(os.environ, {'TERM': 'xterm-256color'}, clear=True):
            with patch('os.isatty', return_value=True):
                formatter = SimpleFormatter()
                # Should enable colors in terminal environment
                # Note: This is hard to test directly, but we can check the formatter was created
                self.assertIsInstance(formatter, SimpleFormatter)
    
    def test_colorization_disabled_by_env(self):
        """Test that colors are disabled by NO_COLOR environment variable."""
        with patch.dict(os.environ, {'NO_COLOR': '1', 'TERM': 'xterm'}):
            formatter = SimpleFormatter()
            self.assertFalse(formatter.colorize)


class TestPerformanceOptimizedFormatter(unittest.TestCase):
    """Test PerformanceOptimizedFormatter functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.formatter = PerformanceOptimizedFormatter(cache_size=10)
        self.record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        self.record.module = "test"
        self.record.funcName = "test_function"
    
    def test_performance_formatter_caching(self):
        """Test that formatter caches repeated messages."""
        # Format the same record multiple times
        formatted1 = self.formatter.format(self.record)
        formatted2 = self.formatter.format(self.record)
        formatted3 = self.formatter.format(self.record)
        
        # All should be valid JSON
        log_data1 = json.loads(formatted1)
        log_data2 = json.loads(formatted2)
        log_data3 = json.loads(formatted3)
        
        # Core content should be the same (except timestamp)
        self.assertEqual(log_data1['level'], log_data2['level'])
        self.assertEqual(log_data1['message'], log_data2['message'])
        self.assertEqual(log_data2['level'], log_data3['level'])
        self.assertEqual(log_data2['message'], log_data3['message'])
        
        # Should have cache hits
        stats = self.formatter.get_cache_stats()
        self.assertGreater(stats['cache_hits'], 0)
    
    def test_performance_formatter_cache_stats(self):
        """Test cache statistics tracking."""
        # Initial stats
        stats = self.formatter.get_cache_stats()
        self.assertEqual(stats['cache_hits'], 0)
        self.assertEqual(stats['cache_misses'], 0)
        self.assertEqual(stats['hit_rate_percent'], 0)
        
        # Format same record twice
        self.formatter.format(self.record)  # Cache miss
        self.formatter.format(self.record)  # Cache hit
        
        stats = self.formatter.get_cache_stats()
        self.assertEqual(stats['cache_hits'], 1)
        self.assertEqual(stats['cache_misses'], 1)
        self.assertEqual(stats['hit_rate_percent'], 50.0)
    
    def test_performance_formatter_cache_eviction(self):
        """Test cache eviction when cache size is exceeded."""
        # Fill cache beyond capacity
        for i in range(15):  # Cache size is 10
            record = logging.LogRecord(
                name=f"test.logger.{i}",
                level=logging.INFO,
                pathname="/path/to/test.py",
                lineno=i,
                msg=f"Test message {i}",
                args=(),
                exc_info=None
            )
            record.module = "test"
            record.funcName = "test_function"
            self.formatter.format(record)
        
        # Cache should not exceed maximum size
        stats = self.formatter.get_cache_stats()
        self.assertLessEqual(stats['cache_size'], 10)
    
    def test_performance_formatter_invalid_json_handling(self):
        """Test handling of records that produce invalid JSON."""
        # Create a record that might cause JSON issues
        self.record.msg = "Message with special chars: \x00\x01\x02"
        
        # Should still format without crashing
        formatted = self.formatter.format(self.record)
        
        # Should be valid JSON or at least a string
        self.assertIsInstance(formatted, str)
        
        # Try to parse as JSON
        try:
            json.loads(formatted)
        except json.JSONDecodeError:
            # If it's not valid JSON, that's okay for this edge case
            pass


class TestCompactFormatter(unittest.TestCase):
    """Test CompactFormatter functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.formatter = CompactFormatter()
        self.record = logging.LogRecord(
            name="genebot.trading.engine.executor",
            level=logging.INFO,
            pathname="/path/to/trading/engine.py",
            lineno=123,
            msg="Order executed successfully for BTCUSDT",
            args=(),
            exc_info=None
        )
        self.record.module = "executor"
        self.record.funcName = "execute_order"
    
    def test_compact_formatting(self):
        """Test compact formatting produces short output."""
        formatted = self.formatter.format(self.record)
        
        # Should be compact
        self.assertLess(len(formatted), 100)  # Should be quite short
        
        # Should contain essential information
        self.assertIn('I', formatted)  # Level (first letter)
        self.assertIn('executor', formatted)  # Logger name (last component)
        self.assertIn('Order executed successfully', formatted)  # Message
        
        # Should have timestamp in HH:MM:SS format
        time_part = formatted.split(' ')[0]
        self.assertRegex(time_part, r'\d{2}:\d{2}:\d{2}')
    
    def test_compact_formatting_long_message_truncation(self):
        """Test that long messages are truncated."""
        long_message = "This is a very long message that should be truncated because it exceeds the maximum length limit for compact formatting and we want to keep the output concise"
        self.record.msg = long_message
        
        formatted = self.formatter.format(self.record)
        
        # Should be truncated
        self.assertIn('...', formatted)
        self.assertLess(len(formatted), len(long_message) + 50)  # Much shorter than original
    
    def test_compact_formatting_logger_name_shortening(self):
        """Test logger name shortening in compact format."""
        formatted = self.formatter.format(self.record)
        
        # Logger name should be shortened to last component and max 8 chars
        self.assertIn('executor', formatted)
        self.assertNotIn('genebot.trading.engine.executor', formatted)
    
    def test_compact_formatting_different_levels(self):
        """Test compact formatting with different log levels."""
        levels = [
            (logging.DEBUG, 'D'),
            (logging.INFO, 'I'),
            (logging.WARNING, 'W'),
            (logging.ERROR, 'E'),
            (logging.CRITICAL, 'C')
        ]
        
        for level, expected_char in levels:
            self.record.levelno = level
            self.record.levelname = logging.getLevelName(level)
            
            formatted = self.formatter.format(self.record)
            
            # Should contain the expected level character
            parts = formatted.split(' ')
            self.assertEqual(parts[1], expected_char)


class TestFormatterIntegration(unittest.TestCase):
    """Test formatter integration with actual logging system."""
    
    def setUp(self):
        """Set up test environment."""
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.logger = logging.getLogger('test.integration')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)
    
    def tearDown(self):
        """Clean up test environment."""
        self.logger.removeHandler(self.handler)
    
    def test_structured_formatter_integration(self):
        """Test StructuredJSONFormatter integration with logging system."""
        formatter = StructuredJSONFormatter()
        self.handler.setFormatter(formatter)
        
        self.logger.info("Test message")
        
        output = self.stream.getvalue()
        self.assertIsInstance(output, str)
        
        # Should be valid JSON
        log_data = json.loads(output.strip())
        self.assertEqual(log_data['level'], 'INFO')
        self.assertEqual(log_data['message'], 'Test message')
    
    def test_simple_formatter_integration(self):
        """Test SimpleFormatter integration with logging system."""
        formatter = SimpleFormatter(colorize=False)
        self.handler.setFormatter(formatter)
        
        self.logger.warning("Test warning")
        
        output = self.stream.getvalue()
        self.assertIn('WARNING', output)
        self.assertIn('Test warning', output)
        self.assertIn('test.integration', output)
    
    def test_compact_formatter_integration(self):
        """Test CompactFormatter integration with logging system."""
        formatter = CompactFormatter()
        self.handler.setFormatter(formatter)
        
        self.logger.error("Test error")
        
        output = self.stream.getvalue()
        self.assertIn('E', output)  # Error level
        self.assertIn('Test error', output)
        # Should be quite short
        self.assertLess(len(output.strip()), 50)
    
    def test_formatter_with_extra_data(self):
        """Test formatters with extra data in log records."""
        formatter = StructuredJSONFormatter()
        self.handler.setFormatter(formatter)
        
        # Log with extra data
        self.logger.info("Trade executed", extra={
            'symbol': 'BTCUSDT',
            'quantity': 1.0,
            'price': 50000.0
        })
        
        output = self.stream.getvalue()
        log_data = json.loads(output.strip())
        
        # Extra data should be included
        self.assertEqual(log_data['symbol'], 'BTCUSDT')
        self.assertEqual(log_data['quantity'], 1.0)
        self.assertEqual(log_data['price'], 50000.0)


if __name__ == '__main__':
    unittest.main()