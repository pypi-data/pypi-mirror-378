"""
CLI Integration Tests
====================

Tests to verify that the CLI properly integrates with existing trading bot components.
"""

import pytest
import asyncio
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from genebot.cli.utils.integration_manager import IntegrationManager
from genebot.cli.utils.account_validator import RealAccountValidator
from genebot.cli.result import CommandResult


class TestCLIIntegration:
    """Test CLI integration with existing trading bot components."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "config"
            config_dir.mkdir(parents=True)
            yield config_dir
    
    @pytest.fixture
    def sample_accounts_config(self, temp_config_dir):
        """Create sample accounts configuration."""
        accounts_config = {
            'crypto_exchanges': {
                'binance-demo': {
                    'name': 'binance-demo',
                    'exchange_type': 'binance',
                    'enabled': True,
                    'sandbox': True,
                    'api_key': '${BINANCE_DEMO_API_KEY}',
                    'api_secret': '${BINANCE_DEMO_API_SECRET}',
                    'rate_limit': 1200,
                    'timeout': 30
                }
            },
            'forex_brokers': {
                'oanda-demo': {
                    'name': 'oanda-demo',
                    'broker_type': 'oanda',
                    'enabled': True,
                    'sandbox': True,
                    'api_key': '${OANDA_DEMO_API_KEY}',
                    'account_id': '${OANDA_DEMO_ACCOUNT_ID}',
                    'timeout': 30,
                    'max_retries': 3
                }
            }
        }
        
        accounts_file = temp_config_dir / "accounts.yaml"
        with open(accounts_file, 'w') as f:
            yaml.dump(accounts_config, f)
        
        return accounts_file
    
    @pytest.fixture
    def sample_trading_config(self, temp_config_dir):
        """Create sample trading bot configuration."""
        trading_config = {
            'app_name': 'TradingBot',
            'version': '1.0.0',
            'debug': False,
            'dry_run': True,
            'base_currency': 'USDT',
            'exchanges': {
                'binance-demo': {
                    'exchange_type': 'binance',
                    'api_key': '${BINANCE_DEMO_API_KEY}',
                    'api_secret': '${BINANCE_DEMO_API_SECRET}',
                    'sandbox': True,
                    'enabled': True
                }
            },
            'database': {
                'database_type': 'sqlite',
                'database_url': 'sqlite:///test_trading_bot.db'
            },
            'logging': {
                'log_level': 'INFO',
                'log_format': 'standard'
            }
        }
        
        config_file = temp_config_dir / "trading_bot_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(trading_config, f)
        
        return config_file
    
    def test_integration_manager_initialization(self, temp_config_dir):
        """Test that integration manager initializes correctly."""
        integration_manager = IntegrationManager(
            config_path=temp_config_dir,
            env_file=Path(".env")
        )
        
        assert integration_manager.config_path == temp_config_dir
        assert integration_manager.env_file == Path(".env")
        assert integration_manager._exchange_adapters == {}
    
    @patch('genebot.cli.utils.integration_manager.get_config_manager')
    def test_config_manager_integration(self, mock_get_config_manager, temp_config_dir, sample_trading_config):
        """Test integration with existing configuration manager."""
        # Mock configuration manager
        mock_config_manager = Mock()
        mock_config = Mock()
        mock_config.exchanges = {'binance-demo': Mock()}
        mock_config.database = Mock()
        mock_config_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_config_manager
        
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Test config manager access
        config_manager = integration_manager.config_manager
        assert config_manager == mock_config_manager
        
        # Verify config manager was called with correct parameters
        mock_get_config_manager.assert_called_once()
    
    @patch('genebot.cli.utils.integration_manager.DatabaseConnection')
    @patch('genebot.cli.utils.integration_manager.get_config_manager')
    def test_database_connection_integration(self, mock_get_config_manager, mock_db_connection, temp_config_dir):
        """Test integration with existing database connection."""
        # Mock configuration
        mock_config_manager = Mock()
        mock_config = Mock()
        mock_config.database = Mock()
        mock_config_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_config_manager
        
        # Mock database connection
        mock_db_instance = Mock()
        mock_db_connection.return_value = mock_db_instance
        
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Test database connection access
        db_connection = integration_manager.db_connection
        assert db_connection == mock_db_instance
        
        # Verify database connection was created with config
        mock_db_connection.assert_called_once_with(mock_config.database)
    
    @patch('genebot.cli.utils.integration_manager.CCXTAdapter')
    @patch('genebot.cli.utils.integration_manager.get_config_manager')
    def test_exchange_adapter_creation(self, mock_get_config_manager, mock_ccxt_adapter, temp_config_dir):
        """Test creation of exchange adapters using existing components."""
        # Mock configuration
        mock_config_manager = Mock()
        mock_config = Mock()
        mock_exchange_config = Mock()
        mock_exchange_config.dict.return_value = {'exchange_type': 'binance', 'api_key': 'test'}
        mock_config.exchanges = {'binance-demo': mock_exchange_config}
        mock_config_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_config_manager
        
        # Mock adapter
        mock_adapter_instance = Mock()
        mock_ccxt_adapter.return_value = mock_adapter_instance
        
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Test adapter creation
        adapter = integration_manager.get_exchange_adapter('binance-demo')
        assert adapter == mock_adapter_instance
        
        # Verify adapter was created with correct parameters
        mock_ccxt_adapter.assert_called_once_with('binance-demo', {'exchange_type': 'binance', 'api_key': 'test'})
    
    @pytest.mark.asyncio
    @patch('genebot.cli.utils.integration_manager.CCXTAdapter')
    @patch('genebot.cli.utils.integration_manager.get_config_manager')
    async def test_exchange_connection_testing(self, mock_get_config_manager, mock_ccxt_adapter, temp_config_dir):
        """Test exchange connection testing using existing adapters."""
        # Mock configuration
        mock_config_manager = Mock()
        mock_config = Mock()
        mock_exchange_config = Mock()
        mock_exchange_config.dict.return_value = {'exchange_type': 'binance'}
        mock_config.exchanges = {'binance-demo': mock_exchange_config}
        mock_config_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_config_manager
        
        # Mock adapter with async methods
        mock_adapter = Mock()
        mock_adapter.connect = AsyncMock(return_value=True)
        mock_adapter.authenticate = AsyncMock(return_value=True)
        mock_adapter.health_check = AsyncMock(return_value={'status': 'healthy'})
        mock_adapter.disconnect = AsyncMock()
        mock_adapter.validate_credentials.return_value = True
        mock_adapter.is_authenticated = True
        mock_ccxt_adapter.return_value = mock_adapter
        
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Test connection
        result = await integration_manager.test_exchange_connection('binance-demo')
        
        assert result.success
        assert 'Successfully connected to binance-demo' in result.message
        assert result.data['connected'] is True
        assert result.data['authenticated'] is True
        
        # Verify adapter methods were called
        mock_adapter.connect.assert_called_once()
        mock_adapter.authenticate.assert_called_once()
        mock_adapter.health_check.assert_called_once()
        mock_adapter.disconnect.assert_called_once()
    
    @patch('genebot.cli.utils.integration_manager.get_config_manager')
    def test_available_exchanges_listing(self, mock_get_config_manager, temp_config_dir):
        """Test listing available exchanges using existing configuration."""
        # Mock configuration
        mock_config_manager = Mock()
        mock_config = Mock()
        
        # Mock crypto exchange
        mock_crypto_config = Mock()
        mock_crypto_config.exchange_type.value = 'binance'
        mock_crypto_config.enabled = True
        mock_crypto_config.sandbox = True
        
        mock_config.exchanges = {'binance-demo': mock_crypto_config}
        mock_config_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_config_manager
        
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Test listing exchanges
        exchanges = integration_manager.get_available_exchanges()
        
        assert len(exchanges) == 1
        assert exchanges[0]['name'] == 'binance-demo'
        assert exchanges[0]['type'] == 'crypto'
        assert exchanges[0]['exchange_type'] == 'binance'
        assert exchanges[0]['enabled'] is True
        assert exchanges[0]['sandbox'] is True
    
    @patch('genebot.cli.utils.integration_manager.validate_config_file')
    @patch('genebot.cli.utils.integration_manager.get_config_manager')
    def test_configuration_validation_integration(self, mock_get_config_manager, mock_validate_config, temp_config_dir, sample_trading_config):
        """Test configuration validation using existing validation utilities."""
        # Mock configuration manager
        mock_config_manager = Mock()
        mock_config = Mock()
        mock_config_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_config_manager
        
        # Mock validation result
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.warnings = []
        mock_validation_result.info = ['Configuration is valid']
        mock_validate_config.return_value = mock_validation_result
        
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Test validation
        result = integration_manager.validate_configuration()
        
        assert result.success
        assert 'Configuration is valid' in result.message
        
        # Verify validation was called with correct file
        mock_validate_config.assert_called_once_with(sample_trading_config)
    
    @patch('genebot.cli.utils.integration_manager.DatabaseConnection')
    @patch('genebot.cli.utils.integration_manager.get_config_manager')
    def test_database_operations_integration(self, mock_get_config_manager, mock_db_connection, temp_config_dir):
        """Test database operations using existing database models."""
        # Mock configuration
        mock_config_manager = Mock()
        mock_config = Mock()
        mock_config.database = Mock()
        mock_config_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_config_manager
        
        # Mock database session and queries
        mock_session = Mock()
        mock_db_instance = Mock()
        mock_db_instance.get_session.return_value = mock_session
        mock_db_connection.return_value = mock_db_instance
        
        # Mock trade data
        mock_trade = Mock()
        mock_trade.id = 1
        mock_trade.symbol = 'BTC/USDT'
        mock_trade.side = 'BUY'
        mock_trade.amount = 0.1
        mock_trade.price = 50000.0
        mock_trade.fees = 5.0
        mock_trade.timestamp = datetime.now(timezone.utc)
        mock_trade.exchange = 'binance-demo'
        
        mock_query = Mock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_trade]
        mock_session.query.return_value = mock_query
        
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Test getting recent trades
        trades = integration_manager.get_recent_trades(limit=10)
        
        assert len(trades) == 1
        assert trades[0]['symbol'] == 'BTC/USDT'
        assert trades[0]['side'] == 'BUY'
        assert trades[0]['exchange'] == 'binance-demo'
        
        # Verify database session was used
        mock_session.query.assert_called()
        mock_session.close.assert_called()
    
    def test_account_validator_integration(self, temp_config_dir, sample_accounts_config):
        """Test account validator integration with existing components."""
        validator = RealAccountValidator(config_path=temp_config_dir)
        
        # Test that integration manager is initialized
        assert validator.integration_manager is not None
        assert validator.integration_manager.config_path == temp_config_dir
        
        # Test loading accounts
        accounts = validator.get_all_accounts()
        
        assert len(accounts) == 2
        
        # Check crypto account
        crypto_account = next((acc for acc in accounts if acc['type'] == 'crypto'), None)
        assert crypto_account is not None
        assert crypto_account['name'] == 'binance-demo'
        assert crypto_account['exchange_type'] == 'binance'
        
        # Check forex account
        forex_account = next((acc for acc in accounts if acc['type'] == 'forex'), None)
        assert forex_account is not None
        assert forex_account['name'] == 'oanda-demo'
        assert forex_account['broker_type'] == 'oanda'
    
    @pytest.mark.asyncio
    @patch('genebot.cli.utils.integration_manager.CCXTAdapter')
    @patch('genebot.cli.utils.integration_manager.get_config_manager')
    async def test_close_all_orders_integration(self, mock_get_config_manager, mock_ccxt_adapter, temp_config_dir):
        """Test closing all orders using existing exchange adapters."""
        # Mock configuration
        mock_config_manager = Mock()
        mock_config = Mock()
        mock_exchange_config = Mock()
        mock_exchange_config.dict.return_value = {'exchange_type': 'binance'}
        mock_config.exchanges = {'binance-demo': mock_exchange_config}
        mock_config_manager.get_config.return_value = mock_config
        mock_get_config_manager.return_value = mock_config_manager
        
        # Mock adapter
        mock_adapter = Mock()
        mock_adapter.connect = AsyncMock()
        mock_adapter.cancel_order = AsyncMock()
        mock_adapter.disconnect = AsyncMock()
        mock_ccxt_adapter.return_value = mock_adapter
        
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Mock get_open_orders to return test orders
        integration_manager.get_open_orders = Mock(return_value=[
            {
                'id': 'order1',
                'symbol': 'BTC/USDT',
                'exchange': 'binance-demo',
                'side': 'BUY',
                'amount': 0.1
            }
        ])
        
        # Test closing orders
        result = await integration_manager.close_all_orders()
        
        assert result.success
        assert 'Successfully closed 1 orders' in result.message
        
        # Verify adapter methods were called
        mock_adapter.connect.assert_called_once()
        mock_adapter.cancel_order.assert_called_once_with('order1', 'BTC/USDT')
        mock_adapter.disconnect.assert_called_once()
    
    def test_error_handling_integration(self, temp_config_dir):
        """Test that CLI error handling integrates with existing exception patterns."""
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Test configuration error handling
        with patch.object(integration_manager, 'config_manager') as mock_config_manager:
            mock_config_manager.get_config.side_effect = Exception("Config error")
            
            with pytest.raises(Exception):  # Should propagate existing exceptions
                integration_manager.get_exchange_adapter('nonexistent')
    
    def test_cleanup_integration(self, temp_config_dir):
        """Test cleanup of integration manager resources."""
        integration_manager = IntegrationManager(config_path=temp_config_dir)
        
        # Add mock adapters
        mock_adapter = Mock()
        mock_adapter.disconnect = AsyncMock()
        integration_manager._exchange_adapters['test'] = mock_adapter
        
        # Add mock database connection
        mock_db = Mock()
        mock_db.close = Mock()
        integration_manager._db_connection = mock_db
        
        # Test cleanup
        integration_manager.cleanup()
        
        # Verify cleanup was called
        mock_db.close.assert_called_once()


class TestExistingComponentCompatibility:
    """Test compatibility with existing trading bot components."""
    
    def test_exchange_adapter_interface_compatibility(self):
        """Test that CLI uses existing exchange adapter interfaces correctly."""
        from src.exchanges.base import ExchangeAdapter
        
        # Verify that the base adapter interface is available
        assert hasattr(ExchangeAdapter, 'connect')
        assert hasattr(ExchangeAdapter, 'authenticate')
        assert hasattr(ExchangeAdapter, 'health_check')
        assert hasattr(ExchangeAdapter, 'get_balance')
        assert hasattr(ExchangeAdapter, 'cancel_order')
    
    def test_database_models_compatibility(self):
        """Test that CLI uses existing database models correctly."""
        from src.models.database_models import TradeModel, OrderModel, PositionModel
        
        # Verify that database models are available
        assert hasattr(TradeModel, 'symbol')
        assert hasattr(TradeModel, 'side')
        assert hasattr(TradeModel, 'amount')
        assert hasattr(OrderModel, 'status')
        assert hasattr(PositionModel, 'size')
    
    def test_configuration_manager_compatibility(self):
        """Test that CLI uses existing configuration manager correctly."""
        from config.manager import ConfigManager
        
        # Verify that configuration manager interface is available
        assert hasattr(ConfigManager, 'get_config')
        assert hasattr(ConfigManager, 'get_exchange_config')
        assert hasattr(ConfigManager, 'validate_config')
    
    def test_validation_utilities_compatibility(self):
        """Test that CLI uses existing validation utilities correctly."""
        from config.validation_utils import validate_config_file
        
        # Verify that validation utilities are available
        assert callable(validate_config_file)
    
    def test_exception_handling_compatibility(self):
        """Test that CLI uses existing exception patterns correctly."""
        from src.exceptions.base_exceptions import (
            TradingBotException, ExchangeException, ConfigurationException
        )
        
        # Verify that exception classes are available
        assert issubclass(ExchangeException, TradingBotException)
        assert issubclass(ConfigurationException, TradingBotException)
        
        # Test exception creation
        exc = ExchangeException("Test error", exchange_name="test")
        assert exc.message == "Test error"
        assert exc.context.get('exchange') == "test"


if __name__ == '__main__':
    pytest.main([__file__])