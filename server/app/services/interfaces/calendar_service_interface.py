"""Calendar service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime


class ICalendarService(ABC):
    """Interface for calendar service operations."""
    
    @abstractmethod
    def create_appointment(self, title: str, start_time: datetime, end_time: datetime,
                          trainer_id: int, beneficiary_id: Optional[int] = None,
                          student_id: Optional[int] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new appointment.
        
        Args:
            title: Appointment title
            start_time: Start time
            end_time: End time
            trainer_id: Trainer ID
            beneficiary_id: Beneficiary ID
            student_id: Student ID
            **kwargs: Additional appointment data
            
        Returns:
            Created appointment data or None if failed
        """
        pass
    
    @abstractmethod
    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """Get appointment by ID.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Appointment data or None if not found
        """
        pass
    
    @abstractmethod
    def get_appointments_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get appointments for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of appointment data
        """
        pass
    
    @abstractmethod
    def get_appointments_by_beneficiary(self, beneficiary_id: int) -> List[Dict[str, Any]]:
        """Get appointments for a beneficiary.
        
        Args:
            beneficiary_id: Beneficiary ID
            
        Returns:
            List of appointment data
        """
        pass
    
    @abstractmethod
    def get_appointments_by_date_range(self, start_date: datetime, end_date: datetime,
                                     user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get appointments in date range.
        
        Args:
            start_date: Start date
            end_date: End date
            user_id: Optional user ID filter
            
        Returns:
            List of appointment data
        """
        pass
    
    @abstractmethod
    def get_upcoming_appointments(self, user_id: Optional[int] = None,
                                limit: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming appointments.
        
        Args:
            user_id: Optional user ID filter
            limit: Maximum number of results
            
        Returns:
            List of upcoming appointment data
        """
        pass
    
    @abstractmethod
    def update_appointment(self, appointment_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update appointment.
        
        Args:
            appointment_id: Appointment ID
            **kwargs: Update data
            
        Returns:
            Updated appointment data or None if failed
        """
        pass
    
    @abstractmethod
    def reschedule_appointment(self, appointment_id: int, new_start_time: datetime,
                             new_end_time: datetime) -> bool:
        """Reschedule appointment.
        
        Args:
            appointment_id: Appointment ID
            new_start_time: New start time
            new_end_time: New end time
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cancel_appointment(self, appointment_id: int, reason: Optional[str] = None) -> bool:
        """Cancel appointment.
        
        Args:
            appointment_id: Appointment ID
            reason: Cancellation reason
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def confirm_appointment(self, appointment_id: int) -> bool:
        """Confirm appointment.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete appointment.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def check_availability(self, user_id: int, start_time: datetime, 
                         end_time: datetime, exclude_appointment_id: Optional[int] = None) -> bool:
        """Check if user is available for time slot.
        
        Args:
            user_id: User ID
            start_time: Start time
            end_time: End time
            exclude_appointment_id: Appointment ID to exclude from conflict check
            
        Returns:
            True if available, False if conflicts exist
        """
        pass
    
    @abstractmethod
    def get_conflicts(self, user_id: int, start_time: datetime, end_time: datetime,
                     exclude_appointment_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conflicting appointments.
        
        Args:
            user_id: User ID
            start_time: Start time
            end_time: End time
            exclude_appointment_id: Appointment ID to exclude
            
        Returns:
            List of conflicting appointment data
        """
        pass
    
    @abstractmethod
    def get_user_schedule(self, user_id: int, date: datetime) -> List[Dict[str, Any]]:
        """Get user's schedule for a specific date.
        
        Args:
            user_id: User ID
            date: Date to get schedule for
            
        Returns:
            List of appointment data for the date
        """
        pass