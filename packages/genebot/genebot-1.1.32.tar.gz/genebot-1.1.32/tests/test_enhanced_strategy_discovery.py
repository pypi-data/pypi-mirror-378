"""
Tests for enhanced strategy discovery and registration system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.orchestration.enhanced_strategy_registry import (
    EnhancedStrategyRegistry, StrategyMetadata, StrategyCapability, 
    MarketType, StrategyComplexity, StrategyCompatibility
)
from src.orchestration.strategy_lifecycle_manager import (
    StrategyLifecycleManager, StrategyState, HealthStatus, 
    StrategyHealthMetrics, PerformanceMetrics
)
from src.strategies.base_strategy import BaseStrategy, StrategyConfig
from src.models.data_models import MarketData, TradingSignal, SignalAction


class MockStrategy(BaseStrategy):
    """Mock strategy for testing."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self._initialized = False
        self._analysis_calls = 0
    
    def initialize(self) -> bool:
        self._initialized = True
        return True
    
    def analyze(self, market_data):
        self._analysis_calls += 1
        return None
    
    def get_required_data_length(self) -> int:
        return 10


class MockTrendStrategy(BaseStrategy):
    """Mock trend following strategy."""
    
    def initialize(self) -> bool:
        return True
    
    def analyze(self, market_data):
        return None
    
    def get_required_data_length(self) -> int:
        return 20


class MockArbitrageStrategy(BaseStrategy):
    """Mock arbitrage strategy."""
    
    def initialize(self) -> bool:
        return True
    
    def analyze(self, market_data):
        return None
    
    def get_required_data_length(self) -> int:
        return 5


@pytest.fixture
def enhanced_registry():
    """Create enhanced strategy registry for testing."""
    return EnhancedStrategyRegistry()


@pytest.fixture
def lifecycle_manager(enhanced_registry):
    """Create strategy lifecycle manager for testing."""
    return StrategyLifecycleManager(enhanced_registry)


@pytest.fixture
def mock_strategy():
    """Create mock strategy for testing."""
    config = StrategyConfig(name="test_strategy")
    return MockStrategy(config)


@pytest.fixture
def strategy_metadata():
    """Create strategy metadata for testing."""
    return StrategyMetadata(
        name="test_strategy",
        description="Test strategy for unit tests",
        capabilities={StrategyCapability.TREND_FOLLOWING, StrategyCapability.MOMENTUM},
        supported_markets={MarketType.CRYPTO, MarketType.FOREX},
        complexity=StrategyComplexity.INTERMEDIATE,
        min_data_points=10,
        risk_level="medium",
        expected_win_rate=0.6,
        tags={"test", "mock"}
    )


class TestEnhancedStrategyRegistry:
    """Test enhanced strategy registry functionality."""
    
    def test_register_strategy_with_metadata(self, enhanced_registry, mock_strategy, strategy_metadata):
        """Test registering strategy with metadata."""
        # Register strategy
        result = enhanced_registry.register_strategy(MockStrategy, "test_strategy", strategy_metadata)
        
        assert result is True
        assert "test_strategy" in enhanced_registry
        assert enhanced_registry.get_strategy_metadata("test_strategy") == strategy_metadata
    
    def test_register_strategy_auto_metadata_generation(self, enhanced_registry):
        """Test automatic metadata generation."""
        # Register strategy without metadata
        result = enhanced_registry.register_strategy(MockTrendStrategy, "trend_strategy")
        
        assert result is True
        metadata = enhanced_registry.get_strategy_metadata("trend_strategy")
        assert metadata is not None
        assert metadata.name == "trend_strategy"
        assert metadata.min_data_points == 20
    
    def test_capability_detection(self, enhanced_registry):
        """Test automatic capability detection."""
        # Register different strategy types
        enhanced_registry.register_strategy(MockTrendStrategy, "trend_strategy")
        enhanced_registry.register_strategy(MockArbitrageStrategy, "arbitrage_strategy")
        
        # Check trend strategy capabilities
        trend_metadata = enhanced_registry.get_strategy_metadata("trend_strategy")
        assert StrategyCapability.TREND_FOLLOWING in trend_metadata.capabilities
        
        # Check arbitrage strategy capabilities
        arbitrage_metadata = enhanced_registry.get_strategy_metadata("arbitrage_strategy")
        assert StrategyCapability.ARBITRAGE in arbitrage_metadata.capabilities
    
    def test_get_strategies_by_capability(self, enhanced_registry, strategy_metadata):
        """Test filtering strategies by capability."""
        # Register strategies with different capabilities
        enhanced_registry.register_strategy(MockStrategy, "test_strategy", strategy_metadata)
        enhanced_registry.register_strategy(MockTrendStrategy, "trend_strategy")
        
        # Get strategies by capability
        trend_strategies = enhanced_registry.get_strategies_by_capability(StrategyCapability.TREND_FOLLOWING)
        momentum_strategies = enhanced_registry.get_strategies_by_capability(StrategyCapability.MOMENTUM)
        
        assert "test_strategy" in trend_strategies
        assert "trend_strategy" in trend_strategies
        assert "test_strategy" in momentum_strategies
        assert "trend_strategy" not in momentum_strategies
    
    def test_get_strategies_by_market(self, enhanced_registry, strategy_metadata):
        """Test filtering strategies by market."""
        # Register strategy with specific market support
        enhanced_registry.register_strategy(MockStrategy, "test_strategy", strategy_metadata)
        
        # Get strategies by market
        crypto_strategies = enhanced_registry.get_strategies_by_market(MarketType.CRYPTO)
        forex_strategies = enhanced_registry.get_strategies_by_market(MarketType.FOREX)
        stocks_strategies = enhanced_registry.get_strategies_by_market(MarketType.STOCKS)
        
        assert "test_strategy" in crypto_strategies
        assert "test_strategy" in forex_strategies
        assert "test_strategy" not in stocks_strategies
    
    def test_strategy_compatibility_check(self, enhanced_registry):
        """Test strategy compatibility checking."""
        # Create compatible strategies
        metadata1 = StrategyMetadata(
            name="strategy1",
            description="First strategy",
            capabilities={StrategyCapability.TREND_FOLLOWING},
            supported_markets={MarketType.CRYPTO},
            risk_level="low"
        )
        
        metadata2 = StrategyMetadata(
            name="strategy2",
            description="Second strategy",
            capabilities={StrategyCapability.MEAN_REVERSION},
            supported_markets={MarketType.CRYPTO},
            risk_level="medium"
        )
        
        # Register strategies
        enhanced_registry.register_strategy(MockStrategy, "strategy1", metadata1)
        enhanced_registry.register_strategy(MockTrendStrategy, "strategy2", metadata2)
        
        # Check compatibility
        compatibility = enhanced_registry.check_strategy_compatibility("strategy1", "strategy2")
        
        assert compatibility.is_compatible is True
        assert compatibility.compatibility_score > 0.5
        assert "Good capability complementarity" in compatibility.reasons
    
    def test_incompatible_strategies(self, enhanced_registry):
        """Test detection of incompatible strategies."""
        # Create incompatible strategies (high overlap and high risk)
        metadata1 = StrategyMetadata(
            name="strategy1",
            description="First strategy",
            capabilities={StrategyCapability.TREND_FOLLOWING, StrategyCapability.MOMENTUM},
            supported_markets={MarketType.CRYPTO},
            risk_level="high",
            correlation_group="trend_group"
        )
        
        metadata2 = StrategyMetadata(
            name="strategy2",
            description="Second strategy",
            capabilities={StrategyCapability.TREND_FOLLOWING, StrategyCapability.MOMENTUM},
            supported_markets={MarketType.CRYPTO},
            risk_level="high",
            correlation_group="trend_group"
        )
        
        # Register strategies
        enhanced_registry.register_strategy(MockStrategy, "strategy1", metadata1)
        enhanced_registry.register_strategy(MockTrendStrategy, "strategy2", metadata2)
        
        # Check compatibility
        compatibility = enhanced_registry.check_strategy_compatibility("strategy1", "strategy2")
        
        assert compatibility.is_compatible is False
        assert compatibility.compatibility_score < 0.5
        assert len(compatibility.warnings) > 0
    
    def test_filter_strategies(self, enhanced_registry):
        """Test strategy filtering with multiple criteria."""
        # Create strategies with different characteristics
        metadata1 = StrategyMetadata(
            name="strategy1",
            description="Conservative crypto strategy",
            capabilities={StrategyCapability.TREND_FOLLOWING},
            supported_markets={MarketType.CRYPTO},
            complexity=StrategyComplexity.SIMPLE,
            expected_win_rate=0.7,
            risk_level="low",
            tags={"conservative", "crypto"}
        )
        
        metadata2 = StrategyMetadata(
            name="strategy2",
            description="Aggressive forex strategy",
            capabilities={StrategyCapability.ARBITRAGE},
            supported_markets={MarketType.FOREX},
            complexity=StrategyComplexity.ADVANCED,
            expected_win_rate=0.5,
            risk_level="high",
            tags={"aggressive", "forex"}
        )
        
        # Register strategies
        enhanced_registry.register_strategy(MockStrategy, "strategy1", metadata1)
        enhanced_registry.register_strategy(MockTrendStrategy, "strategy2", metadata2)
        
        # Filter by various criteria
        crypto_strategies = enhanced_registry.filter_strategies(
            markets={MarketType.CRYPTO}
        )
        assert "strategy1" in crypto_strategies
        assert "strategy2" not in crypto_strategies
        
        simple_strategies = enhanced_registry.filter_strategies(
            max_complexity=StrategyComplexity.INTERMEDIATE
        )
        assert "strategy1" in simple_strategies
        assert "strategy2" not in simple_strategies
        
        high_win_rate_strategies = enhanced_registry.filter_strategies(
            min_win_rate=0.6
        )
        assert "strategy1" in high_win_rate_strategies
        assert "strategy2" not in high_win_rate_strategies
        
        conservative_strategies = enhanced_registry.filter_strategies(
            tags={"conservative"}
        )
        assert "strategy1" in conservative_strategies
        assert "strategy2" not in conservative_strategies
    
    def test_get_compatible_strategies(self, enhanced_registry):
        """Test getting compatible strategies for a given strategy."""
        # Create strategies with varying compatibility
        metadata1 = StrategyMetadata(
            name="strategy1",
            description="Low risk trend strategy",
            capabilities={StrategyCapability.TREND_FOLLOWING},
            supported_markets={MarketType.CRYPTO},
            risk_level="low"
        )
        
        metadata2 = StrategyMetadata(
            name="strategy2",
            description="Mean reversion strategy",
            capabilities={StrategyCapability.MEAN_REVERSION},
            supported_markets={MarketType.CRYPTO},
            risk_level="medium"
        )
        
        metadata3 = StrategyMetadata(
            name="strategy3",
            description="High risk trend strategy",
            capabilities={StrategyCapability.TREND_FOLLOWING},
            supported_markets={MarketType.CRYPTO},
            risk_level="high",
            correlation_group="trend_group"
        )
        
        # Register strategies
        enhanced_registry.register_strategy(MockStrategy, "strategy1", metadata1)
        enhanced_registry.register_strategy(MockTrendStrategy, "strategy2", metadata2)
        enhanced_registry.register_strategy(MockArbitrageStrategy, "strategy3", metadata3)
        
        # Get compatible strategies
        compatible = enhanced_registry.get_compatible_strategies("strategy1", min_compatibility_score=0.7)
        
        assert "strategy2" in compatible  # Should be compatible (complementary)
        # strategy3 might still be compatible, so let's check with a higher threshold
        compatible_strict = enhanced_registry.get_compatible_strategies("strategy1", min_compatibility_score=0.8)
        assert "strategy3" not in compatible_strict  # Should be less compatible with stricter threshold
    
    def test_orchestration_summary(self, enhanced_registry):
        """Test orchestration summary generation."""
        # Register various strategies
        metadata1 = StrategyMetadata(
            name="strategy1",
            description="Simple crypto strategy",
            capabilities={StrategyCapability.TREND_FOLLOWING},
            supported_markets={MarketType.CRYPTO},
            complexity=StrategyComplexity.SIMPLE,
            risk_level="low"
        )
        
        metadata2 = StrategyMetadata(
            name="strategy2",
            description="Advanced forex strategy",
            capabilities={StrategyCapability.ARBITRAGE},
            supported_markets={MarketType.FOREX},
            complexity=StrategyComplexity.ADVANCED,
            risk_level="high"
        )
        
        enhanced_registry.register_strategy(MockStrategy, "strategy1", metadata1)
        enhanced_registry.register_strategy(MockTrendStrategy, "strategy2", metadata2)
        
        # Get orchestration summary
        summary = enhanced_registry.get_orchestration_summary()
        
        assert summary['total_strategies'] == 2
        assert summary['capabilities_distribution']['trend_following'] == 1
        assert summary['capabilities_distribution']['arbitrage'] == 1
        assert summary['market_distribution']['crypto'] == 1
        assert summary['market_distribution']['forex'] == 1
        assert summary['complexity_distribution']['simple'] == 1
        assert summary['complexity_distribution']['advanced'] == 1
        assert summary['risk_distribution']['low'] == 1
        assert summary['risk_distribution']['high'] == 1


class TestStrategyLifecycleManager:
    """Test strategy lifecycle manager functionality."""
    
    def test_register_strategy_for_lifecycle(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test registering strategy for lifecycle management."""
        result = lifecycle_manager.register_strategy_for_lifecycle(
            mock_strategy, strategy_metadata, allocation_weight=0.5, priority=2
        )
        
        assert result is True
        
        # Check strategy state
        state = lifecycle_manager.get_strategy_state("test_strategy")
        assert state == StrategyState.UNINITIALIZED
        
        # Check status
        status = lifecycle_manager.get_all_strategies_status()
        assert "test_strategy" in status
        assert status["test_strategy"]["allocation_weight"] == 0.5
        assert status["test_strategy"]["priority"] == 2
    
    def test_strategy_initialization(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test strategy initialization."""
        # Register strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        
        # Initialize strategy
        result = lifecycle_manager.initialize_strategy("test_strategy")
        assert result is True
        
        # Check state
        state = lifecycle_manager.get_strategy_state("test_strategy")
        assert state == StrategyState.READY
        
        # Check that strategy was actually initialized
        assert mock_strategy._initialized is True
    
    def test_strategy_start_stop(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test strategy start and stop."""
        # Register and initialize strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        lifecycle_manager.initialize_strategy("test_strategy")
        
        # Start strategy
        result = lifecycle_manager.start_strategy("test_strategy")
        assert result is True
        
        state = lifecycle_manager.get_strategy_state("test_strategy")
        assert state == StrategyState.RUNNING
        
        # Stop strategy
        result = lifecycle_manager.stop_strategy("test_strategy")
        assert result is True
        
        state = lifecycle_manager.get_strategy_state("test_strategy")
        assert state == StrategyState.STOPPED
    
    def test_strategy_pause_resume(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test strategy pause and resume."""
        # Register, initialize, and start strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        lifecycle_manager.initialize_strategy("test_strategy")
        lifecycle_manager.start_strategy("test_strategy")
        
        # Pause strategy
        result = lifecycle_manager.pause_strategy("test_strategy")
        assert result is True
        
        state = lifecycle_manager.get_strategy_state("test_strategy")
        assert state == StrategyState.PAUSED
        assert mock_strategy.enabled is False
        
        # Resume strategy
        result = lifecycle_manager.resume_strategy("test_strategy")
        assert result is True
        
        state = lifecycle_manager.get_strategy_state("test_strategy")
        assert state == StrategyState.RUNNING
        assert mock_strategy.enabled is True
    
    def test_strategy_restart(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test strategy restart."""
        # Register and start strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        lifecycle_manager.start_strategy("test_strategy")
        
        # Restart strategy
        result = lifecycle_manager.restart_strategy("test_strategy")
        assert result is True
        
        state = lifecycle_manager.get_strategy_state("test_strategy")
        assert state == StrategyState.RUNNING
        
        # Check restart count
        status = lifecycle_manager.get_all_strategies_status()
        assert status["test_strategy"]["restart_count"] == 1
    
    def test_strategy_restart_limits(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test strategy restart limits."""
        # Register strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        
        # Set low restart limit for testing
        with lifecycle_manager._state_lock:
            lifecycle_manager._strategies["test_strategy"].max_restarts = 1
        
        # Start strategy
        lifecycle_manager.start_strategy("test_strategy")
        
        # First restart should succeed
        result = lifecycle_manager.restart_strategy("test_strategy")
        assert result is True
        
        # Second restart should fail (exceeds limit)
        result = lifecycle_manager.restart_strategy("test_strategy")
        assert result is False
    
    def test_health_metrics_tracking(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test health metrics tracking."""
        # Register and start strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        lifecycle_manager.start_strategy("test_strategy")
        
        # Get initial health metrics
        health = lifecycle_manager.get_strategy_health("test_strategy")
        assert health is not None
        assert health.status == HealthStatus.UNKNOWN
        
        # Simulate some strategy activity
        mock_strategy.signals_generated = 10
        mock_strategy.successful_signals = 8
        
        # Update health metrics (simulate health check)
        with lifecycle_manager._state_lock:
            lifecycle_info = lifecycle_manager._strategies["test_strategy"]
            asyncio.run(lifecycle_manager._check_strategy_health("test_strategy", lifecycle_info))
        
        # Check updated health
        health = lifecycle_manager.get_strategy_health("test_strategy")
        assert health.signals_generated == 10
        assert health.successful_signals == 8
        assert health.failed_signals == 2
    
    def test_performance_metrics_tracking(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test performance metrics tracking."""
        # Register and start strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        lifecycle_manager.start_strategy("test_strategy")
        
        # Get initial performance metrics
        performance = lifecycle_manager.get_strategy_performance("test_strategy")
        assert performance is not None
        assert performance.trades_count == 0
        assert performance.win_rate == 0.0
        
        # Simulate strategy performance
        mock_strategy.signals_generated = 20
        mock_strategy.successful_signals = 15
        
        # Update performance metrics
        with lifecycle_manager._state_lock:
            lifecycle_info = lifecycle_manager._strategies["test_strategy"]
            asyncio.run(lifecycle_manager._update_strategy_performance("test_strategy", lifecycle_info))
        
        # Check updated performance
        performance = lifecycle_manager.get_strategy_performance("test_strategy")
        assert performance.trades_count == 20
        assert performance.winning_trades == 15
        assert performance.losing_trades == 5
        assert performance.win_rate == 0.75
    
    @pytest.mark.asyncio
    async def test_health_monitoring_loop(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test health monitoring loop."""
        # Register and start strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        lifecycle_manager.start_strategy("test_strategy")
        
        # Start health monitoring with short interval
        lifecycle_manager._health_check_interval = 0.1
        lifecycle_manager.start_health_monitoring()
        
        # Wait for a few health checks
        await asyncio.sleep(0.3)
        
        # Stop health monitoring
        lifecycle_manager.stop_health_monitoring()
        
        # Check that health was updated
        health = lifecycle_manager.get_strategy_health("test_strategy")
        assert health.last_health_check is not None
    
    def test_state_change_callbacks(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test state change callbacks."""
        callback_calls = []
        
        def state_change_callback(strategy_name, old_state, new_state):
            callback_calls.append((strategy_name, old_state, new_state))
        
        # Add callback
        lifecycle_manager.add_state_change_callback(state_change_callback)
        
        # Register and start strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        lifecycle_manager.start_strategy("test_strategy")
        
        # Check callback calls
        assert len(callback_calls) >= 3  # Registration, initialization, start
        assert callback_calls[-1] == ("test_strategy", StrategyState.STARTING, StrategyState.RUNNING)
    
    def test_unregister_strategy_cleanup(self, lifecycle_manager, mock_strategy, strategy_metadata):
        """Test proper cleanup when unregistering strategy."""
        # Register and start strategy
        lifecycle_manager.register_strategy_for_lifecycle(mock_strategy, strategy_metadata)
        lifecycle_manager.start_strategy("test_strategy")
        
        # Verify strategy is registered
        assert lifecycle_manager.get_strategy_state("test_strategy") == StrategyState.RUNNING
        
        # Unregister strategy
        result = lifecycle_manager.unregister_strategy_from_lifecycle("test_strategy")
        assert result is True
        
        # Verify strategy is cleaned up
        assert lifecycle_manager.get_strategy_state("test_strategy") is None
        
        status = lifecycle_manager.get_all_strategies_status()
        assert "test_strategy" not in status


@pytest.mark.integration
class TestIntegration:
    """Integration tests for enhanced strategy discovery system."""
    
    def test_full_discovery_and_lifecycle_integration(self):
        """Test full integration of discovery and lifecycle management."""
        # Create registry and lifecycle manager
        registry = EnhancedStrategyRegistry()
        lifecycle_manager = StrategyLifecycleManager(registry)
        
        # Register strategies in registry
        registry.register_strategy(MockTrendStrategy, "trend_strategy")
        registry.register_strategy(MockArbitrageStrategy, "arbitrage_strategy")
        
        # Create strategy instances
        trend_config = StrategyConfig(name="trend_instance")
        arbitrage_config = StrategyConfig(name="arbitrage_instance")
        
        trend_strategy = MockTrendStrategy(trend_config)
        arbitrage_strategy = MockArbitrageStrategy(arbitrage_config)
        
        # Register strategies for lifecycle management
        trend_metadata = registry.get_strategy_metadata("trend_strategy")
        arbitrage_metadata = registry.get_strategy_metadata("arbitrage_strategy")
        
        lifecycle_manager.register_strategy_for_lifecycle(trend_strategy, trend_metadata)
        lifecycle_manager.register_strategy_for_lifecycle(arbitrage_strategy, arbitrage_metadata)
        
        # Start strategies
        assert lifecycle_manager.start_strategy("trend_instance") is True
        assert lifecycle_manager.start_strategy("arbitrage_instance") is True
        
        # Check compatibility between strategies
        compatibility = registry.check_strategy_compatibility("trend_strategy", "arbitrage_strategy")
        assert compatibility.is_compatible is True  # Different capabilities should be compatible
        
        # Get orchestration summary
        summary = registry.get_orchestration_summary()
        assert summary['total_strategies'] == 2
        
        # Get all strategy status
        status = lifecycle_manager.get_all_strategies_status()
        assert len(status) == 2
        assert status["trend_instance"]["state"] == "running"
        assert status["arbitrage_instance"]["state"] == "running"
        
        # Clean up
        lifecycle_manager.stop_strategy("trend_instance")
        lifecycle_manager.stop_strategy("arbitrage_instance")


if __name__ == "__main__":
    pytest.main([__file__])