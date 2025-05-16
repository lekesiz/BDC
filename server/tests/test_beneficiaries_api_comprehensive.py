"""Comprehensive tests for beneficiaries API endpoints."""

import json
from datetime import datetime
import pytest
import os
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from io import BytesIO

from app.models import User, Beneficiary, Tenant, Note, Appointment, Document
from app.extensions import db


@pytest.fixture
def test_users(app, session):
    """Create test users with different roles."""
    with app.app_context():
        # Create test tenant
        tenant = Tenant(
            name='Test Tenant',
            domain='test.com',
            is_active=True
        )
        session.add(tenant)
        session.commit()
        
        # Super admin user
        super_admin = User(
            username='superadmin',
            email='superadmin@test.com',
            first_name='Super',
            last_name='Admin',
            is_active=True,
            role='super_admin'
        )
        super_admin.password = 'password123'
        
        # Tenant admin user  
        tenant_admin = User(
            username='tenantadmin',
            email='tenantadmin@test.com',
            first_name='Tenant',
            last_name='Admin',
            is_active=True,
            role='tenant_admin'
        )
        tenant_admin.password = 'password123'
        
        # Trainer user
        trainer = User(
            username='trainer',
            email='trainer@test.com',
            first_name='Test',
            last_name='Trainer',
            is_active=True,
            role='trainer'
        )
        trainer.password = 'password123'
        
        # Student user
        student = User(
            username='student',
            email='student@test.com',
            first_name='Test',
            last_name='Student',
            is_active=True,
            role='student'
        )
        student.password = 'password123'
        
        session.add_all([super_admin, tenant_admin, trainer, student])
        session.commit()
        
        # Associate tenant_admin with tenant
        tenant_admin.tenants.append(tenant)
        session.commit()
        
        return {
            'tenant': tenant,
            'super_admin': super_admin,
            'tenant_admin': tenant_admin,
            'trainer': trainer,
            'student': student
        }


@pytest.fixture
def test_beneficiaries(app, session, test_users):
    """Create test beneficiaries."""
    with app.app_context():
        # Create beneficiary users
        beneficiary_user1 = User(
            username='beneficiary1',
            email='beneficiary1@test.com',
            first_name='Test',
            last_name='Beneficiary1',
            is_active=True,
            role='student'
        )
        beneficiary_user1.password = 'password123'
        
        beneficiary_user2 = User(
            username='beneficiary2',
            email='beneficiary2@test.com',
            first_name='Test',
            last_name='Beneficiary2',
            is_active=True,
            role='student'
        )
        beneficiary_user2.password = 'password123'
        
        session.add_all([beneficiary_user1, beneficiary_user2])
        session.commit()
        
        # Create beneficiaries
        beneficiary1 = Beneficiary(
            user_id=beneficiary_user1.id,
            trainer_id=test_users['trainer'].id,
            tenant_id=test_users['tenant'].id,
            phone='1234567890',
            gender='male',
            status='active',
            profession='Student',
            company='Test Company',
            birth_date=datetime(1995, 1, 1),
            address='123 Test St'
        )
        
        beneficiary2 = Beneficiary(
            user_id=beneficiary_user2.id,
            trainer_id=test_users['trainer'].id,
            tenant_id=test_users['tenant'].id,
            phone='0987654321',
            gender='female',
            status='inactive',
            profession='Developer',
            company='Another Company',
            birth_date=datetime(1998, 5, 15),
            address='456 Another St'
        )
        
        session.add_all([beneficiary1, beneficiary2])
        session.commit()
        
        return {
            'beneficiary_user1': beneficiary_user1,
            'beneficiary_user2': beneficiary_user2,
            'beneficiary1': beneficiary1,
            'beneficiary2': beneficiary2
        }


@pytest.fixture
def test_notes(app, session, test_users, test_beneficiaries):
    """Create test notes."""
    with app.app_context():
        note1 = Note(
            beneficiary_id=test_beneficiaries['beneficiary1'].id,
            user_id=test_users['trainer'].id,
            type='progress',
            content='Making good progress',
            is_private=False
        )
        
        note2 = Note(
            beneficiary_id=test_beneficiaries['beneficiary1'].id,
            user_id=test_users['trainer'].id,
            type='health',
            content='Private health note',
            is_private=True
        )
        
        session.add_all([note1, note2])
        session.commit()
        
        return {
            'note1': note1,
            'note2': note2
        }


@pytest.fixture
def auth_headers(app, test_users):
    """Generate authentication headers for different roles."""
    from flask_jwt_extended import create_access_token
    
    headers = {}
    with app.app_context():
        for role, user in test_users.items():
            if role != 'tenant':  # Skip tenant as it's not a user
                token = create_access_token(identity=user.id)
                headers[role] = {'Authorization': f'Bearer {token}'}
    
    return headers


class TestBeneficiariesAPI:
    """Test class for beneficiaries API endpoints."""
    
    def test_get_beneficiaries_unauthorized(self, client):
        """Test getting beneficiaries without authentication."""
        response = client.get('/api/beneficiaries')
        assert response.status_code == 401
    
    def test_get_beneficiaries_as_super_admin(self, client, auth_headers, test_beneficiaries):
        """Test getting beneficiaries as super admin."""
        response = client.get('/api/beneficiaries', headers=auth_headers['super_admin'])
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        assert 'total' in data
        assert len(data['items']) >= 2
    
    def test_get_beneficiaries_as_tenant_admin(self, client, auth_headers, test_beneficiaries):
        """Test getting beneficiaries as tenant admin (filtered by tenant)."""
        response = client.get('/api/beneficiaries', headers=auth_headers['tenant_admin'])
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        # All beneficiaries should belong to the tenant admin's tenant
        for beneficiary in data['items']:
            assert beneficiary['tenant_id'] == test_beneficiaries['beneficiary1'].tenant_id
    
    def test_get_beneficiaries_as_trainer(self, client, auth_headers, test_beneficiaries):
        """Test getting beneficiaries as trainer (filtered by trainer)."""
        response = client.get('/api/beneficiaries', headers=auth_headers['trainer'])
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        # All beneficiaries should be assigned to this trainer
        for beneficiary in data['items']:
            assert beneficiary['trainer_id'] == test_beneficiaries['beneficiary1'].trainer_id
    
    def test_get_beneficiaries_as_student(self, client, auth_headers):
        """Test that students cannot access beneficiaries list."""
        response = client.get('/api/beneficiaries', headers=auth_headers['student'])
        assert response.status_code == 403
    
    def test_get_beneficiaries_filtered_by_status(self, client, auth_headers, test_beneficiaries):
        """Test filtering beneficiaries by status."""
        response = client.get('/api/beneficiaries?status=active', headers=auth_headers['super_admin'])
        assert response.status_code == 200
        data = response.json
        assert all(b['status'] == 'active' for b in data['items'])
    
    def test_get_beneficiaries_with_search_query(self, client, auth_headers, test_beneficiaries):
        """Test searching beneficiaries by query."""
        response = client.get('/api/beneficiaries?query=Beneficiary1', headers=auth_headers['super_admin'])
        assert response.status_code == 200
        data = response.json
        assert len(data['items']) >= 1
        assert 'Beneficiary1' in data['items'][0]['user']['last_name']
    
    def test_get_beneficiaries_pagination(self, client, auth_headers, test_beneficiaries):
        """Test beneficiaries pagination."""
        response = client.get('/api/beneficiaries?page=1&per_page=1', headers=auth_headers['super_admin'])
        assert response.status_code == 200
        data = response.json
        assert data['page'] == 1
        assert data['per_page'] == 1
        assert len(data['items']) == 1
    
    @patch('app.services.BeneficiaryService.get_beneficiaries')
    def test_get_beneficiaries_server_error(self, mock_get, client, auth_headers):
        """Test server error handling in get beneficiaries."""
        mock_get.side_effect = Exception('Database error')
        response = client.get('/api/beneficiaries', headers=auth_headers['super_admin'])
        assert response.status_code == 500
        assert response.json['error'] == 'server_error'
    
    def test_get_beneficiary_by_id(self, client, auth_headers, test_beneficiaries):
        """Test getting a single beneficiary by ID."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        response = client.get(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers['super_admin'])
        assert response.status_code == 200
        data = response.json
        assert data['id'] == beneficiary_id
        assert data['phone'] == '1234567890'
    
    def test_get_beneficiary_not_found(self, client, auth_headers):
        """Test getting non-existent beneficiary."""
        response = client.get('/api/beneficiaries/99999', headers=auth_headers['super_admin'])
        assert response.status_code == 404
        assert response.json['error'] == 'not_found'
    
    def test_get_beneficiary_forbidden_trainer(self, client, auth_headers, test_beneficiaries, test_users):
        """Test trainer cannot access beneficiary not assigned to them."""
        # Create another trainer
        another_trainer = User(
            username='trainer2',
            email='trainer2@test.com',
            first_name='Another',
            last_name='Trainer',
            is_active=True,
            role='trainer'
        )
        another_trainer.password = 'password123'
        db.session.add(another_trainer)
        db.session.commit()
        
        # Create token for another trainer
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=another_trainer.id)
        headers = {'Authorization': f'Bearer {token}'}
        
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        response = client.get(f'/api/beneficiaries/{beneficiary_id}', headers=headers)
        assert response.status_code == 403
    
    def test_get_beneficiary_as_student_self(self, client, test_beneficiaries):
        """Test student can access their own beneficiary record."""
        from flask_jwt_extended import create_access_token
        
        # Create token for beneficiary user
        token = create_access_token(identity=test_beneficiaries['beneficiary_user1'].id)
        headers = {'Authorization': f'Bearer {token}'}
        
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        response = client.get(f'/api/beneficiaries/{beneficiary_id}', headers=headers)
        assert response.status_code == 200
    
    def test_get_beneficiary_forbidden_student(self, client, test_beneficiaries, auth_headers):
        """Test student cannot access other beneficiary records."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        response = client.get(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers['student'])
        assert response.status_code == 403
    
    def test_create_beneficiary_as_super_admin(self, client, auth_headers, test_users):
        """Test creating a beneficiary as super admin."""
        data = {
            'email': 'newbeneficiary@test.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'Beneficiary',
            'tenant_id': test_users['tenant'].id,
            'trainer_id': test_users['trainer'].id,
            'phone': '5555555555',
            'gender': 'male',
            'status': 'active',
            'profession': 'Student',
            'company': 'New Company'
        }
        
        response = client.post(
            '/api/beneficiaries',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 201
        result = response.json
        assert result['phone'] == '5555555555'
        assert result['user']['email'] == 'newbeneficiary@test.com'
    
    def test_create_beneficiary_as_tenant_admin(self, client, auth_headers, test_users):
        """Test creating a beneficiary as tenant admin (tenant_id overridden)."""
        data = {
            'email': 'tenantbeneficiary@test.com',
            'password': 'password123',
            'first_name': 'Tenant',
            'last_name': 'Beneficiary',
            'tenant_id': 99999,  # This should be overridden
            'trainer_id': test_users['trainer'].id,
            'phone': '6666666666',
            'gender': 'female',
            'status': 'active'
        }
        
        response = client.post(
            '/api/beneficiaries',
            data=json.dumps(data),
            headers=auth_headers['tenant_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 201
        result = response.json
        assert result['tenant_id'] == test_users['tenant'].id  # Should be tenant admin's tenant
    
    def test_create_beneficiary_validation_error(self, client, auth_headers):
        """Test creating beneficiary with invalid data."""
        data = {
            'email': 'invalid',  # Invalid email
            'password': '123',   # Too short
            'first_name': '',    # Empty
            'last_name': '',     # Empty
            'phone': '123',      # Too short
            'gender': 'invalid'  # Invalid gender
        }
        
        response = client.post(
            '/api/beneficiaries',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert response.json['error'] == 'validation_error'
        assert 'errors' in response.json
    
    def test_create_beneficiary_forbidden(self, client, auth_headers):
        """Test that trainers cannot create beneficiaries."""
        data = {
            'email': 'forbidden@test.com',
            'password': 'password123',
            'first_name': 'Forbidden',
            'last_name': 'User'
        }
        
        response = client.post(
            '/api/beneficiaries',
            data=json.dumps(data),
            headers=auth_headers['trainer'],
            content_type='application/json'
        )
        
        assert response.status_code == 403
    
    @patch('app.services.BeneficiaryService.create_beneficiary')
    def test_create_beneficiary_server_error(self, mock_create, client, auth_headers):
        """Test server error handling in create beneficiary."""
        mock_create.side_effect = Exception('Database error')
        
        data = {
            'email': 'error@test.com',
            'password': 'password123',
            'first_name': 'Error',
            'last_name': 'User',
            'tenant_id': 1
        }
        
        response = client.post(
            '/api/beneficiaries',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 500
        assert response.json['error'] == 'server_error'
    
    def test_update_beneficiary_as_super_admin(self, client, auth_headers, test_beneficiaries):
        """Test updating a beneficiary as super admin."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {
            'phone': '9999999999',
            'profession': 'Updated Profession',
            'company': 'Updated Company',
            'address': 'Updated Address'
        }
        
        response = client.patch(
            f'/api/beneficiaries/{beneficiary_id}',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.json
        assert result['phone'] == '9999999999'
        assert result['profession'] == 'Updated Profession'
    
    def test_update_beneficiary_as_trainer(self, client, auth_headers, test_beneficiaries):
        """Test updating a beneficiary as assigned trainer."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {
            'status': 'completed'
        }
        
        response = client.patch(
            f'/api/beneficiaries/{beneficiary_id}',
            data=json.dumps(data),
            headers=auth_headers['trainer'],
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'completed'
    
    def test_update_beneficiary_not_found(self, client, auth_headers):
        """Test updating non-existent beneficiary."""
        data = {'phone': '1234567890'}
        
        response = client.patch(
            '/api/beneficiaries/99999',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_update_beneficiary_forbidden(self, client, auth_headers, test_beneficiaries, test_users):
        """Test trainer cannot update beneficiary not assigned to them."""
        # Create another trainer
        another_trainer = User(
            username='trainer3',
            email='trainer3@test.com',
            first_name='Another',
            last_name='Trainer',
            is_active=True,
            role='trainer'
        )
        another_trainer.password = 'password123'
        db.session.add(another_trainer)
        db.session.commit()
        
        # Create token for another trainer
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=another_trainer.id)
        headers = {'Authorization': f'Bearer {token}'}
        
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {'phone': '1234567890'}
        
        response = client.patch(
            f'/api/beneficiaries/{beneficiary_id}',
            data=json.dumps(data),
            headers=headers,
            content_type='application/json'
        )
        
        assert response.status_code == 403
    
    def test_update_beneficiary_validation_error(self, client, auth_headers, test_beneficiaries):
        """Test updating beneficiary with invalid data."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {
            'phone': '123',  # Too short
            'gender': 'invalid'  # Invalid gender
        }
        
        response = client.patch(
            f'/api/beneficiaries/{beneficiary_id}',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert response.json['error'] == 'validation_error'
    
    def test_delete_beneficiary_as_super_admin(self, client, auth_headers, test_beneficiaries):
        """Test deleting a beneficiary as super admin."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        
        response = client.delete(
            f'/api/beneficiaries/{beneficiary_id}',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 200
        assert response.json['message'] == 'Beneficiary deleted successfully'
    
    def test_delete_beneficiary_as_tenant_admin(self, client, auth_headers, test_beneficiaries):
        """Test deleting a beneficiary as tenant admin."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        
        response = client.delete(
            f'/api/beneficiaries/{beneficiary_id}',
            headers=auth_headers['tenant_admin']
        )
        
        assert response.status_code == 200
    
    def test_delete_beneficiary_not_found(self, client, auth_headers):
        """Test deleting non-existent beneficiary."""
        response = client.delete(
            '/api/beneficiaries/99999',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 404
    
    def test_delete_beneficiary_forbidden_trainer(self, client, auth_headers, test_beneficiaries):
        """Test that trainers cannot delete beneficiaries."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        
        response = client.delete(
            f'/api/beneficiaries/{beneficiary_id}',
            headers=auth_headers['trainer']
        )
        
        assert response.status_code == 403
    
    def test_delete_beneficiary_forbidden_tenant_admin_wrong_tenant(self, client, test_beneficiaries):
        """Test tenant admin cannot delete beneficiary from another tenant."""
        # Create another tenant and admin
        another_tenant = Tenant(name='Another Tenant', domain='another.com', is_active=True)
        db.session.add(another_tenant)
        
        another_admin = User(
            username='anotheradmin',
            email='anotheradmin@test.com',
            first_name='Another',
            last_name='Admin',
            is_active=True,
            role='tenant_admin'
        )
        another_admin.password = 'password123'
        db.session.add(another_admin)
        db.session.commit()
        
        another_admin.tenants.append(another_tenant)
        db.session.commit()
        
        # Create token for another admin
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=another_admin.id)
        headers = {'Authorization': f'Bearer {token}'}
        
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        response = client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=headers)
        assert response.status_code == 403
    
    @patch('app.services.BeneficiaryService.delete_beneficiary')
    def test_delete_beneficiary_server_error(self, mock_delete, client, auth_headers, test_beneficiaries):
        """Test server error handling in delete beneficiary."""
        mock_delete.side_effect = Exception('Database error')
        
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        response = client.delete(
            f'/api/beneficiaries/{beneficiary_id}',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 500
        assert response.json['error'] == 'server_error'
    
    def test_assign_trainer_as_super_admin(self, client, auth_headers, test_beneficiaries, test_users):
        """Test assigning a trainer as super admin."""
        # Create another trainer
        new_trainer = User(
            username='newtrainer',
            email='newtrainer@test.com',
            first_name='New',
            last_name='Trainer',
            is_active=True,
            role='trainer'
        )
        new_trainer.password = 'password123'
        db.session.add(new_trainer)
        db.session.commit()
        
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {'trainer_id': new_trainer.id}
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/assign-trainer',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.json['trainer_id'] == new_trainer.id
    
    def test_assign_trainer_validation_error(self, client, auth_headers, test_beneficiaries):
        """Test assigning trainer with missing trainer_id."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {}  # Missing trainer_id
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/assign-trainer',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert response.json['error'] == 'validation_error'
    
    def test_assign_trainer_null_trainer(self, client, auth_headers, test_beneficiaries):
        """Test unassigning trainer by setting null."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {'trainer_id': None}  # Unassign trainer
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/assign-trainer',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.json['trainer_id'] is None
    
    def test_assign_trainer_not_found(self, client, auth_headers):
        """Test assigning trainer to non-existent beneficiary."""
        data = {'trainer_id': 1}
        
        response = client.post(
            '/api/beneficiaries/99999/assign-trainer',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_assign_trainer_forbidden(self, client, auth_headers, test_beneficiaries):
        """Test that trainers cannot assign trainers."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {'trainer_id': 1}
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/assign-trainer',
            data=json.dumps(data),
            headers=auth_headers['trainer'],
            content_type='application/json'
        )
        
        assert response.status_code == 403
    
    @patch('app.services.BeneficiaryService.assign_trainer')
    def test_assign_trainer_server_error(self, mock_assign, client, auth_headers, test_beneficiaries):
        """Test server error handling in assign trainer."""
        mock_assign.side_effect = Exception('Database error')
        
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {'trainer_id': 1}
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/assign-trainer',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 500
        assert response.json['error'] == 'server_error'
    
    # Note endpoints tests
    
    def test_get_notes_for_beneficiary(self, client, auth_headers, test_beneficiaries, test_notes):
        """Test getting notes for a beneficiary."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        
        response = client.get(
            f'/api/beneficiaries/{beneficiary_id}/notes',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        assert len(data['items']) >= 2
    
    def test_get_notes_filtered_by_type(self, client, auth_headers, test_beneficiaries, test_notes):
        """Test filtering notes by type."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        
        response = client.get(
            f'/api/beneficiaries/{beneficiary_id}/notes?type=progress',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 200
        data = response.json
        assert all(note['type'] == 'progress' for note in data['items'])
    
    def test_get_notes_filtered_by_privacy(self, client, auth_headers, test_beneficiaries, test_notes):
        """Test filtering notes by privacy."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        
        response = client.get(
            f'/api/beneficiaries/{beneficiary_id}/notes?is_private=false',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 200
        data = response.json
        assert all(not note['is_private'] for note in data['items'])
    
    def test_get_notes_as_student_non_private_only(self, client, test_beneficiaries, test_notes):
        """Test students can only see non-private notes."""
        from flask_jwt_extended import create_access_token
        
        # Create token for beneficiary user
        token = create_access_token(identity=test_beneficiaries['beneficiary_user1'].id)
        headers = {'Authorization': f'Bearer {token}'}
        
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        response = client.get(f'/api/beneficiaries/{beneficiary_id}/notes', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert all(not note['is_private'] for note in data['items'])
    
    def test_get_notes_forbidden(self, client, auth_headers, test_beneficiaries):
        """Test unauthorized access to notes."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        
        # Try with a student that is not the beneficiary
        response = client.get(
            f'/api/beneficiaries/{beneficiary_id}/notes',
            headers=auth_headers['student']
        )
        
        assert response.status_code == 403
    
    def test_get_notes_beneficiary_not_found(self, client, auth_headers):
        """Test getting notes for non-existent beneficiary."""
        response = client.get(
            '/api/beneficiaries/99999/notes',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 404
    
    def test_create_note_for_beneficiary(self, client, auth_headers, test_beneficiaries):
        """Test creating a note for a beneficiary."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {
            'type': 'general',
            'content': 'This is a test note',
            'is_private': False
        }
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/notes',
            data=json.dumps(data),
            headers=auth_headers['trainer'],
            content_type='application/json'
        )
        
        assert response.status_code == 201
        result = response.json
        assert result['content'] == 'This is a test note'
        assert result['type'] == 'general'
        assert result['beneficiary_id'] == beneficiary_id
    
    def test_create_note_validation_error(self, client, auth_headers, test_beneficiaries):
        """Test creating note with invalid data."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {
            'type': 'invalid_type',  # Invalid type
            'content': '',  # Empty content
        }
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/notes',
            data=json.dumps(data),
            headers=auth_headers['trainer'],
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert response.json['error'] == 'validation_error'
    
    def test_create_note_forbidden(self, client, auth_headers, test_beneficiaries):
        """Test that students cannot create notes."""
        beneficiary_id = test_beneficiaries['beneficiary1'].id
        data = {
            'type': 'general',
            'content': 'Forbidden note'
        }
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/notes',
            data=json.dumps(data),
            headers=auth_headers['student'],
            content_type='application/json'
        )
        
        assert response.status_code == 403
    
    def test_update_note(self, client, auth_headers, test_notes):
        """Test updating a note."""
        note_id = test_notes['note1'].id
        data = {
            'content': 'Updated note content',
            'type': 'general'
        }
        
        response = client.patch(
            f'/api/beneficiaries/notes/{note_id}',
            data=json.dumps(data),
            headers=auth_headers['trainer'],
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = response.json
        assert result['content'] == 'Updated note content'
        assert result['type'] == 'general'
    
    def test_update_note_not_found(self, client, auth_headers):
        """Test updating non-existent note."""
        data = {'content': 'Updated content'}
        
        response = client.patch(
            '/api/beneficiaries/notes/99999',
            data=json.dumps(data),
            headers=auth_headers['super_admin'],
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_update_note_forbidden(self, client, auth_headers, test_notes, test_users):
        """Test unauthorized note update."""
        # Create another trainer
        another_trainer = User(
            username='anothertrainer',
            email='anothertrainer@test.com',
            first_name='Another',
            last_name='Trainer',
            is_active=True,
            role='trainer'
        )
        another_trainer.password = 'password123'
        db.session.add(another_trainer)
        db.session.commit()
        
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=another_trainer.id)
        headers = {'Authorization': f'Bearer {token}'}
        
        note_id = test_notes['note1'].id
        data = {'content': 'Unauthorized update'}
        
        response = client.patch(
            f'/api/beneficiaries/notes/{note_id}',
            data=json.dumps(data),
            headers=headers,
            content_type='application/json'
        )
        
        assert response.status_code == 403
    
    def test_delete_note(self, client, auth_headers, test_notes):
        """Test deleting a note."""
        note_id = test_notes['note1'].id
        
        response = client.delete(
            f'/api/beneficiaries/notes/{note_id}',
            headers=auth_headers['trainer']
        )
        
        assert response.status_code == 200
        assert response.json['message'] == 'Note deleted successfully'
    
    def test_delete_note_not_found(self, client, auth_headers):
        """Test deleting non-existent note."""
        response = client.delete(
            '/api/beneficiaries/notes/99999',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 404
    
    def test_delete_note_forbidden(self, client, auth_headers, test_notes):
        """Test unauthorized note deletion."""
        note_id = test_notes['note1'].id
        
        response = client.delete(
            f'/api/beneficiaries/notes/{note_id}',
            headers=auth_headers['student']
        )
        
        assert response.status_code == 403
    
    @patch('app.services.NoteService.delete_note')
    def test_delete_note_server_error(self, mock_delete, client, auth_headers, test_notes):
        """Test server error handling in delete note."""
        mock_delete.side_effect = Exception('Database error')
        
        note_id = test_notes['note1'].id
        response = client.delete(
            f'/api/beneficiaries/notes/{note_id}',
            headers=auth_headers['super_admin']
        )
        
        assert response.status_code == 500
        assert response.json['error'] == 'server_error'