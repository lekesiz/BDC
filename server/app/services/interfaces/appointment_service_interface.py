"""Appointment service interface module."""

from abc import ABC, abstractmethod
from datetime import datetime


class IAppointmentService(ABC):
    """Interface for AppointmentService."""
    
    @abstractmethod
    def get_appointments(self, user_id, page=1, per_page=10, start_date=None, end_date=None, status=None):
        """
        Get paginated appointments for a user.
        
        Args:
            user_id: The user's ID
            page: Page number
            per_page: Items per page
            start_date: Filter appointments from this date
            end_date: Filter appointments to this date
            status: Filter by appointment status
            
        Returns:
            Dict containing appointments, total count, pages, and current page
        """
        pass
    
    @abstractmethod
    def create_appointment(self, trainer_id, appointment_data):
        """
        Create a new appointment.
        
        Args:
            trainer_id: The trainer's user ID
            appointment_data: Dict containing appointment details
            
        Returns:
            Created appointment object
        """
        pass
    
    @abstractmethod
    def update_appointment(self, appointment_id, user_id, update_data):
        """
        Update an existing appointment.
        
        Args:
            appointment_id: The appointment ID
            user_id: The requesting user's ID
            update_data: Dict containing updated appointment data
            
        Returns:
            Updated appointment object
        """
        pass
    
    @abstractmethod
    def delete_appointment(self, appointment_id, user_id):
        """
        Delete an appointment.
        
        Args:
            appointment_id: The appointment ID
            user_id: The requesting user's ID
            
        Returns:
            Success message
        """
        pass
    
    @abstractmethod
    def sync_to_calendar(self, appointment_id, user_id):
        """
        Sync appointment to Google Calendar.
        
        Args:
            appointment_id: The appointment ID
            user_id: The requesting user's ID
            
        Returns:
            Dict containing sync status and event ID
        """
        pass
    
    @abstractmethod
    def unsync_from_calendar(self, appointment_id, user_id):
        """
        Remove appointment from Google Calendar.
        
        Args:
            appointment_id: The appointment ID
            user_id: The requesting user's ID
            
        Returns:
            Success message
        """
        pass