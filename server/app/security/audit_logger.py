"""
Comprehensive audit logging and security event monitoring.
"""

import json
import time
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from flask import Flask, request, g, current_app
import logging
import logging.handlers
from contextlib import contextmanager

class SecurityEventType(Enum):
    """Types of security events to log."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGIN_BLOCKED = "login_blocked"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    PERMISSION_DENIED = "permission_denied"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    ADMIN_ACTION = "admin_action"
    CONFIGURATION_CHANGE = "configuration_change"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    XSS_ATTEMPT = "xss_attempt"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    CSRF_VIOLATION = "csrf_violation"
    INPUT_VALIDATION_FAILED = "input_validation_failed"
    API_KEY_USED = "api_key_used"
    API_KEY_INVALID = "api_key_invalid"
    SESSION_HIJACK_ATTEMPT = "session_hijack_attempt"
    COMPLIANCE_VIOLATION = "compliance_violation"

@dataclass
class SecurityEvent:
    """Security event data structure."""
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    success: bool
    message: str
    details: Dict[str, Any]
    risk_level: str  # low, medium, high, critical
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None

class AuditLogger:
    """Comprehensive audit logging service."""
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize audit logger."""
        self.app = app
        self.logger = None
        self.security_logger = None
        self.compliance_logger = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize audit logging for Flask app."""
        self.app = app
        self._setup_loggers()
        
        # Add request tracking
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_request(self._teardown_request)
    
    def _setup_loggers(self):
        """Setup specialized loggers for different types of events."""
        # General audit logger
        self.logger = logging.getLogger('bdc.audit')
        self.logger.setLevel(logging.INFO)
        
        # Security events logger
        self.security_logger = logging.getLogger('bdc.security')
        self.security_logger.setLevel(logging.WARNING)
        
        # Compliance logger (for GDPR, SOC2, etc.)
        self.compliance_logger = logging.getLogger('bdc.compliance')
        self.compliance_logger.setLevel(logging.INFO)
        
        # Create handlers if they don't exist
        if not self.logger.handlers:
            self._create_handlers()
    
    def _create_handlers(self):
        """Create log handlers for different log types."""
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Audit log handler
        audit_handler = logging.handlers.RotatingFileHandler(
            'logs/audit.log',
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        audit_handler.setFormatter(log_format)
        self.logger.addHandler(audit_handler)
        
        # Security log handler
        security_handler = logging.handlers.RotatingFileHandler(
            'logs/security.log',
            maxBytes=50*1024*1024,  # 50MB
            backupCount=20  # Keep more security logs
        )
        security_handler.setFormatter(log_format)
        self.security_logger.addHandler(security_handler)
        
        # Compliance log handler
        compliance_handler = logging.handlers.RotatingFileHandler(
            'logs/compliance.log',
            maxBytes=50*1024*1024,  # 50MB
            backupCount=50  # Keep compliance logs longer
        )
        compliance_handler.setFormatter(log_format)
        self.compliance_logger.addHandler(compliance_handler)
        
        # Console handler for development
        if self.app.config.get('DEBUG'):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_format)
            self.logger.addHandler(console_handler)
            self.security_logger.addHandler(console_handler)
    
    def _before_request(self):
        """Log request start and set up tracking."""
        g.request_start_time = time.time()
        g.request_id = self._generate_request_id()
        
        # Log request details for audit trail
        self.log_request_start()
    
    def _after_request(self, response):
        """Log request completion."""
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            g.request_duration = duration
        
        self.log_request_end(response)
        return response
    
    def _teardown_request(self, exception):
        """Log any request exceptions."""
        if exception:
            self.log_security_event(
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                success=False,
                message=f"Request exception: {str(exception)}",
                details={'exception_type': type(exception).__name__},
                risk_level='medium'
            )
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        return hashlib.sha256(f"{time.time()}{request.remote_addr}".encode()).hexdigest()[:16]
    
    def log_security_event(self, event_type: SecurityEventType, success: bool,
                          message: str, details: Optional[Dict[str, Any]] = None,
                          user_id: Optional[str] = None, risk_level: str = 'low'):
        """Log a security event."""
        if details is None:
            details = {}
        
        event = SecurityEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id or self._get_current_user_id(),
            session_id=self._get_session_id(),
            ip_address=self._get_client_ip(),
            user_agent=request.headers.get('User-Agent', 'Unknown'),
            endpoint=request.endpoint or 'unknown',
            method=request.method,
            success=success,
            message=message,
            details=details,
            risk_level=risk_level,
            request_id=getattr(g, 'request_id', None)
        )
        
        # Log to appropriate logger based on risk level
        log_data = self._serialize_event(event)
        
        if risk_level in ['high', 'critical']:
            self.security_logger.error(log_data)
        elif risk_level == 'medium':
            self.security_logger.warning(log_data)
        else:
            self.logger.info(log_data)
        
        # Also log to compliance logger for specific event types
        compliance_events = [
            SecurityEventType.DATA_ACCESS,
            SecurityEventType.DATA_MODIFICATION,
            SecurityEventType.DATA_DELETION,
            SecurityEventType.ADMIN_ACTION,
            SecurityEventType.CONFIGURATION_CHANGE
        ]
        
        if event_type in compliance_events:
            self.compliance_logger.info(log_data)
    
    def log_authentication_event(self, event_type: SecurityEventType, 
                                username: str, success: bool, 
                                details: Optional[Dict[str, Any]] = None):
        """Log authentication-related events."""
        if details is None:
            details = {}
        
        details['username'] = username
        risk_level = 'low' if success else 'medium'
        
        message = f"Authentication event: {event_type.value} for user {username}"
        
        self.log_security_event(
            event_type=event_type,
            success=success,
            message=message,
            details=details,
            risk_level=risk_level
        )
    
    def log_data_access(self, resource_type: str, resource_id: str,
                       action: str, success: bool = True):
        """Log data access events for compliance."""
        self.log_security_event(
            event_type=SecurityEventType.DATA_ACCESS,
            success=success,
            message=f"Data access: {action} on {resource_type} {resource_id}",
            details={
                'resource_type': resource_type,
                'resource_id': resource_id,
                'action': action
            },
            risk_level='low'
        )
    
    def log_admin_action(self, action: str, target: str, 
                        details: Optional[Dict[str, Any]] = None):
        """Log administrative actions."""
        self.log_security_event(
            event_type=SecurityEventType.ADMIN_ACTION,
            success=True,
            message=f"Admin action: {action} on {target}",
            details=details or {},
            risk_level='medium'
        )
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activity for security monitoring."""
        self.log_security_event(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            success=False,
            message=f"Suspicious activity detected: {activity_type}",
            details=details,
            risk_level='high'
        )
    
    def log_compliance_event(self, event_type: str, details: Dict[str, Any]):
        """Log compliance-related events."""
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'user_id': self._get_current_user_id(),
            'ip_address': self._get_client_ip(),
            'details': details
        }
        
        self.compliance_logger.info(json.dumps(log_data))
    
    def log_request_start(self):
        """Log request start for audit trail."""
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            self.logger.info(json.dumps({
                'event': 'request_start',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'request_id': getattr(g, 'request_id', None),
                'method': request.method,
                'endpoint': request.endpoint,
                'path': request.path,
                'ip_address': self._get_client_ip(),
                'user_agent': request.headers.get('User-Agent'),
                'user_id': self._get_current_user_id()
            }))
    
    def log_request_end(self, response):
        """Log request completion."""
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            self.logger.info(json.dumps({
                'event': 'request_end',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'request_id': getattr(g, 'request_id', None),
                'method': request.method,
                'endpoint': request.endpoint,
                'status_code': response.status_code,
                'duration': getattr(g, 'request_duration', 0),
                'ip_address': self._get_client_ip(),
                'user_id': self._get_current_user_id()
            }))
    
    def _serialize_event(self, event: SecurityEvent) -> str:
        """Serialize security event to JSON."""
        event_dict = asdict(event)
        event_dict['timestamp'] = event.timestamp.isoformat()
        event_dict['event_type'] = event.event_type.value
        return json.dumps(event_dict)
    
    def _get_current_user_id(self) -> Optional[str]:
        """Get current user ID from various sources."""
        # Try Flask-Login
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                return str(current_user.id)
        except ImportError:
            pass
        
        # Try JWT
        try:
            from flask_jwt_extended import get_jwt_identity
            return get_jwt_identity()
        except ImportError:
            pass
        
        # Try session
        from flask import session
        return session.get('user_id')
    
    def _get_session_id(self) -> Optional[str]:
        """Get session ID."""
        from flask import session
        return session.get('session_id') or session.sid
    
    def _get_client_ip(self) -> str:
        """Get client IP address."""
        # Check for forwarded headers
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        return request.remote_addr or '127.0.0.1'
    
    @contextmanager
    def audit_context(self, operation: str, resource: str):
        """Context manager for auditing operations."""
        start_time = time.time()
        
        try:
            self.log_security_event(
                event_type=SecurityEventType.DATA_ACCESS,
                success=True,
                message=f"Starting operation: {operation} on {resource}",
                details={'operation': operation, 'resource': resource},
                risk_level='low'
            )
            
            yield
            
            duration = time.time() - start_time
            self.log_security_event(
                event_type=SecurityEventType.DATA_ACCESS,
                success=True,
                message=f"Completed operation: {operation} on {resource}",
                details={
                    'operation': operation,
                    'resource': resource,
                    'duration': duration
                },
                risk_level='low'
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_security_event(
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                success=False,
                message=f"Failed operation: {operation} on {resource}",
                details={
                    'operation': operation,
                    'resource': resource,
                    'duration': duration,
                    'error': str(e)
                },
                risk_level='medium'
            )
            raise
    
    def get_security_events(self, event_type: Optional[SecurityEventType] = None,
                           user_id: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve security events for analysis."""
        # This would typically query a database or log aggregation system
        # For now, return empty list as this is file-based logging
        return []
    
    def generate_security_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate security report for the specified period."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time.replace(day=end_time.day - days)
        
        # This would analyze logs and generate a comprehensive report
        return {
            'period': f'{start_time.isoformat()} to {end_time.isoformat()}',
            'total_events': 0,
            'security_incidents': 0,
            'failed_logins': 0,
            'suspicious_activities': 0,
            'compliance_events': 0,
            'recommendations': []
        }