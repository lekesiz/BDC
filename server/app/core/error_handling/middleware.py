"""
Error Handling Middleware Integration.

Provides Flask middleware integration for comprehensive error handling across the application.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from flask import Flask, Request, Response, request, jsonify, g
from werkzeug.exceptions import HTTPException

from .error_manager import error_manager, ErrorContext
from .error_monitor import error_monitor
from .user_messages import error_message_mapper, UserMessageFormatter
from .exceptions import ErrorHandlingException
from ..exceptions import AppException


class ErrorHandlingMiddleware:
    """Flask middleware for comprehensive error handling."""
    
    def __init__(
        self,
        app: Optional[Flask] = None,
        logger: Optional[logging.Logger] = None,
        enable_monitoring: bool = True,
        include_stack_trace: bool = False,
        default_locale: str = "en"
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.enable_monitoring = enable_monitoring
        self.include_stack_trace = include_stack_trace
        self.default_locale = default_locale
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the middleware with a Flask app."""
        app.config.setdefault('ERROR_HANDLING_ENABLED', True)
        app.config.setdefault('ERROR_MONITORING_ENABLED', self.enable_monitoring)
        app.config.setdefault('ERROR_INCLUDE_STACK_TRACE', self.include_stack_trace)
        app.config.setdefault('ERROR_DEFAULT_LOCALE', self.default_locale)
        
        # Register error handlers
        self._register_error_handlers(app)
        
        # Register before/after request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        self.logger.info("Error handling middleware initialized")
    
    def _register_error_handlers(self, app: Flask):
        """Register error handlers with the Flask app."""
        
        @app.errorhandler(Exception)
        def handle_exception(error):
            """Handle all uncaught exceptions."""
            return self._handle_error(error, request)
        
        @app.errorhandler(HTTPException)
        def handle_http_exception(error):
            """Handle HTTP exceptions."""
            return self._handle_http_error(error, request)
        
        @app.errorhandler(AppException)
        def handle_app_exception(error):
            """Handle application-specific exceptions."""
            return self._handle_app_error(error, request)
        
        @app.errorhandler(ErrorHandlingException)
        def handle_error_handling_exception(error):
            """Handle error handling system exceptions."""
            return self._handle_error_handling_error(error, request)
    
    def _before_request(self):
        """Execute before each request."""
        # Store request start time for performance monitoring
        g.request_start_time = datetime.utcnow()
        
        # Initialize request context for error handling
        g.error_context = {
            'request_id': self._generate_request_id(),
            'endpoint': request.endpoint,
            'method': request.method,
            'url': request.url,
            'ip_address': self._get_client_ip(),
            'user_agent': request.headers.get('User-Agent'),
            'user_id': self._get_user_id(),
            'tenant_id': self._get_tenant_id()
        }
    
    def _after_request(self, response: Response) -> Response:
        """Execute after each request."""
        # Calculate request duration
        if hasattr(g, 'request_start_time'):
            duration = (datetime.utcnow() - g.request_start_time).total_seconds()
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        # Add request ID to response headers
        if hasattr(g, 'error_context'):
            response.headers['X-Request-ID'] = g.error_context.get('request_id', 'unknown')
        
        return response
    
    def _handle_error(self, error: Exception, req: Request) -> Tuple[Response, int]:
        """Handle general exceptions."""
        # Get error context
        error_context = self._build_error_context(error, req)
        
        # Handle the error through error manager
        error_info = error_manager.handle_error(
            error,
            context=error_context,
            user_id=error_context.get('user_id'),
            tenant_id=error_context.get('tenant_id'),
            request_id=error_context.get('request_id'),
            endpoint=error_context.get('endpoint'),
            method=error_context.get('method'),
            ip_address=error_context.get('ip_address'),
            user_agent=error_context.get('user_agent')
        )
        
        # Record for monitoring
        if self.enable_monitoring:
            try:
                error_monitor.record_error(error_info)
            except Exception as e:
                self.logger.error(f"Failed to record error for monitoring: {e}")
        
        # Get user-friendly message
        locale = self._get_locale(req)
        user_message = error_message_mapper.map_exception_to_message(
            error,
            locale,
            include_technical_details=self.include_stack_trace
        )
        
        # Build response
        response_data = self._build_error_response(error_info, user_message, error)
        
        # Determine status code
        status_code = self._get_status_code(error)
        
        return jsonify(response_data), status_code
    
    def _handle_http_error(self, error: HTTPException, req: Request) -> Tuple[Response, int]:
        """Handle HTTP exceptions."""
        # Build minimal error context
        error_context = self._build_error_context(error, req)
        
        # Create user-friendly message for HTTP errors
        locale = self._get_locale(req)
        
        # Map common HTTP errors to user messages
        http_error_messages = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN", 
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            429: "RATE_LIMITED",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
            504: "GATEWAY_TIMEOUT"
        }
        
        error_code = http_error_messages.get(error.code, "HTTP_ERROR")
        user_message = error_message_mapper.get_user_message(error_code, locale)
        
        # Build response
        response_data = {
            'success': False,
            'error': {
                'code': error_code,
                'message': user_message.message,
                'type': user_message.message_type.value,
                'suggested_actions': user_message.suggested_actions,
                'http_status': error.code,
                'request_id': error_context.get('request_id')
            }
        }
        
        if user_message.support_info:
            response_data['error']['support_info'] = user_message.support_info
        
        return jsonify(response_data), error.code
    
    def _handle_app_error(self, error: AppException, req: Request) -> Tuple[Response, int]:
        """Handle application-specific exceptions."""
        # Get error context
        error_context = self._build_error_context(error, req)
        
        # Handle through error manager
        error_info = error_manager.handle_error(
            error,
            context=error_context,
            user_id=error_context.get('user_id'),
            tenant_id=error_context.get('tenant_id'),
            request_id=error_context.get('request_id'),
            endpoint=error_context.get('endpoint'),
            method=error_context.get('method'),
            ip_address=error_context.get('ip_address'),
            user_agent=error_context.get('user_agent')
        )
        
        # Record for monitoring
        if self.enable_monitoring:
            try:
                error_monitor.record_error(error_info)
            except Exception as e:
                self.logger.error(f"Failed to record error for monitoring: {e}")
        
        # Get user-friendly message
        locale = self._get_locale(req)
        user_message = error_message_mapper.map_exception_to_message(
            error,
            locale,
            include_technical_details=self.include_stack_trace
        )
        
        # Build response using AppException's built-in structure
        response_data = {
            'success': False,
            'error': {
                'code': user_message.code,
                'message': user_message.message,
                'type': user_message.message_type.value,
                'suggested_actions': user_message.suggested_actions,
                'request_id': error_context.get('request_id'),
                'error_id': error_info.error_id
            }
        }
        
        if user_message.support_info:
            response_data['error']['support_info'] = user_message.support_info
        
        if self.include_stack_trace and user_message.technical_details:
            response_data['error']['technical_details'] = user_message.technical_details
        
        return jsonify(response_data), error.status_code
    
    def _handle_error_handling_error(self, error: ErrorHandlingException, req: Request) -> Tuple[Response, int]:
        """Handle errors from the error handling system itself."""
        self.logger.critical(f"Error handling system failure: {error}")
        
        # Fallback to basic error response
        response_data = {
            'success': False,
            'error': {
                'code': 'SYSTEM_ERROR',
                'message': 'An internal system error occurred. Please try again later.',
                'type': 'error',
                'request_id': getattr(g, 'error_context', {}).get('request_id', 'unknown')
            }
        }
        
        return jsonify(response_data), 500
    
    def _build_error_context(self, error: Exception, req: Request) -> Dict[str, Any]:
        """Build error context from request and error."""
        context = getattr(g, 'error_context', {}).copy()
        
        # Add error-specific information
        context.update({
            'error_type': type(error).__name__,
            'error_message': str(error),
            'request_data': self._get_safe_request_data(req),
            'headers': dict(req.headers),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return context
    
    def _build_error_response(
        self,
        error_info: ErrorContext,
        user_message,
        original_error: Exception
    ) -> Dict[str, Any]:
        """Build the error response data."""
        response_data = {
            'success': False,
            'error': UserMessageFormatter.to_dict(user_message, self.include_stack_trace)
        }
        
        # Add error tracking information
        response_data['error'].update({
            'error_id': error_info.error_id,
            'request_id': error_info.request_id,
            'timestamp': error_info.timestamp.isoformat(),
            'category': error_info.category.value,
            'severity': error_info.severity.value
        })
        
        return response_data
    
    def _get_status_code(self, error: Exception) -> int:
        """Determine HTTP status code for an exception."""
        if hasattr(error, 'status_code'):
            return error.status_code
        
        # Map exception types to status codes
        status_mappings = {
            ValueError: 400,
            KeyError: 400,
            TypeError: 400,
            PermissionError: 403,
            FileNotFoundError: 404,
            ConnectionError: 503,
            TimeoutError: 504
        }
        
        for exc_type, status_code in status_mappings.items():
            if isinstance(error, exc_type):
                return status_code
        
        return 500  # Default to internal server error
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _get_client_ip(self) -> str:
        """Get client IP address."""
        # Check for forwarded IPs first (for load balancers/proxies)
        forwarded_ips = request.headers.get('X-Forwarded-For')
        if forwarded_ips:
            return forwarded_ips.split(',')[0].strip()
        
        return request.headers.get('X-Real-IP', request.remote_addr)
    
    def _get_user_id(self) -> Optional[str]:
        """Get current user ID from request context."""
        # Try to get user ID from Flask-Login or similar
        try:
            from flask_login import current_user
            if hasattr(current_user, 'id') and current_user.is_authenticated:
                return str(current_user.id)
        except ImportError:
            pass
        
        # Try to get from JWT or session
        try:
            if hasattr(g, 'current_user') and g.current_user:
                return str(getattr(g.current_user, 'id', None))
        except:
            pass
        
        return None
    
    def _get_tenant_id(self) -> Optional[str]:
        """Get current tenant ID from request context."""
        # Try to get tenant ID from request context
        try:
            if hasattr(g, 'current_tenant') and g.current_tenant:
                return str(getattr(g.current_tenant, 'id', None))
        except:
            pass
        
        return None
    
    def _get_locale(self, req: Request) -> str:
        """Get locale from request."""
        # Try different sources for locale
        locale = (
            req.args.get('locale') or
            req.headers.get('Accept-Language', '').split(',')[0].split('-')[0] or
            self.default_locale
        )
        
        return locale.lower()
    
    def _get_safe_request_data(self, req: Request) -> Dict[str, Any]:
        """Get safe request data (excluding sensitive information)."""
        safe_data = {}
        
        # Include query parameters
        if req.args:
            safe_data['query_params'] = dict(req.args)
        
        # Include form data (excluding password fields)
        if req.form:
            form_data = {}
            for key, value in req.form.items():
                if 'password' not in key.lower() and 'secret' not in key.lower():
                    form_data[key] = value
                else:
                    form_data[key] = '[REDACTED]'
            safe_data['form_data'] = form_data
        
        # Include JSON data (excluding sensitive fields)
        if req.is_json:
            try:
                json_data = req.get_json()
                if isinstance(json_data, dict):
                    safe_json = {}
                    for key, value in json_data.items():
                        if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'token', 'key']):
                            safe_json[key] = '[REDACTED]'
                        else:
                            safe_json[key] = value
                    safe_data['json_data'] = safe_json
            except Exception:
                safe_data['json_data'] = '[INVALID JSON]'
        
        return safe_data


def create_error_handling_middleware(
    app: Optional[Flask] = None,
    enable_monitoring: bool = True,
    include_stack_trace: bool = False,
    default_locale: str = "en"
) -> ErrorHandlingMiddleware:
    """Factory function to create error handling middleware."""
    return ErrorHandlingMiddleware(
        app=app,
        enable_monitoring=enable_monitoring,
        include_stack_trace=include_stack_trace,
        default_locale=default_locale
    )