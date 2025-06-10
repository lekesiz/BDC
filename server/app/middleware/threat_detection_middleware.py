"""Threat detection middleware for Flask application."""

import json
import logging
from flask import request, abort, current_app, g
from functools import wraps
from app.security.threat_detection import ThreatDetectionEngine, ThreatIndicator
from app.extensions import redis_client
from app.security.audit_logger import AuditLogger

logger = logging.getLogger(__name__)


class ThreatDetectionMiddleware:
    """Middleware for real-time threat detection and response."""
    
    def __init__(self, app=None):
        self.app = app
        self.threat_detector = None
        self.audit_logger = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app."""
        self.app = app
        self.threat_detector = ThreatDetectionEngine(redis_client)
        self.audit_logger = AuditLogger()
        
        # Register before_request handler
        app.before_request(self.detect_threats)
        
        # Register error handlers
        app.errorhandler(403)(self.handle_forbidden)
        app.errorhandler(429)(self.handle_rate_limit)
    
    def detect_threats(self):
        """Analyze each request for potential threats."""
        # Skip threat detection for health checks
        if request.path == '/health' or request.path == '/api/health':
            return
        
        # Extract request data
        request_data = {
            'ip': self._get_client_ip(),
            'user_id': getattr(g, 'current_user_id', None),
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers),
            'params': request.args.to_dict(),
            'body': self._get_request_body()
        }
        
        # Check if IP is blacklisted
        if self.threat_detector.is_ip_blacklisted(request_data['ip']):
            self._log_blocked_request(request_data['ip'], 'IP blacklisted')
            abort(403, description="Access denied: Your IP has been blacklisted due to suspicious activity")
        
        # Analyze request for threats
        threats = self.threat_detector.analyze_request(request_data)
        
        # Handle detected threats
        if threats:
            self._handle_threats(threats, request_data)
    
    def _get_client_ip(self):
        """Get the real client IP address."""
        if 'X-Forwarded-For' in request.headers:
            # X-Forwarded-For can contain multiple IPs
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif 'X-Real-IP' in request.headers:
            ip = request.headers.get('X-Real-IP')
        else:
            ip = request.remote_addr or '127.0.0.1'
        return ip
    
    def _get_request_body(self):
        """Safely get request body as string."""
        try:
            if request.is_json:
                return json.dumps(request.get_json())
            elif request.form:
                return str(dict(request.form))
            else:
                return request.get_data(as_text=True)[:1000]  # Limit to 1000 chars
        except:
            return ''
    
    def _handle_threats(self, threats: list[ThreatIndicator], request_data: dict):
        """Handle detected threats based on severity."""
        # Group threats by severity
        critical_threats = [t for t in threats if t.severity == 'critical']
        high_threats = [t for t in threats if t.severity == 'high']
        medium_threats = [t for t in threats if t.severity == 'medium']
        low_threats = [t for t in threats if t.severity == 'low']
        
        # Log all threats
        for threat in threats:
            self._log_threat(threat)
        
        # Handle critical threats - immediate block
        if critical_threats:
            self._block_request(critical_threats[0])
        
        # Handle high threats - block if multiple
        elif len(high_threats) >= 2:
            self._block_request(high_threats[0])
        
        # Handle medium threats - rate limit if multiple
        elif len(medium_threats) >= 3:
            self._apply_rate_limit(request_data['ip'])
        
        # For low threats, just log and monitor
        # The suspicious score will accumulate and eventually trigger blocking
    
    def _log_threat(self, threat: ThreatIndicator):
        """Log threat to audit system."""
        self.audit_logger.log_security_event(
            event_type=threat.threat_type,
            severity=threat.severity,
            description=threat.description,
            source_ip=threat.source_ip,
            user_id=threat.user_id,
            details=threat.details
        )
        
        # Also log to application logger
        logger.warning(f"Threat detected: {threat.threat_type} from {threat.source_ip} - {threat.description}")
    
    def _block_request(self, threat: ThreatIndicator):
        """Block the current request."""
        self._log_blocked_request(threat.source_ip, threat.description)
        
        # Add custom response based on threat type
        if threat.threat_type in ['sql_injection_attempt', 'command_injection_attempt']:
            abort(403, description="Invalid request detected")
        elif threat.threat_type == 'brute_force_attempt':
            abort(429, description="Too many failed attempts. Please try again later.")
        else:
            abort(403, description="Access denied due to suspicious activity")
    
    def _apply_rate_limit(self, ip: str):
        """Apply stricter rate limiting for suspicious IPs."""
        if redis_client:
            # Reduce rate limit for this IP
            key = f"strict_rate_limit:{ip}"
            redis_client.setex(key, 3600, 1)  # 1 hour strict limit
    
    def _log_blocked_request(self, ip: str, reason: str):
        """Log blocked request."""
        self.audit_logger.log_security_event(
            event_type='request_blocked',
            severity='high',
            description=f"Request blocked: {reason}",
            source_ip=ip,
            details={
                'path': request.path,
                'method': request.method,
                'reason': reason
            }
        )
    
    def handle_forbidden(self, error):
        """Custom 403 error handler."""
        return {
            'error': 'Forbidden',
            'message': str(error.description) if error.description else 'Access denied',
            'code': 403
        }, 403
    
    def handle_rate_limit(self, error):
        """Custom 429 error handler."""
        return {
            'error': 'Rate Limit Exceeded',
            'message': str(error.description) if error.description else 'Too many requests',
            'code': 429
        }, 429


def require_threat_check(f):
    """Decorator to ensure threat detection is performed on specific endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Additional threat checking can be added here for specific endpoints
        # The middleware already runs before each request
        return f(*args, **kwargs)
    return decorated_function


# Initialize global instance
threat_detection_middleware = ThreatDetectionMiddleware()