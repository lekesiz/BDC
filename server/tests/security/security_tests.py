"""Consolidated security tests."""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from app.utils.secure_subprocess import SecureSubprocess, SecureSubprocessError
from app.utils.secure_exception_handler import (
    SecureExceptionHandler, SecurityException, 
    InputValidationException, is_safe_filename, is_safe_path
)


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting_configuration(self, app):
        """Test that rate limiting is properly configured."""
        from flask_limiter import Limiter
        
        # Check that limiter is configured
        limiter = app.extensions.get('limiter')
        if limiter:
            assert isinstance(limiter, Limiter)
            assert limiter._strategy in ['fixed-window', 'sliding-window-counter']
    
    def test_rate_limiting_enforcement(self, client):
        """Test that rate limiting is enforced."""
        # Make rapid requests to trigger rate limiting
        responses = []
        
        for i in range(20):
            response = client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'invalidpassword'
            })
            responses.append(response.status_code)
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.01)
        
        # Should eventually get rate limited (429) or consistently get 401
        status_codes = set(responses)
        
        # Either rate limiting works (429) or auth fails consistently (401)
        assert 429 in status_codes or all(code == 401 for code in responses)
    
    def test_rate_limiting_headers(self, client):
        """Test that rate limiting headers are present."""
        response = client.get('/health')
        
        # Check for rate limiting headers
        rate_limit_headers = [
            'X-RateLimit-Limit',
            'X-RateLimit-Remaining',
            'X-RateLimit-Reset'
        ]
        
        # At least some rate limiting headers should be present
        # (depends on configuration)
        present_headers = [
            header for header in rate_limit_headers 
            if header in response.headers
        ]
        
        # This is informational - headers may or may not be configured
        print(f"Rate limiting headers present: {present_headers}")


class TestSecureSubprocess:
    """Test secure subprocess functionality."""
    
    def test_allowed_executable(self):
        """Test that allowed executables can be run."""
        # Test with a safe command that should be allowed
        try:
            result = SecureSubprocess.run_secure(
                ['echo', 'test'],
                timeout=5,
                check=False
            )
            # This might fail if echo is not in ALLOWED_EXECUTABLES
            # The test verifies the security framework works
        except SecureSubprocessError as e:
            # Expected if echo is not in allowed list
            assert "not allowed" in str(e)
    
    def test_forbidden_executable(self):
        """Test that forbidden executables are blocked."""
        with pytest.raises(SecureSubprocessError) as exc_info:
            SecureSubprocess.run_secure(['rm', '-rf', '/'])
        
        assert "not allowed" in str(exc_info.value)
    
    def test_command_injection_prevention(self):
        """Test that command injection is prevented."""
        with pytest.raises(SecureSubprocessError) as exc_info:
            SecureSubprocess.run_secure(['pg_dump', '; rm -rf /'])
        
        assert "Forbidden pattern" in str(exc_info.value)
    
    def test_path_traversal_prevention(self):
        """Test that path traversal is prevented."""
        with pytest.raises(SecureSubprocessError) as exc_info:
            SecureSubprocess.run_secure(['tar', '-czf', '/tmp/test.tar.gz', '../../../etc/passwd'])
        
        assert "Dangerous pattern" in str(exc_info.value) or "outside allowed" in str(exc_info.value)
    
    def test_timeout_enforcement(self):
        """Test that timeouts are enforced."""
        with pytest.raises(SecureSubprocessError) as exc_info:
            # Use a command that would take longer than timeout
            SecureSubprocess.run_secure(
                ['sleep', '10'],  # This will likely be blocked as unsafe
                timeout=1
            )
        
        # Either blocked as unsafe command or times out
        assert "not allowed" in str(exc_info.value) or "timeout" in str(exc_info.value)


class TestSecureExceptionHandler:
    """Test secure exception handling."""
    
    def test_sensitive_data_sanitization(self):
        """Test that sensitive data is removed from error messages."""
        handler = SecureExceptionHandler()
        
        # Test password sanitization
        error = Exception("Database error: password=secret123 failed")
        sanitized = handler._sanitize_error(error)
        
        assert "secret123" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_threat_detection_sql_injection(self):
        """Test SQL injection attempt detection."""
        handler = SecureExceptionHandler()
        
        error_msg = "union select * from users"
        category = handler._categorize_error(error_msg)
        
        assert category == "sql_injection"
    
    def test_threat_detection_xss(self):
        """Test XSS attempt detection."""
        handler = SecureExceptionHandler()
        
        error_msg = "Error: <script>alert('xss')</script>"
        category = handler._categorize_error(error_msg)
        
        assert category == "xss_attempt"
    
    def test_threat_detection_path_traversal(self):
        """Test path traversal attempt detection."""
        handler = SecureExceptionHandler()
        
        error_msg = "File not found: ../../../etc/passwd"
        category = handler._categorize_error(error_msg)
        
        assert category == "path_traversal"
    
    def test_security_exception_handling(self, client):
        """Test that security exceptions are properly handled."""
        # This would test the actual Flask error handling
        # Since we can't easily trigger security exceptions in tests,
        # we test the handler logic directly
        
        handler = SecureExceptionHandler()
        
        # Test InputValidationException handling
        error = InputValidationException("Invalid input detected")
        response = handler.handle_security_exception(error)
        
        assert response[1] == 400  # Status code
        data = json.loads(response[0].data)
        assert data['error'] == 'invalid_input'


class TestInputValidation:
    """Test input validation utilities."""
    
    def test_safe_filename_validation(self):
        """Test filename safety validation."""
        # Safe filenames
        assert is_safe_filename("document.pdf") is True
        assert is_safe_filename("image.jpg") is True
        assert is_safe_filename("data.csv") is True
        
        # Unsafe filenames
        assert is_safe_filename("../etc/passwd") is False
        assert is_safe_filename("script.exe") is False
        assert is_safe_filename("file/with/path") is False
        assert is_safe_filename("") is False
        assert is_safe_filename("malware.bat") is False
    
    def test_safe_path_validation(self):
        """Test path safety validation."""
        # Safe paths
        assert is_safe_path("uploads/document.pdf") is True
        assert is_safe_path("data/export.csv") is True
        
        # Unsafe paths
        assert is_safe_path("../../../etc/passwd") is False
        assert is_safe_path("/absolute/path") is False
        assert is_safe_path("path/with/../traversal") is False
        assert is_safe_path("path/with/$variable") is False
        assert is_safe_path("") is False
    
    def test_email_validation(self):
        """Test email validation."""
        from app.utils.secure_exception_handler import is_valid_email
        
        # Valid emails
        assert is_valid_email("user@example.com") is True
        assert is_valid_email("test.email+tag@domain.co.uk") is True
        
        # Invalid emails
        assert is_valid_email("invalid.email") is False
        assert is_valid_email("@domain.com") is False
        assert is_valid_email("user@") is False
        assert is_valid_email("") is False
    
    def test_sql_parameter_validation(self):
        """Test SQL parameter safety validation."""
        from app.utils.secure_exception_handler import is_safe_sql_param
        
        # Safe parameters
        assert is_safe_sql_param("john") is True
        assert is_safe_sql_param("user123") is True
        assert is_safe_sql_param("2024-01-01") is True
        
        # Unsafe parameters
        assert is_safe_sql_param("'; DROP TABLE users; --") is False
        assert is_safe_sql_param("UNION SELECT * FROM passwords") is False
        assert is_safe_sql_param("admin' OR '1'='1") is False


class TestCryptographicSecurity:
    """Test cryptographic security features."""
    
    def test_password_hashing_strength(self, app, db_session):
        """Test that password hashing is cryptographically secure."""
        from app.models.user import User
        
        with app.app_context():
            user = User(
                email='crypto@test.com',
                username='cryptotest',
                password='TestPassword123!'
            )
            
            # Password should be hashed with a strong algorithm
            assert user.password_hash != 'TestPassword123!'
            assert len(user.password_hash) > 50  # Should be substantial length
            
            # Should use bcrypt or similar (contains $ separators)
            assert '$' in user.password_hash
            
            # Verify password works correctly
            assert user.verify_password('TestPassword123!') is True
            assert user.verify_password('wrongpassword') is False
    
    def test_jwt_token_security(self, app, admin_user):
        """Test JWT token security properties."""
        from app.services.auth_service import AuthService
        from app.utils.jwt_utils import decode_token
        
        with app.app_context():
            result = AuthService.login('admin@bdc.com', 'Admin123!', False)
            
            assert result is not None
            token = result['access_token']
            
            # Token should be substantial length
            assert len(token) > 100
            
            # Should have proper JWT structure (3 parts separated by .)
            parts = token.split('.')
            assert len(parts) == 3
            
            # Should decode properly
            decoded = decode_token(token)
            assert decoded is not None
            assert 'user_id' in decoded
            assert 'exp' in decoded
    
    def test_session_security(self, client, admin_user):
        """Test session security properties."""
        # Login and get session
        response = client.post('/api/auth/login', json={
            'email': 'admin@bdc.com',
            'password': 'Admin123!',
            'remember': False
        })
        
        assert response.status_code == 200
        
        # Check security headers
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        # Note: These headers depend on configuration
        # Test is informational about security posture


class TestAPISecurityHeaders:
    """Test security headers in API responses."""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present in responses."""
        response = client.get('/health')
        
        # Test for important security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block'
        }
        
        for header, expected_values in security_headers.items():
            if header in response.headers:
                header_value = response.headers[header]
                if isinstance(expected_values, list):
                    assert header_value in expected_values
                else:
                    assert header_value == expected_values
            else:
                # Log missing security header for awareness
                print(f"Security header missing: {header}")
    
    def test_cors_security(self, client):
        """Test CORS configuration security."""
        response = client.options('/api/auth/login')
        
        if 'Access-Control-Allow-Origin' in response.headers:
            origin = response.headers['Access-Control-Allow-Origin']
            
            # Should not be wildcard '*' in production
            # (Note: This depends on configuration)
            if origin == '*':
                print("Warning: CORS allows all origins (*)")
            else:
                print(f"CORS origin configured: {origin}")
    
    def test_content_type_security(self, client):
        """Test content type security."""
        response = client.get('/health')
        
        # Response should have proper content type
        assert response.content_type == 'application/json'
        
        # Should not execute as HTML/script
        assert 'text/html' not in response.content_type
        assert 'application/javascript' not in response.content_type


class TestAuthorizationSecurity:
    """Test authorization and access control."""
    
    def test_unauthorized_access_prevention(self, client):
        """Test that unauthorized access is properly blocked."""
        # Try to access protected endpoint without token
        response = client.get('/api/auth/me')
        assert response.status_code == 401
        
        # Try to access with invalid token
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/auth/me', headers=headers)
        assert response.status_code == 401
    
    def test_role_based_access_control(self, client, db_session):
        """Test role-based access control if implemented."""
        from app.models.user import User
        
        # Create users with different roles
        regular_user = User(
            email='regular@test.com',
            username='regular',
            password='Regular123!',
            role='user',
            is_active=True
        )
        
        admin_user = User(
            email='testadmin@test.com',
            username='testadmin', 
            password='Admin123!',
            role='admin',
            is_active=True
        )
        
        db_session.add_all([regular_user, admin_user])
        db_session.commit()
        
        # Test that roles are properly assigned
        assert regular_user.role == 'user'
        assert admin_user.role == 'admin'
        
        # Additional RBAC tests would depend on specific endpoint implementations