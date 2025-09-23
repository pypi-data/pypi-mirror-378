#!/usr/bin/env python3
"""
Orchestrator API Usage Example
==============================

Example demonstrating how to use the orchestrator REST API.
"""

import asyncio
import time
import json
from datetime import datetime, timedelta

# Import the API client
try:
    from src.orchestration.api_client import OrchestratorAPIClient, create_client
    API_CLIENT_AVAILABLE = True
except ImportError:
    print("API client not available. Make sure to install requests: pip install requests")
    API_CLIENT_AVAILABLE = False


def basic_api_usage_example():
    """Basic API usage example"""
    if not API_CLIENT_AVAILABLE:
        print("API client not available")
        return
    
    print("=== Basic Orchestrator API Usage Example ===\n")
    
    # Create API client
    client = create_client(base_url="http://127.0.0.1:8080")
    
    try:
        # 1. Health check
        print("1. Checking API health...")
        health = client.health_check()
        print(f"   Health status: {health.get('status', 'unknown')}")
        print()
        
        # 2. Check orchestrator status
        print("2. Checking orchestrator status...")
        status = client.get_orchestrator_status()
        if status.get('success'):
            orchestrator_status = status.get('data', {}).get('status', 'unknown')
            print(f"   Orchestrator status: {orchestrator_status}")
        else:
            print(f"   Error: {status.get('message', 'Unknown error')}")
        print()
        
        # 3. Start orchestrator if not running
        if not client.is_running():
            print("3. Starting orchestrator...")
            start_result = client.start_orchestrator(daemon_mode=True)
            if start_result.get('success'):
                print("   Orchestrator started successfully")
                
                # Wait for startup
                print("   Waiting for orchestrator to be ready...")
                if client.wait_for_start(timeout=30):
                    print("   Orchestrator is ready")
                else:
                    print("   Timeout waiting for orchestrator to start")
            else:
                print(f"   Failed to start: {start_result.get('message', 'Unknown error')}")
        else:
            print("3. Orchestrator is already running")
        print()
        
        # 4. Get detailed status
        print("4. Getting detailed status...")
        detailed_status = client.get_orchestrator_status(verbose=True)
        if detailed_status.get('success'):
            data = detailed_status.get('data', {})
            strategies = data.get('strategies', {})
            print(f"   Active strategies: {strategies.get('active', 0)}")
            print(f"   Total strategies: {strategies.get('total', 0)}")
            
            performance = data.get('performance', {})
            if performance.get('status') != 'unavailable':
                print(f"   Total return: {performance.get('total_return', 0):.2%}")
                print(f"   Sharpe ratio: {performance.get('sharpe_ratio', 0):.2f}")
        print()
        
        # 5. Get configuration
        print("5. Getting configuration...")
        config = client.get_config()
        if config.get('success'):
            print("   Configuration retrieved successfully")
            # Print some key config values
            config_data = config.get('data', {})
            allocation_config = config_data.get('allocation', {})
            print(f"   Allocation method: {allocation_config.get('method', 'unknown')}")
            print(f"   Rebalance frequency: {allocation_config.get('rebalance_frequency', 'unknown')}")
        print()
        
        # 6. Get metrics
        print("6. Getting metrics (last 24 hours)...")
        metrics = client.get_metrics(hours=24)
        if metrics.get('success'):
            data = metrics.get('data', {})
            print(f"   Time range: {data.get('time_range_hours', 0)} hours")
            print(f"   Orchestrator metrics available: {bool(data.get('orchestrator_metrics'))}")
        print()
        
        # 7. Get strategy list
        print("7. Getting strategy list...")
        strategies = client.get_strategy_list()
        if strategies:
            print(f"   Active strategies: {', '.join(strategies)}")
        else:
            print("   No active strategies found")
        print()
        
        # 8. Get allocation weights
        print("8. Getting allocation weights...")
        weights = client.get_allocation_weights()
        if weights:
            print("   Current allocation weights:")
            for strategy, weight in weights.items():
                print(f"     {strategy}: {weight:.1%}")
        else:
            print("   No allocation weights available")
        print()
        
    except Exception as e:
        print(f"Error during API operations: {e}")


def advanced_api_usage_example():
    """Advanced API usage example with interventions"""
    if not API_CLIENT_AVAILABLE:
        print("API client not available")
        return
    
    print("=== Advanced Orchestrator API Usage Example ===\n")
    
    client = create_client()
    
    try:
        # Check if orchestrator is running
        if not client.is_running():
            print("Orchestrator is not running. Please start it first.")
            return
        
        # 1. Get performance analytics
        print("1. Getting performance analytics...")
        analytics = client.get_performance_analytics()
        if analytics.get('success'):
            print("   Performance analytics retrieved successfully")
            data = analytics.get('data', {})
            portfolio_metrics = data.get('portfolio_metrics', {})
            if portfolio_metrics:
                print(f"   Portfolio metrics available: {len(portfolio_metrics)} categories")
        print()
        
        # 2. Update configuration
        print("2. Updating configuration...")
        config_update = client.update_config(
            max_drawdown=0.15,  # 15% max drawdown
            config_updates={
                'monitoring.alert_threshold': 0.05
            }
        )
        if config_update.get('success'):
            updates = config_update.get('data', {}).get('updates', {})
            print(f"   Updated {len(updates)} configuration parameters")
        print()
        
        # 3. Force rebalancing
        print("3. Forcing allocation rebalancing...")
        rebalance_result = client.force_rebalance()
        if rebalance_result.get('success'):
            data = rebalance_result.get('data', {})
            old_allocations = data.get('old_allocations', {})
            new_allocations = data.get('new_allocations', {})
            print(f"   Rebalancing completed")
            print(f"   Old allocations: {len(old_allocations)} strategies")
            print(f"   New allocations: {len(new_allocations)} strategies")
        print()
        
        # 4. Generate performance report
        print("4. Generating performance report...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Last 7 days
        
        report = client.get_performance_report(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            format='json'
        )
        if report.get('success'):
            data = report.get('data', {})
            print(f"   Report generated for period: {data.get('start_date')} to {data.get('end_date')}")
            print(f"   Report type: {data.get('report_type', 'unknown')}")
        print()
        
        # 5. Generate audit report
        print("5. Generating audit report...")
        audit_report = client.get_audit_report(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        if audit_report.get('success'):
            data = audit_report.get('data', {})
            audit_data = data.get('data', {})
            print(f"   Audit report generated")
            print(f"   Allocation changes: {len(audit_data.get('allocation_changes', []))}")
            print(f"   Risk events: {len(audit_data.get('risk_events', []))}")
            print(f"   Interventions: {len(audit_data.get('interventions', []))}")
        print()
        
    except Exception as e:
        print(f"Error during advanced API operations: {e}")


def intervention_example():
    """Example of manual interventions via API"""
    if not API_CLIENT_AVAILABLE:
        print("API client not available")
        return
    
    print("=== Manual Intervention Example ===\n")
    
    client = create_client()
    
    try:
        # Check if orchestrator is running
        if not client.is_running():
            print("Orchestrator is not running. Please start it first.")
            return
        
        # Get list of strategies
        strategies = client.get_strategy_list()
        if not strategies:
            print("No active strategies found for intervention example")
            return
        
        print(f"Available strategies: {', '.join(strategies)}")
        
        # Example: Pause first strategy
        if len(strategies) > 0:
            strategy_to_pause = strategies[0]
            print(f"\n1. Pausing strategy: {strategy_to_pause}")
            
            pause_result = client.pause_strategy(strategy_to_pause)
            if pause_result.get('success'):
                data = pause_result.get('data', {})
                print(f"   Strategy paused at: {data.get('timestamp')}")
                
                # Wait a moment
                time.sleep(2)
                
                # Resume the strategy
                print(f"2. Resuming strategy: {strategy_to_pause}")
                resume_result = client.resume_strategy(strategy_to_pause)
                if resume_result.get('success'):
                    data = resume_result.get('data', {})
                    print(f"   Strategy resumed at: {data.get('timestamp')}")
        
        # Example: Adjust allocation
        if len(strategies) > 0:
            strategy_to_adjust = strategies[0]
            print(f"\n3. Adjusting allocation for: {strategy_to_adjust}")
            
            # Get current weight
            current_weights = client.get_allocation_weights()
            current_weight = current_weights.get(strategy_to_adjust, 0.0)
            new_weight = min(current_weight + 0.05, 1.0)  # Increase by 5%
            
            adjust_result = client.adjust_allocation(strategy_to_adjust, new_weight)
            if adjust_result.get('success'):
                data = adjust_result.get('data', {})
                print(f"   Allocation adjusted from {data.get('old_weight', 0):.1%} to {data.get('new_weight', 0):.1%}")
        
        print("\nIntervention example completed successfully")
        
    except Exception as e:
        print(f"Error during intervention example: {e}")


def monitoring_example():
    """Example of continuous monitoring via API"""
    if not API_CLIENT_AVAILABLE:
        print("API client not available")
        return
    
    print("=== Continuous Monitoring Example ===\n")
    
    client = create_client()
    
    try:
        # Check if orchestrator is running
        if not client.is_running():
            print("Orchestrator is not running. Please start it first.")
            return
        
        print("Starting 30-second monitoring session...")
        print("Press Ctrl+C to stop monitoring\n")
        
        start_time = time.time()
        iteration = 0
        
        while time.time() - start_time < 30:  # Monitor for 30 seconds
            iteration += 1
            print(f"--- Monitoring Iteration {iteration} ---")
            
            # Get current status
            status = client.get_orchestrator_status()
            if status.get('success'):
                data = status.get('data', {})
                print(f"Status: {data.get('status', 'unknown')}")
                
                strategies = data.get('strategies', {})
                print(f"Active strategies: {strategies.get('active', 0)}/{strategies.get('total', 0)}")
                
                performance = data.get('performance', {})
                if performance.get('status') != 'unavailable':
                    print(f"Total return: {performance.get('total_return', 0):.2%}")
                    print(f"Sharpe ratio: {performance.get('sharpe_ratio', 0):.2f}")
                
                risk = data.get('risk', {})
                if risk.get('status') != 'unavailable':
                    print(f"Current drawdown: {risk.get('current_drawdown', 0):.2%}")
            
            print(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}")
            print()
            
            # Wait 5 seconds before next iteration
            time.sleep(5)
        
        print("Monitoring session completed")
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error during monitoring: {e}")


def main():
    """Main function to run all examples"""
    print("Orchestrator API Usage Examples")
    print("=" * 50)
    
    if not API_CLIENT_AVAILABLE:
        print("ERROR: API client dependencies not available.")
        print("Please install required packages: pip install requests")
        return
    
    try:
        # Run basic example
        basic_api_usage_example()
        
        print("\n" + "=" * 50 + "\n")
        
        # Run advanced example
        advanced_api_usage_example()
        
        print("\n" + "=" * 50 + "\n")
        
        # Run intervention example
        intervention_example()
        
        print("\n" + "=" * 50 + "\n")
        
        # Ask user if they want to run monitoring example
        response = input("Run continuous monitoring example? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            monitoring_example()
        
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    main()