"""
Test CLI Reporting and Analytics Commands
========================================

Tests for the enhanced reporting and analytics functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from genebot.cli.commands.monitoring import ReportCommand
from genebot.cli.commands.analytics import AnalyticsCommand, BacktestAnalyticsCommand
from genebot.cli.utils.data_manager import TradeInfo, TradingSummary, BotStatusInfo
from genebot.cli.context import CLIContext
from genebot.cli.utils.logger import CLILogger
from genebot.cli.utils.error_handler import CLIErrorHandler
from genebot.cli.result import CommandResult


class TestReportCommand:
    """Test enhanced report generation functionality"""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock CLI context"""
        context = Mock(spec=CLIContext)
        context.workspace_path = Path("/test/workspace")
        context.config_path = Path("/test/config")
        context.log_level = "INFO"
        context.verbose = False
        context.dry_run = False
        return context
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger"""
        return Mock(spec=CLILogger)
    
    @pytest.fixture
    def mock_error_handler(self):
        """Create mock error handler"""
        return Mock(spec=CLIErrorHandler)
    
    @pytest.fixture
    def report_command(self, mock_context, mock_logger, mock_error_handler):
        """Create report command instance"""
        return ReportCommand(mock_context, mock_logger, mock_error_handler)
    
    @pytest.fixture
    def sample_trades(self):
        """Create sample trade data"""
        trades = []
        base_time = datetime.utcnow() - timedelta(days=5)
        
        for i in range(10):
            trade = TradeInfo(
                timestamp=base_time + timedelta(hours=i),
                symbol=f"BTC/USD" if i % 2 == 0 else "ETH/USD",
                side="BUY" if i % 2 == 0 else "SELL",
                quantity=Decimal(str(0.1 + i * 0.01)),
                price=Decimal(str(50000 + i * 100)),
                pnl=Decimal(str(10.5 if i % 3 == 0 else -5.2)),
                account="binance-demo",
                exchange="binance",
                strategy=f"strategy_{i % 3}",
                fees=Decimal("2.5")
            )
            trades.append(trade)
        
        return trades
    
    @pytest.fixture
    def sample_summary(self):
        """Create sample trading summary"""
        return TradingSummary(
            total_trades=10,
            winning_trades=6,
            losing_trades=4,
            win_rate=60.0,
            total_pnl=Decimal("125.50"),
            max_drawdown=Decimal("15.2"),
            sharpe_ratio=1.25,
            avg_win=Decimal("25.5"),
            avg_loss=Decimal("-12.3")
        )
    
    def test_performance_report_generation(self, report_command, sample_trades, sample_summary):
        """Test performance report generation"""
        args = Mock()
        args.type = 'performance'
        args.days = 30
        args.output = None
        args.format = 'json'
        args.charts = False
        
        with patch('genebot.cli.commands.monitoring.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_trading_summary.return_value = sample_summary
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm_instance._get_strategy_performance.return_value = {
                'strategy_0': {'total_trades': 4, 'win_rate': 75.0, 'total_pnl': 50.0},
                'strategy_1': {'total_trades': 3, 'win_rate': 66.7, 'total_pnl': 35.5},
                'strategy_2': {'total_trades': 3, 'win_rate': 33.3, 'total_pnl': 40.0}
            }
            mock_dm_instance._calculate_daily_pnl.return_value = [10.5, -5.2, 15.3, -8.1, 12.7]
            mock_dm.return_value = mock_dm_instance
            
            result = report_command.execute(args)
            
            assert result.success
            assert "performance report generated successfully" in result.message.lower()
            assert result.data['report_type'] == 'performance'
    
    def test_compliance_report_generation(self, report_command, sample_trades):
        """Test compliance report generation"""
        args = Mock()
        args.type = 'compliance'
        args.days = 30
        args.output = None
        args.format = 'json'
        args.charts = False
        
        with patch('genebot.cli.commands.monitoring.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm.return_value = mock_dm_instance
            
            # Mock compliance components
            with patch('src.compliance.reporting_engine.ReportingEngine') as mock_re, \
                 patch('src.compliance.audit_trail.AuditTrail') as mock_at:
                
                mock_re_instance = Mock()
                mock_re_instance.generate_compliance_report.return_value = {
                    'data': {'summary': {'total_events': 5, 'violations': 0, 'compliant': 5}},
                    'file_path': '/test/compliance_report.json'
                }
                mock_re_instance.generate_trade_report.return_value = {
                    'data': {'trades': []},
                    'file_path': '/test/trade_report.json'
                }
                mock_re.return_value = mock_re_instance
                
                mock_at_instance = Mock()
                mock_at_instance.get_compliance_events.return_value = []
                mock_at.return_value = mock_at_instance
                
                result = report_command.execute(args)
                
                assert result.success
                assert "compliance report generated successfully" in result.message.lower()
    
    def test_strategy_report_generation(self, report_command, sample_trades):
        """Test strategy-specific report generation"""
        args = Mock()
        args.type = 'strategy'
        args.days = 30
        args.output = None
        args.format = 'html'
        args.charts = False
        
        with patch('genebot.cli.commands.monitoring.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm_instance._get_strategy_performance.return_value = {
                'strategy_0': {'total_trades': 4, 'win_rate': 75.0, 'total_pnl': 50.0},
                'strategy_1': {'total_trades': 3, 'win_rate': 66.7, 'total_pnl': 35.5}
            }
            mock_dm.return_value = mock_dm_instance
            
            result = report_command.execute(args)
            
            assert result.success
            assert "strategy report generated successfully" in result.message.lower()
    
    def test_pnl_analysis_report(self, report_command, sample_trades, sample_summary):
        """Test P&L analysis report generation"""
        args = Mock()
        args.type = 'pnl'
        args.days = 30
        args.output = None
        args.format = 'text'
        args.charts = False
        
        with patch('genebot.cli.commands.monitoring.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm_instance.get_trading_summary.return_value = sample_summary
            mock_dm_instance._calculate_daily_pnl.return_value = [10.5, -5.2, 15.3]
            mock_dm.return_value = mock_dm_instance
            
            result = report_command.execute(args)
            
            assert result.success
            assert "pnl_analysis report generated successfully" in result.message.lower()
    
    def test_report_with_charts(self, report_command, sample_trades, sample_summary):
        """Test report generation with charts"""
        args = Mock()
        args.type = 'performance'
        args.days = 30
        args.output = None
        args.format = 'html'
        args.charts = True
        
        with patch('genebot.cli.commands.monitoring.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_trading_summary.return_value = sample_summary
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm_instance._get_strategy_performance.return_value = {}
            mock_dm_instance._calculate_daily_pnl.return_value = [10.5, -5.2, 15.3]
            mock_dm.return_value = mock_dm_instance
            
            with patch('matplotlib.pyplot') as mock_plt:
                mock_plt.figure.return_value = Mock()
                mock_plt.plot.return_value = Mock()
                mock_plt.savefig.return_value = Mock()
                mock_plt.close.return_value = Mock()
                
                result = report_command.execute(args)
                
                assert result.success
    
    def test_report_output_formats(self, report_command, sample_trades, sample_summary):
        """Test different report output formats"""
        formats = ['text', 'json', 'csv', 'html']
        
        for fmt in formats:
            args = Mock()
            args.type = 'performance'
            args.days = 30
            args.output = None
            args.format = fmt
            args.charts = False
            
            with patch('genebot.cli.commands.monitoring.RealDataManager') as mock_dm:
                mock_dm_instance = Mock()
                mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
                mock_dm_instance.__exit__ = Mock(return_value=None)
                mock_dm_instance.get_trading_summary.return_value = sample_summary
                mock_dm_instance.get_recent_trades.return_value = sample_trades
                mock_dm_instance._get_strategy_performance.return_value = {
                    'strategy_0': {'total_trades': 4, 'win_rate': 75.0, 'total_pnl': 50.0}
                }
                mock_dm_instance._calculate_daily_pnl.return_value = [10.5, -5.2]
                mock_dm.return_value = mock_dm_instance
                
                result = report_command.execute(args)
                
                assert result.success, f"Format {fmt} failed: {result.message}"
                assert result.data['format'] == fmt
    
    def test_report_file_output(self, report_command, sample_trades, sample_summary):
        """Test report output to file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            args = Mock()
            args.type = 'performance'
            args.days = 30
            args.output = tmp_file.name
            args.format = 'json'
            args.charts = False
            
            with patch('genebot.cli.commands.monitoring.RealDataManager') as mock_dm:
                mock_dm_instance = Mock()
                mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
                mock_dm_instance.__exit__ = Mock(return_value=None)
                mock_dm_instance.get_trading_summary.return_value = sample_summary
                mock_dm_instance.get_recent_trades.return_value = sample_trades
                mock_dm_instance._get_strategy_performance.return_value = {}
                mock_dm_instance._calculate_daily_pnl.return_value = [10.5]
                mock_dm.return_value = mock_dm_instance
                
                result = report_command.execute(args)
                
                assert result.success
                
                # Verify file was created
                output_path = Path(tmp_file.name)
                assert output_path.exists()
                
                # Clean up
                output_path.unlink()


class TestAnalyticsCommand:
    """Test advanced analytics functionality"""
    
    @pytest.fixture
    def analytics_command(self, mock_context, mock_logger, mock_error_handler):
        """Create analytics command instance"""
        return AnalyticsCommand(mock_context, mock_logger, mock_error_handler)
    
    @pytest.fixture
    def mock_context(self):
        """Create mock CLI context"""
        context = Mock(spec=CLIContext)
        context.workspace_path = Path("/test/workspace")
        return context
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger"""
        return Mock(spec=CLILogger)
    
    @pytest.fixture
    def mock_error_handler(self):
        """Create mock error handler"""
        return Mock(spec=CLIErrorHandler)
    
    def test_performance_analytics(self, analytics_command):
        """Test performance analytics execution"""
        args = Mock()
        args.type = 'performance'
        args.days = 30
        args.output = None
        args.format = 'json'
        
        sample_trades = [
            TradeInfo(
                timestamp=datetime.now(),
                symbol="BTC/USD",
                side="BUY",
                quantity=Decimal("0.1"),
                price=Decimal("50000"),
                pnl=Decimal("10.5"),
                account="test",
                exchange="test"
            )
        ]
        
        sample_summary = TradingSummary(
            total_trades=1,
            winning_trades=1,
            losing_trades=0,
            win_rate=100.0,
            total_pnl=Decimal("10.5"),
            max_drawdown=Decimal("0"),
            sharpe_ratio=2.5,
            avg_win=Decimal("10.5"),
            avg_loss=Decimal("0")
        )
        
        with patch('genebot.cli.commands.analytics.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm_instance.get_trading_summary.return_value = sample_summary
            mock_dm.return_value = mock_dm_instance
            
            with patch('genebot.cli.commands.analytics.PerformanceAnalyzer') as mock_analyzer:
                mock_analyzer_instance = Mock()
                mock_analyzer_instance.calculate_performance_metrics.return_value = {}
                mock_analyzer_instance.calculate_rolling_metrics.return_value = Mock()
                mock_analyzer_instance.calculate_rolling_metrics.return_value.empty = True
                mock_analyzer_instance.calculate_rolling_metrics.return_value.to_dict.return_value = {}
                mock_analyzer.return_value = mock_analyzer_instance
                
                result = analytics_command.execute(args)
                
                assert result.success
                assert "Performance analysis completed" in result.message
    
    def test_risk_analytics(self, analytics_command):
        """Test risk analytics execution"""
        args = Mock()
        args.type = 'risk'
        args.days = 30
        args.output = None
        args.format = 'json'
        
        with patch('genebot.cli.commands.analytics.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_recent_trades.return_value = []
            mock_dm_instance.get_active_positions.return_value = []
            mock_dm.return_value = mock_dm_instance
            
            result = analytics_command.execute(args)
            
            # Should return warning for no data
            assert not result.success or "No trading data available" in result.message
    
    def test_correlation_analytics(self, analytics_command):
        """Test correlation analytics execution"""
        args = Mock()
        args.type = 'correlation'
        args.days = 30
        args.output = None
        args.format = 'json'
        
        sample_trades = [
            TradeInfo(
                timestamp=datetime.utcnow(),
                symbol="BTC/USD",
                side="BUY",
                quantity=Decimal("0.1"),
                price=Decimal("50000"),
                pnl=Decimal("10.5"),
                account="test",
                exchange="test"
            )
        ]
        
        with patch('genebot.cli.commands.analytics.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm.return_value = mock_dm_instance
            
            result = analytics_command.execute(args)
            
            assert result.success
            assert "Correlation analysis completed" in result.message
    
    def test_attribution_analytics(self, analytics_command):
        """Test attribution analytics execution"""
        args = Mock()
        args.type = 'attribution'
        args.days = 30
        args.output = None
        args.format = 'json'
        
        sample_trades = [
            TradeInfo(
                timestamp=datetime.utcnow(),
                symbol="BTC/USD",
                side="BUY",
                quantity=Decimal("0.1"),
                price=Decimal("50000"),
                pnl=Decimal("10.5"),
                account="test",
                exchange="test",
                strategy="test_strategy"
            )
        ]
        
        with patch('genebot.cli.commands.analytics.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm.return_value = mock_dm_instance
            
            result = analytics_command.execute(args)
            
            assert result.success
            assert "Attribution analysis completed" in result.message
    
    def test_optimization_analytics(self, analytics_command):
        """Test optimization analytics execution"""
        args = Mock()
        args.type = 'optimization'
        args.days = 30
        args.output = None
        args.format = 'json'
        
        sample_trades = [
            TradeInfo(
                timestamp=datetime.utcnow(),
                symbol="BTC/USD",
                side="BUY",
                quantity=Decimal("0.1"),
                price=Decimal("50000"),
                pnl=Decimal("10.5"),
                account="test",
                exchange="test"
            )
        ]
        
        sample_summary = TradingSummary(
            total_trades=1,
            winning_trades=1,
            losing_trades=0,
            win_rate=100.0,
            total_pnl=Decimal("10.5"),
            max_drawdown=Decimal("0"),
            sharpe_ratio=2.5,
            avg_win=Decimal("10.5"),
            avg_loss=Decimal("0")
        )
        
        with patch('genebot.cli.commands.analytics.RealDataManager') as mock_dm:
            mock_dm_instance = Mock()
            mock_dm_instance.__enter__ = Mock(return_value=mock_dm_instance)
            mock_dm_instance.__exit__ = Mock(return_value=None)
            mock_dm_instance.get_recent_trades.return_value = sample_trades
            mock_dm_instance.get_trading_summary.return_value = sample_summary
            mock_dm.return_value = mock_dm_instance
            
            result = analytics_command.execute(args)
            
            assert result.success
            assert "Optimization analysis completed" in result.message
    
    def test_invalid_analytics_type(self, analytics_command):
        """Test handling of invalid analytics type"""
        args = Mock()
        args.type = 'invalid_type'
        args.days = 30
        args.output = None
        args.format = 'json'
        
        result = analytics_command.execute(args)
        
        assert not result.success
        assert "Unknown analysis type" in result.message


class TestBacktestAnalyticsCommand:
    """Test backtest analytics functionality"""
    
    @pytest.fixture
    def backtest_analytics_command(self, mock_context, mock_logger, mock_error_handler):
        """Create backtest analytics command instance"""
        return BacktestAnalyticsCommand(mock_context, mock_logger, mock_error_handler)
    
    @pytest.fixture
    def mock_context(self):
        """Create mock CLI context"""
        context = Mock(spec=CLIContext)
        context.workspace_path = Path("/test/workspace")
        return context
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger"""
        return Mock(spec=CLILogger)
    
    @pytest.fixture
    def mock_error_handler(self):
        """Create mock error handler"""
        return Mock(spec=CLIErrorHandler)
    
    def test_backtest_analytics_execution(self, backtest_analytics_command):
        """Test backtest analytics execution"""
        args = Mock()
        args.file = '/test/backtest_results.json'
        args.output = None
        args.format = 'html'
        
        # Mock the backtest file loading to return None (file not found)
        result = backtest_analytics_command.execute(args)
        
        # Should fail because file loading returns None
        assert not result.success
        assert "Could not load backtest results" in result.message
    
    def test_backtest_analytics_with_valid_data(self, backtest_analytics_command):
        """Test backtest analytics with valid data"""
        args = Mock()
        args.file = '/test/backtest_results.json'
        args.output = '/test/output.html'
        args.format = 'html'
        
        # Mock successful backtest data loading
        mock_backtest_data = Mock()
        
        with patch.object(backtest_analytics_command, '_load_backtest_results', return_value=mock_backtest_data):
            with patch('src.backtesting.report_generator.ReportGenerator') as mock_rg:
                mock_rg_instance = Mock()
                mock_rg_instance.generate_full_report.return_value = {
                    'html_report': '/test/generated_report.html'
                }
                mock_rg.return_value = mock_rg_instance
                
                with patch('shutil.move') as mock_move:
                    result = backtest_analytics_command.execute(args)
                    
                    assert result.success
                    assert "Backtest analytics completed successfully" in result.message
                    mock_move.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])