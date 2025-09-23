"""
Tests for CLI Real Data Manager
==============================

Integration tests for the RealDataManager that connects to actual database
and replaces mock data in CLI commands.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch, MagicMock

from genebot.cli.utils.data_manager import RealDataManager, TradeInfo, PositionInfo, BotStatusInfo, TradingSummary
from src.database.connection import DatabaseManager
from src.models.database_models import (
    TradeModel, OrderModel, PositionModel, StrategyPerformanceModel,
    TradingSignalModel, RiskEventModel
)


class TestRealDataManager:
    """Test suite for RealDataManager"""
    
    @pytest.fixture
    def temp_db_url(self):
        """Create temporary SQLite database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_url = f"sqlite:///{f.name}"
        yield db_url
        # Cleanup
        try:
            os.unlink(f.name)
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def temp_logs_path(self):
        """Create temporary logs directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def data_manager(self, temp_db_url, temp_logs_path):
        """Create RealDataManager instance for testing"""
        return RealDataManager(database_url=temp_db_url, logs_path=temp_logs_path)
    
    @pytest.fixture
    def sample_trade_data(self, data_manager):
        """Create sample trade data in database"""
        with data_manager.db_manager.get_session() as session:
            # Create sample order
            order = OrderModel(
                id="order_123",
                symbol="BTC/USDT",
                side="BUY",
                amount=Decimal('0.1'),
                price=Decimal('45000.00'),
                order_type="MARKET",
                status="filled",
                timestamp=datetime.utcnow() - timedelta(hours=1),
                exchange="binance",
                filled_amount=Decimal('0.1'),
                average_fill_price=Decimal('45000.00'),
                fees=Decimal('4.50')
            )
            session.add(order)
            
            # Create sample trade
            trade = TradeModel(
                order_id="order_123",
                symbol="BTC/USDT",
                side="BUY",
                amount=Decimal('0.1'),
                price=Decimal('45000.00'),
                fees=Decimal('4.50'),
                timestamp=datetime.utcnow() - timedelta(hours=1),
                exchange="binance",
                trade_id="trade_456"
            )
            session.add(trade)
            
            # Create sample position
            position = PositionModel(
                symbol="BTC/USDT",
                size=Decimal('0.1'),
                entry_price=Decimal('45000.00'),
                current_price=Decimal('46000.00'),
                side="BUY",
                exchange="binance",
                opened_at=datetime.utcnow() - timedelta(hours=2),
                is_active="true"
            )
            session.add(position)
            
            # Create sample trading signal
            signal = TradingSignalModel(
                symbol="BTC/USDT",
                action="BUY",
                confidence=Decimal('0.85'),
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                strategy_name="RSI_Strategy",
                price=Decimal('45500.00')
            )
            session.add(signal)
            
            session.commit()
    
    def test_get_recent_trades_success(self, data_manager, sample_trade_data):
        """Test successful retrieval of recent trades"""
        trades = data_manager.get_recent_trades(limit=10)
        
        assert len(trades) == 1
        assert isinstance(trades[0], TradeInfo)
        assert trades[0].symbol == "BTC/USDT"
        assert trades[0].side == "BUY"
        assert trades[0].quantity == Decimal('0.1')
        assert trades[0].price == Decimal('45000.00')
        assert trades[0].exchange == "binance"
        assert trades[0].fees == Decimal('4.50')
    
    def test_get_recent_trades_with_filters(self, data_manager, sample_trade_data):
        """Test trade retrieval with account and time filters"""
        # Test account filter
        trades = data_manager.get_recent_trades(account_filter="binance")
        assert len(trades) == 1
        
        trades = data_manager.get_recent_trades(account_filter="nonexistent")
        assert len(trades) == 0
        
        # Test days filter
        trades = data_manager.get_recent_trades(days=1)
        assert len(trades) == 1
        
        # Note: The days filter uses >= comparison, so trades from 1 hour ago 
        # are still within the last day. This is correct behavior.
    
    def test_get_recent_trades_database_error(self, temp_logs_path):
        """Test trade retrieval fallback when database fails"""
        # Create data manager with invalid database URL
        data_manager = RealDataManager(database_url="sqlite:///nonexistent/path.db", logs_path=temp_logs_path)
        
        # Mock trade logger to return sample data
        with patch.object(data_manager.trade_logger, 'get_trade_history') as mock_history:
            mock_event = MagicMock()
            mock_event.event_type = 'order_filled'
            mock_event.timestamp = datetime.utcnow()
            mock_event.symbol = "ETH/USDT"
            mock_event.side = "sell"
            mock_event.quantity = Decimal('2.0')
            mock_event.price = Decimal('3000.00')
            mock_event.pnl = Decimal('50.00')
            mock_event.exchange = "binance"
            mock_event.strategy = "test_strategy"
            mock_event.fee = Decimal('3.00')
            
            mock_history.return_value = [mock_event]
            
            trades = data_manager.get_recent_trades(limit=10)
            
            assert len(trades) == 1
            assert trades[0].symbol == "ETH/USDT"
            assert trades[0].side == "SELL"
    
    def test_get_active_positions_success(self, data_manager, sample_trade_data):
        """Test successful retrieval of active positions"""
        positions = data_manager.get_active_positions()
        
        assert len(positions) == 1
        assert isinstance(positions[0], PositionInfo)
        assert positions[0].symbol == "BTC/USDT"
        assert positions[0].side == "BUY"
        assert positions[0].size == Decimal('0.1')
        assert positions[0].entry_price == Decimal('45000.00')
        assert positions[0].current_price == Decimal('46000.00')
        assert positions[0].exchange == "binance"
        # PnL should be positive (current > entry for BUY)
        assert positions[0].pnl > 0
    
    def test_get_active_positions_with_filter(self, data_manager, sample_trade_data):
        """Test position retrieval with account filter"""
        positions = data_manager.get_active_positions(account_filter="binance")
        assert len(positions) == 1
        
        positions = data_manager.get_active_positions(account_filter="nonexistent")
        assert len(positions) == 0
    
    def test_get_bot_status_info(self, data_manager, sample_trade_data):
        """Test bot status information retrieval"""
        status = data_manager.get_bot_status_info()
        
        assert isinstance(status, BotStatusInfo)
        assert status.active_positions == 1
        assert status.trades_today >= 0  # Depends on when trade was created
        assert isinstance(status.total_pnl_today, Decimal)
        assert isinstance(status.active_strategies, list)
        assert status.error_count >= 0
    
    def test_get_trading_summary(self, data_manager, sample_trade_data):
        """Test trading summary calculation"""
        summary = data_manager.get_trading_summary(days=30)
        
        assert isinstance(summary, TradingSummary)
        assert summary.total_trades == 1
        assert isinstance(summary.total_pnl, Decimal)
        assert 0 <= summary.win_rate <= 100
        assert isinstance(summary.avg_win, Decimal)
        assert isinstance(summary.avg_loss, Decimal)
    
    def test_get_trading_summary_no_data(self, data_manager):
        """Test trading summary with no data"""
        summary = data_manager.get_trading_summary(days=30)
        
        assert summary.total_trades == 0
        assert summary.winning_trades == 0
        assert summary.losing_trades == 0
        assert summary.win_rate == 0.0
        assert summary.total_pnl == Decimal('0')
    
    def test_get_recent_activity(self, data_manager, sample_trade_data):
        """Test recent activity retrieval"""
        activities = data_manager.get_recent_activity(limit=5)
        
        assert isinstance(activities, list)
        assert len(activities) > 0
        # Should contain trade and signal activities
        activity_text = ' '.join(activities)
        assert "BTC/USDT" in activity_text
    
    def test_generate_report_data_summary(self, data_manager, sample_trade_data):
        """Test summary report generation"""
        report = data_manager.generate_report_data("summary", days=30)
        
        assert "generated_at" in report
        assert "period" in report
        assert "total_trades" in report
        assert "win_rate" in report
        assert "total_pnl" in report
        assert report["total_trades"] == 1
    
    def test_generate_report_data_detailed(self, data_manager, sample_trade_data):
        """Test detailed report generation"""
        report = data_manager.generate_report_data("detailed", days=30)
        
        assert "recent_trades" in report
        assert "active_positions" in report
        assert "daily_pnl" in report
        assert "strategy_performance" in report
        
        assert len(report["recent_trades"]) == 1
        assert len(report["active_positions"]) == 1
        assert isinstance(report["daily_pnl"], list)
    
    def test_close_all_orders(self, data_manager, sample_trade_data):
        """Test order closure functionality"""
        # Add an open order to the database
        with data_manager.db_manager.get_session() as session:
            open_order = OrderModel(
                id="open_order_123",
                symbol="ETH/USDT",
                side="BUY",
                amount=Decimal('1.0'),
                price=Decimal('3000.00'),
                order_type="LIMIT",
                status="open",
                timestamp=datetime.utcnow(),
                exchange="binance"
            )
            session.add(open_order)
            session.commit()
        
        closed, failed = data_manager.close_all_orders()
        
        # Should close the open order (mock implementation)
        assert closed >= 1
        assert failed == 0
        
        # Verify order status was updated
        with data_manager.db_manager.get_session() as session:
            updated_order = session.query(OrderModel).filter_by(id="open_order_123").first()
            assert updated_order.status == "cancelled"
    
    def test_close_all_orders_with_filter(self, data_manager):
        """Test order closure with account filter"""
        # Add orders for different exchanges
        with data_manager.db_manager.get_session() as session:
            binance_order = OrderModel(
                id="binance_order",
                symbol="BTC/USDT",
                side="BUY",
                amount=Decimal('0.1'),
                price=Decimal('45000.00'),
                order_type="LIMIT",
                status="open",
                timestamp=datetime.utcnow(),
                exchange="binance"
            )
            
            coinbase_order = OrderModel(
                id="coinbase_order",
                symbol="BTC/USD",
                side="BUY",
                amount=Decimal('0.1'),
                price=Decimal('45000.00'),
                order_type="LIMIT",
                status="open",
                timestamp=datetime.utcnow(),
                exchange="coinbase"
            )
            
            session.add_all([binance_order, coinbase_order])
            session.commit()
        
        # Close only binance orders
        closed, failed = data_manager.close_all_orders(account_filter="binance")
        
        assert closed == 1  # Only binance order should be closed
        assert failed == 0
    
    def test_context_manager(self, temp_db_url, temp_logs_path):
        """Test RealDataManager as context manager"""
        with RealDataManager(database_url=temp_db_url, logs_path=temp_logs_path) as dm:
            assert isinstance(dm, RealDataManager)
            assert dm.db_manager is not None
        
        # Should clean up properly after context exit
    
    def test_database_connection_error_handling(self, temp_logs_path):
        """Test handling of database connection errors"""
        # Mock the DatabaseManager to raise an exception during initialization
        with patch('genebot.cli.utils.data_manager.DatabaseManager') as mock_db_manager:
            mock_db_manager.side_effect = Exception("Database connection failed")
            
            # This should handle the error gracefully
            with patch('genebot.cli.utils.data_manager.TradeLogger'):
                data_manager = RealDataManager(database_url="sqlite:///test.db", logs_path=temp_logs_path)
                
                # Should handle errors gracefully
                trades = data_manager.get_recent_trades()
                assert isinstance(trades, list)  # Should return empty list or fallback data
                
                positions = data_manager.get_active_positions()
                assert isinstance(positions, list)
                
                status = data_manager.get_bot_status_info()
                assert isinstance(status, BotStatusInfo)
                assert status.active_positions == 0  # Default values when DB fails


    def test_real_pnl_calculation(self, data_manager, sample_trade_data):
        """Test that PnL calculation uses real position tracking"""
        with data_manager.db_manager.get_session() as session:
            # Add a position that corresponds to our sample trade
            position = PositionModel(
                symbol="BTC/USDT",
                size=Decimal('0.1'),
                entry_price=Decimal('44000.00'),  # Lower entry price
                current_price=Decimal('45000.00'),  # Trade price
                side="BUY",
                exchange="binance",
                opened_at=datetime.utcnow() - timedelta(hours=3),
                closed_at=datetime.utcnow() - timedelta(hours=1),  # Closed by our trade
                is_active="false"
            )
            session.add(position)
            session.commit()
        
        # Get trades and verify PnL calculation
        trades = data_manager.get_recent_trades(limit=10)
        
        # Should have calculated real PnL based on position
        trade_with_pnl = next((t for t in trades if t.pnl is not None), None)
        assert trade_with_pnl is not None
        # PnL should be (45000 - 44000) * 0.1 - fees = 100 - 4.5 = 95.5
        expected_pnl = (Decimal('45000.00') - Decimal('44000.00')) * Decimal('0.1') - Decimal('4.50')
        assert abs(trade_with_pnl.pnl - expected_pnl) < Decimal('0.01')
    
    def test_real_performance_stats(self, data_manager, sample_trade_data):
        """Test that performance statistics use real calculations"""
        # Add more realistic trade data
        with data_manager.db_manager.get_session() as session:
            # Add a winning position
            winning_position = PositionModel(
                symbol="ETH/USDT",
                size=Decimal('1.0'),
                entry_price=Decimal('3000.00'),
                current_price=Decimal('3100.00'),
                side="BUY",
                exchange="binance",
                opened_at=datetime.utcnow() - timedelta(hours=2),
                closed_at=datetime.utcnow() - timedelta(hours=1),
                is_active="false"
            )
            
            # Add corresponding trade
            winning_trade = TradeModel(
                order_id="order_winning",
                symbol="ETH/USDT",
                side="SELL",  # Closing long position
                amount=Decimal('1.0'),
                price=Decimal('3100.00'),
                fees=Decimal('3.10'),
                timestamp=datetime.utcnow() - timedelta(hours=1),
                exchange="binance",
                trade_id="trade_winning"
            )
            
            session.add_all([winning_position, winning_trade])
            session.commit()
        
        # Get trading summary
        summary = data_manager.get_trading_summary(days=1)
        
        # Should have real performance calculations
        assert summary.total_trades >= 1
        assert summary.total_pnl != Decimal('0')  # Should have real PnL
    
    def test_live_log_data_reading(self, data_manager, temp_logs_path):
        """Test reading live log data from files"""
        # Create sample log files
        main_log = temp_logs_path / "trading_bot.log"
        main_log.write_text("""
2024-01-01 10:00:01 - INFO - Bot started successfully
2024-01-01 10:00:05 - INFO - Connected to Binance exchange
2024-01-01 10:00:10 - INFO - Strategy RSI_Strategy initialized
2024-01-01 10:01:00 - INFO - BUY signal generated for BTC/USDT
2024-01-01 10:01:05 - INFO - Order placed: BUY 0.1 BTC/USDT at 45000.00
        """.strip())
        
        error_log_dir = temp_logs_path / "errors"
        error_log_dir.mkdir(exist_ok=True)
        error_log = error_log_dir / "error.log"
        error_log.write_text("""
2024-01-01 10:02:00 - ERROR - Connection timeout to exchange
2024-01-01 10:02:30 - WARNING - Retrying connection
        """.strip())
        
        # Test log reading
        log_entries = data_manager.get_live_log_data(lines=10)
        
        assert isinstance(log_entries, list)
        assert len(log_entries) > 0
        
        # Should include both regular and error logs
        log_text = ' '.join(log_entries)
        assert "Bot started" in log_text or "Order placed" in log_text
    
    def test_system_health_metrics(self, data_manager):
        """Test system health metrics collection"""
        metrics = data_manager.get_system_health_metrics()
        
        assert isinstance(metrics, dict)
        assert 'database_available' in metrics
        assert 'bot_running' in metrics
        
        # Should have system metrics if psutil is available
        if 'error' not in metrics:
            assert 'system_cpu_percent' in metrics
            assert 'system_memory_percent' in metrics


class TestDataManagerIntegration:
    """Integration tests with actual CLI commands"""
    
    def test_data_manager_with_monitoring_functions(self):
        """Test data manager integration with monitoring functions"""
        # Test that the data manager can be imported and used by monitoring commands
        from genebot.cli.utils.data_manager import RealDataManager
        
        # Test basic instantiation
        with patch('genebot.cli.utils.data_manager.DatabaseManager'):
            with patch('genebot.cli.utils.data_manager.TradeLogger'):
                data_manager = RealDataManager()
                
                # Test that all required methods exist
                assert hasattr(data_manager, 'get_recent_trades')
                assert hasattr(data_manager, 'get_active_positions')
                assert hasattr(data_manager, 'get_bot_status_info')
                assert hasattr(data_manager, 'get_trading_summary')
                assert hasattr(data_manager, 'get_recent_activity')
                assert hasattr(data_manager, 'generate_report_data')
                assert hasattr(data_manager, 'close_all_orders')
    
    def test_monitoring_command_imports(self):
        """Test that monitoring commands can import and use RealDataManager"""
        # Test imports work correctly
        from genebot.cli.commands.monitoring import TradesCommand, MonitorCommand, ReportCommand, CloseOrdersCommand
        from genebot.cli.utils.data_manager import RealDataManager
        
        # Verify the classes exist and can be imported
        assert TradesCommand is not None
        assert MonitorCommand is not None
        assert ReportCommand is not None
        assert CloseOrdersCommand is not None
        assert RealDataManager is not None
    
    def test_data_serialization_for_json_output(self):
        """Test that monitoring commands can handle Decimal serialization"""
        from genebot.cli.commands.monitoring import ReportCommand
        
        # Test that the ReportCommand has the serialization method
        # This is where the serialization actually happens
        with patch('genebot.cli.commands.monitoring.RealDataManager'):
            # Create a mock command to test serialization
            sample_data = {
                'total_pnl': Decimal('100.50'),
                'nested': {
                    'avg_win': Decimal('25.25')
                },
                'list_data': [Decimal('10.10'), 'string', 42]
            }
            
            # Test that we can import the command and it has the serialization method
            assert hasattr(ReportCommand, '_serialize_report_data')
            
            # Test serialization works (create a mock instance)
            mock_command = MagicMock()
            mock_command._serialize_report_data = ReportCommand._serialize_report_data.__get__(mock_command)
            
            serialized = mock_command._serialize_report_data(sample_data)
            assert isinstance(serialized['total_pnl'], float)
            assert isinstance(serialized['nested']['avg_win'], float)
            assert isinstance(serialized['list_data'][0], float)


if __name__ == "__main__":
    pytest.main([__file__])