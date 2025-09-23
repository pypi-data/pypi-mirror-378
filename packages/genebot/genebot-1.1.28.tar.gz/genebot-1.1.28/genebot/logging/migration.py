"""
Logging configuration migration utilities.

This module provides tools to migrate existing logging configurations to the
centralized logging system, including backup/restore functionality and validation.
"""

import os
import json
import yaml
import shutil
import logging
import logging.config
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict

from .config import LoggingConfig, get_default_config


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    success: bool
    message: str
    backup_path: Optional[Path] = None
    migrated_config: Optional[LoggingConfig] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class LegacyConfigDetector:
    """Detects and analyzes legacy logging configurations."""
    
    @staticmethod
    def find_legacy_configs(root_path: Path) -> List[Path]:
        """
        Find all legacy logging configuration files.
        
        Args:
            root_path: Root directory to search
            
        Returns:
            List of paths to legacy configuration files
        """
        legacy_patterns = [
            "**/logging.py",
            "**/logging_config.yaml",
            "**/logging_config.yml",
            "**/logging.yaml",
            "**/logging.yml",
            "**/log_config.py",
            "**/log_config.yaml",
            "**/log_config.yml"
        ]
        
        found_configs = []
        for pattern in legacy_patterns:
            found_configs.extend(root_path.glob(pattern))
        
        return found_configs
    
    @staticmethod
    def analyze_python_logging_config(file_path: Path) -> Dict[str, Any]:
        """
        Analyze Python logging configuration file.
        
        Args:
            file_path: Path to Python logging config file
            
        Returns:
            Dictionary with extracted configuration
        """
        config_info = {
            'type': 'python',
            'path': file_path,
            'handlers': [],
            'loggers': [],
            'formatters': [],
            'level': 'INFO',
            'issues': []
        }
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for common patterns
            if 'basicConfig' in content:
                config_info['issues'].append('Uses basicConfig - should be replaced')
            
            if 'StreamHandler' in content:
                config_info['handlers'].append('console')
            
            if 'FileHandler' in content or 'RotatingFileHandler' in content:
                config_info['handlers'].append('file')
            
            if 'JSONFormatter' in content or 'json.dumps' in content:
                config_info['formatters'].append('json')
            
            # Extract log level if possible
            for line in content.split('\n'):
                if 'level' in line.lower() and any(level in line.upper() for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']):
                    for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                        if level in line.upper():
                            config_info['level'] = level
                            break
            
        except Exception as e:
            config_info['issues'].append(f'Error reading file: {e}')
        
        return config_info
    
    @staticmethod
    def analyze_yaml_logging_config(file_path: Path) -> Dict[str, Any]:
        """
        Analyze YAML logging configuration file.
        
        Args:
            file_path: Path to YAML logging config file
            
        Returns:
            Dictionary with extracted configuration
        """
        config_info = {
            'type': 'yaml',
            'path': file_path,
            'handlers': [],
            'loggers': [],
            'formatters': [],
            'level': 'INFO',
            'issues': []
        }
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data:
                config_info['issues'].append('Empty or invalid YAML file')
                return config_info
            
            # Extract logging section
            logging_config = data.get('logging', data)
            
            # Extract level
            config_info['level'] = logging_config.get('level', 'INFO')
            
            # Extract handlers
            if 'handlers' in logging_config:
                config_info['handlers'] = list(logging_config['handlers'].keys())
            
            # Extract loggers
            if 'loggers' in logging_config:
                config_info['loggers'] = list(logging_config['loggers'].keys())
            
            # Extract formatters
            if 'formatters' in logging_config:
                config_info['formatters'] = list(logging_config['formatters'].keys())
            
        except Exception as e:
            config_info['issues'].append(f'Error reading YAML file: {e}')
        
        return config_info


class ConfigurationMigrator:
    """Migrates legacy logging configurations to centralized system."""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize migrator.
        
        Args:
            backup_dir: Directory for configuration backups
        """
        self.backup_dir = backup_dir or Path("config/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, config_path: Path) -> Path:
        """
        Create backup of existing configuration.
        
        Args:
            config_path: Path to configuration file to backup
            
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{config_path.name}.{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(config_path, backup_path)
        return backup_path
    
    def migrate_python_config(self, config_path: Path) -> MigrationResult:
        """
        Migrate Python logging configuration.
        
        Args:
            config_path: Path to Python config file
            
        Returns:
            MigrationResult with migration details
        """
        try:
            # Create backup
            backup_path = self.create_backup(config_path)
            
            # Analyze existing config
            config_info = LegacyConfigDetector.analyze_python_logging_config(config_path)
            
            # Create new centralized config
            new_config = get_default_config()
            new_config.level = config_info['level']
            
            # Map handlers
            if 'console' in config_info['handlers']:
                new_config.console_output = True
            if 'file' in config_info['handlers']:
                new_config.file_output = True
            
            # Set format based on detected formatters
            if 'json' in config_info['formatters']:
                new_config.format_type = "structured"
            else:
                new_config.format_type = "simple"
            
            warnings = []
            if config_info['issues']:
                warnings.extend(config_info['issues'])
            
            return MigrationResult(
                success=True,
                message=f"Successfully migrated Python config from {config_path}",
                backup_path=backup_path,
                migrated_config=new_config,
                warnings=warnings
            )
            
        except Exception as e:
            return MigrationResult(
                success=False,
                message=f"Failed to migrate Python config: {e}"
            )
    
    def migrate_yaml_config(self, config_path: Path) -> MigrationResult:
        """
        Migrate YAML logging configuration.
        
        Args:
            config_path: Path to YAML config file
            
        Returns:
            MigrationResult with migration details
        """
        try:
            # Create backup
            backup_path = self.create_backup(config_path)
            
            # Load existing YAML config
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            
            logging_config = data.get('logging', data)
            
            # Create new centralized config with mapped values
            config_kwargs = {}
            
            # Map common fields
            field_mappings = {
                'level': 'level',
                'format_type': 'format_type',
                'console_output': 'console_output',
                'file_output': 'file_output',
                'log_directory': 'log_directory',
                'max_file_size': 'max_file_size',
                'backup_count': 'backup_count',
                'environment': 'environment',
                'enable_performance_logging': 'enable_performance_logging',
                'enable_trade_logging': 'enable_trade_logging',
                'enable_cli_logging': 'enable_cli_logging',
                'enable_error_logging': 'enable_error_logging',
                'external_lib_level': 'external_lib_level',
                'enable_async_logging': 'enable_async_logging',
                'log_buffer_size': 'log_buffer_size'
            }
            
            for yaml_key, config_key in field_mappings.items():
                if yaml_key in logging_config:
                    config_kwargs[config_key] = logging_config[yaml_key]
            
            new_config = LoggingConfig(**config_kwargs)
            
            warnings = []
            
            # Check for unmapped fields
            mapped_keys = set(field_mappings.keys())
            existing_keys = set(logging_config.keys())
            unmapped_keys = existing_keys - mapped_keys
            
            if unmapped_keys:
                warnings.append(f"Unmapped configuration keys: {', '.join(unmapped_keys)}")
            
            return MigrationResult(
                success=True,
                message=f"Successfully migrated YAML config from {config_path}",
                backup_path=backup_path,
                migrated_config=new_config,
                warnings=warnings
            )
            
        except Exception as e:
            return MigrationResult(
                success=False,
                message=f"Failed to migrate YAML config: {e}"
            )
    
    def migrate_config_file(self, config_path: Path) -> MigrationResult:
        """
        Migrate any supported configuration file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            MigrationResult with migration details
        """
        if not config_path.exists():
            return MigrationResult(
                success=False,
                message=f"Configuration file not found: {config_path}"
            )
        
        if config_path.suffix == '.py':
            return self.migrate_python_config(config_path)
        elif config_path.suffix in ['.yaml', '.yml']:
            return self.migrate_yaml_config(config_path)
        else:
            return MigrationResult(
                success=False,
                message=f"Unsupported configuration file type: {config_path.suffix}"
            )
    
    def migrate_all_configs(self, root_path: Path) -> List[MigrationResult]:
        """
        Migrate all legacy configurations found in directory tree.
        
        Args:
            root_path: Root directory to search for configurations
            
        Returns:
            List of MigrationResult for each found configuration
        """
        legacy_configs = LegacyConfigDetector.find_legacy_configs(root_path)
        results = []
        
        for config_path in legacy_configs:
            result = self.migrate_config_file(config_path)
            results.append(result)
        
        return results


class ConfigurationValidator:
    """Validates migrated logging configurations."""
    
    @staticmethod
    def validate_config(config: LoggingConfig) -> Tuple[bool, List[str]]:
        """
        Validate logging configuration.
        
        Args:
            config: LoggingConfig to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            # Test configuration creation
            test_config = LoggingConfig(**asdict(config))
            
            # Check log directory accessibility
            if config.file_output:
                try:
                    config.log_directory.mkdir(parents=True, exist_ok=True)
                    test_file = config.log_directory / "test.log"
                    test_file.touch()
                    test_file.unlink()
                except Exception as e:
                    issues.append(f"Log directory not writable: {e}")
            
            # Check file size limits
            if config.max_file_size < 1024:  # Less than 1KB
                issues.append("Max file size is very small, may cause frequent rotation")
            
            # Check backup count
            if config.backup_count > 100:
                issues.append("Backup count is very high, may consume excessive disk space")
            
            # Check async settings
            if config.enable_async_logging and config.log_buffer_size < 100:
                issues.append("Async logging buffer size is very small, may impact performance")
            
        except Exception as e:
            issues.append(f"Configuration validation error: {e}")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def test_logging_functionality(config: LoggingConfig) -> Tuple[bool, List[str]]:
        """
        Test actual logging functionality with configuration.
        
        Args:
            config: LoggingConfig to test
            
        Returns:
            Tuple of (test_passed, list_of_issues)
        """
        issues = []
        
        try:
            # Import and setup logging with test config
            from .factory import setup_global_config, get_logger
            
            # Setup with test config
            setup_global_config(config)
            
            # Test basic logging
            test_logger = get_logger("migration_test")
            test_logger.info("Migration validation test message")
            
            # Test specialized loggers
            from .factory import get_trade_logger, get_performance_logger, get_error_logger
            
            trade_logger = get_trade_logger()
            trade_logger.info("Test trade log message")
            
            perf_logger = get_performance_logger()
            perf_logger.info("Test performance log message")
            
            error_logger = get_error_logger()
            error_logger.error("Test error log message")
            
        except Exception as e:
            issues.append(f"Logging functionality test failed: {e}")
        
        return len(issues) == 0, issues


class CompatibilityLayer:
    """Provides compatibility layer for gradual migration."""
    
    def __init__(self, enable_legacy_support: bool = True):
        """
        Initialize compatibility layer.
        
        Args:
            enable_legacy_support: Whether to enable legacy logging support
        """
        self.enable_legacy_support = enable_legacy_support
        self._legacy_loggers = {}
    
    def get_legacy_logger(self, name: str) -> logging.Logger:
        """
        Get logger with legacy interface.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance with legacy compatibility
        """
        if name in self._legacy_loggers:
            return self._legacy_loggers[name]
        
        if self.enable_legacy_support:
            # Create logger with legacy configuration
            logger = logging.getLogger(name)
            
            # Add compatibility wrapper if needed
            if not logger.handlers:
                # Setup basic handler for legacy support
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            
            self._legacy_loggers[name] = logger
            return logger
        else:
            # Use centralized system
            from .factory import get_logger
            return get_logger(name)
    
    def migrate_logger_calls(self, source_file: Path, backup: bool = True) -> MigrationResult:
        """
        Migrate logger calls in source file to use centralized system.
        
        Args:
            source_file: Path to source file to migrate
            backup: Whether to create backup before migration
            
        Returns:
            MigrationResult with migration details
        """
        try:
            if backup:
                backup_path = Path(f"{source_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copy2(source_file, backup_path)
            else:
                backup_path = None
            
            with open(source_file, 'r') as f:
                content = f.read()
            
            # Replace common legacy patterns
            replacements = [
                ('import logging', 'from genebot.logging.factory import get_logger'),
                ('logging.getLogger(', 'get_logger('),
                ('logging.basicConfig(', '# Replaced with centralized config: logging.basicConfig('),
                ('logger = logging.getLogger(__name__)', 'logger = get_logger(__name__)'),
            ]
            
            modified_content = content
            changes_made = []
            
            for old_pattern, new_pattern in replacements:
                if old_pattern in modified_content:
                    modified_content = modified_content.replace(old_pattern, new_pattern)
                    changes_made.append(f"Replaced '{old_pattern}' with '{new_pattern}'")
            
            if changes_made:
                with open(source_file, 'w') as f:
                    f.write(modified_content)
                
                return MigrationResult(
                    success=True,
                    message=f"Successfully migrated logger calls in {source_file}",
                    backup_path=backup_path,
                    warnings=changes_made
                )
            else:
                return MigrationResult(
                    success=True,
                    message=f"No logger calls to migrate in {source_file}",
                    backup_path=backup_path
                )
                
        except Exception as e:
            return MigrationResult(
                success=False,
                message=f"Failed to migrate logger calls: {e}"
            )


def create_migration_script(output_path: Path, root_path: Path) -> None:
    """
    Create a standalone migration script for the project.
    
    Args:
        output_path: Where to save the migration script
        root_path: Root path of the project to migrate
    """
    script_content = f'''#!/usr/bin/env python3
"""
Automated logging configuration migration script.

This script migrates legacy logging configurations to the centralized logging system.
Generated on {datetime.now().isoformat()}
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from genebot.logging.migration import ConfigurationMigrator, ConfigurationValidator

def main():
    """Run the migration process."""
    print("Starting logging configuration migration...")
    
    # Initialize migrator
    migrator = ConfigurationMigrator()
    
    # Migrate all configurations
    root_path = Path("{root_path}")
    results = migrator.migrate_all_configs(root_path)
    
    print(f"\\nMigration completed. Processed {{len(results)}} configurations:")
    
    for result in results:
        if result.success:
            print(f"✓ {{result.message}}")
            if result.backup_path:
                print(f"  Backup: {{result.backup_path}}")
            if result.warnings:
                for warning in result.warnings:
                    print(f"  Warning: {{warning}}")
            
            # Validate migrated configuration
            if result.migrated_config:
                is_valid, issues = ConfigurationValidator.validate_config(result.migrated_config)
                if not is_valid:
                    print(f"  Validation issues: {{', '.join(issues)}}")
        else:
            print(f"✗ {{result.message}}")
    
    print("\\nMigration process completed.")

if __name__ == "__main__":
    main()
'''
    
    with open(output_path, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    output_path.chmod(0o755)