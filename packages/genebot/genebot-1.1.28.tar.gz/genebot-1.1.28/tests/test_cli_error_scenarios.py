"""
CLI Error Scenarios and Recovery Testing
=======================================

Comprehensive error scenario testing for CLI error handling, recovery procedures,
and user guidance validation.
"""

import pytest
import tempfile
import os
import sys
import subprocess
import yaml
import json
import sqlite3
import signal
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ErrorScenarioTestFramework:
    """Framework for testing error scenarios and recovery procedures"""
    
    def __init__(self):
        self.temp_workspace = None
        self.error_scenarios = {}
        
    def setup(self):
        """Set up error scenario testing environment"""
        self.temp_workspace = Path(tempfile.mkdtemp(prefix="cli_error_test_"))
        
        # Create directory structure
        config_dir = self.temp_workspace / "config"
        logs_dir = self.temp_workspace / "logs"
        data_dir = self.temp_workspace / "data"
        
        for directory in [config_dir, logs_dir, data_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ.update({
            'CONFIG_PATH': str(config_dir),
            'LOGS_PATH': str(logs_dir),
            'WORKSPACE_PATH': str(self.temp_workspace),
            'CLI_ERROR_TEST': 'true'
        })
    
    def teardown(self):
        """Clean up error scenario testing environment"""
        # Clean up environment
        for key in ['CONFIG_PATH', 'LOGS_PATH', 'WORKSPACE_PATH', 'CLI_ERROR_TEST']:
            os.environ.pop(key, None)
        
        # Clean up temporary files
        if self.temp_workspace and self.temp_workspace.exists():
            import shutil
            shutil.rmtree(self.temp_workspace, ignore_errors=True)
    
    def run_cli_command(self, args, expect_failure=False):
        """Run CLI command and capture result"""
        result = subprocess.run(
            [sys.executable, "-m", "genebot.cli"] + args,
            cwd=self.temp_workspace,
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        
        return {
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0,
            'failed_as_expected': (result.returncode != 0) == expect_failure
        }
    
    def create_corrupted_config(self, config_type='accounts'):
        """Create corrupted configuration file"""
        config_dir = Path(os.environ['CONFIG_PATH'])
        
        if config_type == 'accounts':
            config_file = config_dir / "accounts.yaml"
            # Write invalid YAML
            config_file.write_text("invalid: yaml: content: [unclosed")
        elif config_type == 'trading_bot':
            config_file = config_dir / "trading_bot_config.yaml"
            # Write invalid JSON-like content
            config_file.write_text('{"invalid": json, "missing": quote}')
        
        return config_file
    
    def create_valid_config(self, config_type='accounts'):
        """Create valid configuration file"""
        config_dir = Path(os.environ['CONFIG_PATH'])
        
        if config_type == 'accounts':
            config_file = config_dir / "accounts.yaml"
            config = {
                'crypto_exchanges': {
                    'test-exchange': {
                        'name': 'test-exchange',
                        'exchange_type': 'binance',
                        'enabled': True,
                        'sandbox': True
                    }
                },
                'forex_brokers': {}
            }
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
        
        return config_file
    
    def simulate_permission_error(self, path):
        """Simulate permission denied error"""
        if isinstance(path, str):
            path = Path(path)
        
        # Make directory/file read-only
        if path.is_dir():
            path.chmod(0o444)
        else:
            path.chmod(0o444)
        
        return path
    
    def restore_permissions(self, path):
        """Restore normal permissions"""
        if isinstance(path, str):
            path = Path(path)
        
        if path.is_dir():
            path.chmod(0o755)
        else:
            path.chmod(0o644)


@pytest.fixture
def error_framework():
    """Pytest fixture for error scenario testing framework"""
    framework = ErrorScenarioTestFramework()
    framework.setup()
    try:
        yield framework
    finally:
        framework.teardown()


class TestConfigurationErrors:
    """Test configuration-related error scenarios"""
    
    def test_missing_accounts_config(self, error_framework):
        """Test handling of missing accounts configuration file"""
        # Don't create accounts.yaml
        result = error_framework.run_cli_command(['list-accounts'], expect_failure=True)
        
        assert not result['success']
        assert result['failed_as_expected']
        
        # Should provide helpful error message
        error_output = result['stderr'].lower()
        assert any(keyword in error_output for keyword in [
            'configuration', 'not found', 'missing', 'accounts'
        ]), f"Error message not helpful: {result['stderr']}"
        
        # Should suggest solution
        assert any(keyword in error_output for keyword in [
            'init-config', 'create', 'setup'
        ]), f"No solution suggested: {result['stderr']}"
    
    def test_corrupted_accounts_config(self, error_framework):
        """Test handling of corrupted accounts configuration"""
        error_framework.create_corrupted_config('accounts')
        
        result = error_framework.run_cli_command(['list-accounts'], expect_failure=True)
        
        assert not result['success']
        assert result['failed_as_expected']
        
        # Should identify YAML parsing error
        error_output = result['stderr'].lower()
        assert any(keyword in error_output for keyword in [
            'yaml', 'parse', 'syntax', 'invalid'
        ]), f"YAML error not identified: {result['stderr']}"
    
    def test_empty_accounts_config(self, error_framework):
        """Test handling of empty accounts configuration"""
        config_dir = Path(os.environ['CONFIG_PATH'])
        accounts_file = config_dir / "accounts.yaml"
        accounts_file.write_text("")  # Empty file
        
        result = error_framework.run_cli_command(['list-accounts'])
        
        # Should handle gracefully (empty config is valid)
        if not result['success']:
            # If it fails, should provide clear message
            assert 'empty' in result['stderr'].lower() or 'no accounts' in result['stderr'].lower()
    
    def test_invalid_account_structure(self, error_framework):
        """Test handling of invalid account configuration structure"""
        config_dir = Path(os.environ['CONFIG_PATH'])
        accounts_file = config_dir / "accounts.yaml"
        
        # Create config with invalid structure
        invalid_config = {
            'invalid_section': {
                'test': 'data'
            },
            'crypto_exchanges': 'this_should_be_a_dict'
        }
        
        with open(accounts_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        result = error_framework.run_cli_command(['list-accounts'], expect_failure=True)
        
        assert not result['success']
        # Should identify structure validation error
        error_output = result['stderr'].lower()
        assert any(keyword in error_output for keyword in [
            'structure', 'format', 'invalid', 'validation'
        ]), f"Structure error not identified: {result['stderr']}"
    
    def test_missing_required_fields(self, error_framework):
        """Test handling of missing required fields in configuration"""
        config_dir = Path(os.environ['CONFIG_PATH'])
        accounts_file = config_dir / "accounts.yaml"
        
        # Create config with missing required fields
        incomplete_config = {
            'crypto_exchanges': {
                'incomplete-exchange': {
                    'name': 'incomplete-exchange',
                    # Missing exchange_type, enabled, etc.
                }
            }
        }
        
        with open(accounts_file, 'w') as f:
            yaml.dump(incomplete_config, f)
        
        result = error_framework.run_cli_command(['validate-accounts'], expect_failure=True)
        
        if not result['success']:
            # Should identify missing fields
            error_output = result['stderr'].lower()
            assert any(keyword in error_output for keyword in [
                'missing', 'required', 'field', 'exchange_type'
            ]), f"Missing field error not identified: {result['stderr']}"


class TestPermissionErrors:
    """Test permission-related error scenarios"""
    
    def test_config_directory_permission_denied(self, error_framework):
        """Test handling of permission denied on config directory"""
        config_dir = Path(os.environ['CONFIG_PATH'])
        error_framework.create_valid_config('accounts')
        
        # Make config directory read-only
        error_framework.simulate_permission_error(config_dir)
        
        try:
            result = error_framework.run_cli_command([
                'add-crypto', '--name', 'permission-test', 
                '--exchange-type', 'binance', '--mode', 'demo'
            ], expect_failure=True)
            
            assert not result['success']
            assert result['failed_as_expected']
            
            # Should identify permission error
            error_output = result['stderr'].lower()
            assert any(keyword in error_output for keyword in [
                'permission', 'denied', 'access', 'write'
            ]), f"Permission error not identified: {result['stderr']}"
            
            # Should suggest solution
            assert any(keyword in error_output for keyword in [
                'chmod', 'permission', 'access'
            ]) or len(result['stderr']) > 0
        
        finally:
            # Restore permissions for cleanup
            error_framework.restore_permissions(config_dir)
    
    def test_config_file_permission_denied(self, error_framework):
        """Test handling of permission denied on config file"""
        accounts_file = error_framework.create_valid_config('accounts')
        
        # Make accounts file read-only
        error_framework.simulate_permission_error(accounts_file)
        
        try:
            result = error_framework.run_cli_command([
                'add-crypto', '--name', 'permission-test',
                '--exchange-type', 'binance', '--mode', 'demo'
            ], expect_failure=True)
            
            assert not result['success']
            
            # Should identify file permission error
            error_output = result['stderr'].lower()
            assert any(keyword in error_output for keyword in [
                'permission', 'denied', 'read-only', 'write'
            ]), f"File permission error not identified: {result['stderr']}"
        
        finally:
            # Restore permissions
            error_framework.restore_permissions(accounts_file)
    
    def test_logs_directory_permission_denied(self, error_framework):
        """Test handling of permission denied on logs directory"""
        logs_dir = Path(os.environ['LOGS_PATH'])
        error_framework.create_valid_config('accounts')
        
        # Make logs directory read-only
        error_framework.simulate_permission_error(logs_dir)
        
        try:
            result = error_framework.run_cli_command(['list-accounts'])
            
            # Command might succeed but with logging warnings
            if not result['success']:
                error_output = result['stderr'].lower()
                assert 'log' in error_output or 'permission' in error_output
        
        finally:
            # Restore permissions
            error_framework.restore_permissions(logs_dir)


class TestNetworkErrors:
    """Test network-related error scenarios"""
    
    def test_connection_timeout(self, error_framework):
        """Test handling of connection timeout errors"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.account_validator.RealAccountValidator') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate_account.side_effect = ConnectionError("Connection timed out")
            mock_validator.return_value = mock_instance
            
            result = error_framework.run_cli_command(['validate-accounts'])
            
            # Should handle gracefully
            if not result['success']:
                error_output = result['stderr'].lower()
                assert any(keyword in error_output for keyword in [
                    'connection', 'timeout', 'network', 'unreachable'
                ]), f"Network error not identified: {result['stderr']}"
    
    def test_dns_resolution_failure(self, error_framework):
        """Test handling of DNS resolution failures"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.account_validator.RealAccountValidator') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate_account.side_effect = OSError("Name or service not known")
            mock_validator.return_value = mock_instance
            
            result = error_framework.run_cli_command(['validate-accounts'])
            
            if not result['success']:
                error_output = result['stderr'].lower()
                assert any(keyword in error_output for keyword in [
                    'dns', 'resolution', 'name', 'service', 'network'
                ]), f"DNS error not identified: {result['stderr']}"
    
    def test_api_authentication_failure(self, error_framework):
        """Test handling of API authentication failures"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.account_validator.RealAccountValidator') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate_account.return_value = {
                'connected': False,
                'authenticated': False,
                'error': 'Invalid API credentials'
            }
            mock_validator.return_value = mock_instance
            
            result = error_framework.run_cli_command(['validate-accounts'])
            
            # Should report authentication failure clearly
            output = result['stdout'] + result['stderr']
            assert any(keyword in output.lower() for keyword in [
                'authentication', 'credentials', 'invalid', 'api'
            ]), f"Authentication error not reported: {output}"
    
    def test_rate_limit_exceeded(self, error_framework):
        """Test handling of API rate limit errors"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.account_validator.RealAccountValidator') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate_account.side_effect = Exception("Rate limit exceeded")
            mock_validator.return_value = mock_instance
            
            result = error_framework.run_cli_command(['validate-accounts'])
            
            if not result['success']:
                error_output = result['stderr'].lower()
                assert any(keyword in error_output for keyword in [
                    'rate', 'limit', 'exceeded', 'throttle'
                ]), f"Rate limit error not identified: {result['stderr']}"


class TestDatabaseErrors:
    """Test database-related error scenarios"""
    
    def test_database_connection_failure(self, error_framework):
        """Test handling of database connection failures"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.data_manager.RealDataManager') as mock_dm:
            mock_instance = Mock()
            mock_instance.get_recent_trades.side_effect = Exception("Database connection failed")
            mock_dm.return_value = mock_instance
            
            result = error_framework.run_cli_command(['trades'], expect_failure=True)
            
            assert not result['success']
            
            error_output = result['stderr'].lower()
            assert any(keyword in error_output for keyword in [
                'database', 'connection', 'failed'
            ]), f"Database error not identified: {result['stderr']}"
    
    def test_corrupted_database(self, error_framework):
        """Test handling of corrupted database"""
        # Create corrupted database file
        data_dir = Path(os.environ['WORKSPACE_PATH']) / "data"
        data_dir.mkdir(exist_ok=True)
        db_file = data_dir / "trading_bot.db"
        
        # Write invalid content to database file
        db_file.write_text("This is not a valid SQLite database")
        
        with patch('genebot.cli.utils.data_manager.RealDataManager') as mock_dm:
            mock_instance = Mock()
            mock_instance.get_recent_trades.side_effect = sqlite3.DatabaseError("Database disk image is malformed")
            mock_dm.return_value = mock_instance
            
            result = error_framework.run_cli_command(['trades'], expect_failure=True)
            
            assert not result['success']
            
            error_output = result['stderr'].lower()
            assert any(keyword in error_output for keyword in [
                'database', 'corrupted', 'malformed', 'disk'
            ]), f"Database corruption not identified: {result['stderr']}"
    
    def test_database_locked(self, error_framework):
        """Test handling of database lock errors"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.data_manager.RealDataManager') as mock_dm:
            mock_instance = Mock()
            mock_instance.get_recent_trades.side_effect = sqlite3.OperationalError("Database is locked")
            mock_dm.return_value = mock_instance
            
            result = error_framework.run_cli_command(['trades'], expect_failure=True)
            
            if not result['success']:
                error_output = result['stderr'].lower()
                assert any(keyword in error_output for keyword in [
                    'database', 'locked', 'busy'
                ]), f"Database lock error not identified: {result['stderr']}"


class TestProcessErrors:
    """Test process-related error scenarios"""
    
    def test_bot_process_not_found(self, error_framework):
        """Test handling when bot process is not found"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
            mock_instance = Mock()
            mock_instance.get_bot_status.return_value = {
                'running': False,
                'pid': None,
                'error': 'Process not found'
            }
            mock_pm.return_value = mock_instance
            
            result = error_framework.run_cli_command(['status'])
            
            # Should handle gracefully and report status
            output = result['stdout'] + result['stderr']
            assert any(keyword in output.lower() for keyword in [
                'not running', 'stopped', 'not found'
            ]), f"Process status not reported: {output}"
    
    def test_bot_start_failure(self, error_framework):
        """Test handling of bot start failures"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
            mock_instance = Mock()
            mock_instance.start_bot.return_value = {
                'success': False,
                'error': 'Failed to start bot: Configuration error'
            }
            mock_pm.return_value = mock_instance
            
            result = error_framework.run_cli_command(['start'], expect_failure=True)
            
            assert not result['success']
            
            error_output = result['stderr'].lower()
            assert any(keyword in error_output for keyword in [
                'failed', 'start', 'configuration'
            ]), f"Start failure not reported: {result['stderr']}"
    
    def test_bot_stop_failure(self, error_framework):
        """Test handling of bot stop failures"""
        error_framework.create_valid_config('accounts')
        
        with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
            mock_instance = Mock()
            mock_instance.stop_bot.return_value = {
                'success': False,
                'error': 'Process not responding'
            }
            mock_pm.return_value = mock_instance
            
            result = error_framework.run_cli_command(['stop'], expect_failure=True)
            
            if not result['success']:
                error_output = result['stderr'].lower()
                assert any(keyword in error_output for keyword in [
                    'failed', 'stop', 'not responding'
                ]), f"Stop failure not reported: {result['stderr']}"


class TestRecoveryProcedures:
    """Test automated recovery procedures"""
    
    def test_configuration_recovery(self, error_framework):
        """Test configuration recovery procedures"""
        # Create corrupted config
        error_framework.create_corrupted_config('accounts')
        
        # Test recovery command
        result = error_framework.run_cli_command(['repair-config', '--auto'])
        
        # Should attempt recovery
        if result['success']:
            # Verify config was repaired
            config_dir = Path(os.environ['CONFIG_PATH'])
            accounts_file = config_dir / "accounts.yaml"
            
            if accounts_file.exists():
                try:
                    with open(accounts_file, 'r') as f:
                        yaml.safe_load(f)  # Should not raise exception
                except yaml.YAMLError:
                    pytest.fail("Configuration not properly recovered")
    
    def test_system_diagnostics(self, error_framework):
        """Test system diagnostics and recovery suggestions"""
        result = error_framework.run_cli_command(['diagnostics'])
        
        # Should provide system information
        output = result['stdout'] + result['stderr']
        assert len(output) > 0, "Diagnostics should provide output"
        
        # Should check various system components
        if result['success']:
            output_lower = output.lower()
            # Should mention checking various components
            expected_checks = ['config', 'permission', 'directory']
            found_checks = sum(1 for check in expected_checks if check in output_lower)
            assert found_checks > 0, "Diagnostics should check system components"
    
    def test_backup_and_restore(self, error_framework):
        """Test backup and restore functionality"""
        # Create valid config
        error_framework.create_valid_config('accounts')
        
        # Create backup
        result = error_framework.run_cli_command(['config-backup'])
        
        if result['success']:
            # Verify backup was created
            workspace = Path(os.environ['WORKSPACE_PATH'])
            backup_files = list(workspace.glob("**/backup*")) + list(workspace.glob("**/*.backup"))
            
            # Should create some form of backup
            assert len(backup_files) > 0 or 'backup' in result['stdout'].lower()
    
    def test_error_reporting(self, error_framework):
        """Test error reporting and logging"""
        # Cause an error
        result = error_framework.run_cli_command(['invalid-command'], expect_failure=True)
        
        assert not result['success']
        
        # Should provide helpful error message
        error_output = result['stderr']
        assert len(error_output) > 0, "Should provide error message"
        
        # Should suggest help or valid commands
        assert any(keyword in error_output.lower() for keyword in [
            'help', 'usage', 'command', 'available'
        ]), f"Should suggest help: {error_output}"


class TestConcurrentErrorHandling:
    """Test error handling under concurrent conditions"""
    
    def test_concurrent_config_access_errors(self, error_framework):
        """Test handling of concurrent configuration access errors"""
        error_framework.create_valid_config('accounts')
        
        def run_command():
            return error_framework.run_cli_command([
                'add-crypto', '--name', f'concurrent-{threading.current_thread().ident}',
                '--exchange-type', 'binance', '--mode', 'demo', '--force'
            ])
        
        # Run multiple commands concurrently
        threads = []
        results = []
        
        for i in range(3):
            thread = threading.Thread(target=lambda: results.append(run_command()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # At least one should succeed, others may fail gracefully
        success_count = sum(1 for r in results if r['success'])
        assert success_count >= 1, "At least one concurrent operation should succeed"
        
        # Failed operations should have meaningful error messages
        for result in results:
            if not result['success']:
                assert len(result['stderr']) > 0, "Failed operations should have error messages"
    
    def test_resource_exhaustion_handling(self, error_framework):
        """Test handling of resource exhaustion scenarios"""
        error_framework.create_valid_config('accounts')
        
        # Simulate resource exhaustion with mock
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            result = error_framework.run_cli_command(['config-backup'], expect_failure=True)
            
            if not result['success']:
                error_output = result['stderr'].lower()
                assert any(keyword in error_output for keyword in [
                    'space', 'disk', 'resource', 'no space'
                ]), f"Resource exhaustion not handled: {result['stderr']}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])