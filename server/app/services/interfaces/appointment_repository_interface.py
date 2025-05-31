"""Interface for appointment repository operations."""

from abc import ABC, abstractmethod


class IAppointmentRepository(ABC):
    """Interface for appointment repository operations."""
    
    @abstractmethod
    def find_by_id(self, appointment_id):
        """Find appointment by ID."""
        pass
    
    @abstractmethod
    def find_all(self, filters=None, pagination=None):
        """Find all appointments matching filters with pagination."""
        pass
    
    @abstractmethod
    def create(self, appointment_data):
        """Create a new appointment."""
        pass
    
    @abstractmethod
    def update(self, appointment_id, update_data):
        """Update an existing appointment."""
        pass
    
    @abstractmethod
    def delete(self, appointment_id):
        """Delete an appointment."""
        pass