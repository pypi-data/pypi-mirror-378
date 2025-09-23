#!/usr/bin/env python3
"""
Example demonstrating the unified configuration loading system.

This example shows how to use the new unified configuration infrastructure
that automatically discovers and loads configuration files from multiple sources.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    get_enhanced_config_manager,
    get_unified_config,
    UnifiedConfigLoader,
    ConfigurationDiscovery
)


def demonstrate_configuration_discovery():
    """Demonstrate configuration file discovery."""
    print("Configuration Discovery Example")
    print("=" * 40)
    
    discovery = ConfigurationDiscovery()
    
    # Discover configuration files
    bot_config = discovery.find_bot_config()
    accounts_config = discovery.find_accounts_config()
    env_file = discovery.find_env_file()
    
    print(f"Bot configuration: {bot_config or 'Not found'}")
    print(f"Accounts configuration: {accounts_config or 'Not found'}")
    print(f"Environment file: {env_file or 'Not found'}")
    
    # Show discovery report
    print("\nDiscovery Report:")
    for line in discovery.get_discovery_report():
        print(f"  {line}")
    
    print()


def demonstrate_unified_loader():
    """Demonstrate unified configuration loading."""
    print("Unified Configuration Loading Example")
    print("=" * 40)
    
    loader = UnifiedConfigLoader()
    
    # Discover configuration sources
    sources = loader.discover_configuration()
    print(f"Configuration Sources:")
    print(f"  Bot config: {sources.bot_config_file}")
    print(f"  Accounts config: {sources.accounts_config_file}")
    print(f"  Environment file: {sources.env_file}")
    print(f"  Environment variables: {len(sources.environment_variables)} found")
    
    # Get configuration status
    status = loader.get_configuration_status()
    print(f"\nConfiguration Status:")
    print(f"  Active sources: {len(status.active_sources)}")
    print(f"  Missing files: {len(status.missing_files)}")
    print(f"  Validation valid: {status.validation_status.is_valid if status.validation_status else 'Unknown'}")
    
    if status.recommendations:
        print(f"  Recommendations:")
        for rec in status.recommendations:
            print(f"    - {rec}")
    
    if status.merge_conflicts:
        print(f"  Merge conflicts: {len(status.merge_conflicts)}")
        for conflict in status.merge_conflicts:
            print(f"    - {conflict.key}: {conflict.source2} overrides {conflict.source1}")
    
    print()


def demonstrate_enhanced_manager():
    """Demonstrate enhanced configuration manager."""
    print("Enhanced Configuration Manager Example")
    print("=" * 40)
    
    # Get enhanced config manager (uses unified loading by default)
    manager = get_enhanced_config_manager()
    
    print(f"Using unified loading: {manager.is_using_unified_loading()}")
    
    # Get active sources
    active_sources = manager.get_active_sources()
    print(f"Active configuration sources: {len(active_sources)}")
    for source in active_sources:
        print(f"  - {source.file_path} ({source.source_type})")
    
    # Get configuration status
    status = manager.get_configuration_status()
    print(f"\nConfiguration Status:")
    print(f"  Valid: {status.validation_status.is_valid if status.validation_status else 'Unknown'}")
    
    if status.validation_status and not status.validation_status.is_valid:
        print(f"  Errors: {len(status.validation_status.errors)}")
        for error in status.validation_status.errors[:3]:  # Show first 3 errors
            print(f"    - {error}")
    
    if status.validation_status and status.validation_status.warnings:
        print(f"  Warnings: {len(status.validation_status.warnings)}")
        for warning in status.validation_status.warnings[:3]:  # Show first 3 warnings
            print(f"    - {warning}")
    
    print()


def demonstrate_configuration_loading():
    """Demonstrate loading configuration with unified system."""
    print("Configuration Loading Example")
    print("=" * 40)
    
    try:
        # Load configuration using unified system
        config = get_unified_config()
        
        print(f"Configuration loaded successfully!")
        print(f"  App name: {config.app_name}")
        print(f"  Version: {config.version}")
        print(f"  Debug mode: {config.debug}")
        print(f"  Dry run: {config.dry_run}")
        print(f"  Base currency: {config.base_currency}")
        print(f"  Exchanges: {len(config.exchanges)}")
        print(f"  Strategies: {len(config.strategies)}")
        
        # Show enabled exchanges
        enabled_exchanges = [name for name, cfg in config.exchanges.items() if cfg.enabled]
        if enabled_exchanges:
            print(f"  Enabled exchanges: {', '.join(enabled_exchanges)}")
        
        # Show enabled strategies
        enabled_strategies = [name for name, cfg in config.strategies.items() if cfg.enabled]
        if enabled_strategies:
            print(f"  Enabled strategies: {', '.join(enabled_strategies)}")
        
    except Exception as e:
        print(f"Configuration loading failed: {e}")
        print("This is expected if no valid configuration files are present.")
        print("Run 'genebot init-config' to create initial configuration.")
    
    print()


def main():
    """Run all examples."""
    print("Unified Configuration System Examples")
    print("=" * 50)
    print()
    
    demonstrate_configuration_discovery()
    demonstrate_unified_loader()
    demonstrate_enhanced_manager()
    demonstrate_configuration_loading()
    
    print("Examples completed!")
    print("\nThe unified configuration system provides:")
    print("- Automatic configuration file discovery")
    print("- Multi-source configuration merging")
    print("- Environment variable precedence")
    print("- Configuration status reporting")
    print("- Backward compatibility with existing code")


if __name__ == "__main__":
    main()