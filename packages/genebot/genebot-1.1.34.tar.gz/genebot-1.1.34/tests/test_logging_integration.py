"""
Integration tests for the logging system.

This module tests end-to-end logging flow, multiple logger interaction,
file rotation, and external library integration.
"""

import json
import logging
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO
import shutil

from genebot.logging.factory import LoggerFactory
from genebot.logging.config import LoggingConfig
from genebot.logging.context import LogContext, set_context, clear_context


class TestEndToEndLoggingFlow(unittest.TestCase):
    """Test complete logging flow from application to output."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        
        # Reset factory singleton
        LoggerFactory._instance = None
        
        # Clear any existing context
        clear_context()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
        clear_context()
    
    def test_complete_logging_flow_structured(self):
        """Test complete logging flow with structured output."""
        # Configure logging
        config = LoggingConfig(
            level="DEBUG",
            format_type="structured",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            enable_trade_logging=True,
            enable_performance_logging=True,
            enable_error_logging=True
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get different types of loggers
        main_logger = factory.get_logger("genebot.main")
        trade_logger = factory.get_trade_logger()
        perf_logger = factory.get_performance_logger()
        error_logger = factory.get_error_logger()
        
        # Set context
        context = LogContext(
            component="integration_test",
            operation="end_to_end_test",
            symbol="BTCUSDT",
            exchange="binance"
        )
        set_context(context)
        
        # Log various messages
        main_logger.info("Application started")
        trade_logger.trade_opened("BTCUSDT", "BUY", 1.0, 50000.0)
        perf_logger.execution_time("order_processing", 125.5)
        error_logger.error_occurred("ValidationError", "Invalid symbol", "trading")
        main_logger.debug("Debug information")
        
        # Verify files were created
        main_log_file = self.log_dir / "genebot.log"
        trade_log_file = self.log_dir / "trades.log"
        perf_log_file = self.log_dir / "performance.log"
        error_log_file = self.log_dir / "errors.log"
        
        self.assertTrue(main_log_file.exists())
        self.assertTrue(trade_log_file.exists())
        self.assertTrue(perf_log_file.exists())
        self.assertTrue(error_log_file.exists())
        
        # Verify content in main log
        with open(main_log_file, 'r') as f:
            main_content = f.read()
        
        self.assertIn("Application started", main_content)
        self.assertIn("Debug information", main_content)
        
        # Parse and verify structured format
        main_lines = [line for line in main_content.strip().split('\n') if line]
        for line in main_lines:
            log_data = json.loads(line)
            self.assertIn('timestamp', log_data)
            self.assertIn('level', log_data)
            self.assertIn('logger', log_data)
            self.assertIn('message', log_data)
            self.assertIn('context', log_data)
            
            # Verify context is included
            context_data = log_data['context']
            self.assertEqual(context_data['component'], 'integration_test')
            self.assertEqual(context_data['operation'], 'end_to_end_test')
        
        # Verify trade log content
        with open(trade_log_file, 'r') as f:
            trade_content = f.read()
        
        self.assertIn("Trade opened", trade_content)
        trade_data = json.loads(trade_content.strip())
        self.assertEqual(trade_data['trade_event'], 'opened')
        self.assertEqual(trade_data['symbol'], 'BTCUSDT')
        
        # Verify performance log content
        with open(perf_log_file, 'r') as f:
            perf_content = f.read()
        
        self.assertIn("Performance", perf_content)
        perf_data = json.loads(perf_content.strip())
        self.assertEqual(perf_data['metric_type'], 'execution_time')
        self.assertEqual(perf_data['duration_ms'], 125.5)
        
        # Verify error log content
        with open(error_log_file, 'r') as f:
            error_content = f.read()
        
        self.assertIn("ValidationError", error_content)
        error_data = json.loads(error_content.strip())
        self.assertEqual(error_data['error_type'], 'ValidationError')
    
    def test_complete_logging_flow_simple(self):
        """Test complete logging flow with simple output."""
        # Configure logging with simple format
        config = LoggingConfig(
            level="INFO",
            format_type="simple",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            enable_trade_logging=False,  # Only main log for simplicity
            enable_performance_logging=False,
            enable_error_logging=False
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        logger = factory.get_logger("genebot.test")
        
        # Log messages
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Verify file content
        log_file = self.log_dir / "genebot.log"
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Should be human-readable format
        self.assertIn("INFO", content)
        self.assertIn("WARNING", content)
        self.assertIn("ERROR", content)
        self.assertIn("Test info message", content)
        self.assertIn("Test warning message", content)
        self.assertIn("Test error message", content)
        
        # Should not be JSON format
        lines = content.strip().split('\n')
        for line in lines:
            with self.assertRaises(json.JSONDecodeError):
                json.loads(line)


class TestMultipleLoggerInteraction(unittest.TestCase):
    """Test interaction between multiple loggers."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
        clear_context()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
        clear_context()
    
    def test_logger_hierarchy_and_propagation(self):
        """Test logger hierarchy and propagation settings."""
        config = LoggingConfig(
            level="DEBUG",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            enable_trade_logging=True
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get loggers at different hierarchy levels
        parent_logger = factory.get_logger("genebot")
        child_logger = factory.get_logger("genebot.trading")
        grandchild_logger = factory.get_logger("genebot.trading.engine")
        trade_logger = factory.get_trade_logger()  # genebot.trades
        
        # Log messages from different loggers
        parent_logger.info("Parent message")
        child_logger.info("Child message")
        grandchild_logger.info("Grandchild message")
        trade_logger.info("Trade message")
        
        # Verify main log file
        main_log_file = self.log_dir / "genebot.log"
        self.assertTrue(main_log_file.exists())
        
        with open(main_log_file, 'r') as f:
            main_content = f.read()
        
        # Should contain messages from genebot hierarchy
        self.assertIn("Parent message", main_content)
        self.assertIn("Child message", main_content)
        self.assertIn("Grandchild message", main_content)
        
        # Should NOT contain trade message (separate logger with propagate=False)
        self.assertNotIn("Trade message", main_content)
        
        # Verify trade log file
        trade_log_file = self.log_dir / "trades.log"
        self.assertTrue(trade_log_file.exists())
        
        with open(trade_log_file, 'r') as f:
            trade_content = f.read()
        
        # Should contain only trade message
        self.assertIn("Trade message", trade_content)
        self.assertNotIn("Parent message", trade_content)
    
    def test_concurrent_logging_from_multiple_threads(self):
        """Test concurrent logging from multiple threads."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        results = []
        
        def log_from_thread(thread_id, num_messages):
            logger = factory.get_logger(f"genebot.thread_{thread_id}")
            context = LogContext(
                component=f"thread_{thread_id}",
                operation="concurrent_test"
            )
            
            for i in range(num_messages):
                logger.info(f"Message {i} from thread {thread_id}", context=context)
            
            results.append(f"thread_{thread_id}_completed")
        
        # Start multiple threads
        threads = []
        num_threads = 5
        messages_per_thread = 10
        
        for i in range(num_threads):
            thread = threading.Thread(target=log_from_thread, args=(i, messages_per_thread))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all threads completed
        self.assertEqual(len(results), num_threads)
        
        # Verify log file
        log_file = self.log_dir / "genebot.log"
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Count total messages
        lines = [line for line in content.strip().split('\n') if line]
        self.assertEqual(len(lines), num_threads * messages_per_thread)
        
        # Verify messages from each thread are present
        for thread_id in range(num_threads):
            for msg_id in range(messages_per_thread):
                expected_msg = f"Message {msg_id} from thread {thread_id}"
                self.assertIn(expected_msg, content)
    
    def test_logger_caching_and_reuse(self):
        """Test that loggers are properly cached and reused."""
        config = LoggingConfig(
            console_output=False,
            file_output=False,  # No file output for this test
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get same logger multiple times
        logger1 = factory.get_logger("test.logger")
        logger2 = factory.get_logger("test.logger")
        logger3 = factory.get_logger("test.logger")
        
        # Should be the same instance (cached)
        self.assertIs(logger1, logger2)
        self.assertIs(logger2, logger3)
        
        # Different logger names should be different instances
        different_logger = factory.get_logger("different.logger")
        self.assertIsNot(logger1, different_logger)
        
        # Same name with different context should be different instances
        context = LogContext(component="test", operation="cache_test")
        context_logger = factory.get_logger("test.logger", context=context)
        self.assertIsNot(logger1, context_logger)


class TestFileRotationAndHandlerManagement(unittest.TestCase):
    """Test file rotation and handler management."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
    
    def test_log_file_creation_and_rotation_setup(self):
        """Test that log files are created and rotation is set up."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            max_file_size=1024,  # Small size to test rotation
            backup_count=3,
            enable_trade_logging=True,
            enable_performance_logging=True,
            enable_error_logging=True
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get loggers to trigger handler creation
        main_logger = factory.get_logger("genebot.main")
        trade_logger = factory.get_trade_logger()
        perf_logger = factory.get_performance_logger()
        error_logger = factory.get_error_logger()
        
        # Log some messages
        main_logger.info("Main log message")
        trade_logger.info("Trade log message")
        perf_logger.info("Performance log message")
        error_logger.error("Error log message")
        
        # Verify log directory was created
        self.assertTrue(self.log_dir.exists())
        
        # Verify log files were created
        expected_files = ["genebot.log", "trades.log", "performance.log", "errors.log"]
        for filename in expected_files:
            log_file = self.log_dir / filename
            self.assertTrue(log_file.exists(), f"Log file {filename} was not created")
            
            # Verify file has content
            with open(log_file, 'r') as f:
                content = f.read()
            self.assertGreater(len(content), 0, f"Log file {filename} is empty")
    
    def test_log_directory_creation(self):
        """Test that log directory is created if it doesn't exist."""
        # Use a nested directory that doesn't exist
        nested_log_dir = self.log_dir / "nested" / "logs"
        
        config = LoggingConfig(
            console_output=False,
            file_output=True,
            log_directory=nested_log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        logger = factory.get_logger("test.logger")
        logger.info("Test message")
        
        # Directory should be created
        self.assertTrue(nested_log_dir.exists())
        
        # Log file should exist
        log_file = nested_log_dir / "genebot.log"
        self.assertTrue(log_file.exists())
    
    def test_handler_deduplication(self):
        """Test that duplicate handlers are not created."""
        config = LoggingConfig(
            console_output=True,
            file_output=True,
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get the same logger multiple times
        logger1 = factory.get_logger("genebot.test")
        logger2 = factory.get_logger("genebot.test")
        
        # Should be the same instance with same handlers
        self.assertIs(logger1, logger2)
        
        # Check underlying Python logger handlers
        python_logger = logging.getLogger("genebot.test")
        initial_handler_count = len(python_logger.handlers)
        
        # Get logger again - should not add more handlers
        logger3 = factory.get_logger("genebot.test")
        final_handler_count = len(python_logger.handlers)
        
        self.assertEqual(initial_handler_count, final_handler_count)


class TestExternalLibraryLoggerIntegration(unittest.TestCase):
    """Test integration with external library loggers."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
        
        # Store original log levels to restore later
        self.original_levels = {}
        for lib in ['ccxt', 'urllib3', 'requests']:
            logger = logging.getLogger(lib)
            self.original_levels[lib] = logger.level
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
        
        # Restore original log levels
        for lib, level in self.original_levels.items():
            logger = logging.getLogger(lib)
            logger.setLevel(level)
    
    def test_external_library_log_level_control(self):
        """Test that external library log levels are properly controlled."""
        config = LoggingConfig(
            level="DEBUG",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            external_lib_level="WARNING"
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get external library loggers
        ccxt_logger = logging.getLogger('ccxt')
        urllib3_logger = logging.getLogger('urllib3')
        requests_logger = logging.getLogger('requests')
        
        # Verify their levels are set correctly
        self.assertEqual(ccxt_logger.level, logging.WARNING)
        self.assertEqual(urllib3_logger.level, logging.WARNING)
        self.assertEqual(requests_logger.level, logging.WARNING)
        
        # Log messages at different levels
        ccxt_logger.debug("CCXT debug message")  # Should not appear
        ccxt_logger.info("CCXT info message")    # Should not appear
        ccxt_logger.warning("CCXT warning message")  # Should appear
        ccxt_logger.error("CCXT error message")      # Should appear
        
        urllib3_logger.info("urllib3 info message")     # Should not appear
        urllib3_logger.warning("urllib3 warning message")  # Should appear
        
        # Check log file content
        log_file = self.log_dir / "genebot.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Should contain warning and error messages
            self.assertIn("CCXT warning message", content)
            self.assertIn("CCXT error message", content)
            self.assertIn("urllib3 warning message", content)
            
            # Should not contain debug and info messages
            self.assertNotIn("CCXT debug message", content)
            self.assertNotIn("CCXT info message", content)
            self.assertNotIn("urllib3 info message", content)
    
    def test_external_library_noise_reduction(self):
        """Test that external library noise is properly reduced."""
        config = LoggingConfig(
            level="DEBUG",  # Very verbose for our loggers
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            external_lib_level="ERROR"  # Very quiet for external libs
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get our logger and external library logger
        our_logger = factory.get_logger("genebot.test")
        external_logger = logging.getLogger('ccxt')
        
        # Log many messages from both
        for i in range(10):
            our_logger.debug(f"Our debug message {i}")
            our_logger.info(f"Our info message {i}")
            external_logger.debug(f"External debug message {i}")
            external_logger.info(f"External info message {i}")
            external_logger.warning(f"External warning message {i}")
        
        # Check log file
        log_file = self.log_dir / "genebot.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Should contain all our messages
            for i in range(10):
                self.assertIn(f"Our debug message {i}", content)
                self.assertIn(f"Our info message {i}", content)
            
            # Should not contain external debug/info/warning (only ERROR and above)
            for i in range(10):
                self.assertNotIn(f"External debug message {i}", content)
                self.assertNotIn(f"External info message {i}", content)
                self.assertNotIn(f"External warning message {i}", content)
    
    def test_external_library_configuration_isolation(self):
        """Test that external library configuration doesn't affect our loggers."""
        config = LoggingConfig(
            level="INFO",
            console_output=False,
            file_output=True,
            log_directory=self.log_dir,
            external_lib_level="CRITICAL"
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        # Get our logger
        our_logger = factory.get_logger("genebot.test")
        
        # Manually change external library logger level
        external_logger = logging.getLogger('urllib3')
        external_logger.setLevel(logging.DEBUG)  # Override our setting
        
        # Log messages
        our_logger.info("Our info message")
        our_logger.debug("Our debug message")  # Should not appear (our level is INFO)
        external_logger.debug("External debug message")  # Might appear due to manual override
        
        # Our logger behavior should be unaffected
        log_file = self.log_dir / "genebot.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Our info message should appear
            self.assertIn("Our info message", content)
            
            # Our debug message should not appear (level filtering)
            self.assertNotIn("Our debug message", content)


class TestLoggingSystemRecovery(unittest.TestCase):
    """Test logging system recovery and error handling."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        LoggerFactory._instance = None
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LoggerFactory._instance = None
    
    def test_logging_with_invalid_log_directory(self):
        """Test logging behavior with invalid log directory."""
        # Use a directory that can't be created (invalid path)
        if os.name == 'nt':  # Windows
            invalid_dir = Path("C:\\invalid\\path\\that\\cannot\\be\\created")
        else:  # Unix-like
            invalid_dir = Path("/root/invalid/path/that/cannot/be/created")
        
        config = LoggingConfig(
            console_output=True,  # Should still work
            file_output=True,     # This might fail
            log_directory=invalid_dir
        )
        
        factory = LoggerFactory()
        
        # Should not crash even with invalid directory
        try:
            factory.setup_global_config(config)
            logger = factory.get_logger("test.logger")
            logger.info("Test message")
            # If we get here, the system handled the error gracefully
        except Exception as e:
            # If an exception occurs, it should be a reasonable one
            self.assertIsInstance(e, (OSError, PermissionError, FileNotFoundError))
    
    def test_logging_with_no_permissions(self):
        """Test logging behavior when file permissions are denied."""
        # Create a directory with no write permissions
        restricted_dir = Path(self.temp_dir) / "restricted"
        restricted_dir.mkdir()
        
        # Remove write permissions (Unix-like systems)
        if hasattr(os, 'chmod'):
            try:
                os.chmod(restricted_dir, 0o444)  # Read-only
                
                config = LoggingConfig(
                    console_output=True,
                    file_output=True,
                    log_directory=restricted_dir
                )
                
                factory = LoggerFactory()
                
                # Should handle permission error gracefully
                try:
                    factory.setup_global_config(config)
                    logger = factory.get_logger("test.logger")
                    logger.info("Test message")
                except (OSError, PermissionError):
                    # Expected behavior - permission denied
                    pass
                
            finally:
                # Restore permissions for cleanup
                os.chmod(restricted_dir, 0o755)
    
    def test_fallback_to_console_logging(self):
        """Test fallback to console logging when file logging fails."""
        config = LoggingConfig(
            console_output=True,
            file_output=False,  # Disable file output
            log_directory=self.log_dir
        )
        
        factory = LoggerFactory()
        factory.setup_global_config(config)
        
        logger = factory.get_logger("test.logger")
        
        # Should work without file output
        logger.info("Console only message")
        logger.error("Console error message")
        
        # No log files should be created
        if self.log_dir.exists():
            log_files = list(self.log_dir.glob("*.log"))
            self.assertEqual(len(log_files), 0)


if __name__ == '__main__':
    unittest.main()