"""Tests for Appointment model."""

import pytest
from datetime import datetime
from unittest.mock import Mock
from app.models.appointment import Appointment


class TestAppointmentModel:
    """Test the Appointment model."""
    
    @pytest.fixture
    def appointment(self):
        """Create a test appointment."""
        appt = Appointment(
            beneficiary_id=1,
            trainer_id=2,
            title='Career Counseling Session',
            description='Monthly career guidance session',
            start_time=datetime(2024, 1, 15, 10, 0, 0),
            end_time=datetime(2024, 1, 15, 11, 0, 0),
            location='Meeting Room A'
        )
        # Set timestamps for testing
        appt.created_at = datetime(2024, 1, 10, 9, 0, 0)
        appt.updated_at = datetime(2024, 1, 10, 9, 0, 0)
        return appt
    
    def test_appointment_creation(self, appointment):
        """Test appointment creation with basic fields."""
        assert appointment.beneficiary_id == 1
        assert appointment.trainer_id == 2
        assert appointment.title == 'Career Counseling Session'
        assert appointment.description == 'Monthly career guidance session'
        assert appointment.start_time == datetime(2024, 1, 15, 10, 0, 0)
        assert appointment.end_time == datetime(2024, 1, 15, 11, 0, 0)
        assert appointment.location == 'Meeting Room A'
        assert appointment.status == 'scheduled'
    
    def test_appointment_defaults(self):
        """Test appointment default values."""
        appt = Appointment(
            beneficiary_id=1,
            trainer_id=1,
            title='Test',
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        assert appt.status == 'scheduled'
        assert appt.description is None
        assert appt.location is None
        assert appt.notes is None
        assert appt.calendar_event_id is None
    
    def test_appointment_to_dict_basic(self, appointment):
        """Test appointment to_dict without relationships."""
        appointment.beneficiary = None
        appointment.trainer = None
        
        result = appointment.to_dict()
        
        assert result['id'] == appointment.id
        assert result['beneficiary_id'] == 1
        assert result['trainer_id'] == 2
        assert result['title'] == 'Career Counseling Session'
        assert result['description'] == 'Monthly career guidance session'
        assert result['start_time'] == '2024-01-15T10:00:00'
        assert result['end_time'] == '2024-01-15T11:00:00'
        assert result['location'] == 'Meeting Room A'
        assert result['status'] == 'scheduled'
        assert result['beneficiary'] is None
        assert result['trainer'] is None
    
    def test_appointment_to_dict_with_relationships(self, appointment):
        """Test appointment to_dict with relationships."""
        # Mock beneficiary
        appointment.beneficiary = Mock()
        appointment.beneficiary.id = 1
        appointment.beneficiary.user = Mock()
        appointment.beneficiary.user.first_name = 'John'
        appointment.beneficiary.user.last_name = 'Doe'
        appointment.beneficiary.user.email = 'john@example.com'
        
        # Mock trainer
        appointment.trainer = Mock()
        appointment.trainer.id = 2
        appointment.trainer.first_name = 'Jane'
        appointment.trainer.last_name = 'Smith'
        appointment.trainer.email = 'jane@example.com'
        
        result = appointment.to_dict()
        
        assert result['beneficiary']['first_name'] == 'John'
        assert result['beneficiary']['last_name'] == 'Doe'
        assert result['beneficiary']['email'] == 'john@example.com'
        assert result['trainer']['first_name'] == 'Jane'
        assert result['trainer']['last_name'] == 'Smith'
        assert result['trainer']['email'] == 'jane@example.com'
    
    def test_appointment_with_calendar_event(self, appointment):
        """Test appointment with calendar integration."""
        appointment.calendar_event_id = 'google_calendar_event_123'
        appointment.notes = 'Discussed career goals and next steps'
        
        appointment.beneficiary = None
        appointment.trainer = None
        
        result = appointment.to_dict()
        
        assert result['calendar_event_id'] == 'google_calendar_event_123'
        assert result['notes'] == 'Discussed career goals and next steps'
    
    def test_appointment_status_changes(self, appointment):
        """Test appointment status changes."""
        assert appointment.status == 'scheduled'
        
        appointment.status = 'completed'
        assert appointment.status == 'completed'
        
        appointment.status = 'cancelled'
        assert appointment.status == 'cancelled'
    
    def test_appointment_repr(self, appointment):
        """Test appointment string representation."""
        appointment.id = 123
        assert repr(appointment) == '<Appointment 123 Career Counseling Session>'
    
    def test_appointment_relationships(self, appointment):
        """Test appointment relationships."""
        assert hasattr(appointment, 'beneficiary')
        assert hasattr(appointment, 'trainer')