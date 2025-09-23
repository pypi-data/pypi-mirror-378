"""
CLI Validation Utilities
========================

Input validation and configuration validation for CLI operations.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urlparse

from .error_handler import ValidationError


class CLIValidator:
    """Comprehensive validation utilities for CLI operations"""
    
    # Common validation patterns
    PATTERNS = {
        'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        'api_key': re.compile(r'^[a-zA-Z0-9_-]{16,}$'),
        'account_name': re.compile(r'^[a-zA-Z0-9_-]{3,50}$'),
        'exchange_name': re.compile(r'^[a-zA-Z0-9_-]{2,20}$'),
        'symbol': re.compile(r'^[A-Z]{3,10}[/_-]?[A-Z]{3,10}$'),
        'percentage': re.compile(r'^\d+(\.\d+)?%?$'),
        'positive_number': re.compile(r'^\d+(\.\d+)?$'),
        'port': re.compile(r'^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$')
    }
    
    # Supported exchanges and brokers
    SUPPORTED_EXCHANGES = {
        'crypto': ['binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okx', 'bybit', 'kucoin'],
        'forex': ['oanda', 'ib', 'mt5', 'fxcm', 'pepperstone']
    }
    
    def __init__(self):
        self.errors = []
    
    def reset_errors(self) -> None:
        """Reset validation errors"""
        self.errors = []
    
    def add_error(self, error: str) -> None:
        """Add validation error"""
        self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """Get all validation errors"""
        return self.errors.copy()
    
    def validate_required_field(self, value: Any, field_name: str) -> bool:
        """Validate required field is present and not empty"""
        if value is None or (isinstance(value, str) and not value.strip()):
            self.add_error(f"Required field '{field_name}' is missing or empty")
            return False
        return True
    
    def validate_pattern(self, value: str, pattern_name: str, field_name: str) -> bool:
        """Validate value against a pattern"""
        if pattern_name not in self.PATTERNS:
            self.add_error(f"Unknown validation pattern: {pattern_name}")
            return False
        
        pattern = self.PATTERNS[pattern_name]
        if not pattern.match(value):
            self.add_error(f"Invalid format for '{field_name}': {value}")
            return False
        return True
    
    def validate_email(self, email: str, field_name: str = "email") -> bool:
        """Validate email address"""
        return self.validate_pattern(email, 'email', field_name)
    
    def validate_api_key(self, api_key: str, field_name: str = "API key") -> bool:
        """Validate API key format"""
        if not api_key or len(api_key) < 16:
            self.add_error(f"Invalid {field_name}: must be at least 16 characters")
            return False
        return True
    
    def validate_account_name(self, name: str) -> bool:
        """Validate account name"""
        return self.validate_pattern(name, 'account_name', 'account name')
    
    def validate_exchange_name(self, exchange: str, account_type: str = 'crypto') -> bool:
        """Validate exchange/broker name"""
        if account_type not in self.SUPPORTED_EXCHANGES:
            self.add_error(f"Unsupported account type: {account_type}")
            return False
        
        supported = self.SUPPORTED_EXCHANGES[account_type]
        if exchange.lower() not in supported:
            self.add_error(f"Unsupported {account_type} exchange: {exchange}")
            self.add_error(f"Supported exchanges: {', '.join(supported)}")
            return False
        return True
    
    def validate_percentage(self, value: Union[str, float], field_name: str, 
                          min_val: float = 0, max_val: float = 100) -> bool:
        """Validate percentage value"""
        try:
            # Convert string percentage to float
            if isinstance(value, str):
                if value.endswith('%'):
                    value = float(value[:-1])
                else:
                    value = float(value)
            
            if not min_val <= value <= max_val:
                self.add_error(f"{field_name} must be between {min_val}% and {max_val}%")
                return False
            return True
        except (ValueError, TypeError):
            self.add_error(f"Invalid percentage format for {field_name}: {value}")
            return False
    
    def validate_positive_number(self, value: Union[str, float], field_name: str) -> bool:
        """Validate positive number"""
        try:
            num_value = float(value)
            if num_value <= 0:
                self.add_error(f"{field_name} must be a positive number")
                return False
            return True
        except (ValueError, TypeError):
            self.add_error(f"Invalid number format for {field_name}: {value}")
            return False
    
    def validate_port(self, port: Union[str, int], field_name: str = "port") -> bool:
        """Validate port number"""
        try:
            port_num = int(port)
            if not 1 <= port_num <= 65535:
                self.add_error(f"{field_name} must be between 1 and 65535")
                return False
            return True
        except (ValueError, TypeError):
            self.add_error(f"Invalid port number: {port}")
            return False
    
    def validate_url(self, url: str, field_name: str = "URL") -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                self.add_error(f"Invalid {field_name} format: {url}")
                return False
            return True
        except Exception:
            self.add_error(f"Invalid {field_name} format: {url}")
            return False
    
    def validate_file_path(self, path: Union[str, Path], field_name: str, 
                          must_exist: bool = False, must_be_writable: bool = False) -> bool:
        """Validate file path"""
        try:
            path_obj = Path(path)
            
            if must_exist and not path_obj.exists():
                self.add_error(f"{field_name} does not exist: {path}")
                return False
            
            if must_be_writable:
                # Check if parent directory is writable
                parent = path_obj.parent
                if not parent.exists():
                    self.add_error(f"Parent directory does not exist for {field_name}: {parent}")
                    return False
                if not parent.is_dir():
                    self.add_error(f"Parent path is not a directory for {field_name}: {parent}")
                    return False
            
            return True
        except Exception as e:
            self.add_error(f"Invalid path for {field_name}: {str(e)}")
            return False
    
    def validate_choice(self, value: str, choices: List[str], field_name: str) -> bool:
        """Validate value is in allowed choices"""
        if value not in choices:
            self.add_error(f"Invalid {field_name}: '{value}'. Must be one of: {', '.join(choices)}")
            return False
        return True
    
    def validate_account_config(self, config: Dict[str, Any], account_type: str) -> bool:
        """Validate account configuration"""
        valid = True
        
        # Common validations
        if not self.validate_required_field(config.get('name'), 'name'):
            valid = False
        
        if not self.validate_required_field(config.get('enabled'), 'enabled'):
            valid = False
        elif not isinstance(config['enabled'], bool):
            self.add_error("Field 'enabled' must be a boolean")
            valid = False
        
        # Type-specific validations
        if account_type == 'crypto':
            valid &= self._validate_crypto_config(config)
        elif account_type == 'forex':
            valid &= self._validate_forex_config(config)
        else:
            self.add_error(f"Unknown account type: {account_type}")
            valid = False
        
        return valid
    
    def _validate_crypto_config(self, config: Dict[str, Any]) -> bool:
        """Validate crypto account configuration"""
        valid = True
        
        exchange = config.get('exchange_type')
        if not self.validate_required_field(exchange, 'exchange_type'):
            valid = False
        elif not self.validate_exchange_name(exchange, 'crypto'):
            valid = False
        
        if not self.validate_required_field(config.get('api_key'), 'api_key'):
            valid = False
        
        if not self.validate_required_field(config.get('api_secret'), 'api_secret'):
            valid = False
        
        # Validate sandbox setting
        sandbox = config.get('sandbox')
        if sandbox is not None and not isinstance(sandbox, bool):
            self.add_error("Field 'sandbox' must be a boolean")
            valid = False
        
        return valid
    
    def _validate_forex_config(self, config: Dict[str, Any]) -> bool:
        """Validate forex account configuration"""
        valid = True
        
        broker = config.get('broker_type')
        if not self.validate_required_field(broker, 'broker_type'):
            valid = False
        elif not self.validate_exchange_name(broker, 'forex'):
            valid = False
        
        # Broker-specific validations
        if broker == 'oanda':
            valid &= self._validate_oanda_config(config)
        elif broker == 'ib':
            valid &= self._validate_ib_config(config)
        elif broker == 'mt5':
            valid &= self._validate_mt5_config(config)
        
        return valid
    
    def _validate_oanda_config(self, config: Dict[str, Any]) -> bool:
        """Validate OANDA configuration"""
        valid = True
        
        if not self.validate_required_field(config.get('api_key'), 'api_key'):
            valid = False
        
        if not self.validate_required_field(config.get('account_id'), 'account_id'):
            valid = False
        
        return valid
    
    def _validate_ib_config(self, config: Dict[str, Any]) -> bool:
        """Validate Interactive Brokers configuration"""
        valid = True
        
        host = config.get('host', 'localhost')
        if not self.validate_required_field(host, 'host'):
            valid = False
        
        port = config.get('port')
        if not self.validate_required_field(port, 'port'):
            valid = False
        elif not self.validate_port(port):
            valid = False
        
        client_id = config.get('client_id')
        if client_id is not None:
            try:
                int(client_id)
            except (ValueError, TypeError):
                self.add_error("Field 'client_id' must be an integer")
                valid = False
        
        return valid
    
    def _validate_mt5_config(self, config: Dict[str, Any]) -> bool:
        """Validate MetaTrader 5 configuration"""
        valid = True
        
        if not self.validate_required_field(config.get('login'), 'login'):
            valid = False
        
        if not self.validate_required_field(config.get('password'), 'password'):
            valid = False
        
        if not self.validate_required_field(config.get('server'), 'server'):
            valid = False
        
        return valid
    
    def validate_and_raise(self, context: str = "") -> None:
        """Validate and raise exception if errors found"""
        if self.has_errors():
            message = f"Validation failed"
            if context:
                message = f"{context}: {message}"
            
            raise ValidationError(
                message,
                suggestions=self.get_errors()
            )