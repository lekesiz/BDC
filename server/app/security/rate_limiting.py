"""
Advanced rate limiting and DDoS protection.
"""

import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, deque
from flask import Flask, request, g, abort, current_app
import redis
from functools import wraps

@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests: int
    window: int  # seconds
    per: str = "ip"  # ip, user, endpoint
    burst_requests: Optional[int] = None
    burst_window: Optional[int] = None

class RateLimitingService:
    """Advanced rate limiting service with DDoS protection."""
    
    def __init__(self, app: Optional[Flask] = None, redis_client: Optional[redis.Redis] = None):
        """Initialize rate limiting service."""
        self.app = app
        self.redis_client = redis_client
        self.memory_store = defaultdict(deque)
        self.blocked_ips = set()
        self.suspicious_ips = defaultdict(int)
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize rate limiting for Flask app."""
        self.app = app
        
        # Initialize Redis if URL provided
        redis_url = app.config.get('REDIS_URL')
        if redis_url and not self.redis_client:
            try:
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                app.logger.warning(f"Redis connection failed, using memory store: {e}")
        
        # Add rate limiting middleware
        app.before_request(self.check_rate_limit)
        
        # Cleanup task
        self._schedule_cleanup()
    
    def get_client_ip(self) -> str:
        """Get real client IP address considering proxies."""
        # Check for common proxy headers
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Take the first IP (original client)
            ip = forwarded_for.split(',')[0].strip()
            return ip
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to remote address
        return request.remote_addr or '127.0.0.1'
    
    def get_rate_limit_key(self, limit: RateLimit, endpoint: str = "") -> str:
        """Generate rate limit key based on configuration."""
        if limit.per == "ip":
            identifier = self.get_client_ip()
        elif limit.per == "user":
            identifier = self._get_user_id() or self.get_client_ip()
        elif limit.per == "endpoint":
            identifier = f"{endpoint}:{self.get_client_ip()}"
        else:
            identifier = self.get_client_ip()
        
        return f"rate_limit:{limit.per}:{identifier}:{endpoint}"
    
    def _get_user_id(self) -> Optional[str]:
        """Get current user ID."""
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                return str(current_user.id)
        except ImportError:
            pass
        
        # Try JWT token
        try:
            from flask_jwt_extended import get_jwt_identity
            return get_jwt_identity()
        except ImportError:
            pass
        
        return None
    
    def is_allowed(self, limit: RateLimit, endpoint: str = "") -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed based on rate limit."""
        key = self.get_rate_limit_key(limit, endpoint)
        current_time = int(time.time())
        
        # Use Redis if available, otherwise memory store
        if self.redis_client:
            return self._check_redis_rate_limit(key, limit, current_time)
        else:
            return self._check_memory_rate_limit(key, limit, current_time)
    
    def _check_redis_rate_limit(self, key: str, limit: RateLimit, 
                               current_time: int) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using Redis."""
        try:
            pipe = self.redis_client.pipeline()
            
            # Sliding window implementation
            window_start = current_time - limit.window
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, limit.window)
            
            results = pipe.execute()
            request_count = results[1]
            
            # Check burst limit if configured
            burst_allowed = True
            if limit.burst_requests and limit.burst_window:
                burst_key = f"{key}:burst"
                burst_start = current_time - limit.burst_window
                
                self.redis_client.zremrangebyscore(burst_key, 0, burst_start)
                burst_count = self.redis_client.zcard(burst_key)
                
                if burst_count >= limit.burst_requests:
                    burst_allowed = False
                else:
                    self.redis_client.zadd(burst_key, {str(current_time): current_time})
                    self.redis_client.expire(burst_key, limit.burst_window)
            
            allowed = request_count <= limit.requests and burst_allowed
            
            return allowed, {
                'requests': request_count,
                'limit': limit.requests,
                'window': limit.window,
                'reset_time': current_time + limit.window - (current_time % limit.window)
            }
            
        except Exception as e:
            current_app.logger.error(f"Redis rate limit error: {e}")
            # Fallback to allowing request if Redis fails
            return True, {}
    
    def _check_memory_rate_limit(self, key: str, limit: RateLimit, 
                                current_time: int) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using memory store."""
        request_times = self.memory_store[key]
        
        # Remove old entries
        window_start = current_time - limit.window
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # Check current count
        request_count = len(request_times)
        
        # Add current request if allowed
        if request_count < limit.requests:
            request_times.append(current_time)
            allowed = True
        else:
            allowed = False
        
        return allowed, {
            'requests': request_count,
            'limit': limit.requests,
            'window': limit.window,
            'reset_time': current_time + limit.window - (current_time % limit.window)
        }
    
    def check_rate_limit(self):
        """Middleware to check rate limits for requests."""
        # Skip for OPTIONS requests
        if request.method == 'OPTIONS':
            return
        
        # Check if IP is blocked
        client_ip = self.get_client_ip()
        if client_ip in self.blocked_ips:
            abort(429, description="IP temporarily blocked due to suspicious activity")
        
        # Get endpoint-specific rate limits
        endpoint = request.endpoint or 'unknown'
        limits = self._get_rate_limits_for_endpoint(endpoint)
        
        for limit in limits:
            allowed, info = self.is_allowed(limit, endpoint)
            
            if not allowed:
                # Track suspicious activity
                self._track_suspicious_activity(client_ip)
                
                # Add rate limit headers
                g.rate_limit_info = info
                
                # Log rate limit exceeded
                current_app.logger.warning(
                    f"Rate limit exceeded for {client_ip} on {endpoint}: "
                    f"{info.get('requests', 0)}/{info.get('limit', 0)} requests"
                )
                
                abort(429, description="Rate limit exceeded")
        
        # Track legitimate requests to detect patterns
        self._track_request_pattern(client_ip, endpoint)
    
    def _get_rate_limits_for_endpoint(self, endpoint: str) -> List[RateLimit]:
        """Get rate limits configured for specific endpoint."""
        limits = []
        
        # Default rate limit
        default_limit = current_app.config.get('RATELIMIT_DEFAULT', '100/hour')
        limits.append(self._parse_rate_limit(default_limit))
        
        # Endpoint-specific limits
        endpoint_limits = {
            'auth.login': RateLimit(5, 300, 'ip'),  # 5 login attempts per 5 minutes
            'auth.register': RateLimit(3, 3600, 'ip'),  # 3 registrations per hour
            'auth.reset_password': RateLimit(3, 3600, 'ip'),  # 3 password resets per hour
            'api.upload_file': RateLimit(10, 600, 'user'),  # 10 uploads per 10 minutes
            'api.send_email': RateLimit(20, 3600, 'user'),  # 20 emails per hour
        }
        
        if endpoint in endpoint_limits:
            limits.append(endpoint_limits[endpoint])
        
        # API endpoints get stricter limits
        if endpoint.startswith('api.'):
            api_limit = current_app.config.get('RATELIMIT_API', '1000/hour')
            limits.append(self._parse_rate_limit(api_limit, 'user'))
        
        return limits
    
    def _parse_rate_limit(self, limit_str: str, per: str = 'ip') -> RateLimit:
        """Parse rate limit string like '100/hour' into RateLimit object."""
        try:
            requests_str, period_str = limit_str.split('/')
            requests = int(requests_str)
            
            period_map = {
                'second': 1,
                'minute': 60,
                'hour': 3600,
                'day': 86400
            }
            
            window = period_map.get(period_str, 3600)
            return RateLimit(requests, window, per)
            
        except (ValueError, KeyError):
            # Default to 100 requests per hour
            return RateLimit(100, 3600, per)
    
    def _track_suspicious_activity(self, ip: str):
        """Track and respond to suspicious activity patterns."""
        self.suspicious_ips[ip] += 1
        
        # Block IP after multiple rate limit violations
        if self.suspicious_ips[ip] >= 10:
            self.blocked_ips.add(ip)
            current_app.logger.warning(f"Blocked IP {ip} due to repeated violations")
            
            # Schedule unblock after 1 hour
            if self.redis_client:
                self.redis_client.setex(f"blocked_ip:{ip}", 3600, "1")
    
    def _track_request_pattern(self, ip: str, endpoint: str):
        """Track request patterns for anomaly detection."""
        key = f"pattern:{ip}:{int(time.time() // 60)}"  # Per minute tracking
        
        if self.redis_client:
            try:
                self.redis_client.hincrby(key, endpoint, 1)
                self.redis_client.expire(key, 300)  # Keep for 5 minutes
                
                # Check for unusual patterns
                patterns = self.redis_client.hgetall(key)
                total_requests = sum(int(v) for v in patterns.values())
                
                # Alert on high volume from single IP
                if total_requests > 100:  # 100 requests per minute
                    current_app.logger.warning(
                        f"High volume detected from IP {ip}: {total_requests} requests/minute"
                    )
                    
            except Exception as e:
                current_app.logger.error(f"Pattern tracking error: {e}")
    
    def _schedule_cleanup(self):
        """Schedule cleanup of old data."""
        # This would typically be handled by a background task
        # For now, we'll do basic cleanup on each request
        pass
    
    def unblock_ip(self, ip: str):
        """Manually unblock an IP address."""
        self.blocked_ips.discard(ip)
        self.suspicious_ips.pop(ip, None)
        
        if self.redis_client:
            self.redis_client.delete(f"blocked_ip:{ip}")
    
    def get_rate_limit_status(self, ip: str = None) -> Dict[str, Any]:
        """Get current rate limit status for IP."""
        if not ip:
            ip = self.get_client_ip()
        
        status = {
            'ip': ip,
            'blocked': ip in self.blocked_ips,
            'violations': self.suspicious_ips.get(ip, 0),
            'limits': {}
        }
        
        # Check current status for each limit type
        for limit_type in ['default', 'login', 'api']:
            limit = self._get_rate_limits_for_endpoint(limit_type)[0]
            key = self.get_rate_limit_key(limit, limit_type)
            
            if self.redis_client:
                try:
                    count = self.redis_client.zcard(key)
                    status['limits'][limit_type] = {
                        'current': count,
                        'limit': limit.requests,
                        'window': limit.window
                    }
                except Exception:
                    pass
        
        return status


def rate_limit(requests: int, window: int, per: str = 'ip'):
    """Decorator for applying rate limits to specific routes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rate_limiter = RateLimitingService()
            limit = RateLimit(requests, window, per)
            
            allowed, info = rate_limiter.is_allowed(limit, request.endpoint)
            
            if not allowed:
                g.rate_limit_info = info
                abort(429, description="Rate limit exceeded")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator