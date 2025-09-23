"""
Example demonstrating the orchestration performance monitoring and optimization system.

This example shows how to use the comprehensive performance monitoring and 
analytics system for strategy orchestration, including:
- Real-time performance metrics collection
- Performance attribution analysis
- Strategy scoring and selection
- Performance-based optimization
- Underperformance detection and response
"""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestration.performance import PerformanceMonitor
from src.orchestration.performance_optimizer import (
    PerformanceBasedOptimizer, PerformanceBasedSelector, MeanVarianceOptimizer,
    OptimizationObjective, OptimizationConstraints
)
from src.orchestration.interfaces import PerformanceMetrics, RiskMetrics
from src.orchestration.config import MonitoringConfig, OptimizationConfig


def create_sample_performance_metrics() -> Dict[str, PerformanceMetrics]:
    """Create sample performance metrics for demonstration."""
    return {
        "moving_average_strategy": PerformanceMetrics(
            total_return=0.15,
            sharpe_ratio=1.2,
            max_drawdown=0.05,
            win_rate=0.65,
            profit_factor=1.8,
            volatility=0.12,
            alpha=0.02,
            beta=0.95,
            information_ratio=0.8,
            calmar_ratio=2.5,
            sortino_ratio=1.5
        ),
        "rsi_strategy": PerformanceMetrics(
            total_return=0.10,
            sharpe_ratio=0.9,
            max_drawdown=0.08,
            win_rate=0.60,
            profit_factor=1.5,
            volatility=0.15,
            alpha=0.01,
            beta=1.1,
            information_ratio=0.6,
            calmar_ratio=1.8,
            sortino_ratio=1.2
        ),
        "mean_reversion_strategy": PerformanceMetrics(
            total_return=0.08,
            sharpe_ratio=0.7,
            max_drawdown=0.12,
            win_rate=0.55,
            profit_factor=1.3,
            volatility=0.18,
            alpha=-0.005,
            beta=0.8,
            information_ratio=0.4,
            calmar_ratio=1.2,
            sortino_ratio=0.9
        ),
        "momentum_strategy": PerformanceMetrics(
            total_return=0.18,
            sharpe_ratio=1.4,
            max_drawdown=0.06,
            win_rate=0.70,
            profit_factor=2.1,
            volatility=0.14,
            alpha=0.03,
            beta=1.2,
            information_ratio=1.0,
            calmar_ratio=3.0,
            sortino_ratio=1.8
        ),
        "underperforming_strategy": PerformanceMetrics(
            total_return=-0.05,
            sharpe_ratio=-0.3,
            max_drawdown=0.20,
            win_rate=0.35,
            profit_factor=0.8,
            volatility=0.25,
            alpha=-0.02,
            beta=1.5,
            information_ratio=-0.5,
            calmar_ratio=-0.5,
            sortino_ratio=-0.4
        )
    }


def create_sample_risk_metrics() -> Dict[str, RiskMetrics]:
    """Create sample risk metrics for demonstration."""
    return {
        "moving_average_strategy": RiskMetrics(
            var_95=0.03,
            cvar_95=0.045,
            max_drawdown=0.05,
            volatility=0.12,
            correlation_to_market=0.6,
            beta=0.95,
            tracking_error=0.08,
            downside_deviation=0.09
        ),
        "rsi_strategy": RiskMetrics(
            var_95=0.04,
            cvar_95=0.06,
            max_drawdown=0.08,
            volatility=0.15,
            correlation_to_market=0.7,
            beta=1.1,
            tracking_error=0.10,
            downside_deviation=0.11
        ),
        "mean_reversion_strategy": RiskMetrics(
            var_95=0.06,
            cvar_95=0.09,
            max_drawdown=0.12,
            volatility=0.18,
            correlation_to_market=0.5,
            beta=0.8,
            tracking_error=0.12,
            downside_deviation=0.14
        ),
        "momentum_strategy": RiskMetrics(
            var_95=0.035,
            cvar_95=0.05,
            max_drawdown=0.06,
            volatility=0.14,
            correlation_to_market=0.8,
            beta=1.2,
            tracking_error=0.09,
            downside_deviation=0.10
        ),
        "underperforming_strategy": RiskMetrics(
            var_95=0.12,
            cvar_95=0.18,
            max_drawdown=0.20,
            volatility=0.25,
            correlation_to_market=0.9,
            beta=1.5,
            tracking_error=0.20,
            downside_deviation=0.22
        )
    }


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    print("=== Performance Monitoring Demonstration ===\n")
    
    # Initialize performance monitor
    config = MonitoringConfig(
        performance_tracking=True,
        real_time_metrics=True,
        alert_thresholds={
            "drawdown": 0.05,
            "correlation": 0.75,
            "performance_degradation": -0.10
        }
    )
    
    monitor = PerformanceMonitor(config)
    print("✓ Performance monitor initialized")
    
    # Simulate recording performance data over time
    print("\n1. Recording Performance Data")
    print("-" * 30)
    
    strategies = ["moving_average", "rsi", "momentum", "mean_reversion"]
    
    # Simulate 30 days of performance data
    for day in range(30):
        for strategy in strategies:
            # Generate realistic daily returns
            if strategy == "momentum":
                daily_return = np.random.normal(0.001, 0.015)  # Higher return, higher vol
            elif strategy == "moving_average":
                daily_return = np.random.normal(0.0008, 0.012)  # Moderate return, low vol
            elif strategy == "rsi":
                daily_return = np.random.normal(0.0006, 0.014)  # Lower return, moderate vol
            else:  # mean_reversion
                daily_return = np.random.normal(0.0004, 0.016)  # Lowest return, higher vol
            
            total_return = 0.05 + (day * daily_return)  # Cumulative return
            allocation = 0.25  # Equal allocation
            
            monitor.record_strategy_snapshot(
                strategy_name=strategy,
                total_return=total_return,
                daily_return=daily_return,
                allocation=allocation,
                positions_count=np.random.randint(3, 8),
                trades_count=day + 1
            )
        
        # Record portfolio performance
        portfolio_return = np.random.normal(0.0007, 0.013)
        portfolio_value = 100000 * (1 + 0.05 + (day * portfolio_return))
        
        monitor.record_portfolio_snapshot(
            total_return=0.05 + (day * portfolio_return),
            daily_return=portfolio_return,
            total_value=portfolio_value,
            active_strategies=len(strategies),
            total_positions=np.random.randint(12, 20)
        )
    
    print(f"✓ Recorded 30 days of performance data for {len(strategies)} strategies")
    
    # Collect current performance metrics
    print("\n2. Collecting Performance Metrics")
    print("-" * 35)
    
    current_metrics = monitor.collect_performance_metrics()
    
    for strategy_name, metrics in current_metrics.items():
        if strategy_name != 'portfolio':
            print(f"Strategy: {strategy_name}")
            print(f"  Total Return: {metrics.total_return:.3f}")
            print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.3f}")
            print(f"  Max Drawdown: {metrics.max_drawdown:.3f}")
            print(f"  Win Rate: {metrics.win_rate:.3f}")
            print()
    
    # Detect performance degradation
    print("3. Performance Degradation Detection")
    print("-" * 38)
    
    degraded_strategies = monitor.detect_performance_degradation()
    if degraded_strategies:
        print(f"⚠️  Degraded strategies detected: {degraded_strategies}")
    else:
        print("✓ No performance degradation detected")
    
    # Generate performance report
    print("\n4. Performance Report Generation")
    print("-" * 34)
    
    report = monitor.generate_performance_report()
    
    print(f"Report Timestamp: {report['timestamp']}")
    print(f"Total Strategies: {report['summary']['total_strategies']}")
    print(f"Portfolio Return: {report['summary']['portfolio_return']:.3f}")
    print(f"Portfolio Sharpe: {report['summary']['portfolio_sharpe']:.3f}")
    print(f"Recent Alerts: {report['summary']['alerts_count']}")
    
    return monitor


def demonstrate_strategy_selection():
    """Demonstrate strategy selection and scoring."""
    print("\n=== Strategy Selection Demonstration ===\n")
    
    # Create performance monitor (mock)
    config = MonitoringConfig()
    monitor = PerformanceMonitor(config)
    
    # Initialize selector
    selector = PerformanceBasedSelector(monitor)
    print("✓ Performance-based selector initialized")
    
    # Get sample metrics
    performance_metrics = create_sample_performance_metrics()
    risk_metrics = create_sample_risk_metrics()
    
    print("\n1. Strategy Scoring")
    print("-" * 20)
    
    # Score strategies
    strategy_scores = selector.score_strategies(
        performance_metrics, 
        risk_metrics,
        market_conditions={'volatility': 'normal', 'trend': 'neutral'}
    )
    
    print("Strategy Scores (Rank | Strategy | Score | Recommendation):")
    print("-" * 60)
    for score in strategy_scores:
        print(f"{score.rank:2d} | {score.strategy_name:25s} | {score.score:.3f} | {score.recommendation}")
    
    print("\n2. Strategy Selection")
    print("-" * 21)
    
    # Select strategies
    selected_strategies = selector.select_strategies(
        strategy_scores, 
        max_strategies=3, 
        min_score=0.4
    )
    
    print(f"Selected Strategies: {selected_strategies}")
    
    # Show selection reasons for top strategies
    print("\n3. Selection Reasoning")
    print("-" * 22)
    
    for score in strategy_scores[:3]:  # Top 3 strategies
        print(f"\n{score.strategy_name}:")
        print(f"  Score: {score.score:.3f}")
        print(f"  Recommendation: {score.recommendation}")
        print(f"  Reasons: {', '.join(score.reasons[:3])}")  # Show first 3 reasons
    
    return selector, strategy_scores


def demonstrate_portfolio_optimization():
    """Demonstrate portfolio optimization."""
    print("\n=== Portfolio Optimization Demonstration ===\n")
    
    # Initialize optimizer
    config = OptimizationConfig(
        optimization_frequency="weekly",
        lookback_period=30,
        min_performance_threshold=0.0
    )
    
    monitor = PerformanceMonitor(MonitoringConfig())
    optimizer = PerformanceBasedOptimizer(config, monitor)
    print("✓ Performance-based optimizer initialized")
    
    # Get sample metrics
    performance_metrics = create_sample_performance_metrics()
    risk_metrics = create_sample_risk_metrics()
    
    print("\n1. Portfolio Optimization")
    print("-" * 26)
    
    # Run optimization
    current_allocations = {
        "moving_average_strategy": 0.25,
        "rsi_strategy": 0.25,
        "mean_reversion_strategy": 0.25,
        "momentum_strategy": 0.25
    }
    
    optimization_result = optimizer.optimize_portfolio(
        performance_metrics, 
        risk_metrics, 
        current_allocations
    )
    
    print("Optimization Results:")
    print(f"  Expected Return: {optimization_result.expected_return:.3f}")
    print(f"  Expected Risk: {optimization_result.expected_risk:.3f}")
    print(f"  Expected Sharpe: {optimization_result.expected_sharpe:.3f}")
    print(f"  Optimization Time: {optimization_result.optimization_time_ms:.2f}ms")
    print(f"  Constraints Satisfied: {optimization_result.constraints_satisfied}")
    
    print("\nOptimal Allocations:")
    for strategy, allocation in optimization_result.allocations.items():
        print(f"  {strategy}: {allocation:.3f}")
    
    print("\n2. Underperformance Detection")
    print("-" * 30)
    
    # Detect underperformance
    underperforming = optimizer.detect_underperformance(performance_metrics)
    
    if underperforming:
        print(f"⚠️  Underperforming strategies: {underperforming}")
        
        # Show adjustment
        adjusted_allocations = optimizer.adjust_allocations(
            current_allocations, performance_metrics
        )
        
        print("\nAdjusted Allocations:")
        for strategy, allocation in adjusted_allocations.items():
            old_allocation = current_allocations.get(strategy, 0.0)
            change = allocation - old_allocation
            print(f"  {strategy}: {allocation:.3f} ({change:+.3f})")
    else:
        print("✓ No underperforming strategies detected")
    
    print("\n3. Reoptimization Criteria")
    print("-" * 26)
    
    should_reopt = optimizer.should_reoptimize(current_allocations, performance_metrics)
    print(f"Should Reoptimize: {should_reopt}")
    
    # Get performance summary
    print("\n4. Performance Summary")
    print("-" * 21)
    
    summary = optimizer.get_performance_summary()
    print(f"Total Optimizations: {summary['total_optimizations']}")
    print(f"Average Objective Value: {summary['average_objective_value']:.3f}")
    print(f"Degraded Strategies: {len(summary['degraded_strategies'])}")
    
    return optimizer


def demonstrate_attribution_analysis():
    """Demonstrate performance attribution analysis."""
    print("\n=== Attribution Analysis Demonstration ===\n")
    
    # Initialize performance monitor
    config = MonitoringConfig()
    monitor = PerformanceMonitor(config)
    
    # Simulate some historical data
    strategies = ["strategy_a", "strategy_b", "strategy_c"]
    
    # Add historical performance data
    for day in range(30):
        for i, strategy in enumerate(strategies):
            daily_return = np.random.normal(0.001 * (i + 1), 0.01)
            total_return = 0.03 * (i + 1) + (day * daily_return)
            allocation = 0.33
            
            monitor.record_strategy_snapshot(
                strategy_name=strategy,
                total_return=total_return,
                daily_return=daily_return,
                allocation=allocation
            )
        
        # Portfolio performance
        portfolio_return = np.random.normal(0.0008, 0.012)
        monitor.record_portfolio_snapshot(
            total_return=0.04 + (day * portfolio_return),
            daily_return=portfolio_return,
            total_value=100000 * (1.04 + day * portfolio_return),
            active_strategies=3,
            total_positions=15
        )
    
    print("✓ Historical performance data simulated")
    
    # Perform attribution analysis
    print("\n1. Attribution Analysis")
    print("-" * 23)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    attribution = monitor.analyze_attribution(start_date, end_date)
    
    print(f"Analysis Period: {start_date.date()} to {end_date.date()}")
    print(f"Total Return: {attribution.total_return:.3f}")
    print(f"Allocation Effect: {attribution.allocation_effect:.3f}")
    print(f"Selection Effect: {attribution.selection_effect:.3f}")
    print(f"Interaction Effect: {attribution.interaction_effect:.3f}")
    
    print("\nStrategy Contributions:")
    for strategy, contribution in attribution.strategy_contributions.items():
        print(f"  {strategy}: {contribution:.3f}")
    
    return attribution


async def main():
    """Main demonstration function."""
    print("🚀 Orchestration Performance Monitoring & Optimization Demo")
    print("=" * 60)
    
    try:
        # Demonstrate performance monitoring
        monitor = demonstrate_performance_monitoring()
        
        # Demonstrate strategy selection
        selector, scores = demonstrate_strategy_selection()
        
        # Demonstrate portfolio optimization
        optimizer = demonstrate_portfolio_optimization()
        
        # Demonstrate attribution analysis
        attribution = demonstrate_attribution_analysis()
        
        print("\n" + "=" * 60)
        print("✅ All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("• Real-time performance metrics collection")
        print("• Strategy scoring and selection algorithms")
        print("• Performance-based portfolio optimization")
        print("• Underperformance detection and response")
        print("• Performance attribution analysis")
        print("• Comprehensive reporting and analytics")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())