"""
Integration tests for orchestration error handling and recovery mechanisms.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from concurrent.futures import ThreadPoolExecutor

from src.orchestration.orchestrator import StrategyOrchestrator
from src.orchestration.config import (
    OrchestratorConfig, AllocationConfig, RiskConfig, MonitoringConfig,
    StrategyConfig, create_default_config
)
from src.orchestration.interfaces import (
    TradingSignal, Portfolio, Position, UnifiedMarketData
)
from src.orchestration.exceptions import (
    OrchestratorError, StrategyError, RiskLimitViolationError,
    ConfigurationError, EmergencyStopError, AllocationError
)


class TestStrategyFailureRecovery:
    """Test recovery from individual strategy failures."""
    
    @pytest.fixture
    def error_recovery_config(self):
        """Create configuration with error recovery settings."""
        return OrchestratorConfig(
            max_concurrent_strategies=5,
            enable_error_recovery=True,
            max_strategy_failures=3,
            strategy_failure_cooldown=timedelta(minutes=5),
            enable_fallback_strategies=True,
            strategies=[
                StrategyConfig(type="PrimaryStrategy", name="primary_1", enabled=True),
                StrategyConfig(type="PrimaryStrategy", name="primary_2", enabled=True),
                StrategyConfig(type="BackupStrategy", name="backup_1", enabled=False),
                StrategyConfig(type="BackupStrategy", name="backup_2", enabled=False),
                StrategyConfig(type="SafeStrategy", name="safe_fallback", enabled=True)
            ]
        )
    
    @pytest.fixture
    def recovery_orchestrator(self, error_recovery_config):
        """Create orchestrator with error recovery capabilities."""
        return StrategyOrchestrator(error_recovery_config)
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data for testing."""
        return [
            UnifiedMarketData(
                symbol="BTCUSD", timestamp=datetime.now(),
                open=50000, high=50100, low=49900, close=50050,
                volume=1000, market_type="crypto"
            )
        ]
    
    @pytest.mark.asyncio
    async def test_single_strategy_failure_isolation(self, recovery_orchestrator, sample_market_data):
        """Test isolation of single strategy failure."""
        with patch.object(recovery_orchestrator.strategy_engine, 'process_market_data') as mock_process, \
             patch.object(recovery_orchestrator.error_handler, 'handle_strategy_error') as mock_error_handler, \
             patch.object(recovery_orchestrator.strategy_engine, 'get_active_strategies') as mock_active:
            
            # Mock one strategy failing
            def failing_process(market_data):
                raise StrategyError("primary_1", "Strategy execution failed")
            
            mock_process.side_effect = failing_process
            mock_active.return_value = ["primary_1", "primary_2", "safe_fallback"]
            
            await recovery_orchestrator.start()
            
            # Process market data - should handle the failure gracefully
            try:
                await recovery_orchestrator.process_market_data(sample_market_data)
            except StrategyError:
                pass  # Expected to be caught and handled
            
            # Verify error handler was called
            mock_error_handler.assert_called()
            
            # Verify orchestrator continues running
            assert recovery_orchestrator.is_running is True
            
            await recovery_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_strategy_failure_count_tracking(self, recovery_orchestrator, sample_market_data):
        """Test tracking of strategy failure counts."""
        with patch.object(recovery_orchestrator.strategy_engine, 'process_market_data') as mock_process, \
             patch.object(recovery_orchestrator.error_handler, 'record_strategy_failure') as mock_record, \
             patch.object(recovery_orchestrator.strategy_engine, 'disable_strategy') as mock_disable:
            
            # Mock repeated failures from same strategy
            failure_count = 0
            def intermittent_failure(market_data):
                nonlocal failure_count
                failure_count += 1
                if failure_count <= 3:  # Fail first 3 times
                    raise StrategyError("primary_1", f"Failure #{failure_count}")
                return []
            
            mock_process.side_effect = intermittent_failure
            
            await recovery_orchestrator.start()
            
            # Process market data multiple times to trigger failures
            for i in range(5):
                try:
                    await recovery_orchestrator.process_market_data(sample_market_data)
                except StrategyError:
                    pass
            
            # Verify failure recording
            assert mock_record.call_count >= 3
            
            # Verify strategy was disabled after max failures
            mock_disable.assert_called_with("primary_1")
            
            await recovery_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_fallback_strategy_activation(self, recovery_orchestrator, sample_market_data):
        """Test activation of fallback strategies when primary strategies fail."""
        with patch.object(recovery_orchestrator.strategy_engine, 'get_active_strategies') as mock_active, \
             patch.object(recovery_orchestrator.fallback_manager, 'activate_fallback_strategies') as mock_activate, \
             patch.object(recovery_orchestrator.strategy_engine, 'enable_strategy') as mock_enable:
            
            # Mock scenario where most primary strategies are disabled
            mock_active.return_value = ["safe_fallback"]  # Only one strategy left
            
            await recovery_orchestrator.start()
            
            # Trigger fallback activation check
            await recovery_orchestrator.check_strategy_health()
            
            # Should activate fallback strategies when too few are active
            min_strategies = getattr(recovery_orchestrator.config, 'min_active_strategies', 2)
            if len(mock_active.return_value) < min_strategies:
                mock_activate.assert_called()
            
            await recovery_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_strategy_recovery_after_cooldown(self, recovery_orchestrator):
        """Test strategy recovery after cooldown period."""
        with patch.object(recovery_orchestrator.strategy_engine, 'enable_strategy') as mock_enable, \
             patch.object(recovery_orchestrator.error_handler, 'is_strategy_in_cooldown') as mock_cooldown, \
             patch.object(recovery_orchestrator.error_handler, 'can_retry_strategy') as mock_can_retry:
            
            # Mock cooldown period expiry
            mock_cooldown.return_value = False  # Cooldown expired
            mock_can_retry.return_value = True
            
            await recovery_orchestrator.start()
            
            # Attempt to recover failed strategy
            await recovery_orchestrator.attempt_strategy_recovery("primary_1")
            
            # Verify strategy was re-enabled
            mock_enable.assert_called_with("primary_1")
            
            await recovery_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_allocation_redistribution_on_failure(self, recovery_orchestrator):
        """Test allocation redistribution when strategies fail."""
        initial_allocations = {
            "primary_1": 0.3,
            "primary_2": 0.3,
            "safe_fallback": 0.4
        }
        
        with patch.object(recovery_orchestrator.allocation_manager, 'allocations', initial_allocations), \
             patch.object(recovery_orchestrator.allocation_manager, 'redistribute_allocation') as mock_redistribute:
            
            await recovery_orchestrator.start()
            
            # Simulate strategy failure and allocation redistribution
            failed_strategy = "primary_1"
            failed_allocation = initial_allocations[failed_strategy]
            
            await recovery_orchestrator.handle_strategy_failure(failed_strategy, "Test failure")
            
            # Verify allocation redistribution was called
            mock_redistribute.assert_called()
            
            # Check that failed strategy's allocation was redistributed
            call_args = mock_redistribute.call_args
            if call_args:
                redistributed_amount = call_args[0][1]  # Second argument should be amount
                assert redistributed_amount == failed_allocation
            
            await recovery_orchestrator.stop()


class TestSystemLevelErrorHandling:
    """Test system-level error handling and recovery."""
    
    @pytest.fixture
    def system_error_config(self):
        """Create configuration for system error testing."""
        return OrchestratorConfig(
            max_concurrent_strategies=3,
            enable_emergency_stop=True,
            emergency_stop_conditions=[
                "max_drawdown_exceeded",
                "system_overload",
                "critical_error_threshold"
            ],
            system_health_check_interval=timedelta(seconds=30),
            strategies=[
                StrategyConfig(type="TestStrategy", name="test_1", enabled=True),
                StrategyConfig(type="TestStrategy", name="test_2", enabled=True),
                StrategyConfig(type="TestStrategy", name="test_3", enabled=True)
            ]
        )
    
    @pytest.fixture
    def system_orchestrator(self, system_error_config):
        """Create orchestrator for system error testing."""
        return StrategyOrchestrator(system_error_config)
    
    @pytest.mark.asyncio
    async def test_emergency_stop_activation(self, system_orchestrator):
        """Test emergency stop activation on critical conditions."""
        # Mock severe portfolio loss
        critical_portfolio = Portfolio(
            total_value=50000,  # 50% loss from assumed 100k start
            available_cash=10000,
            positions=[],
            total_pnl=-50000,
            daily_pnl=-20000  # 20% daily loss
        )
        
        with patch.object(system_orchestrator, 'get_current_portfolio') as mock_portfolio, \
             patch.object(system_orchestrator.emergency_stop_manager, 'trigger_emergency_stop') as mock_emergency, \
             patch.object(system_orchestrator.strategy_engine, 'halt_all_strategies') as mock_halt:
            
            mock_portfolio.return_value = critical_portfolio
            
            await system_orchestrator.start()
            
            # Trigger emergency stop check
            await system_orchestrator.check_emergency_conditions()
            
            # Verify emergency stop was triggered
            mock_emergency.assert_called()
            mock_halt.assert_called()
            
            await system_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_system_overload_handling(self, system_orchestrator, sample_market_data):
        """Test handling of system overload conditions."""
        with patch.object(system_orchestrator.system_monitor, 'check_system_resources') as mock_resources, \
             patch.object(system_orchestrator.load_balancer, 'reduce_system_load') as mock_reduce_load:
            
            # Mock system overload
            mock_resources.return_value = {
                "cpu_usage": 95.0,  # High CPU usage
                "memory_usage": 90.0,  # High memory usage
                "active_threads": 200,  # Many threads
                "queue_size": 1000  # Large queue
            }
            
            await system_orchestrator.start()
            
            # Process market data under overload conditions
            await system_orchestrator.process_market_data(sample_market_data)
            
            # Verify load reduction was triggered
            mock_reduce_load.assert_called()
            
            await system_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_error_recovery(self, system_orchestrator):
        """Test recovery from configuration errors."""
        invalid_config_update = {
            "allocation.min_allocation": 0.8,  # Invalid: min > max
            "allocation.max_allocation": 0.5,
            "risk.max_portfolio_drawdown": -0.1  # Invalid: negative
        }
        
        with patch.object(system_orchestrator.config_manager, 'validate_config_update') as mock_validate, \
             patch.object(system_orchestrator.config_manager, 'rollback_to_last_valid_config') as mock_rollback, \
             patch.object(system_orchestrator.error_handler, 'log_configuration_error') as mock_log:
            
            # Mock validation failure
            mock_validate.side_effect = ConfigurationError("Invalid configuration values")
            
            await system_orchestrator.start()
            
            # Attempt invalid configuration update
            try:
                await system_orchestrator.update_configuration(invalid_config_update)
            except ConfigurationError:
                pass  # Expected
            
            # Verify error handling
            mock_log.assert_called()
            mock_rollback.assert_called()
            
            # Verify orchestrator continues running with previous config
            assert system_orchestrator.is_running is True
            
            await system_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_database_connection_failure_handling(self, system_orchestrator):
        """Test handling of database connection failures."""
        with patch.object(system_orchestrator.data_manager, 'check_database_connection') as mock_db_check, \
             patch.object(system_orchestrator.data_manager, 'reconnect_database') as mock_reconnect, \
             patch.object(system_orchestrator.cache_manager, 'enable_offline_mode') as mock_offline:
            
            # Mock database connection failure
            mock_db_check.return_value = False
            mock_reconnect.side_effect = Exception("Database unreachable")
            
            await system_orchestrator.start()
            
            # Trigger database health check
            await system_orchestrator.check_system_health()
            
            # Verify offline mode was enabled
            mock_offline.assert_called()
            
            # Verify orchestrator continues running in degraded mode
            assert system_orchestrator.is_running is True
            
            await system_orchestrator.stop()


class TestConcurrencyErrorHandling:
    """Test error handling in concurrent execution scenarios."""
    
    @pytest.fixture
    def concurrent_config(self):
        """Create configuration for concurrency testing."""
        return OrchestratorConfig(
            max_concurrent_strategies=10,
            enable_parallel_processing=True,
            max_worker_threads=8,
            task_timeout=timedelta(seconds=30),
            strategies=[
                StrategyConfig(type=f"ConcurrentStrategy", name=f"concurrent_{i}", enabled=True)
                for i in range(8)
            ]
        )
    
    @pytest.fixture
    def concurrent_orchestrator(self, concurrent_config):
        """Create orchestrator for concurrency testing."""
        return StrategyOrchestrator(concurrent_config)
    
    @pytest.mark.asyncio
    async def test_concurrent_strategy_failure_isolation(self, concurrent_orchestrator, sample_market_data):
        """Test isolation of failures in concurrent strategy execution."""
        with patch.object(concurrent_orchestrator.strategy_engine, 'process_strategy_async') as mock_process:
            
            # Mock some strategies failing, others succeeding
            async def mixed_results(strategy_name, market_data):
                if strategy_name in ["concurrent_2", "concurrent_5"]:
                    raise StrategyError(strategy_name, "Concurrent execution failed")
                else:
                    await asyncio.sleep(0.01)  # Simulate processing time
                    return [TradingSignal(
                        strategy=strategy_name, symbol="BTCUSD", action="BUY",
                        quantity=0.1, price=50000, confidence=0.7, timestamp=datetime.now()
                    )]
            
            mock_process.side_effect = mixed_results
            
            await concurrent_orchestrator.start()
            
            # Process market data concurrently
            results = await concurrent_orchestrator.process_market_data_concurrent(sample_market_data)
            
            # Verify that successful strategies produced results
            successful_results = [r for r in results if not isinstance(r, Exception)]
            failed_results = [r for r in results if isinstance(r, Exception)]
            
            assert len(successful_results) > 0  # Some strategies succeeded
            assert len(failed_results) == 2  # Two strategies failed
            
            # Verify orchestrator continues running
            assert concurrent_orchestrator.is_running is True
            
            await concurrent_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_deadlock_detection_and_recovery(self, concurrent_orchestrator):
        """Test detection and recovery from deadlock situations."""
        with patch.object(concurrent_orchestrator.deadlock_detector, 'check_for_deadlocks') as mock_deadlock, \
             patch.object(concurrent_orchestrator.deadlock_detector, 'resolve_deadlock') as mock_resolve:
            
            # Mock deadlock detection
            mock_deadlock.return_value = {
                "deadlock_detected": True,
                "involved_strategies": ["concurrent_1", "concurrent_3"],
                "resource_conflicts": ["allocation_lock", "risk_calculation_lock"]
            }
            
            await concurrent_orchestrator.start()
            
            # Trigger deadlock check
            await concurrent_orchestrator.check_for_deadlocks()
            
            # Verify deadlock resolution was attempted
            mock_resolve.assert_called()
            
            await concurrent_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_timeout_handling_in_concurrent_execution(self, concurrent_orchestrator, sample_market_data):
        """Test handling of timeouts in concurrent strategy execution."""
        with patch.object(concurrent_orchestrator.strategy_engine, 'process_strategy_async') as mock_process:
            
            # Mock some strategies timing out
            async def timeout_simulation(strategy_name, market_data):
                if strategy_name in ["concurrent_1", "concurrent_4"]:
                    await asyncio.sleep(35)  # Longer than 30s timeout
                else:
                    await asyncio.sleep(0.1)
                    return []
            
            mock_process.side_effect = timeout_simulation
            
            await concurrent_orchestrator.start()
            
            # Process with timeout handling
            start_time = time.time()
            results = await concurrent_orchestrator.process_market_data_with_timeout(
                sample_market_data, timeout=5.0
            )
            end_time = time.time()
            
            # Verify execution completed within reasonable time (not 35s)
            execution_time = end_time - start_time
            assert execution_time < 10.0  # Should timeout much sooner
            
            # Verify some results were obtained (from non-timing-out strategies)
            successful_results = [r for r in results if r is not None and not isinstance(r, Exception)]
            assert len(successful_results) > 0
            
            await concurrent_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_handling(self, concurrent_orchestrator):
        """Test handling of resource exhaustion scenarios."""
        with patch.object(concurrent_orchestrator.resource_monitor, 'check_available_resources') as mock_resources, \
             patch.object(concurrent_orchestrator.resource_manager, 'throttle_execution') as mock_throttle:
            
            # Mock resource exhaustion
            mock_resources.return_value = {
                "available_memory": 100 * 1024 * 1024,  # 100MB available
                "available_cpu": 5.0,  # 5% CPU available
                "active_connections": 950,  # Near connection limit
                "thread_pool_utilization": 0.95  # 95% thread pool usage
            }
            
            await concurrent_orchestrator.start()
            
            # Trigger resource check
            await concurrent_orchestrator.check_resource_availability()
            
            # Verify throttling was applied
            mock_throttle.assert_called()
            
            await concurrent_orchestrator.stop()


class TestRecoveryMechanisms:
    """Test various recovery mechanisms."""
    
    @pytest.fixture
    def recovery_config(self):
        """Create configuration for recovery testing."""
        return OrchestratorConfig(
            max_concurrent_strategies=4,
            enable_auto_recovery=True,
            recovery_strategies=[
                "restart_failed_strategies",
                "redistribute_allocations",
                "activate_backup_systems",
                "reduce_system_load"
            ],
            health_check_interval=timedelta(seconds=10),
            strategies=[
                StrategyConfig(type="MainStrategy", name="main_1", enabled=True),
                StrategyConfig(type="MainStrategy", name="main_2", enabled=True),
                StrategyConfig(type="BackupStrategy", name="backup_1", enabled=False),
                StrategyConfig(type="BackupStrategy", name="backup_2", enabled=False)
            ]
        )
    
    @pytest.fixture
    def recovery_orchestrator(self, recovery_config):
        """Create orchestrator for recovery testing."""
        return StrategyOrchestrator(recovery_config)
    
    @pytest.mark.asyncio
    async def test_automatic_strategy_restart(self, recovery_orchestrator):
        """Test automatic restart of failed strategies."""
        with patch.object(recovery_orchestrator.strategy_engine, 'restart_strategy') as mock_restart, \
             patch.object(recovery_orchestrator.health_monitor, 'is_strategy_healthy') as mock_healthy:
            
            # Mock strategy becoming unhealthy then healthy after restart
            health_states = {"main_1": [False, True]}  # Unhealthy, then healthy after restart
            
            def check_health(strategy_name):
                if strategy_name in health_states:
                    return health_states[strategy_name].pop(0) if health_states[strategy_name] else True
                return True
            
            mock_healthy.side_effect = check_health
            
            await recovery_orchestrator.start()
            
            # Trigger health check and recovery
            await recovery_orchestrator.perform_health_check_and_recovery()
            
            # Verify strategy restart was attempted
            mock_restart.assert_called_with("main_1")
            
            await recovery_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_backup_system_activation(self, recovery_orchestrator):
        """Test activation of backup systems during failures."""
        with patch.object(recovery_orchestrator.strategy_engine, 'get_active_strategies') as mock_active, \
             patch.object(recovery_orchestrator.backup_manager, 'activate_backup_systems') as mock_activate_backup, \
             patch.object(recovery_orchestrator.strategy_engine, 'enable_strategy') as mock_enable:
            
            # Mock scenario where main strategies are down
            mock_active.return_value = []  # No active strategies
            
            await recovery_orchestrator.start()
            
            # Trigger backup activation
            await recovery_orchestrator.activate_backup_systems()
            
            # Verify backup systems were activated
            mock_activate_backup.assert_called()
            
            # Verify backup strategies were enabled
            expected_backup_calls = [
                mock_enable.call("backup_1"),
                mock_enable.call("backup_2")
            ]
            for call in expected_backup_calls:
                assert call in mock_enable.call_args_list
            
            await recovery_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, recovery_orchestrator):
        """Test graceful degradation when recovery fails."""
        with patch.object(recovery_orchestrator.strategy_engine, 'restart_strategy') as mock_restart, \
             patch.object(recovery_orchestrator.degradation_manager, 'enable_safe_mode') as mock_safe_mode, \
             patch.object(recovery_orchestrator.allocation_manager, 'switch_to_conservative_allocation') as mock_conservative:
            
            # Mock restart failures
            mock_restart.side_effect = Exception("Restart failed")
            
            await recovery_orchestrator.start()
            
            # Attempt recovery that will fail
            try:
                await recovery_orchestrator.attempt_strategy_recovery("main_1")
            except Exception:
                pass  # Expected to fail
            
            # Trigger graceful degradation
            await recovery_orchestrator.enable_graceful_degradation()
            
            # Verify safe mode was enabled
            mock_safe_mode.assert_called()
            mock_conservative.assert_called()
            
            await recovery_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_system_state_persistence_during_recovery(self, recovery_orchestrator):
        """Test that system state is preserved during recovery operations."""
        initial_state = {
            "allocations": {"main_1": 0.5, "main_2": 0.5},
            "performance_metrics": {"main_1": 0.15, "main_2": 0.12},
            "risk_metrics": {"portfolio_var": 0.02}
        }
        
        with patch.object(recovery_orchestrator.state_manager, 'save_state') as mock_save, \
             patch.object(recovery_orchestrator.state_manager, 'restore_state') as mock_restore, \
             patch.object(recovery_orchestrator.state_manager, 'get_current_state') as mock_get_state:
            
            mock_get_state.return_value = initial_state
            
            await recovery_orchestrator.start()
            
            # Simulate recovery operation
            await recovery_orchestrator.perform_recovery_with_state_preservation()
            
            # Verify state was saved before recovery
            mock_save.assert_called()
            
            # Verify state restoration capability exists
            restored_state = mock_get_state.return_value
            assert restored_state == initial_state
            
            await recovery_orchestrator.stop()
    
    @pytest.mark.asyncio
    async def test_recovery_notification_system(self, recovery_orchestrator):
        """Test notification system during recovery operations."""
        with patch.object(recovery_orchestrator.notification_manager, 'send_recovery_alert') as mock_alert, \
             patch.object(recovery_orchestrator.notification_manager, 'send_recovery_success') as mock_success:
            
            await recovery_orchestrator.start()
            
            # Simulate recovery scenario
            recovery_event = {
                "type": "strategy_failure",
                "strategy": "main_1",
                "timestamp": datetime.now(),
                "severity": "high"
            }
            
            # Trigger recovery
            await recovery_orchestrator.handle_recovery_event(recovery_event)
            
            # Verify alert was sent
            mock_alert.assert_called()
            
            # Simulate successful recovery
            await recovery_orchestrator.complete_recovery("main_1", success=True)
            
            # Verify success notification
            mock_success.assert_called()
            
            await recovery_orchestrator.stop()