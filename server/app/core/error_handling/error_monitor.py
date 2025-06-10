"""
Error Monitoring and Alerting System.

Provides comprehensive error monitoring, metrics collection, and alerting capabilities.
"""

import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
import logging
import json
from collections import defaultdict, deque

from .exceptions import MonitoringError, AlertingError
from .error_manager import ErrorContext, ErrorSeverity, ErrorCategory


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"


@dataclass
class AlertRule:
    """Configuration for an alert rule."""
    name: str
    description: str
    condition: Callable[[Dict[str, Any]], bool]
    level: AlertLevel
    channels: List[AlertChannel]
    cooldown_minutes: int = 15  # Minimum time between alerts
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """An alert instance."""
    rule_name: str
    level: AlertLevel
    message: str
    timestamp: datetime
    data: Dict[str, Any]
    channels: List[AlertChannel]
    alert_id: str = None
    
    def __post_init__(self):
        if not self.alert_id:
            self.alert_id = f"{self.rule_name}_{int(self.timestamp.timestamp())}"


@dataclass
class ErrorMetrics:
    """Error metrics for monitoring."""
    total_errors: int = 0
    errors_by_category: Dict[str, int] = field(default_factory=dict)
    errors_by_severity: Dict[str, int] = field(default_factory=dict)
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    error_rate_per_minute: float = 0.0
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_error(self, error_context: ErrorContext):
        """Add an error to the metrics."""
        self.total_errors += 1
        
        # Count by category
        category = error_context.category.value
        self.errors_by_category[category] = self.errors_by_category.get(category, 0) + 1
        
        # Count by severity
        severity = error_context.severity.value
        self.errors_by_severity[severity] = self.errors_by_severity.get(severity, 0) + 1
        
        # Count by type
        error_type = error_context.exception_type
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
        
        # Add to recent errors
        self.recent_errors.append(error_context)
        
        # Calculate error rate (errors per minute over last 5 minutes)
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        recent_count = sum(1 for error in self.recent_errors 
                          if error.timestamp > cutoff_time)
        self.error_rate_per_minute = recent_count / 5.0


class AlertManager:
    """Manages alert rules and delivery."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._rules: Dict[str, AlertRule] = {}
        self._alert_history: List[Alert] = []
        self._last_alert_times: Dict[str, datetime] = {}
        self._alert_handlers: Dict[AlertChannel, Callable] = {}
        self._lock = threading.RLock()
        
        # Setup default alert handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default alert handlers."""
        def log_handler(alert: Alert):
            log_level = {
                AlertLevel.INFO: logging.INFO,
                AlertLevel.WARNING: logging.WARNING,
                AlertLevel.ERROR: logging.ERROR,
                AlertLevel.CRITICAL: logging.CRITICAL
            }.get(alert.level, logging.INFO)
            
            self.logger.log(log_level, f"ALERT [{alert.level.value.upper()}]: {alert.message}")
        
        self._alert_handlers[AlertChannel.LOG] = log_handler
    
    def register_alert_handler(self, channel: AlertChannel, handler: Callable[[Alert], None]):
        """Register a custom alert handler for a channel."""
        self._alert_handlers[channel] = handler
        self.logger.info(f"Registered alert handler for channel: {channel.value}")
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        with self._lock:
            self._rules[rule.name] = rule
            self.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove an alert rule."""
        with self._lock:
            if rule_name in self._rules:
                del self._rules[rule_name]
                self.logger.info(f"Removed alert rule: {rule_name}")
    
    def enable_rule(self, rule_name: str):
        """Enable an alert rule."""
        with self._lock:
            if rule_name in self._rules:
                self._rules[rule_name].enabled = True
    
    def disable_rule(self, rule_name: str):
        """Disable an alert rule."""
        with self._lock:
            if rule_name in self._rules:
                self._rules[rule_name].enabled = False
    
    def check_rules(self, metrics_data: Dict[str, Any]):
        """Check all alert rules against current metrics."""
        with self._lock:
            triggered_alerts = []
            
            for rule in self._rules.values():
                if not rule.enabled:
                    continue
                
                try:
                    # Check cooldown
                    last_alert_time = self._last_alert_times.get(rule.name)
                    if last_alert_time:
                        cooldown_end = last_alert_time + timedelta(minutes=rule.cooldown_minutes)
                        if datetime.utcnow() < cooldown_end:
                            continue
                    
                    # Evaluate rule condition
                    if rule.condition(metrics_data):
                        alert = self._create_alert(rule, metrics_data)
                        triggered_alerts.append(alert)
                        self._last_alert_times[rule.name] = datetime.utcnow()
                
                except Exception as e:
                    self.logger.error(f"Error evaluating alert rule '{rule.name}': {e}")
            
            # Send alerts
            for alert in triggered_alerts:
                self._send_alert(alert)
    
    def _create_alert(self, rule: AlertRule, metrics_data: Dict[str, Any]) -> Alert:
        """Create an alert from a rule and metrics data."""
        message = f"Alert: {rule.description}"
        
        return Alert(
            rule_name=rule.name,
            level=rule.level,
            message=message,
            timestamp=datetime.utcnow(),
            data=metrics_data.copy(),
            channels=rule.channels
        )
    
    def _send_alert(self, alert: Alert):
        """Send an alert through configured channels."""
        self._alert_history.append(alert)
        
        # Keep only recent alerts
        if len(self._alert_history) > 1000:
            self._alert_history = self._alert_history[-1000:]
        
        for channel in alert.channels:
            try:
                if channel in self._alert_handlers:
                    self._alert_handlers[channel](alert)
                else:
                    self.logger.warning(f"No handler registered for alert channel: {channel.value}")
            except Exception as e:
                self.logger.error(f"Failed to send alert via {channel.value}: {e}")
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self._alert_history if alert.timestamp > cutoff_time]


class ErrorMonitor:
    """Main error monitoring system."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._metrics = ErrorMetrics()
        self._alert_manager = AlertManager(logger)
        self._monitoring_enabled = True
        self._lock = threading.RLock()
        
        # Setup default alert rules
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules for common scenarios."""
        
        # High error rate rule
        def high_error_rate_condition(data: Dict[str, Any]) -> bool:
            error_rate = data.get('error_rate_per_minute', 0)
            return error_rate > 10  # More than 10 errors per minute
        
        high_error_rate_rule = AlertRule(
            name="high_error_rate",
            description="High error rate detected (>10 errors/minute)",
            condition=high_error_rate_condition,
            level=AlertLevel.WARNING,
            channels=[AlertChannel.LOG],
            cooldown_minutes=5
        )
        
        # Critical error rule
        def critical_error_condition(data: Dict[str, Any]) -> bool:
            critical_errors = data.get('errors_by_severity', {}).get('critical', 0)
            return critical_errors > 0
        
        critical_error_rule = AlertRule(
            name="critical_error",
            description="Critical error detected",
            condition=critical_error_condition,
            level=AlertLevel.CRITICAL,
            channels=[AlertChannel.LOG],
            cooldown_minutes=1
        )
        
        # Many database errors rule
        def database_error_condition(data: Dict[str, Any]) -> bool:
            db_errors = data.get('errors_by_category', {}).get('database', 0)
            total_errors = data.get('total_errors', 1)
            return db_errors > 0 and (db_errors / total_errors) > 0.5  # >50% are database errors
        
        database_error_rule = AlertRule(
            name="database_errors",
            description="High proportion of database errors detected",
            condition=database_error_condition,
            level=AlertLevel.ERROR,
            channels=[AlertChannel.LOG],
            cooldown_minutes=10
        )
        
        # External service errors rule
        def external_service_error_condition(data: Dict[str, Any]) -> bool:
            ext_errors = data.get('errors_by_category', {}).get('external_service', 0)
            return ext_errors > 5  # More than 5 external service errors
        
        external_service_error_rule = AlertRule(
            name="external_service_errors",
            description="Multiple external service errors detected",
            condition=external_service_error_condition,
            level=AlertLevel.WARNING,
            channels=[AlertChannel.LOG],
            cooldown_minutes=15
        )
        
        # Add default rules
        self._alert_manager.add_rule(high_error_rate_rule)
        self._alert_manager.add_rule(critical_error_rule)
        self._alert_manager.add_rule(database_error_rule)
        self._alert_manager.add_rule(external_service_error_rule)
    
    def record_error(self, error_context: ErrorContext):
        """Record an error for monitoring."""
        if not self._monitoring_enabled:
            return
        
        with self._lock:
            try:
                self._metrics.add_error(error_context)
                
                # Check alert rules
                metrics_data = self.get_current_metrics()
                self._alert_manager.check_rules(metrics_data)
                
            except Exception as e:
                self.logger.error(f"Error recording error for monitoring: {e}")
                raise MonitoringError("error_recording", str(e))
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current error metrics."""
        with self._lock:
            return {
                'total_errors': self._metrics.total_errors,
                'errors_by_category': self._metrics.errors_by_category.copy(),
                'errors_by_severity': self._metrics.errors_by_severity.copy(),
                'errors_by_type': self._metrics.errors_by_type.copy(),
                'error_rate_per_minute': self._metrics.error_rate_per_minute,
                'recent_error_count': len(self._metrics.recent_errors),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_error_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get error trends over time."""
        with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Filter recent errors within time window
            time_window_errors = [
                error for error in self._metrics.recent_errors 
                if error.timestamp > cutoff_time
            ]
            
            # Group errors by hour
            hourly_counts = defaultdict(int)
            hourly_categories = defaultdict(lambda: defaultdict(int))
            
            for error in time_window_errors:
                hour_key = error.timestamp.replace(minute=0, second=0, microsecond=0)
                hourly_counts[hour_key] += 1
                hourly_categories[hour_key][error.category.value] += 1
            
            # Convert to lists for easier charting
            hours = sorted(hourly_counts.keys())
            error_counts = [hourly_counts[hour] for hour in hours]
            
            return {
                'time_period_hours': hours,
                'total_errors': len(time_window_errors),
                'hourly_error_counts': error_counts,
                'hourly_timestamps': [hour.isoformat() for hour in hours],
                'category_trends': dict(hourly_categories),
                'peak_error_hour': max(hourly_counts.items(), key=lambda x: x[1])[0].isoformat() if hourly_counts else None,
                'average_errors_per_hour': sum(error_counts) / len(error_counts) if error_counts else 0
            }
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a custom alert rule."""
        self._alert_manager.add_rule(rule)
    
    def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule."""
        self._alert_manager.remove_rule(rule_name)
    
    def register_alert_handler(self, channel: AlertChannel, handler: Callable[[Alert], None]):
        """Register a custom alert handler."""
        self._alert_manager.register_alert_handler(channel, handler)
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history."""
        alerts = self._alert_manager.get_alert_history(hours)
        return [
            {
                'alert_id': alert.alert_id,
                'rule_name': alert.rule_name,
                'level': alert.level.value,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'channels': [channel.value for channel in alert.channels],
                'data': alert.data
            }
            for alert in alerts
        ]
    
    def enable_monitoring(self):
        """Enable error monitoring."""
        self._monitoring_enabled = True
        self.logger.info("Error monitoring enabled")
    
    def disable_monitoring(self):
        """Disable error monitoring."""
        self._monitoring_enabled = False
        self.logger.info("Error monitoring disabled")
    
    def is_monitoring_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self._monitoring_enabled
    
    def reset_metrics(self):
        """Reset all metrics."""
        with self._lock:
            self._metrics = ErrorMetrics()
            self.logger.info("Error metrics reset")
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export current metrics in specified format."""
        metrics = self.get_current_metrics()
        
        if format.lower() == 'json':
            return json.dumps(metrics, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global error monitor instance
error_monitor = ErrorMonitor()