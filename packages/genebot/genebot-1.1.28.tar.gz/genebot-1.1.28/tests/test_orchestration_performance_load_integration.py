"""
Performance and load testing for orchestration system integration.
"""

import pytest
import asyncio
import time
import psutil
import os
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

from src.orchestration.orchestrator import StrategyOrchestrator
from src.orchestration.config import (
    OrchestratorConfig, AllocationConfig, RiskConfig, MonitoringConfig,
    StrategyConfig, AllocationMethod, RebalanceFrequency
)
from src.orchestration.interfaces import (
    TradingSignal, Portfolio, Position, UnifiedMarketData, PerformanceMetrics
)


class TestHighFrequencyDataProcessing:
    """Test orchestrator performance with high-frequency data."""
    
    @pytest.fixture
    def high_frequency_config(self):
        """Create configuration optimized for high-frequency processing."""
        return OrchestratorConfig(
            max_concurrent_strategies=20,
            enable_parallel_processing=True,
            max_worker_threads=16,
            enable_data_batching=True,
            batch_size=100,
            processing_timeout=timedelta(seconds=1),
            allocation=AllocationConfig(
                method=AllocationMethod.PERFORMANCE_BASED,
                rebalance_frequency=RebalanceFrequency.HOURLY  # Less frequent for performance
            ),
            monitoring=MonitoringConfig(
                metrics_collection_interval=30,  # Less frequent collection
                enable_detailed_logging=False  # Reduce logging overhead
            ),
            strategies=[
                StrategyConfig(type=f"HighFreqStrategy", name=f"hf_strategy_{i}", enabled=True)
                for i in range(15)
            ]
        )
    
    @pytest.fixture
    def hf_orchestrator(self, high_frequency_config):
        """Create orchestrator for high-frequency testing."""
        return StrategyOrchestrator(high_frequency_config)
    
    def generate_high_frequency_data(self, num_symbols=10, num_updates=1000, time_interval_ms=100):
        """Generate high-frequency market data."""
        symbols = [f"SYMBOL_{i}" for i in range(num_symbols)]
        market_data = []
        
        base_time = datetime.now()
        base_prices = {symbol: 100.0 + i * 10 for i, symbol in enumerate(symbols)}
        
        for update in range(num_updates):
            timestamp = base_time + timedelta(milliseconds=update * time_interval_ms)
            
            for symbol in symbols:
                # Simulate realistic price movement
                price_change = np.random.normal(0, 0.001)  # 0.1% volatility
                base_prices[symbol] *= (1 + price_change)
                
                price = base_prices[symbol]
                spread = price * 0.0001  # 1 basis point spread
                
                market_data.append(UnifiedMarketData(
                    symbol=symbol,
                    timestamp=timestamp,
                    open=price,
                    high=price + spread,
                    low=price - spread,
                    close=price + price_change * price,
                    volume=np.random.randint(100, 1000),
                    market_type="crypto"
                ))
        
        return market_data
    
    @pytest.mark.asyncio
    async def test_high_frequency_data_throughput(self, hf_orchestrator):
        """Test throughput with high-frequency market data."""
        # Generate large dataset
        market_data = self.generate_high_frequency_data(
            num_symbols=5, num_updates=500, time_interval_ms=50
        )
        
        with patch.object(hf_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            # Mock fast processing
            mock_process.return_value = []
            
            await hf_orchestrator.start()
            
            # Measure processing throughput
            start_time = time.time()
            processed_count = 0
            
            # Process data in batches
            batch_size = 50
            for i in range(0, len(market_data), batch_size):
                batch = market_data[i:i + batch_size]
                await hf_orchestrator.process_market_data(batch)
                processed_count += len(batch)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Calculate throughput metrics
            throughput = processed_count / processing_time
            
            # Verify performance requirements
            assert throughput > 1000  # Should process >1000 data points per second
            assert processing_time < 5.0  # Should complete within 5 seconds
            
            # Verify all data was processed
            assert processed_count == len(market_data)
            
            await hf_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_symbol_processing(self, hf_orchestrator):
        """Test concurrent processing of multiple symbols."""
        symbols = ["BTCUSD", "ETHUSD", "LTCUSD", "ADAUSD", "DOTUSD"]
        
        # Generate data for each symbol
        symbol_data = {}
        for symbol in symbols:
            symbol_data[symbol] = [
                UnifiedMarketData(
                    symbol=symbol, timestamp=datetime.now() + timedelta(seconds=i),
                    open=50000 + i, high=50100 + i, low=49900 + i, close=50050 + i,
                    volume=1000, market_type="crypto"
                ) for i in range(100)
            ]
        
        with patch.object(hf_orchestrator.strategy_engine, 'process_market_data_by_symbol') as mock_process:
            
            # Mock concurrent processing
            async def concurrent_symbol_process(symbol, data):
                await asyncio.sleep(0.01)  # Simulate processing time
                return len(data)  # Return number of processed items
            
            mock_process.side_effect = concurrent_symbol_process
            
            await hf_orchestrator.start()
            
            # Process all symbols concurrently
            start_time = time.time()
            
            tasks = []
            for symbol, data in symbol_data.items():
                task = asyncio.create_task(
                    hf_orchestrator.process_symbol_data_concurrent(symbol, data)
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            concurrent_time = end_time - start_time
            
            # Verify concurrent processing was faster than sequential
            # Sequential time would be approximately: len(symbols) * 0.01 * 100 = 5 seconds
            # Concurrent should be much faster
            assert concurrent_time < 2.0  # Should be much faster than sequential
            
            # Verify all symbols were processed
            assert len(results) == len(symbols)
            assert all(result == 100 for result in results)  # Each symbol had 100 data points
            
            await hf_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_memory_efficiency_under_load(self, hf_orchestrator):
        """Test memory efficiency during high-load processing."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate large dataset
        large_dataset = self.generate_high_frequency_data(
            num_symbols=20, num_updates=1000, time_interval_ms=10
        )
        
        with patch.object(hf_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await hf_orchestrator.start()
            
            # Process data in chunks to test memory management
            chunk_size = 200
            max_memory_growth = 0
            
            for i in range(0, len(large_dataset), chunk_size):
                chunk = large_dataset[i:i + chunk_size]
                await hf_orchestrator.process_market_data(chunk)
                
                # Check memory usage
                current_memory = process.memory_info().rss
                memory_growth = current_memory - initial_memory
                max_memory_growth = max(max_memory_growth, memory_growth)
                
                # Force garbage collection periodically
                if i % (chunk_size * 5) == 0:
                    import gc
                    gc.collect()
            
            final_memory = process.memory_info().rss
            final_memory_growth = final_memory - initial_memory
            
            # Memory growth should be reasonable
            max_acceptable_growth = 200 * 1024 * 1024  # 200MB
            assert max_memory_growth < max_acceptable_growth
            assert final_memory_growth < max_acceptable_growth
            
            await hf_orchestrator.stop()


class TestScalabilityTesting:
    """Test orchestrator scalability with increasing load."""
    
    @pytest.fixture
    def scalable_config(self):
        """Create configuration for scalability testing."""
        return OrchestratorConfig(
            max_concurrent_strategies=50,
            enable_parallel_processing=True,
            enable_adaptive_scaling=True,
            auto_scale_threshold=0.8,  # Scale when 80% capacity reached
            max_worker_threads=32,
            strategies=[
                StrategyConfig(type=f"ScalableStrategy", name=f"scalable_{i}", enabled=True)
                for i in range(30)
            ]
        )
    
    @pytest.fixture
    def scalable_orchestrator(self, scalable_config):
        """Create orchestrator for scalability testing."""
        return StrategyOrchestrator(scalable_config)
    
    @pytest.mark.asyncio
    async def test_strategy_count_scaling(self, scalable_orchestrator):
        """Test performance scaling with increasing strategy count."""
        strategy_counts = [5, 10, 20, 30]
        performance_results = {}
        
        with patch.object(scalable_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            market_data = [
                UnifiedMarketData(
                    symbol="BTCUSD", timestamp=datetime.now(),
                    open=50000, high=50100, low=49900, close=50050,
                    volume=1000, market_type="crypto"
                )
            ]
            
            await scalable_orchestrator.start()
            
            for count in strategy_counts:
                # Enable specific number of strategies
                active_strategies = [f"scalable_{i}" for i in range(count)]
                
                with patch.object(scalable_orchestrator.strategy_engine, 'get_active_strategies') as mock_active:
                    mock_active.return_value = active_strategies
                    
                    # Measure processing time
                    start_time = time.time()
                    
                    # Process multiple batches
                    for _ in range(10):
                        await scalable_orchestrator.process_market_data(market_data)
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    performance_results[count] = processing_time
            
            # Analyze scaling characteristics
            # Processing time should scale sub-linearly with strategy count
            time_5 = performance_results[5]
            time_30 = performance_results[30]
            
            # 6x strategies should not take 6x time (should be better due to parallelization)
            scaling_factor = time_30 / time_5
            assert scaling_factor < 4.0  # Should scale better than linear
            
            await scalable_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_data_volume_scaling(self, scalable_orchestrator):
        """Test performance scaling with increasing data volume."""
        data_volumes = [100, 500, 1000, 2000]
        performance_results = {}
        
        with patch.object(scalable_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await scalable_orchestrator.start()
            
            for volume in data_volumes:
                # Generate data of specified volume
                market_data = [
                    UnifiedMarketData(
                        symbol=f"SYMBOL_{i % 10}", timestamp=datetime.now() + timedelta(seconds=i),
                        open=50000 + i, high=50100 + i, low=49900 + i, close=50050 + i,
                        volume=1000, market_type="crypto"
                    ) for i in range(volume)
                ]
                
                # Measure processing time
                start_time = time.time()
                await scalable_orchestrator.process_market_data(market_data)
                end_time = time.time()
                
                processing_time = end_time - start_time
                performance_results[volume] = processing_time
            
            # Analyze data volume scaling
            # Should scale approximately linearly with data volume
            time_100 = performance_results[100]
            time_2000 = performance_results[2000]
            
            # 20x data should take roughly 20x time (linear scaling)
            scaling_factor = time_2000 / time_100
            assert 15 < scaling_factor < 25  # Allow some variance around 20x
            
            await scalable_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_user_scaling(self, scalable_orchestrator):
        """Test scaling with multiple concurrent users/requests."""
        concurrent_users = [1, 5, 10, 20]
        performance_results = {}
        
        with patch.object(scalable_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            market_data = [
                UnifiedMarketData(
                    symbol="BTCUSD", timestamp=datetime.now(),
                    open=50000, high=50100, low=49900, close=50050,
                    volume=1000, market_type="crypto"
                )
            ]
            
            await scalable_orchestrator.start()
            
            for user_count in concurrent_users:
                
                async def simulate_user_request():
                    """Simulate a user request."""
                    await scalable_orchestrator.process_market_data(market_data)
                    return True
                
                # Measure concurrent processing time
                start_time = time.time()
                
                # Create concurrent tasks
                tasks = [simulate_user_request() for _ in range(user_count)]
                results = await asyncio.gather(*tasks)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                performance_results[user_count] = processing_time
                
                # Verify all requests completed successfully
                assert all(results)
            
            # Analyze concurrent user scaling
            time_1 = performance_results[1]
            time_20 = performance_results[20]
            
            # 20 concurrent users should not take 20x time due to parallelization
            scaling_factor = time_20 / time_1
            assert scaling_factor < 10  # Should scale better than linear
            
            await scalable_orchestrator.stop()


class TestStressAndEnduranceTesting:
    """Test orchestrator under stress and endurance conditions."""
    
    @pytest.fixture
    def stress_config(self):
        """Create configuration for stress testing."""
        return OrchestratorConfig(
            max_concurrent_strategies=25,
            enable_parallel_processing=True,
            max_worker_threads=20,
            enable_circuit_breaker=True,
            circuit_breaker_threshold=0.5,
            enable_rate_limiting=True,
            max_requests_per_second=1000,
            strategies=[
                StrategyConfig(type=f"StressStrategy", name=f"stress_{i}", enabled=True)
                for i in range(20)
            ]
        )
    
    @pytest.fixture
    def stress_orchestrator(self, stress_config):
        """Create orchestrator for stress testing."""
        return StrategyOrchestrator(stress_config)
    
    @pytest.mark.asyncio
    async def test_sustained_high_load(self, stress_orchestrator):
        """Test orchestrator under sustained high load."""
        duration_minutes = 2  # Run for 2 minutes
        requests_per_second = 50
        
        market_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now(),
                open=50000, high=50100, low=49900, close=50050,
                volume=1000, market_type="crypto"
            )
        ]
        
        with patch.object(stress_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await stress_orchestrator.start()
            
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            
            request_count = 0
            error_count = 0
            response_times = []
            
            while time.time() < end_time:
                batch_start = time.time()
                
                # Send batch of requests
                tasks = []
                for _ in range(requests_per_second):
                    task = asyncio.create_task(
                        stress_orchestrator.process_market_data(market_data)
                    )
                    tasks.append(task)
                
                # Wait for batch completion
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Count errors
                    batch_errors = sum(1 for r in results if isinstance(r, Exception))
                    error_count += batch_errors
                    request_count += len(tasks)
                    
                    batch_end = time.time()
                    batch_time = batch_end - batch_start
                    response_times.append(batch_time)
                    
                    # Rate limiting - wait for next second
                    sleep_time = max(0, 1.0 - batch_time)
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                        
                except Exception as e:
                    error_count += requests_per_second
                    request_count += requests_per_second
            
            total_time = time.time() - start_time
            
            # Analyze stress test results
            error_rate = error_count / request_count if request_count > 0 else 1.0
            avg_response_time = np.mean(response_times) if response_times else float('inf')
            throughput = request_count / total_time
            
            # Verify stress test requirements
            assert error_rate < 0.05  # Less than 5% error rate
            assert avg_response_time < 2.0  # Average response time under 2 seconds
            assert throughput > 30  # Maintain >30 requests per second throughput
            
            # Verify orchestrator is still responsive
            assert stress_orchestrator.is_running is True
            
            await stress_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, stress_orchestrator):
        """Test for memory leaks during extended operation."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        market_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now(),
                open=50000, high=50100, low=49900, close=50050,
                volume=1000, market_type="crypto"
            )
        ]
        
        with patch.object(stress_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await stress_orchestrator.start()
            
            memory_samples = []
            
            # Run for extended period with memory monitoring
            for iteration in range(100):  # 100 iterations
                await stress_orchestrator.process_market_data(market_data)
                
                # Sample memory every 10 iterations
                if iteration % 10 == 0:
                    current_memory = process.memory_info().rss
                    memory_growth = current_memory - initial_memory
                    memory_samples.append(memory_growth)
                
                # Force garbage collection periodically
                if iteration % 20 == 0:
                    import gc
                    gc.collect()
            
            # Analyze memory growth pattern
            if len(memory_samples) > 2:
                # Check if memory growth is linear (indicating leak)
                memory_trend = np.polyfit(range(len(memory_samples)), memory_samples, 1)[0]
                
                # Memory growth should be minimal or decreasing
                max_acceptable_growth_per_sample = 1024 * 1024  # 1MB per sample
                assert memory_trend < max_acceptable_growth_per_sample
            
            final_memory = process.memory_info().rss
            total_growth = final_memory - initial_memory
            
            # Total memory growth should be reasonable
            max_acceptable_total_growth = 50 * 1024 * 1024  # 50MB
            assert total_growth < max_acceptable_total_growth
            
            await stress_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_recovery(self, stress_orchestrator):
        """Test recovery from resource exhaustion scenarios."""
        with patch.object(stress_orchestrator.resource_monitor, 'get_system_resources') as mock_resources, \
             patch.object(stress_orchestrator.circuit_breaker, 'is_open') as mock_circuit_breaker:
            
            # Simulate resource exhaustion
            resource_states = [
                {"cpu_usage": 95, "memory_usage": 90, "available_threads": 2},  # Exhausted
                {"cpu_usage": 85, "memory_usage": 80, "available_threads": 5},  # Recovering
                {"cpu_usage": 60, "memory_usage": 70, "available_threads": 15}  # Normal
            ]
            
            resource_index = 0
            def get_resources():
                nonlocal resource_index
                if resource_index < len(resource_states):
                    result = resource_states[resource_index]
                    resource_index += 1
                    return result
                return resource_states[-1]  # Return normal state
            
            mock_resources.side_effect = get_resources
            
            # Circuit breaker opens under stress, closes when recovered
            circuit_states = [True, True, False]  # Open, Open, Closed
            circuit_index = 0
            def circuit_breaker_state():
                nonlocal circuit_index
                if circuit_index < len(circuit_states):
                    result = circuit_states[circuit_index]
                    circuit_index += 1
                    return result
                return False  # Closed
            
            mock_circuit_breaker.side_effect = circuit_breaker_state
            
            await stress_orchestrator.start()
            
            market_data = [
                UnifiedMarketData(
                    symbol="BTCUSD", timestamp=datetime.now(),
                    open=50000, high=50100, low=49900, close=50050,
                    volume=1000, market_type="crypto"
                )
            ]
            
            # Test processing under different resource conditions
            results = []
            for i in range(3):
                try:
                    result = await stress_orchestrator.process_market_data_with_circuit_breaker(market_data)
                    results.append(("success", result))
                except Exception as e:
                    results.append(("error", str(e)))
            
            # Verify circuit breaker behavior
            # First two attempts should fail (circuit open)
            # Third attempt should succeed (circuit closed, resources recovered)
            assert results[0][0] == "error" or results[1][0] == "error"  # At least one failure
            assert results[2][0] == "success"  # Final attempt succeeds
            
            await stress_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_under_load(self, stress_orchestrator):
        """Test graceful degradation when system is overloaded."""
        with patch.object(stress_orchestrator.load_balancer, 'get_current_load') as mock_load, \
             patch.object(stress_orchestrator.degradation_manager, 'apply_degradation') as mock_degrade:
            
            # Simulate increasing load
            load_levels = [0.3, 0.6, 0.8, 0.95, 0.99]  # Increasing load
            load_index = 0
            
            def get_load():
                nonlocal load_index
                if load_index < len(load_levels):
                    result = load_levels[load_index]
                    load_index += 1
                    return result
                return 0.99  # High load
            
            mock_load.side_effect = get_load
            
            await stress_orchestrator.start()
            
            market_data = [
                UnifiedMarketData(
                    symbol="BTCUSD", timestamp=datetime.now(),
                    open=50000, high=50100, low=49900, close=50050,
                    volume=1000, market_type="crypto"
                )
            ]
            
            # Process data under increasing load
            for i in range(5):
                await stress_orchestrator.process_market_data_with_load_balancing(market_data)
            
            # Verify degradation was applied when load exceeded threshold
            degradation_calls = mock_degrade.call_args_list
            high_load_calls = [call for call in degradation_calls if call[0][0] > 0.8]
            
            assert len(high_load_calls) > 0  # Degradation should be applied under high load
            
            await stress_orchestrator.stop()


class TestPerformanceBenchmarking:
    """Benchmark orchestrator performance against requirements."""
    
    @pytest.fixture
    def benchmark_config(self):
        """Create configuration for benchmarking."""
        return OrchestratorConfig(
            max_concurrent_strategies=15,
            enable_parallel_processing=True,
            enable_performance_monitoring=True,
            strategies=[
                StrategyConfig(type=f"BenchmarkStrategy", name=f"benchmark_{i}", enabled=True)
                for i in range(10)
            ]
        )
    
    @pytest.fixture
    def benchmark_orchestrator(self, benchmark_config):
        """Create orchestrator for benchmarking."""
        return StrategyOrchestrator(benchmark_config)
    
    @pytest.mark.asyncio
    async def test_latency_benchmarks(self, benchmark_orchestrator):
        """Benchmark processing latency requirements."""
        market_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now(),
                open=50000, high=50100, low=49900, close=50050,
                volume=1000, market_type="crypto"
            )
        ]
        
        with patch.object(benchmark_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await benchmark_orchestrator.start()
            
            # Measure latency over multiple runs
            latencies = []
            
            for _ in range(100):  # 100 measurements
                start_time = time.perf_counter()
                await benchmark_orchestrator.process_market_data(market_data)
                end_time = time.perf_counter()
                
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                latencies.append(latency)
            
            # Calculate latency statistics
            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
            max_latency = np.max(latencies)
            
            # Verify latency requirements
            assert avg_latency < 100  # Average latency under 100ms
            assert p95_latency < 200  # 95th percentile under 200ms
            assert p99_latency < 500  # 99th percentile under 500ms
            assert max_latency < 1000  # Maximum latency under 1 second
            
            await benchmark_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_throughput_benchmarks(self, benchmark_orchestrator):
        """Benchmark throughput requirements."""
        # Generate test data
        market_data = [
            UnifiedMarketData(
                symbol=f"SYMBOL_{i % 5}", timestamp=datetime.now() + timedelta(seconds=i),
                open=50000 + i, high=50100 + i, low=49900 + i, close=50050 + i,
                volume=1000, market_type="crypto"
            ) for i in range(1000)  # 1000 data points
        ]
        
        with patch.object(benchmark_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await benchmark_orchestrator.start()
            
            # Measure throughput
            start_time = time.time()
            
            # Process data in batches
            batch_size = 100
            processed_count = 0
            
            for i in range(0, len(market_data), batch_size):
                batch = market_data[i:i + batch_size]
                await benchmark_orchestrator.process_market_data(batch)
                processed_count += len(batch)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Calculate throughput metrics
            throughput = processed_count / processing_time
            
            # Verify throughput requirements
            assert throughput > 500  # Should process >500 data points per second
            assert processing_time < 3.0  # Should complete within 3 seconds
            
            await benchmark_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_resource_utilization_benchmarks(self, benchmark_orchestrator):
        """Benchmark resource utilization efficiency."""
        process = psutil.Process(os.getpid())
        
        # Baseline measurements
        initial_cpu_percent = process.cpu_percent()
        initial_memory = process.memory_info().rss
        
        market_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now(),
                open=50000, high=50100, low=49900, close=50050,
                volume=1000, market_type="crypto"
            )
        ]
        
        with patch.object(benchmark_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await benchmark_orchestrator.start()
            
            # Run workload and measure resource usage
            cpu_samples = []
            memory_samples = []
            
            for i in range(50):  # 50 iterations
                await benchmark_orchestrator.process_market_data(market_data)
                
                # Sample resource usage
                if i % 5 == 0:  # Every 5th iteration
                    cpu_percent = process.cpu_percent()
                    memory_info = process.memory_info().rss
                    
                    cpu_samples.append(cpu_percent)
                    memory_samples.append(memory_info - initial_memory)
            
            # Calculate resource utilization statistics
            avg_cpu = np.mean(cpu_samples) if cpu_samples else 0
            max_memory_growth = max(memory_samples) if memory_samples else 0
            
            # Verify resource utilization requirements
            assert avg_cpu < 50  # Average CPU usage under 50%
            assert max_memory_growth < 100 * 1024 * 1024  # Memory growth under 100MB
            
            await benchmark_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_performance_benchmarks(self, benchmark_orchestrator):
        """Benchmark performance under concurrent load."""
        market_data = [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now(),
                open=50000, high=50100, low=49900, close=50050,
                volume=1000, market_type="crypto"
            )
        ]
        
        with patch.object(benchmark_orchestrator.strategy_engine, 'process_market_data') as mock_process:
            mock_process.return_value = []
            
            await benchmark_orchestrator.start()
            
            # Test different concurrency levels
            concurrency_levels = [1, 5, 10, 20]
            performance_results = {}
            
            for concurrency in concurrency_levels:
                
                async def concurrent_task():
                    start_time = time.perf_counter()
                    await benchmark_orchestrator.process_market_data(market_data)
                    end_time = time.perf_counter()
                    return end_time - start_time
                
                # Run concurrent tasks
                start_time = time.time()
                tasks = [concurrent_task() for _ in range(concurrency)]
                task_times = await asyncio.gather(*tasks)
                end_time = time.time()
                
                # Calculate metrics
                total_time = end_time - start_time
                avg_task_time = np.mean(task_times)
                throughput = concurrency / total_time
                
                performance_results[concurrency] = {
                    "total_time": total_time,
                    "avg_task_time": avg_task_time,
                    "throughput": throughput
                }
            
            # Verify concurrent performance scaling
            single_throughput = performance_results[1]["throughput"]
            concurrent_throughput = performance_results[20]["throughput"]
            
            # Concurrent throughput should be significantly higher
            scaling_factor = concurrent_throughput / single_throughput
            assert scaling_factor > 5  # Should scale well with concurrency
            
            # Task times should not degrade significantly under concurrency
            single_task_time = performance_results[1]["avg_task_time"]
            concurrent_task_time = performance_results[20]["avg_task_time"]
            
            degradation_factor = concurrent_task_time / single_task_time
            assert degradation_factor < 3  # Task time should not increase more than 3x
            
            await benchmark_orchestrator.stop()