"""Integration tests for beneficiary service and API."""
import pytest
import json
from datetime import datetime, timedelta

from tests.integration.base_integration_test import BaseIntegrationTest
from app.core.container import get_beneficiary_service
from app.models import Beneficiary, Note, Document, Appointment, Program


class TestBeneficiaryIntegration(BaseIntegrationTest):
    """Test beneficiary service integration."""
    
    @pytest.fixture
    def test_beneficiary(self, session, test_tenant):
        """Create a test beneficiary."""
        beneficiary = Beneficiary(
            name='Test',
            surname='Beneficiary',
            email='beneficiary@example.com',
            phone='+1234567890',
            national_id='12345678901',
            date_of_birth=datetime(1990, 1, 1).date(),
            city='Test City',
            status='active',
            tenant_id=test_tenant.id
        )
        session.add(beneficiary)
        session.commit()
        return beneficiary
    
    @pytest.fixture
    def test_program(self, session, test_tenant):
        """Create a test program."""
        program = Program(
            name='Test Program',
            description='Test program description',
            category='education',
            start_date=datetime.utcnow().date(),
            is_active=True,
            tenant_id=test_tenant.id
        )
        session.add(program)
        session.commit()
        return program
    
    def test_create_beneficiary_via_api(self, client, admin_auth_headers, test_tenant):
        """Test creating beneficiary through API."""
        response = client.post('/api/v2/beneficiaries',
                             headers=admin_auth_headers,
                             json={
                                 'name': 'New',
                                 'surname': 'Beneficiary',
                                 'email': 'new@example.com',
                                 'phone': '+0987654321',
                                 'national_id': '98765432101',
                                 'city': 'New City',
                                 'status': 'active',
                                 'tenant_id': test_tenant.id
                             })
        
        self.assert_response_ok(response, 201)
        data = json.loads(response.data)
        assert data['beneficiary']['email'] == 'new@example.com'
    
    def test_search_beneficiaries(self, client, admin_auth_headers, test_beneficiary):
        """Test searching beneficiaries."""
        response = client.get('/api/v2/beneficiaries?q=Test',
                            headers=admin_auth_headers)
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert len(data['beneficiaries']) > 0
        assert data['beneficiaries'][0]['name'] == 'Test'
    
    def test_beneficiary_statistics(self, client, admin_auth_headers, session):
        """Test getting beneficiary statistics."""
        # Create multiple beneficiaries
        for i in range(3):
            beneficiary = Beneficiary(
                name=f'Ben{i}',
                surname='Test',
                email=f'ben{i}@example.com',
                status='active' if i < 2 else 'inactive',
                city='City1' if i == 0 else 'City2',
                tenant_id=1
            )
            session.add(beneficiary)
        session.commit()
        
        response = client.get('/api/v2/beneficiaries/statistics',
                            headers=admin_auth_headers)
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert data['total'] >= 3
        assert data['active'] >= 2
        assert data['inactive'] >= 1
    
    def test_beneficiary_notes(self, client, admin_auth_headers, test_beneficiary, admin_user):
        """Test beneficiary notes functionality."""
        # Add note
        response = client.post(f'/api/v2/beneficiaries/{test_beneficiary.id}/notes',
                             headers=admin_auth_headers,
                             json={
                                 'content': 'Test note content',
                                 'note_type': 'general',
                                 'is_private': False
                             })
        
        self.assert_response_ok(response, 201)
        data = json.loads(response.data)
        note_id = data['note']['id']
        
        # Get notes
        response = client.get(f'/api/v2/beneficiaries/{test_beneficiary.id}/notes',
                            headers=admin_auth_headers)
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert len(data['notes']) == 1
        
        # Update note
        response = client.put(f'/api/v2/beneficiaries/notes/{note_id}',
                            headers=admin_auth_headers,
                            json={'content': 'Updated content'})
        
        self.assert_response_ok(response)
        
        # Delete note
        response = client.delete(f'/api/v2/beneficiaries/notes/{note_id}',
                               headers=admin_auth_headers)
        
        self.assert_response_ok(response)
    
    def test_beneficiary_appointments(self, client, admin_auth_headers, test_beneficiary):
        """Test beneficiary appointments functionality."""
        # Schedule appointment
        response = client.post(f'/api/v2/beneficiaries/{test_beneficiary.id}/appointments',
                             headers=admin_auth_headers,
                             json={
                                 'title': 'Test Appointment',
                                 'scheduled_date': (datetime.utcnow() + timedelta(days=1)).date().isoformat(),
                                 'scheduled_time': '14:00',
                                 'duration_minutes': 60,
                                 'location': 'Office'
                             })
        
        self.assert_response_ok(response, 201)
        data = json.loads(response.data)
        appointment_id = data['appointment']['id']
        
        # Get appointments
        response = client.get(f'/api/v2/beneficiaries/{test_beneficiary.id}/appointments',
                            headers=admin_auth_headers)
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert len(data['appointments']) == 1
        
        # Cancel appointment
        response = client.post(f'/api/v2/beneficiaries/appointments/{appointment_id}/cancel',
                             headers=admin_auth_headers,
                             json={'reason': 'Test cancellation'})
        
        self.assert_response_ok(response)
    
    def test_beneficiary_program_enrollment(self, app, session, test_beneficiary, test_program, test_user):
        """Test program enrollment functionality."""
        with app.app_context():
            beneficiary_service = get_beneficiary_service()
            
            # Enroll in program
            success = beneficiary_service.enroll_in_program(
                test_beneficiary.id,
                test_program.id
            )
            assert success
            
            # Check enrollment
            beneficiaries = beneficiary_service.get_beneficiaries_by_program(test_program.id)
            assert len(beneficiaries) == 1
            assert beneficiaries[0].id == test_beneficiary.id
            
            # Unenroll
            success = beneficiary_service.unenroll_from_program(
                test_beneficiary.id,
                test_program.id
            )
            assert success
    
    def test_beneficiary_export(self, client, admin_auth_headers, test_beneficiary):
        """Test beneficiary data export."""
        # Export as PDF
        response = client.get(f'/api/v2/beneficiaries/{test_beneficiary.id}/export?format=pdf',
                            headers=admin_auth_headers)
        
        self.assert_response_ok(response)
        assert response.content_type == 'application/pdf'
        
        # Export as CSV
        response = client.get(f'/api/v2/beneficiaries/{test_beneficiary.id}/export?format=csv',
                            headers=admin_auth_headers)
        
        self.assert_response_ok(response)
        assert response.content_type == 'text/csv'
    
    def test_beneficiary_service_caching(self, app, test_beneficiary):
        """Test that beneficiary service uses caching."""
        with app.app_context():
            beneficiary_service = get_beneficiary_service()
            
            # First call - should hit database
            beneficiary1 = beneficiary_service.get_beneficiary(test_beneficiary.id)
            
            # Second call - should hit cache
            beneficiary2 = beneficiary_service.get_beneficiary(test_beneficiary.id)
            
            assert beneficiary1.id == beneficiary2.id
            
            # Update should clear cache
            beneficiary_service.update_beneficiary(test_beneficiary.id, {'city': 'New City'})
            
            # Next call should hit database again
            beneficiary3 = beneficiary_service.get_beneficiary(test_beneficiary.id)
            assert beneficiary3.city == 'New City'
    
    def test_beneficiary_duplicate_prevention(self, app, session, test_beneficiary):
        """Test that duplicate beneficiaries are prevented."""
        with app.app_context():
            beneficiary_service = get_beneficiary_service()
            
            # Try to create with same email
            with pytest.raises(ValueError) as exc:
                beneficiary_service.create_beneficiary({
                    'name': 'Another',
                    'surname': 'Person',
                    'email': test_beneficiary.email,
                    'status': 'active'
                })
            assert 'already exists' in str(exc.value)
            
            # Try to create with same national ID
            with pytest.raises(ValueError) as exc:
                beneficiary_service.create_beneficiary({
                    'name': 'Another',
                    'surname': 'Person',
                    'email': 'another@example.com',
                    'national_id': test_beneficiary.national_id,
                    'status': 'active'
                })
            assert 'already exists' in str(exc.value)
    
    def test_upcoming_appointments(self, app, session, test_beneficiary):
        """Test getting upcoming appointments across all beneficiaries."""
        with app.app_context():
            beneficiary_service = get_beneficiary_service()
            
            # Schedule appointments
            for i in range(3):
                beneficiary_service.schedule_appointment(test_beneficiary.id, {
                    'title': f'Appointment {i}',
                    'scheduled_date': datetime.utcnow().date() + timedelta(days=i+1),
                    'scheduled_time': '10:00',
                    'created_by_id': 1
                })
            
            # Get upcoming appointments
            appointments = beneficiary_service.get_upcoming_appointments(days=7)
            assert len(appointments) == 3