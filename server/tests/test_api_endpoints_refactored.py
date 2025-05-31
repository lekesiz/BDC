"""API endpoint tests for refactored services."""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.services.appointment_service_refactored import AppointmentServiceRefactored
from app.services.evaluation_service_refactored import (
    EvaluationServiceRefactored,
    PaginationResult
)
from app.exceptions import NotFoundException, ForbiddenException, ValidationException


class TestAppointmentAPI:
    """Test appointment API endpoints."""
    
    @patch('app.api.appointments.appointment_service')
    @patch('app.api.appointments.get_jwt_identity')
    def test_get_appointments_success(self, mock_jwt_identity, mock_service, client):
        """Test successful retrieval of appointments."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.get_appointments_for_user.return_value = {
            'appointments': [
                {
                    'id': 1,
                    'title': 'Test Appointment',
                    'start_time': datetime.utcnow().isoformat(),
                    'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                    'status': 'scheduled'
                }
            ],
            'total': 1,
            'pages': 1,
            'current_page': 1
        }
        
        # Make request
        response = client.get('/api/appointments', headers={'Authorization': 'Bearer fake-token'})
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        assert len(data['appointments']) == 1
        assert data['appointments'][0]['title'] == 'Test Appointment'
    
    @patch('app.api.appointments.appointment_service')
    @patch('app.api.appointments.get_jwt_identity')
    def test_get_appointments_not_found(self, mock_jwt_identity, mock_service, client):
        """Test appointments not found error."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.get_appointments_for_user.side_effect = NotFoundException("User not found")
        
        # Make request
        response = client.get('/api/appointments', headers={'Authorization': 'Bearer fake-token'})
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'not_found'
    
    @patch('app.api.appointments.appointment_service')
    @patch('app.api.appointments.get_jwt_identity')
    def test_create_appointment_success(self, mock_jwt_identity, mock_service, client):
        """Test successful appointment creation."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.create_appointment.return_value = {
            'id': 1,
            'title': 'New Appointment',
            'status': 'scheduled'
        }
        
        # Request data
        appointment_data = {
            'title': 'New Appointment',
            'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'beneficiary_id': 10
        }
        
        # Make request
        response = client.post(
            '/api/appointments',
            json=appointment_data,
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['id'] == 1
        assert data['title'] == 'New Appointment'
    
    @patch('app.api.appointments.appointment_service')
    @patch('app.api.appointments.get_jwt_identity')
    def test_update_appointment_success(self, mock_jwt_identity, mock_service, client):
        """Test successful appointment update."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.update_appointment.return_value = {
            'id': 1,
            'title': 'Updated Appointment',
            'status': 'completed'
        }
        
        # Update data
        update_data = {
            'title': 'Updated Appointment',
            'status': 'completed'
        }
        
        # Make request
        response = client.put(
            '/api/appointments/1',
            json=update_data,
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Appointment'
        assert data['status'] == 'completed'
    
    @patch('app.api.appointments.appointment_service')
    @patch('app.api.appointments.get_jwt_identity')
    def test_delete_appointment_success(self, mock_jwt_identity, mock_service, client):
        """Test successful appointment deletion."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.delete_appointment.return_value = {'message': 'Appointment deleted successfully'}
        
        # Make request
        response = client.delete(
            '/api/appointments/1',
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Appointment deleted successfully'
    
    @patch('app.api.appointments.appointment_service')
    @patch('app.api.appointments.get_jwt_identity')
    def test_appointment_validation_error(self, mock_jwt_identity, mock_service, client):
        """Test appointment validation error."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.create_appointment.side_effect = ValidationException("Invalid date format")
        
        # Invalid data
        appointment_data = {
            'title': 'Invalid Appointment',
            'start_time': 'invalid-date',
            'end_time': 'invalid-date',
            'beneficiary_id': 10
        }
        
        # Make request
        response = client.post(
            '/api/appointments',
            json=appointment_data,
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'validation_error'


class TestEvaluationAPI:
    """Test evaluation API endpoints."""
    
    @patch('app.api.evaluations.evaluation_service')
    @patch('app.api.evaluations.get_jwt_identity')
    def test_get_evaluations_success(self, mock_jwt_identity, mock_service, client):
        """Test successful retrieval of evaluations."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_result = PaginationResult(
            items=[
                {
                    'id': 1,
                    'title': 'Test Evaluation',
                    'type': 'assessment',
                    'status': 'published'
                }
            ],
            total=1,
            pages=1,
            current_page=1
        )
        mock_service.get_evaluations.return_value = mock_result
        
        # Make request
        response = client.get('/api/evaluations', headers={'Authorization': 'Bearer fake-token'})
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        assert len(data['items']) == 1
        assert data['items'][0]['title'] == 'Test Evaluation'
    
    @patch('app.api.evaluations.evaluation_service')
    @patch('app.api.evaluations.get_jwt_identity')
    def test_create_evaluation_success(self, mock_jwt_identity, mock_service, client):
        """Test successful evaluation creation."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_evaluation = Mock()
        mock_evaluation.to_dict.return_value = {
            'id': 1,
            'title': 'New Evaluation',
            'type': 'quiz',
            'status': 'draft'
        }
        mock_service.create_evaluation.return_value = mock_evaluation
        
        # Request data
        evaluation_data = {
            'title': 'New Evaluation',
            'type': 'quiz',
            'tenant_id': 1,
            'questions': [
                {
                    'text': 'Sample question?',
                    'type': 'multiple_choice',
                    'options': ['A', 'B', 'C'],
                    'correct_answer': 'A'
                }
            ]
        }
        
        # Make request
        response = client.post(
            '/api/evaluations',
            json=evaluation_data,
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['id'] == 1
        assert data['title'] == 'New Evaluation'
    
    @patch('app.api.evaluations.evaluation_service')
    @patch('app.api.evaluations.get_jwt_identity')
    def test_create_test_session_success(self, mock_jwt_identity, mock_service, client):
        """Test successful test session creation."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_session = Mock()
        mock_session.to_dict.return_value = {
            'id': 100,
            'test_set_id': 1,
            'status': 'in_progress',
            'started_at': datetime.utcnow().isoformat()
        }
        mock_service.create_test_session.return_value = mock_session
        
        # Make request
        response = client.post(
            '/api/evaluations/1/sessions',
            json={},
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['id'] == 100
        assert data['status'] == 'in_progress'
    
    @patch('app.api.evaluations.evaluation_service')
    @patch('app.api.evaluations.get_jwt_identity')
    def test_submit_response_success(self, mock_jwt_identity, mock_service, client):
        """Test successful response submission."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_response = Mock()
        mock_response.to_dict.return_value = {
            'id': 1,
            'question_id': 10,
            'answer': 'A',
            'is_correct': True,
            'score': 10
        }
        mock_service.submit_response.return_value = mock_response
        
        # Request data
        response_data = {
            'answer': 'A'
        }
        
        # Make request
        response = client.post(
            '/api/sessions/100/questions/10/response',
            json=response_data,
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['answer'] == 'A'
        assert data['is_correct'] is True
    
    @patch('app.api.evaluations.evaluation_service')
    @patch('app.api.evaluations.get_jwt_identity')
    def test_complete_session_success(self, mock_jwt_identity, mock_service, client):
        """Test successful session completion."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_session = Mock()
        mock_session.to_dict.return_value = {
            'id': 100,
            'status': 'completed',
            'score': 80,
            'total_score': 100,
            'completed_at': datetime.utcnow().isoformat()
        }
        mock_service.complete_session.return_value = mock_session
        
        # Make request
        response = client.post(
            '/api/sessions/100/complete',
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'completed'
        assert data['score'] == 80
        assert data['total_score'] == 100
    
    @patch('app.api.evaluations.evaluation_service')
    @patch('app.api.evaluations.get_jwt_identity')
    def test_evaluation_forbidden_error(self, mock_jwt_identity, mock_service, client):
        """Test evaluation forbidden error."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.create_evaluation.side_effect = ForbiddenException("You do not have permission")
        
        # Request data
        evaluation_data = {
            'title': 'Forbidden Evaluation',
            'type': 'quiz',
            'tenant_id': 1
        }
        
        # Make request
        response = client.post(
            '/api/evaluations',
            json=evaluation_data,
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['error'] == 'forbidden'


class TestCalendarIntegration:
    """Test calendar integration endpoints."""
    
    @patch('app.api.appointments.appointment_service')
    @patch('app.api.appointments.get_jwt_identity')
    def test_sync_to_calendar_success(self, mock_jwt_identity, mock_service, client):
        """Test successful calendar sync."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.sync_to_calendar.return_value = {
            'message': 'Appointment synced to Google Calendar successfully',
            'calendar_event_id': 'google_event_123'
        }
        
        # Make request
        response = client.post(
            '/api/appointments/1/sync',
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'synced to Google Calendar' in data['message']
        assert data['calendar_event_id'] == 'google_event_123'
    
    @patch('app.api.appointments.appointment_service')
    @patch('app.api.appointments.get_jwt_identity')
    def test_unsync_from_calendar_success(self, mock_jwt_identity, mock_service, client):
        """Test successful calendar unsync."""
        # Setup mocks
        mock_jwt_identity.return_value = 1
        mock_service.unsync_from_calendar.return_value = {
            'message': 'Appointment unsynced from Google Calendar successfully'
        }
        
        # Make request
        response = client.delete(
            '/api/appointments/1/sync',
            headers={'Authorization': 'Bearer fake-token'}
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'unsynced from Google Calendar' in data['message']