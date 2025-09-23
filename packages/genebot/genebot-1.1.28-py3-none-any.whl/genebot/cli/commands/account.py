"""
Account Management Commands
==========================

Commands for managing trading accounts (crypto exchanges and forex brokers).
"""

from argparse import Namespace
from typing import List, Dict, Any

from ..result import CommandResult
from .base import BaseCommand
from ..utils.account_manager import AccountManager
from ..utils.integration_manager import IntegrationManager


class ListAccountsCommand(BaseCommand):
    """List all configured accounts"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute list accounts command"""
        self.logger.section("Configured Trading Accounts")
        
        account_type_filter = getattr(args, 'type', 'all')
        status_filter = getattr(args, 'status', 'all')
        
        self.logger.info(f"Filtering by type: {account_type_filter}, status: {status_filter}")
        
        try:
            # Initialize account manager
            account_manager = AccountManager()
            all_accounts = account_manager.get_all_accounts()
            
            if not all_accounts:
                return CommandResult.warning(
                    "No accounts configured",
                    suggestions=[
                        "Add accounts with 'genebot add-crypto <exchange>' or 'genebot add-forex <broker>'",
                        "Create config/accounts.yaml file",
                        "Run 'genebot init-config' to generate configuration templates"
                    ]
                )
            
            # Apply filters
            filtered_accounts = self._filter_accounts(all_accounts, account_type_filter, status_filter)
            
            if not filtered_accounts:
                return CommandResult.warning(
                    "No accounts found matching the specified criteria",
                    suggestions=[
                        "Check filter criteria (type, status)",
                        "Add accounts with 'genebot add-crypto <exchange>' or 'genebot add-forex <broker>'",
                        "Check account configuration in config/accounts.yaml"
                    ]
                )
            
            self._display_accounts(filtered_accounts)
            
            return CommandResult.success(
                f"Listed {len(filtered_accounts)} account(s) (Total configured: {len(all_accounts)})",
                data={'accounts': [acc.__dict__ for acc in filtered_accounts], 'total_accounts': len(all_accounts)}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load accounts: {e}")
            return CommandResult.error(
                f"Failed to load accounts: {str(e)}",
                suggestions=[
                    "Check config/accounts.yaml file format",
                    "Verify file permissions",
                    "Check log files for detailed error information"
                ]
            )
    
    def _filter_accounts(self, accounts: List, type_filter: str, status_filter: str) -> List:
        """Filter accounts by type and status"""
        filtered = accounts
        
        if type_filter != 'all':
            filtered = [acc for acc in filtered if acc.type == type_filter]
        
        if status_filter != 'all':
            # Map status filter to enabled status
            if status_filter == 'enabled':
                filtered = [acc for acc in filtered if acc.enabled]
            elif status_filter == 'disabled':
                filtered = [acc for acc in filtered if not acc.enabled]
            elif status_filter == 'active':
                # For backward compatibility, treat 'active' as 'enabled'
                filtered = [acc for acc in filtered if acc.enabled]
        
        return filtered
    
    def _display_accounts(self, accounts: List) -> None:
        """Display accounts in a formatted table"""
        if not accounts:
            return
        
        self.logger.table_header(['Name', 'Type', 'Exchange/Broker', 'Mode', 'Enabled'])
        
        for account in accounts:
            # Determine mode (sandbox/live)
            mode = "Sandbox" if account.sandbox else "Live"
            mode_icon = "🧪" if account.sandbox else "💰"
            
            enabled_icon = "✅" if account.enabled else "❌"
            
            self.logger.table_row([
                account.name,
                account.type.upper(),
                account.exchange_or_broker,
                f"{mode_icon} {mode}",
                enabled_icon
            ])


class ListExchangesCommand(BaseCommand):
    """List available crypto exchanges"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute list exchanges command"""
        self.logger.section("Available Crypto Exchanges")
        
        # Load from account manager
        account_manager = AccountManager()
        exchanges = account_manager.supported_crypto_exchanges
        
        for exchange in exchanges:
            self.logger.list_item(exchange, "info")
        
        return CommandResult.success(
            f"Listed {len(exchanges)} available exchanges",
            data={'exchanges': exchanges}
        )


class ListBrokersCommand(BaseCommand):
    """List available forex brokers"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute list brokers command"""
        self.logger.section("Available Forex Brokers")
        
        # Load from account manager
        account_manager = AccountManager()
        brokers = account_manager.supported_forex_brokers
        
        for broker in brokers:
            self.logger.list_item(broker, "info")
        
        return CommandResult.success(
            f"Listed {len(brokers)} available brokers",
            data={'brokers': brokers}
        )


class AddCryptoCommand(BaseCommand):
    """Add crypto exchange account"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute add crypto account command"""
        exchange = args.exchange
        mode = getattr(args, 'mode', 'demo')
        name = getattr(args, 'name', None)
        api_key = getattr(args, 'api_key', None)
        api_secret = getattr(args, 'api_secret', None)
        
        self.logger.section(f"Adding Crypto Account")
        
        # Initialize account manager
        account_manager = AccountManager()
        
        # Collect additional parameters
        kwargs = {}
        for attr in ['enabled', 'rate_limit', 'timeout', 'api_passphrase']:
            value = getattr(args, attr, None)
            if value is not None:
                kwargs[attr] = value
        
        # Add the account
        result = account_manager.add_crypto_account(
            exchange_type=exchange,
            name=name,
            mode=mode,
            api_key=api_key,
            api_secret=api_secret,
            **kwargs
        )
        
        if result.success:
            self.logger.success(result.message)
            if result.data:
                self.logger.info(f"Exchange: {result.data['exchange_type']}")
                self.logger.info(f"Mode: {result.data['mode']}")
                self.logger.info(f"Sandbox: {result.data['sandbox']}")
        
        return result


class AddForexCommand(BaseCommand):
    """Add forex broker account"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute add forex account command"""
        broker = args.broker
        mode = getattr(args, 'mode', 'demo')
        name = getattr(args, 'name', None)
        api_key = getattr(args, 'api_key', None)
        account_id = getattr(args, 'account_id', None)
        
        self.logger.section(f"Adding Forex Account")
        
        # Initialize account manager
        account_manager = AccountManager()
        
        # Collect additional parameters
        kwargs = {}
        for attr in ['enabled', 'timeout', 'max_retries', 'host', 'port', 'client_id', 'login', 'password', 'server', 'path']:
            value = getattr(args, attr, None)
            if value is not None:
                kwargs[attr] = value
        
        # Add the account
        result = account_manager.add_forex_account(
            broker_type=broker,
            name=name,
            mode=mode,
            api_key=api_key,
            account_id=account_id,
            **kwargs
        )
        
        if result.success:
            self.logger.success(result.message)
            if result.data:
                self.logger.info(f"Broker: {result.data['broker_type']}")
                self.logger.info(f"Mode: {result.data['mode']}")
                self.logger.info(f"Sandbox: {result.data['sandbox']}")
        
        return result


class EditCryptoCommand(BaseCommand):
    """Edit crypto exchange account"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute edit crypto account command"""
        name = args.name
        interactive = getattr(args, 'interactive', False)
        
        self.logger.section(f"Editing Crypto Account: {name}")
        
        # Initialize account manager
        account_manager = AccountManager()
        
        # Collect update parameters
        updates = {}
        for attr in ['enabled', 'sandbox', 'rate_limit', 'timeout', 'api_key', 'api_secret', 'api_passphrase']:
            value = getattr(args, attr, None)
            if value is not None:
                updates[attr] = value
        
        # Edit the account
        result = account_manager.edit_account(name, interactive=interactive, **updates)
        
        if result.success:
            self.logger.success(result.message)
        
        return result


class EditForexCommand(BaseCommand):
    """Edit forex broker account"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute edit forex account command"""
        name = args.name
        interactive = getattr(args, 'interactive', False)
        
        self.logger.section(f"Editing Forex Account: {name}")
        
        # Initialize account manager
        account_manager = AccountManager()
        
        # Collect update parameters
        updates = {}
        for attr in ['enabled', 'sandbox', 'timeout', 'max_retries', 'host', 'port', 'client_id', 'api_key', 'account_id', 'login', 'password', 'server', 'path']:
            value = getattr(args, attr, None)
            if value is not None:
                updates[attr] = value
        
        # Edit the account
        result = account_manager.edit_account(name, interactive=interactive, **updates)
        
        if result.success:
            self.logger.success(result.message)
        
        return result


class RemoveAccountCommand(BaseCommand):
    """Remove an account"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute remove account command"""
        name = args.name
        confirm = getattr(args, 'confirm', False)
        
        self.logger.section(f"Removing Account: {name}")
        
        # Initialize account manager
        account_manager = AccountManager()
        
        # Remove the account
        result = account_manager.remove_account(name, confirm=confirm)
        
        if result.success:
            self.logger.success(result.message)
        
        return result


class EnableAccountCommand(BaseCommand):
    """Enable an account"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute enable account command"""
        name = args.name
        
        self.logger.section(f"Enabling Account: {name}")
        
        # Initialize account manager
        account_manager = AccountManager()
        
        # Enable the account
        result = account_manager.enable_account(name)
        
        if result.success:
            self.logger.success(result.message)
        
        return result


class DisableAccountCommand(BaseCommand):
    """Disable an account"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute disable account command"""
        name = args.name
        
        self.logger.section(f"Disabling Account: {name}")
        
        # Initialize account manager
        account_manager = AccountManager()
        
        # Disable the account
        result = account_manager.disable_account(name)
        
        if result.success:
            self.logger.success(result.message)
        
        return result


class ValidateAccountsCommand(BaseCommand):
    """Validate all accounts"""
    
    def execute(self, args: Namespace) -> CommandResult:
        """Execute validate accounts command"""
        import asyncio
        from ..utils.account_validator import RealAccountValidator
        
        account_filter = getattr(args, 'account', None)
        timeout = getattr(args, 'timeout', 30)
        account_type = getattr(args, 'type', None)
        enabled_only = getattr(args, 'enabled_only', False)
        
        self.logger.section("Account Validation")
        
        if account_filter:
            self.logger.info(f"Validating specific account: {account_filter}")
        else:
            self.logger.info("Validating all accounts")
        
        if account_type:
            self.logger.info(f"Filtering by type: {account_type}")
        
        if enabled_only:
            self.logger.info("Only validating enabled accounts")
        
        self.logger.info(f"Connection timeout: {timeout} seconds")
        
        try:
            # Initialize real account validator
            validator = RealAccountValidator()
            
            # Run validation asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                statuses = loop.run_until_complete(
                    validator.validate_all_accounts(
                        account_filter=account_filter,
                        account_type=account_type,
                        enabled_only=enabled_only,
                        timeout=timeout
                    )
                )
            finally:
                loop.close()
            
            if not statuses:
                return CommandResult.warning(
                    "No accounts found matching the specified criteria",
                    suggestions=[
                        "Check that accounts are configured in config/accounts.yaml",
                        "Verify account filters (type, enabled status)",
                        "Add accounts with 'genebot add-crypto' or 'genebot add-forex'"
                    ]
                )
            
            # Display validation results
            self._display_validation_results(statuses)
            
            # Save validation history for tracking
            try:
                validator.save_validation_history(statuses)
            except Exception as e:
                self.logger.warning(f"Failed to save validation history: {e}")
            
            # Generate summary
            summary = validator.get_validation_summary(statuses)
            
            # Determine result based on validation outcomes
            valid_accounts = summary['valid_accounts']
            invalid_accounts = summary['invalid_accounts']
            total_accounts = summary['total_accounts']
            
            if invalid_accounts > 0:
                failed_accounts = [s for s in statuses if not (s.connected and s.authenticated)]
                suggestions = [
                    "Check API credentials for failed accounts",
                    "Verify network connectivity",
                    "Check exchange/broker status"
                ]
                
                # Add specific suggestions based on error types
                auth_failures = [s for s in failed_accounts if s.connected and not s.authenticated]
                if auth_failures:
                    suggestions.append("Review API key permissions and account settings")
                
                connection_failures = [s for s in failed_accounts if not s.connected]
                if connection_failures:
                    suggestions.append("Check firewall settings and network connectivity")
                
                return CommandResult.warning(
                    f"Validation completed: {valid_accounts}/{total_accounts} accounts valid "
                    f"(Success rate: {summary['success_rate']}%)",
                    data={'summary': summary, 'statuses': statuses},
                    suggestions=suggestions
                )
            
            return CommandResult.success(
                f"All {valid_accounts} account(s) validated successfully "
                f"(Average latency: {summary['average_latency_ms']}ms)",
                data={'summary': summary, 'statuses': statuses}
            )
            
        except FileNotFoundError as e:
            return CommandResult.error(
                "Accounts configuration file not found",
                suggestions=[
                    "Create config/accounts.yaml file",
                    "Run 'genebot init-config' to generate configuration templates",
                    "Add accounts with 'genebot add-crypto' or 'genebot add-forex'"
                ]
            )
        except Exception as e:
            self.logger.error(f"Account validation failed: {e}")
            return CommandResult.error(
                f"Account validation failed: {str(e)}",
                suggestions=[
                    "Check configuration file format",
                    "Verify network connectivity",
                    "Check log files for detailed error information"
                ]
            )
    
    def _display_validation_results(self, statuses: List) -> None:
        """Display validation results in a formatted table"""
        if not statuses:
            return
        
        self.logger.table_header([
            'Account', 'Type', 'Exchange/Broker', 'Status', 'Connection', 'Auth', 'Latency', 'Error'
        ])
        
        for status in statuses:
            # Status indicators
            if status.connected and status.authenticated:
                status_icon = "🟢 Valid"
                status_color = "success"
            elif status.connected and not status.authenticated:
                status_icon = "🟡 Auth Failed"
                status_color = "warning"
            elif not status.connected:
                status_icon = "🔴 No Connection"
                status_color = "error"
            else:
                status_icon = "❓ Unknown"
                status_color = "info"
            
            connection_icon = "✅" if status.connected else "❌"
            auth_icon = "✅" if status.authenticated else "❌"
            
            latency_str = f"{status.latency_ms}ms" if status.latency_ms else "N/A"
            
            # Truncate error message for display
            error_display = ""
            if status.error_message:
                error_display = status.error_message[:50] + "..." if len(status.error_message) > 50 else status.error_message
            
            self.logger.table_row([
                status.name,
                status.type.upper(),
                status.exchange_or_broker,
                status_icon,
                connection_icon,
                auth_icon,
                latency_str,
                error_display
            ])
        
        # Display balance information for successful validations
        successful_accounts = [s for s in statuses if s.connected and s.authenticated and s.balance]
        if successful_accounts:
            self.logger.info("\nAccount Balances:")
            for status in successful_accounts:
                if status.balance:
                    balance_str = ", ".join([f"{curr}: {amount}" for curr, amount in status.balance.items()])
                    self.logger.list_item(f"{status.name}: {balance_str}", "info")