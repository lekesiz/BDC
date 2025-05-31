"""Report model."""

from datetime import datetime
from app.extensions import db

class Report(db.Model):
    """Model for system reports."""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50), nullable=False)  # beneficiary, trainer, program, performance
    format = db.Column(db.String(20), default='pdf')  # pdf, xlsx, csv
    status = db.Column(db.String(20), default='draft')  # draft, generating, completed, failed
    
    # Report parameters (JSON)
    parameters = db.Column(db.JSON, default={})
    
    # File information
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    
    # Metadata
    run_count = db.Column(db.Integer, default=0)
    last_generated = db.Column(db.DateTime)
    
    # Relationships
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
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
            'type': self.type,
            'format': self.format,
            'status': self.status,
            'parameters': self.parameters,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'run_count': self.run_count,
            'last_generated': self.last_generated.isoformat() if self.last_generated else None,
            'created_by': {
                'id': self.created_by.id,
                'name': f"{self.created_by.first_name} {self.created_by.last_name}"
            } if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ReportSchedule(db.Model):
    """Model for scheduled reports."""
    __tablename__ = 'report_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    
    # Schedule information
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    schedule_time = db.Column(db.Time)
    day_of_week = db.Column(db.Integer)  # 0-6 for weekly
    day_of_month = db.Column(db.Integer)  # 1-31 for monthly
    
    # Recipients
    recipients = db.Column(db.JSON, default=[])  # List of email addresses
    recipients_count = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, paused, error
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    report = db.relationship('Report', back_populates='schedules')
    
    def to_dict(self):
        """Convert schedule to dictionary."""
        return {
            'id': self.id,
            'report': {
                'id': self.report.id,
                'name': self.report.name,
                'type': self.report.type
            } if self.report else None,
            'frequency': self.frequency,
            'schedule_time': self.schedule_time.isoformat() if self.schedule_time else None,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
            'recipients': self.recipients,
            'recipients_count': self.recipients_count,
            'is_active': self.is_active,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }