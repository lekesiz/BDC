"""
API Response Optimizer

Optimizes API responses through compression, caching headers,
response streaming, and payload optimization.
"""

import gzip
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from flask import Response, request, current_app
from werkzeug.http import parse_accept_header


@dataclass
class OptimizationConfig:
    """Response optimization configuration"""
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress responses larger than 1KB
    compression_level: int = 6  # gzip compression level (1-9)
    enable_caching_headers: bool = True
    default_cache_ttl: int = 3600
    enable_etag: bool = True
    enable_conditional_requests: bool = True
    max_response_size: int = 10 * 1024 * 1024  # 10MB
    enable_streaming: bool = True
    chunk_size: int = 8192


@dataclass
class ResponseMetrics:
    """Response optimization metrics"""
    responses_compressed: int = 0
    compression_ratio: float = 0.0
    cache_hits: int = 0
    conditional_requests: int = 0
    avg_response_size: int = 0
    avg_compression_time: float = 0.0


class ResponseOptimizer:
    """
    Advanced API response optimizer for improved performance and bandwidth efficiency.
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.metrics = ResponseMetrics()
        self.etag_cache = {}
        self.compression_stats = []
        
    def optimize_response(self, response: Response) -> Response:
        """
        Apply comprehensive response optimizations.
        """
        start_time = time.time()
        
        try:
            # Skip optimization for certain content types
            if self._should_skip_optimization(response):
                return response
            
            # Apply caching headers
            if self.config.enable_caching_headers:
                response = self._add_caching_headers(response)
            
            # Handle conditional requests (ETags)
            if self.config.enable_conditional_requests:
                response = self._handle_conditional_requests(response)
            
            # Apply compression
            if self.config.enable_compression:
                response = self._compress_response(response)
            
            # Add performance headers
            response = self._add_performance_headers(response, start_time)
            
            # Update metrics
            self._update_metrics(response, start_time)
            
        except Exception as e:
            logging.error(f"Response optimization failed: {e}")
        
        return response
    
    def create_streaming_response(self, data_generator, content_type: str = 'application/json') -> Response:
        """
        Create a streaming response for large datasets.
        """
        def generate():
            chunk_count = 0
            for chunk in data_generator:
                if isinstance(chunk, dict):
                    chunk = json.dumps(chunk)
                
                if isinstance(chunk, str):
                    chunk = chunk.encode('utf-8')
                
                # Yield chunk with size information
                yield f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n"
                chunk_count += 1
                
                # Yield final chunk
                if chunk_count % 100 == 0:  # Periodic flush
                    yield b"0\r\n\r\n"
        
        response = Response(
            generate(),
            content_type=content_type,
            headers={
                'Transfer-Encoding': 'chunked',
                'Cache-Control': 'no-cache',
                'X-Streaming': 'true'
            }
        )
        
        return response
    
    def optimize_json_response(self, data: Any, status_code: int = 200) -> Response:
        """
        Create optimized JSON response with compression and caching.
        """
        # Serialize JSON with optimizations
        json_data = self._optimize_json_serialization(data)
        
        # Create response
        response = Response(
            json_data,
            status=status_code,
            content_type='application/json; charset=utf-8'
        )
        
        # Apply optimizations
        return self.optimize_response(response)
    
    def create_paginated_response(self, data: List[Any], page: int, per_page: int,
                                total: int, endpoint: str) -> Dict[str, Any]:
        """
        Create optimized paginated response structure.
        """
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        # Build pagination links
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_prev': has_prev
        }
        
        # Add navigation links
        base_url = request.base_url
        if has_next:
            pagination['next_url'] = f"{base_url}?page={page + 1}&per_page={per_page}"
        if has_prev:
            pagination['prev_url'] = f"{base_url}?page={page - 1}&per_page={per_page}"
        
        pagination['first_url'] = f"{base_url}?page=1&per_page={per_page}"
        pagination['last_url'] = f"{base_url}?page={total_pages}&per_page={per_page}"
        
        return {
            'data': data,
            'pagination': pagination,
            'meta': {
                'total_count': total,
                'page_count': len(data),
                'cache_key': self._generate_cache_key(endpoint, page, per_page)
            }
        }
    
    def add_response_timing(self, response: Response, start_time: float) -> Response:
        """
        Add timing information to response headers.
        """
        processing_time = time.time() - start_time
        
        response.headers['X-Response-Time'] = f"{processing_time:.3f}s"
        response.headers['X-Processing-Time-Ms'] = f"{processing_time * 1000:.1f}"
        
        return response
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive optimization statistics.
        """
        stats = {
            'responses_compressed': self.metrics.responses_compressed,
            'compression_ratio': round(self.metrics.compression_ratio, 2),
            'cache_hits': self.metrics.cache_hits,
            'conditional_requests': self.metrics.conditional_requests,
            'avg_response_size_kb': round(self.metrics.avg_response_size / 1024, 2),
            'avg_compression_time_ms': round(self.metrics.avg_compression_time * 1000, 2)
        }
        
        # Calculate bandwidth savings
        if self.compression_stats:
            total_original = sum(stat['original_size'] for stat in self.compression_stats)
            total_compressed = sum(stat['compressed_size'] for stat in self.compression_stats)
            bandwidth_saved = total_original - total_compressed
            
            stats['bandwidth_saved_mb'] = round(bandwidth_saved / (1024 * 1024), 2)
            stats['bandwidth_saved_percent'] = round((bandwidth_saved / total_original) * 100, 1) if total_original > 0 else 0
        
        return stats
    
    # Private methods
    def _should_skip_optimization(self, response: Response) -> bool:
        """Check if response should skip optimization"""
        # Skip for certain content types
        content_type = response.content_type or ''
        skip_types = ['image/', 'video/', 'audio/', 'application/octet-stream']
        
        if any(ct in content_type for ct in skip_types):
            return True
        
        # Skip for very small responses
        if hasattr(response, 'content_length') and response.content_length:
            if response.content_length < 100:  # Less than 100 bytes
                return True
        
        # Skip for error responses that shouldn't be cached
        if response.status_code >= 500:
            return True
        
        return False
    
    def _add_caching_headers(self, response: Response) -> Response:
        """Add appropriate caching headers"""
        if response.status_code == 200:
            # Add cache control headers
            if 'Cache-Control' not in response.headers:
                if self._is_static_content(response):
                    # Static content - long cache
                    response.headers['Cache-Control'] = f'public, max-age={self.config.default_cache_ttl * 24}'  # 24x longer for static
                else:
                    # Dynamic content - shorter cache
                    response.headers['Cache-Control'] = f'public, max-age={self.config.default_cache_ttl}'
            
            # Add Vary header for content negotiation
            response.headers['Vary'] = 'Accept-Encoding, Accept'
        
        elif response.status_code == 304:
            # Not modified - keep existing cache headers
            pass
        else:
            # Other responses - no cache
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    def _handle_conditional_requests(self, response: Response) -> Response:
        """Handle ETags and conditional requests"""
        if not self.config.enable_etag or response.status_code != 200:
            return response
        
        # Generate ETag for response content
        if hasattr(response, 'get_data'):
            content = response.get_data()
            if content:
                etag = self._generate_etag(content)
                response.set_etag(etag)
                
                # Check if client has matching ETag
                if request.if_none_match and etag in request.if_none_match:
                    # Return 304 Not Modified
                    response.status_code = 304
                    response.data = b''
                    self.metrics.conditional_requests += 1
        
        return response
    
    def _compress_response(self, response: Response) -> Response:
        """Apply gzip compression to response"""
        # Check if compression is supported by client
        if not self._client_supports_compression():
            return response
        
        # Check response size threshold
        if hasattr(response, 'content_length') and response.content_length:
            if response.content_length < self.config.compression_threshold:
                return response
        
        # Get response data
        if not hasattr(response, 'get_data'):
            return response
        
        start_time = time.time()
        original_data = response.get_data()
        
        if not original_data or len(original_data) < self.config.compression_threshold:
            return response
        
        try:
            # Compress data
            compressed_data = gzip.compress(
                original_data, 
                compresslevel=self.config.compression_level
            )
            
            # Only use compression if it actually reduces size
            if len(compressed_data) < len(original_data):
                response.data = compressed_data
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = str(len(compressed_data))
                
                # Update metrics
                compression_time = time.time() - start_time
                self.metrics.responses_compressed += 1
                self.metrics.avg_compression_time = (
                    (self.metrics.avg_compression_time + compression_time) / 2
                )
                
                # Track compression statistics
                compression_ratio = len(compressed_data) / len(original_data)
                self.metrics.compression_ratio = (
                    (self.metrics.compression_ratio + compression_ratio) / 2
                )
                
                self.compression_stats.append({
                    'original_size': len(original_data),
                    'compressed_size': len(compressed_data),
                    'ratio': compression_ratio,
                    'time': compression_time
                })
                
                # Keep only recent stats
                if len(self.compression_stats) > 1000:
                    self.compression_stats = self.compression_stats[-500:]
        
        except Exception as e:
            logging.error(f"Response compression failed: {e}")
        
        return response
    
    def _add_performance_headers(self, response: Response, start_time: float) -> Response:
        """Add performance-related headers"""
        processing_time = time.time() - start_time
        
        response.headers['X-Optimization-Time'] = f"{processing_time:.4f}s"
        response.headers['X-Optimized'] = 'true'
        
        # Add content size information
        if hasattr(response, 'content_length') and response.content_length:
            response.headers['X-Content-Size'] = str(response.content_length)
        
        return response
    
    def _optimize_json_serialization(self, data: Any) -> str:
        """Optimize JSON serialization"""
        # Use compact JSON serialization
        return json.dumps(
            data,
            separators=(',', ':'),  # Remove spaces
            ensure_ascii=False,      # Allow unicode
            sort_keys=True          # Consistent ordering for caching
        )
    
    def _client_supports_compression(self) -> bool:
        """Check if client supports gzip compression"""
        accept_encoding = request.headers.get('Accept-Encoding', '')
        return 'gzip' in accept_encoding.lower()
    
    def _is_static_content(self, response: Response) -> bool:
        """Check if response contains static content"""
        content_type = response.content_type or ''
        static_types = [
            'text/css', 'text/javascript', 'application/javascript',
            'application/css', 'image/', 'font/', 'application/font'
        ]
        
        return any(st in content_type for st in static_types)
    
    def _generate_etag(self, content: bytes) -> str:
        """Generate ETag for content"""
        import hashlib
        return f'"{hashlib.md5(content).hexdigest()}"'
    
    def _generate_cache_key(self, endpoint: str, page: int, per_page: int) -> str:
        """Generate cache key for paginated responses"""
        import hashlib
        key_string = f"{endpoint}:page={page}:per_page={per_page}"
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def _update_metrics(self, response: Response, start_time: float):
        """Update optimization metrics"""
        # Update average response size
        if hasattr(response, 'content_length') and response.content_length:
            current_avg = self.metrics.avg_response_size
            new_size = response.content_length
            
            # Simple moving average
            self.metrics.avg_response_size = int((current_avg + new_size) / 2)