"""
Security headers middleware for comprehensive HTTP security.
"""

from flask import Flask, request, g
from typing import Dict, Optional, List
import re

class SecurityHeaders:
    """Security headers middleware for Flask applications."""
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize security headers middleware."""
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize security headers for Flask app."""
        app.after_request(self.add_security_headers)
        app.before_request(self.validate_request)
    
    @staticmethod
    def add_security_headers(response):
        """Add comprehensive security headers to response."""
        from .security_config import SecurityConfig
        
        # Add all configured security headers
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Content-Type-specific headers
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Cache control for sensitive pages
        if request.endpoint and any(endpoint in request.endpoint for endpoint in 
                                  ['auth', 'login', 'profile', 'admin']):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # HSTS for HTTPS
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
        
        # Remove server header for security
        response.headers.pop('Server', None)
        
        return response
    
    @staticmethod
    def validate_request():
        """Validate incoming request for security issues."""
        # Check for suspicious headers
        suspicious_headers = [
            'X-Forwarded-Host',
            'X-Original-Host', 
            'X-Rewrite-URL',
            'X-Original-URL'
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # Log suspicious activity
                g.security_alert = f"Suspicious header detected: {header}"
        
        # Validate Content-Type for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('Content-Type', '')
            
            if not content_type:
                g.security_alert = "Missing Content-Type header"
            elif not any(allowed in content_type for allowed in 
                        ['application/json', 'multipart/form-data', 'application/x-www-form-urlencoded']):
                g.security_alert = f"Unexpected Content-Type: {content_type}"
        
        # Check for oversized requests
        if request.content_length:
            from .security_config import SecurityConfig
            if request.content_length > SecurityConfig.MAX_REQUEST_SIZE:
                g.security_alert = f"Request too large: {request.content_length} bytes"
        
        # Validate User-Agent
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or len(user_agent) < 10 or len(user_agent) > 1000:
            g.security_alert = "Suspicious or missing User-Agent"
        
        # Check for common attack patterns in URL
        suspicious_patterns = [
            r'\.\./',           # Directory traversal
            r'%2e%2e%2f',      # URL encoded directory traversal
            r'<script',         # XSS attempt
            r'javascript:',     # JavaScript protocol
            r'vbscript:',      # VBScript protocol
            r'data:',          # Data URLs
            r'\\x',            # Hex encoding
            r'%00',            # Null byte
        ]
        
        url_path = request.full_path.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, url_path, re.IGNORECASE):
                g.security_alert = f"Suspicious URL pattern: {pattern}"
                break
    
    @staticmethod
    def get_csp_header(nonce: Optional[str] = None, 
                      additional_sources: Optional[Dict[str, List[str]]] = None) -> str:
        """Generate Content Security Policy header with nonce support."""
        policy_parts = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self' wss: https:",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests"
        ]
        
        # Add nonce for scripts if provided
        if nonce:
            policy_parts[1] = f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net"
        
        # Add additional sources if provided
        if additional_sources:
            for directive, sources in additional_sources.items():
                for i, part in enumerate(policy_parts):
                    if part.startswith(directive):
                        policy_parts[i] += ' ' + ' '.join(sources)
                        break
        
        return '; '.join(policy_parts)
    
    @staticmethod
    def validate_origin(origin: str, allowed_origins: List[str]) -> bool:
        """Validate request origin against allowed origins."""
        if not origin:
            return False
        
        # Remove protocol and port for comparison
        origin_domain = origin.replace('https://', '').replace('http://', '').split(':')[0]
        
        for allowed in allowed_origins:
            allowed_domain = allowed.replace('https://', '').replace('http://', '').split(':')[0]
            if origin_domain == allowed_domain:
                return True
        
        return False
    
    @staticmethod
    def get_frame_options(value: str = 'DENY') -> str:
        """Get X-Frame-Options header value."""
        allowed_values = ['DENY', 'SAMEORIGIN']
        if value in allowed_values:
            return value
        return 'DENY'
    
    @staticmethod
    def get_permissions_policy() -> str:
        """Get Permissions-Policy header for modern browsers."""
        policies = [
            'geolocation=()',
            'microphone=()',
            'camera=()',
            'payment=()',
            'usb=()',
            'magnetometer=()',
            'gyroscope=()',
            'accelerometer=()',
            'ambient-light-sensor=()',
            'autoplay=()',
            'encrypted-media=()',
            'fullscreen=(self)',
            'picture-in-picture=()',
        ]
        return ', '.join(policies)
    
    @staticmethod
    def add_hsts_header(response, max_age: int = 31536000, 
                       include_subdomains: bool = True, preload: bool = True):
        """Add HTTP Strict Transport Security header."""
        hsts_value = f'max-age={max_age}'
        
        if include_subdomains:
            hsts_value += '; includeSubDomains'
        
        if preload:
            hsts_value += '; preload'
        
        response.headers['Strict-Transport-Security'] = hsts_value
        return response
    
    @staticmethod
    def add_csp_report_uri(csp_header: str, report_uri: str) -> str:
        """Add report-uri to CSP header for violation reporting."""
        return f"{csp_header}; report-uri {report_uri}"
    
    @staticmethod
    def is_secure_context(request) -> bool:
        """Check if request is in a secure context (HTTPS)."""
        # Check if using HTTPS
        if request.is_secure:
            return True
        
        # Check for proxy headers indicating HTTPS
        if request.headers.get('X-Forwarded-Proto') == 'https':
            return True
        
        if request.headers.get('X-Forwarded-SSL') == 'on':
            return True
        
        return False