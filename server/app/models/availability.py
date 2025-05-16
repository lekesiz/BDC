"""Availability model module."""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.extensions import db

class AvailabilitySchedule(db.Model):
    """Availability schedule model for trainers."""
    __tablename__ = 'availability_schedules'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False, default='Default Schedule')
    is_active = Column(Boolean, default=True)
    time_zone = Column(String(50), nullable=False, default='UTC')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='availability_schedules')
    slots = relationship('AvailabilitySlot', backref='schedule', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Return a dict representation of the availability schedule."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'is_active': self.is_active,
            'time_zone': self.time_zone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the availability schedule."""
        return f'<AvailabilitySchedule {self.id}: {self.title}>'


class AvailabilitySlot(db.Model):
    """Availability slot model for specific time slots."""
    __tablename__ = 'availability_slots'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('availability_schedules.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    start_time = Column(String(5), nullable=False)  # Format: HH:MM (24-hour format)
    end_time = Column(String(5), nullable=False)  # Format: HH:MM (24-hour format)
    is_available = Column(Boolean, default=True)
    
    def to_dict(self):
        """Return a dict representation of the availability slot."""
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'is_available': self.is_available
        }
    
    def __repr__(self):
        """String representation of the availability slot."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = days[self.day_of_week]
        return f'<AvailabilitySlot {self.id}: {day_name} {self.start_time}-{self.end_time}>'


class AvailabilityException(db.Model):
    """Availability exception model for overriding regular schedules."""
    __tablename__ = 'availability_exceptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=False)  # True for adding availability, False for blocking
    title = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    start_time = Column(String(5), nullable=True)  # If null, entire day is affected
    end_time = Column(String(5), nullable=True)  # If null, entire day is affected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='availability_exceptions')
    
    def to_dict(self):
        """Return a dict representation of the availability exception."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'is_available': self.is_available,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the availability exception."""
        date_str = self.date.strftime('%Y-%m-%d')
        if self.start_time and self.end_time:
            return f'<AvailabilityException {self.id}: {date_str} {self.start_time}-{self.end_time}>'
        return f'<AvailabilityException {self.id}: {date_str} All Day>'