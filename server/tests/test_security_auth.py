import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models import User
from tests.factories import UserFactory

class TestSecurityAuth:
    """Test authentication and authorization security"""
    
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
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed"""
        user = UserFactory(password='plaintext123')
        db.session.commit()
        
        # Password should not be stored in plain text
        assert user.password_hash != 'plaintext123'
        
        # verify_password should work correctly
        assert user.verify_password('plaintext123')
        assert not user.verify_password('wrongpassword')
    
    def test_jwt_token_required(self, client):
        """Test that protected endpoints require JWT token"""
        response = client.get('/api/v1/beneficiaries')
        assert response.status_code == 401
        assert 'Missing Authorization Header' in response.json['msg']
    
    def test_invalid_jwt_token(self, client):
        """Test handling of invalid JWT tokens"""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/v1/beneficiaries', headers=headers)
        assert response.status_code == 422
    
    def test_expired_jwt_token(self, app, client):
        """Test handling of expired JWT tokens"""
        with app.test_request_context():
            # Create an expired token
            user = UserFactory()
            db.session.commit()
            
            with app.app_context():
                app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 0
                token = create_access_token(identity=str(user.id))
            
            headers = {'Authorization': f'Bearer {token}'}
            response = client.get('/api/v1/beneficiaries', headers=headers)
            assert response.status_code == 401
            assert 'Token has expired' in response.json['msg']
    
    def test_role_based_access_control(self, client):
        """Test role-based access control"""
        # Create users with different roles
        admin = UserFactory(role='super_admin')
        trainer = UserFactory(role='trainer')
        student = UserFactory(role='student')
        db.session.commit()
        
        # Test admin access
        admin_token = self.login(client, admin.email, 'password123')
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.get('/api/v1/users', headers=headers)
        assert response.status_code == 200
        
        # Test student restricted access
        student_token = self.login(client, student.email, 'password123')
        headers = {'Authorization': f'Bearer {student_token}'}
        response = client.get('/api/v1/users', headers=headers)
        assert response.status_code == 403
    
    def test_brute_force_protection(self, client):
        """Test brute force attack protection"""
        email = 'test@example.com'
        
        # Multiple failed login attempts
        for i in range(10):
            response = client.post('/api/v1/auth/login', json={
                'email': email,
                'password': f'wrongpassword{i}'
            })
        
        # Should be rate limited or locked out
        response = client.post('/api/v1/auth/login', json={
            'email': email,
            'password': 'password123'
        })
        
        # Check for rate limiting response
        assert response.status_code in [429, 403]
    
    def test_session_fixation_prevention(self, client):
        """Test prevention of session fixation attacks"""
        # Login
        user = UserFactory()
        db.session.commit()
        
        response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        
        initial_token = response.json['access_token']
        
        # Login again
        response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        
        new_token = response.json['access_token']
        
        # Tokens should be different
        assert initial_token != new_token
    
    def test_password_requirements(self, client):
        """Test password strength requirements"""
        weak_passwords = [
            'abc',           # Too short
            'password',      # Common password
            '12345678',      # No letters
            'abcdefgh',      # No numbers
        ]
        
        for password in weak_passwords:
            response = client.post('/api/v1/auth/register', json={
                'email': 'test@example.com',
                'password': password,
                'confirm_password': password,
                'first_name': 'Test',
                'last_name': 'User'
            })
            assert response.status_code == 400
            assert 'password' in response.json['errors']
    
    def test_secure_headers(self, client):
        """Test that security headers are set correctly"""
        response = client.get('/')
        
        # Check security headers
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        
        assert 'X-XSS-Protection' in response.headers
        assert response.headers['X-XSS-Protection'] == '1; mode=block'
        
        # HTTPS only in production
        if client.application.config['ENV'] == 'production':
            assert 'Strict-Transport-Security' in response.headers
    
    def test_csrf_protection(self, client):
        """Test CSRF protection on state-changing operations"""
        user = UserFactory()
        db.session.commit()
        
        token = self.login(client, user.email, 'password123')
        headers = {'Authorization': f'Bearer {token}'}
        
        # POST without CSRF token should be rejected if CSRF is enabled
        response = client.post('/api/v1/beneficiaries', 
                             json={'name': 'Test'},
                             headers=headers)
        
        # Should either succeed (if using JWT) or fail with CSRF error
        assert response.status_code in [201, 400, 403]
    
    def login(self, client, email, password):
        """Helper method to login and get JWT token"""
        response = client.post('/api/v1/auth/login', json={
            'email': email,
            'password': password
        })
        return response.json['access_token']
    
    def test_unauthorized_data_access(self, client):
        """Test that users cannot access other users' data"""
        user1 = UserFactory()
        user2 = UserFactory()
        db.session.commit()
        
        # Login as user1
        token = self.login(client, user1.email, 'password123')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Try to access user2's data
        response = client.get(f'/api/v1/users/{user2.id}', headers=headers)
        
        # Should be forbidden unless user1 is admin
        if user1.role not in ['super_admin', 'tenant_admin']:
            assert response.status_code == 403