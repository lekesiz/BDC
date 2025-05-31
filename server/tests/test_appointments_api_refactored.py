"""Tests for the refactored appointments API endpoints."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.exceptions import NotFoundException, ForbiddenException, ValidationException


@pytest.fixture
def mock_appointment_service():
    """Create a mock appointment service."""
    return Mock()


class TestAppointmentsAPIRefactored:
    """Test suite for refactored appointments API endpoints."""
    
    def test_get_appointments_success(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test successful get appointments."""
        # Mock the service
        mock_result = {
            'appointments': [
                {
                    'id': 1,
                    'title': 'Test Appointment',
                    'start_time': datetime.utcnow().isoformat(),
                    'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat()
                }
            ],
            'total': 1,
            'pages': 1,
            'current_page': 1
        }
        mock_appointment_service.get_appointments.return_value = mock_result
        
        # Patch the container to return our mock
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Make request
        response = client.get(
            '/api/appointments',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert len(data['appointments']) == 1
        
        # Verify service was called correctly
        mock_appointment_service.get_appointments.assert_called_once()
        call_args = mock_appointment_service.get_appointments.call_args
        assert call_args[1]['user_id'] == 1  # trainer user ID
        assert call_args[1]['page'] == 1
        assert call_args[1]['per_page'] == 10
    
    def test_get_appointments_with_filters(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test get appointments with filters."""
        # Mock the service
        mock_appointment_service.get_appointments.return_value = {
            'appointments': [],
            'total': 0,
            'pages': 0,
            'current_page': 1
        }
        
        # Patch the container
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Make request with filters
        response = client.get(
            '/api/appointments?start_date=2024-01-01&end_date=2024-01-31&status=scheduled&page=2',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify service was called with filters
        call_args = mock_appointment_service.get_appointments.call_args
        assert call_args[1]['start_date'] == '2024-01-01'
        assert call_args[1]['end_date'] == '2024-01-31'
        assert call_args[1]['status'] == 'scheduled'
        assert call_args[1]['page'] == 2
    
    def test_create_appointment_success(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test successful appointment creation."""
        # Mock the service
        created_appointment = {
            'id': 1,
            'title': 'New Appointment',
            'beneficiary_id': 1
        }
        mock_appointment_service.create_appointment.return_value = created_appointment
        
        # Patch the container
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Appointment data
        appointment_data = {
            'title': 'New Appointment',
            'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'beneficiary_id': 1
        }
        
        # Make request
        response = client.post(
            '/api/appointments',
            json=appointment_data,
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['id'] == 1
        assert data['title'] == 'New Appointment'
        
        # Verify service was called
        mock_appointment_service.create_appointment.assert_called_once_with(
            trainer_id=1,
            appointment_data=appointment_data
        )
    
    def test_create_appointment_validation_error(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test create appointment with validation error."""
        # Mock the service to raise validation error
        mock_appointment_service.create_appointment.side_effect = ValidationException("Invalid date format")
        
        # Patch the container
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Make request
        response = client.post(
            '/api/appointments',
            json={'title': 'Test'},
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'ValidationException'
        assert data['message'] == 'Invalid date format'
    
    def test_update_appointment_success(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test successful appointment update."""
        # Mock the service
        updated_appointment = {
            'id': 1,
            'title': 'Updated Appointment'
        }
        mock_appointment_service.update_appointment.return_value = updated_appointment
        
        # Patch the container
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Update data
        update_data = {'title': 'Updated Appointment'}
        
        # Make request
        response = client.put(
            '/api/appointments/1',
            json=update_data,
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Updated Appointment'
        
        # Verify service was called
        mock_appointment_service.update_appointment.assert_called_once_with(
            appointment_id=1,
            user_id=1,
            update_data=update_data
        )
    
    def test_update_appointment_forbidden(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test update appointment without permission."""
        # Mock the service to raise forbidden error
        mock_appointment_service.update_appointment.side_effect = ForbiddenException(
            "You do not have permission to update this appointment"
        )
        
        # Patch the container
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Make request
        response = client.put(
            '/api/appointments/1',
            json={'title': 'Updated'},
            headers={'Authorization': f'Bearer {auth_tokens["student"]}'}
        )
        
        # Assert
        assert response.status_code == 403
        data = response.get_json()
        assert data['error'] == 'ForbiddenException'
    
    def test_delete_appointment_success(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test successful appointment deletion."""
        # Mock the service
        mock_appointment_service.delete_appointment.return_value = {
            'message': 'Appointment deleted successfully'
        }
        
        # Patch the container
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Make request
        response = client.delete(
            '/api/appointments/1',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Appointment deleted successfully'
        
        # Verify service was called
        mock_appointment_service.delete_appointment.assert_called_once_with(
            appointment_id=1,
            user_id=1
        )
    
    def test_sync_appointment_to_calendar_success(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test successful sync to calendar."""
        # Mock the service
        mock_appointment_service.sync_to_calendar.return_value = {
            'message': 'Appointment synced to Google Calendar successfully',
            'calendar_event_id': 'google-event-123'
        }
        
        # Patch the container
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Make request
        response = client.post(
            '/api/appointments/1/sync',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Appointment synced to Google Calendar successfully'
        assert data['calendar_event_id'] == 'google-event-123'
    
    def test_unsync_appointment_from_calendar_success(self, client, auth_tokens, mock_appointment_service, monkeypatch):
        """Test successful unsync from calendar."""
        # Mock the service
        mock_appointment_service.unsync_from_calendar.return_value = {
            'message': 'Appointment unsynced from Google Calendar successfully'
        }
        
        # Patch the container
        def mock_resolve(service_name):
            if service_name == 'appointment_service':
                return mock_appointment_service
            return Mock()
        
        monkeypatch.setattr('app.container.container.resolve', mock_resolve)
        
        # Make request
        response = client.post(
            '/api/appointments/1/unsync',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Appointment unsynced from Google Calendar successfully'
    
    @patch('app.api.appointments_refactored.CalendarService')
    def test_authorize_google_calendar(self, mock_calendar_service, client, auth_tokens):
        """Test Google Calendar authorization."""
        # Mock the service
        mock_calendar_service.get_authorization_url.return_value = 'https://accounts.google.com/oauth/authorize'
        
        # Make request
        response = client.get(
            '/api/calendar/authorize',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['authorization_url'] == 'https://accounts.google.com/oauth/authorize'
    
    @patch('app.api.appointments_refactored.CalendarService')
    @patch('app.models.integration.UserIntegration')
    def test_oauth2_callback(self, mock_integration, mock_calendar_service, client):
        """Test OAuth2 callback handling."""
        # Mock integration
        integration = Mock()
        integration.user_id = 1
        mock_integration.query.filter_by.return_value.first.return_value = integration
        
        # Mock calendar service
        mock_calendar_service.handle_callback.return_value = True
        
        # Make request
        response = client.get('/api/calendar/callback?code=test-code&state=test-state')
        
        # Assert
        assert response.status_code == 302  # Redirect
        assert 'success=true' in response.location
    
    @patch('app.models.integration.UserIntegration')
    def test_get_calendar_integration_status(self, mock_integration, client, auth_tokens):
        """Test get calendar integration status."""
        # Mock integration
        integration = Mock()
        integration.status = 'active'
        integration.updated_at = datetime.utcnow()
        mock_integration.query.filter_by.return_value.first.return_value = integration
        
        # Make request
        response = client.get(
            '/api/calendar/status',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'active'
        assert 'connected_at' in data
    
    def test_get_calendar_integration_status_not_connected(self, client, auth_tokens):
        """Test get calendar integration status when not connected."""
        # Make request
        response = client.get(
            '/api/calendar/status',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'not_connected'
    
    @patch('app.models.integration.UserIntegration')
    def test_disconnect_google_calendar(self, mock_integration, client, auth_tokens):
        """Test disconnect Google Calendar."""
        # Mock integration
        integration = Mock()
        mock_integration.query.filter_by.return_value.first.return_value = integration
        
        # Make request
        response = client.post(
            '/api/calendar/disconnect',
            headers={'Authorization': f'Bearer {auth_tokens["trainer"]}'}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Google Calendar disconnected successfully'