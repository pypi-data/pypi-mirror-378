"""
Orchestrator Migration CLI Commands
==================================

CLI commands for migrating existing setups to orchestrator.
"""

import json
from argparse import Namespace
from pathlib import Path

from ..context import CLIContext
from ..result import CommandResult
from ..utils.logger import CLILogger
from ..utils.error_handler import CLIErrorHandler
from .base import BaseCommand

# Import migration utilities
try:
    import sys
    from pathlib import Path
    # Add project root to path for config imports
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from config.orchestrator_migration import OrchestratorMigrator, create_migration_guide
    from config.manager import get_config_manager
    MIGRATION_AVAILABLE = True
except ImportError as e:
    MIGRATION_AVAILABLE = False
    import_error = str(e)


class OrchestratorMigrationCommand(BaseCommand):
    """Handle orchestrator migration operations"""
    
    def validate_args(self, args: Namespace) -> CommandResult:
        """Validate migration command arguments"""
        if not MIGRATION_AVAILABLE:
            return CommandResult.error(
                "Migration utilities not available",
                details=[f"Import error: {import_error}"]
            )
        
        action = getattr(args, 'action', None)
        if not action:
            return CommandResult.error("Migration action is required")
        
        # Validate action-specific arguments
        if action == 'validate' and not getattr(args, 'config', None):
            return CommandResult.error("Configuration file path required for validation")
        
        return CommandResult.success("Arguments validated")
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute migration command"""
        try:
            action = args.action
            
            if action == 'analyze':
                return self._analyze_setup(args)
            elif action == 'backup':
                return self._create_backup(args)
            elif action == 'generate':
                return self._generate_config(args)
            elif action == 'migrate':
                return self._perform_migration(args)
            elif action == 'validate':
                return self._validate_config(args)
            elif action == 'guide':
                return self._show_guide(args)
            else:
                return CommandResult.error(f"Unknown migration action: {action}")
                
        except Exception as e:
            return CommandResult.error(f"Migration command failed: {e}")
    
    def _analyze_setup(self, args: Namespace) -> CommandResult:
        """Analyze existing setup for migration"""
        try:
            config_manager = get_config_manager()
            migrator = OrchestratorMigrator(config_manager)
            
            self.logger.info("Analyzing existing setup...")
            analysis = migrator.analyze_existing_setup()
            
            # Format analysis output
            output_lines = [
                "=== Migration Analysis ===",
                f"Timestamp: {analysis['timestamp']}",
                f"Migration Required: {'Yes' if analysis['migration_required'] else 'No'}",
                "",
                f"Existing Strategies ({len(analysis['existing_strategies'])}):"
            ]
            
            for strategy in analysis['existing_strategies']:
                status = "✓ Enabled" if strategy['enabled'] else "✗ Disabled"
                output_lines.append(f"  - {strategy['name']} ({strategy['type']}) - {status}")
            
            output_lines.extend([
                "",
                f"Existing Exchanges ({len(analysis['existing_exchanges'])}):"
            ])
            
            for exchange in analysis['existing_exchanges']:
                status = "✓ Enabled" if exchange['enabled'] else "✗ Disabled"
                mode = "Sandbox" if exchange.get('sandbox', False) else "Live"
                output_lines.append(f"  - {exchange['name']} ({exchange['type']}) - {status} ({mode})")
            
            if analysis['recommendations']:
                output_lines.extend([
                    "",
                    "Recommendations:"
                ])
                for rec in analysis['recommendations']:
                    output_lines.append(f"  • {rec}")
            
            if analysis['warnings']:
                output_lines.extend([
                    "",
                    "Warnings:"
                ])
                for warning in analysis['warnings']:
                    output_lines.append(f"  ⚠ {warning}")
            
            formatted_output = "\n".join(output_lines)
            
            return CommandResult.success(
                "Setup analysis completed",
                message=formatted_output,
                data=analysis
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to analyze setup: {e}")
    
    def _create_backup(self, args: Namespace) -> CommandResult:
        """Create backup of existing configuration"""
        try:
            config_manager = get_config_manager()
            migrator = OrchestratorMigrator(config_manager)
            
            self.logger.info("Creating configuration backup...")
            backup_path = migrator.create_migration_backup()
            
            return CommandResult.success(
                "Configuration backup created",
                data={
                    'backup_path': str(backup_path),
                    'files_backed_up': len(list(backup_path.glob('*')))
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to create backup: {e}")
    
    def _generate_config(self, args: Namespace) -> CommandResult:
        """Generate orchestrator configuration"""
        try:
            config_manager = get_config_manager()
            migrator = OrchestratorMigrator(config_manager)
            
            # Get generation parameters
            allocation_method = getattr(args, 'allocation_method', 'performance_based')
            rebalance_frequency = getattr(args, 'rebalance_frequency', 'daily')
            max_drawdown = getattr(args, 'max_drawdown', 0.10)
            
            self.logger.info(f"Generating orchestrator configuration with {allocation_method} allocation...")
            
            orchestrator_config = migrator.generate_orchestrator_config(
                allocation_method=allocation_method,
                rebalance_frequency=rebalance_frequency,
                max_drawdown=max_drawdown
            )
            
            # Determine output path
            output_path = getattr(args, 'output', None)
            if output_path:
                output_path = Path(output_path)
            else:
                output_path = Path('config/orchestrator_config.yaml')
            
            # Save configuration
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            import yaml
            with open(output_path, 'w') as f:
                yaml.dump(orchestrator_config, f, default_flow_style=False, indent=2)
            
            # Count strategies
            strategy_count = len(orchestrator_config.get('orchestrator', {}).get('strategies', []))
            
            return CommandResult.success(
                "Orchestrator configuration generated",
                data={
                    'config_path': str(output_path),
                    'strategy_count': strategy_count,
                    'allocation_method': allocation_method,
                    'rebalance_frequency': rebalance_frequency,
                    'max_drawdown': max_drawdown
                }
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to generate configuration: {e}")
    
    def _perform_migration(self, args: Namespace) -> CommandResult:
        """Perform complete migration"""
        try:
            config_manager = get_config_manager()
            migrator = OrchestratorMigrator(config_manager)
            
            # Get migration parameters
            output_path = getattr(args, 'output', None)
            allocation_method = getattr(args, 'allocation_method', 'performance_based')
            rebalance_frequency = getattr(args, 'rebalance_frequency', 'daily')
            max_drawdown = getattr(args, 'max_drawdown', 0.10)
            create_backup = not getattr(args, 'no_backup', False)
            
            self.logger.info("Performing complete migration to orchestrator...")
            
            migration_result = migrator.migrate_to_orchestrator(
                output_path=output_path,
                allocation_method=allocation_method,
                rebalance_frequency=rebalance_frequency,
                max_drawdown=max_drawdown,
                create_backup=create_backup
            )
            
            if migration_result['success']:
                output_lines = [
                    "=== Migration Completed Successfully ===",
                    f"Configuration saved to: {migration_result['config_path']}"
                ]
                
                if migration_result['backup_path']:
                    output_lines.append(f"Backup created at: {migration_result['backup_path']}")
                
                if migration_result['warnings']:
                    output_lines.extend([
                        "",
                        "Important Notes:"
                    ])
                    for warning in migration_result['warnings']:
                        output_lines.append(f"  ⚠ {warning}")
                
                output_lines.extend([
                    "",
                    "Next Steps:",
                    "  1. Validate configuration: genebot orchestrator-config validate",
                    "  2. Test in dry-run mode: genebot orchestrator-start --daemon",
                    "  3. Monitor performance: genebot orchestrator-monitor"
                ])
                
                formatted_output = "\n".join(output_lines)
                
                return CommandResult.success(
                    "Migration completed successfully",
                    message=formatted_output,
                    data=migration_result
                )
            else:
                error_details = migration_result.get('errors', ['Unknown error'])
                return CommandResult.error(
                    "Migration failed",
                    details=error_details
                )
            
        except Exception as e:
            return CommandResult.error(f"Migration failed: {e}")
    
    def _validate_config(self, args: Namespace) -> CommandResult:
        """Validate orchestrator configuration"""
        try:
            config_manager = get_config_manager()
            migrator = OrchestratorMigrator(config_manager)
            
            config_path = getattr(args, 'config', 'config/orchestrator_config.yaml')
            
            self.logger.info(f"Validating orchestrator configuration: {config_path}")
            
            validation_result = migrator.validate_migration(config_path)
            
            output_lines = [
                "=== Configuration Validation ===",
                f"Configuration: {config_path}",
                f"Valid: {'✓ Yes' if validation_result['valid'] else '✗ No'}"
            ]
            
            if validation_result['errors']:
                output_lines.extend([
                    "",
                    "Errors:"
                ])
                for error in validation_result['errors']:
                    output_lines.append(f"  ✗ {error}")
            
            if validation_result['warnings']:
                output_lines.extend([
                    "",
                    "Warnings:"
                ])
                for warning in validation_result['warnings']:
                    output_lines.append(f"  ⚠ {warning}")
            
            if validation_result['recommendations']:
                output_lines.extend([
                    "",
                    "Recommendations:"
                ])
                for rec in validation_result['recommendations']:
                    output_lines.append(f"  • {rec}")
            
            formatted_output = "\n".join(output_lines)
            
            if validation_result['valid']:
                return CommandResult.success(
                    "Configuration is valid",
                    message=formatted_output,
                    data=validation_result
                )
            else:
                return CommandResult.error(
                    "Configuration validation failed",
                    message=formatted_output,
                    data=validation_result
                )
            
        except Exception as e:
            return CommandResult.error(f"Validation failed: {e}")
    
    def _show_guide(self, args: Namespace) -> CommandResult:
        """Show migration guide"""
        try:
            guide = create_migration_guide()
            
            return CommandResult.success(
                "Migration Guide",
                message=guide
            )
            
        except Exception as e:
            return CommandResult.error(f"Failed to show guide: {e}")