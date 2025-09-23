"""
Account Manager
===============

AccountManager class that reads/writes actual config files and provides
comprehensive account management functionality for the CLI.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import yaml
from dataclasses import dataclass, asdict

from .config_manager import ConfigurationManager
from .file_manager import FileManager
from .error_handler import CLIException, ConfigurationError
from ..result import CommandResult


@dataclass
class AccountInfo:
    """Account information structure"""
    name: str
    type: str  # 'crypto' or 'forex'
    exchange_or_broker: str
    enabled: bool
    sandbox: bool
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    additional_fields: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        result = {
            'name': self.name,
            'enabled': self.enabled,
            'sandbox': self.sandbox
        }
        
        if self.type == 'crypto':
            result['exchange_type'] = self.exchange_or_broker
            if self.api_key:
                result['api_key'] = self.api_key
            if self.api_secret:
                result['api_secret'] = self.api_secret
        elif self.type == 'forex':
            result['broker_type'] = self.exchange_or_broker
            if self.api_key:
                result['api_key'] = self.api_key
        
        # Add additional fields
        if self.additional_fields:
            result.update(self.additional_fields)
        
        return result


class AccountManager:
    """
    Account Manager that handles real configuration file operations.
    
    Provides functionality to:
    - Read/write accounts.yaml configuration
    - Add, edit, and remove accounts
    - Validate account configurations
    - Manage environment variables for credentials
    """
    
    def __init__(self, config_path: Path = None, env_file: Path = None):
        """
        Initialize account manager.
        
        Args:
            config_path: Path to configuration directory
            env_file: Path to environment file
        """
        self.config_path = config_path or Path("config")
        self.env_file = env_file or Path(".env")
        
        # Initialize managers
        self.config_manager = ConfigurationManager(self.config_path, self.env_file)
        self.file_manager = FileManager(backup_dir=self.config_path / 'backups')
        
        # Account configuration file
        self.accounts_file = self.config_path / "accounts.yaml"
        
        # Supported exchanges and brokers
        self.supported_crypto_exchanges = [
            'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 
            'okx', 'bybit', 'kucoin', 'gate', 'ftx'
        ]
        
        self.supported_forex_brokers = [
            'oanda', 'ib', 'mt5', 'fxcm', 'pepperstone'
        ]
    
    def get_all_accounts(self) -> List[AccountInfo]:
        """
        Get all configured accounts.
        
        Returns:
            List of AccountInfo objects
        """
        try:
            accounts_config = self.config_manager.load_accounts_config()
            accounts = []
            
            # Process crypto exchanges
            crypto_exchanges = accounts_config.get('crypto_exchanges', {})
            for name, config in crypto_exchanges.items():
                account = AccountInfo(
                    name=name,
                    type='crypto',
                    exchange_or_broker=config.get('exchange_type', 'unknown'),
                    enabled=config.get('enabled', False),
                    sandbox=config.get('sandbox', True),
                    api_key=config.get('api_key'),
                    api_secret=config.get('api_secret'),
                    additional_fields={k: v for k, v in config.items() 
                                     if k not in ['name', 'exchange_type', 'enabled', 'sandbox', 'api_key', 'api_secret']}
                )
                accounts.append(account)
            
            # Process forex brokers
            forex_brokers = accounts_config.get('forex_brokers', {})
            for name, config in forex_brokers.items():
                account = AccountInfo(
                    name=name,
                    type='forex',
                    exchange_or_broker=config.get('broker_type', 'unknown'),
                    enabled=config.get('enabled', False),
                    sandbox=config.get('sandbox', True),
                    api_key=config.get('api_key'),
                    additional_fields={k: v for k, v in config.items() 
                                     if k not in ['name', 'broker_type', 'enabled', 'sandbox', 'api_key']}
                )
                accounts.append(account)
            
            return accounts
            
        except FileNotFoundError:
            raise ConfigurationError(
                "Accounts configuration file not found",
                suggestions=[
                    "Create config/accounts.yaml file",
                    "Run 'genebot init-config' to create configuration files",
                    "Add accounts with 'genebot add-crypto' or 'genebot add-forex'"
                ]
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load accounts: {str(e)}",
                suggestions=[
                    "Check config/accounts.yaml file format",
                    "Verify file permissions",
                    "Run 'genebot init-config' to create configuration files"
                ]
            )
    
    def get_account_by_name(self, name: str) -> Optional[AccountInfo]:
        """
        Get account by name.
        
        Args:
            name: Account name
            
        Returns:
            AccountInfo or None if not found
        """
        accounts = self.get_all_accounts()
        for account in accounts:
            if account.name == name:
                return account
        return None
    
    def account_exists(self, name: str) -> bool:
        """
        Check if account exists.
        
        Args:
            name: Account name
            
        Returns:
            True if account exists
        """
        return self.get_account_by_name(name) is not None
    
    def validate_exchange_type(self, exchange_type: str) -> bool:
        """
        Validate crypto exchange type.
        
        Args:
            exchange_type: Exchange type to validate
            
        Returns:
            True if supported
        """
        return exchange_type.lower() in self.supported_crypto_exchanges
    
    def validate_broker_type(self, broker_type: str) -> bool:
        """
        Validate forex broker type.
        
        Args:
            broker_type: Broker type to validate
            
        Returns:
            True if supported
        """
        return broker_type.lower() in self.supported_forex_brokers
    
    def add_crypto_account(self, exchange_type: str, name: str = None, 
                          mode: str = 'demo', api_key: str = None, 
                          api_secret: str = None, **kwargs) -> CommandResult:
        """
        Add a crypto exchange account.
        
        Args:
            exchange_type: Type of exchange (binance, coinbase, etc.)
            name: Account name (auto-generated if None)
            mode: Account mode ('demo' or 'live')
            api_key: API key (optional, can be set later)
            api_secret: API secret (optional, can be set later)
            **kwargs: Additional configuration parameters
            
        Returns:
            CommandResult with operation status
        """
        try:
            # Validate exchange type
            if not self.validate_exchange_type(exchange_type):
                return CommandResult.error(
                    f"Unsupported exchange type: {exchange_type}",
                    suggestions=[
                        f"Supported exchanges: {', '.join(self.supported_crypto_exchanges)}",
                        "Check exchange name spelling",
                        "Use 'genebot list-exchanges' to see all supported exchanges"
                    ]
                )
            
            # Generate account name if not provided
            if not name:
                name = f"{exchange_type}-{mode}"
            
            # Check if account already exists
            if self.account_exists(name):
                return CommandResult.error(
                    f"Account '{name}' already exists",
                    suggestions=[
                        f"Use a different name",
                        f"Edit existing account with 'genebot edit-crypto {name}'",
                        f"Remove existing account with 'genebot remove-account {name}'"
                    ]
                )
            
            # Load current configuration
            accounts_config = self.config_manager.load_accounts_config()
            
            # Prepare account configuration
            account_config = {
                'name': name,
                'exchange_type': exchange_type.lower(),
                'enabled': kwargs.get('enabled', True),
                'sandbox': mode == 'demo',
                'rate_limit': kwargs.get('rate_limit', 1200),
                'timeout': kwargs.get('timeout', 30)
            }
            
            # Add API credentials if provided
            if api_key:
                account_config['api_key'] = api_key
            else:
                # Use environment variable reference
                env_key = f"{exchange_type.upper()}_{mode.upper()}_API_KEY"
                account_config['api_key'] = f"${{{env_key}}}"
            
            if api_secret:
                account_config['api_secret'] = api_secret
            else:
                # Use environment variable reference
                env_secret = f"{exchange_type.upper()}_{mode.upper()}_API_SECRET"
                account_config['api_secret'] = f"${{{env_secret}}}"
            
            # Add exchange-specific fields
            if exchange_type.lower() == 'coinbase':
                passphrase_key = f"{exchange_type.upper()}_{mode.upper()}_PASSPHRASE"
                account_config['api_passphrase'] = kwargs.get('api_passphrase', f"${{{passphrase_key}}}")
            
            # Add additional fields
            for key, value in kwargs.items():
                if key not in ['enabled', 'rate_limit', 'timeout', 'api_passphrase']:
                    account_config[key] = value
            
            # Add to configuration
            if 'crypto_exchanges' not in accounts_config:
                accounts_config['crypto_exchanges'] = {}
            
            accounts_config['crypto_exchanges'][name] = account_config
            
            # Save configuration
            self.config_manager.save_accounts_config(accounts_config)
            
            # Generate environment variable suggestions
            env_suggestions = []
            if not api_key:
                env_key = f"{exchange_type.upper()}_{mode.upper()}_API_KEY"
                env_suggestions.append(f"Set {env_key} in .env file")
            
            if not api_secret:
                env_secret = f"{exchange_type.upper()}_{mode.upper()}_API_SECRET"
                env_suggestions.append(f"Set {env_secret} in .env file")
            
            if exchange_type.lower() == 'coinbase' and 'api_passphrase' not in kwargs:
                passphrase_key = f"{exchange_type.upper()}_{mode.upper()}_PASSPHRASE"
                env_suggestions.append(f"Set {passphrase_key} in .env file")
            
            suggestions = [
                "Run 'genebot validate-accounts' to test connectivity",
                "Use 'genebot list-accounts' to view all accounts"
            ]
            suggestions.extend(env_suggestions)
            
            return CommandResult.success(
                f"Crypto account '{name}' added successfully",
                data={
                    'account_name': name,
                    'exchange_type': exchange_type,
                    'mode': mode,
                    'sandbox': mode == 'demo'
                },
                suggestions=suggestions
            )
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to add crypto account: {str(e)}",
                suggestions=[
                    "Check configuration file permissions",
                    "Verify account parameters",
                    "Check log files for detailed error information"
                ]
            )
    
    def add_forex_account(self, broker_type: str, name: str = None, 
                         mode: str = 'demo', api_key: str = None, 
                         account_id: str = None, **kwargs) -> CommandResult:
        """
        Add a forex broker account.
        
        Args:
            broker_type: Type of broker (oanda, ib, mt5, etc.)
            name: Account name (auto-generated if None)
            mode: Account mode ('demo' or 'live')
            api_key: API key (for OANDA)
            account_id: Account ID (for OANDA)
            **kwargs: Additional configuration parameters
            
        Returns:
            CommandResult with operation status
        """
        try:
            # Validate broker type
            if not self.validate_broker_type(broker_type):
                return CommandResult.error(
                    f"Unsupported broker type: {broker_type}",
                    suggestions=[
                        f"Supported brokers: {', '.join(self.supported_forex_brokers)}",
                        "Check broker name spelling",
                        "Use 'genebot list-brokers' to see all supported brokers"
                    ]
                )
            
            # Generate account name if not provided
            if not name:
                name = f"{broker_type}-{mode}"
            
            # Check if account already exists
            if self.account_exists(name):
                return CommandResult.error(
                    f"Account '{name}' already exists",
                    suggestions=[
                        f"Use a different name",
                        f"Edit existing account with 'genebot edit-forex {name}'",
                        f"Remove existing account with 'genebot remove-account {name}'"
                    ]
                )
            
            # Load current configuration
            accounts_config = self.config_manager.load_accounts_config()
            
            # Prepare account configuration based on broker type
            account_config = {
                'name': name,
                'broker_type': broker_type.lower(),
                'enabled': kwargs.get('enabled', True),
                'sandbox': mode == 'demo',
                'timeout': kwargs.get('timeout', 30)
            }
            
            # Add broker-specific configuration
            if broker_type.lower() == 'oanda':
                if api_key:
                    account_config['api_key'] = api_key
                else:
                    env_key = f"OANDA_{mode.upper()}_API_KEY"
                    account_config['api_key'] = f"${{{env_key}}}"
                
                if account_id:
                    account_config['account_id'] = account_id
                else:
                    env_account_id = f"OANDA_{mode.upper()}_ACCOUNT_ID"
                    account_config['account_id'] = f"${{{env_account_id}}}"
                
                account_config['max_retries'] = kwargs.get('max_retries', 3)
                
            elif broker_type.lower() == 'ib':
                account_config['host'] = kwargs.get('host', 'localhost')
                account_config['port'] = kwargs.get('port', 7497 if mode == 'demo' else 7496)
                account_config['client_id'] = kwargs.get('client_id', 1)
                
            elif broker_type.lower() == 'mt5':
                login_env = f"MT5_{mode.upper()}_LOGIN"
                password_env = f"MT5_{mode.upper()}_PASSWORD"
                server_env = f"MT5_{mode.upper()}_SERVER"
                
                account_config['login'] = kwargs.get('login', f"${{{login_env}}}")
                account_config['password'] = kwargs.get('password', f"${{{password_env}}}")
                account_config['server'] = kwargs.get('server', f"${{{server_env}}}")
                account_config['path'] = kwargs.get('path', '')
            
            # Add additional fields
            for key, value in kwargs.items():
                if key not in ['enabled', 'timeout', 'max_retries', 'host', 'port', 'client_id', 'login', 'password', 'server', 'path']:
                    account_config[key] = value
            
            # Add to configuration
            if 'forex_brokers' not in accounts_config:
                accounts_config['forex_brokers'] = {}
            
            accounts_config['forex_brokers'][name] = account_config
            
            # Save configuration
            self.config_manager.save_accounts_config(accounts_config)
            
            # Generate environment variable suggestions
            env_suggestions = []
            if broker_type.lower() == 'oanda':
                if not api_key:
                    env_key = f"OANDA_{mode.upper()}_API_KEY"
                    env_suggestions.append(f"Set {env_key} in .env file")
                if not account_id:
                    env_account_id = f"OANDA_{mode.upper()}_ACCOUNT_ID"
                    env_suggestions.append(f"Set {env_account_id} in .env file")
            elif broker_type.lower() == 'mt5':
                if 'login' not in kwargs:
                    env_suggestions.append(f"Set MT5_{mode.upper()}_LOGIN in .env file")
                if 'password' not in kwargs:
                    env_suggestions.append(f"Set MT5_{mode.upper()}_PASSWORD in .env file")
                if 'server' not in kwargs:
                    env_suggestions.append(f"Set MT5_{mode.upper()}_SERVER in .env file")
            
            suggestions = [
                "Run 'genebot validate-accounts' to test connectivity",
                "Use 'genebot list-accounts' to view all accounts"
            ]
            suggestions.extend(env_suggestions)
            
            return CommandResult.success(
                f"Forex account '{name}' added successfully",
                data={
                    'account_name': name,
                    'broker_type': broker_type,
                    'mode': mode,
                    'sandbox': mode == 'demo'
                },
                suggestions=suggestions
            )
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to add forex account: {str(e)}",
                suggestions=[
                    "Check configuration file permissions",
                    "Verify account parameters",
                    "Check log files for detailed error information"
                ]
            )
    
    def edit_account(self, name: str, interactive: bool = False, **updates) -> CommandResult:
        """
        Edit an existing account.
        
        Args:
            name: Account name to edit
            interactive: Whether to use interactive editing
            **updates: Fields to update
            
        Returns:
            CommandResult with operation status
        """
        try:
            # Check if account exists
            account = self.get_account_by_name(name)
            if not account:
                return CommandResult.error(
                    f"Account '{name}' not found",
                    suggestions=[
                        "Use 'genebot list-accounts' to see available accounts",
                        "Check account name spelling",
                        f"Add account with 'genebot add-crypto' or 'genebot add-forex'"
                    ]
                )
            
            # Load current configuration
            accounts_config = self.config_manager.load_accounts_config()
            
            # Get account configuration section
            if account.type == 'crypto':
                account_config = accounts_config['crypto_exchanges'][name]
            else:
                account_config = accounts_config['forex_brokers'][name]
            
            # Interactive editing
            if interactive:
                return self._interactive_edit_account(name, account, account_config)
            
            # Apply updates
            if not updates:
                return CommandResult.error(
                    "No updates provided",
                    suggestions=[
                        "Specify fields to update as arguments",
                        "Use --interactive flag for interactive editing",
                        f"Example: genebot edit-{account.type} {name} --enabled true"
                    ]
                )
            
            # Validate and apply updates
            updated_fields = []
            for field, value in updates.items():
                if field in account_config:
                    old_value = account_config[field]
                    account_config[field] = value
                    updated_fields.append(f"{field}: {old_value} -> {value}")
                else:
                    return CommandResult.error(
                        f"Unknown field '{field}' for {account.type} account",
                        suggestions=[
                            f"Valid fields: {', '.join(account_config.keys())}",
                            "Use --interactive flag to see all available fields"
                        ]
                    )
            
            # Save configuration
            self.config_manager.save_accounts_config(accounts_config)
            
            return CommandResult.success(
                f"Account '{name}' updated successfully",
                data={
                    'account_name': name,
                    'updated_fields': updated_fields
                },
                suggestions=[
                    "Run 'genebot validate-accounts' to test changes",
                    "Use 'genebot list-accounts' to view updated configuration"
                ]
            )
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to edit account: {str(e)}",
                suggestions=[
                    "Check configuration file permissions",
                    "Verify update parameters",
                    "Check log files for detailed error information"
                ]
            )
    
    def _interactive_edit_account(self, name: str, account: AccountInfo, 
                                 account_config: Dict[str, Any]) -> CommandResult:
        """
        Interactive account editing.
        
        Args:
            name: Account name
            account: Account information
            account_config: Current account configuration
            
        Returns:
            CommandResult with operation status
        """
        try:
            print(f"\nEditing account: {name}")
            print(f"Type: {account.type}")
            print(f"Exchange/Broker: {account.exchange_or_broker}")
            print("\nCurrent configuration:")
            
            # Display current values
            for key, value in account_config.items():
                if key not in ['api_key', 'api_secret', 'password']:  # Hide sensitive fields
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: [HIDDEN]")
            
            print("\nEnter new values (press Enter to keep current value):")
            
            # Interactive prompts for common fields
            editable_fields = ['enabled', 'sandbox', 'timeout']
            if account.type == 'crypto':
                editable_fields.extend(['rate_limit'])
            elif account.type == 'forex' and account.exchange_or_broker == 'oanda':
                editable_fields.extend(['max_retries'])
            elif account.type == 'forex' and account.exchange_or_broker == 'ib':
                editable_fields.extend(['host', 'port', 'client_id'])
            
            updates = {}
            for field in editable_fields:
                if field in account_config:
                    current_value = account_config[field]
                    try:
                        new_value = input(f"{field} [{current_value}]: ").strip()
                        if new_value:
                            # Type conversion
                            if isinstance(current_value, bool):
                                new_value = new_value.lower() in ('true', 'yes', '1', 'on')
                            elif isinstance(current_value, int):
                                new_value = int(new_value)
                            elif isinstance(current_value, float):
                                new_value = float(new_value)
                            
                            updates[field] = new_value
                    except (ValueError, KeyboardInterrupt):
                        print("Invalid input or cancelled")
                        return CommandResult.info("Account editing cancelled")
            
            if not updates:
                return CommandResult.info("No changes made")
            
            # Apply updates
            return self.edit_account(name, interactive=False, **updates)
            
        except Exception as e:
            return CommandResult.error(
                f"Interactive editing failed: {str(e)}",
                suggestions=[
                    "Try non-interactive editing",
                    "Check terminal compatibility"
                ]
            )
    
    def remove_account(self, name: str, confirm: bool = False) -> CommandResult:
        """
        Remove an account.
        
        Args:
            name: Account name to remove
            confirm: Skip confirmation prompt
            
        Returns:
            CommandResult with operation status
        """
        try:
            # Check if account exists
            account = self.get_account_by_name(name)
            if not account:
                return CommandResult.error(
                    f"Account '{name}' not found",
                    suggestions=[
                        "Use 'genebot list-accounts' to see available accounts",
                        "Check account name spelling"
                    ]
                )
            
            # Confirmation prompt
            if not confirm:
                try:
                    response = input(f"Are you sure you want to remove account '{name}'? (y/N): ").strip().lower()
                    if response not in ('y', 'yes'):
                        return CommandResult.info("Account removal cancelled")
                except KeyboardInterrupt:
                    return CommandResult.info("Account removal cancelled")
            
            # Load current configuration
            accounts_config = self.config_manager.load_accounts_config()
            
            # Remove account from configuration
            if account.type == 'crypto':
                if name in accounts_config.get('crypto_exchanges', {}):
                    del accounts_config['crypto_exchanges'][name]
            else:
                if name in accounts_config.get('forex_brokers', {}):
                    del accounts_config['forex_brokers'][name]
            
            # Save configuration
            self.config_manager.save_accounts_config(accounts_config)
            
            return CommandResult.success(
                f"Account '{name}' removed successfully",
                data={'account_name': name, 'account_type': account.type},
                suggestions=[
                    "Use 'genebot list-accounts' to view remaining accounts",
                    "Consider removing related environment variables from .env file"
                ]
            )
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to remove account: {str(e)}",
                suggestions=[
                    "Check configuration file permissions",
                    "Check log files for detailed error information"
                ]
            )
    
    def enable_account(self, name: str) -> CommandResult:
        """
        Enable an account.
        
        Args:
            name: Account name to enable
            
        Returns:
            CommandResult with operation status
        """
        return self.edit_account(name, enabled=True)
    
    def disable_account(self, name: str) -> CommandResult:
        """
        Disable an account.
        
        Args:
            name: Account name to disable
            
        Returns:
            CommandResult with operation status
        """
        return self.edit_account(name, enabled=False)
    
    def get_account_statistics(self) -> Dict[str, Any]:
        """
        Get account statistics.
        
        Returns:
            Dictionary with account statistics
        """
        try:
            accounts = self.get_all_accounts()
            
            stats = {
                'total_accounts': len(accounts),
                'crypto_accounts': len([a for a in accounts if a.type == 'crypto']),
                'forex_accounts': len([a for a in accounts if a.type == 'forex']),
                'enabled_accounts': len([a for a in accounts if a.enabled]),
                'disabled_accounts': len([a for a in accounts if not a.enabled]),
                'sandbox_accounts': len([a for a in accounts if a.sandbox]),
                'live_accounts': len([a for a in accounts if not a.sandbox]),
                'exchanges': {},
                'brokers': {}
            }
            
            # Count by exchange/broker
            for account in accounts:
                if account.type == 'crypto':
                    exchange = account.exchange_or_broker
                    if exchange not in stats['exchanges']:
                        stats['exchanges'][exchange] = 0
                    stats['exchanges'][exchange] += 1
                else:
                    broker = account.exchange_or_broker
                    if broker not in stats['brokers']:
                        stats['brokers'][broker] = 0
                    stats['brokers'][broker] += 1
            
            return stats
            
        except Exception:
            return {
                'total_accounts': 0,
                'error': 'Failed to load account statistics'
            }
    
    def export_accounts_config(self, output_file: Path) -> CommandResult:
        """
        Export accounts configuration to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            CommandResult with operation status
        """
        try:
            accounts_config = self.config_manager.load_accounts_config()
            
            # Create sanitized version (remove sensitive data)
            sanitized_config = {}
            
            for section_name, section_data in accounts_config.items():
                sanitized_config[section_name] = {}
                for account_name, account_config in section_data.items():
                    sanitized_account = dict(account_config)
                    
                    # Remove or mask sensitive fields
                    sensitive_fields = ['api_key', 'api_secret', 'password', 'api_passphrase']
                    for field in sensitive_fields:
                        if field in sanitized_account:
                            if sanitized_account[field].startswith('${'):
                                # Keep environment variable references
                                pass
                            else:
                                # Mask actual values
                                sanitized_account[field] = '[REDACTED]'
                    
                    sanitized_config[section_name][account_name] = sanitized_account
            
            # Write to file
            self.file_manager.safe_write_yaml(output_file, sanitized_config)
            
            return CommandResult.success(
                f"Accounts configuration exported to {output_file}",
                data={'output_file': str(output_file)},
                suggestions=[
                    "Review exported file before sharing",
                    "Sensitive data has been redacted for security"
                ]
            )
            
        except Exception as e:
            return CommandResult.error(
                f"Failed to export accounts configuration: {str(e)}",
                suggestions=[
                    "Check output directory permissions",
                    "Verify output file path"
                ]
            )