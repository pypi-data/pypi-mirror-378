#!/usr/bin/env python3
"""
Real Account Validation Example
==============================

This example demonstrates how to use the RealAccountValidator to test
actual API connectivity with crypto exchanges and forex brokers.

This replaces the previous mock validation system with real API tests.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add the project root to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from genebot.cli.utils.account_validator import RealAccountValidator, AccountStatus


async def main():
    """Main demonstration function"""
    print("🔍 Real Account Validation Example")
    print("=" * 50)
    
    # Initialize the validator
    # In a real scenario, this would point to your actual config directory
    validator = RealAccountValidator()
    
    print("\n📋 Loading Account Configuration...")
    try:
        # Get all configured accounts
        all_accounts = validator.get_all_accounts()
        
        if not all_accounts:
            print("❌ No accounts found in configuration")
            print("\n💡 To use this example:")
            print("1. Create config/accounts.yaml with your account configurations")
            print("2. Add API credentials to your .env file")
            print("3. Run this example again")
            
            # Show example configuration
            print("\n📝 Example accounts.yaml structure:")
            example_config = """
crypto_exchanges:
  binance-demo:
    name: binance-demo
    exchange_type: binance
    api_key: your_binance_api_key
    api_secret: your_binance_api_secret
    sandbox: true
    enabled: true
    rate_limit: 1200
    timeout: 30

forex_brokers:
  oanda-practice:
    name: oanda-practice
    broker_type: oanda
    api_key: your_oanda_api_key
    account_id: your_oanda_account_id
    sandbox: true
    enabled: true
    timeout: 30
"""
            print(example_config)
            return
        
        print(f"✅ Found {len(all_accounts)} configured account(s)")
        
        # Display account summary
        crypto_accounts = [acc for acc in all_accounts if acc.get('type') == 'crypto']
        forex_accounts = [acc for acc in all_accounts if acc.get('type') == 'forex']
        
        print(f"   📈 Crypto exchanges: {len(crypto_accounts)}")
        print(f"   💱 Forex brokers: {len(forex_accounts)}")
        
        # Show account details
        print("\n📊 Account Details:")
        for account in all_accounts:
            status_icon = "✅" if account.get('enabled', False) else "❌"
            mode_icon = "🧪" if account.get('sandbox', False) else "💰"
            
            if account.get('type') == 'crypto':
                provider = account.get('exchange_type', 'unknown')
            else:
                provider = account.get('broker_type', 'unknown')
            
            print(f"   {status_icon} {account.get('name', 'unknown')} ({account.get('type', 'unknown').upper()}) - {provider} {mode_icon}")
        
        print(f"\n🔄 Starting Real API Validation...")
        print("   This will test actual connectivity to exchanges and brokers")
        print("   Please wait while we validate each account...\n")
        
        # Perform validation with real API calls
        start_time = datetime.now()
        
        # Validate all accounts (this makes real API calls)
        validation_results = await validator.validate_all_accounts(timeout=30)
        
        end_time = datetime.now()
        validation_duration = (end_time - start_time).total_seconds()
        
        if not validation_results:
            print("❌ No validation results returned")
            return
        
        print(f"✅ Validation completed in {validation_duration:.2f} seconds")
        print(f"📊 Results for {len(validation_results)} account(s):\n")
        
        # Display detailed results
        for i, status in enumerate(validation_results, 1):
            print(f"🔍 Account {i}: {status.name}")
            print(f"   Type: {status.type.upper()}")
            print(f"   Provider: {status.exchange_or_broker}")
            print(f"   Enabled: {'✅' if status.enabled else '❌'}")
            
            # Connection status
            if status.connected and status.authenticated:
                print(f"   Status: 🟢 VALID (Connected & Authenticated)")
                if status.latency_ms:
                    print(f"   Latency: {status.latency_ms}ms")
            elif status.connected and not status.authenticated:
                print(f"   Status: 🟡 AUTH FAILED (Connected but not authenticated)")
            elif not status.connected:
                print(f"   Status: 🔴 CONNECTION FAILED")
            else:
                print(f"   Status: ❓ UNKNOWN")
            
            # Show balance if available
            if status.balance:
                print(f"   Balance:")
                for currency, amount in status.balance.items():
                    if hasattr(amount, 'items'):  # Dict with free/used/total
                        total = amount.get('total', 0)
                        print(f"     {currency}: {total}")
                    else:  # Direct amount
                        print(f"     {currency}: {amount}")
            
            # Show error if any
            if status.error_message:
                print(f"   Error: {status.error_message}")
            
            # Show additional info if available
            if status.additional_info:
                print(f"   Additional Info: {status.additional_info}")
            
            print()  # Empty line between accounts
        
        # Generate and display summary
        summary = validator.get_validation_summary(validation_results)
        
        print("📈 Validation Summary:")
        print(f"   Total Accounts: {summary['total_accounts']}")
        print(f"   Valid Accounts: {summary['valid_accounts']} ✅")
        print(f"   Invalid Accounts: {summary['invalid_accounts']} ❌")
        print(f"   Success Rate: {summary['success_rate']}%")
        
        if summary['average_latency_ms'] > 0:
            print(f"   Average Latency: {summary['average_latency_ms']}ms")
        
        print(f"   Crypto Accounts: {summary['crypto_accounts']}")
        print(f"   Forex Accounts: {summary['forex_accounts']}")
        print(f"   Enabled Accounts: {summary['enabled_accounts']}")
        print(f"   Disabled Accounts: {summary['disabled_accounts']}")
        
        # Save validation history
        print(f"\n💾 Saving validation history...")
        validator.save_validation_history(validation_results)
        print("   History saved for future trend analysis")
        
        # Show recommendations based on results
        print(f"\n💡 Recommendations:")
        
        failed_accounts = [s for s in validation_results if not (s.connected and s.authenticated)]
        if failed_accounts:
            print("   🔧 Fix failed accounts:")
            for account in failed_accounts:
                if not account.connected:
                    print(f"     - {account.name}: Check network connectivity and exchange status")
                elif not account.authenticated:
                    print(f"     - {account.name}: Verify API credentials and permissions")
        
        successful_accounts = [s for s in validation_results if s.connected and s.authenticated]
        if successful_accounts:
            print(f"   ✅ {len(successful_accounts)} account(s) ready for trading")
        
        if summary['success_rate'] < 100:
            print("   📚 Check the troubleshooting guide for common issues")
            print("   🔍 Run 'genebot validate-accounts --help' for more options")
        
    except FileNotFoundError:
        print("❌ Configuration file not found")
        print("💡 Create config/accounts.yaml with your account configurations")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        print("💡 Check your configuration and network connectivity")


def demonstrate_filtering():
    """Demonstrate account filtering capabilities"""
    print("\n🔍 Account Filtering Example")
    print("=" * 30)
    
    validator = RealAccountValidator()
    
    try:
        all_accounts = validator.get_all_accounts()
        
        if not all_accounts:
            print("❌ No accounts to filter")
            return
        
        print(f"📊 Total accounts: {len(all_accounts)}")
        
        # Filter by type
        crypto_accounts = validator.filter_accounts(all_accounts, account_type='crypto')
        forex_accounts = validator.filter_accounts(all_accounts, account_type='forex')
        
        print(f"📈 Crypto accounts: {len(crypto_accounts)}")
        print(f"💱 Forex accounts: {len(forex_accounts)}")
        
        # Filter by enabled status
        enabled_accounts = validator.filter_accounts(all_accounts, enabled_only=True)
        print(f"✅ Enabled accounts: {len(enabled_accounts)}")
        
        # Combined filters
        enabled_crypto = validator.filter_accounts(
            all_accounts, account_type='crypto', enabled_only=True
        )
        print(f"📈✅ Enabled crypto accounts: {len(enabled_crypto)}")
        
    except Exception as e:
        print(f"❌ Filtering failed: {e}")


async def demonstrate_single_account_validation():
    """Demonstrate validating a single account"""
    print("\n🎯 Single Account Validation Example")
    print("=" * 40)
    
    validator = RealAccountValidator()
    
    try:
        all_accounts = validator.get_all_accounts()
        
        if not all_accounts:
            print("❌ No accounts available for single validation")
            return
        
        # Pick the first account for demonstration
        test_account = all_accounts[0]
        account_name = test_account.get('name', 'unknown')
        
        print(f"🎯 Testing single account: {account_name}")
        print("   This demonstrates targeted validation of a specific account")
        
        # Validate just this account
        status = await validator.validate_single_account(test_account, timeout=15)
        
        print(f"\n📊 Results for {status.name}:")
        print(f"   Connected: {'✅' if status.connected else '❌'}")
        print(f"   Authenticated: {'✅' if status.authenticated else '❌'}")
        
        if status.latency_ms:
            print(f"   Response Time: {status.latency_ms}ms")
        
        if status.error_message:
            print(f"   Error: {status.error_message}")
        
    except Exception as e:
        print(f"❌ Single account validation failed: {e}")


if __name__ == "__main__":
    print("🚀 Real Account Validation System")
    print("This example demonstrates the new real API connectivity testing")
    print("that replaces the previous mock validation system.\n")
    
    # Run the main validation example
    asyncio.run(main())
    
    # Demonstrate filtering
    demonstrate_filtering()
    
    # Demonstrate single account validation
    asyncio.run(demonstrate_single_account_validation())
    
    print("\n✨ Example completed!")
    print("💡 Use 'genebot validate-accounts' command for CLI access to this functionality")