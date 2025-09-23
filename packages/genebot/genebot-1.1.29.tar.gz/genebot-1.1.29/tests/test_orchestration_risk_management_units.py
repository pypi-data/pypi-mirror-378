"""
Unit tests for orchestration risk management components.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.orchestration.risk import (
    OrchestratorRiskManager, PositionMonitor, CorrelationMonitor,
    DrawdownMonitor, RiskLimitValidator, EmergencyStopManager
)
from src.orchestration.config import RiskConfig
from src.orchestration.interfaces import RiskMetrics, TradingSignal, Portfolio, Position
from src.orchestration.exceptions import RiskLimitViolationError, EmergencyStopError


class TestOrchestratorRiskManager:
    """Test the main orchestrator risk manager."""
    
    @pytest.fixture
    def risk_config(self):
        """Create test risk configuration."""
        return RiskConfig(
            max_portfolio_drawdown=0.10,
            max_strategy_correlation=0.80,
            position_size_limit=0.05,
            stop_loss_threshold=0.02,
            max_daily_loss=0.03,
            max_position_concentration=0.25,
            correlation_lookback_period=30
        )
    
    @pytest.fixture
    def risk_manager(self, risk_config):
        """Create risk manager instance."""
        return OrchestratorRiskManager(risk_config)
    
    @pytest.fixture
    def sample_portfolio(self):
        """Create sample portfolio."""
        positions = [
            Position(
                symbol="BTCUSD",
                strategy="strategy_1",
                size=1000,
                entry_price=50000,
                current_price=51000,
                unrealized_pnl=1000
            ),
            Position(
                symbol="ETHUSD",
                strategy="strategy_2",
                size=10,
                entry_price=3000,
                current_price=3100,
                unrealized_pnl=1000
            )
        ]
        return Portfolio(
            total_value=100000,
            available_cash=20000,
            positions=positions,
            total_pnl=2000,
            daily_pnl=500
        )
    
    @pytest.fixture
    def sample_signal(self):
        """Create sample trading signal."""
        return TradingSignal(
            strategy="strategy_1",
            symbol="BTCUSD",
            action="BUY",
            quantity=0.5,
            price=50000,
            confidence=0.8,
            timestamp=datetime.now()
        )
    
    def test_initialization(self, risk_manager, risk_config):
        """Test risk manager initialization."""
        assert risk_manager.config == risk_config
        assert isinstance(risk_manager.position_monitor, PositionMonitor)
        assert isinstance(risk_manager.correlation_monitor, CorrelationMonitor)
        assert isinstance(risk_manager.drawdown_monitor, DrawdownMonitor)
        assert isinstance(risk_manager.limit_validator, RiskLimitValidator)
        assert isinstance(risk_manager.emergency_stop, EmergencyStopManager)
    
    def test_validate_signal_success(self, risk_manager, sample_signal, sample_portfolio):
        """Test successful signal validation."""
        # Mock all validators to return True
        with patch.object(risk_manager.limit_validator, 'validate_position_size', return_value=True), \
             patch.object(risk_manager.limit_validator, 'validate_concentration', return_value=True), \
             patch.object(risk_manager.drawdown_monitor, 'check_drawdown_limits', return_value=True), \
             patch.object(risk_manager.correlation_monitor, 'check_correlation_limits', return_value=True):
            
            result = risk_manager.validate_signal(sample_signal, sample_portfolio)
            assert result is True
    
    def test_validate_signal_position_size_violation(self, risk_manager, sample_signal, sample_portfolio):
        """Test signal validation with position size violation."""
        with patch.object(risk_manager.limit_validator, 'validate_position_size', return_value=False):
            result = risk_manager.validate_signal(sample_signal, sample_portfolio)
            assert result is False
    
    def test_validate_signal_drawdown_violation(self, risk_manager, sample_signal, sample_portfolio):
        """Test signal validation with drawdown violation."""
        with patch.object(risk_manager.limit_validator, 'validate_position_size', return_value=True), \
             patch.object(risk_manager.drawdown_monitor, 'check_drawdown_limits', return_value=False):
            result = risk_manager.validate_signal(sample_signal, sample_portfolio)
            assert result is False
    
    def test_check_correlation_limits(self, risk_manager):
        """Test correlation limits checking."""
        strategies = ["strategy_1", "strategy_2", "strategy_3"]
        
        with patch.object(risk_manager.correlation_monitor, 'check_correlation_limits', return_value=True) as mock_check:
            result = risk_manager.check_correlation_limits(strategies)
            assert result is True
            mock_check.assert_called_once_with(strategies)
    
    def test_trigger_emergency_stop(self, risk_manager):
        """Test emergency stop triggering."""
        reason = "Maximum drawdown exceeded"
        
        with patch.object(risk_manager.emergency_stop, 'trigger_stop') as mock_trigger:
            result = risk_manager.trigger_emergency_stop(reason)
            mock_trigger.assert_called_once_with(reason)
    
    def test_get_risk_metrics(self, risk_manager, sample_portfolio):
        """Test risk metrics calculation."""
        with patch.object(risk_manager.position_monitor, 'calculate_portfolio_risk') as mock_calc:
            mock_calc.return_value = RiskMetrics(
                var_95=0.02, cvar_95=0.03, max_drawdown=0.05,
                volatility=0.12, beta=0.8, correlation_to_market=0.6
            )
            
            metrics = risk_manager.get_risk_metrics(sample_portfolio)
            assert isinstance(metrics, RiskMetrics)
            mock_calc.assert_called_once_with(sample_portfolio)


class TestPositionMonitor:
    """Test position monitoring component."""
    
    @pytest.fixture
    def position_monitor(self):
        """Create position monitor."""
        config = RiskConfig()
        return PositionMonitor(config)
    
    @pytest.fixture
    def sample_positions(self):
        """Create sample positions."""
        return [
            Position(
                symbol="BTCUSD", strategy="strategy_1", size=1000,
                entry_price=50000, current_price=51000, unrealized_pnl=1000
            ),
            Position(
                symbol="ETHUSD", strategy="strategy_2", size=10,
                entry_price=3000, current_price=2900, unrealized_pnl=-1000
            )
        ]
    
    def test_calculate_position_size(self, position_monitor, sample_positions):
        """Test position size calculation."""
        portfolio_value = 100000
        position_sizes = position_monitor.calculate_position_sizes(sample_positions, portfolio_value)
        
        # BTC position: 1000 * 51000 / 100000 = 0.51
        assert abs(position_sizes["BTCUSD"] - 0.51) < 1e-6
        
        # ETH position: 10 * 2900 / 100000 = 0.29
        assert abs(position_sizes["ETHUSD"] - 0.29) < 1e-6
    
    def test_calculate_portfolio_risk(self, position_monitor):
        """Test portfolio risk calculation."""
        portfolio = Portfolio(
            total_value=100000,
            available_cash=20000,
            positions=[],
            total_pnl=2000,
            daily_pnl=500
        )
        
        # Mock historical returns for risk calculation
        with patch.object(position_monitor, '_get_historical_returns') as mock_returns:
            mock_returns.return_value = np.array([0.01, -0.02, 0.015, -0.01, 0.005])
            
            risk_metrics = position_monitor.calculate_portfolio_risk(portfolio)
            
            assert isinstance(risk_metrics, RiskMetrics)
            assert risk_metrics.volatility > 0
            assert risk_metrics.var_95 > 0
            assert risk_metrics.cvar_95 > 0
    
    def test_check_position_concentration(self, position_monitor, sample_positions):
        """Test position concentration checking."""
        portfolio_value = 100000
        max_concentration = 0.30
        
        # BTC position is 51% of portfolio - should exceed limit
        result = position_monitor.check_position_concentration(
            sample_positions, portfolio_value, max_concentration
        )
        assert result is False
        
        # With higher limit, should pass
        result = position_monitor.check_position_concentration(
            sample_positions, portfolio_value, 0.60
        )
        assert result is True


class TestCorrelationMonitor:
    """Test correlation monitoring component."""
    
    @pytest.fixture
    def correlation_monitor(self):
        """Create correlation monitor."""
        config = RiskConfig(max_strategy_correlation=0.80)
        return CorrelationMonitor(config)
    
    def test_calculate_strategy_correlations(self, correlation_monitor):
        """Test strategy correlation calculation."""
        strategies = ["strategy_1", "strategy_2", "strategy_3"]
        
        # Mock returns data
        returns_data = {
            "strategy_1": np.array([0.01, -0.02, 0.015, -0.01, 0.005]),
            "strategy_2": np.array([0.012, -0.018, 0.013, -0.008, 0.003]),
            "strategy_3": np.array([-0.005, 0.01, -0.008, 0.012, -0.002])
        }
        
        with patch.object(correlation_monitor, '_get_strategy_returns', return_value=returns_data):
            correlations = correlation_monitor.calculate_strategy_correlations(strategies)
            
            assert isinstance(correlations, dict)
            assert len(correlations) == 3  # 3 pairs for 3 strategies
            
            # Check correlation values are between -1 and 1
            for pair, corr in correlations.items():
                assert -1 <= corr <= 1
    
    def test_check_correlation_limits(self, correlation_monitor):
        """Test correlation limits checking."""
        strategies = ["strategy_1", "strategy_2"]
        
        # Mock high correlation
        with patch.object(correlation_monitor, 'calculate_strategy_correlations') as mock_calc:
            mock_calc.return_value = {("strategy_1", "strategy_2"): 0.85}
            
            result = correlation_monitor.check_correlation_limits(strategies)
            assert result is False  # Exceeds 0.80 limit
        
        # Mock acceptable correlation
        with patch.object(correlation_monitor, 'calculate_strategy_correlations') as mock_calc:
            mock_calc.return_value = {("strategy_1", "strategy_2"): 0.75}
            
            result = correlation_monitor.check_correlation_limits(strategies)
            assert result is True
    
    def test_identify_highly_correlated_strategies(self, correlation_monitor):
        """Test identification of highly correlated strategies."""
        correlations = {
            ("strategy_1", "strategy_2"): 0.85,
            ("strategy_1", "strategy_3"): 0.60,
            ("strategy_2", "strategy_3"): 0.90
        }
        
        highly_correlated = correlation_monitor.identify_highly_correlated_strategies(correlations)
        
        # Should identify the two pairs exceeding 0.80 threshold
        expected_pairs = [("strategy_1", "strategy_2"), ("strategy_2", "strategy_3")]
        assert len(highly_correlated) == 2
        for pair in expected_pairs:
            assert pair in highly_correlated or (pair[1], pair[0]) in highly_correlated


class TestDrawdownMonitor:
    """Test drawdown monitoring component."""
    
    @pytest.fixture
    def drawdown_monitor(self):
        """Create drawdown monitor."""
        config = RiskConfig(max_portfolio_drawdown=0.10)
        return DrawdownMonitor(config)
    
    def test_calculate_current_drawdown(self, drawdown_monitor):
        """Test current drawdown calculation."""
        portfolio_values = [100000, 105000, 102000, 98000, 95000]
        
        drawdown = drawdown_monitor.calculate_current_drawdown(portfolio_values)
        
        # Peak was 105000, current is 95000
        # Drawdown = (105000 - 95000) / 105000 = 0.095
        expected_drawdown = 0.095
        assert abs(drawdown - expected_drawdown) < 1e-6
    
    def test_calculate_max_drawdown(self, drawdown_monitor):
        """Test maximum drawdown calculation."""
        portfolio_values = [100000, 105000, 102000, 98000, 95000, 97000]
        
        max_drawdown = drawdown_monitor.calculate_max_drawdown(portfolio_values)
        
        # Maximum drawdown occurred from peak 105000 to trough 95000
        expected_max_drawdown = 0.095
        assert abs(max_drawdown - expected_max_drawdown) < 1e-6
    
    def test_check_drawdown_limits(self, drawdown_monitor):
        """Test drawdown limits checking."""
        # Mock current drawdown exceeding limit
        with patch.object(drawdown_monitor, 'get_current_portfolio_drawdown', return_value=0.12):
            result = drawdown_monitor.check_drawdown_limits()
            assert result is False  # Exceeds 0.10 limit
        
        # Mock acceptable drawdown
        with patch.object(drawdown_monitor, 'get_current_portfolio_drawdown', return_value=0.08):
            result = drawdown_monitor.check_drawdown_limits()
            assert result is True
    
    def test_get_drawdown_alert_level(self, drawdown_monitor):
        """Test drawdown alert level determination."""
        # No alert for low drawdown
        alert_level = drawdown_monitor.get_drawdown_alert_level(0.03)
        assert alert_level == "none"
        
        # Warning for moderate drawdown
        alert_level = drawdown_monitor.get_drawdown_alert_level(0.07)
        assert alert_level == "warning"
        
        # Critical for high drawdown
        alert_level = drawdown_monitor.get_drawdown_alert_level(0.12)
        assert alert_level == "critical"


class TestRiskLimitValidator:
    """Test risk limit validation component."""
    
    @pytest.fixture
    def validator(self):
        """Create risk limit validator."""
        config = RiskConfig(
            position_size_limit=0.05,
            max_position_concentration=0.25,
            max_daily_loss=0.03
        )
        return RiskLimitValidator(config)
    
    def test_validate_position_size(self, validator):
        """Test position size validation."""
        signal = TradingSignal(
            strategy="strategy_1", symbol="BTCUSD", action="BUY",
            quantity=0.5, price=50000, confidence=0.8, timestamp=datetime.now()
        )
        portfolio_value = 100000
        
        # Position value: 0.5 * 50000 = 25000
        # Position size: 25000 / 100000 = 0.25 (exceeds 0.05 limit)
        result = validator.validate_position_size(signal, portfolio_value)
        assert result is False
        
        # Smaller position should pass
        signal.quantity = 0.001  # 0.001 * 50000 = 50, 50/100000 = 0.0005
        result = validator.validate_position_size(signal, portfolio_value)
        assert result is True
    
    def test_validate_concentration(self, validator):
        """Test concentration validation."""
        existing_positions = [
            Position(
                symbol="BTCUSD", strategy="strategy_1", size=1000,
                entry_price=50000, current_price=50000, unrealized_pnl=0
            )
        ]
        
        new_signal = TradingSignal(
            strategy="strategy_2", symbol="BTCUSD", action="BUY",
            quantity=0.5, price=50000, confidence=0.8, timestamp=datetime.now()
        )
        portfolio_value = 100000
        
        # Existing position: 1000 * 50000 = 50M (50% of portfolio)
        # New position: 0.5 * 50000 = 25K (0.25% of portfolio)
        # Total concentration would exceed 25% limit
        result = validator.validate_concentration(new_signal, existing_positions, portfolio_value)
        assert result is False
    
    def test_validate_daily_loss_limit(self, validator):
        """Test daily loss limit validation."""
        portfolio = Portfolio(
            total_value=100000, available_cash=20000, positions=[],
            total_pnl=0, daily_pnl=-4000  # -4% daily loss
        )
        
        # Daily loss exceeds 3% limit
        result = validator.validate_daily_loss_limit(portfolio)
        assert result is False
        
        # Acceptable daily loss
        portfolio.daily_pnl = -2000  # -2% daily loss
        result = validator.validate_daily_loss_limit(portfolio)
        assert result is True


class TestEmergencyStopManager:
    """Test emergency stop management component."""
    
    @pytest.fixture
    def emergency_stop(self):
        """Create emergency stop manager."""
        config = RiskConfig()
        return EmergencyStopManager(config)
    
    def test_trigger_stop(self, emergency_stop):
        """Test emergency stop triggering."""
        reason = "Maximum drawdown exceeded"
        
        with patch.object(emergency_stop, '_notify_administrators') as mock_notify, \
             patch.object(emergency_stop, '_halt_all_strategies') as mock_halt, \
             patch.object(emergency_stop, '_close_all_positions') as mock_close:
            
            emergency_stop.trigger_stop(reason)
            
            assert emergency_stop.is_stopped is True
            assert emergency_stop.stop_reason == reason
            mock_notify.assert_called_once()
            mock_halt.assert_called_once()
            mock_close.assert_called_once()
    
    def test_reset_stop(self, emergency_stop):
        """Test emergency stop reset."""
        # First trigger a stop
        emergency_stop.trigger_stop("Test reason")
        assert emergency_stop.is_stopped is True
        
        # Then reset
        emergency_stop.reset_stop()
        assert emergency_stop.is_stopped is False
        assert emergency_stop.stop_reason is None
    
    def test_check_stop_conditions(self, emergency_stop):
        """Test stop condition checking."""
        portfolio = Portfolio(
            total_value=100000, available_cash=20000, positions=[],
            total_pnl=-15000, daily_pnl=-12000  # Severe losses
        )
        
        with patch.object(emergency_stop, 'trigger_stop') as mock_trigger:
            emergency_stop.check_stop_conditions(portfolio)
            
            # Should trigger stop due to severe losses
            mock_trigger.assert_called()
    
    def test_is_stop_active(self, emergency_stop):
        """Test stop status checking."""
        assert emergency_stop.is_stop_active() is False
        
        emergency_stop.trigger_stop("Test reason")
        assert emergency_stop.is_stop_active() is True
        
        emergency_stop.reset_stop()
        assert emergency_stop.is_stop_active() is False