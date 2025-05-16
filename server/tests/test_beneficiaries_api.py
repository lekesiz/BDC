"""Tests for beneficiaries API."""

import pytest
import json
import uuid
from datetime import datetime
from io import BytesIO
from unittest.mock import patch, MagicMock
from app.models import User, Beneficiary, Note, Appointment, Document
from app.extensions import db


@pytest.fixture
def setup_beneficiaries_data(session, app):
    """Setup test data for beneficiaries API tests."""
    # Generate unique suffix
    suffix = str(uuid.uuid4())[:8]
    
    # Create test users
    admin_user = User(
        username=f'admin_{suffix}',
        email=f'admin_{suffix}@test.com',
        first_name='Admin',
        last_name='User',
        is_active=True,
        role='super_admin',
        tenant_id=1
    )
    admin_user.password = 'password123'
    
    trainer_user = User(
        username=f'trainer_{suffix}',
        email=f'trainer_{suffix}@test.com',
        first_name='Trainer',
        last_name='User',
        is_active=True,
        role='trainer',
        tenant_id=1
    )
    trainer_user.password = 'password123'
    
    beneficiary_user = User(
        username=f'beneficiary_{suffix}',
        email=f'beneficiary_{suffix}@test.com',
        first_name='Beneficiary',
        last_name='User',
        is_active=True,
        role='student',
        tenant_id=1
    )
    beneficiary_user.password = 'password123'
    
    session.add_all([admin_user, trainer_user, beneficiary_user])
    session.commit()
    
    # Create test beneficiary
    beneficiary = Beneficiary(
        user_id=beneficiary_user.id,
        trainer_id=trainer_user.id,
        tenant_id=1,
        phone='1234567890',
        status='active'
    )
    
    session.add(beneficiary)
    session.commit()
    
    return {
        'admin': admin_user,
        'trainer': trainer_user,
        'beneficiary_user': beneficiary_user,
        'beneficiary': beneficiary,
        'admin_id': admin_user.id,
        'trainer_id': trainer_user.id,
        'beneficiary_id': beneficiary.id
    }


class TestBeneficiariesAPI:
    """Test cases for beneficiaries API endpoints."""
    
    def test_get_beneficiaries_admin(self, client, setup_beneficiaries_data, app):
        """Test getting beneficiaries as admin."""
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/beneficiaries', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data
    
    def test_get_beneficiaries_trainer(self, client, setup_beneficiaries_data, app):
        """Test getting beneficiaries as trainer."""
        # Generate auth headers for trainer
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['trainer_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/beneficiaries', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
    
    def test_get_beneficiaries_unauthorized(self, client, setup_beneficiaries_data):
        """Test getting beneficiaries without authorization."""
        response = client.get('/api/beneficiaries')
        assert response.status_code == 401
    
    def test_get_beneficiary_by_id(self, client, setup_beneficiaries_data, app):
        """Test getting a specific beneficiary by ID."""
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        beneficiary_id = setup_beneficiaries_data['beneficiary_id']
        response = client.get(f'/api/beneficiaries/{beneficiary_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == beneficiary_id
    
    @patch('app.services.email_service.send_welcome_email')
    def test_create_beneficiary(self, mock_send_email, client, setup_beneficiaries_data, session, app):
        """Test creating a new beneficiary."""
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['admin_id'])
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Create a new user for the beneficiary
        suffix = str(uuid.uuid4())[:8]
        new_beneficiary_data = {
            'email': f'new_beneficiary_{suffix}@test.com',
            'first_name': 'New',
            'last_name': 'Beneficiary',
            'phone': '9876543210',
            'trainer_id': setup_beneficiaries_data['trainer_id'],
            'tenant_id': 1,
            'password': 'password123',
            'confirm_password': 'password123'
        }
        
        response = client.post(
            '/api/beneficiaries',
            data=json.dumps(new_beneficiary_data),
            headers=headers
        )
        
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.json}")
        
        assert response.status_code == 201
        data = response.json
        assert 'id' in data
        assert data['user']['email'] == new_beneficiary_data['email']
    
    def test_update_beneficiary(self, client, setup_beneficiaries_data, app):
        """Test updating a beneficiary."""
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['admin_id'])
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        beneficiary_id = setup_beneficiaries_data['beneficiary_id']
        update_data = {
            'status': 'inactive',
            'phone': '5555555555',
            'city': 'Updated City'
        }
        
        response = client.patch(
            f'/api/beneficiaries/{beneficiary_id}',
            data=json.dumps(update_data),
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['status'] == update_data['status']
    
    def test_delete_beneficiary(self, client, setup_beneficiaries_data, app):
        """Test deleting a beneficiary."""
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        beneficiary_id = setup_beneficiaries_data['beneficiary_id']
        response = client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=headers)
        
        assert response.status_code == 200
    
    def test_get_beneficiary_notes(self, client, setup_beneficiaries_data, app):
        """Test getting beneficiary notes."""
        # Generate auth headers for trainer
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['trainer_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        beneficiary_id = setup_beneficiaries_data['beneficiary_id']
        response = client.get(f'/api/beneficiaries/{beneficiary_id}/notes', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
    
    def test_create_beneficiary_note(self, client, setup_beneficiaries_data, app):
        """Test creating a note for a beneficiary."""
        # Generate auth headers for trainer
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['trainer_id'])
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        beneficiary_id = setup_beneficiaries_data['beneficiary_id']
        note_data = {
            'beneficiary_id': beneficiary_id,
            'content': 'Test note content',
            'type': 'general'
        }
        
        response = client.post(
            f'/api/beneficiaries/{beneficiary_id}/notes',
            data=json.dumps(note_data),
            headers=headers
        )
        
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.json}")
        
        assert response.status_code == 201
        data = response.json
        assert 'id' in data
        assert data['content'] == note_data['content']
    
    def test_update_beneficiary_note(self, client, setup_beneficiaries_data, session, app):
        """Test updating a beneficiary note."""
        # Create a test note first
        beneficiary_id = setup_beneficiaries_data['beneficiary_id']
        trainer_id = setup_beneficiaries_data['trainer_id']
        
        note = Note(
            beneficiary_id=beneficiary_id,
            user_id=trainer_id,
            content='Original content',
            type='general'
        )
        session.add(note)
        session.commit()
        note_id = note.id
        
        # Generate auth headers for trainer
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=trainer_id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        update_data = {
            'content': 'Updated content'
        }
        
        response = client.patch(
            f'/api/beneficiaries/notes/{note_id}',
            data=json.dumps(update_data),
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['content'] == update_data['content']
    
    def test_delete_beneficiary_note(self, client, setup_beneficiaries_data, session, app):
        """Test deleting a beneficiary note."""
        # Create a test note first
        beneficiary_id = setup_beneficiaries_data['beneficiary_id']
        trainer_id = setup_beneficiaries_data['trainer_id']
        
        note = Note(
            beneficiary_id=beneficiary_id,
            user_id=trainer_id,
            content='Test content',
            type='general'
        )
        session.add(note)
        session.commit()
        note_id = note.id
        
        # Generate auth headers for trainer
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=trainer_id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.delete(
            f'/api/beneficiaries/notes/{note_id}',
            headers=headers
        )
        
        assert response.status_code == 200
    
    
    def test_role_based_access(self, client, setup_beneficiaries_data, app):
        """Test role-based access control for beneficiaries."""
        # Test student trying to access beneficiaries (should fail)
        from flask_jwt_extended import create_access_token
        beneficiary_user_id = setup_beneficiaries_data['beneficiary_user'].id
        access_token = create_access_token(identity=beneficiary_user_id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/beneficiaries', headers=headers)
        assert response.status_code == 403
    
    def test_search_beneficiaries(self, client, setup_beneficiaries_data, app):
        """Test searching beneficiaries."""
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Search by name
        response = client.get('/api/beneficiaries?search=Beneficiary', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
    
    def test_filter_beneficiaries_by_status(self, client, setup_beneficiaries_data, app):
        """Test filtering beneficiaries by status."""
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Filter by status
        response = client.get('/api/beneficiaries?status=active', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
    
    def test_pagination(self, client, setup_beneficiaries_data, app):
        """Test pagination of beneficiaries."""
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_beneficiaries_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Test pagination
        response = client.get('/api/beneficiaries?page=1&per_page=10', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        assert data['page'] == 1
        assert data['per_page'] == 10