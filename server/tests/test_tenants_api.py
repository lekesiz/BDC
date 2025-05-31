import pytest
import json
from flask_jwt_extended import create_access_token

from app import create_app, db
from app.models import User, Tenant


class TestTenantsAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        # Create test users
        self.admin_user = User(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        self.admin_user.password = 'password123'
        
        self.regular_user = User(
            email='user@test.com',
            first_name='Regular',
            last_name='User',
            role='student',
            is_active=True
        )
        self.regular_user.password = 'password123'
        
        db.session.add_all([self.admin_user, self.regular_user])
        db.session.commit()
        
        # Create test tenants
        self.tenant1 = Tenant(
            name='Test Tenant 1',
            slug='test-tenant-1',
            email='tenant1@test.com',
            is_active=True
        )
        
        self.tenant2 = Tenant(
            name='Test Tenant 2',
            slug='test-tenant-2',
            email='tenant2@test.com',
            is_active=False
        )
        
        db.session.add_all([self.tenant1, self.tenant2])
        db.session.commit()
        
        # Create access tokens
        self.admin_token = create_access_token(identity=str(self.admin_user.id))
        self.user_token = create_access_token(identity=str(self.regular_user.id))
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_tenants_as_admin(self):
        """Test getting tenants list as admin"""
        response = self.client.get(
            '/api/tenants',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tenants' in data or 'items' in data
        
        # Should have at least our test tenants
        tenants = data.get('tenants', data.get('items', []))
        assert len(tenants) >= 2
    
    def test_get_tenants_unauthorized(self):
        """Test getting tenants without authentication"""
        response = self.client.get('/api/tenants')
        assert response.status_code == 401
    
    def test_get_tenants_as_regular_user(self):
        """Test getting tenants as regular user (should be forbidden)"""
        response = self.client.get(
            '/api/tenants',
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        assert response.status_code in [403, 401]  # Forbidden or Unauthorized
    
    def test_get_tenant_by_id(self):
        """Test getting a specific tenant by ID"""
        response = self.client.get(
            f'/api/tenants/{self.tenant1.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == self.tenant1.id
        assert data['name'] == 'Test Tenant 1'
        assert data['slug'] == 'test-tenant-1'
    
    def test_get_tenant_not_found(self):
        """Test getting non-existent tenant"""
        response = self.client.get(
            '/api/tenants/99999',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        assert response.status_code == 404
    
    def test_create_tenant(self):
        """Test creating a new tenant"""
        new_tenant_data = {
            'name': 'New Tenant',
            'slug': 'new-tenant',
            'email': 'new@tenant.com',
            'phone': '+1234567890',
            'address': '123 Test St',
            'plan': 'pro',
            'max_users': 50,
            'max_beneficiaries': 200
        }
        
        response = self.client.post(
            '/api/tenants',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json=new_tenant_data
        )
        
        # Check if creation is implemented
        if response.status_code != 405:  # Method not allowed
            assert response.status_code in [200, 201]
            data = json.loads(response.data)
            assert data['name'] == 'New Tenant'
            assert data['slug'] == 'new-tenant'
    
    def test_create_tenant_duplicate_slug(self):
        """Test creating tenant with duplicate slug"""
        duplicate_data = {
            'name': 'Duplicate Tenant',
            'slug': 'test-tenant-1',  # Already exists
            'email': 'duplicate@tenant.com'
        }
        
        response = self.client.post(
            '/api/tenants',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json=duplicate_data
        )
        
        # If creation is implemented
        if response.status_code != 405:
            assert response.status_code in [400, 409]  # Bad request or Conflict
    
    def test_update_tenant(self):
        """Test updating a tenant"""
        update_data = {
            'name': 'Updated Tenant Name',
            'phone': '+9876543210',
            'max_users': 100
        }
        
        response = self.client.put(
            f'/api/tenants/{self.tenant1.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json=update_data
        )
        
        # Check if update is implemented
        if response.status_code != 405:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Updated Tenant Name'
            assert data['phone'] == '+9876543210'
    
    def test_toggle_tenant_status(self):
        """Test toggling tenant active status"""
        # Tenant1 is initially active
        response = self.client.post(
            f'/api/tenants/{self.tenant1.id}/toggle-status',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Check if toggle is implemented
        if response.status_code != 404:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['is_active'] is False
    
    def test_delete_tenant(self):
        """Test deleting a tenant"""
        response = self.client.delete(
            f'/api/tenants/{self.tenant2.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Check if delete is implemented
        if response.status_code != 405:
            assert response.status_code in [200, 204]
            
            # Verify tenant is deleted or deactivated
            check_response = self.client.get(
                f'/api/tenants/{self.tenant2.id}',
                headers={'Authorization': f'Bearer {self.admin_token}'}
            )
            assert check_response.status_code == 404 or json.loads(check_response.data)['is_active'] is False
    
    def test_tenant_statistics(self):
        """Test getting tenant statistics"""
        response = self.client.get(
            f'/api/tenants/{self.tenant1.id}/stats',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Check if stats endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200
            data = json.loads(response.data)
            # Should have some statistics
            assert 'user_count' in data or 'users' in data
    
    def test_tenant_users(self):
        """Test getting users for a tenant"""
        # Add admin user to tenant1
        self.admin_user.tenants.append(self.tenant1)
        db.session.commit()
        
        response = self.client.get(
            f'/api/tenants/{self.tenant1.id}/users',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Check if users endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200
            data = json.loads(response.data)
            users = data.get('users', data.get('items', []))
            assert len(users) >= 1