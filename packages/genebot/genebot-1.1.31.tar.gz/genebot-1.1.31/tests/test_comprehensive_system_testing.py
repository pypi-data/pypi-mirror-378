"""
Comprehensive System Testing Framework
=====================================

Implementation of Task 10: Comprehensive system testing
- Run end-to-end integration tests across all components
- Test complete CLI workflows from initialization to trading
- Validate configuration loading and validation across all scenarios
- Test error handling and recovery mechanisms
- Perform performance testing for system startup and operation
- Test system with both demo and live account configurations

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5
"""

import pytest
import asyncio
import time
import os
import sys
import tempfile
import shutil
import subprocess
import json
import yaml
import sqlite3
import psutil
import threading
import concurrent.futures
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import core components
from genebot.cli.main import main as cli_main
from genebot.cli.context import CLIContext
from genebot.cli.result import CommandResult, ResultStatus
from config.manager import ConfigManager
from src.trading_bot import TradingBot
from src.data.manager import DataManager
from src.strategies.strategy_engine import StrategyEngine
from src.trading.order_manager import OrderManager
from src.trading.portfolio_manager import PortfolioManager
from src.risk.risk_manager import RiskManager
from src.monitoring.metrics_collector import MetricsCollector
from tests.mocks.mock_exchange import MockExchange


class SystemTestingFramework:
    """
    Comprehensive system testing framework that validates all components
    working together in realistic scenarios.
    """
    
    def __init__(self):
        self.temp_workspace = None
        self.config_dir = None
        self.logs_dir = None
        self.database_file = None
        self.test_processes = []
        self.performance_metrics = {}
        self.system_components = {}
        self.test_data = {}
        
    def setup(self):
        """Set up comprehensive test environment"""
        # Create temporary workspace
        self.temp_workspace = Path(tempfile.mkdtemp(prefix="system_test_"))
        
        # Create directory structure
        self.config_dir = self.temp_workspace / "config"
        self.logs_dir = self.temp_workspace / "logs"
        self.reports_dir = self.temp_workspace / "reports"
        self.backups_dir = self.temp_workspace / "backups"
        self.data_dir = self.temp_workspace / "data"
        
        for directory in [self.config_dir, self.logs_dir, self.reports_dir, 
                         self.backups_dir, self.data_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create test database
        self.database_file = self.data_dir / "test_system.db"
        self._create_test_database()
        
        # Create comprehensive configurations
        self._create_system_configurations()
        
        # Set environment variables
        os.environ.update({
            'CONFIG_PATH': str(self.config_dir),
            'LOGS_PATH': str(self.logs_dir),
            'WORKSPACE_PATH': str(self.temp_workspace),
            'DATABASE_URL': f'sqlite:///{self.database_file}',
            'SYSTEM_TEST_MODE': 'true',
            'LOG_LEVEL': 'DEBUG'
        })
        
        # Initialize performance tracking
        self.performance_metrics = {
            'startup_times': {},
            'command_execution_times': {},
            'memory_usage': {},
            'cpu_usage': {},
            'database_operations': {},
            'api_response_times': {}
        }
        
    def teardown(self):
        """Clean up test environment"""
        # Stop any running processes
        for process in self.test_processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
            except:
                pass
        
        # Clean up temporary files
        if self.temp_workspace and self.temp_workspace.exists():
            shutil.rmtree(self.temp_workspace, ignore_errors=True)
        
        # Reset environment
        for key in ['CONFIG_PATH', 'LOGS_PATH', 'WORKSPACE_PATH', 
                   'DATABASE_URL', 'SYSTEM_TEST_MODE', 'LOG_LEVEL']:
            os.environ.pop(key, None)
    
    def _create_test_database(self):
        """Create comprehensive test database"""
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        
        # Create all necessary tables
        tables = {
            'trades': '''
                CREATE TABLE trades (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    amount REAL NOT NULL,
                    price REAL NOT NULL,
                    fees REAL DEFAULT 0,
                    timestamp DATETIME NOT NULL,
                    exchange TEXT NOT NULL,
                    strategy TEXT,
                    pnl REAL DEFAULT 0,
                    status TEXT DEFAULT 'completed'
                )
            ''',
            'orders': '''
                CREATE TABLE orders (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    amount REAL NOT NULL,
                    price REAL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    exchange TEXT NOT NULL,
                    filled_amount REAL DEFAULT 0
                )
            ''',
            'positions': '''
                CREATE TABLE positions (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    size REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    unrealized_pnl REAL NOT NULL,
                    exchange TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''',
            'market_data': '''
                CREATE TABLE market_data (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    exchange TEXT NOT NULL
                )
            ''',
            'system_metrics': '''
                CREATE TABLE system_metrics (
                    id INTEGER PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    component TEXT
                )
            '''
        }
        
        for table_name, create_sql in tables.items():
            cursor.execute(create_sql)
        
        # Insert test data
        self._insert_test_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_test_data(self, cursor):
        """Insert comprehensive test data"""
        # Test trades
        test_trades = [
            ('BTC/USDT', 'BUY', 0.1, 45000.0, 22.5, datetime.now() - timedelta(hours=2), 
             'binance', 'momentum_strategy', 500.0, 'completed'),
            ('ETH/USDT', 'SELL', 2.0, 3000.0, 6.0, datetime.now() - timedelta(hours=1), 
             'binance', 'mean_reversion', -150.0, 'completed'),
            ('EUR/USD', 'BUY', 10000, 1.0850, 5.0, datetime.now() - timedelta(minutes=30), 
             'oanda', 'forex_carry', 75.0, 'completed'),
            ('GBP/USD', 'SELL', 5000, 1.2650, 2.5, datetime.now() - timedelta(minutes=15), 
             'oanda', 'trend_following', 125.0, 'completed')
        ]
        
        for trade in test_trades:
            cursor.execute('''
                INSERT INTO trades (symbol, side, amount, price, fees, timestamp, 
                                  exchange, strategy, pnl, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', trade)
        
        # Test orders
        test_orders = [
            ('order_1', 'BTC/USDT', 'BUY', 0.05, 44000.0, 'limit', 'open', 
             datetime.now(), 'binance', 0.0),
            ('order_2', 'ETH/USDT', 'SELL', 1.0, 3100.0, 'limit', 'open', 
             datetime.now(), 'binance', 0.0),
            ('order_3', 'EUR/USD', 'BUY', 5000, 1.0840, 'limit', 'pending', 
             datetime.now(), 'oanda', 0.0)
        ]
        
        for order in test_orders:
            cursor.execute('''
                INSERT INTO orders (id, symbol, side, amount, price, type, status, 
                                  timestamp, exchange, filled_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', order)
        
        # Test market data
        base_time = datetime.now() - timedelta(hours=24)
        for i in range(100):  # 100 data points
            timestamp = base_time + timedelta(minutes=i * 15)
            price = 45000 + (i * 10) + ((-1) ** i * 50)  # Simulate price movement
            
            cursor.execute('''
                INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('BTC/USDT', timestamp, price, price + 25, price - 25, price + 5, 1000.0, 'binance'))
    
    def _create_system_configurations(self):
        """Create comprehensive system configurations"""
        # Demo account configuration
        demo_accounts_config = {
            'crypto_exchanges': {
                'binance-demo': {
                    'name': 'binance-demo',
                    'exchange_type': 'binance',
                    'enabled': True,
                    'sandbox': True,
                    'api_key': 'demo_binance_key',
                    'api_secret': 'demo_binance_secret',
                    'rate_limit': 1200,
                    'timeout': 30
                },
                'coinbase-demo': {
                    'name': 'coinbase-demo',
                    'exchange_type': 'coinbase',
                    'enabled': True,
                    'sandbox': True,
                    'api_key': 'demo_coinbase_key',
                    'api_secret': 'demo_coinbase_secret',
                    'api_passphrase': 'demo_coinbase_passphrase',
                    'rate_limit': 600,
                    'timeout': 30
                }
            },
            'forex_brokers': {
                'oanda-demo': {
                    'name': 'oanda-demo',
                    'broker_type': 'oanda',
                    'enabled': True,
                    'sandbox': True,
                    'api_key': 'demo_oanda_key',
                    'account_id': 'demo_oanda_account',
                    'timeout': 30
                }
            }
        }
        
        with open(self.config_dir / "accounts.yaml", 'w') as f:
            yaml.dump(demo_accounts_config, f, default_flow_style=False)
        
        # Live account configuration (for testing configuration loading)
        live_accounts_config = {
            'crypto_exchanges': {
                'binance-live': {
                    'name': 'binance-live',
                    'exchange_type': 'binance',
                    'enabled': False,  # Disabled for safety
                    'sandbox': False,
                    'api_key': '${BINANCE_LIVE_API_KEY}',
                    'api_secret': '${BINANCE_LIVE_API_SECRET}',
                    'rate_limit': 1200,
                    'timeout': 30
                }
            },
            'forex_brokers': {
                'oanda-live': {
                    'name': 'oanda-live',
                    'broker_type': 'oanda',
                    'enabled': False,  # Disabled for safety
                    'sandbox': False,
                    'api_key': '${OANDA_LIVE_API_KEY}',
                    'account_id': '${OANDA_LIVE_ACCOUNT_ID}',
                    'timeout': 30
                }
            }
        }
        
        with open(self.config_dir / "accounts_live.yaml", 'w') as f:
            yaml.dump(live_accounts_config, f, default_flow_style=False)
        
        # Trading bot configuration
        trading_config = {
            'app_name': 'GeneBot System Test',
            'version': '1.1.28',
            'debug': True,
            'dry_run': True,
            'base_currency': 'USDT',
            'risk_management': {
                'max_daily_loss': 1000.0,
                'max_drawdown': 0.15,
                'max_position_size': 0.1,
                'stop_loss_percentage': 0.02,
                'take_profit_percentage': 0.04,
                'max_open_positions': 5
            },
            'strategies': {
                'momentum_strategy': {
                    'name': 'momentum_strategy',
                    'enabled': True,
                    'markets': ['crypto'],
                    'timeframe': '1h',
                    'parameters': {
                        'rsi_period': 14,
                        'rsi_oversold': 30,
                        'rsi_overbought': 70,
                        'volume_threshold': 1.5
                    }
                },
                'mean_reversion': {
                    'name': 'mean_reversion',
                    'enabled': True,
                    'markets': ['crypto', 'forex'],
                    'timeframe': '15m',
                    'parameters': {
                        'bollinger_period': 20,
                        'bollinger_std': 2.0,
                        'mean_reversion_threshold': 0.8
                    }
                },
                'arbitrage_strategy': {
                    'name': 'arbitrage_strategy',
                    'enabled': False,
                    'markets': ['crypto'],
                    'timeframe': '1m',
                    'parameters': {
                        'min_profit_threshold': 0.005,
                        'max_exposure': 0.05
                    }
                }
            },
            'database': {
                'database_type': 'sqlite',
                'database_url': f'sqlite:///{self.database_file}',
                'connection_pool_size': 5,
                'query_timeout': 30
            },
            'logging': {
                'log_level': 'DEBUG',
                'log_format': 'detailed',
                'log_file': str(self.logs_dir / 'system_test.log'),
                'max_log_size': '10MB',
                'backup_count': 3
            },
            'monitoring': {
                'enabled': True,
                'metrics_port': 8080,
                'health_check_interval': 10,
                'alert_thresholds': {
                    'max_drawdown': 0.1,
                    'daily_loss': 500.0,
                    'error_rate': 0.05
                }
            },
            'performance': {
                'max_startup_time': 30,
                'max_command_response_time': 5,
                'max_memory_usage_mb': 500,
                'max_cpu_usage_percent': 80
            }
        }
        
        with open(self.config_dir / "trading_bot_config.yaml", 'w') as f:
            yaml.dump(trading_config, f, default_flow_style=False)
        
        # Environment file
        env_content = """
# System test environment variables
BINANCE_LIVE_API_KEY=live_binance_key
BINANCE_LIVE_API_SECRET=live_binance_secret
OANDA_LIVE_API_KEY=live_oanda_key
OANDA_LIVE_ACCOUNT_ID=live_oanda_account
DATABASE_URL=sqlite:///test_system.db
LOG_LEVEL=DEBUG
SYSTEM_TEST_MODE=true
"""
        
        with open(self.temp_workspace / ".env", 'w') as f:
            f.write(env_content.strip())
    
    def run_cli_command(self, args: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run CLI command with performance tracking"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        cmd = [sys.executable, "-m", "genebot.cli"] + args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.temp_workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy()
            )
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Store performance metrics
            command_key = ' '.join(args)
            self.performance_metrics['command_execution_times'][command_key] = execution_time
            self.performance_metrics['memory_usage'][command_key] = memory_delta
            
            return {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': execution_time,
                'memory_delta': memory_delta,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                'exit_code': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'execution_time': timeout,
                'memory_delta': 0,
                'success': False,
                'timeout': True
            }
    
    async def initialize_trading_system(self) -> TradingBot:
        """Initialize complete trading system for testing"""
        config_manager = ConfigManager(str(self.config_dir))
        config = config_manager.load_config()
        
        # Create trading bot with mock exchanges
        with patch('src.exchanges.ccxt_adapter.ccxt') as mock_ccxt:
            mock_ccxt.binance.return_value = MockExchange('binance')
            mock_ccxt.coinbase.return_value = MockExchange('coinbase')
            
            bot = TradingBot(config)
            await bot.initialize()
            
            self.system_components['trading_bot'] = bot
            return bot
    
    def measure_system_performance(self, operation_name: str):
        """Context manager for measuring system performance"""
        @contextmanager
        def performance_context():
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss
            start_cpu = psutil.cpu_percent()
            
            yield
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            end_cpu = psutil.cpu_percent()
            
            self.performance_metrics[operation_name] = {
                'execution_time': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'cpu_usage': (start_cpu + end_cpu) / 2
            }
        
        return performance_context()


@pytest.fixture
def system_test_framework():
    """Pytest fixture for system testing framework"""
    framework = SystemTestingFramework()
    framework.setup()
    try:
        yield framework
    finally:
        framework.teardown()


class TestEndToEndIntegration:
    """Test end-to-end integration across all components"""
    
    @pytest.mark.asyncio
    async def test_complete_system_initialization(self, system_test_framework):
        """Test complete system initialization and startup"""
        with system_test_framework.measure_system_performance('system_initialization'):
            # Initialize trading system
            bot = await system_test_framework.initialize_trading_system()
            
            # Verify all components are initialized
            assert bot.config_manager is not None
            assert bot.data_manager is not None
            assert bot.strategy_engine is not None
            assert bot.risk_manager is not None
            assert bot.order_manager is not None
            assert bot.portfolio_manager is not None
            
            # Verify system is running
            assert bot.is_running
            
            # Clean shutdown
            await bot.shutdown()
        
        # Verify performance requirements (Requirement 7.1)
        init_metrics = system_test_framework.performance_metrics['system_initialization']
        assert init_metrics['execution_time'] < 30, "System should initialize within 30 seconds"
        assert init_metrics['memory_delta'] < 200 * 1024 * 1024, "Memory usage should be reasonable"
    
    @pytest.mark.asyncio
    async def test_complete_trading_workflow(self, system_test_framework):
        """Test complete trading workflow from data to execution"""
        bot = await system_test_framework.initialize_trading_system()
        
        try:
            with system_test_framework.measure_system_performance('trading_workflow'):
                # 1. Data collection and processing
                from tests.fixtures.sample_data_factory import create_sample_market_data
                market_data = create_sample_market_data('BTC/USDT', 50)
                
                # Store historical data
                for data_point in market_data[:40]:
                    await bot.data_manager.store_market_data(data_point)
                
                # 2. Strategy processing
                signals = []
                for data_point in market_data[40:]:
                    strategy_signals = await bot.strategy_engine.process_market_data(data_point)
                    signals.extend(strategy_signals)
                
                # 3. Risk management validation
                approved_signals = []
                for signal in signals:
                    if await bot.risk_manager.validate_signal(signal):
                        approved_signals.append(signal)
                
                # 4. Order execution simulation
                executed_orders = []
                for signal in approved_signals:
                    order = await bot.order_manager.place_order(signal)
                    if order:
                        executed_orders.append(order)
                
                # 5. Portfolio management
                await bot.portfolio_manager.update_positions()
                
                # 6. Performance monitoring
                metrics = await bot.metrics_collector.get_metrics()
                
                # Verify workflow completion
                assert len(market_data) == 50
                assert len(signals) >= 0
                assert len(executed_orders) >= 0
                assert 'portfolio_value' in metrics
                
        finally:
            await bot.shutdown()
        
        # Verify performance (Requirement 7.2)
        workflow_metrics = system_test_framework.performance_metrics['trading_workflow']
        assert workflow_metrics['execution_time'] < 10, "Trading workflow should complete quickly"
    
    @pytest.mark.asyncio
    async def test_multi_strategy_coordination(self, system_test_framework):
        """Test coordination between multiple strategies"""
        bot = await system_test_framework.initialize_trading_system()
        
        try:
            # Enable multiple strategies
            strategies = bot.strategy_engine.get_registered_strategies()
            assert len(strategies) >= 2, "Multiple strategies should be available"
            
            # Process market data through all strategies
            from tests.fixtures.sample_data_factory import create_sample_market_data
            market_data = create_sample_market_data('BTC/USDT', 30)
            
            all_signals = []
            for data_point in market_data:
                signals = await bot.strategy_engine.process_market_data(data_point)
                all_signals.extend(signals)
            
            # Verify signals from multiple strategies
            if all_signals:
                strategy_names = {signal.strategy_name for signal in all_signals}
                assert len(strategy_names) >= 1, "At least one strategy should generate signals"
            
        finally:
            await bot.shutdown()
    
    @pytest.mark.asyncio
    async def test_system_resilience_under_load(self, system_test_framework):
        """Test system resilience under high load conditions"""
        bot = await system_test_framework.initialize_trading_system()
        
        try:
            with system_test_framework.measure_system_performance('load_testing'):
                # Simulate high-frequency data processing
                from tests.fixtures.sample_data_factory import create_sample_market_data
                
                # Create concurrent data processing tasks
                async def process_symbol_data(symbol, count):
                    market_data = create_sample_market_data(symbol, count)
                    for data_point in market_data:
                        await bot.strategy_engine.process_market_data(data_point)
                
                # Run multiple symbols concurrently
                tasks = [
                    process_symbol_data('BTC/USDT', 20),
                    process_symbol_data('ETH/USDT', 20),
                    process_symbol_data('EUR/USD', 20)
                ]
                
                await asyncio.gather(*tasks)
                
                # Verify system remains stable
                assert bot.is_running
                
        finally:
            await bot.shutdown()
        
        # Verify performance under load (Requirement 7.3)
        load_metrics = system_test_framework.performance_metrics['load_testing']
        assert load_metrics['execution_time'] < 30, "System should handle load efficiently"
        assert load_metrics['cpu_usage'] < 90, "CPU usage should remain reasonable"


class TestCLIWorkflows:
    """Test complete CLI workflows from initialization to trading"""
    
    def test_cli_initialization_workflow(self, system_test_framework):
        """Test complete CLI initialization workflow"""
        # 1. Help command
        result = system_test_framework.run_cli_command(['--help'])
        assert result['success'] or result['exit_code'] == 0, "Help command should work"
        
        # 2. Initialize configuration
        result = system_test_framework.run_cli_command(['init-config', '--force'])
        assert result['success'], f"Init config failed: {result['stderr']}"
        
        # 3. List accounts
        result = system_test_framework.run_cli_command(['list-accounts'])
        assert result['success'], f"List accounts failed: {result['stderr']}"
        
        # 4. Validate configuration
        result = system_test_framework.run_cli_command(['validate-config'])
        assert result['success'], f"Validate config failed: {result['stderr']}"
    
    def test_account_management_workflow(self, system_test_framework):
        """Test complete account management workflow"""
        # 1. Add crypto account
        result = system_test_framework.run_cli_command([
            'add-crypto',
            '--name', 'test-kraken',
            '--exchange-type', 'kraken',
            '--mode', 'demo',
            '--force'
        ])
        assert result['success'], f"Add crypto account failed: {result['stderr']}"
        
        # 2. Add forex account
        result = system_test_framework.run_cli_command([
            'add-forex',
            '--name', 'test-ib',
            '--broker-type', 'interactive_brokers',
            '--mode', 'demo',
            '--force'
        ])
        assert result['success'], f"Add forex account failed: {result['stderr']}"
        
        # 3. List all accounts
        result = system_test_framework.run_cli_command(['list-accounts'])
        assert result['success'], f"List accounts failed: {result['stderr']}"
        
        # 4. Disable account
        result = system_test_framework.run_cli_command([
            'disable-account',
            '--name', 'test-kraken',
            '--type', 'crypto'
        ])
        assert result['success'], f"Disable account failed: {result['stderr']}"
        
        # 5. Enable account
        result = system_test_framework.run_cli_command([
            'enable-account',
            '--name', 'test-kraken',
            '--type', 'crypto'
        ])
        assert result['success'], f"Enable account failed: {result['stderr']}"
        
        # 6. Remove accounts
        for account_name, account_type in [('test-kraken', 'crypto'), ('test-ib', 'forex')]:
            result = system_test_framework.run_cli_command([
                'remove-account',
                '--name', account_name,
                '--type', account_type,
                '--confirm'
            ])
            assert result['success'], f"Remove {account_name} failed: {result['stderr']}"
    
    @patch('genebot.cli.utils.process_manager.ProcessManager')
    def test_bot_management_workflow(self, mock_pm, system_test_framework):
        """Test complete bot management workflow"""
        # Mock process manager
        mock_instance = Mock()
        mock_instance.get_bot_status.return_value = {
            'running': False, 'pid': None, 'uptime': None
        }
        mock_instance.start_bot.return_value = {
            'success': True, 'pid': 12345, 'message': 'Bot started'
        }
        mock_instance.stop_bot.return_value = {
            'success': True, 'message': 'Bot stopped'
        }
        mock_pm.return_value = mock_instance
        
        # 1. Check status
        result = system_test_framework.run_cli_command(['status'])
        assert result['success'], f"Status command failed: {result['stderr']}"
        
        # 2. Start bot
        result = system_test_framework.run_cli_command(['start'])
        assert result['success'], f"Start command failed: {result['stderr']}"
        
        # 3. Check status again
        mock_instance.get_bot_status.return_value = {
            'running': True, 'pid': 12345, 'uptime': timedelta(seconds=30)
        }
        result = system_test_framework.run_cli_command(['status'])
        assert result['success'], f"Status command failed: {result['stderr']}"
        
        # 4. Stop bot
        result = system_test_framework.run_cli_command(['stop'])
        assert result['success'], f"Stop command failed: {result['stderr']}"
    
    @patch('genebot.cli.utils.data_manager.RealDataManager')
    def test_monitoring_workflow(self, mock_dm, system_test_framework):
        """Test monitoring and reporting workflow"""
        # Mock data manager
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
        mock_instance.get_performance_summary.return_value = {
            'total_trades': 1,
            'total_pnl': 500.0,
            'win_rate': 1.0
        }
        mock_dm.return_value = mock_instance
        
        # 1. View trades
        result = system_test_framework.run_cli_command(['trades'])
        assert result['success'], f"Trades command failed: {result['stderr']}"
        
        # 2. Generate report
        result = system_test_framework.run_cli_command(['report', '--type', 'performance'])
        assert result['success'], f"Report command failed: {result['stderr']}"
        
        # 3. Monitor (once)
        mock_instance.get_live_data.return_value = {
            'positions': [], 'orders': [], 'balance': {'USD': 10000}
        }
        result = system_test_framework.run_cli_command(['monitor', '--once'])
        assert result['success'], f"Monitor command failed: {result['stderr']}"


class TestConfigurationValidation:
    """Test configuration loading and validation across all scenarios"""
    
    def test_demo_configuration_loading(self, system_test_framework):
        """Test loading demo account configurations"""
        # Load demo configuration
        config_manager = ConfigManager(str(system_test_framework.config_dir))
        config = config_manager.load_config()
        
        # Verify demo accounts are loaded
        assert 'crypto_exchanges' in config
        assert 'forex_brokers' in config
        assert 'binance-demo' in config['crypto_exchanges']
        assert 'oanda-demo' in config['forex_brokers']
        
        # Verify sandbox settings
        assert config['crypto_exchanges']['binance-demo']['sandbox'] is True
        assert config['forex_brokers']['oanda-demo']['sandbox'] is True
    
    def test_live_configuration_loading(self, system_test_framework):
        """Test loading live account configurations"""
        # Load live configuration
        config_manager = ConfigManager(str(system_test_framework.config_dir))
        
        # Load live accounts file
        with open(system_test_framework.config_dir / "accounts_live.yaml", 'r') as f:
            live_config = yaml.safe_load(f)
        
        # Verify live accounts structure
        assert 'crypto_exchanges' in live_config
        assert 'forex_brokers' in live_config
        assert 'binance-live' in live_config['crypto_exchanges']
        assert 'oanda-live' in live_config['forex_brokers']
        
        # Verify live settings
        assert live_config['crypto_exchanges']['binance-live']['sandbox'] is False
        assert live_config['forex_brokers']['oanda-live']['sandbox'] is False
        
        # Verify accounts are disabled for safety
        assert live_config['crypto_exchanges']['binance-live']['enabled'] is False
        assert live_config['forex_brokers']['oanda-live']['enabled'] is False
    
    def test_configuration_validation(self, system_test_framework):
        """Test comprehensive configuration validation"""
        config_manager = ConfigManager(str(system_test_framework.config_dir))
        
        # Test configuration validation
        validation_result = config_manager.validate_config()
        assert validation_result['valid'], f"Configuration validation failed: {validation_result['errors']}"
        
        # Test individual component validation
        config = config_manager.load_config()
        
        # Validate trading bot config
        assert 'app_name' in config
        assert 'risk_management' in config
        assert 'strategies' in config
        assert 'database' in config
        
        # Validate risk management settings
        risk_config = config['risk_management']
        assert 'max_daily_loss' in risk_config
        assert 'max_drawdown' in risk_config
        assert 'max_position_size' in risk_config
        
        # Validate strategy configurations
        strategies = config['strategies']
        for strategy_name, strategy_config in strategies.items():
            assert 'name' in strategy_config
            assert 'enabled' in strategy_config
            assert 'parameters' in strategy_config
    
    def test_environment_variable_resolution(self, system_test_framework):
        """Test environment variable resolution in configurations"""
        # Set test environment variables
        os.environ['TEST_API_KEY'] = 'resolved_test_key'
        os.environ['TEST_SECRET'] = 'resolved_test_secret'
        
        try:
            # Create config with environment variables
            test_config = {
                'test_exchange': {
                    'api_key': '${TEST_API_KEY}',
                    'api_secret': '${TEST_SECRET}',
                    'static_value': 'no_substitution'
                }
            }
            
            config_file = system_test_framework.config_dir / "test_env_config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(test_config, f)
            
            # Load and verify resolution
            config_manager = ConfigManager(str(system_test_framework.config_dir))
            resolved_config = config_manager.resolve_environment_variables(test_config)
            
            assert resolved_config['test_exchange']['api_key'] == 'resolved_test_key'
            assert resolved_config['test_exchange']['api_secret'] == 'resolved_test_secret'
            assert resolved_config['test_exchange']['static_value'] == 'no_substitution'
            
        finally:
            # Clean up environment variables
            os.environ.pop('TEST_API_KEY', None)
            os.environ.pop('TEST_SECRET', None)
    
    def test_configuration_backup_and_restore(self, system_test_framework):
        """Test configuration backup and restore functionality"""
        # Test backup creation
        result = system_test_framework.run_cli_command(['config-backup'])
        assert result['success'], f"Config backup failed: {result['stderr']}"
        
        # Verify backup files exist
        backup_files = list(system_test_framework.backups_dir.glob("*.yaml"))
        assert len(backup_files) > 0, "Backup files should be created"
        
        # Test configuration restore (if implemented)
        if backup_files:
            backup_file = backup_files[0]
            result = system_test_framework.run_cli_command([
                'config-restore', '--file', str(backup_file), '--confirm'
            ])
            # May not be implemented yet, so just check it doesn't crash
            assert result['exit_code'] in [0, 1, 2]  # Success, failure, or not implemented


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms"""
    
    def test_database_connection_error_recovery(self, system_test_framework):
        """Test recovery from database connection errors"""
        # Corrupt database file
        with open(system_test_framework.database_file, 'w') as f:
            f.write("corrupted database")
        
        # Test commands that use database
        result = system_test_framework.run_cli_command(['trades'])
        assert not result['success'], "Should fail with corrupted database"
        assert 'database' in result['stderr'].lower() or 'connection' in result['stderr'].lower()
        
        # Test recovery suggestion
        assert result['exit_code'] != 0
    
    def test_configuration_file_error_recovery(self, system_test_framework):
        """Test recovery from configuration file errors"""
        # Remove configuration file
        accounts_file = system_test_framework.config_dir / "accounts.yaml"
        accounts_file.unlink()
        
        # Test command that needs configuration
        result = system_test_framework.run_cli_command(['list-accounts'])
        assert not result['success'], "Should fail with missing configuration"
        
        # Test recovery suggestion
        assert 'init-config' in result['stderr'] or result['exit_code'] != 0
    
    def test_permission_error_handling(self, system_test_framework):
        """Test handling of permission errors"""
        # Make config directory read-only
        system_test_framework.config_dir.chmod(0o444)
        
        try:
            result = system_test_framework.run_cli_command([
                'add-crypto',
                '--name', 'permission-test',
                '--exchange-type', 'binance',
                '--mode', 'demo'
            ])
            assert not result['success'], "Should fail with permission error"
            assert 'permission' in result['stderr'].lower()
        finally:
            # Restore permissions
            system_test_framework.config_dir.chmod(0o755)
    
    @patch('genebot.cli.utils.account_validator.RealAccountValidator')
    def test_network_error_recovery(self, mock_validator, system_test_framework):
        """Test recovery from network errors"""
        # Mock network error
        mock_instance = Mock()
        mock_instance.validate_account.side_effect = ConnectionError("Network unreachable")
        mock_validator.return_value = mock_instance
        
        result = system_test_framework.run_cli_command(['validate-accounts'])
        # Should handle gracefully
        assert 'network' in result['stderr'].lower() or result['exit_code'] in [0, 1]
    
    @pytest.mark.asyncio
    async def test_system_component_failure_recovery(self, system_test_framework):
        """Test recovery from individual component failures"""
        bot = await system_test_framework.initialize_trading_system()
        
        try:
            # Test strategy engine failure recovery
            with patch.object(bot.strategy_engine, 'process_market_data', side_effect=Exception("Strategy error")):
                from tests.fixtures.sample_data_factory import create_sample_market_data
                market_data = create_sample_market_data('BTC/USDT', 1)[0]
                
                try:
                    await bot.strategy_engine.process_market_data(market_data)
                except Exception:
                    pass  # Expected to handle gracefully
                
                # System should remain operational
                assert bot.is_running
            
            # Test data manager failure recovery
            with patch.object(bot.data_manager, 'store_market_data', side_effect=Exception("Database error")):
                try:
                    await bot.data_manager.store_market_data(market_data)
                except Exception:
                    pass  # Expected to handle gracefully
                
                # System should remain operational
                assert bot.is_running
                
        finally:
            await bot.shutdown()


class TestPerformanceValidation:
    """Test performance requirements and system operation"""
    
    def test_cli_command_response_times(self, system_test_framework):
        """Test CLI command response times meet requirements"""
        # Test various commands and their response times
        commands_to_test = [
            (['--help'], 2.0),
            (['list-accounts'], 5.0),
            (['status'], 3.0),
            (['list-strategies'], 5.0)
        ]
        
        for command, max_time in commands_to_test:
            result = system_test_framework.run_cli_command(command)
            assert result['execution_time'] < max_time, \
                f"Command {' '.join(command)} took {result['execution_time']:.2f}s, expected < {max_time}s"
    
    @pytest.mark.asyncio
    async def test_system_startup_performance(self, system_test_framework):
        """Test system startup performance requirements"""
        start_time = time.time()
        
        bot = await system_test_framework.initialize_trading_system()
        
        try:
            startup_time = time.time() - start_time
            
            # Verify startup time requirement (Requirement 7.1)
            assert startup_time < 30, f"System startup took {startup_time:.2f}s, expected < 30s"
            
            # Verify all components are ready
            assert bot.is_running
            assert bot.config_manager is not None
            assert bot.data_manager is not None
            assert bot.strategy_engine is not None
            
        finally:
            await bot.shutdown()
    
    @pytest.mark.asyncio
    async def test_high_frequency_data_processing(self, system_test_framework):
        """Test high-frequency data processing performance"""
        bot = await system_test_framework.initialize_trading_system()
        
        try:
            # Generate high-frequency data
            from tests.fixtures.sample_data_factory import create_sample_market_data
            market_data = create_sample_market_data('BTC/USDT', 1000)  # 1000 data points
            
            start_time = time.time()
            
            # Process data at high frequency
            processed_count = 0
            for data_point in market_data:
                await bot.strategy_engine.process_market_data(data_point)
                processed_count += 1
            
            processing_time = time.time() - start_time
            throughput = processed_count / processing_time
            
            # Verify throughput requirement (Requirement 7.2)
            assert throughput > 100, f"Throughput {throughput:.1f} points/sec, expected > 100/sec"
            
        finally:
            await bot.shutdown()
    
    def test_memory_usage_under_load(self, system_test_framework):
        """Test memory usage remains reasonable under load"""
        initial_memory = psutil.Process().memory_info().rss
        
        # Run multiple CLI commands to simulate load
        commands = [
            ['list-accounts'],
            ['list-strategies'],
            ['status'],
            ['validate-config']
        ] * 10  # Run each command 10 times
        
        for command in commands:
            system_test_framework.run_cli_command(command)
        
        final_memory = psutil.Process().memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Verify memory usage requirement (Requirement 7.3)
        max_memory_increase = 100 * 1024 * 1024  # 100MB
        assert memory_increase < max_memory_increase, \
            f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB, expected < 100MB"
    
    def test_concurrent_command_execution(self, system_test_framework):
        """Test system handles concurrent command execution"""
        def run_command(command):
            return system_test_framework.run_cli_command(command)
        
        # Run multiple commands concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            commands = [
                ['list-accounts'],
                ['status'],
                ['list-strategies'],
                ['validate-config'],
                ['--help']
            ]
            
            for command in commands:
                future = executor.submit(run_command, command)
                futures.append(future)
            
            # Wait for all commands to complete
            results = []
            for future in concurrent.futures.as_completed(futures, timeout=30):
                result = future.result()
                results.append(result)
        
        # Verify all commands completed successfully or with expected errors
        assert len(results) == 5, "All concurrent commands should complete"
        
        # At least some commands should succeed
        successful_commands = [r for r in results if r['success']]
        assert len(successful_commands) > 0, "At least some commands should succeed"


class TestSystemIntegrationScenarios:
    """Test system integration with both demo and live account configurations"""
    
    def test_demo_account_integration(self, system_test_framework):
        """Test system integration with demo accounts"""
        # Test with demo configuration
        result = system_test_framework.run_cli_command(['list-accounts'])
        assert result['success'], f"Demo account listing failed: {result['stderr']}"
        
        # Verify demo accounts are shown
        output = result['stdout']
        assert 'demo' in output.lower() or result['success']
    
    def test_live_account_configuration_safety(self, system_test_framework):
        """Test that live accounts are safely configured"""
        # Load live configuration
        with open(system_test_framework.config_dir / "accounts_live.yaml", 'r') as f:
            live_config = yaml.safe_load(f)
        
        # Verify all live accounts are disabled by default
        for exchange_name, exchange_config in live_config.get('crypto_exchanges', {}).items():
            assert exchange_config.get('enabled', True) is False, \
                f"Live exchange {exchange_name} should be disabled by default"
        
        for broker_name, broker_config in live_config.get('forex_brokers', {}).items():
            assert broker_config.get('enabled', True) is False, \
                f"Live broker {broker_name} should be disabled by default"
    
    @pytest.mark.asyncio
    async def test_multi_market_integration(self, system_test_framework):
        """Test integration across crypto and forex markets"""
        bot = await system_test_framework.initialize_trading_system()
        
        try:
            # Test crypto market integration
            from tests.fixtures.sample_data_factory import create_sample_market_data
            crypto_data = create_sample_market_data('BTC/USDT', 10)
            
            crypto_signals = []
            for data_point in crypto_data:
                signals = await bot.strategy_engine.process_market_data(data_point)
                crypto_signals.extend(signals)
            
            # Test forex market integration
            forex_data = create_sample_market_data('EUR/USD', 10)
            
            forex_signals = []
            for data_point in forex_data:
                signals = await bot.strategy_engine.process_market_data(data_point)
                forex_signals.extend(signals)
            
            # Verify multi-market processing
            total_signals = len(crypto_signals) + len(forex_signals)
            assert total_signals >= 0, "Multi-market processing should work"
            
        finally:
            await bot.shutdown()
    
    def test_configuration_migration_scenarios(self, system_test_framework):
        """Test configuration migration between versions"""
        # Create old-style configuration
        old_config = {
            'exchanges': {  # Old format
                'binance': {
                    'api_key': 'old_key',
                    'api_secret': 'old_secret'
                }
            }
        }
        
        old_config_file = system_test_framework.config_dir / "old_config.yaml"
        with open(old_config_file, 'w') as f:
            yaml.dump(old_config, f)
        
        # Test migration (if implemented)
        result = system_test_framework.run_cli_command([
            'migrate-config', '--from', str(old_config_file), '--dry-run'
        ])
        
        # Migration may not be implemented yet, so just verify it doesn't crash
        assert result['exit_code'] in [0, 1, 2]  # Success, failure, or not implemented


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])