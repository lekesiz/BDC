"""Report model for system reports."""

from datetime import datetime
from app.extensions import db


class Report(db.Model):
    """Model for system reports."""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    report_type = db.Column(db.String(50))  # user_activity, beneficiary_progress, etc.
    
    # Report configuration
    config = db.Column(db.JSON, default={})
    filters = db.Column(db.JSON, default={})
    
    # Ownership
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_run_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', back_populates='reports')
    tenant = db.relationship('Tenant', back_populates='reports')
    schedules = db.relationship('ReportSchedule', back_populates='report', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert report to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'report_type': self.report_type,
            'config': self.config,
            'filters': self.filters,
            'is_active': self.is_active,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ReportSchedule(db.Model):
    """Model for scheduled reports."""
    __tablename__ = 'report_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    
    # Schedule configuration
    frequency = db.Column(db.String(20))  # daily, weekly, monthly
    schedule_config = db.Column(db.JSON, default={})  # cron expression or specific times
    
    # Recipients
    recipients = db.Column(db.JSON, default=[])  # List of email addresses
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_sent_at = db.Column(db.DateTime)
    next_run_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    report = db.relationship('Report', back_populates='schedules')
    
    def to_dict(self):
        """Convert schedule to dictionary."""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'frequency': self.frequency,
            'schedule_config': self.schedule_config,
            'recipients': self.recipients,
            'is_active': self.is_active,
            'last_sent_at': self.last_sent_at.isoformat() if self.last_sent_at else None,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }