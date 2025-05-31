"""Tests for appointment service."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from app.services.appointment_service_refactored import AppointmentServiceRefactored
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.exceptions import NotFoundException, ForbiddenException, ValidationException


class TestAppointmentService:
    """Test suite for appointment service."""
    
    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories."""
        appointment_repo = Mock()
        user_repo = Mock()
        beneficiary_repo = Mock()
        return appointment_repo, user_repo, beneficiary_repo
    
    @pytest.fixture
    def appointment_service(self, mock_repositories):
        """Create appointment service instance."""
        appointment_repo, user_repo, beneficiary_repo = mock_repositories
        return AppointmentServiceRefactored(appointment_repo, user_repo, beneficiary_repo)
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = 1
        user.role = 'trainer'
        user.email = 'trainer@example.com'
        user.first_name = 'John'
        user.last_name = 'Doe'
        return user
    
    @pytest.fixture
    def mock_beneficiary(self):
        """Create a mock beneficiary."""
        beneficiary = Mock(spec=Beneficiary)
        beneficiary.id = 1
        beneficiary.trainer_id = 1
        beneficiary.user = Mock(spec=User)
        beneficiary.user.id = 2
        beneficiary.user.first_name = 'Jane'
        beneficiary.user.last_name = 'Smith'
        beneficiary.user.email = 'jane@example.com'
        return beneficiary
    
    @pytest.fixture
    def mock_appointment(self, mock_user, mock_beneficiary):
        """Create a mock appointment."""
        appointment = Mock(spec=Appointment)
        appointment.id = 1
        appointment.trainer_id = 1
        appointment.beneficiary_id = 1
        appointment.trainer = mock_user
        appointment.beneficiary = mock_beneficiary
        appointment.title = "Test Appointment"
        appointment.start_time = datetime.utcnow() + timedelta(hours=1)
        appointment.end_time = datetime.utcnow() + timedelta(hours=2)
        appointment.status = 'scheduled'
        appointment.calendar_event_id = None
        appointment.to_dict = Mock(return_value={
            'id': 1,
            'title': 'Test Appointment',
            'start_time': appointment.start_time.isoformat(),
            'end_time': appointment.end_time.isoformat(),
            'status': 'scheduled'
        })
        return appointment
    
    def test_get_appointments_success(self, appointment_service, mock_repositories, mock_user, mock_appointment):
        """Test successful appointment retrieval."""
        appointment_repo, user_repo, beneficiary_repo = mock_repositories
        
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_all.return_value = {
            'items': [mock_appointment],
            'total': 1,
            'pages': 1,
            'current_page': 1
        }
        
        result = appointment_service.get_appointments(user_id=1)
        
        user_repo.find_by_id.assert_called_once_with(1)
        appointment_repo.find_all.assert_called_once()
        assert len(result['appointments']) == 1
        assert result['total'] == 1
    
    def test_get_appointments_user_not_found(self, appointment_service, mock_repositories):
        """Test get appointments with non-existent user."""
        _, user_repo, _ = mock_repositories
        user_repo.find_by_id.return_value = None
        
        with pytest.raises(NotFoundException) as excinfo:
            appointment_service.get_appointments(user_id=999)
        
        assert "User 999 not found" in str(excinfo.value)
    
    def test_create_appointment_success(self, appointment_service, mock_repositories, mock_user, mock_beneficiary, mock_appointment):
        """Test successful appointment creation."""
        appointment_repo, user_repo, beneficiary_repo = mock_repositories
        
        user_repo.find_by_id.return_value = mock_user
        beneficiary_repo.find_by_id.return_value = mock_beneficiary
        appointment_repo.create.return_value = mock_appointment
        
        appointment_data = {
            'title': 'Test Appointment',
            'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'beneficiary_id': 1
        }
        
        result = appointment_service.create_appointment(trainer_id=1, appointment_data=appointment_data)
        
        user_repo.find_by_id.assert_called_once_with(1)
        beneficiary_repo.find_by_id.assert_called_once_with(1)
        appointment_repo.create.assert_called_once()
        assert result['id'] == 1
    
    def test_create_appointment_invalid_role(self, appointment_service, mock_repositories, mock_user):
        """Test appointment creation with invalid user role."""
        _, user_repo, _ = mock_repositories
        mock_user.role = 'student'
        user_repo.find_by_id.return_value = mock_user
        
        appointment_data = {
            'title': 'Test Appointment',
            'start_time': datetime.utcnow().isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'beneficiary_id': 1
        }
        
        with pytest.raises(ForbiddenException) as excinfo:
            appointment_service.create_appointment(trainer_id=1, appointment_data=appointment_data)
        
        assert "Only trainers and admins can create appointments" in str(excinfo.value)
    
    def test_create_appointment_missing_fields(self, appointment_service, mock_repositories, mock_user):
        """Test appointment creation with missing fields."""
        _, user_repo, _ = mock_repositories
        user_repo.find_by_id.return_value = mock_user
        
        appointment_data = {
            'title': 'Test Appointment'
        }
        
        with pytest.raises(ValidationException) as excinfo:
            appointment_service.create_appointment(trainer_id=1, appointment_data=appointment_data)
        
        assert "Missing required field" in str(excinfo.value)
    
    def test_create_appointment_past_date(self, appointment_service, mock_repositories, mock_user, mock_beneficiary):
        """Test appointment creation with past date."""
        _, user_repo, beneficiary_repo = mock_repositories
        user_repo.find_by_id.return_value = mock_user
        beneficiary_repo.find_by_id.return_value = mock_beneficiary
        
        appointment_data = {
            'title': 'Test Appointment',
            'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            'beneficiary_id': 1
        }
        
        with pytest.raises(ValidationException) as excinfo:
            appointment_service.create_appointment(trainer_id=1, appointment_data=appointment_data)
        
        assert "Cannot create appointments in the past" in str(excinfo.value)
    
    def test_update_appointment_success(self, appointment_service, mock_repositories, mock_user, mock_appointment):
        """Test successful appointment update."""
        appointment_repo, user_repo, _ = mock_repositories
        
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = mock_appointment
        
        updated_appointment = Mock(spec=Appointment)
        updated_appointment.start_time = datetime.utcnow() + timedelta(hours=2)
        updated_appointment.end_time = datetime.utcnow() + timedelta(hours=3)
        updated_appointment.to_dict = Mock(return_value={'id': 1, 'title': 'Updated'})
        appointment_repo.update.return_value = updated_appointment
        
        update_data = {'title': 'Updated Appointment'}
        result = appointment_service.update_appointment(
            appointment_id=1,
            user_id=1,
            update_data=update_data
        )
        
        user_repo.find_by_id.assert_called_once_with(1)
        appointment_repo.find_by_id.assert_called_once_with(1)
        appointment_repo.update.assert_called_once_with(1, {'title': 'Updated Appointment'})
        assert result['id'] == 1
    
    def test_update_appointment_not_found(self, appointment_service, mock_repositories, mock_user):
        """Test update non-existent appointment."""
        appointment_repo, user_repo, _ = mock_repositories
        
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = None
        
        with pytest.raises(NotFoundException) as excinfo:
            appointment_service.update_appointment(
                appointment_id=999,
                user_id=1,
                update_data={'title': 'Updated'}
            )
        
        assert "Appointment 999 not found" in str(excinfo.value)
    
    def test_update_appointment_no_permission(self, appointment_service, mock_repositories, mock_user, mock_appointment):
        """Test update appointment without permission."""
        appointment_repo, user_repo, _ = mock_repositories
        
        mock_appointment.trainer_id = 2  # Different trainer
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = mock_appointment
        
        with pytest.raises(ForbiddenException) as excinfo:
            appointment_service.update_appointment(
                appointment_id=1,
                user_id=1,
                update_data={'title': 'Updated'}
            )
        
        assert "You do not have permission to update this appointment" in str(excinfo.value)
    
    def test_delete_appointment_success(self, appointment_service, mock_repositories, mock_user, mock_appointment):
        """Test successful appointment deletion."""
        appointment_repo, user_repo, _ = mock_repositories
        
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = mock_appointment
        appointment_repo.delete.return_value = True
        
        result = appointment_service.delete_appointment(appointment_id=1, user_id=1)
        
        assert result['message'] == 'Appointment deleted successfully'
        appointment_repo.delete.assert_called_once_with(1)
    
    def test_delete_appointment_not_found(self, appointment_service, mock_repositories, mock_user):
        """Test delete non-existent appointment."""
        appointment_repo, user_repo, _ = mock_repositories
        
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = None
        
        with pytest.raises(NotFoundException) as excinfo:
            appointment_service.delete_appointment(appointment_id=999, user_id=1)
        
        assert "Appointment 999 not found" in str(excinfo.value)
    
    def test_delete_appointment_no_permission(self, appointment_service, mock_repositories, mock_user, mock_appointment):
        """Test delete appointment without permission."""
        appointment_repo, user_repo, _ = mock_repositories
        
        mock_appointment.trainer_id = 2  # Different trainer
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = mock_appointment
        
        with pytest.raises(ForbiddenException) as excinfo:
            appointment_service.delete_appointment(appointment_id=1, user_id=1)
        
        assert "You do not have permission to delete this appointment" in str(excinfo.value)
    
    @patch('app.services.appointment_service_refactored.UserIntegration')
    @patch('app.services.appointment_service_refactored.CalendarService')
    def test_sync_to_calendar_success(self, mock_calendar_service, mock_user_integration, 
                                    appointment_service, mock_repositories, mock_user, mock_appointment):
        """Test successful calendar sync."""
        appointment_repo, user_repo, _ = mock_repositories
        
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = mock_appointment
        
        # Mock Flask-SQLAlchemy query
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_first = Mock()
        mock_integration = Mock()
        
        mock_user_integration.query = mock_query
        mock_query.filter_by.return_value = mock_filter_by 
        mock_filter_by.first.return_value = mock_integration
        
        mock_calendar_service.create_calendar_event.return_value = 'event123'
        
        result = appointment_service.sync_to_calendar(appointment_id=1, user_id=1)
        
        assert result['message'] == 'Appointment synced to Google Calendar successfully'
        assert result['calendar_event_id'] == 'event123'
        appointment_repo.update.assert_called_once_with(1, {'calendar_event_id': 'event123'})
    
    @patch('app.services.appointment_service_refactored.UserIntegration')
    def test_sync_to_calendar_no_integration(self, mock_user_integration, 
                                           appointment_service, mock_repositories, mock_user):
        """Test calendar sync without integration."""
        _, user_repo, _ = mock_repositories
        
        user_repo.find_by_id.return_value = mock_user
        
        # Mock Flask-SQLAlchemy query to return None
        mock_query = Mock()
        mock_filter_by = Mock()
        
        mock_user_integration.query = mock_query
        mock_query.filter_by.return_value = mock_filter_by
        mock_filter_by.first.return_value = None
        
        with pytest.raises(ValidationException) as excinfo:
            appointment_service.sync_to_calendar(appointment_id=1, user_id=1)
        
        assert "Google Calendar not connected" in str(excinfo.value)
    
    @patch('app.services.appointment_service_refactored.UserIntegration')
    @patch('app.services.appointment_service_refactored.CalendarService')
    def test_unsync_from_calendar_success(self, mock_calendar_service, mock_user_integration,
                                        appointment_service, mock_repositories, mock_user, mock_appointment):
        """Test successful calendar unsync."""
        appointment_repo, user_repo, _ = mock_repositories
        
        mock_appointment.calendar_event_id = 'event123'
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = mock_appointment
        
        # Mock Flask-SQLAlchemy query
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_integration = Mock()
        
        mock_user_integration.query = mock_query
        mock_query.filter_by.return_value = mock_filter_by
        mock_filter_by.first.return_value = mock_integration
        
        mock_calendar_service.delete_calendar_event.return_value = True
        
        result = appointment_service.unsync_from_calendar(appointment_id=1, user_id=1)
        
        assert result['message'] == 'Appointment unsynced from Google Calendar successfully'
        appointment_repo.update.assert_called_once_with(1, {'calendar_event_id': None})
        mock_calendar_service.delete_calendar_event.assert_called_once()
    
    def test_unsync_from_calendar_not_synced(self, appointment_service, mock_repositories, mock_user, mock_appointment):
        """Test unsync appointment that's not synced."""
        appointment_repo, user_repo, _ = mock_repositories
        
        mock_appointment.calendar_event_id = None
        user_repo.find_by_id.return_value = mock_user
        appointment_repo.find_by_id.return_value = mock_appointment
        
        result = appointment_service.unsync_from_calendar(appointment_id=1, user_id=1)
        
        assert result['message'] == 'Appointment is not synced to Google Calendar'
        appointment_repo.update.assert_not_called()