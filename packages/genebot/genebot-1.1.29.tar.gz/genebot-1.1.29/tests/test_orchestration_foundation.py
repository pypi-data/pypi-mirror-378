"""
Tests for the orchestration system foundation and core interfaces.
"""

import pytest
from datetime import datetime
from pathlib import Path

from src.orchestration.config import (
    OrchestratorConfig, AllocationConfig, RiskConfig, MonitoringConfig,
    OptimizationConfig, StrategyConfig, AllocationMethod, RebalanceFrequency,
    OptimizationMethod, create_default_config
)
from src.orchestration.interfaces import (
    PerformanceMetrics, RiskMetrics, AllocationSnapshot, AttributionAnalysis
)
from src.orchestration.orchestrator import StrategyOrchestrator
from src.orchestration.allocation import AllocationManager
from src.orchestration.risk import OrchestratorRiskManager
from src.orchestration.performance import PerformanceMonitor


class TestOrchestratorConfig:
    """Test orchestrator configuration."""
    
    def test_default_config_creation(self):
        """Test creating default configuration."""
        config = create_default_config()
        
        assert isinstance(config, OrchestratorConfig)
        assert len(config.strategies) == 2
        assert config.max_concurrent_strategies == 20
        assert config.enable_dynamic_allocation is True
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = OrchestratorConfig()
        errors = config.validate()
        
        # Should have no errors with default values
        assert len(errors) == 0
    
    def test_invalid_allocation_config(self):
        """Test invalid allocation configuration."""
        with pytest.raises(ValueError):
            AllocationConfig(min_allocation=0.5, max_allocation=0.3)  # min > max
    
    def test_invalid_risk_config(self):
        """Test invalid risk configuration."""
        with pytest.raises(ValueError):
            RiskConfig(max_portfolio_drawdown=1.5)  # > 1.0
    
    def test_strategy_config_validation(self):
        """Test strategy configuration validation."""
        with pytest.raises(ValueError):
            StrategyConfig(type="", name="test")  # Empty type
        
        with pytest.raises(ValueError):
            StrategyConfig(type="TestStrategy", name="", allocation_weight=-1.0)  # Invalid weight
    
    def test_config_to_dict_conversion(self):
        """Test configuration to dictionary conversion."""
        config = create_default_config()
        config_dict = config.to_dict()
        
        assert 'orchestrator' in config_dict
        assert 'allocation' in config_dict['orchestrator']
        assert 'risk' in config_dict['orchestrator']
        assert 'strategies' in config_dict['orchestrator']
    
    def test_config_from_dict_creation(self):
        """Test creating configuration from dictionary."""
        config_dict = {
            'orchestrator': {
                'max_concurrent_strategies': 10,
                'allocation': {
                    'method': 'equal_weight',
                    'rebalance_frequency': 'weekly'
                },
                'strategies': [
                    {
                        'type': 'TestStrategy',
                        'name': 'test_strategy',
                        'enabled': True,
                        'allocation_weight': 1.0,
                        'parameters': {}
                    }
                ]
            }
        }
        
        config = OrchestratorConfig.from_dict(config_dict)
        
        assert config.max_concurrent_strategies == 10
        assert config.allocation.method == AllocationMethod.EQUAL_WEIGHT
        assert config.allocation.rebalance_frequency == RebalanceFrequency.WEEKLY
        assert len(config.strategies) == 1
        assert config.strategies[0].name == 'test_strategy'


class TestOrchestratorInterfaces:
    """Test orchestrator interfaces and data models."""
    
    def test_performance_metrics_creation(self):
        """Test performance metrics creation."""
        metrics = PerformanceMetrics(
            total_return=0.15,
            sharpe_ratio=1.2,
            max_drawdown=0.08,
            win_rate=0.65,
            profit_factor=1.8,
            volatility=0.12
        )
        
        assert metrics.total_return == 0.15
        assert metrics.sharpe_ratio == 1.2
        assert metrics.max_drawdown == 0.08
    
    def test_risk_metrics_creation(self):
        """Test risk metrics creation."""
        metrics = RiskMetrics(
            var_95=0.05,
            cvar_95=0.08,
            max_drawdown=0.10,
            volatility=0.15,
            correlation_to_market=0.7,
            beta=1.1
        )
        
        assert metrics.var_95 == 0.05
        assert metrics.beta == 1.1
    
    def test_allocation_snapshot_creation(self):
        """Test allocation snapshot creation."""
        snapshot = AllocationSnapshot(
            timestamp=datetime.now(),
            allocations={'strategy1': 0.4, 'strategy2': 0.6},
            reason='rebalancing',
            performance_trigger='performance_degradation'
        )
        
        assert len(snapshot.allocations) == 2
        assert snapshot.reason == 'rebalancing'
        assert snapshot.performance_trigger == 'performance_degradation'
    
    def test_attribution_analysis_creation(self):
        """Test attribution analysis creation."""
        analysis = AttributionAnalysis(
            strategy_contributions={'strategy1': 0.08, 'strategy2': 0.07},
            allocation_effect=0.02,
            selection_effect=0.03,
            interaction_effect=0.01,
            total_return=0.15,
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 12, 31)
        )
        
        assert len(analysis.strategy_contributions) == 2
        assert analysis.total_return == 0.15


class TestOrchestratorComponents:
    """Test orchestrator component implementations."""
    
    def test_allocation_manager_creation(self):
        """Test allocation manager creation."""
        config = AllocationConfig()
        manager = AllocationManager(config)
        
        assert manager.config == config
        assert len(manager.allocations) == 0
        assert len(manager.allocation_history) == 0
    
    def test_risk_manager_creation(self):
        """Test risk manager creation."""
        config = RiskConfig()
        manager = OrchestratorRiskManager(config)
        
        assert manager.config == config
    
    def test_performance_monitor_creation(self):
        """Test performance monitor creation."""
        config = MonitoringConfig()
        monitor = PerformanceMonitor(config)
        
        assert monitor.config == config
    
    def test_orchestrator_creation(self):
        """Test orchestrator creation."""
        config = create_default_config()
        allocation_manager = AllocationManager(config.allocation)
        risk_manager = OrchestratorRiskManager(config.risk)
        performance_monitor = PerformanceMonitor(config.monitoring)
        
        orchestrator = StrategyOrchestrator(
            config=config,
            allocation_manager=allocation_manager,
            risk_manager=risk_manager,
            performance_monitor=performance_monitor
        )
        
        assert orchestrator.config == config
        assert orchestrator.allocation_manager == allocation_manager
        assert orchestrator.risk_manager == risk_manager
        assert orchestrator.performance_monitor == performance_monitor
        assert orchestrator.is_running is False
    
    def test_orchestrator_start_stop(self):
        """Test orchestrator start and stop functionality."""
        config = create_default_config()
        allocation_manager = AllocationManager(config.allocation)
        risk_manager = OrchestratorRiskManager(config.risk)
        performance_monitor = PerformanceMonitor(config.monitoring)
        
        orchestrator = StrategyOrchestrator(
            config=config,
            allocation_manager=allocation_manager,
            risk_manager=risk_manager,
            performance_monitor=performance_monitor
        )
        
        # Test start
        assert orchestrator.start_orchestration() is True
        assert orchestrator.is_running is True
        
        # Test stop
        assert orchestrator.stop_orchestration() is True
        assert orchestrator.is_running is False
    
    def test_orchestrator_status(self):
        """Test orchestrator status reporting."""
        config = create_default_config()
        allocation_manager = AllocationManager(config.allocation)
        risk_manager = OrchestratorRiskManager(config.risk)
        performance_monitor = PerformanceMonitor(config.monitoring)
        
        orchestrator = StrategyOrchestrator(
            config=config,
            allocation_manager=allocation_manager,
            risk_manager=risk_manager,
            performance_monitor=performance_monitor
        )
        
        status = orchestrator.get_orchestration_status()
        
        assert 'is_running' in status
        assert 'active_strategies' in status
        assert 'total_strategies' in status
        assert 'strategy_states' in status
        assert 'strategy_weights' in status
        assert 'metrics' in status


class TestConfigurationFiles:
    """Test configuration file handling."""
    
    def test_simple_config_file_exists(self):
        """Test that simple configuration file exists."""
        config_path = Path("config/examples/simple_orchestrator_config.yaml")
        assert config_path.exists()
    
    def test_template_config_file_exists(self):
        """Test that template configuration file exists."""
        config_path = Path("config/templates/orchestrator_config_template.yaml")
        assert config_path.exists()
    
    def test_load_simple_config(self):
        """Test loading simple configuration file."""
        config_path = Path("config/examples/simple_orchestrator_config.yaml")
        
        if config_path.exists():
            config = OrchestratorConfig.from_yaml(config_path)
            
            assert isinstance(config, OrchestratorConfig)
            assert config.max_concurrent_strategies == 5
            assert len(config.strategies) == 3
            
            # Validate configuration
            errors = config.validate()
            assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__])