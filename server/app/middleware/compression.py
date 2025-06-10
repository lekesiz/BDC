"""
Compression Middleware for BDC Platform
Provides response compression, static asset optimization, and bandwidth management.
"""

import gzip
import brotli
import zlib
import io
import logging
from flask import request, Response, current_app
from functools import wraps
from typing import Union, Tuple, Optional
import mimetypes
import os

logger = logging.getLogger(__name__)

class CompressionMiddleware:
    """Advanced compression middleware with multiple algorithms"""
    
    def __init__(self, app=None):
        self.app = app
        self.config = {
            'COMPRESSION_ENABLED': True,
            'COMPRESSION_LEVEL': 6,  # 1-9, higher = better compression
            'COMPRESSION_MIN_SIZE': 500,  # bytes
            'COMPRESSION_MIMETYPES': [
                'text/html',
                'text/css',
                'text/xml',
                'text/plain',
                'text/javascript',
                'application/javascript',
                'application/json',
                'application/xml',
                'application/rss+xml',
                'application/atom+xml',
                'application/font-woff',
                'application/font-woff2',
                'application/vnd.ms-fontobject',
                'application/x-font-ttf',
                'font/opentype',
                'image/svg+xml',
                'image/x-icon'
            ],
            'COMPRESSION_ALGORITHMS': ['br', 'gzip', 'deflate'],  # Order of preference
            'COMPRESSION_CACHE_ENABLED': True,
            'COMPRESSION_CACHE_SIZE': 100  # Number of compressed responses to cache
        }
        
        # Compression cache
        self.compression_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'bytes_saved': 0,
            'total_compressed': 0
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Update config from app
        for key in self.config:
            app_key = f'COMPRESS_{key}'
            if app_key in app.config:
                self.config[key] = app.config[app_key]
        
        # Register after_request handler
        app.after_request(self.compress_response)
    
    def compress_response(self, response: Response) -> Response:
        """Compress response if applicable"""
        try:
            # Check if compression is enabled
            if not self.config['COMPRESSION_ENABLED']:
                return response
            
            # Check if already compressed
            if response.headers.get('Content-Encoding'):
                return response
            
            # Check response size
            content_length = response.calculate_content_length()
            if content_length and content_length < self.config['COMPRESSION_MIN_SIZE']:
                return response
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if not self._should_compress(content_type):
                return response
            
            # Check if client accepts compression
            accept_encoding = request.headers.get('Accept-Encoding', '')
            algorithm = self._select_algorithm(accept_encoding)
            if not algorithm:
                return response
            
            # Try cache first
            if self.config['COMPRESSION_CACHE_ENABLED']:
                cached = self._get_cached_compression(response, algorithm)
                if cached:
                    self.cache_stats['hits'] += 1
                    return cached
                else:
                    self.cache_stats['misses'] += 1
            
            # Compress response
            compressed_response = self._compress_data(response, algorithm)
            
            # Cache if enabled
            if self.config['COMPRESSION_CACHE_ENABLED'] and compressed_response:
                self._cache_compression(response, algorithm, compressed_response)
            
            return compressed_response or response
            
        except Exception as e:
            logger.error(f"Compression error: {str(e)}")
            return response
    
    def _should_compress(self, content_type: str) -> bool:
        """Check if content type should be compressed"""
        if not content_type:
            return False
        
        # Extract base content type
        content_type = content_type.split(';')[0].strip().lower()
        
        # Check against allowed types
        for allowed_type in self.config['COMPRESSION_MIMETYPES']:
            if content_type == allowed_type or content_type.startswith(allowed_type + '/'):
                return True
        
        return False
    
    def _select_algorithm(self, accept_encoding: str) -> Optional[str]:
        """Select best compression algorithm based on client support"""
        accept_encoding = accept_encoding.lower()
        
        for algorithm in self.config['COMPRESSION_ALGORITHMS']:
            if algorithm in accept_encoding:
                return algorithm
        
        return None
    
    def _compress_data(self, response: Response, algorithm: str) -> Optional[Response]:
        """Compress response data using specified algorithm"""
        try:
            # Get response data
            data = response.get_data()
            original_size = len(data)
            
            # Compress based on algorithm
            if algorithm == 'br' and hasattr(brotli, 'compress'):
                compressed_data = brotli.compress(
                    data,
                    quality=self.config['COMPRESSION_LEVEL']
                )
            elif algorithm == 'gzip':
                compressed_data = gzip.compress(
                    data,
                    compresslevel=self.config['COMPRESSION_LEVEL']
                )
            elif algorithm == 'deflate':
                compressed_data = zlib.compress(
                    data,
                    level=self.config['COMPRESSION_LEVEL']
                )
            else:
                return None
            
            compressed_size = len(compressed_data)
            
            # Only use compression if it reduces size
            if compressed_size >= original_size:
                return None
            
            # Create new response with compressed data
            compressed_response = Response(
                compressed_data,
                status=response.status_code,
                headers=dict(response.headers)
            )
            
            # Update headers
            compressed_response.headers['Content-Encoding'] = algorithm
            compressed_response.headers['Content-Length'] = str(compressed_size)
            compressed_response.headers.add('Vary', 'Accept-Encoding')
            
            # Add compression stats header (optional)
            compression_ratio = round((1 - compressed_size / original_size) * 100, 1)
            compressed_response.headers['X-Compression-Ratio'] = f"{compression_ratio}%"
            
            # Update stats
            self.cache_stats['bytes_saved'] += (original_size - compressed_size)
            self.cache_stats['total_compressed'] += 1
            
            logger.debug(
                f"Compressed response: {original_size} -> {compressed_size} bytes "
                f"({compression_ratio}% reduction) using {algorithm}"
            )
            
            return compressed_response
            
        except Exception as e:
            logger.error(f"Compression failed for {algorithm}: {str(e)}")
            return None
    
    def _get_cache_key(self, response: Response, algorithm: str) -> str:
        """Generate cache key for compressed response"""
        import hashlib
        
        # Use content hash for cache key
        content = response.get_data()
        content_hash = hashlib.md5(content).hexdigest()
        
        return f"{algorithm}:{content_hash}"
    
    def _get_cached_compression(
        self,
        response: Response,
        algorithm: str
    ) -> Optional[Response]:
        """Get cached compressed response"""
        cache_key = self._get_cache_key(response, algorithm)
        
        if cache_key in self.compression_cache:
            cached_data, headers = self.compression_cache[cache_key]
            
            # Create response from cached data
            cached_response = Response(
                cached_data,
                status=response.status_code,
                headers=headers
            )
            
            return cached_response
        
        return None
    
    def _cache_compression(
        self,
        original_response: Response,
        algorithm: str,
        compressed_response: Response
    ):
        """Cache compressed response"""
        # Limit cache size
        if len(self.compression_cache) >= self.config['COMPRESSION_CACHE_SIZE']:
            # Remove oldest entry (simple FIFO)
            first_key = next(iter(self.compression_cache))
            del self.compression_cache[first_key]
        
        cache_key = self._get_cache_key(original_response, algorithm)
        self.compression_cache[cache_key] = (
            compressed_response.get_data(),
            dict(compressed_response.headers)
        )
    
    def get_stats(self) -> dict:
        """Get compression statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (
            (self.cache_stats['hits'] / total_requests * 100)
            if total_requests > 0 else 0
        )
        
        return {
            'enabled': self.config['COMPRESSION_ENABLED'],
            'algorithms': self.config['COMPRESSION_ALGORITHMS'],
            'cache_enabled': self.config['COMPRESSION_CACHE_ENABLED'],
            'cache_size': len(self.compression_cache),
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'cache_hit_rate': round(hit_rate, 2),
            'total_compressed': self.cache_stats['total_compressed'],
            'bytes_saved': self.cache_stats['bytes_saved'],
            'mb_saved': round(self.cache_stats['bytes_saved'] / 1024 / 1024, 2)
        }
    
    def clear_cache(self):
        """Clear compression cache"""
        self.compression_cache.clear()
        logger.info("Compression cache cleared")


def compress(algorithms: Union[str, list] = None, min_size: int = None):
    """Decorator to compress specific endpoints"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Execute the view function
            response = f(*args, **kwargs)
            
            # Convert to Response object if needed
            if not isinstance(response, Response):
                response = Response(response)
            
            # Apply compression settings for this endpoint
            if algorithms:
                response.headers['X-Compression-Algorithms'] = (
                    ','.join(algorithms) if isinstance(algorithms, list) else algorithms
                )
            
            if min_size is not None:
                response.headers['X-Compression-Min-Size'] = str(min_size)
            
            return response
        
        return wrapped
    return decorator


class StaticFileCompression:
    """Pre-compress static files for better performance"""
    
    @staticmethod
    def precompress_static_files(
        static_folder: str,
        extensions: list = None,
        algorithms: list = None
    ):
        """Pre-compress static files"""
        if extensions is None:
            extensions = ['.js', '.css', '.json', '.xml', '.svg', '.html']
        
        if algorithms is None:
            algorithms = ['gzip', 'br']
        
        compressed_count = 0
        total_saved = 0
        
        for root, dirs, files in os.walk(static_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext not in extensions:
                    continue
                
                # Skip already compressed files
                if file.endswith(('.gz', '.br')):
                    continue
                
                # Compress with each algorithm
                for algorithm in algorithms:
                    compressed_path = None
                    
                    try:
                        with open(file_path, 'rb') as f:
                            data = f.read()
                        
                        original_size = len(data)
                        
                        if algorithm == 'gzip':
                            compressed_data = gzip.compress(data, compresslevel=9)
                            compressed_path = f"{file_path}.gz"
                        elif algorithm == 'br' and hasattr(brotli, 'compress'):
                            compressed_data = brotli.compress(data, quality=11)
                            compressed_path = f"{file_path}.br"
                        
                        if compressed_path and len(compressed_data) < original_size:
                            with open(compressed_path, 'wb') as f:
                                f.write(compressed_data)
                            
                            saved = original_size - len(compressed_data)
                            total_saved += saved
                            compressed_count += 1
                            
                            logger.info(
                                f"Pre-compressed {file} with {algorithm}: "
                                f"{original_size} -> {len(compressed_data)} bytes"
                            )
                            
                    except Exception as e:
                        logger.error(f"Failed to compress {file_path}: {str(e)}")
        
        logger.info(
            f"Pre-compressed {compressed_count} files, "
            f"saved {total_saved / 1024 / 1024:.2f} MB"
        )
        
        return compressed_count, total_saved


# Response compression utilities
def gzip_response(data: Union[str, bytes], level: int = 6) -> Tuple[bytes, dict]:
    """Gzip compress response data"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    compressed = gzip.compress(data, compresslevel=level)
    
    headers = {
        'Content-Encoding': 'gzip',
        'Content-Length': str(len(compressed)),
        'Vary': 'Accept-Encoding'
    }
    
    return compressed, headers


def brotli_response(data: Union[str, bytes], quality: int = 4) -> Tuple[bytes, dict]:
    """Brotli compress response data"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    compressed = brotli.compress(data, quality=quality)
    
    headers = {
        'Content-Encoding': 'br',
        'Content-Length': str(len(compressed)),
        'Vary': 'Accept-Encoding'
    }
    
    return compressed, headers


# Global instance
compression_middleware = CompressionMiddleware()