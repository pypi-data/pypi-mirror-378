"""
Configuration Management Integration
===================================

ConfigurationManager class that works with existing config system and provides
CLI-specific functionality with backup, rollback, and validation capabilities.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import yaml
from dotenv import load_dotenv, set_key, unset_key

from genebot.config.manager import ConfigManager, ConfigurationError, get_config_manager
from genebot.config.validation_utils import ConfigValidator, ConfigValidationResult
from genebot.config.models import TradingBotConfig
from .file_manager import FileManager
from .error_handler import CLIException, ConfigurationError
from ..result import CommandResult


class ConfigurationManager:
    """
    CLI Configuration Manager that integrates with existing config system.
    
    Provides safe file operations, backup/rollback capabilities, configuration
    validation, and template generation for CLI operations.
    """
    
    def __init__(self, config_path: Path, env_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration directory
            env_file: Path to environment file (defaults to .env)
        """
        self.config_path = Path(config_path)
        self.env_file = env_file or Path('.env')
        self.file_manager = FileManager(backup_dir=self.config_path / 'backups')
        
        # Initialize core config manager
        self._core_config_manager: Optional[ConfigManager] = None
        
        # Configuration file paths
        self.accounts_file = self.config_path / 'accounts.yaml'
        self.bot_config_file = self.config_path / 'trading_bot_config.yaml'
        self.multi_market_config_file = self.config_path / 'multi_market_config.yaml'
        
        # Ensure config directory exists
        self.file_manager.ensure_directory(self.config_path)
    
    @property
    def core_config_manager(self) -> ConfigManager:
        """Get or create core configuration manager instance"""
        if self._core_config_manager is None:
            try:
                # Try to get existing config manager
                self._core_config_manager = get_config_manager()
            except Exception:
                # Fallback: create new config manager
                self._core_config_manager = ConfigManager(
                    config_path=str(self.bot_config_file) if self.bot_config_file.exists() else None,
                    env_file=str(self.env_file) if self.env_file.exists() else None
                )
        return self._core_config_manager
    
    def validate_configuration(self) -> ConfigValidationResult:
        """
        Validate current configuration using existing validation utilities.
        
        Returns:
            ConfigValidationResult: Validation results with errors, warnings, and info
        """
        try:
            # Use existing validation utilities
            from genebot.config.validation_utils import validate_config_file
            
            # Validate main bot configuration
            if self.bot_config_file.exists():
                result = validate_config_file(self.bot_config_file)
            else:
                result = ConfigValidationResult()
                result.add_error("Main bot configuration file not found")
                if hasattr(result, 'add_info'):
                    result.add_info("Run 'genebot init-config' to create configuration files")
            
            # Additional CLI-specific validations
            self._validate_cli_requirements(result)
            
            return result
            
        except Exception as e:
            result = ConfigValidationResult()
            result.add_error(f"Configuration validation failed: {str(e)}")
            return result
    
    def _validate_cli_requirements(self, result: ConfigValidationResult) -> None:
        """Perform CLI-specific configuration validation"""
        # Check required directories
        required_dirs = ['logs', 'reports', 'backups']
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                result.add_warning(f"Required directory missing: {dir_name}")
                if hasattr(result, 'add_info'):
                    result.add_info(f"Create directory with 'mkdir -p {dir_name}'")
        
        # Check environment file
        if not self.env_file.exists():
            result.add_error("Environment file (.env) not found")
            if hasattr(result, 'add_info'):
                result.add_info("Create .env file with API credentials")
        else:
            # Check for placeholder values in .env
            try:
                with open(self.env_file, 'r') as f:
                    env_content = f.read()
                    
                placeholder_patterns = ['your_', 'placeholder', 'example', 'test_']
                for pattern in placeholder_patterns:
                    if pattern in env_content.lower():
                        result.add_warning("Environment file contains placeholder values")
                        if hasattr(result, 'add_info'):
                            result.add_info("Update .env file with actual API credentials")
                        break
            except Exception:
                result.add_warning("Could not read environment file")
        
        # Check accounts configuration
        if not self.accounts_file.exists():
            result.add_warning("Accounts configuration file not found")
            result.add_suggestion("Add accounts with 'genebot add-crypto' or 'genebot add-forex'")
    
    def load_configuration(self) -> TradingBotConfig:
        """
        Load and validate complete configuration.
        
        Returns:
            TradingBotConfig: Validated configuration object
            
        Raises:
            CLIConfigurationError: If configuration cannot be loaded or is invalid
        """
        try:
            return self.core_config_manager.load_config()
        except Exception as e:  # Catch any configuration error from core manager
            raise ConfigurationError(
                f"Failed to load configuration: {str(e)}",
                suggestions=[
                    "Check configuration file syntax",
                    "Validate environment variables",
                    "Run 'genebot validate' for detailed error information"
                ]
            )
    
    def reload_configuration(self) -> TradingBotConfig:
        """
        Reload configuration from files.
        
        Returns:
            TradingBotConfig: Reloaded configuration
        """
        self._core_config_manager = None  # Force recreation
        return self.load_configuration()
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create backup of configuration file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file or None if file doesn't exist
        """
        return self.file_manager.create_backup(file_path)
    
    def restore_backup(self, file_path: Path) -> bool:
        """
        Restore file from most recent backup.
        
        Args:
            file_path: Path to file to restore
            
        Returns:
            True if restore successful, False otherwise
        """
        return self.file_manager.restore_backup(file_path)
    
    def list_backups(self, file_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        List available configuration backups.
        
        Args:
            file_path: Optional specific file to list backups for
            
        Returns:
            List of backup information dictionaries
        """
        return self.file_manager.list_backups(file_path)
    
    def save_accounts_config(self, accounts_data: Dict[str, Any]) -> None:
        """
        Save accounts configuration with backup.
        
        Args:
            accounts_data: Accounts configuration data
        """
        self.file_manager.safe_write_yaml(self.accounts_file, accounts_data)
    
    def load_accounts_config(self) -> Dict[str, Any]:
        """
        Load accounts configuration.
        
        Returns:
            Accounts configuration data
            
        Raises:
            FileNotFoundError: If accounts.yaml doesn't exist
        """
        if not self.accounts_file.exists():
            raise FileNotFoundError(f"Accounts configuration file not found: {self.accounts_file}")
        
        return self.file_manager.read_yaml(self.accounts_file)
    
    def save_bot_config(self, bot_config_data: Dict[str, Any]) -> None:
        """
        Save bot configuration with backup.
        
        Args:
            bot_config_data: Bot configuration data
        """
        self.file_manager.safe_write_yaml(self.bot_config_file, bot_config_data)
    
    def load_bot_config(self) -> Dict[str, Any]:
        """
        Load bot configuration.
        
        Returns:
            Bot configuration data
        """
        if not self.bot_config_file.exists():
            return self._get_default_bot_config()
        
        return self.file_manager.read_yaml(self.bot_config_file)
    
    def update_env_variable(self, key: str, value: str) -> None:
        """
        Update environment variable in .env file.
        
        Args:
            key: Environment variable name
            value: Environment variable value
        """
        if not self.env_file.exists():
            self.env_file.touch()
        
        # Create backup before modification
        self.create_backup(self.env_file)
        
        # Update the variable
        set_key(str(self.env_file), key, value)
        
        # Reload environment
        load_dotenv(self.env_file, override=True)
    
    def remove_env_variable(self, key: str) -> None:
        """
        Remove environment variable from .env file.
        
        Args:
            key: Environment variable name to remove
        """
        if not self.env_file.exists():
            return
        
        # Create backup before modification
        self.create_backup(self.env_file)
        
        # Remove the variable
        unset_key(str(self.env_file), key)
        
        # Reload environment
        load_dotenv(self.env_file, override=True)
    
    def get_env_variables(self) -> Dict[str, str]:
        """
        Get all environment variables from .env file.
        
        Returns:
            Dictionary of environment variables
        """
        if not self.env_file.exists():
            return {}
        
        env_vars = {}
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')
        except Exception:
            pass
        
        return env_vars
    
    def generate_config_template(self, template_type: str = 'development') -> Dict[str, Dict[str, Any]]:
        """
        Generate configuration templates for initialization.
        
        Args:
            template_type: Type of template ('development', 'production', 'testing')
            
        Returns:
            Dictionary containing all configuration templates
        """
        templates = {}
        
        # Bot configuration template
        templates['bot_config'] = self._get_bot_config_template(template_type)
        
        # Accounts configuration template
        templates['accounts'] = self._get_accounts_config_template(template_type)
        
        # Environment variables template
        templates['env'] = self._get_env_template(template_type)
        
        return templates
    
    def initialize_configuration(self, template_type: str = 'development', 
                               overwrite: bool = False) -> CommandResult:
        """
        Initialize configuration files from templates.
        
        Args:
            template_type: Type of template to use
            overwrite: Whether to overwrite existing files
            
        Returns:
            CommandResult with initialization status
        """
        created_files = []
        skipped_files = []
        
        try:
            # Create required directories
            required_dirs = [
                self.config_path,
                Path('logs'),
                Path('reports'),
                Path('backups')
            ]
            
            for dir_path in required_dirs:
                self.file_manager.ensure_directory(dir_path)
            
            # Generate templates
            templates = self.generate_config_template(template_type)
            
            # Create bot configuration
            if not self.bot_config_file.exists() or overwrite:
                self.file_manager.safe_write_yaml(
                    self.bot_config_file, 
                    templates['bot_config'],
                    create_backup=overwrite
                )
                created_files.append(str(self.bot_config_file))
            else:
                skipped_files.append(str(self.bot_config_file))
            
            # Create accounts configuration
            if not self.accounts_file.exists() or overwrite:
                self.file_manager.safe_write_yaml(
                    self.accounts_file,
                    templates['accounts'],
                    create_backup=overwrite
                )
                created_files.append(str(self.accounts_file))
            else:
                skipped_files.append(str(self.accounts_file))
            
            # Create environment file
            if not self.env_file.exists() or overwrite:
                env_content = self._format_env_content(templates['env'])
                self.file_manager.safe_write_text(
                    self.env_file,
                    env_content,
                    create_backup=overwrite
                )
                created_files.append(str(self.env_file))
            else:
                skipped_files.append(str(self.env_file))
            
            # Prepare result message
            message_parts = []
            if created_files:
                message_parts.append(f"Created {len(created_files)} configuration files")
            if skipped_files:
                message_parts.append(f"Skipped {len(skipped_files)} existing files")
            
            message = "; ".join(message_parts) if message_parts else "No files created"
            
            suggestions = [
                "Edit .env file to add your API credentials",
                "Add trading accounts with 'genebot add-crypto' or 'genebot add-forex'",
                "Run 'genebot validate' to check configuration",
                "Use 'genebot config-help' for detailed setup guide"
            ]
            
            return CommandResult.success(
                message,
                data={
                    'created_files': created_files,
                    'skipped_files': skipped_files,
                    'template_type': template_type
                },
                suggestions=suggestions
            )
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to initialize configuration: {str(e)}",
                suggestions=[
                    "Check directory permissions",
                    "Ensure sufficient disk space",
                    "Try with --overwrite flag if files exist"
                ]
            )
    
    def _get_bot_config_template(self, template_type: str) -> Dict[str, Any]:
        """Generate bot configuration template"""
        is_production = template_type == 'production'
        
        return {
            'app_name': 'GeneBot',
            'version': '1.1.28',
            'debug': not is_production,
            'dry_run': not is_production,
            'base_currency': 'USDT',
            'exchanges': {},  # Will be populated when accounts are added
            'strategies': {
                'rsi_strategy': {
                    'strategy_type': 'rsi',
                    'enabled': True,
                    'symbols': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT'],
                    'timeframe': '1h',
                    'parameters': {
                        'rsi_period': 14,
                        'oversold_threshold': 30,
                        'overbought_threshold': 70,
                        'min_confidence': 0.7
                    },
                    'max_positions': 3,
                    'risk_per_trade': 0.02
                },
                'moving_average_strategy': {
                    'strategy_type': 'moving_average',
                    'enabled': True,
                    'symbols': ['BTC/USDT', 'ETH/USDT', 'LTC/USDT'],
                    'timeframe': '4h',
                    'parameters': {
                        'short_window': 10,
                        'long_window': 30,
                        'min_confidence': 0.7
                    },
                    'max_positions': 2,
                    'risk_per_trade': 0.015
                },
                'multi_indicator_strategy': {
                    'strategy_type': 'multi_indicator',
                    'enabled': False,
                    'symbols': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT'],
                    'timeframe': '1h',
                    'parameters': {
                        'ma_fast': 10,
                        'ma_slow': 20,
                        'rsi_period': 14,
                        'rsi_oversold': 30,
                        'rsi_overbought': 70,
                        'min_confidence': 0.85
                    },
                    'max_positions': 3,
                    'risk_per_trade': 0.025
                },
                'forex_session_strategy': {
                    'strategy_type': 'forex_session',
                    'enabled': False,
                    'symbols': ['EUR/USD', 'GBP/USD', 'USD/JPY'],
                    'timeframe': '15m',
                    'parameters': {
                        'session_overlap_only': True,
                        'min_volatility_threshold': 0.0015,
                        'preferred_sessions': ['london', 'new_york'],
                        'min_confidence': 0.8
                    },
                    'max_positions': 2,
                    'risk_per_trade': 0.02
                },
                'cross_market_arbitrage_strategy': {
                    'strategy_type': 'cross_market_arbitrage',
                    'enabled': False,
                    'symbols': ['BTC/USD', 'EUR/USD'],
                    'timeframe': '5m',
                    'parameters': {
                        'min_arbitrage_opportunity': 0.001,
                        'max_execution_time': 30,
                        'correlation_threshold': 0.7,
                        'min_confidence': 0.90
                    },
                    'max_positions': 1,
                    'risk_per_trade': 0.005
                }
            },
            'risk': {
                'max_position_size': 0.1,
                'max_daily_loss': 0.05,
                'max_drawdown': 0.15,
                'stop_loss_percentage': 0.02,
                'max_open_positions': 5,
                'position_sizing_method': 'fixed_fraction',
                'risk_per_trade': 0.01
            },
            'database': {
                'database_type': 'sqlite',
                'database_url': 'sqlite:///genebot.db',
                'pool_size': 5,
                'echo': False
            },
            'logging': {
                'log_level': 'DEBUG' if not is_production else 'INFO',
                'log_format': 'standard',
                'log_file': 'logs/genebot.log',
                'max_file_size': 10485760,
                'backup_count': 5
            }
        }
    
    def _get_accounts_config_template(self, template_type: str) -> Dict[str, Any]:
        """Generate accounts configuration template"""
        return {
            'crypto_exchanges': {
                # Examples will be added when accounts are created
            },
            'forex_brokers': {
                # Examples will be added when accounts are created
            }
        }
    
    def _get_env_template(self, template_type: str) -> Dict[str, str]:
        """Generate environment variables template"""
        is_production = template_type == 'production'
        
        return {
            'GENEBOT_ENV': template_type,
            'DEBUG': 'false' if is_production else 'true',
            'DRY_RUN': 'false' if is_production else 'true',
            'APP_NAME': 'GeneBot',
            'APP_VERSION': '1.1.28',
            'LOG_LEVEL': 'INFO' if is_production else 'DEBUG',
            
            # Crypto Exchange API Keys
            'BINANCE_API_KEY': 'your_binance_api_key_here',
            'BINANCE_API_SECRET': 'your_binance_api_secret_here',
            'BINANCE_SANDBOX': 'false' if is_production else 'true',
            'COINBASE_API_KEY': 'your_coinbase_api_key_here',
            'COINBASE_API_SECRET': 'your_coinbase_api_secret_here',
            'COINBASE_PASSPHRASE': 'your_coinbase_passphrase_here',
            'COINBASE_SANDBOX': 'false' if is_production else 'true',
            'KRAKEN_API_KEY': 'your_kraken_api_key_here',
            'KRAKEN_API_SECRET': 'your_kraken_api_secret_here',
            'KUCOIN_API_KEY': 'your_kucoin_api_key_here',
            'KUCOIN_API_SECRET': 'your_kucoin_api_secret_here',
            'KUCOIN_PASSPHRASE': 'your_kucoin_passphrase_here',
            'KUCOIN_SANDBOX': 'false' if is_production else 'true',
            'BYBIT_API_KEY': 'your_bybit_api_key_here',
            'BYBIT_API_SECRET': 'your_bybit_api_secret_here',
            'BYBIT_SANDBOX': 'false' if is_production else 'true',
            
            # Forex Broker Credentials
            'OANDA_API_KEY': 'your_oanda_api_key_here',
            'OANDA_ACCOUNT_ID': 'your_oanda_account_id_here',
            'OANDA_ENVIRONMENT': 'live' if is_production else 'practice',
            'MT5_LOGIN': 'your_mt5_login_here',
            'MT5_PASSWORD': 'your_mt5_password_here',
            'MT5_SERVER': 'your_mt5_server_here',
            'MT5_PATH': '/Applications/MetaTrader 5/terminal64.exe',
            'IB_HOST': '127.0.0.1',
            'IB_PORT': '7496' if is_production else '7497',
            'IB_CLIENT_ID': '1',
            'ALPACA_API_KEY': 'your_alpaca_api_key_here',
            'ALPACA_API_SECRET': 'your_alpaca_api_secret_here',
            'ALPACA_BASE_URL': 'https://api.alpaca.markets' if is_production else 'https://paper-api.alpaca.markets',
            'FXCM_API_KEY': 'your_fxcm_api_key_here',
            'FXCM_ACCESS_TOKEN': 'your_fxcm_access_token_here',
            'FXCM_SERVER': 'real' if is_production else 'demo',
            
            # Database and other settings
            'DATABASE_URL': 'sqlite:///genebot.db',
            'PORTFOLIO_VALUE': '100000',
            'BASE_CURRENCY': 'USD',
            'RISK_PER_TRADE': '0.01',
            'MAX_DAILY_LOSS': '0.05'
        }
    
    def _get_default_bot_config(self) -> Dict[str, Any]:
        """Get default bot configuration"""
        return self._get_bot_config_template('development')
    
    def _format_env_content(self, env_vars: Dict[str, str]) -> str:
        """Format environment variables into .env file content with comments"""
        lines = [
            "# GeneBot Multi-Market Trading Bot Configuration",
            "# Generated automatically - edit as needed",
            "",
            "# Application Settings",
            f"GENEBOT_ENV={env_vars.get('GENEBOT_ENV', 'development')}",
            f"DEBUG={env_vars.get('DEBUG', 'true')}",
            f"DRY_RUN={env_vars.get('DRY_RUN', 'true')}",
            f"APP_NAME={env_vars.get('APP_NAME', 'GeneBot')}",
            f"APP_VERSION={env_vars.get('APP_VERSION', '1.1.28')}",
            f"LOG_LEVEL={env_vars.get('LOG_LEVEL', 'DEBUG')}",
            "",
            "# =============================================================================",
            "# CRYPTO EXCHANGE API CREDENTIALS",
            "# =============================================================================",
            "",
            "# Binance (Primary crypto exchange)",
            f"BINANCE_API_KEY={env_vars.get('BINANCE_API_KEY', 'your_binance_api_key_here')}",
            f"BINANCE_API_SECRET={env_vars.get('BINANCE_API_SECRET', 'your_binance_api_secret_here')}",
            f"BINANCE_SANDBOX={env_vars.get('BINANCE_SANDBOX', 'true')}",
            "",
            "# Coinbase Pro",
            f"COINBASE_API_KEY={env_vars.get('COINBASE_API_KEY', 'your_coinbase_api_key_here')}",
            f"COINBASE_API_SECRET={env_vars.get('COINBASE_API_SECRET', 'your_coinbase_api_secret_here')}",
            f"COINBASE_PASSPHRASE={env_vars.get('COINBASE_PASSPHRASE', 'your_coinbase_passphrase_here')}",
            f"COINBASE_SANDBOX={env_vars.get('COINBASE_SANDBOX', 'true')}",
            "",
            "# Kraken",
            f"KRAKEN_API_KEY={env_vars.get('KRAKEN_API_KEY', 'your_kraken_api_key_here')}",
            f"KRAKEN_API_SECRET={env_vars.get('KRAKEN_API_SECRET', 'your_kraken_api_secret_here')}",
            "",
            "# KuCoin",
            f"KUCOIN_API_KEY={env_vars.get('KUCOIN_API_KEY', 'your_kucoin_api_key_here')}",
            f"KUCOIN_API_SECRET={env_vars.get('KUCOIN_API_SECRET', 'your_kucoin_api_secret_here')}",
            f"KUCOIN_PASSPHRASE={env_vars.get('KUCOIN_PASSPHRASE', 'your_kucoin_passphrase_here')}",
            f"KUCOIN_SANDBOX={env_vars.get('KUCOIN_SANDBOX', 'true')}",
            "",
            "# Bybit",
            f"BYBIT_API_KEY={env_vars.get('BYBIT_API_KEY', 'your_bybit_api_key_here')}",
            f"BYBIT_API_SECRET={env_vars.get('BYBIT_API_SECRET', 'your_bybit_api_secret_here')}",
            f"BYBIT_SANDBOX={env_vars.get('BYBIT_SANDBOX', 'true')}",
            "",
            "# =============================================================================",
            "# FOREX BROKER CREDENTIALS",
            "# =============================================================================",
            "",
            "# OANDA (Primary forex broker)",
            f"OANDA_API_KEY={env_vars.get('OANDA_API_KEY', 'your_oanda_api_key_here')}",
            f"OANDA_ACCOUNT_ID={env_vars.get('OANDA_ACCOUNT_ID', 'your_oanda_account_id_here')}",
            f"OANDA_ENVIRONMENT={env_vars.get('OANDA_ENVIRONMENT', 'practice')}",
            "",
            "# MetaTrader 5",
            f"MT5_LOGIN={env_vars.get('MT5_LOGIN', 'your_mt5_login_here')}",
            f"MT5_PASSWORD={env_vars.get('MT5_PASSWORD', 'your_mt5_password_here')}",
            f"MT5_SERVER={env_vars.get('MT5_SERVER', 'your_mt5_server_here')}",
            f"MT5_PATH={env_vars.get('MT5_PATH', '/Applications/MetaTrader 5/terminal64.exe')}",
            "",
            "# Interactive Brokers",
            f"IB_HOST={env_vars.get('IB_HOST', '127.0.0.1')}",
            f"IB_PORT={env_vars.get('IB_PORT', '7497')}",
            f"IB_CLIENT_ID={env_vars.get('IB_CLIENT_ID', '1')}",
            "",
            "# Alpaca (Forex)",
            f"ALPACA_API_KEY={env_vars.get('ALPACA_API_KEY', 'your_alpaca_api_key_here')}",
            f"ALPACA_API_SECRET={env_vars.get('ALPACA_API_SECRET', 'your_alpaca_api_secret_here')}",
            f"ALPACA_BASE_URL={env_vars.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')}",
            "",
            "# FXCM",
            f"FXCM_API_KEY={env_vars.get('FXCM_API_KEY', 'your_fxcm_api_key_here')}",
            f"FXCM_ACCESS_TOKEN={env_vars.get('FXCM_ACCESS_TOKEN', 'your_fxcm_access_token_here')}",
            f"FXCM_SERVER={env_vars.get('FXCM_SERVER', 'demo')}",
            "",
            "# =============================================================================",
            "# TRADING CONFIGURATION",
            "# =============================================================================",
            "",
            f"DATABASE_URL={env_vars.get('DATABASE_URL', 'sqlite:///genebot.db')}",
            f"PORTFOLIO_VALUE={env_vars.get('PORTFOLIO_VALUE', '100000')}",
            f"BASE_CURRENCY={env_vars.get('BASE_CURRENCY', 'USD')}",
            f"RISK_PER_TRADE={env_vars.get('RISK_PER_TRADE', '0.01')}",
            f"MAX_DAILY_LOSS={env_vars.get('MAX_DAILY_LOSS', '0.05')}",
            ""
        ]
        return '\n'.join(lines)
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive configuration status.
        
        Returns:
            Dictionary with configuration status information
        """
        status = {
            'config_directory': {
                'path': str(self.config_path),
                'exists': self.config_path.exists(),
                'writable': self.config_path.exists() and os.access(self.config_path, os.W_OK)
            },
            'files': {},
            'validation': None,
            'backups_available': len(self.list_backups()) > 0
        }
        
        # Check configuration files
        config_files = {
            'bot_config': self.bot_config_file,
            'accounts': self.accounts_file,
            'env': self.env_file
        }
        
        for name, file_path in config_files.items():
            status['files'][name] = self.file_manager.get_file_info(file_path)
        
        # Run validation if possible
        try:
            validation_result = self.validate_configuration()
            status['validation'] = {
                'is_valid': validation_result.is_valid,
                'error_count': len(validation_result.errors),
                'warning_count': len(validation_result.warnings),
                'errors': validation_result.errors,
                'warnings': validation_result.warnings
            }
        except Exception as e:
            status['validation'] = {
                'is_valid': False,
                'error': str(e)
            }
        
        return status