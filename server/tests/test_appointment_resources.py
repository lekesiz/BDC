"""Tests for appointment API resources."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.resources.refactored.appointment_resources import (
    AppointmentListResource,
    AppointmentResource,
    AppointmentSyncResource
)
from app.exceptions import NotFoundException, ForbiddenException, ValidationException


class TestAppointmentListResource:
    """Test suite for appointment list resource."""
    
    @pytest.fixture
    def appointment_list_resource(self):
        """Create appointment list resource instance."""
        return AppointmentListResource()
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    @patch('app.resources.refactored.appointment_resources.request')
    def test_get_appointments_success(self, mock_request, mock_get_jwt_identity, appointment_list_resource):
        """Test successful appointment list retrieval."""
        mock_get_jwt_identity.return_value = 1
        mock_request.args = {
            'page': 1,
            'per_page': 10,
            'status': 'scheduled'
        }
        
        mock_service = Mock()
        mock_service.get_appointments.return_value = {
            'appointments': [{'id': 1, 'title': 'Test'}],
            'total': 1,
            'pages': 1,
            'current_page': 1
        }
        
        response, status_code = appointment_list_resource.get(service=mock_service)
        
        assert status_code == 200
        assert response.json['appointments'][0]['id'] == 1
        mock_service.get_appointments.assert_called_once_with(
            user_id=1,
            page=1,
            per_page=10,
            start_date=None,
            end_date=None,
            status='scheduled'
        )
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    @patch('app.resources.refactored.appointment_resources.request')
    def test_create_appointment_success(self, mock_request, mock_get_jwt_identity, appointment_list_resource):
        """Test successful appointment creation."""
        mock_get_jwt_identity.return_value = 1
        mock_request.get_json.return_value = {
            'title': 'New Appointment',
            'start_time': datetime.utcnow().isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'beneficiary_id': 2
        }
        
        mock_service = Mock()
        mock_service.create_appointment.return_value = {
            'id': 1,
            'title': 'New Appointment'
        }
        
        response, status_code = appointment_list_resource.post(service=mock_service)
        
        assert status_code == 201
        assert response.json['id'] == 1
        mock_service.create_appointment.assert_called_once()
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    @patch('app.resources.refactored.appointment_resources.request')
    def test_create_appointment_no_data(self, mock_request, mock_get_jwt_identity, appointment_list_resource):
        """Test appointment creation with no data."""
        mock_get_jwt_identity.return_value = 1
        mock_request.get_json.return_value = None
        
        mock_service = Mock()
        
        response, status_code = appointment_list_resource.post(service=mock_service)
        
        assert status_code == 400
        assert 'No JSON data provided' in response.json['error']


class TestAppointmentResource:
    """Test suite for appointment resource."""
    
    @pytest.fixture
    def appointment_resource(self):
        """Create appointment resource instance."""
        return AppointmentResource()
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    def test_get_appointment_success(self, mock_get_jwt_identity, appointment_resource):
        """Test successful appointment retrieval."""
        mock_get_jwt_identity.return_value = 1
        
        mock_service = Mock()
        mock_service.get_appointments.return_value = {
            'appointments': [
                {'id': 1, 'title': 'Test 1'},
                {'id': 2, 'title': 'Test 2'}
            ],
            'total': 2,
            'pages': 1,
            'current_page': 1
        }
        
        response, status_code = appointment_resource.get(appointment_id=1, service=mock_service)
        
        assert status_code == 200
        assert response.json['id'] == 1
        assert response.json['title'] == 'Test 1'
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    def test_get_appointment_not_found(self, mock_get_jwt_identity, appointment_resource):
        """Test appointment not found."""
        mock_get_jwt_identity.return_value = 1
        
        mock_service = Mock()
        mock_service.get_appointments.return_value = {
            'appointments': [],
            'total': 0,
            'pages': 0,
            'current_page': 1
        }
        
        response, status_code = appointment_resource.get(appointment_id=999, service=mock_service)
        
        assert status_code == 404
        assert 'Appointment not found' in response.json['error']
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    @patch('app.resources.refactored.appointment_resources.request')
    def test_update_appointment_success(self, mock_request, mock_get_jwt_identity, appointment_resource):
        """Test successful appointment update."""
        mock_get_jwt_identity.return_value = 1
        mock_request.get_json.return_value = {'title': 'Updated Title'}
        
        mock_service = Mock()
        mock_service.update_appointment.return_value = {
            'id': 1,
            'title': 'Updated Title'
        }
        
        response, status_code = appointment_resource.put(appointment_id=1, service=mock_service)
        
        assert status_code == 200
        assert response.json['title'] == 'Updated Title'
        mock_service.update_appointment.assert_called_once_with(
            appointment_id=1,
            user_id=1,
            update_data={'title': 'Updated Title'}
        )
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    def test_delete_appointment_success(self, mock_get_jwt_identity, appointment_resource):
        """Test successful appointment deletion."""
        mock_get_jwt_identity.return_value = 1
        
        mock_service = Mock()
        mock_service.delete_appointment.return_value = {'message': 'Appointment deleted successfully'}
        
        response, status_code = appointment_resource.delete(appointment_id=1, service=mock_service)
        
        assert status_code == 200
        assert response.json['message'] == 'Appointment deleted successfully'
        mock_service.delete_appointment.assert_called_once_with(
            appointment_id=1,
            user_id=1
        )


class TestAppointmentSyncResource:
    """Test suite for appointment sync resource."""
    
    @pytest.fixture
    def appointment_sync_resource(self):
        """Create appointment sync resource instance."""
        return AppointmentSyncResource()
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    def test_sync_to_calendar_success(self, mock_get_jwt_identity, appointment_sync_resource):
        """Test successful calendar sync."""
        mock_get_jwt_identity.return_value = 1
        
        mock_service = Mock()
        mock_service.sync_to_calendar.return_value = {
            'message': 'Appointment synced to Google Calendar successfully',
            'calendar_event_id': 'event123'
        }
        
        response, status_code = appointment_sync_resource.post(appointment_id=1, service=mock_service)
        
        assert status_code == 200
        assert response.json['calendar_event_id'] == 'event123'
        mock_service.sync_to_calendar.assert_called_once_with(
            appointment_id=1,
            user_id=1
        )
    
    @patch('app.resources.refactored.appointment_resources.get_jwt_identity')
    def test_unsync_from_calendar_success(self, mock_get_jwt_identity, appointment_sync_resource):
        """Test successful calendar unsync."""
        mock_get_jwt_identity.return_value = 1
        
        mock_service = Mock()
        mock_service.unsync_from_calendar.return_value = {
            'message': 'Appointment unsynced from Google Calendar successfully'
        }
        
        response, status_code = appointment_sync_resource.delete(appointment_id=1, service=mock_service)
        
        assert status_code == 200
        assert 'unsynced' in response.json['message']
        mock_service.unsync_from_calendar.assert_called_once_with(
            appointment_id=1,
            user_id=1
        )