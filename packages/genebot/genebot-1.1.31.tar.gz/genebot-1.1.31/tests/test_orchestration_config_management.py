"""
Tests for orchestration configuration management system.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.orchestration.config import OrchestratorConfig, StrategyConfig, create_default_config
from src.orchestration.config_manager import ConfigurationManager, ConfigurationError
from src.orchestration.config_schema import ConfigSchemaValidator, validate_config_with_schema
from src.orchestration.config_migration import (
    ConfigMigrationManager, Migration_1_0_to_1_1, Migration_1_1_to_1_2,
    migrate_config_file, MigrationError
)


class TestOrchestratorConfig:
    """Test orchestrator configuration models."""
    
    def test_create_default_config(self):
        """Test creating default configuration."""
        config = create_default_config()
        
        assert isinstance(config, OrchestratorConfig)
        assert len(config.strategies) >= 2
        assert config.allocation.method.value == "performance_based"
        assert config.risk.max_portfolio_drawdown == 0.10
        
        # Validate configuration
        errors = config.validate()
        assert len(errors) == 0
    
    def test_config_from_dict(self):
        """Test creating configuration from dictionary."""
        config_data = {
            "orchestrator": {
                "allocation": {
                    "method": "equal_weight",
                    "rebalance_frequency": "daily",
                    "min_allocation": 0.05,
                    "max_allocation": 0.30
                },
                "risk": {
                    "max_portfolio_drawdown": 0.15,
                    "max_strategy_correlation": 0.85,
                    "position_size_limit": 0.08,
                    "stop_loss_threshold": 0.03
                },
                "monitoring": {
                    "performance_tracking": True,
                    "real_time_metrics": False
                },
                "optimization": {
                    "optimization_frequency": "weekly",
                    "lookback_period": 30,
                    "optimization_method": "sharpe_ratio"
                },
                "strategies": [
                    {
                        "type": "MovingAverageStrategy",
                        "name": "test_ma",
                        "enabled": True,
                        "allocation_weight": 1.0,
                        "parameters": {"short_period": 10, "long_period": 20}
                    }
                ]
            }
        }
        
        config = OrchestratorConfig.from_dict(config_data)
        
        assert config.allocation.method.value == "equal_weight"
        assert config.risk.max_portfolio_drawdown == 0.15
        assert len(config.strategies) == 1
        assert config.strategies[0].name == "test_ma"
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid allocation
        config = create_default_config()
        config.allocation.min_allocation = 0.8
        config.allocation.max_allocation = 0.2
        
        errors = config.validate()
        assert len(errors) > 0
        assert any("min_allocation must be less than max_allocation" in error for error in errors)
    
    def test_config_to_yaml(self):
        """Test saving configuration to YAML."""
        config = create_default_config()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config.save_to_yaml(f.name)
            
            # Load and verify
            with open(f.name, 'r') as read_f:
                loaded_data = yaml.safe_load(read_f)
            
            assert "orchestrator" in loaded_data
            assert "allocation" in loaded_data["orchestrator"]
            assert "strategies" in loaded_data["orchestrator"]
        
        Path(f.name).unlink()


class TestConfigurationManager:
    """Test configuration manager."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigurationManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_config(self):
        """Test loading configuration from file."""
        # Create test config
        config = create_default_config()
        config_path = Path(self.temp_dir) / "test_config.yaml"
        config.save_to_yaml(config_path)
        
        # Load config
        loaded_config = self.config_manager.load_config(config_path)
        
        assert isinstance(loaded_config, OrchestratorConfig)
        assert len(loaded_config.strategies) == len(config.strategies)
        assert loaded_config.allocation.method == config.allocation.method
    
    def test_load_invalid_config(self):
        """Test loading invalid configuration."""
        # Create invalid config file
        config_path = Path(self.temp_dir) / "invalid_config.yaml"
        with open(config_path, 'w') as f:
            f.write("invalid: yaml: content:")
        
        with pytest.raises(ConfigurationError):
            self.config_manager.load_config(config_path)
    
    def test_save_config(self):
        """Test saving configuration."""
        config = create_default_config()
        
        saved_path = self.config_manager.save_config(config)
        
        assert saved_path.exists()
        
        # Verify saved config can be loaded
        loaded_config = self.config_manager.load_config(saved_path)
        assert len(loaded_config.strategies) == len(config.strategies)
    
    def test_validate_config(self):
        """Test configuration validation."""
        # Create valid config
        config = create_default_config()
        config_path = Path(self.temp_dir) / "valid_config.yaml"
        config.save_to_yaml(config_path)
        
        is_valid, errors = self.config_manager.validate_config(config_path)
        assert is_valid
        assert len(errors) == 0
        
        # Create invalid config
        invalid_config_path = Path(self.temp_dir) / "invalid_config.yaml"
        with open(invalid_config_path, 'w') as f:
            yaml.dump({"orchestrator": {"invalid": "config"}}, f)
        
        is_valid, errors = self.config_manager.validate_config(invalid_config_path)
        assert not is_valid
        assert len(errors) > 0
    
    def test_create_from_template(self):
        """Test creating configuration from template."""
        # Create a template
        template_config = create_default_config()
        template_path = self.config_manager.templates_dir / "test_template.yaml"
        template_config.save_to_yaml(template_path)
        
        # Create config from template
        output_path = Path(self.temp_dir) / "from_template.yaml"
        overrides = {
            "orchestrator": {
                "max_concurrent_strategies": 15,
                "allocation": {
                    "method": "risk_parity"
                }
            }
        }
        
        created_config = self.config_manager.create_from_template(
            "test_template", output_path, overrides
        )
        
        assert created_config.max_concurrent_strategies == 15
        assert created_config.allocation.method.value == "risk_parity"
        assert output_path.exists()
    
    def test_list_templates(self):
        """Test listing available templates."""
        # Create test templates
        template1_path = self.config_manager.templates_dir / "template1.yaml"
        template2_path = self.config_manager.templates_dir / "template2.yaml"
        
        config = create_default_config()
        config.save_to_yaml(template1_path)
        config.save_to_yaml(template2_path)
        
        templates = self.config_manager.list_templates()
        
        assert "template1" in templates
        assert "template2" in templates
        assert len(templates) >= 2
    
    def test_create_template(self):
        """Test creating template from configuration."""
        config = create_default_config()
        
        template_path = self.config_manager.create_template(
            "new_template", config, "Test template description"
        )
        
        assert template_path.exists()
        
        # Verify template content
        with open(template_path, 'r') as f:
            template_data = yaml.safe_load(f)
        
        assert "_template_metadata" in template_data
        assert template_data["_template_metadata"]["name"] == "new_template"
        assert "orchestrator" in template_data
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        # Create and save config
        config = create_default_config()
        config_path = self.config_manager.save_config(config, "test_config.yaml")
        
        # Modify config
        config.max_concurrent_strategies = 25
        self.config_manager.save_config(config, config_path)
        
        # List backups
        backups = self.config_manager.list_backups()
        assert len(backups) >= 1
        
        # Restore backup
        backup_name = backups[0]["name"]
        restored_path = self.config_manager.restore_backup(backup_name, config_path)
        
        # Verify restoration
        restored_config = self.config_manager.load_config(restored_path)
        assert restored_config.max_concurrent_strategies != 25  # Should be original value


class TestConfigSchemaValidator:
    """Test configuration schema validation."""
    
    def test_schema_validation_valid_config(self):
        """Test schema validation with valid configuration."""
        config = create_default_config()
        config_data = config.to_dict()
        
        validator = ConfigSchemaValidator()
        
        if validator.schema_available:
            errors = validator.validate(config_data)
            assert len(errors) == 0
        else:
            # Skip test if jsonschema not available
            pytest.skip("jsonschema package not available")
    
    def test_schema_validation_invalid_config(self):
        """Test schema validation with invalid configuration."""
        invalid_config = {
            "orchestrator": {
                "allocation": {
                    "method": "invalid_method",  # Invalid enum value
                    "min_allocation": 1.5,  # Invalid range
                    "max_allocation": -0.1   # Invalid range
                },
                "strategies": []  # Empty array (violates minItems)
            }
        }
        
        validator = ConfigSchemaValidator()
        
        if validator.schema_available:
            errors = validator.validate(invalid_config)
            assert len(errors) > 0
        else:
            pytest.skip("jsonschema package not available")
    
    def test_validate_config_with_schema_function(self):
        """Test standalone validation function."""
        config = create_default_config()
        config_data = config.to_dict()
        
        errors = validate_config_with_schema(config_data)
        
        # Should either pass validation or skip due to missing jsonschema
        assert isinstance(errors, list)


class TestConfigMigration:
    """Test configuration migration system."""
    
    def test_migration_1_0_to_1_1(self):
        """Test migration from version 1.0 to 1.1."""
        # Create 1.0 config (without monitoring)
        config_1_0 = {
            "orchestrator": {
                "allocation": {
                    "method": "equal_weight",
                    "rebalance_frequency": "daily",
                    "min_allocation": 0.1,
                    "max_allocation": 0.3
                },
                "risk": {
                    "max_portfolio_drawdown": 0.15,
                    "max_strategy_correlation": 0.8,
                    "position_size_limit": 0.05,
                    "stop_loss_threshold": 0.02
                },
                "strategies": [
                    {
                        "type": "MovingAverageStrategy",
                        "name": "test_ma",
                        "enabled": True
                    }
                ]
            }
        }
        
        migration = Migration_1_0_to_1_1()
        migrated = migration.migrate(config_1_0)
        
        assert "monitoring" in migrated["orchestrator"]
        assert migrated["orchestrator"]["monitoring"]["performance_tracking"] is True
        assert "_version" in migrated
        assert migrated["_version"] == "1.1"
    
    def test_migration_1_1_to_1_2(self):
        """Test migration from version 1.1 to 1.2."""
        # Create 1.1 config (with monitoring, without optimization)
        config_1_1 = {
            "orchestrator": {
                "allocation": {
                    "method": "performance_based",
                    "rebalance_frequency": "daily",
                    "min_allocation": 0.05,
                    "max_allocation": 0.25
                },
                "risk": {
                    "max_portfolio_drawdown": 0.1,
                    "max_strategy_correlation": 0.8,
                    "position_size_limit": 0.05,
                    "stop_loss_threshold": 0.02
                },
                "monitoring": {
                    "performance_tracking": True,
                    "real_time_metrics": True
                },
                "strategies": [
                    {
                        "type": "RSIStrategy",
                        "name": "test_rsi",
                        "enabled": True
                    }
                ]
            }
        }
        
        migration = Migration_1_1_to_1_2()
        migrated = migration.migrate(config_1_1)
        
        assert "optimization" in migrated["orchestrator"]
        assert "rebalance_threshold" in migrated["orchestrator"]["allocation"]
        assert "performance_thresholds" in migrated["orchestrator"]["strategies"][0]
        assert migrated["_version"] == "1.2"
    
    def test_migration_manager(self):
        """Test configuration migration manager."""
        manager = ConfigMigrationManager()
        
        # Test version detection
        config_1_0 = {"orchestrator": {"allocation": {}, "risk": {}, "strategies": []}}
        assert manager.detect_version(config_1_0) == "1.0"
        
        config_1_1 = {"orchestrator": {"monitoring": {}, "allocation": {}, "risk": {}, "strategies": []}}
        assert manager.detect_version(config_1_1) == "1.1"
        
        config_1_2 = {"orchestrator": {"optimization": {}, "monitoring": {}, "allocation": {"rebalance_threshold": 0.05}, "risk": {}, "strategies": []}}
        assert manager.detect_version(config_1_2) == "1.2"
        
        # Test migration path
        path = manager.get_migration_path("1.0", "1.2")
        assert path == ["1.0", "1.1"]
        
        # Test full migration
        config_1_0 = {
            "orchestrator": {
                "allocation": {
                    "method": "equal_weight",
                    "rebalance_frequency": "daily",
                    "min_allocation": 0.1,
                    "max_allocation": 0.3
                },
                "risk": {
                    "max_portfolio_drawdown": 0.15,
                    "max_strategy_correlation": 0.8,
                    "position_size_limit": 0.05,
                    "stop_loss_threshold": 0.02
                },
                "strategies": [{"type": "MovingAverageStrategy", "name": "test", "enabled": True}]
            }
        }
        
        migrated = manager.migrate(config_1_0, "1.0", "1.2")
        
        assert migrated["_version"] == "1.2"
        assert "monitoring" in migrated["orchestrator"]
        assert "optimization" in migrated["orchestrator"]
        assert "rebalance_threshold" in migrated["orchestrator"]["allocation"]
    
    def test_migration_report(self):
        """Test migration report generation."""
        manager = ConfigMigrationManager()
        
        config_1_0 = {"orchestrator": {"allocation": {}, "risk": {}, "strategies": []}}
        
        report = manager.create_migration_report(config_1_0)
        
        assert report["current_version"] == "1.0"
        assert report["target_version"] == "1.2"
        assert report["migration_needed"] is True
        assert len(report["migration_path"]) > 0
        assert len(report["estimated_changes"]) > 0
    
    def test_migrate_config_file(self):
        """Test migrating configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_1_0 = {
                "orchestrator": {
                    "allocation": {
                        "method": "equal_weight",
                        "rebalance_frequency": "daily",
                        "min_allocation": 0.1,
                        "max_allocation": 0.3
                    },
                    "risk": {
                        "max_portfolio_drawdown": 0.15,
                        "max_strategy_correlation": 0.8,
                        "position_size_limit": 0.05,
                        "stop_loss_threshold": 0.02
                    },
                    "strategies": [{"type": "MovingAverageStrategy", "name": "test", "enabled": True}]
                }
            }
            
            yaml.dump(config_1_0, f, default_flow_style=False)
            config_path = Path(f.name)
        
        try:
            migrated_path = migrate_config_file(config_path, "1.2")
            
            assert migrated_path.exists()
            assert migrated_path != config_path
            
            # Verify migrated content
            with open(migrated_path, 'r') as f:
                migrated_data = yaml.safe_load(f)
            
            assert migrated_data["_version"] == "1.2"
            assert "monitoring" in migrated_data["orchestrator"]
            assert "optimization" in migrated_data["orchestrator"]
            
        finally:
            config_path.unlink(missing_ok=True)
            if 'migrated_path' in locals():
                migrated_path.unlink(missing_ok=True)


class TestConfigurationIntegration:
    """Integration tests for configuration management."""
    
    def test_end_to_end_config_workflow(self):
        """Test complete configuration workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigurationManager(temp_dir)
            
            # 1. Create configuration from template
            config = create_default_config()
            template_path = config_manager.create_template("test_template", config)
            
            # 2. Create new config from template with overrides
            overrides = {
                "orchestrator": {
                    "max_concurrent_strategies": 12,
                    "allocation": {"method": "risk_parity"}
                }
            }
            
            new_config = config_manager.create_from_template(
                "test_template", "new_config.yaml", overrides
            )
            
            # 3. Validate configuration
            is_valid, errors = config_manager.validate_config(
                Path(temp_dir) / "new_config.yaml"
            )
            if not is_valid:
                print(f"Validation errors: {errors}")
            assert is_valid
            assert len(errors) == 0
            
            # 4. Modify and save configuration
            new_config.risk.max_portfolio_drawdown = 0.12
            saved_path = config_manager.save_config(new_config)
            
            # 5. Reload and verify
            reloaded_config = config_manager.load_config(saved_path)
            assert reloaded_config.risk.max_portfolio_drawdown == 0.12
            assert reloaded_config.max_concurrent_strategies == 12
            assert reloaded_config.allocation.method.value == "risk_parity"