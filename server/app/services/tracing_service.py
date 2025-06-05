"""
Distributed Tracing Service for BDC Application
Provides OpenTelemetry instrumentation and correlation ID management
"""

import uuid
import logging
import functools
import contextvars
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
import threading
import time
import os

from flask import request, g, current_app, has_request_context
from opentelemetry import trace, metrics, baggage
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import inject, extract
from opentelemetry.trace import Status, StatusCode
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.baggage import set_baggage, get_baggage

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Context variables for correlation tracking
correlation_id_context: contextvars.ContextVar = contextvars.ContextVar('correlation_id', default=None)
request_id_context: contextvars.ContextVar = contextvars.ContextVar('request_id', default=None)
user_context: contextvars.ContextVar = contextvars.ContextVar('user_context', default=None)

class TracingService:
    """
    Central service for managing distributed tracing and correlation IDs
    """
    
    def __init__(self):
        self.tracer_provider = None
        self.tracer = None
        self.meter = None
        self.enabled = False
        self.service_name = "bdc-backend"
        self.service_version = "1.0.0"
        self.environment = "production"
        
        # Metrics
        self.request_counter = None
        self.request_duration = None
        self.error_counter = None
        self.database_operation_counter = None
        self.database_operation_duration = None
        
        # Configuration
        self.jaeger_endpoint = None
        self.otlp_endpoint = None
        self.sample_rate = 1.0
        
        # Initialize if tracing is enabled
        if os.getenv('TRACING_ENABLED', 'true').lower() == 'true':
            self.initialize()
    
    def initialize(self):
        """Initialize OpenTelemetry tracing"""
        try:
            # Configuration from environment
            self.service_name = os.getenv('OTEL_SERVICE_NAME', 'bdc-backend')
            self.service_version = os.getenv('BDC_VERSION', '1.0.0')
            self.environment = os.getenv('BDC_ENVIRONMENT', 'production')
            self.jaeger_endpoint = os.getenv('OTEL_EXPORTER_JAEGER_ENDPOINT', 'http://jaeger:14268/api/traces')
            self.otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://otel-collector:4318')
            self.sample_rate = float(os.getenv('TRACING_SAMPLE_RATE', '1.0'))
            
            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": self.service_version,
                "deployment.environment": self.environment,
                "service.namespace": "bdc",
                "service.instance.id": f"{self.service_name}-{uuid.uuid4().hex[:8]}"
            })
            
            # Create tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)
            
            # Create exporters
            exporters = []
            
            # Jaeger exporter
            if self.jaeger_endpoint:
                jaeger_exporter = JaegerExporter(
                    endpoint=self.jaeger_endpoint,
                    collector_endpoint=self.jaeger_endpoint.replace('/api/traces', '/api/traces')
                )
                exporters.append(jaeger_exporter)
            
            # OTLP exporter
            if self.otlp_endpoint:
                otlp_exporter = OTLPSpanExporter(
                    endpoint=self.otlp_endpoint,
                    headers={"api-key": os.getenv('OTEL_API_KEY', 'demo')}
                )
                exporters.append(otlp_exporter)
            
            # Console exporter for development
            if self.environment == 'development':
                console_exporter = ConsoleSpanExporter()
                exporters.append(console_exporter)
            
            # Add exporters to tracer provider
            for exporter in exporters:
                span_processor = BatchSpanProcessor(
                    exporter,
                    max_queue_size=2048,
                    max_export_batch_size=512,
                    export_timeout_millis=30000,
                    schedule_delay_millis=5000
                )
                self.tracer_provider.add_span_processor(span_processor)
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__, self.service_version)
            
            # Initialize metrics
            self._initialize_metrics()
            
            # Auto-instrument libraries
            self._auto_instrument()
            
            self.enabled = True
            logger.info(f"Distributed tracing initialized for {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {str(e)}")
            self.enabled = False
    
    def _initialize_metrics(self):
        """Initialize custom metrics"""
        try:
            # Get meter
            self.meter = metrics.get_meter(__name__, self.service_version)
            
            # Request metrics
            self.request_counter = self.meter.create_counter(
                name="bdc_requests_total",
                description="Total number of HTTP requests",
                unit="1"
            )
            
            self.request_duration = self.meter.create_histogram(
                name="bdc_request_duration_seconds",
                description="HTTP request duration in seconds",
                unit="s"
            )
            
            self.error_counter = self.meter.create_counter(
                name="bdc_errors_total",
                description="Total number of errors",
                unit="1"
            )
            
            # Database metrics
            self.database_operation_counter = self.meter.create_counter(
                name="bdc_database_operations_total",
                description="Total number of database operations",
                unit="1"
            )
            
            self.database_operation_duration = self.meter.create_histogram(
                name="bdc_database_operation_duration_seconds",
                description="Database operation duration in seconds",
                unit="s"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics: {str(e)}")
    
    def _auto_instrument(self):
        """Auto-instrument Flask and other libraries"""
        try:
            # Instrument Flask
            FlaskInstrumentor().instrument()
            
            # Instrument SQLAlchemy
            SQLAlchemyInstrumentor().instrument()
            
            # Instrument Redis
            RedisInstrumentor().instrument()
            
            # Instrument Requests
            RequestsInstrumentor().instrument()
            
            logger.info("Auto-instrumentation completed")
            
        except Exception as e:
            logger.error(f"Auto-instrumentation failed: {str(e)}")
    
    def generate_correlation_id(self) -> str:
        """Generate a new correlation ID"""
        return f"bdc_{uuid.uuid4().hex}"
    
    def generate_request_id(self) -> str:
        """Generate a new request ID"""
        return f"req_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID"""
        # Try context variable first
        correlation_id = correlation_id_context.get()
        if correlation_id:
            return correlation_id
        
        # Try Flask request context
        if has_request_context():
            return getattr(g, 'correlation_id', None)
        
        # Try OpenTelemetry baggage
        return get_baggage('correlation_id')
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID in all contexts"""
        # Set in context variable
        correlation_id_context.set(correlation_id)
        
        # Set in Flask context if available
        if has_request_context():
            g.correlation_id = correlation_id
        
        # Set in OpenTelemetry baggage
        set_baggage('correlation_id', correlation_id)
        
        # Add to current span if available
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute('correlation_id', correlation_id)
    
    def get_request_id(self) -> Optional[str]:
        """Get current request ID"""
        # Try context variable first
        request_id = request_id_context.get()
        if request_id:
            return request_id
        
        # Try Flask request context
        if has_request_context():
            return getattr(g, 'request_id', None)
        
        return None
    
    def set_request_id(self, request_id: str):
        """Set request ID in all contexts"""
        # Set in context variable
        request_id_context.set(request_id)
        
        # Set in Flask context if available
        if has_request_context():
            g.request_id = request_id
        
        # Add to current span if available
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute('request_id', request_id)
    
    def get_user_context(self) -> Optional[Dict[str, Any]]:
        """Get current user context"""
        return user_context.get()
    
    def set_user_context(self, user_data: Dict[str, Any]):
        """Set user context"""
        user_context.set(user_data)
        
        # Add to current span if available
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute('user.id', user_data.get('user_id'))
            span.set_attribute('user.email', user_data.get('email'))
            span.set_attribute('user.role', user_data.get('role'))
    
    def create_span(self, 
                   name: str, 
                   kind: trace.SpanKind = trace.SpanKind.INTERNAL,
                   attributes: Dict[str, Any] = None) -> trace.Span:
        """Create a new span"""
        if not self.enabled or not self.tracer:
            return trace.NonRecordingSpan(trace.INVALID_SPAN_CONTEXT)
        
        span = self.tracer.start_span(name, kind=kind)
        
        # Add default attributes
        if span.is_recording():
            span.set_attribute('service.name', self.service_name)
            span.set_attribute('service.version', self.service_version)
            span.set_attribute('deployment.environment', self.environment)
            
            # Add correlation ID
            correlation_id = self.get_correlation_id()
            if correlation_id:
                span.set_attribute('correlation_id', correlation_id)
            
            # Add request ID
            request_id = self.get_request_id()
            if request_id:
                span.set_attribute('request_id', request_id)
            
            # Add user context
            user_data = self.get_user_context()
            if user_data:
                span.set_attribute('user.id', user_data.get('user_id'))
                span.set_attribute('user.role', user_data.get('role'))
            
            # Add custom attributes
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
        
        return span
    
    @contextmanager
    def trace_operation(self, 
                       operation_name: str,
                       kind: trace.SpanKind = trace.SpanKind.INTERNAL,
                       attributes: Dict[str, Any] = None):
        """Context manager for tracing an operation"""
        span = self.create_span(operation_name, kind, attributes)
        
        try:
            with trace.use_span(span):
                start_time = time.time()
                yield span
                
        except Exception as e:
            if span.is_recording():
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
        finally:
            if span.is_recording():
                # Record operation duration
                duration = time.time() - start_time
                span.set_attribute('operation.duration', duration)
                span.set_status(Status(StatusCode.OK))
            span.end()
    
    def inject_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """Inject tracing headers for outgoing requests"""
        if headers is None:
            headers = {}
        
        # Inject OpenTelemetry context
        inject(headers)
        
        # Add custom headers
        correlation_id = self.get_correlation_id()
        if correlation_id:
            headers['X-Correlation-ID'] = correlation_id
        
        request_id = self.get_request_id()
        if request_id:
            headers['X-Request-ID'] = request_id
        
        user_data = self.get_user_context()
        if user_data:
            headers['X-User-ID'] = str(user_data.get('user_id', ''))
            headers['X-User-Role'] = str(user_data.get('role', ''))
        
        return headers
    
    def extract_headers(self, headers: Dict[str, str]):
        """Extract tracing context from incoming headers"""
        # Extract OpenTelemetry context
        context = extract(headers)
        
        # Extract custom headers
        correlation_id = headers.get('X-Correlation-ID') or headers.get('x-correlation-id')
        if correlation_id:
            self.set_correlation_id(correlation_id)
        
        request_id = headers.get('X-Request-ID') or headers.get('x-request-id')
        if request_id:
            self.set_request_id(request_id)
        
        return context
    
    def record_request_metrics(self, 
                             method: str,
                             endpoint: str,
                             status_code: int,
                             duration: float):
        """Record HTTP request metrics"""
        if not self.enabled or not self.request_counter:
            return
        
        try:
            # Request counter
            self.request_counter.add(1, {
                "method": method,
                "endpoint": endpoint,
                "status_code": str(status_code),
                "service": self.service_name
            })
            
            # Request duration
            self.request_duration.record(duration, {
                "method": method,
                "endpoint": endpoint,
                "status_code": str(status_code),
                "service": self.service_name
            })
            
            # Error counter
            if status_code >= 400:
                self.error_counter.add(1, {
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": str(status_code),
                    "service": self.service_name
                })
                
        except Exception as e:
            logger.error(f"Failed to record request metrics: {str(e)}")
    
    def record_database_metrics(self, 
                              operation: str,
                              table: str,
                              duration: float,
                              success: bool = True):
        """Record database operation metrics"""
        if not self.enabled or not self.database_operation_counter:
            return
        
        try:
            # Database operation counter
            self.database_operation_counter.add(1, {
                "operation": operation,
                "table": table,
                "success": str(success),
                "service": self.service_name
            })
            
            # Database operation duration
            self.database_operation_duration.record(duration, {
                "operation": operation,
                "table": table,
                "success": str(success),
                "service": self.service_name
            })
            
        except Exception as e:
            logger.error(f"Failed to record database metrics: {str(e)}")

# Global tracing service instance
tracing_service = TracingService()

def trace_function(operation_name: str = None, 
                  kind: trace.SpanKind = trace.SpanKind.INTERNAL,
                  attributes: Dict[str, Any] = None):
    """
    Decorator for tracing function calls
    
    Usage:
        @trace_function("user_authentication")
        def authenticate_user(email, password):
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not tracing_service.enabled:
                return func(*args, **kwargs)
            
            func_attributes = attributes or {}
            func_attributes.update({
                'function.name': func.__name__,
                'function.module': func.__module__
            })
            
            with tracing_service.trace_operation(op_name, kind, func_attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    if span.is_recording():
                        span.set_attribute('function.result_type', type(result).__name__)
                    return result
                except Exception as e:
                    if span.is_recording():
                        span.set_attribute('function.error', str(e))
                    raise
        
        return wrapper
    return decorator

def trace_database_operation(operation: str, table: str = None):
    """
    Decorator for tracing database operations
    
    Usage:
        @trace_database_operation("select", "users")
        def get_user_by_id(user_id):
            # Database query implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not tracing_service.enabled:
                return func(*args, **kwargs)
            
            operation_name = f"db.{operation}"
            if table:
                operation_name += f".{table}"
            
            attributes = {
                'db.operation': operation,
                'db.table': table or 'unknown',
                'db.system': 'postgresql'
            }
            
            start_time = time.time()
            with tracing_service.trace_operation(
                operation_name, 
                trace.SpanKind.CLIENT, 
                attributes
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Record metrics
                    tracing_service.record_database_metrics(
                        operation, table or 'unknown', duration, True
                    )
                    
                    if span.is_recording():
                        span.set_attribute('db.rows_affected', getattr(result, 'rowcount', 0))
                    
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    
                    # Record error metrics
                    tracing_service.record_database_metrics(
                        operation, table or 'unknown', duration, False
                    )
                    
                    if span.is_recording():
                        span.set_attribute('db.error', str(e))
                    raise
        
        return wrapper
    return decorator

def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return tracing_service.get_correlation_id()

def set_correlation_id(correlation_id: str):
    """Set correlation ID"""
    tracing_service.set_correlation_id(correlation_id)

def get_request_id() -> Optional[str]:
    """Get current request ID"""
    return tracing_service.get_request_id()

def set_request_id(request_id: str):
    """Set request ID"""
    tracing_service.set_request_id(request_id)