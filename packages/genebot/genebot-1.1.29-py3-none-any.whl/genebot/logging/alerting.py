"""
Log-based alerting capabilities.

This module provides comprehensive alerting based on log patterns, error rates,
performance metrics, and other log-derived signals.
"""

import re
import time
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Pattern, Union
import logging

from .context import LogContext
from .monitoring import LogAlert, AlertType, AlertSeverity


class AlertCondition(Enum):
    """Types of alert conditions."""
    THRESHOLD = "threshold"
    RATE = "rate"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    ABSENCE = "absence"


class AlertOperator(Enum):
    """Alert comparison operators."""
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    CONTAINS = "contains"
    MATCHES = "matches"


@dataclass
class AlertRule:
    """Defines an alert rule."""
    name: str
    condition: AlertCondition
    operator: AlertOperator
    threshold: Union[float, int, str]
    severity: AlertSeverity
    description: str
    enabled: bool = True
    cooldown_minutes: int = 15
    tags: List[str] = field(default_factory=list)
    
    # Condition-specific parameters
    time_window_minutes: int = 5
    min_occurrences: int = 1
    pattern: Optional[str] = None
    logger_filter: Optional[str] = None
    level_filter: Optional[str] = None
    
    # State tracking
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def is_in_cooldown(self) -> bool:
        """Check if rule is in cooldown period."""
        if not self.last_triggered:
            return False
        
        cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
        return datetime.now() < cooldown_end
    
    def matches_log_entry(self, level: str, logger: str, message: str) -> bool:
        """Check if log entry matches rule filters."""
        if self.level_filter and level != self.level_filter:
            return False
        
        if self.logger_filter and not re.search(self.logger_filter, logger):
            return False
        
        return True


class AlertEngine:
    """Main alerting engine that processes log events and triggers alerts."""
    
    def __init__(self):
        """Initialize alert engine."""
        self.rules: Dict[str, AlertRule] = {}
        self.event_buffer: deque = deque(maxlen=10000)
        self.pattern_cache: Dict[str, Pattern] = {}
        self.statistics = defaultdict(lambda: defaultdict(int))
        self.rate_trackers = defaultdict(lambda: deque(maxlen=1000))
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[LogAlert], None]] = []
        
        # Thread safety
        self.lock = threading.RLock()
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        with self.lock:
            self.rules[rule.name] = rule
    
    def remove_rule(self, rule_name: str) -> None:
        """Remove an alert rule."""
        with self.lock:
            self.rules.pop(rule_name, None)
    
    def add_alert_callback(self, callback: Callable[[LogAlert], None]) -> None:
        """Add callback for alert notifications."""
        self.alert_callbacks.append(callback)
    
    def process_log_event(
        self,
        level: str,
        logger: str,
        message: str,
        timestamp: Optional[datetime] = None,
        context: Optional[LogContext] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Process a log event and check for alert conditions."""
        if timestamp is None:
            timestamp = datetime.now()
        
        event = {
            'timestamp': timestamp,
            'level': level,
            'logger': logger,
            'message': message,
            'context': context,
            'extra': extra or {}
        }
        
        with self.lock:
            # Add to event buffer
            self.event_buffer.append(event)
            
            # Update statistics
            self.statistics[logger][level] += 1
            self.statistics['_total'][level] += 1
            
            # Update rate trackers
            self.rate_trackers[f"{logger}:{level}"].append(timestamp)
            self.rate_trackers[f"_total:{level}"].append(timestamp)
            
            # Check all rules
            for rule in self.rules.values():
                if rule.enabled and not rule.is_in_cooldown():
                    if self._check_rule(rule, event):
                        self._trigger_alert(rule, event)
    
    def _check_rule(self, rule: AlertRule, event: Dict[str, Any]) -> bool:
        """Check if an event triggers an alert rule."""
        # Check basic filters
        if not rule.matches_log_entry(event['level'], event['logger'], event['message']):
            return False
        
        if rule.condition == AlertCondition.THRESHOLD:
            return self._check_threshold_condition(rule, event)
        elif rule.condition == AlertCondition.RATE:
            return self._check_rate_condition(rule, event)
        elif rule.condition == AlertCondition.PATTERN:
            return self._check_pattern_condition(rule, event)
        elif rule.condition == AlertCondition.ANOMALY:
            return self._check_anomaly_condition(rule, event)
        elif rule.condition == AlertCondition.ABSENCE:
            return self._check_absence_condition(rule, event)
        
        return False
    
    def _check_threshold_condition(self, rule: AlertRule, event: Dict[str, Any]) -> bool:
        """Check threshold-based condition."""
        # Count matching events in time window
        cutoff_time = datetime.now() - timedelta(minutes=rule.time_window_minutes)
        
        matching_events = 0
        for buffered_event in reversed(self.event_buffer):
            if buffered_event['timestamp'] < cutoff_time:
                break
            
            if (rule.matches_log_entry(
                buffered_event['level'],
                buffered_event['logger'],
                buffered_event['message']
            )):
                matching_events += 1
        
        # Check threshold
        if rule.operator == AlertOperator.GREATER_THAN:
            return matching_events > rule.threshold
        elif rule.operator == AlertOperator.LESS_THAN:
            return matching_events < rule.threshold
        elif rule.operator == AlertOperator.EQUAL:
            return matching_events == rule.threshold
        elif rule.operator == AlertOperator.NOT_EQUAL:
            return matching_events != rule.threshold
        
        return False
    
    def _check_rate_condition(self, rule: AlertRule, event: Dict[str, Any]) -> bool:
        """Check rate-based condition."""
        tracker_key = f"{event['logger']}:{event['level']}"
        if rule.logger_filter == "_total":
            tracker_key = f"_total:{event['level']}"
        
        rate_data = self.rate_trackers[tracker_key]
        if not rate_data:
            return False
        
        # Calculate rate in time window
        cutoff_time = datetime.now() - timedelta(minutes=rule.time_window_minutes)
        recent_events = [t for t in rate_data if t >= cutoff_time]
        
        rate_per_minute = len(recent_events) / rule.time_window_minutes
        
        # Check rate threshold
        if rule.operator == AlertOperator.GREATER_THAN:
            return rate_per_minute > rule.threshold
        elif rule.operator == AlertOperator.LESS_THAN:
            return rate_per_minute < rule.threshold
        
        return False
    
    def _check_pattern_condition(self, rule: AlertRule, event: Dict[str, Any]) -> bool:
        """Check pattern-based condition."""
        if not rule.pattern:
            return False
        
        # Get or compile pattern
        if rule.pattern not in self.pattern_cache:
            try:
                self.pattern_cache[rule.pattern] = re.compile(rule.pattern, re.IGNORECASE)
            except re.error:
                logging.getLogger(__name__).error(f"Invalid regex pattern in rule {rule.name}: {rule.pattern}")
                return False
        
        pattern = self.pattern_cache[rule.pattern]
        
        # Check if pattern matches message
        if rule.operator == AlertOperator.MATCHES:
            return bool(pattern.search(event['message']))
        elif rule.operator == AlertOperator.CONTAINS:
            return rule.threshold.lower() in event['message'].lower()
        
        return False
    
    def _check_anomaly_condition(self, rule: AlertRule, event: Dict[str, Any]) -> bool:
        """Check anomaly-based condition."""
        # Simple anomaly detection based on historical rates
        tracker_key = f"{event['logger']}:{event['level']}"
        rate_data = self.rate_trackers[tracker_key]
        
        if len(rate_data) < 50:  # Need enough historical data
            return False
        
        # Calculate recent rate vs historical average
        cutoff_time = datetime.now() - timedelta(minutes=rule.time_window_minutes)
        recent_events = [t for t in rate_data if t >= cutoff_time]
        recent_rate = len(recent_events) / rule.time_window_minutes
        
        # Calculate historical average (excluding recent window)
        historical_cutoff = datetime.now() - timedelta(minutes=rule.time_window_minutes * 2)
        historical_events = [t for t in rate_data if t < cutoff_time and t >= historical_cutoff]
        
        if not historical_events:
            return False
        
        historical_rate = len(historical_events) / rule.time_window_minutes
        
        # Check for anomaly (rate significantly higher than historical)
        if historical_rate > 0:
            rate_ratio = recent_rate / historical_rate
            return rate_ratio > rule.threshold  # e.g., 3x higher than normal
        
        return False
    
    def _check_absence_condition(self, rule: AlertRule, event: Dict[str, Any]) -> bool:
        """Check absence-based condition (alert when expected logs are missing)."""
        # This is checked periodically, not on each event
        # For now, return False as it requires different handling
        return False
    
    def _trigger_alert(self, rule: AlertRule, event: Dict[str, Any]) -> None:
        """Trigger an alert for a rule."""
        rule.last_triggered = datetime.now()
        rule.trigger_count += 1
        
        # Create alert
        alert = LogAlert(
            alert_type=self._get_alert_type_from_rule(rule),
            severity=rule.severity,
            message=self._generate_alert_message(rule, event),
            timestamp=datetime.now(),
            context=event.get('context'),
            metrics=self._get_alert_metrics(rule, event),
            suggested_actions=self._get_suggested_actions(rule, event)
        )
        
        # Send alert to callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logging.getLogger(__name__).error(f"Alert callback failed: {e}")
    
    def _get_alert_type_from_rule(self, rule: AlertRule) -> AlertType:
        """Get alert type based on rule characteristics."""
        if rule.condition == AlertCondition.RATE and 'error' in rule.name.lower():
            return AlertType.ERROR_RATE
        elif 'performance' in rule.name.lower():
            return AlertType.PERFORMANCE_DEGRADATION
        elif 'volume' in rule.name.lower():
            return AlertType.LOG_VOLUME
        elif 'security' in rule.name.lower():
            return AlertType.SECURITY_VIOLATION
        else:
            return AlertType.CONFIGURATION_ERROR
    
    def _generate_alert_message(self, rule: AlertRule, event: Dict[str, Any]) -> str:
        """Generate alert message."""
        base_message = f"Alert rule '{rule.name}' triggered"
        
        if rule.condition == AlertCondition.THRESHOLD:
            return f"{base_message}: threshold condition met"
        elif rule.condition == AlertCondition.RATE:
            return f"{base_message}: rate condition exceeded"
        elif rule.condition == AlertCondition.PATTERN:
            return f"{base_message}: pattern matched in log message"
        elif rule.condition == AlertCondition.ANOMALY:
            return f"{base_message}: anomalous behavior detected"
        
        return base_message
    
    def _get_alert_metrics(self, rule: AlertRule, event: Dict[str, Any]) -> Dict[str, float]:
        """Get metrics for the alert."""
        metrics = {
            'trigger_count': float(rule.trigger_count),
            'time_window_minutes': float(rule.time_window_minutes)
        }
        
        if rule.condition == AlertCondition.RATE:
            tracker_key = f"{event['logger']}:{event['level']}"
            rate_data = self.rate_trackers[tracker_key]
            cutoff_time = datetime.now() - timedelta(minutes=rule.time_window_minutes)
            recent_events = [t for t in rate_data if t >= cutoff_time]
            metrics['current_rate'] = len(recent_events) / rule.time_window_minutes
        
        return metrics
    
    def _get_suggested_actions(self, rule: AlertRule, event: Dict[str, Any]) -> List[str]:
        """Get suggested actions for the alert."""
        actions = []
        
        if rule.condition == AlertCondition.RATE and 'error' in rule.name.lower():
            actions.extend([
                "Check application logs for error details",
                "Verify system resources and dependencies",
                "Review recent deployments or configuration changes"
            ])
        elif 'performance' in rule.name.lower():
            actions.extend([
                "Check system resources (CPU, memory, disk)",
                "Review performance metrics and bottlenecks",
                "Consider scaling or optimization"
            ])
        elif rule.condition == AlertCondition.PATTERN:
            actions.extend([
                "Investigate the specific log message pattern",
                "Check for related system issues",
                "Review application behavior"
            ])
        
        # Add rule-specific tags as actions if they look like actions
        for tag in rule.tags:
            if tag.startswith('action:'):
                actions.append(tag[7:])  # Remove 'action:' prefix
        
        return actions
    
    def check_absence_rules(self) -> None:
        """Check rules for log absence conditions."""
        with self.lock:
            for rule in self.rules.values():
                if (rule.enabled and 
                    rule.condition == AlertCondition.ABSENCE and 
                    not rule.is_in_cooldown()):
                    
                    if self._check_absence_rule(rule):
                        # Create a synthetic event for absence
                        event = {
                            'timestamp': datetime.now(),
                            'level': 'WARNING',
                            'logger': rule.logger_filter or 'unknown',
                            'message': f"Expected logs missing for rule: {rule.name}",
                            'context': None,
                            'extra': {}
                        }
                        self._trigger_alert(rule, event)
    
    def _check_absence_rule(self, rule: AlertRule) -> bool:
        """Check if expected logs are absent."""
        cutoff_time = datetime.now() - timedelta(minutes=rule.time_window_minutes)
        
        # Look for matching events in the time window
        matching_events = 0
        for event in reversed(self.event_buffer):
            if event['timestamp'] < cutoff_time:
                break
            
            if rule.matches_log_entry(event['level'], event['logger'], event['message']):
                matching_events += 1
        
        # Alert if fewer than expected minimum occurrences
        return matching_events < rule.min_occurrences
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get alerting statistics."""
        with self.lock:
            return {
                'rules': {
                    'total': len(self.rules),
                    'enabled': sum(1 for r in self.rules.values() if r.enabled),
                    'triggered': sum(1 for r in self.rules.values() if r.trigger_count > 0)
                },
                'events_processed': len(self.event_buffer),
                'recent_triggers': [
                    {
                        'rule': rule.name,
                        'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None,
                        'trigger_count': rule.trigger_count
                    }
                    for rule in self.rules.values()
                    if rule.trigger_count > 0
                ]
            }


class AlertRuleBuilder:
    """Builder for creating alert rules."""
    
    def __init__(self, name: str):
        """Initialize builder with rule name."""
        self.rule = AlertRule(
            name=name,
            condition=AlertCondition.THRESHOLD,
            operator=AlertOperator.GREATER_THAN,
            threshold=1,
            severity=AlertSeverity.MEDIUM,
            description=""
        )
    
    def threshold(self, value: Union[int, float], operator: AlertOperator = AlertOperator.GREATER_THAN) -> 'AlertRuleBuilder':
        """Set threshold condition."""
        self.rule.condition = AlertCondition.THRESHOLD
        self.rule.threshold = value
        self.rule.operator = operator
        return self
    
    def rate(self, events_per_minute: float, operator: AlertOperator = AlertOperator.GREATER_THAN) -> 'AlertRuleBuilder':
        """Set rate condition."""
        self.rule.condition = AlertCondition.RATE
        self.rule.threshold = events_per_minute
        self.rule.operator = operator
        return self
    
    def pattern(self, regex_pattern: str) -> 'AlertRuleBuilder':
        """Set pattern condition."""
        self.rule.condition = AlertCondition.PATTERN
        self.rule.pattern = regex_pattern
        self.rule.operator = AlertOperator.MATCHES
        return self
    
    def anomaly(self, multiplier: float = 3.0) -> 'AlertRuleBuilder':
        """Set anomaly condition."""
        self.rule.condition = AlertCondition.ANOMALY
        self.rule.threshold = multiplier
        return self
    
    def absence(self, min_expected: int = 1) -> 'AlertRuleBuilder':
        """Set absence condition."""
        self.rule.condition = AlertCondition.ABSENCE
        self.rule.min_occurrences = min_expected
        return self
    
    def severity(self, level: AlertSeverity) -> 'AlertRuleBuilder':
        """Set alert severity."""
        self.rule.severity = level
        return self
    
    def description(self, text: str) -> 'AlertRuleBuilder':
        """Set rule description."""
        self.rule.description = text
        return self
    
    def time_window(self, minutes: int) -> 'AlertRuleBuilder':
        """Set time window for evaluation."""
        self.rule.time_window_minutes = minutes
        return self
    
    def cooldown(self, minutes: int) -> 'AlertRuleBuilder':
        """Set cooldown period."""
        self.rule.cooldown_minutes = minutes
        return self
    
    def filter_logger(self, logger_pattern: str) -> 'AlertRuleBuilder':
        """Filter by logger name pattern."""
        self.rule.logger_filter = logger_pattern
        return self
    
    def filter_level(self, level: str) -> 'AlertRuleBuilder':
        """Filter by log level."""
        self.rule.level_filter = level
        return self
    
    def tags(self, *tag_list: str) -> 'AlertRuleBuilder':
        """Add tags to the rule."""
        self.rule.tags.extend(tag_list)
        return self
    
    def build(self) -> AlertRule:
        """Build the alert rule."""
        return self.rule


# Pre-defined alert rules
def create_default_alert_rules() -> List[AlertRule]:
    """Create a set of default alert rules."""
    rules = []
    
    # High error rate
    rules.append(
        AlertRuleBuilder("high_error_rate")
        .rate(10.0)  # More than 10 errors per minute
        .filter_level("ERROR")
        .severity(AlertSeverity.HIGH)
        .description("High error rate detected")
        .time_window(5)
        .cooldown(15)
        .tags("error", "rate", "action:Check application logs")
        .build()
    )
    
    # Critical errors
    rules.append(
        AlertRuleBuilder("critical_errors")
        .threshold(1)  # Any critical error
        .filter_level("CRITICAL")
        .severity(AlertSeverity.CRITICAL)
        .description("Critical error occurred")
        .time_window(1)
        .cooldown(5)
        .tags("critical", "error", "action:Immediate investigation required")
        .build()
    )
    
    # Security violations
    rules.append(
        AlertRuleBuilder("security_violations")
        .pattern(r"(unauthorized|forbidden|access denied|security violation)")
        .severity(AlertSeverity.HIGH)
        .description("Security-related log message detected")
        .time_window(5)
        .cooldown(10)
        .tags("security", "pattern", "action:Review security logs")
        .build()
    )
    
    # Performance degradation
    rules.append(
        AlertRuleBuilder("performance_degradation")
        .pattern(r"(timeout|slow|performance|degradation)")
        .severity(AlertSeverity.MEDIUM)
        .description("Performance issue detected in logs")
        .time_window(10)
        .cooldown(20)
        .tags("performance", "pattern", "action:Check system resources")
        .build()
    )
    
    # High log volume
    rules.append(
        AlertRuleBuilder("high_log_volume")
        .rate(1000.0)  # More than 1000 logs per minute
        .severity(AlertSeverity.MEDIUM)
        .description("Unusually high log volume")
        .time_window(5)
        .cooldown(30)
        .tags("volume", "rate", "action:Check for log loops")
        .build()
    )
    
    # Missing heartbeat (absence rule)
    rules.append(
        AlertRuleBuilder("missing_heartbeat")
        .absence(1)  # Expect at least 1 heartbeat
        .filter_logger(".*heartbeat.*")
        .severity(AlertSeverity.HIGH)
        .description("Application heartbeat missing")
        .time_window(10)
        .cooldown(5)
        .tags("heartbeat", "absence", "action:Check application status")
        .build()
    )
    
    return rules


# Global alert engine instance
_global_alert_engine: Optional[AlertEngine] = None


def get_global_alert_engine() -> AlertEngine:
    """Get the global alert engine instance."""
    global _global_alert_engine
    if _global_alert_engine is None:
        _global_alert_engine = AlertEngine()
        
        # Add default rules
        for rule in create_default_alert_rules():
            _global_alert_engine.add_rule(rule)
    
    return _global_alert_engine


def setup_log_alerting(config: Dict[str, Any]) -> AlertEngine:
    """Set up log alerting based on configuration."""
    engine = get_global_alert_engine()
    
    # Load custom rules from config
    custom_rules = config.get('alert_rules', [])
    for rule_config in custom_rules:
        rule = AlertRule(**rule_config)
        engine.add_rule(rule)
    
    # Set up alert callbacks based on config
    if config.get('slack', {}).get('enabled', False):
        from .monitoring import SlackHook
        slack_hook = SlackHook(
            webhook_url=config['slack']['webhook_url'],
            channel=config['slack'].get('channel')
        )
        engine.add_alert_callback(lambda alert: slack_hook.send_alert(alert))
    
    if config.get('email', {}).get('enabled', False):
        # Email alerting would be implemented here
        pass
    
    return engine