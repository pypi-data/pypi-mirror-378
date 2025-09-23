#!/usr/bin/env python3
"""
Tests for orchestration parameter optimization system.

This module tests the parameter optimization algorithms and system
for finding optimal orchestration settings.
"""

import pytest
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict

from src.orchestration.parameter_optimizer import (
    ParameterOptimizationSystem,
    OptimizationConfig,
    OptimizationMethod,
    ParameterRange,
    OptimizationObjective,
    OptimizationConstraint,
    ParameterSet,
    GridSearchOptimizer,
    GeneticAlgorithmOptimizer,
    OptimizationResult
)
from src.orchestration.config import OrchestratorConfig, AllocationConfig, RiskConfig, MonitoringConfig
from src.orchestration.backtesting_engine import OrchestratorBacktestConfig, OrchestratorBacktestResult


class TestParameterRange:
    """Test ParameterRange functionality."""
    
    def test_float_parameter_range(self):
        """Test float parameter range."""
        param_range = ParameterRange(
            name="test_param",
            min_value=0.1,
            max_value=0.9,
            parameter_type="float"
        )
        
        # Test sampling
        for _ in range(10):
            value = param_range.sample_value()
            assert 0.1 <= value <= 0.9
            assert isinstance(value, float)
        
        # Test grid values
        grid_values = param_range.get_grid_values(5)
        assert len(grid_values) == 5
        assert grid_values[0] == 0.1
        assert grid_values[-1] == 0.9
    
    def test_int_parameter_range(self):
        """Test integer parameter range."""
        param_range = ParameterRange(
            name="test_param",
            min_value=5,
            max_value=15,
            parameter_type="int"
        )
        
        # Test sampling
        for _ in range(10):
            value = param_range.sample_value()
            assert 5 <= value <= 15
            assert isinstance(value, int)
        
        # Test grid values
        grid_values = param_range.get_grid_values()
        assert len(grid_values) == 11  # 5 to 15 inclusive
        assert all(isinstance(v, int) for v in grid_values)
    
    def test_categorical_parameter_range(self):
        """Test categorical parameter range."""
        categories = ["method_a", "method_b", "method_c"]
        param_range = ParameterRange(
            name="test_param",
            min_value=0,
            max_value=2,
            parameter_type="categorical",
            categorical_values=categories
        )
        
        # Test sampling
        for _ in range(10):
            value = param_range.sample_value()
            assert value in categories
        
        # Test grid values
        grid_values = param_range.get_grid_values()
        assert grid_values == categories


class TestOptimizationObjective:
    """Test OptimizationObjective functionality."""
    
    def test_sharpe_ratio_objective(self):
        """Test Sharpe ratio objective evaluation."""
        objective = OptimizationObjective(name="sharpe_ratio", maximize=True, weight=1.0)
        
        # Mock backtest result
        mock_result = Mock()
        mock_result.sharpe_ratio = 1.5
        
        value = objective.evaluate(mock_result)
        assert value == 1.5
    
    def test_max_drawdown_objective(self):
        """Test max drawdown objective evaluation."""
        objective = OptimizationObjective(name="max_drawdown", maximize=False, weight=1.0)
        
        # Mock backtest result
        mock_result = Mock()
        mock_result.max_drawdown = -0.15
        
        value = objective.evaluate(mock_result)
        assert value == 0.15  # Should be positive (minimizing negative drawdown)
    
    def test_weighted_objective(self):
        """Test weighted objective evaluation."""
        objective = OptimizationObjective(name="total_return", maximize=True, weight=0.5)
        
        # Mock backtest result
        mock_result = Mock()
        mock_result.total_return = 0.20
        
        value = objective.evaluate(mock_result)
        assert value == 0.10  # 0.20 * 0.5


class TestOptimizationConstraint:
    """Test OptimizationConstraint functionality."""
    
    def test_max_drawdown_constraint(self):
        """Test max drawdown constraint."""
        constraint = OptimizationConstraint(
            name="max_drawdown",
            constraint_type="max",
            value=0.20
        )
        
        # Mock results
        good_result = Mock()
        good_result.max_drawdown = -0.15
        
        bad_result = Mock()
        bad_result.max_drawdown = -0.25
        
        assert constraint.is_satisfied(good_result) == True
        assert constraint.is_satisfied(bad_result) == False
    
    def test_min_sharpe_constraint(self):
        """Test minimum Sharpe ratio constraint."""
        constraint = OptimizationConstraint(
            name="min_sharpe",
            constraint_type="min",
            value=1.0
        )
        
        # Mock results
        good_result = Mock()
        good_result.sharpe_ratio = 1.2
        
        bad_result = Mock()
        bad_result.sharpe_ratio = 0.8
        
        assert constraint.is_satisfied(good_result) == True
        assert constraint.is_satisfied(bad_result) == False


class TestParameterSet:
    """Test ParameterSet functionality."""
    
    def test_parameter_set_creation(self):
        """Test parameter set creation."""
        params = {"param1": 0.5, "param2": 10}
        param_set = ParameterSet(parameters=params)
        
        assert param_set.parameters == params
        assert param_set.objective_value is None
        assert param_set.constraint_violations == 0
    
    def test_to_config_conversion(self):
        """Test conversion to orchestrator config."""
        # Create base config
        base_config = OrchestratorConfig(
            allocation=AllocationConfig(method="equal_weight"),
            risk=RiskConfig(max_portfolio_drawdown=0.10),
            monitoring=MonitoringConfig(performance_tracking=True),
            strategies=[]
        )
        
        # Create parameter set
        params = {
            "allocation.rebalance_threshold": 0.05,
            "risk.max_portfolio_drawdown": 0.15
        }
        param_set = ParameterSet(parameters=params)
        
        # Convert to config
        new_config = param_set.to_config(base_config)
        
        # Verify parameters were applied
        assert hasattr(new_config.allocation, 'rebalance_threshold')
        assert new_config.risk.max_portfolio_drawdown == 0.15


class TestGridSearchOptimizer:
    """Test GridSearchOptimizer functionality."""
    
    @pytest.fixture
    def grid_optimizer(self):
        """Create grid search optimizer."""
        return GridSearchOptimizer()
    
    @pytest.fixture
    def sample_config(self):
        """Create sample optimization configuration."""
        parameter_ranges = [
            ParameterRange(name="param1", min_value=0.1, max_value=0.3, parameter_type="float"),
            ParameterRange(name="param2", min_value=5, max_value=10, parameter_type="int")
        ]
        
        objectives = [
            OptimizationObjective(name="sharpe_ratio", maximize=True, weight=1.0)
        ]
        
        return OptimizationConfig(
            method=OptimizationMethod.GRID_SEARCH,
            parameter_ranges=parameter_ranges,
            objectives=objectives,
            grid_resolution=3
        )
    
    def test_parameter_grid_generation(self, grid_optimizer, sample_config):
        """Test parameter grid generation."""
        grid = grid_optimizer._generate_parameter_grid(
            sample_config.parameter_ranges, 
            sample_config.grid_resolution
        )
        
        # Should have 3 * 6 = 18 combinations (3 float values * 6 int values)
        assert len(grid) == 18
        
        # Check that all combinations are present
        param1_values = set()
        param2_values = set()
        
        for params in grid:
            param1_values.add(params["param1"])
            param2_values.add(params["param2"])
        
        assert len(param1_values) == 3  # 3 grid points for float
        assert len(param2_values) == 6  # 6 integer values (5-10 inclusive)
    
    @pytest.mark.asyncio
    async def test_parameter_evaluation(self, grid_optimizer):
        """Test parameter set evaluation."""
        # Mock dependencies
        param_set = ParameterSet(parameters={"test_param": 0.5})
        
        mock_base_config = Mock()
        mock_backtest_config = Mock()
        mock_market_data = {}
        
        objectives = [OptimizationObjective(name="sharpe_ratio", maximize=True, weight=1.0)]
        constraints = []
        
        # Mock backtest result
        mock_backtest_result = Mock()
        mock_backtest_result.sharpe_ratio = 1.2
        
        with patch('src.orchestration.parameter_optimizer.OrchestratorBacktestEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.run_backtest = AsyncMock(return_value=mock_backtest_result)
            
            result = await grid_optimizer._evaluate_parameter_set(
                param_set, mock_base_config, mock_backtest_config,
                mock_market_data, objectives, constraints
            )
            
            assert result.objective_value == 1.2
            assert result.constraint_violations == 0
            assert result.backtest_result == mock_backtest_result


class TestGeneticAlgorithmOptimizer:
    """Test GeneticAlgorithmOptimizer functionality."""
    
    @pytest.fixture
    def ga_optimizer(self):
        """Create genetic algorithm optimizer."""
        return GeneticAlgorithmOptimizer()
    
    @pytest.fixture
    def parameter_ranges(self):
        """Create parameter ranges for testing."""
        return [
            ParameterRange(name="param1", min_value=0.0, max_value=1.0, parameter_type="float"),
            ParameterRange(name="param2", min_value=1, max_value=10, parameter_type="int"),
            ParameterRange(name="param3", min_value=0, max_value=2, parameter_type="categorical",
                          categorical_values=["a", "b", "c"])
        ]
    
    def test_population_initialization(self, ga_optimizer, parameter_ranges):
        """Test population initialization."""
        population = ga_optimizer._initialize_population(parameter_ranges, 10)
        
        assert len(population) == 10
        
        for individual in population:
            assert "param1" in individual.parameters
            assert "param2" in individual.parameters
            assert "param3" in individual.parameters
            
            assert 0.0 <= individual.parameters["param1"] <= 1.0
            assert 1 <= individual.parameters["param2"] <= 10
            assert individual.parameters["param3"] in ["a", "b", "c"]
    
    def test_tournament_selection(self, ga_optimizer):
        """Test tournament selection."""
        # Create population with known fitness values
        population = []
        for i in range(5):
            param_set = ParameterSet(parameters={"param": i})
            param_set.objective_value = i * 0.1  # Increasing fitness
            population.append(param_set)
        
        # Tournament selection should favor higher fitness
        selected_values = []
        for _ in range(20):
            selected = ga_optimizer._tournament_selection(population, tournament_size=3)
            selected_values.append(selected.objective_value)
        
        # Should select higher fitness individuals more often
        avg_selected = np.mean(selected_values)
        assert avg_selected > 0.2  # Should be above random selection average
    
    def test_crossover(self, ga_optimizer, parameter_ranges):
        """Test crossover operation."""
        param_ranges_dict = {pr.name: pr for pr in parameter_ranges}
        
        parent1 = ParameterSet(parameters={"param1": 0.2, "param2": 3, "param3": "a"})
        parent2 = ParameterSet(parameters={"param1": 0.8, "param2": 7, "param3": "c"})
        
        child = ga_optimizer._crossover(parent1, parent2, param_ranges_dict)
        
        # Child should have parameters from both parents
        assert "param1" in child.parameters
        assert "param2" in child.parameters
        assert "param3" in child.parameters
        
        # Values should be from one of the parents
        assert child.parameters["param1"] in [0.2, 0.8]
        assert child.parameters["param2"] in [3, 7]
        assert child.parameters["param3"] in ["a", "c"]
    
    def test_mutation(self, ga_optimizer, parameter_ranges):
        """Test mutation operation."""
        param_ranges_dict = {pr.name: pr for pr in parameter_ranges}
        
        original = ParameterSet(parameters={"param1": 0.5, "param2": 5, "param3": "b"})
        
        # Test multiple mutations to see variation
        mutations = []
        for _ in range(50):
            mutated = ga_optimizer._mutate(original, param_ranges_dict, mutation_rate=1.0)
            mutations.append(mutated.parameters.copy())
        
        # Should see some variation in parameters
        param1_values = [m["param1"] for m in mutations]
        param2_values = [m["param2"] for m in mutations]
        
        assert len(set(param1_values)) > 1  # Should have variation
        assert len(set(param2_values)) > 1  # Should have variation


class TestParameterOptimizationSystem:
    """Test ParameterOptimizationSystem functionality."""
    
    @pytest.fixture
    def optimization_system(self):
        """Create parameter optimization system."""
        return ParameterOptimizationSystem()
    
    def test_system_initialization(self, optimization_system):
        """Test system initialization."""
        assert OptimizationMethod.GRID_SEARCH in optimization_system.optimizers
        assert OptimizationMethod.GENETIC_ALGORITHM in optimization_system.optimizers
        
        # Bayesian optimization availability depends on sklearn
        try:
            import sklearn
            assert OptimizationMethod.BAYESIAN_OPTIMIZATION in optimization_system.optimizers
        except ImportError:
            assert optimization_system.optimizers[OptimizationMethod.BAYESIAN_OPTIMIZATION] is None
    
    def test_default_parameter_ranges(self, optimization_system):
        """Test default parameter ranges creation."""
        ranges = optimization_system.create_default_parameter_ranges()
        
        assert len(ranges) > 0
        
        # Check that common parameters are included
        param_names = [r.name for r in ranges]
        assert "allocation.rebalance_threshold" in param_names
        assert "risk.max_portfolio_drawdown" in param_names
        assert "risk.position_size_limit" in param_names
    
    def test_default_objectives(self, optimization_system):
        """Test default objectives creation."""
        objectives = optimization_system.create_default_objectives()
        
        assert len(objectives) > 0
        
        # Check that common objectives are included
        obj_names = [o.name for o in objectives]
        assert "sharpe_ratio" in obj_names
        assert "total_return" in obj_names
        assert "max_drawdown" in obj_names
    
    def test_default_constraints(self, optimization_system):
        """Test default constraints creation."""
        constraints = optimization_system.create_default_constraints()
        
        assert len(constraints) > 0
        
        # Check that common constraints are included
        constraint_names = [c.name for c in constraints]
        assert "max_drawdown" in constraint_names
        assert "min_sharpe" in constraint_names
    
    def test_config_validation(self, optimization_system):
        """Test optimization configuration validation."""
        # Valid configuration
        valid_config = OptimizationConfig(
            method=OptimizationMethod.GRID_SEARCH,
            parameter_ranges=[
                ParameterRange(name="param1", min_value=0.1, max_value=0.9, parameter_type="float")
            ],
            objectives=[
                OptimizationObjective(name="sharpe_ratio", maximize=True, weight=1.0)
            ]
        )
        
        # Should not raise exception
        optimization_system._validate_optimization_config(valid_config)
        
        # Invalid configuration - no parameter ranges
        invalid_config = OptimizationConfig(
            method=OptimizationMethod.GRID_SEARCH,
            parameter_ranges=[],
            objectives=[
                OptimizationObjective(name="sharpe_ratio", maximize=True, weight=1.0)
            ]
        )
        
        with pytest.raises(ValueError, match="No parameter ranges specified"):
            optimization_system._validate_optimization_config(invalid_config)
        
        # Invalid configuration - no objectives
        invalid_config2 = OptimizationConfig(
            method=OptimizationMethod.GRID_SEARCH,
            parameter_ranges=[
                ParameterRange(name="param1", min_value=0.1, max_value=0.9, parameter_type="float")
            ],
            objectives=[]
        )
        
        with pytest.raises(ValueError, match="No optimization objectives specified"):
            optimization_system._validate_optimization_config(invalid_config2)


class TestOptimizationResult:
    """Test OptimizationResult functionality."""
    
    def test_result_creation(self):
        """Test optimization result creation."""
        best_params = ParameterSet(parameters={"param1": 0.5})
        best_params.objective_value = 1.0
        
        all_results = [best_params]
        
        result = OptimizationResult(
            best_parameters=best_params,
            all_results=all_results,
            optimization_history=[1.0],
            convergence_achieved=True,
            total_evaluations=1,
            optimization_time=10.0,
            method_used=OptimizationMethod.GRID_SEARCH
        )
        
        assert result.best_parameters == best_params
        assert result.total_evaluations == 1
        assert result.convergence_achieved == True
    
    def test_top_n_results(self):
        """Test getting top N results."""
        # Create multiple parameter sets with different objective values
        results = []
        for i in range(10):
            param_set = ParameterSet(parameters={"param": i})
            param_set.objective_value = i * 0.1
            results.append(param_set)
        
        best_params = results[-1]  # Highest objective value
        
        result = OptimizationResult(
            best_parameters=best_params,
            all_results=results,
            optimization_history=[],
            convergence_achieved=True,
            total_evaluations=10,
            optimization_time=10.0,
            method_used=OptimizationMethod.GRID_SEARCH
        )
        
        top_3 = result.get_top_n_results(3)
        assert len(top_3) == 3
        
        # Should be sorted by objective value (descending)
        assert top_3[0].objective_value >= top_3[1].objective_value
        assert top_3[1].objective_value >= top_3[2].objective_value
    
    def test_save_and_load_results(self, tmp_path):
        """Test saving and loading optimization results."""
        best_params = ParameterSet(parameters={"param1": 0.5})
        best_params.objective_value = 1.0
        
        result = OptimizationResult(
            best_parameters=best_params,
            all_results=[best_params],
            optimization_history=[1.0],
            convergence_achieved=True,
            total_evaluations=1,
            optimization_time=10.0,
            method_used=OptimizationMethod.GRID_SEARCH
        )
        
        # Save to file
        filepath = tmp_path / "test_results.pkl"
        result.save_to_file(str(filepath))
        
        # Load from file
        loaded_result = OptimizationResult.load_from_file(str(filepath))
        
        assert loaded_result.best_parameters.parameters == result.best_parameters.parameters
        assert loaded_result.total_evaluations == result.total_evaluations
        assert loaded_result.method_used == result.method_used


@pytest.mark.integration
class TestParameterOptimizationIntegration:
    """Integration tests for parameter optimization."""
    
    def create_sample_market_data(self) -> Dict[str, pd.DataFrame]:
        """Create sample market data for testing."""
        dates = pd.date_range(start="2023-01-01", end="2023-03-31", freq="D")
        
        data = pd.DataFrame(index=dates)
        data['close'] = 100 + np.cumsum(np.random.normal(0, 1, len(dates)))
        data['open'] = data['close'].shift(1).fillna(data['close'].iloc[0])
        data['high'] = np.maximum(data['open'], data['close']) * 1.01
        data['low'] = np.minimum(data['open'], data['close']) * 0.99
        data['volume'] = 1000000
        
        return {"TESTCOIN": data}
    
    def create_base_config(self) -> OrchestratorConfig:
        """Create base orchestrator configuration."""
        from src.orchestration.config import StrategyConfig
        
        return OrchestratorConfig(
            allocation=AllocationConfig(method="equal_weight"),
            risk=RiskConfig(max_portfolio_drawdown=0.15),
            monitoring=MonitoringConfig(performance_tracking=True),
            strategies=[
                StrategyConfig(type="TestStrategy", name="test", enabled=True, parameters={})
            ]
        )
    
    @pytest.mark.asyncio
    async def test_end_to_end_optimization(self):
        """Test end-to-end parameter optimization."""
        # Create optimization configuration
        opt_config = OptimizationConfig(
            method=OptimizationMethod.GRID_SEARCH,
            parameter_ranges=[
                ParameterRange(name="risk.max_portfolio_drawdown", min_value=0.10, max_value=0.20, 
                              step_size=0.05, parameter_type="float")
            ],
            objectives=[
                OptimizationObjective(name="sharpe_ratio", maximize=True, weight=1.0)
            ],
            grid_resolution=3,
            enable_cross_validation=False
        )
        
        # Create configurations
        base_config = self.create_base_config()
        backtest_config = OrchestratorBacktestConfig(
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 2, 28),
            initial_capital=100000.0
        )
        
        market_data = self.create_sample_market_data()
        
        # Mock the backtesting engine to avoid complex dependencies
        with patch('src.orchestration.parameter_optimizer.OrchestratorBacktestEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            
            # Mock backtest result
            mock_result = Mock()
            mock_result.sharpe_ratio = 1.0
            mock_result.total_return = 0.10
            mock_result.max_drawdown = -0.05
            mock_result.win_rate = 0.60
            mock_result.profit_factor = 1.5
            mock_result.portfolio_history = pd.DataFrame()
            
            mock_engine.run_backtest = AsyncMock(return_value=mock_result)
            
            # Run optimization
            optimizer = ParameterOptimizationSystem()
            result = await optimizer.optimize_parameters(
                opt_config, base_config, backtest_config, market_data
            )
            
            # Verify results
            assert result is not None
            assert result.best_parameters is not None
            assert result.total_evaluations > 0
            assert result.method_used == OptimizationMethod.GRID_SEARCH
            
            # Verify that backtest engine was called
            assert mock_engine.run_backtest.called


if __name__ == "__main__":
    pytest.main([__file__])