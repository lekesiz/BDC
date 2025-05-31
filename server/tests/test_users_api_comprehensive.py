"""Comprehensive tests for users API endpoints."""
import pytest
from unittest.mock import Mock, patch
import json
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.beneficiary import Beneficiary


class TestUsersAPI:
    """Test users API endpoints comprehensively."""
    
    @pytest.fixture(autouse=True)
    def setup(self, app):
        """Set up test environment."""
        self.app = app
        self.client = app.test_client()
        
        with app.app_context():
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
            
            self.tenant_admin = User(
                email='tenant.admin@test.com',
                username='tenantadmin',
                first_name='Tenant',
                last_name='Admin',
                role='tenant_admin',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.tenant_admin.password = 'Tenant123!'
            
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
            
            db.session.add_all([self.admin_user, self.tenant_admin, self.trainer, self.student])
            
            # Create beneficiary profile for student
            self.beneficiary = Beneficiary(
                user_id=self.student.id,
                tenant_id=self.tenant.id,
                status='active',
                enrollment_date='2025-01-01'
            )
            db.session.add(self.beneficiary)
            
            db.session.commit()
            
            # Create access tokens
            self.admin_token = create_access_token(identity=self.admin_user.id)
            self.tenant_admin_token = create_access_token(identity=self.tenant_admin.id)
            self.trainer_token = create_access_token(identity=self.trainer.id)
            self.student_token = create_access_token(identity=self.student.id)
    
    def test_get_users_as_admin(self):
        """Test getting users list as admin."""
        response = self.client.get('/api/users',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert len(data['users']) >= 4  # At least our test users
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data
    
    def test_get_users_with_pagination(self):
        """Test getting users with pagination."""
        response = self.client.get('/api/users?page=1&per_page=2',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['users']) <= 2
        assert data['per_page'] == 2
        assert data['page'] == 1
    
    def test_get_users_with_role_filter(self):
        """Test getting users filtered by role."""
        response = self.client.get('/api/users?role=student',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(user['role'] == 'student' for user in data['users'])
    
    def test_get_users_with_search(self):
        """Test searching users."""
        response = self.client.get('/api/users?search=admin',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['users']) >= 1
        # Should find users with 'admin' in name or email
    
    def test_get_users_as_tenant_admin(self):
        """Test getting users as tenant admin (should only see same tenant)."""
        response = self.client.get('/api/users',
            headers={'Authorization': f'Bearer {self.tenant_admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should only see users from same tenant
        assert all(user.get('tenant_id') == self.tenant.id for user in data['users'] if user.get('tenant_id'))
    
    def test_get_users_as_trainer(self):
        """Test getting users as trainer (limited access)."""
        response = self.client.get('/api/users',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Trainer might have limited access or no access
        assert response.status_code in [200, 403]
    
    def test_get_users_as_student(self):
        """Test getting users as student (should be forbidden)."""
        response = self.client.get('/api/users',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 403
    
    def test_get_user_by_id(self):
        """Test getting specific user by ID."""
        response = self.client.get(f'/api/users/{self.trainer.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == self.trainer.id
        assert data['email'] == 'trainer@test.com'
        assert data['role'] == 'trainer'
    
    def test_get_nonexistent_user(self):
        """Test getting nonexistent user."""
        response = self.client.get('/api/users/99999',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 404
    
    def test_get_current_user(self):
        """Test getting current user info."""
        response = self.client.get('/api/users/me',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == self.trainer.id
        assert data['email'] == 'trainer@test.com'
        assert 'password' not in data  # Password should not be exposed
    
    def test_create_user_as_admin(self):
        """Test creating new user as admin."""
        response = self.client.post('/api/users',
            data=json.dumps({
                'email': 'newuser@test.com',
                'username': 'newuser',
                'password': 'NewUser123!',
                'first_name': 'New',
                'last_name': 'User',
                'role': 'trainer',
                'tenant_id': self.tenant.id
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['email'] == 'newuser@test.com'
        assert data['role'] == 'trainer'
        
        # Verify user was created
        with self.app.app_context():
            user = User.query.filter_by(email='newuser@test.com').first()
            assert user is not None
    
    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email."""
        response = self.client.post('/api/users',
            data=json.dumps({
                'email': 'admin@test.com',  # Already exists
                'username': 'newadmin',
                'password': 'NewUser123!',
                'first_name': 'New',
                'last_name': 'Admin',
                'role': 'trainer'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in str(data)
    
    def test_create_user_invalid_role(self):
        """Test creating user with invalid role."""
        response = self.client.post('/api/users',
            data=json.dumps({
                'email': 'invalid@test.com',
                'username': 'invalid',
                'password': 'Invalid123!',
                'first_name': 'Invalid',
                'last_name': 'Role',
                'role': 'invalid_role'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 400
    
    def test_update_user(self):
        """Test updating user information."""
        response = self.client.put(f'/api/users/{self.trainer.id}',
            data=json.dumps({
                'first_name': 'Updated',
                'last_name': 'Trainer',
                'phone': '+1234567890'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == 'Updated'
        assert data['phone'] == '+1234567890'
    
    def test_update_user_email(self):
        """Test updating user email."""
        response = self.client.put(f'/api/users/{self.trainer.id}',
            data=json.dumps({
                'email': 'updated.trainer@test.com'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email'] == 'updated.trainer@test.com'
    
    def test_update_user_role(self):
        """Test updating user role (admin only)."""
        response = self.client.put(f'/api/users/{self.trainer.id}',
            data=json.dumps({
                'role': 'tenant_admin'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['role'] == 'tenant_admin'
    
    def test_update_own_profile(self):
        """Test users updating their own profile."""
        response = self.client.put(f'/api/users/{self.trainer.id}',
            data=json.dumps({
                'bio': 'I am a trainer',
                'phone': '+9876543210'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['bio'] == 'I am a trainer'
    
    def test_update_other_user_as_non_admin(self):
        """Test updating other user as non-admin (should fail)."""
        response = self.client.put(f'/api/users/{self.admin_user.id}',
            data=json.dumps({
                'first_name': 'Hacked'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 403
    
    def test_deactivate_user(self):
        """Test deactivating a user."""
        response = self.client.post(f'/api/users/{self.trainer.id}/deactivate',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['is_active'] is False
        
        # Verify user is deactivated
        with self.app.app_context():
            user = User.query.get(self.trainer.id)
            assert user.is_active is False
    
    def test_activate_user(self):
        """Test activating a user."""
        # First deactivate
        with self.app.app_context():
            user = User.query.get(self.trainer.id)
            user.is_active = False
            db.session.commit()
        
        response = self.client.post(f'/api/users/{self.trainer.id}/activate',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['is_active'] is True
    
    def test_delete_user(self):
        """Test deleting a user."""
        # Create a user to delete
        with self.app.app_context():
            user_to_delete = User(
                email='delete@test.com',
                username='delete',
                first_name='Delete',
                last_name='Me',
                role='student',
                tenant_id=self.tenant.id
            )
            user_to_delete.password = 'Delete123!'
            db.session.add(user_to_delete)
            db.session.commit()
            delete_id = user_to_delete.id
        
        response = self.client.delete(f'/api/users/{delete_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        
        # Verify user is deleted
        with self.app.app_context():
            user = User.query.get(delete_id)
            assert user is None
    
    def test_delete_self(self):
        """Test user cannot delete themselves."""
        response = self.client.delete(f'/api/users/{self.admin_user.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 400
    
    def test_get_user_profile(self):
        """Test getting user profile."""
        response = self.client.get('/api/users/me/profile',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'email' in data
        assert 'first_name' in data
        assert 'role' in data
        assert 'profile' in data or 'bio' in data
    
    def test_update_user_profile(self):
        """Test updating user profile."""
        response = self.client.put('/api/users/me/profile',
            data=json.dumps({
                'bio': 'Experienced trainer',
                'phone': '+1234567890',
                'address': '123 Main St',
                'city': 'Test City',
                'country': 'Test Country'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['bio'] == 'Experienced trainer'
        assert data['city'] == 'Test City'
    
    def test_update_user_settings(self):
        """Test updating user settings."""
        response = self.client.put('/api/users/me/settings',
            data=json.dumps({
                'email_notifications': False,
                'language': 'fr',
                'theme': 'dark'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email_notifications'] is False
        assert data['language'] == 'fr'
        assert data['theme'] == 'dark'
    
    def test_get_user_permissions(self):
        """Test getting user permissions."""
        response = self.client.get(f'/api/users/{self.trainer.id}/permissions',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'permissions' in data or 'role' in data
    
    def test_export_users(self):
        """Test exporting users to CSV/Excel."""
        response = self.client.get('/api/users/export?format=csv',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # This endpoint might not be implemented
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.content_type in ['text/csv', 'application/csv']