import pytest
from app import create_app, db
from app.models import User
from app.tests.factories import UserFactory

class TestSecurityInputValidation:
    """Test input validation for security vulnerabilities"""
    
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
        user = UserFactory(role='trainer')
        db.session.commit()
        
        response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        token = response.json['access_token']
        
        return {'Authorization': f'Bearer {token}'}
    
    def test_sql_injection_prevention(self, client, auth_headers):
        """Test protection against SQL injection attacks"""
        # Attempt SQL injection in search query
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM users WHERE 1=1;",
        ]
        
        for payload in malicious_inputs:
            response = client.get(
                f'/api/v1/beneficiaries/search?q={payload}',
                headers=auth_headers
            )
            
            # Should return empty results or 400, not execute SQL
            assert response.status_code in [200, 400]
            if response.status_code == 200:
                assert len(response.json['data']) == 0
    
    def test_xss_prevention(self, client, auth_headers):
        """Test protection against XSS attacks"""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
        ]
        
        for payload in xss_payloads:
            # Try to inject in various endpoints
            response = client.post('/api/v1/beneficiaries', json={
                'first_name': payload,
                'last_name': 'Test',
                'email': 'test@example.com'
            }, headers=auth_headers)
            
            # Check that the payload is either rejected or properly escaped
            if response.status_code == 201:
                created_data = response.json
                assert '<script>' not in created_data['first_name']
                assert 'javascript:' not in created_data['first_name']
    
    def test_file_upload_validation(self, client, auth_headers):
        """Test file upload security"""
        from io import BytesIO
        
        # Test dangerous file types
        dangerous_files = [
            ('malicious.exe', b'MZ\x90\x00'),  # Executable
            ('shell.php', b'<?php system($_GET["cmd"]); ?>'),  # PHP shell
            ('test.jsp', b'<%@ page import="java.io.*" %>'),  # JSP
        ]
        
        for filename, content in dangerous_files:
            data = {
                'file': (BytesIO(content), filename)
            }
            
            response = client.post(
                '/api/v1/documents/upload',
                data=data,
                headers=auth_headers,
                content_type='multipart/form-data'
            )
            
            # Should reject dangerous file types
            assert response.status_code in [400, 415]
    
    def test_path_traversal_prevention(self, client, auth_headers):
        """Test protection against path traversal attacks"""
        path_traversal_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
            '....//....//....//etc/passwd',
        ]
        
        for payload in path_traversal_payloads:
            response = client.get(
                f'/api/v1/documents/{payload}',
                headers=auth_headers
            )
            
            # Should not allow access to system files
            assert response.status_code in [400, 404]
    
    def test_command_injection_prevention(self, client, auth_headers):
        """Test protection against command injection"""
        command_payloads = [
            '; cat /etc/passwd',
            '| ls -la',
            '`whoami`',
            '$(cat /etc/passwd)',
        ]
        
        for payload in command_payloads:
            # Try in various inputs
            response = client.post('/api/v1/reports/generate', json={
                'title': payload,
                'format': 'pdf'
            }, headers=auth_headers)
            
            # Should not execute commands
            assert response.status_code in [200, 400]
    
    def test_email_validation(self, client):
        """Test email validation to prevent injection"""
        invalid_emails = [
            'test@example.com<script>alert("XSS")</script>',
            'test+<script>@example.com',
            'test@example.com\r\nBCC: attacker@evil.com',
            'test@example.com%0d%0abcc:attacker@evil.com',
        ]
        
        for email in invalid_emails:
            response = client.post('/api/v1/auth/register', json={
                'email': email,
                'password': 'StrongPassword123!',
                'first_name': 'Test',
                'last_name': 'User'
            })
            
            # Should reject invalid emails
            assert response.status_code == 400
            assert 'email' in response.json['errors']
    
    def test_integer_overflow_prevention(self, client, auth_headers):
        """Test protection against integer overflow"""
        overflow_values = [
            2**31,  # Max 32-bit signed integer + 1
            -2**31 - 1,  # Min 32-bit signed integer - 1
            9999999999999999999999,  # Very large number
        ]
        
        for value in overflow_values:
            response = client.post('/api/v1/evaluations', json={
                'score': value,
                'test_id': 1
            }, headers=auth_headers)
            
            # Should handle gracefully
            assert response.status_code in [400, 422]
    
    def test_json_injection_prevention(self, client, auth_headers):
        """Test protection against JSON injection"""
        json_payloads = [
            {'$where': 'function() { return true; }'},  # MongoDB injection
            {'$gt': ''},  # MongoDB operator injection
            {'__proto__': {'isAdmin': True}},  # Prototype pollution
        ]
        
        for payload in json_payloads:
            response = client.post('/api/v1/beneficiaries/search', 
                                 json=payload,
                                 headers=auth_headers)
            
            # Should not execute injected code
            assert response.status_code in [400, 422]
    
    def test_xml_injection_prevention(self, client, auth_headers):
        """Test protection against XML injection and XXE"""
        xml_payloads = [
            '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
            '<user><name>test</name><role>admin</role></user>',
        ]
        
        for payload in xml_payloads:
            response = client.post('/api/v1/import/xml',
                                 data=payload,
                                 headers={**auth_headers, 'Content-Type': 'application/xml'})
            
            # Should not process malicious XML
            assert response.status_code in [400, 415]
    
    def test_ldap_injection_prevention(self, client):
        """Test protection against LDAP injection"""
        ldap_payloads = [
            'admin)(&(password=*))',
            '*)(uid=*))(&(uid=*',
            'admin)|(password=*',
        ]
        
        for payload in ldap_payloads:
            response = client.post('/api/v1/auth/ldap-login', json={
                'username': payload,
                'password': 'test'
            })
            
            # Should not execute LDAP injection
            assert response.status_code in [400, 401]
    
    def test_header_injection_prevention(self, client, auth_headers):
        """Test protection against header injection"""
        header_payloads = [
            'test\r\nX-Injected: true',
            'test\nContent-Type: text/html',
            'test\r\n\r\n<script>alert("XSS")</script>',
        ]
        
        for payload in header_payloads:
            response = client.post('/api/v1/notifications/send', json={
                'subject': payload,
                'message': 'Test message'
            }, headers=auth_headers)
            
            # Should not allow header injection
            assert response.status_code in [200, 400]
            assert 'X-Injected' not in response.headers