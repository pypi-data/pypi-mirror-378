"""
Example demonstrating the orchestration configuration management system.

This example shows how to use the configuration management features including:
- Loading and validating configurations
- Dynamic configuration updates with hot-reload
- Configuration rollback and audit trails
- Template management and migration
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.orchestration.config import OrchestratorConfig, StrategyConfig, create_default_config
from src.orchestration.config_manager import ConfigurationManager, create_default_configuration_files
from src.orchestration.dynamic_config import (
    create_dynamic_config_manager, apply_config_updates,
    ConfigChangeType
)
from src.orchestration.config_migration import migrate_config_file


def basic_configuration_example():
    """Demonstrate basic configuration management."""
    print("=== Basic Configuration Management ===")
    
    # Create configuration manager
    config_manager = ConfigurationManager("example_config")
    
    # Create default configuration
    config = create_default_config()
    print(f"Created default configuration with {len(config.strategies)} strategies")
    
    # Save configuration
    config_path = config_manager.save_config(config, "basic_config.yaml")
    print(f"Saved configuration to {config_path}")
    
    # Validate configuration
    is_valid, errors = config_manager.validate_config(config_path)
    print(f"Configuration valid: {is_valid}")
    if errors:
        print(f"Validation errors: {errors}")
    
    # Load configuration
    loaded_config = config_manager.load_config(config_path)
    print(f"Loaded configuration with {len(loaded_config.strategies)} strategies")
    
    print()


def template_management_example():
    """Demonstrate template management."""
    print("=== Template Management ===")
    
    config_manager = ConfigurationManager("example_config")
    
    # Create a custom configuration
    custom_config = create_default_config()
    custom_config.max_concurrent_strategies = 8
    custom_config.allocation.method = custom_config.allocation.method.__class__("risk_parity")
    
    # Add a custom strategy
    custom_strategy = StrategyConfig(
        type="CustomTestStrategy",
        name="custom_test",
        enabled=True,
        allocation_weight=1.5,
        parameters={"custom_param": 100, "threshold": 0.05}
    )
    custom_config.strategies.append(custom_strategy)
    
    # Create template from custom config
    template_path = config_manager.create_template(
        "custom_example",
        custom_config,
        "Example template with custom settings"
    )
    print(f"Created template at {template_path}")
    
    # List available templates
    templates = config_manager.list_templates()
    print(f"Available templates: {templates}")
    
    # Create configuration from template with overrides
    overrides = {
        "orchestrator": {
            "max_concurrent_strategies": 12,
            "allocation": {
                "rebalance_frequency": "weekly"
            }
        }
    }
    
    new_config = config_manager.create_from_template(
        "custom_example",
        "from_template_config.yaml",
        overrides
    )
    
    print(f"Created config from template with {new_config.max_concurrent_strategies} max strategies")
    print(f"Rebalance frequency: {new_config.allocation.rebalance_frequency.value}")
    
    print()


def dynamic_configuration_example():
    """Demonstrate dynamic configuration updates."""
    print("=== Dynamic Configuration Updates ===")
    
    # Create initial configuration
    config = create_default_config()
    config_path = Path("example_config/dynamic_config.yaml")
    config.save_to_yaml(config_path)
    
    # Create dynamic manager with hot-reload disabled for this example
    dynamic_manager = create_dynamic_config_manager(config_path, enable_hot_reload=False)
    
    # Add change listener
    def config_change_listener(config, changes):
        print(f"Configuration changed! {len(changes)} changes detected:")
        for change in changes:
            print(f"  - {change.change_type.value}: {change.description}")
    
    dynamic_manager.add_change_listener(config_change_listener)
    
    # Update 1: Change allocation method
    print("Updating allocation method...")
    updates = {
        "orchestrator": {
            "allocation": {
                "method": "risk_parity",
                "rebalance_frequency": "weekly"
            }
        }
    }
    
    success = apply_config_updates(dynamic_manager, updates, user="example_user")
    print(f"Update successful: {success}")
    
    # Update 2: Add new strategy
    print("\nAdding new strategy...")
    current_strategies = dynamic_manager.get_current_config().to_dict()["orchestrator"]["strategies"]
    new_strategy = {
        "type": "ExampleNewStrategy",
        "name": "example_new",
        "enabled": True,
        "allocation_weight": 1.2,
        "parameters": {"example_param": 42}
    }
    
    updates = {
        "orchestrator": {
            "strategies": current_strategies + [new_strategy]
        }
    }
    
    success = apply_config_updates(dynamic_manager, updates, user="example_user")
    print(f"Strategy addition successful: {success}")
    
    # Update 3: Modify risk settings
    print("\nModifying risk settings...")
    updates = {
        "orchestrator": {
            "risk": {
                "max_portfolio_drawdown": 0.12,
                "position_size_limit": 0.06
            }
        }
    }
    
    success = apply_config_updates(dynamic_manager, updates, user="example_user")
    print(f"Risk update successful: {success}")
    
    # Show audit trail
    print("\nRecent changes:")
    recent_changes = dynamic_manager.audit_trail.get_recent_changes(5)
    for change in recent_changes:
        print(f"  {change.timestamp.strftime('%H:%M:%S')} - {change.description} (by {change.user})")
    
    # Clean up
    dynamic_manager.stop_hot_reload_monitoring()
    
    print()


def rollback_example():
    """Demonstrate configuration rollback."""
    print("=== Configuration Rollback ===")
    
    # Create initial configuration
    config = create_default_config()
    config_path = Path("example_config/rollback_config.yaml")
    config.save_to_yaml(config_path)
    
    # Create dynamic manager
    dynamic_manager = create_dynamic_config_manager(config_path, enable_hot_reload=False)
    
    # Get initial snapshot
    initial_snapshots = dynamic_manager.audit_trail.get_snapshots()
    initial_snapshot = initial_snapshots[0] if initial_snapshots else None
    print(f"Initial snapshot: {initial_snapshot.snapshot_id if initial_snapshot else 'None'}")
    
    # Make several changes
    print("Making changes...")
    
    # Change 1
    updates = {"orchestrator": {"max_concurrent_strategies": 15}}
    apply_config_updates(dynamic_manager, updates, user="test_user")
    
    # Change 2
    updates = {"orchestrator": {"allocation": {"method": "equal_weight"}}}
    apply_config_updates(dynamic_manager, updates, user="test_user")
    
    # Create manual snapshot
    current_config = dynamic_manager.get_current_config()
    manual_snapshot = dynamic_manager.audit_trail.create_snapshot(
        current_config, "After major changes"
    )
    print(f"Created manual snapshot: {manual_snapshot.snapshot_id}")
    
    # Make more changes
    updates = {"orchestrator": {"risk": {"max_portfolio_drawdown": 0.20}}}
    apply_config_updates(dynamic_manager, updates, user="test_user")
    
    print(f"Current max strategies: {dynamic_manager.get_current_config().max_concurrent_strategies}")
    print(f"Current max drawdown: {dynamic_manager.get_current_config().risk.max_portfolio_drawdown}")
    
    # Rollback to manual snapshot
    print(f"\nRolling back to snapshot {manual_snapshot.snapshot_id}...")
    rollback_success = dynamic_manager.rollback_to_snapshot(manual_snapshot.snapshot_id)
    print(f"Rollback successful: {rollback_success}")
    
    print(f"After rollback max strategies: {dynamic_manager.get_current_config().max_concurrent_strategies}")
    print(f"After rollback max drawdown: {dynamic_manager.get_current_config().risk.max_portfolio_drawdown}")
    
    # Show snapshots
    print("\nAvailable snapshots:")
    snapshots = dynamic_manager.audit_trail.get_snapshots()
    for snapshot in snapshots:
        print(f"  {snapshot.snapshot_id} - {snapshot.timestamp.strftime('%H:%M:%S')} - {snapshot.description}")
    
    # Clean up
    dynamic_manager.stop_hot_reload_monitoring()
    
    print()


def hot_reload_example():
    """Demonstrate hot-reload functionality."""
    print("=== Hot-Reload Configuration ===")
    
    # Create initial configuration
    config = create_default_config()
    config_path = Path("example_config/hot_reload_config.yaml")
    config.save_to_yaml(config_path)
    
    # Create dynamic manager with hot-reload enabled
    dynamic_manager = create_dynamic_config_manager(config_path, enable_hot_reload=True)
    
    # Add change listener
    reload_detected = []
    
    def hot_reload_listener(config, changes):
        reload_detected.append(len(changes))
        print(f"Hot-reload detected! {len(changes)} changes applied")
        for change in changes:
            print(f"  - {change.description}")
    
    dynamic_manager.add_change_listener(hot_reload_listener)
    
    print("Hot-reload monitoring started. Modifying configuration file externally...")
    
    # Wait a moment for monitoring to start
    time.sleep(0.5)
    
    # Modify configuration file externally (simulating external editor)
    modified_config = dynamic_manager.get_current_config()
    modified_config.max_concurrent_strategies = 25
    modified_config.allocation.rebalance_frequency = modified_config.allocation.rebalance_frequency.__class__("hourly")
    
    # Save modified config
    modified_config.save_to_yaml(config_path)
    print("Configuration file modified externally")
    
    # Wait for hot-reload to detect change
    print("Waiting for hot-reload detection...")
    time.sleep(2.0)
    
    # Check if reload was detected
    current_config = dynamic_manager.get_current_config()
    print(f"Current max strategies: {current_config.max_concurrent_strategies}")
    print(f"Current rebalance frequency: {current_config.allocation.rebalance_frequency.value}")
    
    if reload_detected:
        print(f"Hot-reload successfully detected {sum(reload_detected)} total changes")
    else:
        print("Hot-reload not detected (may need more time or different system)")
    
    # Clean up
    dynamic_manager.stop_hot_reload_monitoring()
    
    print()


def audit_trail_example():
    """Demonstrate audit trail functionality."""
    print("=== Audit Trail Management ===")
    
    # Create configuration with some changes
    config = create_default_config()
    config_path = Path("example_config/audit_config.yaml")
    config.save_to_yaml(config_path)
    
    dynamic_manager = create_dynamic_config_manager(config_path, enable_hot_reload=False)
    
    # Make various changes to generate audit trail
    changes_to_make = [
        ({"orchestrator": {"max_concurrent_strategies": 10}}, "Reduce max strategies"),
        ({"orchestrator": {"allocation": {"method": "risk_parity"}}}, "Change to risk parity"),
        ({"orchestrator": {"risk": {"max_portfolio_drawdown": 0.08}}}, "Tighten risk limits"),
        ({"orchestrator": {"monitoring": {"enable_notifications": False}}}, "Disable notifications")
    ]
    
    for updates, description in changes_to_make:
        apply_config_updates(dynamic_manager, updates, user="audit_example")
        time.sleep(0.1)  # Small delay to ensure different timestamps
    
    # Get audit trail
    audit_trail = dynamic_manager.audit_trail
    
    # Show all changes
    print("All recorded changes:")
    all_changes = audit_trail.changes
    for change in all_changes:
        print(f"  {change.change_id} - {change.timestamp.strftime('%H:%M:%S')} - {change.change_type.value}")
        print(f"    Path: {change.path}")
        print(f"    Description: {change.description}")
        print(f"    User: {change.user}")
        print()
    
    # Show changes by type
    print("Changes by type:")
    for change_type in ConfigChangeType:
        type_changes = audit_trail.get_changes_by_type(change_type)
        if type_changes:
            print(f"  {change_type.value}: {len(type_changes)} changes")
    
    # Export audit report
    report_path = Path("example_config/audit_report.json")
    audit_trail.export_audit_report(report_path)
    print(f"\nExported audit report to {report_path}")
    
    # Show report summary
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    print(f"Report summary:")
    print(f"  Total changes: {report['total_changes']}")
    print(f"  Changes by type: {report['changes_by_type']}")
    
    # Clean up
    dynamic_manager.stop_hot_reload_monitoring()
    
    print()


def migration_example():
    """Demonstrate configuration migration."""
    print("=== Configuration Migration ===")
    
    # Create old-style configuration (version 1.0)
    old_config_data = {
        "orchestrator": {
            "allocation": {
                "method": "equal_weight",
                "rebalance_frequency": "daily",
                "min_allocation": 0.1,
                "max_allocation": 0.3
            },
            "risk": {
                "max_portfolio_drawdown": 0.15,
                "max_strategy_correlation": 0.8,
                "position_size_limit": 0.05,
                "stop_loss_threshold": 0.02
            },
            "strategies": [
                {
                    "type": "MovingAverageStrategy",
                    "name": "old_ma",
                    "enabled": True,
                    "allocation_weight": 1.0,
                    "parameters": {"short_period": 10, "long_period": 20}
                }
            ]
        }
    }
    
    # Save old config
    old_config_path = Path("example_config/old_config.yaml")
    old_config_path.parent.mkdir(parents=True, exist_ok=True)
    
    import yaml
    with open(old_config_path, 'w') as f:
        yaml.dump(old_config_data, f, default_flow_style=False, indent=2)
    
    print(f"Created old-style configuration at {old_config_path}")
    
    # Migrate configuration
    print("Migrating configuration to latest version...")
    migrated_path = migrate_config_file(old_config_path, backup=True)
    
    print(f"Migrated configuration saved to {migrated_path}")
    
    # Load and examine migrated configuration
    migrated_config = OrchestratorConfig.from_yaml(migrated_path)
    
    print("Migration results:")
    print(f"  Added monitoring section: {'monitoring' in migrated_config.to_dict()['orchestrator']}")
    print(f"  Added optimization section: {'optimization' in migrated_config.to_dict()['orchestrator']}")
    print(f"  Added rebalance_threshold: {hasattr(migrated_config.allocation, 'rebalance_threshold')}")
    
    # Show migration history if available
    migrated_data = migrated_config.to_dict()
    if "_migration_history" in migrated_data:
        print("Migration history:")
        for migration in migrated_data["_migration_history"]:
            print(f"  {migration['from_version']} -> {migration['to_version']}: {migration['changes']}")
    
    print()


def validation_example():
    """Demonstrate configuration validation."""
    print("=== Configuration Validation ===")
    
    config_manager = ConfigurationManager("example_config")
    
    # Create valid configuration
    valid_config = create_default_config()
    valid_path = config_manager.save_config(valid_config, "valid_config.yaml")
    
    is_valid, errors = config_manager.validate_config(valid_path)
    print(f"Valid configuration check: {is_valid}")
    if errors:
        print(f"Unexpected errors: {errors}")
    
    # Create invalid configuration
    invalid_config = create_default_config()
    invalid_config.allocation.min_allocation = 0.8  # Invalid: min > max
    invalid_config.allocation.max_allocation = 0.2
    invalid_config.risk.max_portfolio_drawdown = -0.1  # Invalid: negative
    
    try:
        invalid_path = config_manager.save_config(invalid_config, "invalid_config.yaml")
        
        is_valid, errors = config_manager.validate_config(invalid_path)
        print(f"\nInvalid configuration check: {is_valid}")
        if errors:
            print("Validation errors found:")
            for error in errors:
                print(f"  - {error}")
    except Exception as e:
        print(f"\nExpected error when saving invalid configuration: {e}")
        print("This demonstrates that the validation system is working correctly.")
    
    print()


def main():
    """Run all configuration management examples."""
    print("Orchestration Configuration Management Examples")
    print("=" * 50)
    
    # Create example directory
    Path("example_config").mkdir(exist_ok=True)
    
    try:
        # Run examples
        basic_configuration_example()
        template_management_example()
        dynamic_configuration_example()
        rollback_example()
        hot_reload_example()
        audit_trail_example()
        migration_example()
        validation_example()
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up example files
        import shutil
        try:
            shutil.rmtree("example_config", ignore_errors=True)
            print("Cleaned up example files")
        except Exception:
            pass


if __name__ == "__main__":
    main()