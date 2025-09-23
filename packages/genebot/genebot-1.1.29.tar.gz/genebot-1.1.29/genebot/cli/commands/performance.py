"""
Performance monitoring and optimization CLI commands.
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
from argparse import Namespace

from ..result import CommandResult
from ..context import CLIContext
from ..utils.logger import CLILogger
from ..utils.error_handler import CLIErrorHandler
from .base import BaseCommand
from ...logging import get_logger

logger = get_logger(__name__)


class ProfileStartupCommand(BaseCommand):
    """Profile system startup performance."""
    
    def run(self, args: Namespace) -> CommandResult:
        """Profile system startup performance."""
        try:
            from src.monitoring.performance_profiler import profiler
            
            logger.info("Profiling system startup...")
            
            # Profile startup sequence
            startup_metrics = profiler.profile_startup_sequence()
            
            # Generate report
            report = profiler.get_performance_report()
            
            # Save report if requested
            if getattr(args, 'save_report', False):
                output_path = Path(getattr(args, 'output_dir', 'reports')) / f"startup_profile_{int(time.time())}.json"
                output_path.parent.mkdir(exist_ok=True)
                
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                logger.info(f"Startup profile saved to {output_path}")
            
            # Display summary
            total_time = startup_metrics.get('total_startup_time', 0)
            
            result_data = {
                'total_startup_time': total_time,
                'startup_phases': {
                    name: metric.duration for name, metric in profiler.metrics.items()
                    if name.startswith('startup_') and metric.duration
                },
                'system_health': report.get('system_health', {}),
                'recommendations': report.get('recommendations', [])
            }
            
            return CommandResult(
                success=True,
                message=f"Startup profiling completed in {total_time:.2f} seconds",
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Startup profiling failed: {e}")
            return CommandResult(
                success=False,
                message=f"Startup profiling failed: {e}"
            )


class MonitorPerformanceCommand(BaseCommand):
    """Start continuous performance monitoring."""
    
    def run(self, args: Namespace) -> CommandResult:
        """Start continuous performance monitoring."""
        try:
            from src.monitoring.performance_profiler import profiler
            
            duration = getattr(args, 'duration', 60)  # Default 1 minute
            interval = getattr(args, 'interval', 1.0)  # Default 1 second
            
            logger.info(f"Starting performance monitoring for {duration} seconds...")
            
            # Start monitoring
            profiler.start_continuous_monitoring(interval=interval)
            
            try:
                # Monitor for specified duration
                time.sleep(duration)
                
                # Generate report
                report = profiler.get_performance_report()
                
                # Save report if requested
                if getattr(args, 'save_report', False):
                    output_path = Path(getattr(args, 'output_dir', 'reports')) / f"performance_monitor_{int(time.time())}.json"
                    output_path.parent.mkdir(exist_ok=True)
                    
                    with open(output_path, 'w') as f:
                        json.dump(report, f, indent=2, default=str)
                    
                    logger.info(f"Performance report saved to {output_path}")
                
                # Display summary
                memory_analysis = report.get('memory_analysis', {})
                cpu_analysis = report.get('cpu_analysis', {})
                
                result_data = {
                    'monitoring_duration': duration,
                    'samples_collected': len(profiler.system_snapshots),
                    'memory_usage': {
                        'current_mb': memory_analysis.get('current_memory_mb', 0),
                        'peak_mb': memory_analysis.get('peak_memory_mb', 0),
                        'average_mb': memory_analysis.get('average_memory_mb', 0)
                    },
                    'cpu_usage': {
                        'current_percent': cpu_analysis.get('current_cpu_percent', 0),
                        'peak_percent': cpu_analysis.get('peak_cpu_percent', 0),
                        'average_percent': cpu_analysis.get('average_cpu_percent', 0)
                    },
                    'system_health': report.get('system_health', {}),
                    'recommendations': report.get('recommendations', [])
                }
                
                return CommandResult(
                    success=True,
                    message=f"Performance monitoring completed ({duration}s, {len(profiler.system_snapshots)} samples)",
                    data=result_data
                )
                
            finally:
                profiler.stop_continuous_monitoring()
            
        except Exception as e:
            logger.error(f"Performance monitoring failed: {e}")
            return CommandResult(
                success=False,
                message=f"Performance monitoring failed: {e}"
            )


class OptimizeSystemCommand(BaseCommand):
    """Run system performance optimization."""
    
    def run(self, args: Namespace) -> CommandResult:
        """Run system performance optimization."""
        try:
            from src.monitoring.performance_optimizer import optimizer
            
            logger.info("Running system optimization...")
            
            # Run optimization
            optimization_result = optimizer.optimize_system()
            
            # Save report if requested
            if getattr(args, 'save_report', False):
                output_path = Path(getattr(args, 'output_dir', 'reports')) / f"optimization_result_{int(time.time())}.json"
                output_path.parent.mkdir(exist_ok=True)
                
                with open(output_path, 'w') as f:
                    json.dump(optimization_result, f, indent=2, default=str)
                
                logger.info(f"Optimization report saved to {output_path}")
            
            # Display summary
            applied_optimizations = optimization_result.get('applied_optimizations', [])
            duration = optimization_result.get('duration', 0)
            
            result_data = {
                'optimization_duration': duration,
                'optimizations_applied': len(applied_optimizations),
                'optimization_details': [
                    {
                        'rule': opt['rule'],
                        'description': opt['description']
                    }
                    for opt in applied_optimizations
                ],
                'cache_stats': optimizer.get_cache_stats()
            }
            
            return CommandResult(
                success=True,
                message=f"System optimization completed in {duration:.2f}s, applied {len(applied_optimizations)} optimizations",
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"System optimization failed: {e}")
            return CommandResult(
                success=False,
                message=f"System optimization failed: {e}"
            )


class ValidatePerformanceCommand(BaseCommand):
    """Run performance validation tests."""
    
    def run(self, args: Namespace) -> CommandResult:
        """Run performance validation tests."""
        try:
            from scripts.performance_validation import PerformanceValidator
            
            logger.info("Running performance validation...")
            
            validator = PerformanceValidator(output_dir=getattr(args, 'output_dir', 'reports'))
            
            # Determine which tests to run
            test_type = getattr(args, 'test_type', 'all')
            
            if test_type == 'all':
                results = validator.run_full_validation()
            elif test_type == 'startup':
                results = {'startup_performance': validator.validate_startup_performance()}
            elif test_type == 'memory':
                duration = getattr(args, 'duration', 5)
                results = {'memory_usage': validator.validate_memory_usage(duration_minutes=duration)}
            elif test_type == 'multi_strategy':
                strategy_count = getattr(args, 'strategy_count', 5)
                results = {'multi_strategy_performance': validator.validate_multi_strategy_performance(strategy_count=strategy_count)}
            elif test_type == 'stability':
                duration = getattr(args, 'duration', 10)
                results = {'extended_operation_stability': validator.validate_extended_operation_stability(duration_minutes=duration)}
            elif test_type == 'optimization':
                results = {'optimization_effectiveness': validator.validate_optimization_effectiveness()}
            else:
                return CommandResult(
                    success=False,
                    message=f"Unknown test type: {test_type}"
                )
            
            # Save validation report
            validator.save_validation_report(results)
            
            # Determine overall success
            if test_type == 'all':
                overall_passed = results.get('overall_passed', False)
                total_issues = results.get('total_issues', 0)
                validation_duration = results.get('validation_duration', 0)
                
                result_data = {
                    'overall_passed': overall_passed,
                    'total_issues': total_issues,
                    'validation_duration': validation_duration,
                    'summary': results.get('summary', {})
                }
                
                message = f"Performance validation {'PASSED' if overall_passed else 'FAILED'} in {validation_duration:.2f}s"
                if total_issues > 0:
                    message += f" ({total_issues} issues found)"
            else:
                test_result = list(results.values())[0]
                passed = test_result.get('passed', False)
                issues = test_result.get('issues', [])
                
                result_data = {
                    'test_type': test_type,
                    'passed': passed,
                    'issues': issues,
                    'test_result': test_result
                }
                
                message = f"Performance test '{test_type}' {'PASSED' if passed else 'FAILED'}"
                if issues:
                    message += f" ({len(issues)} issues found)"
            
            return CommandResult(
                success=result_data.get('overall_passed', result_data.get('passed', False)),
                message=message,
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Performance validation failed: {e}")
            return CommandResult(
                success=False,
                message=f"Performance validation failed: {e}"
            )


class BenchmarkOperationCommand(BaseCommand):
    """Benchmark a specific operation."""
    
    def run(self, args: Namespace) -> CommandResult:
        """Benchmark a specific operation."""
        try:
            from src.monitoring.performance_optimizer import optimizer
            
            operation_name = getattr(args, 'operation', 'startup')
            iterations = getattr(args, 'iterations', 100)
            
            logger.info(f"Benchmarking operation '{operation_name}' for {iterations} iterations...")
            
            # Define benchmark operations
            benchmark_operations = {
                'startup': self._benchmark_startup,
                'strategy_load': self._benchmark_strategy_load,
                'data_processing': self._benchmark_data_processing,
                'memory_allocation': self._benchmark_memory_allocation
            }
            
            if operation_name not in benchmark_operations:
                return CommandResult(
                    success=False,
                    message=f"Unknown operation: {operation_name}. Available: {', '.join(benchmark_operations.keys())}"
                )
            
            # Run benchmark
            operation_func = benchmark_operations[operation_name]
            benchmark_result = optimizer.benchmark_operation(operation_func, iterations=iterations)
            
            # Save report if requested
            if getattr(args, 'save_report', False):
                output_path = Path(getattr(args, 'output_dir', 'reports')) / f"benchmark_{operation_name}_{int(time.time())}.json"
                output_path.parent.mkdir(exist_ok=True)
                
                with open(output_path, 'w') as f:
                    json.dump(benchmark_result, f, indent=2, default=str)
                
                logger.info(f"Benchmark report saved to {output_path}")
            
            # Display results
            if 'error' in benchmark_result:
                return CommandResult(
                    success=False,
                    message=f"Benchmark failed: {benchmark_result['error']}"
                )
            
            avg_duration = benchmark_result.get('avg_duration', 0)
            min_duration = benchmark_result.get('min_duration', 0)
            max_duration = benchmark_result.get('max_duration', 0)
            
            result_data = {
                'operation': operation_name,
                'iterations': benchmark_result.get('iterations', 0),
                'avg_duration_ms': avg_duration * 1000,
                'min_duration_ms': min_duration * 1000,
                'max_duration_ms': max_duration * 1000,
                'total_duration_s': benchmark_result.get('total_duration', 0),
                'avg_memory_delta_mb': benchmark_result.get('avg_memory_delta', 0)
            }
            
            return CommandResult(
                success=True,
                message=f"Benchmark completed: {operation_name} averaged {avg_duration*1000:.2f}ms over {iterations} iterations",
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return CommandResult(
                success=False,
                message=f"Benchmark failed: {e}"
            )
    
    def _benchmark_startup(self):
        """Benchmark startup operation."""
        # Simulate startup components
        time.sleep(0.01)  # Config loading
        time.sleep(0.02)  # Database connection
        time.sleep(0.01)  # Strategy loading
    
    def _benchmark_strategy_load(self):
        """Benchmark strategy loading operation."""
        # Simulate strategy loading
        data = [i for i in range(100)]
        result = sum(x * x for x in data)
        return result
    
    def _benchmark_data_processing(self):
        """Benchmark data processing operation."""
        # Simulate data processing
        data = [i * 1.5 for i in range(500)]
        processed = [x / 2 for x in data if x > 100]
        return sum(processed)
    
    def _benchmark_memory_allocation(self):
        """Benchmark memory allocation operation."""
        # Simulate memory allocation and cleanup
        data = [i for i in range(1000)]
        processed = [x * x for x in data]
        del data
        return len(processed)


class PerformanceStatusCommand(BaseCommand):
    """Get current performance status."""
    
    def run(self, args: Namespace) -> CommandResult:
        """Get current performance status."""
        try:
            from src.monitoring.performance_profiler import profiler
            from src.monitoring.performance_optimizer import optimizer
            
            # Get current performance report
            performance_report = profiler.get_performance_report()
            optimization_report = optimizer.get_optimization_report()
            
            # Extract key metrics
            memory_analysis = performance_report.get('memory_analysis', {})
            cpu_analysis = performance_report.get('cpu_analysis', {})
            system_health = performance_report.get('system_health', {})
            
            result_data = {
                'system_health': {
                    'score': system_health.get('score', 0),
                    'status': system_health.get('status', 'unknown'),
                    'issues': system_health.get('issues', [])
                },
                'memory_status': {
                    'current_mb': memory_analysis.get('current_memory_mb', 0),
                    'peak_mb': memory_analysis.get('peak_memory_mb', 0),
                    'stability': memory_analysis.get('memory_stability', 0)
                },
                'cpu_status': {
                    'current_percent': cpu_analysis.get('current_cpu_percent', 0),
                    'average_percent': cpu_analysis.get('average_cpu_percent', 0)
                },
                'optimization_status': {
                    'cache_hit_rate': optimization_report.get('cache_stats', {}).get('hit_rate', 0),
                    'cache_size': optimization_report.get('cache_stats', {}).get('cache_size', 0),
                    'recent_optimizations': len(optimization_report.get('optimization_history', []))
                },
                'recommendations': performance_report.get('recommendations', [])
            }
            
            health_status = system_health.get('status', 'unknown')
            health_score = system_health.get('score', 0)
            
            return CommandResult(
                success=True,
                message=f"System health: {health_status} (score: {health_score})",
                data=result_data
            )
            
        except Exception as e:
            logger.error(f"Failed to get performance status: {e}")
            return CommandResult(
                success=False,
                message=f"Failed to get performance status: {e}"
            )