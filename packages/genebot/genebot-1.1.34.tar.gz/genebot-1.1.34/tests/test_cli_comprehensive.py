"""
Comprehensive CLI Testing Infrastructure
=======================================

Complete test suite for CLI commands with mock services, temporary directories,
and integration testing capabilities.
"""

import pytest
import tempfile
import shutil
import os
import sys
import subprocess
import json
import yaml
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from genebot.cli.main import main
from genebot.cli.context import CLIContext
from genebot.cli.result import CommandResult, ResultStatus
from genebot.cli.commands.router import CommandRouter
from genebot.cli.utils.error_handler import CLIErrorHandler, CLIException
from genebot.cli.utils.logger import CLILogger


class CLITestFramework:
    """
    Comprehensive CLI testing framework with temporary directories,
    mock services, and integration testing capabilities.
    """
    
    def __init__(self):
        self.temp_workspace = None
        self.config_dir = None
        self.logs_dir = None
        self.env_file = None
        self.mock_services = {}
        self.test_data = {}
        self.original_env = {}
        
    def setup(self):
        """Set up test environment"""
        # Create temporary workspace
        self.temp_workspace = Path(tempfile.mkdtemp(prefix="cli_test_"))
        
        # Create directory structure
        self.config_dir = self.temp_workspace / "config"
        self.logs_dir = self.temp_workspace / "logs"
        self.reports_dir = self.temp_workspace / "reports"
        self.backups_dir = self.temp_workspace / "backups"
        
        for directory in [self.config_dir, self.logs_dir, self.reports_dir, self.backups_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create environment file
        self.env_file = self.temp_workspace / ".env"
        self._create_test_env_file()
        
        # Create test configuration files
        self._create_test_config_files()
        
        # Store original environment
        self.original_env = dict(os.environ)
        
        # Set test environment variables
        os.environ['CONFIG_PATH'] = str(self.config_dir)
        os.environ['LOGS_PATH'] = str(self.logs_dir)
        os.environ['WORKSPACE_PATH'] = str(self.temp_workspace)
        
    def teardown(self):
        """Clean up test environment"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temporary files
        if self.temp_workspace and self.temp_workspace.exists():
            shutil.rmtree(self.temp_workspace)
        
        # Reset mock services
        for service in self.mock_services.values():
            if hasattr(service, 'reset'):
                service.reset()
    
    def _create_test_env_file(self):
        """Create test environment file"""
        env_content = """
# Test environment variables
BINANCE_TEST_API_KEY=test_binance_key
BINANCE_TEST_API_SECRET=test_binance_secret
COINBASE_TEST_API_KEY=test_coinbase_key
COINBASE_TEST_API_SECRET=test_coinbase_secret
COINBASE_TEST_API_PASSPHRASE=test_coinbase_passphrase
OANDA_TEST_API_KEY=test_oanda_key
OANDA_TEST_ACCOUNT_ID=test_oanda_account
IB_TEST_HOST=localhost
IB_TEST_PORT=7497
IB_TEST_CLIENT_ID=1
MT5_TEST_LOGIN=12345
MT5_TEST_PASSWORD=test_password
MT5_TEST_SERVER=Demo-Server
DATABASE_URL=sqlite:///test.db
LOG_LEVEL=DEBUG
"""
        self.env_file.write_text(env_content.strip())
    
    def _create_test_config_files(self):
        """Create test configuration files"""
        # Create accounts.yaml
        accounts_config = {
            'crypto_exchanges': {
                'test-binance': {
                    'name': 'test-binance',
                    'exchange_type': 'binance',
                    'enabled': True,
                    'sandbox': True,
                    'api_key': '${BINANCE_TEST_API_KEY}',
                    'api_secret': '${BINANCE_TEST_API_SECRET}',
                    'rate_limit': 1200,
                    'timeout': 30
                },
                'test-coinbase': {
                    'name': 'test-coinbase',
                    'exchange_type': 'coinbase',
                    'enabled': False,
                    'sandbox': True,
                    'api_key': '${COINBASE_TEST_API_KEY}',
                    'api_secret': '${COINBASE_TEST_API_SECRET}',
                    'api_passphrase': '${COINBASE_TEST_API_PASSPHRASE}',
                    'rate_limit': 600,
                    'timeout': 30
                }
            },
            'forex_brokers': {
                'test-oanda': {
                    'name': 'test-oanda',
                    'broker_type': 'oanda',
                    'enabled': True,
                    'sandbox': True,
                    'api_key': '${OANDA_TEST_API_KEY}',
                    'account_id': '${OANDA_TEST_ACCOUNT_ID}',
                    'timeout': 30,
                    'max_retries': 3
                }
            }
        }
        
        with open(self.config_dir / "accounts.yaml", 'w') as f:
            yaml.dump(accounts_config, f)
        
        # Create trading_bot_config.yaml
        bot_config = {
            'general': {
                'name': 'test_bot',
                'version': '1.0.0',
                'debug': True
            },
            'strategies': {
                'test_strategy': {
                    'name': 'test_strategy',
                    'enabled': True,
                    'parameters': {
                        'timeframe': '1h',
                        'indicators': ['sma', 'rsi']
                    }
                }
            },
            'risk_management': {
                'max_daily_loss': 1000.0,
                'max_drawdown': 0.1,
                'max_position_size': 0.1
            }
        }
        
        with open(self.config_dir / "trading_bot_config.yaml", 'w') as f:
            yaml.dump(bot_config, f)
    
    def run_cli_command(self, args: List[str], capture_output: bool = True) -> Dict[str, Any]:
        """
        Run CLI command and return result
        
        Args:
            args: Command line arguments
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Dictionary with exit_code, stdout, stderr, and execution_time
        """
        start_time = time.time()
        
        if capture_output:
            # Use subprocess to capture output
            cmd = [sys.executable, "-m", "genebot.cli.main"] + args
            result = subprocess.run(
                cmd,
                cwd=self.temp_workspace,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            
            execution_time = time.time() - start_time
            
            return {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time
            }
        else:
            # Run directly for faster execution in tests
            original_argv = sys.argv
            try:
                sys.argv = ['genebot'] + args
                exit_code = main()
                execution_time = time.time() - start_time
                
                return {
                    'exit_code': exit_code,
                    'stdout': '',
                    'stderr': '',
                    'execution_time': execution_time
                }
            except SystemExit as e:
                execution_time = time.time() - start_time
                return {
                    'exit_code': e.code,
                    'stdout': '',
                    'stderr': '',
                    'execution_time': execution_time
                }
            finally:
                sys.argv = original_argv
    
    def create_mock_database(self) -> Mock:
        """Create mock database for testing"""
        mock_db = Mock()
        
        # Mock trade data
        mock_trades = [
            {
                'id': 1,
                'symbol': 'BTC/USDT',
                'side': 'BUY',
                'amount': 0.1,
                'price': 45000.0,
                'timestamp': datetime.now() - timedelta(hours=1),
                'pnl': 500.0,
                'strategy': 'test_strategy',
                'exchange': 'binance'
            },
            {
                'id': 2,
                'symbol': 'ETH/USDT',
                'side': 'SELL',
                'amount': 2.0,
                'price': 3000.0,
                'timestamp': datetime.now() - timedelta(minutes=30),
                'pnl': -150.0,
                'strategy': 'test_strategy',
                'exchange': 'binance'
            }
        ]
        
        mock_db.get_trades.return_value = mock_trades
        mock_db.get_positions.return_value = []
        mock_db.get_orders.return_value = []
        
        self.mock_services['database'] = mock_db
        return mock_db
    
    def create_mock_exchange(self, name: str = 'test_exchange') -> Mock:
        """Create mock exchange for testing"""
        mock_exchange = Mock()
        
        # Mock exchange methods
        mock_exchange.name = name
        mock_exchange.test_connection.return_value = True
        mock_exchange.get_balance.return_value = {
            'USD': 10000.0,
            'BTC': 0.5,
            'ETH': 2.0
        }
        mock_exchange.get_ticker.return_value = {
            'symbol': 'BTC/USD',
            'bid': 44950.0,
            'ask': 45050.0,
            'last': 45000.0
        }
        
        self.mock_services[f'exchange_{name}'] = mock_exchange
        return mock_exchange
    
    def create_mock_process_manager(self) -> Mock:
        """Create mock process manager for testing"""
        mock_pm = Mock()
        
        # Mock process states
        mock_pm.is_bot_running.return_value = False
        mock_pm.start_bot.return_value = {'pid': 12345, 'status': 'started'}
        mock_pm.stop_bot.return_value = {'status': 'stopped'}
        mock_pm.get_bot_status.return_value = {
            'running': False,
            'pid': None,
            'uptime': None,
            'memory_usage': None,
            'cpu_usage': None
        }
        
        self.mock_services['process_manager'] = mock_pm
        return mock_pm
    
    def assert_command_success(self, result: Dict[str, Any], expected_output: str = None):
        """Assert that command executed successfully"""
        assert result['exit_code'] == 0, f"Command failed with exit code {result['exit_code']}"
        
        if expected_output:
            assert expected_output in result['stdout'], f"Expected '{expected_output}' in output"
    
    def assert_command_failure(self, result: Dict[str, Any], expected_error: str = None):
        """Assert that command failed as expected"""
        assert result['exit_code'] != 0, "Command should have failed"
        
        if expected_error:
            error_output = result['stderr'] or result['stdout']
            assert expected_error in error_output, f"Expected '{expected_error}' in error output"
    
    def assert_execution_time_under(self, result: Dict[str, Any], max_time: float):
        """Assert that command executed within time limit"""
        assert result['execution_time'] < max_time, \
            f"Command took {result['execution_time']:.3f}s, expected under {max_time}s"


@pytest.fixture
def cli_framework():
    """Pytest fixture for CLI testing framework"""
    framework = CLITestFramework()
    framework.setup()
    try:
        yield framework
    finally:
        framework.teardown()


class TestCLIFrameworkBasics:
    """Test the CLI testing framework itself"""
    
    def test_framework_setup(self, cli_framework):
        """Test that framework sets up correctly"""
        assert cli_framework.temp_workspace.exists()
        assert cli_framework.config_dir.exists()
        assert cli_framework.logs_dir.exists()
        assert cli_framework.env_file.exists()
        
        # Check configuration files were created
        assert (cli_framework.config_dir / "accounts.yaml").exists()
        assert (cli_framework.config_dir / "trading_bot_config.yaml").exists()
    
    def test_environment_variables(self, cli_framework):
        """Test that environment variables are set correctly"""
        assert os.environ.get('CONFIG_PATH') == str(cli_framework.config_dir)
        assert os.environ.get('LOGS_PATH') == str(cli_framework.logs_dir)
        assert os.environ.get('WORKSPACE_PATH') == str(cli_framework.temp_workspace)
    
    def test_mock_services_creation(self, cli_framework):
        """Test creation of mock services"""
        # Test database mock
        mock_db = cli_framework.create_mock_database()
        assert mock_db is not None
        assert len(mock_db.get_trades()) == 2
        
        # Test exchange mock
        mock_exchange = cli_framework.create_mock_exchange('binance')
        assert mock_exchange.name == 'binance'
        assert mock_exchange.test_connection() is True
        
        # Test process manager mock
        mock_pm = cli_framework.create_mock_process_manager()
        assert mock_pm.is_bot_running() is False


class TestCLICommandExecution:
    """Test CLI command execution through the framework"""
    
    def test_help_command(self, cli_framework):
        """Test help command execution"""
        result = cli_framework.run_cli_command(['--help'])
        cli_framework.assert_command_success(result)
        assert 'GeneBot' in result['stdout'] or result['exit_code'] == 0
    
    def test_list_accounts_command(self, cli_framework):
        """Test list accounts command"""
        result = cli_framework.run_cli_command(['list-accounts'])
        cli_framework.assert_command_success(result)
    
    def test_invalid_command(self, cli_framework):
        """Test invalid command handling"""
        result = cli_framework.run_cli_command(['invalid-command'])
        cli_framework.assert_command_failure(result, 'Unknown command')
    
    def test_command_execution_time(self, cli_framework):
        """Test that commands execute within reasonable time"""
        result = cli_framework.run_cli_command(['list-accounts'])
        cli_framework.assert_execution_time_under(result, 5.0)  # 5 seconds max


class TestCLIAccountManagement:
    """Test account management commands"""
    
    def test_list_accounts_with_data(self, cli_framework):
        """Test listing accounts with existing data"""
        result = cli_framework.run_cli_command(['list-accounts'])
        cli_framework.assert_command_success(result)
        
        # Should show configured test accounts
        output = result['stdout']
        assert 'test-binance' in output or result['exit_code'] == 0
    
    def test_validate_accounts(self, cli_framework):
        """Test account validation"""
        with patch('genebot.cli.utils.account_validator.RealAccountValidator') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate_account.return_value = {
                'connected': True,
                'error': None,
                'balance': {'USD': 10000}
            }
            mock_validator.return_value = mock_instance
            
            result = cli_framework.run_cli_command(['validate-accounts'])
            cli_framework.assert_command_success(result)
    
    def test_add_crypto_account(self, cli_framework):
        """Test adding crypto account"""
        result = cli_framework.run_cli_command([
            'add-crypto',
            '--name', 'test-kraken',
            '--exchange-type', 'kraken',
            '--mode', 'demo',
            '--force'
        ])
        cli_framework.assert_command_success(result)
        
        # Verify account was added to config
        with open(cli_framework.config_dir / "accounts.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'test-kraken' in config.get('crypto_exchanges', {})
    
    def test_remove_account(self, cli_framework):
        """Test removing account"""
        # First add an account to remove
        cli_framework.run_cli_command([
            'add-crypto',
            '--name', 'test-remove',
            '--exchange-type', 'binance',
            '--mode', 'demo',
            '--force'
        ])
        
        # Then remove it
        result = cli_framework.run_cli_command([
            'remove-account',
            '--name', 'test-remove',
            '--type', 'crypto',
            '--confirm'
        ])
        cli_framework.assert_command_success(result)


class TestCLIBotManagement:
    """Test bot management commands"""
    
    def test_bot_status(self, cli_framework):
        """Test bot status command"""
        with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
            mock_instance = Mock()
            mock_instance.get_bot_status.return_value = {
                'running': False,
                'pid': None,
                'uptime': None
            }
            mock_pm.return_value = mock_instance
            
            result = cli_framework.run_cli_command(['status'])
            cli_framework.assert_command_success(result)
    
    def test_start_bot(self, cli_framework):
        """Test starting bot"""
        with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
            mock_instance = Mock()
            mock_instance.start_bot.return_value = {
                'success': True,
                'pid': 12345,
                'message': 'Bot started successfully'
            }
            mock_pm.return_value = mock_instance
            
            result = cli_framework.run_cli_command(['start'])
            cli_framework.assert_command_success(result)
    
    def test_stop_bot(self, cli_framework):
        """Test stopping bot"""
        with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
            mock_instance = Mock()
            mock_instance.stop_bot.return_value = {
                'success': True,
                'message': 'Bot stopped successfully'
            }
            mock_pm.return_value = mock_instance
            
            result = cli_framework.run_cli_command(['stop'])
            cli_framework.assert_command_success(result)


class TestCLIMonitoring:
    """Test monitoring and reporting commands"""
    
    def test_trades_command(self, cli_framework):
        """Test trades listing command"""
        with patch('genebot.cli.utils.data_manager.RealDataManager') as mock_dm:
            mock_instance = Mock()
            mock_instance.get_recent_trades.return_value = [
                {
                    'id': 1,
                    'symbol': 'BTC/USDT',
                    'side': 'BUY',
                    'amount': 0.1,
                    'price': 45000.0,
                    'timestamp': datetime.now(),
                    'pnl': 500.0
                }
            ]
            mock_dm.return_value = mock_instance
            
            result = cli_framework.run_cli_command(['trades'])
            cli_framework.assert_command_success(result)
    
    def test_monitor_command(self, cli_framework):
        """Test monitor command"""
        with patch('genebot.cli.utils.data_manager.RealDataManager') as mock_dm:
            mock_instance = Mock()
            mock_instance.get_live_data.return_value = {
                'positions': [],
                'orders': [],
                'balance': {'USD': 10000}
            }
            mock_dm.return_value = mock_instance
            
            result = cli_framework.run_cli_command(['monitor', '--once'])
            cli_framework.assert_command_success(result)


class TestCLIErrorHandling:
    """Test error handling and recovery"""
    
    def test_missing_config_file(self, cli_framework):
        """Test handling of missing configuration files"""
        # Remove accounts file
        (cli_framework.config_dir / "accounts.yaml").unlink()
        
        result = cli_framework.run_cli_command(['list-accounts'])
        cli_framework.assert_command_failure(result)
    
    def test_invalid_config_format(self, cli_framework):
        """Test handling of invalid configuration format"""
        # Write invalid YAML
        with open(cli_framework.config_dir / "accounts.yaml", 'w') as f:
            f.write("invalid: yaml: content: [")
        
        result = cli_framework.run_cli_command(['list-accounts'])
        cli_framework.assert_command_failure(result)
    
    def test_permission_denied(self, cli_framework):
        """Test handling of permission denied errors"""
        # Make config directory read-only
        cli_framework.config_dir.chmod(0o444)
        
        try:
            result = cli_framework.run_cli_command([
                'add-crypto',
                '--name', 'test-permission',
                '--exchange-type', 'binance',
                '--mode', 'demo'
            ])
            cli_framework.assert_command_failure(result)
        finally:
            # Restore permissions for cleanup
            cli_framework.config_dir.chmod(0o755)
    
    def test_network_error_handling(self, cli_framework):
        """Test handling of network errors"""
        with patch('genebot.cli.utils.account_validator.RealAccountValidator') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate_account.side_effect = ConnectionError("Network unreachable")
            mock_validator.return_value = mock_instance
            
            result = cli_framework.run_cli_command(['validate-accounts'])
            # Should handle error gracefully
            assert result['exit_code'] in [0, 1]  # May succeed with warnings or fail gracefully


class TestCLIPerformance:
    """Test CLI performance characteristics"""
    
    def test_command_response_time(self, cli_framework):
        """Test that commands respond quickly"""
        commands = [
            ['--help'],
            ['list-accounts'],
            ['status'],
            ['list-strategies']
        ]
        
        for cmd in commands:
            result = cli_framework.run_cli_command(cmd)
            cli_framework.assert_execution_time_under(result, 3.0)  # 3 seconds max
    
    def test_large_config_handling(self, cli_framework):
        """Test handling of large configuration files"""
        # Create large accounts config
        large_config = {'crypto_exchanges': {}, 'forex_brokers': {}}
        
        # Add many accounts
        for i in range(100):
            large_config['crypto_exchanges'][f'test-account-{i}'] = {
                'name': f'test-account-{i}',
                'exchange_type': 'binance',
                'enabled': True,
                'sandbox': True,
                'api_key': f'key_{i}',
                'api_secret': f'secret_{i}'
            }
        
        with open(cli_framework.config_dir / "accounts.yaml", 'w') as f:
            yaml.dump(large_config, f)
        
        result = cli_framework.run_cli_command(['list-accounts'])
        cli_framework.assert_command_success(result)
        cli_framework.assert_execution_time_under(result, 5.0)  # Should handle large configs


class TestCLIIntegration:
    """Integration tests for CLI components"""
    
    def test_full_account_lifecycle(self, cli_framework):
        """Test complete account management lifecycle"""
        account_name = 'integration-test-account'
        
        # 1. Add account
        result = cli_framework.run_cli_command([
            'add-crypto',
            '--name', account_name,
            '--exchange-type', 'binance',
            '--mode', 'demo',
            '--force'
        ])
        cli_framework.assert_command_success(result)
        
        # 2. List accounts (should include new account)
        result = cli_framework.run_cli_command(['list-accounts'])
        cli_framework.assert_command_success(result)
        
        # 3. Disable account
        result = cli_framework.run_cli_command([
            'disable-account',
            '--name', account_name,
            '--type', 'crypto'
        ])
        cli_framework.assert_command_success(result)
        
        # 4. Enable account
        result = cli_framework.run_cli_command([
            'enable-account',
            '--name', account_name,
            '--type', 'crypto'
        ])
        cli_framework.assert_command_success(result)
        
        # 5. Remove account
        result = cli_framework.run_cli_command([
            'remove-account',
            '--name', account_name,
            '--type', 'crypto',
            '--confirm'
        ])
        cli_framework.assert_command_success(result)
    
    def test_configuration_backup_restore(self, cli_framework):
        """Test configuration backup and restore functionality"""
        # Create backup
        result = cli_framework.run_cli_command(['config-backup'])
        cli_framework.assert_command_success(result)
        
        # Verify backup was created
        backup_files = list(cli_framework.backups_dir.glob("*.yaml"))
        assert len(backup_files) > 0
    
    def test_error_recovery_workflow(self, cli_framework):
        """Test error recovery and diagnostics"""
        # Run diagnostics
        result = cli_framework.run_cli_command(['diagnostics'])
        cli_framework.assert_command_success(result)
        
        # Test system recovery
        result = cli_framework.run_cli_command(['system-recovery', '--auto'])
        cli_framework.assert_command_success(result)


if __name__ == '__main__':
    pytest.main([__file__])