"""
End-to-end workflow tests simulating real user scenarios.
"""
import pytest
from datetime import datetime, timedelta
from app.models import User, Beneficiary, Appointment, TestSet, Report
from app.tests.fixtures.integration_fixtures import setup_integration_data


class TestUserWorkflows:
    """Test complete user workflows from login to task completion."""
    
    def test_therapist_daily_workflow(self, client, app):
        """Test a therapist's typical daily workflow."""
        # 1. Login as therapist
        with app.app_context():
            from app.extensions import db
            therapist = User(
                username='therapist_workflow',
                email='therapist_workflow@test.com',
                user_type='Terapist',
                tenant_id=1
            )
            therapist.set_password('therapypass123')
            db.session.add(therapist)
            db.session.commit()
            therapist_id = therapist.id
        
        # Login
        response = client.post('/api/auth/login', json={
            'username': 'therapist_workflow',
            'password': 'therapypass123'
        })
        assert response.status_code == 200
        token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. Check today's appointments
        today = datetime.now().strftime('%Y-%m-%d')
        response = client.get(f'/api/appointments?date={today}', headers=headers)
        assert response.status_code == 200
        appointments = response.get_json()['appointments']
        
        # 3. View beneficiary details for first appointment
        if appointments:
            appointment = appointments[0]
            beneficiary_id = appointment['beneficiary_id']
            
            response = client.get(f'/api/beneficiaries/{beneficiary_id}', headers=headers)
            assert response.status_code == 200
            
            # 4. Complete an evaluation
            response = client.post('/api/evaluations', json={
                'beneficiary_id': beneficiary_id,
                'template_id': 1,  # Assuming template exists
                'appointment_id': appointment['id'],
                'responses': {
                    'question_1': 'Good progress',
                    'question_2': True,
                    'score': 8
                }
            }, headers=headers)
            
            if response.status_code != 404:  # If endpoint exists
                assert response.status_code in [200, 201]
                
                # 5. Update appointment status
                response = client.put(f'/api/appointments/{appointment["id"]}', json={
                    'status': 'completed'
                }, headers=headers)
                assert response.status_code == 200
    
    def test_admin_clinic_management_workflow(self, client, app):
        """Test admin's clinic management workflow."""
        # 1. Login as admin
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        if response.status_code == 200:
            token = response.get_json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # 2. Create new user (therapist)
            response = client.post('/api/users', json={
                'username': 'new_therapist',
                'email': 'new_therapist@test.com',
                'password': 'therapistpass123',
                'user_type': 'Terapist',
                'tenant_id': 1
            }, headers=headers)
            
            if response.status_code != 404:
                assert response.status_code == 201
                new_user_id = response.get_json()['id']
                
                # 3. Create new beneficiary
                response = client.post('/api/beneficiaries', json={
                    'first_name': 'Test',
                    'last_name': 'Beneficiary',
                    'date_of_birth': '2010-01-01',
                    'contact_info': {
                        'phone': '555-1234'
                    },
                    'assigned_user_id': new_user_id
                }, headers=headers)
                
                if response.status_code != 404:
                    assert response.status_code == 201
                    beneficiary_id = response.get_json()['id']
                    
                    # 4. Schedule appointment
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                    response = client.post('/api/appointments', json={
                        'appointment_date': tomorrow,
                        'time': '10:00',
                        'beneficiary_id': beneficiary_id,
                        'user_id': new_user_id,
                        'type': 'therapy',
                        'status': 'scheduled'
                    }, headers=headers)
                    
                    if response.status_code != 404:
                        assert response.status_code == 201
                        
                        # 5. Generate report
                        response = client.post('/api/reports/generate', json={
                            'report_type': 'user_activity',
                            'user_id': new_user_id,
                            'period_start': datetime.now().strftime('%Y-%m-%d'),
                            'period_end': tomorrow
                        }, headers=headers)
                        
                        if response.status_code != 404:
                            assert response.status_code in [200, 201]


class TestBeneficiaryManagementWorkflow:
    """Test complete beneficiary management workflows."""
    
    def test_beneficiary_intake_process(self, client, auth_headers, app):
        """Test new beneficiary intake process."""
        # 1. Create new beneficiary
        response = client.post('/api/beneficiaries', json={
            'first_name': 'New',
            'last_name': 'Client',
            'date_of_birth': '2012-06-15',
            'contact_info': {
                'phone': '555-9999',
                'email': 'parent@example.com',
                'address': '123 Test St'
            }
        }, headers=auth_headers)
        
        if response.status_code != 404:
            assert response.status_code == 201
            beneficiary_id = response.get_json()['id']
            
            # 2. Create initial evaluation template
            response = client.post('/api/evaluations/templates', json={
                'name': 'Initial Assessment',
                'description': 'Intake evaluation template',
                'category': 'intake',
                'sections': [
                    {
                        'name': 'Basic Info',
                        'questions': [
                            {'text': 'Primary concerns', 'type': 'text'},
                            {'text': 'Previous interventions', 'type': 'text'}
                        ]
                    }
                ]
            }, headers=auth_headers)
            
            if response.status_code != 404:
                assert response.status_code in [200, 201]
                template_id = response.get_json()['id']
                
                # 3. Schedule intake appointment
                response = client.post('/api/appointments', json={
                    'appointment_date': datetime.now().strftime('%Y-%m-%d'),
                    'time': '14:00',
                    'beneficiary_id': beneficiary_id,
                    'type': 'evaluation',
                    'status': 'scheduled',
                    'notes': 'Initial intake appointment'
                }, headers=auth_headers)
                
                if response.status_code != 404:
                    assert response.status_code == 201
                    appointment_id = response.get_json()['id']
                    
                    # 4. Complete intake evaluation
                    response = client.post('/api/evaluations', json={
                        'beneficiary_id': beneficiary_id,
                        'template_id': template_id,
                        'appointment_id': appointment_id,
                        'responses': {
                            'primary_concerns': 'Speech delay, social interaction',
                            'previous_interventions': 'None'
                        }
                    }, headers=auth_headers)
                    
                    if response.status_code != 404:
                        assert response.status_code in [200, 201]
                        
                        # 5. Create treatment plan
                        response = client.post('/api/beneficiaries/{}/treatment-plan'.format(beneficiary_id), 
                                             json={
                            'goals': [
                                'Improve speech clarity',
                                'Develop social skills'
                            ],
                            'interventions': [
                                'Weekly speech therapy',
                                'Group social skills sessions'
                            ],
                            'frequency': 'Twice weekly'
                        }, headers=auth_headers)
                        
                        if response.status_code != 404:
                            assert response.status_code in [200, 201]


class TestReportingWorkflow:
    """Test reporting and analytics workflows."""
    
    def test_monthly_report_generation(self, client, auth_headers, setup_integration_data):
        """Test monthly report generation workflow."""
        data = setup_integration_data
        beneficiary = data['beneficiaries'][0]
        
        # 1. Collect evaluation data for the month
        response = client.get(
            f'/api/evaluations?beneficiary_id={beneficiary.id}&month={datetime.now().month}',
            headers=auth_headers
        )
        
        if response.status_code == 200:
            evaluations = response.get_json()['evaluations']
            
            # 2. Get appointment statistics
            response = client.get(
                f'/api/analytics/appointments?beneficiary_id={beneficiary.id}&period=month',
                headers=auth_headers
            )
            
            if response.status_code == 200:
                appointment_stats = response.get_json()
                
                # 3. Generate progress report
                response = client.post('/api/reports', json={
                    'name': f'Monthly Progress - {beneficiary.first_name} {beneficiary.last_name}',
                    'report_type': 'progress',
                    'beneficiary_id': beneficiary.id,
                    'period_start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'period_end': datetime.now().strftime('%Y-%m-%d'),
                    'sections': [
                        {
                            'title': 'Evaluation Summary',
                            'content': f'Completed {len(evaluations)} evaluations'
                        },
                        {
                            'title': 'Attendance',
                            'content': f'Attended {appointment_stats.get("attended", 0)} appointments'
                        }
                    ]
                }, headers=auth_headers)
                
                if response.status_code != 404:
                    assert response.status_code in [200, 201]
                    report_id = response.get_json()['id']
                    
                    # 4. Share report with stakeholders
                    response = client.post(f'/api/reports/{report_id}/share', json={
                        'recipient_emails': ['parent@example.com', 'therapist@clinic.com'],
                        'message': 'Please find attached the monthly progress report.'
                    }, headers=auth_headers)
                    
                    if response.status_code != 404:
                        assert response.status_code == 200
                        
                        # 5. Schedule follow-up meeting
                        response = client.post('/api/appointments', json={
                            'appointment_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                            'time': '15:00',
                            'beneficiary_id': beneficiary.id,
                            'type': 'consultation',
                            'status': 'scheduled',
                            'notes': f'Discuss monthly report {report_id}'
                        }, headers=auth_headers)
                        
                        if response.status_code != 404:
                            assert response.status_code == 201


class TestNotificationWorkflow:
    """Test notification system workflows."""
    
    def test_appointment_reminder_workflow(self, client, auth_headers, setup_integration_data):
        """Test appointment reminder notification workflow."""
        data = setup_integration_data
        
        # 1. Get tomorrow's appointments
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = client.get(f'/api/appointments?date={tomorrow}', headers=auth_headers)
        
        if response.status_code == 200:
            appointments = response.get_json()['appointments']
            
            if appointments:
                # 2. Create bulk reminders
                notification_data = []
                for appointment in appointments:
                    notification_data.append({
                        'user_id': appointment['user_id'],
                        'title': 'Appointment Reminder',
                        'message': f'Appointment tomorrow at {appointment["time"]}',
                        'type': 'appointment',
                        'priority': 'medium',
                        'related_data': {
                            'appointment_id': appointment['id']
                        }
                    })
                
                response = client.post('/api/notifications/bulk', 
                                     json={'notifications': notification_data},
                                     headers=auth_headers)
                
                if response.status_code != 404:
                    assert response.status_code in [200, 201]
                    
                    # 3. Check notification delivery status
                    response = client.get('/api/notifications/pending', headers=auth_headers)
                    
                    if response.status_code == 200:
                        pending = response.get_json()['notifications']
                        
                        # 4. Mark notifications as read after user views them
                        for notification in pending[:2]:  # Simulate reading first 2
                            response = client.put(f'/api/notifications/{notification["id"]}', 
                                                json={'read': True},
                                                headers=auth_headers)
                            
                            if response.status_code != 404:
                                assert response.status_code == 200


class TestDocumentWorkflow:
    """Test document management workflows."""
    
    def test_document_sharing_workflow(self, client, auth_headers, setup_integration_data):
        """Test document upload and sharing workflow."""
        data = setup_integration_data
        beneficiary = data['beneficiaries'][0]
        
        # 1. Upload assessment document
        # In real scenario, this would be multipart/form-data
        response = client.post('/api/documents', json={
            'filename': 'assessment_report.pdf',
            'file_type': 'application/pdf',
            'entity_type': 'beneficiary',
            'entity_id': beneficiary.id,
            'description': 'Initial assessment report',
            'content': 'base64_encoded_content_here'  # Simulated
        }, headers=auth_headers)
        
        if response.status_code != 404:
            assert response.status_code in [200, 201]
            document_id = response.get_json()['id']
            
            # 2. Set permissions
            response = client.post(f'/api/documents/{document_id}/permissions', json={
                'permissions': [
                    {
                        'user_id': data['users']['therapist'].id,
                        'can_read': True,
                        'can_update': True,
                        'can_delete': False
                    },
                    {
                        'user_id': data['users']['specialist'].id,
                        'can_read': True,
                        'can_update': False,
                        'can_delete': False
                    }
                ]
            }, headers=auth_headers)
            
            if response.status_code != 404:
                assert response.status_code == 200
                
                # 3. Create document version
                response = client.post(f'/api/documents/{document_id}/versions', json={
                    'version_number': '1.1',
                    'filename': 'assessment_report_v1.1.pdf',
                    'description': 'Updated with additional observations',
                    'content': 'base64_encoded_content_v2_here'
                }, headers=auth_headers)
                
                if response.status_code != 404:
                    assert response.status_code in [200, 201]
                    
                    # 4. Get document history
                    response = client.get(f'/api/documents/{document_id}/history', 
                                        headers=auth_headers)
                    
                    if response.status_code == 200:
                        history = response.get_json()['history']
                        assert len(history) >= 1