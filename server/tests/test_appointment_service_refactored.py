"""Comprehensive tests for the refactored appointment service."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.appointment_service_refactored import AppointmentServiceRefactored
from app.exceptions import NotFoundException, ForbiddenException, ValidationException


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock()
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.delete = Mock()
    session.refresh = Mock()
    return session


@pytest.fixture
def appointment_service(mock_db_session):
    """Create appointment service instance with mocked dependencies."""
    return AppointmentServiceRefactored(mock_db_session)


@pytest.fixture
def sample_trainer():
    """Create a sample trainer user."""
    trainer = Mock()
    trainer.id = 1
    trainer.role = 'trainer'
    trainer.first_name = 'John'
    trainer.last_name = 'Doe'
    trainer.email = 'trainer@example.com'
    return trainer


@pytest.fixture
def sample_student():
    """Create a sample student user."""
    student = Mock()
    student.id = 2
    student.role = 'student'
    student.first_name = 'Jane'
    student.last_name = 'Smith'
    student.email = 'student@example.com'
    return student


@pytest.fixture
def sample_admin():
    """Create a sample admin user."""
    admin = Mock()
    admin.id = 3
    admin.role = 'admin'
    admin.first_name = 'Admin'
    admin.last_name = 'User'
    admin.email = 'admin@example.com'
    return admin


@pytest.fixture
def sample_beneficiary(sample_student, sample_trainer):
    """Create a sample beneficiary."""
    beneficiary = Mock()
    beneficiary.id = 10
    beneficiary.user_id = sample_student.id
    beneficiary.user = sample_student
    beneficiary.trainer_id = sample_trainer.id
    return beneficiary


@pytest.fixture
def sample_appointment(sample_trainer, sample_beneficiary):
    """Create a sample appointment."""
    appointment = Mock()
    appointment.id = 100
    appointment.title = 'Test Appointment'
    appointment.description = 'Test description'
    appointment.location = 'Test location'
    appointment.start_time = datetime.utcnow() + timedelta(hours=1)
    appointment.end_time = datetime.utcnow() + timedelta(hours=2)
    appointment.trainer_id = sample_trainer.id
    appointment.trainer = sample_trainer
    appointment.beneficiary_id = sample_beneficiary.id
    appointment.beneficiary = sample_beneficiary
    appointment.status = 'scheduled'
    appointment.calendar_event_id = None
    appointment.created_at = datetime.utcnow()
    appointment.updated_at = datetime.utcnow()
    return appointment


class TestGetAppointmentsForUser:
    """Test cases for get_appointments_for_user method."""
    
    def test_get_appointments_for_trainer(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test getting appointments for a trainer."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_trainer
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # Mock pagination
        mock_pagination = Mock()
        mock_pagination.items = [sample_appointment]
        mock_pagination.total = 1
        mock_pagination.pages = 1
        mock_pagination.page = 1
        mock_query.paginate.return_value = mock_pagination
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = appointment_service.get_appointments_for_user(
            user_id=sample_trainer.id,
            page=1,
            per_page=10
        )
        
        # Assert
        assert result['total'] == 1
        assert result['pages'] == 1
        assert result['current_page'] == 1
        assert len(result['appointments']) == 1
        assert result['appointments'][0]['id'] == sample_appointment.id
    
    def test_get_appointments_for_student(
        self,
        appointment_service,
        mock_db_session,
        sample_student,
        sample_beneficiary,
        sample_appointment
    ):
        """Test getting appointments for a student."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_student,  # First call for user
            sample_beneficiary  # Second call for beneficiary
        ]
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # Mock pagination
        mock_pagination = Mock()
        mock_pagination.items = [sample_appointment]
        mock_pagination.total = 1
        mock_pagination.pages = 1
        mock_pagination.page = 1
        mock_query.paginate.return_value = mock_pagination
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = appointment_service.get_appointments_for_user(
            user_id=sample_student.id
        )
        
        # Assert
        assert len(result['appointments']) == 1
        # Students see appointments but beneficiary info is limited based on their role
    
    def test_get_appointments_with_filters(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test getting appointments with date and status filters."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_trainer
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # Mock pagination
        mock_pagination = Mock()
        mock_pagination.items = [sample_appointment]
        mock_pagination.total = 1
        mock_pagination.pages = 1
        mock_pagination.page = 1
        mock_query.paginate.return_value = mock_pagination
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        start_date = datetime.utcnow()
        end_date = datetime.utcnow() + timedelta(days=7)
        
        result = appointment_service.get_appointments_for_user(
            user_id=sample_trainer.id,
            start_date=start_date,
            end_date=end_date,
            status='scheduled'
        )
        
        # Assert query filters were applied
        mock_query.filter.assert_called()
        mock_query.filter_by.assert_called_with(status='scheduled')
    
    def test_get_appointments_user_not_found(
        self,
        appointment_service,
        mock_db_session
    ):
        """Test getting appointments when user doesn't exist."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = None
        
        # Execute and assert
        with pytest.raises(NotFoundException) as exc_info:
            appointment_service.get_appointments_for_user(user_id=999)
        
        assert "User 999 not found" in str(exc_info.value)


class TestCreateAppointment:
    """Test cases for create_appointment method."""
    
    def test_create_appointment_success(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_beneficiary
    ):
        """Test successful appointment creation."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,  # First call for trainer
            sample_beneficiary  # Second call for beneficiary
        ]
        
        # Appointment data
        appointment_data = {
            'title': 'New Appointment',
            'description': 'Test description',
            'location': 'Online',
            'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'beneficiary_id': sample_beneficiary.id
        }
        
        # Mock the created appointment
        created_appointment = Mock()
        created_appointment.id = 101
        created_appointment.title = appointment_data['title']
        created_appointment.description = appointment_data['description']
        created_appointment.location = appointment_data['location']
        created_appointment.start_time = datetime.fromisoformat(appointment_data['start_time'].replace('Z', '+00:00'))
        created_appointment.end_time = datetime.fromisoformat(appointment_data['end_time'].replace('Z', '+00:00'))
        created_appointment.trainer_id = sample_trainer.id
        created_appointment.trainer = sample_trainer
        created_appointment.beneficiary_id = sample_beneficiary.id
        created_appointment.beneficiary = sample_beneficiary
        created_appointment.status = 'scheduled'
        created_appointment.calendar_event_id = None
        created_appointment.created_at = datetime.utcnow()
        created_appointment.updated_at = datetime.utcnow()
        
        # Mock refresh to return the created appointment
        mock_db_session.refresh.side_effect = lambda x: setattr(x, 'id', 101) or setattr(x, 'created_at', datetime.utcnow()) or setattr(x, 'updated_at', datetime.utcnow())
        
        # Execute
        with patch.object(appointment_service, '_serialize_appointment', return_value={'id': 101, 'title': appointment_data['title']}):
            result = appointment_service.create_appointment(
                trainer_id=sample_trainer.id,
                appointment_data=appointment_data
            )
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        assert result['title'] == appointment_data['title']
    
    def test_create_appointment_student_forbidden(
        self,
        appointment_service,
        mock_db_session,
        sample_student
    ):
        """Test that students cannot create appointments."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_student
        
        # Execute and assert
        with pytest.raises(ForbiddenException) as exc_info:
            appointment_service.create_appointment(
                trainer_id=sample_student.id,
                appointment_data={'title': 'Test'}
            )
        
        assert "Only trainers and admins can manage appointments" in str(exc_info.value)
    
    def test_create_appointment_missing_fields(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer
    ):
        """Test appointment creation with missing required fields."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_trainer
        
        # Missing required fields
        appointment_data = {
            'title': 'New Appointment'
            # Missing start_time, end_time, beneficiary_id
        }
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            appointment_service.create_appointment(
                trainer_id=sample_trainer.id,
                appointment_data=appointment_data
            )
        
        assert "Missing required field" in str(exc_info.value)
    
    def test_create_appointment_invalid_dates(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer
    ):
        """Test appointment creation with invalid date range."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_trainer
        
        # Invalid date range (end before start)
        appointment_data = {
            'title': 'New Appointment',
            'start_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'beneficiary_id': 10
        }
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            appointment_service.create_appointment(
                trainer_id=sample_trainer.id,
                appointment_data=appointment_data
            )
        
        assert "Start time must be before end time" in str(exc_info.value)
    
    def test_create_appointment_past_date(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer
    ):
        """Test appointment creation with past date."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_trainer
        
        # Past date
        appointment_data = {
            'title': 'New Appointment',
            'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'beneficiary_id': 10
        }
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            appointment_service.create_appointment(
                trainer_id=sample_trainer.id,
                appointment_data=appointment_data
            )
        
        assert "Cannot create appointments in the past" in str(exc_info.value)
    
    def test_create_appointment_trainer_no_access(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_beneficiary
    ):
        """Test appointment creation when trainer doesn't have access to beneficiary."""
        # Setup mocks
        sample_beneficiary.trainer_id = 999  # Different trainer
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_beneficiary
        ]
        
        appointment_data = {
            'title': 'New Appointment',
            'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'beneficiary_id': sample_beneficiary.id
        }
        
        # Execute and assert
        with pytest.raises(ForbiddenException) as exc_info:
            appointment_service.create_appointment(
                trainer_id=sample_trainer.id,
                appointment_data=appointment_data
            )
        
        assert "You do not have access to this beneficiary" in str(exc_info.value)


class TestUpdateAppointment:
    """Test cases for update_appointment method."""
    
    def test_update_appointment_success(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test successful appointment update."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment
        ]
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'status': 'completed'
        }
        
        # Execute
        result = appointment_service.update_appointment(
            appointment_id=sample_appointment.id,
            user_id=sample_trainer.id,
            update_data=update_data
        )
        
        # Assert
        mock_db_session.commit.assert_called_once()
        assert sample_appointment.title == 'Updated Title'
        assert sample_appointment.status == 'completed'
    
    def test_update_appointment_trainer_no_permission(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test appointment update when trainer doesn't own it."""
        # Setup mocks
        sample_appointment.trainer_id = 999  # Different trainer
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment
        ]
        
        # Execute and assert
        with pytest.raises(ForbiddenException) as exc_info:
            appointment_service.update_appointment(
                appointment_id=sample_appointment.id,
                user_id=sample_trainer.id,
                update_data={'title': 'New Title'}
            )
        
        assert "You do not have permission" in str(exc_info.value)
    
    def test_update_appointment_invalid_dates(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test appointment update with invalid date range."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment
        ]
        
        # Set initial valid dates
        sample_appointment.start_time = datetime.utcnow() + timedelta(hours=1)
        sample_appointment.end_time = datetime.utcnow() + timedelta(hours=2)
        
        update_data = {
            'start_time': (datetime.utcnow() + timedelta(hours=3)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            appointment_service.update_appointment(
                appointment_id=sample_appointment.id,
                user_id=sample_trainer.id,
                update_data=update_data
            )
        
        assert "Start time must be before end time" in str(exc_info.value)


class TestDeleteAppointment:
    """Test cases for delete_appointment method."""
    
    def test_delete_appointment_success(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test successful appointment deletion."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment
        ]
        
        # Execute
        result = appointment_service.delete_appointment(
            appointment_id=sample_appointment.id,
            user_id=sample_trainer.id
        )
        
        # Assert
        mock_db_session.delete.assert_called_once_with(sample_appointment)
        mock_db_session.commit.assert_called_once()
        assert result['message'] == 'Appointment deleted successfully'
    
    @patch('app.services.appointment_service_refactored.CalendarService')
    def test_delete_appointment_with_calendar_sync(
        self,
        mock_calendar_service,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test appointment deletion with calendar sync."""
        # Setup mocks
        sample_appointment.calendar_event_id = 'google_event_123'
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment,
            Mock()  # Calendar integration
        ]
        
        # Execute
        result = appointment_service.delete_appointment(
            appointment_id=sample_appointment.id,
            user_id=sample_trainer.id
        )
        
        # Assert
        mock_calendar_service.delete_calendar_event.assert_called_once()
        assert result['message'] == 'Appointment deleted successfully'
    
    def test_delete_appointment_not_found(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer
    ):
        """Test appointment deletion when appointment doesn't exist."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            None  # Appointment not found
        ]
        
        # Execute and assert
        with pytest.raises(NotFoundException) as exc_info:
            appointment_service.delete_appointment(
                appointment_id=999,
                user_id=sample_trainer.id
            )
        
        assert "Appointment 999 not found" in str(exc_info.value)


class TestCalendarSync:
    """Test cases for calendar sync methods."""
    
    @patch('app.services.appointment_service_refactored.CalendarService')
    @patch('app.services.appointment_service_refactored.send_notification_email')
    def test_sync_to_calendar_success(
        self,
        mock_send_email,
        mock_calendar_service,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test successful calendar sync."""
        # Setup mocks
        mock_integration = Mock()
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment,
            mock_integration
        ]
        
        mock_calendar_service.create_calendar_event.return_value = 'new_event_id'
        
        # Execute
        result = appointment_service.sync_to_calendar(
            appointment_id=sample_appointment.id,
            user_id=sample_trainer.id
        )
        
        # Assert
        assert result['calendar_event_id'] == 'new_event_id'
        assert sample_appointment.calendar_event_id == 'new_event_id'
        mock_send_email.assert_called_once()
        mock_db_session.commit.assert_called()
    
    def test_sync_to_calendar_no_integration(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test calendar sync when no integration exists."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment,
            None  # No integration
        ]
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            appointment_service.sync_to_calendar(
                appointment_id=sample_appointment.id,
                user_id=sample_trainer.id
            )
        
        assert "Google Calendar not connected" in str(exc_info.value)
    
    @patch('app.services.appointment_service_refactored.CalendarService')
    def test_unsync_from_calendar_success(
        self,
        mock_calendar_service,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test successful calendar unsync."""
        # Setup mocks
        sample_appointment.calendar_event_id = 'event_to_remove'
        
        mock_integration = Mock()
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment,
            mock_integration
        ]
        
        # Execute
        result = appointment_service.unsync_from_calendar(
            appointment_id=sample_appointment.id,
            user_id=sample_trainer.id
        )
        
        # Assert
        assert sample_appointment.calendar_event_id is None
        mock_calendar_service.delete_calendar_event.assert_called_once()
        assert result['message'] == 'Appointment unsynced from Google Calendar successfully'
    
    def test_unsync_from_calendar_not_synced(
        self,
        appointment_service,
        mock_db_session,
        sample_trainer,
        sample_appointment
    ):
        """Test calendar unsync when appointment is not synced."""
        # Setup mocks
        sample_appointment.calendar_event_id = None
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_appointment
        ]
        
        # Execute
        result = appointment_service.unsync_from_calendar(
            appointment_id=sample_appointment.id,
            user_id=sample_trainer.id
        )
        
        # Assert
        assert result['message'] == 'Appointment is not synced to Google Calendar'