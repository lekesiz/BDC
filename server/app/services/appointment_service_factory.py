"""Factory for creating appointment service instances."""

from app.services.appointment_service import AppointmentService
from app import db


class AppointmentServiceFactory:
    """Factory for creating appointment service instances."""
    
    @staticmethod
    def create():
        """Create an appointment service instance with all dependencies."""
        # For now, return None to avoid complex dependency issues
        # TODO: Implement proper repository pattern
        return None