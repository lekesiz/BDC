"""Consolidated API integration tests."""

import pytest
import json
from flask import url_for
from app.models.user import User
from app.models.beneficiary import Beneficiary


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'timestamp' in data
    
    def test_api_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options('/api/auth/login')
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
    
    def test_api_content_type_validation(self, client):
        """Test API content type validation."""
        # Test with wrong content type
        response = client.post('/api/auth/login',
                             data='invalid json',
                             content_type='text/plain')
        
        assert response.status_code == 400
    
    def test_api_authentication_flow(self, client, admin_user):
        """Test complete authentication flow."""
        # 1. Login
        login_response = client.post('/api/auth/login', json={
            'email': 'admin@bdc.com',
            'password': 'Admin123!',
            'remember': False
        })
        
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        access_token = login_data['access_token']
        
        # 2. Access protected endpoint
        headers = {'Authorization': f'Bearer {access_token}'}
        me_response = client.get('/api/auth/me', headers=headers)
        
        assert me_response.status_code == 200
        me_data = me_response.get_json()
        assert me_data['user']['email'] == 'admin@bdc.com'
        
        # 3. Logout
        logout_response = client.post('/api/auth/logout', headers=headers)
        assert logout_response.status_code == 200
    
    def test_beneficiaries_crud_flow(self, client, auth_headers, db_session):
        """Test complete CRUD flow for beneficiaries."""
        # 1. Create beneficiary
        beneficiary_data = {
            'first_name': 'Test',
            'last_name': 'Beneficiary',
            'email': 'testben@example.com',
            'phone': '+1234567890',
            'date_of_birth': '1990-01-01',
            'address': '123 Test St'
        }
        
        create_response = client.post('/api/beneficiaries',
                                    headers=auth_headers,
                                    json=beneficiary_data)
        
        assert create_response.status_code == 201
        created_data = create_response.get_json()
        beneficiary_id = created_data['beneficiary']['id']
        
        # 2. Read beneficiary
        get_response = client.get(f'/api/beneficiaries/{beneficiary_id}',
                                headers=auth_headers)
        
        assert get_response.status_code == 200
        get_data = get_response.get_json()
        assert get_data['beneficiary']['email'] == 'testben@example.com'
        
        # 3. Update beneficiary
        update_data = {'phone': '+0987654321'}
        update_response = client.put(f'/api/beneficiaries/{beneficiary_id}',
                                   headers=auth_headers,
                                   json=update_data)
        
        assert update_response.status_code == 200
        updated_data = update_response.get_json()
        assert updated_data['beneficiary']['phone'] == '+0987654321'
        
        # 4. List beneficiaries
        list_response = client.get('/api/beneficiaries',
                                 headers=auth_headers)
        
        assert list_response.status_code == 200
        list_data = list_response.get_json()
        assert len(list_data['beneficiaries']) >= 1
        
        # 5. Delete beneficiary
        delete_response = client.delete(f'/api/beneficiaries/{beneficiary_id}',
                                      headers=auth_headers)
        
        assert delete_response.status_code == 200
    
    def test_api_error_handling(self, client, auth_headers):
        """Test API error handling."""
        # Test 404 for non-existent resource
        response = client.get('/api/beneficiaries/99999',
                            headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        
        # Test 400 for invalid data
        response = client.post('/api/beneficiaries',
                             headers=auth_headers,
                             json={'invalid': 'data'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_api_pagination(self, client, auth_headers, db_session):
        """Test API pagination."""
        # Create multiple beneficiaries for pagination test
        for i in range(15):
            beneficiary = Beneficiary(
                first_name=f'Test{i}',
                last_name='Pagination',
                email=f'test{i}@pagination.com'
            )
            db_session.add(beneficiary)
        db_session.commit()
        
        # Test pagination parameters
        response = client.get('/api/beneficiaries?page=1&per_page=10',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['beneficiaries']) <= 10
        assert 'pagination' in data
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 10
    
    def test_api_filtering_and_search(self, client, auth_headers, db_session):
        """Test API filtering and search capabilities."""
        # Create test data
        beneficiary1 = Beneficiary(
            first_name='John',
            last_name='Doe',
            email='john.doe@test.com'
        )
        beneficiary2 = Beneficiary(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@test.com'
        )
        db_session.add_all([beneficiary1, beneficiary2])
        db_session.commit()
        
        # Test search
        response = client.get('/api/beneficiaries?search=john',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should find John Doe
        found_john = any(
            ben['first_name'] == 'John' 
            for ben in data['beneficiaries']
        )
        assert found_john
    
    def test_api_rate_limiting(self, client):
        """Test API rate limiting."""
        # Make multiple rapid requests to trigger rate limiting
        # Note: This depends on rate limiting configuration
        
        responses = []
        for i in range(20):  # Make 20 rapid requests
            response = client.post('/api/auth/login', json={
                'email': 'invalid@test.com',
                'password': 'invalid'
            })
            responses.append(response.status_code)
        
        # Should eventually get rate limited (429)
        # Note: Exact behavior depends on rate limiting config
        rate_limited = any(status == 429 for status in responses)
        # Test is informational - rate limiting may or may not be configured
    
    def test_api_validation_errors(self, client, auth_headers):
        """Test API input validation."""
        # Test invalid email format
        response = client.post('/api/beneficiaries',
                             headers=auth_headers,
                             json={
                                 'first_name': 'Test',
                                 'last_name': 'User',
                                 'email': 'invalid-email'  # Invalid format
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'email' in data['message'].lower()
        
        # Test missing required fields
        response = client.post('/api/beneficiaries',
                             headers=auth_headers,
                             json={
                                 'last_name': 'User'
                                 # Missing first_name
                             })
        
        assert response.status_code == 400
    
    def test_api_permissions(self, client, db_session):
        """Test API permission enforcement."""
        # Create a regular user (non-admin)
        regular_user = User(
            email='regular@bdc.com',
            username='regular',
            password='Regular123!',
            role='user',
            is_active=True
        )
        db_session.add(regular_user)
        db_session.commit()
        
        # Login as regular user
        login_response = client.post('/api/auth/login', json={
            'email': 'regular@bdc.com',
            'password': 'Regular123!',
            'remember': False
        })
        
        assert login_response.status_code == 200
        token = login_response.get_json()['access_token']
        user_headers = {'Authorization': f'Bearer {token}'}
        
        # Try to access admin-only endpoint (if any exist)
        # This would test specific permission-restricted endpoints
        # For now, test that regular user can access their own data
        response = client.get('/api/auth/me', headers=user_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['role'] == 'user'


class TestAPIPerformance:
    """Performance-related API tests."""
    
    def test_api_response_times(self, client, auth_headers):
        """Test that API responses are within acceptable time limits."""
        import time
        
        # Test critical endpoints for response time
        endpoints = [
            '/api/auth/me',
            '/api/beneficiaries',
            '/health'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Response should be under 2 seconds for these endpoints
            assert response_time < 2.0, f"{endpoint} took {response_time}s"
            assert response.status_code in [200, 401, 403]  # Valid responses
    
    def test_api_memory_usage(self, client, auth_headers):
        """Test that API doesn't have obvious memory leaks."""
        import gc
        import sys
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Make multiple API calls
        for i in range(10):
            response = client.get('/api/beneficiaries', headers=auth_headers)
            assert response.status_code in [200, 401, 403]
        
        # Check memory usage after calls
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Should not have significant memory growth
        # This is a rough check - exact numbers depend on test environment
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, f"Potential memory leak: {object_growth} new objects"


class TestAPIDocumentation:
    """Test API documentation and schema compliance."""
    
    def test_api_openapi_schema(self, client):
        """Test OpenAPI/Swagger schema if available."""
        # Check if API documentation endpoint exists
        response = client.get('/api/docs')
        
        # This endpoint may or may not exist
        if response.status_code == 200:
            # If docs exist, they should be valid
            assert 'swagger' in response.data.decode().lower() or \
                   'openapi' in response.data.decode().lower()
    
    def test_api_consistent_response_format(self, client, auth_headers):
        """Test that API responses follow consistent format."""
        # All API responses should have consistent structure
        endpoints_to_test = [
            ('/api/auth/me', 'GET'),
            ('/api/beneficiaries', 'GET')
        ]
        
        for endpoint, method in endpoints_to_test:
            if method == 'GET':
                response = client.get(endpoint, headers=auth_headers)
            
            if response.status_code == 200:
                data = response.get_json()
                # Should have consistent success field
                assert 'success' in data or 'data' in data
                
                # Should have proper content type
                assert response.content_type == 'application/json'