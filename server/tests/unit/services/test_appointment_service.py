"""Unit tests for AppointmentService."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.services.appointment_service import AppointmentService
from app.exceptions import NotFoundException, ForbiddenException, ValidationException


class TestAppointmentService:
    """Test cases for AppointmentService."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.appointment_repository = Mock()
        self.user_repository = Mock()
        self.beneficiary_repository = Mock()
        
        self.service = AppointmentService(
            appointment_repository=self.appointment_repository,
            user_repository=self.user_repository,
            beneficiary_repository=self.beneficiary_repository
        )
        
        # Mock user data
        self.mock_trainer = Mock(
            id=1,
            role='trainer',
            first_name='John',
            last_name='Doe',
            email='trainer@test.com'
        )
        
        self.mock_student = Mock(
            id=2,
            role='student',
            first_name='Jane',
            last_name='Smith',
            email='student@test.com'
        )
        
        self.mock_admin = Mock(
            id=3,
            role='admin',
            first_name='Admin',
            last_name='User',
            email='admin@test.com'
        )
        
        # Mock beneficiary
        self.mock_beneficiary = Mock(
            id=1,
            user=self.mock_student,
            trainer_id=1,
            user_id=2
        )
        
        # Mock appointment
        self.mock_appointment = Mock(
            id=1,
            title='Test Appointment',
            description='Test Description',
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            trainer_id=1,
            trainer=self.mock_trainer,
            beneficiary_id=1,
            beneficiary=self.mock_beneficiary,
            status='scheduled',
            calendar_event_id=None,
            to_dict=Mock(return_value={
                'id': 1,
                'title': 'Test Appointment',
                'description': 'Test Description',
                'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                'trainer_id': 1,
                'beneficiary_id': 1,
                'status': 'scheduled'
            })
        )
    
    def test_get_appointments_trainer(self):
        """Test getting appointments for a trainer."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.appointment_repository.find_all.return_value = {
            'items': [self.mock_appointment],
            'total': 1,
            'pages': 1,
            'current_page': 1
        }
        
        # Test
        result = self.service.get_appointments(
            user_id=1,
            page=1,
            per_page=10
        )
        
        # Verify
        assert len(result['appointments']) == 1
        assert result['total'] == 1
        assert result['pages'] == 1
        assert result['current_page'] == 1
        
        # Verify repository calls
        self.user_repository.find_by_id.assert_called_once_with(1)
        self.appointment_repository.find_all.assert_called_once()
        
        # Verify filters
        call_args = self.appointment_repository.find_all.call_args
        assert call_args[1]['filters']['user_id'] == 1
        assert call_args[1]['filters']['role'] == 'trainer'
    
    def test_get_appointments_student(self):
        """Test getting appointments for a student."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_student
        self.appointment_repository.find_all.return_value = {
            'items': [self.mock_appointment],
            'total': 1,
            'pages': 1,
            'current_page': 1
        }
        
        # Test
        result = self.service.get_appointments(
            user_id=2,
            page=1,
            per_page=10
        )
        
        # Verify
        assert len(result['appointments']) == 1
        
        # Verify filters
        call_args = self.appointment_repository.find_all.call_args
        assert call_args[1]['filters']['user_id'] == 2
        assert call_args[1]['filters']['role'] == 'student'
    
    def test_get_appointments_user_not_found(self):
        """Test getting appointments when user is not found."""
        self.user_repository.find_by_id.return_value = None
        
        with pytest.raises(NotFoundException) as exc:
            self.service.get_appointments(user_id=999)
        
        assert "User 999 not found" in str(exc.value)
    
    def test_get_appointments_with_filters(self):
        """Test getting appointments with date and status filters."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.appointment_repository.find_all.return_value = {
            'items': [],
            'total': 0,
            'pages': 0,
            'current_page': 1
        }
        
        # Test with date strings
        result = self.service.get_appointments(
            user_id=1,
            start_date='2024-01-01',
            end_date='2024-01-31',
            status='scheduled'
        )
        
        # Verify filters were applied
        call_args = self.appointment_repository.find_all.call_args
        filters = call_args[1]['filters']
        assert 'start_date' in filters
        assert isinstance(filters['start_date'], datetime)
        assert 'end_date' in filters
        assert isinstance(filters['end_date'], datetime)
        assert filters['status'] == 'scheduled'
    
    def test_create_appointment_success(self):
        """Test successful appointment creation."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.beneficiary_repository.find_by_id.return_value = self.mock_beneficiary
        self.appointment_repository.create.return_value = self.mock_appointment
        
        # Test data
        appointment_data = {
            'title': 'Test Appointment',
            'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'beneficiary_id': 1
        }
        
        # Test
        result = self.service.create_appointment(
            trainer_id=1,
            appointment_data=appointment_data
        )
        
        # Verify
        assert result['title'] == 'Test Appointment'
        self.appointment_repository.create.assert_called_once()
    
    def test_create_appointment_unauthorized_role(self):
        """Test appointment creation with unauthorized role."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_student
        
        with pytest.raises(ForbiddenException) as exc:
            self.service.create_appointment(
                trainer_id=2,
                appointment_data={}
            )
        
        assert "Only trainers and admins can create appointments" in str(exc.value)
    
    def test_create_appointment_missing_fields(self):
        """Test appointment creation with missing required fields."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        
        with pytest.raises(ValidationException) as exc:
            self.service.create_appointment(
                trainer_id=1,
                appointment_data={'title': 'Test'}
            )
        
        assert "Missing required field" in str(exc.value)
    
    def test_create_appointment_invalid_dates(self):
        """Test appointment creation with invalid dates."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        
        # Test invalid date format
        with pytest.raises(ValidationException) as exc:
            self.service.create_appointment(
                trainer_id=1,
                appointment_data={
                    'title': 'Test',
                    'start_time': 'invalid-date',
                    'end_time': 'invalid-date',
                    'beneficiary_id': 1
                }
            )
        
        assert "Invalid date format" in str(exc.value)
    
    def test_create_appointment_start_after_end(self):
        """Test appointment creation with start time after end time."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        
        with pytest.raises(ValidationException) as exc:
            self.service.create_appointment(
                trainer_id=1,
                appointment_data={
                    'title': 'Test',
                    'start_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                    'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                    'beneficiary_id': 1
                }
            )
        
        assert "Start time must be before end time" in str(exc.value)
    
    def test_create_appointment_in_past(self):
        """Test appointment creation in the past."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        
        with pytest.raises(ValidationException) as exc:
            self.service.create_appointment(
                trainer_id=1,
                appointment_data={
                    'title': 'Test',
                    'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                    'end_time': datetime.utcnow().isoformat(),
                    'beneficiary_id': 1
                }
            )
        
        assert "Cannot create appointments in the past" in str(exc.value)
    
    def test_create_appointment_trainer_no_access(self):
        """Test appointment creation when trainer doesn't have access to beneficiary."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.mock_beneficiary.trainer_id = 999  # Different trainer
        self.beneficiary_repository.find_by_id.return_value = self.mock_beneficiary
        
        with pytest.raises(ForbiddenException) as exc:
            self.service.create_appointment(
                trainer_id=1,
                appointment_data={
                    'title': 'Test',
                    'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                    'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                    'beneficiary_id': 1
                }
            )
        
        assert "You do not have access to this beneficiary" in str(exc.value)
    
    def test_update_appointment_success(self):
        """Test successful appointment update."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        self.appointment_repository.update.return_value = self.mock_appointment
        
        # Test
        result = self.service.update_appointment(
            appointment_id=1,
            user_id=1,
            update_data={'title': 'Updated Title'}
        )
        
        # Verify
        assert result['id'] == 1
        self.appointment_repository.update.assert_called_once_with(
            1,
            {'title': 'Updated Title'}
        )
    
    def test_update_appointment_forbidden(self):
        """Test appointment update without permission."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.mock_appointment.trainer_id = 999  # Different trainer
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        with pytest.raises(ForbiddenException) as exc:
            self.service.update_appointment(
                appointment_id=1,
                user_id=1,
                update_data={'title': 'Updated'}
            )
        
        assert "You do not have permission to update this appointment" in str(exc.value)
    
    def test_update_appointment_invalid_status(self):
        """Test appointment update with invalid status."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        self.appointment_repository.update.return_value = self.mock_appointment
        
        # Status should be ignored if invalid
        result = self.service.update_appointment(
            appointment_id=1,
            user_id=1,
            update_data={'status': 'invalid-status'}
        )
        
        # Verify invalid status was not included in update
        call_args = self.appointment_repository.update.call_args
        assert 'status' not in call_args[0][1]
    
    def test_delete_appointment_success(self):
        """Test successful appointment deletion."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        # Test
        result = self.service.delete_appointment(
            appointment_id=1,
            user_id=1
        )
        
        # Verify
        assert result['message'] == 'Appointment deleted successfully'
        self.appointment_repository.delete.assert_called_once_with(1)
    
    def test_delete_appointment_forbidden(self):
        """Test appointment deletion without permission."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.mock_appointment.trainer_id = 999  # Different trainer
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        with pytest.raises(ForbiddenException) as exc:
            self.service.delete_appointment(
                appointment_id=1,
                user_id=1
            )
        
        assert "You do not have permission to delete this appointment" in str(exc.value)
    
    def test_delete_appointment_admin_success(self):
        """Test appointment deletion by admin."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_admin
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        # Test
        result = self.service.delete_appointment(
            appointment_id=1,
            user_id=3
        )
        
        # Verify - admin can delete any appointment
        assert result['message'] == 'Appointment deleted successfully'
        self.appointment_repository.delete.assert_called_once_with(1)
    
    @patch('app.services.appointment_service.UserIntegration')
    @patch('app.services.appointment_service.CalendarService')
    def test_delete_appointment_with_calendar_sync(self, mock_calendar_service, mock_integration):
        """Test appointment deletion with calendar sync."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.mock_appointment.calendar_event_id = 'google-event-123'
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        # Mock calendar integration
        mock_integration.query.filter_by.return_value.first.return_value = Mock(
            status='active'
        )
        
        # Test
        result = self.service.delete_appointment(
            appointment_id=1,
            user_id=1
        )
        
        # Verify calendar event was deleted
        mock_calendar_service.delete_calendar_event.assert_called_once_with(
            user_id=1,
            event_id='google-event-123'
        )
        self.appointment_repository.delete.assert_called_once_with(1)
    
    @patch('app.services.appointment_service.UserIntegration')
    @patch('app.services.appointment_service.CalendarService')
    @patch('app.services.appointment_service.send_notification_email')
    def test_sync_to_calendar_success(self, mock_send_email, mock_calendar_service, mock_integration):
        """Test successful calendar sync."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        # Mock calendar integration
        mock_integration.query.filter_by.return_value.first.return_value = Mock(
            status='active'
        )
        mock_calendar_service.create_calendar_event.return_value = 'new-event-id'
        
        # Test
        result = self.service.sync_to_calendar(
            appointment_id=1,
            user_id=1
        )
        
        # Verify
        assert result['message'] == 'Appointment synced to Google Calendar successfully'
        assert result['calendar_event_id'] == 'new-event-id'
        mock_calendar_service.create_calendar_event.assert_called_once()
        mock_send_email.assert_called_once()
    
    @patch('app.services.appointment_service.UserIntegration')
    def test_sync_to_calendar_no_integration(self, mock_integration):
        """Test calendar sync without integration."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        
        # No calendar integration
        mock_integration.query.filter_by.return_value.first.return_value = None
        
        with pytest.raises(ValidationException) as exc:
            self.service.sync_to_calendar(
                appointment_id=1,
                user_id=1
            )
        
        assert "Google Calendar not connected" in str(exc.value)
    
    def test_sync_to_calendar_forbidden(self):
        """Test calendar sync without permission."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.mock_appointment.trainer_id = 999  # Different trainer
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        with pytest.raises(ForbiddenException) as exc:
            self.service.sync_to_calendar(
                appointment_id=1,
                user_id=1
            )
        
        assert "Not authorized to sync this appointment" in str(exc.value)
    
    @patch('app.services.appointment_service.UserIntegration')
    @patch('app.services.appointment_service.CalendarService')
    def test_unsync_from_calendar_success(self, mock_calendar_service, mock_integration):
        """Test successful calendar unsync."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.mock_appointment.calendar_event_id = 'google-event-123'
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        # Mock calendar integration
        mock_integration.query.filter_by.return_value.first.return_value = Mock(
            status='active'
        )
        mock_calendar_service.delete_calendar_event.return_value = True
        
        # Test
        result = self.service.unsync_from_calendar(
            appointment_id=1,
            user_id=1
        )
        
        # Verify
        assert result['message'] == 'Appointment unsynced from Google Calendar successfully'
        mock_calendar_service.delete_calendar_event.assert_called_once()
        self.appointment_repository.update.assert_called_once_with(
            1,
            {'calendar_event_id': None}
        )
    
    def test_unsync_from_calendar_not_synced(self):
        """Test calendar unsync when appointment is not synced."""
        # Mock repository responses
        self.user_repository.find_by_id.return_value = self.mock_trainer
        self.mock_appointment.calendar_event_id = None
        self.appointment_repository.find_by_id.return_value = self.mock_appointment
        
        # Test
        result = self.service.unsync_from_calendar(
            appointment_id=1,
            user_id=1
        )
        
        # Verify
        assert result['message'] == 'Appointment is not synced to Google Calendar'