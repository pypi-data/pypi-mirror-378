#!/usr/bin/env python3
"""
Performance Optimization Example for Strategy Orchestrator

This example demonstrates advanced performance optimization techniques
for the Strategy Orchestrator, including parameter optimization,
allocation optimization, and adaptive strategy selection.

Key Features:
- Automated parameter optimization using multiple algorithms
- Dynamic allocation optimization based on market conditions
- Strategy performance attribution analysis
- Adaptive strategy selection and weighting
- Multi-objective optimization (return vs risk)
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy.optimize import minimize, differential_evolution
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit

from src.orchestration.orchestrator import StrategyOrchestrator
from src.orchestration.config import OrchestratorConfig
from src.orchestration.performance import PerformanceAnalyzer
from src.orchestration.backtesting import BacktestEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Results from optimization process."""
    parameters: Dict
    performance_metrics: Dict
    improvement: float
    confidence: float
    backtest_results: Dict


class PerformanceOptimizer:
    """
    Advanced performance optimizer for strategy orchestration.
    """
    
    def __init__(self, orchestrator: StrategyOrchestrator):
        """Initialize the performance optimizer."""
        self.orchestrator = orchestrator
        self.performance_analyzer = PerformanceAnalyzer()
        self.backtest_engine = BacktestEngine()
        
        # Optimization algorithms
        self.optimization_algorithms = {
            'genetic': self.genetic_algorithm_optimization,
            'bayesian': self.bayesian_optimization,
            'grid_search': self.grid_search_optimization,
            'random_search': self.random_search_optimization,
            'ml_guided': self.ml_guided_optimization
        }
        
        # Performance history for learning
        self.performance_history = []
        self.parameter_history = []
        
    async def optimize_orchestrator(self, 
                                  optimization_type: str = 'comprehensive',
                                  lookback_days: int = 30) -> OptimizationResult:
        """
        Perform comprehensive orchestrator optimization.
        
        Args:
            optimization_type: Type of optimization ('parameters', 'allocation', 'comprehensive')
            lookback_days: Number of days to look back for optimization
        """
        logger.info(f"Starting {optimization_type} optimization...")
        
        if optimization_type == 'parameters':
            return await self.optimize_strategy_parameters(lookback_days)
        elif optimization_type == 'allocation':
            return await self.optimize_allocation_strategy(lookback_days)
        elif optimization_type == 'comprehensive':
            return await self.comprehensive_optimization(lookback_days)
        else:
            raise ValueError(f"Unknown optimization type: {optimization_type}")
    
    async def comprehensive_optimization(self, lookback_days: int) -> OptimizationResult:
        """Perform comprehensive optimization of all components."""
        logger.info("Starting comprehensive optimization...")
        
        # Step 1: Optimize individual strategy parameters
        strategy_optimization = await self.optimize_strategy_parameters(lookback_days)
        
        # Step 2: Optimize allocation strategy
        allocation_optimization = await self.optimize_allocation_strategy(lookback_days)
        
        # Step 3: Optimize risk management parameters
        risk_optimization = await self.optimize_risk_parameters(lookback_days)
        
        # Step 4: Combine optimizations and validate
        combined_parameters = {
            **strategy_optimization.parameters,
            **allocation_optimization.parameters,
            **risk_optimization.parameters
        }
        
        # Validate combined optimization
        validation_result = await self.validate_optimization(combined_parameters, lookback_days)
        
        return OptimizationResult(
            parameters=combined_parameters,
            performance_metrics=validation_result['metrics'],
            improvement=validation_result['improvement'],
            confidence=validation_result['confidence'],
            backtest_results=validation_result['backtest']
        )
    
    async def optimize_strategy_parameters(self, lookback_days: int) -> OptimizationResult:
        """Optimize individual strategy parameters."""
        logger.info("Optimizing strategy parameters...")
        
        best_parameters = {}
        total_improvement = 0
        
        for strategy in self.orchestrator.active_strategies:
            strategy_name = strategy.name
            logger.info(f"Optimizing parameters for strategy: {strategy_name}")
            
            # Get current parameters
            current_params = strategy.get_parameters()
            
            # Define parameter search space
            param_space = self.get_parameter_search_space(strategy)
            
            # Optimize using multiple algorithms
            optimization_results = []
            
            for algo_name, algo_func in self.optimization_algorithms.items():
                try:
                    result = await algo_func(strategy_name, param_space, lookback_days)
                    optimization_results.append((algo_name, result))
                except Exception as e:
                    logger.warning(f"Optimization algorithm {algo_name} failed for {strategy_name}: {e}")
            
            # Select best result
            if optimization_results:
                best_algo, best_result = max(optimization_results, 
                                           key=lambda x: x[1]['performance'])
                
                best_parameters[strategy_name] = best_result['parameters']
                total_improvement += best_result['improvement']
                
                logger.info(f"Best parameters for {strategy_name} found using {best_algo}: "
                           f"improvement = {best_result['improvement']:.4f}")
        
        # Backtest combined parameter optimization
        backtest_result = await self.backtest_parameters(best_parameters, lookback_days)
        
        return OptimizationResult(
            parameters=best_parameters,
            performance_metrics=backtest_result['metrics'],
            improvement=total_improvement / len(self.orchestrator.active_strategies),
            confidence=backtest_result['confidence'],
            backtest_results=backtest_result
        )
    
    async def optimize_allocation_strategy(self, lookback_days: int) -> OptimizationResult:
        """Optimize allocation strategy and parameters."""
        logger.info("Optimizing allocation strategy...")
        
        # Test different allocation methods
        allocation_methods = [
            'equal_weight',
            'performance_based',
            'risk_parity',
            'mean_variance',
            'black_litterman',
            'adaptive_allocation'
        ]
        
        allocation_results = []
        
        for method in allocation_methods:
            try:
                # Test allocation method
                result = await self.test_allocation_method(method, lookback_days)
                allocation_results.append((method, result))
                
                logger.info(f"Allocation method {method}: Sharpe = {result['sharpe']:.4f}, "
                           f"Return = {result['return']:.4f}")
                
            except Exception as e:
                logger.warning(f"Failed to test allocation method {method}: {e}")
        
        # Select best allocation method
        best_method, best_result = max(allocation_results, 
                                     key=lambda x: x[1]['risk_adjusted_return'])
        
        # Optimize parameters for best method
        if best_method in ['performance_based', 'risk_parity', 'adaptive_allocation']:
            optimized_params = await self.optimize_allocation_parameters(best_method, lookback_days)
        else:
            optimized_params = {}
        
        allocation_parameters = {
            'allocation_method': best_method,
            **optimized_params
        }
        
        return OptimizationResult(
            parameters=allocation_parameters,
            performance_metrics=best_result,
            improvement=best_result['improvement_vs_baseline'],
            confidence=best_result['confidence'],
            backtest_results=best_result['backtest']
        )
    
    async def optimize_risk_parameters(self, lookback_days: int) -> OptimizationResult:
        """Optimize risk management parameters."""
        logger.info("Optimizing risk management parameters...")
        
        # Define risk parameter search space
        risk_param_space = {
            'max_portfolio_drawdown': [0.05, 0.08, 0.10, 0.12, 0.15],
            'position_size_limit': [0.02, 0.03, 0.04, 0.05, 0.06],
            'stop_loss_threshold': [0.01, 0.015, 0.02, 0.025, 0.03],
            'max_strategy_correlation': [0.70, 0.75, 0.80, 0.85, 0.90]
        }
        
        # Use grid search for risk parameters
        best_risk_params = await self.grid_search_risk_parameters(risk_param_space, lookback_days)
        
        # Validate risk parameter optimization
        validation_result = await self.validate_risk_parameters(best_risk_params, lookback_days)
        
        return OptimizationResult(
            parameters=best_risk_params,
            performance_metrics=validation_result['metrics'],
            improvement=validation_result['improvement'],
            confidence=validation_result['confidence'],
            backtest_results=validation_result['backtest']
        )
    
    async def genetic_algorithm_optimization(self, 
                                           strategy_name: str, 
                                           param_space: Dict, 
                                           lookback_days: int) -> Dict:
        """Optimize using genetic algorithm."""
        logger.info(f"Running genetic algorithm optimization for {strategy_name}")
        
        def objective_function(params):
            # Convert parameter array to dictionary
            param_dict = self.array_to_param_dict(params, param_space)
            
            # Evaluate parameters
            performance = asyncio.run(self.evaluate_parameters(strategy_name, param_dict, lookback_days))
            
            # Return negative performance for minimization
            return -performance['risk_adjusted_return']
        
        # Define bounds for genetic algorithm
        bounds = self.get_parameter_bounds(param_space)
        
        # Run genetic algorithm
        result = differential_evolution(
            objective_function,
            bounds,
            maxiter=50,
            popsize=15,
            seed=42
        )
        
        # Convert result back to parameter dictionary
        best_params = self.array_to_param_dict(result.x, param_space)
        
        # Evaluate best parameters
        performance = await self.evaluate_parameters(strategy_name, best_params, lookback_days)
        
        return {
            'parameters': best_params,
            'performance': performance['risk_adjusted_return'],
            'improvement': performance['improvement_vs_baseline'],
            'details': performance
        }
    
    async def bayesian_optimization(self, 
                                  strategy_name: str, 
                                  param_space: Dict, 
                                  lookback_days: int) -> Dict:
        """Optimize using Bayesian optimization."""
        logger.info(f"Running Bayesian optimization for {strategy_name}")
        
        # Simplified Bayesian optimization using random search with learning
        n_iterations = 30
        best_params = None
        best_performance = -np.inf
        
        # Random search with Gaussian Process learning (simplified)
        for i in range(n_iterations):
            # Sample parameters
            if i < 10:  # Random exploration phase
                params = self.sample_random_parameters(param_space)
            else:  # Exploitation phase
                params = self.sample_promising_parameters(param_space, self.parameter_history)
            
            # Evaluate parameters
            performance = await self.evaluate_parameters(strategy_name, params, lookback_days)
            
            # Update history
            self.parameter_history.append(params)
            self.performance_history.append(performance['risk_adjusted_return'])
            
            # Update best
            if performance['risk_adjusted_return'] > best_performance:
                best_performance = performance['risk_adjusted_return']
                best_params = params
                
            logger.debug(f"Bayesian iteration {i+1}: performance = {performance['risk_adjusted_return']:.4f}")
        
        final_performance = await self.evaluate_parameters(strategy_name, best_params, lookback_days)
        
        return {
            'parameters': best_params,
            'performance': best_performance,
            'improvement': final_performance['improvement_vs_baseline'],
            'details': final_performance
        }
    
    async def ml_guided_optimization(self, 
                                   strategy_name: str, 
                                   param_space: Dict, 
                                   lookback_days: int) -> Dict:
        """Optimize using machine learning guided search."""
        logger.info(f"Running ML-guided optimization for {strategy_name}")
        
        # Collect training data
        training_data = await self.collect_training_data(strategy_name, param_space, lookback_days)
        
        if len(training_data) < 20:
            # Fall back to random search if insufficient data
            return await self.random_search_optimization(strategy_name, param_space, lookback_days)
        
        # Train ML model
        X = np.array([list(params.values()) for params, _ in training_data])
        y = np.array([performance for _, performance in training_data])
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Generate candidate parameters
        n_candidates = 100
        candidates = [self.sample_random_parameters(param_space) for _ in range(n_candidates)]
        
        # Predict performance for candidates
        candidate_arrays = np.array([list(params.values()) for params in candidates])
        predicted_performance = model.predict(candidate_arrays)
        
        # Select top candidates
        top_indices = np.argsort(predicted_performance)[-10:]
        top_candidates = [candidates[i] for i in top_indices]
        
        # Evaluate top candidates
        best_params = None
        best_performance = -np.inf
        
        for params in top_candidates:
            performance = await self.evaluate_parameters(strategy_name, params, lookback_days)
            
            if performance['risk_adjusted_return'] > best_performance:
                best_performance = performance['risk_adjusted_return']
                best_params = params
        
        final_performance = await self.evaluate_parameters(strategy_name, best_params, lookback_days)
        
        return {
            'parameters': best_params,
            'performance': best_performance,
            'improvement': final_performance['improvement_vs_baseline'],
            'details': final_performance
        }
    
    async def grid_search_optimization(self, 
                                     strategy_name: str, 
                                     param_space: Dict, 
                                     lookback_days: int) -> Dict:
        """Optimize using grid search."""
        logger.info(f"Running grid search optimization for {strategy_name}")
        
        # Generate parameter grid
        param_grid = self.generate_parameter_grid(param_space)
        
        best_params = None
        best_performance = -np.inf
        
        for i, params in enumerate(param_grid):
            performance = await self.evaluate_parameters(strategy_name, params, lookback_days)
            
            if performance['risk_adjusted_return'] > best_performance:
                best_performance = performance['risk_adjusted_return']
                best_params = params
                
            if i % 10 == 0:
                logger.debug(f"Grid search progress: {i+1}/{len(param_grid)}")
        
        final_performance = await self.evaluate_parameters(strategy_name, best_params, lookback_days)
        
        return {
            'parameters': best_params,
            'performance': best_performance,
            'improvement': final_performance['improvement_vs_baseline'],
            'details': final_performance
        }
    
    async def random_search_optimization(self, 
                                       strategy_name: str, 
                                       param_space: Dict, 
                                       lookback_days: int) -> Dict:
        """Optimize using random search."""
        logger.info(f"Running random search optimization for {strategy_name}")
        
        n_iterations = 50
        best_params = None
        best_performance = -np.inf
        
        for i in range(n_iterations):
            params = self.sample_random_parameters(param_space)
            performance = await self.evaluate_parameters(strategy_name, params, lookback_days)
            
            if performance['risk_adjusted_return'] > best_performance:
                best_performance = performance['risk_adjusted_return']
                best_params = params
                
            if i % 10 == 0:
                logger.debug(f"Random search progress: {i+1}/{n_iterations}")
        
        final_performance = await self.evaluate_parameters(strategy_name, best_params, lookback_days)
        
        return {
            'parameters': best_params,
            'performance': best_performance,
            'improvement': final_performance['improvement_vs_baseline'],
            'details': final_performance
        }
    
    async def evaluate_parameters(self, 
                                strategy_name: str, 
                                parameters: Dict, 
                                lookback_days: int) -> Dict:
        """Evaluate strategy parameters using backtesting."""
        
        # Create temporary strategy configuration
        temp_config = self.create_temp_strategy_config(strategy_name, parameters)
        
        # Run backtest
        backtest_result = await self.backtest_engine.run_backtest(
            strategies=[temp_config],
            start_date=datetime.now() - timedelta(days=lookback_days),
            end_date=datetime.now()
        )
        
        # Calculate performance metrics
        metrics = self.performance_analyzer.calculate_metrics(backtest_result)
        
        # Get baseline performance for comparison
        baseline_metrics = await self.get_baseline_performance(strategy_name, lookback_days)
        
        # Calculate improvement
        improvement = (metrics['sharpe_ratio'] - baseline_metrics['sharpe_ratio']) / baseline_metrics['sharpe_ratio']
        
        return {
            'total_return': metrics['total_return'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'max_drawdown': metrics['max_drawdown'],
            'win_rate': metrics['win_rate'],
            'risk_adjusted_return': metrics['sharpe_ratio'],
            'improvement_vs_baseline': improvement,
            'backtest_result': backtest_result
        }
    
    def get_parameter_search_space(self, strategy) -> Dict:
        """Get parameter search space for a strategy."""
        strategy_type = type(strategy).__name__
        
        # Define search spaces for different strategy types
        search_spaces = {
            'MovingAverageStrategy': {
                'short_period': [5, 10, 15, 20, 25],
                'long_period': [20, 30, 40, 50, 60],
                'signal_threshold': [0.005, 0.01, 0.015, 0.02]
            },
            'RSIStrategy': {
                'period': [10, 14, 18, 22, 26],
                'oversold': [20, 25, 30, 35],
                'overbought': [65, 70, 75, 80]
            },
            'AdvancedMomentumStrategy': {
                'lookback_period': [10, 15, 20, 25, 30],
                'momentum_threshold': [0.01, 0.015, 0.02, 0.025, 0.03],
                'acceleration_factor': [1.0, 1.2, 1.5, 1.8, 2.0]
            }
        }
        
        return search_spaces.get(strategy_type, {})
    
    def sample_random_parameters(self, param_space: Dict) -> Dict:
        """Sample random parameters from search space."""
        params = {}
        for param_name, param_values in param_space.items():
            params[param_name] = np.random.choice(param_values)
        return params
    
    def sample_promising_parameters(self, param_space: Dict, history: List[Dict]) -> Dict:
        """Sample parameters from promising regions based on history."""
        if not history:
            return self.sample_random_parameters(param_space)
        
        # Simple heuristic: sample near best performing parameters
        best_idx = np.argmax(self.performance_history[-len(history):])
        best_params = history[best_idx]
        
        # Add noise to best parameters
        params = {}
        for param_name, param_values in param_space.items():
            if param_name in best_params:
                best_value = best_params[param_name]
                # Find index of best value
                try:
                    best_idx = param_values.index(best_value)
                    # Sample from neighborhood
                    start_idx = max(0, best_idx - 1)
                    end_idx = min(len(param_values), best_idx + 2)
                    params[param_name] = np.random.choice(param_values[start_idx:end_idx])
                except ValueError:
                    params[param_name] = np.random.choice(param_values)
            else:
                params[param_name] = np.random.choice(param_values)
        
        return params
    
    async def collect_training_data(self, 
                                  strategy_name: str, 
                                  param_space: Dict, 
                                  lookback_days: int) -> List[Tuple[Dict, float]]:
        """Collect training data for ML-guided optimization."""
        training_data = []
        
        # Sample random parameters and evaluate
        n_samples = 30
        for _ in range(n_samples):
            params = self.sample_random_parameters(param_space)
            performance = await self.evaluate_parameters(strategy_name, params, lookback_days)
            training_data.append((params, performance['risk_adjusted_return']))
        
        return training_data
    
    def create_temp_strategy_config(self, strategy_name: str, parameters: Dict) -> Dict:
        """Create temporary strategy configuration for backtesting."""
        base_config = self.orchestrator.get_strategy_config(strategy_name)
        temp_config = base_config.copy()
        temp_config['parameters'].update(parameters)
        return temp_config
    
    async def get_baseline_performance(self, strategy_name: str, lookback_days: int) -> Dict:
        """Get baseline performance for comparison."""
        # Use current strategy parameters as baseline
        current_config = self.orchestrator.get_strategy_config(strategy_name)
        
        backtest_result = await self.backtest_engine.run_backtest(
            strategies=[current_config],
            start_date=datetime.now() - timedelta(days=lookback_days),
            end_date=datetime.now()
        )
        
        return self.performance_analyzer.calculate_metrics(backtest_result)


async def main():
    """Main function to demonstrate performance optimization."""
    
    # Load orchestrator configuration
    config = OrchestratorConfig.from_file('config/orchestrator_config.yaml')
    orchestrator = StrategyOrchestrator(config)
    
    # Initialize orchestrator
    await orchestrator.start()
    
    # Create performance optimizer
    optimizer = PerformanceOptimizer(orchestrator)
    
    try:
        # Run comprehensive optimization
        logger.info("Starting comprehensive performance optimization...")
        
        optimization_result = await optimizer.optimize_orchestrator(
            optimization_type='comprehensive',
            lookback_days=30
        )
        
        logger.info(f"Optimization completed!")
        logger.info(f"Performance improvement: {optimization_result.improvement:.4f}")
        logger.info(f"Confidence: {optimization_result.confidence:.4f}")
        logger.info(f"Optimized parameters: {optimization_result.parameters}")
        
        # Apply optimized parameters
        if optimization_result.improvement > 0.05:  # 5% improvement threshold
            logger.info("Applying optimized parameters...")
            await orchestrator.update_configuration(optimization_result.parameters)
            logger.info("Optimization applied successfully")
        else:
            logger.info("Optimization improvement below threshold, not applying changes")
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())