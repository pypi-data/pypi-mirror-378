"""
Unit tests for orchestration configuration management components.
"""

import pytest
import yaml
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

from src.orchestration.config_manager import (
    ConfigurationManager, ConfigValidator, ConfigMigrator,
    ConfigTemplateManager, ConfigAuditLogger
)
from src.orchestration.config import (
    OrchestratorConfig, AllocationConfig, RiskConfig, MonitoringConfig,
    OptimizationConfig, StrategyConfig, AllocationMethod, RebalanceFrequency
)
from src.orchestration.exceptions import ConfigurationError, ValidationError


class TestConfigurationManager:
    """Test the main configuration manager."""
    
    @pytest.fixture
    def config_manager(self):
        """Create configuration manager instance."""
        return ConfigurationManager()
    
    @pytest.fixture
    def sample_config_dict(self):
        """Create sample configuration dictionary."""
        return {
            "orchestrator": {
                "max_concurrent_strategies": 10,
                "enable_dynamic_allocation": True,
                "allocation": {
                    "method": "performance_based",
                    "rebalance_frequency": "daily",
                    "min_allocation": 0.01,
                    "max_allocation": 0.25
                },
                "risk": {
                    "max_portfolio_drawdown": 0.10,
                    "max_strategy_correlation": 0.80,
                    "position_size_limit": 0.05
                },
                "monitoring": {
                    "performance_tracking": True,
                    "alert_thresholds": {
                        "drawdown": 0.05,
                        "correlation": 0.75
                    }
                },
                "strategies": [
                    {
                        "type": "MovingAverageStrategy",
                        "name": "ma_short",
                        "enabled": True,
                        "parameters": {
                            "short_period": 10,
                            "long_period": 20
                        }
                    }
                ]
            }
        }
    
    @pytest.fixture
    def sample_config_file(self, sample_config_dict):
        """Create temporary configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_config_dict, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        os.unlink(temp_file)
    
    def test_initialization(self, config_manager):
        """Test configuration manager initialization."""
        assert isinstance(config_manager.validator, ConfigValidator)
        assert isinstance(config_manager.migrator, ConfigMigrator)
        assert isinstance(config_manager.template_manager, ConfigTemplateManager)
        assert isinstance(config_manager.audit_logger, ConfigAuditLogger)
        assert config_manager.current_config is None
    
    def test_load_config_from_file(self, config_manager, sample_config_file):
        """Test loading configuration from file."""
        config = config_manager.load_config(sample_config_file)
        
        assert isinstance(config, OrchestratorConfig)
        assert config.max_concurrent_strategies == 10
        assert config.enable_dynamic_allocation is True
        assert len(config.strategies) == 1
        assert config.strategies[0].name == "ma_short"
    
    def test_load_config_from_dict(self, config_manager, sample_config_dict):
        """Test loading configuration from dictionary."""
        config = config_manager.load_config_from_dict(sample_config_dict)
        
        assert isinstance(config, OrchestratorConfig)
        assert config.max_concurrent_strategies == 10
        assert config.allocation.method == AllocationMethod.PERFORMANCE_BASED
    
    def test_load_invalid_config_file(self, config_manager):
        """Test loading invalid configuration file."""
        with pytest.raises(ConfigurationError):
            config_manager.load_config("nonexistent_file.yaml")
    
    def test_save_config(self, config_manager, sample_config_dict):
        """Test saving configuration to file."""
        config = config_manager.load_config_from_dict(sample_config_dict)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            config_manager.save_config(config, temp_file)
            
            # Verify file was created and contains valid YAML
            assert os.path.exists(temp_file)
            with open(temp_file, 'r') as f:
                loaded_data = yaml.safe_load(f)
                assert "orchestrator" in loaded_data
        finally:
            os.unlink(temp_file)
    
    def test_validate_config(self, config_manager, sample_config_dict):
        """Test configuration validation."""
        config = config_manager.load_config_from_dict(sample_config_dict)
        
        # Should not raise any exceptions for valid config
        config_manager.validate_config(config)
    
    def test_validate_invalid_config(self, config_manager):
        """Test validation of invalid configuration."""
        invalid_config_dict = {
            "orchestrator": {
                "allocation": {
                    "min_allocation": 0.5,  # Invalid: min > max
                    "max_allocation": 0.3
                }
            }
        }
        
        with pytest.raises(ValidationError):
            config = config_manager.load_config_from_dict(invalid_config_dict)
            config_manager.validate_config(config)
    
    def test_update_config(self, config_manager, sample_config_dict):
        """Test configuration updates."""
        config = config_manager.load_config_from_dict(sample_config_dict)
        config_manager.current_config = config
        
        updates = {
            "allocation.rebalance_frequency": "weekly",
            "risk.max_portfolio_drawdown": 0.15
        }
        
        updated_config = config_manager.update_config(updates)
        
        assert updated_config.allocation.rebalance_frequency == RebalanceFrequency.WEEKLY
        assert updated_config.risk.max_portfolio_drawdown == 0.15
    
    def test_get_config_template(self, config_manager):
        """Test configuration template retrieval."""
        with patch.object(config_manager.template_manager, 'get_template') as mock_get:
            mock_get.return_value = {"orchestrator": {"template": "data"}}
            
            template = config_manager.get_config_template("development")
            
            assert template == {"orchestrator": {"template": "data"}}
            mock_get.assert_called_once_with("development")


class TestConfigValidator:
    """Test configuration validation component."""
    
    @pytest.fixture
    def validator(self):
        """Create config validator."""
        return ConfigValidator()
    
    def test_validate_orchestrator_config(self, validator):
        """Test orchestrator configuration validation."""
        config = OrchestratorConfig(
            max_concurrent_strategies=10,
            enable_dynamic_allocation=True
        )
        
        errors = validator.validate_orchestrator_config(config)
        assert len(errors) == 0
    
    def test_validate_invalid_orchestrator_config(self, validator):
        """Test invalid orchestrator configuration validation."""
        config = OrchestratorConfig(
            max_concurrent_strategies=-1,  # Invalid: negative value
            enable_dynamic_allocation=True
        )
        
        errors = validator.validate_orchestrator_config(config)
        assert len(errors) > 0
        assert any("max_concurrent_strategies" in error for error in errors)
    
    def test_validate_allocation_config(self, validator):
        """Test allocation configuration validation."""
        config = AllocationConfig(
            method=AllocationMethod.EQUAL_WEIGHT,
            min_allocation=0.01,
            max_allocation=0.25
        )
        
        errors = validator.validate_allocation_config(config)
        assert len(errors) == 0
    
    def test_validate_invalid_allocation_config(self, validator):
        """Test invalid allocation configuration validation."""
        config = AllocationConfig(
            method=AllocationMethod.EQUAL_WEIGHT,
            min_allocation=0.5,  # Invalid: min > max
            max_allocation=0.3
        )
        
        errors = validator.validate_allocation_config(config)
        assert len(errors) > 0
        assert any("min_allocation" in error and "max_allocation" in error for error in errors)
    
    def test_validate_risk_config(self, validator):
        """Test risk configuration validation."""
        config = RiskConfig(
            max_portfolio_drawdown=0.10,
            max_strategy_correlation=0.80,
            position_size_limit=0.05
        )
        
        errors = validator.validate_risk_config(config)
        assert len(errors) == 0
    
    def test_validate_invalid_risk_config(self, validator):
        """Test invalid risk configuration validation."""
        config = RiskConfig(
            max_portfolio_drawdown=1.5,  # Invalid: > 1.0
            max_strategy_correlation=0.80,
            position_size_limit=-0.05  # Invalid: negative
        )
        
        errors = validator.validate_risk_config(config)
        assert len(errors) >= 2
    
    def test_validate_strategy_config(self, validator):
        """Test strategy configuration validation."""
        config = StrategyConfig(
            type="MovingAverageStrategy",
            name="ma_test",
            enabled=True,
            parameters={"short_period": 10, "long_period": 20}
        )
        
        errors = validator.validate_strategy_config(config)
        assert len(errors) == 0
    
    def test_validate_invalid_strategy_config(self, validator):
        """Test invalid strategy configuration validation."""
        config = StrategyConfig(
            type="",  # Invalid: empty type
            name="",  # Invalid: empty name
            enabled=True,
            parameters={}
        )
        
        errors = validator.validate_strategy_config(config)
        assert len(errors) >= 2
    
    def test_validate_strategy_parameters(self, validator):
        """Test strategy parameter validation."""
        # Mock strategy class with parameter requirements
        with patch.object(validator, '_get_strategy_class') as mock_get_class:
            mock_strategy_class = Mock()
            mock_strategy_class.get_required_parameters.return_value = ["short_period", "long_period"]
            mock_strategy_class.get_parameter_constraints.return_value = {
                "short_period": {"type": int, "min": 1, "max": 100},
                "long_period": {"type": int, "min": 1, "max": 200}
            }
            mock_get_class.return_value = mock_strategy_class
            
            # Valid parameters
            errors = validator.validate_strategy_parameters(
                "MovingAverageStrategy",
                {"short_period": 10, "long_period": 20}
            )
            assert len(errors) == 0
            
            # Invalid parameters
            errors = validator.validate_strategy_parameters(
                "MovingAverageStrategy",
                {"short_period": -5, "long_period": 300}  # Out of range
            )
            assert len(errors) >= 2


class TestConfigMigrator:
    """Test configuration migration component."""
    
    @pytest.fixture
    def migrator(self):
        """Create config migrator."""
        return ConfigMigrator()
    
    def test_get_config_version(self, migrator):
        """Test configuration version detection."""
        config_v1 = {"version": "1.0", "orchestrator": {}}
        config_v2 = {"version": "2.0", "orchestrator": {}}
        config_no_version = {"orchestrator": {}}
        
        assert migrator.get_config_version(config_v1) == "1.0"
        assert migrator.get_config_version(config_v2) == "2.0"
        assert migrator.get_config_version(config_no_version) == "1.0"  # Default
    
    def test_needs_migration(self, migrator):
        """Test migration need detection."""
        config_v1 = {"version": "1.0", "orchestrator": {}}
        config_v2 = {"version": "2.0", "orchestrator": {}}
        
        assert migrator.needs_migration(config_v1) is True
        assert migrator.needs_migration(config_v2) is False
    
    def test_migrate_config(self, migrator):
        """Test configuration migration."""
        old_config = {
            "version": "1.0",
            "orchestrator": {
                "allocation_method": "equal_weight",  # Old format
                "rebalance_interval": "daily"  # Old format
            }
        }
        
        with patch.object(migrator, '_migrate_v1_to_v2') as mock_migrate:
            mock_migrate.return_value = {
                "version": "2.0",
                "orchestrator": {
                    "allocation": {
                        "method": "equal_weight",  # New format
                        "rebalance_frequency": "daily"  # New format
                    }
                }
            }
            
            migrated_config = migrator.migrate_config(old_config)
            
            assert migrated_config["version"] == "2.0"
            assert "allocation" in migrated_config["orchestrator"]
            mock_migrate.assert_called_once_with(old_config)
    
    def test_create_backup(self, migrator):
        """Test configuration backup creation."""
        config = {"version": "1.0", "orchestrator": {}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            original_file = f.name
            yaml.dump(config, f)
        
        try:
            backup_file = migrator.create_backup(original_file)
            
            assert os.path.exists(backup_file)
            assert backup_file.endswith('.backup')
            
            # Verify backup content
            with open(backup_file, 'r') as f:
                backup_data = yaml.safe_load(f)
                assert backup_data == config
        finally:
            os.unlink(original_file)
            if os.path.exists(backup_file):
                os.unlink(backup_file)


class TestConfigTemplateManager:
    """Test configuration template management component."""
    
    @pytest.fixture
    def template_manager(self):
        """Create template manager."""
        return ConfigTemplateManager()
    
    def test_get_available_templates(self, template_manager):
        """Test available templates listing."""
        with patch.object(template_manager, '_scan_template_directory') as mock_scan:
            mock_scan.return_value = ["development", "production", "minimal"]
            
            templates = template_manager.get_available_templates()
            
            assert len(templates) == 3
            assert "development" in templates
            assert "production" in templates
            assert "minimal" in templates
    
    def test_get_template(self, template_manager):
        """Test template retrieval."""
        template_data = {
            "orchestrator": {
                "max_concurrent_strategies": 5,
                "allocation": {"method": "equal_weight"}
            }
        }
        
        with patch.object(template_manager, '_load_template_file') as mock_load:
            mock_load.return_value = template_data
            
            template = template_manager.get_template("development")
            
            assert template == template_data
            mock_load.assert_called_once_with("development")
    
    def test_create_template(self, template_manager):
        """Test template creation."""
        config = OrchestratorConfig(
            max_concurrent_strategies=10,
            enable_dynamic_allocation=True
        )
        template_name = "custom_template"
        
        with patch.object(template_manager, '_save_template_file') as mock_save:
            template_manager.create_template(config, template_name)
            
            mock_save.assert_called_once()
            args, kwargs = mock_save.call_args
            assert args[0] == template_name
            assert isinstance(args[1], dict)
    
    def test_validate_template(self, template_manager):
        """Test template validation."""
        valid_template = {
            "orchestrator": {
                "max_concurrent_strategies": 10,
                "allocation": {"method": "equal_weight"}
            }
        }
        
        invalid_template = {
            "orchestrator": {
                "max_concurrent_strategies": -1  # Invalid
            }
        }
        
        with patch.object(template_manager, 'validator') as mock_validator:
            mock_validator.validate_template.return_value = []
            
            # Valid template
            errors = template_manager.validate_template(valid_template)
            assert len(errors) == 0
            
            # Invalid template
            mock_validator.validate_template.return_value = ["Invalid max_concurrent_strategies"]
            errors = template_manager.validate_template(invalid_template)
            assert len(errors) > 0


class TestConfigAuditLogger:
    """Test configuration audit logging component."""
    
    @pytest.fixture
    def audit_logger(self):
        """Create audit logger."""
        return ConfigAuditLogger()
    
    def test_log_config_change(self, audit_logger):
        """Test configuration change logging."""
        old_config = {"orchestrator": {"max_concurrent_strategies": 5}}
        new_config = {"orchestrator": {"max_concurrent_strategies": 10}}
        user = "test_user"
        reason = "Performance optimization"
        
        with patch.object(audit_logger, '_write_audit_log') as mock_write:
            audit_logger.log_config_change(old_config, new_config, user, reason)
            
            mock_write.assert_called_once()
            args, kwargs = mock_write.call_args
            log_entry = args[0]
            
            assert log_entry["action"] == "config_change"
            assert log_entry["user"] == user
            assert log_entry["reason"] == reason
            assert "changes" in log_entry
    
    def test_log_config_load(self, audit_logger):
        """Test configuration load logging."""
        config_file = "/path/to/config.yaml"
        user = "test_user"
        
        with patch.object(audit_logger, '_write_audit_log') as mock_write:
            audit_logger.log_config_load(config_file, user)
            
            mock_write.assert_called_once()
            args, kwargs = mock_write.call_args
            log_entry = args[0]
            
            assert log_entry["action"] == "config_load"
            assert log_entry["config_file"] == config_file
            assert log_entry["user"] == user
    
    def test_log_validation_error(self, audit_logger):
        """Test validation error logging."""
        config_file = "/path/to/config.yaml"
        errors = ["Invalid allocation method", "Missing required parameter"]
        
        with patch.object(audit_logger, '_write_audit_log') as mock_write:
            audit_logger.log_validation_error(config_file, errors)
            
            mock_write.assert_called_once()
            args, kwargs = mock_write.call_args
            log_entry = args[0]
            
            assert log_entry["action"] == "validation_error"
            assert log_entry["config_file"] == config_file
            assert log_entry["errors"] == errors
    
    def test_get_audit_history(self, audit_logger):
        """Test audit history retrieval."""
        mock_history = [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "config_change",
                "user": "user1"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "action": "config_load",
                "user": "user2"
            }
        ]
        
        with patch.object(audit_logger, '_read_audit_log') as mock_read:
            mock_read.return_value = mock_history
            
            history = audit_logger.get_audit_history(limit=10)
            
            assert len(history) == 2
            assert history[0]["action"] == "config_change"
            assert history[1]["action"] == "config_load"
    
    def test_filter_audit_history(self, audit_logger):
        """Test audit history filtering."""
        mock_history = [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "config_change",
                "user": "user1"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "action": "config_load",
                "user": "user1"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "action": "config_change",
                "user": "user2"
            }
        ]
        
        with patch.object(audit_logger, '_read_audit_log') as mock_read:
            mock_read.return_value = mock_history
            
            # Filter by user
            filtered = audit_logger.get_audit_history(user_filter="user1")
            assert len(filtered) == 2
            assert all(entry["user"] == "user1" for entry in filtered)
            
            # Filter by action
            filtered = audit_logger.get_audit_history(action_filter="config_change")
            assert len(filtered) == 2
            assert all(entry["action"] == "config_change" for entry in filtered)