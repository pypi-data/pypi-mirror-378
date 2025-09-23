"""
Configuration Integration Tests

Tests for the unified configuration loading system, covering:
- Configuration discovery in various scenarios (fresh install, CLI-generated, mixed sources)
- Configuration precedence and merging logic
- Error handling and recovery flows

Requirements covered: 1.1, 1.2, 1.3, 4.1
"""

import os
import tempfile
import shutil
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch, Mock
from typing import Dict, Any, Optional

from config.unified_loader import (
    UnifiedConfigLoader,
    ConfigurationDiscovery,
    ConfigurationMerger,
    ConfigurationSources,
    ConfigurationSource,
    ConfigurationStatus,
    ConfigurationNotFoundError,
    PartialConfigurationError,
    ConfigurationValidationError,
    MergeConflict
)
from config.enhanced_manager import EnhancedConfigManager
from config.models import TradingBotConfig
from tests.utils.test_helpers import test_environment, ConfigTestManager


class TestConfigurationDiscovery:
    """Test configuration discovery functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Change to temp directory for testing
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_fresh_install_scenario(self):
        """Test configuration discovery in fresh install scenario (no config files exist)."""
        discovery = ConfigurationDiscovery()
        
        # No configuration files should be found
        bot_config = discovery.find_bot_config()
        accounts_config = discovery.find_accounts_config()
        env_file = discovery.find_env_file()
        
        assert bot_config is None
        assert accounts_config is None
        assert env_file is None
        
        # Check discovery report
        report = discovery.get_discovery_report()
        assert any("No bot_config file found" in entry for entry in report)
        assert any("No accounts_config file found" in entry for entry in report)
        assert any("No env_file file found" in entry for entry in report)
    
    def test_cli_generated_config_discovery(self):
        """Test discovery of CLI-generated configuration files."""
        # Create CLI-generated config files
        bot_config_content = {
            'app_name': 'TradingBot',
            'version': '1.1.28',
            'debug': False,
            'dry_run': True
        }
        accounts_config_content = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret',
                    'sandbox': True
                }
            }
        }
        
        # Write CLI-generated files
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        accounts_config_path = self.config_dir / "accounts.yaml"
        env_file_path = self.config_dir / ".env"
        
        with open(bot_config_path, 'w') as f:
            yaml.dump(bot_config_content, f)
        
        with open(accounts_config_path, 'w') as f:
            yaml.dump(accounts_config_content, f)
        
        with open(env_file_path, 'w') as f:
            f.write("DEBUG=true\nDRY_RUN=false\n")
        
        discovery = ConfigurationDiscovery()
        
        # Should find CLI-generated files
        found_bot_config = discovery.find_bot_config()
        found_accounts_config = discovery.find_accounts_config()
        found_env_file = discovery.find_env_file()
        
        assert found_bot_config == bot_config_path
        assert found_accounts_config == accounts_config_path
        assert found_env_file == env_file_path
        
        # Check source information
        bot_source_info = discovery.get_source_info('bot_config')
        assert bot_source_info['source_type'] == 'cli_generated'
        assert bot_source_info['priority'] == 1
        
        accounts_source_info = discovery.get_source_info('accounts_config')
        assert accounts_source_info['source_type'] == 'cli_generated'
        assert accounts_source_info['priority'] == 1
    
    def test_mixed_sources_discovery(self):
        """Test discovery with mixed configuration sources."""
        # Create CLI-generated bot config
        cli_bot_config = self.config_dir / "trading_bot_config.yaml"
        with open(cli_bot_config, 'w') as f:
            yaml.dump({'app_name': 'CLI_Bot'}, f)
        
        # Create user-specified accounts config in current directory
        user_accounts_config = self.temp_dir / "accounts.yaml"
        with open(user_accounts_config, 'w') as f:
            yaml.dump({'exchanges': {'coinbase': {'exchange_type': 'coinbase'}}}, f)
        
        # Create env file in current directory
        env_file = self.temp_dir / ".env"
        with open(env_file, 'w') as f:
            f.write("LOG_LEVEL=DEBUG\n")
        
        discovery = ConfigurationDiscovery()
        
        found_bot_config = discovery.find_bot_config()
        found_accounts_config = discovery.find_accounts_config()
        found_env_file = discovery.find_env_file()
        
        # Should find CLI-generated bot config (higher priority)
        assert found_bot_config == cli_bot_config
        # Should find user accounts config in current directory
        assert found_accounts_config == user_accounts_config
        # Should find env file in current directory
        assert found_env_file == env_file
        
        # Verify source types
        all_sources = discovery.get_all_source_info()
        assert all_sources['bot_config']['source_type'] == 'cli_generated'
        assert all_sources['accounts_config']['source_type'] == 'current_directory'
        assert all_sources['env_file']['source_type'] == 'current_directory'
    
    @patch.dict(os.environ, {
        'GENEBOT_CONFIG_FILE': '/custom/path/config.yaml',
        'GENEBOT_ACCOUNTS_FILE': '/custom/path/accounts.yaml'
    })
    def test_environment_variable_overrides(self):
        """Test configuration discovery with environment variable overrides."""
        # Create files at custom paths (mock their existence)
        with patch('pathlib.Path.exists') as mock_exists:
            with patch('pathlib.Path.is_file') as mock_is_file:
                # Mock that custom paths exist
                def exists_side_effect(path_obj):
                    path_str = str(path_obj)
                    return '/custom/path/' in path_str
                
                mock_exists.side_effect = lambda: exists_side_effect(mock_exists.call_args[0][0])
                mock_is_file.return_value = True
                
                discovery = ConfigurationDiscovery()
                
                found_bot_config = discovery.find_bot_config()
                found_accounts_config = discovery.find_accounts_config()
                
                assert str(found_bot_config) == '/custom/path/config.yaml'
                assert str(found_accounts_config) == '/custom/path/accounts.yaml'
                
                # Verify environment override source type
                bot_source_info = discovery.get_source_info('bot_config')
                accounts_source_info = discovery.get_source_info('accounts_config')
                
                assert bot_source_info['source_type'] == 'environment_override'
                assert accounts_source_info['source_type'] == 'environment_override'
                assert bot_source_info['priority'] == 0  # Highest priority
                assert accounts_source_info['priority'] == 0
    
    def test_legacy_config_support(self):
        """Test discovery of legacy configuration files."""
        # Create legacy multi_market_config.yaml
        legacy_config_path = self.config_dir / "multi_market_config.yaml"
        with open(legacy_config_path, 'w') as f:
            yaml.dump({'app_name': 'LegacyBot', 'version': '1.0.0'}, f)
        
        discovery = ConfigurationDiscovery()
        found_config = discovery.find_bot_config()
        
        # Should find legacy config
        assert found_config == legacy_config_path
        
        source_info = discovery.get_source_info('bot_config')
        assert source_info['source_type'] == 'cli_generated'
    
    def test_environment_override_detection(self):
        """Test detection of environment variable overrides."""
        with patch.dict(os.environ, {
            'DEBUG': 'true',
            'DRY_RUN': 'false',
            'RISK_MAX_POSITION_SIZE': '0.2',
            'LOG_LEVEL': 'DEBUG',
            'DATABASE_URL': 'postgresql://test:test@localhost/test'
        }):
            discovery = ConfigurationDiscovery()
            env_overrides = discovery.detect_environment_overrides()
            
            assert 'DEBUG' in env_overrides
            assert 'DRY_RUN' in env_overrides
            assert 'RISK_MAX_POSITION_SIZE' in env_overrides
            assert 'LOG_LEVEL' in env_overrides
            assert 'DATABASE_URL' in env_overrides
            
            # Check override details
            debug_override = env_overrides['DEBUG']
            assert debug_override['value'] == 'true'
            assert debug_override['type'] == 'value_override'
            
            risk_override = env_overrides['RISK_MAX_POSITION_SIZE']
            assert risk_override['value'] == '0.2'
            assert 'Maximum position size' in risk_override['description']
    
    def test_configuration_status_report(self):
        """Test comprehensive configuration status reporting."""
        # Create some config files
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        with open(bot_config_path, 'w') as f:
            yaml.dump({'app_name': 'TestBot'}, f)
        
        with patch.dict(os.environ, {'DEBUG': 'true', 'LOG_LEVEL': 'INFO'}):
            discovery = ConfigurationDiscovery()
            
            # Trigger discovery
            discovery.find_bot_config()
            discovery.find_accounts_config()
            discovery.find_env_file()
            
            status_report = discovery.generate_configuration_status_report()
            
            assert 'discovery_report' in status_report
            assert 'source_tracking' in status_report
            assert 'environment_overrides' in status_report
            assert 'search_paths' in status_report
            
            # Check that bot config was found
            assert 'bot_config' in status_report['source_tracking']
            
            # Check environment overrides
            assert 'DEBUG' in status_report['environment_overrides']
            assert 'LOG_LEVEL' in status_report['environment_overrides']


class TestConfigurationMerger:
    """Test configuration merging functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.merger = ConfigurationMerger()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_configuration_merge(self):
        """Test merging with default configuration only."""
        sources = ConfigurationSources()
        merged_config = self.merger.merge_sources(sources)
        
        # Should contain default values
        assert merged_config['app_name'] == 'TradingBot'
        assert merged_config['version'] == '1.1.28'
        assert merged_config['debug'] is False
        assert merged_config['dry_run'] is True
        assert 'risk' in merged_config
        assert 'database' in merged_config
        assert 'logging' in merged_config
    
    def test_cli_generated_config_precedence(self):
        """Test that CLI-generated config takes precedence over defaults."""
        # Create CLI-generated config file
        cli_config_path = self.temp_dir / "trading_bot_config.yaml"
        cli_config_content = {
            'app_name': 'CLI_TradingBot',
            'debug': True,
            'risk': {
                'max_position_size': 0.2,
                'stop_loss_percentage': 0.03
            }
        }
        
        with open(cli_config_path, 'w') as f:
            yaml.dump(cli_config_content, f)
        
        sources = ConfigurationSources(bot_config_file=cli_config_path)
        merged_config = self.merger.merge_sources(sources)
        
        # CLI values should override defaults
        assert merged_config['app_name'] == 'CLI_TradingBot'
        assert merged_config['debug'] is True
        assert merged_config['risk']['max_position_size'] == 0.2
        assert merged_config['risk']['stop_loss_percentage'] == 0.03
        
        # Default values should still be present for unspecified keys
        assert merged_config['version'] == '1.1.28'  # Default
        assert merged_config['risk']['max_daily_loss'] == 0.05  # Default
    
    def test_accounts_config_merge(self):
        """Test merging of accounts configuration."""
        # Create accounts config file
        accounts_config_path = self.temp_dir / "accounts.yaml"
        accounts_config_content = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret',
                    'sandbox': True
                },
                'coinbase': {
                    'exchange_type': 'coinbase',
                    'api_key': 'cb_key',
                    'api_secret': 'cb_secret'
                }
            }
        }
        
        with open(accounts_config_path, 'w') as f:
            yaml.dump(accounts_config_content, f)
        
        sources = ConfigurationSources(accounts_config_file=accounts_config_path)
        merged_config = self.merger.merge_sources(sources)
        
        # Should have exchanges from accounts config
        assert 'exchanges' in merged_config
        assert 'binance' in merged_config['exchanges']
        assert 'coinbase' in merged_config['exchanges']
        assert merged_config['exchanges']['binance']['api_key'] == 'test_key'
        assert merged_config['exchanges']['coinbase']['api_key'] == 'cb_key'
    
    def test_environment_variable_precedence(self):
        """Test that environment variables take highest precedence."""
        # Create config file
        config_path = self.temp_dir / "config.yaml"
        config_content = {
            'app_name': 'FileBot',
            'debug': False,
            'risk': {
                'max_position_size': 0.1,
                'stop_loss_percentage': 0.02
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_content, f)
        
        with patch.dict(os.environ, {
            'APP_NAME': 'EnvBot',
            'DEBUG': 'true',
            'RISK_MAX_POSITION_SIZE': '0.3',
            'LOG_LEVEL': 'DEBUG'
        }):
            sources = ConfigurationSources(bot_config_file=config_path)
            merged_config = self.merger.merge_sources(sources)
            
            # Environment variables should override file values
            assert merged_config['app_name'] == 'EnvBot'
            assert merged_config['debug'] is True
            assert merged_config['risk']['max_position_size'] == 0.3
            assert merged_config['logging']['log_level'] == 'DEBUG'
            
            # File values should be preserved for non-overridden keys
            assert merged_config['risk']['stop_loss_percentage'] == 0.02
    
    def test_merge_conflict_detection(self):
        """Test detection and resolution of merge conflicts."""
        # Create two config files with conflicting values
        config1_path = self.temp_dir / "config1.yaml"
        config1_content = {
            'app_name': 'Bot1',
            'risk': {
                'max_position_size': 0.1
            }
        }
        
        config2_path = self.temp_dir / "config2.yaml"
        config2_content = {
            'app_name': 'Bot2',
            'risk': {
                'max_position_size': 0.2
            }
        }
        
        with open(config1_path, 'w') as f:
            yaml.dump(config1_content, f)
        
        with open(config2_path, 'w') as f:
            yaml.dump(config2_content, f)
        
        # Simulate merging with different precedence
        base_config = self.merger._get_default_configuration()
        
        # Load and merge first config
        config1_data = self.merger._load_yaml_file(config1_path)
        merged_config = self.merger._deep_merge_with_conflict_detection(
            base_config, config1_data, 'config1', 'defaults'
        )
        
        # Load and merge second config (should create conflicts)
        config2_data = self.merger._load_yaml_file(config2_path)
        final_config = self.merger._deep_merge_with_conflict_detection(
            merged_config, config2_data, 'config2', 'config1'
        )
        
        # Check that conflicts were detected
        assert len(self.merger.merge_conflicts) > 0
        
        # Find the app_name conflict
        app_name_conflict = next(
            (c for c in self.merger.merge_conflicts if c.key == 'app_name'), 
            None
        )
        assert app_name_conflict is not None
        assert app_name_conflict.value1 == 'Bot1'
        assert app_name_conflict.value2 == 'Bot2'
        assert app_name_conflict.resolved_value == 'Bot2'  # config2 wins
    
    def test_exchange_environment_overrides(self):
        """Test dynamic exchange environment variable overrides."""
        with patch.dict(os.environ, {
            'EXCHANGE_BINANCE_API_KEY': 'env_binance_key',
            'EXCHANGE_BINANCE_SANDBOX': 'false',
            'EXCHANGE_COINBASE_API_KEY': 'env_coinbase_key',
            'EXCHANGE_COINBASE_ENABLED': 'true'
        }):
            sources = ConfigurationSources()
            merged_config = self.merger.merge_sources(sources)
            
            # Should have exchanges from environment variables
            assert 'exchanges' in merged_config
            assert 'binance' in merged_config['exchanges']
            assert 'coinbase' in merged_config['exchanges']
            
            assert merged_config['exchanges']['binance']['api_key'] == 'env_binance_key'
            assert merged_config['exchanges']['binance']['sandbox'] is False
            assert merged_config['exchanges']['coinbase']['api_key'] == 'env_coinbase_key'
            assert merged_config['exchanges']['coinbase']['enabled'] is True
    
    def test_strategy_environment_overrides(self):
        """Test dynamic strategy environment variable overrides."""
        with patch.dict(os.environ, {
            'STRATEGY_RSI_ENABLED': 'true',
            'STRATEGY_RSI_RSI_PERIOD': '21',
            'STRATEGY_RSI_OVERSOLD': '25',
            'STRATEGY_MA_ENABLED': 'false',
            'STRATEGY_MA_FAST_PERIOD': '5'
        }):
            sources = ConfigurationSources()
            merged_config = self.merger.merge_sources(sources)
            
            # Should have strategies from environment variables
            assert 'strategies' in merged_config
            assert 'rsi' in merged_config['strategies']
            assert 'ma' in merged_config['strategies']
            
            assert merged_config['strategies']['rsi']['enabled'] is True
            assert merged_config['strategies']['rsi']['rsi_period'] == 21
            assert merged_config['strategies']['rsi']['oversold'] == 25
            assert merged_config['strategies']['ma']['enabled'] is False
            assert merged_config['strategies']['ma']['fast_period'] == 5
    
    def test_merge_history_tracking(self):
        """Test that merge history is properly tracked."""
        sources = ConfigurationSources()
        self.merger.merge_sources(sources)
        
        merge_history = self.merger.get_merge_history()
        
        # Should have recorded merge steps
        assert len(merge_history) > 0
        
        # Should have defaults step
        defaults_step = next((step for step in merge_history if step['step'] == 'defaults'), None)
        assert defaults_step is not None
        assert 'timestamp' in defaults_step
        assert 'config_keys' in defaults_step
        
        # Should have environment variables step
        env_step = next((step for step in merge_history if step['step'] == 'environment_variables'), None)
        assert env_step is not None


class TestUnifiedConfigLoader:
    """Test unified configuration loader functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Change to temp directory for testing
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_fresh_install_error_handling(self):
        """Test error handling for fresh install scenario."""
        loader = UnifiedConfigLoader()
        
        with pytest.raises(ConfigurationNotFoundError) as exc_info:
            loader.load_configuration()
        
        error = exc_info.value
        assert "No configuration files found" in str(error)
        assert len(error.guidance) > 0
        assert any("init-config" in guidance for guidance in error.guidance)
    
    def test_partial_configuration_error_handling(self):
        """Test error handling for partial configuration scenario."""
        # Create only bot config, missing accounts config
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        with open(bot_config_path, 'w') as f:
            yaml.dump({'app_name': 'PartialBot'}, f)
        
        loader = UnifiedConfigLoader()
        
        with pytest.raises(PartialConfigurationError) as exc_info:
            loader.load_configuration()
        
        error = exc_info.value
        assert "Partial configuration detected" in str(error)
        assert 'accounts.yaml' in error.missing_files
        assert str(bot_config_path) in error.found_files
        assert len(error.completion_suggestions) > 0
    
    def test_successful_configuration_loading(self):
        """Test successful configuration loading with complete setup."""
        # Create complete configuration
        bot_config_content = {
            'app_name': 'TestBot',
            'version': '1.1.28',
            'debug': False,
            'dry_run': True,
            'base_currency': 'USDT'
        }
        
        accounts_config_content = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret',
                    'sandbox': True,
                    'enabled': True
                }
            }
        }
        
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        accounts_config_path = self.config_dir / "accounts.yaml"
        
        with open(bot_config_path, 'w') as f:
            yaml.dump(bot_config_content, f)
        
        with open(accounts_config_path, 'w') as f:
            yaml.dump(accounts_config_content, f)
        
        loader = UnifiedConfigLoader()
        config = loader.load_configuration()
        
        # Should successfully load and validate configuration
        assert isinstance(config, TradingBotConfig)
        assert config.app_name == 'TestBot'
        assert len(config.exchanges) == 1
        assert 'binance' in config.exchanges
    
    def test_configuration_status_reporting(self):
        """Test configuration status reporting."""
        # Create configuration files
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        accounts_config_path = self.config_dir / "accounts.yaml"
        
        with open(bot_config_path, 'w') as f:
            yaml.dump({'app_name': 'StatusBot'}, f)
        
        with open(accounts_config_path, 'w') as f:
            yaml.dump({'exchanges': {'binance': {'exchange_type': 'binance'}}}, f)
        
        loader = UnifiedConfigLoader()
        
        # Load configuration first
        try:
            loader.load_configuration()
        except Exception:
            pass  # May fail validation, but we want to test status reporting
        
        status = loader.get_configuration_status()
        
        assert isinstance(status, ConfigurationStatus)
        assert len(status.active_sources) > 0
        
        # Should have found both config files
        source_paths = [source.file_path for source in status.active_sources]
        assert bot_config_path in source_paths
        assert accounts_config_path in source_paths
    
    def test_configuration_discovery_integration(self):
        """Test integration between discovery and loading."""
        # Create mixed configuration sources
        cli_bot_config = self.config_dir / "trading_bot_config.yaml"
        user_accounts_config = self.temp_dir / "accounts.yaml"
        
        with open(cli_bot_config, 'w') as f:
            yaml.dump({'app_name': 'MixedBot', 'debug': True}, f)
        
        with open(user_accounts_config, 'w') as f:
            yaml.dump({'exchanges': {'coinbase': {'exchange_type': 'coinbase'}}}, f)
        
        loader = UnifiedConfigLoader()
        sources = loader.discover_configuration()
        
        assert sources.bot_config_file == cli_bot_config
        assert sources.accounts_config_file == user_accounts_config
        
        # Discovery method should be recorded
        assert sources.discovery_method == "automatic"


class TestEnhancedConfigManager:
    """Test enhanced configuration manager integration."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Change to temp directory for testing
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_enhanced_manager_initialization(self):
        """Test enhanced configuration manager initialization."""
        manager = EnhancedConfigManager()
        
        assert hasattr(manager, 'unified_loader')
        assert isinstance(manager.unified_loader, UnifiedConfigLoader)
    
    def test_load_with_discovery_integration(self):
        """Test loading configuration with discovery integration."""
        # Create complete configuration
        bot_config_content = {
            'app_name': 'EnhancedBot',
            'version': '1.1.28',
            'debug': False
        }
        
        accounts_config_content = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': 'enhanced_key',
                    'api_secret': 'enhanced_secret',
                    'sandbox': True,
                    'enabled': True
                }
            }
        }
        
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        accounts_config_path = self.config_dir / "accounts.yaml"
        
        with open(bot_config_path, 'w') as f:
            yaml.dump(bot_config_content, f)
        
        with open(accounts_config_path, 'w') as f:
            yaml.dump(accounts_config_content, f)
        
        manager = EnhancedConfigManager()
        config = manager.load_with_discovery()
        
        assert isinstance(config, TradingBotConfig)
        assert config.app_name == 'EnhancedBot'
        assert len(config.exchanges) == 1
    
    def test_active_sources_reporting(self):
        """Test active sources reporting."""
        # Create configuration files
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        with open(bot_config_path, 'w') as f:
            yaml.dump({'app_name': 'SourceBot'}, f)
        
        manager = EnhancedConfigManager()
        
        try:
            manager.load_with_discovery()
        except Exception:
            pass  # May fail validation
        
        active_sources = manager.get_active_sources()
        
        assert isinstance(active_sources, list)
        assert len(active_sources) > 0
        
        # Should have bot config source
        bot_config_source = next(
            (source for source in active_sources if source.file_path == bot_config_path),
            None
        )
        assert bot_config_source is not None
        assert bot_config_source.source_type == 'cli_generated'


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery flows."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Change to temp directory for testing
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_yaml_error_handling(self):
        """Test handling of invalid YAML files."""
        # Create invalid YAML file
        invalid_config_path = self.config_dir / "trading_bot_config.yaml"
        with open(invalid_config_path, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        loader = UnifiedConfigLoader()
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_configuration()
        
        error = exc_info.value
        assert "Configuration validation failed" in str(error)
        assert len(error.validation_errors) > 0
        assert any("YAML" in err or "yaml" in err for err in error.validation_errors)
    
    def test_missing_required_fields_error_handling(self):
        """Test handling of configuration with missing required fields."""
        # Create config with missing required exchanges
        incomplete_config_content = {
            'app_name': 'IncompleteBot',
            'version': '1.1.28'
            # Missing exchanges and strategies
        }
        
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        accounts_config_path = self.config_dir / "accounts.yaml"
        
        with open(bot_config_path, 'w') as f:
            yaml.dump(incomplete_config_content, f)
        
        with open(accounts_config_path, 'w') as f:
            yaml.dump({}, f)  # Empty accounts config
        
        loader = UnifiedConfigLoader()
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_configuration()
        
        error = exc_info.value
        assert len(error.validation_errors) > 0
        assert len(error.recovery_suggestions) > 0
    
    def test_permission_error_handling(self):
        """Test handling of permission errors when reading config files."""
        # Create config file
        config_path = self.config_dir / "trading_bot_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump({'app_name': 'PermissionBot'}, f)
        
        # Mock permission error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            loader = UnifiedConfigLoader()
            
            with pytest.raises(ConfigurationValidationError) as exc_info:
                loader.load_configuration()
            
            error = exc_info.value
            assert "Permission denied" in str(error) or any("Permission" in err for err in error.validation_errors)
    
    def test_configuration_recovery_suggestions(self):
        """Test that appropriate recovery suggestions are provided."""
        loader = UnifiedConfigLoader()
        
        # Test fresh install scenario
        with pytest.raises(ConfigurationNotFoundError) as exc_info:
            loader.load_configuration()
        
        error = exc_info.value
        guidance = error.guidance
        
        # Should suggest running init-config
        assert any("init-config" in suggestion for suggestion in guidance)
        assert any("configuration" in suggestion.lower() for suggestion in guidance)
    
    def test_partial_configuration_recovery(self):
        """Test recovery suggestions for partial configuration."""
        # Create only bot config
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        with open(bot_config_path, 'w') as f:
            yaml.dump({'app_name': 'PartialBot'}, f)
        
        loader = UnifiedConfigLoader()
        
        with pytest.raises(PartialConfigurationError) as exc_info:
            loader.load_configuration()
        
        error = exc_info.value
        suggestions = error.completion_suggestions
        
        # Should suggest creating missing files
        assert len(suggestions) > 0
        assert any("accounts" in suggestion.lower() for suggestion in suggestions)
    
    def test_validation_error_recovery(self):
        """Test recovery suggestions for validation errors."""
        # Create config with validation errors
        invalid_config_content = {
            'app_name': 'InvalidBot',
            'version': '1.1.28',
            'debug': 'not_a_boolean',  # Invalid type
            'risk': {
                'max_position_size': 1.5  # Invalid value > 1.0
            }
        }
        
        accounts_config_content = {
            'exchanges': {
                'binance': {
                    'exchange_type': 'binance',
                    'api_key': '',  # Invalid empty key
                    'api_secret': 'test_secret'
                }
            }
        }
        
        bot_config_path = self.config_dir / "trading_bot_config.yaml"
        accounts_config_path = self.config_dir / "accounts.yaml"
        
        with open(bot_config_path, 'w') as f:
            yaml.dump(invalid_config_content, f)
        
        with open(accounts_config_path, 'w') as f:
            yaml.dump(accounts_config_content, f)
        
        loader = UnifiedConfigLoader()
        
        with pytest.raises(ConfigurationValidationError) as exc_info:
            loader.load_configuration()
        
        error = exc_info.value
        
        # Should have specific validation errors
        assert len(error.validation_errors) > 0
        
        # Should have recovery suggestions
        assert len(error.recovery_suggestions) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])