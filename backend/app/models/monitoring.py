"""
Models for monitoring and error tracking
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index, Boolean, Float
from backend.app.extensions import db


class ErrorLog(db.Model):
    """Model for storing error logs"""
    __tablename__ = 'error_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    traceback = Column(Text)
    severity = Column(String(20), nullable=False)  # critical, error, warning
    context = Column(JSON)
    request_id = Column(String(36))
    user_id = Column(Integer, db.ForeignKey('users.id'))
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_error_logs_timestamp', 'timestamp'),
        Index('idx_error_logs_error_type', 'error_type'),
        Index('idx_error_logs_severity', 'severity'),
        Index('idx_error_logs_user_id', 'user_id'),
        Index('idx_error_logs_request_id', 'request_id'),
    )
    
    def to_dict(self):
        """Convert error log to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'traceback': self.traceback,
            'severity': self.severity,
            'context': self.context,
            'request_id': self.request_id,
            'user_id': self.user_id
        }


class ErrorMetrics(db.Model):
    """Model for storing aggregated error metrics"""
    __tablename__ = 'error_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metric_type = Column(String(50), nullable=False)  # hourly, daily, weekly
    error_type = Column(String(100))
    severity = Column(String(20))
    count = Column(Integer, default=0)
    average_response_time = Column(Integer)  # milliseconds
    affected_users = Column(Integer, default=0)
    metadata = Column(JSON)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_error_metrics_timestamp', 'timestamp'),
        Index('idx_error_metrics_type', 'metric_type'),
        Index('idx_error_metrics_error_type', 'error_type'),
        Index('idx_error_metrics_severity', 'severity'),
    )
    
    def to_dict(self):
        """Convert error metrics to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metric_type': self.metric_type,
            'error_type': self.error_type,
            'severity': self.severity,
            'count': self.count,
            'average_response_time': self.average_response_time,
            'affected_users': self.affected_users,
            'metadata': self.metadata
        }


class AlarmRule(db.Model):
    """Model for alarm rules"""
    __tablename__ = 'alarm_rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    metric_type = Column(String(50), nullable=False)
    threshold_value = Column(Float, nullable=False)
    operator = Column(String(10), nullable=False)  # gt, lt, eq, gte, lte
    severity = Column(String(20), nullable=False)  # info, warning, error, critical
    duration = Column(Integer, default=0)  # seconds before triggering
    cooldown = Column(Integer, default=300)  # seconds before re-triggering
    notification_channels = Column(JSON, default=[])
    enabled = Column(Boolean, default=True)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_alarm_rules_name', 'name'),
        Index('idx_alarm_rules_metric_type', 'metric_type'),
        Index('idx_alarm_rules_enabled', 'enabled'),
    )
    
    def to_dict(self):
        """Convert alarm rule to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'metric_type': self.metric_type,
            'threshold_value': self.threshold_value,
            'operator': self.operator,
            'severity': self.severity,
            'duration': self.duration,
            'cooldown': self.cooldown,
            'notification_channels': self.notification_channels,
            'enabled': self.enabled,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AlarmHistory(db.Model):
    """Model for alarm history"""
    __tablename__ = 'alarm_history'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    rule_name = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)  # triggered, resolved, acknowledged, silenced
    severity = Column(String(20), nullable=False)
    data = Column(JSON)
    user_id = Column(Integer, db.ForeignKey('users.id'))
    
    # Indexes
    __table_args__ = (
        Index('idx_alarm_history_timestamp', 'timestamp'),
        Index('idx_alarm_history_rule_name', 'rule_name'),
        Index('idx_alarm_history_event_type', 'event_type'),
        Index('idx_alarm_history_severity', 'severity'),
    )
    
    def to_dict(self):
        """Convert alarm history to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'rule_name': self.rule_name,
            'event_type': self.event_type,
            'severity': self.severity,
            'data': self.data,
            'user_id': self.user_id
        }