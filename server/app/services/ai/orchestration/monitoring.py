"""Pipeline monitoring and logging system."""

import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import time
from collections import defaultdict
import statistics


logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics to track."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class PipelineMetrics:
    """Container for pipeline execution metrics."""
    
    def __init__(self):
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time = 0.0
        self.average_execution_time = 0.0
        self.min_execution_time = float('inf')
        self.max_execution_time = 0.0
        self.throughput = 0.0  # executions per hour
        self.error_rate = 0.0
        self.execution_times: List[float] = []
        self.last_execution = None
        self.last_success = None
        self.last_failure = None
    
    def update_execution(self, execution_time: float, success: bool):
        """Update metrics with new execution data."""
        self.execution_count += 1
        self.total_execution_time += execution_time
        self.execution_times.append(execution_time)
        
        # Keep only last 100 execution times for memory efficiency
        if len(self.execution_times) > 100:
            self.execution_times.pop(0)
        
        if success:
            self.success_count += 1
            self.last_success = datetime.utcnow()
        else:
            self.failure_count += 1
            self.last_failure = datetime.utcnow()
        
        self.last_execution = datetime.utcnow()
        
        # Recalculate derived metrics
        self.average_execution_time = self.total_execution_time / self.execution_count
        self.min_execution_time = min(self.min_execution_time, execution_time)
        self.max_execution_time = max(self.max_execution_time, execution_time)
        self.error_rate = self.failure_count / self.execution_count
        
        # Calculate throughput (executions per hour)
        if self.execution_count > 1 and self.execution_times:
            time_span_hours = (len(self.execution_times) * self.average_execution_time) / 3600
            self.throughput = len(self.execution_times) / time_span_hours if time_span_hours > 0 else 0
    
    def get_percentiles(self) -> Dict[str, float]:
        """Calculate execution time percentiles."""
        if not self.execution_times:
            return {}
        
        sorted_times = sorted(self.execution_times)
        return {
            "p50": statistics.median(sorted_times),
            "p90": sorted_times[int(0.9 * len(sorted_times))] if len(sorted_times) > 1 else sorted_times[0],
            "p95": sorted_times[int(0.95 * len(sorted_times))] if len(sorted_times) > 1 else sorted_times[0],
            "p99": sorted_times[int(0.99 * len(sorted_times))] if len(sorted_times) > 1 else sorted_times[0]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        percentiles = self.get_percentiles()
        return {
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": (self.success_count / self.execution_count) if self.execution_count > 0 else 0,
            "error_rate": self.error_rate,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": self.average_execution_time,
            "min_execution_time": self.min_execution_time if self.min_execution_time != float('inf') else 0,
            "max_execution_time": self.max_execution_time,
            "throughput": self.throughput,
            "percentiles": percentiles,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None
        }


class Alert:
    """Represents a monitoring alert."""
    
    def __init__(self,
                 id: str,
                 pipeline_id: str,
                 severity: AlertSeverity,
                 message: str,
                 metric_name: str,
                 threshold: float,
                 current_value: float,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.pipeline_id = pipeline_id
        self.severity = severity
        self.message = message
        self.metric_name = metric_name
        self.threshold = threshold
        self.current_value = current_value
        self.created_at = created_at or datetime.utcnow()
        self.acknowledged = False
        self.acknowledged_by = None
        self.acknowledged_at = None
    
    def acknowledge(self, user: str):
        """Acknowledge the alert."""
        self.acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "severity": self.severity.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "created_at": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }


class AlertRule:
    """Defines conditions for triggering alerts."""
    
    def __init__(self,
                 name: str,
                 metric_name: str,
                 operator: str,  # >, <, >=, <=, ==
                 threshold: float,
                 severity: AlertSeverity,
                 message_template: str,
                 cooldown_minutes: int = 30):
        self.name = name
        self.metric_name = metric_name
        self.operator = operator
        self.threshold = threshold
        self.severity = severity
        self.message_template = message_template
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None
    
    def should_trigger(self, current_value: float) -> bool:
        """Check if the rule should trigger an alert."""
        # Check cooldown period
        if self.last_triggered:
            cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
            if datetime.utcnow() < cooldown_end:
                return False
        
        # Check threshold condition
        if self.operator == ">":
            return current_value > self.threshold
        elif self.operator == "<":
            return current_value < self.threshold
        elif self.operator == ">=":
            return current_value >= self.threshold
        elif self.operator == "<=":
            return current_value <= self.threshold
        elif self.operator == "==":
            return current_value == self.threshold
        
        return False
    
    def create_alert(self, pipeline_id: str, current_value: float) -> Alert:
        """Create an alert for this rule."""
        import uuid
        
        message = self.message_template.format(
            metric=self.metric_name,
            threshold=self.threshold,
            current_value=current_value,
            pipeline=pipeline_id
        )
        
        alert = Alert(
            id=str(uuid.uuid4()),
            pipeline_id=pipeline_id,
            severity=self.severity,
            message=message,
            metric_name=self.metric_name,
            threshold=self.threshold,
            current_value=current_value
        )
        
        self.last_triggered = datetime.utcnow()
        return alert


class PipelineMonitor:
    """Comprehensive pipeline monitoring system."""
    
    def __init__(self, redis_client):
        """Initialize the monitoring system."""
        self.redis_client = redis_client
        self.metrics_key = "monitor:metrics:"
        self.executions_key = "monitor:executions:"
        self.alerts_key = "monitor:alerts:"
        self.events_key = "monitor:events:"
        
        # In-memory storage for active monitoring
        self.pipeline_metrics: Dict[str, PipelineMetrics] = {}
        self.alert_rules: Dict[str, List[AlertRule]] = defaultdict(list)
        self.active_alerts: Dict[str, Alert] = {}
        self.event_handlers: List[Callable] = []
        
        # Background monitoring
        self.monitoring_active = True
        self._start_monitoring()
        
        # Setup default alert rules
        self._setup_default_alerts()
    
    def _start_monitoring(self):
        """Start background monitoring tasks."""
        asyncio.create_task(self._periodic_metric_collection())
        asyncio.create_task(self._periodic_alert_checking())
        asyncio.create_task(self._periodic_cleanup())
    
    def _setup_default_alerts(self):
        """Setup default alert rules for common issues."""
        default_rules = [
            AlertRule(
                name="High Error Rate",
                metric_name="error_rate",
                operator=">",
                threshold=0.1,  # 10%
                severity=AlertSeverity.WARNING,
                message_template="Pipeline {pipeline} has high error rate: {current_value:.2%} (threshold: {threshold:.2%})"
            ),
            AlertRule(
                name="Critical Error Rate",
                metric_name="error_rate",
                operator=">",
                threshold=0.25,  # 25%
                severity=AlertSeverity.CRITICAL,
                message_template="Pipeline {pipeline} has critical error rate: {current_value:.2%} (threshold: {threshold:.2%})"
            ),
            AlertRule(
                name="Long Execution Time",
                metric_name="average_execution_time",
                operator=">",
                threshold=3600,  # 1 hour
                severity=AlertSeverity.WARNING,
                message_template="Pipeline {pipeline} has long average execution time: {current_value:.1f}s (threshold: {threshold}s)"
            ),
            AlertRule(
                name="Low Throughput",
                metric_name="throughput",
                operator="<",
                threshold=1.0,  # 1 execution per hour
                severity=AlertSeverity.INFO,
                message_template="Pipeline {pipeline} has low throughput: {current_value:.2f} exec/hour (threshold: {threshold})"
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule("*", rule)  # Apply to all pipelines
    
    async def _periodic_metric_collection(self):
        """Periodically collect and store metrics."""
        while self.monitoring_active:
            try:
                await asyncio.sleep(60)  # Every minute
                self._store_metrics()
            except Exception as e:
                logger.error(f"Error in metric collection: {str(e)}")
    
    async def _periodic_alert_checking(self):
        """Periodically check alert conditions."""
        while self.monitoring_active:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                self._check_alerts()
            except Exception as e:
                logger.error(f"Error in alert checking: {str(e)}")
    
    async def _periodic_cleanup(self):
        """Periodically clean up old data."""
        while self.monitoring_active:
            try:
                await asyncio.sleep(3600)  # Every hour
                self._cleanup_old_data()
            except Exception as e:
                logger.error(f"Error in cleanup: {str(e)}")
    
    def register_pipeline(self, pipeline_id: str, config: Dict[str, Any]):
        """Register a pipeline for monitoring."""
        if pipeline_id not in self.pipeline_metrics:
            self.pipeline_metrics[pipeline_id] = PipelineMetrics()
        
        # Store pipeline configuration
        self.redis_client.hset(
            f"monitor:pipelines",
            pipeline_id,
            json.dumps({
                "config": config,
                "registered_at": datetime.utcnow().isoformat()
            })
        )
        
        logger.info(f"Registered pipeline for monitoring: {pipeline_id}")
    
    def start_execution(self, execution_id: str, pipeline_id: str):
        """Record the start of a pipeline execution."""
        execution_data = {
            "execution_id": execution_id,
            "pipeline_id": pipeline_id,
            "started_at": datetime.utcnow().isoformat(),
            "status": "running"
        }
        
        # Store execution start
        self.redis_client.hset(
            self.executions_key + execution_id,
            mapping=execution_data
        )
        
        # Set TTL for execution data (7 days)
        self.redis_client.expire(self.executions_key + execution_id, 604800)
        
        # Log event
        self._log_event(pipeline_id, "execution_started", {
            "execution_id": execution_id
        })
    
    def complete_execution(self, execution_id: str, status: str):
        """Record the completion of a pipeline execution."""
        # Get execution data
        execution_data = self.redis_client.hgetall(self.executions_key + execution_id)
        if not execution_data:
            logger.warning(f"Execution data not found: {execution_id}")
            return
        
        # Calculate execution time
        started_at = datetime.fromisoformat(execution_data[b"started_at"].decode())
        completed_at = datetime.utcnow()
        execution_time = (completed_at - started_at).total_seconds()
        
        # Update execution data
        execution_data.update({
            "completed_at": completed_at.isoformat(),
            "status": status,
            "execution_time": execution_time
        })
        
        # Store updated data
        self.redis_client.hset(
            self.executions_key + execution_id,
            mapping={k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v 
                    for k, v in execution_data.items()}
        )
        
        # Update pipeline metrics
        pipeline_id = execution_data[b"pipeline_id"].decode()
        if pipeline_id in self.pipeline_metrics:
            success = status in ["completed", "success"]
            self.pipeline_metrics[pipeline_id].update_execution(execution_time, success)
        
        # Log event
        self._log_event(pipeline_id, "execution_completed", {
            "execution_id": execution_id,
            "status": status,
            "execution_time": execution_time
        })
    
    def update_execution_status(self, execution_id: str, status: str):
        """Update the status of a running execution."""
        self.redis_client.hset(
            self.executions_key + execution_id,
            "status",
            status
        )
    
    def add_alert_rule(self, pipeline_id: str, rule: AlertRule):
        """Add an alert rule for a pipeline."""
        self.alert_rules[pipeline_id].append(rule)
        logger.info(f"Added alert rule '{rule.name}' for pipeline: {pipeline_id}")
    
    def remove_alert_rule(self, pipeline_id: str, rule_name: str) -> bool:
        """Remove an alert rule."""
        if pipeline_id in self.alert_rules:
            self.alert_rules[pipeline_id] = [
                rule for rule in self.alert_rules[pipeline_id]
                if rule.name != rule_name
            ]
            return True
        return False
    
    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledge(user)
            
            # Update in Redis
            self.redis_client.hset(
                self.alerts_key + alert_id,
                mapping=self.active_alerts[alert_id].to_dict()
            )
            
            logger.info(f"Alert {alert_id} acknowledged by {user}")
            return True
        return False
    
    def get_pipeline_metrics(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get current metrics for a pipeline."""
        if pipeline_id in self.pipeline_metrics:
            return self.pipeline_metrics[pipeline_id].to_dict()
        return None
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all pipelines."""
        return {
            pipeline_id: metrics.to_dict()
            for pipeline_id, metrics in self.pipeline_metrics.items()
        }
    
    def get_active_alerts(self, pipeline_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active alerts, optionally filtered by pipeline."""
        alerts = []
        for alert in self.active_alerts.values():
            if pipeline_id is None or alert.pipeline_id == pipeline_id:
                if not alert.acknowledged:
                    alerts.append(alert.to_dict())
        
        return sorted(alerts, key=lambda a: a["created_at"], reverse=True)
    
    def get_execution_history(self, 
                            pipeline_id: Optional[str] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history."""
        executions = []
        
        # Scan for execution keys
        pattern = self.executions_key + "*"
        for key in self.redis_client.scan_iter(match=pattern):
            execution_data = self.redis_client.hgetall(key)
            if not execution_data:
                continue
            
            # Convert bytes to strings
            execution = {
                k.decode() if isinstance(k, bytes) else k: 
                v.decode() if isinstance(v, bytes) else v
                for k, v in execution_data.items()
            }
            
            # Filter by pipeline if specified
            if pipeline_id and execution.get("pipeline_id") != pipeline_id:
                continue
            
            executions.append(execution)
        
        # Sort by start time (newest first) and limit
        executions.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        return executions[:limit]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        total_pipelines = len(self.pipeline_metrics)
        total_executions = sum(m.execution_count for m in self.pipeline_metrics.values())
        total_failures = sum(m.failure_count for m in self.pipeline_metrics.values())
        
        health_data = {
            "total_pipelines": total_pipelines,
            "active_pipelines": len([p for p in self.pipeline_metrics.values() if p.last_execution]),
            "total_executions": total_executions,
            "total_failures": total_failures,
            "overall_success_rate": (total_executions - total_failures) / total_executions if total_executions > 0 else 0,
            "active_alerts": len([a for a in self.active_alerts.values() if not a.acknowledged]),
            "system_uptime": (datetime.utcnow() - datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds(),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Add top performing and problematic pipelines
        if self.pipeline_metrics:
            pipeline_performance = [
                (pid, metrics.error_rate, metrics.average_execution_time)
                for pid, metrics in self.pipeline_metrics.items()
                if metrics.execution_count > 0
            ]
            
            if pipeline_performance:
                # Best performing (lowest error rate)
                best_pipeline = min(pipeline_performance, key=lambda x: x[1])
                health_data["best_performing_pipeline"] = {
                    "id": best_pipeline[0],
                    "error_rate": best_pipeline[1],
                    "avg_execution_time": best_pipeline[2]
                }
                
                # Most problematic (highest error rate)
                worst_pipeline = max(pipeline_performance, key=lambda x: x[1])
                if worst_pipeline[1] > 0:
                    health_data["most_problematic_pipeline"] = {
                        "id": worst_pipeline[0],
                        "error_rate": worst_pipeline[1],
                        "avg_execution_time": worst_pipeline[2]
                    }
        
        return health_data
    
    def _store_metrics(self):
        """Store current metrics to Redis."""
        for pipeline_id, metrics in self.pipeline_metrics.items():
            metrics_data = metrics.to_dict()
            metrics_data["timestamp"] = datetime.utcnow().isoformat()
            
            # Store with timestamp
            timestamp_key = f"{self.metrics_key}{pipeline_id}:{int(time.time())}"
            self.redis_client.setex(
                timestamp_key,
                86400,  # 24 hours TTL
                json.dumps(metrics_data)
            )
    
    def _check_alerts(self):
        """Check all alert rules and trigger alerts if needed."""
        for pipeline_id, metrics in self.pipeline_metrics.items():
            if metrics.execution_count == 0:
                continue
            
            metrics_dict = metrics.to_dict()
            
            # Check rules for this specific pipeline and global rules
            rules_to_check = self.alert_rules.get(pipeline_id, []) + self.alert_rules.get("*", [])
            
            for rule in rules_to_check:
                if rule.metric_name not in metrics_dict:
                    continue
                
                current_value = metrics_dict[rule.metric_name]
                
                if rule.should_trigger(current_value):
                    alert = rule.create_alert(pipeline_id, current_value)
                    self._trigger_alert(alert)
    
    def _trigger_alert(self, alert: Alert):
        """Trigger an alert."""
        # Check if we already have an active alert for this condition
        existing_alert_key = f"{alert.pipeline_id}:{alert.metric_name}"
        if existing_alert_key in [f"{a.pipeline_id}:{a.metric_name}" for a in self.active_alerts.values() if not a.acknowledged]:
            return  # Don't spam with duplicate alerts
        
        # Store alert
        self.active_alerts[alert.id] = alert
        
        # Persist to Redis
        self.redis_client.hset(
            self.alerts_key + alert.id,
            mapping=alert.to_dict()
        )
        
        # Set TTL for alerts (30 days)
        self.redis_client.expire(self.alerts_key + alert.id, 2592000)
        
        # Log event
        self._log_event(alert.pipeline_id, "alert_triggered", {
            "alert_id": alert.id,
            "severity": alert.severity.value,
            "message": alert.message
        })
        
        # Notify event handlers
        for handler in self.event_handlers:
            try:
                handler("alert_triggered", alert.to_dict())
            except Exception as e:
                logger.error(f"Error in alert handler: {str(e)}")
        
        logger.warning(f"Alert triggered: {alert.message}")
    
    def _log_event(self, pipeline_id: str, event_type: str, data: Dict[str, Any]):
        """Log a monitoring event."""
        event = {
            "pipeline_id": pipeline_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        # Store event
        event_key = f"{self.events_key}{pipeline_id}:{int(time.time())}"
        self.redis_client.setex(
            event_key,
            604800,  # 7 days TTL
            json.dumps(event)
        )
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data."""
        try:
            # Clean up old metrics (keep last 7 days)
            cutoff_time = int((datetime.utcnow() - timedelta(days=7)).timestamp())
            
            patterns = [
                self.metrics_key + "*",
                self.events_key + "*",
                self.executions_key + "*"
            ]
            
            for pattern in patterns:
                for key in self.redis_client.scan_iter(match=pattern):
                    # Extract timestamp from key
                    try:
                        timestamp_str = key.decode().split(":")[-1]
                        timestamp = int(timestamp_str)
                        if timestamp < cutoff_time:
                            self.redis_client.delete(key)
                    except (ValueError, IndexError):
                        # Skip keys that don't have timestamp format
                        continue
            
            # Clean up acknowledged alerts older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            alerts_to_remove = []
            
            for alert_id, alert in self.active_alerts.items():
                if alert.acknowledged and alert.acknowledged_at and alert.acknowledged_at < cutoff_date:
                    alerts_to_remove.append(alert_id)
            
            for alert_id in alerts_to_remove:
                del self.active_alerts[alert_id]
                self.redis_client.delete(self.alerts_key + alert_id)
            
            logger.info("Completed monitoring data cleanup")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def add_event_handler(self, handler: Callable):
        """Add an event handler for monitoring events."""
        self.event_handlers.append(handler)
    
    def stop_monitoring(self):
        """Stop background monitoring tasks."""
        self.monitoring_active = False