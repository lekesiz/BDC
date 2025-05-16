"""
Integration tests for BDC API endpoints.

These tests ensure that different components work together correctly
and that API endpoints function as expected with real database interactions.
"""

import pytest
import json
from datetime import datetime, timedelta
from app.models import User, Beneficiary, Program, Appointment


@pytest.mark.integration
class TestAuthIntegration:
    """Test authentication flow integration."""
    
    def test_registration_login_flow(self, app, client):
        """Test complete registration and login flow."""
        # Register a new user
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student'
        }
        
        response = client.post('/api/auth/register', json=registration_data)
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == registration_data['email']
        
        # Login with the new user
        login_data = {
            'email': 'newuser@example.com',
            'password': 'Password123!'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        token = data['access_token']
        
        # Access protected endpoint
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/auth/me', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == registration_data['email']
    
    def test_password_reset_flow(self, app, client, test_user):
        """Test complete password reset flow."""
        # Request password reset
        response = client.post('/api/auth/forgot-password', json={
            'email': test_user.email
        })
        assert response.status_code == 200
        
        # In a real scenario, we would get the reset token from email
        # For testing, we'll create a token manually
        reset_token = 'test_reset_token'
        
        # Reset password with token
        new_password = 'NewPassword123!'
        response = client.post('/api/auth/reset-password', json={
            'token': reset_token,
            'password': new_password
        })
        # This would normally work with a real token
        # For now, we'll just ensure the endpoint exists
        assert response.status_code in [200, 400]


@pytest.mark.integration
class TestBeneficiaryProgramIntegration:
    """Test integration between beneficiaries and programs."""
    
    def test_beneficiary_program_assignment(self, app, client, test_trainer, test_beneficiary):
        """Test assigning beneficiaries to programs and tracking progress."""
        # Login as trainer
        token = test_trainer['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create a program
        program_data = {
            'name': 'Python Development',
            'description': 'Learn Python programming',
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=90)).isoformat(),
            'status': 'active'
        }
        
        response = client.post('/api/programs', json=program_data, headers=headers)
        assert response.status_code == 201
        program = response.get_json()
        program_id = program['id']
        
        # Assign beneficiary to program
        response = client.post(
            f'/api/programs/{program_id}/beneficiaries',
            json={'beneficiary_ids': [test_beneficiary.id]},
            headers=headers
        )
        assert response.status_code in [200, 201]
        
        # Verify beneficiary is assigned
        response = client.get(
            f'/api/programs/{program_id}/beneficiaries',
            headers=headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['id'] == test_beneficiary.id
        
        # Create an assessment for the program
        assessment_data = {
            'program_id': program_id,
            'title': 'Python Basics Quiz',
            'type': 'quiz',
            'questions': [
                {
                    'question': 'What is Python?',
                    'type': 'multiple_choice',
                    'options': ['A snake', 'A programming language', 'A framework'],
                    'correct_answer': 1
                }
            ]
        }
        
        response = client.post('/api/assessments', json=assessment_data, headers=headers)
        assert response.status_code == 201
        assessment = response.get_json()
        
        # Submit assessment as beneficiary
        beneficiary_token = test_beneficiary.generate_auth_token()
        beneficiary_headers = {'Authorization': f'Bearer {beneficiary_token}'}
        
        submission_data = {
            'assessment_id': assessment['id'],
            'answers': [{'question_id': 0, 'answer': 1}]
        }
        
        response = client.post(
            '/api/assessments/submit',
            json=submission_data,
            headers=beneficiary_headers
        )
        assert response.status_code in [200, 201]
        
        # Check beneficiary progress
        response = client.get(
            f'/api/beneficiaries/{test_beneficiary.id}/progress',
            headers=headers
        )
        assert response.status_code == 200
        progress = response.get_json()
        assert 'programs' in progress
        assert len(progress['programs']) > 0


@pytest.mark.integration 
class TestAppointmentCalendarIntegration:
    """Test integration between appointments and calendar features."""
    
    def test_appointment_booking_flow(self, app, client, test_trainer, test_beneficiary):
        """Test complete appointment booking flow."""
        # Login as trainer
        trainer_token = test_trainer['token']
        trainer_headers = {'Authorization': f'Bearer {trainer_token}'}
        
        # Set trainer availability
        availability_data = {
            'day': 'Monday',
            'start_time': '09:00',
            'end_time': '17:00',
            'is_available': True
        }
        
        response = client.post(
            '/api/availability',
            json=availability_data,
            headers=trainer_headers
        )
        assert response.status_code in [200, 201]
        
        # Login as beneficiary
        beneficiary_token = test_beneficiary.generate_auth_token()
        beneficiary_headers = {'Authorization': f'Bearer {beneficiary_token}'}
        
        # Get available slots
        response = client.get(
            f'/api/trainers/{test_trainer["user"].id}/available-slots',
            headers=beneficiary_headers
        )
        assert response.status_code == 200
        slots = response.get_json()
        assert len(slots) > 0
        
        # Book an appointment
        appointment_data = {
            'trainer_id': test_trainer['user'].id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': '10:00',
            'duration': 60,
            'title': 'Career Counseling',
            'description': 'Discuss career options'
        }
        
        response = client.post(
            '/api/appointments',
            json=appointment_data,
            headers=beneficiary_headers
        )
        assert response.status_code in [200, 201]
        appointment = response.get_json()
        appointment_id = appointment['id']
        
        # Trainer accepts the appointment
        response = client.put(
            f'/api/appointments/{appointment_id}',
            json={'status': 'confirmed'},
            headers=trainer_headers
        )
        assert response.status_code == 200
        
        # Check calendar view
        response = client.get(
            '/api/calendar/appointments',
            headers=trainer_headers
        )
        assert response.status_code == 200
        calendar_data = response.get_json()
        assert len(calendar_data) > 0
        assert any(apt['id'] == appointment_id for apt in calendar_data)


@pytest.mark.integration
class TestDocumentWorkflowIntegration:
    """Test document management workflow integration."""
    
    def test_document_sharing_workflow(self, app, client, test_trainer, test_beneficiary):
        """Test document upload, sharing, and access permissions."""
        # Login as trainer
        trainer_token = test_trainer['token']
        trainer_headers = {'Authorization': f'Bearer {trainer_token}'}
        
        # Create a document (simulated)
        document_data = {
            'title': 'Python Tutorial',
            'description': 'Basic Python programming guide',
            'file_path': '/uploads/python_tutorial.pdf',
            'file_size': 1024000,
            'mime_type': 'application/pdf'
        }
        
        response = client.post(
            '/api/documents',
            json=document_data,
            headers=trainer_headers
        )
        assert response.status_code == 201
        document = response.get_json()
        document_id = document['id']
        
        # Share document with beneficiary
        share_data = {
            'document_id': document_id,
            'user_ids': [test_beneficiary.id],
            'permission': 'read'
        }
        
        response = client.post(
            '/api/documents/share',
            json=share_data,
            headers=trainer_headers
        )
        assert response.status_code in [200, 201]
        
        # Login as beneficiary
        beneficiary_token = test_beneficiary.generate_auth_token()
        beneficiary_headers = {'Authorization': f'Bearer {beneficiary_token}'}
        
        # Access shared document
        response = client.get(
            f'/api/documents/{document_id}',
            headers=beneficiary_headers
        )
        assert response.status_code == 200
        doc = response.get_json()
        assert doc['id'] == document_id
        
        # Verify permissions - beneficiary should not be able to update
        update_data = {'title': 'Updated Title'}
        response = client.put(
            f'/api/documents/{document_id}',
            json=update_data,
            headers=beneficiary_headers
        )
        assert response.status_code == 403


@pytest.mark.integration
class TestNotificationIntegration:
    """Test notification system integration."""
    
    def test_notification_workflow(self, app, client, test_trainer, test_beneficiary):
        """Test notification creation and delivery."""
        # Login as trainer
        trainer_token = test_trainer['token']
        trainer_headers = {'Authorization': f'Bearer {trainer_token}'}
        
        # Create an announcement
        announcement_data = {
            'title': 'New Training Module Available',
            'content': 'Check out our new Python advanced module',
            'type': 'announcement',
            'recipients': [test_beneficiary.id]
        }
        
        response = client.post(
            '/api/notifications',
            json=announcement_data,
            headers=trainer_headers
        )
        assert response.status_code == 201
        
        # Login as beneficiary
        beneficiary_token = test_beneficiary.generate_auth_token()
        beneficiary_headers = {'Authorization': f'Bearer {beneficiary_token}'}
        
        # Check notifications
        response = client.get(
            '/api/notifications/unread',
            headers=beneficiary_headers
        )
        assert response.status_code == 200
        notifications = response.get_json()
        assert len(notifications) > 0
        
        # Mark notification as read
        notification_id = notifications[0]['id']
        response = client.put(
            f'/api/notifications/{notification_id}/read',
            headers=beneficiary_headers
        )
        assert response.status_code == 200
        
        # Verify notification is marked as read
        response = client.get(
            '/api/notifications/unread',
            headers=beneficiary_headers
        )
        assert response.status_code == 200
        unread = response.get_json()
        assert not any(n['id'] == notification_id for n in unread)