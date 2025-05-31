"""Factory for creating appointment service instances."""

from app.services.appointment_service_refactored import AppointmentServiceRefactored
from app import db


class AppointmentServiceFactory:
    """Factory for creating appointment service instances."""
    
    @staticmethod
    def create():
        """Create an appointment service instance with all dependencies."""
        return AppointmentServiceRefactored(db.session)