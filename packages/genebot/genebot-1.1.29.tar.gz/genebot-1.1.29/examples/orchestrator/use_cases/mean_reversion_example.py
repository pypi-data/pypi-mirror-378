#!/usr/bin/env python3
"""
Mean Reversion Strategy Orchestration Example

This example demonstrates how to set up and run a mean reversion focused
orchestration system. It combines multiple mean reversion strategies with
volatility-based allocation and market regime detection.

Key Features:
- Multiple mean reversion strategies
- Volatility-based allocation adjustments
- Market regime detection (trending vs sideways)
- Dynamic parameter adjustment based on market conditions
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

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


class MeanReversionOrchestrator:
    """
    Specialized orchestrator for mean reversion strategies.
    """
    
    def __init__(self, config_path: str):
        """Initialize the mean reversion orchestrator."""
        self.config = OrchestratorConfig.from_file(config_path)
        self.orchestrator = StrategyOrchestrator(self.config)
        self.market_regime_detector = MarketRegimeDetector()
        self.volatility_analyzer = VolatilityAnalyzer()
        
    async def start(self):
        """Start the mean reversion orchestration system."""
        logger.info("Starting mean reversion orchestrator...")
        
        # Initialize components
        await self.market_regime_detector.initialize()
        await self.volatility_analyzer.initialize()
        
        # Start the main orchestrator
        await self.orchestrator.start()
        
        # Start monitoring tasks
        asyncio.create_task(self.monitor_market_regimes())
        asyncio.create_task(self.adjust_for_volatility())
        
        logger.info("Mean reversion orchestrator started successfully")
    
    async def monitor_market_regimes(self):
        """Monitor market regimes and adjust strategy parameters."""
        while True:
            try:
                # Detect current market regime
                regime_analysis = await self.market_regime_detector.detect_regime()
                
                # Adjust strategies based on regime
                await self.adjust_for_market_regime(regime_analysis)
                
                # Wait before next analysis
                await asyncio.sleep(600)  # 10 minutes
                
            except Exception as e:
                logger.error(f"Error in market regime monitoring: {e}")
                await asyncio.sleep(120)  # Wait 2 minutes on error
    
    async def adjust_for_volatility(self):
        """Adjust allocations based on volatility conditions."""
        while True:
            try:
                # Analyze current volatility
                volatility_analysis = await self.volatility_analyzer.analyze_volatility()
                
                # Adjust allocations based on volatility
                await self.adjust_allocations_for_volatility(volatility_analysis)
                
                # Wait before next analysis
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in volatility monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def adjust_for_market_regime(self, regime_analysis: Dict):
        """Adjust strategy parameters based on market regime."""
        parameter_adjustments = {}
        
        for market, regime_data in regime_analysis.items():
            regime_type = regime_data['regime']
            confidence = regime_data['confidence']
            
            if regime_type == 'sideways' and confidence > 0.7:
                # Boost mean reversion strategies in sideways markets
                for strategy_name in self.get_mean_reversion_strategies_for_market(market):
                    parameter_adjustments[strategy_name] = {
                        'allocation_boost': 1.3,  # 30% boost
                        'std_dev_threshold': 1.8,  # More sensitive
                        'reversion_speed': 0.3     # Faster reversion expectation
                    }
                    
            elif regime_type == 'trending' and confidence > 0.7:
                # Reduce mean reversion strategies in trending markets
                for strategy_name in self.get_mean_reversion_strategies_for_market(market):
                    parameter_adjustments[strategy_name] = {
                        'allocation_boost': 0.7,   # 30% reduction
                        'std_dev_threshold': 2.5,  # Less sensitive
                        'reversion_speed': 0.1     # Slower reversion expectation
                    }
        
        # Apply parameter adjustments
        if parameter_adjustments:
            await self.orchestrator.update_strategy_parameters(parameter_adjustments)
            logger.info(f"Applied regime-based parameter adjustments: {parameter_adjustments}")
    
    async def adjust_allocations_for_volatility(self, volatility_analysis: Dict):
        """Adjust strategy allocations based on volatility."""
        allocation_adjustments = {}
        
        for market, vol_data in volatility_analysis.items():
            volatility_level = vol_data['level']  # 'low', 'medium', 'high'
            volatility_percentile = vol_data['percentile']
            
            mean_reversion_strategies = self.get_mean_reversion_strategies_for_market(market)
            
            for strategy_name in mean_reversion_strategies:
                current_weight = self.orchestrator.get_strategy_weight(strategy_name)
                
                if volatility_level == 'high':
                    # Increase allocation in high volatility (more mean reversion opportunities)
                    boost_factor = 1.0 + (volatility_percentile - 0.7) * 2  # Up to 60% boost
                    allocation_adjustments[strategy_name] = current_weight * boost_factor
                    
                elif volatility_level == 'low':
                    # Reduce allocation in low volatility (fewer opportunities)
                    reduction_factor = 0.6 + volatility_percentile * 0.4  # 60-100% of original
                    allocation_adjustments[strategy_name] = current_weight * reduction_factor
        
        # Apply allocation adjustments
        if allocation_adjustments:
            await self.orchestrator.update_strategy_weights(allocation_adjustments)
            logger.info(f"Applied volatility-based allocation adjustments")
    
    def get_mean_reversion_strategies_for_market(self, market: str) -> List[str]:
        """Get mean reversion strategies for a specific market."""
        mean_reversion_strategies = []
        for strategy in self.orchestrator.active_strategies:
            if (hasattr(strategy, 'strategy_type') and 
                'reversion' in strategy.strategy_type.lower() and
                market in strategy.markets):
                mean_reversion_strategies.append(strategy.name)
        return mean_reversion_strategies


class MarketRegimeDetector:
    """
    Detects market regimes (trending vs sideways) using multiple indicators.
    """
    
    def __init__(self):
        self.regime_indicators = {
            'adx': self.adx_regime_detection,
            'price_range': self.price_range_regime,
            'volatility_clustering': self.volatility_clustering_regime,
            'autocorrelation': self.autocorrelation_regime
        }
    
    async def initialize(self):
        """Initialize regime detection components."""
        logger.info("Initializing market regime detector...")
    
    async def detect_regime(self) -> Dict:
        """Detect market regime across all markets."""
        regime_analysis = {}
        
        markets = ['crypto', 'forex']
        
        for market in markets:
            market_data = await self.get_market_data(market)
            regime_analysis[market] = await self.analyze_market_regime(market_data)
        
        return regime_analysis
    
    async def analyze_market_regime(self, market_data: Dict) -> Dict:
        """Analyze regime for a specific market."""
        regime_scores = []
        
        # Apply multiple regime indicators
        for indicator_name, indicator_func in self.regime_indicators.items():
            score = await indicator_func(market_data)
            regime_scores.append(score)
        
        # Calculate overall regime
        avg_score = sum(regime_scores) / len(regime_scores)
        
        if avg_score > 0.3:
            regime_type = 'trending'
        elif avg_score < -0.3:
            regime_type = 'sideways'
        else:
            regime_type = 'mixed'
        
        confidence = self.calculate_regime_confidence(regime_scores)
        
        return {
            'regime': regime_type,
            'confidence': confidence,
            'score': avg_score,
            'individual_scores': dict(zip(self.regime_indicators.keys(), regime_scores))
        }
    
    async def adx_regime_detection(self, market_data: Dict) -> float:
        """Detect regime using ADX indicator."""
        adx = market_data.get('adx', 0)
        
        if adx > 40:
            return 1.0  # Strong trend
        elif adx > 25:
            return 0.5  # Moderate trend
        elif adx < 15:
            return -1.0  # Sideways
        else:
            return -0.5  # Weak trend/sideways
    
    async def price_range_regime(self, market_data: Dict) -> float:
        """Detect regime based on price range analysis."""
        high_20 = market_data.get('high_20', 0)
        low_20 = market_data.get('low_20', 0)
        current_price = market_data.get('close', 0)
        
        if high_20 == low_20:
            return 0
        
        price_range = (high_20 - low_20) / current_price
        
        if price_range > 0.15:  # High range = trending
            return 1.0
        elif price_range < 0.05:  # Low range = sideways
            return -1.0
        else:
            return (price_range - 0.10) * 10  # Linear interpolation
    
    async def volatility_clustering_regime(self, market_data: Dict) -> float:
        """Detect regime based on volatility clustering."""
        volatility_series = market_data.get('volatility_20', [])
        
        if len(volatility_series) < 10:
            return 0
        
        # Calculate volatility of volatility
        vol_of_vol = np.std(volatility_series)
        mean_vol = np.mean(volatility_series)
        
        if mean_vol == 0:
            return 0
        
        vol_ratio = vol_of_vol / mean_vol
        
        if vol_ratio > 0.5:  # High volatility clustering = trending
            return 1.0
        elif vol_ratio < 0.2:  # Low volatility clustering = sideways
            return -1.0
        else:
            return (vol_ratio - 0.35) * 3.33  # Linear interpolation
    
    async def autocorrelation_regime(self, market_data: Dict) -> float:
        """Detect regime based on price autocorrelation."""
        returns = market_data.get('returns_20', [])
        
        if len(returns) < 15:
            return 0
        
        # Calculate first-order autocorrelation
        autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]
        
        if np.isnan(autocorr):
            return 0
        
        if autocorr > 0.3:  # Positive autocorr = trending
            return 1.0
        elif autocorr < -0.3:  # Negative autocorr = mean reverting
            return -1.0
        else:
            return autocorr * 3.33  # Scale to [-1, 1]
    
    def calculate_regime_confidence(self, regime_scores: List[float]) -> float:
        """Calculate confidence in regime detection."""
        if not regime_scores:
            return 0
        
        # Confidence based on agreement between indicators
        avg_score = sum(regime_scores) / len(regime_scores)
        agreement = sum(1 for score in regime_scores if score * avg_score > 0) / len(regime_scores)
        
        return agreement
    
    async def get_market_data(self, market: str) -> Dict:
        """Get market data for regime analysis."""
        # Mock data for demonstration
        return {
            'close': 45000,
            'high_20': 47000,
            'low_20': 43000,
            'adx': 28,
            'volatility_20': [0.02, 0.025, 0.018, 0.022, 0.019, 0.024, 0.021, 0.017, 0.023, 0.020],
            'returns_20': [0.01, -0.005, 0.008, -0.003, 0.012, -0.007, 0.004, -0.009, 0.006, -0.002]
        }


class VolatilityAnalyzer:
    """
    Analyzes market volatility for mean reversion strategy optimization.
    """
    
    def __init__(self):
        self.volatility_lookback = 30
    
    async def initialize(self):
        """Initialize volatility analyzer."""
        logger.info("Initializing volatility analyzer...")
    
    async def analyze_volatility(self) -> Dict:
        """Analyze volatility across all markets."""
        volatility_analysis = {}
        
        markets = ['crypto', 'forex']
        
        for market in markets:
            market_data = await self.get_market_data(market)
            volatility_analysis[market] = await self.analyze_market_volatility(market_data)
        
        return volatility_analysis
    
    async def analyze_market_volatility(self, market_data: Dict) -> Dict:
        """Analyze volatility for a specific market."""
        current_vol = market_data.get('current_volatility', 0)
        historical_vol = market_data.get('historical_volatility', [])
        
        if not historical_vol:
            return {'level': 'medium', 'percentile': 0.5}
        
        # Calculate volatility percentile
        percentile = sum(1 for vol in historical_vol if vol < current_vol) / len(historical_vol)
        
        # Classify volatility level
        if percentile > 0.8:
            level = 'high'
        elif percentile < 0.2:
            level = 'low'
        else:
            level = 'medium'
        
        return {
            'level': level,
            'percentile': percentile,
            'current': current_vol,
            'mean': np.mean(historical_vol),
            'std': np.std(historical_vol)
        }
    
    async def get_market_data(self, market: str) -> Dict:
        """Get market data for volatility analysis."""
        # Mock data for demonstration
        historical_vol = [0.02 + 0.01 * np.random.randn() for _ in range(100)]
        return {
            'current_volatility': 0.035,
            'historical_volatility': historical_vol
        }


async def main():
    """Main function to run the mean reversion orchestrator example."""
    
    # Configuration for mean reversion orchestrator
    config = {
        'orchestrator': {
            'allocation': {
                'method': 'risk_parity',
                'rebalance_frequency': 'daily',
                'min_allocation': 0.02,
                'max_allocation': 0.25,
                'risk_parity': {
                    'risk_metric': 'volatility',
                    'lookback_period': 30
                }
            },
            'risk': {
                'max_portfolio_drawdown': 0.06,
                'position_size_limit': 0.03,
                'mean_reversion_risk_adjustment': True
            },
            'strategies': [
                {
                    'type': 'RSIStrategy',
                    'name': 'rsi_mean_reversion',
                    'enabled': True,
                    'allocation_weight': 1.0,
                    'markets': ['crypto', 'forex'],
                    'parameters': {
                        'period': 14,
                        'oversold': 30,
                        'overbought': 70,
                        'mean_reversion_mode': True
                    }
                },
                {
                    'type': 'MeanReversionStrategy',
                    'name': 'statistical_mean_reversion',
                    'enabled': True,
                    'allocation_weight': 1.2,
                    'markets': ['crypto', 'forex'],
                    'parameters': {
                        'lookback_period': 20,
                        'std_dev_threshold': 2.0,
                        'mean_type': 'exponential',
                        'reversion_speed': 0.2
                    }
                },
                {
                    'type': 'BollingerBandsStrategy',
                    'name': 'bollinger_mean_reversion',
                    'enabled': True,
                    'allocation_weight': 1.1,
                    'markets': ['crypto', 'forex'],
                    'parameters': {
                        'period': 20,
                        'std_dev': 2.0,
                        'mean_reversion_mode': True
                    }
                },
                {
                    'type': 'PairsTradingStrategy',
                    'name': 'pairs_mean_reversion',
                    'enabled': True,
                    'allocation_weight': 1.3,
                    'markets': ['crypto'],
                    'parameters': {
                        'pairs': [['BTC/USD', 'ETH/USD'], ['ADA/USD', 'DOT/USD']],
                        'lookback_period': 30,
                        'z_score_threshold': 2.0,
                        'cointegration_test': True
                    }
                }
            ],
            'monitoring': {
                'performance_tracking': True,
                'metrics_frequency': '2m',
                'alert_thresholds': {
                    'regime_change': True,
                    'volatility_spike': 0.05,
                    'mean_reversion_failure': 0.8
                }
            }
        }
    }
    
    # Save configuration to file
    import yaml
    with open('mean_reversion_config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    # Create and start the mean reversion orchestrator
    orchestrator = MeanReversionOrchestrator('mean_reversion_config.yaml')
    
    try:
        await orchestrator.start()
        
        # Run for demonstration
        logger.info("Running mean reversion orchestrator for 60 seconds...")
        await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        logger.info("Shutting down mean reversion orchestrator...")
    except Exception as e:
        logger.error(f"Error running orchestrator: {e}")
    finally:
        await orchestrator.orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())