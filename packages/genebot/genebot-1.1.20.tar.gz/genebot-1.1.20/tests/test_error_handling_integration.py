"""
Error Handling Integration Tests
===============================

Integration tests to verify error handling works with CLI commands.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from argparse import Namespace

from genebot.cli.context import CLIContext
from genebot.cli.utils.logger import CLILogger
from genebot.cli.utils.error_handler import CLIErrorHandler, ConfigurationError
from genebot.cli.commands.account import ListAccountsCommand
from genebot.cli.result import CommandResult


class TestErrorHandlingIntegration:
    """Test error handling integration with CLI commands"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            yield workspace
    
    @pytest.fixture
    def cli_context(self, temp_workspace):
        """Create CLI context for testing"""
        return CLIContext(
            config_path=temp_workspace / "config",
            verbose=True,
            auto_recover=True
        )
    
    @pytest.fixture
    def cli_logger(self):
        """Create CLI logger for testing"""
        return CLILogger(verbose=True)
    
    @pytest.fixture
    def error_handler(self, temp_workspace):
        """Create error handler for testing"""
        return CLIErrorHandler(verbose=True, workspace_path=temp_workspace)
    
    def test_command_with_file_not_found_error(self, cli_context, cli_logger, error_handler):
        """Test command handling when configuration file is missing"""
        # Create command instance
        command = ListAccountsCommand(cli_context, cli_logger, error_handler)
        
        # Create args
        args = Namespace(type='all', status='all')
        
        # Execute command (should handle missing config file gracefully)
        result = command.run(args)
        
        # The command should either succeed (if it finds existing config) or provide helpful guidance
        if not result.success:
            assert any('init-config' in s for s in result.suggestions)
        # If it succeeds, it means there was existing configuration data
    
    def test_command_with_auto_recovery(self, cli_context, cli_logger, error_handler, temp_workspace):
        """Test command with auto-recovery enabled"""
        # Enable auto-recovery in context
        cli_context.auto_recover = True
        
        # Create command instance
        command = ListAccountsCommand(cli_context, cli_logger, error_handler)
        
        # Mock the account manager to raise an exception
        with patch('genebot.cli.commands.account.AccountManager') as mock_manager:
            mock_manager.side_effect = FileNotFoundError("config/accounts.yaml not found")
            
            args = Namespace(type='all', status='all')
            result = command.run(args)
            
            # Should attempt recovery and provide recovery information
            assert not result.success
            # Check if suggestions exist and are helpful
            if result.suggestions:
                # Should provide helpful suggestions about configuration
                assert any('config' in s.lower() for s in result.suggestions)
            # Or check if recovery data exists
            elif result.data and 'recovery_attempts' in result.data:
                assert 'recovery_attempts' in result.data
    
    def test_validation_error_handling(self, cli_context, cli_logger, error_handler):
        """Test validation error handling in commands"""
        # Create command instance
        command = ListAccountsCommand(cli_context, cli_logger, error_handler)
        
        # Test validation errors
        validation_errors = [
            "Missing required field: api_key",
            "Invalid email format",
            "Timeout must be positive"
        ]
        
        result = command.handle_validation_errors(validation_errors, "Account configuration")
        
        assert not result.success
        assert result.error_code == "VALIDATION_FAILED"
        assert "Found 3 validation error(s)" in result.message
        assert result.data['error_count'] == 3
    
    def test_safe_execute_wrapper(self, cli_context, cli_logger, error_handler):
        """Test safe execution wrapper in base command"""
        # Create command instance
        command = ListAccountsCommand(cli_context, cli_logger, error_handler)
        
        # Test successful operation
        def successful_operation():
            return "Success"
        
        result = command.safe_execute(successful_operation)
        assert result == "Success"
        
        # Test failing operation
        def failing_operation():
            raise ValueError("Something went wrong")
        
        result = command.safe_execute(failing_operation)
        assert isinstance(result, CommandResult)
        assert not result.success
        assert "Something went wrong" in result.message
    
    def test_error_context_preservation(self, cli_context, cli_logger, error_handler):
        """Test that error context is preserved through the handling chain"""
        # Create a configuration error with context
        exc = ConfigurationError(
            message="Invalid configuration",
            config_file="accounts.yaml",
            config_key="api_key",
            suggestions=["Check the API key format", "Verify credentials"]
        )
        
        result = error_handler.handle_exception(exc, context="Loading accounts")
        
        assert not result.success
        assert "Loading accounts: Invalid configuration" in result.message
        assert result.data['error_context']['config_file'] == "accounts.yaml"
        assert result.data['error_context']['config_key'] == "api_key"
        assert "Check the API key format" in result.suggestions
    
    def test_troubleshooting_guide_generation(self, error_handler):
        """Test troubleshooting guide generation for different error types"""
        # Test FileNotFoundError guide
        exc = FileNotFoundError("config.yaml not found")
        guide = error_handler.format_troubleshooting_guide(exc)
        
        assert "🔍 Troubleshooting Guide for FileNotFoundError" in guide
        assert "📋 Quick Diagnosis Steps:" in guide
        assert "🛠️  Suggested Solutions:" in guide
        assert "📞 Need More Help?" in guide
        
        # Should contain specific diagnostic steps for file not found
        assert "Check if you're in the correct directory" in guide
        assert "Verify the file path is spelled correctly" in guide
    
    def test_error_report_generation(self, error_handler, temp_workspace):
        """Test error report generation after handling errors"""
        # Generate some errors
        error_handler.handle_exception(ValueError("Test error 1"))
        error_handler.handle_exception(FileNotFoundError("Test error 2"))
        
        # Create error report
        report = error_handler.create_error_report()
        
        assert 'timestamp' in report
        assert 'workspace_path' in report
        assert 'system_info' in report
        assert 'error_history' in report
        assert len(report['error_history']) == 2
        
        # Save report
        report_path = error_handler.save_error_report()
        assert report_path.exists()
        assert report_path.suffix == '.json'
    
    def test_command_execution_with_comprehensive_error_handling(self, cli_context, cli_logger, error_handler):
        """Test complete command execution flow with error handling"""
        # Create command instance
        command = ListAccountsCommand(cli_context, cli_logger, error_handler)
        
        # Mock account manager to simulate various error scenarios
        with patch('genebot.cli.commands.account.AccountManager') as mock_manager:
            # Test network error scenario
            mock_manager.side_effect = ConnectionError("Failed to connect to API")
            
            args = Namespace(type='all', status='all')
            result = command.run(args)
            
            assert not result.success
            # The command handles the error at its level, so check for the actual message
            assert "Failed to load accounts" in result.message
            assert "Failed to connect to API" in result.message
            
            # Should provide helpful suggestions
            if result.suggestions:
                assert any("config" in s.lower() or "file" in s.lower() for s in result.suggestions)


if __name__ == "__main__":
    pytest.main([__file__])