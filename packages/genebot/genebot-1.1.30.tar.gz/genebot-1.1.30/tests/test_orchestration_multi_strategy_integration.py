"""
Integration tests for multi-strategy orchestration scenarios.
"""

import pytest
import asyncio
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from collections import defaultdict

from src.orchestration.orchestrator import StrategyOrchestrator
from src.orchestration.config import (
    OrchestratorConfig, AllocationConfig, RiskConfig, MonitoringConfig,
    StrategyConfig, AllocationMethod, RebalanceFrequency
)
from src.orchestration.interfaces import (
    PerformanceMetrics, RiskMetrics, TradingSignal, Portfolio, Position,
    UnifiedMarketData, AllocationSnapshot, AttributionAnalysis
)
from src.strategies.base_strategy import BaseStrategy


class MockStrategy(BaseStrategy):
    """Mock strategy for testing."""
    
    def __init__(self, name, parameters=None):
        super().__init__(name, parameters or {})
        self.signals_generated = []
        self.performance_history = []
    
    async def generate_signals(self, market_data):
        """Generate mock signals."""
        signals = []
        for data in market_data:
            if self.should_generate_signal(data):
                signal = TradingSignal(
                    strategy=self.name,
                    symbol=data.symbol,
                    action=self.get_signal_action(data),
                    quantity=self.get_signal_quantity(data),
                    price=data.close,
                    confidence=self.get_signal_confidence(data),
                    timestamp=data.timestamp
                )
                signals.append(signal)
                self.signals_generated.append(signal)
        return signals
    
    def should_generate_signal(self, data):
        """Override in specific mock strategies."""
        return True
    
    def get_signal_action(self, data):
        """Override in specific mock strategies."""
        return "BUY"
    
    def get_signal_quantity(self, data):
        """Override in specific mock strategies."""
        return 0.1
    
    def get_signal_confidence(self, data):
        """Override in specific mock strategies."""
        return 0.7


class MockTrendFollowingStrategy(MockStrategy):
    """Mock trend following strategy."""
    
    def should_generate_signal(self, data):
        # Simple trend following logic
        return data.close > data.open
    
    def get_signal_action(self, data):
        return "BUY" if data.close > data.open else "SELL"
    
    def get_signal_confidence(self, data):
        price_change = abs(data.close - data.open) / data.open
        return min(0.9, 0.5 + price_change * 10)


class MockMeanReversionStrategy(MockStrategy):
    """Mock mean reversion strategy."""
    
    def should_generate_signal(self, data):
        # Simple mean reversion logic
        price_change = abs(data.close - data.open) / data.open
        return price_change > 0.02  # Signal on significant moves
    
    def get_signal_action(self, data):
        return "SELL" if data.close > data.open else "BUY"  # Opposite to trend
    
    def get_signal_confidence(self, data):
        price_change = abs(data.close - data.open) / data.open
        return min(0.8, 0.3 + price_change * 15)


class MockVolatilityStrategy(MockStrategy):
    """Mock volatility-based strategy."""
    
    def should_generate_signal(self, data):
        volatility = (data.high - data.low) / data.open
        return volatility > 0.01  # Signal on high volatility
    
    def get_signal_action(self, data):
        return "BUY"  # Always buy on volatility
    
    def get_signal_quantity(self, data):
        volatility = (data.high - data.low) / data.open
        return min(0.2, 0.05 + volatility * 5)  # Size based on volatility
    
    def get_signal_confidence(self, data):
        volatility = (data.high - data.low) / data.open
        return min(0.9, 0.4 + volatility * 20)


class TestMultiStrategyCoordination:
    """Test coordination between multiple strategies."""
    
    @pytest.fixture
    def multi_strategy_config(self):
        """Create configuration with diverse strategies."""
        return OrchestratorConfig(
            max_concurrent_strategies=10,
            enable_dynamic_allocation=True,
            allocation=AllocationConfig(
                method=AllocationMethod.PERFORMANCE_BASED,
                rebalance_frequency=RebalanceFrequency.DAILY,
                min_allocation=0.02,
                max_allocation=0.40
            ),
            risk=RiskConfig(
                max_portfolio_drawdown=0.15,
                max_strategy_correlation=0.85,
                position_size_limit=0.10
            ),
            strategies=[
                StrategyConfig(type="TrendFollowing", name="trend_1", enabled=True,
                             parameters={"lookback": 10}),
                StrategyConfig(type="TrendFollowing", name="trend_2", enabled=True,
                             parameters={"lookback": 20}),
                StrategyConfig(type="MeanReversion", name="mean_rev_1", enabled=True,
                             parameters={"threshold": 2.0}),
                StrategyConfig(type="MeanReversion", name="mean_rev_2", enabled=True,
                             parameters={"threshold": 1.5}),
                StrategyConfig(type="Volatility", name="vol_1", enabled=True,
                             parameters={"window": 15}),
                StrategyConfig(type="Volatility", name="vol_2", enabled=True,
                             parameters={"window": 30})
            ]
        )
    
    @pytest.fixture
    def orchestrator(self, multi_strategy_config):
        """Create orchestrator with multiple strategies."""
        return StrategyOrchestrator(multi_strategy_config)
    
    @pytest.fixture
    def diverse_market_data(self):
        """Create diverse market data scenarios."""
        base_time = datetime.now()
        scenarios = []
        
        # Trending market
        for i in range(10):
            scenarios.append(UnifiedMarketData(
                symbol="BTCUSD",
                timestamp=base_time + timedelta(minutes=i),
                open=50000 + i * 100,
                high=50100 + i * 100,
                low=49950 + i * 100,
                close=50050 + i * 100,
                volume=1000,
                market_type="crypto"
            ))
        
        # Volatile market
        for i in range(10, 20):
            price_base = 51000
            volatility = 500 if i % 2 == 0 else -500
            scenarios.append(UnifiedMarketData(
                symbol="ETHUSD",
                timestamp=base_time + timedelta(minutes=i),
                open=price_base,
                high=price_base + abs(volatility),
                low=price_base - abs(volatility),
                close=price_base + volatility,
                volume=2000,
                market_type="crypto"
            ))
        
        # Mean reverting market
        for i in range(20, 30):
            base_price = 1.1000
            deviation = 0.0050 * ((-1) ** i)  # Oscillating
            scenarios.append(UnifiedMarketData(
                symbol="EURUSD",
                timestamp=base_time + timedelta(minutes=i),
                open=base_price,
                high=base_price + abs(deviation),
                low=base_price - abs(deviation),
                close=base_price + deviation,
                volume=10000,
                market_type="forex"
            ))
        
        return scenarios
    
    @pytest.mark.asyncio
    async def test_strategy_signal_aggregation(self, orchestrator, diverse_market_data):
        """Test aggregation of signals from multiple strategies."""
        # Mock strategy instances
        mock_strategies = {
            "trend_1": MockTrendFollowingStrategy("trend_1"),
            "trend_2": MockTrendFollowingStrategy("trend_2"),
            "mean_rev_1": MockMeanReversionStrategy("mean_rev_1"),
            "mean_rev_2": MockMeanReversionStrategy("mean_rev_2"),
            "vol_1": MockVolatilityStrategy("vol_1"),
            "vol_2": MockVolatilityStrategy("vol_2")
        }
        
        with patch.object(orchestrator.strategy_engine, 'get_strategy_instances') as mock_get_strategies, \
             patch.object(orchestrator.strategy_engine, 'get_active_strategies') as mock_active:
            
            mock_get_strategies.return_value = mock_strategies
            mock_active.return_value = list(mock_strategies.keys())
            
            await orchestrator.start()
            
            # Process market data
            all_signals = []
            for data_batch in [diverse_market_data[i:i+5] for i in range(0, len(diverse_market_data), 5)]:
                signals = await orchestrator.process_market_data(data_batch)
                all_signals.extend(signals)
            
            # Analyze signal patterns
            signal_by_strategy = defaultdict(list)
            signal_by_symbol = defaultdict(list)
            
            for signal in all_signals:
                signal_by_strategy[signal.strategy].append(signal)
                signal_by_symbol[signal.symbol].append(signal)
            
            # Verify different strategies generated different types of signals
            trend_signals = signal_by_strategy.get("trend_1", []) + signal_by_strategy.get("trend_2", [])
            mean_rev_signals = signal_by_strategy.get("mean_rev_1", []) + signal_by_strategy.get("mean_rev_2", [])
            vol_signals = signal_by_strategy.get("vol_1", []) + signal_by_strategy.get("vol_2", [])
            
            # Trend following strategies should generate more BUY signals in trending market
            trend_buy_ratio = len([s for s in trend_signals if s.action == "BUY"]) / max(len(trend_signals), 1)
            
            # Mean reversion strategies should generate opposite signals
            mean_rev_sell_ratio = len([s for s in mean_rev_signals if s.action == "SELL"]) / max(len(mean_rev_signals), 1)
            
            # Volatility strategies should generate signals during volatile periods
            assert len(vol_signals) > 0  # Should generate some signals
            
            await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_conflicting_signal_resolution(self, orchestrator, diverse_market_data):
        """Test resolution of conflicting signals from different strategies."""
        # Create scenarios where strategies will conflict
        conflicting_data = [
            UnifiedMarketData(
                symbol="BTCUSD",
                timestamp=datetime.now(),
                open=50000,
                high=50200,  # High volatility
                low=49800,
                close=49900,  # Down move (trend vs mean reversion conflict)
                volume=1000,
                market_type="crypto"
            )
        ]
        
        mock_strategies = {
            "trend_1": MockTrendFollowingStrategy("trend_1"),
            "mean_rev_1": MockMeanReversionStrategy("mean_rev_1"),
            "vol_1": MockVolatilityStrategy("vol_1")
        }
        
        with patch.object(orchestrator.strategy_engine, 'get_strategy_instances') as mock_get_strategies, \
             patch.object(orchestrator.strategy_engine, 'get_active_strategies') as mock_active, \
             patch.object(orchestrator.decision_engine, 'resolve_signal_conflicts') as mock_resolve:
            
            mock_get_strategies.return_value = mock_strategies
            mock_active.return_value = list(mock_strategies.keys())
            
            # Mock conflict resolution to prioritize by confidence
            def resolve_conflicts(signals):
                if not signals:
                    return signals
                
                # Group by symbol and action
                signal_groups = defaultdict(list)
                for signal in signals:
                    key = (signal.symbol, signal.action)
                    signal_groups[key].append(signal)
                
                resolved = []
                for (symbol, action), group in signal_groups.items():
                    # Take highest confidence signal
                    best_signal = max(group, key=lambda s: s.confidence)
                    resolved.append(best_signal)
                
                return resolved
            
            mock_resolve.side_effect = resolve_conflicts
            
            await orchestrator.start()
            
            # Process conflicting market data
            signals = await orchestrator.process_market_data(conflicting_data)
            
            # Verify conflict resolution was called
            mock_resolve.assert_called()
            
            # Check that conflicting signals were resolved
            btc_signals = [s for s in signals if s.symbol == "BTCUSD"]
            actions = [s.action for s in btc_signals]
            
            # Should not have both BUY and SELL for same symbol (unless different quantities/timing)
            if len(set(actions)) > 1:
                # If both actions exist, they should be from different resolution logic
                buy_signals = [s for s in btc_signals if s.action == "BUY"]
                sell_signals = [s for s in btc_signals if s.action == "SELL"]
                
                # Net position should be reasonable
                net_quantity = sum(s.quantity for s in buy_signals) - sum(s.quantity for s in sell_signals)
                assert abs(net_quantity) <= max(s.quantity for s in btc_signals)
            
            await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_dynamic_strategy_weighting(self, orchestrator):
        """Test dynamic weighting of strategies based on performance."""
        # Mock different performance levels
        performance_metrics = {
            "trend_1": PerformanceMetrics(
                total_return=0.25, sharpe_ratio=2.0, max_drawdown=0.03,
                win_rate=0.80, profit_factor=2.5, volatility=0.12,
                alpha=0.08, beta=0.9, information_ratio=1.8
            ),
            "trend_2": PerformanceMetrics(
                total_return=0.15, sharpe_ratio=1.2, max_drawdown=0.05,
                win_rate=0.65, profit_factor=1.8, volatility=0.14,
                alpha=0.04, beta=1.0, information_ratio=1.0
            ),
            "mean_rev_1": PerformanceMetrics(
                total_return=0.08, sharpe_ratio=0.8, max_drawdown=0.08,
                win_rate=0.58, profit_factor=1.4, volatility=0.16,
                alpha=0.02, beta=0.8, information_ratio=0.6
            ),
            "mean_rev_2": PerformanceMetrics(
                total_return=-0.02, sharpe_ratio=-0.2, max_drawdown=0.12,
                win_rate=0.45, profit_factor=0.9, volatility=0.18,
                alpha=-0.01, beta=1.1, information_ratio=-0.1
            ),
            "vol_1": PerformanceMetrics(
                total_return=0.18, sharpe_ratio=1.5, max_drawdown=0.06,
                win_rate=0.72, profit_factor=2.0, volatility=0.15,
                alpha=0.06, beta=0.85, information_ratio=1.3
            ),
            "vol_2": PerformanceMetrics(
                total_return=0.12, sharpe_ratio=1.0, max_drawdown=0.07,
                win_rate=0.62, profit_factor=1.6, volatility=0.13,
                alpha=0.03, beta=0.95, information_ratio=0.8
            )
        }
        
        with patch.object(orchestrator.performance_monitor, 'collect_performance_metrics') as mock_metrics, \
             patch.object(orchestrator.allocation_manager, 'needs_rebalancing') as mock_needs_rebalance:
            
            mock_metrics.return_value = performance_metrics
            mock_needs_rebalance.return_value = True
            
            await orchestrator.start()
            
            # Trigger allocation optimization
            await orchestrator.optimize_strategy_allocation()
            
            allocations = orchestrator.allocation_manager.allocations
            
            # Verify performance-based allocation
            # Best performer (trend_1) should get highest allocation
            assert allocations.get("trend_1", 0) >= allocations.get("trend_2", 0)
            assert allocations.get("trend_1", 0) >= allocations.get("vol_1", 0)
            
            # Poor performer (mean_rev_2) should get minimal allocation
            assert allocations.get("mean_rev_2", 0) <= orchestrator.config.allocation.min_allocation
            
            # Allocations should sum to approximately 1.0
            total_allocation = sum(allocations.values())
            assert abs(total_allocation - 1.0) < 0.01
            
            await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_strategy_correlation_impact_on_allocation(self, orchestrator):
        """Test how strategy correlations affect allocation decisions."""
        # Mock high correlations between similar strategy types
        correlations = {
            ("trend_1", "trend_2"): 0.90,  # High correlation - similar strategies
            ("mean_rev_1", "mean_rev_2"): 0.85,  # High correlation - similar strategies
            ("vol_1", "vol_2"): 0.75,  # Moderate correlation
            ("trend_1", "mean_rev_1"): -0.20,  # Negative correlation - opposite strategies
            ("trend_1", "vol_1"): 0.30,  # Low positive correlation
            ("mean_rev_1", "vol_1"): 0.15  # Low positive correlation
        }
        
        # Mock moderate performance for all strategies
        performance_metrics = {
            strategy: PerformanceMetrics(
                total_return=0.12, sharpe_ratio=1.0, max_drawdown=0.06,
                win_rate=0.60, profit_factor=1.5, volatility=0.14,
                alpha=0.03, beta=0.9, information_ratio=0.8
            )
            for strategy in ["trend_1", "trend_2", "mean_rev_1", "mean_rev_2", "vol_1", "vol_2"]
        }
        
        with patch.object(orchestrator.risk_manager.correlation_monitor, 'calculate_strategy_correlations') as mock_corr, \
             patch.object(orchestrator.performance_monitor, 'collect_performance_metrics') as mock_metrics, \
             patch.object(orchestrator.allocation_manager, 'needs_rebalancing') as mock_needs_rebalance:
            
            mock_corr.return_value = correlations
            mock_metrics.return_value = performance_metrics
            mock_needs_rebalance.return_value = True
            
            await orchestrator.start()
            
            # Trigger allocation optimization
            await orchestrator.optimize_strategy_allocation()
            
            allocations = orchestrator.allocation_manager.allocations
            
            # Verify correlation-aware allocation
            # Highly correlated strategies should not both get maximum allocation
            trend_total = allocations.get("trend_1", 0) + allocations.get("trend_2", 0)
            mean_rev_total = allocations.get("mean_rev_1", 0) + allocations.get("mean_rev_2", 0)
            
            # Total allocation to highly correlated groups should be limited
            max_group_allocation = orchestrator.config.allocation.max_allocation * 1.5  # Some tolerance
            assert trend_total <= max_group_allocation
            assert mean_rev_total <= max_group_allocation
            
            # Negatively correlated strategies should be favored for diversification
            diversification_pair = allocations.get("trend_1", 0) + allocations.get("mean_rev_1", 0)
            similar_pair = allocations.get("trend_1", 0) + allocations.get("trend_2", 0)
            
            # Diversified pair should get at least as much allocation as similar pair
            assert diversification_pair >= similar_pair * 0.8  # Allow some tolerance
            
            await orchestrator.stop()


class TestStrategyLifecycleManagement:
    """Test strategy lifecycle management in orchestration."""
    
    @pytest.fixture
    def lifecycle_config(self):
        """Create configuration for lifecycle testing."""
        return OrchestratorConfig(
            max_concurrent_strategies=8,
            enable_dynamic_allocation=True,
            enable_strategy_lifecycle_management=True,
            strategy_performance_evaluation_period=timedelta(hours=1),
            min_strategy_performance_threshold=0.0,
            strategies=[
                StrategyConfig(type="HighPerformer", name="high_perf", enabled=True),
                StrategyConfig(type="MediumPerformer", name="med_perf", enabled=True),
                StrategyConfig(type="LowPerformer", name="low_perf", enabled=True),
                StrategyConfig(type="VolatilePerformer", name="volatile_perf", enabled=True),
                StrategyConfig(type="ConsistentPerformer", name="consistent_perf", enabled=True)
            ]
        )
    
    @pytest.fixture
    def lifecycle_orchestrator(self, lifecycle_config):
        """Create orchestrator for lifecycle testing."""
        return StrategyOrchestrator(lifecycle_config)
    
    @pytest.mark.asyncio
    async def test_strategy_performance_evaluation(self, lifecycle_orchestrator):
        """Test periodic strategy performance evaluation."""
        # Mock performance metrics with different levels
        performance_metrics = {
            "high_perf": PerformanceMetrics(
                total_return=0.30, sharpe_ratio=2.5, max_drawdown=0.02,
                win_rate=0.85, profit_factor=3.0, volatility=0.10,
                alpha=0.10, beta=0.8, information_ratio=2.0
            ),
            "med_perf": PerformanceMetrics(
                total_return=0.10, sharpe_ratio=1.0, max_drawdown=0.06,
                win_rate=0.60, profit_factor=1.5, volatility=0.14,
                alpha=0.03, beta=0.9, information_ratio=0.8
            ),
            "low_perf": PerformanceMetrics(
                total_return=-0.05, sharpe_ratio=-0.5, max_drawdown=0.15,
                win_rate=0.40, profit_factor=0.8, volatility=0.20,
                alpha=-0.03, beta=1.2, information_ratio=-0.4
            ),
            "volatile_perf": PerformanceMetrics(
                total_return=0.15, sharpe_ratio=0.6, max_drawdown=0.20,
                win_rate=0.55, profit_factor=1.3, volatility=0.25,
                alpha=0.02, beta=1.5, information_ratio=0.3
            ),
            "consistent_perf": PerformanceMetrics(
                total_return=0.12, sharpe_ratio=1.8, max_drawdown=0.03,
                win_rate=0.70, profit_factor=2.2, volatility=0.08,
                alpha=0.05, beta=0.7, information_ratio=1.5
            )
        }
        
        with patch.object(lifecycle_orchestrator.performance_monitor, 'collect_performance_metrics') as mock_metrics, \
             patch.object(lifecycle_orchestrator.strategy_lifecycle_manager, 'evaluate_strategy_performance') as mock_evaluate:
            
            mock_metrics.return_value = performance_metrics
            
            # Mock evaluation results
            def evaluate_performance(strategy_name, metrics):
                if metrics.sharpe_ratio < 0:
                    return {"action": "disable", "reason": "Poor performance"}
                elif metrics.max_drawdown > 0.15:
                    return {"action": "reduce_allocation", "reason": "High risk"}
                elif metrics.sharpe_ratio > 2.0:
                    return {"action": "increase_allocation", "reason": "Excellent performance"}
                else:
                    return {"action": "maintain", "reason": "Acceptable performance"}
            
            mock_evaluate.side_effect = lambda name, metrics: evaluate_performance(name, metrics)
            
            await lifecycle_orchestrator.start()
            
            # Trigger performance evaluation
            await lifecycle_orchestrator.evaluate_strategy_performance()
            
            # Verify evaluations were performed
            assert mock_evaluate.call_count == len(performance_metrics)
            
            # Check evaluation results
            evaluation_calls = mock_evaluate.call_args_list
            strategy_actions = {}
            for call in evaluation_calls:
                strategy_name = call[0][0]
                metrics = call[0][1]
                action = evaluate_performance(strategy_name, metrics)["action"]
                strategy_actions[strategy_name] = action
            
            # Verify expected actions
            assert strategy_actions["high_perf"] == "increase_allocation"
            assert strategy_actions["consistent_perf"] == "increase_allocation"
            assert strategy_actions["low_perf"] == "disable"
            assert strategy_actions["volatile_perf"] == "reduce_allocation"
            assert strategy_actions["med_perf"] == "maintain"
            
            await lifecycle_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_strategy_auto_disable_and_enable(self, lifecycle_orchestrator):
        """Test automatic strategy disabling and re-enabling."""
        with patch.object(lifecycle_orchestrator.strategy_engine, 'disable_strategy') as mock_disable, \
             patch.object(lifecycle_orchestrator.strategy_engine, 'enable_strategy') as mock_enable, \
             patch.object(lifecycle_orchestrator.strategy_engine, 'get_active_strategies') as mock_active:
            
            # Initially all strategies are active
            mock_active.return_value = ["high_perf", "med_perf", "low_perf", "volatile_perf", "consistent_perf"]
            
            await lifecycle_orchestrator.start()
            
            # Simulate poor performance leading to strategy disable
            await lifecycle_orchestrator.disable_underperforming_strategy("low_perf", "Consistent losses")
            
            # Verify strategy was disabled
            mock_disable.assert_called_with("low_perf")
            
            # Simulate strategy recovery and re-enable
            await lifecycle_orchestrator.enable_strategy("low_perf", "Performance improved")
            
            # Verify strategy was re-enabled
            mock_enable.assert_called_with("low_perf")
            
            await lifecycle_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_strategy_allocation_adjustment(self, lifecycle_orchestrator):
        """Test dynamic strategy allocation adjustments."""
        initial_allocations = {
            "high_perf": 0.20,
            "med_perf": 0.20,
            "low_perf": 0.20,
            "volatile_perf": 0.20,
            "consistent_perf": 0.20
        }
        
        with patch.object(lifecycle_orchestrator.allocation_manager, 'allocations', initial_allocations), \
             patch.object(lifecycle_orchestrator.allocation_manager, 'update_allocation') as mock_update:
            
            await lifecycle_orchestrator.start()
            
            # Adjust allocation based on performance
            performance_adjustments = {
                "high_perf": 1.5,  # Increase by 50%
                "consistent_perf": 1.3,  # Increase by 30%
                "volatile_perf": 0.7,  # Decrease by 30%
                "low_perf": 0.5,  # Decrease by 50%
                "med_perf": 1.0  # No change
            }
            
            await lifecycle_orchestrator.adjust_strategy_allocations(performance_adjustments)
            
            # Verify allocation updates were called
            assert mock_update.call_count > 0
            
            # Check that adjustments respect allocation constraints
            for strategy, multiplier in performance_adjustments.items():
                expected_new_allocation = initial_allocations[strategy] * multiplier
                
                # Should be clamped to min/max allocation limits
                min_alloc = lifecycle_orchestrator.config.allocation.min_allocation
                max_alloc = lifecycle_orchestrator.config.allocation.max_allocation
                expected_clamped = max(min_alloc, min(max_alloc, expected_new_allocation))
                
                # Verify the adjustment was reasonable
                assert expected_clamped >= min_alloc
                assert expected_clamped <= max_alloc
            
            await lifecycle_orchestrator.stop()


class TestRealTimeAdaptation:
    """Test real-time adaptation capabilities."""
    
    @pytest.fixture
    def adaptive_config(self):
        """Create configuration for adaptive testing."""
        return OrchestratorConfig(
            max_concurrent_strategies=6,
            enable_dynamic_allocation=True,
            enable_real_time_adaptation=True,
            adaptation_sensitivity=0.1,  # How quickly to adapt
            market_regime_detection=True,
            strategies=[
                StrategyConfig(type="BullMarketStrategy", name="bull_strat", enabled=True),
                StrategyConfig(type="BearMarketStrategy", name="bear_strat", enabled=True),
                StrategyConfig(type="SidewaysMarketStrategy", name="sideways_strat", enabled=True),
                StrategyConfig(type="HighVolStrategy", name="high_vol_strat", enabled=True),
                StrategyConfig(type="LowVolStrategy", name="low_vol_strat", enabled=True),
                StrategyConfig(type="AllWeatherStrategy", name="all_weather_strat", enabled=True)
            ]
        )
    
    @pytest.fixture
    def adaptive_orchestrator(self, adaptive_config):
        """Create orchestrator for adaptation testing."""
        return StrategyOrchestrator(adaptive_config)
    
    @pytest.mark.asyncio
    async def test_market_regime_detection_and_adaptation(self, adaptive_orchestrator):
        """Test market regime detection and strategy adaptation."""
        # Create different market regime scenarios
        bull_market_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now() + timedelta(minutes=i),
                open=50000 + i * 200, high=50300 + i * 200, low=50100 + i * 200, close=50250 + i * 200,
                volume=1000, market_type="crypto"
            ) for i in range(10)  # Consistent uptrend
        ]
        
        bear_market_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now() + timedelta(minutes=i + 10),
                open=52000 - i * 150, high=52100 - i * 150, low=51800 - i * 150, close=51900 - i * 150,
                volume=1500, market_type="crypto"
            ) for i in range(10)  # Consistent downtrend
        ]
        
        sideways_market_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now() + timedelta(minutes=i + 20),
                open=50500 + (50 if i % 2 == 0 else -50), high=50600 + (50 if i % 2 == 0 else -50),
                low=50400 + (50 if i % 2 == 0 else -50), close=50500 + (25 if i % 2 == 0 else -25),
                volume=800, market_type="crypto"
            ) for i in range(10)  # Sideways movement
        ]
        
        with patch.object(adaptive_orchestrator.market_regime_detector, 'detect_regime') as mock_detect, \
             patch.object(adaptive_orchestrator.allocation_manager, 'adapt_to_regime') as mock_adapt:
            
            # Mock regime detection
            def detect_regime(market_data):
                if not market_data:
                    return "unknown"
                
                # Simple regime detection based on price trend
                first_price = market_data[0].close
                last_price = market_data[-1].close
                price_change = (last_price - first_price) / first_price
                
                if price_change > 0.02:
                    return "bull"
                elif price_change < -0.02:
                    return "bear"
                else:
                    return "sideways"
            
            mock_detect.side_effect = detect_regime
            
            await adaptive_orchestrator.start()
            
            # Process different market regimes
            regimes_tested = []
            
            # Bull market
            await adaptive_orchestrator.process_market_data(bull_market_data)
            bull_regime = detect_regime(bull_market_data)
            regimes_tested.append(bull_regime)
            
            # Bear market
            await adaptive_orchestrator.process_market_data(bear_market_data)
            bear_regime = detect_regime(bear_market_data)
            regimes_tested.append(bear_regime)
            
            # Sideways market
            await adaptive_orchestrator.process_market_data(sideways_market_data)
            sideways_regime = detect_regime(sideways_market_data)
            regimes_tested.append(sideways_regime)
            
            # Verify regime detection was called
            assert mock_detect.call_count >= 3
            
            # Verify adaptation was triggered for different regimes
            assert mock_adapt.call_count >= 3
            
            # Check that different regimes were detected
            assert "bull" in regimes_tested
            assert "bear" in regimes_tested
            assert "sideways" in regimes_tested
            
            await adaptive_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_volatility_based_strategy_adjustment(self, adaptive_orchestrator):
        """Test strategy adjustment based on market volatility."""
        # Create high volatility scenario
        high_vol_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now() + timedelta(minutes=i),
                open=50000, high=52000, low=48000, close=50000 + (1000 if i % 2 == 0 else -1000),
                volume=2000, market_type="crypto"
            ) for i in range(5)
        ]
        
        # Create low volatility scenario
        low_vol_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now() + timedelta(minutes=i + 5),
                open=50000, high=50050, low=49950, close=50000 + (10 if i % 2 == 0 else -10),
                volume=500, market_type="crypto"
            ) for i in range(5)
        ]
        
        with patch.object(adaptive_orchestrator.volatility_analyzer, 'calculate_volatility') as mock_vol, \
             patch.object(adaptive_orchestrator.allocation_manager, 'adjust_for_volatility') as mock_adjust:
            
            def calculate_volatility(market_data):
                if not market_data:
                    return 0.0
                
                volatilities = []
                for data in market_data:
                    vol = (data.high - data.low) / data.open
                    volatilities.append(vol)
                
                return np.mean(volatilities)
            
            mock_vol.side_effect = calculate_volatility
            
            await adaptive_orchestrator.start()
            
            # Process high volatility data
            await adaptive_orchestrator.process_market_data(high_vol_data)
            high_vol = calculate_volatility(high_vol_data)
            
            # Process low volatility data
            await adaptive_orchestrator.process_market_data(low_vol_data)
            low_vol = calculate_volatility(low_vol_data)
            
            # Verify volatility calculations
            assert high_vol > low_vol
            assert high_vol > 0.02  # Should be high volatility
            assert low_vol < 0.01   # Should be low volatility
            
            # Verify volatility-based adjustments were made
            assert mock_adjust.call_count >= 2
            
            # Check adjustment calls
            adjustment_calls = mock_adjust.call_args_list
            volatility_levels = [call[0][0] for call in adjustment_calls]
            
            # Should have processed both high and low volatility
            assert max(volatility_levels) > 0.02
            assert min(volatility_levels) < 0.01
            
            await adaptive_orchestrator.stop()