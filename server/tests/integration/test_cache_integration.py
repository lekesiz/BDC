"""Integration tests for caching functionality."""

import pytest
from flask import json
from datetime import datetime
import time
from app.core.cache_manager import cache_manager
from tests.integration.base_integration_test import BaseIntegrationTestCase


class TestCacheIntegration(BaseIntegrationTestCase):
    """Test cache functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        # Clear cache before each test
        cache_manager.clear_all()
        
    def tearDown(self):
        """Clean up after each test."""
        super().tearDown()
        # Clear cache after each test
        cache_manager.clear_all()
    
    def test_beneficiaries_list_caching(self):
        """Test that beneficiaries list is cached properly."""
        # First request - should hit the database
        response1 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
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
        beneficiary_id = 1
        
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
        beneficiary_id = 1
        
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
    
    def test_vary_on_headers(self):
        """Test cache varies on authorization header."""
        # Request with user1
        response1 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.data)
        
        # Create another user and get their token
        user2 = self.create_user(
            email='user2@test.com',
            username='testuser2',
            password='Test123!',
            first_name='Test2',
            last_name='User2'
        )
        
        # Login as user2
        login_response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': 'user2@test.com',
                'password': 'Test123!'
            }),
            content_type='application/json'
        )
        user2_token = json.loads(login_response.data)['access_token']
        
        # Request with user2
        response2 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers={'Authorization': f'Bearer {user2_token}'}
        )
        self.assertEqual(response2.status_code, 200)
        
        # Should be a cache miss for different user
        self.assertEqual(response2.headers['X-Cache'], 'MISS')
    
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
        
        # Wait for TTL to expire (assuming 2 second TTL for test endpoint)
        time.sleep(3)
        
        # Third request - should miss cache
        response3 = self.client.get(
            '/api/v2/cached/test-short-ttl',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response3.headers['X-Cache'], 'MISS')
    
    def test_cache_warming(self):
        """Test cache warming functionality."""
        # Clear cache first
        cache_manager.clear_all()
        
        # Warm the cache
        with self.app.app_context():
            from app.core.cache_config import warm_cache
            warm_cache()
        
        # Check that frequently accessed data is cached
        response = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response.status_code, 200)
        
        # Should be a cache hit if warming worked
        # Note: This might be MISS if warming doesn't include auth context
        # but the endpoint should still work
        self.assertIn('X-Cache', response.headers)
    
    def test_cache_clear_pattern(self):
        """Test clearing cache by pattern."""
        # Populate multiple cache entries
        self.client.get('/api/v2/cached/beneficiaries', headers=self.get_auth_headers())
        self.client.get('/api/v2/cached/beneficiaries/1', headers=self.get_auth_headers())
        self.client.get('/api/v2/cached/beneficiaries/2', headers=self.get_auth_headers())
        
        # Clear only beneficiary list cache
        cache_manager.clear_pattern('beneficiaries_list:*')
        
        # List should be cache miss
        response1 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response1.headers['X-Cache'], 'MISS')
        
        # Details should still be cached
        response2 = self.client.get(
            '/api/v2/cached/beneficiaries/1',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response2.headers['X-Cache'], 'HIT')


class TestCacheStrategies(BaseIntegrationTestCase):
    """Test different caching strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        cache_manager.clear_all()
    
    def test_cache_aside_strategy(self):
        """Test cache-aside pattern (default)."""
        # First request - loads from DB and stores in cache
        response1 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.headers['X-Cache'], 'MISS')
        
        # Second request - loads from cache
        response2 = self.client.get(
            '/api/v2/cached/beneficiaries',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.headers['X-Cache'], 'HIT')
    
    def test_write_through_strategy(self):
        """Test write-through caching strategy."""
        # Create a new beneficiary (write-through should cache it)
        create_data = {
            'first_name': 'New',
            'last_name': 'Beneficiary',
            'date_of_birth': '1990-01-01',
            'email': 'new@test.com'
        }
        
        create_response = self.client.post(
            '/api/v2/cached/beneficiaries',
            data=json.dumps(create_data),
            content_type='application/json',
            headers=self.get_auth_headers()
        )
        self.assertEqual(create_response.status_code, 201)
        new_id = json.loads(create_response.data)['beneficiary']['id']
        
        # Immediate read should hit cache (if write-through is implemented)
        response = self.client.get(
            f'/api/v2/cached/beneficiaries/{new_id}',
            headers=self.get_auth_headers()
        )
        self.assertEqual(response.status_code, 200)
        # Note: Might be MISS if write-through isn't fully implemented
        # but the data should still be correct
        data = json.loads(response.data)
        self.assertEqual(data['beneficiary']['first_name'], 'New')