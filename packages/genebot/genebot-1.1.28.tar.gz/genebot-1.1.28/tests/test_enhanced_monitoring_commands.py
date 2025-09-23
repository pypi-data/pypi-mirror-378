"""
Tests for Enhanced Monitoring Commands
=====================================

Tests for the enhanced bot status and monitoring commands with real process monitoring,
live monitoring, strategy information, and order closure functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from genebot.cli.commands.monitoring import (
    MonitorCommand, TradesCommand, ReportCommand, CloseOrdersCommand,
    ComprehensiveStatusCommand
)
from genebot.cli.context import CLIContext
from genebot.cli.result import CommandResult
from genebot.cli.utils.logger import CLILogger
from genebot.cli.utils.error_handler import CLIErrorHandler
from genebot.cli.utils.data_manager import BotStatusInfo, TradeInfo, PositionInfo, TradingSummary
from genebot.cli.utils.process_manager import BotStatus, ProcessInfo
from argparse import Namespace


class TestEnhancedMonitorCommand:
    """Test enhanced monitor command with real process monitoring"""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock CLI context"""
        context = Mock(spec=CLIContext)
        context.workspace_path = Path("/test/workspace")
        return context
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock CLI logger"""
        return Mock(spec=CLILogger)
    
    @pytest.fixture
    def mock_error_handler(self):
        """Create mock error handler"""
        return Mock(spec=CLIErrorHandler)
    
    @pytest.fixture
    def monitor_command(self, mock_context, mock_logger, mock_error_handler):
        """Create monitor command instance"""
        return MonitorCommand(mock_context, mock_logger, mock_error_handler)
    
    @patch('genebot.cli.commands.monitoring.RealDataManager')
    @patch('genebot.cli.commands.monitoring.ProcessManager')
    def test_monitor_with_real_process_status(self, mock_process_manager_class, mock_data_manager_class, monitor_command):
        """Test monitor command with real process status integration"""
        # Setup mocks
        mock_process_manager = Mock()
        mock_process_manager_class.return_value = mock_process_manager
        
        mock_data_manager = Mock()
        mock_data_manager_class.return_value.__enter__.return_value = mock_data_manager
        
        # Mock process status
        process_info = ProcessInfo(
            pid=12345,
            name="python",
            status="running",
            cpu_percent=15.5,
            memory_percent=8.2,
            memory_mb=256.0,
            create_time=datetime.now() - timedelta(hours=2),
            uptime=timedelta(hours=2),
            command_line=["python", "main.py"]
        )
        
        bot_status = BotStatus(
            running=True,
            pid=12345,
            uptime=timedelta(hours=2),
            memory_usage=256.0,
            cpu_usage=15.5,
            last_activity=datetime.now(),
            process_info=process_info
        )
        
        mock_process_manager.get_bot_status.return_value = bot_status
        
        # Mock trading status
        trading_status = BotStatusInfo(
            active_positions=3,
            total_pnl_today=Decimal('125.50'),
            trades_today=8,
            active_strategies=['RSIStrategy', 'MovingAverageStrategy'],
            last_activity=datetime.now(),
            error_count=0
        )
        
        mock_data_manager.get_bot_status_info.return_value = trading_status
        mock_data_manager.get_active_positions.return_value = []
        mock_data_manager.get_recent_activity.return_value = ["Test activity"]
        
        # Test args
        args = Namespace(refresh=1, account=None)
        
        # Mock KeyboardInterrupt to stop the loop
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            result = monitor_command.execute(args)
        
        # Verify result
        assert result.success
        assert "Monitoring session completed" in result.message
        
        # Verify process manager was called
        mock_process_manager.get_bot_status.assert_called()
        
        # Verify data manager was called
        mock_data_manager.get_bot_status_info.assert_called()
    
    def test_format_uptime(self, monitor_command):
        """Test uptime formatting"""
        # Test various uptime values
        assert monitor_command._format_uptime(timedelta(seconds=30)) == "30s"
        assert monitor_command._format_uptime(timedelta(minutes=5, seconds=30)) == "5m 30s"
        assert monitor_command._format_uptime(timedelta(hours=2, minutes=15)) == "2h 15m"
        assert monitor_command._format_uptime(None) == "N/A"
    
    @patch('genebot.cli.commands.monitoring.StrategyConfigManager')
    @patch('genebot.cli.commands.monitoring.ConfigurationManager')
    def test_display_strategy_info(self, mock_config_manager_class, mock_strategy_manager_class, monitor_command):
        """Test strategy information display"""
        # Setup mocks
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        
        mock_strategy_manager = Mock()
        mock_strategy_manager_class.return_value = mock_strategy_manager
        
        # Mock configuration
        bot_config = {
            'strategies': {
                'RSIStrategy': {
                    'enabled': True,
                    'parameters': {'min_confidence': 0.85}
                },
                'MovingAverageStrategy': {
                    'enabled': False,
                    'parameters': {'min_confidence': 0.75}
                }
            }
        }
        
        mock_config_manager.load_config.return_value = bot_config
        
        # Test strategy display
        active_strategies = ['RSIStrategy', 'MovingAverageStrategy']
        monitor_command._display_strategy_info(active_strategies)
        
        # Verify configuration was loaded
        mock_config_manager.load_config.assert_called()


class TestEnhancedCloseOrdersCommand:
    """Test enhanced close orders command with real exchange APIs"""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock CLI context"""
        context = Mock(spec=CLIContext)
        context.workspace_path = Path("/test/workspace")
        return context
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock CLI logger"""
        return Mock(spec=CLILogger)
    
    @pytest.fixture
    def mock_error_handler(self):
        """Create mock error handler"""
        return Mock(spec=CLIErrorHandler)
    
    @pytest.fixture
    def close_orders_command(self, mock_context, mock_logger, mock_error_handler):
        """Create close orders command instance"""
        command = CloseOrdersCommand(mock_context, mock_logger, mock_error_handler)
        command.confirm_action = Mock(return_value=True)  # Mock confirmation
        return command
    
    @patch('genebot.cli.commands.monitoring.asyncio.run')
    def test_close_orders_with_real_exchanges(self, mock_asyncio_run, close_orders_command):
        """Test close orders command with real exchange integration"""
        # Mock async result
        mock_asyncio_run.return_value = (5, 1)  # 5 closed, 1 failed
        
        # Test args
        args = Namespace(timeout=300, account=None)
        
        # Execute command
        result = close_orders_command.execute(args)
        
        # Verify result
        assert result.success is False  # Should be warning due to failed orders
        assert "Closed 5 orders, 1 failed" in result.message
        assert len(result.suggestions) > 0
        
        # Verify async function was called
        mock_asyncio_run.assert_called_once()
    
    @patch('genebot.cli.commands.monitoring.CCXTAdapter')
    async def test_close_orders_via_exchanges(self, mock_ccxt_adapter_class, close_orders_command):
        """Test the actual exchange order closing logic"""
        # Mock accounts configuration
        accounts_config = {
            'binance_demo': {
                'exchange': 'binance',
                'enabled': True,
                'api_key': 'test_key',
                'secret': 'test_secret',
                'sandbox': True
            }
        }
        
        # Mock the _load_accounts_config method
        close_orders_command._load_accounts_config = Mock(return_value=accounts_config)
        
        # Mock exchange adapter
        mock_adapter = AsyncMock()
        mock_ccxt_adapter_class.return_value = mock_adapter
        
        mock_adapter.connect.return_value = True
        mock_adapter.authenticate.return_value = True
        
        # Mock open orders
        mock_order = Mock()
        mock_order.id = "order123"
        mock_order.symbol = "BTC/USDT"
        
        mock_adapter.get_open_orders.return_value = [mock_order]
        mock_adapter.cancel_order.return_value = None
        
        # Test the method
        closed, failed = await close_orders_command._close_orders_via_exchanges(None, 300)
        
        # Verify results
        assert closed == 1
        assert failed == 0
        
        # Verify adapter calls
        mock_adapter.connect.assert_called_once()
        mock_adapter.authenticate.assert_called_once()
        mock_adapter.get_open_orders.assert_called_once()
        mock_adapter.cancel_order.assert_called_once_with("order123", "BTC/USDT")
        mock_adapter.disconnect.assert_called_once()
    
    async def test_create_exchange_adapter_success(self, close_orders_command):
        """Test successful exchange adapter creation"""
        account_config = {
            'exchange': 'binance',
            'api_key': 'test_key',
            'secret': 'test_secret',
            'sandbox': True
        }
        
        with patch('genebot.cli.commands.monitoring.CCXTAdapter') as mock_ccxt:
            mock_adapter = AsyncMock()
            mock_ccxt.return_value = mock_adapter
            
            mock_adapter.connect.return_value = True
            mock_adapter.authenticate.return_value = True
            
            result = await close_orders_command._create_exchange_adapter('test_account', account_config)
            
            assert result == mock_adapter
            mock_adapter.connect.assert_called_once()
            mock_adapter.authenticate.assert_called_once()
    
    async def test_create_exchange_adapter_connection_failure(self, close_orders_command):
        """Test exchange adapter creation with connection failure"""
        account_config = {
            'exchange': 'binance',
            'api_key': 'test_key',
            'secret': 'test_secret'
        }
        
        with patch('genebot.cli.commands.monitoring.CCXTAdapter') as mock_ccxt:
            mock_adapter = AsyncMock()
            mock_ccxt.return_value = mock_adapter
            
            mock_adapter.connect.return_value = False
            
            result = await close_orders_command._create_exchange_adapter('test_account', account_config)
            
            assert result is None
            mock_adapter.connect.assert_called_once()
            mock_adapter.authenticate.assert_not_called()


class TestComprehensiveStatusCommand:
    """Test comprehensive status command with resource usage and health metrics"""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock CLI context"""
        context = Mock(spec=CLIContext)
        context.workspace_path = Path("/test/workspace")
        return context
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock CLI logger"""
        return Mock(spec=CLILogger)
    
    @pytest.fixture
    def mock_error_handler(self):
        """Create mock error handler"""
        return Mock(spec=CLIErrorHandler)
    
    @pytest.fixture
    def comprehensive_status_command(self, mock_context, mock_logger, mock_error_handler):
        """Create comprehensive status command instance"""
        return ComprehensiveStatusCommand(mock_context, mock_logger, mock_error_handler)
    
    @patch('genebot.cli.commands.monitoring.psutil')
    @patch('genebot.cli.commands.monitoring.ProcessManager')
    @patch('genebot.cli.commands.monitoring.RealDataManager')
    def test_gather_comprehensive_status(self, mock_data_manager_class, mock_process_manager_class, mock_psutil, comprehensive_status_command):
        """Test comprehensive status gathering"""
        # Setup process manager mock
        mock_process_manager = Mock()
        mock_process_manager_class.return_value = mock_process_manager
        
        bot_status = BotStatus(
            running=True,
            pid=12345,
            uptime=timedelta(hours=2),
            memory_usage=256.0,
            cpu_usage=15.5
        )
        
        mock_process_manager.get_bot_status.return_value = bot_status
        mock_process_manager.monitor_health.return_value = {
            'healthy': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # Setup data manager mock
        mock_data_manager = Mock()
        mock_data_manager_class.return_value.__enter__.return_value = mock_data_manager
        
        trading_status = BotStatusInfo(
            active_positions=2,
            total_pnl_today=Decimal('50.25'),
            trades_today=5,
            active_strategies=['RSIStrategy'],
            last_activity=datetime.now(),
            error_count=0
        )
        
        mock_data_manager.get_bot_status_info.return_value = trading_status
        
        # Setup psutil mocks
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.cpu_count.return_value = 8
        
        mock_memory = Mock()
        mock_memory.total = 16 * 1024**3  # 16GB
        mock_memory.available = 8 * 1024**3  # 8GB
        mock_memory.used = 8 * 1024**3  # 8GB
        mock_memory.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_memory
        
        mock_disk = Mock()
        mock_disk.total = 1000 * 1024**3  # 1TB
        mock_disk.free = 500 * 1024**3  # 500GB
        mock_disk.used = 500 * 1024**3  # 500GB
        mock_psutil.disk_usage.return_value = mock_disk
        
        mock_network = Mock()
        mock_network.bytes_sent = 1024**3  # 1GB
        mock_network.bytes_recv = 2 * 1024**3  # 2GB
        mock_network.packets_sent = 1000000
        mock_network.packets_recv = 2000000
        mock_psutil.net_io_counters.return_value = mock_network
        
        # Mock async operations
        with patch('genebot.cli.commands.monitoring.asyncio.run') as mock_asyncio:
            mock_asyncio.return_value = {
                'total_accounts': 2,
                'connected': 1,
                'failed': 1,
                'accounts': []
            }
            
            # Test status gathering
            status_data = comprehensive_status_command._gather_comprehensive_status()
        
        # Verify status data structure
        assert 'process' in status_data
        assert 'trading' in status_data
        assert 'system' in status_data
        assert 'accounts' in status_data
        assert 'configuration' in status_data
        
        # Verify process data
        process_data = status_data['process']
        assert process_data['running'] is True
        assert process_data['pid'] == 12345
        assert process_data['memory_usage_mb'] == 256.0
        assert process_data['cpu_usage_percent'] == 15.5
        
        # Verify trading data
        trading_data = status_data['trading']
        assert trading_data['active_positions'] == 2
        assert trading_data['total_pnl_today'] == 50.25
        assert trading_data['trades_today'] == 5
        
        # Verify system data
        system_data = status_data['system']
        assert system_data['cpu']['usage_percent'] == 25.5
        assert system_data['cpu']['count'] == 8
        assert system_data['memory']['total_gb'] == 16.0
        assert system_data['disk']['total_gb'] == 1000.0
    
    def test_get_system_resources(self, comprehensive_status_command):
        """Test system resource gathering"""
        with patch('genebot.cli.commands.monitoring.psutil') as mock_psutil:
            # Setup psutil mocks
            mock_psutil.cpu_percent.return_value = 30.0
            mock_psutil.cpu_count.return_value = 4
            
            mock_memory = Mock()
            mock_memory.total = 8 * 1024**3  # 8GB
            mock_memory.available = 4 * 1024**3  # 4GB
            mock_memory.used = 4 * 1024**3  # 4GB
            mock_memory.percent = 50.0
            mock_psutil.virtual_memory.return_value = mock_memory
            
            mock_disk = Mock()
            mock_disk.total = 500 * 1024**3  # 500GB
            mock_disk.free = 250 * 1024**3  # 250GB
            mock_disk.used = 250 * 1024**3  # 250GB
            mock_psutil.disk_usage.return_value = mock_disk
            
            mock_network = Mock()
            mock_network.bytes_sent = 1024**2  # 1MB
            mock_network.bytes_recv = 2 * 1024**2  # 2MB
            mock_network.packets_sent = 1000
            mock_network.packets_recv = 2000
            mock_psutil.net_io_counters.return_value = mock_network
            
            # Test resource gathering
            resources = comprehensive_status_command._get_system_resources()
            
            # Verify results
            assert resources['cpu']['usage_percent'] == 30.0
            assert resources['cpu']['count'] == 4
            assert resources['memory']['total_gb'] == 8.0
            assert resources['memory']['usage_percent'] == 50.0
            assert resources['disk']['total_gb'] == 500.0
            assert resources['network']['bytes_sent'] == 1024**2
    
    @patch('genebot.cli.commands.monitoring.RealAccountValidator')
    async def test_check_account_connectivity(self, mock_validator_class, comprehensive_status_command):
        """Test account connectivity checking"""
        accounts_config = {
            'binance_demo': {
                'exchange': 'binance',
                'enabled': True
            },
            'oanda_demo': {
                'exchange': 'oanda',
                'enabled': True
            }
        }
        
        # Mock the _load_accounts_config method
        comprehensive_status_command._load_accounts_config = Mock(return_value=accounts_config)
        
        mock_validator = AsyncMock()
        mock_validator_class.return_value = mock_validator
        
        # Mock validation results
        mock_validator.validate_account_connectivity.side_effect = [True, False]
        
        # Test connectivity check
        result = await comprehensive_status_command._check_account_connectivity()
        
        # Verify results
        assert result['total_accounts'] == 2
        assert result['connected'] == 1
        assert result['failed'] == 1
        assert len(result['accounts']) == 2
        
        # Verify account details
        accounts = result['accounts']
        assert accounts[0]['name'] == 'binance_demo'
        assert accounts[0]['status'] == 'connected'
        assert accounts[1]['name'] == 'oanda_demo'
        assert accounts[1]['status'] == 'failed'
    
    def test_format_uptime_seconds(self, comprehensive_status_command):
        """Test uptime seconds formatting"""
        # Test various durations
        assert comprehensive_status_command._format_uptime_seconds(30) == "30s"
        assert comprehensive_status_command._format_uptime_seconds(90) == "1m 30s"
        assert comprehensive_status_command._format_uptime_seconds(3661) == "1h 1m"
        assert comprehensive_status_command._format_uptime_seconds(7200) == "2h 0m"
    
    def test_execute_json_output(self, comprehensive_status_command):
        """Test comprehensive status command with JSON output"""
        args = Namespace(detailed=False, json=True)
        
        # Mock the status gathering
        mock_status_data = {
            'process': {'running': True, 'pid': 12345},
            'trading': {'active_positions': 1},
            'system': {'cpu': {'usage_percent': 25.0}},
            'accounts': {'total_accounts': 1},
            'configuration': {'main_config': {'exists': True}}
        }
        
        with patch.object(comprehensive_status_command, '_gather_comprehensive_status', return_value=mock_status_data):
            with patch('builtins.print') as mock_print:
                result = comprehensive_status_command.execute(args)
        
        # Verify result
        assert result.success
        assert "JSON format" in result.message
        
        # Verify JSON was printed
        mock_print.assert_called_once()
        printed_data = json.loads(mock_print.call_args[0][0])
        assert printed_data['process']['running'] is True
        assert printed_data['process']['pid'] == 12345


class TestMonitoringIntegration:
    """Integration tests for monitoring commands"""
    
    def test_monitor_command_error_handling(self):
        """Test monitor command error handling"""
        context = Mock(spec=CLIContext)
        logger = Mock(spec=CLILogger)
        error_handler = Mock(spec=CLIErrorHandler)
        
        command = MonitorCommand(context, logger, error_handler)
        
        # Mock data manager to raise exception
        with patch('genebot.cli.commands.monitoring.RealDataManager') as mock_dm:
            mock_dm.return_value.__enter__.side_effect = Exception("Database connection failed")
            
            args = Namespace(refresh=5, account=None)
            result = command.execute(args)
            
            assert not result.success
            assert "Monitoring failed" in result.message
            assert len(result.suggestions) > 0
    
    def test_comprehensive_status_error_recovery(self):
        """Test comprehensive status command error recovery"""
        context = Mock(spec=CLIContext)
        logger = Mock(spec=CLILogger)
        error_handler = Mock(spec=CLIErrorHandler)
        
        command = ComprehensiveStatusCommand(context, logger, error_handler)
        
        # Mock partial failures in status gathering
        with patch.object(command, '_gather_comprehensive_status') as mock_gather:
            mock_gather.return_value = {
                'process': {'error': 'Process check failed'},
                'trading': {'active_positions': 0},
                'system': {'error': 'System check failed'},
                'accounts': {'total_accounts': 0},
                'configuration': {'main_config': {'exists': True}}
            }
            
            args = Namespace(detailed=False, json=False)
            result = command.execute(args)
            
            # Should still succeed with partial data
            assert result.success
            assert "Comprehensive status information displayed" in result.message


if __name__ == '__main__':
    pytest.main([__file__])