#!/usr/bin/env python3
"""
Configuration Hot-Reloading Example

This example demonstrates the configuration hot-reloading capabilities
of the trading bot. It shows how to:

1. Enable configuration hot-reloading
2. Monitor configuration file changes
3. Handle automatic reloading with validation
4. Use callbacks to respond to configuration changes
5. Manually trigger configuration reloads

Run this example and then modify configuration files to see hot-reloading in action.
"""

import os
import sys
import time
import signal
import asyncio
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.enhanced_manager import (
    get_enhanced_config_manager,
    start_global_hot_reloader,
    stop_global_hot_reloader,
    get_global_hot_reload_status,
    manual_global_reload
)

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    print(f"\nReceived signal {signum}. Shutting down gracefully...")
    running = False


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if hasattr(signal, 'SIGHUP'):
        signal.signal(signal.SIGHUP, signal_handler)


def create_example_config_files():
    """Create example configuration files for demonstration."""
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    
    # Create example bot configuration
    bot_config = {
        'app_name': 'HotReloadDemo',
        'version': '1.0.0',
        'debug': False,
        'dry_run': True,
        'base_currency': 'USDT',
        'exchanges': {
            'demo_exchange': {
                'exchange_type': 'demo',
                'api_key': 'demo_key',
                'api_secret': 'demo_secret',
                'enabled': True,
                'sandbox': True
            }
        },
        'strategies': {
            'demo_strategy': {
                'strategy_type': 'moving_average',
                'enabled': True,
                'symbols': ['BTC/USDT', 'ETH/USDT'],
                'timeframe': '1h',
                'parameters': {
                    'fast_period': 10,
                    'slow_period': 20
                }
            }
        },
        'risk': {
            'max_position_size': 0.1,
            'max_daily_loss': 0.05,
            'max_drawdown': 0.15,
            'stop_loss_percentage': 0.02,
            'max_open_positions': 5
        },
        'database': {
            'database_type': 'sqlite',
            'database_url': 'sqlite:///hot_reload_demo.db'
        },
        'logging': {
            'log_level': 'INFO',
            'log_format': 'standard'
        }
    }
    
    # Create example accounts configuration
    accounts_config = {
        'exchanges': {
            'demo_exchange': {
                'exchange_type': 'demo',
                'api_key': 'demo_key',
                'api_secret': 'demo_secret',
                'enabled': True,
                'sandbox': True,
                'rate_limit': 1200,
                'timeout': 30
            }
        }
    }
    
    # Create example environment file
    env_content = """# Configuration Hot-Reload Demo Environment Variables
DEBUG=false
DRY_RUN=true
LOG_LEVEL=INFO
ENABLE_CONFIG_HOT_RELOAD=true

# Demo API credentials (not real)
DEMO_API_KEY=demo_key_from_env
DEMO_API_SECRET=demo_secret_from_env

# Risk management overrides
RISK_MAX_POSITION_SIZE=0.1
RISK_MAX_DAILY_LOSS=0.05
"""
    
    # Write configuration files
    import yaml
    
    bot_config_file = config_dir / 'trading_bot_config.yaml'
    with open(bot_config_file, 'w') as f:
        yaml.dump(bot_config, f, default_flow_style=False, indent=2)
    
    accounts_config_file = config_dir / 'accounts.yaml'
    with open(accounts_config_file, 'w') as f:
        yaml.dump(accounts_config, f, default_flow_style=False, indent=2)
    
    env_file = Path('.env')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✓ Created example configuration files:")
    print(f"  • {bot_config_file}")
    print(f"  • {accounts_config_file}")
    print(f"  • {env_file}")
    print()
    
    return bot_config_file, accounts_config_file, env_file


def print_configuration_summary(config):
    """Print a summary of the current configuration."""
    print("Current Configuration Summary:")
    print("=" * 40)
    print(f"App Name: {config.app_name}")
    print(f"Version: {config.version}")
    print(f"Debug Mode: {config.debug}")
    print(f"Dry Run: {config.dry_run}")
    print(f"Base Currency: {config.base_currency}")
    
    print(f"\nExchanges ({len(config.exchanges)}):")
    for name, exchange in config.exchanges.items():
        status = "ENABLED" if exchange.enabled else "DISABLED"
        print(f"  • {name}: {exchange.exchange_type} ({status})")
    
    print(f"\nStrategies ({len(config.strategies)}):")
    for name, strategy in config.strategies.items():
        status = "ENABLED" if strategy.enabled else "DISABLED"
        symbols = ', '.join(strategy.symbols) if strategy.symbols else 'None'
        print(f"  • {name}: {strategy.strategy_type} ({status}) - {symbols}")
    
    print(f"\nRisk Management:")
    print(f"  • Max Position Size: {config.risk.max_position_size}")
    print(f"  • Max Daily Loss: {config.risk.max_daily_loss}")
    print(f"  • Stop Loss: {config.risk.stop_loss_percentage}")
    print(f"  • Max Open Positions: {config.risk.max_open_positions}")
    
    print(f"\nLogging:")
    print(f"  • Level: {config.logging.log_level}")
    print(f"  • Format: {config.logging.log_format}")
    print()


def print_hot_reload_status():
    """Print the current hot-reload status."""
    status = get_global_hot_reload_status()
    
    print("Hot-Reload Status:")
    print("-" * 20)
    print(f"Enabled: {status.get('enabled', False)}")
    print(f"Available: {status.get('available', False)}")
    print(f"Running: {status.get('is_running', False)}")
    
    if status.get('enabled'):
        print(f"Auto-reload: {status.get('auto_reload_enabled', False)}")
        print(f"Validation Required: {status.get('validation_required', False)}")
        print(f"Monitored Files: {len(status.get('monitored_files', []))}")
        
        if status.get('monitored_files'):
            print("  Files being monitored:")
            for file_path in status['monitored_files']:
                print(f"    • {file_path}")
        
        print(f"Total Reloads: {status.get('reload_count', 0)}")
        print(f"Successful: {status.get('successful_reloads', 0)}")
        print(f"Failed: {status.get('failed_reloads', 0)}")
        
        if status.get('last_reload_time'):
            print(f"Last Reload: {status['last_reload_time']}")
    else:
        reason = status.get('reason', 'Unknown')
        print(f"Reason: {reason}")
    
    print()


def setup_hot_reload_callbacks(config_manager):
    """Setup callbacks to monitor configuration changes."""
    
    def on_config_reloaded(result):
        """Handle configuration reload events."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if result.success:
            print(f"\n🔄 [{timestamp}] Configuration automatically reloaded!")
            
            if result.changes:
                print("Changes detected:")
                for change in result.changes:
                    print(f"  • {change.file_path}: {change.change_type}")
            
            if result.warnings:
                print("Warnings:")
                for warning in result.warnings:
                    print(f"  ⚠️  {warning}")
            
            # Print updated configuration summary
            try:
                updated_config = config_manager.get_config()
                print_configuration_summary(updated_config)
            except Exception as e:
                print(f"Error getting updated configuration: {e}")
        else:
            print(f"\n❌ [{timestamp}] Configuration reload failed!")
            
            if result.errors:
                print("Errors:")
                for error in result.errors:
                    print(f"  • {error}")
            
            if result.rollback_performed:
                print("🔄 Configuration rollback was performed")
        
        print("=" * 60)
        print("Monitoring for changes... (Ctrl+C to exit)")
        print("Try modifying configuration files to see hot-reloading in action!")
        print()
    
    def on_config_changed(change):
        """Handle configuration file change events."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n📁 [{timestamp}] File {change.change_type}: {change.file_path}")
    
    # Add callbacks
    config_manager.add_reload_callback(on_config_reloaded)
    config_manager.add_change_callback(on_config_changed)
    
    return on_config_reloaded, on_config_changed


async def interactive_demo():
    """Run an interactive demonstration of hot-reloading."""
    print("Configuration Hot-Reload Interactive Demo")
    print("=" * 50)
    print()
    
    while running:
        print("Available commands:")
        print("  1. Show current configuration")
        print("  2. Show hot-reload status")
        print("  3. Manually trigger reload")
        print("  4. Modify configuration (guided)")
        print("  5. Exit")
        print()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                print("\n" + "=" * 60)
                try:
                    config_manager = get_enhanced_config_manager()
                    config = config_manager.get_config()
                    print_configuration_summary(config)
                except Exception as e:
                    print(f"Error getting configuration: {e}")
                print("=" * 60)
            
            elif choice == '2':
                print("\n" + "=" * 60)
                print_hot_reload_status()
                print("=" * 60)
            
            elif choice == '3':
                print("\nTriggering manual configuration reload...")
                result = manual_global_reload()
                if result:
                    if result.success:
                        print("✓ Configuration reloaded successfully")
                        if result.warnings:
                            for warning in result.warnings:
                                print(f"⚠️  Warning: {warning}")
                    else:
                        print("❌ Configuration reload failed")
                        for error in result.errors:
                            print(f"Error: {error}")
                else:
                    print("Hot-reloader not available")
            
            elif choice == '4':
                print("\nGuided Configuration Modification")
                print("-" * 35)
                print("This will help you modify configuration files to see hot-reloading.")
                print()
                
                modify_choice = input("What would you like to modify?\n"
                                    "  a) App name and version\n"
                                    "  b) Debug mode\n"
                                    "  c) Risk settings\n"
                                    "  d) Add a new strategy\n"
                                    "Enter choice (a-d): ").strip().lower()
                
                if modify_choice == 'a':
                    await modify_app_info()
                elif modify_choice == 'b':
                    await modify_debug_mode()
                elif modify_choice == 'c':
                    await modify_risk_settings()
                elif modify_choice == 'd':
                    await add_new_strategy()
                else:
                    print("Invalid choice")
            
            elif choice == '5':
                print("Exiting demo...")
                break
            
            else:
                print("Invalid choice. Please enter 1-5.")
            
            print()
            
        except KeyboardInterrupt:
            print("\nExiting demo...")
            break
        except EOFError:
            print("\nExiting demo...")
            break
        except Exception as e:
            print(f"Error: {e}")


async def modify_app_info():
    """Modify app name and version."""
    import yaml
    
    config_file = Path('config/trading_bot_config.yaml')
    if not config_file.exists():
        print("Configuration file not found")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"Current app name: {config.get('app_name', 'Unknown')}")
        print(f"Current version: {config.get('version', 'Unknown')}")
        
        new_name = input("Enter new app name (or press Enter to keep current): ").strip()
        new_version = input("Enter new version (or press Enter to keep current): ").strip()
        
        if new_name:
            config['app_name'] = new_name
        if new_version:
            config['version'] = new_version
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"✓ Updated {config_file}")
        print("Watch for automatic reload...")
        
    except Exception as e:
        print(f"Error modifying configuration: {e}")


async def modify_debug_mode():
    """Toggle debug mode."""
    import yaml
    
    config_file = Path('config/trading_bot_config.yaml')
    if not config_file.exists():
        print("Configuration file not found")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        current_debug = config.get('debug', False)
        new_debug = not current_debug
        
        config['debug'] = new_debug
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"✓ Debug mode changed from {current_debug} to {new_debug}")
        print("Watch for automatic reload...")
        
    except Exception as e:
        print(f"Error modifying configuration: {e}")


async def modify_risk_settings():
    """Modify risk management settings."""
    import yaml
    
    config_file = Path('config/trading_bot_config.yaml')
    if not config_file.exists():
        print("Configuration file not found")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        risk = config.get('risk', {})
        
        print("Current risk settings:")
        print(f"  Max Position Size: {risk.get('max_position_size', 'Unknown')}")
        print(f"  Max Daily Loss: {risk.get('max_daily_loss', 'Unknown')}")
        print(f"  Stop Loss %: {risk.get('stop_loss_percentage', 'Unknown')}")
        
        new_pos_size = input("Enter new max position size (0.01-1.0, or Enter to skip): ").strip()
        new_daily_loss = input("Enter new max daily loss (0.01-1.0, or Enter to skip): ").strip()
        new_stop_loss = input("Enter new stop loss % (0.01-0.1, or Enter to skip): ").strip()
        
        if new_pos_size:
            try:
                risk['max_position_size'] = float(new_pos_size)
            except ValueError:
                print("Invalid position size value")
                return
        
        if new_daily_loss:
            try:
                risk['max_daily_loss'] = float(new_daily_loss)
            except ValueError:
                print("Invalid daily loss value")
                return
        
        if new_stop_loss:
            try:
                risk['stop_loss_percentage'] = float(new_stop_loss)
            except ValueError:
                print("Invalid stop loss value")
                return
        
        config['risk'] = risk
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"✓ Updated risk settings in {config_file}")
        print("Watch for automatic reload...")
        
    except Exception as e:
        print(f"Error modifying configuration: {e}")


async def add_new_strategy():
    """Add a new strategy to the configuration."""
    import yaml
    
    config_file = Path('config/trading_bot_config.yaml')
    if not config_file.exists():
        print("Configuration file not found")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        strategies = config.get('strategies', {})
        
        strategy_name = input("Enter strategy name: ").strip()
        if not strategy_name:
            print("Strategy name is required")
            return
        
        strategy_type = input("Enter strategy type (moving_average, rsi, momentum): ").strip()
        if not strategy_type:
            strategy_type = 'moving_average'
        
        symbols = input("Enter symbols (comma-separated, e.g., BTC/USDT,ETH/USDT): ").strip()
        symbol_list = [s.strip() for s in symbols.split(',')] if symbols else ['BTC/USDT']
        
        new_strategy = {
            'strategy_type': strategy_type,
            'enabled': True,
            'symbols': symbol_list,
            'timeframe': '1h',
            'parameters': {
                'period': 14
            }
        }
        
        strategies[strategy_name] = new_strategy
        config['strategies'] = strategies
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"✓ Added new strategy '{strategy_name}' to {config_file}")
        print("Watch for automatic reload...")
        
    except Exception as e:
        print(f"Error adding strategy: {e}")


async def main():
    """Main function."""
    setup_signal_handlers()
    
    print("Configuration Hot-Reloading Example")
    print("=" * 50)
    print()
    
    # Check if configuration files exist, create them if not
    config_dir = Path('config')
    bot_config_file = config_dir / 'trading_bot_config.yaml'
    
    if not bot_config_file.exists():
        print("Creating example configuration files...")
        create_example_config_files()
    else:
        print("Using existing configuration files")
        print()
    
    try:
        # Initialize configuration manager with hot-reloading enabled
        print("Initializing configuration manager with hot-reloading...")
        config_manager = get_enhanced_config_manager(
            use_unified_loading=True,
            enable_hot_reload=True,
            auto_reload=True,
            validation_required=True
        )
        
        # Load initial configuration
        print("Loading initial configuration...")
        config = config_manager.get_config()
        print_configuration_summary(config)
        
        # Start hot-reloader
        print("Starting configuration hot-reloader...")
        success = start_global_hot_reloader(
            enable_hot_reload=True,
            auto_reload=True,
            validation_required=True
        )
        
        if success:
            print("✓ Hot-reloader started successfully")
            print_hot_reload_status()
            
            # Setup callbacks
            print("Setting up hot-reload callbacks...")
            reload_callback, change_callback = setup_hot_reload_callbacks(config_manager)
            
            print("=" * 60)
            print("Configuration hot-reloading is now active!")
            print("=" * 60)
            print()
            
            # Run interactive demo
            await interactive_demo()
            
        else:
            print("❌ Failed to start hot-reloader")
            print("This might be due to missing dependencies (watchdog)")
            print("Install with: pip install watchdog")
    
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\nStopping hot-reloader...")
        stop_global_hot_reloader()
        print("✓ Hot-reloader stopped")
        print("Example completed.")


if __name__ == "__main__":
    asyncio.run(main())