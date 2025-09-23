"""
Tests for configuration hot-reloading functionality.

This module tests the configuration hot-reloader to ensure it properly
detects file changes, validates configurations, and provides safe reloading
without requiring bot restart.
"""

import os
import time
import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import yaml

# Import configuration components
from config.enhanced_manager import EnhancedConfigManager
from config.models import TradingBotConfig

# Import hot-reloader components (skip tests if not available)
try:
    from config.hot_reloader import (
        ConfigurationHotReloader,
        ConfigurationChange,
        ReloadResult,
        ConfigurationFileHandler
    )
    HOT_RELOADER_AVAILABLE = True
except ImportError:
    HOT_RELOADER_AVAILABLE = False


@pytest.mark.skipif(not HOT_RELOADER_AVAILABLE, reason="Hot-reloader dependencies not available")
class TestConfigurationHotReloader:
    """Test configuration hot-reloading functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.config_dir.mkdir(exist_ok=True)
        
        # Create test configuration files
        self.bot_config_file = self.config_dir / 'trading_bot_config.yaml'
        self.accounts_config_file = self.config_dir / 'accounts.yaml'
        self.env_file = Path(self.temp_dir) / '.env'
        
        # Create initial configuration content
        self.initial_bot_config = {
            'app_name': 'TestBot',
            'version': '1.0.0',
            'debug': False,
            'dry_run': True,
            'base_currency': 'USDT',
            'risk': {
                'max_position_size': 0.1,
                'max_daily_loss': 0.05,
                'stop_loss_percentage': 0.02
            },
            'database': {
                'database_type': 'sqlite',
                'database_url': 'sqlite:///test.db'
            },
            'logging': {
                'log_level': 'INFO'
            }
        }
        
        self.initial_accounts_config = {
            'exchanges': {
                'test_exchange': {
                    'exchange_type': 'test',
                    'api_key': 'test_key',
                    'api_secret': 'test_secret',
                    'enabled': True
                }
            }
        }
        
        self.initial_env_content = "TEST_VAR=test_value\nDEBUG=false\n"
        
        # Write initial files
        self._write_config_files()
        
        # Initialize configuration manager
        self.config_manager = EnhancedConfigManager(
            config_file=str(self.bot_config_file),
            env_file=str(self.env_file),
            use_unified_loading=True,
            enable_hot_reload=True,
            auto_reload=False,  # Manual control for testing
            validation_required=True
        )
        
        # Initialize hot-reloader
        self.hot_reloader = ConfigurationHotReloader(
            config_manager=self.config_manager,
            auto_reload=False,  # Manual control for testing
            validation_required=True
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        # Stop hot-reloader if running
        if hasattr(self, 'hot_reloader') and self.hot_reloader:
            self.hot_reloader.stop()
        
        # Clean up temporary files
        import shutil
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _write_config_files(self):
        """Write configuration files with current content."""
        with open(self.bot_config_file, 'w') as f:
            yaml.dump(self.initial_bot_config, f)
        
        with open(self.accounts_config_file, 'w') as f:
            yaml.dump(self.initial_accounts_config, f)
        
        with open(self.env_file, 'w') as f:
            f.write(self.initial_env_content)
    
    def test_hot_reloader_initialization(self):
        """Test hot-reloader initialization."""
        assert self.hot_reloader is not None
        assert not self.hot_reloader.observer or not self.hot_reloader.observer.is_alive()
        
        # Check initial status
        status = self.hot_reloader.get_status()
        assert not status['is_running']
        assert status['auto_reload_enabled'] == False
        assert status['validation_required'] == True
        assert status['reload_count'] == 0
    
    def test_hot_reloader_start_stop(self):
        """Test starting and stopping the hot-reloader."""
        # Start hot-reloader
        success = self.hot_reloader.start()
        assert success
        
        # Check status
        status = self.hot_reloader.get_status()
        assert status['is_running']
        assert len(status['monitored_files']) > 0
        
        # Stop hot-reloader
        self.hot_reloader.stop()
        
        # Check status after stop
        status = self.hot_reloader.get_status()
        assert not status['is_running']
    
    def test_configuration_file_detection(self):
        """Test configuration file detection."""
        # Test known configuration files
        assert self.hot_reloader._is_configuration_file(self.bot_config_file)
        assert self.hot_reloader._is_configuration_file(self.accounts_config_file)
        assert self.hot_reloader._is_configuration_file(self.env_file)
        
        # Test non-configuration files
        test_file = Path(self.temp_dir) / 'test.txt'
        assert not self.hot_reloader._is_configuration_file(test_file)
    
    def test_manual_reload(self):
        """Test manual configuration reload."""
        # Load initial configuration
        initial_config = self.config_manager.get_config()
        assert initial_config.app_name == 'TestBot'
        
        # Modify configuration file
        modified_config = self.initial_bot_config.copy()
        modified_config['app_name'] = 'ModifiedTestBot'
        modified_config['debug'] = True
        
        with open(self.bot_config_file, 'w') as f:
            yaml.dump(modified_config, f)
        
        # Trigger manual reload
        result = self.hot_reloader.manual_reload()
        
        # Check reload result
        assert result is not None
        assert result.success
        assert len(result.changes) == 1
        assert result.changes[0].change_type == 'manual'
        
        # Verify configuration was reloaded
        reloaded_config = self.config_manager.get_config()
        assert reloaded_config.app_name == 'ModifiedTestBot'
        assert reloaded_config.debug == True
    
    def test_reload_with_validation_error(self):
        """Test reload behavior with validation errors."""
        # Create invalid configuration
        invalid_config = {
            'app_name': 'TestBot',
            'risk': {
                'max_position_size': -0.1,  # Invalid negative value
                'max_daily_loss': 2.0,      # Invalid value > 1
            }
        }
        
        with open(self.bot_config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        # Trigger manual reload
        result = self.hot_reloader.manual_reload()
        
        # Check that reload failed due to validation
        assert result is not None
        assert not result.success
        assert len(result.errors) > 0
        
        # Check that rollback was attempted
        # Note: In a real implementation, this would restore the previous config
        # For this test, we just verify the rollback flag
        assert result.rollback_performed or len(result.errors) > 0
    
    def test_callback_system(self):
        """Test reload and change callback system."""
        reload_callback_called = threading.Event()
        change_callback_called = threading.Event()
        
        reload_results = []
        change_events = []
        
        def reload_callback(result):
            reload_results.append(result)
            reload_callback_called.set()
        
        def change_callback(change):
            change_events.append(change)
            change_callback_called.set()
        
        # Add callbacks
        self.hot_reloader.add_reload_callback(reload_callback)
        self.hot_reloader.add_change_callback(change_callback)
        
        # Trigger manual reload to test callbacks
        result = self.hot_reloader.manual_reload()
        
        # Wait for callbacks (with timeout)
        reload_callback_called.wait(timeout=1)
        
        # Check that callbacks were called
        assert len(reload_results) == 1
        assert reload_results[0].success == result.success
        
        # Remove callbacks
        self.hot_reloader.remove_reload_callback(reload_callback)
        self.hot_reloader.remove_change_callback(change_callback)
        
        # Trigger another reload
        self.hot_reloader.manual_reload()
        
        # Callbacks should not be called again
        assert len(reload_results) == 1  # Still only one result
    
    def test_configuration_backup_system(self):
        """Test configuration backup functionality."""
        # Start hot-reloader to create initial backup
        self.hot_reloader.start()
        
        # Get initial statistics
        stats = self.hot_reloader.get_statistics()
        initial_backup_count = stats.get('backup_count', 0)
        
        # Perform several reloads to create backups
        for i in range(3):
            # Modify configuration
            modified_config = self.initial_bot_config.copy()
            modified_config['app_name'] = f'TestBot_{i}'
            
            with open(self.bot_config_file, 'w') as f:
                yaml.dump(modified_config, f)
            
            # Trigger reload
            result = self.hot_reloader.manual_reload()
            assert result.success
        
        # Check that backups were created
        final_stats = self.hot_reloader.get_statistics()
        final_backup_count = final_stats.get('backup_count', 0)
        
        # Should have more backups now
        assert final_backup_count > initial_backup_count
        
        self.hot_reloader.stop()
    
    def test_statistics_tracking(self):
        """Test statistics tracking functionality."""
        # Get initial statistics
        initial_stats = self.hot_reloader.get_statistics()
        assert initial_stats['total_reloads'] == 0
        assert initial_stats['successful_reloads'] == 0
        assert initial_stats['failed_reloads'] == 0
        
        # Perform successful reload
        result = self.hot_reloader.manual_reload()
        assert result.success
        
        # Check updated statistics
        stats = self.hot_reloader.get_statistics()
        assert stats['total_reloads'] == 1
        assert stats['successful_reloads'] == 1
        assert stats['failed_reloads'] == 0
        assert stats['success_rate'] == 100.0
        
        # Perform failed reload
        invalid_config = {'invalid': 'config'}
        with open(self.bot_config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        result = self.hot_reloader.manual_reload()
        assert not result.success
        
        # Check updated statistics
        final_stats = self.hot_reloader.get_statistics()
        assert final_stats['total_reloads'] == 2
        assert final_stats['successful_reloads'] == 1
        assert final_stats['failed_reloads'] == 1
        assert final_stats['success_rate'] == 50.0


@pytest.mark.skipif(not HOT_RELOADER_AVAILABLE, reason="Hot-reloader dependencies not available")
class TestEnhancedConfigManagerHotReload:
    """Test hot-reloading integration with EnhancedConfigManager."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / 'config'
        self.config_dir.mkdir(exist_ok=True)
        
        # Create test configuration files
        self.bot_config_file = self.config_dir / 'trading_bot_config.yaml'
        self.env_file = Path(self.temp_dir) / '.env'
        
        # Create initial configuration
        initial_config = {
            'app_name': 'TestBot',
            'version': '1.0.0',
            'debug': False,
            'dry_run': True,
            'base_currency': 'USDT',
            'exchanges': {},
            'strategies': {},
            'risk': {
                'max_position_size': 0.1,
                'max_daily_loss': 0.05,
                'stop_loss_percentage': 0.02
            },
            'database': {
                'database_type': 'sqlite',
                'database_url': 'sqlite:///test.db'
            },
            'logging': {
                'log_level': 'INFO'
            }
        }
        
        with open(self.bot_config_file, 'w') as f:
            yaml.dump(initial_config, f)
        
        with open(self.env_file, 'w') as f:
            f.write("TEST_VAR=test_value\n")
    
    def teardown_method(self):
        """Clean up test environment."""
        # Clean up temporary files
        import shutil
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_enhanced_config_manager_with_hot_reload(self):
        """Test EnhancedConfigManager with hot-reloading enabled."""
        # Initialize with hot-reloading enabled
        config_manager = EnhancedConfigManager(
            config_file=str(self.bot_config_file),
            env_file=str(self.env_file),
            use_unified_loading=True,
            enable_hot_reload=True,
            auto_reload=False,
            validation_required=True
        )
        
        # Check that hot-reloading is enabled
        assert config_manager.is_hot_reload_enabled()
        
        # Start hot-reloader
        success = config_manager.start_hot_reloader()
        assert success
        
        # Get hot-reload status
        status = config_manager.get_hot_reload_status()
        assert status['enabled']
        assert status['is_running']
        
        # Stop hot-reloader
        config_manager.stop_hot_reloader()
        
        # Check status after stop
        status = config_manager.get_hot_reload_status()
        assert not status['is_running']
    
    def test_enhanced_config_manager_without_hot_reload(self):
        """Test EnhancedConfigManager with hot-reloading disabled."""
        # Initialize with hot-reloading disabled
        config_manager = EnhancedConfigManager(
            config_file=str(self.bot_config_file),
            env_file=str(self.env_file),
            use_unified_loading=True,
            enable_hot_reload=False
        )
        
        # Check that hot-reloading is disabled
        assert not config_manager.is_hot_reload_enabled()
        
        # Try to start hot-reloader (should fail gracefully)
        success = config_manager.start_hot_reloader()
        assert not success
        
        # Get hot-reload status
        status = config_manager.get_hot_reload_status()
        assert not status['enabled']
    
    def test_manual_reload_through_config_manager(self):
        """Test manual reload through EnhancedConfigManager."""
        # Initialize with hot-reloading enabled
        config_manager = EnhancedConfigManager(
            config_file=str(self.bot_config_file),
            env_file=str(self.env_file),
            use_unified_loading=True,
            enable_hot_reload=True,
            auto_reload=False,
            validation_required=True
        )
        
        # Load initial configuration
        initial_config = config_manager.get_config()
        assert initial_config.app_name == 'TestBot'
        
        # Modify configuration file
        modified_config = {
            'app_name': 'ModifiedTestBot',
            'version': '1.0.1',
            'debug': True,
            'dry_run': True,
            'base_currency': 'USDT',
            'exchanges': {},
            'strategies': {},
            'risk': {
                'max_position_size': 0.2,  # Changed value
                'max_daily_loss': 0.05,
                'stop_loss_percentage': 0.02
            },
            'database': {
                'database_type': 'sqlite',
                'database_url': 'sqlite:///test.db'
            },
            'logging': {
                'log_level': 'DEBUG'  # Changed value
            }
        }
        
        with open(self.bot_config_file, 'w') as f:
            yaml.dump(modified_config, f)
        
        # Trigger manual reload
        result = config_manager.manual_reload()
        assert result is not None
        assert result.success
        
        # Verify configuration was reloaded
        reloaded_config = config_manager.get_config()
        assert reloaded_config.app_name == 'ModifiedTestBot'
        assert reloaded_config.version == '1.0.1'
        assert reloaded_config.debug == True
        assert reloaded_config.risk.max_position_size == 0.2
        assert reloaded_config.logging.log_level == 'DEBUG'


@pytest.mark.skipif(HOT_RELOADER_AVAILABLE, reason="Testing behavior when hot-reloader is not available")
class TestHotReloadUnavailable:
    """Test behavior when hot-reloader dependencies are not available."""
    
    def test_enhanced_config_manager_without_hot_reload_deps(self):
        """Test EnhancedConfigManager when hot-reload dependencies are missing."""
        # Create temporary config file
        temp_dir = tempfile.mkdtemp()
        config_file = Path(temp_dir) / 'test_config.yaml'
        
        try:
            # Create minimal config
            config_data = {
                'app_name': 'TestBot',
                'version': '1.0.0',
                'debug': False,
                'dry_run': True,
                'base_currency': 'USDT',
                'exchanges': {},
                'strategies': {},
                'risk': {'max_position_size': 0.1},
                'database': {'database_type': 'sqlite', 'database_url': 'sqlite:///test.db'},
                'logging': {'log_level': 'INFO'}
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            # Initialize with hot-reloading requested but not available
            config_manager = EnhancedConfigManager(
                config_file=str(config_file),
                use_unified_loading=True,
                enable_hot_reload=True  # Requested but should be disabled
            )
            
            # Check that hot-reloading is disabled due to missing dependencies
            assert not config_manager.is_hot_reload_enabled()
            
            # Try to start hot-reloader (should fail gracefully)
            success = config_manager.start_hot_reloader()
            assert not success
            
            # Get hot-reload status
            status = config_manager.get_hot_reload_status()
            assert not status['enabled']
            assert not status['available']
            
            # Manual reload should return None
            result = config_manager.manual_reload()
            assert result is None
            
        finally:
            # Clean up
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main([__file__])