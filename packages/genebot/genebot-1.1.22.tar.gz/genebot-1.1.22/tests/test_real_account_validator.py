"""
Tests for Real Account Validator
===============================

Integration tests for the RealAccountValidator that test actual API connectivity
with mock exchange responses.
"""

import pytest
import asyncio
import tempfile
import yaml
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal

from genebot.cli.utils.account_validator import RealAccountValidator, AccountStatus
from genebot.cli.result import ResultStatus


class TestRealAccountValidator:
    """Test suite for RealAccountValidator"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir)
            yield config_path
    
    @pytest.fixture
    def sample_accounts_config(self):
        """Sample accounts configuration"""
        return {
            'crypto_exchanges': {
                'test-binance': {
                    'name': 'test-binance',
                    'exchange_type': 'binance',
                    'api_key': 'test_api_key',
                    'api_secret': 'test_api_secret',
                    'sandbox': True,
                    'enabled': True,
                    'rate_limit': 1200,
                    'timeout': 30
                },
                'test-coinbase': {
                    'name': 'test-coinbase',
                    'exchange_type': 'coinbase',
                    'api_key': 'coinbase_key',
                    'api_secret': 'coinbase_secret',
                    'api_passphrase': 'coinbase_passphrase',
                    'sandbox': True,
                    'enabled': False,
                    'rate_limit': 600,
                    'timeout': 30
                }
            },
            'forex_brokers': {
                'test-oanda': {
                    'name': 'test-oanda',
                    'broker_type': 'oanda',
                    'api_key': 'oanda_api_key',
                    'account_id': '101-001-12345678-001',
                    'sandbox': True,
                    'enabled': True,
                    'timeout': 30,
                    'max_retries': 3
                },
                'test-ib': {
                    'name': 'test-ib',
                    'broker_type': 'ib',
                    'host': 'localhost',
                    'port': 7497,
                    'client_id': 1,
                    'enabled': True,
                    'timeout': 30
                }
            }
        }
    
    @pytest.fixture
    def validator_with_config(self, temp_config_dir, sample_accounts_config):
        """Create validator with sample configuration"""
        accounts_file = temp_config_dir / "accounts.yaml"
        with open(accounts_file, 'w') as f:
            yaml.dump(sample_accounts_config, f)
        
        return RealAccountValidator(config_path=temp_config_dir)
    
    def test_load_accounts_config(self, validator_with_config):
        """Test loading accounts configuration from YAML"""
        config = validator_with_config._load_accounts_config()
        
        assert 'crypto_exchanges' in config
        assert 'forex_brokers' in config
        assert 'test-binance' in config['crypto_exchanges']
        assert 'test-oanda' in config['forex_brokers']
    
    def test_load_accounts_config_missing_file(self, temp_config_dir):
        """Test handling of missing accounts configuration file"""
        validator = RealAccountValidator(config_path=temp_config_dir)
        
        with pytest.raises(FileNotFoundError):
            validator._load_accounts_config()
    
    def test_get_all_accounts(self, validator_with_config):
        """Test getting all configured accounts"""
        accounts = validator_with_config.get_all_accounts()
        
        assert len(accounts) == 4  # 2 crypto + 2 forex
        
        # Check that accounts have correct type information
        crypto_accounts = [acc for acc in accounts if acc['type'] == 'crypto']
        forex_accounts = [acc for acc in accounts if acc['type'] == 'forex']
        
        assert len(crypto_accounts) == 2
        assert len(forex_accounts) == 2
        
        # Verify account names
        account_names = [acc['name'] for acc in accounts]
        assert 'test-binance' in account_names
        assert 'test-coinbase' in account_names
        assert 'test-oanda' in account_names
        assert 'test-ib' in account_names
    
    def test_get_account_by_name(self, validator_with_config):
        """Test getting specific account by name"""
        account = validator_with_config.get_account_by_name('test-binance')
        
        assert account is not None
        assert account['name'] == 'test-binance'
        assert account['type'] == 'crypto'
        assert account['exchange_type'] == 'binance'
        
        # Test non-existent account
        non_existent = validator_with_config.get_account_by_name('non-existent')
        assert non_existent is None
    
    def test_filter_accounts(self, validator_with_config):
        """Test filtering accounts by type and enabled status"""
        all_accounts = validator_with_config.get_all_accounts()
        
        # Filter by type
        crypto_accounts = validator_with_config.filter_accounts(all_accounts, account_type='crypto')
        assert len(crypto_accounts) == 2
        assert all(acc['type'] == 'crypto' for acc in crypto_accounts)
        
        forex_accounts = validator_with_config.filter_accounts(all_accounts, account_type='forex')
        assert len(forex_accounts) == 2
        assert all(acc['type'] == 'forex' for acc in forex_accounts)
        
        # Filter by enabled status
        enabled_accounts = validator_with_config.filter_accounts(all_accounts, enabled_only=True)
        assert len(enabled_accounts) == 3  # test-binance, test-oanda, test-ib are enabled
        assert all(acc['enabled'] for acc in enabled_accounts)
        
        # Combined filters
        enabled_crypto = validator_with_config.filter_accounts(
            all_accounts, account_type='crypto', enabled_only=True
        )
        assert len(enabled_crypto) == 1  # Only test-binance is enabled crypto
        assert enabled_crypto[0]['name'] == 'test-binance'
    
    @pytest.mark.asyncio
    async def test_validate_single_account_crypto_success(self, validator_with_config):
        """Test successful validation of crypto account"""
        # Mock the CCXT adapter
        mock_adapter = AsyncMock()
        mock_adapter.connect.return_value = True
        mock_adapter.authenticate.return_value = True
        mock_adapter.get_balance.return_value = {'USDT': Decimal('1000.0'), 'BTC': Decimal('0.1')}
        mock_adapter.health_check.return_value = {
            'status': 'healthy',
            'latency_ms': 150.5,
            'server_time': datetime.now(timezone.utc).isoformat()
        }
        mock_adapter.disconnect = AsyncMock()
        
        with patch.object(validator_with_config, '_create_crypto_adapter', return_value=mock_adapter):
            account_config = {
                'name': 'test-binance',
                'type': 'crypto',
                'exchange_type': 'binance',
                'enabled': True
            }
            
            status = await validator_with_config.validate_single_account(account_config, timeout=30)
            
            assert status.name == 'test-binance'
            assert status.type == 'crypto'
            assert status.exchange_or_broker == 'binance'
            assert status.enabled is True
            assert status.connected is True
            assert status.authenticated is True
            assert status.error_message is None
            assert status.balance is not None
            assert 'USDT' in status.balance
            assert status.latency_ms is not None
            
            # Verify adapter methods were called
            mock_adapter.connect.assert_called_once()
            mock_adapter.authenticate.assert_called_once()
            mock_adapter.get_balance.assert_called_once()
            mock_adapter.health_check.assert_called_once()
            mock_adapter.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_single_account_crypto_connection_failure(self, validator_with_config):
        """Test crypto account validation with connection failure"""
        from genebot.exceptions.base_exceptions import ConnectionException
        
        mock_adapter = AsyncMock()
        mock_adapter.connect.side_effect = ConnectionException("Network error")
        mock_adapter.disconnect = AsyncMock()
        
        with patch.object(validator_with_config, '_create_crypto_adapter', return_value=mock_adapter):
            account_config = {
                'name': 'test-binance',
                'type': 'crypto',
                'exchange_type': 'binance',
                'enabled': True
            }
            
            status = await validator_with_config.validate_single_account(account_config, timeout=30)
            
            assert status.name == 'test-binance'
            assert status.connected is False
            assert status.authenticated is False
            assert status.error_message is not None
            assert "Network error" in status.error_message
            
            mock_adapter.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_single_account_crypto_auth_failure(self, validator_with_config):
        """Test crypto account validation with authentication failure"""
        from genebot.exceptions.base_exceptions import AuthenticationException
        
        mock_adapter = AsyncMock()
        mock_adapter.connect.return_value = True
        mock_adapter.authenticate.side_effect = AuthenticationException("Invalid API key")
        mock_adapter.disconnect = AsyncMock()
        
        with patch.object(validator_with_config, '_create_crypto_adapter', return_value=mock_adapter):
            account_config = {
                'name': 'test-binance',
                'type': 'crypto',
                'exchange_type': 'binance',
                'enabled': True
            }
            
            status = await validator_with_config.validate_single_account(account_config, timeout=30)
            
            assert status.name == 'test-binance'
            assert status.connected is True  # Connection succeeded
            assert status.authenticated is False  # But auth failed
            assert status.error_message is not None
            assert "API error" in status.error_message
    
    @pytest.mark.asyncio
    async def test_validate_single_account_forex_success(self, validator_with_config):
        """Test successful validation of forex account"""
        mock_adapter = AsyncMock()
        mock_adapter.connect.return_value = True
        mock_adapter.authenticate.return_value = True
        mock_adapter.get_balance.return_value = {'USD': Decimal('10000.0')}
        mock_adapter.health_check.return_value = {
            'status': 'healthy',
            'account_id': '101-001-12345678-001',
            'currency': 'USD',
            'balance': 10000.0
        }
        mock_adapter.disconnect = AsyncMock()
        
        with patch.object(validator_with_config, '_create_forex_adapter', return_value=mock_adapter):
            account_config = {
                'name': 'test-oanda',
                'type': 'forex',
                'broker_type': 'oanda',
                'enabled': True
            }
            
            status = await validator_with_config.validate_single_account(account_config, timeout=30)
            
            assert status.name == 'test-oanda'
            assert status.type == 'forex'
            assert status.exchange_or_broker == 'oanda'
            assert status.connected is True
            assert status.authenticated is True
            assert status.error_message is None
            assert status.balance is not None
            assert 'USD' in status.balance
    
    @pytest.mark.asyncio
    async def test_validate_single_account_timeout(self, validator_with_config):
        """Test account validation with timeout"""
        mock_adapter = AsyncMock()
        
        # Simulate timeout by making connect hang
        async def slow_connect():
            await asyncio.sleep(2)  # Longer than timeout
            return True
        
        mock_adapter.connect = slow_connect
        mock_adapter.disconnect = AsyncMock()
        
        with patch.object(validator_with_config, '_create_crypto_adapter', return_value=mock_adapter):
            account_config = {
                'name': 'test-binance',
                'type': 'crypto',
                'exchange_type': 'binance',
                'enabled': True
            }
            
            status = await validator_with_config.validate_single_account(account_config, timeout=1)
            
            assert status.name == 'test-binance'
            assert status.connected is False
            assert status.authenticated is False
            assert status.error_message is not None
            assert "timeout" in status.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_all_accounts(self, validator_with_config):
        """Test validating all accounts"""
        # Mock successful validation for all accounts
        mock_crypto_adapter = AsyncMock()
        mock_crypto_adapter.connect.return_value = True
        mock_crypto_adapter.authenticate.return_value = True
        mock_crypto_adapter.get_balance.return_value = {'USDT': Decimal('1000.0')}
        mock_crypto_adapter.health_check.return_value = {'status': 'healthy'}
        mock_crypto_adapter.disconnect = AsyncMock()
        
        mock_forex_adapter = AsyncMock()
        mock_forex_adapter.connect.return_value = True
        mock_forex_adapter.authenticate.return_value = True
        mock_forex_adapter.get_balance.return_value = {'USD': Decimal('10000.0')}
        mock_forex_adapter.health_check.return_value = {'status': 'healthy'}
        mock_forex_adapter.disconnect = AsyncMock()
        
        with patch.object(validator_with_config, '_create_crypto_adapter', return_value=mock_crypto_adapter), \
             patch.object(validator_with_config, '_create_forex_adapter', return_value=mock_forex_adapter):
            
            statuses = await validator_with_config.validate_all_accounts(timeout=30)
            
            assert len(statuses) == 4  # All 4 accounts
            
            # All should be successful
            successful = [s for s in statuses if s.connected and s.authenticated]
            assert len(successful) == 4
    
    @pytest.mark.asyncio
    async def test_validate_all_accounts_with_filters(self, validator_with_config):
        """Test validating accounts with filters"""
        mock_adapter = AsyncMock()
        mock_adapter.connect.return_value = True
        mock_adapter.authenticate.return_value = True
        mock_adapter.get_balance.return_value = {'USDT': Decimal('1000.0')}
        mock_adapter.health_check.return_value = {'status': 'healthy'}
        mock_adapter.disconnect = AsyncMock()
        
        with patch.object(validator_with_config, '_create_crypto_adapter', return_value=mock_adapter):
            # Test filtering by account type
            statuses = await validator_with_config.validate_all_accounts(
                account_type='crypto', timeout=30
            )
            
            assert len(statuses) == 2  # Only crypto accounts
            assert all(s.type == 'crypto' for s in statuses)
            
            # Test filtering by enabled status
            statuses = await validator_with_config.validate_all_accounts(
                account_type='crypto', enabled_only=True, timeout=30
            )
            
            assert len(statuses) == 1  # Only enabled crypto account (test-binance)
            assert statuses[0].name == 'test-binance'
            
            # Test filtering by specific account
            statuses = await validator_with_config.validate_all_accounts(
                account_filter='test-binance', timeout=30
            )
            
            assert len(statuses) == 1
            assert statuses[0].name == 'test-binance'
    
    def test_get_validation_summary(self, validator_with_config):
        """Test generating validation summary"""
        # Create sample statuses
        statuses = [
            AccountStatus(
                name='account1', type='crypto', exchange_or_broker='binance',
                enabled=True, connected=True, authenticated=True,
                last_check=datetime.now(timezone.utc), latency_ms=100.0
            ),
            AccountStatus(
                name='account2', type='crypto', exchange_or_broker='coinbase',
                enabled=False, connected=True, authenticated=False,
                last_check=datetime.now(timezone.utc), latency_ms=200.0,
                error_message='Auth failed'
            ),
            AccountStatus(
                name='account3', type='forex', exchange_or_broker='oanda',
                enabled=True, connected=False, authenticated=False,
                last_check=datetime.now(timezone.utc),
                error_message='Connection failed'
            )
        ]
        
        summary = validator_with_config.get_validation_summary(statuses)
        
        assert summary['total_accounts'] == 3
        assert summary['valid_accounts'] == 1  # Only account1 is fully valid
        assert summary['invalid_accounts'] == 2
        assert summary['enabled_accounts'] == 2
        assert summary['disabled_accounts'] == 1
        assert summary['crypto_accounts'] == 2
        assert summary['forex_accounts'] == 1
        assert summary['success_rate'] == 33.3  # 1/3 * 100
        assert summary['average_latency_ms'] == 150.0  # Average of connected accounts (100 + 200) / 2
    
    def test_get_validation_summary_empty(self, validator_with_config):
        """Test validation summary with empty status list"""
        summary = validator_with_config.get_validation_summary([])
        
        assert summary['total_accounts'] == 0
        assert summary['valid_accounts'] == 0
        assert summary['invalid_accounts'] == 0
        assert summary['success_rate'] == 0.0
        assert summary['average_latency_ms'] == 0.0


class TestAccountValidatorIntegration:
    """Integration tests for account validator with CLI commands"""
    
    @pytest.fixture
    def mock_validator(self):
        """Create mock validator for CLI integration tests"""
        validator = MagicMock()
        validator.validate_all_accounts = AsyncMock()
        validator.get_validation_summary = MagicMock()
        return validator
    
    def test_cli_integration_successful_validation(self, mock_validator):
        """Test CLI integration with successful validation"""
        from genebot.cli.commands.account import ValidateAccountsCommand
        from genebot.cli.context import CLIContext
        from genebot.cli.utils.logger import CLILogger
        from genebot.cli.utils.error_handler import CLIErrorHandler
        from argparse import Namespace
        
        # Mock successful validation results
        mock_statuses = [
            AccountStatus(
                name='test-account', type='crypto', exchange_or_broker='binance',
                enabled=True, connected=True, authenticated=True,
                last_check=datetime.now(timezone.utc), latency_ms=150.0
            )
        ]
        
        mock_validator.validate_all_accounts.return_value = mock_statuses
        mock_validator.get_validation_summary.return_value = {
            'total_accounts': 1,
            'valid_accounts': 1,
            'invalid_accounts': 0,
            'success_rate': 100.0,
            'average_latency_ms': 150.0
        }
        mock_validator.save_validation_history = MagicMock()
        
        # Create mock CLI components
        mock_context = MagicMock(spec=CLIContext)
        mock_logger = MagicMock(spec=CLILogger)
        mock_error_handler = MagicMock(spec=CLIErrorHandler)
        
        # Test command execution
        command = ValidateAccountsCommand(mock_context, mock_logger, mock_error_handler)
        args = Namespace(account=None, timeout=30, type=None, enabled_only=False)
        
        with patch('genebot.cli.utils.account_validator.RealAccountValidator', return_value=mock_validator):
            result = command.execute(args)
        
        assert result.success is True
        assert "1 account(s) validated successfully" in result.message
        assert "150.0ms" in result.message
    
    def test_cli_integration_validation_failures(self, mock_validator):
        """Test CLI integration with validation failures"""
        from genebot.cli.commands.account import ValidateAccountsCommand
        from genebot.cli.context import CLIContext
        from genebot.cli.utils.logger import CLILogger
        from genebot.cli.utils.error_handler import CLIErrorHandler
        from argparse import Namespace
        
        # Mock mixed validation results
        mock_statuses = [
            AccountStatus(
                name='good-account', type='crypto', exchange_or_broker='binance',
                enabled=True, connected=True, authenticated=True,
                last_check=datetime.now(timezone.utc), latency_ms=150.0
            ),
            AccountStatus(
                name='bad-account', type='crypto', exchange_or_broker='coinbase',
                enabled=True, connected=False, authenticated=False,
                last_check=datetime.now(timezone.utc),
                error_message='Connection failed'
            )
        ]
        
        mock_validator.validate_all_accounts.return_value = mock_statuses
        mock_validator.get_validation_summary.return_value = {
            'total_accounts': 2,
            'valid_accounts': 1,
            'invalid_accounts': 1,
            'success_rate': 50.0,
            'average_latency_ms': 150.0
        }
        mock_validator.save_validation_history = MagicMock()
        
        # Create mock CLI components
        mock_context = MagicMock(spec=CLIContext)
        mock_logger = MagicMock(spec=CLILogger)
        mock_error_handler = MagicMock(spec=CLIErrorHandler)
        
        command = ValidateAccountsCommand(mock_context, mock_logger, mock_error_handler)
        args = Namespace(account=None, timeout=30, type=None, enabled_only=False)
        
        with patch('genebot.cli.utils.account_validator.RealAccountValidator', return_value=mock_validator):
            result = command.execute(args)
        
        assert result.status.value == "warning"  # Should be warning due to failures
        assert "1/2 accounts valid" in result.message
        assert "Success rate: 50.0%" in result.message
        assert len(result.suggestions) > 0


class TestRealAdapterCreation:
    """Test real adapter creation and error handling"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir)
            yield config_path
    
    @pytest.fixture
    def validator(self, temp_config_dir):
        """Create validator instance"""
        return RealAccountValidator(config_path=temp_config_dir)
    
    @pytest.mark.asyncio
    async def test_create_crypto_adapter_missing_exchange_type(self, validator):
        """Test crypto adapter creation with missing exchange type"""
        account_config = {
            'name': 'test-account',
            'type': 'crypto',
            'api_key': 'test_key',
            'api_secret': 'test_secret'
            # Missing exchange_type
        }
        
        with pytest.raises(ValueError, match="Missing exchange_type"):
            await validator._create_crypto_adapter(account_config)
    
    @pytest.mark.asyncio
    async def test_create_forex_adapter_missing_broker_type(self, validator):
        """Test forex adapter creation with missing broker type"""
        account_config = {
            'name': 'test-account',
            'type': 'forex',
            'api_key': 'test_key'
            # Missing broker_type
        }
        
        with pytest.raises(ValueError, match="Missing broker_type"):
            await validator._create_forex_adapter(account_config)
    
    @pytest.mark.asyncio
    async def test_create_forex_adapter_unsupported_broker(self, validator):
        """Test forex adapter creation with unsupported broker type"""
        account_config = {
            'name': 'test-account',
            'type': 'forex',
            'broker_type': 'unsupported_broker',
            'api_key': 'test_key'
        }
        
        with pytest.raises(ValueError, match="Unsupported broker type"):
            await validator._create_forex_adapter(account_config)
    
    @pytest.mark.asyncio
    async def test_validate_unknown_account_type(self, validator):
        """Test validation with unknown account type"""
        account_config = {
            'name': 'test-account',
            'type': 'unknown',
            'enabled': True
        }
        
        status = await validator.validate_single_account(account_config)
        
        assert status.name == 'test-account'
        assert status.type == 'unknown'
        assert status.connected is False
        assert status.authenticated is False
        assert "Unknown account type" in status.error_message
    
    def test_validation_history_operations(self, validator):
        """Test validation history save and retrieve operations"""
        # Create sample statuses
        statuses = [
            AccountStatus(
                name='account1', type='crypto', exchange_or_broker='binance',
                enabled=True, connected=True, authenticated=True,
                last_check=datetime.now(timezone.utc), latency_ms=100.0
            ),
            AccountStatus(
                name='account2', type='forex', exchange_or_broker='oanda',
                enabled=True, connected=False, authenticated=False,
                last_check=datetime.now(timezone.utc),
                error_message='Connection failed'
            )
        ]
        
        # Save validation history
        validator.save_validation_history(statuses)
        
        # Retrieve history
        history = validator.get_validation_history(limit=5)
        assert len(history) >= 1
        
        # Check that the latest entry contains our accounts
        latest_entry = history[-1]
        assert 'accounts' in latest_entry
        assert len(latest_entry['accounts']) == 2
        
        # Test filtering by account name
        account1_history = validator.get_validation_history(account_name='account1', limit=5)
        assert len(account1_history) >= 1
        
        # Verify the filtered history only contains account1
        for entry in account1_history:
            account_names = [acc['name'] for acc in entry['accounts']]
            assert 'account1' in account_names
            assert 'account2' not in account_names
    
    def test_account_status_trend_analysis(self, validator):
        """Test account status trend analysis"""
        # Test with no data
        trend = validator.get_account_status_trend('non-existent-account')
        assert trend['trend'] == 'no_data'
        assert trend['entries'] == 0
        
        # Create and save some validation history first
        statuses = [
            AccountStatus(
                name='trending-account', type='crypto', exchange_or_broker='binance',
                enabled=True, connected=True, authenticated=True,
                last_check=datetime.now(timezone.utc), latency_ms=100.0
            )
        ]
        
        validator.save_validation_history(statuses)
        
        # Analyze trend
        trend = validator.get_account_status_trend('trending-account', days=7)
        assert trend['account'] == 'trending-account'
        assert trend['entries'] >= 1
        assert 'success_rate' in trend
        assert 'trend' in trend


class TestRealAccountValidatorErrorScenarios:
    """Test error scenarios and edge cases"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir)
            yield config_path
    
    @pytest.fixture
    def validator_with_invalid_config(self, temp_config_dir):
        """Create validator with invalid configuration"""
        # Create invalid YAML file
        accounts_file = temp_config_dir / "accounts.yaml"
        with open(accounts_file, 'w') as f:
            f.write("invalid: yaml: content: [")  # Invalid YAML
        
        return RealAccountValidator(config_path=temp_config_dir)
    
    def test_load_invalid_yaml_config(self, validator_with_invalid_config):
        """Test handling of invalid YAML configuration"""
        with pytest.raises(yaml.YAMLError):
            validator_with_invalid_config._load_accounts_config()
    
    def test_get_accounts_with_invalid_config(self, validator_with_invalid_config):
        """Test getting accounts with invalid configuration"""
        # Should return empty list when config is invalid
        accounts = validator_with_invalid_config.get_all_accounts()
        assert accounts == []
    
    @pytest.mark.asyncio
    async def test_validate_accounts_with_invalid_config(self, validator_with_invalid_config):
        """Test validation with invalid configuration"""
        # Should return empty list when config is invalid
        statuses = await validator_with_invalid_config.validate_all_accounts()
        assert statuses == []
    
    def test_validation_summary_edge_cases(self, temp_config_dir):
        """Test validation summary with edge cases"""
        validator = RealAccountValidator(config_path=temp_config_dir)
        
        # Test with empty status list
        summary = validator.get_validation_summary([])
        assert summary['total_accounts'] == 0
        assert summary['success_rate'] == 0.0
        
        # Test with mixed latencies (some None)
        statuses = [
            AccountStatus(
                name='account1', type='crypto', exchange_or_broker='binance',
                enabled=True, connected=True, authenticated=True,
                last_check=datetime.now(timezone.utc), latency_ms=100.0
            ),
            AccountStatus(
                name='account2', type='crypto', exchange_or_broker='coinbase',
                enabled=True, connected=False, authenticated=False,
                last_check=datetime.now(timezone.utc), latency_ms=None,
                error_message='Connection failed'
            )
        ]
        
        summary = validator.get_validation_summary(statuses)
        assert summary['total_accounts'] == 2
        assert summary['valid_accounts'] == 1
        assert summary['invalid_accounts'] == 1
        assert summary['success_rate'] == 50.0
        assert summary['average_latency_ms'] == 100.0  # Only successful connection counted


if __name__ == '__main__':
    pytest.main([__file__])