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

# Import enhanced configuration system from project root
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from config.enhanced_manager import EnhancedConfigManager, get_enhanced_config_manager
    from config.unified_loader import (
        UnifiedConfigLoader, 
        ConfigurationSources, 
        ConfigurationStatus,
        ConfigurationNotFoundError,
        PartialConfigurationError,
        ConfigurationValidationError
    )
    ENHANCED_CONFIG_AVAILABLE = True
except ImportError as e:
    # Fallback if enhanced configuration system is not available
    ENHANCED_CONFIG_AVAILABLE = False
    EnhancedConfigManager = None
    get_enhanced_config_manager = None
    UnifiedConfigLoader = None
    ConfigurationSources = None
    ConfigurationStatus = None
    ConfigurationNotFoundError = Exception
    PartialConfigurationError = Exception
    ConfigurationValidationError = Exception
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
        
        # Initialize enhanced config manager with unified loading
        self._enhanced_config_manager: Optional[EnhancedConfigManager] = None
        self._core_config_manager: Optional[ConfigManager] = None  # Keep for backward compatibility
        
        # Configuration file paths
        self.accounts_file = self.config_path / 'accounts.yaml'
        self.bot_config_file = self.config_path / 'trading_bot_config.yaml'
        self.multi_market_config_file = self.config_path / 'multi_market_config.yaml'
        
        # Ensure config directory exists
        self.file_manager.ensure_directory(self.config_path)
    
    @property
    def enhanced_config_manager(self) -> EnhancedConfigManager:
        """Get or create enhanced configuration manager instance with unified loading"""
        if not ENHANCED_CONFIG_AVAILABLE:
            raise ConfigurationError(
                "Enhanced configuration system not available",
                suggestions=[
                    "Ensure the enhanced configuration system is properly installed",
                    "Check that config/enhanced_manager.py exists",
                    "Verify all required dependencies are installed"
                ]
            )
        
        if self._enhanced_config_manager is None:
            try:
                # Try to get existing enhanced config manager
                self._enhanced_config_manager = get_enhanced_config_manager(use_unified_loading=True)
            except Exception:
                # Fallback: create new enhanced config manager
                # Determine config file path using same discovery logic as unified loader
                config_file = None
                if self.bot_config_file.exists():
                    config_file = str(self.bot_config_file)
                elif self.multi_market_config_file.exists():
                    config_file = str(self.multi_market_config_file)
                
                self._enhanced_config_manager = EnhancedConfigManager(
                    config_file=config_file,
                    env_file=str(self.env_file) if self.env_file.exists() else None,
                    use_unified_loading=True
                )
        return self._enhanced_config_manager
    
    @property
    def core_config_manager(self) -> ConfigManager:
        """Get or create core configuration manager instance (legacy compatibility)"""
        if self._core_config_manager is None:
            try:
                # Try to get existing config manager
                self._core_config_manager = get_config_manager()
            except Exception:
                # Fallback: create new config manager
                # Determine config file path
                config_file = None
                if self.bot_config_file.exists():
                    config_file = str(self.bot_config_file)
                elif self.multi_market_config_file.exists():
                    config_file = str(self.multi_market_config_file)
                
                self._core_config_manager = ConfigManager(
                    config_file=config_file,
                    env_file=str(self.env_file) if self.env_file.exists() else None
                )
        return self._core_config_manager
    
    def validate_configuration(self) -> ConfigValidationResult:
        """
        Validate current configuration using unified validation system.
        
        This ensures CLI and runtime use identical configuration validation.
        
        Returns:
            ConfigValidationResult: Validation results with errors, warnings, and info
        """
        if not ENHANCED_CONFIG_AVAILABLE:
            # Fallback to legacy validation
            return self._validate_configuration_legacy()
        
        try:
            # Use enhanced config manager with unified validation
            enhanced_manager = self.enhanced_config_manager
            
            # Perform validation using same rules as runtime
            validation_result = enhanced_manager.validate_with_cli_rules()
            
            # Convert to CLI ConfigValidationResult format
            cli_result = ConfigValidationResult()
            
            # Add errors
            for error in validation_result.errors:
                cli_result.add_error(error)
            
            # Add warnings
            for warning in validation_result.warnings:
                cli_result.add_warning(warning)
            
            # Additional CLI-specific validations
            self._validate_cli_requirements(cli_result)
            
            # Add configuration discovery information
            try:
                sources = enhanced_manager.get_active_sources()
                if sources:
                    cli_result.add_info("Active configuration sources:")
                    for source in sources:
                        status = "✓" if source.exists and source.readable else "✗"
                        cli_result.add_info(f"  {status} {source.file_path} ({source.source_type})")
                else:
                    cli_result.add_warning("No active configuration sources found")
                    cli_result.add_info("Run 'genebot init-config' to create configuration files")
                
                # Check if CLI-generated configuration is being used
                if enhanced_manager.has_cli_generated_config():
                    cli_result.add_info("✓ Using CLI-generated configuration")
                else:
                    cli_result.add_warning("Not using CLI-generated configuration")
                    cli_result.add_info("Consider running 'genebot init-config --upgrade' for better integration")
                
            except Exception as discovery_error:
                cli_result.add_warning(f"Could not analyze configuration sources: {discovery_error}")
            
            return cli_result
            
        except ConfigurationNotFoundError as e:
            result = ConfigValidationResult()
            result.add_error("Configuration files not found")
            result.add_info("Run 'genebot init-config' to create configuration files")
            for guidance in e.guidance:
                result.add_info(guidance)
            return result
            
        except PartialConfigurationError as e:
            result = ConfigValidationResult()
            result.add_error(f"Partial configuration detected: {e}")
            result.add_info(f"Found files: {', '.join(e.found_files)}")
            result.add_info(f"Missing files: {', '.join(e.missing_files)}")
            for suggestion in e.completion_suggestions:
                result.add_info(f"• {suggestion}")
            return result
            
        except ConfigurationValidationError as e:
            result = ConfigValidationResult()
            result.add_error(f"Configuration validation failed: {e}")
            for error in e.validation_errors:
                result.add_error(error)
            for warning in e.validation_warnings:
                result.add_warning(warning)
            for suggestion in e.recovery_suggestions:
                result.add_info(f"• {suggestion}")
            return result
            
        except Exception as e:
            # Fallback to legacy validation
            result = ConfigValidationResult()
            result.add_warning(f"Enhanced validation failed, using legacy validation: {str(e)}")
            legacy_result = self._validate_configuration_legacy()
            
            # Merge results
            for error in legacy_result.errors:
                result.add_error(error)
            for warning in legacy_result.warnings:
                result.add_warning(warning)
            for info in legacy_result.info:
                result.add_info(info)
            
            return result
    
    def _validate_configuration_legacy(self) -> ConfigValidationResult:
        """Legacy configuration validation method."""
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
            result.add_info("Add accounts with 'genebot add-crypto' or 'genebot add-forex'")
    
    def load_configuration(self) -> TradingBotConfig:
        """
        Load and validate complete configuration using unified discovery system.
        
        This ensures CLI and runtime use identical configuration loading logic.
        
        Returns:
            TradingBotConfig: Validated configuration object
            
        Raises:
            ConfigurationError: If configuration cannot be loaded or is invalid
        """
        if not ENHANCED_CONFIG_AVAILABLE:
            # Fallback to legacy loading
            try:
                return self.core_config_manager.load_config()
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to load configuration (enhanced system not available): {str(e)}",
                    suggestions=[
                        "Check configuration file syntax and format",
                        "Validate environment variables",
                        "Run 'genebot validate' for detailed error information",
                        "Install enhanced configuration system for better integration"
                    ]
                )
        
        try:
            # Use enhanced config manager with unified loading
            enhanced_manager = self.enhanced_config_manager
            return enhanced_manager.load_with_discovery()
            
        except ConfigurationNotFoundError as e:
            raise ConfigurationError(
                f"Configuration files not found: {e}",
                suggestions=[
                    "Run 'genebot init-config' to create configuration files",
                    "Check if configuration files exist in expected locations",
                    "Verify file permissions and accessibility"
                ] + e.guidance
            )
            
        except PartialConfigurationError as e:
            suggestions = [
                f"Found files: {', '.join(e.found_files)}",
                f"Missing files: {', '.join(e.missing_files)}",
                ""
            ] + e.completion_suggestions
            
            raise ConfigurationError(
                f"Incomplete configuration setup: {e}",
                suggestions=suggestions
            )
            
        except ConfigurationValidationError as e:
            suggestions = [
                "Configuration validation errors found:",
                ""
            ]
            suggestions.extend([f"  ✗ {error}" for error in e.validation_errors])
            
            if e.validation_warnings:
                suggestions.extend([
                    "",
                    "Warnings:"
                ])
                suggestions.extend([f"  ⚠ {warning}" for warning in e.validation_warnings])
            
            if e.recovery_suggestions:
                suggestions.extend([
                    "",
                    "Recovery suggestions:"
                ])
                suggestions.extend([f"  • {suggestion}" for suggestion in e.recovery_suggestions])
            
            raise ConfigurationError(
                f"Configuration validation failed: {e}",
                suggestions=suggestions
            )
            
        except Exception as e:
            # Fallback to legacy loading for backward compatibility
            try:
                return self.core_config_manager.load_config()
            except Exception as legacy_error:
                raise ConfigurationError(
                    f"Failed to load configuration with both unified and legacy systems: {str(e)} | Legacy error: {str(legacy_error)}",
                    suggestions=[
                        "Check configuration file syntax and format",
                        "Validate environment variables",
                        "Run 'genebot validate --verbose' for detailed error information",
                        "Try 'genebot init-config --overwrite' to recreate configuration",
                        "Check file permissions and disk space"
                    ]
                )
    
    def reload_configuration(self) -> TradingBotConfig:
        """
        Reload configuration from files using unified discovery system.
        
        Returns:
            TradingBotConfig: Reloaded configuration
        """
        # Force recreation of both managers
        self._enhanced_config_manager = None
        self._core_config_manager = None
        
        # Use enhanced config manager for reloading
        enhanced_manager = self.enhanced_config_manager
        return enhanced_manager.reload_with_discovery()
    
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
    
    def get_configuration_sources(self):
        """
        Get discovered configuration sources using unified discovery system.
        
        Returns:
            ConfigurationSources: Discovered configuration sources (or dict for fallback)
        """
        if not ENHANCED_CONFIG_AVAILABLE:
            # Return a simple dict structure for fallback
            return {
                'bot_config_file': self.bot_config_file if self.bot_config_file.exists() else None,
                'accounts_config_file': self.accounts_file if self.accounts_file.exists() else None,
                'env_file': self.env_file if self.env_file.exists() else None,
                'discovery_method': 'legacy_fallback',
                'get_all_sources': lambda: []  # Empty list for fallback
            }
        
        enhanced_manager = self.enhanced_config_manager
        return enhanced_manager.discover_configuration_sources()
    
    def get_configuration_status(self) -> ConfigurationStatus:
        """
        Get detailed configuration status using unified system.
        
        Returns:
            ConfigurationStatus: Detailed configuration status
        """
        enhanced_manager = self.enhanced_config_manager
        return enhanced_manager.get_configuration_status()
    
    def get_active_configuration_sources(self) -> List:
        """
        Get list of active configuration sources.
        
        Returns:
            List of active configuration sources
        """
        enhanced_manager = self.enhanced_config_manager
        return enhanced_manager.get_active_sources()
    
    def has_cli_generated_configuration(self) -> bool:
        """
        Check if CLI-generated configuration is present and being used.
        
        Returns:
            True if CLI-generated configuration is active
        """
        if not ENHANCED_CONFIG_AVAILABLE:
            # Fallback: check if CLI-generated files exist
            cli_config_paths = [
                self.bot_config_file,
                self.accounts_file
            ]
            return any(path.exists() for path in cli_config_paths)
        
        enhanced_manager = self.enhanced_config_manager
        return enhanced_manager.has_cli_generated_config()
    
    def get_configuration_source_summary(self) -> Dict[str, Any]:
        """
        Get summary of configuration sources being used.
        
        Returns:
            Dictionary with source summary information
        """
        enhanced_manager = self.enhanced_config_manager
        return enhanced_manager.get_configuration_source_summary()
    
    def generate_configuration_guidance(self) -> List[str]:
        """
        Generate comprehensive configuration guidance based on current state.
        
        Returns:
            List of guidance messages
        """
        enhanced_manager = self.enhanced_config_manager
        return enhanced_manager.generate_configuration_guidance()
    
    def validate_with_runtime_consistency(self) -> ConfigValidationResult:
        """
        Validate configuration ensuring consistency with runtime validation.
        
        This method ensures that CLI validation uses exactly the same rules
        as the runtime system, preventing discrepancies.
        
        Returns:
            ConfigValidationResult: Validation results
        """
        return self.validate_configuration()  # Already updated to use unified validation
    
    def test_runtime_configuration_availability(self) -> CommandResult:
        """
        Test that CLI-generated configuration is immediately available to bot runtime.
        
        This method verifies that configuration created or modified by CLI commands
        can be immediately loaded by the bot runtime without restart.
        
        Returns:
            CommandResult: Test results with detailed information
        """
        try:
            # Test 1: Load configuration using CLI system
            cli_config = self.load_configuration()
            
            # Test 2: Load configuration using runtime system (simulated)
            from config.enhanced_manager import get_enhanced_config_manager
            runtime_manager = get_enhanced_config_manager(use_unified_loading=True)
            runtime_config = runtime_manager.load_with_discovery()
            
            # Test 3: Compare configuration sources
            cli_sources = self.get_active_configuration_sources()
            runtime_sources = runtime_manager.get_active_sources()
            
            # Test 4: Verify same files are being used
            cli_files = {str(source.file_path) for source in cli_sources}
            runtime_files = {str(source.file_path) for source in runtime_sources}
            
            test_results = {
                'cli_config_loaded': True,
                'runtime_config_loaded': True,
                'same_sources': cli_files == runtime_files,
                'cli_sources': [str(source.file_path) for source in cli_sources],
                'runtime_sources': [str(source.file_path) for source in runtime_sources],
                'config_consistency': True  # Will be updated below
            }
            
            # Test 5: Compare key configuration values
            consistency_checks = []
            
            # Check app name
            cli_app_name = getattr(cli_config, 'app_name', 'Unknown')
            runtime_app_name = getattr(runtime_config, 'app_name', 'Unknown')
            if cli_app_name == runtime_app_name:
                consistency_checks.append("✓ App name consistent")
            else:
                consistency_checks.append(f"✗ App name mismatch: CLI='{cli_app_name}', Runtime='{runtime_app_name}'")
                test_results['config_consistency'] = False
            
            # Check enabled exchanges
            cli_exchanges = set(name for name, cfg in cli_config.exchanges.items() if cfg.enabled)
            runtime_exchanges = set(name for name, cfg in runtime_config.exchanges.items() if cfg.enabled)
            if cli_exchanges == runtime_exchanges:
                consistency_checks.append("✓ Enabled exchanges consistent")
            else:
                consistency_checks.append(f"✗ Enabled exchanges mismatch: CLI={cli_exchanges}, Runtime={runtime_exchanges}")
                test_results['config_consistency'] = False
            
            # Check enabled strategies
            cli_strategies = set(name for name, cfg in cli_config.strategies.items() if cfg.enabled)
            runtime_strategies = set(name for name, cfg in runtime_config.strategies.items() if cfg.enabled)
            if cli_strategies == runtime_strategies:
                consistency_checks.append("✓ Enabled strategies consistent")
            else:
                consistency_checks.append(f"✗ Enabled strategies mismatch: CLI={cli_strategies}, Runtime={runtime_strategies}")
                test_results['config_consistency'] = False
            
            test_results['consistency_checks'] = consistency_checks
            
            # Generate result message
            if test_results['config_consistency'] and test_results['same_sources']:
                message = "✓ CLI-generated configuration is immediately available to bot runtime"
                suggestions = [
                    "Configuration integration is working correctly",
                    "CLI changes will be immediately available to the bot",
                    "No restart required for configuration updates"
                ]
                return CommandResult.success(message, data=test_results, suggestions=suggestions)
            else:
                issues = []
                if not test_results['same_sources']:
                    issues.append("CLI and runtime are using different configuration sources")
                if not test_results['config_consistency']:
                    issues.append("Configuration values are inconsistent between CLI and runtime")
                
                message = "⚠️ Configuration integration issues detected"
                suggestions = [
                    "Issues found:"
                ] + [f"  • {issue}" for issue in issues] + [
                    "",
                    "Troubleshooting steps:",
                    "1. Run 'genebot validate' to check configuration",
                    "2. Ensure all configuration files are readable",
                    "3. Check for file permission issues",
                    "4. Try 'genebot init-config --overwrite' to recreate configuration"
                ]
                
                return CommandResult.warning(message, data=test_results, suggestions=suggestions)
                
        except Exception as e:
            return CommandResult.error(
                f"Failed to test runtime configuration availability: {str(e)}",
                suggestions=[
                    "Check that configuration files exist and are readable",
                    "Verify that the unified configuration system is properly installed",
                    "Run 'genebot validate' to check for configuration issues",
                    "Check system logs for detailed error information"
                ]
            )
    
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
            'version': '1.1.31',
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
            'APP_VERSION': '1.1.31',
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
            f"APP_VERSION={env_vars.get('APP_VERSION', '1.1.31')}",
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
    
    def get_comprehensive_configuration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive configuration status using unified system.
        
        Returns:
            Dictionary with detailed configuration status information
        """
        try:
            # Get enhanced status from unified system
            enhanced_manager = self.enhanced_config_manager
            enhanced_status = enhanced_manager.get_detailed_status_report()
            
            # Add CLI-specific information
            cli_status = {
                'config_directory': {
                    'path': str(self.config_path),
                    'exists': self.config_path.exists(),
                    'writable': self.config_path.exists() and os.access(self.config_path, os.W_OK)
                },
                'backups_available': len(self.list_backups()) > 0,
                'cli_integration': {
                    'using_unified_loading': True,
                    'cli_generated_config': self.has_cli_generated_configuration(),
                    'runtime_consistency': True  # Will be tested below
                }
            }
            
            # Test runtime consistency
            try:
                consistency_test = self.test_runtime_configuration_availability()
                cli_status['cli_integration']['runtime_consistency'] = consistency_test.success
                cli_status['cli_integration']['consistency_details'] = consistency_test.data
            except Exception as e:
                cli_status['cli_integration']['runtime_consistency'] = False
                cli_status['cli_integration']['consistency_error'] = str(e)
            
            # Merge enhanced status with CLI status
            return {
                **enhanced_status,
                **cli_status
            }
            
        except Exception as e:
            # Fallback to basic status if enhanced system fails
            return {
                'mode': 'fallback',
                'error': str(e),
                'config_directory': {
                    'path': str(self.config_path),
                    'exists': self.config_path.exists(),
                    'writable': self.config_path.exists() and os.access(self.config_path, os.W_OK)
                },
                'files': {
                    'bot_config': self.file_manager.get_file_info(self.bot_config_file),
                    'accounts': self.file_manager.get_file_info(self.accounts_file),
                    'env': self.file_manager.get_file_info(self.env_file)
                },
                'backups_available': len(self.list_backups()) > 0
            }