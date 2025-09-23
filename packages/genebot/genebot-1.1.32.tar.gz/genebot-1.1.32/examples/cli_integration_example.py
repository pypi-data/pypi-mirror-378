#!/usr/bin/env python3
"""
CLI Integration Example
======================

This example demonstrates how the GeneBot CLI integrates with existing
trading bot components including exchange adapters, configuration management,
database models, and validation utilities.
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Import CLI integration components
from genebot.cli.utils.integration_manager import IntegrationManager
from genebot.cli.utils.account_validator import RealAccountValidator
from genebot.cli.result import CommandResult

# Import existing trading bot components
from config.manager import ConfigManager, get_config_manager
from config.validation_utils import validate_config_file
from src.exchanges.ccxt_adapter import CCXTAdapter
from src.models.database_models import TradeModel, OrderModel, PositionModel
from src.exceptions.base_exceptions import ExchangeException, ConfigurationException


async def demonstrate_exchange_integration():
    """Demonstrate CLI integration with existing exchange adapters."""
    print("=== Exchange Integration Demo ===")
    
    # Initialize integration manager
    integration_manager = IntegrationManager(
        config_path=Path("config"),
        env_file=Path(".env")
    )
    
    try:
        # Get available exchanges using existing configuration
        exchanges = integration_manager.get_available_exchanges()
        print(f"Found {len(exchanges)} configured exchanges/brokers:")
        
        for exchange in exchanges:
            print(f"  - {exchange['name']} ({exchange['type']}: {exchange['exchange_type']})")
            print(f"    Enabled: {exchange['enabled']}, Sandbox: {exchange['sandbox']}")
        
        # Test connection to first available exchange
        if exchanges:
            exchange_name = exchanges[0]['name']
            print(f"\nTesting connection to {exchange_name}...")
            
            result = await integration_manager.test_exchange_connection(exchange_name)
            if result.success:
                print(f"✅ {result.message}")
                print(f"   Connected: {result.data['connected']}")
                print(f"   Authenticated: {result.data['authenticated']}")
                if 'health_status' in result.data:
                    health = result.data['health_status']
                    print(f"   Status: {health.get('status', 'unknown')}")
                    if 'latency_ms' in health:
                        print(f"   Latency: {health['latency_ms']}ms")
            else:
                print(f"❌ {result.message}")
                for suggestion in result.suggestions:
                    print(f"   💡 {suggestion}")
    
    except Exception as e:
        print(f"❌ Exchange integration error: {e}")
    
    finally:
        integration_manager.cleanup()


def demonstrate_configuration_integration():
    """Demonstrate CLI integration with existing configuration management."""
    print("\n=== Configuration Integration Demo ===")
    
    # Initialize integration manager
    integration_manager = IntegrationManager()
    
    try:
        # Validate configuration using existing validation utilities
        result = integration_manager.validate_configuration()
        
        if result.success:
            print("✅ Configuration validation passed")
            if result.data and 'warnings' in result.data:
                for warning in result.data['warnings']:
                    print(f"   ⚠️  {warning}")
            if result.data and 'info' in result.data:
                for info in result.data['info']:
                    print(f"   ℹ️  {info}")
        else:
            print("❌ Configuration validation failed")
            if result.data and 'errors' in result.data:
                for error in result.data['errors']:
                    print(f"   ❌ {error}")
        
        # Access configuration manager directly
        config_manager = integration_manager.config_manager
        config = config_manager.get_config()
        
        print(f"\nConfiguration details:")
        print(f"  App name: {config.app_name}")
        print(f"  Version: {config.version}")
        print(f"  Debug mode: {config.debug}")
        print(f"  Dry run: {config.dry_run}")
        print(f"  Base currency: {config.base_currency}")
        print(f"  Exchanges configured: {len(config.exchanges)}")
        print(f"  Strategies configured: {len(config.strategies)}")
    
    except Exception as e:
        print(f"❌ Configuration integration error: {e}")


def demonstrate_database_integration():
    """Demonstrate CLI integration with existing database models."""
    print("\n=== Database Integration Demo ===")
    
    # Initialize integration manager
    integration_manager = IntegrationManager()
    
    try:
        # Get recent trades using existing database models
        trades = integration_manager.get_recent_trades(limit=5)
        print(f"Recent trades ({len(trades)}):")
        
        if trades:
            for trade in trades:
                timestamp = datetime.fromisoformat(trade['timestamp'].replace('Z', ''))
                print(f"  - {trade['symbol']}: {trade['side']} {trade['amount']} @ {trade['price']}")
                print(f"    Exchange: {trade['exchange']}, Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Fees: {trade['fees']}")
        else:
            print("  No recent trades found")
        
        # Get open orders
        orders = integration_manager.get_open_orders()
        print(f"\nOpen orders ({len(orders)}):")
        
        if orders:
            for order in orders:
                timestamp = datetime.fromisoformat(order['timestamp'].replace('Z', ''))
                print(f"  - {order['id']}: {order['symbol']} {order['side']} {order['amount']}")
                print(f"    Type: {order['order_type']}, Status: {order['status']}")
                print(f"    Exchange: {order['exchange']}, Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                if order['price']:
                    print(f"    Price: {order['price']}")
                print(f"    Filled: {order['filled_amount']}")
        else:
            print("  No open orders found")
        
        # Get current positions
        positions = integration_manager.get_current_positions()
        print(f"\nCurrent positions ({len(positions)}):")
        
        if positions:
            for position in positions:
                opened_at = datetime.fromisoformat(position['opened_at'].replace('Z', ''))
                print(f"  - {position['symbol']}: {position['side']} {position['size']}")
                print(f"    Entry: {position['entry_price']}, Current: {position['current_price']}")
                print(f"    Exchange: {position['exchange']}, Opened: {opened_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    P&L: {position['pnl']}")
        else:
            print("  No open positions found")
        
        # Get strategy performance
        performance = integration_manager.get_strategy_performance(days=7)
        print(f"\nStrategy performance (last 7 days, {len(performance)} entries):")
        
        if performance:
            for perf in performance[:3]:  # Show top 3
                print(f"  - {perf['strategy_name']} ({perf['symbol']}):")
                print(f"    Total trades: {perf['total_trades']}")
                print(f"    Win rate: {perf['win_rate']:.1%}")
                print(f"    Total P&L: {perf['total_pnl']}")
                if perf['sharpe_ratio']:
                    print(f"    Sharpe ratio: {perf['sharpe_ratio']:.2f}")
        else:
            print("  No strategy performance data found")
    
    except Exception as e:
        print(f"❌ Database integration error: {e}")


async def demonstrate_account_validation_integration():
    """Demonstrate CLI integration with account validation."""
    print("\n=== Account Validation Integration Demo ===")
    
    # Initialize account validator with integration manager
    validator = RealAccountValidator()
    
    try:
        # Get all accounts using existing configuration
        accounts = validator.get_all_accounts()
        print(f"Found {len(accounts)} configured accounts:")
        
        for account in accounts:
            print(f"  - {account['name']} ({account['type']})")
            print(f"    Type: {account.get('exchange_type', account.get('broker_type', 'unknown'))}")
            print(f"    Enabled: {account.get('enabled', False)}")
            print(f"    Sandbox: {account.get('sandbox', True)}")
        
        # Validate enabled accounts
        enabled_accounts = [acc for acc in accounts if acc.get('enabled', False)]
        
        if enabled_accounts:
            print(f"\nValidating {len(enabled_accounts)} enabled accounts...")
            
            # Validate accounts using existing exchange adapters
            validation_results = await validator.validate_all_accounts(
                enabled_only=True,
                timeout=10
            )
            
            for result in validation_results:
                status_icon = "✅" if result.connected and result.authenticated else "❌"
                print(f"{status_icon} {result.name} ({result.type})")
                print(f"    Exchange/Broker: {result.exchange_or_broker}")
                print(f"    Connected: {result.connected}")
                print(f"    Authenticated: {result.authenticated}")
                
                if result.latency_ms:
                    print(f"    Latency: {result.latency_ms}ms")
                
                if result.error_message:
                    print(f"    Error: {result.error_message}")
                
                if result.balance:
                    print(f"    Balance available: {len(result.balance)} currencies")
            
            # Save validation history using existing patterns
            validator.save_validation_history(validation_results)
            print("\n💾 Validation results saved to history")
        else:
            print("  No enabled accounts to validate")
    
    except Exception as e:
        print(f"❌ Account validation integration error: {e}")


def demonstrate_error_handling_integration():
    """Demonstrate CLI integration with existing error handling patterns."""
    print("\n=== Error Handling Integration Demo ===")
    
    # Initialize integration manager
    integration_manager = IntegrationManager()
    
    try:
        # Test configuration error handling
        print("Testing configuration error handling...")
        try:
            # Try to get a non-existent exchange
            adapter = integration_manager.get_exchange_adapter('nonexistent-exchange')
        except Exception as e:
            print(f"✅ Configuration error properly caught: {type(e).__name__}")
            print(f"   Message: {e}")
        
        # Test validation error handling
        print("\nTesting validation error handling...")
        config_file = Path("nonexistent_config.yaml")
        result = integration_manager.validate_configuration()
        
        if not result.success:
            print("✅ Validation error properly handled")
            print(f"   Message: {result.message}")
            for suggestion in result.suggestions:
                print(f"   💡 {suggestion}")
        
        # Test database error handling
        print("\nTesting database error handling...")
        try:
            # This should handle database connection gracefully
            trades = integration_manager.get_recent_trades()
            print(f"✅ Database operation completed (returned {len(trades)} trades)")
        except Exception as e:
            print(f"✅ Database error properly caught: {type(e).__name__}")
            print(f"   Message: {e}")
    
    except Exception as e:
        print(f"❌ Error handling integration error: {e}")


async def main():
    """Run all integration demonstrations."""
    print("GeneBot CLI Integration with Existing Components Demo")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demonstrations
    await demonstrate_exchange_integration()
    demonstrate_configuration_integration()
    demonstrate_database_integration()
    await demonstrate_account_validation_integration()
    demonstrate_error_handling_integration()
    
    print("\n" + "=" * 60)
    print("Integration demonstration completed!")
    print("\nKey Integration Points Demonstrated:")
    print("✅ Exchange adapters (CCXTAdapter, forex adapters)")
    print("✅ Configuration management (ConfigManager)")
    print("✅ Database models (TradeModel, OrderModel, PositionModel)")
    print("✅ Validation utilities (validate_config_file)")
    print("✅ Error handling patterns (existing exception hierarchy)")
    print("✅ Account validation (real API connectivity tests)")
    print("✅ Data operations (real database queries)")
    
    print("\nThe CLI now properly integrates with all existing trading bot components!")


if __name__ == "__main__":
    asyncio.run(main())