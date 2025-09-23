"""
Integration tests for performance optimization and validation system.
"""

import pytest
import time
import tempfile
import json
from pathlib import Path

from src.monitoring.performance_profiler import PerformanceProfiler
from src.monitoring.performance_optimizer import PerformanceOptimizer
from scripts.performance_validation import PerformanceValidator


class TestPerformanceIntegration:
    """Integration tests for performance system."""
    
    def test_profiler_optimizer_integration(self):
        """Test that profiler and optimizer work together."""
        profiler = PerformanceProfiler()
        optimizer = PerformanceOptimizer()
        
        # Profile some operations
        with profiler.profile_operation("test_operation"):
            time.sleep(0.1)
        
        # Run optimization
        result = optimizer.optimize_system()
        
        assert result['status'] == 'completed'
        assert 'applied_optimizations' in result
        assert 'performance_before' in result
    
    def test_validation_system_integration(self):
        """Test that validation system works end-to-end."""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = PerformanceValidator(output_dir=temp_dir)
            
            # Run startup validation
            result = validator.validate_startup_performance()
            
            assert 'passed' in result
            assert 'startup_metrics' in result
            assert 'thresholds' in result
            
            # Save and verify report
            validator.save_validation_report({'startup_performance': result})
            
            # Check that files were created
            report_files = list(Path(temp_dir).glob("*.json"))
            assert len(report_files) > 0
            
            # Verify report content
            with open(report_files[0]) as f:
                saved_report = json.load(f)
            
            assert 'startup_performance' in saved_report
    
    def test_performance_optimization_effectiveness(self):
        """Test that performance optimizations actually improve performance."""
        profiler = PerformanceProfiler()
        optimizer = PerformanceOptimizer()
        
        # Create a function that can be optimized
        @optimizer.optimize_function
        def test_function(x):
            return x * x
        
        # Call function multiple times
        results = []
        for i in range(10):
            results.append(test_function(i))
        
        # Check cache effectiveness
        cache_stats = optimizer.get_cache_stats()
        assert cache_stats['hits'] > 0  # Should have cache hits
        assert cache_stats['hit_rate'] > 0  # Should have positive hit rate
    
    def test_memory_monitoring_accuracy(self):
        """Test that memory monitoring provides accurate measurements."""
        profiler = PerformanceProfiler()
        
        # Start monitoring
        profiler.start_continuous_monitoring(interval=0.1)
        
        try:
            # Allocate some memory
            large_data = [i for i in range(100000)]
            time.sleep(0.5)  # Let monitoring capture the allocation
            
            # Clean up
            del large_data
            time.sleep(0.5)  # Let monitoring capture the cleanup
            
            # Analyze memory usage
            analysis = profiler.analyze_memory_usage()
            
            assert analysis['peak_memory_mb'] > analysis['current_memory_mb']
            assert len(profiler.system_snapshots) > 0
            
        finally:
            profiler.stop_continuous_monitoring()
    
    def test_multi_strategy_performance_simulation(self):
        """Test multi-strategy performance simulation."""
        optimizer = PerformanceOptimizer()
        
        # Create mock strategies
        strategies = [f"strategy_{i}" for i in range(5)]
        
        # Profile multi-strategy performance
        result = optimizer.profile_multi_strategy_performance(strategies)
        
        assert result['strategy_count'] == 5
        assert result['completed_strategies'] > 0
        assert 'performance_report' in result
        assert 'multi_strategy_stable' in result
    
    def test_performance_bottleneck_detection(self):
        """Test that performance bottlenecks are detected."""
        profiler = PerformanceProfiler()
        
        # Create a slow operation
        with profiler.profile_operation("slow_operation"):
            time.sleep(0.2)  # Intentionally slow
        
        # Create a fast operation
        with profiler.profile_operation("fast_operation"):
            time.sleep(0.01)  # Fast
        
        # Generate recommendations
        recommendations = profiler._generate_recommendations()
        
        # Should detect the slow operation
        slow_op_mentioned = any('slow_operation' in rec for rec in recommendations)
        assert slow_op_mentioned
    
    def test_system_health_assessment(self):
        """Test system health assessment accuracy."""
        profiler = PerformanceProfiler()
        
        # Simulate normal operation
        with profiler.profile_operation("normal_operation"):
            time.sleep(0.05)
        
        # Get health assessment
        report = profiler.get_performance_report()
        health = report['system_health']
        
        assert 'score' in health
        assert 'status' in health
        assert 'issues' in health
        assert health['score'] >= 0
        assert health['score'] <= 100
        assert health['status'] in ['healthy', 'warning', 'critical']
    
    def test_performance_report_completeness(self):
        """Test that performance reports contain all expected data."""
        profiler = PerformanceProfiler()
        optimizer = PerformanceOptimizer()
        
        # Generate some activity
        with profiler.profile_operation("test_activity"):
            time.sleep(0.05)
        
        # Get reports
        performance_report = profiler.get_performance_report()
        optimization_report = optimizer.get_optimization_report()
        
        # Check performance report structure
        expected_keys = [
            'timestamp', 'operation_metrics', 'memory_analysis',
            'cpu_analysis', 'system_health', 'recommendations'
        ]
        for key in expected_keys:
            assert key in performance_report
        
        # Check optimization report structure
        expected_opt_keys = [
            'cache_stats', 'optimization_history', 'active_rules', 'thread_pool_stats'
        ]
        for key in expected_opt_keys:
            assert key in optimization_report
    
    def test_performance_thresholds_validation(self):
        """Test that performance thresholds are properly validated."""
        validator = PerformanceValidator()
        
        # Test startup validation with known good performance
        result = validator.validate_startup_performance()
        
        assert 'thresholds' in result
        assert 'passed' in result
        
        thresholds = result['thresholds']
        assert 'max_startup_time' in thresholds
        assert thresholds['max_startup_time'] > 0
    
    def test_extended_operation_stability(self):
        """Test extended operation stability monitoring."""
        optimizer = PerformanceOptimizer()
        
        # Run short stability test
        result = optimizer.test_extended_operation_stability(duration_minutes=0.1)
        
        assert 'start_time' in result
        assert 'duration_minutes' in result
        assert 'memory_samples' in result
        assert 'cpu_samples' in result
        assert 'final_analysis' in result
        
        # Check final analysis
        analysis = result['final_analysis']
        assert 'status' in analysis
        assert analysis['status'] in ['stable', 'unstable', 'insufficient_data']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])