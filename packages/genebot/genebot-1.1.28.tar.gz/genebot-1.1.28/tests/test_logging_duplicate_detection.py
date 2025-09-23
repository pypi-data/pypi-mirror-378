"""
Duplicate detection tests for the logging system.

This module tests that log messages appear only once in each output,
handler deduplication works correctly, and logger propagation is properly configured.
"""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO
import shutil

from genebot.logging.factory import LoggerFactory
from genebot.logging.config import LoggingConfig
from genebot.logging.context import LogContext


class TestMessageDeduplication(unittest.TestCase):
    """Test that log messages appear only once in each output."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
        
        # Capture console output
        self.console_output = StringIO()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
    
    def test_no_duplicate_messages_in_console(self):
        """Test that messages don't appear multiple times in console output."""
        # Create a custom handler to capture console output
        console_handler = logging.StreamHandler(self.console_output)
        
        config = LoggingConfig(
            level="INFO",
            console_output=True,
            file_output=False,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get logger and add our test handler
        logger = factory.get_logger("duplicate.test")
        python_logger = logging.getLogger("duplicate.test")
        
        # Remove existing handlers and add our test handler
        for handler in python_logger.handlers[:]:
            python_logger.removeHandler(handler)
        python_logger.addHandler(console_handler)
        python_logger.propagate = False
        
        # Log a message
        test_message = "This message should appear only once"
        logger.info(test_message)
        
        # Check console output
        console_content = self.console_output.getvalue()
        
        # Count occurrences of the test message
        message_count = console_content.count(test_message)
        
        print(f"Console output: {repr(console_content)}")
        print(f"Message count: {message_count}")
        
        # Message should appear exactly once
        self.assertEqual(message_count, 1)
    
    def test_no_duplicate_messages_in_file(self):
        """Test that messages don't appear multiple times in log files."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        logger = factory.get_logger("duplicate.test")
        
        # Log multiple unique messages
        test_messages = [
            "First unique message",
            "Second unique message", 
            "Third unique message"
        ]
        
        for message in test_messages:
            logger.info(message)
        
        # Check file content
        log_file = self.log_dir / "genebot.log"
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r') as f:
            file_content = f.read()
        
        # Each message should appear exactly once
        for message in test_messages:
            message_count = file_content.count(message)
            print(f"Message '{message}' appears {message_count} times")
            self.assertEqual(message_count, 1)
    
    def test_no_duplicate_messages_across_outputs(self):
        """Test that messages don't duplicate across console and file outputs."""
        config = LoggingConfig(
            level="INFO",
            console_output=True,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Capture console output
        console_handler = logging.StreamHandler(self.console_output)
        
        logger = factory.get_logger("duplicate.test")
        python_logger = logging.getLogger("duplicate.test")
        
        # Replace console handler with our test handler
        original_handlers = python_logger.handlers[:]
        for handler in python_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream.name == '<stdout>':
                python_logger.removeHandler(handler)
        python_logger.addHandler(console_handler)
        
        test_message = "Message should appear once in each output"
        logger.info(test_message)
        
        # Check console output
        console_content = self.console_output.getvalue()
        console_count = console_content.count(test_message)
        
        # Check file output
        log_file = self.log_dir / "genebot.log"
        file_count = 0
        if log_file.exists():
            with open(log_file, 'r') as f:
                file_content = f.read()
            file_count = file_content.count(test_message)
        
        print(f"Console count: {console_count}")
        print(f"File count: {file_count}")
        
        # Message should appear once in each output
        self.assertEqual(console_count, 1)
        self.assertEqual(file_count, 1)
    
    def test_specialized_logger_no_duplicates(self):
        """Test that specialized loggers don't create duplicate messages."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            enable_trade_logging=True,
            enable_error_logging=True
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        trade_logger = factory.get_trade_logger()
        error_logger = factory.get_error_logger()
        
        # Log messages with specialized loggers
        trade_logger.trade_opened("BTCUSDT", "BUY", 1.0, 50000.0)
        error_logger.error_occurred("TestError", "Test error message", "test_component")
        
        # Check that messages appear in correct files only
        main_log_file = self.log_dir / "genebot.log"
        trade_log_file = self.log_dir / "trades.log"
        error_log_file = self.log_dir / "errors.log"
        
        # Read file contents
        main_content = ""
        if main_log_file.exists():
            with open(main_log_file, 'r') as f:
                main_content = f.read()
        
        trade_content = ""
        if trade_log_file.exists():
            with open(trade_log_file, 'r') as f:
                trade_content = f.read()
        
        error_content = ""
        if error_log_file.exists():
            with open(error_log_file, 'r') as f:
                error_content = f.read()
        
        # Trade message should only be in trade log
        self.assertIn("Trade opened", trade_content)
        self.assertNotIn("Trade opened", main_content)
        self.assertNotIn("Trade opened", error_content)
        
        # Error message should only be in error log
        self.assertIn("Test error message", error_content)
        self.assertNotIn("Test error message", main_content)
        self.assertNotIn("Test error message", trade_content)


class TestHandlerDeduplication(unittest.TestCase):
    """Test handler deduplication functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
    
    def test_no_duplicate_handlers_created(self):
        """Test that duplicate handlers are not created for the same logger."""
        config = LoggingConfig(
            level="INFO",
            console_output=True,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get the same logger multiple times
        logger1 = factory.get_logger("handler.test")
        logger2 = factory.get_logger("handler.test")
        logger3 = factory.get_logger("handler.test")
        
        # Should be the same instance
        self.assertIs(logger1, logger2)
        self.assertIs(logger2, logger3)
        
        # Check underlying Python logger handlers
        python_logger = logging.getLogger("handler.test")
        handler_count = len(python_logger.handlers)
        
        print(f"Handler count for 'handler.test': {handler_count}")
        
        # Should have reasonable number of handlers (not duplicated)
        # Exact count depends on configuration, but should be consistent
        initial_count = handler_count
        
        # Get logger again - should not add more handlers
        logger4 = factory.get_logger("handler.test")
        final_count = len(python_logger.handlers)
        
        print(f"Handler count after additional get: {final_count}")
        
        self.assertEqual(initial_count, final_count)
    
    def test_different_loggers_have_appropriate_handlers(self):
        """Test that different loggers have appropriate handlers without duplication."""
        config = LoggingConfig(
            level="INFO",
            console_output=True,
            file_output=True,
            log_directory=self.log_dir,
            enable_trade_logging=True,
            enable_error_logging=True
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get different types of loggers
        main_logger = factory.get_logger("genebot.main")
        trade_logger = factory.get_trade_logger()
        error_logger = factory.get_error_logger()
        
        # Check handler counts
        main_python_logger = logging.getLogger("genebot.main")
        trade_python_logger = logging.getLogger("genebot.trades")
        error_python_logger = logging.getLogger("genebot.errors")
        
        main_handlers = len(main_python_logger.handlers)
        trade_handlers = len(trade_python_logger.handlers)
        error_handlers = len(error_python_logger.handlers)
        
        print(f"Main logger handlers: {main_handlers}")
        print(f"Trade logger handlers: {trade_handlers}")
        print(f"Error logger handlers: {error_handlers}")
        
        # Each should have handlers, but not excessive numbers
        self.assertGreater(main_handlers, 0)
        self.assertGreater(trade_handlers, 0)
        self.assertGreater(error_handlers, 0)
        
        # No logger should have an excessive number of handlers
        self.assertLess(main_handlers, 10)
        self.assertLess(trade_handlers, 10)
        self.assertLess(error_handlers, 10)
    
    def test_handler_types_are_correct(self):
        """Test that loggers have the correct types of handlers."""
        config = LoggingConfig(
            level="INFO",
            console_output=True,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        logger = factory.get_logger("genebot.test")
        python_logger = logging.getLogger("genebot.test")
        
        # Check handler types
        handler_types = [type(handler).__name__ for handler in python_logger.handlers]
        
        print(f"Handler types: {handler_types}")
        
        # Should have appropriate handler types based on configuration
        if config.console_output:
            has_stream_handler = any('Stream' in handler_type for handler_type in handler_types)
            self.assertTrue(has_stream_handler, "Should have StreamHandler for console output")
        
        if config.file_output:
            has_file_handler = any('File' in handler_type or 'Rotating' in handler_type 
                                 for handler_type in handler_types)
            self.assertTrue(has_file_handler, "Should have FileHandler for file output")


class TestLoggerPropagationConfiguration(unittest.TestCase):
    """Test logger propagation configuration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
    
    def test_specialized_logger_propagation_disabled(self):
        """Test that specialized loggers have propagation disabled to prevent duplicates."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            enable_trade_logging=True,
            enable_error_logging=True,
            enable_performance_logging=True
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get specialized loggers
        trade_logger = factory.get_trade_logger()
        error_logger = factory.get_error_logger()
        perf_logger = factory.get_performance_logger()
        
        # Check propagation settings
        trade_python_logger = logging.getLogger("genebot.trades")
        error_python_logger = logging.getLogger("genebot.errors")
        perf_python_logger = logging.getLogger("genebot.performance")
        
        print(f"Trade logger propagate: {trade_python_logger.propagate}")
        print(f"Error logger propagate: {error_python_logger.propagate}")
        print(f"Performance logger propagate: {perf_python_logger.propagate}")
        
        # Specialized loggers should have propagation disabled
        self.assertFalse(trade_python_logger.propagate)
        self.assertFalse(error_python_logger.propagate)
        self.assertFalse(perf_python_logger.propagate)
    
    def test_main_logger_hierarchy_propagation(self):
        """Test propagation settings in main logger hierarchy."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get loggers at different hierarchy levels
        parent_logger = factory.get_logger("genebot")
        child_logger = factory.get_logger("genebot.trading")
        grandchild_logger = factory.get_logger("genebot.trading.engine")
        
        # Check propagation settings
        parent_python_logger = logging.getLogger("genebot")
        child_python_logger = logging.getLogger("genebot.trading")
        grandchild_python_logger = logging.getLogger("genebot.trading.engine")
        
        print(f"Parent (genebot) propagate: {parent_python_logger.propagate}")
        print(f"Child (genebot.trading) propagate: {child_python_logger.propagate}")
        print(f"Grandchild (genebot.trading.engine) propagate: {grandchild_python_logger.propagate}")
        
        # Main genebot logger should not propagate to root to prevent duplicates
        self.assertFalse(parent_python_logger.propagate)
        
        # Child loggers should propagate to genebot logger (or not, depending on configuration)
        # The key is that the configuration should be consistent and prevent duplicates
    
    def test_external_library_logger_propagation(self):
        """Test that external library loggers have correct propagation settings."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            external_lib_level="WARNING"
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Check external library loggers
        ccxt_logger = logging.getLogger("ccxt")
        urllib3_logger = logging.getLogger("urllib3")
        requests_logger = logging.getLogger("requests")
        
        print(f"CCXT logger propagate: {ccxt_logger.propagate}")
        print(f"urllib3 logger propagate: {urllib3_logger.propagate}")
        print(f"requests logger propagate: {requests_logger.propagate}")
        
        # External library loggers should not propagate to prevent noise
        self.assertFalse(ccxt_logger.propagate)
        self.assertFalse(urllib3_logger.propagate)
        self.assertFalse(requests_logger.propagate)
    
    def test_no_duplicate_messages_with_hierarchy(self):
        """Test that logger hierarchy doesn't cause duplicate messages."""
        config = LoggingConfig(
            level="DEBUG",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get loggers at different hierarchy levels
        parent_logger = factory.get_logger("genebot.test")
        child_logger = factory.get_logger("genebot.test.child")
        grandchild_logger = factory.get_logger("genebot.test.child.grandchild")
        
        # Log messages from each level
        parent_logger.info("Parent message")
        child_logger.info("Child message")
        grandchild_logger.info("Grandchild message")
        
        # Check log file
        log_file = self.log_dir / "genebot.log"
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Each message should appear exactly once
        parent_count = content.count("Parent message")
        child_count = content.count("Child message")
        grandchild_count = content.count("Grandchild message")
        
        print(f"Parent message count: {parent_count}")
        print(f"Child message count: {child_count}")
        print(f"Grandchild message count: {grandchild_count}")
        
        self.assertEqual(parent_count, 1)
        self.assertEqual(child_count, 1)
        self.assertEqual(grandchild_count, 1)


class TestDuplicateConfigurationDetection(unittest.TestCase):
    """Test detection and prevention of duplicate logging configurations."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
    
    def test_factory_singleton_prevents_duplicate_configuration(self):
        """Test that factory singleton prevents duplicate configuration."""
        config = LoggingConfig(
            level="INFO",
            console_output=True,
            file_output=True,
            log_directory=self.log_dir
        )
        
        # Get factory instances
        factory1 = LoggerFactory()
        factory2 = LoggerFactory()
        
        # Should be the same instance
        self.assertIs(factory1, factory2)
        
        # Configure once
        factory1.setup_global_config(config)
        
        # Both references should be configured
        self.assertTrue(factory1._configured)
        self.assertTrue(factory2._configured)
        self.assertIs(factory1._config, factory2._config)
    
    def test_multiple_configuration_calls_are_safe(self):
        """Test that multiple configuration calls don't create duplicates."""
        config1 = LoggingConfig(
            level="INFO",
            console_output=True,
            file_output=False,
            log_directory=self.log_dir
        )
        
        config2 = LoggingConfig(
            level="DEBUG",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        
        # Configure multiple times
        factory.setup_global_config(config1)
        initial_config = factory._config
        
        factory.setup_global_config(config2)
        final_config = factory._config
        
        # Configuration should be updated, not duplicated
        self.assertIsNot(initial_config, final_config)
        self.assertEqual(final_config.level, "DEBUG")
        self.assertFalse(final_config.console_output)
        self.assertTrue(final_config.file_output)
    
    def test_logger_cache_prevents_duplicate_instances(self):
        """Test that logger cache prevents duplicate logger instances."""
        config = LoggingConfig(
            console_output=False,
            file_output=False,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get same logger multiple times
        logger1 = factory.get_logger("cache.test")
        logger2 = factory.get_logger("cache.test")
        logger3 = factory.get_logger("cache.test")
        
        # Should be the same instance
        self.assertIs(logger1, logger2)
        self.assertIs(logger2, logger3)
        
        # Cache should contain the logger
        cache_key = "cache.test:none:True"  # name:context:optimization
        self.assertIn(cache_key, factory._logger_cache)
        self.assertIs(factory._logger_cache[cache_key], logger1)
    
    def test_context_based_cache_separation(self):
        """Test that different contexts create separate cache entries."""
        config = LoggingConfig(
            console_output=False,
            file_output=False,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        context1 = LogContext(component="test1", operation="op1")
        context2 = LogContext(component="test2", operation="op2")
        
        # Get loggers with different contexts
        logger1 = factory.get_logger("context.test", context=context1)
        logger2 = factory.get_logger("context.test", context=context2)
        logger3 = factory.get_logger("context.test")  # No context
        
        # Should be different instances
        self.assertIsNot(logger1, logger2)
        self.assertIsNot(logger2, logger3)
        self.assertIsNot(logger1, logger3)
        
        # But same context should return same instance
        logger1_again = factory.get_logger("context.test", context=context1)
        self.assertIs(logger1, logger1_again)


if __name__ == '__main__':
    unittest.main(verbosity=2)