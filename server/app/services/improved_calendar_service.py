"""Improved calendar service with dependency injection."""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging

from app.services.interfaces.calendar_service_interface import ICalendarService
from app.repositories.interfaces.calendar_repository_interface import ICalendarRepository
from app.extensions import db

logger = logging.getLogger(__name__)


class ImprovedCalendarService(ICalendarService):
    """Improved calendar service with dependency injection."""
    
    def __init__(self, calendar_repository: ICalendarRepository, db_session: Optional[Session] = None):
        """Initialize service with dependencies.
        
        Args:
            calendar_repository: Calendar repository implementation
            db_session: Database session (optional)
        """
        self.calendar_repository = calendar_repository
        self.db_session = db_session or db.session
    
    def create_appointment(self, title: str, start_time: datetime, end_time: datetime,
                          trainer_id: int, beneficiary_id: Optional[int] = None,
                          student_id: Optional[int] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new appointment."""
        try:
            # Check for conflicts before creating
            conflicts = self.calendar_repository.find_conflicts(
                start_time, end_time, trainer_id
            )
            if conflicts:
                logger.warning(f"Appointment conflicts detected for trainer {trainer_id}")
                return None
            
            appointment_data = {
                'title': title,
                'start_time': start_time,
                'end_time': end_time,
                'trainer_id': trainer_id,
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            if beneficiary_id:
                appointment_data['beneficiary_id'] = beneficiary_id
            if student_id:
                appointment_data['student_id'] = student_id
            
            # Add any additional kwargs
            appointment_data.update(kwargs)
            
            appointment = self.calendar_repository.create(**appointment_data)
            self.db_session.commit()
            
            logger.info(f"Created appointment {appointment.id}: {title}")
            return appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment)
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create appointment: {str(e)}")
            return None
    
    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """Get appointment by ID."""
        try:
            appointment = self.calendar_repository.find_by_id(appointment_id)
            if appointment:
                return appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment)
            return None
        except Exception as e:
            logger.error(f"Failed to get appointment {appointment_id}: {str(e)}")
            return None
    
    def get_appointments_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get appointments for a user."""
        try:
            appointments = self.calendar_repository.find_by_user_id(user_id)
            return [appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment) 
                   for appointment in appointments]
        except Exception as e:
            logger.error(f"Failed to get appointments for user {user_id}: {str(e)}")
            return []
    
    def get_appointments_by_beneficiary(self, beneficiary_id: int) -> List[Dict[str, Any]]:
        """Get appointments for a beneficiary."""
        try:
            appointments = self.calendar_repository.find_by_beneficiary_id(beneficiary_id)
            return [appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment) 
                   for appointment in appointments]
        except Exception as e:
            logger.error(f"Failed to get appointments for beneficiary {beneficiary_id}: {str(e)}")
            return []
    
    def get_appointments_by_date_range(self, start_date: datetime, end_date: datetime,
                                     user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get appointments in date range."""
        try:
            appointments = self.calendar_repository.find_by_date_range(start_date, end_date, user_id)
            return [appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment) 
                   for appointment in appointments]
        except Exception as e:
            logger.error(f"Failed to get appointments by date range: {str(e)}")
            return []
    
    def get_upcoming_appointments(self, user_id: Optional[int] = None,
                                limit: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming appointments."""
        try:
            appointments = self.calendar_repository.find_upcoming(user_id, limit)
            return [appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment) 
                   for appointment in appointments]
        except Exception as e:
            logger.error(f"Failed to get upcoming appointments: {str(e)}")
            return []
    
    def update_appointment(self, appointment_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update appointment."""
        try:
            appointment = self.calendar_repository.update(appointment_id, **kwargs)
            if appointment:
                self.db_session.commit()
                logger.info(f"Updated appointment {appointment_id}")
                return appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment)
            return None
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update appointment {appointment_id}: {str(e)}")
            return None
    
    def reschedule_appointment(self, appointment_id: int, new_start_time: datetime,
                             new_end_time: datetime) -> bool:
        """Reschedule appointment."""
        try:
            # Get the current appointment to check trainer
            appointment = self.calendar_repository.find_by_id(appointment_id)
            if not appointment:
                return False
            
            # Check for conflicts with new time
            conflicts = self.calendar_repository.find_conflicts(
                new_start_time, new_end_time, 
                getattr(appointment, 'trainer_id', 0), 
                appointment_id
            )
            if conflicts:
                logger.warning(f"Cannot reschedule appointment {appointment_id} - conflicts detected")
                return False
            
            success = self.calendar_repository.reschedule(
                appointment_id, new_start_time, new_end_time
            )
            if success:
                self.db_session.commit()
                logger.info(f"Rescheduled appointment {appointment_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to reschedule appointment {appointment_id}: {str(e)}")
            return False
    
    def cancel_appointment(self, appointment_id: int, reason: Optional[str] = None) -> bool:
        """Cancel appointment."""
        try:
            success = self.calendar_repository.cancel(appointment_id, reason)
            if success:
                self.db_session.commit()
                logger.info(f"Cancelled appointment {appointment_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to cancel appointment {appointment_id}: {str(e)}")
            return False
    
    def confirm_appointment(self, appointment_id: int) -> bool:
        """Confirm appointment."""
        try:
            success = self.calendar_repository.update_status(appointment_id, 'confirmed')
            if success:
                self.db_session.commit()
                logger.info(f"Confirmed appointment {appointment_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to confirm appointment {appointment_id}: {str(e)}")
            return False
    
    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete appointment."""
        try:
            success = self.calendar_repository.delete(appointment_id)
            if success:
                self.db_session.commit()
                logger.info(f"Deleted appointment {appointment_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete appointment {appointment_id}: {str(e)}")
            return False
    
    def check_availability(self, user_id: int, start_time: datetime, 
                         end_time: datetime, exclude_appointment_id: Optional[int] = None) -> bool:
        """Check if user is available for time slot."""
        try:
            conflicts = self.calendar_repository.find_conflicts(
                start_time, end_time, user_id, exclude_appointment_id
            )
            return len(conflicts) == 0
        except Exception as e:
            logger.error(f"Failed to check availability for user {user_id}: {str(e)}")
            return False
    
    def get_conflicts(self, user_id: int, start_time: datetime, end_time: datetime,
                     exclude_appointment_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conflicting appointments."""
        try:
            conflicts = self.calendar_repository.find_conflicts(
                start_time, end_time, user_id, exclude_appointment_id
            )
            return [appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment) 
                   for appointment in conflicts]
        except Exception as e:
            logger.error(f"Failed to get conflicts for user {user_id}: {str(e)}")
            return []
    
    def get_user_schedule(self, user_id: int, date: datetime) -> List[Dict[str, Any]]:
        """Get user's schedule for a specific date."""
        try:
            # Get appointments for the entire day
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            appointments = self.calendar_repository.find_by_date_range(
                start_of_day, end_of_day, user_id
            )
            return [appointment.to_dict() if hasattr(appointment, 'to_dict') else self._serialize_appointment(appointment) 
                   for appointment in appointments]
        except Exception as e:
            logger.error(f"Failed to get schedule for user {user_id} on {date}: {str(e)}")
            return []
    
    def _serialize_appointment(self, appointment) -> Dict[str, Any]:
        """Serialize appointment for API response."""
        return {
            'id': appointment.id,
            'title': getattr(appointment, 'title', ''),
            'description': getattr(appointment, 'description', ''),
            'start_time': getattr(appointment, 'start_time', datetime.now()).isoformat(),
            'end_time': getattr(appointment, 'end_time', datetime.now()).isoformat(),
            'trainer_id': getattr(appointment, 'trainer_id', None),
            'student_id': getattr(appointment, 'student_id', None),
            'beneficiary_id': getattr(appointment, 'beneficiary_id', None),
            'status': getattr(appointment, 'status', 'scheduled'),
            'location': getattr(appointment, 'location', ''),
            'notes': getattr(appointment, 'notes', ''),
            'created_at': getattr(appointment, 'created_at', datetime.now()).isoformat(),
            'updated_at': getattr(appointment, 'updated_at', datetime.now()).isoformat()
        }