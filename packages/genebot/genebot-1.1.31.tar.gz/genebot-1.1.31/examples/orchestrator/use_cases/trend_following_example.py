#!/usr/bin/env python3
"""
Trend Following Strategy Orchestration Example

This example demonstrates how to set up and run a trend-following focused
orchestration system. It combines multiple trend-following strategies with
intelligent allocation and risk management.

Key Features:
- Multiple trend-following strategies
- Trend strength-based allocation
- Market regime detection
- Dynamic position sizing based on trend strength
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.orchestration.orchestrator import StrategyOrchestrator
from src.orchestration.config import OrchestratorConfig
from src.orchestration.allocation import AllocationManager
from src.orchestration.risk import OrchestratorRiskManager
from src.orchestration.performance import PerformanceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendFollowingOrchestrator:
    """
    Specialized orchestrator for trend-following strategies.
    """
    
    def __init__(self, config_path: str):
        """Initialize the trend-following orchestrator."""
        self.config = OrchestratorConfig.from_file(config_path)
        self.orchestrator = StrategyOrchestrator(self.config)
        self.trend_analyzer = TrendAnalyzer()
        
    async def start(self):
        """Start the trend-following orchestration system."""
        logger.info("Starting trend-following orchestrator...")
        
        # Initialize trend analysis
        await self.trend_analyzer.initialize()
        
        # Start the main orchestrator
        await self.orchestrator.start()
        
        # Start trend monitoring
        asyncio.create_task(self.monitor_trends())
        
        logger.info("Trend-following orchestrator started successfully")
    
    async def monitor_trends(self):
        """Monitor market trends and adjust strategy allocation."""
        while True:
            try:
                # Analyze current market trends
                trend_analysis = await self.trend_analyzer.analyze_trends()
                
                # Adjust allocations based on trend strength
                await self.adjust_allocations_for_trends(trend_analysis)
                
                # Wait before next analysis
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in trend monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def adjust_allocations_for_trends(self, trend_analysis: Dict):
        """Adjust strategy allocations based on trend analysis."""
        allocation_adjustments = {}
        
        for market, trend_data in trend_analysis.items():
            trend_strength = trend_data['strength']
            trend_direction = trend_data['direction']
            
            # Boost allocation for strategies in strong trending markets
            if trend_strength > 0.7:  # Strong trend
                for strategy_name in self.get_trend_strategies_for_market(market):
                    current_weight = self.orchestrator.get_strategy_weight(strategy_name)
                    boost_factor = 1.0 + (trend_strength - 0.7) * 2  # Up to 60% boost
                    allocation_adjustments[strategy_name] = current_weight * boost_factor
                    
            # Reduce allocation in sideways markets
            elif trend_strength < 0.3:  # Weak trend/sideways
                for strategy_name in self.get_trend_strategies_for_market(market):
                    current_weight = self.orchestrator.get_strategy_weight(strategy_name)
                    reduction_factor = 0.5 + trend_strength  # 50-80% of original
                    allocation_adjustments[strategy_name] = current_weight * reduction_factor
        
        # Apply allocation adjustments
        if allocation_adjustments:
            await self.orchestrator.update_strategy_weights(allocation_adjustments)
            logger.info(f"Applied trend-based allocation adjustments: {allocation_adjustments}")
    
    def get_trend_strategies_for_market(self, market: str) -> List[str]:
        """Get trend-following strategies for a specific market."""
        trend_strategies = []
        for strategy in self.orchestrator.active_strategies:
            if (hasattr(strategy, 'strategy_type') and 
                'trend' in strategy.strategy_type.lower() and
                market in strategy.markets):
                trend_strategies.append(strategy.name)
        return trend_strategies


class TrendAnalyzer:
    """
    Analyzes market trends across different timeframes and markets.
    """
    
    def __init__(self):
        self.trend_indicators = {
            'sma_cross': self.sma_crossover_trend,
            'adx': self.adx_trend_strength,
            'price_momentum': self.price_momentum_trend,
            'volume_trend': self.volume_trend_analysis
        }
    
    async def initialize(self):
        """Initialize trend analysis components."""
        logger.info("Initializing trend analyzer...")
        # Initialize data feeds, indicators, etc.
        
    async def analyze_trends(self) -> Dict:
        """Analyze trends across all markets."""
        trend_analysis = {}
        
        markets = ['crypto', 'forex']
        
        for market in markets:
            market_data = await self.get_market_data(market)
            trend_analysis[market] = await self.analyze_market_trend(market_data)
        
        return trend_analysis
    
    async def analyze_market_trend(self, market_data: Dict) -> Dict:
        """Analyze trend for a specific market."""
        trend_scores = []
        
        # Apply multiple trend indicators
        for indicator_name, indicator_func in self.trend_indicators.items():
            score = await indicator_func(market_data)
            trend_scores.append(score)
        
        # Calculate overall trend strength and direction
        avg_score = sum(trend_scores) / len(trend_scores)
        trend_strength = abs(avg_score)
        trend_direction = 'up' if avg_score > 0 else 'down'
        
        return {
            'strength': trend_strength,
            'direction': trend_direction,
            'confidence': self.calculate_confidence(trend_scores),
            'individual_scores': dict(zip(self.trend_indicators.keys(), trend_scores))
        }
    
    async def sma_crossover_trend(self, market_data: Dict) -> float:
        """Calculate trend based on SMA crossover."""
        # Simplified implementation
        short_sma = market_data.get('sma_20', 0)
        long_sma = market_data.get('sma_50', 0)
        
        if long_sma == 0:
            return 0
        
        crossover_strength = (short_sma - long_sma) / long_sma
        return max(-1, min(1, crossover_strength * 10))  # Normalize to [-1, 1]
    
    async def adx_trend_strength(self, market_data: Dict) -> float:
        """Calculate trend strength using ADX."""
        adx = market_data.get('adx', 0)
        di_plus = market_data.get('di_plus', 0)
        di_minus = market_data.get('di_minus', 0)
        
        if adx < 25:  # Weak trend
            return 0
        
        # Determine direction and strength
        direction = 1 if di_plus > di_minus else -1
        strength = min(1, (adx - 25) / 50)  # Normalize ADX to [0, 1]
        
        return direction * strength
    
    async def price_momentum_trend(self, market_data: Dict) -> float:
        """Calculate trend based on price momentum."""
        current_price = market_data.get('close', 0)
        price_20_ago = market_data.get('close_20', 0)
        
        if price_20_ago == 0:
            return 0
        
        momentum = (current_price - price_20_ago) / price_20_ago
        return max(-1, min(1, momentum * 5))  # Normalize to [-1, 1]
    
    async def volume_trend_analysis(self, market_data: Dict) -> float:
        """Analyze volume trend to confirm price trend."""
        current_volume = market_data.get('volume', 0)
        avg_volume = market_data.get('volume_avg_20', 0)
        price_change = market_data.get('price_change_pct', 0)
        
        if avg_volume == 0:
            return 0
        
        volume_ratio = current_volume / avg_volume
        
        # Volume confirmation of price trend
        if price_change > 0 and volume_ratio > 1.2:  # Rising price with high volume
            return min(1, volume_ratio - 1)
        elif price_change < 0 and volume_ratio > 1.2:  # Falling price with high volume
            return -min(1, volume_ratio - 1)
        else:
            return 0
    
    def calculate_confidence(self, trend_scores: List[float]) -> float:
        """Calculate confidence in trend analysis."""
        if not trend_scores:
            return 0
        
        # Confidence based on agreement between indicators
        avg_score = sum(trend_scores) / len(trend_scores)
        variance = sum((score - avg_score) ** 2 for score in trend_scores) / len(trend_scores)
        
        # Lower variance = higher confidence
        confidence = max(0, 1 - variance)
        return confidence
    
    async def get_market_data(self, market: str) -> Dict:
        """Get market data for trend analysis."""
        # This would connect to actual data sources
        # For demo purposes, return mock data
        return {
            'close': 45000,
            'close_20': 43000,
            'sma_20': 44500,
            'sma_50': 43800,
            'adx': 35,
            'di_plus': 25,
            'di_minus': 15,
            'volume': 1000000,
            'volume_avg_20': 800000,
            'price_change_pct': 0.02
        }


async def main():
    """Main function to run the trend-following orchestrator example."""
    
    # Configuration for trend-following orchestrator
    config = {
        'orchestrator': {
            'allocation': {
                'method': 'performance_based',
                'rebalance_frequency': 'daily',
                'min_allocation': 0.02,
                'max_allocation': 0.30,
                'performance_based': {
                    'lookback_period': 20,
                    'performance_metric': 'total_return',
                    'trend_adjustment': True  # Enable trend-based adjustments
                }
            },
            'risk': {
                'max_portfolio_drawdown': 0.08,
                'position_size_limit': 0.04,
                'trend_following_risk_adjustment': True
            },
            'strategies': [
                {
                    'type': 'MovingAverageStrategy',
                    'name': 'ma_trend_short',
                    'enabled': True,
                    'allocation_weight': 1.0,
                    'markets': ['crypto', 'forex'],
                    'parameters': {
                        'short_period': 10,
                        'long_period': 20,
                        'trend_filter': True
                    }
                },
                {
                    'type': 'MovingAverageStrategy',
                    'name': 'ma_trend_medium',
                    'enabled': True,
                    'allocation_weight': 1.0,
                    'markets': ['crypto', 'forex'],
                    'parameters': {
                        'short_period': 20,
                        'long_period': 50,
                        'trend_filter': True
                    }
                },
                {
                    'type': 'AdvancedMomentumStrategy',
                    'name': 'momentum_trend',
                    'enabled': True,
                    'allocation_weight': 1.2,
                    'markets': ['crypto'],
                    'parameters': {
                        'lookback_period': 15,
                        'momentum_threshold': 0.02,
                        'trend_confirmation': True
                    }
                },
                {
                    'type': 'ATRVolatilityStrategy',
                    'name': 'atr_breakout',
                    'enabled': True,
                    'allocation_weight': 1.1,
                    'markets': ['crypto'],
                    'parameters': {
                        'atr_period': 14,
                        'volatility_multiplier': 2.0,
                        'trend_filter': True
                    }
                }
            ],
            'monitoring': {
                'performance_tracking': True,
                'metrics_frequency': '1m',
                'alert_thresholds': {
                    'trend_weakness': 0.3,  # Alert when trend strength < 30%
                    'trend_reversal': True   # Alert on trend reversals
                }
            }
        }
    }
    
    # Save configuration to file
    import yaml
    with open('trend_following_config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    # Create and start the trend-following orchestrator
    orchestrator = TrendFollowingOrchestrator('trend_following_config.yaml')
    
    try:
        await orchestrator.start()
        
        # Run for demonstration (in practice, this would run indefinitely)
        logger.info("Running trend-following orchestrator for 60 seconds...")
        await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        logger.info("Shutting down trend-following orchestrator...")
    except Exception as e:
        logger.error(f"Error running orchestrator: {e}")
    finally:
        await orchestrator.orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())