"""
Integration Manager
==================

Manages integration between CLI and existing trading bot components.
Provides unified access to exchange adapters, configuration system,
database models, and validation utilities.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Type
from datetime import datetime, timedelta
from decimal import Decimal

# Import existing trading bot components
from genebot.config.manager import ConfigManager, get_config_manager
# Import existing trading bot components with fallbacks
try:
    from src.exchanges.base import ExchangeAdapter
    from src.exchanges.ccxt_adapter import CCXTAdapter
except ImportError:
    # Create minimal stubs for CLI functionality
    class ExchangeAdapter:
        def __init__(self, *args, **kwargs):
            pass
    
    class CCXTAdapter(ExchangeAdapter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

try:
    from src.models.database_models import (
        OrderModel, TradeModel, PositionModel, MarketDataModel,
        StrategyPerformanceModel, RiskEventModel
    )
except ImportError:
    # Create minimal stubs
    class OrderModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class TradeModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class PositionModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class MarketDataModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class StrategyPerformanceModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class RiskEventModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

try:
    from src.exceptions.base_exceptions import (
        TradingBotException, ExchangeException, ConfigurationException,
        ValidationException
    )
except ImportError:
    # Create minimal exception stubs
    class TradingBotException(Exception):
        pass
    
    class ExchangeException(TradingBotException):
        pass
    
    class ConfigurationException(TradingBotException):
        pass
    
    class ValidationException(TradingBotException):
        pass

# Import validation utilities with fallback
try:
    from genebot.config.validation_utils import ConfigValidator, validate_config_file
except ImportError:
    ConfigValidator = None
    validate_config_file = None

# Import database connection with fallback
try:
    from src.database.connection import DatabaseConnection
except ImportError:
    class DatabaseConnection:
        def __init__(self, *args, **kwargs):
            pass
        
        def connect(self):
            return None
        
        def close(self):
            pass

# Forex adapters will be imported dynamically when needed

from ..result import CommandResult
from .error_handler import CLIException, ConfigurationError


class IntegrationManager:
    """
    Manages integration between CLI and existing trading bot components.
    
    Provides unified access to:
    - Exchange adapters (crypto and forex)
    - Configuration management system
    - Database models and connections
    - Validation utilities
    - Error handling patterns
    """
    
    def __init__(self, config_path: Path = None, env_file: Path = None):
        """
        Initialize integration manager.
        
        Args:
            config_path: Path to configuration directory
            env_file: Path to environment file
        """
        self.config_path = config_path or Path("config")
        self.env_file = env_file or Path(".env")
        self.logger = logging.getLogger(__name__)
        
        # Initialize configuration manager
        self._config_manager = None
        self._db_connection = None
        self._exchange_adapters: Dict[str, ExchangeAdapter] = {}
        
    @property
    def config_manager(self) -> ConfigManager:
        """Get configuration manager instance."""
        if self._config_manager is None:
            try:
                # Try to get existing config manager or create new one
                self._config_manager = get_config_manager()
            except Exception:
                # Fallback: create new config manager
                config_file = self.config_path / "trading_bot_config.yaml"
                self._config_manager = ConfigManager(
                    config_path=str(config_file) if config_file.exists() else None,
                    env_file=str(self.env_file) if self.env_file.exists() else None
                )
        return self._config_manager
    
    @property
    def db_connection(self):
        """Get database connection instance."""
        if DatabaseConnection is None:
            raise ConfigurationError(
                "Database connection not available",
                suggestions=[
                    "Install database dependencies",
                    "Check database configuration"
                ]
            )
        
        if self._db_connection is None:
            try:
                config = self.config_manager.get_config()
                self._db_connection = DatabaseConnection(config.database)
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to initialize database connection: {e}",
                    suggestions=[
                        "Check database configuration in trading_bot_config.yaml",
                        "Ensure database is accessible",
                        "Verify database credentials"
                    ]
                )
        return self._db_connection
    
    def get_exchange_adapter(self, exchange_name: str) -> ExchangeAdapter:
        """
        Get exchange adapter instance.
        
        Args:
            exchange_name: Name of the exchange/broker
            
        Returns:
            ExchangeAdapter: Exchange adapter instance
            
        Raises:
            ConfigurationError: If exchange is not configured
        """
        if exchange_name in self._exchange_adapters:
            return self._exchange_adapters[exchange_name]
        
        try:
            config = self.config_manager.get_config()
            
            # Handle both dict and object config formats
            if isinstance(config, dict):
                exchanges = config.get('exchanges', {})
            else:
                exchanges = getattr(config, 'exchanges', {})
            
            # Check if it's a crypto exchange
            if exchange_name in exchanges:
                exchange_config = exchanges[exchange_name]
                if isinstance(exchange_config, dict):
                    adapter = CCXTAdapter(exchange_name, exchange_config)
                else:
                    adapter = CCXTAdapter(exchange_name, exchange_config.dict())
                self._exchange_adapters[exchange_name] = adapter
                return adapter
            
            # Check if it's a forex broker (if multi-market config exists)
            try:
                from config.multi_market_manager import MultiMarketConfigManager
                multi_config_manager = MultiMarketConfigManager(
                    config_file=self.config_path / "multi_market_config.yaml"
                )
                multi_config = multi_config_manager.get_config()
                
                if multi_config.forex.enabled and exchange_name in multi_config.forex.brokers:
                    broker_config = multi_config.forex.brokers[exchange_name]
                    
                    # Create appropriate forex adapter with dynamic imports
                    if broker_config.broker_type.value == 'oanda':
                        try:
                            from src.exchanges.forex.oanda_adapter import OANDAAdapter
                            adapter = OANDAAdapter(exchange_name, broker_config.dict())
                        except ImportError as e:
                            raise ConfigurationError(
                                f"OANDA adapter not available: {e}",
                                suggestions=["Install forex adapter dependencies", "Check OANDA adapter implementation"]
                            )
                    elif broker_config.broker_type.value == 'ib':
                        try:
                            from src.exchanges.forex.ib_adapter import IBAdapter
                            adapter = IBAdapter(exchange_name, broker_config.dict())
                        except ImportError as e:
                            raise ConfigurationError(
                                f"Interactive Brokers adapter not available: {e}",
                                suggestions=["Install IB API dependencies", "Check IB adapter implementation"]
                            )
                    elif broker_config.broker_type.value == 'mt5':
                        try:
                            from src.exchanges.forex.mt5_adapter import MT5Adapter
                            adapter = MT5Adapter(exchange_name, broker_config.dict())
                        except ImportError as e:
                            raise ConfigurationError(
                                f"MetaTrader 5 adapter not available: {e}",
                                suggestions=["Install MT5 dependencies", "Check MT5 adapter implementation"]
                            )
                    else:
                        raise ConfigurationError(f"Unsupported broker type: {broker_config.broker_type}")
                    
                    self._exchange_adapters[exchange_name] = adapter
                    return adapter
                    
            except ImportError:
                # Multi-market config not available, continue with error
                pass
            
            raise ConfigurationError(
                f"Exchange/broker '{exchange_name}' not found in configuration",
                suggestions=[
                    "Check exchange name spelling",
                    "Add exchange configuration to trading_bot_config.yaml",
                    "Use 'genebot list-exchanges' to see available exchanges"
                ]
            )
            
        except Exception as e:
            if isinstance(e, CLIException):
                raise
            raise ConfigurationError(
                f"Failed to create exchange adapter for '{exchange_name}': {e}",
                suggestions=[
                    "Check exchange configuration",
                    "Verify API credentials",
                    "Check network connectivity"
                ]
            )
    
    async def test_exchange_connection(self, exchange_name: str) -> CommandResult:
        """
        Test connection to an exchange/broker.
        
        Args:
            exchange_name: Name of the exchange/broker
            
        Returns:
            CommandResult: Test result
        """
        try:
            adapter = self.get_exchange_adapter(exchange_name)
            
            # Test connection
            await adapter.connect()
            
            # Test authentication if credentials are provided
            if adapter.validate_credentials():
                await adapter.authenticate()
            
            # Perform health check
            health_status = await adapter.health_check()
            
            await adapter.disconnect()
            
            return CommandResult.success(
                f"Successfully connected to {exchange_name}",
                data={
                    'exchange': exchange_name,
                    'connected': True,
                    'authenticated': adapter.is_authenticated,
                    'health_status': health_status
                },
                suggestions=[
                    f"Exchange '{exchange_name}' is ready for trading",
                    "Use 'genebot start' to begin trading"
                ]
            )
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to connect to {exchange_name}: {e}",
                suggestions=[
                    "Check API credentials in configuration",
                    "Verify network connectivity",
                    "Check exchange status",
                    f"Use 'genebot validate-accounts' to test all accounts"
                ]
            )
    
    def get_available_exchanges(self) -> List[Dict[str, Any]]:
        """
        Get list of available exchanges and brokers.
        
        Returns:
            List of exchange/broker information
        """
        exchanges = []
        
        try:
            config = self.config_manager.get_config()
            
            # Add crypto exchanges
            for name, exchange_config in config.exchanges.items():
                exchanges.append({
                    'name': name,
                    'type': 'crypto',
                    'exchange_type': exchange_config.exchange_type.value,
                    'enabled': exchange_config.enabled,
                    'sandbox': exchange_config.sandbox
                })
            
            # Add forex brokers if multi-market config exists
            try:
                from config.multi_market_manager import MultiMarketConfigManager
                multi_config_manager = MultiMarketConfigManager(
                    config_file=self.config_path / "multi_market_config.yaml"
                )
                multi_config = multi_config_manager.get_config()
                
                if multi_config.forex.enabled:
                    for name, broker_config in multi_config.forex.brokers.items():
                        exchanges.append({
                            'name': name,
                            'type': 'forex',
                            'broker_type': broker_config.broker_type.value,
                            'enabled': broker_config.enabled,
                            'sandbox': broker_config.sandbox
                        })
                        
            except ImportError:
                # Multi-market config not available
                pass
            
        except Exception as e:
            self.logger.warning(f"Failed to load exchange configurations: {e}")
        
        return exchanges
    
    def validate_configuration(self) -> CommandResult:
        """
        Validate current configuration using existing validation utilities.
        
        Returns:
            CommandResult: Validation result
        """
        try:
            # Validate main configuration
            config = self.config_manager.get_config()
            
            # Use existing validation utilities if available
            config_file = self.config_path / "trading_bot_config.yaml"
            if config_file.exists() and validate_config_file is not None:
                validation_result = validate_config_file(config_file)
                
                if validation_result.is_valid:
                    return CommandResult.success(
                        "Configuration is valid",
                        data={
                            'config_file': str(config_file),
                            'warnings': validation_result.warnings,
                            'info': validation_result.info
                        },
                        suggestions=[
                            "Configuration passed all validation checks",
                            "Use 'genebot validate-accounts' to test exchange connections"
                        ]
                    )
                else:
                    return CommandResult.error(
                        "Configuration validation failed",
                        data={
                            'errors': validation_result.errors,
                            'warnings': validation_result.warnings
                        },
                        suggestions=[
                            "Fix configuration errors before proceeding",
                            "Check configuration file format and values",
                            "Use configuration templates for reference"
                        ]
                    )
            elif config_file.exists():
                # Basic validation without advanced utilities
                return CommandResult.success(
                    "Configuration loaded successfully",
                    data={'config_file': str(config_file)},
                    suggestions=[
                        "Configuration file loaded",
                        "Advanced validation utilities not available"
                    ]
                )
            else:
                return CommandResult.error(
                    "Configuration file not found",
                    suggestions=[
                        "Run 'genebot init-config' to create configuration files",
                        "Check configuration file path",
                        "Copy from configuration templates"
                    ]
                )
                
        except Exception as e:
            return CommandResult.error(
                f"Configuration validation error: {e}",
                suggestions=[
                    "Check configuration file format",
                    "Verify file permissions",
                    "Check log files for detailed errors"
                ]
            )
    
    def get_database_session(self):
        """Get database session for data operations."""
        try:
            return self.db_connection.get_session()
        except Exception as e:
            raise ConfigurationError(
                f"Failed to get database session: {e}",
                suggestions=[
                    "Check database configuration",
                    "Ensure database is running",
                    "Verify database permissions"
                ]
            )
    
    def get_recent_trades(self, limit: int = 10, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Get recent trades from database.
        
        Args:
            limit: Maximum number of trades to return
            symbol: Optional symbol filter
            
        Returns:
            List of trade data
        """
        try:
            session = self.get_database_session()
            
            query = session.query(TradeModel)
            if symbol:
                query = query.filter(TradeModel.symbol == symbol)
            
            trades = query.order_by(TradeModel.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'amount': float(trade.amount),
                    'price': float(trade.price),
                    'fees': float(trade.fees),
                    'timestamp': trade.timestamp.isoformat(),
                    'exchange': trade.exchange
                }
                for trade in trades
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get recent trades: {e}")
            return []
        finally:
            if 'session' in locals():
                session.close()
    
    def get_open_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Get open orders from database.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of open orders
        """
        try:
            session = self.get_database_session()
            
            query = session.query(OrderModel).filter(OrderModel.status == 'OPEN')
            if symbol:
                query = query.filter(OrderModel.symbol == symbol)
            
            orders = query.order_by(OrderModel.timestamp.desc()).all()
            
            return [
                {
                    'id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'amount': float(order.amount),
                    'price': float(order.price) if order.price else None,
                    'order_type': order.order_type,
                    'status': order.status,
                    'timestamp': order.timestamp.isoformat(),
                    'exchange': order.exchange,
                    'filled_amount': float(order.filled_amount)
                }
                for order in orders
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get open orders: {e}")
            return []
        finally:
            if 'session' in locals():
                session.close()
    
    def get_current_positions(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Get current positions from database.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of current positions
        """
        try:
            session = self.get_database_session()
            
            query = session.query(PositionModel).filter(PositionModel.is_active == 'true')
            if symbol:
                query = query.filter(PositionModel.symbol == symbol)
            
            positions = query.all()
            
            return [
                {
                    'id': position.id,
                    'symbol': position.symbol,
                    'size': float(position.size),
                    'entry_price': float(position.entry_price),
                    'current_price': float(position.current_price),
                    'side': position.side,
                    'exchange': position.exchange,
                    'opened_at': position.opened_at.isoformat(),
                    'pnl': float((position.current_price - position.entry_price) * position.size)
                }
                for position in positions
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get current positions: {e}")
            return []
        finally:
            if 'session' in locals():
                session.close()
    
    def get_strategy_performance(self, strategy_name: str = None, 
                               days: int = 30) -> List[Dict[str, Any]]:
        """
        Get strategy performance data.
        
        Args:
            strategy_name: Optional strategy filter
            days: Number of days to look back
            
        Returns:
            List of strategy performance data
        """
        try:
            session = self.get_database_session()
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = session.query(StrategyPerformanceModel).filter(
                StrategyPerformanceModel.period_start >= cutoff_date
            )
            
            if strategy_name:
                query = query.filter(StrategyPerformanceModel.strategy_name == strategy_name)
            
            performance_data = query.order_by(StrategyPerformanceModel.period_start.desc()).all()
            
            return [
                {
                    'strategy_name': perf.strategy_name,
                    'symbol': perf.symbol,
                    'period_start': perf.period_start.isoformat(),
                    'period_end': perf.period_end.isoformat(),
                    'total_trades': perf.total_trades,
                    'winning_trades': perf.winning_trades,
                    'losing_trades': perf.losing_trades,
                    'total_pnl': float(perf.total_pnl),
                    'win_rate': float(perf.win_rate),
                    'sharpe_ratio': float(perf.sharpe_ratio) if perf.sharpe_ratio else None,
                    'max_drawdown': float(perf.max_drawdown)
                }
                for perf in performance_data
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get strategy performance: {e}")
            return []
        finally:
            if 'session' in locals():
                session.close()
    
    async def close_all_orders(self, symbol: str = None, 
                              exchange: str = None) -> CommandResult:
        """
        Close all open orders using exchange APIs.
        
        Args:
            symbol: Optional symbol filter
            exchange: Optional exchange filter
            
        Returns:
            CommandResult: Operation result
        """
        try:
            # Get open orders from database
            open_orders = self.get_open_orders(symbol)
            
            if not open_orders:
                return CommandResult.success(
                    "No open orders to close",
                    suggestions=["All orders are already closed or filled"]
                )
            
            # Filter by exchange if specified
            if exchange:
                open_orders = [order for order in open_orders if order['exchange'] == exchange]
            
            closed_orders = []
            failed_orders = []
            
            # Group orders by exchange
            orders_by_exchange = {}
            for order in open_orders:
                exchange_name = order['exchange']
                if exchange_name not in orders_by_exchange:
                    orders_by_exchange[exchange_name] = []
                orders_by_exchange[exchange_name].append(order)
            
            # Close orders on each exchange
            for exchange_name, orders in orders_by_exchange.items():
                try:
                    adapter = self.get_exchange_adapter(exchange_name)
                    await adapter.connect()
                    
                    for order in orders:
                        try:
                            await adapter.cancel_order(order['id'], order['symbol'])
                            closed_orders.append(order)
                        except Exception as e:
                            self.logger.error(f"Failed to close order {order['id']}: {e}")
                            failed_orders.append({'order': order, 'error': str(e)})
                    
                    await adapter.disconnect()
                    
                except Exception as e:
                    self.logger.error(f"Failed to connect to {exchange_name}: {e}")
                    for order in orders:
                        failed_orders.append({'order': order, 'error': f"Connection failed: {e}"})
            
            # Prepare result
            if closed_orders and not failed_orders:
                return CommandResult.success(
                    f"Successfully closed {len(closed_orders)} orders",
                    data={
                        'closed_orders': len(closed_orders),
                        'failed_orders': 0
                    },
                    suggestions=["All orders closed successfully"]
                )
            elif closed_orders and failed_orders:
                return CommandResult.warning(
                    f"Closed {len(closed_orders)} orders, {len(failed_orders)} failed",
                    data={
                        'closed_orders': len(closed_orders),
                        'failed_orders': len(failed_orders),
                        'failures': failed_orders
                    },
                    suggestions=[
                        "Some orders could not be closed",
                        "Check exchange connectivity",
                        "Retry failed orders manually"
                    ]
                )
            else:
                return CommandResult.error(
                    f"Failed to close any orders ({len(failed_orders)} failures)",
                    data={'failures': failed_orders},
                    suggestions=[
                        "Check exchange connectivity",
                        "Verify API credentials",
                        "Check order status manually"
                    ]
                )
                
        except Exception as e:
            return CommandResult.error(
                f"Failed to close orders: {e}",
                suggestions=[
                    "Check exchange connectivity",
                    "Verify configuration",
                    "Check log files for detailed errors"
                ]
            )
    
    def cleanup(self):
        """Clean up resources."""
        # Close exchange adapters
        for adapter in self._exchange_adapters.values():
            try:
                if hasattr(adapter, 'disconnect'):
                    asyncio.create_task(adapter.disconnect())
            except Exception as e:
                self.logger.warning(f"Error disconnecting adapter: {e}")
        
        # Close database connection
        if self._db_connection:
            try:
                self._db_connection.close()
            except Exception as e:
                self.logger.warning(f"Error closing database connection: {e}")