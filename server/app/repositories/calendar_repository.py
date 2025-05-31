"""Calendar/Appointment repository implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.calendar_repository_interface import ICalendarRepository
from app.models import Appointment
from app.extensions import db


class CalendarRepository(BaseRepository[Appointment], ICalendarRepository):
    """Calendar/Appointment repository implementation."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize calendar repository."""
        super().__init__(Appointment, db_session)
    
    def find_by_user_id(self, user_id: int) -> List[Appointment]:
        """Find appointments by user ID."""
        return self.db_session.query(Appointment).filter(
            or_(
                Appointment.trainer_id == user_id,
                Appointment.student_id == user_id
            )
        ).order_by(Appointment.start_time.asc()).all()
    
    def find_by_beneficiary_id(self, beneficiary_id: int) -> List[Appointment]:
        """Find appointments by beneficiary ID."""
        return self.db_session.query(Appointment).filter_by(
            beneficiary_id=beneficiary_id
        ).order_by(Appointment.start_time.asc()).all()
    
    def find_by_date_range(self, start_date: datetime, end_date: datetime, 
                          user_id: Optional[int] = None) -> List[Appointment]:
        """Find appointments by date range."""
        query = self.db_session.query(Appointment).filter(
            and_(
                Appointment.start_time >= start_date,
                Appointment.start_time <= end_date
            )
        )
        
        if user_id:
            query = query.filter(
                or_(
                    Appointment.trainer_id == user_id,
                    Appointment.student_id == user_id
                )
            )
        
        return query.order_by(Appointment.start_time.asc()).all()
    
    def find_by_status(self, status: str) -> List[Appointment]:
        """Find appointments by status."""
        return self.db_session.query(Appointment).filter_by(
            status=status
        ).order_by(Appointment.start_time.asc()).all()
    
    def find_upcoming(self, user_id: Optional[int] = None, limit: int = 10) -> List[Appointment]:
        """Find upcoming appointments."""
        now = datetime.utcnow()
        query = self.db_session.query(Appointment).filter(
            and_(
                Appointment.start_time > now,
                Appointment.status.in_(['scheduled', 'confirmed'])
            )
        )
        
        if user_id:
            query = query.filter(
                or_(
                    Appointment.trainer_id == user_id,
                    Appointment.student_id == user_id
                )
            )
        
        return query.order_by(Appointment.start_time.asc()).limit(limit).all()
    
    def find_conflicts(self, start_time: datetime, end_time: datetime, 
                      user_id: int, exclude_id: Optional[int] = None) -> List[Appointment]:
        """Find conflicting appointments."""
        query = self.db_session.query(Appointment).filter(
            and_(
                or_(
                    Appointment.trainer_id == user_id,
                    Appointment.student_id == user_id
                ),
                Appointment.status.in_(['scheduled', 'confirmed']),
                or_(
                    and_(
                        Appointment.start_time <= start_time,
                        Appointment.end_time > start_time
                    ),
                    and_(
                        Appointment.start_time < end_time,
                        Appointment.end_time >= end_time
                    ),
                    and_(
                        Appointment.start_time >= start_time,
                        Appointment.end_time <= end_time
                    )
                )
            )
        )
        
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)
        
        return query.all()
    
    def update_status(self, appointment_id: int, status: str) -> bool:
        """Update appointment status."""
        try:
            appointment = self.find_by_id(appointment_id)
            if not appointment:
                return False
            
            appointment.status = status
            if hasattr(appointment, 'updated_at'):
                appointment.updated_at = datetime.utcnow()
            
            self.db_session.flush()
            return True
        except Exception:
            return False
    
    def reschedule(self, appointment_id: int, new_start_time: datetime, 
                  new_end_time: datetime) -> bool:
        """Reschedule appointment."""
        try:
            appointment = self.find_by_id(appointment_id)
            if not appointment:
                return False
            
            appointment.start_time = new_start_time
            appointment.end_time = new_end_time
            if hasattr(appointment, 'updated_at'):
                appointment.updated_at = datetime.utcnow()
            
            self.db_session.flush()
            return True
        except Exception:
            return False
    
    def cancel(self, appointment_id: int, reason: Optional[str] = None) -> bool:
        """Cancel appointment."""
        try:
            appointment = self.find_by_id(appointment_id)
            if not appointment:
                return False
            
            appointment.status = 'cancelled'
            if reason and hasattr(appointment, 'cancellation_reason'):
                appointment.cancellation_reason = reason
            if hasattr(appointment, 'updated_at'):
                appointment.updated_at = datetime.utcnow()
            
            self.db_session.flush()
            return True
        except Exception:
            return False
    
    def create(self, **kwargs) -> Appointment:
        """Create a new appointment."""
        appointment = Appointment(**kwargs)
        self.db_session.add(appointment)
        self.db_session.flush()
        return appointment
    
    def update(self, appointment_id: int, **kwargs) -> Optional[Appointment]:
        """Update appointment by ID."""
        appointment = self.find_by_id(appointment_id)
        if not appointment:
            return None
        
        for key, value in kwargs.items():
            if hasattr(appointment, key):
                setattr(appointment, key, value)
        
        if hasattr(appointment, 'updated_at'):
            appointment.updated_at = datetime.utcnow()
        
        self.db_session.flush()
        return appointment
    
    def delete(self, appointment_id: int) -> bool:
        """Delete appointment by ID."""
        appointment = self.find_by_id(appointment_id)
        if not appointment:
            return False
        
        self.db_session.delete(appointment)
        self.db_session.flush()
        return True
    
    def save(self, appointment: Appointment) -> Appointment:
        """Save appointment instance."""
        self.db_session.add(appointment)
        self.db_session.flush()
        return appointment
    
    def find_all(self, limit: int = None, offset: int = None) -> List[Appointment]:
        """Find all appointments with optional pagination."""
        query = self.db_session.query(Appointment).order_by(Appointment.start_time.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def count(self) -> int:
        """Count total appointments."""
        return self.db_session.query(Appointment).count()