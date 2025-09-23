"""
Tests for orchestration monitoring and alerting systems.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass

from src.orchestration.monitoring import (
    OrchestratorMonitor, RealTimeMetricsCollector, SystemHealthMonitor,
    DashboardDataGenerator, OrchestratorMetrics, StrategyHealthMetrics
)
from src.orchestration.alerting import (
    AlertManager, AlertConditionDetector, EmailNotificationChannel,
    SlackNotificationChannel, Alert, AlertType, AlertSeverity, AlertStatus
)
from src.orchestration.monitoring_integration import MonitoringIntegration, MonitoringMetrics
from src.orchestration.config import OrchestratorConfig, MonitoringConfig, AlertingConfig
from src.orchestration.interfaces import IPerformanceMonitor, PerformanceMetrics
from src.models.data_models import TradingSignal, SignalAction
from decimal import Decimal


@dataclass
class MockPerformanceMonitor(IPerformanceMonitor):
    """Mock performance monitor for testing."""
    
    def collect_performance_metrics(self):
        return {
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
            'strategy1': PerformanceMetrics(
                total_return=0.08,
                sharpe_ratio=1.5,
                max_drawdown=0.02,
                win_rate=0.70,
                profit_factor=2.1,
                volatility=0.12,
                alpha=0.03,
                beta=0.90,
                information_ratio=1.0
            )
        }
    
    def analyze_attribution(self, start_date, end_date):
        return Mock()
    
    def detect_performance_degradation(self):
        return []
    
    def generate_performance_report(self):
        return {'status': 'ok'}


class TestRealTimeMetricsCollector:
    """Test real-time metrics collector."""
    
    def test_initialization(self):
        """Test metrics collector initialization."""
        collector = RealTimeMetricsCollector(max_history=100)
        
        assert len(collector._orchestrator_metrics) == 0
        assert len(collector._strategy_metrics) == 0
        assert len(collector._signal_metrics) == 0
    
    def test_record_orchestrator_metrics(self):
        """Test recording orchestrator metrics."""
        collector = RealTimeMetricsCollector()
        
        metrics = OrchestratorMetrics(
            timestamp=datetime.utcnow(),
            active_strategies=3,
            total_signals_generated=10,
            signals_executed=8,
            signals_rejected=2,
            processing_time_ms=150.0,
            allocation_changes=1,
            risk_violations=0,
            performance_score=85.0,
            system_health='healthy'
        )
        
        collector.record_orchestrator_metrics(metrics)
        
        assert len(collector._orchestrator_metrics) == 1
        assert collector._orchestrator_metrics[0] == metrics
    
    def test_record_strategy_metrics(self):
        """Test recording strategy metrics."""
        collector = RealTimeMetricsCollector()
        
        metrics = StrategyHealthMetrics(
            strategy_name='test_strategy',
            timestamp=datetime.utcnow(),
            is_active=True,
            signals_generated=5,
            signals_executed=4,
            error_count=0,
            last_error=None,
            performance_score=90.0,
            allocation=0.25,
            processing_time_ms=50.0,
            health_status='healthy'
        )
        
        collector.record_strategy_metrics(metrics)
        
        assert len(collector._strategy_metrics['test_strategy']) == 1
        assert collector._strategy_metrics['test_strategy'][0] == metrics
    
    def test_record_signal_processing(self):
        """Test recording signal processing metrics."""
        collector = RealTimeMetricsCollector()
        
        signal = TradingSignal(
            symbol='BTCUSD',
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.utcnow(),
            strategy_name='test_strategy',
            price=Decimal('50000.0'),
            metadata={'strategy': 'test_strategy'}
        )
        
        collector.record_signal_processing(signal, 25.0, True)
        
        assert len(collector._signal_metrics) == 1
        assert collector._counters['signals_executed'] == 1
        assert collector._counters['signals_generated'] == 1
    
    def test_get_signal_flow_metrics(self):
        """Test getting signal flow metrics."""
        collector = RealTimeMetricsCollector()
        
        # Record some signals
        for i in range(5):
            signal = TradingSignal(
                symbol=f'SYMBOL{i}',
                action=SignalAction.BUY,
                confidence=0.8,
                timestamp=datetime.utcnow(),
                strategy_name=f'strategy{i % 2}',
                price=Decimal('100.0'),
                metadata={'strategy': f'strategy{i % 2}'}
            )
            collector.record_signal_processing(signal, 25.0, i % 2 == 0)
        
        flow_metrics = collector.get_signal_flow_metrics(60)
        
        assert flow_metrics['total_generated'] == 5
        assert flow_metrics['executed'] == 3  # 0, 2, 4
        assert flow_metrics['rejected'] == 2  # 1, 3
        assert 'strategy0' in flow_metrics['by_strategy']
        assert 'strategy1' in flow_metrics['by_strategy']


class TestSystemHealthMonitor:
    """Test system health monitor."""
    
    def test_initialization(self):
        """Test health monitor initialization."""
        config = MonitoringConfig()
        monitor = SystemHealthMonitor(config)
        
        assert monitor.config == config
        assert 'processing_time_warning' in monitor._thresholds
    
    def test_assess_orchestrator_health_healthy(self):
        """Test assessing healthy orchestrator."""
        config = MonitoringConfig()
        monitor = SystemHealthMonitor(config)
        
        metrics = OrchestratorMetrics(
            timestamp=datetime.utcnow(),
            active_strategies=3,
            total_signals_generated=10,
            signals_executed=9,
            signals_rejected=1,
            processing_time_ms=150.0,
            allocation_changes=0,
            risk_violations=0,
            performance_score=85.0,
            system_health='unknown'
        )
        
        health = monitor.assess_orchestrator_health(metrics, [])
        assert health == 'healthy'
    
    def test_assess_orchestrator_health_warning(self):
        """Test assessing orchestrator with warnings."""
        config = MonitoringConfig()
        monitor = SystemHealthMonitor(config)
        
        metrics = OrchestratorMetrics(
            timestamp=datetime.utcnow(),
            active_strategies=3,
            total_signals_generated=10,
            signals_executed=5,
            signals_rejected=5,
            processing_time_ms=2000.0,  # High processing time
            allocation_changes=0,
            risk_violations=0,
            performance_score=85.0,
            system_health='unknown'
        )
        
        health = monitor.assess_orchestrator_health(metrics, [])
        assert health == 'warning'
    
    def test_assess_strategy_health_error(self):
        """Test assessing strategy with errors."""
        config = MonitoringConfig()
        monitor = SystemHealthMonitor(config)
        
        metrics = StrategyHealthMetrics(
            strategy_name='test_strategy',
            timestamp=datetime.utcnow(),
            is_active=True,
            signals_generated=5,
            signals_executed=2,
            error_count=3,  # High error count
            last_error='Test error',
            performance_score=30.0,
            allocation=0.25,
            processing_time_ms=50.0,
            health_status='unknown'
        )
        
        health = monitor.assess_strategy_health('test_strategy', metrics, [])
        assert health == 'warning'


class TestDashboardDataGenerator:
    """Test dashboard data generator."""
    
    def test_generate_dashboard_data(self):
        """Test generating dashboard data."""
        metrics_collector = RealTimeMetricsCollector()
        health_monitor = SystemHealthMonitor(MonitoringConfig())
        performance_monitor = MockPerformanceMonitor()
        
        generator = DashboardDataGenerator(
            metrics_collector, health_monitor, performance_monitor
        )
        
        # Add some test data
        orchestrator_metrics = OrchestratorMetrics(
            timestamp=datetime.utcnow(),
            active_strategies=2,
            total_signals_generated=10,
            signals_executed=8,
            signals_rejected=2,
            processing_time_ms=150.0,
            allocation_changes=1,
            risk_violations=0,
            performance_score=85.0,
            system_health='healthy'
        )
        metrics_collector.record_orchestrator_metrics(orchestrator_metrics)
        
        dashboard_data = generator.generate_dashboard_data()
        
        assert dashboard_data.orchestrator_metrics is not None
        assert dashboard_data.performance_summary is not None
        assert dashboard_data.system_status is not None
        assert dashboard_data.allocation_breakdown is not None
        assert dashboard_data.signal_flow is not None


class TestAlertConditionDetector:
    """Test alert condition detector."""
    
    def test_initialization(self):
        """Test detector initialization."""
        config = AlertingConfig()
        detector = AlertConditionDetector(config)
        
        assert len(detector._rules) > 0
        assert detector.config == config
    
    def test_check_performance_degradation(self):
        """Test performance degradation detection."""
        config = AlertingConfig()
        detector = AlertConditionDetector(config)
        
        # Test with low performance score
        data = Mock()
        data.performance_score = 20.0  # Below threshold
        
        result = detector._check_performance_degradation(data)
        assert result is True
        
        # Test with good performance score
        data.performance_score = 80.0
        result = detector._check_performance_degradation(data)
        assert result is False
    
    def test_check_strategy_failure(self):
        """Test strategy failure detection."""
        config = AlertingConfig()
        detector = AlertConditionDetector(config)
        
        # Test with error status
        data = Mock()
        data.health_status = 'error'
        
        result = detector._check_strategy_failure(data)
        assert result is True
        
        # Test with healthy status
        data.health_status = 'healthy'
        result = detector._check_strategy_failure(data)
        assert result is False


class TestEmailNotificationChannel:
    """Test email notification channel."""
    
    def test_initialization(self):
        """Test email channel initialization."""
        config = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'username': 'test@example.com',
            'password': 'password',
            'from_email': 'test@example.com',
            'to_emails': ['admin@example.com']
        }
        
        channel = EmailNotificationChannel('email', config)
        
        assert channel.smtp_server == 'smtp.example.com'
        assert channel.smtp_port == 587
        assert channel.to_emails == ['admin@example.com']
    
    @patch('smtplib.SMTP')
    async def test_send_notification(self, mock_smtp):
        """Test sending email notification."""
        config = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'from_email': 'test@example.com',
            'to_emails': ['admin@example.com']
        }
        
        channel = EmailNotificationChannel('email', config)
        
        alert = Alert(
            id='test_alert',
            timestamp=datetime.utcnow(),
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.MEDIUM,
            title='Test Alert',
            message='This is a test alert',
            source='test'
        )
        
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = await channel.send_notification(alert)
        
        assert result is True
        mock_server.send_message.assert_called_once()


class TestSlackNotificationChannel:
    """Test Slack notification channel."""
    
    def test_initialization(self):
        """Test Slack channel initialization."""
        config = {
            'webhook_url': 'https://hooks.slack.com/test',
            'channel': '#alerts',
            'username': 'Bot'
        }
        
        channel = SlackNotificationChannel('slack', config)
        
        assert channel.webhook_url == 'https://hooks.slack.com/test'
        assert channel.channel == '#alerts'
        assert channel.username == 'Bot'
    
    @patch('requests.post')
    async def test_send_notification(self, mock_post):
        """Test sending Slack notification."""
        config = {
            'webhook_url': 'https://hooks.slack.com/test',
            'channel': '#alerts'
        }
        
        channel = SlackNotificationChannel('slack', config)
        
        alert = Alert(
            id='test_alert',
            timestamp=datetime.utcnow(),
            alert_type=AlertType.STRATEGY_FAILURE,
            severity=AlertSeverity.HIGH,
            title='Test Alert',
            message='This is a test alert',
            source='test'
        )
        
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await channel.send_notification(alert)
        
        assert result is True
        mock_post.assert_called_once()


class TestAlertManager:
    """Test alert manager."""
    
    def test_initialization(self):
        """Test alert manager initialization."""
        config = AlertingConfig()
        manager = AlertManager(config)
        
        assert manager.config == config
        assert manager.detector is not None
        assert len(manager._active_alerts) == 0
    
    async def test_process_alert(self):
        """Test processing an alert."""
        config = AlertingConfig()
        manager = AlertManager(config)
        
        alert = Alert(
            id='test_alert',
            timestamp=datetime.utcnow(),
            alert_type=AlertType.SYSTEM_ERROR,
            severity=AlertSeverity.CRITICAL,
            title='Test Alert',
            message='This is a test alert',
            source='test'
        )
        
        await manager._process_alert(alert)
        
        assert alert.id in manager._active_alerts
        assert len(manager._alert_history) == 1
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        config = AlertingConfig()
        manager = AlertManager(config)
        
        alert = Alert(
            id='test_alert',
            timestamp=datetime.utcnow(),
            alert_type=AlertType.SYSTEM_ERROR,
            severity=AlertSeverity.CRITICAL,
            title='Test Alert',
            message='This is a test alert',
            source='test'
        )
        
        manager._active_alerts[alert.id] = alert
        
        result = manager.acknowledge_alert(alert.id, 'test_user')
        
        assert result is True
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == 'test_user'
        assert alert.acknowledged_at is not None
    
    def test_resolve_alert(self):
        """Test resolving an alert."""
        config = AlertingConfig()
        manager = AlertManager(config)
        
        alert = Alert(
            id='test_alert',
            timestamp=datetime.utcnow(),
            alert_type=AlertType.SYSTEM_ERROR,
            severity=AlertSeverity.CRITICAL,
            title='Test Alert',
            message='This is a test alert',
            source='test'
        )
        
        manager._active_alerts[alert.id] = alert
        
        result = manager.resolve_alert(alert.id)
        
        assert result is True
        assert alert.status == AlertStatus.RESOLVED
        assert alert.resolved_at is not None
        assert alert.id not in manager._active_alerts


class TestMonitoringIntegration:
    """Test monitoring integration."""
    
    def test_initialization(self):
        """Test integration initialization."""
        config = OrchestratorConfig()
        performance_monitor = MockPerformanceMonitor()
        
        integration = MonitoringIntegration(config, performance_monitor)
        
        assert integration.config == config
        assert integration.performance_monitor == performance_monitor
        assert integration.orchestrator_monitor is not None
        assert integration.alert_manager is not None
    
    def test_record_orchestrator_activity(self):
        """Test recording orchestrator activity."""
        config = OrchestratorConfig()
        performance_monitor = MockPerformanceMonitor()
        
        integration = MonitoringIntegration(config, performance_monitor)
        
        # This should not raise an exception
        integration.record_orchestrator_activity(
            active_strategies=3,
            signals_generated=10,
            signals_executed=8,
            signals_rejected=2,
            processing_time_ms=150.0
        )
    
    def test_get_monitoring_status(self):
        """Test getting monitoring status."""
        config = OrchestratorConfig()
        performance_monitor = MockPerformanceMonitor()
        
        integration = MonitoringIntegration(config, performance_monitor)
        
        status = integration.get_monitoring_status()
        
        assert 'monitoring_active' in status
        assert 'alerting_active' in status
        assert 'system_health' in status
        assert 'active_strategies' in status
        assert 'active_alerts' in status


class TestMonitoringMetrics:
    """Test monitoring metrics helper."""
    
    def test_format_dashboard_for_api(self):
        """Test formatting dashboard data for API."""
        # Create mock dashboard data
        orchestrator_metrics = OrchestratorMetrics(
            timestamp=datetime.utcnow(),
            active_strategies=2,
            total_signals_generated=10,
            signals_executed=8,
            signals_rejected=2,
            processing_time_ms=150.0,
            allocation_changes=1,
            risk_violations=0,
            performance_score=85.0,
            system_health='healthy'
        )
        
        strategy_metrics = {
            'strategy1': StrategyHealthMetrics(
                strategy_name='strategy1',
                timestamp=datetime.utcnow(),
                is_active=True,
                signals_generated=5,
                signals_executed=4,
                error_count=0,
                last_error=None,
                performance_score=90.0,
                allocation=0.5,
                processing_time_ms=50.0,
                health_status='healthy'
            )
        }
        
        from src.orchestration.monitoring import DashboardData
        dashboard_data = DashboardData(
            timestamp=datetime.utcnow(),
            orchestrator_metrics=orchestrator_metrics,
            strategy_metrics=strategy_metrics,
            performance_summary={'total_return': 0.05},
            recent_alerts=[],
            system_status={'status': 'ok'},
            allocation_breakdown={'strategy1': 100.0},
            signal_flow={'total_generated': 10}
        )
        
        formatted = MonitoringMetrics.format_dashboard_for_api(dashboard_data)
        
        assert 'timestamp' in formatted
        assert 'orchestrator' in formatted
        assert 'strategies' in formatted
        assert 'performance' in formatted
        assert formatted['orchestrator']['active_strategies'] == 2
        assert 'strategy1' in formatted['strategies']
    
    def test_calculate_system_health_score(self):
        """Test calculating system health score."""
        # Create mock dashboard data with healthy system
        orchestrator_metrics = OrchestratorMetrics(
            timestamp=datetime.utcnow(),
            active_strategies=2,
            total_signals_generated=10,
            signals_executed=8,
            signals_rejected=2,
            processing_time_ms=150.0,
            allocation_changes=1,
            risk_violations=0,
            performance_score=85.0,
            system_health='healthy'
        )
        
        from src.orchestration.monitoring import DashboardData
        dashboard_data = DashboardData(
            timestamp=datetime.utcnow(),
            orchestrator_metrics=orchestrator_metrics,
            strategy_metrics={},
            performance_summary={'total_return': 0.05},
            recent_alerts=[],
            system_status={'status': 'ok'},
            allocation_breakdown={},
            signal_flow={}
        )
        
        score = MonitoringMetrics.calculate_system_health_score(dashboard_data)
        
        assert 0 <= score <= 100
        assert score > 50  # Should be above neutral for healthy system


if __name__ == '__main__':
    pytest.main([__file__])