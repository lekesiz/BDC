"""Virus scan log model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db


class VirusScanLog(db.Model):
    """Log of virus scan operations."""
    __tablename__ = 'virus_scan_logs'
    
    id = Column(Integer, primary_key=True)
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA256
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(100), nullable=True)
    
    # Scan results
    scan_result = Column(String(20), nullable=False)  # clean, infected, error, blocked
    is_infected = Column(Boolean, default=False)
    threats_found = Column(Text, nullable=True)  # JSON array of threats
    scan_details = Column(Text, nullable=True)  # JSON object with detailed results
    
    # Performance metrics
    scan_duration = Column(Float, nullable=True)  # seconds
    
    # Action taken
    action_taken = Column(String(50), nullable=True)  # quarantined, deleted, allowed
    quarantine_path = Column(String(500), nullable=True)
    
    # User information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='virus_scans')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'scan_result': self.scan_result,
            'is_infected': self.is_infected,
            'threats_found': self.threats_found,
            'scan_details': self.scan_details,
            'scan_duration': self.scan_duration,
            'action_taken': self.action_taken,
            'quarantine_path': self.quarantine_path,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_recent_infections(cls, limit=10):
        """Get recent infections."""
        return cls.query.filter_by(is_infected=True)\
            .order_by(cls.created_at.desc())\
            .limit(limit)\
            .all()
    
    @classmethod
    def get_user_scan_history(cls, user_id, limit=50):
        """Get scan history for a user."""
        return cls.query.filter_by(user_id=user_id)\
            .order_by(cls.created_at.desc())\
            .limit(limit)\
            .all()