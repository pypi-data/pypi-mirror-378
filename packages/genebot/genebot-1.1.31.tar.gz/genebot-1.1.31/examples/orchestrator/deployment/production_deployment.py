#!/usr/bin/env python3
"""
Production Deployment Example for Strategy Orchestrator

This example demonstrates how to deploy the Strategy Orchestrator in a
production environment with proper monitoring, logging, error handling,
and operational procedures.

Key Features:
- Production-ready configuration
- Comprehensive monitoring and alerting
- Automated backup and recovery
- Health checks and diagnostics
- Graceful shutdown procedures
"""

import asyncio
import logging
import signal
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from src.orchestration.orchestrator import StrategyOrchestrator
from src.orchestration.config import OrchestratorConfig
from src.orchestration.monitoring import ProductionMonitor
from src.orchestration.backup import BackupManager
from src.orchestration.health import HealthChecker

# Configure production logging
def setup_production_logging():
    """Set up production-grade logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Main application log
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "orchestrator_production.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Separate error log
    error_handler = logging.FileHandler(log_dir / "orchestrator_errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Add error handler to root logger
    logging.getLogger().addHandler(error_handler)
    
    return logging.getLogger(__name__)


class ProductionOrchestrator:
    """
    Production-ready orchestrator with comprehensive monitoring and management.
    """
    
    def __init__(self, config_path: str):
        """Initialize production orchestrator."""
        self.config_path = config_path
        self.config = OrchestratorConfig.from_file(config_path)
        self.orchestrator = StrategyOrchestrator(self.config)
        
        # Production components
        self.monitor = ProductionMonitor(self.config)
        self.backup_manager = BackupManager(self.config)
        self.health_checker = HealthChecker(self.orchestrator)
        
        # State management
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        self.logger = logging.getLogger(__name__)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.graceful_shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the production orchestrator."""
        self.logger.info("Starting production orchestrator...")
        
        try:
            # Pre-startup checks
            await self.pre_startup_checks()
            
            # Initialize components
            await self.initialize_components()
            
            # Start orchestrator
            await self.orchestrator.start()
            self.is_running = True
            
            # Start monitoring tasks
            await self.start_monitoring_tasks()
            
            # Create backup
            await self.backup_manager.create_startup_backup()
            
            self.logger.info("Production orchestrator started successfully")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            self.logger.error(f"Failed to start production orchestrator: {e}")
            await self.emergency_shutdown()
            raise
    
    async def pre_startup_checks(self):
        """Perform pre-startup health checks."""
        self.logger.info("Performing pre-startup checks...")
        
        # Check configuration validity
        if not self.config.validate():
            raise RuntimeError("Configuration validation failed")
        
        # Check system resources
        await self.check_system_resources()
        
        # Check external dependencies
        await self.check_external_dependencies()
        
        # Check data integrity
        await self.check_data_integrity()
        
        self.logger.info("Pre-startup checks completed successfully")
    
    async def check_system_resources(self):
        """Check system resources (memory, disk, etc.)."""
        import psutil
        
        # Check available memory
        memory = psutil.virtual_memory()
        if memory.available < 1024 * 1024 * 1024:  # 1GB
            raise RuntimeError(f"Insufficient memory: {memory.available / 1024**3:.2f}GB available")
        
        # Check disk space
        disk = psutil.disk_usage('/')
        if disk.free < 5 * 1024 * 1024 * 1024:  # 5GB
            raise RuntimeError(f"Insufficient disk space: {disk.free / 1024**3:.2f}GB available")
        
        self.logger.info(f"System resources OK - Memory: {memory.available / 1024**3:.2f}GB, "
                        f"Disk: {disk.free / 1024**3:.2f}GB")
    
    async def check_external_dependencies(self):
        """Check external dependencies (exchanges, databases, etc.)."""
        # Check exchange connectivity
        exchanges = self.config.get_exchanges()
        for exchange_name in exchanges:
            try:
                # Test connection (mock implementation)
                await self.test_exchange_connection(exchange_name)
                self.logger.info(f"Exchange {exchange_name} connection OK")
            except Exception as e:
                raise RuntimeError(f"Failed to connect to exchange {exchange_name}: {e}")
        
        # Check database connectivity
        try:
            await self.test_database_connection()
            self.logger.info("Database connection OK")
        except Exception as e:
            raise RuntimeError(f"Database connection failed: {e}")
    
    async def check_data_integrity(self):
        """Check data integrity and consistency."""
        # Check configuration files
        config_files = [
            self.config_path,
            "config/accounts.yaml",
            "config/strategies/"
        ]
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                raise RuntimeError(f"Required configuration file missing: {config_file}")
        
        # Check log directories
        log_dirs = ["logs", "logs/strategies", "logs/performance"]
        for log_dir in log_dirs:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Data integrity checks completed")
    
    async def initialize_components(self):
        """Initialize all production components."""
        self.logger.info("Initializing production components...")
        
        # Initialize monitor
        await self.monitor.initialize()
        
        # Initialize backup manager
        await self.backup_manager.initialize()
        
        # Initialize health checker
        await self.health_checker.initialize()
        
        self.logger.info("Production components initialized")
    
    async def start_monitoring_tasks(self):
        """Start all monitoring and maintenance tasks."""
        self.logger.info("Starting monitoring tasks...")
        
        # Start health monitoring
        asyncio.create_task(self.health_monitoring_loop())
        
        # Start performance monitoring
        asyncio.create_task(self.performance_monitoring_loop())
        
        # Start backup tasks
        asyncio.create_task(self.backup_loop())
        
        # Start log rotation
        asyncio.create_task(self.log_rotation_loop())
        
        # Start system monitoring
        asyncio.create_task(self.system_monitoring_loop())
        
        self.logger.info("Monitoring tasks started")
    
    async def health_monitoring_loop(self):
        """Continuous health monitoring."""
        while self.is_running:
            try:
                health_status = await self.health_checker.check_health()
                
                if not health_status['healthy']:
                    self.logger.warning(f"Health check failed: {health_status['issues']}")
                    await self.handle_health_issues(health_status['issues'])
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)
    
    async def performance_monitoring_loop(self):
        """Continuous performance monitoring."""
        while self.is_running:
            try:
                performance_metrics = await self.monitor.collect_performance_metrics()
                
                # Check for performance issues
                await self.check_performance_thresholds(performance_metrics)
                
                # Log performance metrics
                self.logger.info(f"Performance metrics: {performance_metrics}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(300)
    
    async def backup_loop(self):
        """Regular backup creation."""
        while self.is_running:
            try:
                # Create hourly backup
                await self.backup_manager.create_backup("hourly")
                
                # Wait for next backup
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                self.logger.error(f"Error in backup creation: {e}")
                await asyncio.sleep(3600)
    
    async def log_rotation_loop(self):
        """Log file rotation and cleanup."""
        while self.is_running:
            try:
                # Rotate logs daily
                await self.rotate_logs()
                
                # Wait for next rotation
                await asyncio.sleep(86400)  # 24 hours
                
            except Exception as e:
                self.logger.error(f"Error in log rotation: {e}")
                await asyncio.sleep(86400)
    
    async def system_monitoring_loop(self):
        """System resource monitoring."""
        while self.is_running:
            try:
                import psutil
                
                # Monitor system resources
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                cpu = psutil.cpu_percent(interval=1)
                
                # Check thresholds
                if memory.percent > 85:
                    self.logger.warning(f"High memory usage: {memory.percent}%")
                
                if disk.percent > 90:
                    self.logger.warning(f"High disk usage: {disk.percent}%")
                
                if cpu > 90:
                    self.logger.warning(f"High CPU usage: {cpu}%")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(300)
    
    async def handle_health_issues(self, issues: List[str]):
        """Handle detected health issues."""
        for issue in issues:
            if "strategy_failure" in issue:
                await self.handle_strategy_failure(issue)
            elif "exchange_connectivity" in issue:
                await self.handle_exchange_connectivity_issue(issue)
            elif "performance_degradation" in issue:
                await self.handle_performance_degradation(issue)
            else:
                self.logger.warning(f"Unhandled health issue: {issue}")
    
    async def handle_strategy_failure(self, issue: str):
        """Handle strategy failure."""
        self.logger.warning(f"Handling strategy failure: {issue}")
        
        # Extract strategy name from issue
        strategy_name = issue.split(":")[-1].strip()
        
        # Disable failed strategy
        await self.orchestrator.disable_strategy(strategy_name)
        
        # Redistribute allocation
        await self.orchestrator.rebalance_allocations()
        
        # Send alert
        await self.monitor.send_alert("strategy_failure", {
            "strategy": strategy_name,
            "timestamp": datetime.now().isoformat(),
            "action": "disabled_and_rebalanced"
        })
    
    async def handle_exchange_connectivity_issue(self, issue: str):
        """Handle exchange connectivity issues."""
        self.logger.warning(f"Handling exchange connectivity issue: {issue}")
        
        # Extract exchange name
        exchange_name = issue.split(":")[-1].strip()
        
        # Switch to backup exchange if available
        backup_exchange = self.config.get_backup_exchange(exchange_name)
        if backup_exchange:
            await self.orchestrator.switch_exchange(exchange_name, backup_exchange)
            self.logger.info(f"Switched from {exchange_name} to {backup_exchange}")
    
    async def handle_performance_degradation(self, issue: str):
        """Handle performance degradation."""
        self.logger.warning(f"Handling performance degradation: {issue}")
        
        # Trigger performance analysis
        analysis = await self.monitor.analyze_performance_degradation()
        
        # Take corrective actions based on analysis
        if analysis['cause'] == 'high_correlation':
            await self.orchestrator.reduce_correlated_strategies()
        elif analysis['cause'] == 'market_regime_change':
            await self.orchestrator.adapt_to_market_regime()
    
    async def check_performance_thresholds(self, metrics: Dict):
        """Check performance metrics against thresholds."""
        thresholds = self.config.get_performance_thresholds()
        
        for metric, value in metrics.items():
            if metric in thresholds:
                threshold = thresholds[metric]
                if value < threshold['min'] or value > threshold['max']:
                    await self.monitor.send_alert("performance_threshold", {
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "timestamp": datetime.now().isoformat()
                    })
    
    async def graceful_shutdown(self):
        """Perform graceful shutdown."""
        self.logger.info("Starting graceful shutdown...")
        
        try:
            # Stop accepting new trades
            await self.orchestrator.stop_new_trades()
            
            # Close existing positions (optional)
            if self.config.get('close_positions_on_shutdown', False):
                await self.orchestrator.close_all_positions()
            
            # Create final backup
            await self.backup_manager.create_backup("shutdown")
            
            # Stop orchestrator
            await self.orchestrator.stop()
            
            # Stop monitoring
            self.is_running = False
            
            # Final log entry
            self.logger.info("Graceful shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during graceful shutdown: {e}")
        finally:
            self.shutdown_event.set()
    
    async def emergency_shutdown(self):
        """Perform emergency shutdown."""
        self.logger.error("Performing emergency shutdown...")
        
        try:
            # Immediate stop
            await self.orchestrator.emergency_stop()
            
            # Create emergency backup
            await self.backup_manager.create_backup("emergency")
            
            # Send emergency alert
            await self.monitor.send_alert("emergency_shutdown", {
                "timestamp": datetime.now().isoformat(),
                "reason": "system_failure"
            })
            
        except Exception as e:
            self.logger.error(f"Error during emergency shutdown: {e}")
        finally:
            self.is_running = False
            self.shutdown_event.set()
    
    async def test_exchange_connection(self, exchange_name: str):
        """Test connection to an exchange."""
        # Mock implementation
        await asyncio.sleep(0.1)
        return True
    
    async def test_database_connection(self):
        """Test database connection."""
        # Mock implementation
        await asyncio.sleep(0.1)
        return True
    
    async def rotate_logs(self):
        """Rotate log files."""
        log_dir = Path("logs")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_size > 100 * 1024 * 1024:  # 100MB
                rotated_name = f"{log_file.stem}_{timestamp}.log"
                log_file.rename(log_dir / rotated_name)
                self.logger.info(f"Rotated log file: {log_file.name} -> {rotated_name}")


async def main():
    """Main function for production deployment."""
    
    # Setup production logging
    logger = setup_production_logging()
    
    # Configuration file path
    config_path = os.getenv('ORCHESTRATOR_CONFIG', 'config/production_orchestrator_config.yaml')
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Create production orchestrator
    orchestrator = ProductionOrchestrator(config_path)
    
    try:
        logger.info("Starting production orchestrator deployment...")
        await orchestrator.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Production orchestrator failed: {e}")
        sys.exit(1)
    finally:
        logger.info("Production orchestrator deployment ended")


if __name__ == "__main__":
    asyncio.run(main())