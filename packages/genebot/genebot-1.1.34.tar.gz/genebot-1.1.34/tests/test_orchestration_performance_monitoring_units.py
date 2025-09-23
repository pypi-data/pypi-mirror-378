"""
Unit tests for orchestration performance monitoring components.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.orchestration.performance import (
    PerformanceMonitor, MetricsCollector, PerformanceAnalyzer,
    AttributionAnalyzer, PerformanceOptimizer, AlertManager
)
from src.orchestration.config import MonitoringConfig
from src.orchestration.interfaces import (
    PerformanceMetrics, AttributionAnalysis, PerformanceReport,
    Alert, TradingSignal, Portfolio, Position
)


class TestPerformanceMonitor:
    """Test the main performance monitor."""
    
    @pytest.fixture
    def monitoring_config(self):
        """Create test monitoring configuration."""
        return MonitoringConfig(
            performance_tracking=True,
            alert_thresholds={
                "drawdown": 0.05,
                "correlation": 0.75,
                "underperformance": 0.10
            },
            metrics_collection_interval=60,
            performance_lookback_period=30
        )
    
    @pytest.fixture
    def performance_monitor(self, monitoring_config):
        """Create performance monitor instance."""
        return PerformanceMonitor(monitoring_config)
    
    @pytest.fixture
    def sample_strategies(self):
        """Create sample strategy list."""
        return ["strategy_1", "strategy_2", "strategy_3"]
    
    def test_initialization(self, performance_monitor, monitoring_config):
        """Test performance monitor initialization."""
        assert performance_monitor.config == monitoring_config
        assert isinstance(performance_monitor.metrics_collector, MetricsCollector)
        assert isinstance(performance_monitor.performance_analyzer, PerformanceAnalyzer)
        assert isinstance(performance_monitor.attribution_analyzer, AttributionAnalyzer)
        assert isinstance(performance_monitor.alert_manager, AlertManager)
    
    def test_collect_performance_metrics(self, performance_monitor, sample_strategies):
        """Test performance metrics collection."""
        # Mock the metrics collector
        expected_metrics = {
            "strategy_1": PerformanceMetrics(
                total_return=0.15, sharpe_ratio=1.2, max_drawdown=0.05,
                win_rate=0.65, profit_factor=1.8, volatility=0.12,
                alpha=0.03, beta=0.8, information_ratio=0.9
            ),
            "strategy_2": PerformanceMetrics(
                total_return=0.08, sharpe_ratio=0.9, max_drawdown=0.08,
                win_rate=0.58, profit_factor=1.4, volatility=0.15,
                alpha=0.01, beta=1.1, information_ratio=0.6
            )
        }
        
        with patch.object(performance_monitor.metrics_collector, 'collect_strategy_metrics', return_value=expected_metrics):
            metrics = performance_monitor.collect_performance_metrics(sample_strategies)
            
            assert metrics == expected_metrics
            performance_monitor.metrics_collector.collect_strategy_metrics.assert_called_once_with(sample_strategies)
    
    def test_analyze_attribution(self, performance_monitor):
        """Test performance attribution analysis."""
        portfolio_return = 0.12
        strategy_returns = {
            "strategy_1": 0.15,
            "strategy_2": 0.08,
            "strategy_3": 0.10
        }
        allocations = {
            "strategy_1": 0.4,
            "strategy_2": 0.3,
            "strategy_3": 0.3
        }
        
        expected_attribution = AttributionAnalysis(
            strategy_contributions={"strategy_1": 0.06, "strategy_2": 0.024, "strategy_3": 0.03},
            allocation_effect=0.002,
            selection_effect=0.003,
            interaction_effect=0.001,
            total_return=0.12
        )
        
        with patch.object(performance_monitor.attribution_analyzer, 'analyze_attribution', return_value=expected_attribution):
            attribution = performance_monitor.analyze_attribution(portfolio_return, strategy_returns, allocations)
            
            assert attribution == expected_attribution
    
    def test_generate_performance_report(self, performance_monitor):
        """Test performance report generation."""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        expected_report = PerformanceReport(
            period_start=start_date,
            period_end=end_date,
            total_return=0.12,
            sharpe_ratio=1.1,
            max_drawdown=0.06,
            strategy_metrics={},
            attribution_analysis=None
        )
        
        with patch.object(performance_monitor.performance_analyzer, 'generate_report', return_value=expected_report):
            report = performance_monitor.generate_performance_report(start_date, end_date)
            
            assert report == expected_report
    
    def test_check_alert_conditions(self, performance_monitor):
        """Test alert condition checking."""
        metrics = {
            "strategy_1": PerformanceMetrics(
                total_return=-0.12, sharpe_ratio=0.3, max_drawdown=0.08,
                win_rate=0.45, profit_factor=0.8, volatility=0.18,
                alpha=-0.02, beta=1.2, information_ratio=-0.3
            )
        }
        
        expected_alerts = [
            Alert(
                type="underperformance",
                strategy="strategy_1",
                message="Strategy underperforming threshold",
                severity="warning",
                timestamp=datetime.now()
            )
        ]
        
        with patch.object(performance_monitor.alert_manager, 'check_alerts', return_value=expected_alerts):
            alerts = performance_monitor.check_alert_conditions(metrics)
            
            assert len(alerts) == 1
            assert alerts[0].type == "underperformance"


class TestMetricsCollector:
    """Test metrics collection component."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector."""
        config = MonitoringConfig()
        return MetricsCollector(config)
    
    @pytest.fixture
    def sample_trades(self):
        """Create sample trade data."""
        return [
            {
                "strategy": "strategy_1",
                "symbol": "BTCUSD",
                "entry_time": datetime.now() - timedelta(hours=2),
                "exit_time": datetime.now() - timedelta(hours=1),
                "entry_price": 50000,
                "exit_price": 51000,
                "quantity": 0.1,
                "pnl": 100,
                "side": "long"
            },
            {
                "strategy": "strategy_1",
                "symbol": "ETHUSD",
                "entry_time": datetime.now() - timedelta(hours=3),
                "exit_time": datetime.now() - timedelta(hours=2),
                "entry_price": 3000,
                "exit_price": 2950,
                "quantity": 1.0,
                "pnl": -50,
                "side": "long"
            }
        ]
    
    def test_collect_strategy_metrics(self, metrics_collector, sample_trades):
        """Test strategy metrics collection."""
        strategies = ["strategy_1"]
        
        with patch.object(metrics_collector, '_get_strategy_trades', return_value=sample_trades):
            metrics = metrics_collector.collect_strategy_metrics(strategies)
            
            assert "strategy_1" in metrics
            strategy_metrics = metrics["strategy_1"]
            
            assert isinstance(strategy_metrics, PerformanceMetrics)
            assert strategy_metrics.total_return > 0  # Net positive return
            assert strategy_metrics.win_rate == 0.5  # 1 win out of 2 trades
            assert strategy_metrics.profit_factor > 0
    
    def test_calculate_sharpe_ratio(self, metrics_collector):
        """Test Sharpe ratio calculation."""
        returns = np.array([0.01, -0.02, 0.015, -0.01, 0.005, 0.02, -0.005])
        risk_free_rate = 0.02  # 2% annual
        
        sharpe_ratio = metrics_collector.calculate_sharpe_ratio(returns, risk_free_rate)
        
        assert isinstance(sharpe_ratio, float)
        assert not np.isnan(sharpe_ratio)
    
    def test_calculate_max_drawdown(self, metrics_collector):
        """Test maximum drawdown calculation."""
        portfolio_values = np.array([100000, 105000, 102000, 98000, 95000, 97000, 103000])
        
        max_drawdown = metrics_collector.calculate_max_drawdown(portfolio_values)
        
        # Maximum drawdown from peak 105000 to trough 95000
        expected_drawdown = (105000 - 95000) / 105000
        assert abs(max_drawdown - expected_drawdown) < 1e-6
    
    def test_calculate_win_rate(self, metrics_collector, sample_trades):
        """Test win rate calculation."""
        win_rate = metrics_collector.calculate_win_rate(sample_trades)
        
        # 1 winning trade out of 2 total trades
        assert win_rate == 0.5
    
    def test_calculate_profit_factor(self, metrics_collector, sample_trades):
        """Test profit factor calculation."""
        profit_factor = metrics_collector.calculate_profit_factor(sample_trades)
        
        # Gross profit: 100, Gross loss: 50
        # Profit factor: 100 / 50 = 2.0
        assert profit_factor == 2.0
    
    def test_calculate_information_ratio(self, metrics_collector):
        """Test information ratio calculation."""
        strategy_returns = np.array([0.01, -0.02, 0.015, -0.01, 0.005])
        benchmark_returns = np.array([0.008, -0.015, 0.012, -0.008, 0.003])
        
        info_ratio = metrics_collector.calculate_information_ratio(strategy_returns, benchmark_returns)
        
        assert isinstance(info_ratio, float)
        assert not np.isnan(info_ratio)


class TestPerformanceAnalyzer:
    """Test performance analysis component."""
    
    @pytest.fixture
    def performance_analyzer(self):
        """Create performance analyzer."""
        config = MonitoringConfig()
        return PerformanceAnalyzer(config)
    
    def test_generate_report(self, performance_analyzer):
        """Test performance report generation."""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        strategy_metrics = {
            "strategy_1": PerformanceMetrics(
                total_return=0.15, sharpe_ratio=1.2, max_drawdown=0.05,
                win_rate=0.65, profit_factor=1.8, volatility=0.12,
                alpha=0.03, beta=0.8, information_ratio=0.9
            )
        }
        
        with patch.object(performance_analyzer, '_calculate_portfolio_metrics') as mock_portfolio, \
             patch.object(performance_analyzer, '_generate_attribution_analysis') as mock_attribution:
            
            mock_portfolio.return_value = (0.12, 1.1, 0.06)  # return, sharpe, drawdown
            mock_attribution.return_value = AttributionAnalysis(
                strategy_contributions={"strategy_1": 0.12},
                allocation_effect=0.0,
                selection_effect=0.0,
                interaction_effect=0.0,
                total_return=0.12
            )
            
            report = performance_analyzer.generate_report(start_date, end_date, strategy_metrics)
            
            assert isinstance(report, PerformanceReport)
            assert report.period_start == start_date
            assert report.period_end == end_date
            assert report.total_return == 0.12
            assert report.sharpe_ratio == 1.1
            assert report.max_drawdown == 0.06
    
    def test_compare_strategies(self, performance_analyzer):
        """Test strategy comparison."""
        metrics_1 = PerformanceMetrics(
            total_return=0.15, sharpe_ratio=1.2, max_drawdown=0.05,
            win_rate=0.65, profit_factor=1.8, volatility=0.12,
            alpha=0.03, beta=0.8, information_ratio=0.9
        )
        
        metrics_2 = PerformanceMetrics(
            total_return=0.08, sharpe_ratio=0.9, max_drawdown=0.08,
            win_rate=0.58, profit_factor=1.4, volatility=0.15,
            alpha=0.01, beta=1.1, information_ratio=0.6
        )
        
        comparison = performance_analyzer.compare_strategies("strategy_1", "strategy_2", metrics_1, metrics_2)
        
        assert comparison["better_strategy"] == "strategy_1"  # Higher Sharpe ratio
        assert comparison["metrics_comparison"]["sharpe_ratio"]["winner"] == "strategy_1"
        assert comparison["metrics_comparison"]["total_return"]["winner"] == "strategy_1"
    
    def test_identify_underperforming_strategies(self, performance_analyzer):
        """Test underperforming strategy identification."""
        strategy_metrics = {
            "strategy_1": PerformanceMetrics(
                total_return=0.15, sharpe_ratio=1.2, max_drawdown=0.05,
                win_rate=0.65, profit_factor=1.8, volatility=0.12,
                alpha=0.03, beta=0.8, information_ratio=0.9
            ),
            "strategy_2": PerformanceMetrics(
                total_return=-0.05, sharpe_ratio=-0.3, max_drawdown=0.12,
                win_rate=0.42, profit_factor=0.8, volatility=0.18,
                alpha=-0.02, beta=1.2, information_ratio=-0.4
            )
        }
        
        underperforming = performance_analyzer.identify_underperforming_strategies(
            strategy_metrics, min_sharpe_ratio=0.5
        )
        
        assert "strategy_2" in underperforming
        assert "strategy_1" not in underperforming


class TestAttributionAnalyzer:
    """Test attribution analysis component."""
    
    @pytest.fixture
    def attribution_analyzer(self):
        """Create attribution analyzer."""
        config = MonitoringConfig()
        return AttributionAnalyzer(config)
    
    def test_analyze_attribution(self, attribution_analyzer):
        """Test attribution analysis."""
        portfolio_return = 0.12
        strategy_returns = {
            "strategy_1": 0.15,
            "strategy_2": 0.08,
            "strategy_3": 0.10
        }
        allocations = {
            "strategy_1": 0.4,
            "strategy_2": 0.3,
            "strategy_3": 0.3
        }
        
        attribution = attribution_analyzer.analyze_attribution(portfolio_return, strategy_returns, allocations)
        
        assert isinstance(attribution, AttributionAnalysis)
        assert len(attribution.strategy_contributions) == 3
        
        # Check that contributions sum to total return (approximately)
        total_contribution = sum(attribution.strategy_contributions.values())
        assert abs(total_contribution - portfolio_return) < 0.01
    
    def test_calculate_strategy_contributions(self, attribution_analyzer):
        """Test strategy contribution calculation."""
        strategy_returns = {"strategy_1": 0.15, "strategy_2": 0.08}
        allocations = {"strategy_1": 0.6, "strategy_2": 0.4}
        
        contributions = attribution_analyzer.calculate_strategy_contributions(strategy_returns, allocations)
        
        # Strategy 1: 0.15 * 0.6 = 0.09
        # Strategy 2: 0.08 * 0.4 = 0.032
        assert abs(contributions["strategy_1"] - 0.09) < 1e-6
        assert abs(contributions["strategy_2"] - 0.032) < 1e-6
    
    def test_calculate_allocation_effect(self, attribution_analyzer):
        """Test allocation effect calculation."""
        actual_allocations = {"strategy_1": 0.6, "strategy_2": 0.4}
        benchmark_allocations = {"strategy_1": 0.5, "strategy_2": 0.5}
        strategy_returns = {"strategy_1": 0.15, "strategy_2": 0.08}
        
        allocation_effect = attribution_analyzer.calculate_allocation_effect(
            actual_allocations, benchmark_allocations, strategy_returns
        )
        
        # Effect = (0.6-0.5)*0.15 + (0.4-0.5)*0.08 = 0.015 - 0.008 = 0.007
        assert abs(allocation_effect - 0.007) < 1e-6


class TestPerformanceOptimizer:
    """Test performance optimization component."""
    
    @pytest.fixture
    def performance_optimizer(self):
        """Create performance optimizer."""
        config = MonitoringConfig()
        return PerformanceOptimizer(config)
    
    def test_optimize_strategy_selection(self, performance_optimizer):
        """Test strategy selection optimization."""
        strategy_metrics = {
            "strategy_1": PerformanceMetrics(
                total_return=0.15, sharpe_ratio=1.2, max_drawdown=0.05,
                win_rate=0.65, profit_factor=1.8, volatility=0.12,
                alpha=0.03, beta=0.8, information_ratio=0.9
            ),
            "strategy_2": PerformanceMetrics(
                total_return=0.08, sharpe_ratio=0.9, max_drawdown=0.08,
                win_rate=0.58, profit_factor=1.4, volatility=0.15,
                alpha=0.01, beta=1.1, information_ratio=0.6
            ),
            "strategy_3": PerformanceMetrics(
                total_return=-0.05, sharpe_ratio=-0.3, max_drawdown=0.12,
                win_rate=0.42, profit_factor=0.8, volatility=0.18,
                alpha=-0.02, beta=1.2, information_ratio=-0.4
            )
        }
        
        selected_strategies = performance_optimizer.optimize_strategy_selection(
            strategy_metrics, max_strategies=2, min_sharpe_ratio=0.5
        )
        
        # Should select top 2 strategies with positive Sharpe ratios
        assert len(selected_strategies) == 2
        assert "strategy_1" in selected_strategies
        assert "strategy_2" in selected_strategies
        assert "strategy_3" not in selected_strategies
    
    def test_suggest_allocation_adjustments(self, performance_optimizer):
        """Test allocation adjustment suggestions."""
        current_allocations = {"strategy_1": 0.5, "strategy_2": 0.5}
        performance_metrics = {
            "strategy_1": PerformanceMetrics(
                total_return=0.15, sharpe_ratio=1.5, max_drawdown=0.05,
                win_rate=0.65, profit_factor=1.8, volatility=0.12,
                alpha=0.03, beta=0.8, information_ratio=0.9
            ),
            "strategy_2": PerformanceMetrics(
                total_return=0.05, sharpe_ratio=0.5, max_drawdown=0.08,
                win_rate=0.52, profit_factor=1.1, volatility=0.15,
                alpha=0.0, beta=1.1, information_ratio=0.2
            )
        }
        
        adjustments = performance_optimizer.suggest_allocation_adjustments(
            current_allocations, performance_metrics
        )
        
        # Should suggest increasing allocation to better performing strategy
        assert adjustments["strategy_1"] > 0  # Increase allocation
        assert adjustments["strategy_2"] < 0  # Decrease allocation


class TestAlertManager:
    """Test alert management component."""
    
    @pytest.fixture
    def alert_manager(self):
        """Create alert manager."""
        config = MonitoringConfig(
            alert_thresholds={
                "drawdown": 0.05,
                "correlation": 0.75,
                "underperformance": 0.10
            }
        )
        return AlertManager(config)
    
    def test_check_alerts(self, alert_manager):
        """Test alert checking."""
        strategy_metrics = {
            "strategy_1": PerformanceMetrics(
                total_return=-0.12, sharpe_ratio=-0.5, max_drawdown=0.08,
                win_rate=0.42, profit_factor=0.8, volatility=0.18,
                alpha=-0.02, beta=1.2, information_ratio=-0.4
            )
        }
        
        alerts = alert_manager.check_alerts(strategy_metrics)
        
        # Should generate alerts for underperformance and high drawdown
        assert len(alerts) >= 1
        alert_types = [alert.type for alert in alerts]
        assert "underperformance" in alert_types or "drawdown" in alert_types
    
    def test_create_drawdown_alert(self, alert_manager):
        """Test drawdown alert creation."""
        strategy = "strategy_1"
        drawdown = 0.08
        
        alert = alert_manager.create_drawdown_alert(strategy, drawdown)
        
        assert alert.type == "drawdown"
        assert alert.strategy == strategy
        assert alert.severity == "warning"  # Above threshold but not critical
        assert str(drawdown) in alert.message
    
    def test_create_underperformance_alert(self, alert_manager):
        """Test underperformance alert creation."""
        strategy = "strategy_1"
        performance = -0.12
        
        alert = alert_manager.create_underperformance_alert(strategy, performance)
        
        assert alert.type == "underperformance"
        assert alert.strategy == strategy
        assert alert.severity == "critical"  # Significant underperformance
        assert str(performance) in alert.message
    
    def test_filter_duplicate_alerts(self, alert_manager):
        """Test duplicate alert filtering."""
        alerts = [
            Alert(
                type="drawdown", strategy="strategy_1", message="High drawdown",
                severity="warning", timestamp=datetime.now()
            ),
            Alert(
                type="drawdown", strategy="strategy_1", message="High drawdown",
                severity="warning", timestamp=datetime.now()
            ),
            Alert(
                type="underperformance", strategy="strategy_2", message="Poor performance",
                severity="critical", timestamp=datetime.now()
            )
        ]
        
        filtered_alerts = alert_manager.filter_duplicate_alerts(alerts)
        
        # Should remove duplicate drawdown alert
        assert len(filtered_alerts) == 2
        alert_keys = [(alert.type, alert.strategy) for alert in filtered_alerts]
        assert ("drawdown", "strategy_1") in alert_keys
        assert ("underperformance", "strategy_2") in alert_keys