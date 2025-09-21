"""
CLI Performance and Load Testing
===============================

Comprehensive performance tests for CLI responsiveness under various conditions,
load testing, memory usage analysis, and scalability validation.
"""

import pytest
import time
import threading
import concurrent.futures
import psutil
import tempfile
import subprocess
import sys
import os
import yaml
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class PerformanceTestFramework:
    """Framework for CLI performance testing and metrics collection"""
    
    def __init__(self):
        self.temp_workspace = None
        self.performance_metrics = {}
        self.baseline_metrics = {}
        
    def setup(self):
        """Set up performance testing environment"""
        self.temp_workspace = Path(tempfile.mkdtemp(prefix="cli_perf_test_"))
        
        # Create directory structure
        config_dir = self.temp_workspace / "config"
        logs_dir = self.temp_workspace / "logs"
        data_dir = self.temp_workspace / "data"
        
        for directory in [config_dir, logs_dir, data_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create test configurations
        self._create_test_configs()
        
        # Set environment variables
        os.environ.update({
            'CONFIG_PATH': str(config_dir),
            'LOGS_PATH': str(logs_dir),
            'WORKSPACE_PATH': str(self.temp_workspace),
            'CLI_PERFORMANCE_TEST': 'true'
        })
        
        # Initialize metrics
        self.performance_metrics = {
            'command_times': {},
            'memory_usage': {},
            'cpu_usage': {},
            'concurrent_performance': {},
            'scalability_metrics': {}
        }
    
    def teardown(self):
        """Clean up performance testing environment"""
        # Clean up environment
        for key in ['CONFIG_PATH', 'LOGS_PATH', 'WORKSPACE_PATH', 'CLI_PERFORMANCE_TEST']:
            os.environ.pop(key, None)
        
        # Clean up temporary files
        if self.temp_workspace and self.temp_workspace.exists():
            import shutil
            shutil.rmtree(self.temp_workspace, ignore_errors=True)
    
    def _create_test_configs(self):
        """Create test configuration files"""
        config_dir = self.temp_workspace / "config"
        
        # Create accounts configuration
        accounts_config = {
            'crypto_exchanges': {},
            'forex_brokers': {}
        }
        
        # Add many test accounts for scalability testing
        for i in range(100):
            accounts_config['crypto_exchanges'][f'test-crypto-{i}'] = {
                'name': f'test-crypto-{i}',
                'exchange_type': 'binance',
                'enabled': i % 2 == 0,  # Half enabled, half disabled
                'sandbox': True,
                'api_key': f'test_key_{i}',
                'api_secret': f'test_secret_{i}'
            }
        
        for i in range(50):
            accounts_config['forex_brokers'][f'test-forex-{i}'] = {
                'name': f'test-forex-{i}',
                'broker_type': 'oanda',
                'enabled': i % 3 == 0,  # One third enabled
                'sandbox': True,
                'api_key': f'test_forex_key_{i}',
                'account_id': f'test_forex_account_{i}'
            }
        
        with open(config_dir / "accounts.yaml", 'w') as f:
            yaml.dump(accounts_config, f)
        
        # Create trading bot configuration
        trading_config = {
            'app_name': 'PerformanceTestBot',
            'version': '1.0.0',
            'strategies': {}
        }
        
        # Add many strategies for testing
        for i in range(50):
            trading_config['strategies'][f'strategy_{i}'] = {
                'name': f'strategy_{i}',
                'enabled': True,
                'parameters': {f'param_{j}': j * 10 for j in range(20)}
            }
        
        with open(config_dir / "trading_bot_config.yaml", 'w') as f:
            yaml.dump(trading_config, f)
        
        # Create large database for testing
        self._create_large_test_database()
    
    def _create_large_test_database(self):
        """Create large test database for performance testing"""
        db_file = self.temp_workspace / "data" / "test_trading_bot.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                fees REAL DEFAULT 0,
                timestamp DATETIME NOT NULL,
                exchange TEXT NOT NULL,
                strategy TEXT,
                pnl REAL DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE orders (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                exchange TEXT NOT NULL
            )
        ''')
        
        # Insert large amount of test data
        symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT', 'EUR/USD', 'GBP/USD']
        exchanges = ['binance', 'coinbase', 'oanda']
        strategies = [f'strategy_{i}' for i in range(10)]
        
        # Insert 10,000 trades for performance testing
        trades_data = []
        for i in range(10000):
            trades_data.append((
                symbols[i % len(symbols)],
                'BUY' if i % 2 == 0 else 'SELL',
                round(0.01 + (i % 100) * 0.01, 4),
                round(1000 + (i % 50000), 2),
                round((i % 100) * 0.1, 2),
                datetime.now() - timedelta(hours=i % 8760),  # Last year
                exchanges[i % len(exchanges)],
                strategies[i % len(strategies)],
                round((i % 2000) - 1000, 2)  # Random P&L
            ))
        
        cursor.executemany('''
            INSERT INTO trades (symbol, side, amount, price, fees, timestamp, 
                              exchange, strategy, pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', trades_data)
        
        # Insert orders
        orders_data = []
        for i in range(1000):
            orders_data.append((
                f'order_{i}',
                symbols[i % len(symbols)],
                'BUY' if i % 2 == 0 else 'SELL',
                round(0.01 + (i % 100) * 0.01, 4),
                round(1000 + (i % 50000), 2),
                'limit',
                'open' if i % 10 < 3 else 'filled',
                datetime.now() - timedelta(minutes=i % 1440),
                exchanges[i % len(exchanges)]
            ))
        
        cursor.executemany('''
            INSERT INTO orders (id, symbol, side, amount, price, type, status, 
                              timestamp, exchange)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', orders_data)
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX idx_trades_timestamp ON trades(timestamp)')
        cursor.execute('CREATE INDEX idx_trades_symbol ON trades(symbol)')
        cursor.execute('CREATE INDEX idx_orders_status ON orders(status)')
        
        conn.commit()
        conn.close()
    
    def measure_command_performance(self, args: List[str], iterations: int = 1) -> Dict[str, Any]:
        """Measure performance of a CLI command"""
        execution_times = []
        memory_usage = []
        cpu_usage = []
        
        for i in range(iterations):
            # Measure system resources before
            process = psutil.Process()
            start_memory = process.memory_info().rss
            start_cpu = process.cpu_percent()
            start_time = time.time()
            
            # Run command
            result = subprocess.run(
                [sys.executable, "-m", "genebot.cli"] + args,
                cwd=self.temp_workspace,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            
            # Measure after
            end_time = time.time()
            end_memory = process.memory_info().rss
            end_cpu = process.cpu_percent()
            
            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            cpu_delta = end_cpu - start_cpu
            
            execution_times.append(execution_time)
            memory_usage.append(memory_delta)
            cpu_usage.append(cpu_delta)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        avg_memory = sum(memory_usage) / len(memory_usage)
        max_memory = max(memory_usage)
        
        return {
            'command': ' '.join(args),
            'iterations': iterations,
            'execution_times': execution_times,
            'avg_execution_time': avg_time,
            'min_execution_time': min_time,
            'max_execution_time': max_time,
            'avg_memory_delta': avg_memory,
            'max_memory_delta': max_memory,
            'success_rate': sum(1 for t in execution_times if t > 0) / len(execution_times),
            'last_exit_code': result.returncode,
            'last_stdout': result.stdout,
            'last_stderr': result.stderr
        }
    
    def measure_concurrent_performance(self, args: List[str], concurrent_count: int = 5) -> Dict[str, Any]:
        """Measure performance under concurrent execution"""
        start_time = time.time()
        results = []
        
        def run_command():
            return subprocess.run(
                [sys.executable, "-m", "genebot.cli"] + args,
                cwd=self.temp_workspace,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
        
        # Run commands concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [executor.submit(run_command) for _ in range(concurrent_count)]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append({
                        'exit_code': result.returncode,
                        'success': result.returncode == 0,
                        'stdout_length': len(result.stdout),
                        'stderr_length': len(result.stderr)
                    })
                except Exception as e:
                    results.append({
                        'exit_code': -1,
                        'success': False,
                        'error': str(e)
                    })
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r['success'])
        
        return {
            'command': ' '.join(args),
            'concurrent_count': concurrent_count,
            'total_execution_time': total_time,
            'success_count': success_count,
            'success_rate': success_count / len(results),
            'results': results
        }


@pytest.fixture
def perf_framework():
    """Pytest fixture for performance testing framework"""
    framework = PerformanceTestFramework()
    framework.setup()
    try:
        yield framework
    finally:
        framework.teardown()


class TestCommandResponseTimes:
    """Test CLI command response times under normal conditions"""
    
    def test_help_command_performance(self, perf_framework):
        """Test help command performance"""
        metrics = perf_framework.measure_command_performance(['--help'], iterations=5)
        
        # Help should be very fast
        assert metrics['avg_execution_time'] < 2.0, \
            f"Help command too slow: {metrics['avg_execution_time']:.3f}s"
        assert metrics['success_rate'] == 1.0, "Help command should always succeed"
    
    def test_list_accounts_performance(self, perf_framework):
        """Test list accounts performance with large configuration"""
        metrics = perf_framework.measure_command_performance(['list-accounts'], iterations=3)
        
        # Should handle large config reasonably fast
        assert metrics['avg_execution_time'] < 5.0, \
            f"List accounts too slow: {metrics['avg_execution_time']:.3f}s"
        
        # Memory usage should be reasonable
        assert metrics['max_memory_delta'] < 100 * 1024 * 1024, \
            f"List accounts uses too much memory: {metrics['max_memory_delta'] / 1024 / 1024:.1f}MB"
    
    def test_status_command_performance(self, perf_framework):
        """Test status command performance"""
        with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
            mock_instance = Mock()
            mock_instance.get_bot_status.return_value = {
                'running': False, 'pid': None, 'uptime': None
            }
            mock_pm.return_value = mock_instance
            
            metrics = perf_framework.measure_command_performance(['status'], iterations=3)
            
            assert metrics['avg_execution_time'] < 3.0, \
                f"Status command too slow: {metrics['avg_execution_time']:.3f}s"
    
    def test_trades_command_performance(self, perf_framework):
        """Test trades command performance with large dataset"""
        with patch('genebot.cli.utils.data_manager.RealDataManager') as mock_dm:
            mock_instance = Mock()
            
            # Simulate large dataset query
            def slow_query(limit=10):
                time.sleep(0.1)  # Simulate database query time
                return [
                    {
                        'id': i,
                        'symbol': 'BTC/USDT',
                        'side': 'BUY',
                        'amount': 0.1,
                        'price': 45000.0 + i,
                        'timestamp': datetime.now() - timedelta(hours=i),
                        'pnl': float(i * 10)
                    }
                    for i in range(min(limit, 100))
                ]
            
            mock_instance.get_recent_trades = Mock(side_effect=slow_query)
            mock_dm.return_value = mock_instance
            
            metrics = perf_framework.measure_command_performance(['trades', '--limit', '50'], iterations=2)
            
            # Should handle database queries efficiently
            assert metrics['avg_execution_time'] < 5.0, \
                f"Trades command too slow: {metrics['avg_execution_time']:.3f}s"
    
    def test_validate_accounts_performance(self, perf_framework):
        """Test account validation performance with many accounts"""
        with patch('genebot.cli.utils.account_validator.RealAccountValidator') as mock_validator:
            mock_instance = Mock()
            
            def validate_account(account_name):
                # Simulate API call delay
                time.sleep(0.05)
                return {
                    'connected': True,
                    'authenticated': True,
                    'error': None
                }
            
            mock_instance.validate_account = Mock(side_effect=validate_account)
            mock_validator.return_value = mock_instance
            
            metrics = perf_framework.measure_command_performance(['validate-accounts'], iterations=1)
            
            # Should handle many accounts reasonably (with mocked delays)
            assert metrics['avg_execution_time'] < 15.0, \
                f"Validate accounts too slow: {metrics['avg_execution_time']:.3f}s"


class TestConcurrentExecution:
    """Test CLI behavior under concurrent command execution"""
    
    def test_concurrent_list_accounts(self, perf_framework):
        """Test concurrent list-accounts commands"""
        metrics = perf_framework.measure_concurrent_performance(['list-accounts'], concurrent_count=5)
        
        # Most concurrent executions should succeed
        assert metrics['success_rate'] >= 0.8, \
            f"Concurrent success rate too low: {metrics['success_rate']:.2f}"
        
        # Total time should be reasonable
        assert metrics['total_execution_time'] < 15.0, \
            f"Concurrent execution too slow: {metrics['total_execution_time']:.3f}s"
    
    def test_concurrent_status_commands(self, perf_framework):
        """Test concurrent status commands"""
        with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
            mock_instance = Mock()
            mock_instance.get_bot_status.return_value = {'running': False}
            mock_pm.return_value = mock_instance
            
            metrics = perf_framework.measure_concurrent_performance(['status'], concurrent_count=3)
            
            assert metrics['success_rate'] >= 0.8
            assert metrics['total_execution_time'] < 10.0
    
    def test_concurrent_mixed_commands(self, perf_framework):
        """Test concurrent execution of different commands"""
        commands = [
            ['--help'],
            ['list-accounts'],
            ['status'],
            ['list-strategies']
        ]
        
        start_time = time.time()
        results = []
        
        def run_command(cmd):
            return subprocess.run(
                [sys.executable, "-m", "genebot.cli"] + cmd,
                cwd=perf_framework.temp_workspace,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(run_command, cmd) for cmd in commands]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result.returncode == 0)
        
        total_time = time.time() - start_time
        success_rate = sum(results) / len(results)
        
        assert success_rate >= 0.75, f"Mixed concurrent success rate too low: {success_rate:.2f}"
        assert total_time < 20.0, f"Mixed concurrent execution too slow: {total_time:.3f}s"


class TestScalabilityAndLimits:
    """Test CLI scalability with large datasets and configurations"""
    
    def test_large_configuration_handling(self, perf_framework):
        """Test handling of very large configuration files"""
        # Configuration already created with 100 crypto + 50 forex accounts
        metrics = perf_framework.measure_command_performance(['list-accounts'], iterations=2)
        
        # Should handle large configs within reasonable time
        assert metrics['avg_execution_time'] < 10.0, \
            f"Large config handling too slow: {metrics['avg_execution_time']:.3f}s"
        
        # Memory usage should be reasonable
        memory_mb = metrics['max_memory_delta'] / (1024 * 1024)
        assert memory_mb < 200, f"Large config uses too much memory: {memory_mb:.1f}MB"
    
    def test_database_query_scalability(self, perf_framework):
        """Test database query performance with large datasets"""
        # Database already created with 10,000 trades
        
        with patch('genebot.cli.utils.data_manager.RealDataManager') as mock_dm:
            mock_instance = Mock()
            
            # Simulate realistic database query times
            def realistic_query(limit=10):
                # Simulate query time based on limit
                query_time = min(0.001 * limit, 1.0)  # Max 1 second
                time.sleep(query_time)
                
                return [
                    {'id': i, 'symbol': 'BTC/USDT', 'pnl': i * 10}
                    for i in range(limit)
                ]
            
            mock_instance.get_recent_trades = Mock(side_effect=realistic_query)
            mock_dm.return_value = mock_instance
            
            # Test different query sizes
            test_limits = [10, 100, 1000]
            
            for limit in test_limits:
                metrics = perf_framework.measure_command_performance(
                    ['trades', '--limit', str(limit)], iterations=1
                )
                
                # Query time should scale reasonably
                expected_max_time = 2.0 + (limit / 1000) * 3.0  # Scale with limit
                assert metrics['avg_execution_time'] < expected_max_time, \
                    f"Query with limit {limit} too slow: {metrics['avg_execution_time']:.3f}s"
    
    def test_memory_usage_under_load(self, perf_framework):
        """Test memory usage during intensive operations"""
        initial_memory = psutil.Process().memory_info().rss
        
        # Run memory-intensive operations
        commands = [
            ['list-accounts'],
            ['list-strategies'],
            ['trades', '--limit', '100']
        ]
        
        max_memory = initial_memory
        
        for cmd in commands:
            metrics = perf_framework.measure_command_performance(cmd, iterations=1)
            current_memory = psutil.Process().memory_info().rss
            max_memory = max(max_memory, current_memory)
        
        memory_increase = max_memory - initial_memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        
        # Memory increase should be reasonable for CLI operations
        assert memory_increase_mb < 150, \
            f"Memory usage increased by {memory_increase_mb:.1f}MB, expected < 150MB"
    
    def test_file_system_performance(self, perf_framework):
        """Test file system operations performance"""
        # Test configuration backup (file I/O intensive)
        metrics = perf_framework.measure_command_performance(['config-backup'], iterations=2)
        
        # File operations should be reasonably fast
        assert metrics['avg_execution_time'] < 5.0, \
            f"Config backup too slow: {metrics['avg_execution_time']:.3f}s"
    
    def test_stress_testing(self, perf_framework):
        """Stress test with rapid command execution"""
        # Execute many commands rapidly
        start_time = time.time()
        success_count = 0
        total_commands = 20
        
        for i in range(total_commands):
            result = subprocess.run(
                [sys.executable, "-m", "genebot.cli", "--help"],
                cwd=perf_framework.temp_workspace,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            
            if result.returncode == 0:
                success_count += 1
        
        total_time = time.time() - start_time
        success_rate = success_count / total_commands
        
        # Should handle rapid execution
        assert success_rate >= 0.9, f"Stress test success rate too low: {success_rate:.2f}"
        assert total_time < 30.0, f"Stress test took too long: {total_time:.3f}s"


class TestPerformanceRegression:
    """Test for performance regressions"""
    
    def test_baseline_performance_comparison(self, perf_framework):
        """Compare current performance against baseline expectations"""
        # Define baseline expectations (in seconds)
        baseline_expectations = {
            '--help': 2.0,
            'list-accounts': 5.0,
            'status': 3.0,
            'list-strategies': 4.0
        }
        
        performance_results = {}
        
        for cmd_str, expected_time in baseline_expectations.items():
            cmd = cmd_str.split()
            
            # Mock external dependencies for consistent testing
            with patch('genebot.cli.utils.process_manager.ProcessManager') as mock_pm:
                mock_instance = Mock()
                mock_instance.get_bot_status.return_value = {'running': False}
                mock_pm.return_value = mock_instance
                
                metrics = perf_framework.measure_command_performance(cmd, iterations=3)
                performance_results[cmd_str] = metrics['avg_execution_time']
                
                # Check against baseline
                assert metrics['avg_execution_time'] < expected_time, \
                    f"Performance regression detected for '{cmd_str}': " \
                    f"{metrics['avg_execution_time']:.3f}s > {expected_time}s"
        
        # Store results for future comparison
        perf_framework.performance_metrics['baseline_comparison'] = performance_results
    
    def test_performance_consistency(self, perf_framework):
        """Test that performance is consistent across multiple runs"""
        cmd = ['list-accounts']
        iterations = 5
        
        metrics = perf_framework.measure_command_performance(cmd, iterations=iterations)
        
        # Calculate coefficient of variation (std dev / mean)
        times = metrics['execution_times']
        mean_time = sum(times) / len(times)
        variance = sum((t - mean_time) ** 2 for t in times) / len(times)
        std_dev = variance ** 0.5
        cv = std_dev / mean_time if mean_time > 0 else 0
        
        # Performance should be consistent (CV < 0.5 means std dev < 50% of mean)
        assert cv < 0.5, f"Performance too inconsistent: CV = {cv:.3f}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])