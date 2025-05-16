"""Appointment model module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.extensions import db

class Appointment(db.Model):
    """Appointment model."""
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=False)
    trainer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default='scheduled')  # 'scheduled', 'completed', 'cancelled'
    calendar_event_id = Column(String(255), nullable=True)  # Google Calendar event ID
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiary = relationship('Beneficiary', back_populates='appointments')
    trainer = relationship('User', backref='trainer_appointments')
    
    def to_dict(self):
        """Return a dict representation of the appointment."""
        return {
            'id': self.id,
            'beneficiary_id': self.beneficiary_id,
            'trainer_id': self.trainer_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'location': self.location,
            'status': self.status,
            'notes': self.notes,
            'calendar_event_id': self.calendar_event_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'beneficiary': {
                'id': self.beneficiary.id,
                'first_name': self.beneficiary.user.first_name,
                'last_name': self.beneficiary.user.last_name,
                'email': self.beneficiary.user.email
            } if self.beneficiary else None,
            'trainer': {
                'id': self.trainer.id,
                'first_name': self.trainer.first_name,
                'last_name': self.trainer.last_name,
                'email': self.trainer.email
            } if self.trainer else None
        }
    
    def __repr__(self):
        """String representation of the appointment."""
        return f'<Appointment {self.id} {self.title}>'