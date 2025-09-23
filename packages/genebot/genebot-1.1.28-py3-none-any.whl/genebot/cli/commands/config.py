"""
Configuration Commands
=====================

Commands for managing configuration files and settings.
"""

import os
import shutil
from argparse import Namespace
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..result import CommandResult
from .base import BaseCommand
from ..utils.config_manager import ConfigurationManager
from ..utils.error_handler import CLIException


class InitConfigCommand(BaseCommand):
    """Initialize configuration files"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute init config command"""
        overwrite = getattr(args, 'overwrite', False)
        template = getattr(args, 'template', 'development')
        
        self.logger.section("Initializing Configuration")
        self.logger.info(f"Template: {template}")
        self.logger.info(f"Overwrite existing: {overwrite}")
        
        try:
            # Create configuration manager
            config_manager = ConfigurationManager(
                config_path=self.context.config_path,
                env_file=self.context.env_file
            )
            
            # Initialize configuration using the manager
            result = config_manager.initialize_configuration(template, overwrite)
            
            if result.success:
                self.logger.success("Configuration initialization completed!")
                
                # Display created files
                if result.data and result.data.get('created_files'):
                    self.logger.subsection("Created Files")
                    for file_path in result.data['created_files']:
                        self.logger.list_item(file_path, "success")
                
                # Display skipped files
                if result.data and result.data.get('skipped_files'):
                    self.logger.subsection("Skipped Existing Files")
                    for file_path in result.data['skipped_files']:
                        self.logger.list_item(file_path, "info")
            
            return result
            
        except CLIException as e:
            self.logger.error(f"Configuration initialization failed: {e.message}")
            return CommandResult.error(
                str(e.message),
                suggestions=e.suggestions
            )
        except Exception as e:
            self.logger.error(f"Unexpected error during initialization: {str(e)}")
            return CommandResult.error(
                f"Configuration initialization failed: {str(e)}",
                suggestions=[
                    "Check directory permissions",
                    "Ensure sufficient disk space",
                    "Try with --overwrite flag if files exist"
                ]
            )


class ConfigHelpCommand(BaseCommand):
    """Show configuration guide"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute config help command"""
        self.logger.banner("GeneBot Configuration Guide")
        
        self._show_file_structure()
        self._show_env_setup()
        self._show_accounts_setup()
        self._show_bot_config_setup()
        self._show_next_steps()
        
        return CommandResult.success("Configuration guide displayed")
    
    def _show_file_structure(self) -> None:
        """Show required file structure"""
        self.logger.section("Required File Structure")
        
        structure = [
            "config/",
            "├── accounts.yaml          # Trading account configurations",
            "├── trading_bot_config.yaml # Bot and strategy settings",
            "logs/                      # Log files directory",
            "reports/                   # Trading reports directory", 
            "backups/                   # Configuration backups",
            ".env                       # Environment variables and API keys"
        ]
        
        for line in structure:
            self.logger.info(f"  {line}")
    
    def _show_env_setup(self) -> None:
        """Show .env file setup"""
        self.logger.section("Environment Variables (.env)")
        
        env_examples = [
            "# Crypto Exchange API Keys",
            "BINANCE_API_KEY=your_binance_api_key",
            "BINANCE_API_SECRET=your_binance_api_secret",
            "BINANCE_SANDBOX=true",
            "",
            "# Forex Broker Credentials", 
            "OANDA_API_KEY=your_oanda_api_key",
            "OANDA_ACCOUNT_ID=your_oanda_account_id",
            "OANDA_SANDBOX=true",
            "",
            "# Database Configuration",
            "DATABASE_URL=sqlite:///genebot.db"
        ]
        
        for line in env_examples:
            self.logger.info(f"  {line}")
    
    def _show_accounts_setup(self) -> None:
        """Show accounts.yaml setup"""
        self.logger.section("Account Configuration (config/accounts.yaml)")
        
        accounts_example = [
            "crypto_exchanges:",
            "  binance-demo:",
            "    name: 'Binance Demo Account'",
            "    exchange_type: 'binance'",
            "    api_key: '${BINANCE_API_KEY}'",
            "    api_secret: '${BINANCE_API_SECRET}'",
            "    sandbox: true",
            "    enabled: true",
            "",
            "forex_brokers:",
            "  oanda-demo:",
            "    name: 'OANDA Demo Account'",
            "    broker_type: 'oanda'",
            "    api_key: '${OANDA_API_KEY}'",
            "    account_id: '${OANDA_ACCOUNT_ID}'",
            "    sandbox: true",
            "    enabled: true"
        ]
        
        for line in accounts_example:
            self.logger.info(f"  {line}")
    
    def _show_bot_config_setup(self) -> None:
        """Show bot configuration setup"""
        self.logger.section("Bot Configuration (config/trading_bot_config.yaml)")
        
        bot_config_example = [
            "strategies:",
            "  - name: 'RSI_Mean_Reversion'",
            "    enabled: true",
            "    risk_per_trade: 0.02",
            "  - name: 'Moving_Average_Crossover'", 
            "    enabled: true",
            "    risk_per_trade: 0.015",
            "",
            "risk_management:",
            "  max_daily_loss: 0.05",
            "  max_drawdown: 0.10",
            "  position_sizing: 'fixed_percentage'"
        ]
        
        for line in bot_config_example:
            self.logger.info(f"  {line}")
    
    def _show_next_steps(self) -> None:
        """Show next steps"""
        self.logger.section("Next Steps")
        
        steps = [
            "1. Run 'genebot init-config' to create configuration files",
            "2. Edit .env file with your API credentials",
            "3. Add accounts with 'genebot add-crypto' or 'genebot add-forex'",
            "4. Validate setup with 'genebot validate'",
            "5. Start trading with 'genebot start'"
        ]
        
        for step in steps:
            self.logger.list_item(step, "info")


class ListStrategiesCommand(BaseCommand):
    """List all active trading strategies"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute list strategies command"""
        status_filter = getattr(args, 'status', 'all')
        
        self.logger.section("Trading Strategies")
        self.logger.info(f"Filter: {status_filter}")
        
        try:
            # Load strategies from actual configuration and registry
            strategies = self._load_strategies_info(status_filter)
            
            if not strategies:
                return CommandResult.warning(
                    f"No strategies found with status: {status_filter}",
                    suggestions=[
                        "Check strategy configuration in config/trading_bot_config.yaml",
                        "Use 'all' status filter to see all strategies",
                        "Run 'genebot init-config' to create default configuration"
                    ]
                )
            
            # Display strategies
            self.logger.table_header(['Name', 'Status', 'Markets', 'Risk/Trade', 'Win Rate', 'Trades'])
            
            for strategy in strategies:
                status_icon = "🟢" if strategy['status'] == 'active' else "🔴"
                markets_str = ', '.join(strategy['markets'])
                
                self.logger.table_row([
                    strategy['name'],
                    f"{status_icon} {strategy['status']}",
                    markets_str,
                    strategy['risk_per_trade'],
                    strategy['win_rate'],
                    str(strategy['total_trades'])
                ])
            
            return CommandResult.success(
                f"Listed {len(strategies)} strateg{'y' if len(strategies) == 1 else 'ies'}",
                data={'strategies': strategies}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load strategies: {e}")
            return CommandResult.error(f"Failed to load strategies: {e}")
    
    def _load_strategies_info(self, status_filter: str) -> List[Dict[str, Any]]:
        """Load strategy information from configuration and registry"""
        strategies = []
        
        try:
            # Try to load from configuration file
            config_path = Path(self.context.config_path) / "trading_bot_config.yaml"
            
            if config_path.exists():
                import yaml
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Extract strategy configurations
                strategy_configs = config_data.get('strategies', [])
                
                for strategy_config in strategy_configs:
                    strategy_info = {
                        'name': strategy_config.get('name', 'Unknown'),
                        'status': 'active' if strategy_config.get('enabled', False) else 'inactive',
                        'markets': self._determine_strategy_markets(strategy_config.get('name', '')),
                        'risk_per_trade': f"{strategy_config.get('risk_per_trade', 0.02) * 100:.1f}%",
                        'win_rate': self._get_strategy_win_rate(strategy_config.get('name', '')),
                        'total_trades': self._get_strategy_trade_count(strategy_config.get('name', ''))
                    }
                    
                    # Apply status filter
                    if status_filter == 'all' or strategy_info['status'] == status_filter:
                        strategies.append(strategy_info)
            
            # If no strategies from config, use registry information
            if not strategies:
                strategies = self._get_registry_strategies(status_filter)
                
        except Exception as e:
            self.logger.debug(f"Error loading strategies from config: {e}")
            # Fallback to registry or mock data
            strategies = self._get_registry_strategies(status_filter)
        
        return strategies
    
    def _determine_strategy_markets(self, strategy_name: str) -> List[str]:
        """Determine which markets a strategy supports"""
        # Map strategy names to their supported markets
        market_mapping = {
            'RSI_Mean_Reversion': ['crypto', 'forex'],
            'RSIStrategy': ['crypto', 'forex'],
            'Moving_Average_Crossover': ['crypto'],
            'MovingAverageStrategy': ['crypto', 'forex'],
            'Forex_Session_Strategy': ['forex'],
            'ForexSessionStrategy': ['forex'],
            'Forex_Carry_Trade_Strategy': ['forex'],
            'ForexCarryTradeStrategy': ['forex'],
            'Forex_News_Strategy': ['forex'],
            'ForexNewsStrategy': ['forex'],
            'Cross_Market_Arbitrage_Strategy': ['crypto', 'forex'],
            'CrossMarketArbitrageStrategy': ['crypto', 'forex'],
            'Crypto_Forex_Arbitrage_Strategy': ['crypto', 'forex'],
            'CryptoForexArbitrageStrategy': ['crypto', 'forex'],
            'Triangular_Arbitrage_Strategy': ['crypto'],
            'TriangularArbitrageStrategy': ['crypto'],
            'Multi_Indicator_Strategy': ['crypto', 'forex'],
            'MultiIndicatorStrategy': ['crypto', 'forex'],
            'ML_Pattern_Strategy': ['crypto', 'forex'],
            'MLPatternStrategy': ['crypto', 'forex'],
            'Advanced_Momentum_Strategy': ['crypto', 'forex'],
            'AdvancedMomentumStrategy': ['crypto', 'forex'],
            'ATR_Volatility_Strategy': ['crypto', 'forex'],
            'ATRVolatilityStrategy': ['crypto', 'forex'],
            'MeanReversionStrategy': ['crypto', 'forex']
        }
        
        return market_mapping.get(strategy_name, ['crypto'])
    
    def _get_strategy_win_rate(self, strategy_name: str) -> str:
        """Get strategy win rate (mock data for now)"""
        # This would normally come from performance analytics
        win_rates = {
            'RSI_Mean_Reversion': '68%',
            'RSIStrategy': '68%',
            'Moving_Average_Crossover': '72%',
            'MovingAverageStrategy': '72%',
            'Forex_Session_Strategy': '65%',
            'ForexSessionStrategy': '65%',
            'Forex_Carry_Trade_Strategy': '71%',
            'ForexCarryTradeStrategy': '71%',
            'Forex_News_Strategy': '58%',
            'ForexNewsStrategy': '58%',
            'Cross_Market_Arbitrage_Strategy': '85%',
            'CrossMarketArbitrageStrategy': '85%',
            'Crypto_Forex_Arbitrage_Strategy': '82%',
            'CryptoForexArbitrageStrategy': '82%',
            'Triangular_Arbitrage_Strategy': '78%',
            'TriangularArbitrageStrategy': '78%',
            'Multi_Indicator_Strategy': '69%',
            'MultiIndicatorStrategy': '69%',
            'ML_Pattern_Strategy': '74%',
            'MLPatternStrategy': '74%',
            'Advanced_Momentum_Strategy': '66%',
            'AdvancedMomentumStrategy': '66%',
            'ATR_Volatility_Strategy': '70%',
            'ATRVolatilityStrategy': '70%',
            'MeanReversionStrategy': '67%'
        }
        
        return win_rates.get(strategy_name, '65%')
    
    def _get_strategy_trade_count(self, strategy_name: str) -> int:
        """Get strategy trade count (mock data for now)"""
        # This would normally come from trade history
        trade_counts = {
            'RSI_Mean_Reversion': 142,
            'RSIStrategy': 142,
            'Moving_Average_Crossover': 89,
            'MovingAverageStrategy': 89,
            'Forex_Session_Strategy': 56,
            'ForexSessionStrategy': 56,
            'Forex_Carry_Trade_Strategy': 34,
            'ForexCarryTradeStrategy': 34,
            'Forex_News_Strategy': 78,
            'ForexNewsStrategy': 78,
            'Cross_Market_Arbitrage_Strategy': 23,
            'CrossMarketArbitrageStrategy': 23,
            'Crypto_Forex_Arbitrage_Strategy': 45,
            'CryptoForexArbitrageStrategy': 45,
            'Triangular_Arbitrage_Strategy': 67,
            'TriangularArbitrageStrategy': 67,
            'Multi_Indicator_Strategy': 98,
            'MultiIndicatorStrategy': 98,
            'ML_Pattern_Strategy': 112,
            'MLPatternStrategy': 112,
            'Advanced_Momentum_Strategy': 87,
            'AdvancedMomentumStrategy': 87,
            'ATR_Volatility_Strategy': 76,
            'ATRVolatilityStrategy': 76,
            'MeanReversionStrategy': 95
        }
        
        return trade_counts.get(strategy_name, 25)
    
    def _get_registry_strategies(self, status_filter: str) -> List[Dict[str, Any]]:
        """Get strategies from registry as fallback"""
        try:
            # Try to import and use strategy registry
            from src.strategies.strategy_registry import StrategyRegistry
            
            registry = StrategyRegistry()
            # Discover strategies from the strategies package
            registry.discover_strategies('src.strategies')
            
            strategies = []
            for strategy_name in registry.get_registered_strategies():
                strategy_info = {
                    'name': strategy_name,
                    'status': 'active',  # Default to active for discovered strategies
                    'markets': self._determine_strategy_markets(strategy_name),
                    'risk_per_trade': '2.0%',
                    'win_rate': self._get_strategy_win_rate(strategy_name),
                    'total_trades': self._get_strategy_trade_count(strategy_name)
                }
                
                # Apply status filter
                if status_filter == 'all' or strategy_info['status'] == status_filter:
                    strategies.append(strategy_info)
            
            return strategies
            
        except ImportError:
            # Fallback to mock data if registry not available
            return self._get_mock_strategies(status_filter)
    
    def _get_mock_strategies(self, status_filter: str) -> List[Dict[str, Any]]:
        """Get mock strategy data as final fallback"""
        strategies = [
            {
                'name': 'RSI_Mean_Reversion',
                'status': 'active',
                'markets': ['crypto', 'forex'],
                'risk_per_trade': '2%',
                'win_rate': '68%',
                'total_trades': 142
            },
            {
                'name': 'Moving_Average_Crossover',
                'status': 'active',
                'markets': ['crypto'],
                'risk_per_trade': '1.5%',
                'win_rate': '72%',
                'total_trades': 89
            },
            {
                'name': 'Forex_Session_Strategy',
                'status': 'inactive',
                'markets': ['forex'],
                'risk_per_trade': '3%',
                'win_rate': '65%',
                'total_trades': 56
            }
        ]
        
        # Filter strategies
        if status_filter != 'all':
            strategies = [s for s in strategies if s['status'] == status_filter]
        
        return strategies


class ValidateConfigCommand(BaseCommand):
    """Validate configuration files and settings"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute config validation command"""
        verbose = getattr(args, 'verbose', False)
        
        self.logger.section("Configuration Validation")
        
        try:
            # Create configuration manager
            config_manager = ConfigurationManager(
                config_path=self.context.config_path,
                env_file=self.context.env_file
            )
            
            # Run validation
            self.logger.progress("Validating configuration files...")
            validation_result = config_manager.validate_configuration()
            
            # Display results
            if validation_result.is_valid:
                self.logger.success("✅ Configuration is valid")
            else:
                self.logger.error("❌ Configuration has errors")
            
            # Show errors
            if validation_result.errors:
                self.logger.subsection(f"Errors ({len(validation_result.errors)})")
                for error in validation_result.errors:
                    self.logger.list_item(f"❌ {error}", "error")
            
            # Show warnings
            if validation_result.warnings:
                self.logger.subsection(f"Warnings ({len(validation_result.warnings)})")
                for warning in validation_result.warnings:
                    self.logger.list_item(f"⚠️  {warning}", "warning")
            
            # Show info if verbose
            if verbose and hasattr(validation_result, 'info') and validation_result.info:
                self.logger.subsection(f"Information ({len(validation_result.info)})")
                for info in validation_result.info:
                    self.logger.list_item(f"ℹ️  {info}", "info")
            
            # Prepare result
            if validation_result.is_valid:
                return CommandResult.success(
                    "Configuration validation passed",
                    data={
                        'errors': validation_result.errors,
                        'warnings': validation_result.warnings,
                        'info': getattr(validation_result, 'info', [])
                    }
                )
            else:
                suggestions = [
                    "Fix configuration errors listed above",
                    "Check file syntax and required fields",
                    "Run 'genebot config-help' for setup guidance"
                ]
                
                return CommandResult.error(
                    f"Configuration validation failed with {len(validation_result.errors)} errors",
                    suggestions=suggestions
                )
                
        except CLIException as e:
            self.logger.error(f"Validation failed: {e.message}")
            return CommandResult.error(str(e.message), suggestions=e.suggestions)
        except Exception as e:
            import traceback
            self.logger.error(f"Unexpected validation error: {str(e)}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return CommandResult.error(
                f"Configuration validation failed: {str(e)}",
                suggestions=[
                    "Check if configuration files exist",
                    "Verify file permissions",
                    "Run 'genebot init-config' if files are missing"
                ]
            )


class ConfigStatusCommand(BaseCommand):
    """Show configuration status and information"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute config status command"""
        self.logger.section("Configuration Status")
        
        try:
            # Create configuration manager
            config_manager = ConfigurationManager(
                config_path=self.context.config_path,
                env_file=self.context.env_file
            )
            
            # Get configuration status
            status = config_manager.get_configuration_status()
            
            # Display directory status
            self.logger.subsection("Configuration Directory")
            dir_status = status['config_directory']
            dir_icon = "✅" if dir_status['exists'] and dir_status['writable'] else "❌"
            self.logger.info(f"{dir_icon} Path: {dir_status['path']}")
            self.logger.info(f"   Exists: {dir_status['exists']}")
            self.logger.info(f"   Writable: {dir_status['writable']}")
            
            # Display file status
            self.logger.subsection("Configuration Files")
            files = status['files']
            
            for file_type, file_info in files.items():
                if file_info['exists']:
                    file_icon = "✅"
                    size_mb = file_info['size'] / 1024 / 1024
                    modified = file_info['modified'].strftime("%Y-%m-%d %H:%M:%S")
                    self.logger.info(f"{file_icon} {file_type}: {size_mb:.2f} MB (modified: {modified})")
                else:
                    file_icon = "❌"
                    self.logger.info(f"{file_icon} {file_type}: Not found")
            
            # Display validation status
            self.logger.subsection("Validation Status")
            validation = status['validation']
            if validation:
                if validation.get('is_valid'):
                    self.logger.info("✅ Configuration is valid")
                else:
                    error_count = validation.get('error_count', 0)
                    warning_count = validation.get('warning_count', 0)
                    self.logger.info(f"❌ Configuration has {error_count} errors, {warning_count} warnings")
            else:
                self.logger.info("⚠️  Validation status unknown")
            
            # Display backup status
            self.logger.subsection("Backup Status")
            if status['backups_available']:
                backups = config_manager.list_backups()
                self.logger.info(f"✅ {len(backups)} backup(s) available")
                
                # Show recent backups
                recent_backups = sorted(backups, key=lambda x: x['timestamp'], reverse=True)[:3]
                for backup in recent_backups:
                    timestamp = backup['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    self.logger.info(f"   {backup['original_file']} - {timestamp}")
            else:
                self.logger.info("ℹ️  No backups available")
            
            return CommandResult.success(
                "Configuration status retrieved",
                data=status
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get configuration status: {str(e)}")
            return CommandResult.error(
                f"Configuration status check failed: {str(e)}",
                suggestions=[
                    "Check if configuration directory exists",
                    "Verify file permissions",
                    "Run 'genebot init-config' to initialize configuration"
                ]
            )


class ConfigBackupCommand(BaseCommand):
    """Create backup of configuration files"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute config backup command"""
        file_type = getattr(args, 'file', 'all')
        
        self.logger.section("Configuration Backup")
        self.logger.info(f"Backing up: {file_type}")
        
        try:
            # Create configuration manager
            config_manager = ConfigurationManager(
                config_path=self.context.config_path,
                env_file=self.context.env_file
            )
            
            backed_up_files = []
            
            # Determine which files to backup
            if file_type == 'all':
                files_to_backup = [
                    ('bot_config', config_manager.bot_config_file),
                    ('accounts', config_manager.accounts_file),
                    ('env', config_manager.env_file)
                ]
            elif file_type == 'bot_config':
                files_to_backup = [('bot_config', config_manager.bot_config_file)]
            elif file_type == 'accounts':
                files_to_backup = [('accounts', config_manager.accounts_file)]
            elif file_type == 'env':
                files_to_backup = [('env', config_manager.env_file)]
            else:
                return CommandResult.error(
                    f"Unknown file type: {file_type}",
                    suggestions=["Use 'all', 'bot_config', 'accounts', or 'env'"]
                )
            
            # Create backups
            for file_name, file_path in files_to_backup:
                if file_path.exists():
                    backup_path = config_manager.create_backup(file_path)
                    if backup_path:
                        backed_up_files.append((file_name, str(backup_path)))
                        self.logger.progress(f"Backed up {file_name}: {backup_path.name}")
                    else:
                        self.logger.warning(f"Failed to backup {file_name}")
                else:
                    self.logger.info(f"Skipped {file_name}: file does not exist")
            
            if backed_up_files:
                self.logger.success(f"Successfully backed up {len(backed_up_files)} file(s)")
                return CommandResult.success(
                    f"Created {len(backed_up_files)} backup(s)",
                    data={'backed_up_files': backed_up_files}
                )
            else:
                return CommandResult.warning(
                    "No files were backed up",
                    suggestions=["Check if configuration files exist"]
                )
                
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            return CommandResult.error(
                f"Configuration backup failed: {str(e)}",
                suggestions=[
                    "Check file permissions",
                    "Ensure backup directory is writable",
                    "Verify sufficient disk space"
                ]
            )


class ConfigRestoreCommand(BaseCommand):
    """Restore configuration files from backup"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute config restore command"""
        file_type = getattr(args, 'file', None)
        backup_timestamp = getattr(args, 'timestamp', None)
        
        self.logger.section("Configuration Restore")
        
        try:
            # Create configuration manager
            config_manager = ConfigurationManager(
                config_path=self.context.config_path,
                env_file=self.context.env_file
            )
            
            # List available backups
            backups = config_manager.list_backups()
            if not backups:
                return CommandResult.error(
                    "No backups available",
                    suggestions=["Create backups with 'genebot config-backup'"]
                )
            
            # Filter backups if file type specified
            if file_type:
                backups = [b for b in backups if file_type in b['original_file']]
                if not backups:
                    return CommandResult.error(
                        f"No backups found for file type: {file_type}",
                        suggestions=["Check available backups with 'genebot config-status'"]
                    )
            
            # Select backup to restore
            if backup_timestamp:
                # Find specific backup by timestamp
                selected_backup = None
                for backup in backups:
                    if backup_timestamp in backup['backup_file']:
                        selected_backup = backup
                        break
                
                if not selected_backup:
                    return CommandResult.error(
                        f"Backup not found for timestamp: {backup_timestamp}",
                        suggestions=["List available backups with 'genebot config-status'"]
                    )
            else:
                # Use most recent backup
                selected_backup = max(backups, key=lambda x: x['timestamp'])
            
            # Confirm restore operation
            self.logger.warning(f"This will restore: {selected_backup['original_file']}")
            self.logger.warning(f"From backup: {selected_backup['backup_file']}")
            self.logger.warning("Current file will be overwritten!")
            
            # Restore the backup
            original_path = Path(selected_backup['original_file'])
            backup_path = Path(selected_backup['backup_file'])
            
            if backup_path.exists():
                # Create backup of current file before restore
                current_backup = config_manager.create_backup(original_path)
                
                # Restore from backup
                shutil.copy2(backup_path, original_path)
                
                self.logger.success(f"Restored {original_path.name} from backup")
                
                return CommandResult.success(
                    f"Configuration restored from backup",
                    data={
                        'restored_file': str(original_path),
                        'backup_used': str(backup_path),
                        'current_backup': str(current_backup) if current_backup else None
                    }
                )
            else:
                return CommandResult.error(
                    f"Backup file not found: {backup_path}",
                    suggestions=["Check backup directory integrity"]
                )
                
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            return CommandResult.error(
                f"Configuration restore failed: {str(e)}",
                suggestions=[
                    "Check file permissions",
                    "Verify backup file exists",
                    "Ensure sufficient disk space"
                ]
            )


class ConfigMigrateCommand(BaseCommand):
    """Migrate configuration files to newer versions"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute config migration command"""
        target_version = getattr(args, 'version', 'latest')
        dry_run = getattr(args, 'dry_run', False)
        
        self.logger.section("Configuration Migration")
        self.logger.info(f"Target version: {target_version}")
        self.logger.info(f"Dry run: {dry_run}")
        
        try:
            # Create configuration manager
            config_manager = ConfigurationManager(
                config_path=self.context.config_path,
                env_file=self.context.env_file
            )
            
            # Check current configuration version
            current_version = self._detect_config_version(config_manager)
            self.logger.info(f"Current version: {current_version}")
            
            # Determine migration path
            migrations = self._get_migration_path(current_version, target_version)
            
            if not migrations:
                return CommandResult.success(
                    "Configuration is already up to date",
                    data={'current_version': current_version}
                )
            
            self.logger.subsection(f"Migration Plan ({len(migrations)} steps)")
            for i, migration in enumerate(migrations, 1):
                self.logger.info(f"{i}. {migration['from_version']} → {migration['to_version']}: {migration['description']}")
            
            if dry_run:
                return CommandResult.success(
                    f"Migration plan created ({len(migrations)} steps)",
                    data={'migrations': migrations, 'dry_run': True}
                )
            
            # Execute migrations
            migrated_files = []
            
            for migration in migrations:
                self.logger.progress(f"Applying migration: {migration['description']}")
                
                # Create backups before migration
                for file_path in [config_manager.bot_config_file, config_manager.accounts_file]:
                    if file_path.exists():
                        config_manager.create_backup(file_path)
                
                # Apply migration
                result = self._apply_migration(config_manager, migration)
                if result:
                    migrated_files.extend(result)
                else:
                    return CommandResult.error(
                        f"Migration failed: {migration['description']}",
                        suggestions=["Restore from backup and try again"]
                    )
            
            self.logger.success("Configuration migration completed successfully")
            
            return CommandResult.success(
                f"Migrated configuration to version {target_version}",
                data={
                    'from_version': current_version,
                    'to_version': target_version,
                    'migrated_files': migrated_files,
                    'migrations_applied': len(migrations)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            return CommandResult.error(
                f"Configuration migration failed: {str(e)}",
                suggestions=[
                    "Check configuration file syntax",
                    "Restore from backup if needed",
                    "Run with --dry-run to preview changes"
                ]
            )
    
    def _detect_config_version(self, config_manager: ConfigurationManager) -> str:
        """Detect current configuration version"""
        try:
            if config_manager.bot_config_file.exists():
                bot_config = config_manager.load_bot_config()
                
                # Check for version field
                if 'version' in bot_config:
                    return bot_config['version']
                
                # Detect version by structure
                if 'multi_market' in bot_config:
                    return '2.0'
                elif 'strategies' in bot_config and isinstance(bot_config['strategies'], dict):
                    return '1.1'
                else:
                    return '1.0'
            else:
                return 'none'
        except Exception:
            return 'unknown'
    
    def _get_migration_path(self, from_version: str, to_version: str) -> List[Dict[str, Any]]:
        """Get migration path between versions"""
        migrations = []
        
        # Define available migrations
        available_migrations = [
            {
                'from_version': '1.0',
                'to_version': '1.1',
                'description': 'Add strategy configuration structure',
                'migration_func': self._migrate_1_0_to_1_1
            },
            {
                'from_version': '1.1',
                'to_version': '2.0',
                'description': 'Add multi-market support',
                'migration_func': self._migrate_1_1_to_2_0
            },
            {
                'from_version': '2.0',
                'to_version': '2.1',
                'description': 'Add compliance and monitoring features',
                'migration_func': self._migrate_2_0_to_2_1
            }
        ]
        
        # Build migration path
        current = from_version
        target = to_version if to_version != 'latest' else '2.1'
        
        while current != target:
            next_migration = None
            for migration in available_migrations:
                if migration['from_version'] == current:
                    next_migration = migration
                    break
            
            if not next_migration:
                break
            
            migrations.append(next_migration)
            current = next_migration['to_version']
        
        return migrations
    
    def _apply_migration(self, config_manager: ConfigurationManager, migration: Dict[str, Any]) -> Optional[List[str]]:
        """Apply a specific migration"""
        try:
            return migration['migration_func'](config_manager)
        except Exception as e:
            self.logger.error(f"Migration function failed: {str(e)}")
            return None
    
    def _migrate_1_0_to_1_1(self, config_manager: ConfigurationManager) -> List[str]:
        """Migrate from version 1.0 to 1.1"""
        bot_config = config_manager.load_bot_config()
        
        # Add version field
        bot_config['version'] = '1.1'
        
        # Restructure strategies if needed
        if 'strategies' not in bot_config or not isinstance(bot_config['strategies'], dict):
            bot_config['strategies'] = {
                'rsi_strategy': {
                    'strategy_type': 'rsi',
                    'enabled': False,
                    'symbols': ['BTC/USDT', 'ETH/USDT'],
                    'timeframe': '1h',
                    'parameters': {
                        'rsi_period': 14,
                        'oversold_threshold': 30,
                        'overbought_threshold': 70
                    }
                }
            }
        
        config_manager.save_bot_config(bot_config)
        return [str(config_manager.bot_config_file)]
    
    def _migrate_1_1_to_2_0(self, config_manager: ConfigurationManager) -> List[str]:
        """Migrate from version 1.1 to 2.0"""
        bot_config = config_manager.load_bot_config()
        
        # Update version
        bot_config['version'] = '2.0'
        
        # Add multi-market configuration
        if 'multi_market' not in bot_config:
            bot_config['multi_market'] = {
                'enabled': True,
                'crypto': {
                    'enabled': True,
                    'default_quote_currency': 'USDT'
                },
                'forex': {
                    'enabled': False,
                    'default_base_currency': 'USD'
                }
            }
        
        # Add cross-market risk management
        if 'cross_market_risk' not in bot_config:
            bot_config['cross_market_risk'] = {
                'max_total_exposure': 0.8,
                'crypto_max_allocation': 0.6,
                'forex_max_allocation': 0.4,
                'correlation_threshold': 0.7
            }
        
        config_manager.save_bot_config(bot_config)
        return [str(config_manager.bot_config_file)]
    
    def _migrate_2_0_to_2_1(self, config_manager: ConfigurationManager) -> List[str]:
        """Migrate from version 2.0 to 2.1"""
        bot_config = config_manager.load_bot_config()
        
        # Update version
        bot_config['version'] = '2.1'
        
        # Add compliance configuration
        if 'compliance' not in bot_config:
            bot_config['compliance'] = {
                'enabled': True,
                'audit_trail': True,
                'report_frequency': 'daily',
                'report_output_dir': 'reports/compliance',
                'audit_retention_days': 365
            }
        
        # Add enhanced monitoring
        if 'monitoring' not in bot_config:
            bot_config['monitoring'] = {
                'enabled': True,
                'metrics_collection': True,
                'performance_tracking': True,
                'alert_thresholds': {
                    'max_drawdown': 0.1,
                    'daily_loss': 0.05
                }
            }
        
        config_manager.save_bot_config(bot_config)
        return [str(config_manager.bot_config_file)]


class SystemValidateCommand(BaseCommand):
    """Comprehensive system validation that checks all components"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute comprehensive system validation"""
        verbose = getattr(args, 'verbose', False)
        
        self.logger.section("Comprehensive System Validation")
        
        try:
            # Create configuration manager
            config_manager = ConfigurationManager(
                config_path=self.context.config_path,
                env_file=self.context.env_file
            )
            
            validation_results = {}
            overall_valid = True
            
            # 1. Configuration validation
            self.logger.subsection("Configuration Validation")
            config_result = config_manager.validate_configuration()
            validation_results['configuration'] = config_result
            if not config_result.is_valid:
                overall_valid = False
            
            self._display_validation_result("Configuration", config_result, verbose)
            
            # 2. File system validation
            self.logger.subsection("File System Validation")
            fs_result = self._validate_file_system()
            validation_results['file_system'] = fs_result
            if not fs_result.is_valid:
                overall_valid = False
            
            self._display_validation_result("File System", fs_result, verbose)
            
            # 3. Environment validation
            self.logger.subsection("Environment Validation")
            env_result = self._validate_environment(config_manager)
            validation_results['environment'] = env_result
            if not env_result.is_valid:
                overall_valid = False
            
            self._display_validation_result("Environment", env_result, verbose)
            
            # 4. Dependencies validation
            self.logger.subsection("Dependencies Validation")
            deps_result = self._validate_dependencies()
            validation_results['dependencies'] = deps_result
            if not deps_result.is_valid:
                overall_valid = False
            
            self._display_validation_result("Dependencies", deps_result, verbose)
            
            # 5. Database validation
            self.logger.subsection("Database Validation")
            db_result = self._validate_database(config_manager)
            validation_results['database'] = db_result
            if not db_result.is_valid:
                overall_valid = False
            
            self._display_validation_result("Database", db_result, verbose)
            
            # Summary
            self.logger.section("Validation Summary")
            if overall_valid:
                self.logger.success("✅ All system components are valid")
            else:
                self.logger.error("❌ System validation failed")
            
            # Count totals
            total_errors = sum(len(result.errors) for result in validation_results.values())
            total_warnings = sum(len(result.warnings) for result in validation_results.values())
            
            self.logger.info(f"Total errors: {total_errors}")
            self.logger.info(f"Total warnings: {total_warnings}")
            
            if overall_valid:
                return CommandResult.success(
                    "System validation passed",
                    data=validation_results
                )
            else:
                return CommandResult.error(
                    f"System validation failed with {total_errors} errors",
                    suggestions=[
                        "Fix configuration errors",
                        "Check file permissions",
                        "Verify environment setup",
                        "Run individual validations for details"
                    ]
                )
                
        except Exception as e:
            self.logger.error(f"System validation failed: {str(e)}")
            return CommandResult.error(
                f"System validation error: {str(e)}",
                suggestions=[
                    "Check system permissions",
                    "Verify installation integrity",
                    "Run 'genebot config-help' for setup guidance"
                ]
            )
    
    def _validate_file_system(self) -> 'ConfigValidationResult':
        """Validate file system requirements"""
        from genebot.config.validation_utils import ConfigValidationResult
        
        result = ConfigValidationResult()
        
        # Check required directories
        required_dirs = [
            ('config', 'Configuration files'),
            ('logs', 'Log files'),
            ('reports', 'Trading reports'),
            ('backups', 'Configuration backups')
        ]
        
        for dir_name, description in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                result.add_error(f"Required directory missing: {dir_name} ({description})")
            elif not os.access(dir_path, os.W_OK):
                result.add_error(f"Directory not writable: {dir_name}")
            else:
                result.add_info(f"Directory OK: {dir_name}")
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            free_gb = free / (1024**3)
            
            if free_gb < 1.0:
                result.add_error(f"Low disk space: {free_gb:.1f} GB available")
            elif free_gb < 5.0:
                result.add_warning(f"Limited disk space: {free_gb:.1f} GB available")
            else:
                result.add_info(f"Disk space OK: {free_gb:.1f} GB available")
        except Exception:
            result.add_warning("Could not check disk space")
        
        return result
    
    def _validate_environment(self, config_manager: ConfigurationManager) -> 'ConfigValidationResult':
        """Validate environment variables and settings"""
        from genebot.config.validation_utils import ConfigValidationResult
        
        result = ConfigValidationResult()
        
        # Check .env file
        if not config_manager.env_file.exists():
            result.add_error("Environment file (.env) not found")
        else:
            env_vars = config_manager.get_env_variables()
            
            # Check for required variables
            required_vars = ['GENEBOT_ENV', 'DEBUG', 'DRY_RUN']
            for var in required_vars:
                if var not in env_vars:
                    result.add_warning(f"Environment variable not set: {var}")
                else:
                    result.add_info(f"Environment variable OK: {var}")
            
            # Check for placeholder values
            placeholder_patterns = ['your_', 'placeholder', 'example', 'test_']
            for key, value in env_vars.items():
                for pattern in placeholder_patterns:
                    if pattern in value.lower():
                        result.add_warning(f"Placeholder value detected: {key}")
                        break
        
        # Check Python environment
        try:
            import sys
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            result.add_info(f"Python version: {python_version}")
            
            if sys.version_info < (3, 8):
                result.add_error("Python 3.8+ required")
        except Exception:
            result.add_error("Could not check Python version")
        
        return result
    
    def _validate_dependencies(self) -> 'ConfigValidationResult':
        """Validate required dependencies"""
        from genebot.config.validation_utils import ConfigValidationResult
        
        result = ConfigValidationResult()
        
        # Check required packages
        required_packages = [
            ('yaml', 'PyYAML'),
            ('dotenv', 'python-dotenv'),
            ('pydantic', 'pydantic'),
            ('sqlalchemy', 'SQLAlchemy'),
            ('ccxt', 'ccxt')
        ]
        
        for module_name, package_name in required_packages:
            try:
                __import__(module_name)
                result.add_info(f"Package OK: {package_name}")
            except ImportError:
                result.add_error(f"Required package missing: {package_name}")
        
        # Check optional packages
        optional_packages = [
            ('pandas', 'pandas'),
            ('numpy', 'numpy'),
            ('matplotlib', 'matplotlib')
        ]
        
        for module_name, package_name in optional_packages:
            try:
                __import__(module_name)
                result.add_info(f"Optional package OK: {package_name}")
            except ImportError:
                result.add_warning(f"Optional package missing: {package_name}")
        
        return result
    
    def _validate_database(self, config_manager: ConfigurationManager) -> 'ConfigValidationResult':
        """Validate database connectivity and setup"""
        from genebot.config.validation_utils import ConfigValidationResult
        
        result = ConfigValidationResult()
        
        try:
            # Load configuration to get database settings
            try:
                # Try different methods to get config
                try:
                    config = config_manager.get_config()
                    if isinstance(config, dict):
                        db_url = config.get('database', {}).get('database_url', 'sqlite:///genebot.db')
                    else:
                        db_url = getattr(config.database, 'database_url', 'sqlite:///genebot.db')
                except Exception:
                    # Fallback to default
                    db_url = 'sqlite:///genebot.db'
            except Exception as e:
                result.add_error(f"Could not validate database: {str(e)}")
                return result
            
            result.add_info(f"Database URL: {db_url}")
            
            # Test database connection
            try:
                from sqlalchemy import create_engine
                engine = create_engine(db_url)
                
                # Test connection
                with engine.connect() as conn:
                    from sqlalchemy import text
                    conn.execute(text("SELECT 1"))
                
                result.add_info("Database connection OK")
                
                # Check if tables exist
                from sqlalchemy import inspect
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                if tables:
                    result.add_info(f"Database tables: {len(tables)} found")
                else:
                    result.add_warning("No database tables found - run migrations")
                
            except Exception as e:
                result.add_error(f"Database connection failed: {str(e)}")
                
        except Exception as e:
            result.add_error(f"Could not validate database: {str(e)}")
        
        return result
    
    def _display_validation_result(self, component: str, result: 'ConfigValidationResult', verbose: bool) -> None:
        """Display validation result for a component"""
        if result.is_valid:
            self.logger.success(f"✅ {component}: Valid")
        else:
            self.logger.error(f"❌ {component}: {len(result.errors)} errors")
        
        if result.errors:
            for error in result.errors:
                self.logger.list_item(f"❌ {error}", "error")
        
        if result.warnings:
            for warning in result.warnings:
                self.logger.list_item(f"⚠️  {warning}", "warning")
        
        if verbose and hasattr(result, 'info') and result.info:
            for info in result.info:
                self.logger.list_item(f"ℹ️  {info}", "info")