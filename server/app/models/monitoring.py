"""
Models for monitoring and error tracking
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index, Boolean, Float
from app.extensions import db


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
    meta_data = Column(JSON)
    
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
            'metadata': self.meta_data
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
    meta_data = Column(JSON)
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
            'metadata': self.meta_data,
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


# AI Analysis ve Human Verification modelleri ekleyelim
class AIAnalysis(db.Model):
    """Model for AI analysis results"""
    __tablename__ = 'ai_analysis'
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(50), nullable=False)  # beneficiary, evaluation, etc.
    content_id = Column(Integer, nullable=False)
    analysis_type = Column(String(50), nullable=False)  # sentiment, skills, test, etc.
    raw_input = Column(Text)
    raw_output = Column(Text)
    final_output = Column(Text)  # After human verification
    confidence_score = Column(Float, default=0.0)
    meta_data = Column(JSON)
    human_verified = Column(Boolean, default=False)
    verification_status = Column(String(20))  # approved, rejected, modified
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_analysis_content', 'content_type', 'content_id'),
        Index('idx_ai_analysis_type', 'analysis_type'),
        Index('idx_ai_analysis_verified', 'human_verified'),
        Index('idx_ai_analysis_created', 'created_at'),
    )
    
    def to_dict(self):
        """Convert AI analysis to dictionary"""
        return {
            'id': self.id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'analysis_type': self.analysis_type,
            'raw_input': self.raw_input,
            'raw_output': self.raw_output,
            'final_output': self.final_output,
            'confidence_score': self.confidence_score,
            'metadata': self.meta_data,
            'human_verified': self.human_verified,
            'verification_status': self.verification_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class HumanVerification(db.Model):
    """Model for human verification of AI-generated content"""
    __tablename__ = 'human_verifications'
    
    id = Column(Integer, primary_key=True)
    content_type = Column(String(50), nullable=False)
    content_id = Column(Integer, nullable=False) 
    ai_output = Column(Text, nullable=False)
    modified_output = Column(Text)
    confidence_score = Column(Float, default=0.0)
    verification_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    priority = Column(String(20), default='normal')  # low, normal, high, urgent
    status = Column(String(20), default='pending')  # pending, approved, rejected, modified
    reviewer_id = Column(Integer, db.ForeignKey('users.id'))
    review_feedback = Column(Text)
    auto_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_verifications_content', 'content_type', 'content_id'),
        Index('idx_verifications_reviewer', 'reviewer_id'),
        Index('idx_verifications_status', 'status'),
        Index('idx_verifications_priority', 'priority'),
        Index('idx_verifications_created', 'created_at'),
    )
    
    def to_dict(self):
        """Convert verification to dictionary"""
        return {
            'id': self.id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'ai_output': self.ai_output,
            'modified_output': self.modified_output,
            'confidence_score': self.confidence_score,
            'verification_level': self.verification_level,
            'priority': self.priority,
            'status': self.status,
            'reviewer_id': self.reviewer_id,
            'review_feedback': self.review_feedback,
            'auto_approved': self.auto_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }


# Create an alias for backward compatibility
Monitoring = ErrorLog