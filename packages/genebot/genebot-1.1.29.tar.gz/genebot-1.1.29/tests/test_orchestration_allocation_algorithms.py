"""
Unit tests for orchestration allocation algorithms.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.orchestration.allocation import (
    AllocationManager, EqualWeightAllocator, PerformanceBasedAllocator,
    RiskParityAllocator, CustomAllocator
)
from src.orchestration.config import AllocationConfig, AllocationMethod
from src.orchestration.interfaces import PerformanceMetrics, RiskMetrics, AllocationSnapshot


class TestAllocationManager:
    """Test the main allocation manager."""
    
    @pytest.fixture
    def allocation_config(self):
        """Create test allocation configuration."""
        return AllocationConfig(
            method=AllocationMethod.PERFORMANCE_BASED,
            rebalance_frequency="daily",
            min_allocation=0.01,
            max_allocation=0.25,
            lookback_period=30
        )
    
    @pytest.fixture
    def allocation_manager(self, allocation_config):
        """Create allocation manager instance."""
        return AllocationManager(allocation_config)
    
    @pytest.fixture
    def sample_performance_metrics(self):
        """Create sample performance metrics."""
        return {
            "strategy_1": PerformanceMetrics(
                total_return=0.15,
                sharpe_ratio=1.2,
                max_drawdown=0.05,
                win_rate=0.65,
                profit_factor=1.8,
                volatility=0.12,
                alpha=0.03,
                beta=0.8,
                information_ratio=0.9
            ),
            "strategy_2": PerformanceMetrics(
                total_return=0.08,
                sharpe_ratio=0.9,
                max_drawdown=0.08,
                win_rate=0.58,
                profit_factor=1.4,
                volatility=0.15,
                alpha=0.01,
                beta=1.1,
                information_ratio=0.6
            ),
            "strategy_3": PerformanceMetrics(
                total_return=0.22,
                sharpe_ratio=1.5,
                max_drawdown=0.03,
                win_rate=0.72,
                profit_factor=2.1,
                volatility=0.10,
                alpha=0.05,
                beta=0.7,
                information_ratio=1.2
            )
        }
    
    @pytest.fixture
    def sample_risk_metrics(self):
        """Create sample risk metrics."""
        return {
            "strategy_1": RiskMetrics(
                var_95=0.02,
                cvar_95=0.03,
                max_drawdown=0.05,
                volatility=0.12,
                beta=0.8,
                correlation_to_market=0.6
            ),
            "strategy_2": RiskMetrics(
                var_95=0.025,
                cvar_95=0.035,
                max_drawdown=0.08,
                volatility=0.15,
                beta=1.1,
                correlation_to_market=0.8
            ),
            "strategy_3": RiskMetrics(
                var_95=0.015,
                cvar_95=0.02,
                max_drawdown=0.03,
                volatility=0.10,
                beta=0.7,
                correlation_to_market=0.5
            )
        }
    
    def test_initialization(self, allocation_manager, allocation_config):
        """Test allocation manager initialization."""
        assert allocation_manager.config == allocation_config
        assert allocation_manager.allocations == {}
        assert allocation_manager.allocation_history == []
        assert allocation_manager.last_rebalance is None
    
    def test_calculate_optimal_allocation(self, allocation_manager, sample_performance_metrics, sample_risk_metrics):
        """Test optimal allocation calculation."""
        allocations = allocation_manager.calculate_optimal_allocation(
            sample_performance_metrics, sample_risk_metrics
        )
        
        # Check that allocations sum to 1.0
        assert abs(sum(allocations.values()) - 1.0) < 1e-6
        
        # Check that all allocations are within bounds
        for allocation in allocations.values():
            assert allocation >= allocation_manager.config.min_allocation
            assert allocation <= allocation_manager.config.max_allocation
        
        # Strategy 3 should have highest allocation (best Sharpe ratio)
        assert allocations["strategy_3"] >= allocations["strategy_1"]
        assert allocations["strategy_3"] >= allocations["strategy_2"]
    
    def test_rebalance_allocations(self, allocation_manager):
        """Test allocation rebalancing."""
        current_positions = {
            "strategy_1": 0.4,
            "strategy_2": 0.3,
            "strategy_3": 0.3
        }
        
        # Mock the optimal allocation calculation
        with patch.object(allocation_manager, 'calculate_optimal_allocation') as mock_calc:
            mock_calc.return_value = {
                "strategy_1": 0.3,
                "strategy_2": 0.2,
                "strategy_3": 0.5
            }
            
            rebalance_actions = allocation_manager.rebalance_allocations(current_positions)
            
            # Check rebalance actions
            assert rebalance_actions["strategy_1"] == -0.1  # Reduce by 10%
            assert rebalance_actions["strategy_2"] == -0.1  # Reduce by 10%
            assert rebalance_actions["strategy_3"] == 0.2   # Increase by 20%
    
    def test_apply_risk_constraints(self, allocation_manager):
        """Test risk constraint application."""
        proposed_allocations = {
            "strategy_1": 0.5,  # Exceeds max_allocation
            "strategy_2": 0.3,
            "strategy_3": 0.2
        }
        
        constrained_allocations = allocation_manager.apply_risk_constraints(proposed_allocations)
        
        # Check that max allocation constraint is applied
        assert constrained_allocations["strategy_1"] <= allocation_manager.config.max_allocation
        
        # Check that allocations still sum to 1.0
        assert abs(sum(constrained_allocations.values()) - 1.0) < 1e-6
    
    def test_record_allocation_snapshot(self, allocation_manager):
        """Test allocation snapshot recording."""
        allocations = {"strategy_1": 0.4, "strategy_2": 0.6}
        reason = "Performance rebalancing"
        
        allocation_manager.record_allocation_snapshot(allocations, reason)
        
        assert len(allocation_manager.allocation_history) == 1
        snapshot = allocation_manager.allocation_history[0]
        assert snapshot.allocations == allocations
        assert snapshot.reason == reason
        assert isinstance(snapshot.timestamp, datetime)
    
    def test_needs_rebalancing(self, allocation_manager):
        """Test rebalancing need detection."""
        # No previous rebalance - should need rebalancing
        assert allocation_manager.needs_rebalancing()
        
        # Recent rebalance - should not need rebalancing
        allocation_manager.last_rebalance = datetime.now()
        assert not allocation_manager.needs_rebalancing()
        
        # Old rebalance - should need rebalancing
        allocation_manager.last_rebalance = datetime.now() - timedelta(days=2)
        assert allocation_manager.needs_rebalancing()


class TestEqualWeightAllocator:
    """Test equal weight allocation algorithm."""
    
    @pytest.fixture
    def allocator(self):
        """Create equal weight allocator."""
        config = AllocationConfig(method=AllocationMethod.EQUAL_WEIGHT)
        return EqualWeightAllocator(config)
    
    def test_calculate_allocation(self, allocator):
        """Test equal weight allocation calculation."""
        strategies = ["strategy_1", "strategy_2", "strategy_3"]
        allocations = allocator.calculate_allocation(strategies, {}, {})
        
        # Each strategy should get equal allocation
        expected_allocation = 1.0 / len(strategies)
        for strategy in strategies:
            assert abs(allocations[strategy] - expected_allocation) < 1e-6
        
        # Total should sum to 1.0
        assert abs(sum(allocations.values()) - 1.0) < 1e-6
    
    def test_empty_strategies(self, allocator):
        """Test allocation with empty strategies list."""
        allocations = allocator.calculate_allocation([], {}, {})
        assert allocations == {}


class TestPerformanceBasedAllocator:
    """Test performance-based allocation algorithm."""
    
    @pytest.fixture
    def allocator(self):
        """Create performance-based allocator."""
        config = AllocationConfig(method=AllocationMethod.PERFORMANCE_BASED)
        return PerformanceBasedAllocator(config)
    
    @pytest.fixture
    def performance_metrics(self):
        """Create performance metrics for testing."""
        return {
            "strategy_1": PerformanceMetrics(
                total_return=0.10, sharpe_ratio=1.0, max_drawdown=0.05,
                win_rate=0.6, profit_factor=1.5, volatility=0.12,
                alpha=0.02, beta=0.8, information_ratio=0.8
            ),
            "strategy_2": PerformanceMetrics(
                total_return=0.20, sharpe_ratio=1.5, max_drawdown=0.03,
                win_rate=0.7, profit_factor=2.0, volatility=0.10,
                alpha=0.04, beta=0.7, information_ratio=1.2
            )
        }
    
    def test_calculate_allocation(self, allocator, performance_metrics):
        """Test performance-based allocation calculation."""
        strategies = list(performance_metrics.keys())
        allocations = allocator.calculate_allocation(strategies, performance_metrics, {})
        
        # Strategy 2 should get higher allocation (better Sharpe ratio)
        assert allocations["strategy_2"] > allocations["strategy_1"]
        
        # Total should sum to 1.0
        assert abs(sum(allocations.values()) - 1.0) < 1e-6
    
    def test_zero_sharpe_ratios(self, allocator):
        """Test allocation with zero Sharpe ratios."""
        performance_metrics = {
            "strategy_1": PerformanceMetrics(
                total_return=0.0, sharpe_ratio=0.0, max_drawdown=0.05,
                win_rate=0.5, profit_factor=1.0, volatility=0.12,
                alpha=0.0, beta=1.0, information_ratio=0.0
            ),
            "strategy_2": PerformanceMetrics(
                total_return=0.0, sharpe_ratio=0.0, max_drawdown=0.05,
                win_rate=0.5, profit_factor=1.0, volatility=0.12,
                alpha=0.0, beta=1.0, information_ratio=0.0
            )
        }
        
        strategies = list(performance_metrics.keys())
        allocations = allocator.calculate_allocation(strategies, performance_metrics, {})
        
        # Should fall back to equal weight
        expected_allocation = 1.0 / len(strategies)
        for strategy in strategies:
            assert abs(allocations[strategy] - expected_allocation) < 1e-6


class TestRiskParityAllocator:
    """Test risk parity allocation algorithm."""
    
    @pytest.fixture
    def allocator(self):
        """Create risk parity allocator."""
        config = AllocationConfig(method=AllocationMethod.RISK_PARITY)
        return RiskParityAllocator(config)
    
    @pytest.fixture
    def risk_metrics(self):
        """Create risk metrics for testing."""
        return {
            "strategy_1": RiskMetrics(
                var_95=0.02, cvar_95=0.03, max_drawdown=0.05,
                volatility=0.15, beta=0.8, correlation_to_market=0.6
            ),
            "strategy_2": RiskMetrics(
                var_95=0.015, cvar_95=0.02, max_drawdown=0.03,
                volatility=0.10, beta=0.7, correlation_to_market=0.5
            )
        }
    
    def test_calculate_allocation(self, allocator, risk_metrics):
        """Test risk parity allocation calculation."""
        strategies = list(risk_metrics.keys())
        allocations = allocator.calculate_allocation(strategies, {}, risk_metrics)
        
        # Strategy 2 should get higher allocation (lower volatility)
        assert allocations["strategy_2"] > allocations["strategy_1"]
        
        # Total should sum to 1.0
        assert abs(sum(allocations.values()) - 1.0) < 1e-6
    
    def test_equal_volatilities(self, allocator):
        """Test allocation with equal volatilities."""
        risk_metrics = {
            "strategy_1": RiskMetrics(
                var_95=0.02, cvar_95=0.03, max_drawdown=0.05,
                volatility=0.12, beta=0.8, correlation_to_market=0.6
            ),
            "strategy_2": RiskMetrics(
                var_95=0.02, cvar_95=0.03, max_drawdown=0.05,
                volatility=0.12, beta=0.8, correlation_to_market=0.6
            )
        }
        
        strategies = list(risk_metrics.keys())
        allocations = allocator.calculate_allocation(strategies, {}, risk_metrics)
        
        # Should get equal allocation
        expected_allocation = 1.0 / len(strategies)
        for strategy in strategies:
            assert abs(allocations[strategy] - expected_allocation) < 1e-6


class TestCustomAllocator:
    """Test custom allocation algorithm."""
    
    @pytest.fixture
    def allocator(self):
        """Create custom allocator."""
        config = AllocationConfig(
            method=AllocationMethod.CUSTOM,
            custom_weights={"strategy_1": 0.3, "strategy_2": 0.7}
        )
        return CustomAllocator(config)
    
    def test_calculate_allocation(self, allocator):
        """Test custom allocation calculation."""
        strategies = ["strategy_1", "strategy_2"]
        allocations = allocator.calculate_allocation(strategies, {}, {})
        
        # Should match custom weights
        assert allocations["strategy_1"] == 0.3
        assert allocations["strategy_2"] == 0.7
        
        # Total should sum to 1.0
        assert abs(sum(allocations.values()) - 1.0) < 1e-6
    
    def test_missing_strategy_weight(self, allocator):
        """Test allocation with missing strategy weight."""
        strategies = ["strategy_1", "strategy_2", "strategy_3"]
        allocations = allocator.calculate_allocation(strategies, {}, {})
        
        # Strategy 3 should get zero allocation (not in custom weights)
        assert allocations.get("strategy_3", 0) == 0
        
        # Other strategies should be normalized
        total_specified = allocations["strategy_1"] + allocations["strategy_2"]
        assert abs(total_specified - 1.0) < 1e-6