"""
Tests for CLI Account Manager
============================

Comprehensive tests for account management operations including
adding, editing, removing accounts and configuration file operations.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml

from genebot.cli.utils.account_manager import AccountManager, AccountInfo
from genebot.cli.utils.error_handler import ConfigurationError
from genebot.cli.result import CommandResult


class TestAccountManager:
    """Test suite for AccountManager class"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary directory for test configuration
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "config"
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.env_file = self.temp_dir / ".env"
        
        # Create test accounts configuration
        self.test_accounts_config = {
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
        
        # Write test configuration
        accounts_file = self.config_path / "accounts.yaml"
        with open(accounts_file, 'w') as f:
            yaml.dump(self.test_accounts_config, f)
        
        # Create test environment file
        with open(self.env_file, 'w') as f:
            f.write("BINANCE_TEST_API_KEY=test_key\n")
            f.write("BINANCE_TEST_API_SECRET=test_secret\n")
            f.write("OANDA_TEST_API_KEY=test_oanda_key\n")
            f.write("OANDA_TEST_ACCOUNT_ID=test_account_id\n")
        
        # Initialize account manager
        self.account_manager = AccountManager(
            config_path=self.config_path,
            env_file=self.env_file
        )
    
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_all_accounts(self):
        """Test getting all configured accounts"""
        accounts = self.account_manager.get_all_accounts()
        
        assert len(accounts) == 2
        
        # Check crypto account
        crypto_account = next((acc for acc in accounts if acc.type == 'crypto'), None)
        assert crypto_account is not None
        assert crypto_account.name == 'test-binance'
        assert crypto_account.exchange_or_broker == 'binance'
        assert crypto_account.enabled is True
        assert crypto_account.sandbox is True
        
        # Check forex account
        forex_account = next((acc for acc in accounts if acc.type == 'forex'), None)
        assert forex_account is not None
        assert forex_account.name == 'test-oanda'
        assert forex_account.exchange_or_broker == 'oanda'
        assert forex_account.enabled is True
        assert forex_account.sandbox is True
    
    def test_get_account_by_name(self):
        """Test getting account by name"""
        # Test existing account
        account = self.account_manager.get_account_by_name('test-binance')
        assert account is not None
        assert account.name == 'test-binance'
        assert account.type == 'crypto'
        
        # Test non-existing account
        account = self.account_manager.get_account_by_name('non-existent')
        assert account is None
    
    def test_account_exists(self):
        """Test checking if account exists"""
        assert self.account_manager.account_exists('test-binance') is True
        assert self.account_manager.account_exists('test-oanda') is True
        assert self.account_manager.account_exists('non-existent') is False
    
    def test_validate_exchange_type(self):
        """Test exchange type validation"""
        assert self.account_manager.validate_exchange_type('binance') is True
        assert self.account_manager.validate_exchange_type('coinbase') is True
        assert self.account_manager.validate_exchange_type('invalid_exchange') is False
    
    def test_validate_broker_type(self):
        """Test broker type validation"""
        assert self.account_manager.validate_broker_type('oanda') is True
        assert self.account_manager.validate_broker_type('ib') is True
        assert self.account_manager.validate_broker_type('invalid_broker') is False
    
    def test_add_crypto_account_success(self):
        """Test successfully adding a crypto account"""
        result = self.account_manager.add_crypto_account(
            exchange_type='kraken',
            name='test-kraken',
            mode='demo',
            enabled=True
        )
        
        assert result.success is True
        assert 'test-kraken' in result.message
        
        # Verify account was added
        account = self.account_manager.get_account_by_name('test-kraken')
        assert account is not None
        assert account.exchange_or_broker == 'kraken'
        assert account.sandbox is True
    
    def test_add_crypto_account_duplicate_name(self):
        """Test adding crypto account with duplicate name"""
        result = self.account_manager.add_crypto_account(
            exchange_type='binance',
            name='test-binance',  # Already exists
            mode='demo'
        )
        
        assert result.success is False
        assert 'already exists' in result.message
    
    def test_add_crypto_account_invalid_exchange(self):
        """Test adding crypto account with invalid exchange"""
        result = self.account_manager.add_crypto_account(
            exchange_type='invalid_exchange',
            name='test-invalid',
            mode='demo'
        )
        
        assert result.success is False
        assert 'Unsupported exchange type' in result.message
    
    def test_add_forex_account_success(self):
        """Test successfully adding a forex account"""
        result = self.account_manager.add_forex_account(
            broker_type='ib',
            name='test-ib',
            mode='demo',
            host='localhost',
            port=7497,
            client_id=1
        )
        
        assert result.success is True
        assert 'test-ib' in result.message
        
        # Verify account was added
        account = self.account_manager.get_account_by_name('test-ib')
        assert account is not None
        assert account.exchange_or_broker == 'ib'
        assert account.sandbox is True
    
    def test_add_forex_account_oanda_specific(self):
        """Test adding OANDA forex account with specific fields"""
        result = self.account_manager.add_forex_account(
            broker_type='oanda',
            name='test-oanda-2',
            mode='live',
            api_key='live_key',
            account_id='live_account',
            max_retries=5
        )
        
        assert result.success is True
        
        # Verify account configuration
        accounts_config = self.account_manager.config_manager.load_accounts_config()
        oanda_config = accounts_config['forex_brokers']['test-oanda-2']
        assert oanda_config['api_key'] == 'live_key'
        assert oanda_config['account_id'] == 'live_account'
        assert oanda_config['max_retries'] == 5
        assert oanda_config['sandbox'] is False  # live mode
    
    def test_add_forex_account_mt5_specific(self):
        """Test adding MT5 forex account with specific fields"""
        result = self.account_manager.add_forex_account(
            broker_type='mt5',
            name='test-mt5',
            mode='demo',
            login='12345',
            password='password',
            server='Demo-Server'
        )
        
        assert result.success is True
        
        # Verify account configuration
        accounts_config = self.account_manager.config_manager.load_accounts_config()
        mt5_config = accounts_config['forex_brokers']['test-mt5']
        assert mt5_config['login'] == '12345'
        assert mt5_config['password'] == 'password'
        assert mt5_config['server'] == 'Demo-Server'
    
    def test_edit_account_success(self):
        """Test successfully editing an account"""
        result = self.account_manager.edit_account(
            name='test-binance',
            enabled=False,
            timeout=60
        )
        
        assert result.success is True
        assert 'updated successfully' in result.message
        
        # Verify changes
        account = self.account_manager.get_account_by_name('test-binance')
        assert account.enabled is False
        
        # Check configuration file
        accounts_config = self.account_manager.config_manager.load_accounts_config()
        binance_config = accounts_config['crypto_exchanges']['test-binance']
        assert binance_config['enabled'] is False
        assert binance_config['timeout'] == 60
    
    def test_edit_account_not_found(self):
        """Test editing non-existent account"""
        result = self.account_manager.edit_account(
            name='non-existent',
            enabled=False
        )
        
        assert result.success is False
        assert 'not found' in result.message
    
    def test_edit_account_no_updates(self):
        """Test editing account with no updates"""
        result = self.account_manager.edit_account(name='test-binance')
        
        assert result.success is False
        assert 'No updates provided' in result.message
    
    def test_edit_account_invalid_field(self):
        """Test editing account with invalid field"""
        result = self.account_manager.edit_account(
            name='test-binance',
            invalid_field='value'
        )
        
        assert result.success is False
        assert 'Unknown field' in result.message
    
    @patch('builtins.input', side_effect=['n'])
    def test_remove_account_cancelled(self, mock_input):
        """Test removing account when user cancels"""
        result = self.account_manager.remove_account('test-binance')
        
        assert result.success is True  # Cancellation is successful operation
        assert 'cancelled' in result.message
        
        # Verify account still exists
        assert self.account_manager.account_exists('test-binance') is True
    
    @patch('builtins.input', side_effect=['y'])
    def test_remove_account_confirmed(self, mock_input):
        """Test removing account when user confirms"""
        result = self.account_manager.remove_account('test-binance')
        
        assert result.success is True
        assert 'removed successfully' in result.message
        
        # Verify account was removed
        assert self.account_manager.account_exists('test-binance') is False
    
    def test_remove_account_with_confirm_flag(self):
        """Test removing account with confirm flag"""
        result = self.account_manager.remove_account('test-binance', confirm=True)
        
        assert result.success is True
        assert 'removed successfully' in result.message
        
        # Verify account was removed
        assert self.account_manager.account_exists('test-binance') is False
    
    def test_remove_account_not_found(self):
        """Test removing non-existent account"""
        result = self.account_manager.remove_account('non-existent', confirm=True)
        
        assert result.success is False
        assert 'not found' in result.message
    
    def test_enable_account(self):
        """Test enabling an account"""
        # First disable the account
        self.account_manager.edit_account('test-binance', enabled=False)
        
        # Then enable it
        result = self.account_manager.enable_account('test-binance')
        
        assert result.success is True
        
        # Verify account is enabled
        account = self.account_manager.get_account_by_name('test-binance')
        assert account.enabled is True
    
    def test_disable_account(self):
        """Test disabling an account"""
        result = self.account_manager.disable_account('test-binance')
        
        assert result.success is True
        
        # Verify account is disabled
        account = self.account_manager.get_account_by_name('test-binance')
        assert account.enabled is False
    
    def test_get_account_statistics(self):
        """Test getting account statistics"""
        stats = self.account_manager.get_account_statistics()
        
        assert stats['total_accounts'] == 2
        assert stats['crypto_accounts'] == 1
        assert stats['forex_accounts'] == 1
        assert stats['enabled_accounts'] == 2
        assert stats['disabled_accounts'] == 0
        assert stats['sandbox_accounts'] == 2
        assert stats['live_accounts'] == 0
        assert 'binance' in stats['exchanges']
        assert 'oanda' in stats['brokers']
    
    def test_export_accounts_config(self):
        """Test exporting accounts configuration"""
        output_file = self.temp_dir / "exported_accounts.yaml"
        
        result = self.account_manager.export_accounts_config(output_file)
        
        assert result.success is True
        assert output_file.exists()
        
        # Verify exported content
        with open(output_file, 'r') as f:
            exported_config = yaml.safe_load(f)
        
        assert 'crypto_exchanges' in exported_config
        assert 'forex_brokers' in exported_config
        
        # Verify sensitive data is redacted
        binance_config = exported_config['crypto_exchanges']['test-binance']
        assert binance_config['api_key'] == '${BINANCE_TEST_API_KEY}'  # Environment variable reference kept
    
    def test_account_info_to_dict(self):
        """Test AccountInfo to_dict conversion"""
        account = AccountInfo(
            name='test-account',
            type='crypto',
            exchange_or_broker='binance',
            enabled=True,
            sandbox=True,
            api_key='test_key',
            api_secret='test_secret',
            additional_fields={'rate_limit': 1200, 'timeout': 30}
        )
        
        account_dict = account.to_dict()
        
        assert account_dict['name'] == 'test-account'
        assert account_dict['enabled'] is True
        assert account_dict['sandbox'] is True
        assert account_dict['exchange_type'] == 'binance'
        assert account_dict['api_key'] == 'test_key'
        assert account_dict['api_secret'] == 'test_secret'
        assert account_dict['rate_limit'] == 1200
        assert account_dict['timeout'] == 30
    
    def test_load_accounts_config_file_not_found(self):
        """Test loading accounts when config file doesn't exist"""
        # Remove accounts file
        accounts_file = self.config_path / "accounts.yaml"
        accounts_file.unlink()
        
        # Should raise ConfigurationError
        with pytest.raises(ConfigurationError):
            self.account_manager.get_all_accounts()
    
    def test_add_coinbase_account_with_passphrase(self):
        """Test adding Coinbase account with API passphrase"""
        result = self.account_manager.add_crypto_account(
            exchange_type='coinbase',
            name='test-coinbase',
            mode='demo',
            api_passphrase='test_passphrase'
        )
        
        assert result.success is True
        
        # Verify passphrase was added
        accounts_config = self.account_manager.config_manager.load_accounts_config()
        coinbase_config = accounts_config['crypto_exchanges']['test-coinbase']
        assert coinbase_config['api_passphrase'] == 'test_passphrase'
    
    def test_auto_generated_account_names(self):
        """Test auto-generated account names"""
        # Test crypto account name generation
        result = self.account_manager.add_crypto_account(
            exchange_type='kraken',
            mode='live'  # No name provided
        )
        
        assert result.success is True
        assert self.account_manager.account_exists('kraken-live')
        
        # Test forex account name generation
        result = self.account_manager.add_forex_account(
            broker_type='ib',
            mode='demo'  # No name provided
        )
        
        assert result.success is True
        assert self.account_manager.account_exists('ib-demo')


class TestAccountManagerIntegration:
    """Integration tests for AccountManager with real file operations"""
    
    def setup_method(self):
        """Set up integration test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "config"
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.env_file = self.temp_dir / ".env"
        
        # Create empty accounts configuration file
        accounts_file = self.config_path / "accounts.yaml"
        initial_config = {'crypto_exchanges': {}, 'forex_brokers': {}}
        with open(accounts_file, 'w') as f:
            yaml.dump(initial_config, f)
        
        self.account_manager = AccountManager(
            config_path=self.config_path,
            env_file=self.env_file
        )
    
    def teardown_method(self):
        """Clean up integration test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_account_lifecycle(self):
        """Test complete account lifecycle: add, edit, disable, enable, remove"""
        # 1. Add crypto account
        result = self.account_manager.add_crypto_account(
            exchange_type='binance',
            name='lifecycle-test',
            mode='demo'
        )
        assert result.success is True
        
        # 2. Verify account exists and is enabled
        account = self.account_manager.get_account_by_name('lifecycle-test')
        assert account is not None
        assert account.enabled is True
        
        # 3. Edit account settings
        result = self.account_manager.edit_account(
            name='lifecycle-test',
            timeout=60,
            rate_limit=600
        )
        assert result.success is True
        
        # 4. Disable account
        result = self.account_manager.disable_account('lifecycle-test')
        assert result.success is True
        
        account = self.account_manager.get_account_by_name('lifecycle-test')
        assert account.enabled is False
        
        # 5. Enable account
        result = self.account_manager.enable_account('lifecycle-test')
        assert result.success is True
        
        account = self.account_manager.get_account_by_name('lifecycle-test')
        assert account.enabled is True
        
        # 6. Remove account
        result = self.account_manager.remove_account('lifecycle-test', confirm=True)
        assert result.success is True
        
        # 7. Verify account is gone
        assert self.account_manager.account_exists('lifecycle-test') is False
    
    def test_multiple_accounts_same_exchange(self):
        """Test adding multiple accounts for the same exchange"""
        # Add demo account
        result1 = self.account_manager.add_crypto_account(
            exchange_type='binance',
            name='binance-demo',
            mode='demo'
        )
        assert result1.success is True
        
        # Add live account
        result2 = self.account_manager.add_crypto_account(
            exchange_type='binance',
            name='binance-live',
            mode='live'
        )
        assert result2.success is True
        
        # Verify both accounts exist
        accounts = self.account_manager.get_all_accounts()
        binance_accounts = [acc for acc in accounts if acc.exchange_or_broker == 'binance']
        assert len(binance_accounts) == 2
        
        # Verify different sandbox settings
        demo_account = next(acc for acc in binance_accounts if acc.name == 'binance-demo')
        live_account = next(acc for acc in binance_accounts if acc.name == 'binance-live')
        
        assert demo_account.sandbox is True
        assert live_account.sandbox is False
    
    def test_configuration_backup_and_restore(self):
        """Test configuration backup and restore functionality"""
        # First create an initial accounts file
        accounts_file = self.config_path / "accounts.yaml"
        initial_config = {'crypto_exchanges': {}, 'forex_brokers': {}}
        with open(accounts_file, 'w') as f:
            yaml.dump(initial_config, f)
        
        # Add an account (this should create a backup since file exists)
        self.account_manager.add_crypto_account(
            exchange_type='kraken',
            name='backup-test',
            mode='demo'
        )
        
        # Verify backup was created
        backups = self.account_manager.config_manager.list_backups()
        assert len(backups) > 0
        
        # Modify the account (this should create another backup)
        self.account_manager.edit_account('backup-test', enabled=False)
        
        # Restore from backup
        restore_success = self.account_manager.config_manager.restore_backup(accounts_file)
        assert restore_success is True
        
        # Verify account is back to original state
        account = self.account_manager.get_account_by_name('backup-test')
        assert account.enabled is True  # Should be restored to original enabled state


if __name__ == '__main__':
    pytest.main([__file__])