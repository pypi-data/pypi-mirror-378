"""
Example demonstrating the orchestration monitoring and alerting system.

This example shows how to set up and use the comprehensive monitoring and alerting
capabilities of the strategy orchestration system.
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestration.config import OrchestratorConfig, MonitoringConfig, AlertingConfig
from src.orchestration.monitoring_integration import MonitoringIntegration, MonitoringMetrics
from src.orchestration.monitoring import DashboardData
from src.orchestration.alerting import Alert
from src.orchestration.interfaces import IPerformanceMonitor, PerformanceMetrics
from src.models.data_models import TradingSignal, SignalAction
from decimal import Decimal


class MockPerformanceMonitor(IPerformanceMonitor):
    """Mock performance monitor for demonstration."""
    
    def __init__(self):
        self.performance_data = {
            'portfolio': PerformanceMetrics(
                total_return=0.05,
                sharpe_ratio=1.2,
                max_drawdown=0.03,
                win_rate=0.65,
                profit_factor=1.8,
                volatility=0.15,
                alpha=0.02,
                beta=0.95,
                information_ratio=0.8
            ),
            'moving_average_strategy': PerformanceMetrics(
                total_return=0.08,
                sharpe_ratio=1.5,
                max_drawdown=0.02,
                win_rate=0.70,
                profit_factor=2.1,
                volatility=0.12,
                alpha=0.03,
                beta=0.90,
                information_ratio=1.0
            ),
            'rsi_strategy': PerformanceMetrics(
                total_return=0.03,
                sharpe_ratio=0.9,
                max_drawdown=0.04,
                win_rate=0.60,
                profit_factor=1.5,
                volatility=0.18,
                alpha=0.01,
                beta=1.05,
                information_ratio=0.6
            )
        }
    
    def collect_performance_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Collect performance metrics."""
        return self.performance_data.copy()
    
    def analyze_attribution(self, start_date: datetime, end_date: datetime):
        """Mock attribution analysis."""
        return {
            'strategy_contributions': {
                'moving_average_strategy': 0.05,
                'rsi_strategy': 0.02
            },
            'total_return': 0.07
        }
    
    def detect_performance_degradation(self):
        """Mock performance degradation detection."""
        return []
    
    def generate_performance_report(self):
        """Mock performance report generation."""
        return {'status': 'generated', 'timestamp': datetime.utcnow().isoformat()}


class DashboardCallback:
    """Example dashboard callback handler."""
    
    def __init__(self):
        self.dashboard_updates = []
        self.logger = logging.getLogger("dashboard_callback")
    
    def handle_dashboard_update(self, dashboard_data: DashboardData):
        """Handle dashboard data updates."""
        self.dashboard_updates.append(dashboard_data)
        
        # Log key metrics
        orchestrator = dashboard_data.orchestrator_metrics
        self.logger.info(f"Dashboard Update - Health: {orchestrator.system_health}, "
                        f"Active Strategies: {orchestrator.active_strategies}, "
                        f"Signals: {orchestrator.signals_executed}/{orchestrator.total_signals_generated}")
        
        # Print performance summary
        if dashboard_data.performance_summary:
            perf = dashboard_data.performance_summary
            self.logger.info(f"Performance - Return: {perf.get('total_return', 0):.2%}, "
                           f"Sharpe: {perf.get('sharpe_ratio', 0):.2f}, "
                           f"Drawdown: {perf.get('max_drawdown', 0):.2%}")
        
        # Print strategy health
        for name, metrics in dashboard_data.strategy_metrics.items():
            self.logger.info(f"Strategy {name} - Health: {metrics.health_status}, "
                           f"Allocation: {metrics.allocation:.1%}, "
                           f"Score: {metrics.performance_score:.1f}")


class AlertCallback:
    """Example alert callback handler."""
    
    def __init__(self):
        self.alerts_received = []
        self.logger = logging.getLogger("alert_callback")
    
    def handle_alert(self, alert: Alert):
        """Handle alert notifications."""
        self.alerts_received.append(alert)
        
        self.logger.warning(f"ALERT [{alert.severity.value.upper()}] {alert.title}")
        self.logger.warning(f"Source: {alert.source}, Type: {alert.alert_type.value}")
        self.logger.warning(f"Message: {alert.message}")
        
        if alert.metadata:
            self.logger.warning(f"Metadata: {alert.metadata}")


async def demonstrate_monitoring_system():
    """Demonstrate the monitoring system capabilities."""
    print("=== Orchestration Monitoring and Alerting Demo ===\n")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    monitoring_config = MonitoringConfig(
        performance_tracking=True,
        real_time_metrics=True,
        update_interval_seconds=5,  # Fast updates for demo
        dashboard_enabled=True,
        health_check_interval_seconds=10
    )
    
    alerting_config = AlertingConfig(
        enabled=True,
        notification_channels=[
            {
                "name": "console",
                "type": "webhook",
                "url": "http://localhost:8080/alerts",  # Mock endpoint
                "method": "POST"
            }
        ],
        escalation_enabled=True,
        default_escalation_minutes=2,  # Fast escalation for demo
        max_alerts_per_hour=50
    )
    
    config = OrchestratorConfig(
        monitoring=monitoring_config,
        alerting=alerting_config
    )
    
    # Create performance monitor
    performance_monitor = MockPerformanceMonitor()
    
    # Create monitoring integration
    monitoring = MonitoringIntegration(config, performance_monitor)
    
    # Set up callbacks
    dashboard_callback = DashboardCallback()
    alert_callback = AlertCallback()
    
    monitoring.add_dashboard_callback(dashboard_callback.handle_dashboard_update)
    monitoring.add_alert_callback(alert_callback.handle_alert)
    
    print("1. Starting monitoring and alerting systems...")
    monitoring.start()
    
    # Simulate orchestrator activity
    print("\n2. Simulating orchestrator activity...")
    
    # Simulate normal operation
    for i in range(5):
        monitoring.record_orchestrator_activity(
            active_strategies=3,
            signals_generated=10 + i,
            signals_executed=8 + i,
            signals_rejected=2,
            processing_time_ms=100.0 + i * 10,
            allocation_changes=0 if i < 3 else 1,
            risk_violations=0
        )
        
        # Record strategy activities
        monitoring.record_strategy_activity(
            strategy_name='moving_average_strategy',
            is_active=True,
            signals_generated=5 + i,
            signals_executed=4 + i,
            error_count=0,
            last_error=None,
            allocation=0.6,
            processing_time_ms=30.0 + i * 5
        )
        
        monitoring.record_strategy_activity(
            strategy_name='rsi_strategy',
            is_active=True,
            signals_generated=3 + i,
            signals_executed=2 + i,
            error_count=0 if i < 3 else 1,
            last_error='Connection timeout' if i >= 3 else None,
            allocation=0.4,
            processing_time_ms=40.0 + i * 8
        )
        
        # Record signal processing
        signal = TradingSignal(
            symbol='BTCUSD',
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.utcnow(),
            strategy_name='moving_average_strategy',
            price=Decimal(str(50000.0 + i * 100)),
            metadata={'strategy': 'moving_average_strategy'}
        )
        
        monitoring.record_signal_processing(signal, 25.0 + i * 2, True)
        
        await asyncio.sleep(2)  # Wait between iterations
    
    print("\n3. Getting current dashboard data...")
    dashboard_data = monitoring.get_dashboard_data()
    
    # Format for API
    api_data = MonitoringMetrics.format_dashboard_for_api(dashboard_data)
    print(f"API Dashboard Data Keys: {list(api_data.keys())}")
    print(f"System Health Score: {MonitoringMetrics.calculate_system_health_score(dashboard_data):.1f}")
    
    print("\n4. Simulating performance degradation...")
    
    # Simulate degraded performance to trigger alerts
    for i in range(3):
        monitoring.record_orchestrator_activity(
            active_strategies=2,  # One strategy failed
            signals_generated=5,
            signals_executed=2,  # Low execution rate
            signals_rejected=3,
            processing_time_ms=2000.0,  # High processing time
            allocation_changes=2,
            risk_violations=1  # Risk violation
        )
        
        # Record failing strategy
        monitoring.record_strategy_activity(
            strategy_name='rsi_strategy',
            is_active=False,  # Strategy failed
            signals_generated=0,
            signals_executed=0,
            error_count=5,
            last_error='Strategy execution failed',
            allocation=0.0,
            processing_time_ms=0.0
        )
        
        await asyncio.sleep(3)
    
    print("\n5. Checking alerts...")
    active_alerts = monitoring.get_active_alerts()
    print(f"Active alerts: {len(active_alerts)}")
    
    for alert in active_alerts:
        print(f"  - {alert.title} ({alert.severity.value}) - {alert.source}")
    
    # Demonstrate alert management
    if active_alerts:
        print("\n6. Demonstrating alert management...")
        alert_to_manage = active_alerts[0]
        
        # Acknowledge alert
        success = monitoring.acknowledge_alert(alert_to_manage.id, "demo_user")
        print(f"Alert acknowledged: {success}")
        
        # Resolve alert
        success = monitoring.resolve_alert(alert_to_manage.id)
        print(f"Alert resolved: {success}")
    
    print("\n7. Getting monitoring status...")
    status = monitoring.get_monitoring_status()
    print("Monitoring Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n8. Getting alert history...")
    alert_history = monitoring.get_alert_history(hours=1)
    print(f"Alerts in last hour: {len(alert_history)}")
    
    # Format alerts for API
    if alert_history:
        api_alerts = MonitoringMetrics.format_alerts_for_api(alert_history[:3])
        print("Sample alert data for API:")
        for alert_data in api_alerts:
            print(f"  - {alert_data['title']} ({alert_data['severity']})")
    
    print("\n9. Stopping monitoring system...")
    monitoring.stop()
    
    print("\n=== Demo Summary ===")
    print(f"Dashboard updates received: {len(dashboard_callback.dashboard_updates)}")
    print(f"Alerts received: {len(alert_callback.alerts_received)}")
    print("Demo completed successfully!")


def demonstrate_configuration():
    """Demonstrate monitoring and alerting configuration."""
    print("\n=== Configuration Examples ===\n")
    
    # Example monitoring configuration
    monitoring_config = MonitoringConfig(
        performance_tracking=True,
        real_time_metrics=True,
        update_interval_seconds=30,
        alert_thresholds={
            "drawdown": 0.05,
            "correlation": 0.75,
            "performance_degradation": -0.10,
            "risk_limit_breach": 0.90
        },
        reporting_frequency="daily",
        metrics_retention_days=365,
        enable_notifications=True,
        notification_channels=["email", "slack"],
        dashboard_enabled=True,
        health_check_interval_seconds=60
    )
    
    print("Monitoring Configuration:")
    print(f"  Update interval: {monitoring_config.update_interval_seconds}s")
    print(f"  Dashboard enabled: {monitoring_config.dashboard_enabled}")
    print(f"  Alert thresholds: {monitoring_config.alert_thresholds}")
    
    # Example alerting configuration
    alerting_config = AlertingConfig(
        enabled=True,
        notification_channels=[
            {
                "name": "email",
                "type": "email",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "use_tls": True,
                "username": "your_email@gmail.com",
                "password": "your_app_password",
                "from_email": "orchestrator@yourcompany.com",
                "to_emails": ["admin@yourcompany.com", "trader@yourcompany.com"]
            },
            {
                "name": "slack",
                "type": "slack",
                "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                "channel": "#trading-alerts",
                "username": "Orchestrator Bot"
            },
            {
                "name": "webhook",
                "type": "webhook",
                "url": "https://your-monitoring-system.com/api/alerts",
                "method": "POST",
                "headers": {
                    "Authorization": "Bearer your_api_token",
                    "Content-Type": "application/json"
                }
            }
        ],
        escalation_enabled=True,
        default_escalation_minutes=60,
        max_alerts_per_hour=100,
        alert_history_retention_days=30
    )
    
    print("\nAlerting Configuration:")
    print(f"  Enabled: {alerting_config.enabled}")
    print(f"  Notification channels: {len(alerting_config.notification_channels)}")
    print(f"  Escalation enabled: {alerting_config.escalation_enabled}")
    print(f"  Max alerts per hour: {alerting_config.max_alerts_per_hour}")
    
    # Create full orchestrator config
    config = OrchestratorConfig(
        monitoring=monitoring_config,
        alerting=alerting_config
    )
    
    print(f"\nFull configuration validation: {len(config.validate())} errors")


def demonstrate_custom_alert_rules():
    """Demonstrate custom alert rule creation."""
    print("\n=== Custom Alert Rules ===\n")
    
    from src.orchestration.alerting import AlertRule, AlertType, AlertSeverity
    
    # Custom alert rule for high correlation
    correlation_rule = AlertRule(
        name="high_correlation_alert",
        alert_type=AlertType.CORRELATION_SPIKE,
        severity=AlertSeverity.MEDIUM,
        condition=lambda data: hasattr(data, 'correlation') and data.correlation > 0.8,
        message_template="High correlation detected between strategies: {correlation:.2f}",
        cooldown_minutes=30,
        escalation_minutes=90,
        notification_channels=["email", "slack"]
    )
    
    print("Custom Alert Rule Example:")
    print(f"  Name: {correlation_rule.name}")
    print(f"  Type: {correlation_rule.alert_type.value}")
    print(f"  Severity: {correlation_rule.severity.value}")
    print(f"  Cooldown: {correlation_rule.cooldown_minutes} minutes")
    
    # Custom alert rule for processing delays
    delay_rule = AlertRule(
        name="processing_delay_alert",
        alert_type=AlertType.PROCESSING_DELAY,
        severity=AlertSeverity.HIGH,
        condition=lambda data: hasattr(data, 'processing_time_ms') and data.processing_time_ms > 5000,
        message_template="Processing delay detected: {processing_time_ms:.0f}ms",
        cooldown_minutes=15,
        escalation_minutes=45,
        notification_channels=["slack", "webhook"]
    )
    
    print(f"\nAnother Custom Rule:")
    print(f"  Name: {delay_rule.name}")
    print(f"  Condition: Processing time > 5000ms")
    print(f"  Escalation: {delay_rule.escalation_minutes} minutes")


if __name__ == "__main__":
    print("Orchestration Monitoring and Alerting Example")
    print("=" * 50)
    
    # Run configuration demonstration
    demonstrate_configuration()
    
    # Run custom alert rules demonstration
    demonstrate_custom_alert_rules()
    
    # Run main monitoring demonstration
    asyncio.run(demonstrate_monitoring_system())