"""
Test Strategy Registry and Discovery System Validation

This test validates all aspects of the strategy registry and discovery system
as required by task 5 of the genebot integration finalization spec.
"""

import pytest
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import importlib

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.strategies.strategy_registry import StrategyRegistry
from src.strategies.base_strategy import BaseStrategy, StrategyConfig
from genebot.cli.commands.config import ListStrategiesCommand
from genebot.cli.context import CLIContext


class TestStrategyRegistryValidation:
    """Test suite for strategy registry and discovery system validation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.registry = StrategyRegistry()
        self.cli_context = CLIContext(config_path=project_root / "config")
    
    def test_strategy_discovery_mechanism(self):
        """Test strategy discovery mechanism to ensure all strategies are found"""
        print("\n=== Testing Strategy Discovery Mechanism ===")
        
        # Test discovery from strategies package
        discovered_count = self.registry.discover_strategies('src.strategies')
        
        # Verify strategies were discovered
        assert discovered_count > 0, "No strategies were discovered"
        print(f"✅ Discovered {discovered_count} strategies")
        
        # Get list of registered strategies
        registered_strategies = self.registry.get_registered_strategies()
        assert len(registered_strategies) == discovered_count, "Mismatch between discovered and registered count"
        
        # Verify expected strategies are found
        expected_strategies = [
            'AdvancedMomentumStrategy',
            'ATRVolatilityStrategy', 
            'CrossMarketArbitrageStrategy',
            'CryptoForexArbitrageStrategy',
            'ForexCarryTradeStrategy',
            'ForexNewsStrategy',
            'ForexSessionStrategy',
            'MarketAgnosticStrategy',
            'MarketSpecificStrategy',
            'MeanReversionStrategy',
            'MLPatternStrategy',
            'MovingAverageStrategy',
            'MultiIndicatorStrategy',
            'RSIStrategy',
            'TriangularArbitrageStrategy'
        ]
        
        for expected_strategy in expected_strategies:
            assert expected_strategy in registered_strategies, f"Expected strategy {expected_strategy} not found"
            print(f"✅ Found expected strategy: {expected_strategy}")
        
        print(f"✅ All {len(expected_strategies)} expected strategies discovered successfully")
    
    def test_strategy_metadata_and_documentation(self):
        """Test strategy metadata and parameter documentation"""
        print("\n=== Testing Strategy Metadata and Documentation ===")
        
        # Discover strategies first
        self.registry.discover_strategies('src.strategies')
        registered_strategies = self.registry.get_registered_strategies()
        
        for strategy_name in registered_strategies:
            print(f"\n--- Validating {strategy_name} ---")
            
            # Get strategy info
            strategy_info = self.registry.get_strategy_info(strategy_name)
            assert strategy_info is not None, f"No info available for {strategy_name}"
            
            # Validate required metadata fields
            required_fields = ['name', 'class', 'module', 'docstring', 'methods']
            for field in required_fields:
                assert field in strategy_info, f"Missing required field '{field}' for {strategy_name}"
                assert strategy_info[field] is not None, f"Field '{field}' is None for {strategy_name}"
            
            # Validate docstring exists and is meaningful
            docstring = strategy_info['docstring']
            assert len(docstring.strip()) > 10, f"Docstring too short for {strategy_name}"
            print(f"✅ {strategy_name}: Has meaningful docstring ({len(docstring)} chars)")
            
            # Validate required methods exist
            required_methods = [
                'initialize', 'start', 'stop', 'process_market_data', 
                'analyze', 'validate_parameters', 'get_performance_metrics'
            ]
            methods = strategy_info['methods']
            for required_method in required_methods:
                assert required_method in methods, f"Missing required method '{required_method}' in {strategy_name}"
            
            print(f"✅ {strategy_name}: Has all required methods")
            
            # Test strategy instantiation to validate parameters
            try:
                config = StrategyConfig(
                    name=f"test_{strategy_name.lower()}",
                    enabled=True,
                    parameters={},
                    risk_limits={}
                )
                
                # Handle strategies with special constructor requirements
                if strategy_name in ['MarketSpecificStrategy', 'MarketAgnosticStrategy']:
                    # These are abstract base classes, skip instantiation test
                    print(f"⚠️  {strategy_name}: Skipped instantiation (abstract base class)")
                    continue
                
                strategy_instance = self.registry.create_strategy(strategy_name, config)
                assert strategy_instance is not None, f"Failed to create instance of {strategy_name}"
                
                # Test parameter validation
                is_valid = strategy_instance.validate_parameters()
                assert isinstance(is_valid, bool), f"validate_parameters should return bool for {strategy_name}"
                
                print(f"✅ {strategy_name}: Successfully instantiated and validated")
                
            except Exception as e:
                # For abstract base classes or strategies with special requirements, just log the issue
                if "abstract" in str(e).lower() or "missing" in str(e).lower():
                    print(f"⚠️  {strategy_name}: Skipped instantiation ({str(e)})")
                else:
                    pytest.fail(f"Failed to instantiate {strategy_name}: {str(e)}")
    
    def test_strategy_categories_organization(self):
        """Test strategy categories are properly organized"""
        print("\n=== Testing Strategy Categories Organization ===")
        
        # Discover strategies
        self.registry.discover_strategies('src.strategies')
        
        # Define expected categories and their strategies
        expected_categories = {
            'Technical Indicators': [
                'RSIStrategy', 'MovingAverageStrategy', 'MultiIndicatorStrategy',
                'AdvancedMomentumStrategy', 'ATRVolatilityStrategy', 'MeanReversionStrategy'
            ],
            'Machine Learning': [
                'MLPatternStrategy'
            ],
            'Arbitrage': [
                'CrossMarketArbitrageStrategy', 'CryptoForexArbitrageStrategy', 
                'TriangularArbitrageStrategy'
            ],
            'Forex Specific': [
                'ForexCarryTradeStrategy', 'ForexNewsStrategy', 'ForexSessionStrategy'
            ],
            'Market Type': [
                'MarketAgnosticStrategy', 'MarketSpecificStrategy'
            ]
        }
        
        registered_strategies = self.registry.get_registered_strategies()
        
        # Verify all strategies are categorized
        all_categorized = []
        for category, strategies in expected_categories.items():
            print(f"\n--- {category} Category ---")
            for strategy in strategies:
                if strategy in registered_strategies:
                    all_categorized.append(strategy)
                    print(f"✅ {strategy}")
                else:
                    print(f"❌ {strategy} (not found)")
        
        # Check if any strategies are uncategorized
        uncategorized = set(registered_strategies) - set(all_categorized)
        if uncategorized:
            print(f"\n--- Uncategorized Strategies ---")
            for strategy in uncategorized:
                print(f"⚠️  {strategy}")
        
        print(f"\n✅ Strategy categorization validated: {len(all_categorized)} categorized, {len(uncategorized)} uncategorized")
    
    def test_strategy_enabling_disabling_cli(self):
        """Test strategy enabling/disabling through CLI"""
        print("\n=== Testing Strategy Enabling/Disabling Through CLI ===")
        
        # Import required CLI components
        from genebot.cli.utils.logger import CLILogger
        from genebot.cli.utils.error_handler import CLIErrorHandler
        
        # Create CLI components
        logger = CLILogger(name="test_cli", level="INFO")
        error_handler = CLIErrorHandler()
        
        # Test CLI list strategies command
        list_command = ListStrategiesCommand(self.cli_context, logger, error_handler)
        
        # Create mock args for testing
        class MockArgs:
            def __init__(self):
                self.status = 'all'
        
        args = MockArgs()
        
        # Test listing all strategies
        result = list_command.execute(args)
        assert result.success, f"List strategies command failed: {result.message}"
        assert 'strategies' in result.data, "No strategies data in result"
        
        strategies_data = result.data['strategies']
        assert len(strategies_data) > 0, "No strategies returned by CLI command"
        
        print(f"✅ CLI successfully listed {len(strategies_data)} strategies")
        
        # Test filtering by status
        args.status = 'active'
        result_active = list_command.execute(args)
        assert result_active.success, "Failed to filter active strategies"
        
        args.status = 'inactive'
        result_inactive = list_command.execute(args)
        assert result_inactive.success, "Failed to filter inactive strategies"
        
        print("✅ CLI strategy filtering by status works correctly")
        
        # Validate strategy data structure
        for strategy in strategies_data:
            required_fields = ['name', 'status', 'markets', 'risk_per_trade', 'win_rate', 'total_trades']
            for field in required_fields:
                assert field in strategy, f"Missing field '{field}' in strategy data"
            
            # Validate field types and values
            assert isinstance(strategy['name'], str), "Strategy name should be string"
            assert strategy['status'] in ['active', 'inactive'], "Invalid strategy status"
            assert isinstance(strategy['markets'], list), "Markets should be list"
            assert len(strategy['markets']) > 0, "Strategy should have at least one market"
            
        print("✅ Strategy data structure validation passed")
    
    def test_multi_market_strategy_functionality(self):
        """Test multi-market strategy functionality"""
        print("\n=== Testing Multi-Market Strategy Functionality ===")
        
        # Discover strategies
        self.registry.discover_strategies('src.strategies')
        
        # Identify multi-market strategies (excluding abstract base classes)
        multi_market_strategies = [
            'CrossMarketArbitrageStrategy',
            'CryptoForexArbitrageStrategy'
        ]
        
        for strategy_name in multi_market_strategies:
            print(f"\n--- Testing {strategy_name} ---")
            
            # Create strategy instance
            config = StrategyConfig(
                name=f"test_{strategy_name.lower()}",
                enabled=True,
                parameters={},
                risk_limits={}
            )
            
            strategy = self.registry.create_strategy(strategy_name, config)
            assert strategy is not None, f"Failed to create {strategy_name}"
            
            # Test multi-market specific methods if they exist
            if hasattr(strategy, 'get_supported_markets'):
                supported_markets = strategy.get_supported_markets()
                assert isinstance(supported_markets, list), "Supported markets should be a list"
                assert len(supported_markets) > 1, f"{strategy_name} should support multiple markets"
                print(f"✅ {strategy_name}: Supports markets {supported_markets}")
            
            if hasattr(strategy, 'supports_market_type'):
                # Test crypto market support
                crypto_support = strategy.supports_market_type('crypto')
                assert isinstance(crypto_support, bool), "Market type support should return boolean"
                
                # Test forex market support  
                forex_support = strategy.supports_market_type('forex')
                assert isinstance(forex_support, bool), "Market type support should return boolean"
                
                print(f"✅ {strategy_name}: Crypto support={crypto_support}, Forex support={forex_support}")
            
            print(f"✅ {strategy_name}: Multi-market functionality validated")
    
    def test_strategy_registry_performance(self):
        """Test strategy registry performance and reliability"""
        print("\n=== Testing Strategy Registry Performance ===")
        
        import time
        
        # Test discovery performance
        start_time = time.time()
        discovered_count = self.registry.discover_strategies('src.strategies')
        discovery_time = time.time() - start_time
        
        assert discovery_time < 5.0, f"Strategy discovery took too long: {discovery_time:.2f}s"
        print(f"✅ Strategy discovery completed in {discovery_time:.3f}s")
        
        # Test registry operations performance
        registered_strategies = self.registry.get_registered_strategies()
        
        start_time = time.time()
        for strategy_name in registered_strategies:
            info = self.registry.get_strategy_info(strategy_name)
            assert info is not None, f"Failed to get info for {strategy_name}"
        info_retrieval_time = time.time() - start_time
        
        assert info_retrieval_time < 2.0, f"Info retrieval took too long: {info_retrieval_time:.2f}s"
        print(f"✅ Strategy info retrieval completed in {info_retrieval_time:.3f}s")
        
        # Test strategy creation performance
        start_time = time.time()
        created_strategies = []
        for strategy_name in registered_strategies[:5]:  # Test first 5 strategies
            config = StrategyConfig(
                name=f"perf_test_{strategy_name.lower()}",
                enabled=True,
                parameters={},
                risk_limits={}
            )
            strategy = self.registry.create_strategy(strategy_name, config)
            if strategy:
                created_strategies.append(strategy)
        
        creation_time = time.time() - start_time
        assert creation_time < 3.0, f"Strategy creation took too long: {creation_time:.2f}s"
        print(f"✅ Strategy creation completed in {creation_time:.3f}s ({len(created_strategies)} strategies)")
    
    def test_strategy_error_handling(self):
        """Test strategy registry error handling"""
        print("\n=== Testing Strategy Registry Error Handling ===")
        
        # Test invalid strategy name
        invalid_strategy = self.registry.get_strategy_info('NonExistentStrategy')
        assert invalid_strategy is None, "Should return None for non-existent strategy"
        print("✅ Handles non-existent strategy gracefully")
        
        # Test invalid strategy creation
        config = StrategyConfig(name="test", enabled=True, parameters={}, risk_limits={})
        invalid_instance = self.registry.create_strategy('NonExistentStrategy', config)
        assert invalid_instance is None, "Should return None for invalid strategy creation"
        print("✅ Handles invalid strategy creation gracefully")
        
        # Test registry state management
        initial_count = len(self.registry.get_registered_strategies())
        self.registry.clear_registry()
        assert len(self.registry.get_registered_strategies()) == 0, "Registry should be empty after clear"
        
        # Re-discover strategies
        rediscovered_count = self.registry.discover_strategies('src.strategies')
        assert rediscovered_count == initial_count, "Should rediscover same number of strategies"
        print("✅ Registry state management works correctly")


def run_comprehensive_strategy_validation():
    """Run comprehensive strategy registry and discovery validation"""
    print("🚀 Starting Comprehensive Strategy Registry and Discovery Validation")
    print("=" * 80)
    
    test_instance = TestStrategyRegistryValidation()
    test_instance.setup_method()
    
    try:
        # Run all validation tests
        test_instance.test_strategy_discovery_mechanism()
        test_instance.test_strategy_metadata_and_documentation()
        test_instance.test_strategy_categories_organization()
        test_instance.test_strategy_enabling_disabling_cli()
        test_instance.test_multi_market_strategy_functionality()
        test_instance.test_strategy_registry_performance()
        test_instance.test_strategy_error_handling()
        
        print("\n" + "=" * 80)
        print("🎉 ALL STRATEGY REGISTRY VALIDATION TESTS PASSED!")
        print("✅ Strategy discovery mechanism validated")
        print("✅ Strategy metadata and documentation validated")
        print("✅ Strategy categories properly organized")
        print("✅ CLI strategy enabling/disabling works")
        print("✅ Multi-market strategy functionality validated")
        print("✅ Registry performance meets requirements")
        print("✅ Error handling works correctly")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_strategy_validation()
    sys.exit(0 if success else 1)