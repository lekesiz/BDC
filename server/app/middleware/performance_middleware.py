"""
Performance Optimization Middleware
Provides response compression, field selection, pagination, and performance monitoring.
"""

import time
import gzip
import json
from typing import Dict, Any, List, Optional, Set
from functools import wraps
from io import BytesIO

from flask import request, Response, g, current_app, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

from app.utils.logging import logger


class ResponseCompressionMiddleware:
    """Middleware for response compression"""
    
    def __init__(self, app=None, compression_level: int = 6, min_size: int = 500):
        self.compression_level = compression_level
        self.min_size = min_size
        self.compressible_types = {
            'application/json',
            'application/javascript',
            'text/html',
            'text/css',
            'text/plain',
            'text/xml',
            'application/xml'
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        app.wsgi_app = self._wrap_wsgi_app(app.wsgi_app)
    
    def _wrap_wsgi_app(self, wsgi_app):
        """Wrap WSGI app with compression"""
        def compressed_app(environ, start_response):
            # Check if client accepts gzip encoding
            accept_encoding = environ.get('HTTP_ACCEPT_ENCODING', '')
            if 'gzip' not in accept_encoding:
                return wsgi_app(environ, start_response)
            
            # Capture response
            response_data = []
            response_status = []
            response_headers = []
            
            def capture_response(status, headers, exc_info=None):
                response_status.append(status)
                response_headers.extend(headers)
                return start_response(status, headers, exc_info)
            
            app_iter = wsgi_app(environ, capture_response)
            
            try:
                # Collect response data
                for data in app_iter:
                    response_data.append(data)
                
                # Check if we should compress
                if self._should_compress(response_headers, response_data):
                    compressed_data = self._compress_response(response_data)
                    
                    # Update headers
                    self._update_headers_for_compression(response_headers, compressed_data)
                    
                    return [compressed_data]
                else:
                    return response_data
            
            finally:
                if hasattr(app_iter, 'close'):
                    app_iter.close()
        
        return compressed_app
    
    def _should_compress(self, headers: List, data: List[bytes]) -> bool:
        """Determine if response should be compressed"""
        # Check content type
        content_type = None
        for header_name, header_value in headers:
            if header_name.lower() == 'content-type':
                content_type = header_value.split(';')[0].strip()
                break
        
        if content_type not in self.compressible_types:
            return False
        
        # Check content length
        total_size = sum(len(chunk) for chunk in data)
        return total_size >= self.min_size
    
    def _compress_response(self, data: List[bytes]) -> bytes:
        """Compress response data"""
        buffer = BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=self.compression_level) as gz_file:
            for chunk in data:
                gz_file.write(chunk)
        
        return buffer.getvalue()
    
    def _update_headers_for_compression(self, headers: List, compressed_data: bytes):
        """Update response headers for compression"""
        # Remove old content-length header
        headers[:] = [(name, value) for name, value in headers if name.lower() != 'content-length']
        
        # Add compression headers
        headers.append(('Content-Encoding', 'gzip'))
        headers.append(('Content-Length', str(len(compressed_data))))
        headers.append(('Vary', 'Accept-Encoding'))


class FieldSelectionMiddleware:
    """Middleware for API field selection to reduce payload size"""
    
    def __init__(self, app=None):
        self.field_param = 'fields'
        self.exclude_param = 'exclude'
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
    
    def _before_request(self):
        """Process field selection parameters"""
        g.selected_fields = None
        g.excluded_fields = None
        
        # Parse field selection parameters
        fields_param = request.args.get(self.field_param)
        exclude_param = request.args.get(self.exclude_param)
        
        if fields_param:
            g.selected_fields = set(fields_param.split(','))
        
        if exclude_param:
            g.excluded_fields = set(exclude_param.split(','))
    
    def _after_request(self, response: Response) -> Response:
        """Apply field selection to JSON responses"""
        if (response.content_type and 
            'application/json' in response.content_type and
            (g.get('selected_fields') or g.get('excluded_fields'))):
            
            try:
                data = response.get_json()
                if data:
                    filtered_data = self._filter_fields(data, g.get('selected_fields'), g.get('excluded_fields'))
                    response.data = json.dumps(filtered_data)
                    response.content_length = len(response.data)
            
            except Exception as e:
                logger.error(f"Field selection error: {e}")
        
        return response
    
    def _filter_fields(self, data: Any, selected_fields: Optional[Set[str]], excluded_fields: Optional[Set[str]]) -> Any:
        """Filter fields from data structure"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Check if field should be included
                include_field = True
                
                if selected_fields and key not in selected_fields:
                    include_field = False
                
                if excluded_fields and key in excluded_fields:
                    include_field = False
                
                if include_field:
                    result[key] = self._filter_fields(value, selected_fields, excluded_fields)
            
            return result
        
        elif isinstance(data, list):
            return [self._filter_fields(item, selected_fields, excluded_fields) for item in data]
        
        else:
            return data


class PaginationMiddleware:
    """Enhanced pagination middleware with performance optimization"""
    
    def __init__(self, app=None, default_per_page: int = 20, max_per_page: int = 100):
        self.default_per_page = default_per_page
        self.max_per_page = max_per_page
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        app.before_request(self._before_request)
    
    def _before_request(self):
        """Parse pagination parameters"""
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', self.default_per_page, type=int)
        
        # Validate parameters
        page = max(1, page)
        per_page = min(max(1, per_page), self.max_per_page)
        
        # Store in g for use in views
        g.pagination = {
            'page': page,
            'per_page': per_page,
            'offset': (page - 1) * per_page,
            'limit': per_page
        }


class PerformanceMonitoringMiddleware:
    """Middleware for tracking API performance metrics"""
    
    def __init__(self, app=None):
        self.metrics = {
            'total_requests': 0,
            'total_response_time': 0.0,
            'slow_requests': 0,
            'error_requests': 0,
            'endpoints': {}
        }
        self.slow_request_threshold = 2.0  # seconds
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
    
    def _before_request(self):
        """Start timing request"""
        g.start_time = time.time()
    
    def _after_request(self, response: Response) -> Response:
        """Log performance metrics"""
        if not hasattr(g, 'start_time'):
            return response
        
        # Calculate response time
        response_time = time.time() - g.start_time
        
        # Update global metrics
        self.metrics['total_requests'] += 1
        self.metrics['total_response_time'] += response_time
        
        # Track slow requests
        if response_time > self.slow_request_threshold:
            self.metrics['slow_requests'] += 1
            logger.warning(f"Slow request: {request.endpoint} ({response_time:.3f}s)")
        
        # Track errors
        if response.status_code >= 400:
            self.metrics['error_requests'] += 1
        
        # Track endpoint-specific metrics
        endpoint = request.endpoint or 'unknown'
        if endpoint not in self.metrics['endpoints']:
            self.metrics['endpoints'][endpoint] = {
                'requests': 0,
                'total_time': 0.0,
                'errors': 0,
                'average_time': 0.0
            }
        
        endpoint_metrics = self.metrics['endpoints'][endpoint]
        endpoint_metrics['requests'] += 1
        endpoint_metrics['total_time'] += response_time
        endpoint_metrics['average_time'] = endpoint_metrics['total_time'] / endpoint_metrics['requests']
        
        if response.status_code >= 400:
            endpoint_metrics['errors'] += 1
        
        # Add performance headers
        response.headers['X-Response-Time'] = f"{response_time:.3f}s"
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        total_requests = self.metrics['total_requests']
        if total_requests == 0:
            return self.metrics
        
        # Calculate average response time
        average_response_time = self.metrics['total_response_time'] / total_requests
        
        # Calculate error rate
        error_rate = (self.metrics['error_requests'] / total_requests) * 100
        
        # Calculate slow request rate
        slow_request_rate = (self.metrics['slow_requests'] / total_requests) * 100
        
        return {
            **self.metrics,
            'average_response_time': average_response_time,
            'error_rate_percentage': error_rate,
            'slow_request_rate_percentage': slow_request_rate
        }


class StreamingResponseMiddleware:
    """Middleware for streaming large responses"""
    
    def __init__(self, app=None, streaming_threshold: int = 1024 * 1024):  # 1MB
        self.streaming_threshold = streaming_threshold
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        # This would be implemented as a decorator or context manager
        # for specific endpoints that need streaming
        pass


def create_paginated_response(items: List[Any], total: int, page: int, per_page: int, 
                            endpoint: str = None, **kwargs) -> Dict[str, Any]:
    """Create a standardized paginated response"""
    total_pages = (total + per_page - 1) // per_page
    
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None
    }
    
    # Add navigation URLs if endpoint is provided
    if endpoint:
        from flask import url_for
        
        pagination_info['links'] = {
            'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
            'first': url_for(endpoint, page=1, per_page=per_page, **kwargs),
            'last': url_for(endpoint, page=total_pages, per_page=per_page, **kwargs)
        }
        
        if pagination_info['has_prev']:
            pagination_info['links']['prev'] = url_for(
                endpoint, page=pagination_info['prev_page'], per_page=per_page, **kwargs
            )
        
        if pagination_info['has_next']:
            pagination_info['links']['next'] = url_for(
                endpoint, page=pagination_info['next_page'], per_page=per_page, **kwargs
            )
    
    return {
        'data': items,
        'pagination': pagination_info
    }


def streaming_json_response(data_generator, chunk_size: int = 1024):
    """Create a streaming JSON response for large datasets"""
    def generate():
        yield '{"data":['
        
        first_item = True
        for item in data_generator:
            if not first_item:
                yield ','
            
            yield json.dumps(item)
            first_item = False
        
        yield ']}'
    
    return Response(
        generate(),
        content_type='application/json',
        headers={'Transfer-Encoding': 'chunked'}
    )


# Decorator for field selection
def supports_field_selection(func):
    """Decorator to enable field selection for an endpoint"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # The actual field selection is handled by the middleware
        # This decorator is just for documentation/marking
        return func(*args, **kwargs)
    
    return wrapper


# Decorator for pagination
def paginated_response(func):
    """Decorator to automatically paginate query results"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # If result is a query, apply pagination
        if hasattr(result, 'paginate'):
            pagination = g.get('pagination', {'page': 1, 'per_page': 20})
            
            paginated = result.paginate(
                page=pagination['page'],
                per_page=pagination['per_page'],
                error_out=False
            )
            
            return create_paginated_response(
                items=paginated.items,
                total=paginated.total,
                page=paginated.page,
                per_page=paginated.per_page,
                endpoint=request.endpoint
            )
        
        return result
    
    return wrapper


# Global middleware instances
compression_middleware = ResponseCompressionMiddleware()
field_selection_middleware = FieldSelectionMiddleware()
pagination_middleware = PaginationMiddleware()
performance_monitoring_middleware = PerformanceMonitoringMiddleware()
streaming_middleware = StreamingResponseMiddleware()


def init_performance_middleware(app):
    """Initialize all performance middleware"""
    compression_middleware.init_app(app)
    field_selection_middleware.init_app(app)
    pagination_middleware.init_app(app)
    performance_monitoring_middleware.init_app(app)
    streaming_middleware.init_app(app)
    
    logger.info("Performance middleware initialized")