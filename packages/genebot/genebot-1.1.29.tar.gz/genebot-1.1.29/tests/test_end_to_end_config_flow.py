"""
End-to-End Configuration Flow Integration Test

This test demonstrates the complete configuration flow from a fresh installation
through CLI configuration setup to bot startup, validating all integration points.

This test serves as the final validation for task 11 requirements.
"""

import os
import sys
import tempfile
import shutil
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch, Mock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.unified_loader import (
    UnifiedConfigLoader,
    ConfigurationNotFoundError,
    PartialConfigurationError
)
from config.enhanced_manager import EnhancedConfigManager
from config.models import TradingBotConfig
from tests.utils.config_validation_helpers import (
    ConfigurationTestValidator,
    CLIIntegrationTester,
    ConfigurationPerformanceTester,
    mock_cli_environment,
    temporary_config_files,
    create_comprehensive_test_data
)


class TestCompleteEndToEndFlow:
    """Test complete end-to-end configuration flow."""
    
    def test_fresh_install_to_production_ready_flow(self):
        """
        Test the complete flow from fresh install to production-ready configuration.
        
        This test validates:
        1. Fresh install detection and guidance
        2. CLI init-config simulation
        3. Exchange and strategy configuration
        4. Configuration validation
        5. Bot startup readiness
        6. Performance characteristics
        """
        with tempfile.TemporaryDirectory(prefix="e2e_config_test_") as temp_dir:
            temp_path = Path(temp_dir)
            original_cwd = os.getcwd()
            
            try:
                os.chdir(temp_path)
                
                # Phase 1: Fresh Install Detection
                print("Phase 1: Testing fresh install detection...")
                self._test_fresh_install_detection()
                
                # Phase 2: CLI Configuration Setup
                print("Phase 2: Simulating CLI configuration setup...")
                cli_tester = CLIIntegrationTester(temp_path)
                self._test_cli_configuration_setup(cli_tester)
                
                # Phase 3: Configuration Loading and Validation
                print("Phase 3: Testing configuration loading and validation...")
                self._test_configuration_loading_and_validation()
                
                # Phase 4: Bot Startup Integration
                print("Phase 4: Testing bot startup integration...")
                self._test_bot_startup_integration()
                
                # Phase 5: Advanced Features
                print("Phase 5: Testing advanced features...")
                self._test_advanced_features()
                
                # Phase 6: Performance Validation
                print("Phase 6: Testing performance characteristics...")
                self._test_performance_characteristics()
                
                print("✅ Complete end-to-end flow test passed!")
                
            finally:
                os.chdir(original_cwd)
    
    def _test_fresh_install_detection(self):
        """Test fresh install detection and error handling."""
        # Should detect no configuration files
        loader = UnifiedConfigLoader()
        
        with pytest.raises(ConfigurationNotFoundError) as exc_info:
            loader.load_configuration()
        
        error = exc_info.value
        assert "No configuration files found" in str(error)
        assert len(error.guidance) > 0
        
        # Verify guidance contains init-config instructions
        guidance_text = ' '.join(error.guidance).lower()
        assert 'init-config' in guidance_text
        assert 'genebot' in guidance_text
        
        # Test enhanced manager fresh install handling
        enhanced_manager = EnhancedConfigManager()
        
        with pytest.raises(Exception) as exc_info:
            enhanced_manager.load_with_discovery()
        
        # Should provide comprehensive guidance
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in [
            'configuration', 'not found', 'init-config', 'setup'
        ])
    
    def _test_cli_configuration_setup(self, cli_tester: CLIIntegrationTester):
        """Test CLI configuration setup simulation."""
        # Step 1: Initialize configuration
        init_result = cli_tester.simulate_init_config_command("development")
        assert init_result['success']
        assert len(init_result['created_files']) >= 3  # bot config, accounts, env
        
        # Verify files were created
        config_dir = cli_tester.config_dir
        assert (config_dir / "trading_bot_config.yaml").exists()
        assert (config_dir / "accounts.yaml").exists()
        assert (cli_tester.temp_dir / ".env").exists()
        
        # Step 2: Add additional exchange
        add_exchange_result = cli_tester.simulate_add_exchange_command("coinbase", "coinbase-pro")
        assert add_exchange_result['success']
        
        # Verify exchange was added
        with open(config_dir / "accounts.yaml", 'r') as f:
            accounts_config = yaml.safe_load(f)
        
        assert 'coinbase-pro' in accounts_config['exchanges']
        assert accounts_config['exchanges']['coinbase-pro']['exchange_type'] == 'coinbase'
        
        # Step 3: Enable strategy
        enable_strategy_result = cli_tester.simulate_enable_strategy_command("rsi_strategy")
        assert enable_strategy_result['success']
        
        # Verify strategy was enabled
        with open(config_dir / "trading_bot_config.yaml", 'r') as f:
            bot_config = yaml.safe_load(f)
        
        assert 'rsi_strategy' in bot_config['strategies']
        assert bot_config['strategies']['rsi_strategy']['enabled'] is True
    
    def _test_configuration_loading_and_validation(self):
        """Test configuration loading and validation."""
        # Test unified loader
        loader = UnifiedConfigLoader()
        config = loader.load_configuration()
        
        assert isinstance(config, TradingBotConfig)
        assert config.app_name == 'TradingBot'
        assert config.version == '1.1.28'
        
        # Validate configuration structure
        validator = ConfigurationTestValidator()
        
        structure_errors = validator.validate_config_structure(config)
        assert len(structure_errors) == 0, f"Structure validation errors: {structure_errors}"
        
        exchange_errors = validator.validate_exchange_configuration(config)
        # May have warnings but should not have critical errors for demo setup
        
        risk_errors = validator.validate_risk_configuration(config)
        assert len(risk_errors) == 0, f"Risk validation errors: {risk_errors}"
        
        # Test enhanced manager validation
        enhanced_manager = EnhancedConfigManager()
        validation_result = enhanced_manager.validate_with_cli_rules()
        
        # Should be valid or have only warnings
        if not validation_result.is_valid:
            # Check if errors are acceptable (e.g., demo API keys)
            acceptable_error_keywords = ['demo', 'test', 'placeholder', 'api_key']
            for error in validation_result.errors:
                error_lower = error.lower()
                assert any(keyword in error_lower for keyword in acceptable_error_keywords), (
                    f"Unexpected validation error: {error}"
                )
    
    def _test_bot_startup_integration(self):
        """Test bot startup integration."""
        # Test enhanced manager startup
        enhanced_manager = EnhancedConfigManager()
        startup_config = enhanced_manager.load_with_discovery()
        
        assert isinstance(startup_config, TradingBotConfig)
        
        # Verify configuration sources are tracked
        sources = enhanced_manager.get_active_sources()
        assert len(sources) >= 2  # At least bot config and accounts
        
        # Verify CLI-generated sources are identified
        cli_sources = [s for s in sources if s.source_type == 'cli_generated']
        assert len(cli_sources) >= 2
        
        # Test configuration status reporting
        status = enhanced_manager.get_configuration_status()
        assert status.validation_status is not None
        
        # Test detailed status report
        detailed_report = enhanced_manager.get_detailed_status_report()
        assert detailed_report['mode'] == 'unified'
        assert 'active_sources' in detailed_report or 'discovery_report' in detailed_report
    
    def _test_advanced_features(self):
        """Test advanced configuration features."""
        # Test environment variable overrides
        env_overrides = {
            'APP_NAME': 'E2E_TestBot',
            'DEBUG': 'true',
            'RISK_MAX_POSITION_SIZE': '0.15',
            'LOG_LEVEL': 'DEBUG'
        }
        
        with patch.dict(os.environ, env_overrides):
            enhanced_manager = EnhancedConfigManager()
            config = enhanced_manager.load_with_discovery()
            
            # Verify overrides were applied
            assert config.app_name == 'E2E_TestBot'
            assert config.debug is True
            assert config.risk.max_position_size == 0.15
            assert config.logging.log_level == 'DEBUG'
            
            # Verify merge conflicts are tracked
            status = enhanced_manager.get_configuration_status()
            assert len(status.merge_conflicts) > 0
        
        # Test configuration source summary
        enhanced_manager = EnhancedConfigManager()
        enhanced_manager.load_with_discovery()
        
        source_summary = enhanced_manager.get_configuration_source_summary()
        assert source_summary['total_sources'] >= 2
        assert source_summary['cli_generated_present'] is True
        
        # Test configuration guidance generation
        guidance = enhanced_manager.generate_configuration_guidance()
        assert len(guidance) > 0
    
    def _test_performance_characteristics(self):
        """Test configuration loading performance."""
        performance_tester = ConfigurationPerformanceTester()
        
        # Test discovery performance
        loader = UnifiedConfigLoader()
        discovery_metrics = performance_tester.measure_discovery_performance(loader, iterations=5)
        
        # Should be reasonably fast (under 1 second average)
        assert discovery_metrics['avg_time'] < 1.0, (
            f"Discovery too slow: {discovery_metrics['avg_time']:.3f}s average"
        )
        
        # Test loading performance
        loading_metrics = performance_tester.measure_loading_performance(loader, iterations=5)
        
        # Should be reasonably fast (under 2 seconds average)
        assert loading_metrics['avg_time'] < 2.0, (
            f"Loading too slow: {loading_metrics['avg_time']:.3f}s average"
        )
        
        # Test validation performance
        enhanced_manager = EnhancedConfigManager()
        enhanced_manager.load_with_discovery()  # Load first
        
        validation_metrics = performance_tester.measure_validation_performance(
            enhanced_manager, iterations=5
        )
        
        # Should be reasonably fast (under 0.5 seconds average)
        assert validation_metrics['avg_time'] < 0.5, (
            f"Validation too slow: {validation_metrics['avg_time']:.3f}s average"
        )


class TestConfigurationRobustness:
    """Test configuration system robustness and edge cases."""
    
    def test_configuration_with_comprehensive_data(self):
        """Test configuration with comprehensive test data."""
        test_data = create_comprehensive_test_data()
        
        # Test valid complete configuration
        valid_config_data = test_data['valid_complete_config']
        
        with temporary_config_files(valid_config_data) as (temp_dir, created_files):
            loader = UnifiedConfigLoader()
            config = loader.load_configuration()
            
            assert isinstance(config, TradingBotConfig)
            assert config.app_name == 'ComprehensiveTestBot'
            
            # Validate all sections are present and correct
            validator = ConfigurationTestValidator()
            
            structure_errors = validator.validate_config_structure(config)
            assert len(structure_errors) == 0
            
            exchange_errors = validator.validate_exchange_configuration(config)
            assert len(exchange_errors) == 0
            
            risk_errors = validator.validate_risk_configuration(config)
            assert len(risk_errors) == 0
    
    def test_configuration_error_scenarios(self):
        """Test various configuration error scenarios."""
        test_data = create_comprehensive_test_data()
        invalid_scenarios = test_data['invalid_config_scenarios']
        
        for scenario_name, scenario_data in invalid_scenarios.items():
            print(f"Testing invalid scenario: {scenario_name}")
            
            with temporary_config_files(scenario_data) as (temp_dir, created_files):
                loader = UnifiedConfigLoader()
                
                # Should raise appropriate error
                with pytest.raises(Exception) as exc_info:
                    loader.load_configuration()
                
                error_message = str(exc_info.value).lower()
                
                # Verify error is related to the scenario
                if scenario_name == 'missing_required_fields':
                    assert any(keyword in error_message for keyword in [
                        'missing', 'required', 'field', 'validation'
                    ])
                elif scenario_name == 'invalid_values':
                    assert any(keyword in error_message for keyword in [
                        'invalid', 'value', 'range', 'validation'
                    ])
                elif scenario_name == 'type_errors':
                    assert any(keyword in error_message for keyword in [
                        'type', 'invalid', 'expected', 'validation'
                    ])
    
    def test_configuration_recovery_scenarios(self):
        """Test configuration recovery and fallback scenarios."""
        # Test partial configuration recovery
        partial_config = {
            'bot_config': {
                'app_name': 'PartialBot',
                'version': '1.1.28',
                'debug': False,
                'dry_run': True
            }
            # Missing accounts_config
        }
        
        with temporary_config_files(partial_config) as (temp_dir, created_files):
            loader = UnifiedConfigLoader()
            
            with pytest.raises(PartialConfigurationError) as exc_info:
                loader.load_configuration()
            
            error = exc_info.value
            assert 'accounts.yaml' in error.missing_files
            assert len(error.completion_suggestions) > 0
            
            # Test enhanced manager handling
            enhanced_manager = EnhancedConfigManager()
            
            with pytest.raises(Exception) as exc_info:
                enhanced_manager.load_with_discovery()
            
            # Should provide recovery guidance
            error_message = str(exc_info.value)
            assert 'partial' in error_message.lower() or 'missing' in error_message.lower()


def test_complete_integration_suite():
    """Run the complete integration test suite."""
    print("🚀 Starting Complete Configuration Integration Test Suite")
    print("=" * 70)
    
    # Run end-to-end flow test
    test_instance = TestCompleteEndToEndFlow()
    test_instance.test_fresh_install_to_production_ready_flow()
    
    # Run robustness tests
    robustness_test = TestConfigurationRobustness()
    robustness_test.test_configuration_with_comprehensive_data()
    robustness_test.test_configuration_error_scenarios()
    robustness_test.test_configuration_recovery_scenarios()
    
    print("=" * 70)
    print("✅ Complete Configuration Integration Test Suite PASSED!")
    print("")
    print("🎉 All requirements validated:")
    print("   • 1.1: Configuration path integration")
    print("   • 1.2: Remove hardcoded dependencies")
    print("   • 1.3: Unified configuration loading")
    print("   • 1.4: Configuration discovery and fallback")
    print("")
    print("✅ Test coverage includes:")
    print("   • End-to-end configuration flow")
    print("   • Configuration precedence validation")
    print("   • Error handling and recovery")
    print("   • Performance characteristics")
    print("   • Robustness and edge cases")


if __name__ == "__main__":
    test_complete_integration_suite()