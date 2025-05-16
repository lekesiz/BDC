import time
import pytest
from concurrent.futures import ThreadPoolExecutor
from app import create_app, db
from app.models import User, Beneficiary, Evaluation, Appointment
from app.tests.factories import UserFactory, BeneficiaryFactory, EvaluationFactory

class TestPerformance:
    """Performance tests for critical API endpoints"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, client):
        """Create authenticated user and return headers"""
        user = UserFactory(role='trainer')
        db.session.commit()
        
        response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        token = response.json['access_token']
        
        return {'Authorization': f'Bearer {token}'}
    
    def test_beneficiaries_list_performance(self, client, auth_headers):
        """Test beneficiaries list endpoint performance"""
        # Create test data
        for _ in range(100):
            BeneficiaryFactory()
        db.session.commit()
        
        # Measure response time
        start_time = time.time()
        response = client.get('/api/v1/beneficiaries', headers=auth_headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond in less than 1 second
        assert len(response.json['data']) == 20  # Default pagination
    
    def test_evaluations_concurrent_access(self, client, auth_headers):
        """Test concurrent access to evaluations endpoint"""
        # Create test data
        evaluations = [EvaluationFactory() for _ in range(50)]
        db.session.commit()
        
        def make_request():
            return client.get('/api/v1/evaluations', headers=auth_headers)
        
        # Test concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
            end_time = time.time()
        
        total_time = end_time - start_time
        
        # All requests should succeed
        for result in results:
            assert result.status_code == 200
        
        # Should handle 10 concurrent requests in reasonable time
        assert total_time < 3.0
    
    def test_dashboard_data_aggregation(self, client, auth_headers):
        """Test dashboard data aggregation performance"""
        # Create complex test data
        beneficiary = BeneficiaryFactory()
        
        # Create multiple related records
        for _ in range(50):
            EvaluationFactory(beneficiary=beneficiary)
        
        for _ in range(30):
            AppointmentFactory(beneficiary=beneficiary)
        
        db.session.commit()
        
        # Measure dashboard API response time
        start_time = time.time()
        response = client.get(
            f'/api/v1/beneficiaries/{beneficiary.id}/dashboard',
            headers=auth_headers
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Complex aggregation should still be fast
    
    def test_search_performance(self, client, auth_headers):
        """Test search functionality performance"""
        # Create searchable data
        for i in range(100):
            BeneficiaryFactory(
                user=UserFactory(
                    first_name=f'TestUser{i}',
                    email=f'user{i}@example.com'
                )
            )
        db.session.commit()
        
        # Test search performance
        search_queries = ['Test', 'User', '@example.com', 'TestUser50']
        
        for query in search_queries:
            start_time = time.time()
            response = client.get(
                f'/api/v1/beneficiaries/search?q={query}',
                headers=auth_headers
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 0.5  # Search should be fast
    
    def test_bulk_operations_performance(self, client, auth_headers):
        """Test bulk operations performance"""
        # Create test data
        beneficiaries = [BeneficiaryFactory() for _ in range(50)]
        db.session.commit()
        
        # Test bulk update
        update_data = {
            'ids': [b.id for b in beneficiaries[:25]],
            'status': 'active'
        }
        
        start_time = time.time()
        response = client.put(
            '/api/v1/beneficiaries/bulk',
            json=update_data,
            headers=auth_headers
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Bulk operations should be optimized
    
    def test_file_upload_performance(self, client, auth_headers):
        """Test file upload performance"""
        # Create a test file
        test_file = (BytesIO(b'x' * 1024 * 1024), 'test.pdf')  # 1MB file
        
        start_time = time.time()
        response = client.post(
            '/api/v1/documents/upload',
            data={'file': test_file},
            content_type='multipart/form-data',
            headers=auth_headers
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 201
        assert response_time < 2.0  # File upload should be reasonably fast
    
    def test_report_generation_performance(self, client, auth_headers):
        """Test report generation performance"""
        # Create test data for report
        beneficiary = BeneficiaryFactory()
        for _ in range(20):
            EvaluationFactory(beneficiary=beneficiary, score=85)
        db.session.commit()
        
        start_time = time.time()
        response = client.get(
            f'/api/v1/reports/beneficiary/{beneficiary.id}',
            headers=auth_headers
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0  # Report generation can be complex but should be bounded
    
    def test_cache_effectiveness(self, client, auth_headers):
        """Test caching effectiveness"""
        # First request - cache miss
        start_time = time.time()
        response1 = client.get('/api/v1/statistics/overview', headers=auth_headers)
        end_time = time.time()
        first_request_time = end_time - start_time
        
        # Second request - should hit cache
        start_time = time.time()
        response2 = client.get('/api/v1/statistics/overview', headers=auth_headers)
        end_time = time.time()
        second_request_time = end_time - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert second_request_time < first_request_time * 0.5  # Cache should significantly improve performance
    
    @pytest.mark.slow
    def test_stress_test_concurrent_users(self, client):
        """Stress test with multiple concurrent users"""
        # Create multiple users
        users = [UserFactory() for _ in range(20)]
        db.session.commit()
        
        def simulate_user_session(user):
            # Login
            response = client.post('/api/v1/auth/login', json={
                'email': user.email,
                'password': 'password123'
            })
            token = response.json['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Perform various operations
            operations = [
                lambda: client.get('/api/v1/beneficiaries', headers=headers),
                lambda: client.get('/api/v1/evaluations', headers=headers),
                lambda: client.get('/api/v1/appointments', headers=headers),
                lambda: client.get('/api/v1/dashboard', headers=headers)
            ]
            
            results = []
            for op in operations:
                result = op()
                results.append(result.status_code)
            
            return results
        
        # Run concurrent user sessions
        with ThreadPoolExecutor(max_workers=20) as executor:
            start_time = time.time()
            futures = [executor.submit(simulate_user_session, user) for user in users]
            all_results = [f.result() for f in futures]
            end_time = time.time()
        
        total_time = end_time - start_time
        
        # All operations should succeed
        for results in all_results:
            for status_code in results:
                assert status_code in [200, 201]
        
        # Should handle 20 concurrent users
        assert total_time < 10.0
    
    def test_database_query_optimization(self, app, client, auth_headers):
        """Test database query optimization"""
        # Enable query logging
        from sqlalchemy import event
        
        queries = []
        
        def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
            queries.append(statement)
        
        event.listen(db.session.bind, "after_cursor_execute", receive_after_cursor_execute)
        
        # Create test data with relationships
        beneficiary = BeneficiaryFactory()
        for _ in range(10):
            EvaluationFactory(beneficiary=beneficiary)
        db.session.commit()
        
        # Clear query log
        queries.clear()
        
        # Make request that should use eager loading
        response = client.get(
            f'/api/v1/beneficiaries/{beneficiary.id}',
            headers=auth_headers
        )
        
        # Check query count (should use eager loading to minimize queries)
        assert len(queries) < 5  # Should not have N+1 query problem
        assert response.status_code == 200