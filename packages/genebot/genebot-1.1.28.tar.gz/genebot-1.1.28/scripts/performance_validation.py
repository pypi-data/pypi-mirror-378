#!/usr/bin/env python3
"""
Performance validation script for GeneBot system.
Validates startup time, memory usage, multi-strategy performance, and extended operation stability.
"""

import sys
import os
import time
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.performance_profiler import profiler
from src.monitoring.performance_optimizer import optimizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceValidator:
    """Comprehensive performance validation for GeneBot system."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.validation_results = {}
        
    def validate_startup_performance(self) -> Dict[str, Any]:
        """Validate system startup performance."""
        logger.info("Validating startup performance...")
        
        startup_start = time.time()
        
        # Profile startup sequence
        startup_metrics = profiler.profile_startup_sequence()
        
        startup_duration = time.time() - startup_start
        
        # Define performance thresholds
        thresholds = {
            'max_startup_time': 30.0,  # seconds
            'max_config_load_time': 5.0,
            'max_strategy_load_time': 10.0
        }
        
        # Validate against thresholds
        validation_results = {
            'total_startup_time': startup_duration,
            'startup_metrics': startup_metrics,
            'thresholds': thresholds,
            'passed': startup_duration <= thresholds['max_startup_time'],
            'issues': []
        }
        
        if startup_duration > thresholds['max_startup_time']:
            validation_results['issues'].append(
                f"Startup time {startup_duration:.2f}s exceeds threshold {thresholds['max_startup_time']}s"
            )
        
        # Check individual startup phases
        for metric_name, metric in profiler.metrics.items():
            if metric_name.startswith('startup_') and metric.duration:
                phase_name = metric_name.replace('startup_', '')
                threshold_key = f'max_{phase_name}_time'
                
                if threshold_key in thresholds and metric.duration > thresholds[threshold_key]:
                    validation_results['issues'].append(
                        f"{phase_name} phase took {metric.duration:.2f}s, exceeds threshold {thresholds[threshold_key]}s"
                    )
        
        logger.info(f"Startup validation {'PASSED' if validation_results['passed'] else 'FAILED'}")
        return validation_results
    
    def validate_memory_usage(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """Validate memory usage during normal operation."""
        logger.info(f"Validating memory usage for {duration_minutes} minutes...")
        
        # Start continuous monitoring
        profiler.start_continuous_monitoring(interval=1.0)
        
        try:
            # Simulate normal operation
            end_time = time.time() + (duration_minutes * 60)
            operation_count = 0
            
            while time.time() < end_time:
                # Simulate various operations
                with profiler.profile_operation(f"memory_test_op_{operation_count}"):
                    self._simulate_normal_operation()
                    operation_count += 1
                
                time.sleep(2)  # Pause between operations
            
            # Analyze memory usage
            memory_analysis = profiler.analyze_memory_usage()
            
            # Define memory thresholds
            thresholds = {
                'max_memory_mb': 1024,  # 1GB
                'max_memory_growth_rate': 2.0,  # MB per minute
                'min_memory_stability': 0.7
            }
            
            validation_results = {
                'duration_minutes': duration_minutes,
                'operation_count': operation_count,
                'memory_analysis': memory_analysis,
                'thresholds': thresholds,
                'passed': True,
                'issues': []
            }
            
            # Check memory thresholds
            current_memory = memory_analysis.get('current_memory_mb', 0)
            if current_memory > thresholds['max_memory_mb']:
                validation_results['passed'] = False
                validation_results['issues'].append(
                    f"Current memory usage {current_memory:.2f}MB exceeds threshold {thresholds['max_memory_mb']}MB"
                )
            
            growth_rate = memory_analysis.get('memory_growth_rate', 0)
            if growth_rate > thresholds['max_memory_growth_rate']:
                validation_results['passed'] = False
                validation_results['issues'].append(
                    f"Memory growth rate {growth_rate:.2f}MB/min exceeds threshold {thresholds['max_memory_growth_rate']}MB/min"
                )
            
            stability = memory_analysis.get('memory_stability', 1.0)
            if stability < thresholds['min_memory_stability']:
                validation_results['passed'] = False
                validation_results['issues'].append(
                    f"Memory stability {stability:.2f} below threshold {thresholds['min_memory_stability']}"
                )
            
            logger.info(f"Memory validation {'PASSED' if validation_results['passed'] else 'FAILED'}")
            return validation_results
            
        finally:
            profiler.stop_continuous_monitoring()
    
    def validate_multi_strategy_performance(self, strategy_count: int = 5) -> Dict[str, Any]:
        """Validate performance with multiple strategies running."""
        logger.info(f"Validating multi-strategy performance with {strategy_count} strategies...")
        
        # Create mock strategies
        strategies = [self._create_mock_strategy(i) for i in range(strategy_count)]
        
        # Profile multi-strategy performance
        performance_result = optimizer.profile_multi_strategy_performance(strategies)
        
        # Define performance thresholds
        thresholds = {
            'max_avg_cpu_percent': 85.0,
            'max_memory_mb': 800,
            'min_completion_rate': 0.9,  # 90% of strategies should complete
            'required_stability': True
        }
        
        validation_results = {
            'strategy_count': strategy_count,
            'performance_result': performance_result,
            'thresholds': thresholds,
            'passed': True,
            'issues': []
        }
        
        # Check completion rate
        completion_rate = performance_result['completed_strategies'] / performance_result['strategy_count']
        if completion_rate < thresholds['min_completion_rate']:
            validation_results['passed'] = False
            validation_results['issues'].append(
                f"Strategy completion rate {completion_rate:.2f} below threshold {thresholds['min_completion_rate']}"
            )
        
        # Check CPU usage
        cpu_analysis = performance_result['performance_report'].get('cpu_analysis', {})
        avg_cpu = cpu_analysis.get('average_cpu_percent', 0)
        if avg_cpu > thresholds['max_avg_cpu_percent']:
            validation_results['passed'] = False
            validation_results['issues'].append(
                f"Average CPU usage {avg_cpu:.2f}% exceeds threshold {thresholds['max_avg_cpu_percent']}%"
            )
        
        # Check memory usage
        memory_analysis = performance_result['performance_report'].get('memory_analysis', {})
        current_memory = memory_analysis.get('current_memory_mb', 0)
        if current_memory > thresholds['max_memory_mb']:
            validation_results['passed'] = False
            validation_results['issues'].append(
                f"Memory usage {current_memory:.2f}MB exceeds threshold {thresholds['max_memory_mb']}MB"
            )
        
        # Check stability
        if not performance_result['multi_strategy_stable']:
            validation_results['passed'] = False
            validation_results['issues'].append("Multi-strategy execution is not stable")
        
        logger.info(f"Multi-strategy validation {'PASSED' if validation_results['passed'] else 'FAILED'}")
        return validation_results
    
    def validate_extended_operation_stability(self, duration_minutes: int = 10) -> Dict[str, Any]:
        """Validate system stability during extended operation."""
        logger.info(f"Validating extended operation stability for {duration_minutes} minutes...")
        
        # Run extended stability test
        stability_result = optimizer.test_extended_operation_stability(duration_minutes)
        
        # Define stability thresholds
        thresholds = {
            'max_memory_variance': 100,  # MB²
            'max_cpu_variance': 400,     # %²
            'max_memory_trend': 1.0,     # MB/sample
            'max_error_count': 5,
            'allow_performance_degradation': False
        }
        
        validation_results = {
            'duration_minutes': duration_minutes,
            'stability_result': stability_result,
            'thresholds': thresholds,
            'passed': True,
            'issues': []
        }
        
        # Check final analysis
        final_analysis = stability_result.get('final_analysis', {})
        
        if final_analysis.get('status') != 'stable':
            validation_results['passed'] = False
            validation_results['issues'].append("System is not stable during extended operation")
        
        # Check specific metrics
        memory_variance = final_analysis.get('memory_variance', 0)
        if memory_variance > thresholds['max_memory_variance']:
            validation_results['passed'] = False
            validation_results['issues'].append(
                f"Memory variance {memory_variance:.2f} exceeds threshold {thresholds['max_memory_variance']}"
            )
        
        cpu_variance = final_analysis.get('cpu_variance', 0)
        if cpu_variance > thresholds['max_cpu_variance']:
            validation_results['passed'] = False
            validation_results['issues'].append(
                f"CPU variance {cpu_variance:.2f} exceeds threshold {thresholds['max_cpu_variance']}"
            )
        
        memory_trend = abs(final_analysis.get('memory_trend', 0))
        if memory_trend > thresholds['max_memory_trend']:
            validation_results['passed'] = False
            validation_results['issues'].append(
                f"Memory trend {memory_trend:.2f} exceeds threshold {thresholds['max_memory_trend']}"
            )
        
        error_count = final_analysis.get('error_count', 0)
        if error_count > thresholds['max_error_count']:
            validation_results['passed'] = False
            validation_results['issues'].append(
                f"Error count {error_count} exceeds threshold {thresholds['max_error_count']}"
            )
        
        if stability_result.get('performance_degradation') and not thresholds['allow_performance_degradation']:
            validation_results['passed'] = False
            validation_results['issues'].append("Performance degradation detected during extended operation")
        
        logger.info(f"Extended operation validation {'PASSED' if validation_results['passed'] else 'FAILED'}")
        return validation_results
    
    def validate_optimization_effectiveness(self) -> Dict[str, Any]:
        """Validate that performance optimizations are effective."""
        logger.info("Validating optimization effectiveness...")
        
        # Get baseline performance
        baseline_report = profiler.get_performance_report()
        
        # Run optimization
        optimization_result = optimizer.optimize_system()
        
        # Get post-optimization performance
        time.sleep(1)  # Allow optimizations to take effect
        optimized_report = profiler.get_performance_report()
        
        validation_results = {
            'baseline_report': baseline_report,
            'optimization_result': optimization_result,
            'optimized_report': optimized_report,
            'passed': True,
            'issues': [],
            'improvements': []
        }
        
        # Check if optimizations were applied
        applied_optimizations = optimization_result.get('applied_optimizations', [])
        if not applied_optimizations:
            validation_results['issues'].append("No optimizations were applied")
        else:
            validation_results['improvements'].append(f"Applied {len(applied_optimizations)} optimizations")
        
        # Compare memory usage (if applicable)
        baseline_memory = baseline_report.get('memory_analysis', {}).get('current_memory_mb', 0)
        optimized_memory = optimized_report.get('memory_analysis', {}).get('current_memory_mb', 0)
        
        if baseline_memory > 0 and optimized_memory > 0:
            memory_improvement = baseline_memory - optimized_memory
            if memory_improvement > 0:
                validation_results['improvements'].append(f"Reduced memory usage by {memory_improvement:.2f}MB")
        
        # Check system health improvement
        baseline_health = baseline_report.get('system_health', {}).get('score', 0)
        optimized_health = optimized_report.get('system_health', {}).get('score', 0)
        
        if optimized_health > baseline_health:
            validation_results['improvements'].append(
                f"Improved system health score from {baseline_health} to {optimized_health}"
            )
        
        logger.info(f"Optimization validation {'PASSED' if validation_results['passed'] else 'FAILED'}")
        return validation_results
    
    def _simulate_normal_operation(self):
        """Simulate normal system operation."""
        # Simulate data processing
        data = [i * i for i in range(1000)]
        result = sum(data)
        
        # Simulate memory allocation and cleanup
        temp_data = [i for i in range(500)]
        del temp_data
        
        return result
    
    def _create_mock_strategy(self, strategy_id: int):
        """Create a mock strategy for testing."""
        class MockStrategy:
            def __init__(self, strategy_id):
                self.id = strategy_id
                self.name = f"mock_strategy_{strategy_id}"
            
            def execute(self):
                # Simulate strategy execution
                time.sleep(0.1)
                return f"Strategy {self.id} executed"
        
        return MockStrategy(strategy_id)
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete performance validation suite."""
        logger.info("Starting full performance validation suite...")
        
        validation_start = time.time()
        
        # Run all validation tests
        results = {
            'startup_performance': self.validate_startup_performance(),
            'memory_usage': self.validate_memory_usage(duration_minutes=2),  # Shorter for testing
            'multi_strategy_performance': self.validate_multi_strategy_performance(strategy_count=3),
            'extended_operation_stability': self.validate_extended_operation_stability(duration_minutes=3),
            'optimization_effectiveness': self.validate_optimization_effectiveness()
        }
        
        validation_duration = time.time() - validation_start
        
        # Calculate overall results
        all_passed = all(result.get('passed', False) for result in results.values())
        total_issues = sum(len(result.get('issues', [])) for result in results.values())
        
        overall_results = {
            'timestamp': time.time(),
            'validation_duration': validation_duration,
            'overall_passed': all_passed,
            'total_issues': total_issues,
            'individual_results': results,
            'summary': self._generate_validation_summary(results)
        }
        
        logger.info(f"Full validation {'PASSED' if all_passed else 'FAILED'} in {validation_duration:.2f}s")
        
        return overall_results
    
    def _generate_validation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary."""
        summary = {
            'tests_run': len(results),
            'tests_passed': sum(1 for result in results.values() if result.get('passed', False)),
            'tests_failed': sum(1 for result in results.values() if not result.get('passed', False)),
            'critical_issues': [],
            'recommendations': []
        }
        
        # Identify critical issues
        for test_name, result in results.items():
            if not result.get('passed', False):
                for issue in result.get('issues', []):
                    summary['critical_issues'].append(f"{test_name}: {issue}")
        
        # Generate recommendations
        if summary['tests_failed'] > 0:
            summary['recommendations'].append("Review failed tests and address performance issues")
        
        if any('memory' in issue.lower() for issues in [r.get('issues', []) for r in results.values()] for issue in issues):
            summary['recommendations'].append("Investigate memory usage patterns and potential leaks")
        
        if any('cpu' in issue.lower() for issues in [r.get('issues', []) for r in results.values()] for issue in issues):
            summary['recommendations'].append("Optimize CPU-intensive operations")
        
        return summary
    
    def save_validation_report(self, results: Dict[str, Any], filename: str = None):
        """Save validation report to file."""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"performance_validation_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Validation report saved to {filepath}")
        
        # Also save a human-readable summary
        summary_filepath = filepath.with_suffix('.txt')
        self._save_human_readable_summary(results, summary_filepath)
    
    def _save_human_readable_summary(self, results: Dict[str, Any], filepath: Path):
        """Save human-readable validation summary."""
        with open(filepath, 'w') as f:
            f.write("GeneBot Performance Validation Report\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Validation Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Handle both full validation and individual test results
            if 'overall_passed' in results:
                f.write(f"Overall Result: {'PASSED' if results['overall_passed'] else 'FAILED'}\n")
                f.write(f"Total Duration: {results['validation_duration']:.2f} seconds\n")
                f.write(f"Total Issues: {results['total_issues']}\n\n")
                individual_results = results['individual_results']
            else:
                # Single test result
                test_name = list(results.keys())[0]
                test_result = results[test_name]
                passed = test_result.get('passed', False)
                f.write(f"Test Result: {'PASSED' if passed else 'FAILED'}\n")
                f.write(f"Test Type: {test_name}\n")
                f.write(f"Issues: {len(test_result.get('issues', []))}\n\n")
                individual_results = results
            
            # Individual test results
            f.write("Test Results:\n")
            f.write("-" * 13 + "\n")
            
            for test_name, result in individual_results.items():
                status = "PASSED" if result.get('passed', False) else "FAILED"
                f.write(f"{test_name}: {status}\n")
                
                if result.get('issues'):
                    for issue in result['issues']:
                        f.write(f"  - {issue}\n")
                f.write("\n")
            
            # Summary and recommendations (only for full validation)
            if 'summary' in results:
                summary = results['summary']
                f.write("Summary:\n")
                f.write("-" * 8 + "\n")
                f.write(f"Tests Run: {summary['tests_run']}\n")
                f.write(f"Tests Passed: {summary['tests_passed']}\n")
                f.write(f"Tests Failed: {summary['tests_failed']}\n\n")
                
                if summary['recommendations']:
                    f.write("Recommendations:\n")
                    f.write("-" * 15 + "\n")
                    for rec in summary['recommendations']:
                        f.write(f"- {rec}\n")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="GeneBot Performance Validation")
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--test', choices=['startup', 'memory', 'multi-strategy', 'stability', 'optimization', 'all'],
                       default='all', help='Specific test to run')
    parser.add_argument('--duration', type=int, default=5, help='Duration in minutes for time-based tests')
    parser.add_argument('--strategies', type=int, default=5, help='Number of strategies for multi-strategy test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = PerformanceValidator(output_dir=args.output_dir)
    
    try:
        if args.test == 'all':
            results = validator.run_full_validation()
        elif args.test == 'startup':
            startup_result = validator.validate_startup_performance()
            results = {'startup_performance': startup_result}
        elif args.test == 'memory':
            results = {'memory_usage': validator.validate_memory_usage(duration_minutes=args.duration)}
        elif args.test == 'multi-strategy':
            results = {'multi_strategy_performance': validator.validate_multi_strategy_performance(strategy_count=args.strategies)}
        elif args.test == 'stability':
            results = {'extended_operation_stability': validator.validate_extended_operation_stability(duration_minutes=args.duration)}
        elif args.test == 'optimization':
            results = {'optimization_effectiveness': validator.validate_optimization_effectiveness()}
        
        # Save results
        validator.save_validation_report(results)
        
        # Print summary
        if args.test == 'all':
            overall_passed = results.get('overall_passed', False)
            print(f"\nValidation {'PASSED' if overall_passed else 'FAILED'}")
            print(f"Duration: {results.get('validation_duration', 0):.2f} seconds")
            print(f"Issues: {results.get('total_issues', 0)}")
        else:
            test_result = list(results.values())[0]
            passed = test_result.get('passed', False)
            print(f"\nTest {'PASSED' if passed else 'FAILED'}")
            if test_result.get('issues'):
                print("Issues:")
                for issue in test_result['issues']:
                    print(f"  - {issue}")
        
        if args.test == 'all':
            return 0 if results.get('overall_passed', False) else 1
        else:
            return 0 if list(results.values())[0].get('passed', False) else 1
        
    except Exception as e:
        import traceback
        logger.error(f"Validation failed with error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())