"""
Real Account Validator
=====================

Validates trading accounts by testing actual API connectivity with exchanges and brokers.
Replaces mock validation with real API connection tests.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import yaml
from pathlib import Path

from .integration_manager import IntegrationManager
from ..result import CommandResult

# Import existing exceptions through integration manager
try:
    from src.exceptions.base_exceptions import (
        ConnectionException, AuthenticationException, ExchangeException
    )
except ImportError:
    # Create minimal exception stubs
    class ConnectionException(Exception):
        pass
    
    class AuthenticationException(Exception):
        pass
    
    class ExchangeException(Exception):
        pass
except ImportError:
    # Fallback for testing or if modules are not available
    class ConnectionException(Exception):
        pass
    
    class AuthenticationException(Exception):
        pass
    
    class ExchangeException(Exception):
        pass


@dataclass
class AccountStatus:
    """Account status information from real API validation"""
    name: str
    type: str  # 'crypto' or 'forex'
    exchange_or_broker: str
    enabled: bool
    connected: bool
    authenticated: bool
    last_check: datetime
    error_message: Optional[str] = None
    balance: Optional[Dict[str, Decimal]] = None
    latency_ms: Optional[float] = None
    additional_info: Optional[Dict[str, Any]] = None


class RealAccountValidator:
    """
    Real account validator that uses existing exchange adapters to test API connectivity.
    
    This class replaces mock account validation with actual API connection tests
    for both crypto exchanges and forex brokers.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the real account validator.
        
        Args:
            config_path: Path to configuration directory (defaults to config/)
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or Path("config")
        self.accounts_file = self.config_path / "accounts.yaml"
        
        # Initialize integration manager for accessing existing components
        self.integration_manager = IntegrationManager(
            config_path=self.config_path,
            env_file=Path(".env")
        )
        
        # Cache for loaded accounts
        self._accounts_cache = None
        self._cache_timestamp = None
    
    def _load_accounts_config(self) -> Dict[str, Any]:
        """
        Load accounts configuration from YAML file.
        
        Returns:
            Dictionary containing crypto_exchanges and forex_brokers configurations
            
        Raises:
            FileNotFoundError: If accounts.yaml doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        try:
            if not self.accounts_file.exists():
                raise FileNotFoundError(f"Accounts configuration not found: {self.accounts_file}")
            
            # Check if we need to reload cache
            file_mtime = self.accounts_file.stat().st_mtime
            if (self._accounts_cache is None or 
                self._cache_timestamp is None or 
                file_mtime > self._cache_timestamp):
                
                with open(self.accounts_file, 'r') as f:
                    self._accounts_cache = yaml.safe_load(f) or {}
                self._cache_timestamp = file_mtime
                self.logger.debug(f"Loaded accounts configuration from {self.accounts_file}")
            
            return self._accounts_cache
            
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse accounts YAML: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load accounts configuration: {e}")
            raise
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """
        Get all configured accounts (both crypto and forex).
        
        Returns:
            List of account configurations with type information
        """
        try:
            config = self._load_accounts_config()
            accounts = []
            
            # Add crypto exchanges
            crypto_exchanges = config.get('crypto_exchanges', {})
            for name, account_config in crypto_exchanges.items():
                account_config = dict(account_config)  # Make a copy
                account_config['name'] = name
                account_config['type'] = 'crypto'
                accounts.append(account_config)
            
            # Add forex brokers
            forex_brokers = config.get('forex_brokers', {})
            for name, account_config in forex_brokers.items():
                account_config = dict(account_config)  # Make a copy
                account_config['name'] = name
                account_config['type'] = 'forex'
                accounts.append(account_config)
            
            return accounts
            
        except Exception as e:
            self.logger.error(f"Failed to get all accounts: {e}")
            return []
    
    def get_account_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific account configuration by name.
        
        Args:
            name: Account name to search for
            
        Returns:
            Account configuration dictionary or None if not found
        """
        accounts = self.get_all_accounts()
        for account in accounts:
            if account.get('name') == name:
                return account
        return None
    
    def filter_accounts(self, accounts: List[Dict[str, Any]], 
                       account_type: Optional[str] = None,
                       enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        Filter accounts by type and enabled status.
        
        Args:
            accounts: List of account configurations
            account_type: Filter by type ('crypto' or 'forex'), None for all
            enabled_only: If True, only return enabled accounts
            
        Returns:
            Filtered list of accounts
        """
        filtered = accounts
        
        if account_type:
            filtered = [acc for acc in filtered if acc.get('type') == account_type]
        
        if enabled_only:
            filtered = [acc for acc in filtered if acc.get('enabled', False)]
        
        return filtered
    
    async def _create_crypto_adapter(self, account_config: Dict[str, Any]):
        """
        Create a crypto exchange adapter from account configuration using integration manager.
        
        Args:
            account_config: Account configuration dictionary
            
        Returns:
            Initialized exchange adapter
            
        Raises:
            ValueError: If exchange type is not supported
            ImportError: If required modules are not available
        """
        exchange_name = account_config.get('name')
        if not exchange_name:
            raise ValueError("Missing account name in configuration")
        
        # Use integration manager to get exchange adapter
        return self.integration_manager.get_exchange_adapter(exchange_name)
    
    async def _create_forex_adapter(self, account_config: Dict[str, Any]):
        """
        Create a forex broker adapter from account configuration using integration manager.
        
        Args:
            account_config: Account configuration dictionary
            
        Returns:
            Initialized broker adapter
            
        Raises:
            ValueError: If broker type is not supported
            ImportError: If required modules are not available
        """
        broker_name = account_config.get('name')
        if not broker_name:
            raise ValueError("Missing account name in configuration")
        
        # Use integration manager to get broker adapter
        return self.integration_manager.get_exchange_adapter(broker_name)
    
    async def validate_single_account(self, account_config: Dict[str, Any], 
                                    timeout: int = 30) -> AccountStatus:
        """
        Validate a single account by testing API connectivity.
        
        Args:
            account_config: Account configuration dictionary
            timeout: Connection timeout in seconds
            
        Returns:
            AccountStatus with validation results
        """
        account_name = account_config.get('name', 'unknown')
        account_type = account_config.get('type', 'unknown')
        
        start_time = datetime.now()
        
        try:
            # Create appropriate adapter based on account type
            if account_type == 'crypto':
                adapter = await self._create_crypto_adapter(account_config)
                exchange_or_broker = account_config.get('exchange_type', 'unknown')
            elif account_type == 'forex':
                adapter = await self._create_forex_adapter(account_config)
                exchange_or_broker = account_config.get('broker_type', 'unknown')
            else:
                return AccountStatus(
                    name=account_name,
                    type=account_type,
                    exchange_or_broker='unknown',
                    enabled=account_config.get('enabled', False),
                    connected=False,
                    authenticated=False,
                    last_check=datetime.now(timezone.utc),
                    error_message=f"Unknown account type: {account_type}"
                )
            
            # Test connection
            connected = False
            authenticated = False
            balance = None
            error_message = None
            additional_info = None
            
            try:
                # Test basic connection
                connected = await asyncio.wait_for(adapter.connect(), timeout=timeout)
                
                if connected:
                    # Test authentication
                    authenticated = await asyncio.wait_for(adapter.authenticate(), timeout=timeout)
                    
                    if authenticated:
                        # Get additional account information
                        try:
                            balance = await asyncio.wait_for(adapter.get_balance(), timeout=timeout)
                        except Exception as e:
                            self.logger.warning(f"Failed to get balance for {account_name}: {e}")
                        
                        try:
                            health_info = await asyncio.wait_for(adapter.health_check(), timeout=timeout)
                            additional_info = health_info
                        except Exception as e:
                            self.logger.warning(f"Failed to get health info for {account_name}: {e}")
                
            except asyncio.TimeoutError:
                error_message = f"Connection timeout after {timeout} seconds - check network connectivity"
            except ConnectionException as e:
                error_message = f"Connection failed: {str(e)} - verify network settings and exchange status"
            except AuthenticationException as e:
                error_message = f"Authentication failed: {str(e)} - check API credentials and permissions"
                connected = True  # Connection worked, but auth failed
            except ImportError as e:
                error_message = f"Missing dependencies: {str(e)} - install required packages"
            except ValueError as e:
                error_message = f"Configuration error: {str(e)} - check account configuration"
            except Exception as e:
                # Categorize common error types
                error_str = str(e).lower()
                if 'network' in error_str or 'connection' in error_str:
                    error_message = f"Network error: {str(e)} - check internet connection and firewall"
                elif 'api' in error_str or 'key' in error_str or 'auth' in error_str:
                    error_message = f"API error: {str(e)} - verify API credentials and permissions"
                elif 'timeout' in error_str:
                    error_message = f"Request timeout: {str(e)} - try increasing timeout or check server status"
                elif 'rate' in error_str or 'limit' in error_str:
                    error_message = f"Rate limit error: {str(e)} - reduce request frequency"
                else:
                    error_message = f"Validation failed: {str(e)}"
            
            finally:
                # Always disconnect
                try:
                    await adapter.disconnect()
                except Exception as e:
                    self.logger.warning(f"Error disconnecting from {account_name}: {e}")
            
            # Calculate latency
            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            return AccountStatus(
                name=account_name,
                type=account_type,
                exchange_or_broker=exchange_or_broker,
                enabled=account_config.get('enabled', False),
                connected=connected,
                authenticated=authenticated,
                last_check=datetime.now(timezone.utc),
                error_message=error_message,
                balance=balance,
                latency_ms=round(latency_ms, 2),
                additional_info=additional_info
            )
            
        except Exception as e:
            self.logger.error(f"Failed to validate account {account_name}: {e}")
            return AccountStatus(
                name=account_name,
                type=account_type,
                exchange_or_broker=account_config.get('exchange_type', 
                                                   account_config.get('broker_type', 'unknown')),
                enabled=account_config.get('enabled', False),
                connected=False,
                authenticated=False,
                last_check=datetime.now(timezone.utc),
                error_message=f"Validation error: {str(e)}"
            )
    
    async def validate_all_accounts(self, account_filter: Optional[str] = None,
                                  account_type: Optional[str] = None,
                                  enabled_only: bool = False,
                                  timeout: int = 30) -> List[AccountStatus]:
        """
        Validate all configured accounts or a filtered subset.
        
        Args:
            account_filter: Specific account name to validate (None for all)
            account_type: Filter by account type ('crypto' or 'forex')
            enabled_only: Only validate enabled accounts
            timeout: Connection timeout per account in seconds
            
        Returns:
            List of AccountStatus objects with validation results
        """
        try:
            # Get all accounts
            all_accounts = self.get_all_accounts()
            
            # Apply filters
            if account_filter:
                all_accounts = [acc for acc in all_accounts if acc.get('name') == account_filter]
            
            accounts_to_validate = self.filter_accounts(
                all_accounts, 
                account_type=account_type, 
                enabled_only=enabled_only
            )
            
            if not accounts_to_validate:
                self.logger.warning("No accounts found matching the specified criteria")
                return []
            
            self.logger.info(f"Validating {len(accounts_to_validate)} account(s)")
            
            # Validate accounts concurrently (but with some limit to avoid overwhelming APIs)
            semaphore = asyncio.Semaphore(3)  # Max 3 concurrent validations
            
            async def validate_with_semaphore(account_config):
                async with semaphore:
                    return await self.validate_single_account(account_config, timeout)
            
            # Run validations
            validation_tasks = [
                validate_with_semaphore(account_config) 
                for account_config in accounts_to_validate
            ]
            
            results = await asyncio.gather(*validation_tasks, return_exceptions=True)
            
            # Process results and handle any exceptions
            account_statuses = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    account_config = accounts_to_validate[i]
                    self.logger.error(f"Validation failed for {account_config.get('name')}: {result}")
                    
                    # Create error status
                    account_statuses.append(AccountStatus(
                        name=account_config.get('name', 'unknown'),
                        type=account_config.get('type', 'unknown'),
                        exchange_or_broker=account_config.get('exchange_type', 
                                                           account_config.get('broker_type', 'unknown')),
                        enabled=account_config.get('enabled', False),
                        connected=False,
                        authenticated=False,
                        last_check=datetime.now(timezone.utc),
                        error_message=f"Validation exception: {str(result)}"
                    ))
                else:
                    account_statuses.append(result)
            
            return account_statuses
            
        except Exception as e:
            self.logger.error(f"Failed to validate accounts: {e}")
            return []
    
    def save_validation_history(self, statuses: List[AccountStatus]) -> None:
        """
        Save validation results to history file for tracking.
        
        Args:
            statuses: List of AccountStatus objects to save
        """
        try:
            history_file = self.config_path / "validation_history.yaml"
            
            # Load existing history
            history = []
            if history_file.exists():
                try:
                    with open(history_file, 'r') as f:
                        history = yaml.safe_load(f) or []
                except Exception as e:
                    self.logger.warning(f"Failed to load validation history: {e}")
            
            # Add new validation entry
            validation_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'accounts': []
            }
            
            for status in statuses:
                account_entry = {
                    'name': status.name,
                    'type': status.type,
                    'exchange_or_broker': status.exchange_or_broker,
                    'enabled': status.enabled,
                    'connected': status.connected,
                    'authenticated': status.authenticated,
                    'last_check': status.last_check.isoformat(),
                    'error_message': status.error_message,
                    'latency_ms': status.latency_ms
                }
                validation_entry['accounts'].append(account_entry)
            
            history.append(validation_entry)
            
            # Keep only last 50 validation runs
            if len(history) > 50:
                history = history[-50:]
            
            # Save updated history
            with open(history_file, 'w') as f:
                yaml.dump(history, f, default_flow_style=False)
            
            self.logger.debug(f"Saved validation history to {history_file}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save validation history: {e}")
    
    def get_validation_history(self, account_name: Optional[str] = None, 
                             limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get validation history for tracking account status over time.
        
        Args:
            account_name: Filter by specific account name (None for all)
            limit: Maximum number of history entries to return
            
        Returns:
            List of validation history entries
        """
        try:
            history_file = self.config_path / "validation_history.yaml"
            
            if not history_file.exists():
                return []
            
            with open(history_file, 'r') as f:
                history = yaml.safe_load(f) or []
            
            # Filter by account name if specified
            if account_name:
                filtered_history = []
                for entry in history:
                    filtered_accounts = [
                        acc for acc in entry.get('accounts', [])
                        if acc.get('name') == account_name
                    ]
                    if filtered_accounts:
                        filtered_entry = dict(entry)
                        filtered_entry['accounts'] = filtered_accounts
                        filtered_history.append(filtered_entry)
                history = filtered_history
            
            # Return most recent entries up to limit
            return history[-limit:] if len(history) > limit else history
            
        except Exception as e:
            self.logger.warning(f"Failed to load validation history: {e}")
            return []
    
    def get_account_status_trend(self, account_name: str, 
                               days: int = 7) -> Dict[str, Any]:
        """
        Get status trend for a specific account over time.
        
        Args:
            account_name: Name of account to analyze
            days: Number of days to look back
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            history = self.get_validation_history(account_name=account_name, limit=100)
            
            if not history:
                return {'account': account_name, 'trend': 'no_data', 'entries': 0}
            
            # Filter by date range
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            recent_history = []
            
            for entry in history:
                try:
                    entry_date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    if entry_date >= cutoff_date:
                        recent_history.append(entry)
                except Exception:
                    continue
            
            if not recent_history:
                return {'account': account_name, 'trend': 'no_recent_data', 'entries': 0}
            
            # Analyze trend
            success_count = 0
            total_count = len(recent_history)
            
            for entry in recent_history:
                for account in entry.get('accounts', []):
                    if (account.get('name') == account_name and 
                        account.get('connected') and account.get('authenticated')):
                        success_count += 1
                        break
            
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            # Determine trend
            if success_rate >= 90:
                trend = 'excellent'
            elif success_rate >= 75:
                trend = 'good'
            elif success_rate >= 50:
                trend = 'fair'
            elif success_rate >= 25:
                trend = 'poor'
            else:
                trend = 'critical'
            
            return {
                'account': account_name,
                'trend': trend,
                'success_rate': round(success_rate, 1),
                'entries': total_count,
                'successful_validations': success_count,
                'period_days': days
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to analyze account trend: {e}")
            return {'account': account_name, 'trend': 'error', 'entries': 0}

    def get_validation_summary(self, statuses: List[AccountStatus]) -> Dict[str, Any]:
        """
        Generate a summary of validation results.
        
        Args:
            statuses: List of AccountStatus objects
            
        Returns:
            Dictionary containing validation summary statistics
        """
        if not statuses:
            return {
                'total_accounts': 0,
                'valid_accounts': 0,
                'invalid_accounts': 0,
                'enabled_accounts': 0,
                'disabled_accounts': 0,
                'crypto_accounts': 0,
                'forex_accounts': 0,
                'success_rate': 0.0,
                'average_latency_ms': 0.0
            }
        
        total = len(statuses)
        valid = sum(1 for s in statuses if s.connected and s.authenticated)
        invalid = total - valid
        enabled = sum(1 for s in statuses if s.enabled)
        disabled = total - enabled
        crypto = sum(1 for s in statuses if s.type == 'crypto')
        forex = sum(1 for s in statuses if s.type == 'forex')
        
        success_rate = (valid / total * 100) if total > 0 else 0.0
        
        # Calculate average latency for successful connections
        successful_latencies = [s.latency_ms for s in statuses 
                              if s.latency_ms is not None and s.connected]
        avg_latency = (sum(successful_latencies) / len(successful_latencies) 
                      if successful_latencies else 0.0)
        
        return {
            'total_accounts': total,
            'valid_accounts': valid,
            'invalid_accounts': invalid,
            'enabled_accounts': enabled,
            'disabled_accounts': disabled,
            'crypto_accounts': crypto,
            'forex_accounts': forex,
            'success_rate': round(success_rate, 1),
            'average_latency_ms': round(avg_latency, 2)
        }