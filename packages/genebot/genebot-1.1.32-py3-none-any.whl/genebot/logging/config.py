"""
Unified logging configuration system.

This module provides centralized configuration management for the logging system,
supporting environment variables, YAML/JSON configuration files, and validation.
"""

import os
import json
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, Union
from enum import Enum


class LogLevel(Enum):
    """Supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Supported log formats."""
    STRUCTURED = "structured"
    SIMPLE = "simple"


class Environment(Enum):
    """Supported environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class LoggingConfig:
    """
    Unified logging configuration with environment awareness and validation.
    
    This configuration supports:
    - Environment variable overrides
    - YAML/JSON configuration files
    - Schema validation
    - Default values for all environments
    """
    
    # Core logging settings
    level: str = "INFO"
    format_type: str = "structured"
    console_output: bool = True
    file_output: bool = True
    
    # File handling
    log_directory: Path = field(default_factory=lambda: Path("logs"))
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    # Environment settings
    environment: str = "development"
    
    # Feature flags
    enable_performance_logging: bool = True
    enable_trade_logging: bool = True
    enable_cli_logging: bool = True
    enable_error_logging: bool = True
    enable_audit_logging: bool = True
    
    # External library control
    external_lib_level: str = "WARNING"
    
    # Performance settings
    enable_async_logging: bool = False
    log_buffer_size: int = 1000
    async_queue_size: int = 10000
    async_batch_size: int = 100
    async_flush_interval: float = 1.0
    
    # Rotation and file handling settings
    compress_rotated_files: bool = True
    max_log_age_days: int = 30
    min_free_space_mb: int = 100
    cleanup_on_startup: bool = True
    optimized_file_io: bool = True
    
    # Security settings
    mask_sensitive_data: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
        self._apply_environment_overrides()
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate log level
        if self.level not in [level.value for level in LogLevel]:
            raise ValueError(f"Invalid log level: {self.level}")
        
        # Validate format type
        if self.format_type not in [fmt.value for fmt in LogFormat]:
            raise ValueError(f"Invalid format type: {self.format_type}")
        
        # Validate environment
        if self.environment not in [env.value for env in Environment]:
            raise ValueError(f"Invalid environment: {self.environment}")
        
        # Validate file size
        if self.max_file_size <= 0:
            raise ValueError("max_file_size must be positive")
        
        # Validate backup count
        if self.backup_count < 0:
            raise ValueError("backup_count must be non-negative")
        
        # Convert log_directory to Path if it's a string
        if isinstance(self.log_directory, str):
            self.log_directory = Path(self.log_directory)
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides."""
        env_mappings = {
            'LOG_LEVEL': 'level',
            'LOG_FORMAT': 'format_type',
            'LOG_CONSOLE': 'console_output',
            'LOG_FILE': 'file_output',
            'LOG_DIRECTORY': 'log_directory',
            'LOG_MAX_SIZE': 'max_file_size',
            'LOG_BACKUP_COUNT': 'backup_count',
            'ENVIRONMENT': 'environment',
            'LOG_PERFORMANCE': 'enable_performance_logging',
            'LOG_TRADES': 'enable_trade_logging',
            'LOG_CLI': 'enable_cli_logging',
            'LOG_ERRORS': 'enable_error_logging',
            'LOG_EXTERNAL_LEVEL': 'external_lib_level',
            'LOG_ASYNC': 'enable_async_logging',
            'LOG_BUFFER_SIZE': 'log_buffer_size',
            'LOG_ASYNC_QUEUE_SIZE': 'async_queue_size',
            'LOG_ASYNC_BATCH_SIZE': 'async_batch_size',
            'LOG_ASYNC_FLUSH_INTERVAL': 'async_flush_interval',
            'LOG_COMPRESS_ROTATED': 'compress_rotated_files',
            'LOG_MAX_AGE_DAYS': 'max_log_age_days',
            'LOG_MIN_FREE_SPACE_MB': 'min_free_space_mb',
            'LOG_CLEANUP_STARTUP': 'cleanup_on_startup',
            'LOG_OPTIMIZED_IO': 'optimized_file_io',
            'LOG_MASK_SENSITIVE': 'mask_sensitive_data'
        }
        
        for env_var, attr_name in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert environment value to appropriate type
                current_value = getattr(self, attr_name)
                if isinstance(current_value, bool):
                    setattr(self, attr_name, env_value.lower() in ('true', '1', 'yes', 'on'))
                elif isinstance(current_value, int):
                    setattr(self, attr_name, int(env_value))
                elif isinstance(current_value, float):
                    setattr(self, attr_name, float(env_value))
                elif isinstance(current_value, Path):
                    setattr(self, attr_name, Path(env_value))
                else:
                    setattr(self, attr_name, env_value)
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'LoggingConfig':
        """
        Load configuration from YAML or JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            LoggingConfig instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            # Extract logging section if it exists
            if 'logging' in config_data:
                config_data = config_data['logging']
            
            return cls(**config_data)
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
    
    @classmethod
    def for_environment(cls, environment: str) -> 'LoggingConfig':
        """
        Create configuration optimized for specific environment.
        
        Args:
            environment: Target environment (development, testing, production)
            
        Returns:
            LoggingConfig instance with environment-specific defaults
        """
        if environment == Environment.DEVELOPMENT.value:
            return cls(
                level="DEBUG",
                format_type="simple",
                console_output=True,
                file_output=True,
                enable_performance_logging=True,
                enable_async_logging=False
            )
        elif environment == Environment.TESTING.value:
            return cls(
                level="WARNING",
                format_type="simple",
                console_output=False,
                file_output=False,
                enable_performance_logging=False,
                enable_async_logging=False
            )
        elif environment == Environment.PRODUCTION.value:
            return cls(
                level="INFO",
                format_type="structured",
                console_output=False,
                file_output=True,
                enable_performance_logging=True,
                enable_async_logging=True,
                max_file_size=50 * 1024 * 1024,  # 50MB for production
                backup_count=10
            )
        else:
            raise ValueError(f"Unknown environment: {environment}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result
    
    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """
        Save configuration to YAML or JSON file.
        
        Args:
            config_path: Path where to save configuration
        """
        config_path = Path(config_path)
        config_data = {'logging': self.to_dict()}
        
        with open(config_path, 'w') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            elif config_path.suffix.lower() == '.json':
                json.dump(config_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")


def get_default_config() -> LoggingConfig:
    """Get default logging configuration based on current environment."""
    environment = os.getenv('ENVIRONMENT', 'development')
    return LoggingConfig.for_environment(environment)


def load_config_with_fallback(config_paths: list[Union[str, Path]]) -> LoggingConfig:
    """
    Load configuration from multiple possible paths with fallback.
    
    Args:
        config_paths: List of configuration file paths to try
        
    Returns:
        LoggingConfig instance from first found file or default config
    """
    for config_path in config_paths:
        try:
            return LoggingConfig.from_file(config_path)
        except FileNotFoundError:
            continue
    
    # If no config file found, return default
    return get_default_config()