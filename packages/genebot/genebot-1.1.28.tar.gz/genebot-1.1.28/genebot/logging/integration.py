"""
Integration module for logging monitoring and alerting.

This module provides a unified interface to set up and manage all logging
monitoring, alerting, and aggregation features.
"""

import os
import yaml
import threading
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .config import LoggingConfig
from .factory import setup_global_config, get_logger
from .monitoring import get_global_monitor, setup_monitoring_hooks
from .alerting import get_global_alert_engine, setup_log_alerting
from .aggregation import setup_log_aggregation


class LoggingIntegrationManager:
    """Manages all logging integration features."""
    
    def __init__(self):
        """Initialize integration manager."""
        self.config: Optional[Dict[str, Any]] = None
        self.monitoring_config: Optional[Dict[str, Any]] = None
        self.is_initialized = False
        self.monitor = None
        self.alert_engine = None
        self.aggregation_handler = None
        
        # Health check thread
        self.health_check_thread = None
        self.health_check_active = False
    
    def initialize(
        self,
        logging_config_path: Optional[Path] = None,
        monitoring_config_path: Optional[Path] = None
    ) -> None:
        """
        Initialize all logging integration features.
        
        Args:
            logging_config_path: Path to logging configuration file
            monitoring_config_path: Path to monitoring configuration file
        """
        if self.is_initialized:
            return
        
        # Load configurations
        self._load_configurations(logging_config_path, monitoring_config_path)
        
        # Setup core logging
        self._setup_core_logging()
        
        # Setup monitoring
        self._setup_monitoring()
        
        # Setup alerting
        self._setup_alerting()
        
        # Setup aggregation
        self._setup_aggregation()
        
        # Setup health checks
        self._setup_health_checks()
        
        # Integrate components
        self._integrate_components()
        
        self.is_initialized = True
        
        logger = get_logger(__name__)
        logger.info("Logging integration initialized successfully")
    
    def _load_configurations(
        self,
        logging_config_path: Optional[Path],
        monitoring_config_path: Optional[Path]
    ) -> None:
        """Load configuration files."""
        # Load main logging config
        if logging_config_path and logging_config_path.exists():
            self.config = LoggingConfig.from_file(logging_config_path).to_dict()
        else:
            # Use default config
            from .config import get_default_config
            self.config = get_default_config().to_dict()
        
        # Load monitoring config
        if monitoring_config_path and monitoring_config_path.exists():
            with open(monitoring_config_path, 'r') as f:
                self.monitoring_config = yaml.safe_load(f)
        else:
            # Try default location
            default_monitoring_config = Path("config/logging_monitoring_config.yaml")
            if default_monitoring_config.exists():
                with open(default_monitoring_config, 'r') as f:
                    self.monitoring_config = yaml.safe_load(f)
            else:
                self.monitoring_config = self._get_default_monitoring_config()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment-specific configuration overrides."""
        if not self.monitoring_config:
            return
        
        environment = os.getenv('ENVIRONMENT', 'development')
        env_overrides = self.monitoring_config.get('environments', {}).get(environment, {})
        
        if env_overrides:
            # Deep merge environment overrides
            self._deep_merge_dict(self.monitoring_config, env_overrides)
    
    def _deep_merge_dict(self, base_dict: Dict[str, Any], override_dict: Dict[str, Any]) -> None:
        """Deep merge override dictionary into base dictionary."""
        for key, value in override_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge_dict(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _setup_core_logging(self) -> None:
        """Setup core logging configuration."""
        logging_config = LoggingConfig(**self.config)
        setup_global_config(logging_config)
    
    def _setup_monitoring(self) -> None:
        """Setup monitoring features."""
        monitoring_config = self.monitoring_config.get('monitoring', {})
        
        if not monitoring_config.get('enabled', True):
            return
        
        self.monitor = get_global_monitor()
        
        # Setup monitoring hooks
        setup_monitoring_hooks(monitoring_config)
        
        # Start monitoring
        interval = monitoring_config.get('monitoring_interval', 60.0)
        self.monitor.start_monitoring(interval)
    
    def _setup_alerting(self) -> None:
        """Setup alerting features."""
        alerting_config = self.monitoring_config.get('alerting', {})
        
        if not alerting_config.get('enabled', True):
            return
        
        self.alert_engine = setup_log_alerting(alerting_config)
        
        # Setup notification channels
        self._setup_notification_channels()
    
    def _setup_aggregation(self) -> None:
        """Setup log aggregation features."""
        aggregation_config = self.monitoring_config.get('aggregation', {})
        
        if not aggregation_config.get('enabled', False):
            return
        
        self.aggregation_handler = setup_log_aggregation(aggregation_config)
        
        if self.aggregation_handler:
            # Add to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(self.aggregation_handler)
    
    def _setup_health_checks(self) -> None:
        """Setup health check monitoring."""
        health_config = self.monitoring_config.get('health_checks', {})
        
        if not health_config.get('enabled', True):
            return
        
        interval = health_config.get('interval_seconds', 300)
        
        self.health_check_active = True
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            args=(interval,),
            daemon=True,
            name="LoggingHealthCheck"
        )
        self.health_check_thread.start()
    
    def _setup_notification_channels(self) -> None:
        """Setup notification channels for alerts."""
        notifications_config = self.monitoring_config.get('notifications', {})
        
        # Email notifications
        if notifications_config.get('email', {}).get('enabled', False):
            self._setup_email_notifications(notifications_config['email'])
        
        # Webhook notifications
        if notifications_config.get('webhook', {}).get('enabled', False):
            self._setup_webhook_notifications(notifications_config['webhook'])
        
        # Custom script notifications
        if notifications_config.get('custom_script', {}).get('enabled', False):
            self._setup_custom_script_notifications(notifications_config['custom_script'])
    
    def _setup_email_notifications(self, email_config: Dict[str, Any]) -> None:
        """Setup email notification callback."""
        def send_email_alert(alert):
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                msg = MIMEMultipart()
                msg['From'] = email_config['from_address']
                msg['To'] = ', '.join(email_config['to_addresses'])
                msg['Subject'] = f"Trading Bot Alert: {alert.alert_type.value}"
                
                body = f"""
Alert Details:
- Type: {alert.alert_type.value}
- Severity: {alert.severity.value}
- Message: {alert.message}
- Time: {alert.timestamp}

Suggested Actions:
{chr(10).join(['- ' + action for action in alert.suggested_actions or []])}
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
                server.quit()
                
            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to send email alert: {e}")
        
        if self.alert_engine:
            self.alert_engine.add_alert_callback(send_email_alert)
    
    def _setup_webhook_notifications(self, webhook_config: Dict[str, Any]) -> None:
        """Setup webhook notification callback."""
        def send_webhook_alert(alert):
            try:
                import requests
                
                payload = alert.to_dict()
                headers = webhook_config.get('headers', {})
                
                response = requests.post(
                    webhook_config['url'],
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code not in [200, 201, 202]:
                    logging.getLogger(__name__).warning(
                        f"Webhook alert failed: {response.status_code}"
                    )
                    
            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to send webhook alert: {e}")
        
        if self.alert_engine:
            self.alert_engine.add_alert_callback(send_webhook_alert)
    
    def _setup_custom_script_notifications(self, script_config: Dict[str, Any]) -> None:
        """Setup custom script notification callback."""
        def run_custom_script_alert(alert):
            try:
                import subprocess
                import json
                
                script_path = script_config['script_path']
                timeout = script_config.get('timeout_seconds', 30)
                
                # Pass alert data as JSON to script
                alert_json = json.dumps(alert.to_dict())
                
                result = subprocess.run(
                    ['python', script_path],
                    input=alert_json,
                    text=True,
                    timeout=timeout,
                    capture_output=True
                )
                
                if result.returncode != 0:
                    logging.getLogger(__name__).warning(
                        f"Custom alert script failed: {result.stderr}"
                    )
                    
            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to run custom alert script: {e}")
        
        if self.alert_engine:
            self.alert_engine.add_alert_callback(run_custom_script_alert)
    
    def _integrate_components(self) -> None:
        """Integrate monitoring and alerting components."""
        if not (self.monitor and self.alert_engine):
            return
        
        # Connect monitor to alert engine
        def monitor_callback(alert):
            # Monitor alerts are already LogAlert objects
            pass  # Monitor handles its own alert sending
        
        # Connect alert engine to monitor for log events
        original_process_log_event = self.alert_engine.process_log_event
        
        def enhanced_process_log_event(*args, **kwargs):
            # Process in alert engine
            original_process_log_event(*args, **kwargs)
            
            # Also record in monitor if available
            if len(args) >= 3:
                level, logger_name = args[0], args[1]
                context = kwargs.get('context')
                self.monitor.record_log_event(level, logger_name, context)
        
        self.alert_engine.process_log_event = enhanced_process_log_event
    
    def _health_check_loop(self, interval: float) -> None:
        """Health check monitoring loop."""
        import time
        
        while self.health_check_active:
            try:
                self._perform_health_checks()
                time.sleep(interval)
            except Exception as e:
                logging.getLogger(__name__).error(f"Health check error: {e}")
                time.sleep(interval)
    
    def _perform_health_checks(self) -> None:
        """Perform health checks."""
        health_config = self.monitoring_config.get('health_checks', {})
        checks = health_config.get('checks', [])
        
        for check_config in checks:
            if not check_config.get('enabled', True):
                continue
            
            check_name = check_config['name']
            
            try:
                if check_name == 'log_file_growth':
                    self._check_log_file_growth()
                elif check_name == 'disk_space':
                    self._check_disk_space(check_config)
                elif check_name == 'log_rotation':
                    self._check_log_rotation()
                elif check_name == 'handler_health':
                    self._check_handler_health()
                    
            except Exception as e:
                logging.getLogger(__name__).error(f"Health check '{check_name}' failed: {e}")
    
    def _check_log_file_growth(self) -> None:
        """Check if log files are growing (indicating active logging)."""
        # This would check file modification times and sizes
        pass
    
    def _check_disk_space(self, check_config: Dict[str, Any]) -> None:
        """Check available disk space."""
        import shutil
        
        log_dir = Path(self.config.get('log_directory', 'logs'))
        if not log_dir.exists():
            return
        
        total, used, free = shutil.disk_usage(log_dir)
        usage_percent = (used / total) * 100
        
        threshold = check_config.get('threshold_percent', 90)
        
        if usage_percent > threshold:
            if self.alert_engine:
                from .monitoring import LogAlert, AlertType, AlertSeverity
                
                alert = LogAlert(
                    alert_type=AlertType.DISK_SPACE,
                    severity=AlertSeverity.HIGH,
                    message=f"High disk usage: {usage_percent:.1f}% used",
                    timestamp=datetime.now(),
                    metrics={'disk_usage_percent': usage_percent}
                )
                
                self.alert_engine.send_alert(alert)
    
    def _check_log_rotation(self) -> None:
        """Check if log rotation is working properly."""
        # This would check for rotated log files and proper cleanup
        pass
    
    def _check_handler_health(self) -> None:
        """Check if log handlers are functioning."""
        # This would test each handler's functionality
        pass
    
    def _get_default_monitoring_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration."""
        return {
            'monitoring': {
                'enabled': True,
                'monitoring_interval': 60.0
            },
            'alerting': {
                'enabled': True,
                'rules': []
            },
            'aggregation': {
                'enabled': False
            },
            'health_checks': {
                'enabled': True,
                'interval_seconds': 300
            }
        }
    
    def shutdown(self) -> None:
        """Shutdown all integration components."""
        if not self.is_initialized:
            return
        
        # Stop health checks
        self.health_check_active = False
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5.0)
        
        # Stop monitoring
        if self.monitor:
            self.monitor.stop_monitoring()
        
        # Close aggregation handler
        if self.aggregation_handler:
            self.aggregation_handler.close()
        
        self.is_initialized = False
        
        logger = get_logger(__name__)
        logger.info("Logging integration shutdown complete")


# Global integration manager instance
_global_integration_manager: Optional[LoggingIntegrationManager] = None


def get_integration_manager() -> LoggingIntegrationManager:
    """Get the global integration manager instance."""
    global _global_integration_manager
    if _global_integration_manager is None:
        _global_integration_manager = LoggingIntegrationManager()
    return _global_integration_manager


def initialize_logging_integration(
    logging_config_path: Optional[Path] = None,
    monitoring_config_path: Optional[Path] = None
) -> LoggingIntegrationManager:
    """
    Initialize complete logging integration.
    
    Args:
        logging_config_path: Path to logging configuration file
        monitoring_config_path: Path to monitoring configuration file
        
    Returns:
        Initialized LoggingIntegrationManager
    """
    manager = get_integration_manager()
    manager.initialize(logging_config_path, monitoring_config_path)
    return manager


def shutdown_logging_integration() -> None:
    """Shutdown logging integration."""
    manager = get_integration_manager()
    manager.shutdown()


# Integration with existing logging system
class IntegratedLogHandler(logging.Handler):
    """Handler that integrates with monitoring and alerting."""
    
    def __init__(self):
        """Initialize integrated handler."""
        super().__init__()
        self.manager = get_integration_manager()
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record to integrated systems."""
        try:
            # Send to alert engine if available
            if self.manager.alert_engine:
                context = getattr(record, 'context', None)
                extra = getattr(record, 'extra', {})
                
                self.manager.alert_engine.process_log_event(
                    level=record.levelname,
                    logger=record.name,
                    message=record.getMessage(),
                    timestamp=datetime.fromtimestamp(record.created),
                    context=context,
                    extra=extra
                )
            
            # Send to monitor if available
            if self.manager.monitor:
                context = getattr(record, 'context', None)
                self.manager.monitor.record_log_event(
                    level=record.levelname,
                    logger_name=record.name,
                    context=context
                )
                
        except Exception:
            self.handleError(record)


def setup_integrated_logging() -> None:
    """Setup integrated logging with monitoring and alerting."""
    # Initialize integration
    manager = initialize_logging_integration()
    
    # Add integrated handler to root logger
    root_logger = logging.getLogger()
    integrated_handler = IntegratedLogHandler()
    root_logger.addHandler(integrated_handler)
    
    # Setup signal handlers for graceful shutdown
    import signal
    import atexit
    
    def shutdown_handler(signum, frame):
        shutdown_logging_integration()
    
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    atexit.register(shutdown_logging_integration)