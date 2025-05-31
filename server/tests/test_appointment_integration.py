"""Integration tests for appointment functionality."""

import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.extensions import db


class TestAppointmentIntegration:
    """Integration tests for appointment functionality."""
    
    @pytest.fixture
    def sample_data(self, db_session):
        """Create sample data for tests."""
        # Create trainer
        trainer = User(
            email='trainer@example.com',
            username='trainer',
            first_name='John',
            last_name='Trainer',
            role='trainer',
            password='hashed_password'
        )
        db_session.add(trainer)
        
        # Create student
        student = User(
            email='student@example.com',
            username='student',
            first_name='Jane',
            last_name='Student',
            role='student',
            password='hashed_password'
        )
        db_session.add(student)
        
        # Create admin
        admin = User(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            role='admin',
            password='hashed_password'
        )
        db_session.add(admin)
        
        db_session.commit()
        
        # Create beneficiary
        beneficiary = Beneficiary(
            user_id=student.id,
            trainer_id=trainer.id,
            start_date=datetime.utcnow().date()
        )
        db_session.add(beneficiary)
        db_session.commit()
        
        return {
            'trainer': trainer,
            'student': student,
            'admin': admin,
            'beneficiary': beneficiary
        }
    
    def test_complete_appointment_flow(self, client, auth_tokens, sample_data):
        """Test complete appointment flow from creation to deletion."""
        trainer_token = auth_tokens['trainer']
        beneficiary_id = sample_data['beneficiary'].id
        
        # 1. Create appointment
        appointment_data = {
            'title': 'Initial Consultation',
            'description': 'First meeting with the student',
            'start_time': (datetime.utcnow() + timedelta(days=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat(),
            'beneficiary_id': beneficiary_id,
            'location': 'Office Room 101'
        }
        
        response = client.post(
            '/api/appointments',
            json=appointment_data,
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 201
        created_appointment = response.get_json()
        appointment_id = created_appointment['id']
        
        # 2. Get appointments list
        response = client.get(
            '/api/appointments',
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1
        assert any(app['id'] == appointment_id for app in data['appointments'])
        
        # 3. Update appointment
        update_data = {
            'title': 'Updated Consultation',
            'description': 'Rescheduled meeting'
        }
        
        response = client.put(
            f'/api/appointments/{appointment_id}',
            json=update_data,
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 200
        updated_appointment = response.get_json()
        assert updated_appointment['title'] == 'Updated Consultation'
        assert updated_appointment['description'] == 'Rescheduled meeting'
        
        # 4. Student view appointment
        student_token = auth_tokens['student']
        response = client.get(
            '/api/appointments',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1
        student_appointment = next((app for app in data['appointments'] if app['id'] == appointment_id), None)
        assert student_appointment is not None
        assert student_appointment['title'] == 'Updated Consultation'
        
        # 5. Admin view all appointments
        admin_token = auth_tokens['admin']
        response = client.get(
            '/api/appointments',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1
        
        # 6. Delete appointment
        response = client.delete(
            f'/api/appointments/{appointment_id}',
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Appointment deleted successfully'
        
        # 7. Verify appointment is deleted
        response = client.get(
            '/api/appointments',
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert not any(app['id'] == appointment_id for app in data['appointments'])
    
    def test_appointment_permissions(self, client, auth_tokens, sample_data):
        """Test appointment permissions for different roles."""
        trainer_token = auth_tokens['trainer']
        different_trainer_token = auth_tokens.get('trainer2', auth_tokens['trainer'])
        student_token = auth_tokens['student']
        beneficiary_id = sample_data['beneficiary'].id
        
        # Create appointment as trainer
        appointment_data = {
            'title': 'Permission Test Appointment',
            'start_time': (datetime.utcnow() + timedelta(days=2)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(days=2, hours=1)).isoformat(),
            'beneficiary_id': beneficiary_id
        }
        
        response = client.post(
            '/api/appointments',
            json=appointment_data,
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 201
        appointment_id = response.get_json()['id']
        
        # Student cannot create appointment
        response = client.post(
            '/api/appointments',
            json=appointment_data,
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        assert response.status_code == 403
        
        # Student cannot update appointment
        response = client.put(
            f'/api/appointments/{appointment_id}',
            json={'title': 'Updated by Student'},
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        assert response.status_code == 403
        
        # Different trainer cannot update appointment
        if different_trainer_token != trainer_token:
            response = client.put(
                f'/api/appointments/{appointment_id}',
                json={'title': 'Updated by Different Trainer'},
                headers={'Authorization': f'Bearer {different_trainer_token}'}
            )
            
            assert response.status_code == 403
        
        # Student cannot delete appointment
        response = client.delete(
            f'/api/appointments/{appointment_id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        
        assert response.status_code == 403
        
        # Admin can delete appointment
        admin_token = auth_tokens['admin']
        response = client.delete(
            f'/api/appointments/{appointment_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
    
    def test_appointment_date_validation(self, client, auth_tokens, sample_data):
        """Test appointment date validation."""
        trainer_token = auth_tokens['trainer']
        beneficiary_id = sample_data['beneficiary'].id
        
        # Try to create appointment in the past
        past_appointment_data = {
            'title': 'Past Appointment',
            'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            'beneficiary_id': beneficiary_id
        }
        
        response = client.post(
            '/api/appointments',
            json=past_appointment_data,
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 400
        assert 'past' in response.get_json()['message'].lower()
        
        # Try to create appointment with end time before start time
        invalid_time_data = {
            'title': 'Invalid Time Appointment',
            'start_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'beneficiary_id': beneficiary_id
        }
        
        response = client.post(
            '/api/appointments',
            json=invalid_time_data,
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 400
        assert 'before' in response.get_json()['message'].lower()
    
    def test_appointment_filtering(self, client, auth_tokens, sample_data):
        """Test appointment filtering."""
        trainer_token = auth_tokens['trainer']
        beneficiary_id = sample_data['beneficiary'].id
        
        # Create multiple appointments with different statuses
        appointments = []
        for i in range(3):
            appointment_data = {
                'title': f'Appointment {i}',
                'start_time': (datetime.utcnow() + timedelta(days=i+1)).isoformat(),
                'end_time': (datetime.utcnow() + timedelta(days=i+1, hours=1)).isoformat(),
                'beneficiary_id': beneficiary_id
            }
            
            response = client.post(
                '/api/appointments',
                json=appointment_data,
                headers={'Authorization': f'Bearer {trainer_token}'}
            )
            
            assert response.status_code == 201
            appointments.append(response.get_json())
        
        # Update one appointment to completed status
        response = client.put(
            f'/api/appointments/{appointments[0]["id"]}',
            json={'status': 'completed'},
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 200
        
        # Filter by status
        response = client.get(
            '/api/appointments?status=completed',
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert all(app['status'] == 'completed' for app in data['appointments'])
        
        # Filter by date range
        start_date = datetime.utcnow().date()
        end_date = (datetime.utcnow() + timedelta(days=2)).date()
        
        response = client.get(
            f'/api/appointments?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {trainer_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1
        
        # Clean up
        for appointment in appointments:
            client.delete(
                f'/api/appointments/{appointment["id"]}',
                headers={'Authorization': f'Bearer {trainer_token}'}
            )