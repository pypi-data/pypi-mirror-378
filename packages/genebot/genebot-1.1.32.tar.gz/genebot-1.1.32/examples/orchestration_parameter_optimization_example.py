#!/usr/bin/env python3
"""
Example demonstrating orchestration parameter optimization.

This example shows how to use the parameter optimization system to find
optimal orchestration settings using different optimization algorithms.
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import orchestration components
from src.orchestration.parameter_optimizer import (
    ParameterOptimizationSystem,
    OptimizationConfig,
    OptimizationMethod,
    ParameterRange,
    OptimizationObjective,
    OptimizationConstraint
)
from src.orchestration.config import OrchestratorConfig, AllocationConfig, RiskConfig, MonitoringConfig
from src.orchestration.backtesting_engine import OrchestratorBacktestConfig


def generate_sample_market_data(symbols: list, start_date: datetime, end_date: datetime) -> Dict[str, pd.DataFrame]:
    """Generate sample market data for demonstration."""
    market_data = {}
    
    for symbol in symbols:
        # Generate date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate synthetic price data
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
        
        # Random walk with trend
        returns = np.random.normal(0.0005, 0.02, len(dates))  # Daily returns
        prices = 100 * np.exp(np.cumsum(returns))  # Price series
        
        # Create OHLCV data
        data = pd.DataFrame(index=dates)
        data['close'] = prices
        data['open'] = data['close'].shift(1).fillna(data['close'].iloc[0])
        data['high'] = np.maximum(data['open'], data['close']) * (1 + np.random.uniform(0, 0.02, len(data)))
        data['low'] = np.minimum(data['open'], data['close']) * (1 - np.random.uniform(0, 0.02, len(data)))
        data['volume'] = np.random.uniform(1000000, 10000000, len(data))
        
        market_data[symbol] = data
    
    return market_data


def create_base_orchestrator_config() -> OrchestratorConfig:
    """Create base orchestrator configuration."""
    from src.orchestration.config import StrategyConfig
    
    # Create strategy configurations
    strategies = [
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
    
    # Create configuration components
    allocation_config = AllocationConfig(
        method="performance_based",
        rebalance_frequency="daily",
        min_allocation=0.01,
        max_allocation=0.25,
        rebalance_threshold=0.05
    )
    
    risk_config = RiskConfig(
        max_portfolio_drawdown=0.15,
        max_strategy_correlation=0.80,
        position_size_limit=0.05,
        stop_loss_threshold=0.02
    )
    
    monitoring_config = MonitoringConfig(
        performance_tracking=True,
        performance_lookback_days=30,
        underperformance_threshold=-0.05
    )
    
    return OrchestratorConfig(
        allocation=allocation_config,
        risk=risk_config,
        monitoring=monitoring_config,
        strategies=strategies
    )


async def demonstrate_grid_search_optimization():
    """Demonstrate grid search parameter optimization."""
    logger.info("=== Grid Search Optimization Demo ===")
    
    # Create parameter ranges for optimization
    parameter_ranges = [
        ParameterRange(
            name="allocation.rebalance_threshold",
            min_value=0.02,
            max_value=0.10,
            step_size=0.02,
            parameter_type="float"
        ),
        ParameterRange(
            name="risk.max_portfolio_drawdown",
            min_value=0.10,
            max_value=0.20,
            step_size=0.05,
            parameter_type="float"
        ),
        ParameterRange(
            name="monitoring.performance_lookback_days",
            min_value=15,
            max_value=45,
            parameter_type="int"
        )
    ]
    
    # Create optimization objectives
    objectives = [
        OptimizationObjective(name="sharpe_ratio", maximize=True, weight=0.5),
        OptimizationObjective(name="total_return", maximize=True, weight=0.3),
        OptimizationObjective(name="max_drawdown", maximize=False, weight=0.2)
    ]
    
    # Create constraints
    constraints = [
        OptimizationConstraint(name="max_drawdown", constraint_type="max", value=0.18),
        OptimizationConstraint(name="min_sharpe", constraint_type="min", value=0.3)
    ]
    
    # Create optimization configuration
    opt_config = OptimizationConfig(
        method=OptimizationMethod.GRID_SEARCH,
        parameter_ranges=parameter_ranges,
        objectives=objectives,
        constraints=constraints,
        grid_resolution=3,  # Small grid for demo
        enable_cross_validation=False  # Disable for speed
    )
    
    # Create base configurations
    base_config = create_base_orchestrator_config()
    
    backtest_config = OrchestratorBacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 6, 30),
        initial_capital=100000.0,
        commission_rate=0.001,
        slippage_rate=0.0005
    )
    
    # Generate sample market data
    symbols = ["BTCUSD", "ETHUSD", "EURUSD"]
    market_data = generate_sample_market_data(symbols, backtest_config.start_date, backtest_config.end_date)
    
    # Run optimization
    optimizer = ParameterOptimizationSystem()
    
    try:
        result = await optimizer.optimize_parameters(
            opt_config, base_config, backtest_config, market_data
        )
        
        # Display results
        logger.info(f"Grid Search Results:")
        logger.info(f"Best objective value: {result.best_parameters.objective_value:.4f}")
        logger.info(f"Best parameters: {result.best_parameters.parameters}")
        logger.info(f"Total evaluations: {result.total_evaluations}")
        logger.info(f"Optimization time: {result.optimization_time:.2f}s")
        
        if result.best_parameters.backtest_result:
            br = result.best_parameters.backtest_result
            logger.info(f"Backtest performance:")
            logger.info(f"  Total return: {br.total_return:.2%}")
            logger.info(f"  Sharpe ratio: {br.sharpe_ratio:.3f}")
            logger.info(f"  Max drawdown: {br.max_drawdown:.2%}")
            logger.info(f"  Win rate: {br.win_rate:.2%}")
        
        # Show top 3 results
        top_results = result.get_top_n_results(3)
        logger.info(f"\nTop 3 parameter combinations:")
        for i, param_set in enumerate(top_results, 1):
            logger.info(f"{i}. Objective: {param_set.objective_value:.4f}, "
                       f"Parameters: {param_set.parameters}")
        
    except Exception as e:
        logger.error(f"Grid search optimization failed: {e}")


async def demonstrate_genetic_algorithm_optimization():
    """Demonstrate genetic algorithm parameter optimization."""
    logger.info("\n=== Genetic Algorithm Optimization Demo ===")
    
    # Create parameter ranges
    parameter_ranges = [
        ParameterRange(
            name="allocation.min_allocation",
            min_value=0.005,
            max_value=0.05,
            parameter_type="float"
        ),
        ParameterRange(
            name="allocation.max_allocation", 
            min_value=0.15,
            max_value=0.40,
            parameter_type="float"
        ),
        ParameterRange(
            name="risk.position_size_limit",
            min_value=0.02,
            max_value=0.08,
            parameter_type="float"
        ),
        ParameterRange(
            name="monitoring.underperformance_threshold",
            min_value=-0.10,
            max_value=-0.02,
            parameter_type="float"
        )
    ]
    
    # Create optimization objectives
    objectives = [
        OptimizationObjective(name="risk_adjusted_return", maximize=True, weight=0.6),
        OptimizationObjective(name="win_rate", maximize=True, weight=0.4)
    ]
    
    # Create optimization configuration
    opt_config = OptimizationConfig(
        method=OptimizationMethod.GENETIC_ALGORITHM,
        parameter_ranges=parameter_ranges,
        objectives=objectives,
        max_iterations=10,  # Small number for demo
        population_size=20,  # Small population for demo
        early_stopping_patience=5,
        enable_cross_validation=False
    )
    
    # Create configurations
    base_config = create_base_orchestrator_config()
    
    backtest_config = OrchestratorBacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 4, 30),
        initial_capital=100000.0
    )
    
    # Generate market data
    symbols = ["BTCUSD", "ETHUSD"]
    market_data = generate_sample_market_data(symbols, backtest_config.start_date, backtest_config.end_date)
    
    # Run optimization
    optimizer = ParameterOptimizationSystem()
    
    try:
        result = await optimizer.optimize_parameters(
            opt_config, base_config, backtest_config, market_data
        )
        
        # Display results
        logger.info(f"Genetic Algorithm Results:")
        logger.info(f"Best objective value: {result.best_parameters.objective_value:.4f}")
        logger.info(f"Best parameters: {result.best_parameters.parameters}")
        logger.info(f"Convergence achieved: {result.convergence_achieved}")
        logger.info(f"Total evaluations: {result.total_evaluations}")
        logger.info(f"Optimization time: {result.optimization_time:.2f}s")
        
        # Show optimization history
        if result.optimization_history:
            logger.info(f"Optimization progress:")
            for i, obj_val in enumerate(result.optimization_history[-5:], 1):
                logger.info(f"  Generation {len(result.optimization_history)-5+i}: {obj_val:.4f}")
        
    except Exception as e:
        logger.error(f"Genetic algorithm optimization failed: {e}")


async def demonstrate_bayesian_optimization():
    """Demonstrate Bayesian optimization (if available)."""
    logger.info("\n=== Bayesian Optimization Demo ===")
    
    try:
        from sklearn.gaussian_process import GaussianProcessRegressor
        sklearn_available = True
    except ImportError:
        sklearn_available = False
        logger.warning("Scikit-learn not available. Skipping Bayesian optimization demo.")
        return
    
    # Create parameter ranges
    parameter_ranges = [
        ParameterRange(
            name="allocation.rebalance_threshold",
            min_value=0.01,
            max_value=0.15,
            parameter_type="float"
        ),
        ParameterRange(
            name="risk.max_strategy_correlation",
            min_value=0.60,
            max_value=0.90,
            parameter_type="float"
        )
    ]
    
    # Create optimization objectives
    objectives = [
        OptimizationObjective(name="sharpe_ratio", maximize=True, weight=1.0)
    ]
    
    # Create optimization configuration
    opt_config = OptimizationConfig(
        method=OptimizationMethod.BAYESIAN_OPTIMIZATION,
        parameter_ranges=parameter_ranges,
        objectives=objectives,
        max_iterations=15,  # Small number for demo
        n_initial_points=5,
        acquisition_function="EI",
        enable_cross_validation=False
    )
    
    # Create configurations
    base_config = create_base_orchestrator_config()
    
    backtest_config = OrchestratorBacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 3, 31),
        initial_capital=100000.0
    )
    
    # Generate market data
    symbols = ["BTCUSD"]
    market_data = generate_sample_market_data(symbols, backtest_config.start_date, backtest_config.end_date)
    
    # Run optimization
    optimizer = ParameterOptimizationSystem()
    
    try:
        result = await optimizer.optimize_parameters(
            opt_config, base_config, backtest_config, market_data
        )
        
        # Display results
        logger.info(f"Bayesian Optimization Results:")
        logger.info(f"Best objective value: {result.best_parameters.objective_value:.4f}")
        logger.info(f"Best parameters: {result.best_parameters.parameters}")
        logger.info(f"Total evaluations: {result.total_evaluations}")
        logger.info(f"Optimization time: {result.optimization_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Bayesian optimization failed: {e}")


async def demonstrate_parameter_optimization_workflow():
    """Demonstrate complete parameter optimization workflow."""
    logger.info("\n=== Complete Parameter Optimization Workflow ===")
    
    # Create default parameter ranges
    optimizer = ParameterOptimizationSystem()
    parameter_ranges = optimizer.create_default_parameter_ranges()
    objectives = optimizer.create_default_objectives()
    constraints = optimizer.create_default_constraints()
    
    logger.info(f"Using {len(parameter_ranges)} default parameter ranges:")
    for param_range in parameter_ranges:
        logger.info(f"  {param_range.name}: [{param_range.min_value}, {param_range.max_value}]")
    
    # Create optimization configuration with cross-validation
    opt_config = OptimizationConfig(
        method=OptimizationMethod.GRID_SEARCH,
        parameter_ranges=parameter_ranges[:3],  # Use first 3 for demo
        objectives=objectives,
        constraints=constraints,
        grid_resolution=2,  # Very small grid for demo
        enable_cross_validation=True,
        cv_folds=2
    )
    
    # Create configurations
    base_config = create_base_orchestrator_config()
    
    backtest_config = OrchestratorBacktestConfig(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 6, 30),
        initial_capital=100000.0
    )
    
    # Generate market data
    symbols = ["BTCUSD", "ETHUSD", "EURUSD"]
    market_data = generate_sample_market_data(symbols, backtest_config.start_date, backtest_config.end_date)
    
    try:
        result = await optimizer.optimize_parameters(
            opt_config, base_config, backtest_config, market_data
        )
        
        # Display comprehensive results
        logger.info(f"Workflow Results:")
        logger.info(f"Best objective value: {result.best_parameters.objective_value:.4f}")
        logger.info(f"Constraint violations: {result.best_parameters.constraint_violations}")
        
        if result.cross_validation_scores:
            cv_mean = np.mean(result.cross_validation_scores)
            cv_std = np.std(result.cross_validation_scores)
            logger.info(f"Cross-validation score: {cv_mean:.4f} ± {cv_std:.4f}")
        
        # Save results
        result.save_to_file("optimization_results.pkl")
        logger.info("Results saved to optimization_results.pkl")
        
    except Exception as e:
        logger.error(f"Parameter optimization workflow failed: {e}")


async def main():
    """Run all parameter optimization demonstrations."""
    logger.info("Starting Parameter Optimization Examples")
    logger.info("=" * 60)
    
    try:
        # Run demonstrations
        await demonstrate_grid_search_optimization()
        await demonstrate_genetic_algorithm_optimization()
        await demonstrate_bayesian_optimization()
        await demonstrate_parameter_optimization_workflow()
        
        logger.info("\n" + "=" * 60)
        logger.info("All parameter optimization examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in parameter optimization examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())