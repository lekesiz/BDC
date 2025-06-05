"""
Alert Middleware for Flask Application
Automatically triggers alerts for critical errors and events
"""

import functools
import traceback
from datetime import datetime
from flask import request, g, current_app
from werkzeug.exceptions import HTTPException
import logging

from app.services.alert_service import (
    alert_service, 
    AlertSeverity, 
    send_critical_alert,
    send_security_alert,
    send_performance_alert
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AlertMiddleware:
    """
    Middleware to automatically trigger alerts for various application events
    """
    
    def __init__(self, app=None):
        self.app = app
        self.error_counts = {}
        self.performance_thresholds = {
            'response_time_warning': 5.0,  # seconds
            'response_time_critical': 10.0,  # seconds
            'memory_usage_warning': 80,  # percentage
            'memory_usage_critical': 90,  # percentage
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        self.app = app
        
        # Register error handlers
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
        
        # Register error handlers for different HTTP status codes
        app.register_error_handler(500, self.handle_500_error)
        app.register_error_handler(404, self.handle_404_error)
        app.register_error_handler(403, self.handle_403_error)
        app.register_error_handler(401, self.handle_401_error)
        app.register_error_handler(Exception, self.handle_generic_error)
        
        logger.info("Alert middleware initialized")
    
    def before_request(self):
        """Called before each request"""
        g.request_start_time = datetime.now()
        g.request_id = getattr(g, 'request_id', f"req_{int(datetime.now().timestamp())}")
        
        # Log request start for high-value endpoints
        if self._is_critical_endpoint(request.endpoint):
            logger.info(f"Critical endpoint accessed: {request.endpoint}")
    
    def after_request(self, response):
        """Called after each request"""
        if hasattr(g, 'request_start_time'):
            response_time = (datetime.now() - g.request_start_time).total_seconds()
            
            # Check for slow responses
            if response_time > self.performance_thresholds['response_time_critical']:
                send_performance_alert(
                    title="Critical Response Time Alert",
                    message=f"Endpoint {request.endpoint} took {response_time:.2f}s to respond",
                    severity=AlertSeverity.CRITICAL,
                    metadata={
                        "endpoint": request.endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "method": request.method,
                        "user_agent": request.user_agent.string,
                        "ip_address": request.remote_addr
                    },
                    correlation_id=getattr(g, 'request_id', None)
                )
            elif response_time > self.performance_thresholds['response_time_warning']:
                send_performance_alert(
                    title="Slow Response Time Warning",
                    message=f"Endpoint {request.endpoint} took {response_time:.2f}s to respond",
                    severity=AlertSeverity.MEDIUM,
                    metadata={
                        "endpoint": request.endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "method": request.method
                    },
                    correlation_id=getattr(g, 'request_id', None)
                )
            
            # Check for high error rates
            if response.status_code >= 500:
                self._track_error_rate(request.endpoint, response.status_code)
        
        return response
    
    def teardown_request(self, error=None):
        """Called at the end of each request"""
        if error:
            logger.error(f"Request teardown error: {str(error)}")
    
    def handle_500_error(self, error):
        """Handle 500 Internal Server Error"""
        send_critical_alert(
            title="Internal Server Error",
            message=f"500 error on {request.endpoint}: {str(error)}",
            source="flask-app",
            metadata={
                "endpoint": request.endpoint,
                "method": request.method,
                "error": str(error),
                "traceback": traceback.format_exc(),
                "user_agent": request.user_agent.string,
                "ip_address": request.remote_addr,
                "url": request.url
            },
            correlation_id=getattr(g, 'request_id', None)
        )
        
        return {
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(g, 'request_id', None)
        }, 500
    
    def handle_404_error(self, error):
        """Handle 404 Not Found Error"""
        # Only alert for suspicious 404 patterns
        if self._is_suspicious_404(request.path):
            send_security_alert(
                title="Suspicious 404 Pattern Detected",
                message=f"Potential security probe: {request.path}",
                metadata={
                    "path": request.path,
                    "method": request.method,
                    "user_agent": request.user_agent.string,
                    "ip_address": request.remote_addr,
                    "referer": request.referrer
                },
                correlation_id=getattr(g, 'request_id', None)
            )
        
        return {
            "error": "Not found",
            "message": "The requested resource was not found",
            "request_id": getattr(g, 'request_id', None)
        }, 404
    
    def handle_403_error(self, error):
        """Handle 403 Forbidden Error"""
        send_security_alert(
            title="Forbidden Access Attempt",
            message=f"403 error on {request.endpoint}: Unauthorized access attempt",
            metadata={
                "endpoint": request.endpoint,
                "method": request.method,
                "user_agent": request.user_agent.string,
                "ip_address": request.remote_addr,
                "user_id": getattr(g, 'current_user_id', None)
            },
            correlation_id=getattr(g, 'request_id', None)
        )
        
        return {
            "error": "Forbidden",
            "message": "You don't have permission to access this resource",
            "request_id": getattr(g, 'request_id', None)
        }, 403
    
    def handle_401_error(self, error):
        """Handle 401 Unauthorized Error"""
        # Track failed authentication attempts
        self._track_auth_failure(request.remote_addr)
        
        return {
            "error": "Unauthorized",
            "message": "Authentication required",
            "request_id": getattr(g, 'request_id', None)
        }, 401
    
    def handle_generic_error(self, error):
        """Handle any unhandled exceptions"""
        if isinstance(error, HTTPException):
            # Let HTTP exceptions be handled by their specific handlers
            raise error
        
        # This is an unhandled application error
        send_critical_alert(
            title="Unhandled Application Error",
            message=f"Unhandled exception: {str(error)}",
            source="flask-app",
            metadata={
                "endpoint": request.endpoint,
                "method": request.method,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "user_agent": request.user_agent.string,
                "ip_address": request.remote_addr,
                "url": request.url
            },
            correlation_id=getattr(g, 'request_id', None)
        )
        
        return {
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(g, 'request_id', None)
        }, 500
    
    def _is_critical_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is critical and should be monitored closely"""
        critical_endpoints = [
            'auth.login',
            'auth.logout',
            'admin.users',
            'api.evaluations',
            'api.payments',
            'api.export_data'
        ]
        return endpoint in critical_endpoints
    
    def _is_suspicious_404(self, path: str) -> bool:
        """Check if 404 path looks like a security probe"""
        suspicious_patterns = [
            '/admin', '/wp-admin', '/administrator',
            '/phpmyadmin', '/phpinfo', '/config',
            '/.env', '/.git', '/backup',
            '/shell', '/cmd', '/etc/passwd',
            '.php', '.asp', '.jsp'
        ]
        
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in suspicious_patterns)
    
    def _track_error_rate(self, endpoint: str, status_code: int):
        """Track error rates and alert on high error rates"""
        now = datetime.now()
        minute_key = f"{endpoint}_{now.strftime('%Y%m%d_%H%M')}"
        
        if minute_key not in self.error_counts:
            self.error_counts[minute_key] = {'total': 0, 'errors': 0}
        
        self.error_counts[minute_key]['total'] += 1
        
        if status_code >= 500:
            self.error_counts[minute_key]['errors'] += 1
        
        # Check error rate (alert if > 50% errors in a minute)
        counts = self.error_counts[minute_key]
        if counts['total'] >= 10 and counts['errors'] / counts['total'] > 0.5:
            send_critical_alert(
                title="High Error Rate Detected",
                message=f"High error rate on {endpoint}: {counts['errors']}/{counts['total']} requests failed",
                source="flask-app",
                metadata={
                    "endpoint": endpoint,
                    "error_rate": counts['errors'] / counts['total'],
                    "total_requests": counts['total'],
                    "failed_requests": counts['errors'],
                    "time_window": "1 minute"
                }
            )
    
    def _track_auth_failure(self, ip_address: str):
        """Track authentication failures and alert on brute force attempts"""
        now = datetime.now()
        minute_key = f"auth_failure_{ip_address}_{now.strftime('%Y%m%d_%H%M')}"
        
        if minute_key not in self.error_counts:
            self.error_counts[minute_key] = 0
        
        self.error_counts[minute_key] += 1
        
        # Alert on multiple auth failures from same IP
        if self.error_counts[minute_key] >= 5:
            send_security_alert(
                title="Potential Brute Force Attack",
                message=f"Multiple authentication failures from IP {ip_address}",
                metadata={
                    "ip_address": ip_address,
                    "failure_count": self.error_counts[minute_key],
                    "time_window": "1 minute",
                    "user_agent": request.user_agent.string
                }
            )

def alert_on_exception(severity: AlertSeverity = AlertSeverity.HIGH):
    """
    Decorator to automatically alert on function exceptions
    
    Usage:
        @alert_on_exception(AlertSeverity.CRITICAL)
        def critical_function():
            # This will send a critical alert if an exception occurs
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                alert_service.create_alert(
                    title=f"Exception in {func.__name__}",
                    message=f"Function {func.__name__} raised exception: {str(e)}",
                    severity=severity,
                    source="application",
                    event_type="function_exception",
                    metadata={
                        "function_name": func.__name__,
                        "module": func.__module__,
                        "args": str(args)[:200],  # Limit length
                        "kwargs": str(kwargs)[:200],  # Limit length
                        "exception_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
                )
                raise  # Re-raise the exception
        return wrapper
    return decorator

def alert_on_condition(condition_func, title: str, message: str, severity: AlertSeverity = AlertSeverity.MEDIUM):
    """
    Decorator to alert when a condition is met
    
    Usage:
        @alert_on_condition(
            lambda result: result['status'] == 'failed',
            "Process Failed",
            "Process returned failed status"
        )
        def some_process():
            return {'status': 'failed'}
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if condition_func(result):
                alert_service.create_alert(
                    title=title,
                    message=message,
                    severity=severity,
                    source="application",
                    event_type="condition_met",
                    metadata={
                        "function_name": func.__name__,
                        "result": str(result)[:500],  # Limit length
                        "condition": condition_func.__doc__ or "Custom condition"
                    }
                )
            
            return result
        return wrapper
    return decorator

# Performance monitoring decorator
def monitor_performance(warning_threshold: float = 5.0, critical_threshold: float = 10.0):
    """
    Decorator to monitor function performance and alert on slow execution
    
    Usage:
        @monitor_performance(warning_threshold=2.0, critical_threshold=5.0)
        def slow_function():
            # Will alert if function takes longer than thresholds
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                if execution_time > critical_threshold:
                    send_performance_alert(
                        title=f"Critical Performance Alert: {func.__name__}",
                        message=f"Function {func.__name__} took {execution_time:.2f}s to execute",
                        severity=AlertSeverity.CRITICAL,
                        metadata={
                            "function_name": func.__name__,
                            "execution_time": execution_time,
                            "threshold": critical_threshold
                        }
                    )
                elif execution_time > warning_threshold:
                    send_performance_alert(
                        title=f"Performance Warning: {func.__name__}",
                        message=f"Function {func.__name__} took {execution_time:.2f}s to execute",
                        severity=AlertSeverity.MEDIUM,
                        metadata={
                            "function_name": func.__name__,
                            "execution_time": execution_time,
                            "threshold": warning_threshold
                        }
                    )
                
                return result
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                send_critical_alert(
                    title=f"Function Exception with Performance Data: {func.__name__}",
                    message=f"Function {func.__name__} failed after {execution_time:.2f}s: {str(e)}",
                    source="application",
                    metadata={
                        "function_name": func.__name__,
                        "execution_time": execution_time,
                        "exception": str(e),
                        "traceback": traceback.format_exc()
                    }
                )
                raise
        return wrapper
    return decorator