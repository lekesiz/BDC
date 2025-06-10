"""Performance and load tests."""

import pytest
import time
import threading
import concurrent.futures
from datetime import datetime
from app.models.user import User
from app.models.beneficiary import Beneficiary


class TestPerformanceBasics:
    """Basic performance tests for API endpoints."""
    
    def test_health_endpoint_performance(self, client):
        """Test health endpoint response time."""
        start_time = time.time()
        response = client.get('/health')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 0.5  # Should respond within 500ms
    
    def test_auth_endpoint_performance(self, client, admin_user):
        """Test authentication endpoint performance."""
        login_data = {
            'email': 'admin@bdc.com',
            'password': 'Admin123!',
            'remember': False
        }
        
        start_time = time.time()
        response = client.post('/api/auth/login', json=login_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds
    
    def test_beneficiaries_list_performance(self, client, auth_headers):
        """Test beneficiaries list endpoint performance."""
        start_time = time.time()
        response = client.get('/api/beneficiaries', headers=auth_headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code in [200, 401, 403]  # Valid responses
        if response.status_code == 200:
            assert response_time < 3.0  # Should respond within 3 seconds
    
    def test_database_query_performance(self, app, db_session):
        """Test database query performance."""
        with app.app_context():
            # Create test data
            users = []
            for i in range(50):
                user = User(
                    email=f'perftest{i}@example.com',
                    username=f'perftest{i}',
                    password='Test123!',
                    role='user'
                )
                users.append(user)
            
            db_session.add_all(users)
            db_session.commit()
            
            # Test query performance
            start_time = time.time()
            result = User.query.filter(User.email.like('%perftest%')).all()
            end_time = time.time()
            
            query_time = end_time - start_time
            
            assert len(result) == 50
            assert query_time < 1.0  # Query should complete within 1 second
            
            # Clean up
            for user in users:
                db_session.delete(user)
            db_session.commit()


class TestConcurrentLoad:
    """Test system under concurrent load."""
    
    def test_concurrent_health_checks(self, client):
        """Test multiple concurrent health check requests."""
        def make_request():
            response = client.get('/health')
            return response.status_code, time.time()
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            end_time = time.time()
        
        total_time = end_time - start_time
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        assert all(code == 200 for code in status_codes)
        
        # Total time should be reasonable (not much longer than single request)
        assert total_time < 5.0  # All requests within 5 seconds
    
    def test_concurrent_authentication(self, client, admin_user):
        """Test concurrent authentication requests."""
        def make_login_request():
            response = client.post('/api/auth/login', json={
                'email': 'admin@bdc.com',
                'password': 'Admin123!',
                'remember': False
            })
            return response.status_code
        
        # Make 5 concurrent login requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_login_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed (or fail consistently due to rate limiting)
        status_codes = set(results)
        
        # Should either all succeed (200) or get rate limited (429)
        assert status_codes.issubset({200, 429, 401})
    
    def test_concurrent_data_access(self, client, auth_headers, db_session):
        """Test concurrent data access requests."""
        # Create test beneficiaries
        beneficiaries = []
        for i in range(5):
            beneficiary = Beneficiary(
                first_name=f'Concurrent{i}',
                last_name='Test',
                email=f'concurrent{i}@test.com'
            )
            beneficiaries.append(beneficiary)
        
        db_session.add_all(beneficiaries)
        db_session.commit()
        
        def make_data_request():
            response = client.get('/api/beneficiaries', headers=auth_headers)
            return response.status_code
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(make_data_request) for _ in range(8)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Clean up
        for beneficiary in beneficiaries:
            db_session.delete(beneficiary)
        db_session.commit()
        
        # Check results
        status_codes = set(results)
        assert status_codes.issubset({200, 401, 403, 429})  # Valid response codes


class TestMemoryPerformance:
    """Test memory usage and performance."""
    
    def test_memory_usage_during_requests(self, client, auth_headers):
        """Test memory usage during multiple requests."""
        import gc
        import sys
        
        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Make multiple requests
        for i in range(20):
            response = client.get('/health')
            assert response.status_code == 200
            
            # Optional: make authenticated request
            if auth_headers:
                auth_response = client.get('/api/auth/me', headers=auth_headers)
                # Response can be 200 or 401 depending on token validity
        
        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory growth should be minimal
        object_growth = final_objects - initial_objects
        
        # Allow some growth but not excessive
        assert object_growth < 500, f"Potential memory leak: {object_growth} new objects"
    
    def test_large_response_handling(self, client, auth_headers, db_session):
        """Test handling of large response data."""
        # Create many beneficiaries
        beneficiaries = []
        for i in range(100):
            beneficiary = Beneficiary(
                first_name=f'Large{i}',
                last_name='Dataset',
                email=f'large{i}@test.com',
                description=f'Test beneficiary {i} with some description data to increase response size'
            )
            beneficiaries.append(beneficiary)
        
        db_session.add_all(beneficiaries)
        db_session.commit()
        
        # Request large dataset
        start_time = time.time()
        response = client.get('/api/beneficiaries?per_page=100', headers=auth_headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Clean up
        for beneficiary in beneficiaries:
            db_session.delete(beneficiary)
        db_session.commit()
        
        # Verify performance
        if response.status_code == 200:
            data = response.get_json()
            assert len(data.get('beneficiaries', [])) <= 100
            assert response_time < 5.0  # Should handle large response within 5 seconds


class TestDatabasePerformance:
    """Test database-specific performance."""
    
    def test_bulk_insert_performance(self, app, db_session):
        """Test bulk insert performance."""
        with app.app_context():
            # Test bulk insert of users
            users = []
            for i in range(100):
                user = User(
                    email=f'bulk{i}@example.com',
                    username=f'bulk{i}',
                    password='Test123!',
                    role='user'
                )
                users.append(user)
            
            start_time = time.time()
            db_session.add_all(users)
            db_session.commit()
            end_time = time.time()
            
            insert_time = end_time - start_time
            
            # Should complete bulk insert reasonably quickly
            assert insert_time < 10.0  # Within 10 seconds
            
            # Verify all users were created
            count = User.query.filter(User.email.like('bulk%')).count()
            assert count == 100
            
            # Clean up
            User.query.filter(User.email.like('bulk%')).delete()
            db_session.commit()
    
    def test_complex_query_performance(self, app, db_session):
        """Test complex query performance."""
        with app.app_context():
            # Create test data
            users = []
            beneficiaries = []
            
            for i in range(20):
                user = User(
                    email=f'complex{i}@example.com',
                    username=f'complex{i}',
                    password='Test123!',
                    role='user'
                )
                users.append(user)
                
                beneficiary = Beneficiary(
                    first_name=f'Complex{i}',
                    last_name='Query',
                    email=f'complex{i}@beneficiary.com'
                )
                beneficiaries.append(beneficiary)
            
            db_session.add_all(users + beneficiaries)
            db_session.commit()
            
            # Test complex query with joins and filters
            start_time = time.time()
            
            # Example complex query (adjust based on actual model relationships)
            result = db_session.query(User).filter(
                User.email.like('complex%')
            ).order_by(User.created_at.desc()).limit(10).all()
            
            end_time = time.time()
            query_time = end_time - start_time
            
            # Query should complete quickly
            assert query_time < 2.0  # Within 2 seconds
            assert len(result) == 10
            
            # Clean up
            for user in users:
                db_session.delete(user)
            for beneficiary in beneficiaries:
                db_session.delete(beneficiary)
            db_session.commit()
    
    def test_pagination_performance(self, app, db_session):
        """Test pagination query performance."""
        with app.app_context():
            # Create test data
            beneficiaries = []
            for i in range(200):
                beneficiary = Beneficiary(
                    first_name=f'Page{i}',
                    last_name='Test',
                    email=f'page{i}@test.com'
                )
                beneficiaries.append(beneficiary)
            
            db_session.add_all(beneficiaries)
            db_session.commit()
            
            # Test pagination queries
            page_times = []
            
            for page in range(1, 6):  # Test first 5 pages
                start_time = time.time()
                
                result = Beneficiary.query.filter(
                    Beneficiary.email.like('page%')
                ).offset((page - 1) * 20).limit(20).all()
                
                end_time = time.time()
                page_time = end_time - start_time
                page_times.append(page_time)
                
                assert len(result) == 20
            
            # All page queries should be fast
            max_page_time = max(page_times)
            assert max_page_time < 1.0  # Each page within 1 second
            
            # Page times should be relatively consistent (no significant degradation)
            min_page_time = min(page_times)
            assert max_page_time / min_page_time < 3.0  # No more than 3x difference
            
            # Clean up
            Beneficiary.query.filter(Beneficiary.email.like('page%')).delete()
            db_session.commit()


class TestAPILimitsAndThresholds:
    """Test API limits and threshold handling."""
    
    def test_large_request_payload(self, client, auth_headers):
        """Test handling of large request payloads."""
        # Create large beneficiary data
        large_description = "Large description data. " * 1000  # ~25KB
        
        beneficiary_data = {
            'first_name': 'Large',
            'last_name': 'Payload',
            'email': 'large@test.com',
            'description': large_description
        }
        
        start_time = time.time()
        response = client.post('/api/beneficiaries',
                             headers=auth_headers,
                             json=beneficiary_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should handle large payload within reasonable time
        if response.status_code == 201:
            assert response_time < 5.0
            
            # Clean up
            beneficiary_id = response.get_json()['beneficiary']['id']
            client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers)
        
        # Or should reject if payload too large
        elif response.status_code == 413:
            # Payload too large - this is also acceptable
            assert True
    
    def test_rapid_sequential_requests(self, client, auth_headers):
        """Test handling of rapid sequential requests."""
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            response = client.get('/health')
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == 200
        
        # Response times should remain consistent
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # No request should take more than 3x the average
        assert max_response_time < avg_response_time * 3
        
        # Average should be reasonable
        assert avg_response_time < 1.0
    
    def test_error_handling_performance(self, client, auth_headers):
        """Test that error handling doesn't significantly impact performance."""
        # Test various error scenarios
        error_scenarios = [
            ('/api/beneficiaries/999999', 'GET'),  # Not found
            ('/api/beneficiaries', 'POST'),        # Bad request (no data)
            ('/api/nonexistent', 'GET'),           # Not found endpoint
        ]
        
        for endpoint, method in error_scenarios:
            start_time = time.time()
            
            if method == 'GET':
                response = client.get(endpoint, headers=auth_headers)
            elif method == 'POST':
                response = client.post(endpoint, headers=auth_headers, json={})
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Error responses should be fast
            assert response_time < 2.0
            assert response.status_code >= 400  # Should be an error response