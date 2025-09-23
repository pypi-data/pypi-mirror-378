"""
Example demonstrating the enhanced strategy discovery and lifecycle management system.
"""

import asyncio
import logging
from datetime import datetime

from src.orchestration.enhanced_strategy_registry import (
    EnhancedStrategyRegistry, StrategyMetadata, StrategyCapability, 
    MarketType, StrategyComplexity
)
from src.orchestration.strategy_lifecycle_manager import (
    StrategyLifecycleManager, StrategyState, HealthStatus
)
from src.strategies.base_strategy import BaseStrategy, StrategyConfig
from src.models.data_models import MarketData, TradingSignal, SignalAction


# Example strategy implementations
class TrendFollowingStrategy(BaseStrategy):
    """Example trend following strategy."""
    
    def initialize(self) -> bool:
        self.logger.info(f"Initializing {self.name}")
        return True
    
    def analyze(self, market_data):
        # Simple trend following logic
        if len(market_data) >= 2:
            current_price = float(market_data[-1].close)
            previous_price = float(market_data[-2].close)
            
            if current_price > previous_price * 1.01:  # 1% increase
                return TradingSignal(
                    symbol=market_data[-1].symbol,
                    action=SignalAction.BUY,
                    confidence=0.7,
                    timestamp=market_data[-1].timestamp,
                    strategy_name=self.name,
                    price=market_data[-1].close
                )
        return None
    
    def get_required_data_length(self) -> int:
        return 20


class MeanReversionStrategy(BaseStrategy):
    """Example mean reversion strategy."""
    
    def initialize(self) -> bool:
        self.logger.info(f"Initializing {self.name}")
        return True
    
    def analyze(self, market_data):
        # Simple mean reversion logic
        if len(market_data) >= 10:
            prices = [float(data.close) for data in market_data[-10:]]
            avg_price = sum(prices) / len(prices)
            current_price = prices[-1]
            
            if current_price < avg_price * 0.95:  # 5% below average
                return TradingSignal(
                    symbol=market_data[-1].symbol,
                    action=SignalAction.BUY,
                    confidence=0.6,
                    timestamp=market_data[-1].timestamp,
                    strategy_name=self.name,
                    price=market_data[-1].close
                )
        return None
    
    def get_required_data_length(self) -> int:
        return 10


class ArbitrageStrategy(BaseStrategy):
    """Example arbitrage strategy."""
    
    def initialize(self) -> bool:
        self.logger.info(f"Initializing {self.name}")
        return True
    
    def analyze(self, market_data):
        # Simple arbitrage logic (placeholder)
        return None
    
    def get_required_data_length(self) -> int:
        return 5


async def main():
    """Main example function."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=== Enhanced Strategy Discovery Example ===")
    
    # Create enhanced registry and lifecycle manager
    registry = EnhancedStrategyRegistry()
    lifecycle_manager = StrategyLifecycleManager(registry)
    
    # Register strategies with automatic metadata generation
    logger.info("\n1. Registering strategies with automatic metadata generation...")
    
    registry.register_strategy(TrendFollowingStrategy, "trend_strategy")
    registry.register_strategy(MeanReversionStrategy, "mean_reversion_strategy")
    registry.register_strategy(ArbitrageStrategy, "arbitrage_strategy")
    
    # Display discovered capabilities
    logger.info("\n2. Discovered strategy capabilities:")
    for strategy_name in registry.get_registered_strategies():
        metadata = registry.get_strategy_metadata(strategy_name)
        logger.info(f"  {strategy_name}:")
        logger.info(f"    Capabilities: {[cap.value for cap in metadata.capabilities]}")
        logger.info(f"    Markets: {[market.value for market in metadata.supported_markets]}")
        logger.info(f"    Complexity: {metadata.complexity.value}")
        logger.info(f"    Risk Level: {metadata.risk_level}")
    
    # Filter strategies by capability
    logger.info("\n3. Filtering strategies by capability:")
    
    trend_strategies = registry.get_strategies_by_capability(StrategyCapability.TREND_FOLLOWING)
    logger.info(f"  Trend following strategies: {trend_strategies}")
    
    mean_reversion_strategies = registry.get_strategies_by_capability(StrategyCapability.MEAN_REVERSION)
    logger.info(f"  Mean reversion strategies: {mean_reversion_strategies}")
    
    arbitrage_strategies = registry.get_strategies_by_capability(StrategyCapability.ARBITRAGE)
    logger.info(f"  Arbitrage strategies: {arbitrage_strategies}")
    
    # Check strategy compatibility
    logger.info("\n4. Checking strategy compatibility:")
    
    compatibility = registry.check_strategy_compatibility("trend_strategy", "mean_reversion_strategy")
    logger.info(f"  Trend vs Mean Reversion compatibility:")
    logger.info(f"    Compatible: {compatibility.is_compatible}")
    logger.info(f"    Score: {compatibility.compatibility_score:.2f}")
    logger.info(f"    Reasons: {compatibility.reasons}")
    
    # Get compatible strategies
    compatible_strategies = registry.get_compatible_strategies("trend_strategy", min_compatibility_score=0.7)
    logger.info(f"  Strategies compatible with trend_strategy: {compatible_strategies}")
    
    # Create strategy instances for lifecycle management
    logger.info("\n5. Creating strategy instances for lifecycle management...")
    
    trend_config = StrategyConfig(name="trend_instance", parameters={"lookback": 20})
    mean_reversion_config = StrategyConfig(name="mean_reversion_instance", parameters={"window": 10})
    arbitrage_config = StrategyConfig(name="arbitrage_instance")
    
    trend_instance = TrendFollowingStrategy(trend_config)
    mean_reversion_instance = MeanReversionStrategy(mean_reversion_config)
    arbitrage_instance = ArbitrageStrategy(arbitrage_config)
    
    # Register strategies for lifecycle management
    trend_metadata = registry.get_strategy_metadata("trend_strategy")
    mean_reversion_metadata = registry.get_strategy_metadata("mean_reversion_strategy")
    arbitrage_metadata = registry.get_strategy_metadata("arbitrage_strategy")
    
    lifecycle_manager.register_strategy_for_lifecycle(
        trend_instance, trend_metadata, allocation_weight=0.4, priority=1
    )
    lifecycle_manager.register_strategy_for_lifecycle(
        mean_reversion_instance, mean_reversion_metadata, allocation_weight=0.3, priority=2
    )
    lifecycle_manager.register_strategy_for_lifecycle(
        arbitrage_instance, arbitrage_metadata, allocation_weight=0.3, priority=3
    )
    
    # Start strategies
    logger.info("\n6. Starting strategies...")
    
    lifecycle_manager.start_strategy("trend_instance")
    lifecycle_manager.start_strategy("mean_reversion_instance")
    lifecycle_manager.start_strategy("arbitrage_instance")
    
    # Display strategy status
    logger.info("\n7. Strategy status:")
    status = lifecycle_manager.get_all_strategies_status()
    for name, info in status.items():
        logger.info(f"  {name}:")
        logger.info(f"    State: {info['state']}")
        logger.info(f"    Health: {info['health_status']}")
        logger.info(f"    Weight: {info['allocation_weight']}")
        logger.info(f"    Priority: {info['priority']}")
    
    # Start health monitoring
    logger.info("\n8. Starting health monitoring...")
    lifecycle_manager.start_health_monitoring()
    
    # Wait a bit for health checks
    await asyncio.sleep(2)
    
    # Display health metrics
    logger.info("\n9. Health metrics:")
    for strategy_name in ["trend_instance", "mean_reversion_instance", "arbitrage_instance"]:
        health = lifecycle_manager.get_strategy_health(strategy_name)
        logger.info(f"  {strategy_name}:")
        logger.info(f"    Status: {health.status.value}")
        logger.info(f"    Signals Generated: {health.signals_generated}")
        logger.info(f"    Uptime: {health.uptime}")
    
    # Test strategy operations
    logger.info("\n10. Testing strategy operations...")
    
    # Pause a strategy
    lifecycle_manager.pause_strategy("arbitrage_instance")
    logger.info("  Paused arbitrage_instance")
    
    # Resume the strategy
    await asyncio.sleep(1)
    lifecycle_manager.resume_strategy("arbitrage_instance")
    logger.info("  Resumed arbitrage_instance")
    
    # Restart a strategy
    lifecycle_manager.restart_strategy("mean_reversion_instance")
    logger.info("  Restarted mean_reversion_instance")
    
    # Get orchestration summary
    logger.info("\n11. Orchestration summary:")
    summary = registry.get_orchestration_summary()
    logger.info(f"  Total strategies: {summary['total_strategies']}")
    logger.info(f"  Capabilities distribution: {summary['capabilities_distribution']}")
    logger.info(f"  Market distribution: {summary['market_distribution']}")
    logger.info(f"  Complexity distribution: {summary['complexity_distribution']}")
    logger.info(f"  Risk distribution: {summary['risk_distribution']}")
    
    # Filter strategies for specific use case
    logger.info("\n12. Filtering strategies for crypto trading:")
    crypto_strategies = registry.filter_strategies(
        markets={MarketType.CRYPTO},
        max_complexity=StrategyComplexity.INTERMEDIATE,
        max_risk_level="medium"
    )
    logger.info(f"  Suitable crypto strategies: {crypto_strategies}")
    
    # Clean up
    logger.info("\n13. Cleaning up...")
    lifecycle_manager.stop_health_monitoring()
    
    # Stop all strategies
    for strategy_name in ["trend_instance", "mean_reversion_instance", "arbitrage_instance"]:
        lifecycle_manager.stop_strategy(strategy_name)
    
    logger.info("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())