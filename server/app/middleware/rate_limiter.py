"""Rate limiting middleware for Flask."""

import os
import time
import threading
from collections import defaultdict
from flask import request, abort, jsonify

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass

class RateLimiter:
    """Flask middleware for rate limiting requests."""
    
    def __init__(self, app=None):
        self.app = app
        self.lock = threading.Lock()
        self.in_memory_store = defaultdict(list)
        self.cleanup_interval = 60  # Cleanup every 60 seconds
        self.last_cleanup = time.time()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the rate limiter with the Flask app."""
        self.app = app
        
        # Parse rate limit configuration
        rate_limit = os.environ.get('RATE_LIMIT', '60,1')  # Default: 60 requests per minute
        try:
            self.limit, self.period = map(int, rate_limit.split(','))
        except (ValueError, AttributeError):
            self.limit, self.period = 60, 1  # Fallback default
            app.logger.warning(f"Invalid RATE_LIMIT format: {rate_limit}. Using default: 60,1")
        
        # Register error handler for rate limit exceeded
        app.errorhandler(RateLimitExceeded)(self.handle_rate_limit_exceeded)
        
        # Register before_request handler
        app.before_request(self.check_rate_limit)
    
    def get_client_identifier(self):
        """Get a unique identifier for the client (IP address by default)."""
        if 'X-Forwarded-For' in request.headers:
            ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        else:
            ip = request.remote_addr or '127.0.0.1'
        
        # Optionally use API key if available
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"{ip}:{api_key}"
            
        return ip
    
    def check_rate_limit(self):
        """Check if the request exceeds the rate limit."""
        # Skip rate limiting for certain endpoints
        if request.path == '/api/health':
            return
            
        # Check if current time is more than cleanup_interval since last cleanup
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self.cleanup_old_requests()
            self.last_cleanup = current_time
        
        client_id = self.get_client_identifier()
        
        with self.lock:
            # Get timestamps of requests from this client
            request_timestamps = self.in_memory_store[client_id]
            
            # Remove timestamps older than the rate limit period
            cutoff = current_time - self.period
            request_timestamps = [ts for ts in request_timestamps if ts > cutoff]
            
            # Update store with current request timestamps
            self.in_memory_store[client_id] = request_timestamps
            
            # Check if rate limit is exceeded
            if len(request_timestamps) >= self.limit:
                self.app.logger.warning(f"Rate limit exceeded for {client_id}. {len(request_timestamps)} requests in {self.period} seconds.")
                raise RateLimitExceeded()
            
            # Add current request timestamp
            self.in_memory_store[client_id].append(current_time)
    
    def cleanup_old_requests(self):
        """Remove old request timestamps to prevent memory leaks."""
        with self.lock:
            current_time = time.time()
            cutoff = current_time - self.period
            
            for client_id in list(self.in_memory_store.keys()):
                # Remove old timestamps
                timestamps = [ts for ts in self.in_memory_store[client_id] if ts > cutoff]
                
                # Remove client if no recent requests
                if not timestamps:
                    del self.in_memory_store[client_id]
                else:
                    self.in_memory_store[client_id] = timestamps
    
    def handle_rate_limit_exceeded(self, e):
        """Handle rate limit exceeded exception."""
        response = jsonify({
            'error': 'Rate limit exceeded',
            'message': f'You have exceeded the rate limit of {self.limit} requests per {self.period} seconds.'
        })
        response.status_code = 429
        return response