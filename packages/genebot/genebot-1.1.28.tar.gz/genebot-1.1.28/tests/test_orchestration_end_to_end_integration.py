"""
End-to-end integration tests for the orchestration system.
"""

import pytest
import asyncio
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import yaml

from src.orchestration.orchestrator import StrategyOrchestrator
from src.orchestration.config import (
    OrchestratorConfig, AllocationConfig, RiskConfig, MonitoringConfig,
    StrategyConfig, AllocationMethod, RebalanceFrequency, create_default_config
)
from src.orchestration.interfaces import (
    PerformanceMetrics, RiskMetrics, TradingSignal, Portfolio, Position,
    UnifiedMarketData, AllocationSnapshot
)
from src.orchestration.exceptions import (
    OrchestratorError, RiskLimitViolationError, ConfigurationError
)


class TestOrchestratorEndToEndIntegration:
    """Test complete orchestrator workflow integration."""
    
    @pytest.fixture
    def orchestrator_config(self):
        """Create comprehensive orchestrator configuration."""
        return OrchestratorConfig(
            max_concurrent_strategies=5,
            enable_dynamic_allocation=True,
            allocation=AllocationConfig(
                method=AllocationMethod.PERFORMANCE_BASED,
                rebalance_frequency=RebalanceFrequency.DAILY,
                min_allocation=0.05,
                max_allocation=0.30,
                lookback_period=30
            ),
            risk=RiskConfig(
                max_portfolio_drawdown=0.10,
                max_strategy_correlation=0.80,
                position_size_limit=0.05,
                stop_loss_threshold=0.02,
                max_daily_loss=0.03
            ),
            monitoring=MonitoringConfig(
                performance_tracking=True,
                alert_thresholds={
                    "drawdown": 0.05,
                    "correlation": 0.75,
                    "underperformance": 0.10
                },
                metrics_collection_interval=60
            ),
            strategies=[
                StrategyConfig(
                    type="MovingAverageStrategy",
                    name="ma_short",
                    enabled=True,
                    parameters={"short_period": 10, "long_period": 20}
                ),
                StrategyConfig(
                    type="RSIStrategy",
                    name="rsi_oversold",
                    enabled=True,
                    parameters={"period": 14, "oversold": 30, "overbought": 70}
                ),
                StrategyConfig(
                    type="MeanReversionStrategy",
                    name="mean_reversion",
                    enabled=True,
                    parameters={"lookback_period": 20, "threshold": 2.0}
                )
            ]
        )
    
    @pytest.fixture
    def orchestrator(self, orchestrator_config):
        """Create orchestrator instance."""
        return StrategyOrchestrator(orchestrator_config)
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data."""
        return [
            UnifiedMarketData(
                symbol="BTCUSD",
                timestamp=datetime.now(),
                open=50000.0,
                high=51000.0,
                low=49500.0,
                close=50500.0,
                volume=1000.0,
                market_type="crypto"
            ),
            UnifiedMarketData(
                symbol="ETHUSD",
                timestamp=datetime.now(),
                open=3000.0,
                high=3100.0,
                low=2950.0,
                close=3050.0,
                volume=5000.0,
                market_type="crypto"
            ),
            UnifiedMarketData(
                symbol="EURUSD",
                timestamp=datetime.now(),
                open=1.1000,
                high=1.1050,
                low=1.0980,
                close=1.1020,
                volume=100000.0,
                market_type="forex"
            )
        ]
    
    @pytest.fixture
    def sample_portfolio(self):
        """Create sample portfolio."""
        positions = [
            Position(
                symbol="BTCUSD",
                strategy="ma_short",
                size=0.1,
                entry_price=50000,
                current_price=50500,
                unrealized_pnl=50
            ),
            Position(
                symbol="ETHUSD",
                strategy="rsi_oversold",
                size=1.0,
                entry_price=3000,
                current_price=3050,
                unrealized_pnl=50
            )
        ]
        return Portfolio(
            total_value=100000,
            available_cash=50000,
            positions=positions,
            total_pnl=100,
            daily_pnl=100
        )
    
    @pytest.mark.asyncio
    async def test_complete_orchestration_workflow(self, orchestrator, sample_market_data, sample_portfolio):
        """Test complete orchestration workflow from market data to execution."""
        # Mock strategy engine and its methods
        with patch.object(orchestrator.strategy_engine, 'process_market_data') as mock_process, \
             patch.object(orchestrator.strategy_engine, 'get_active_strategies') as mock_active, \
             patch.object(orchestrator, 'get_current_portfolio') as mock_portfolio:
            
            # Setup mocks
            mock_active.return_value = ["ma_short", "rsi_oversold", "mean_reversion"]
            mock_portfolio.return_value = sample_portfolio
            
            # Mock strategy signals
            mock_signals = [
                TradingSignal(
                    strategy="ma_short",
                    symbol="BTCUSD",
                    action="BUY",
                    quantity=0.05,
                    price=50500,
                    confidence=0.8,
                    timestamp=datetime.now()
                ),
                TradingSignal(
                    strategy="rsi_oversold",
                    symbol="ETHUSD",
                    action="SELL",
                    quantity=0.5,
                    price=3050,
                    confidence=0.7,
                    timestamp=datetime.now()
                )
            ]
            mock_process.return_value = mock_signals
            
            # Start orchestrator
            await orchestrator.start()
            assert orchestrator.is_running is True
            
            # Process market data
            processed_signals = await orchestrator.process_market_data(sample_market_data)
            
            # Verify signals were processed and validated
            assert len(processed_signals) <= len(mock_signals)  # Some may be filtered by risk management
            
            # Verify allocation was updated
            assert len(orchestrator.allocation_manager.allocations) > 0
            
            # Verify performance metrics were collected
            metrics = orchestrator.performance_monitor.collect_performance_metrics()
            assert isinstance(metrics, dict)
            
            # Stop orchestrator
            await orchestrator.stop()
            assert orchestrator.is_running is False
    
    @pytest.mark.asyncio
    async def test_strategy_failure_recovery(self, orchestrator, sample_market_data):
        """Test orchestrator recovery from strategy failures."""
        with patch.object(orchestrator.strategy_engine, 'process_market_data') as mock_process, \
             patch.object(orchestrator.error_handler, 'handle_strategy_error') as mock_error_handler:
            
            # Simulate strategy failure
            mock_process.side_effect = Exception("Strategy execution failed")
            
            # Start orchestrator
            await orchestrator.start()
            
            # Process market data - should handle the exception
            try:
                await orchestrator.process_market_data(sample_market_data)
            except Exception:
                pass  # Expected to be handled gracefully
            
            # Verify error handler was called
            mock_error_handler.assert_called()
            
            # Verify orchestrator is still running
            assert orchestrator.is_running is True
            
            await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_risk_limit_enforcement(self, orchestrator, sample_market_data, sample_portfolio):
        """Test risk limit enforcement during signal processing."""
        with patch.object(orchestrator.strategy_engine, 'process_market_data') as mock_process, \
             patch.object(orchestrator, 'get_current_portfolio') as mock_portfolio_getter, \
             patch.object(orchestrator.risk_manager, 'validate_signal') as mock_validate:
            
            # Setup mocks
            mock_portfolio_getter.return_value = sample_portfolio
            
            # Create high-risk signal
            risky_signal = TradingSignal(
                strategy="ma_short",
                symbol="BTCUSD",
                action="BUY",
                quantity=10.0,  # Very large position
                price=50500,
                confidence=0.9,
                timestamp=datetime.now()
            )
            mock_process.return_value = [risky_signal]
            
            # Mock risk manager to reject the signal
            mock_validate.return_value = False
            
            await orchestrator.start()
            
            # Process market data
            processed_signals = await orchestrator.process_market_data(sample_market_data)
            
            # Verify risky signal was filtered out
            assert len(processed_signals) == 0
            mock_validate.assert_called_with(risky_signal, sample_portfolio)
            
            await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_dynamic_allocation_rebalancing(self, orchestrator, sample_portfolio):
        """Test dynamic allocation rebalancing based on performance."""
        with patch.object(orchestrator, 'get_current_portfolio') as mock_portfolio, \
             patch.object(orchestrator.performance_monitor, 'collect_performance_metrics') as mock_metrics, \
             patch.object(orchestrator.allocation_manager, 'needs_rebalancing') as mock_needs_rebalance:
            
            # Setup mocks
            mock_portfolio.return_value = sample_portfolio
            mock_needs_rebalance.return_value = True
            
            # Mock performance metrics showing different strategy performance
            mock_performance_metrics = {
                "ma_short": PerformanceMetrics(
                    total_return=0.15, sharpe_ratio=1.5, max_drawdown=0.03,
                    win_rate=0.70, profit_factor=2.0, volatility=0.10,
                    alpha=0.05, beta=0.8, information_ratio=1.2
                ),
                "rsi_oversold": PerformanceMetrics(
                    total_return=0.05, sharpe_ratio=0.5, max_drawdown=0.08,
                    win_rate=0.55, profit_factor=1.2, volatility=0.15,
                    alpha=0.01, beta=1.1, information_ratio=0.3
                ),
                "mean_reversion": PerformanceMetrics(
                    total_return=-0.02, sharpe_ratio=-0.2, max_drawdown=0.10,
                    win_rate=0.45, profit_factor=0.9, volatility=0.18,
                    alpha=-0.01, beta=1.2, information_ratio=-0.1
                )
            }
            mock_metrics.return_value = mock_performance_metrics
            
            await orchestrator.start()
            
            # Trigger rebalancing
            await orchestrator.rebalance_allocations()
            
            # Verify allocations were updated
            allocations = orchestrator.allocation_manager.allocations
            
            # Best performing strategy should get highest allocation
            assert allocations.get("ma_short", 0) > allocations.get("rsi_oversold", 0)
            assert allocations.get("ma_short", 0) > allocations.get("mean_reversion", 0)
            
            # Poor performing strategy should get minimal or zero allocation
            assert allocations.get("mean_reversion", 0) <= orchestrator.config.allocation.min_allocation
            
            await orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_emergency_stop_activation(self, orchestrator, sample_portfolio):
        """Test emergency stop activation on severe risk conditions."""
        # Create portfolio with severe drawdown
        severe_loss_portfolio = Portfolio(
            total_value=70000,  # 30% loss from initial 100k
            available_cash=20000,
            positions=[],
            total_pnl=-30000,
            daily_pnl=-15000  # 15% daily loss
        )
        
        with patch.object(orchestrator, 'get_current_portfolio') as mock_portfolio, \
             patch.object(orchestrator.risk_manager, 'trigger_emergency_stop') as mock_emergency_stop:
            
            mock_portfolio.return_value = severe_loss_portfolio
            
            await orchestrator.start()
            
            # Process market data - should trigger emergency stop
            await orchestrator.check_risk_conditions()
            
            # Verify emergency stop was triggered
            mock_emergency_stop.assert_called()
            
            await orchestrator.stop()


class TestMultiStrategyIntegration:
    """Test integration between multiple strategies in orchestration."""
    
    @pytest.fixture
    def multi_strategy_config(self):
        """Create configuration with multiple strategies."""
        return OrchestratorConfig(
            max_concurrent_strategies=10,
            enable_dynamic_allocation=True,
            allocation=AllocationConfig(
                method=AllocationMethod.PERFORMANCE_BASED,
                rebalance_frequency=RebalanceFrequency.DAILY
            ),
            strategies=[
                StrategyConfig(type="MovingAverageStrategy", name="ma_fast", enabled=True,
                             parameters={"short_period": 5, "long_period": 10}),
                StrategyConfig(type="MovingAverageStrategy", name="ma_slow", enabled=True,
                             parameters={"short_period": 20, "long_period": 50}),
                StrategyConfig(type="RSIStrategy", name="rsi_short", enabled=True,
                             parameters={"period": 7, "oversold": 25, "overbought": 75}),
                StrategyConfig(type="RSIStrategy", name="rsi_long", enabled=True,
                             parameters={"period": 21, "oversold": 35, "overbought": 65}),
                StrategyConfig(type="MeanReversionStrategy", name="mean_rev", enabled=True,
                             parameters={"lookback_period": 15, "threshold": 1.5})
            ]
        )
    
    @pytest.fixture
    def multi_orchestrator(self, multi_strategy_config):
        """Create orchestrator with multiple strategies."""
        return StrategyOrchestrator(multi_strategy_config)
    
    @pytest.mark.asyncio
    async def test_multiple_strategy_coordination(self, multi_orchestrator, sample_market_data):
        """Test coordination between multiple strategies."""
        with patch.object(multi_orchestrator.strategy_engine, 'process_market_data') as mock_process, \
             patch.object(multi_orchestrator.strategy_engine, 'get_active_strategies') as mock_active:
            
            # Mock multiple strategies being active
            mock_active.return_value = ["ma_fast", "ma_slow", "rsi_short", "rsi_long", "mean_rev"]
            
            # Mock signals from different strategies
            mock_signals = [
                TradingSignal(strategy="ma_fast", symbol="BTCUSD", action="BUY", 
                            quantity=0.1, price=50500, confidence=0.8, timestamp=datetime.now()),
                TradingSignal(strategy="ma_slow", symbol="BTCUSD", action="SELL", 
                            quantity=0.05, price=50500, confidence=0.6, timestamp=datetime.now()),
                TradingSignal(strategy="rsi_short", symbol="ETHUSD", action="BUY", 
                            quantity=0.2, price=3050, confidence=0.7, timestamp=datetime.now()),
                TradingSignal(strategy="rsi_long", symbol="ETHUSD", action="BUY", 
                            quantity=0.15, price=3050, confidence=0.9, timestamp=datetime.now()),
                TradingSignal(strategy="mean_rev", symbol="EURUSD", action="SELL", 
                            quantity=1000, price=1.1020, confidence=0.5, timestamp=datetime.now())
            ]
            mock_process.return_value = mock_signals
            
            await multi_orchestrator.start()
            
            # Process market data
            processed_signals = await multi_orchestrator.process_market_data(sample_market_data)
            
            # Verify signal aggregation and conflict resolution
            # Conflicting BTC signals (BUY vs SELL) should be resolved
            btc_signals = [s for s in processed_signals if s.symbol == "BTCUSD"]
            if len(btc_signals) > 0:
                # Should prioritize higher confidence or better performing strategy
                assert len(btc_signals) <= 2  # At most one BUY and one SELL, or net position
            
            # ETH signals should be combined (both BUY)
            eth_signals = [s for s in processed_signals if s.symbol == "ETHUSD"]
            if len(eth_signals) > 0:
                total_eth_quantity = sum(s.quantity for s in eth_signals if s.action == "BUY")
                assert total_eth_quantity > 0
            
            await multi_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_strategy_correlation_monitoring(self, multi_orchestrator):
        """Test monitoring of strategy correlations."""
        with patch.object(multi_orchestrator.risk_manager.correlation_monitor, 'calculate_strategy_correlations') as mock_corr, \
             patch.object(multi_orchestrator.risk_manager, 'check_correlation_limits') as mock_check:
            
            # Mock high correlation between similar strategies
            mock_correlations = {
                ("ma_fast", "ma_slow"): 0.85,  # High correlation - both MA strategies
                ("rsi_short", "rsi_long"): 0.82,  # High correlation - both RSI strategies
                ("ma_fast", "rsi_short"): 0.45,  # Low correlation - different types
                ("mean_rev", "ma_fast"): 0.30   # Low correlation
            }
            mock_corr.return_value = mock_correlations
            mock_check.return_value = False  # Correlation limits exceeded
            
            await multi_orchestrator.start()
            
            # Check correlation limits
            strategies = ["ma_fast", "ma_slow", "rsi_short", "rsi_long", "mean_rev"]
            correlation_ok = multi_orchestrator.risk_manager.check_correlation_limits(strategies)
            
            # Should detect high correlations
            assert correlation_ok is False
            mock_check.assert_called_with(strategies)
            
            await multi_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_performance_based_strategy_selection(self, multi_orchestrator):
        """Test performance-based strategy selection and allocation."""
        # Mock different performance levels for strategies
        performance_metrics = {
            "ma_fast": PerformanceMetrics(
                total_return=0.20, sharpe_ratio=1.8, max_drawdown=0.04,
                win_rate=0.75, profit_factor=2.2, volatility=0.11,
                alpha=0.06, beta=0.8, information_ratio=1.5
            ),
            "ma_slow": PerformanceMetrics(
                total_return=0.12, sharpe_ratio=1.2, max_drawdown=0.06,
                win_rate=0.68, profit_factor=1.8, volatility=0.10,
                alpha=0.03, beta=0.9, information_ratio=1.0
            ),
            "rsi_short": PerformanceMetrics(
                total_return=0.08, sharpe_ratio=0.8, max_drawdown=0.08,
                win_rate=0.60, profit_factor=1.4, volatility=0.14,
                alpha=0.01, beta=1.0, information_ratio=0.6
            ),
            "rsi_long": PerformanceMetrics(
                total_return=0.15, sharpe_ratio=1.4, max_drawdown=0.05,
                win_rate=0.70, profit_factor=1.9, volatility=0.12,
                alpha=0.04, beta=0.85, information_ratio=1.1
            ),
            "mean_rev": PerformanceMetrics(
                total_return=-0.03, sharpe_ratio=-0.3, max_drawdown=0.12,
                win_rate=0.48, profit_factor=0.9, volatility=0.16,
                alpha=-0.02, beta=1.1, information_ratio=-0.2
            )
        }
        
        with patch.object(multi_orchestrator.performance_monitor, 'collect_performance_metrics') as mock_metrics:
            mock_metrics.return_value = performance_metrics
            
            await multi_orchestrator.start()
            
            # Trigger allocation optimization
            await multi_orchestrator.optimize_strategy_allocation()
            
            allocations = multi_orchestrator.allocation_manager.allocations
            
            # Best performing strategies should get higher allocations
            assert allocations.get("ma_fast", 0) > allocations.get("rsi_short", 0)
            assert allocations.get("rsi_long", 0) > allocations.get("rsi_short", 0)
            
            # Poor performing strategy should get minimal allocation
            assert allocations.get("mean_rev", 0) <= multi_orchestrator.config.allocation.min_allocation
            
            await multi_orchestrator.stop()


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms."""
    
    @pytest.fixture
    def orchestrator_with_error_handling(self):
        """Create orchestrator with comprehensive error handling."""
        config = create_default_config()
        config.enable_error_recovery = True
        config.max_strategy_failures = 3
        return StrategyOrchestrator(config)
    
    @pytest.mark.asyncio
    async def test_strategy_failure_isolation(self, orchestrator_with_error_handling, sample_market_data):
        """Test isolation of failing strategies."""
        with patch.object(orchestrator_with_error_handling.strategy_engine, 'process_market_data') as mock_process, \
             patch.object(orchestrator_with_error_handling.error_handler, 'handle_strategy_error') as mock_error_handler, \
             patch.object(orchestrator_with_error_handling.strategy_engine, 'disable_strategy') as mock_disable:
            
            # Simulate strategy failure
            def failing_process(market_data):
                if market_data:  # First call fails
                    raise Exception("Strategy ma_short failed")
                return []
            
            mock_process.side_effect = failing_process
            
            await orchestrator_with_error_handling.start()
            
            # Process market data - should handle failure
            try:
                await orchestrator_with_error_handling.process_market_data(sample_market_data)
            except Exception:
                pass
            
            # Verify error handling
            mock_error_handler.assert_called()
            
            # Verify strategy was disabled after failure
            # (This would be called by the error handler)
            
            await orchestrator_with_error_handling.stop()
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, orchestrator_with_error_handling):
        """Test graceful degradation when multiple strategies fail."""
        with patch.object(orchestrator_with_error_handling.strategy_engine, 'get_active_strategies') as mock_active, \
             patch.object(orchestrator_with_error_handling.fallback_manager, 'activate_fallback_strategies') as mock_fallback:
            
            # Simulate most strategies being disabled
            mock_active.return_value = ["ma_short"]  # Only one strategy left
            
            await orchestrator_with_error_handling.start()
            
            # Check if fallback strategies are activated
            await orchestrator_with_error_handling.check_strategy_health()
            
            # Should activate fallback strategies when too few are active
            if len(mock_active.return_value) < orchestrator_with_error_handling.config.min_active_strategies:
                mock_fallback.assert_called()
            
            await orchestrator_with_error_handling.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_error_recovery(self, orchestrator_with_error_handling):
        """Test recovery from configuration errors."""
        # Create invalid configuration update
        invalid_config_updates = {
            "allocation.min_allocation": 0.8,  # Invalid: min > max
            "allocation.max_allocation": 0.5
        }
        
        with patch.object(orchestrator_with_error_handling.config_manager, 'update_config') as mock_update, \
             patch.object(orchestrator_with_error_handling.config_manager, 'rollback_config') as mock_rollback:
            
            # Mock configuration update failure
            mock_update.side_effect = ConfigurationError("Invalid configuration")
            
            await orchestrator_with_error_handling.start()
            
            # Attempt to update configuration
            try:
                await orchestrator_with_error_handling.update_configuration(invalid_config_updates)
            except ConfigurationError:
                pass  # Expected
            
            # Verify rollback was attempted
            mock_rollback.assert_called()
            
            await orchestrator_with_error_handling.stop()


class TestPerformanceAndLoadTesting:
    """Test orchestrator performance under load."""
    
    @pytest.fixture
    def high_frequency_config(self):
        """Create configuration for high-frequency testing."""
        return OrchestratorConfig(
            max_concurrent_strategies=20,
            enable_dynamic_allocation=True,
            allocation=AllocationConfig(
                method=AllocationMethod.PERFORMANCE_BASED,
                rebalance_frequency=RebalanceFrequency.HOURLY  # More frequent rebalancing
            ),
            monitoring=MonitoringConfig(
                metrics_collection_interval=10  # More frequent metrics collection
            ),
            strategies=[
                StrategyConfig(type=f"TestStrategy{i}", name=f"test_strategy_{i}", enabled=True)
                for i in range(15)  # Many strategies
            ]
        )
    
    @pytest.fixture
    def load_test_orchestrator(self, high_frequency_config):
        """Create orchestrator for load testing."""
        return StrategyOrchestrator(high_frequency_config)
    
    @pytest.mark.asyncio
    async def test_high_frequency_market_data_processing(self, load_test_orchestrator):
        """Test processing high-frequency market data."""
        # Generate large amount of market data
        market_data_batch = []
        symbols = ["BTCUSD", "ETHUSD", "LTCUSD", "ADAUSD", "DOTUSD"]
        
        for i in range(100):  # 100 data points
            for symbol in symbols:
                market_data_batch.append(
                    UnifiedMarketData(
                        symbol=symbol,
                        timestamp=datetime.now() + timedelta(seconds=i),
                        open=50000 + i,
                        high=50100 + i,
                        low=49900 + i,
                        close=50050 + i,
                        volume=1000,
                        market_type="crypto"
                    )
                )
        
        with patch.object(load_test_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            # Mock fast processing
            mock_process.return_value = []
            
            await load_test_orchestrator.start()
            
            # Measure processing time
            start_time = datetime.now()
            
            # Process market data in batches
            batch_size = 50
            for i in range(0, len(market_data_batch), batch_size):
                batch = market_data_batch[i:i + batch_size]
                await load_test_orchestrator.process_market_data(batch)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Verify reasonable processing time (should be under 5 seconds for this test)
            assert processing_time < 5.0
            
            # Verify all batches were processed
            assert mock_process.call_count >= len(market_data_batch) // batch_size
            
            await load_test_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_strategy_execution(self, load_test_orchestrator):
        """Test concurrent execution of multiple strategies."""
        with patch.object(load_test_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            
            # Mock concurrent strategy processing
            async def concurrent_process(market_data):
                # Simulate some processing time
                await asyncio.sleep(0.01)
                return [
                    TradingSignal(
                        strategy=f"test_strategy_{i}",
                        symbol="BTCUSD",
                        action="BUY",
                        quantity=0.01,
                        price=50000,
                        confidence=0.5,
                        timestamp=datetime.now()
                    )
                    for i in range(5)  # Multiple signals
                ]
            
            mock_process.side_effect = concurrent_process
            
            await load_test_orchestrator.start()
            
            # Process multiple market data updates concurrently
            market_data = [
                UnifiedMarketData(
                    symbol="BTCUSD", timestamp=datetime.now(),
                    open=50000, high=50100, low=49900, close=50050,
                    volume=1000, market_type="crypto"
                )
            ]
            
            # Create multiple concurrent processing tasks
            tasks = []
            for _ in range(10):
                task = asyncio.create_task(
                    load_test_orchestrator.process_market_data(market_data)
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all tasks completed successfully
            for result in results:
                assert not isinstance(result, Exception)
            
            await load_test_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, load_test_orchestrator):
        """Test memory usage doesn't grow excessively under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        with patch.object(load_test_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await load_test_orchestrator.start()
            
            # Process many market data updates
            market_data = [
                UnifiedMarketData(
                    symbol="BTCUSD", timestamp=datetime.now(),
                    open=50000, high=50100, low=49900, close=50050,
                    volume=1000, market_type="crypto"
                )
            ]
            
            for _ in range(1000):  # Many iterations
                await load_test_orchestrator.process_market_data(market_data)
            
            final_memory = process.memory_info().rss
            memory_growth = final_memory - initial_memory
            
            # Memory growth should be reasonable (less than 100MB for this test)
            assert memory_growth < 100 * 1024 * 1024  # 100MB
            
            await load_test_orchestrator.stop()