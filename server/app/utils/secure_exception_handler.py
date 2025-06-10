"""Secure exception handling framework for production safety."""

import logging
import traceback
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from flask import request, current_app, jsonify
import uuid
import hashlib


logger = logging.getLogger(__name__)


class SecurityException(Exception):
    """Base exception for security-related issues."""
    pass


class SensitiveDataException(SecurityException):
    """Exception for sensitive data exposure attempts."""
    pass


class RateLimitException(SecurityException):
    """Exception for rate limiting violations."""
    pass


class InputValidationException(SecurityException):
    """Exception for input validation failures."""
    pass


class SecureExceptionHandler:
    """Secure exception handling with sanitization and monitoring."""
    
    def __init__(self, app=None):
        self.app = app
        self.error_patterns = self._load_error_patterns()
        self.sensitive_patterns = self._load_sensitive_patterns()
        self.error_cache = {}  # Cache for preventing log flooding
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize secure exception handler with Flask app."""
        self.app = app
        
        # Register error handlers
        app.register_error_handler(Exception, self.handle_exception)
        app.register_error_handler(404, self.handle_404)
        app.register_error_handler(500, self.handle_500)
        app.register_error_handler(SecurityException, self.handle_security_exception)
        
        # Set up logging
        self._setup_secure_logging()
    
    def _load_error_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for categorizing errors."""
        return {
            'sql_injection': [
                'union select', 'drop table', 'delete from', 'insert into',
                'update set', 'create table', 'alter table', 'exec ',
                'execute', 'sp_', 'xp_', 'having ', 'information_schema'
            ],
            'xss_attempt': [
                '<script', 'javascript:', 'onload=', 'onerror=', 'onclick=',
                'onmouseover=', 'alert(', 'document.cookie', 'eval(',
                'window.location', 'document.write'
            ],
            'path_traversal': [
                '../', '..\\', '..\/', '..%2f', '..%5c', '%2e%2e',
                '/etc/passwd', '/etc/shadow', 'c:\\windows', 'boot.ini'
            ],
            'command_injection': [
                '|', '&', ';', '`', '$', '$(', '${', 'rm -', 'cat ',
                'ls ', 'ps ', 'wget ', 'curl ', 'nc ', 'netcat'
            ],
            'file_inclusion': [
                'php://', 'file://', 'http://', 'https://', 'ftp://',
                'expect://', 'data:', '/proc/', '/dev/', 'null'
            ]
        }
    
    def _load_sensitive_patterns(self) -> List[str]:
        """Load patterns for detecting sensitive data in errors."""
        return [
            r'password["\s]*[:=]["\s]*[^"\s]+',
            r'api[_-]?key["\s]*[:=]["\s]*[^"\s]+',
            r'secret["\s]*[:=]["\s]*[^"\s]+',
            r'token["\s]*[:=]["\s]*[^"\s]+',
            r'bearer [a-zA-Z0-9_-]+',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card pattern
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'postgresql://[^:]+:[^@]+@',
            r'mysql://[^:]+:[^@]+@',
            r'mongodb://[^:]+:[^@]+@'
        ]
    
    def _setup_secure_logging(self):
        """Setup secure logging configuration."""
        # Create security logger
        security_logger = logging.getLogger('security')
        security_logger.setLevel(logging.WARNING)
        
        # Create file handler for security events
        if self.app.config.get('LOG_TO_FILE', True):
            log_dir = self.app.config.get('LOG_DIR', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            security_handler = logging.FileHandler(
                os.path.join(log_dir, 'security.log')
            )
            security_handler.setLevel(logging.WARNING)
            
            # Secure formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            security_handler.setFormatter(formatter)
            security_logger.addHandler(security_handler)
    
    def handle_exception(self, error: Exception):
        """Handle general exceptions securely."""
        error_id = self._generate_error_id()
        sanitized_error = self._sanitize_error(error)
        
        # Categorize error
        error_category = self._categorize_error(str(error))
        
        # Log securely
        self._log_error_securely(error, error_id, error_category)
        
        # Check for security threats
        if error_category:
            self._handle_security_threat(error, error_category, error_id)
        
        # Return safe response
        if self.app.debug:
            return jsonify({
                'error': 'internal_error',
                'message': sanitized_error,
                'error_id': error_id,
                'debug_info': self._get_debug_info(error)
            }), 500
        else:
            return jsonify({
                'error': 'internal_error',
                'message': 'An internal error occurred. Please try again later.',
                'error_id': error_id
            }), 500
    
    def handle_404(self, error):
        """Handle 404 errors with security monitoring."""
        path = request.path if request else 'unknown'
        
        # Check for suspicious 404 patterns
        suspicious_patterns = [
            '.php', '.asp', '.jsp', 'wp-admin', 'admin.php',
            'phpmyadmin', 'wp-login', '.env', '.git', 'config.php'
        ]
        
        is_suspicious = any(pattern in path.lower() for pattern in suspicious_patterns)
        
        if is_suspicious:
            logger.warning(f"Suspicious 404 request: {path} from {self._get_client_ip()}")
        
        return jsonify({
            'error': 'not_found',
            'message': 'Resource not found'
        }), 404
    
    def handle_500(self, error):
        """Handle 500 errors securely."""
        error_id = self._generate_error_id()
        logger.error(f"Internal server error [{error_id}]: {error}")
        
        return jsonify({
            'error': 'internal_error',
            'message': 'Internal server error occurred',
            'error_id': error_id
        }), 500
    
    def handle_security_exception(self, error: SecurityException):
        """Handle security-specific exceptions."""
        error_id = self._generate_error_id()
        
        # Log security event
        security_logger = logging.getLogger('security')
        security_logger.error(
            f"Security exception [{error_id}]: {type(error).__name__} - "
            f"{str(error)} - IP: {self._get_client_ip()} - "
            f"User-Agent: {self._get_user_agent()}"
        )
        
        # Different responses for different security exceptions
        if isinstance(error, SensitiveDataException):
            return jsonify({
                'error': 'access_denied',
                'message': 'Access to sensitive data denied'
            }), 403
        
        elif isinstance(error, RateLimitException):
            return jsonify({
                'error': 'rate_limit_exceeded',
                'message': 'Rate limit exceeded. Please try again later.'
            }), 429
        
        elif isinstance(error, InputValidationException):
            return jsonify({
                'error': 'invalid_input',
                'message': 'Invalid input provided'
            }), 400
        
        else:
            return jsonify({
                'error': 'security_violation',
                'message': 'Security policy violation'
            }), 403
    
    def _sanitize_error(self, error: Exception) -> str:
        """Sanitize error message to remove sensitive information."""
        error_msg = str(error)
        
        # Remove sensitive patterns
        import re
        for pattern in self.sensitive_patterns:
            error_msg = re.sub(pattern, '[REDACTED]', error_msg, flags=re.IGNORECASE)
        
        # Remove file paths
        error_msg = re.sub(r'/[^\s]+\.py', '[FILE]', error_msg)
        error_msg = re.sub(r'\\[^\s]+\.py', '[FILE]', error_msg)
        
        # Remove line numbers
        error_msg = re.sub(r'line \d+', 'line [NUM]', error_msg)
        
        # Limit length
        if len(error_msg) > 500:
            error_msg = error_msg[:500] + '...'
        
        return error_msg
    
    def _categorize_error(self, error_msg: str) -> Optional[str]:
        """Categorize error to detect potential security threats."""
        error_msg_lower = error_msg.lower()
        
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern in error_msg_lower:
                    return category
        
        return None
    
    def _handle_security_threat(self, error: Exception, category: str, error_id: str):
        """Handle detected security threats."""
        client_ip = self._get_client_ip()
        user_agent = self._get_user_agent()
        
        # Log security event
        security_logger = logging.getLogger('security')
        security_logger.warning(
            f"Security threat detected [{error_id}]: {category} - "
            f"IP: {client_ip} - User-Agent: {user_agent} - "
            f"Path: {request.path if request else 'unknown'}"
        )
        
        # Implement rate limiting for suspicious IPs
        self._increment_threat_counter(client_ip, category)
        
        # Additional security measures could be implemented here
        # such as IP blocking, notification alerts, etc.
    
    def _log_error_securely(self, error: Exception, error_id: str, category: Optional[str]):
        """Log error with security considerations."""
        # Create error hash to prevent log flooding
        error_hash = hashlib.md5(str(error).encode()).hexdigest()
        
        # Check if we've seen this error recently
        if error_hash in self.error_cache:
            count, last_seen = self.error_cache[error_hash]
            if (datetime.now() - last_seen).seconds < 60:  # 1 minute
                self.error_cache[error_hash] = (count + 1, datetime.now())
                if count > 10:  # Don't log if seen more than 10 times in a minute
                    return
        else:
            self.error_cache[error_hash] = (1, datetime.now())
        
        # Prepare log data
        log_data = {
            'error_id': error_id,
            'error_type': type(error).__name__,
            'error_message': self._sanitize_error(error),
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'client_ip': self._get_client_ip(),
            'user_agent': self._get_user_agent(),
            'path': request.path if request else None,
            'method': request.method if request else None
        }
        
        # Log based on severity
        if category:
            logger.error(f"Categorized error [{error_id}]: {json.dumps(log_data)}")
        else:
            logger.info(f"Application error [{error_id}]: {json.dumps(log_data)}")
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID for tracking."""
        return str(uuid.uuid4())[:8]
    
    def _get_client_ip(self) -> str:
        """Get client IP address safely."""
        if not request:
            return 'unknown'
        
        # Check for forwarded headers (but be careful with spoofing)
        if 'X-Forwarded-For' in request.headers:
            return request.headers['X-Forwarded-For'].split(',')[0].strip()
        elif 'X-Real-IP' in request.headers:
            return request.headers['X-Real-IP']
        else:
            return request.remote_addr or 'unknown'
    
    def _get_user_agent(self) -> str:
        """Get user agent safely."""
        if not request:
            return 'unknown'
        return request.headers.get('User-Agent', 'unknown')[:200]  # Limit length
    
    def _get_debug_info(self, error: Exception) -> Dict[str, Any]:
        """Get debug information for development."""
        if not self.app.debug:
            return {}
        
        return {
            'traceback': traceback.format_exc(),
            'error_type': type(error).__name__,
            'error_args': str(error.args) if error.args else None
        }
    
    def _increment_threat_counter(self, ip: str, category: str):
        """Track threat attempts by IP."""
        # This could be implemented with Redis or database
        # For now, just log the pattern
        logger.warning(f"Threat pattern '{category}' from IP: {ip}")


def secure_try_except(
    exceptions: tuple = (Exception,),
    default_return=None,
    log_level: str = 'error',
    reraise: bool = False,
    sanitize: bool = True
):
    """
    Decorator for secure exception handling in functions.
    
    Args:
        exceptions: Tuple of exceptions to catch
        default_return: Default value to return on exception
        log_level: Logging level for caught exceptions
        reraise: Whether to re-raise the exception after logging
        sanitize: Whether to sanitize error messages
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                error_id = str(uuid.uuid4())[:8]
                
                # Sanitize error if requested
                if sanitize:
                    error_msg = SecureExceptionHandler._sanitize_error(None, e)
                else:
                    error_msg = str(e)
                
                # Log based on level
                log_message = f"Exception in {func.__name__} [{error_id}]: {error_msg}"
                
                if log_level == 'error':
                    logger.error(log_message)
                elif log_level == 'warning':
                    logger.warning(log_message)
                elif log_level == 'info':
                    logger.info(log_message)
                
                # Re-raise if requested
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def validate_input(
    validators: Dict[str, Callable],
    sanitize: bool = True,
    raise_on_failure: bool = True
):
    """
    Decorator for input validation with security checks.
    
    Args:
        validators: Dict mapping parameter names to validation functions
        sanitize: Whether to sanitize inputs
        raise_on_failure: Whether to raise exception on validation failure
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate arguments
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    
                    # Sanitize if requested
                    if sanitize and isinstance(value, str):
                        value = _sanitize_input(value)
                        bound_args.arguments[param_name] = value
                    
                    # Validate
                    if not validator(value):
                        error_msg = f"Validation failed for parameter: {param_name}"
                        
                        if raise_on_failure:
                            raise InputValidationException(error_msg)
                        else:
                            logger.warning(error_msg)
                            return None
            
            return func(*bound_args.args, **bound_args.kwargs)
        
        return wrapper
    return decorator


def _sanitize_input(value: str) -> str:
    """Sanitize input string for security."""
    import html
    
    # HTML escape
    value = html.escape(value)
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Limit length
    if len(value) > 10000:
        value = value[:10000]
    
    return value


# Utility functions for common validations
def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe."""
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    dangerous_extensions = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.php', '.asp', '.jsp', '.sh', '.py', '.pl', '.rb'
    ]
    
    return not any(filename.lower().endswith(ext) for ext in dangerous_extensions)


def is_safe_path(path: str) -> bool:
    """Check if file path is safe."""
    if not path or '..' in path or path.startswith('/'):
        return False
    
    dangerous_patterns = ['~', '$', '`', '|', '&', ';', '<', '>']
    return not any(pattern in path for pattern in dangerous_patterns)


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 254


def is_safe_sql_param(value: str) -> bool:
    """Check if value is safe for SQL operations."""
    dangerous_patterns = [
        'union', 'select', 'drop', 'delete', 'insert', 'update',
        'create', 'alter', 'exec', 'execute', 'sp_', 'xp_'
    ]
    
    value_lower = value.lower()
    return not any(pattern in value_lower for pattern in dangerous_patterns)