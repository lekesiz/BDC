"""
Tracing Middleware for Flask Application
Automatically instruments HTTP requests with distributed tracing
"""

import time
import uuid
from datetime import datetime
from flask import Flask, request, g, current_app, jsonify
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Status, StatusCode

from app.services.tracing_service import (
    tracing_service, 
    get_correlation_id, 
    set_correlation_id,
    get_request_id,
    set_request_id
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TracingMiddleware:
    """
    Middleware to automatically add distributed tracing to Flask requests
    """
    
    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the middleware with Flask app"""
        self.app = app
        
        # Register middleware hooks
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
        
        # Add response headers
        app.after_request(self.add_tracing_headers)
        
        logger.info("Tracing middleware initialized")
    
    def before_request(self):
        """Called before each request to set up tracing context"""
        if not tracing_service.enabled:
            return
        
        try:
            # Record request start time
            g.request_start_time = time.time()
            
            # Extract or generate correlation ID
            correlation_id = self._extract_correlation_id()
            if not correlation_id:
                correlation_id = tracing_service.generate_correlation_id()
            set_correlation_id(correlation_id)
            
            # Extract or generate request ID
            request_id = self._extract_request_id()
            if not request_id:
                request_id = tracing_service.generate_request_id()
            set_request_id(request_id)
            
            # Extract tracing headers
            headers = dict(request.headers)
            context = tracing_service.extract_headers(headers)
            
            # Set user context if available
            self._set_user_context()
            
            # Create span for the request
            span_name = f"{request.method} {self._get_route_pattern()}"
            span = tracing_service.create_span(
                span_name,
                trace.SpanKind.SERVER,
                self._get_request_attributes()
            )
            
            # Store span in context
            g.current_span = span
            g.trace_context = trace.set_span_in_context(span, context)
            
            # Log request start
            logger.debug(f"Request started: {span_name} [{correlation_id}]")
            
        except Exception as e:
            logger.error(f"Error in tracing before_request: {str(e)}")
    
    def after_request(self, response):
        """Called after each request to finalize tracing"""
        if not tracing_service.enabled:
            return response
        
        try:
            # Calculate request duration
            if hasattr(g, 'request_start_time'):
                duration = time.time() - g.request_start_time
                g.request_duration = duration
            else:
                duration = 0
            
            # Update span with response information
            if hasattr(g, 'current_span') and g.current_span.is_recording():
                self._update_span_with_response(g.current_span, response, duration)
            
            # Record metrics
            self._record_request_metrics(response, duration)
            
            # Log request completion
            correlation_id = get_correlation_id()
            logger.debug(f"Request completed: {request.method} {request.path} "
                        f"[{response.status_code}] [{correlation_id}] ({duration:.3f}s)")
            
        except Exception as e:
            logger.error(f"Error in tracing after_request: {str(e)}")
        
        return response
    
    def teardown_request(self, error=None):
        """Called at the end of request to clean up tracing"""
        if not tracing_service.enabled:
            return
        
        try:
            # Handle any errors
            if error and hasattr(g, 'current_span') and g.current_span.is_recording():
                g.current_span.record_exception(error)
                g.current_span.set_status(Status(StatusCode.ERROR, str(error)))
            
            # End the span
            if hasattr(g, 'current_span'):
                g.current_span.end()
            
        except Exception as e:
            logger.error(f"Error in tracing teardown_request: {str(e)}")
    
    def add_tracing_headers(self, response):
        """Add tracing headers to response"""
        try:
            # Add correlation ID header
            correlation_id = get_correlation_id()
            if correlation_id:
                response.headers['X-Correlation-ID'] = correlation_id
            
            # Add request ID header
            request_id = get_request_id()
            if request_id:
                response.headers['X-Request-ID'] = request_id
            
            # Add trace ID header if available
            if hasattr(g, 'current_span'):
                trace_id = f"{g.current_span.get_span_context().trace_id:032x}"
                response.headers['X-Trace-ID'] = trace_id
            
            # Add timing header
            if hasattr(g, 'request_duration'):
                response.headers['X-Response-Time'] = f"{g.request_duration:.3f}"
            
        except Exception as e:
            logger.error(f"Error adding tracing headers: {str(e)}")
        
        return response
    
    def _extract_correlation_id(self) -> str:
        """Extract correlation ID from request headers"""
        return (request.headers.get('X-Correlation-ID') or 
                request.headers.get('x-correlation-id') or
                request.headers.get('Correlation-ID'))
    
    def _extract_request_id(self) -> str:
        """Extract request ID from request headers"""
        return (request.headers.get('X-Request-ID') or 
                request.headers.get('x-request-id') or
                request.headers.get('Request-ID'))
    
    def _get_route_pattern(self) -> str:
        """Get the route pattern for the current request"""
        try:
            if request.endpoint:
                return request.url_rule.rule if request.url_rule else request.path
            return request.path
        except Exception:
            return request.path
    
    def _get_request_attributes(self) -> dict:
        """Get OpenTelemetry attributes for the request"""
        attributes = {
            SpanAttributes.HTTP_METHOD: request.method,
            SpanAttributes.HTTP_URL: request.url,
            SpanAttributes.HTTP_SCHEME: request.scheme,
            SpanAttributes.HTTP_HOST: request.host,
            SpanAttributes.HTTP_TARGET: request.path,
            SpanAttributes.HTTP_USER_AGENT: request.user_agent.string,
            SpanAttributes.HTTP_ROUTE: self._get_route_pattern(),
            'http.request.size': request.content_length or 0,
            'http.remote_addr': request.remote_addr,
            'http.endpoint': request.endpoint or 'unknown'
        }
        
        # Add query parameters (be careful with sensitive data)
        if request.args:
            # Only log non-sensitive query parameters
            safe_params = {}
            for key, value in request.args.items():
                if key.lower() not in ['password', 'token', 'key', 'secret']:
                    safe_params[key] = value
            if safe_params:
                attributes['http.query_params'] = str(safe_params)
        
        # Add request headers (excluding sensitive ones)
        sensitive_headers = {'authorization', 'cookie', 'x-api-key', 'x-auth-token'}
        for key, value in request.headers:
            header_key = key.lower()
            if header_key not in sensitive_headers:
                attributes[f"http.request.header.{header_key}"] = value
        
        return attributes
    
    def _update_span_with_response(self, span, response, duration):
        """Update span with response information"""
        if not span.is_recording():
            return
        
        try:
            # HTTP response attributes
            span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, response.status_code)
            span.set_attribute('http.response.size', len(response.get_data()))
            span.set_attribute('http.response.duration', duration)
            
            # Add response headers (excluding sensitive ones)
            sensitive_headers = {'set-cookie', 'authorization'}
            for key, value in response.headers:
                header_key = key.lower()
                if header_key not in sensitive_headers:
                    span.set_attribute(f"http.response.header.{header_key}", value)
            
            # Set span status based on HTTP status code
            if response.status_code >= 400:
                if response.status_code >= 500:
                    span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                else:
                    span.set_status(Status(StatusCode.OK))
            else:
                span.set_status(Status(StatusCode.OK))
            
            # Add performance classification
            if duration > 5.0:
                span.set_attribute('performance.classification', 'slow')
            elif duration > 1.0:
                span.set_attribute('performance.classification', 'medium')
            else:
                span.set_attribute('performance.classification', 'fast')
            
        except Exception as e:
            logger.error(f"Error updating span with response: {str(e)}")
    
    def _set_user_context(self):
        """Set user context from JWT or session"""
        try:
            # Try to get user from JWT token
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
            
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                if user_id:
                    # Get additional user info from JWT claims
                    claims = get_jwt()
                    user_data = {
                        'user_id': user_id,
                        'email': claims.get('email'),
                        'role': claims.get('role'),
                        'tenant_id': claims.get('tenant_id')
                    }
                    tracing_service.set_user_context(user_data)
            except Exception:
                # JWT verification failed or no token present
                pass
            
            # Alternative: Try to get user from session or other auth method
            if hasattr(g, 'current_user') and g.current_user:
                user_data = {
                    'user_id': g.current_user.id,
                    'email': g.current_user.email,
                    'role': g.current_user.role
                }
                tracing_service.set_user_context(user_data)
            
        except Exception as e:
            logger.debug(f"Could not set user context: {str(e)}")
    
    def _record_request_metrics(self, response, duration):
        """Record request metrics"""
        try:
            tracing_service.record_request_metrics(
                method=request.method,
                endpoint=self._get_route_pattern(),
                status_code=response.status_code,
                duration=duration
            )
        except Exception as e:
            logger.error(f"Error recording request metrics: {str(e)}")

def instrument_external_request(method: str, url: str, **kwargs):
    """
    Instrument external HTTP requests with tracing
    
    Usage:
        import requests
        response = instrument_external_request('GET', 'https://api.example.com/data')
    """
    if not tracing_service.enabled:
        import requests
        return requests.request(method, url, **kwargs)
    
    with tracing_service.trace_operation(
        f"HTTP {method.upper()}",
        trace.SpanKind.CLIENT,
        {
            SpanAttributes.HTTP_METHOD: method.upper(),
            SpanAttributes.HTTP_URL: url,
            'http.request.type': 'external'
        }
    ) as span:
        try:
            # Inject tracing headers
            headers = kwargs.get('headers', {})
            headers = tracing_service.inject_headers(headers)
            kwargs['headers'] = headers
            
            # Make the request
            import requests
            start_time = time.time()
            response = requests.request(method, url, **kwargs)
            duration = time.time() - start_time
            
            # Update span with response info
            if span.is_recording():
                span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, response.status_code)
                span.set_attribute('http.response.duration', duration)
                span.set_attribute('http.response.size', len(response.content))
                
                if response.status_code >= 400:
                    span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
                else:
                    span.set_status(Status(StatusCode.OK))
            
            return response
            
        except Exception as e:
            if span.is_recording():
                span.set_attribute('http.error', str(e))
            raise

def create_child_span(name: str, attributes: dict = None):
    """
    Create a child span of the current request span
    
    Usage:
        with create_child_span("database_query", {"table": "users"}) as span:
            # Database operation
            pass
    """
    return tracing_service.trace_operation(name, trace.SpanKind.INTERNAL, attributes)

def add_span_attribute(key: str, value: str):
    """Add attribute to current span"""
    span = trace.get_current_span()
    if span.is_recording():
        span.set_attribute(key, value)

def add_span_event(name: str, attributes: dict = None):
    """Add event to current span"""
    span = trace.get_current_span()
    if span.is_recording():
        span.add_event(name, attributes or {})

def record_span_exception(exception: Exception):
    """Record exception in current span"""
    span = trace.get_current_span()
    if span.is_recording():
        span.record_exception(exception)
        span.set_status(Status(StatusCode.ERROR, str(exception)))