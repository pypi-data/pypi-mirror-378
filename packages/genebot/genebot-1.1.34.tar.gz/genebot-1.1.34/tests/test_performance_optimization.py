"""
Comprehensive performance optimization and validation tests.
"""

import pytest
import time
import threading
import asyncio
from unittest.mock import Mock, patch, MagicMock
import psutil

from src.monitoring.performance_profiler import PerformanceProfiler, profiler
from src.monitoring.performance_optimizer import PerformanceOptimizer, optimizer


class TestPerformanceProfiler:
    """Test performance profiler functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.profiler = PerformanceProfiler()
    
    def test_profile_operation_context_manager(self):
        """Test operation profiling context manager."""
        with self.profiler.profile_operation("test_operation", test_param="value") as metric:
            time.sleep(0.1)  # Simulate work
            assert metric.name == "test_operation"
            assert metric.metadata["test_param"] == "value"
        
        # Check that metric was recorded
        assert "test_operation" in self.profiler.metrics
        recorded_metric = self.profiler.metrics["test_operation"]
        assert recorded_metric.duration >= 0.1
        assert recorded_metric.memory_delta is not None
    
    def test_continuous_monitoring(self):
        """Test continuous system monitoring."""
        self.profiler.start_continuous_monitoring(interval=0.1)
        
        # Let it collect some data
        time.sleep(0.5)
        
        self.profiler.stop_continuous_monitoring()
        
        # Check that snapshots were collected
        assert len(self.profiler.system_snapshots) > 0
        
        snapshot = self.profiler.system_snapshots[0]
        assert snapshot.cpu_percent >= 0
        assert snapshot.memory_percent >= 0
        assert snapshot.memory_used_mb >= 0
    
    def test_memory_analysis(self):
        """Test memory usage analysis."""
        # Add some fake snapshots
        for i in range(10):
            self.profiler.system_snapshots.append(
                type('SystemSnapshot', (), {
                    'memory_used_mb': 100 + i * 10,
                    'timestamp': time.time() + i
                })()
            )
        
        analysis = self.profiler.analyze_memory_usage()
        
        assert 'current_memory_mb' in analysis
        assert 'peak_memory_mb' in analysis
        assert 'average_memory_mb' in analysis
        assert 'memory_growth_rate' in analysis
        assert analysis['peak_memory_mb'] == 190  # 100 + 9*10
    
    def test_cpu_analysis(self):
        """Test CPU usage analysis."""
        # Add some fake snapshots
        for i in range(10):
            self.profiler.system_snapshots.append(
                type('SystemSnapshot', (), {
                    'cpu_percent': 50 + i * 5,
                    'timestamp': time.time() + i
                })()
            )
        
        analysis = self.profiler.analyze_cpu_usage()
        
        assert 'current_cpu_percent' in analysis
        assert 'peak_cpu_percent' in analysis
        assert 'average_cpu_percent' in analysis
        assert analysis['peak_cpu_percent'] == 95  # 50 + 9*5
    
    def test_performance_report_generation(self):
        """Test comprehensive performance report generation."""
        # Add some test data
        with self.profiler.profile_operation("test_op"):
            time.sleep(0.05)
        
        report = self.profiler.get_performance_report()
        
        assert 'timestamp' in report
        assert 'operation_metrics' in report
        assert 'memory_analysis' in report
        assert 'cpu_analysis' in report
        assert 'system_health' in report
        assert 'recommendations' in report
        
        assert 'test_op' in report['operation_metrics']
    
    def test_system_health_assessment(self):
        """Test system health assessment."""
        # Simulate high memory usage
        self.profiler.system_snapshots = [
            type('SystemSnapshot', (), {
                'memory_used_mb': 2000,  # High memory
                'cpu_percent': 90,       # High CPU
                'timestamp': time.time()
            })()
        ]
        
        health = self.profiler._assess_system_health()
        
        assert 'score' in health
        assert 'status' in health
        assert 'issues' in health
        assert health['score'] < 100  # Should be penalized for high usage
    
    def test_recommendations_generation(self):
        """Test performance recommendations generation."""
        # Simulate conditions that should trigger recommendations
        self.profiler.system_snapshots = [
            type('SystemSnapshot', (), {
                'memory_used_mb': 600,  # High memory
                'cpu_percent': 70,      # High CPU
                'timestamp': time.time()
            })()
        ]
        
        # Add slow operation
        self.profiler.metrics['slow_op'] = type('PerformanceMetric', (), {
            'duration': 3.0,  # Slow operation
            'name': 'slow_op'
        })()
        
        recommendations = self.profiler._generate_recommendations()
        
        assert len(recommendations) > 0
        assert any('memory' in rec.lower() for rec in recommendations)
        assert any('slow_op' in rec for rec in recommendations)


class TestPerformanceOptimizer:
    """Test performance optimizer functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.optimizer = PerformanceOptimizer()
    
    def test_optimization_rule_management(self):
        """Test adding, removing, and managing optimization rules."""
        from src.monitoring.performance_optimizer import OptimizationRule
        
        # Add custom rule
        test_rule = OptimizationRule(
            name="test_rule",
            condition=lambda metrics: True,
            action=lambda: None,
            description="Test rule"
        )
        
        self.optimizer.add_rule(test_rule)
        assert any(rule.name == "test_rule" for rule in self.optimizer.optimization_rules)
        
        # Disable rule
        self.optimizer.disable_rule("test_rule")
        test_rule_obj = next(rule for rule in self.optimizer.optimization_rules if rule.name == "test_rule")
        assert not test_rule_obj.enabled
        
        # Remove rule
        self.optimizer.remove_rule("test_rule")
        assert not any(rule.name == "test_rule" for rule in self.optimizer.optimization_rules)
    
    def test_function_optimization_decorator(self):
        """Test function optimization decorator."""
        call_count = 0
        
        @self.optimizer.optimize_function
        def test_function(x, y=1):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call should execute function
        result1 = test_function(1, y=2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call with same args should use cache
        result2 = test_function(1, y=2)
        assert result2 == 3
        assert call_count == 1  # Should not increment due to caching
        
        # Different args should execute function again
        result3 = test_function(2, y=3)
        assert result3 == 5
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_async_function_optimization(self):
        """Test async function optimization decorator."""
        call_count = 0
        
        @self.optimizer.optimize_async_function
        async def async_test_function(x):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2
        
        # First call
        result1 = await async_test_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call with same args should use cache
        result2 = await async_test_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment due to caching
    
    def test_cache_statistics(self):
        """Test cache performance statistics."""
        @self.optimizer.optimize_function
        def cached_function(x):
            return x * 2
        
        # Reset cache stats
        self.optimizer.cache_stats = {'hits': 0, 'misses': 0}
        
        # Make some calls
        cached_function(1)  # Miss
        cached_function(1)  # Hit
        cached_function(2)  # Miss
        cached_function(1)  # Hit
        
        stats = self.optimizer.get_cache_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 2
        assert stats['hit_rate'] == 0.5
    
    def test_benchmark_operation(self):
        """Test operation benchmarking."""
        def test_operation():
            time.sleep(0.01)
            return sum(range(100))
        
        benchmark_result = self.optimizer.benchmark_operation(test_operation, iterations=5)
        
        assert 'iterations' in benchmark_result
        assert 'avg_duration' in benchmark_result
        assert 'min_duration' in benchmark_result
        assert 'max_duration' in benchmark_result
        assert benchmark_result['iterations'] == 5
        assert benchmark_result['avg_duration'] >= 0.01
    
    @patch('src.monitoring.performance_optimizer.profiler')
    def test_multi_strategy_performance_profiling(self, mock_profiler):
        """Test multi-strategy performance profiling."""
        # Mock strategies
        strategies = [Mock() for _ in range(3)]
        
        # Mock profiler methods
        mock_profiler.start_continuous_monitoring = Mock()
        mock_profiler.stop_continuous_monitoring = Mock()
        mock_profiler.get_performance_report = Mock(return_value={
            'memory_analysis': {'memory_stability': 0.8},
            'cpu_analysis': {'average_cpu_percent': 60},
            'system_health': {'status': 'healthy'}
        })
        
        result = self.optimizer.profile_multi_strategy_performance(strategies)
        
        assert 'strategy_count' in result
        assert 'completed_strategies' in result
        assert 'performance_report' in result
        assert 'multi_strategy_stable' in result
        assert result['strategy_count'] == 3
        assert result['multi_strategy_stable'] is True
        
        mock_profiler.start_continuous_monitoring.assert_called_once()
        mock_profiler.stop_continuous_monitoring.assert_called_once()
    
    @patch('time.time')
    @patch('psutil.Process')
    @patch('psutil.cpu_percent')
    def test_extended_operation_stability(self, mock_cpu_percent, mock_process, mock_time):
        """Test extended operation stability testing."""
        # Mock time progression
        mock_time.side_effect = [0, 60, 120, 1800, 1860]  # 30 minutes duration
        
        # Mock system metrics
        mock_process.return_value.memory_info.return_value.rss = 100 * 1024 * 1024  # 100MB
        mock_cpu_percent.return_value = 50
        
        # Mock profiler
        with patch('src.monitoring.performance_optimizer.profiler') as mock_profiler:
            mock_profiler.start_continuous_monitoring = Mock()
            mock_profiler.stop_continuous_monitoring = Mock()
            
            # Run short test (mock will make it appear as 30 minutes)
            result = self.optimizer.test_extended_operation_stability(duration_minutes=0.1)
        
        assert 'start_time' in result
        assert 'duration_minutes' in result
        assert 'memory_samples' in result
        assert 'cpu_samples' in result
        assert 'final_analysis' in result
    
    def test_system_optimization_execution(self):
        """Test system optimization execution."""
        # Create a mock rule that should trigger
        from src.monitoring.performance_optimizer import OptimizationRule
        
        rule_executed = False
        
        def mock_action():
            nonlocal rule_executed
            rule_executed = True
        
        test_rule = OptimizationRule(
            name="test_optimization",
            condition=lambda metrics: True,  # Always trigger
            action=mock_action,
            description="Test optimization"
        )
        
        self.optimizer.add_rule(test_rule)
        
        # Mock profiler to return test data
        with patch('src.monitoring.performance_optimizer.profiler') as mock_profiler:
            mock_profiler.get_performance_report.return_value = {
                'memory_analysis': {},
                'cpu_analysis': {},
                'system_health': {}
            }
            
            result = self.optimizer.optimize_system()
        
        assert result['status'] == 'completed'
        assert len(result['applied_optimizations']) > 0
        assert rule_executed
        assert any(opt['rule'] == 'test_optimization' for opt in result['applied_optimizations'])
    
    def test_optimization_report_generation(self):
        """Test optimization report generation."""
        report = self.optimizer.get_optimization_report()
        
        assert 'cache_stats' in report
        assert 'optimization_history' in report
        assert 'active_rules' in report
        assert 'thread_pool_stats' in report
        
        # Check cache stats structure
        cache_stats = report['cache_stats']
        assert 'hits' in cache_stats
        assert 'misses' in cache_stats
        assert 'hit_rate' in cache_stats
        assert 'cache_size' in cache_stats


class TestPerformanceIntegration:
    """Test integration between profiler and optimizer."""
    
    def test_profiler_optimizer_integration(self):
        """Test that profiler and optimizer work together."""
        # Profile some operations
        with profiler.profile_operation("integration_test"):
            time.sleep(0.05)
        
        # Run optimization
        result = optimizer.optimize_system()
        
        assert result['status'] == 'completed'
        assert 'performance_before' in result
    
    def test_startup_performance_profiling(self):
        """Test startup performance profiling."""
        startup_metrics = profiler.profile_startup_sequence()
        
        assert 'total_startup_time' in startup_metrics
        assert startup_metrics['total_startup_time'] > 0
        
        # Check that startup phases were profiled
        startup_operations = [name for name in profiler.metrics.keys() if name.startswith('startup_')]
        assert len(startup_operations) > 0
    
    @patch('src.monitoring.performance_profiler.psutil.Process')
    def test_memory_leak_detection(self, mock_process):
        """Test memory leak detection capabilities."""
        # Simulate increasing memory usage
        memory_values = [100, 120, 140, 160, 180, 200]  # MB
        mock_process.return_value.memory_info.return_value.rss = 100 * 1024 * 1024
        
        # Add snapshots with increasing memory
        for i, mem_mb in enumerate(memory_values):
            profiler.system_snapshots.append(
                type('SystemSnapshot', (), {
                    'memory_used_mb': mem_mb,
                    'cpu_percent': 50,
                    'timestamp': time.time() + i
                })()
            )
        
        analysis = profiler.analyze_memory_usage()
        
        # Should detect positive growth rate (potential leak)
        assert analysis['memory_growth_rate'] > 0
        
        # Optimizer should recommend investigation
        recommendations = profiler._generate_recommendations()
        assert any('leak' in rec.lower() for rec in recommendations)


class TestPerformanceStressTests:
    """Stress tests for performance monitoring system."""
    
    def test_high_frequency_profiling(self):
        """Test profiling under high frequency operations."""
        profiler_instance = PerformanceProfiler()
        
        # Profile many operations quickly
        for i in range(100):
            with profiler_instance.profile_operation(f"high_freq_op_{i}"):
                pass  # Minimal work
        
        assert len(profiler_instance.metrics) == 100
        
        # Check that all operations were recorded
        for i in range(100):
            assert f"high_freq_op_{i}" in profiler_instance.metrics
    
    def test_concurrent_profiling(self):
        """Test profiling with concurrent operations."""
        profiler_instance = PerformanceProfiler()
        results = []
        
        def profile_operation(op_id):
            with profiler_instance.profile_operation(f"concurrent_op_{op_id}"):
                time.sleep(0.01)
                results.append(op_id)
        
        # Run concurrent operations
        threads = []
        for i in range(10):
            thread = threading.Thread(target=profile_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        assert len(results) == 10
        assert len(profiler_instance.metrics) == 10
    
    def test_memory_pressure_handling(self):
        """Test system behavior under memory pressure."""
        optimizer_instance = PerformanceOptimizer()
        
        # Fill cache with many items
        for i in range(2000):
            optimizer_instance.memory_cache[f"key_{i}"] = f"value_{i}" * 100
        
        # Trigger cache cleanup
        optimizer_instance._cleanup_cache()
        
        # Cache should be reduced
        assert len(optimizer_instance.memory_cache) <= 500
    
    def test_performance_under_load(self):
        """Test performance monitoring system under load."""
        profiler_instance = PerformanceProfiler()
        optimizer_instance = PerformanceOptimizer()
        
        # Start monitoring
        profiler_instance.start_continuous_monitoring(interval=0.1)
        
        try:
            # Simulate load
            for i in range(50):
                with profiler_instance.profile_operation(f"load_test_{i}"):
                    # Simulate CPU and memory work
                    data = [j * j for j in range(1000)]
                    sum(data)
            
            # Run optimization under load
            result = optimizer_instance.optimize_system()
            
            assert result['status'] == 'completed'
            
        finally:
            profiler_instance.stop_continuous_monitoring()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])