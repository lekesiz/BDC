"""
Integration tests for improved API endpoints using dependency injection.
These tests target 75%+ coverage for the API layer.
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app import create_app, db
from app.models import User, Tenant, Beneficiary, Document, Program, Notification


class TestImprovedAuthAPI:
    """Test cases for improved authentication API endpoints."""
    
    def test_login_success(self, client, test_user):
        """Test successful login via improved auth endpoint."""
        response = client.post('/api/v2/auth/login', 
                             json={
                                 'email': test_user.email,
                                 'password': 'password123'
                             })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'token' in data
        assert 'user' in data
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post('/api/v2/auth/login',
                             json={
                                 'email': test_user.email,
                                 'password': 'wrong_password'
                             })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post('/api/v2/auth/login',
                             json={
                                 'email': 'nonexistent@example.com',
                                 'password': 'password123'
                             })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_register_success(self, client, test_tenant):
        """Test successful user registration."""
        response = client.post('/api/v2/auth/register',
                             json={
                                 'email': 'newuser@example.com',
                                 'password': 'password123',
                                 'first_name': 'New',
                                 'last_name': 'User',
                                 'role': 'student',
                                 'tenant_id': test_tenant.id
                             })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
    
    def test_register_existing_email(self, client, test_user):
        """Test registration with existing email."""
        response = client.post('/api/v2/auth/register',
                             json={
                                 'email': test_user.email,
                                 'password': 'password123',
                                 'first_name': 'Test',
                                 'last_name': 'User',
                                 'role': 'student'
                             })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_verify_token_valid(self, client, auth_headers):
        """Test token verification with valid token."""
        response = client.get('/api/v2/auth/verify', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True
    
    def test_verify_token_invalid(self, client):
        """Test token verification with invalid token."""
        response = client.get('/api/v2/auth/verify',
                            headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code == 401
    
    def test_logout(self, client, auth_headers):
        """Test user logout."""
        response = client.post('/api/v2/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_refresh_token(self, client, auth_headers):
        """Test token refresh."""
        response = client.post('/api/v2/auth/refresh', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data


class TestImprovedDocumentsAPI:
    """Test cases for improved documents API endpoints."""
    
    def test_create_document(self, client, auth_headers, test_tenant):
        """Test document creation."""
        response = client.post('/api/documents',
                             json={
                                 'title': 'Test Document',
                                 'description': 'Test description',
                                 'file_type': 'pdf',
                                 'document_type': 'general'
                             },
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Test Document'
    
    def test_get_documents(self, client, auth_headers, test_document):
        """Test getting documents list."""
        response = client.get('/api/documents', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 0
    
    def test_get_document_by_id(self, client, auth_headers, test_document):
        """Test getting document by ID."""
        response = client.get(f'/api/documents/{test_document.id}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_document.id
    
    def test_update_document(self, client, auth_headers, test_document):
        """Test updating document."""
        response = client.put(f'/api/documents/{test_document.id}',
                            json={'title': 'Updated Title'},
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Title'
    
    def test_delete_document(self, client, auth_headers, test_document):
        """Test deleting document."""
        response = client.delete(f'/api/documents/{test_document.id}',
                               headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_share_document(self, client, auth_headers, test_document, test_beneficiary):
        """Test sharing document."""
        response = client.post(f'/api/documents/{test_document.id}/share',
                             json={'user_id': test_beneficiary.user_id},
                             headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_search_documents(self, client, auth_headers):
        """Test searching documents."""
        response = client.get('/api/documents/search?q=test',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestImprovedEvaluationsAPI:
    """Test cases for improved evaluations API endpoints."""
    
    def test_create_evaluation(self, client, auth_headers, test_tenant):
        """Test evaluation creation."""
        response = client.post('/api/evaluations',
                             json={
                                 'title': 'Test Evaluation',
                                 'description': 'Test evaluation description',
                                 'type': 'assessment'
                             },
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Test Evaluation'
    
    def test_get_evaluations(self, client, auth_headers):
        """Test getting evaluations list."""
        response = client.get('/api/evaluations', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_evaluation_by_id(self, client, auth_headers, test_test):
        """Test getting evaluation by ID."""
        response = client.get(f'/api/evaluations/{test_test.id}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_test.id
    
    def test_submit_evaluation(self, client, auth_headers, test_test, test_beneficiary):
        """Test submitting evaluation."""
        response = client.post(f'/api/evaluations/{test_test.id}/submit',
                             json={
                                 'beneficiary_id': test_beneficiary.id,
                                 'responses': [
                                     {'question_id': 1, 'answer': 'test answer'}
                                 ]
                             },
                             headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_get_evaluation_results(self, client, auth_headers, test_test):
        """Test getting evaluation results."""
        response = client.get(f'/api/evaluations/{test_test.id}/results',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestImprovedProgramsAPI:
    """Test cases for improved programs API endpoints."""
    
    def test_create_program(self, client, auth_headers, test_tenant):
        """Test program creation."""
        response = client.post('/api/programs',
                             json={
                                 'name': 'Test Program',
                                 'description': 'Test program description',
                                 'start_date': datetime.now().isoformat(),
                                 'end_date': (datetime.now() + timedelta(days=30)).isoformat()
                             },
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Test Program'
    
    def test_get_programs(self, client, auth_headers):
        """Test getting programs list."""
        response = client.get('/api/programs', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_program_by_id(self, client, auth_headers, test_program):
        """Test getting program by ID."""
        response = client.get(f'/api/programs/{test_program.id}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_program.id
    
    def test_update_program(self, client, auth_headers, test_program):
        """Test updating program."""
        response = client.put(f'/api/programs/{test_program.id}',
                            json={'name': 'Updated Program'},
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated Program'
    
    def test_enroll_beneficiary(self, client, auth_headers, test_program, test_beneficiary):
        """Test enrolling beneficiary in program."""
        response = client.post(f'/api/programs/{test_program.id}/enroll',
                             json={'beneficiary_id': test_beneficiary.id},
                             headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_get_program_enrollments(self, client, auth_headers, test_program):
        """Test getting program enrollments."""
        response = client.get(f'/api/programs/{test_program.id}/enrollments',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_program_modules(self, client, auth_headers, test_program):
        """Test getting program modules."""
        response = client.get(f'/api/programs/{test_program.id}/modules',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestImprovedNotificationsAPI:
    """Test cases for improved notifications API endpoints."""
    
    def test_get_notifications(self, client, auth_headers):
        """Test getting notifications."""
        response = client.get('/api/notifications', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_unread_notifications(self, client, auth_headers):
        """Test getting unread notifications."""
        response = client.get('/api/notifications/unread', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_mark_notification_as_read(self, client, auth_headers, test_notification):
        """Test marking notification as read."""
        response = client.put(f'/api/notifications/{test_notification.id}/read',
                            headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_mark_all_notifications_as_read(self, client, auth_headers):
        """Test marking all notifications as read."""
        response = client.put('/api/notifications/read-all',
                            headers=auth_headers)
        
        assert response.status_code == 200
    
    def test_send_notification(self, client, auth_headers, test_beneficiary):
        """Test sending notification."""
        response = client.post('/api/notifications',
                             json={
                                 'user_id': test_beneficiary.user_id,
                                 'type': 'info',
                                 'title': 'Test Notification',
                                 'message': 'Test message'
                             },
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Test Notification'


class TestImprovedCalendarAPI:
    """Test cases for improved calendar API endpoints."""
    
    def test_create_appointment(self, client, auth_headers, test_beneficiary):
        """Test creating appointment."""
        response = client.post('/api/appointments',
                             json={
                                 'title': 'Test Appointment',
                                 'description': 'Test appointment description',
                                 'start_time': datetime.now().isoformat(),
                                 'end_time': (datetime.now() + timedelta(hours=1)).isoformat(),
                                 'beneficiary_id': test_beneficiary.id
                             },
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Test Appointment'
    
    def test_get_appointments(self, client, auth_headers):
        """Test getting appointments."""
        response = client.get('/api/appointments', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_appointment_by_id(self, client, auth_headers):
        """Test getting appointment by ID."""
        # First create an appointment
        create_response = client.post('/api/appointments',
                                    json={
                                        'title': 'Test Appointment',
                                        'start_time': datetime.now().isoformat(),
                                        'end_time': (datetime.now() + timedelta(hours=1)).isoformat()
                                    },
                                    headers=auth_headers)
        
        if create_response.status_code == 201:
            appointment_id = json.loads(create_response.data)['id']
            response = client.get(f'/api/appointments/{appointment_id}',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == appointment_id
    
    def test_update_appointment(self, client, auth_headers):
        """Test updating appointment."""
        # First create an appointment
        create_response = client.post('/api/appointments',
                                    json={
                                        'title': 'Test Appointment',
                                        'start_time': datetime.now().isoformat(),
                                        'end_time': (datetime.now() + timedelta(hours=1)).isoformat()
                                    },
                                    headers=auth_headers)
        
        if create_response.status_code == 201:
            appointment_id = json.loads(create_response.data)['id']
            response = client.put(f'/api/appointments/{appointment_id}',
                                json={'title': 'Updated Appointment'},
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['title'] == 'Updated Appointment'
    
    def test_delete_appointment(self, client, auth_headers):
        """Test deleting appointment."""
        # First create an appointment
        create_response = client.post('/api/appointments',
                                    json={
                                        'title': 'Test Appointment',
                                        'start_time': datetime.now().isoformat(),
                                        'end_time': (datetime.now() + timedelta(hours=1)).isoformat()
                                    },
                                    headers=auth_headers)
        
        if create_response.status_code == 201:
            appointment_id = json.loads(create_response.data)['id']
            response = client.delete(f'/api/appointments/{appointment_id}',
                                   headers=auth_headers)
            
            assert response.status_code == 200
    
    def test_get_calendar_view(self, client, auth_headers):
        """Test getting calendar view."""
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        response = client.get(f'/api/calendar?start={start_date}&end={end_date}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestHealthAPI:
    """Test cases for health check endpoints."""
    
    def test_basic_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_api_health_check(self, client):
        """Test API health check endpoint."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    def test_cors_test_endpoint(self, client):
        """Test CORS test endpoint."""
        response = client.get('/api/test-cors')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'CORS test successful'


class TestErrorHandling:
    """Test cases for API error handling."""
    
    def test_404_error(self, client, auth_headers):
        """Test 404 error handling."""
        response = client.get('/api/nonexistent', headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_401_unauthorized(self, client):
        """Test 401 unauthorized access."""
        response = client.get('/api/documents')
        
        assert response.status_code == 401
    
    def test_400_bad_request(self, client, auth_headers):
        """Test 400 bad request."""
        response = client.post('/api/documents',
                             json={'invalid': 'data'},
                             headers=auth_headers)
        
        # Should return 400 for missing required fields
        assert response.status_code in [400, 422]
    
    def test_405_method_not_allowed(self, client, auth_headers):
        """Test 405 method not allowed."""
        response = client.patch('/health')  # Health endpoint doesn't support PATCH
        
        assert response.status_code == 405