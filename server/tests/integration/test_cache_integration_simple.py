"""Integration tests for caching functionality."""

import unittest
import json
import time
from datetime import datetime

from app import create_app
from app.extensions import db
from app.models import User, Tenant, Beneficiary
from app.core.cache_manager import cache_manager
from app.core.security import SecurityManager
from flask_jwt_extended import create_access_token


class TestCacheIntegration(unittest.TestCase):
    """Test cache functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('config.TestingConfig')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Create tables
        db.create_all()
        
        # Clear cache
        cache_manager.clear_all()
        
        # Create test tenant and user
        self.tenant = Tenant(
            name='Test Tenant',
            slug='test',
            email='test@tenant.com',
            is_active=True
        )
        db.session.add(self.tenant)
        
        security_manager = SecurityManager()
        self.user = User(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password_hash=security_manager.hash_password('Test123!'),
            role='super_admin',
            is_active=True,
            tenant_id=self.tenant.id
        )
        db.session.add(self.user)
        
        # Create test beneficiary user
        beneficiary_user = User(
            email='beneficiary@test.com',
            username='beneficiary',
            first_name='Test',
            last_name='Beneficiary',
            password_hash=security_manager.hash_password('Test123!'),
            role='student',
            is_active=True,
            tenant_id=self.tenant.id
        )
        db.session.add(beneficiary_user)
        db.session.commit()
        
        # Create test beneficiary profile
        self.beneficiary = Beneficiary(
            user_id=beneficiary_user.id,
            tenant_id=self.tenant.id,
            birth_date=datetime.strptime('1990-01-01', '%Y-%m-%d'),
            status='active'
        )
        db.session.add(self.beneficiary)
        
        db.session.commit()
        
        # Get auth token using flask-jwt-extended
        with self.app.app_context():
            self.token = create_access_token(identity=self.user.id)
        print(f"Generated token for user {self.user.id}: {self.token[:20]}...")
        
    def tearDown(self):
        """Clean up after tests."""
        cache_manager.clear_all()
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
    def get_auth_headers(self):
        """Get authorization headers."""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def test_beneficiaries_list_caching(self):
        """Test that beneficiaries list is cached properly."""
        # First request - should hit the database
        response1 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        if response1.status_code != 200:
            print(f"Response status: {response1.status_code}")
            print(f"Response data: {response1.data}")
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.data)
        
        # Check cache headers
        self.assertIn('X-Cache', response1.headers)
        self.assertEqual(response1.headers['X-Cache'], 'MISS')
        
        # Second request - should hit cache
        response2 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.data)
        
        # Check cache headers
        self.assertEqual(response2.headers['X-Cache'], 'HIT')
        
        # Data should be identical
        self.assertEqual(data1, data2)
    
    def test_beneficiary_detail_caching(self):
        """Test that beneficiary detail is cached properly."""
        beneficiary_id = self.beneficiary.id
        
        # First request
        response1 = self.client.get(
            f'/api/v2/cached/beneficiaries/{beneficiary_id}',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response1.status_code, 200)
        
        # Check cache miss
        self.assertEqual(response1.headers['X-Cache'], 'MISS')
        
        # Second request
        response2 = self.client.get(
            f'/api/v2/cached/beneficiaries/{beneficiary_id}',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response2.status_code, 200)
        
        # Check cache hit
        self.assertEqual(response2.headers['X-Cache'], 'HIT')
    
    def test_cache_invalidation_on_update(self):
        """Test that cache is invalidated when data is updated."""
        beneficiary_id = self.beneficiary.id
        
        # Get initial data (populate cache)
        response1 = self.client.get(
            f'/api/v2/cached/beneficiaries/{beneficiary_id}',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.data)
        
        # Update beneficiary
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        update_response = self.client.put(
            f'/api/v2/cached/beneficiaries/{beneficiary_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        self.assertEqual(update_response.status_code, 200)
        
        # Get data again - should be fresh from database
        response2 = self.client.get(
            f'/api/v2/cached/beneficiaries/{beneficiary_id}',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.data)
        
        # Check cache was invalidated (miss)
        self.assertEqual(response2.headers['X-Cache'], 'MISS')
        
        # Data should be different
        self.assertNotEqual(data1['beneficiary']['first_name'], data2['beneficiary']['first_name'])
        self.assertEqual(data2['beneficiary']['first_name'], 'Updated')
    
    def test_conditional_request_with_etag(self):
        """Test conditional requests using ETags."""
        # First request to get ETag
        response1 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response1.status_code, 200)
        etag = response1.headers.get('ETag')
        self.assertIsNotNone(etag)
        
        # Second request with If-None-Match
        headers = self.get_auth_headers()
        headers['If-None-Match'] = etag
        response2 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=headers
        )
        
        # Should return 304 Not Modified
        self.assertEqual(response2.status_code, 304)
        self.assertEqual(response2.data, b'')
    
    def test_cache_control_headers(self):
        """Test that proper Cache-Control headers are set."""
        response = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response.status_code, 200)
        
        # Check Cache-Control header
        cache_control = response.headers.get('Cache-Control')
        self.assertIsNotNone(cache_control)
        self.assertIn('max-age=300', cache_control)
        self.assertIn('private', cache_control)
    
    def test_cache_ttl_expiration(self):
        """Test that cache expires after TTL."""
        # Use a short TTL endpoint for testing
        response1 = self.client.get(
            '/api/v2/cached/test-short-ttl',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.headers['X-Cache'], 'MISS')
        
        # Immediate second request - should hit cache
        response2 = self.client.get(
            '/api/v2/cached/test-short-ttl',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.headers['X-Cache'], 'HIT')
        
        # Wait for TTL to expire
        time.sleep(3)
        
        # Third request - should miss cache
        response3 = self.client.get(
            '/api/v2/cached/test-short-ttl',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response3.headers['X-Cache'], 'MISS')


if __name__ == '__main__':
    unittest.main()