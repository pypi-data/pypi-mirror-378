"""
Tests for CLI Error Handling System
===================================

Comprehensive tests for error scenarios and recovery mechanisms.
"""

import pytest
import tempfile
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from genebot.cli.utils.error_handler import (
    CLIErrorHandler, ErrorRecoveryManager,
    CLIException, ConfigurationError, AccountError, ProcessError,
    DataError, ValidationError, NetworkError, AuthenticationError,
    FilePermissionError, DependencyError
)
from genebot.cli.result import CommandResult, ResultStatus


class TestCLIExceptions:
    """Test CLI exception classes"""
    
    def test_cli_exception_basic(self):
        """Test basic CLI exception functionality"""
        exc = CLIException(
            message="Test error",
            suggestions=["Fix this", "Try that"],
            error_code="TEST_ERROR",
            context={"key": "value"}
        )
        
        assert exc.message == "Test error"
        assert exc.suggestions == ["Fix this", "Try that"]
        assert exc.error_code == "TEST_ERROR"
        assert exc.context == {"key": "value"}
        assert exc.timestamp is not None
    
    def test_cli_exception_to_dict(self):
        """Test CLI exception serialization"""
        exc = CLIException(
            message="Test error",
            error_code="TEST_ERROR",
            context={"key": "value"}
        )
        
        exc_dict = exc.to_dict()
        
        assert exc_dict['error_type'] == 'CLIException'
        assert exc_dict['error_code'] == 'TEST_ERROR'
        assert exc_dict['message'] == 'Test error'
        assert exc_dict['context'] == {"key": "value"}
        assert 'timestamp' in exc_dict
    
    def test_configuration_error(self):
        """Test configuration error with specific context"""
        exc = ConfigurationError(
            message="Invalid config",
            config_file="config.yaml",
            config_key="api_key"
        )
        
        assert exc.config_file == "config.yaml"
        assert exc.config_key == "api_key"
        assert exc.context['config_file'] == "config.yaml"
        assert exc.context['config_key'] == "api_key"
    
    def test_account_error(self):
        """Test account error with specific context"""
        exc = AccountError(
            message="Account validation failed",
            account_name="test_account",
            account_type="crypto",
            exchange="binance"
        )
        
        assert exc.account_name == "test_account"
        assert exc.account_type == "crypto"
        assert exc.exchange == "binance"
        assert exc.context['account_name'] == "test_account"
    
    def test_process_error(self):
        """Test process error with specific context"""
        exc = ProcessError(
            message="Process failed",
            pid=12345,
            process_name="genebot"
        )
        
        assert exc.pid == 12345
        assert exc.process_name == "genebot"
        assert exc.context['pid'] == 12345
        assert exc.context['process_name'] == "genebot"


class TestErrorRecoveryManager:
    """Test error recovery manager"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace
    
    @pytest.fixture
    def recovery_manager(self, temp_workspace):
        """Create recovery manager for testing"""
        return ErrorRecoveryManager(temp_workspace)
    
    def test_create_config_backup(self, recovery_manager, temp_workspace):
        """Test configuration backup creation"""
        # Create a test config file
        config_file = temp_workspace / "test_config.yaml"
        config_file.write_text("test: config")
        
        # Create backup
        backup_file = recovery_manager.create_config_backup(config_file)
        
        assert backup_file is not None
        assert backup_file.exists()
        assert backup_file.read_text() == "test: config"
        assert "backup" in backup_file.name
    
    def test_create_backup_nonexistent_file(self, recovery_manager, temp_workspace):
        """Test backup creation for non-existent file"""
        config_file = temp_workspace / "nonexistent.yaml"
        backup_file = recovery_manager.create_config_backup(config_file)
        
        assert backup_file is None
    
    def test_restore_config_backup(self, recovery_manager, temp_workspace):
        """Test configuration restoration from backup"""
        # Create original and backup files
        config_file = temp_workspace / "config.yaml"
        backup_file = temp_workspace / "config_backup.yaml"
        
        config_file.write_text("corrupted: config")
        backup_file.write_text("good: config")
        
        # Restore from backup
        success = recovery_manager.restore_config_backup(config_file, backup_file)
        
        assert success
        assert config_file.read_text() == "good: config"
    
    def test_cleanup_stale_processes(self, recovery_manager, temp_workspace):
        """Test cleanup of stale process files"""
        # Create fake PID files
        pid_file1 = temp_workspace / "bot1.pid"
        pid_file2 = temp_workspace / "bot2.pid"
        pid_file3 = temp_workspace / "invalid.pid"
        
        pid_file1.write_text("999999")  # Non-existent PID
        pid_file2.write_text(str(os.getpid()))  # Current process PID
        pid_file3.write_text("invalid")  # Invalid PID
        
        cleaned_pids = recovery_manager.cleanup_stale_processes()
        
        # Should clean up non-existent and invalid PIDs
        assert not pid_file1.exists()
        assert not pid_file3.exists()
        assert pid_file2.exists()  # Current process should remain
        assert 999999 in cleaned_pids
    
    def test_repair_directory_structure(self, recovery_manager, temp_workspace):
        """Test directory structure repair"""
        # Ensure some directories don't exist
        logs_dir = temp_workspace / "logs"
        config_dir = temp_workspace / "config"
        
        assert not logs_dir.exists()
        assert not config_dir.exists()
        
        # Repair directory structure
        created_dirs = recovery_manager.repair_directory_structure()
        
        # Check that directories were created
        assert logs_dir.exists()
        assert config_dir.exists()
        assert len(created_dirs) > 0
    
    def test_check_file_permissions(self, recovery_manager, temp_workspace):
        """Test file permission checking"""
        test_file = temp_workspace / "test_file.txt"
        test_file.write_text("test")
        
        permissions = recovery_manager.check_file_permissions(test_file)
        
        assert 'readable' in permissions
        assert 'writable' in permissions
        assert 'executable' in permissions
        assert permissions['readable']  # Should be readable
        assert permissions['writable']  # Should be writable
    
    def test_fix_file_permissions(self, recovery_manager, temp_workspace):
        """Test file permission fixing"""
        test_file = temp_workspace / "test_file.txt"
        test_file.write_text("test")
        
        # Fix permissions
        success = recovery_manager.fix_file_permissions(test_file, 0o644)
        
        assert success
        # Check that file still exists and is accessible
        assert test_file.exists()
        assert test_file.read_text() == "test"


class TestCLIErrorHandler:
    """Test CLI error handler"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace
    
    @pytest.fixture
    def error_handler(self, temp_workspace):
        """Create error handler for testing"""
        return CLIErrorHandler(verbose=True, workspace_path=temp_workspace)
    
    def test_handle_cli_exception(self, error_handler):
        """Test handling of CLI exceptions"""
        exc = ConfigurationError(
            message="Config file not found",
            error_code="CONFIG_NOT_FOUND",
            suggestions=["Create config file", "Check path"]
        )
        
        result = error_handler.handle_exception(exc, context="Test command")
        
        assert not result.success
        assert result.status == ResultStatus.ERROR
        assert "Test command: Config file not found" in result.message
        assert result.error_code == "CONFIG_NOT_FOUND"
        assert "Create config file" in result.suggestions
    
    def test_handle_standard_exception(self, error_handler):
        """Test handling of standard Python exceptions"""
        exc = FileNotFoundError("config.yaml not found")
        
        result = error_handler.handle_exception(exc, context="Loading config")
        
        assert not result.success
        assert result.status == ResultStatus.ERROR
        assert "Loading config: Required file not found" in result.message
        assert "genebot init-config" in " ".join(result.suggestions)
    
    def test_handle_unknown_exception(self, error_handler):
        """Test handling of unknown exceptions"""
        exc = RuntimeError("Something went wrong")
        
        result = error_handler.handle_exception(exc, context="Unknown operation")
        
        assert not result.success
        assert "Unknown operation: Unexpected error" in result.message
        assert "Check the logs" in " ".join(result.suggestions)
    
    def test_handle_validation_errors(self, error_handler):
        """Test handling of validation errors"""
        errors = [
            "Missing required field: api_key",
            "Invalid format: email",
            "Value out of range: timeout"
        ]
        
        result = error_handler.handle_validation_errors(errors, context="Config validation")
        
        assert not result.success
        assert result.error_code == "VALIDATION_FAILED"
        assert "Found 3 validation error(s)" in result.message
        assert result.data['error_count'] == 3
        assert result.data['validation_errors'] == errors
    
    def test_handle_validation_errors_empty(self, error_handler):
        """Test handling of empty validation errors"""
        result = error_handler.handle_validation_errors([])
        
        assert result.success
        assert result.message == "Validation passed"
    
    def test_auto_recovery(self, error_handler):
        """Test automatic recovery functionality"""
        exc = FileNotFoundError("config.yaml not found")
        
        with patch.object(error_handler, '_attempt_recovery') as mock_recovery:
            mock_recovery.return_value = [
                {'action': 'repair_directory_structure', 'success': True, 'message': 'Directories created'}
            ]
            
            result = error_handler.handle_exception(exc, auto_recover=True)
            
            assert 'recovery_attempts' in result.data
            assert result.data['recovery_attempts'][0]['success']
    
    def test_error_logging(self, error_handler):
        """Test error logging functionality"""
        exc = ValueError("Invalid input")
        
        error_handler.handle_exception(exc, context="Test operation")
        
        assert len(error_handler.error_history) == 1
        error_entry = error_handler.error_history[0]
        assert error_entry['error_type'] == 'ValueError'
        assert error_entry['message'] == 'Invalid input'
        assert error_entry['context'] == 'Test operation'
    
    def test_create_error_report(self, error_handler):
        """Test error report creation"""
        # Generate some errors
        error_handler.handle_exception(ValueError("Test error 1"))
        error_handler.handle_exception(FileNotFoundError("Test error 2"))
        
        report = error_handler.create_error_report()
        
        assert 'timestamp' in report
        assert 'workspace_path' in report
        assert 'system_info' in report
        assert 'error_history' in report
        assert len(report['error_history']) == 2
    
    def test_save_error_report(self, error_handler, temp_workspace):
        """Test error report saving"""
        error_handler.handle_exception(ValueError("Test error"))
        
        report_path = error_handler.save_error_report()
        
        assert report_path.exists()
        assert report_path.suffix == '.json'
        
        # Verify report content
        report_data = json.loads(report_path.read_text())
        assert 'error_history' in report_data
        assert len(report_data['error_history']) == 1
    
    def test_format_result_basic(self, error_handler):
        """Test basic result formatting"""
        result = CommandResult.error(
            message="Test error",
            suggestions=["Fix this", "Try that"],
            error_code="TEST_ERROR"
        )
        
        formatted = error_handler.format_result(result)
        
        assert "❌ Test error" in formatted
        assert "💡 Suggestions:" in formatted
        assert "1. Fix this" in formatted
        assert "2. Try that" in formatted
        assert "Error Code: TEST_ERROR" in formatted
    
    def test_format_result_with_recovery(self, error_handler):
        """Test result formatting with recovery information"""
        result = CommandResult.error(
            message="Test error",
            suggestions=["Fix this"]
        )
        result.add_data('recovery_attempts', [
            {'action': 'test_action', 'success': True, 'message': 'Recovery succeeded'},
            {'action': 'test_action2', 'success': False, 'message': 'Recovery failed'}
        ])
        
        formatted = error_handler.format_result(result)
        
        assert "🔧 Successful Recovery Actions:" in formatted
        assert "❌ Failed Recovery Actions:" in formatted
        assert "Recovery succeeded" in formatted
        assert "Recovery failed" in formatted
    
    def test_format_troubleshooting_guide(self, error_handler):
        """Test troubleshooting guide generation"""
        exc = FileNotFoundError("config.yaml")
        
        guide = error_handler.format_troubleshooting_guide(exc)
        
        assert "🔍 Troubleshooting Guide for FileNotFoundError" in guide
        assert "📋 Quick Diagnosis Steps:" in guide
        assert "🛠️  Suggested Solutions:" in guide
        assert "📞 Need More Help?" in guide
    
    def test_wrap_command_execution_success(self, error_handler):
        """Test command execution wrapping - success case"""
        def successful_command():
            return CommandResult.success("Command succeeded")
        
        result = error_handler.wrap_command_execution(successful_command)
        
        assert result.success
        assert result.message == "Command succeeded"
    
    def test_wrap_command_execution_failure(self, error_handler):
        """Test command execution wrapping - failure case"""
        def failing_command():
            raise ValueError("Command failed")
        
        result = error_handler.wrap_command_execution(failing_command)
        
        assert not result.success
        assert "Command: failing_command" in result.message
        assert 'original_exception' in result.data
        assert isinstance(result.data['original_exception'], ValueError)


class TestErrorRecoveryActions:
    """Test specific error recovery actions"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace
    
    @pytest.fixture
    def error_handler(self, temp_workspace):
        """Create error handler for testing"""
        return CLIErrorHandler(verbose=True, workspace_path=temp_workspace)
    
    def test_network_connectivity_recovery(self, error_handler):
        """Test network connectivity recovery action"""
        # Mock successful network test
        with patch('socket.create_connection') as mock_connect:
            mock_connect.return_value = None
            
            success = error_handler._recovery_test_network_connectivity({})
            assert success
        
        # Mock failed network test
        with patch('socket.create_connection') as mock_connect:
            mock_connect.side_effect = OSError("Network unreachable")
            
            success = error_handler._recovery_test_network_connectivity({})
            assert not success
    
    def test_dependency_check_recovery(self, error_handler, temp_workspace):
        """Test dependency check recovery action"""
        # Create a mock requirements.txt
        requirements_file = temp_workspace / "requirements.txt"
        requirements_file.write_text("requests>=2.25.0\n# Comment line\npytest>=6.0.0")
        
        # Mock pkg_resources.require to succeed
        with patch('pkg_resources.require') as mock_require:
            mock_require.return_value = None
            
            success = error_handler._recovery_check_dependencies({})
            assert success
        
        # Mock pkg_resources.require to fail
        with patch('pkg_resources.require') as mock_require:
            mock_require.side_effect = Exception("Package not found")
            
            success = error_handler._recovery_check_dependencies({})
            assert not success
    
    def test_config_validation_recovery(self, error_handler):
        """Test configuration validation recovery action"""
        # Mock successful validation
        with patch('genebot.cli.utils.config_manager.ConfigurationManager') as mock_config:
            mock_instance = Mock()
            mock_instance.validate_all_configs.return_value = True
            mock_config.return_value = mock_instance
            
            success = error_handler._recovery_validate_config_schema({})
            assert success
        
        # Mock failed validation
        with patch('genebot.cli.utils.config_manager.ConfigurationManager') as mock_config:
            mock_instance = Mock()
            mock_instance.validate_all_configs.side_effect = Exception("Validation failed")
            mock_config.return_value = mock_instance
            
            success = error_handler._recovery_validate_config_schema({})
            assert not success


class TestErrorScenarios:
    """Test specific error scenarios and their handling"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace
    
    @pytest.fixture
    def error_handler(self, temp_workspace):
        """Create error handler for testing"""
        return CLIErrorHandler(verbose=True, workspace_path=temp_workspace)
    
    def test_configuration_file_missing_scenario(self, error_handler):
        """Test scenario: configuration file missing"""
        exc = FileNotFoundError("config/accounts.yaml not found")
        
        result = error_handler.handle_exception(exc, context="Loading accounts")
        
        assert not result.success
        assert "Required file not found" in result.message
        assert any("init-config" in s for s in result.suggestions)
    
    def test_network_connection_failed_scenario(self, error_handler):
        """Test scenario: network connection failed"""
        exc = ConnectionError("Failed to connect to api.binance.com")
        
        result = error_handler.handle_exception(exc, context="Account validation")
        
        assert not result.success
        assert "Network connection failed" in result.message
        assert any("internet connection" in s for s in result.suggestions)
    
    def test_permission_denied_scenario(self, error_handler):
        """Test scenario: permission denied"""
        # Use built-in PermissionError which should be mapped in error_mappings
        import builtins
        exc = builtins.PermissionError("Permission denied: /etc/genebot/config.yaml")
        
        result = error_handler.handle_exception(exc, context="Saving configuration")
        
        assert not result.success
        assert "Permission denied" in result.message
        # Debug: print suggestions to see what's actually there
        print(f"Suggestions: {result.suggestions}")
        assert any("permission" in s.lower() for s in result.suggestions)
    
    def test_process_already_running_scenario(self, error_handler):
        """Test scenario: process already running"""
        exc = ProcessError(
            message="Bot process already running",
            pid=12345,
            suggestions=["Stop the existing process first", "Use restart command instead"]
        )
        
        result = error_handler.handle_exception(exc, context="Starting bot")
        
        assert not result.success
        assert "Bot process already running" in result.message
        assert "Stop the existing process first" in result.suggestions
    
    def test_invalid_credentials_scenario(self, error_handler):
        """Test scenario: invalid API credentials"""
        exc = AuthenticationError(
            message="Invalid API credentials",
            auth_type="api_key",
            suggestions=["Check API key in .env file", "Verify key permissions"]
        )
        
        result = error_handler.handle_exception(exc, context="Account validation")
        
        assert not result.success
        assert "Invalid API credentials" in result.message
        assert "Check API key" in " ".join(result.suggestions)
    
    def test_database_connection_failed_scenario(self, error_handler):
        """Test scenario: database connection failed"""
        exc = DataError(
            message="Database connection failed",
            data_source="trading_bot.db",
            operation="fetch_trades"
        )
        
        result = error_handler.handle_exception(exc, context="Loading trade data")
        
        assert not result.success
        assert "Database connection failed" in result.message
        assert exc.data_source == "trading_bot.db"
        assert exc.operation == "fetch_trades"
    
    def test_multiple_validation_errors_scenario(self, error_handler):
        """Test scenario: multiple validation errors"""
        errors = [
            "API key is required",
            "Invalid email format",
            "Timeout must be positive",
            "Exchange not supported",
            "Missing required field: secret"
        ]
        
        result = error_handler.handle_validation_errors(errors, context="Account configuration")
        
        assert not result.success
        assert "Found 5 validation error(s)" in result.message
        assert result.data['error_count'] == 5
        assert "... and 2 more errors" in result.message  # Should truncate display


if __name__ == "__main__":
    pytest.main([__file__])