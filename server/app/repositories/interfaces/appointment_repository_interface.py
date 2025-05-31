"""Appointment repository interface module."""

from abc import ABC, abstractmethod
from datetime import datetime


class IAppointmentRepository(ABC):
    """Interface for AppointmentRepository."""
    
    @abstractmethod
    def find_by_id(self, appointment_id):
        """
        Find an appointment by ID.
        
        Args:
            appointment_id: The appointment ID
            
        Returns:
            Appointment object or None
        """
        pass
    
    @abstractmethod
    def find_all(self, filters=None, pagination=None):
        """
        Find all appointments matching filters.
        
        Args:
            filters: Dict with filter criteria
            pagination: Dict with page and per_page
            
        Returns:
            Paginated result with appointments
        """
        pass
    
    @abstractmethod
    def create(self, appointment_data):
        """
        Create a new appointment.
        
        Args:
            appointment_data: Dict containing appointment details
            
        Returns:
            Created appointment object
        """
        pass
    
    @abstractmethod
    def update(self, appointment_id, update_data):
        """
        Update an appointment.
        
        Args:
            appointment_id: The appointment ID
            update_data: Dict containing updated data
            
        Returns:
            Updated appointment object
        """
        pass
    
    @abstractmethod
    def delete(self, appointment_id):
        """
        Delete an appointment.
        
        Args:
            appointment_id: The appointment ID
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    def find_by_beneficiary(self, beneficiary_id, pagination=None):
        """
        Find appointments for a beneficiary.
        
        Args:
            beneficiary_id: The beneficiary ID
            pagination: Dict with page and per_page
            
        Returns:
            Paginated result with appointments
        """
        pass
    
    @abstractmethod
    def find_by_trainer(self, trainer_id, pagination=None):
        """
        Find appointments for a trainer.
        
        Args:
            trainer_id: The trainer ID
            pagination: Dict with page and per_page
            
        Returns:
            Paginated result with appointments
        """
        pass