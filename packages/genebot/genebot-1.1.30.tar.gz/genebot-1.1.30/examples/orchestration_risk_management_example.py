"""
Comprehensive Risk Management System Example

This example demonstrates the unified strategy orchestration risk management system,
including portfolio-level controls and risk constraint enforcement.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestration.risk import OrchestratorRiskManager
from src.orchestration.config import RiskConfig
from src.models.data_models import TradingSignal, Position, UnifiedMarketData, SignalAction
from src.markets.types import MarketType, UnifiedSymbol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_signal(symbol: str, confidence: float, quantity: float, price: float) -> TradingSignal:
    """Create a sample trading signal."""
    signal = TradingSignal(
        symbol=symbol,
        action=SignalAction.BUY,
        confidence=confidence,
        timestamp=datetime.now(),
        strategy_name="sample_strategy",
        price=Decimal(str(price))
    )
    signal.quantity = quantity
    return signal


def create_sample_market_data(symbol_str: str, price: float, volatility: float = 0.02) -> UnifiedMarketData:
    """Create sample market data."""
    symbol = UnifiedSymbol(
        base_asset=symbol_str.split('/')[0],
        quote_asset=symbol_str.split('/')[1],
        market_type=MarketType.CRYPTO,
        native_symbol=symbol_str.replace('/', '')
    )
    
    high = price * (1 + volatility)
    low = price * (1 - volatility)
    
    return UnifiedMarketData(
        symbol=symbol,
        timestamp=datetime.now(),
        open=Decimal(str(price * 0.999)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(price)),
        volume=Decimal("1000.0"),
        source="sample_exchange",
        market_type=MarketType.CRYPTO
    )


def create_sample_position(symbol: str, quantity: float, entry_price: float, current_price: float) -> Position:
    """Create a sample position."""
    unrealized_pnl = quantity * (current_price - entry_price)
    unrealized_pnl_pct = (current_price - entry_price) / entry_price * 100
    
    return Position(
        id=f"pos_{symbol}",
        symbol=symbol,
        side="BUY",
        amount=Decimal(str(quantity)),
        entry_price=Decimal(str(entry_price)),
        current_price=Decimal(str(current_price)),
        market_value=Decimal(str(quantity * current_price)),
        unrealized_pnl=Decimal(str(unrealized_pnl)),
        unrealized_pnl_percentage=unrealized_pnl_pct,
        timestamp=datetime.now(),
        exchange="sample_exchange"
    )


async def demonstrate_basic_risk_validation():
    """Demonstrate basic risk validation functionality."""
    print("\n" + "="*60)
    print("BASIC RISK VALIDATION DEMONSTRATION")
    print("="*60)
    
    # Create risk manager with conservative settings
    config = RiskConfig(
        max_portfolio_drawdown=0.10,  # 10% max drawdown
        position_size_limit=0.05,     # 5% max position size
        max_strategy_correlation=0.80, # 80% max correlation
        stop_loss_threshold=0.02,     # 2% stop loss
        max_leverage=2.0              # 2x max leverage
    )
    
    risk_manager = OrchestratorRiskManager(config)
    
    # Test 1: Valid signal validation
    print("\n1. Testing valid signal validation...")
    valid_signal = create_sample_signal("BTCUSD", 0.8, 1.0, 50000.0)
    portfolio = {'total_value': 1000000.0}  # $1M portfolio
    
    is_valid = risk_manager.validate_signal(valid_signal, portfolio)
    print(f"   Valid signal approved: {is_valid}")
    
    # Test 2: Oversized position rejection
    print("\n2. Testing oversized position rejection...")
    oversized_signal = create_sample_signal("BTCUSD", 0.8, 3.0, 50000.0)  # $150k position = 15%
    
    is_valid = risk_manager.validate_signal(oversized_signal, portfolio)
    print(f"   Oversized signal rejected: {not is_valid}")
    
    # Test 3: Comprehensive trade validation
    print("\n3. Testing comprehensive trade validation...")
    result = risk_manager.validate_trade_comprehensive(
        valid_signal, "momentum_strategy", 1000000.0, []
    )
    
    print(f"   Trade approved: {result['is_approved']}")
    print(f"   Risk level: {result['risk_level']}")
    print(f"   Recommended action: {result['recommended_action']}")
    print(f"   Position size adjustment: {result['position_size_adjustment']:.2f}")


async def demonstrate_portfolio_drawdown_monitoring():
    """Demonstrate portfolio drawdown monitoring."""
    print("\n" + "="*60)
    print("PORTFOLIO DRAWDOWN MONITORING DEMONSTRATION")
    print("="*60)
    
    config = RiskConfig(max_portfolio_drawdown=0.10)
    risk_manager = OrchestratorRiskManager(config)
    
    # Simulate portfolio value changes
    portfolio_values = [
        1000000.0,  # Initial value
        1050000.0,  # +5% gain (new peak)
        1020000.0,  # -2.9% from peak
        980000.0,   # -6.7% from peak
        950000.0,   # -9.5% from peak (approaching limit)
        920000.0,   # -12.4% from peak (exceeds limit)
    ]
    
    print("\nSimulating portfolio value changes:")
    for i, value in enumerate(portfolio_values):
        print(f"\nStep {i+1}: Portfolio value = ${value:,.0f}")
        
        # Update portfolio value and get drawdown status
        drawdown_status = risk_manager.drawdown_monitor.update_portfolio_value(value)
        
        print(f"   Current drawdown: {drawdown_status['current_drawdown_pct']:.2%}")
        print(f"   Peak value: ${drawdown_status['peak_value']:,.0f}")
        print(f"   In drawdown: {drawdown_status['is_in_drawdown']}")
        print(f"   Should halt trading: {drawdown_status['should_halt_trading']}")
        
        if drawdown_status['recommendations']:
            print(f"   Recommendations: {drawdown_status['recommendations'][0]}")


async def demonstrate_position_size_validation():
    """Demonstrate position size validation across strategies."""
    print("\n" + "="*60)
    print("POSITION SIZE VALIDATION DEMONSTRATION")
    print("="*60)
    
    config = RiskConfig(position_size_limit=0.05)
    risk_manager = OrchestratorRiskManager(config)
    
    portfolio_value = 1000000.0  # $1M portfolio
    
    # Test different position sizes
    test_cases = [
        ("Small position", 0.5, 50000.0),    # $25k = 2.5%
        ("Medium position", 1.0, 50000.0),   # $50k = 5.0% (at limit)
        ("Large position", 2.0, 50000.0),    # $100k = 10% (exceeds limit)
        ("Very large position", 4.0, 50000.0), # $200k = 20% (way over limit)
    ]
    
    print(f"\nTesting position sizes on ${portfolio_value:,.0f} portfolio:")
    print(f"Position size limit: {config.position_size_limit:.1%}")
    
    for description, quantity, price in test_cases:
        signal = create_sample_signal("BTCUSD", 0.8, quantity, price)
        
        is_valid, reason, adjusted_size = risk_manager.position_validator.validate_position_size(
            signal, "test_strategy", portfolio_value
        )
        
        position_value = quantity * price
        position_pct = position_value / portfolio_value
        
        print(f"\n   {description}:")
        print(f"     Position value: ${position_value:,.0f} ({position_pct:.1%})")
        print(f"     Valid: {is_valid}")
        print(f"     Reason: {reason}")
        if not is_valid:
            print(f"     Adjusted size: {adjusted_size:.2f}")


async def demonstrate_correlation_monitoring():
    """Demonstrate strategy correlation monitoring."""
    print("\n" + "="*60)
    print("STRATEGY CORRELATION MONITORING DEMONSTRATION")
    print("="*60)
    
    config = RiskConfig(max_strategy_correlation=0.80)
    risk_manager = OrchestratorRiskManager(config)
    
    # Simulate strategy returns over time
    strategies = ["momentum_strategy", "mean_reversion_strategy", "breakout_strategy"]
    
    print(f"\nSimulating strategy returns (correlation limit: {config.max_strategy_correlation:.0%}):")
    
    # Add correlated returns for momentum and breakout strategies
    correlated_returns = [0.02, -0.01, 0.015, -0.008, 0.012, -0.005, 0.018, -0.012, 0.009, -0.003]
    uncorrelated_returns = [-0.005, 0.008, -0.012, 0.015, -0.009, 0.006, -0.015, 0.011, -0.007, 0.004]
    
    for i, (ret1, ret2) in enumerate(zip(correlated_returns, uncorrelated_returns)):
        # Momentum and breakout are highly correlated
        risk_manager.correlation_monitor.update_strategy_return("momentum_strategy", ret1)
        risk_manager.correlation_monitor.update_strategy_return("breakout_strategy", ret1 * 0.9)  # Highly correlated
        
        # Mean reversion is uncorrelated
        risk_manager.correlation_monitor.update_strategy_return("mean_reversion_strategy", ret2)
        
        if i == len(correlated_returns) - 1:  # Last iteration
            # Force correlation update
            risk_manager.correlation_monitor._update_correlations()
            
            # Check correlation limits
            is_valid, violations = risk_manager.correlation_monitor.check_correlation_limits(strategies)
            
            print(f"   Correlation check passed: {is_valid}")
            if violations:
                print(f"   Violations: {violations}")
            
            # Get correlation report
            report = risk_manager.correlation_monitor.get_correlation_report()
            print(f"   High correlations detected: {len(report['high_correlations'])}")
            
            for corr_info in report['high_correlations'][:3]:  # Show top 3
                pair = corr_info['strategy_pair']
                correlation = corr_info['correlation']
                exceeds = corr_info['exceeds_limit']
                print(f"     {pair[0]} <-> {pair[1]}: {correlation:.3f} {'(EXCEEDS LIMIT)' if exceeds else ''}")


async def demonstrate_dynamic_risk_adjustment():
    """Demonstrate dynamic risk limit adjustment."""
    print("\n" + "="*60)
    print("DYNAMIC RISK LIMIT ADJUSTMENT DEMONSTRATION")
    print("="*60)
    
    config = RiskConfig(position_size_limit=0.05)
    risk_manager = OrchestratorRiskManager(config)
    
    print(f"Base position size limit: {config.position_size_limit:.1%}")
    
    # Simulate high volatility market conditions
    print("\n1. Simulating high volatility market conditions...")
    high_vol_data = [
        create_sample_market_data("BTC/USD", 50000.0, 0.08),  # 8% daily volatility
        create_sample_market_data("ETH/USD", 3000.0, 0.10),   # 10% daily volatility
    ]
    
    # Update market conditions multiple times to trigger adjustment
    for _ in range(15):
        risk_manager.update_dynamic_risk_limits(high_vol_data, 0.02)  # 2% portfolio performance
    
    adjustment_report = risk_manager.pre_trade_validator.risk_adjuster.get_adjustment_report()
    adjusted_limit = risk_manager.pre_trade_validator.risk_adjuster.get_adjusted_limit('position_size_limit')
    
    print(f"   Adjusted position size limit: {adjusted_limit:.1%}")
    print(f"   Adjustment factor: {adjusted_limit / config.position_size_limit:.2f}x")
    
    # Simulate poor portfolio performance
    print("\n2. Simulating poor portfolio performance...")
    risk_manager.update_dynamic_risk_limits(high_vol_data, -0.08)  # -8% portfolio performance
    
    adjusted_limit_poor = risk_manager.pre_trade_validator.risk_adjuster.get_adjusted_limit('position_size_limit')
    print(f"   Adjusted position size limit after poor performance: {adjusted_limit_poor:.1%}")
    print(f"   Adjustment factor: {adjusted_limit_poor / config.position_size_limit:.2f}x")


async def demonstrate_emergency_stop_procedures():
    """Demonstrate emergency stop procedures."""
    print("\n" + "="*60)
    print("EMERGENCY STOP PROCEDURES DEMONSTRATION")
    print("="*60)
    
    config = RiskConfig(
        max_portfolio_drawdown=0.10,
        emergency_stop_conditions=['max_drawdown_exceeded', 'strategy_failure_cascade']
    )
    risk_manager = OrchestratorRiskManager(config)
    
    # Test 1: Manual emergency stop
    print("\n1. Testing manual emergency stop...")
    success = risk_manager.trigger_emergency_stop("Manual emergency stop for demonstration")
    print(f"   Emergency stop triggered: {success}")
    
    # Test signal validation during emergency stop
    signal = create_sample_signal("BTCUSD", 0.8, 1.0, 50000.0)
    is_valid = risk_manager.validate_signal(signal, {'total_value': 1000000.0})
    print(f"   Signal validation during emergency stop: {is_valid}")
    
    # Reset emergency stop
    risk_manager.emergency_stop_manager.reset_emergency_stop(manual_override=True)
    print("   Emergency stop reset")
    
    # Test 2: Automatic emergency stop due to strategy failures
    print("\n2. Testing automatic emergency stop due to strategy failures...")
    
    # Record multiple strategy failures
    risk_manager.record_strategy_failure("strategy_1")
    risk_manager.record_strategy_failure("strategy_2")
    risk_manager.record_strategy_failure("strategy_3")
    
    # Check emergency conditions
    portfolio_data = {
        'current_drawdown_pct': 0.05,  # Below drawdown limit
        'correlation_violations': [],
        'risk_violations': []
    }
    
    should_stop, reason = risk_manager.emergency_stop_manager.check_emergency_conditions(portfolio_data)
    print(f"   Should trigger emergency stop: {should_stop}")
    print(f"   Reason: {reason}")


async def demonstrate_comprehensive_risk_report():
    """Demonstrate comprehensive risk reporting."""
    print("\n" + "="*60)
    print("COMPREHENSIVE RISK REPORT DEMONSTRATION")
    print("="*60)
    
    config = RiskConfig()
    risk_manager = OrchestratorRiskManager(config)
    
    # Set up some sample data
    risk_manager.portfolio_value = 1000000.0
    
    # Update some components with sample data
    risk_manager.drawdown_monitor.update_portfolio_value(950000.0)  # 5% drawdown
    risk_manager.position_validator.update_position("strategy1", "BTCUSD", 50000.0)
    risk_manager.position_validator.update_position("strategy2", "ETHUSD", 30000.0)
    
    # Generate comprehensive report
    report = risk_manager.get_comprehensive_risk_report()
    
    print("\nComprehensive Risk Report Generated:")
    print(f"   Portfolio value: ${report['portfolio_value']:,.0f}")
    print(f"   Current drawdown: {report['drawdown_status']['current_drawdown_pct']:.2%}")
    print(f"   Total exposure: {report['exposure_report']['total_exposure_pct']:.1%}")
    print(f"   Emergency stop active: {report['emergency_status']['emergency_stop_active']}")
    print(f"   Active alerts: {len(report['active_alerts'])}")
    print(f"   Recent violations: {len(report['recent_violations'])}")
    
    # Show risk limits
    print("\n   Risk Limits:")
    base_limits = report['risk_limits']['base_limits']
    for limit_name, limit_value in base_limits.items():
        if isinstance(limit_value, float):
            print(f"     {limit_name}: {limit_value:.1%}")
        else:
            print(f"     {limit_name}: {limit_value}")


async def main():
    """Run all risk management demonstrations."""
    print("UNIFIED STRATEGY ORCHESTRATION - RISK MANAGEMENT SYSTEM")
    print("=" * 80)
    print("This example demonstrates the comprehensive risk management system")
    print("for the unified strategy orchestration framework.")
    
    try:
        await demonstrate_basic_risk_validation()
        await demonstrate_portfolio_drawdown_monitoring()
        await demonstrate_position_size_validation()
        await demonstrate_correlation_monitoring()
        await demonstrate_dynamic_risk_adjustment()
        await demonstrate_emergency_stop_procedures()
        await demonstrate_comprehensive_risk_report()
        
        print("\n" + "="*80)
        print("RISK MANAGEMENT SYSTEM DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nKey Features Demonstrated:")
        print("✓ Portfolio-level drawdown monitoring")
        print("✓ Position size validation across strategies")
        print("✓ Strategy correlation monitoring")
        print("✓ Dynamic risk limit adjustments")
        print("✓ Emergency stop procedures")
        print("✓ Comprehensive pre-trade risk validation")
        print("✓ Risk violation alerting system")
        print("✓ Real-time risk reporting")
        
    except Exception as e:
        logger.error(f"Error in risk management demonstration: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())