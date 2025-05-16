"""
API response time optimization
"""
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime
import time
import gzip
import json
from flask import Response, request, g
from app.services.monitoring.performance_metrics import performance_monitor
from app.services.optimization.cache_strategy import cache_strategy
from app.core.cache import cache_service
import logging

logger = logging.getLogger(__name__)

class APIOptimizer:
    """API response optimization utilities"""
    
    def __init__(self):
        self.response_stats = {
            'total_requests': 0,
            'cached_responses': 0,
            'compressed_responses': 0,
            'average_response_time': 0,
            'slow_requests': 0
        }
        
        self.slow_request_threshold = 2000  # 2 seconds
        
    def optimize_response(self, 
                         cache_enabled: bool = True,
                         compress_enabled: bool = True,
                         cache_ttl: int = 300):
        """Decorator to optimize API responses"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                # Track request
                self.response_stats['total_requests'] += 1
                
                # Check cache if enabled
                if cache_enabled and request.method == 'GET':
                    cache_key = self._generate_response_cache_key()
                    cached_response = cache_service.get(cache_key)
                    
                    if cached_response:
                        self.response_stats['cached_responses'] += 1
                        return self._prepare_cached_response(cached_response)
                        
                # Execute endpoint
                response = func(*args, **kwargs)
                
                # Process response
                if isinstance(response, tuple):
                    data, status_code = response
                else:
                    data = response
                    status_code = 200
                    
                # Optimize response
                optimized_response = self._optimize_response_data(
                    data, 
                    compress_enabled,
                    cache_enabled,
                    cache_ttl
                )
                
                # Track performance
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                self._track_response_time(response_time)
                
                return optimized_response, status_code
                
            return wrapper
        return decorator
        
    def batch_api_decorator(self, max_batch_size: int = 100):
        """Decorator to enable batch processing for APIs"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check if batch request
                if request.method == 'POST' and 'batch' in request.json:
                    batch_requests = request.json.get('batch', [])
                    
                    if len(batch_requests) > max_batch_size:
                        return {'error': f'Batch size exceeds maximum of {max_batch_size}'}, 400
                        
                    # Process batch
                    results = []
                    for batch_item in batch_requests:
                        try:
                            # Execute individual request
                            result = func(**batch_item)
                            results.append({
                                'success': True,
                                'result': result
                            })
                        except Exception as e:
                            results.append({
                                'success': False,
                                'error': str(e)
                            })
                            
                    return {'batch_results': results}, 200
                    
                # Normal request
                return func(*args, **kwargs)
                
            return wrapper
        return decorator
        
    def paginate_response(self, 
                         query,
                         page: int = 1,
                         per_page: int = 20,
                         max_per_page: int = 100):
        """Paginate database query results"""
        # Validate pagination parameters
        page = max(1, page)
        per_page = min(max(1, per_page), max_per_page)
        
        # Get total count efficiently
        total = query.count()
        
        # Apply pagination
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Prepare response
        return {
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
        }
        
    def stream_large_response(self, data_generator: Callable, chunk_size: int = 1024):
        """Stream large responses to avoid memory issues"""
        def generate():
            for chunk in data_generator():
                if isinstance(chunk, (dict, list)):
                    yield json.dumps(chunk) + '\n'
                else:
                    yield chunk
                    
        return Response(generate(), mimetype='application/x-ndjson')
        
    def _optimize_response_data(self, data: Any, compress: bool, 
                               cache: bool, cache_ttl: int) -> Response:
        """Optimize response data"""
        # Convert to JSON
        json_data = json.dumps(data, default=str)
        
        # Compress if enabled and beneficial
        if compress and len(json_data) > 1024:  # Only compress if > 1KB
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            if len(compressed_data) < len(json_data) * 0.9:  # Only use if 10% smaller
                self.response_stats['compressed_responses'] += 1
                response = Response(
                    compressed_data,
                    mimetype='application/json',
                    headers={'Content-Encoding': 'gzip'}
                )
            else:
                response = Response(json_data, mimetype='application/json')
        else:
            response = Response(json_data, mimetype='application/json')
            
        # Cache if enabled
        if cache and request.method == 'GET':
            cache_key = self._generate_response_cache_key()
            cache_data = {
                'data': data,
                'headers': dict(response.headers),
                'timestamp': datetime.utcnow().isoformat()
            }
            cache_service.set(cache_key, cache_data, expire=cache_ttl)
            
        return response
        
    def _generate_response_cache_key(self) -> str:
        """Generate cache key for response"""
        # Include request path, query params, and headers
        key_parts = [
            'response',
            request.path,
            str(sorted(request.args.items())),
            request.headers.get('Authorization', ''),
            request.headers.get('Accept', '')
        ]
        
        key_string = ':'.join(key_parts)
        
        # Hash if too long
        if len(key_string) > 250:
            import hashlib
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"response:hash:{key_hash}"
            
        return key_string
        
    def _prepare_cached_response(self, cached_data: Dict) -> Response:
        """Prepare response from cached data"""
        data = cached_data.get('data')
        headers = cached_data.get('headers', {})
        
        response = Response(
            json.dumps(data, default=str),
            mimetype='application/json'
        )
        
        # Restore cached headers
        for key, value in headers.items():
            response.headers[key] = value
            
        # Add cache hit header
        response.headers['X-Cache'] = 'HIT'
        
        return response
        
    def _track_response_time(self, response_time: float):
        """Track response time metrics"""
        # Update average
        current_avg = self.response_stats['average_response_time']
        count = self.response_stats['total_requests']
        new_avg = ((current_avg * (count - 1)) + response_time) / count
        self.response_stats['average_response_time'] = new_avg
        
        # Track slow requests
        if response_time > self.slow_request_threshold:
            self.response_stats['slow_requests'] += 1
            logger.warning(f"Slow API request: {request.path} took {response_time:.2f}ms")
            
    def implement_rate_limiting(self, 
                              max_requests: int = 60,
                              window_seconds: int = 60):
        """Implement rate limiting for APIs"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Get client identifier (IP or auth token)
                client_id = request.remote_addr
                if g.get('current_user'):
                    client_id = f"user:{g.current_user.id}"
                    
                # Check rate limit
                rate_limit_key = f"rate_limit:{client_id}:{request.path}"
                current_count = cache_service.get(rate_limit_key) or 0
                
                if current_count >= max_requests:
                    return {
                        'error': 'Rate limit exceeded',
                        'retry_after': window_seconds
                    }, 429
                    
                # Increment counter
                cache_service.set(
                    rate_limit_key, 
                    current_count + 1,
                    expire=window_seconds
                )
                
                # Add rate limit headers
                response = func(*args, **kwargs)
                if isinstance(response, tuple):
                    data, status_code = response
                    response = Response(
                        json.dumps(data, default=str),
                        status=status_code,
                        mimetype='application/json'
                    )
                    
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Remaining'] = str(max_requests - current_count - 1)
                response.headers['X-RateLimit-Reset'] = str(int(time.time()) + window_seconds)
                
                return response
                
            return wrapper
        return decorator
        
    def implement_conditional_requests(self):
        """Implement HTTP conditional requests (ETag/Last-Modified)"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate ETag for GET requests
                if request.method == 'GET':
                    # Get response
                    response = func(*args, **kwargs)
                    
                    if isinstance(response, tuple):
                        data, status_code = response
                    else:
                        data = response
                        status_code = 200
                        
                    # Generate ETag
                    import hashlib
                    content = json.dumps(data, default=str, sort_keys=True)
                    etag = hashlib.md5(content.encode()).hexdigest()
                    
                    # Check If-None-Match header
                    if request.headers.get('If-None-Match') == etag:
                        return '', 304
                        
                    # Add ETag to response
                    response = Response(
                        content,
                        status=status_code,
                        mimetype='application/json'
                    )
                    response.headers['ETag'] = etag
                    
                    return response
                    
                return func(*args, **kwargs)
                
            return wrapper
        return decorator
        
    def optimize_json_serialization(self, data: Any) -> str:
        """Optimize JSON serialization for performance"""
        # Use ujson for faster serialization if available
        try:
            import ujson
            return ujson.dumps(data, default=str)
        except ImportError:
            return json.dumps(data, default=str)
            
    def implement_partial_response(self, fields: Optional[List[str]] = None):
        """Implement partial response to reduce payload size"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Get requested fields from query params
                requested_fields = request.args.get('fields', '').split(',')
                requested_fields = [f.strip() for f in requested_fields if f.strip()]
                
                # Get full response
                response = func(*args, **kwargs)
                
                if isinstance(response, tuple):
                    data, status_code = response
                else:
                    data = response
                    status_code = 200
                    
                # Filter response if fields specified
                if requested_fields and isinstance(data, dict):
                    filtered_data = {}
                    for field in requested_fields:
                        if field in data:
                            filtered_data[field] = data[field]
                    data = filtered_data
                    
                return data, status_code
                
            return wrapper
        return decorator
        
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get API optimization statistics"""
        total_requests = self.response_stats['total_requests']
        
        if total_requests > 0:
            cache_hit_rate = (self.response_stats['cached_responses'] / total_requests) * 100
            compression_rate = (self.response_stats['compressed_responses'] / total_requests) * 100
            slow_request_rate = (self.response_stats['slow_requests'] / total_requests) * 100
        else:
            cache_hit_rate = compression_rate = slow_request_rate = 0
            
        return {
            **self.response_stats,
            'cache_hit_rate': cache_hit_rate,
            'compression_rate': compression_rate,
            'slow_request_rate': slow_request_rate,
            'slow_request_threshold_ms': self.slow_request_threshold
        }
        
    @performance_monitor.track_performance('api_optimization')
    def analyze_api_performance(self) -> Dict[str, Any]:
        """Analyze API performance and suggest improvements"""
        stats = self.get_optimization_stats()
        suggestions = []
        
        # Check cache hit rate
        if stats['cache_hit_rate'] < 30:
            suggestions.append({
                'issue': 'Low cache hit rate',
                'suggestion': 'Consider increasing cache TTL or warming cache for frequently accessed data'
            })
            
        # Check slow requests
        if stats['slow_request_rate'] > 10:
            suggestions.append({
                'issue': 'High percentage of slow requests',
                'suggestion': 'Optimize database queries or implement pagination'
            })
            
        # Check compression usage
        if stats['compression_rate'] < 50:
            suggestions.append({
                'issue': 'Low compression usage',
                'suggestion': 'Enable compression for more response types'
            })
            
        return {
            'statistics': stats,
            'suggestions': suggestions,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }

# Initialize API optimizer
api_optimizer = APIOptimizer()