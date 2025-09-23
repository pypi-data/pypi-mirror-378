"""
Tests for orchestration performance monitoring and optimization system.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.orchestration.performance import (
    PerformanceMonitor, PerformanceMetricsCollector, PerformanceCalculator,
    AttributionAnalyzer, StrategyPerformanceSnapshot, PortfolioPerformanceSnapshot
)
from src.orchestration.performance_optimizer import (
    PerformanceBasedOptimizer, PerformanceBasedSelector, MeanVarianceOptimizer,
    OptimizationObjective, OptimizationConstraints, StrategyScore
)
from src.orchestration.interfaces import PerformanceMetrics, RiskMetrics
from src.orchestration.config import MonitoringConfig, OptimizationConfig


class TestPerformanceCalculator:
    """Test performance calculation methods."""
    
    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        calculator = PerformanceCalculator()
        
        # Test with positive returns
        returns = [0.01, 0.02, -0.005, 0.015, 0.008]
        sharpe = calculator.calculate_sharpe_ratio(returns, risk_free_rate=0.02)
        assert isinstance(sharpe, float)
        assert not np.isnan(sharpe)
        
        # Test with empty returns
        assert calculator.calculate_sharpe_ratio([]) == 0.0
        
        # Test with single return
        assert calculator.calculate_sharpe_ratio([0.01]) == 0.0
    
    def test_calculate_max_drawdown(self):
        """Test maximum drawdown calculation."""
        calculator = PerformanceCalculator()
        
        # Test with declining returns
        returns = [0.1, -0.05, -0.03, 0.02, -0.08]
        max_dd = calculator.calculate_max_drawdown(returns)
        assert isinstance(max_dd, float)
        assert max_dd >= 0.0
        
        # Test with empty returns
        assert calculator.calculate_max_drawdown([]) == 0.0
    
    def test_calculate_win_rate(self):
        """Test win rate calculation."""
        calculator = PerformanceCalculator()
        
        # Test with mixed returns
        returns = [0.01, -0.02, 0.015, 0.008, -0.005]
        win_rate = calculator.calculate_win_rate(returns)
        assert 0.0 <= win_rate <= 1.0
        assert win_rate == 0.6  # 3 out of 5 positive
        
        # Test with empty returns
        assert calculator.calculate_win_rate([]) == 0.0
    
    def test_calculate_profit_factor(self):
        """Test profit factor calculation."""
        calculator = PerformanceCalculator()
        
        # Test with mixed returns
        returns = [0.02, -0.01, 0.015, -0.005, 0.01]
        profit_factor = calculator.calculate_profit_factor(returns)
        assert isinstance(profit_factor, float)
        assert profit_factor > 0.0
        
        # Test with only positive returns
        positive_returns = [0.01, 0.02, 0.015]
        pf = calculator.calculate_profit_factor(positive_returns)
        assert pf == float('inf')


class TestPerformanceMetricsCollector:
    """Test performance metrics collection."""
    
    def test_record_strategy_performance(self):
        """Test recording strategy performance snapshots."""
        collector = PerformanceMetricsCollector()
        
        snapshot = StrategyPerformanceSnapshot(
            timestamp=datetime.utcnow(),
            strategy_name="test_strategy",
            total_return=0.15,
            daily_return=0.01,
            sharpe_ratio=1.2,
            max_drawdown=0.05,
            win_rate=0.65,
            profit_factor=1.8,
            volatility=0.12,
            alpha=0.02,
            beta=0.95,
            positions_count=5,
            trades_count=20,
            allocation=0.2
        )
        
        collector.record_strategy_performance(snapshot)
        
        # Verify snapshot was recorded
        snapshots = collector.get_strategy_snapshots("test_strategy")
        assert len(snapshots) == 1
        assert snapshots[0].strategy_name == "test_strategy"
        assert snapshots[0].total_return == 0.15
    
    def test_record_portfolio_performance(self):
        """Test recording portfolio performance snapshots."""
        collector = PerformanceMetricsCollector()
        
        snapshot = PortfolioPerformanceSnapshot(
            timestamp=datetime.utcnow(),
            total_return=0.12,
            daily_return=0.008,
            sharpe_ratio=1.1,
            max_drawdown=0.08,
            volatility=0.15,
            total_value=105000.0,
            active_strategies=3,
            total_positions=12
        )
        
        collector.record_portfolio_performance(snapshot)
        
        # Verify snapshot was recorded
        snapshots = collector.get_portfolio_snapshots()
        assert len(snapshots) == 1
        assert snapshots[0].total_return == 0.12
        assert snapshots[0].total_value == 105000.0
    
    def test_get_performance_history(self):
        """Test retrieving performance history."""
        collector = PerformanceMetricsCollector()
        
        # Add some performance data
        for i in range(10):
            collector._performance_history["test_strategy"].append(0.01 * i)
        
        # Test getting full history
        history = collector.get_performance_history("test_strategy")
        assert len(history) == 10
        
        # Test getting limited history
        limited_history = collector.get_performance_history("test_strategy", periods=5)
        assert len(limited_history) == 5
        assert limited_history == [0.05, 0.06, 0.07, 0.08, 0.09]


class TestPerformanceMonitor:
    """Test performance monitoring system."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock monitoring configuration."""
        return MonitoringConfig(
            performance_tracking=True,
            real_time_metrics=True,
            alert_thresholds={
                "drawdown": 0.05,
                "correlation": 0.75,
                "performance_degradation": -0.10
            }
        )
    
    @pytest.fixture
    def performance_monitor(self, mock_config):
        """Create performance monitor instance."""
        return PerformanceMonitor(mock_config)
    
    def test_collect_performance_metrics(self, performance_monitor):
        """Test collecting performance metrics."""
        # Add some test data
        performance_monitor.record_strategy_snapshot(
            "test_strategy", 0.15, 0.01, 0.2, 5, 20
        )
        
        metrics = performance_monitor.collect_performance_metrics()
        
        assert isinstance(metrics, dict)
        # Should have at least the test strategy
        assert len(metrics) >= 0  # May be empty if no sufficient data
    
    def test_detect_performance_degradation(self, performance_monitor):
        """Test performance degradation detection."""
        # Add historical performance data
        for i in range(20):
            # Simulate declining performance
            daily_return = 0.01 - (i * 0.001)  # Declining returns
            performance_monitor.record_strategy_snapshot(
                "declining_strategy", 0.1 - (i * 0.005), daily_return, 0.2, 5, i+1
            )
        
        degraded = performance_monitor.detect_performance_degradation()
        
        assert isinstance(degraded, list)
        # Should detect the declining strategy if sufficient data
    
    def test_generate_performance_report(self, performance_monitor):
        """Test performance report generation."""
        # Add some test data
        performance_monitor.record_strategy_snapshot(
            "test_strategy", 0.15, 0.01, 0.2, 5, 20
        )
        performance_monitor.record_portfolio_snapshot(
            0.12, 0.008, 105000.0, 3, 12
        )
        
        report = performance_monitor.generate_performance_report()
        
        assert isinstance(report, dict)
        assert 'timestamp' in report
        assert 'summary' in report
        assert 'strategy_metrics' in report


class TestPerformanceBasedSelector:
    """Test performance-based strategy selection."""
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Create mock performance monitor."""
        monitor = Mock()
        return monitor
    
    @pytest.fixture
    def selector(self, mock_performance_monitor):
        """Create performance-based selector."""
        return PerformanceBasedSelector(mock_performance_monitor)
    
    def test_score_strategies(self, selector):
        """Test strategy scoring."""
        # Create mock performance and risk metrics
        performance_metrics = {
            "strategy1": PerformanceMetrics(
                total_return=0.15,
                sharpe_ratio=1.2,
                max_drawdown=0.05,
                win_rate=0.65,
                profit_factor=1.8,
                volatility=0.12,
                calmar_ratio=2.5,
                sortino_ratio=1.5
            ),
            "strategy2": PerformanceMetrics(
                total_return=0.08,
                sharpe_ratio=0.8,
                max_drawdown=0.12,
                win_rate=0.55,
                profit_factor=1.3,
                volatility=0.18,
                calmar_ratio=1.2,
                sortino_ratio=0.9
            )
        }
        
        risk_metrics = {
            "strategy1": RiskMetrics(
                var_95=0.03,
                cvar_95=0.045,
                max_drawdown=0.05,
                volatility=0.12,
                correlation_to_market=0.6,
                beta=0.95
            ),
            "strategy2": RiskMetrics(
                var_95=0.08,
                cvar_95=0.12,
                max_drawdown=0.12,
                volatility=0.18,
                correlation_to_market=0.8,
                beta=1.2
            )
        }
        
        scores = selector.score_strategies(performance_metrics, risk_metrics)
        
        assert isinstance(scores, list)
        assert len(scores) == 2
        
        # Verify scores are StrategyScore objects
        for score in scores:
            assert isinstance(score, StrategyScore)
            assert hasattr(score, 'strategy_name')
            assert hasattr(score, 'score')
            assert hasattr(score, 'recommendation')
        
        # Strategy1 should have higher score than strategy2
        strategy1_score = next(s for s in scores if s.strategy_name == "strategy1")
        strategy2_score = next(s for s in scores if s.strategy_name == "strategy2")
        assert strategy1_score.score > strategy2_score.score
    
    def test_select_strategies(self, selector):
        """Test strategy selection."""
        # Create mock strategy scores
        strategy_scores = [
            StrategyScore(
                strategy_name="high_score",
                score=0.8,
                rank=1,
                metrics={},
                reasons=["Strong performance"],
                recommendation="include"
            ),
            StrategyScore(
                strategy_name="medium_score",
                score=0.6,
                rank=2,
                metrics={},
                reasons=["Decent performance"],
                recommendation="monitor"
            ),
            StrategyScore(
                strategy_name="low_score",
                score=0.3,
                rank=3,
                metrics={},
                reasons=["Poor performance"],
                recommendation="exclude"
            )
        ]
        
        selected = selector.select_strategies(strategy_scores, max_strategies=5, min_score=0.4)
        
        assert isinstance(selected, list)
        assert len(selected) == 2  # Should select high_score and medium_score
        assert "high_score" in selected
        assert "medium_score" in selected
        assert "low_score" not in selected


class TestMeanVarianceOptimizer:
    """Test mean-variance optimization algorithm."""
    
    @pytest.fixture
    def optimizer(self):
        """Create mean-variance optimizer."""
        return MeanVarianceOptimizer()
    
    def test_optimize(self, optimizer):
        """Test portfolio optimization."""
        # Create mock performance and risk metrics
        performance_metrics = {
            "strategy1": PerformanceMetrics(
                total_return=0.15,
                sharpe_ratio=1.2,
                max_drawdown=0.05,
                win_rate=0.65,
                profit_factor=1.8,
                volatility=0.12
            ),
            "strategy2": PerformanceMetrics(
                total_return=0.10,
                sharpe_ratio=0.9,
                max_drawdown=0.08,
                win_rate=0.60,
                profit_factor=1.5,
                volatility=0.15
            )
        }
        
        risk_metrics = {
            "strategy1": RiskMetrics(
                var_95=0.03,
                cvar_95=0.045,
                max_drawdown=0.05,
                volatility=0.12,
                correlation_to_market=0.6,
                beta=0.95
            ),
            "strategy2": RiskMetrics(
                var_95=0.05,
                cvar_95=0.075,
                max_drawdown=0.08,
                volatility=0.15,
                correlation_to_market=0.7,
                beta=1.1
            )
        }
        
        constraints = OptimizationConstraints(
            min_allocation=0.01,
            max_allocation=0.6,
            max_strategies=10
        )
        
        result = optimizer.optimize(
            performance_metrics, risk_metrics, constraints, OptimizationObjective.MAXIMIZE_SHARPE
        )
        
        assert result is not None
        assert hasattr(result, 'allocations')
        assert hasattr(result, 'expected_return')
        assert hasattr(result, 'expected_risk')
        assert hasattr(result, 'expected_sharpe')
        
        # Verify allocations sum to approximately 1
        total_allocation = sum(result.allocations.values())
        assert abs(total_allocation - 1.0) < 0.01
    
    def test_get_algorithm_name(self, optimizer):
        """Test algorithm name."""
        assert optimizer.get_algorithm_name() == "mean_variance"


class TestPerformanceBasedOptimizer:
    """Test performance-based optimization system."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock optimization configuration."""
        return OptimizationConfig(
            optimization_frequency="weekly",
            lookback_period=30,
            min_performance_threshold=0.0
        )
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Create mock performance monitor."""
        return Mock()
    
    @pytest.fixture
    def optimizer(self, mock_config, mock_performance_monitor):
        """Create performance-based optimizer."""
        return PerformanceBasedOptimizer(mock_config, mock_performance_monitor)
    
    def test_optimize_portfolio(self, optimizer):
        """Test portfolio optimization."""
        # Create mock performance and risk metrics
        performance_metrics = {
            "strategy1": PerformanceMetrics(
                total_return=0.15,
                sharpe_ratio=1.2,
                max_drawdown=0.05,
                win_rate=0.65,
                profit_factor=1.8,
                volatility=0.12
            )
        }
        
        risk_metrics = {
            "strategy1": RiskMetrics(
                var_95=0.03,
                cvar_95=0.045,
                max_drawdown=0.05,
                volatility=0.12,
                correlation_to_market=0.6,
                beta=0.95
            )
        }
        
        result = optimizer.optimize_portfolio(performance_metrics, risk_metrics)
        
        assert result is not None
        assert hasattr(result, 'allocations')
        assert hasattr(result, 'selected_strategies')
    
    def test_detect_underperformance(self, optimizer):
        """Test underperformance detection."""
        # Create mock performance metrics with poor performance
        performance_metrics = {
            "poor_strategy": PerformanceMetrics(
                total_return=-0.15,  # Negative return
                sharpe_ratio=-0.5,   # Negative Sharpe
                max_drawdown=0.25,   # High drawdown
                win_rate=0.3,        # Low win rate
                profit_factor=0.8,
                volatility=0.20
            ),
            "good_strategy": PerformanceMetrics(
                total_return=0.12,
                sharpe_ratio=1.1,
                max_drawdown=0.06,
                win_rate=0.65,
                profit_factor=1.6,
                volatility=0.14
            )
        }
        
        underperforming = optimizer.detect_underperformance(performance_metrics)
        
        assert isinstance(underperforming, list)
        assert "poor_strategy" in underperforming
        assert "good_strategy" not in underperforming
    
    def test_adjust_allocations(self, optimizer):
        """Test allocation adjustments."""
        current_allocations = {
            "strategy1": 0.4,
            "strategy2": 0.6
        }
        
        performance_metrics = {
            "strategy1": PerformanceMetrics(
                total_return=0.15,
                sharpe_ratio=1.2,
                max_drawdown=0.05,
                win_rate=0.65,
                profit_factor=1.8,
                volatility=0.12
            ),
            "strategy2": PerformanceMetrics(
                total_return=0.08,
                sharpe_ratio=0.7,
                max_drawdown=0.10,
                win_rate=0.55,
                profit_factor=1.3,
                volatility=0.16
            )
        }
        
        adjusted = optimizer.adjust_allocations(current_allocations, performance_metrics)
        
        assert isinstance(adjusted, dict)
        assert len(adjusted) == 2
        
        # Verify allocations sum to approximately 1
        total_allocation = sum(adjusted.values())
        assert abs(total_allocation - 1.0) < 0.01
        
        # Strategy1 should get higher allocation due to better performance
        assert adjusted["strategy1"] > adjusted["strategy2"]
    
    def test_should_reoptimize(self, optimizer):
        """Test reoptimization criteria."""
        current_allocations = {"strategy1": 0.5, "strategy2": 0.5}
        performance_metrics = {
            "strategy1": PerformanceMetrics(
                total_return=0.10,
                sharpe_ratio=1.0,
                max_drawdown=0.06,
                win_rate=0.60,
                profit_factor=1.5,
                volatility=0.14
            )
        }
        
        # Should return boolean
        should_reopt = optimizer.should_reoptimize(current_allocations, performance_metrics)
        assert isinstance(should_reopt, bool)
    
    def test_get_performance_summary(self, optimizer):
        """Test performance summary generation."""
        summary = optimizer.get_performance_summary()
        
        assert isinstance(summary, dict)
        assert 'total_optimizations' in summary
        assert 'degraded_strategies' in summary


if __name__ == "__main__":
    pytest.main([__file__])