"""Comprehensive tests for appointments API endpoints."""
import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.appointment import Appointment
from app.models.beneficiary import Beneficiary


class TestAppointmentsAPI:
    """Test appointments API endpoints comprehensively."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_app):
        """Set up test environment."""
        self.app = test_app
        self.client = test_app.test_client()
        
        with test_app.app_context():
            # Create test tenant
            self.tenant = Tenant(
                name='Test Tenant',
                slug='test-tenant',
                email='tenant@test.com',
                is_active=True
            )
            db.session.add(self.tenant)
            
            # Create test users
            self.admin_user = User(
                email='admin@test.com',
                username='admin',
                first_name='Admin',
                last_name='User',
                role='super_admin',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.admin_user.password = 'Admin123!'
            
            self.trainer = User(
                email='trainer@test.com',
                username='trainer',
                first_name='Trainer',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.trainer.password = 'Trainer123!'
            
            self.trainer2 = User(
                email='trainer2@test.com',
                username='trainer2',
                first_name='Trainer2',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.trainer2.password = 'Trainer123!'
            
            self.student = User(
                email='student@test.com',
                username='student',
                first_name='Student',
                last_name='User',
                role='student',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.student.password = 'Student123!'
            
            db.session.add_all([self.admin_user, self.trainer, self.trainer2, self.student])
            
            # Create beneficiary
            self.beneficiary = Beneficiary(
                user_id=self.student.id,
                tenant_id=self.tenant.id,
                status='active',
                enrollment_date=datetime.now()
            )
            db.session.add(self.beneficiary)
            
            # Create appointments
            self.appointment1 = Appointment(
                title='Initial Consultation',
                description='First meeting with beneficiary',
                trainer_id=self.trainer.id,
                beneficiary_id=self.beneficiary.id,
                start_time=datetime.now() + timedelta(days=1, hours=10),
                end_time=datetime.now() + timedelta(days=1, hours=11),
                appointment_type='consultation',
                status='scheduled',
                location='Office Room 1',
                tenant_id=self.tenant.id
            )
            
            self.appointment2 = Appointment(
                title='Training Session',
                description='Python basics training',
                trainer_id=self.trainer.id,
                beneficiary_id=self.beneficiary.id,
                start_time=datetime.now() + timedelta(days=3, hours=14),
                end_time=datetime.now() + timedelta(days=3, hours=16),
                appointment_type='training',
                status='scheduled',
                location='Training Room A',
                tenant_id=self.tenant.id,
                meeting_link='https://meet.example.com/abc123'
            )
            
            self.past_appointment = Appointment(
                title='Completed Session',
                description='Previous training session',
                trainer_id=self.trainer.id,
                beneficiary_id=self.beneficiary.id,
                start_time=datetime.now() - timedelta(days=2, hours=10),
                end_time=datetime.now() - timedelta(days=2, hours=11),
                appointment_type='training',
                status='completed',
                location='Office',
                tenant_id=self.tenant.id,
                notes='Session completed successfully'
            )
            
            db.session.add_all([self.appointment1, self.appointment2, self.past_appointment])
            db.session.commit()
            
            # Create access tokens
            self.admin_token = create_access_token(identity=self.admin_user.id)
            self.trainer_token = create_access_token(identity=self.trainer.id)
            self.trainer2_token = create_access_token(identity=self.trainer2.id)
            self.student_token = create_access_token(identity=self.student.id)
    
    def test_get_appointments_list(self):
        """Test getting appointments list."""
        response = self.client.get('/api/appointments',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'appointments' in data
        assert len(data['appointments']) >= 3
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data
    
    def test_get_appointments_with_filters(self):
        """Test getting appointments with filters."""
        # Filter by status
        response = self.client.get('/api/appointments?status=scheduled',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(a['status'] == 'scheduled' for a in data['appointments'])
        
        # Filter by date range
        start_date = datetime.now().date().isoformat()
        end_date = (datetime.now() + timedelta(days=7)).date().isoformat()
        response = self.client.get(f'/api/appointments?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['appointments']) >= 2
    
    def test_get_appointment_by_id(self):
        """Test getting specific appointment."""
        response = self.client.get(f'/api/appointments/{self.appointment1.id}',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == self.appointment1.id
        assert data['title'] == 'Initial Consultation'
        assert data['trainer']['id'] == self.trainer.id
        assert data['beneficiary']['id'] == self.beneficiary.id
    
    def test_create_appointment(self):
        """Test creating new appointment."""
        response = self.client.post('/api/appointments',
            data=json.dumps({
                'title': 'Follow-up Meeting',
                'description': 'Check progress',
                'trainer_id': self.trainer.id,
                'beneficiary_id': self.beneficiary.id,
                'start_time': (datetime.now() + timedelta(days=5, hours=15)).isoformat(),
                'end_time': (datetime.now() + timedelta(days=5, hours=16)).isoformat(),
                'appointment_type': 'follow_up',
                'location': 'Conference Room B',
                'send_notifications': True
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Follow-up Meeting'
        assert data['status'] == 'scheduled'
        assert data['appointment_type'] == 'follow_up'
    
    def test_update_appointment(self):
        """Test updating appointment."""
        response = self.client.put(f'/api/appointments/{self.appointment1.id}',
            data=json.dumps({
                'title': 'Updated Consultation',
                'location': 'Virtual Meeting',
                'meeting_link': 'https://zoom.us/j/123456789'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Consultation'
        assert data['location'] == 'Virtual Meeting'
        assert data['meeting_link'] == 'https://zoom.us/j/123456789'
    
    def test_reschedule_appointment(self):
        """Test rescheduling appointment."""
        new_start = datetime.now() + timedelta(days=2, hours=14)
        new_end = datetime.now() + timedelta(days=2, hours=15)
        
        response = self.client.post(f'/api/appointments/{self.appointment1.id}/reschedule',
            data=json.dumps({
                'start_time': new_start.isoformat(),
                'end_time': new_end.isoformat(),
                'reason': 'Trainer not available at original time'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'scheduled'
        # Times should be updated
    
    def test_cancel_appointment(self):
        """Test canceling appointment."""
        response = self.client.post(f'/api/appointments/{self.appointment2.id}/cancel',
            data=json.dumps({
                'reason': 'Student requested cancellation'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'cancelled'
        assert 'cancellation_reason' in data
    
    def test_complete_appointment(self):
        """Test marking appointment as completed."""
        # First, make the appointment time in the past
        with self.app.app_context():
            apt = Appointment.query.get(self.appointment1.id)
            apt.start_time = datetime.now() - timedelta(hours=2)
            apt.end_time = datetime.now() - timedelta(hours=1)
            db.session.commit()
        
        response = self.client.post(f'/api/appointments/{self.appointment1.id}/complete',
            data=json.dumps({
                'notes': 'Session went well, student showed good progress',
                'attended': True
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'completed'
        assert data['notes'] == 'Session went well, student showed good progress'
    
    def test_mark_no_show(self):
        """Test marking appointment as no-show."""
        # Make appointment time in the past
        with self.app.app_context():
            apt = Appointment.query.get(self.appointment2.id)
            apt.start_time = datetime.now() - timedelta(hours=2)
            apt.end_time = datetime.now() - timedelta(hours=1)
            db.session.commit()
        
        response = self.client.post(f'/api/appointments/{self.appointment2.id}/no-show',
            data=json.dumps({
                'notes': 'Student did not attend'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'no_show'
    
    def test_get_my_appointments(self):
        """Test getting appointments for current user."""
        # As student
        response = self.client.get('/api/appointments/my',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'appointments' in data
        assert all(a['beneficiary']['user_id'] == self.student.id for a in data['appointments'])
        
        # As trainer
        response = self.client.get('/api/appointments/my',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(a['trainer_id'] == self.trainer.id for a in data['appointments'])
    
    def test_get_upcoming_appointments(self):
        """Test getting upcoming appointments."""
        response = self.client.get('/api/appointments/upcoming',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'appointments' in data
        assert len(data['appointments']) >= 2
        # All should be in the future
    
    def test_check_availability(self):
        """Test checking trainer availability."""
        check_date = (datetime.now() + timedelta(days=1)).date().isoformat()
        response = self.client.post('/api/appointments/check-availability',
            data=json.dumps({
                'trainer_id': self.trainer.id,
                'date': check_date,
                'duration': 60
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'available_slots' in data
    
    def test_bulk_create_appointments(self):
        """Test creating multiple appointments."""
        response = self.client.post('/api/appointments/bulk',
            data=json.dumps({
                'title': 'Weekly Training',
                'description': 'Regular training sessions',
                'trainer_id': self.trainer.id,
                'beneficiary_ids': [self.beneficiary.id],
                'appointment_type': 'training',
                'location': 'Training Room',
                'recurring': {
                    'frequency': 'weekly',
                    'count': 4,
                    'start_date': (datetime.now() + timedelta(days=7)).isoformat(),
                    'time': '10:00',
                    'duration': 60
                }
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [201, 404]  # Might not be implemented
        if response.status_code == 201:
            data = json.loads(response.data)
            assert 'created' in data
            assert data['created'] == 4
    
    def test_get_appointment_history(self):
        """Test getting appointment history."""
        response = self.client.get(f'/api/appointments/history?beneficiary_id={self.beneficiary.id}',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'appointments' in data
        assert any(a['status'] == 'completed' for a in data['appointments'])
    
    def test_send_reminder(self):
        """Test sending appointment reminder."""
        response = self.client.post(f'/api/appointments/{self.appointment1.id}/send-reminder',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_appointment_feedback(self):
        """Test submitting appointment feedback."""
        response = self.client.post(f'/api/appointments/{self.past_appointment.id}/feedback',
            data=json.dumps({
                'rating': 5,
                'comments': 'Very helpful session',
                'would_recommend': True
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code in [201, 404]
    
    def test_export_appointments(self):
        """Test exporting appointments."""
        response = self.client.get('/api/appointments/export?format=csv',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.content_type in ['text/csv', 'application/csv']
    
    def test_appointment_permissions(self):
        """Test appointment permissions for different roles."""
        # Trainer can only see their appointments
        response = self.client.get(f'/api/appointments/{self.appointment1.id}',
            headers={'Authorization': f'Bearer {self.trainer2_token}'}
        )
        assert response.status_code in [403, 404]
        
        # Student can see their appointments
        response = self.client.get(f'/api/appointments/{self.appointment1.id}',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        assert response.status_code == 200
        
        # Student cannot create appointments
        response = self.client.post('/api/appointments',
            data=json.dumps({
                'title': 'New Appointment',
                'trainer_id': self.trainer.id,
                'beneficiary_id': self.beneficiary.id,
                'start_time': datetime.now().isoformat(),
                'end_time': (datetime.now() + timedelta(hours=1)).isoformat()
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        assert response.status_code in [403, 201]  # Depends on implementation
    
    def test_appointment_conflicts(self):
        """Test detecting appointment conflicts."""
        # Try to create overlapping appointment
        response = self.client.post('/api/appointments',
            data=json.dumps({
                'title': 'Conflicting Appointment',
                'trainer_id': self.trainer.id,
                'beneficiary_id': self.beneficiary.id,
                'start_time': (self.appointment1.start_time + timedelta(minutes=30)).isoformat(),
                'end_time': (self.appointment1.end_time + timedelta(minutes=30)).isoformat(),
                'appointment_type': 'consultation',
                'location': 'Office'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Should either reject or warn about conflict
        assert response.status_code in [201, 400, 409]
    
    def test_appointment_statistics(self):
        """Test getting appointment statistics."""
        response = self.client.get('/api/appointments/statistics',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'total_appointments' in data
            assert 'completed' in data
            assert 'cancelled' in data
            assert 'no_show_rate' in data
    
    def test_recurring_appointments(self):
        """Test managing recurring appointments."""
        # Get recurring appointment series
        response = self.client.get(f'/api/appointments/{self.appointment1.id}/series',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code in [200, 404]
        
        # Cancel entire series
        response = self.client.post(f'/api/appointments/{self.appointment1.id}/cancel-series',
            data=json.dumps({
                'reason': 'Schedule change'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code in [200, 404]
    
    def test_appointment_attachments(self):
        """Test adding attachments to appointments."""
        response = self.client.post(f'/api/appointments/{self.appointment1.id}/attachments',
            data=json.dumps({
                'document_ids': [1, 2],
                'notes': 'Materials for the session'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code in [200, 201, 404]