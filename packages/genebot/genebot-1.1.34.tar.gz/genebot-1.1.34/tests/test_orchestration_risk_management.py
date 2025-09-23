"""
Tests for the orchestration risk management system.

This module tests the comprehensive risk management implementation
including portfolio-level controls and risk constraint enforcement.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from src.orchestration.risk import (
    OrchestratorRiskManager, PortfolioDrawdownMonitor, PositionSizeValidator,
    CorrelationMonitor, EmergencyStopManager
)
from src.orchestration.risk_enforcement import (
    PreTradeRiskValidator, RiskBasedPositionSizer, RiskViolationAlertSystem,
    DynamicRiskLimitAdjuster, RiskLevel, AlertSeverity
)
from src.orchestration.config import RiskConfig
from src.models.data_models import TradingSignal, Position, UnifiedMarketData, SignalAction
from src.markets.types import MarketType, UnifiedSymbol


class TestPortfolioDrawdownMonitor:
    """Test portfolio drawdown monitoring functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            max_portfolio_drawdown=0.10,
            position_size_limit=0.05
        )
        self.monitor = PortfolioDrawdownMonitor(self.config)
    
    def test_initial_state(self):
        """Test initial monitor state."""
        assert self.monitor.peak_value == 0.0
        assert self.monitor.current_drawdown_event is None
        assert len(self.monitor.drawdown_history) == 0
    
    def test_peak_value_tracking(self):
        """Test peak value tracking."""
        # First update sets peak
        result = self.monitor.update_portfolio_value(10000.0)
        assert self.monitor.peak_value == 10000.0
        assert result['current_drawdown_pct'] == 0.0
        
        # Higher value updates peak
        result = self.monitor.update_portfolio_value(12000.0)
        assert self.monitor.peak_value == 12000.0
        assert result['current_drawdown_pct'] == 0.0
        
        # Lower value creates drawdown
        result = self.monitor.update_portfolio_value(11000.0)
        assert self.monitor.peak_value == 12000.0
        assert result['current_drawdown_pct'] == pytest.approx(0.0833, rel=1e-3)
    
    def test_drawdown_event_creation(self):
        """Test drawdown event creation and tracking."""
        # Set initial peak
        self.monitor.update_portfolio_value(10000.0)
        
        # Create drawdown
        result = self.monitor.update_portfolio_value(9000.0)
        assert self.monitor.current_drawdown_event is not None
        assert result['is_in_drawdown'] is True
        assert result['current_drawdown_pct'] == 0.1
        
        # Deepen drawdown
        result = self.monitor.update_portfolio_value(8500.0)
        assert result['current_drawdown_pct'] == 0.15
        assert self.monitor.current_drawdown_event.max_drawdown_pct == 0.15
    
    def test_drawdown_recovery(self):
        """Test drawdown recovery detection."""
        # Create drawdown
        self.monitor.update_portfolio_value(10000.0)
        self.monitor.update_portfolio_value(9000.0)
        assert self.monitor.current_drawdown_event is not None
        
        # Recover (need to exceed peak * 0.99)
        self.monitor.update_portfolio_value(10100.0)
        assert self.monitor.current_drawdown_event is None
        assert len(self.monitor.drawdown_history) == 1
    
    def test_emergency_recommendations(self):
        """Test emergency recommendations for severe drawdowns."""
        self.monitor.update_portfolio_value(10000.0)
        
        # Severe drawdown
        result = self.monitor.update_portfolio_value(8000.0)  # 20% drawdown
        assert result['should_halt_trading'] is True
        assert 'EMERGENCY' in str(result['recommendations'])


class TestPositionSizeValidator:
    """Test position size validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(position_size_limit=0.05)
        self.validator = PositionSizeValidator(self.config)
    
    def test_valid_position_size(self):
        """Test validation of valid position sizes."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0  # Add quantity as attribute
        
        is_valid, reason, adjusted_size = self.validator.validate_position_size(
            signal, "test_strategy", 1000000.0  # $1M portfolio
        )
        
        assert is_valid is True
        assert adjusted_size == 1.0
        assert "validated" in reason.lower()
    
    def test_oversized_position(self):
        """Test validation of oversized positions."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 2.0  # $100k position on $1M portfolio = 10%
        
        is_valid, reason, adjusted_size = self.validator.validate_position_size(
            signal, "test_strategy", 1000000.0
        )
        
        assert is_valid is False
        assert "exceeds limit" in reason
        assert adjusted_size < signal.quantity
    
    def test_exposure_tracking(self):
        """Test position exposure tracking."""
        # Add position
        self.validator.update_position("strategy1", "BTCUSD", 50000.0)
        
        report = self.validator.get_exposure_report(1000000.0)
        assert report['total_exposure_pct'] == 0.05
        assert "strategy1" in report['strategy_exposures']
        assert "BTCUSD" in report['symbol_exposures']


class TestCorrelationMonitor:
    """Test strategy correlation monitoring."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            max_strategy_correlation=0.8,
            correlation_lookback=30
        )
        self.monitor = CorrelationMonitor(self.config)
    
    def test_correlation_calculation(self):
        """Test correlation calculation between strategies."""
        # Add correlated returns
        returns1 = [0.01, 0.02, -0.01, 0.015, -0.005] * 4  # 20 returns
        returns2 = [0.012, 0.018, -0.008, 0.013, -0.003] * 4  # Highly correlated
        
        for r1, r2 in zip(returns1, returns2):
            self.monitor.update_strategy_return("strategy1", r1)
            self.monitor.update_strategy_return("strategy2", r2)
        
        # Force correlation update
        self.monitor._update_correlations()
        
        correlation = self.monitor.correlation_matrix.get(("strategy1", "strategy2"), 0.0)
        assert correlation > 0.8  # Should be highly correlated
    
    def test_correlation_limit_violation(self):
        """Test correlation limit violation detection."""
        # Add highly correlated returns
        for i in range(20):
            return_val = 0.01 * (1 if i % 2 == 0 else -1)
            self.monitor.update_strategy_return("strategy1", return_val)
            self.monitor.update_strategy_return("strategy2", return_val)  # Identical returns
        
        self.monitor._update_correlations()
        
        is_valid, violations = self.monitor.check_correlation_limits(["strategy1", "strategy2"])
        assert is_valid is False
        assert len(violations) > 0


class TestEmergencyStopManager:
    """Test emergency stop procedures."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            max_portfolio_drawdown=0.10,
            emergency_stop_conditions=['max_drawdown_exceeded', 'strategy_failure_cascade']
        )
        self.manager = EmergencyStopManager(self.config)
    
    def test_emergency_stop_trigger(self):
        """Test emergency stop triggering."""
        portfolio_data = {
            'current_drawdown_pct': 0.12,  # Exceeds 10% limit
            'correlation_violations': [],
            'risk_violations': []
        }
        
        should_stop, reason = self.manager.check_emergency_conditions(portfolio_data)
        assert should_stop is True
        assert "drawdown exceeded" in reason.lower()
        assert self.manager.emergency_stop_active is True
    
    def test_strategy_failure_cascade(self):
        """Test strategy failure cascade detection."""
        # Record multiple failures quickly
        self.manager.record_strategy_failure("strategy1")
        self.manager.record_strategy_failure("strategy2")
        self.manager.record_strategy_failure("strategy3")
        
        portfolio_data = {
            'current_drawdown_pct': 0.05,
            'correlation_violations': [],
            'risk_violations': []
        }
        
        should_stop, reason = self.manager.check_emergency_conditions(portfolio_data)
        assert should_stop is True
        assert "cascade" in reason.lower()
    
    def test_emergency_stop_reset(self):
        """Test emergency stop reset functionality."""
        # Trigger emergency stop
        self.manager._trigger_emergency_stop("Test reason")
        assert self.manager.emergency_stop_active is True
        
        # Reset should require manual override
        assert self.manager.reset_emergency_stop(manual_override=False) is False
        assert self.manager.emergency_stop_active is True
        
        # Manual override should work
        assert self.manager.reset_emergency_stop(manual_override=True) is True
        assert self.manager.emergency_stop_active is False


class TestDynamicRiskLimitAdjuster:
    """Test dynamic risk limit adjustment."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(position_size_limit=0.05)
        self.adjuster = DynamicRiskLimitAdjuster(self.config)
    
    def test_volatility_adjustment(self):
        """Test risk limit adjustment based on volatility."""
        # Add low volatility data
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USD",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSD"
        )
        low_vol_data = [
            UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open=Decimal("50000.0"),
                high=Decimal("50100.0"),
                low=Decimal("49900.0"),
                close=Decimal("50050.0"),
                volume=Decimal("1000.0"),
                source="test_exchange",
                market_type=MarketType.CRYPTO
            )
        ]
        
        for _ in range(15):  # Need enough data points
            self.adjuster.update_market_conditions(low_vol_data)
        
        # Should allow larger positions in low volatility
        adjusted_limit = self.adjuster.get_adjusted_limit('position_size_limit')
        assert adjusted_limit >= self.config.position_size_limit
    
    def test_performance_adjustment(self):
        """Test risk limit adjustment based on performance."""
        # Poor performance should reduce limits
        self.adjuster.update_portfolio_performance(-0.08)  # -8% performance
        
        adjusted_limit = self.adjuster.get_adjusted_limit('position_size_limit')
        assert adjusted_limit <= self.config.position_size_limit


class TestRiskBasedPositionSizer:
    """Test risk-based position sizing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(position_size_limit=0.05)
        self.adjuster = DynamicRiskLimitAdjuster(self.config)
        self.sizer = RiskBasedPositionSizer(self.config, self.adjuster)
    
    def test_fixed_percentage_sizing(self):
        """Test fixed percentage position sizing."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0
        
        size, details = self.sizer.calculate_position_size(
            signal, "test_strategy", 1000000.0, [], method="FIXED_PERCENTAGE"
        )
        
        assert size > 0
        assert details['method_used'] == "FIXED_PERCENTAGE"
        assert 'percentage_used' in details['method_details']
    
    def test_volatility_adjusted_sizing(self):
        """Test volatility-adjusted position sizing."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0
        
        # Add some volatility data
        self.sizer.update_symbol_volatility("BTCUSD", [50000, 51000, 49000, 50500])
        
        size, details = self.sizer.calculate_position_size(
            signal, "test_strategy", 1000000.0, [], method="VOLATILITY_ADJUSTED"
        )
        
        assert size > 0
        assert details['method_used'] == "VOLATILITY_ADJUSTED"
        assert 'volatility_adjustment' in details['method_details']
    
    def test_confidence_adjustment(self):
        """Test position size adjustment based on signal confidence."""
        high_confidence_signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.9,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        high_confidence_signal.quantity = 1.0
        
        low_confidence_signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.3,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        low_confidence_signal.quantity = 1.0
        
        high_size, _ = self.sizer.calculate_position_size(
            high_confidence_signal, "test_strategy", 1000000.0, []
        )
        
        low_size, _ = self.sizer.calculate_position_size(
            low_confidence_signal, "test_strategy", 1000000.0, []
        )
        
        assert high_size > low_size


class TestRiskViolationAlertSystem:
    """Test risk violation alert system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig()
        self.alert_system = RiskViolationAlertSystem(self.config)
    
    def test_alert_creation(self):
        """Test risk alert creation."""
        from src.orchestration.risk_enforcement import RiskConstraint
        
        constraint = RiskConstraint(
            name="test_constraint",
            description="Test constraint violation",
            constraint_type="HARD",
            limit_value=0.05,
            current_value=0.08,  # Violation
            violation_threshold=1.0,
            enforcement_action="REJECT"
        )
        
        alert = self.alert_system.create_alert(constraint, "test_strategy", "BTCUSD")
        
        assert alert is not None
        assert alert.constraint_name == "test_constraint"
        assert alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]
        assert alert.violation_ratio > 1.0
    
    def test_alert_cooldown(self):
        """Test alert cooldown functionality."""
        from src.orchestration.risk_enforcement import RiskConstraint
        
        constraint = RiskConstraint(
            name="test_constraint",
            description="Test constraint",
            constraint_type="HARD",
            limit_value=0.05,
            current_value=0.08,
            violation_threshold=1.0,
            enforcement_action="REJECT"
        )
        
        # Create first alert
        alert1 = self.alert_system.create_alert(constraint, "test_strategy", "BTCUSD")
        assert alert1 is not None
        
        # Immediate second alert should be blocked by cooldown
        alert2 = self.alert_system.create_alert(constraint, "test_strategy", "BTCUSD")
        assert alert2 is None
    
    def test_alert_acknowledgment(self):
        """Test alert acknowledgment."""
        from src.orchestration.risk_enforcement import RiskConstraint
        
        constraint = RiskConstraint(
            name="test_constraint",
            description="Test constraint",
            constraint_type="HARD",
            limit_value=0.05,
            current_value=0.08,
            violation_threshold=1.0,
            enforcement_action="REJECT"
        )
        
        alert = self.alert_system.create_alert(constraint)
        assert alert.acknowledged is False
        
        success = self.alert_system.acknowledge_alert(alert.alert_id)
        assert success is True
        assert alert.acknowledged is True


class TestPreTradeRiskValidator:
    """Test comprehensive pre-trade risk validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            max_portfolio_drawdown=0.10,
            position_size_limit=0.05,
            max_leverage=2.0
        )
        self.validator = PreTradeRiskValidator(self.config)
    
    def test_valid_trade_approval(self):
        """Test approval of valid trades."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0
        
        assessment = self.validator.validate_trade(
            signal, "test_strategy", 1000000.0, []
        )
        
        assert assessment.is_approved is True
        assert assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        assert assessment.recommended_action in ["APPROVE", "ADJUST_SIZE"]
    
    def test_oversized_trade_rejection(self):
        """Test rejection of oversized trades."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 3.0  # $150k on $1M portfolio = 15%
        
        assessment = self.validator.validate_trade(
            signal, "test_strategy", 1000000.0, []
        )
        
        assert assessment.is_approved is False
        assert assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert "position_size_limit" in assessment.constraint_violations
    
    def test_low_confidence_signal(self):
        """Test handling of low confidence signals."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.2,  # Very low confidence
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0
        
        assessment = self.validator.validate_trade(
            signal, "test_strategy", 1000000.0, []
        )
        
        # Should still be approved but with reduced position size
        assert "Low signal confidence" in assessment.reasons
        assert assessment.position_size_adjustment < 1.0


class TestOrchestratorRiskManager:
    """Test the main orchestrator risk manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RiskConfig(
            max_portfolio_drawdown=0.10,
            position_size_limit=0.05,
            max_strategy_correlation=0.8
        )
        self.risk_manager = OrchestratorRiskManager(self.config)
    
    def test_signal_validation(self):
        """Test basic signal validation."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0
        
        portfolio = {'total_value': 1000000.0}
        
        is_valid = self.risk_manager.validate_signal(signal, portfolio)
        assert is_valid is True
    
    def test_comprehensive_trade_validation(self):
        """Test comprehensive trade validation."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0
        
        result = self.risk_manager.validate_trade_comprehensive(
            signal, "test_strategy", 1000000.0, []
        )
        
        assert 'is_approved' in result
        assert 'risk_level' in result
        assert 'recommended_action' in result
        assert 'position_size_adjustment' in result
    
    def test_position_size_calculation(self):
        """Test risk-adjusted position size calculation."""
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0
        
        size = self.risk_manager.calculate_position_size(signal, {'total_value': 1000000.0})
        assert size > 0
        assert size <= 1.0  # Should not exceed original quantity significantly
    
    def test_emergency_stop_trigger(self):
        """Test emergency stop triggering."""
        success = self.risk_manager.trigger_emergency_stop("Test emergency")
        assert success is True
        
        # Subsequent signals should be rejected
        signal = TradingSignal(
            symbol="BTCUSD",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000.0")
        )
        signal.quantity = 1.0
        
        is_valid = self.risk_manager.validate_signal(signal, {'total_value': 1000000.0})
        assert is_valid is False
    
    def test_comprehensive_risk_report(self):
        """Test comprehensive risk report generation."""
        report = self.risk_manager.get_comprehensive_risk_report()
        
        assert 'timestamp' in report
        assert 'portfolio_value' in report
        assert 'drawdown_status' in report
        assert 'correlation_report' in report
        assert 'exposure_report' in report
        assert 'emergency_status' in report
        assert 'validation_report' in report
        assert 'alert_summary' in report
        assert 'constraint_status' in report
        assert 'risk_limits' in report
    
    def test_alert_management(self):
        """Test risk alert management."""
        # Get initial alerts (should be empty)
        alerts = self.risk_manager.get_active_risk_alerts()
        assert isinstance(alerts, list)
        
        # Test alert filtering
        critical_alerts = self.risk_manager.get_active_risk_alerts(severity_filter="CRITICAL")
        assert isinstance(critical_alerts, list)
    
    def test_dynamic_limit_updates(self):
        """Test dynamic risk limit updates."""
        symbol = UnifiedSymbol(
            base_asset="BTC",
            quote_asset="USD",
            market_type=MarketType.CRYPTO,
            native_symbol="BTCUSD"
        )
        market_data = [
            UnifiedMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open=Decimal("50000.0"),
                high=Decimal("51000.0"),
                low=Decimal("49000.0"),
                close=Decimal("50500.0"),
                volume=Decimal("1000.0"),
                source="test_exchange",
                market_type=MarketType.CRYPTO
            )
        ]
        
        # Should not raise exceptions
        self.risk_manager.update_dynamic_risk_limits(market_data, -0.02)
        
        # Get updated report
        report = self.risk_manager.get_comprehensive_risk_report()
        assert 'dynamic_adjustments' in report['risk_limits']


if __name__ == "__main__":
    pytest.main([__file__])