"""
Session Caching Optimization with Redis
Optimizes session storage and retrieval using Redis for better performance.
"""

import json
import pickle
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import redis
from flask import session, current_app
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from uuid import uuid4

from app.utils.logging import logger


class RedisSession(CallbackDict, SessionMixin):
    """Redis-backed session implementation"""
    
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    """Redis session interface for Flask"""
    
    serializer = pickle
    session_class = RedisSession
    
    def __init__(self, redis_client=None, key_prefix='session:', ttl=3600):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.ttl = ttl
        
    def generate_sid(self):
        """Generate a new session ID"""
        return str(uuid4())
    
    def get_redis_expiration_time(self, app, session):
        """Get Redis expiration time for session"""
        if session.permanent:
            return app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(days=31))
        return timedelta(seconds=self.ttl)
    
    def get_redis_key(self, sid):
        """Get Redis key for session ID"""
        return self.key_prefix + sid
    
    def open_session(self, app, request):
        """Open session from Redis"""
        sid = request.cookies.get(app.config.get('SESSION_COOKIE_NAME', 'session'))
        
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        
        try:
            key = self.get_redis_key(sid)
            data = self.redis.get(key)
            
            if data is not None:
                try:
                    session_data = self.serializer.loads(data)
                    return self.session_class(session_data, sid=sid)
                except Exception as e:
                    logger.error(f"Session deserialization error: {e}")
                    # Return new session if deserialization fails
                    return self.session_class(sid=sid, new=True)
            
            # Session doesn't exist, create new one
            return self.session_class(sid=sid, new=True)
            
        except Exception as e:
            logger.error(f"Session retrieval error: {e}")
            # Fallback to new session
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
    
    def save_session(self, app, session, response):
        """Save session to Redis"""
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        
        if not session:
            # Delete session
            if session.modified:
                try:
                    key = self.get_redis_key(session.sid)
                    self.redis.delete(key)
                except Exception as e:
                    logger.error(f"Session deletion error: {e}")
                
                response.delete_cookie(
                    app.config.get('SESSION_COOKIE_NAME', 'session'),
                    domain=domain,
                    path=path
                )
            return
        
        # Calculate expiration
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        
        try:
            # Serialize and save session
            key = self.get_redis_key(session.sid)
            data = self.serializer.dumps(dict(session))
            
            self.redis.setex(key, int(redis_exp.total_seconds()), data)
            
            # Set cookie
            response.set_cookie(
                app.config.get('SESSION_COOKIE_NAME', 'session'),
                session.sid,
                expires=cookie_exp,
                httponly=self.get_cookie_httponly(app),
                domain=domain,
                path=path,
                secure=self.get_cookie_secure(app),
                samesite=self.get_cookie_samesite(app)
            )
            
        except Exception as e:
            logger.error(f"Session save error: {e}")


class SessionCacheOptimizer:
    """Session caching optimizer with additional features"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.key_prefix = 'session:'
        self.user_sessions_prefix = 'user_sessions:'
        self.session_stats = {
            'created': 0,
            'retrieved': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0
        }
    
    def get_user_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user"""
        try:
            key = f"{self.user_sessions_prefix}{user_id}"
            session_ids = self.redis.smembers(key)
            
            active_sessions = []
            for sid in session_ids:
                session_key = f"{self.key_prefix}{sid.decode()}"
                session_data = self.redis.get(session_key)
                
                if session_data:
                    try:
                        data = pickle.loads(session_data)
                        active_sessions.append({
                            'session_id': sid.decode(),
                            'last_activity': data.get('last_activity'),
                            'ip_address': data.get('ip_address'),
                            'user_agent': data.get('user_agent')
                        })
                    except Exception as e:
                        logger.error(f"Session data parsing error: {e}")
                else:
                    # Remove stale session ID
                    self.redis.srem(key, sid)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    def invalidate_user_sessions(self, user_id: int, keep_current: Optional[str] = None):
        """Invalidate all sessions for a user except optionally the current one"""
        try:
            user_sessions = self.get_user_sessions(user_id)
            invalidated_count = 0
            
            for session_info in user_sessions:
                session_id = session_info['session_id']
                
                if keep_current and session_id == keep_current:
                    continue
                
                # Delete session data
                session_key = f"{self.key_prefix}{session_id}"
                self.redis.delete(session_key)
                
                # Remove from user sessions set
                user_key = f"{self.user_sessions_prefix}{user_id}"
                self.redis.srem(user_key, session_id)
                
                invalidated_count += 1
            
            logger.info(f"Invalidated {invalidated_count} sessions for user {user_id}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Error invalidating user sessions: {e}")
            return 0
    
    def track_user_session(self, user_id: int, session_id: str):
        """Track session ID for a user"""
        try:
            key = f"{self.user_sessions_prefix}{user_id}"
            self.redis.sadd(key, session_id)
            
            # Set expiration for user sessions tracking
            self.redis.expire(key, 86400 * 30)  # 30 days
            
        except Exception as e:
            logger.error(f"Error tracking user session: {e}")
    
    def update_session_activity(self, session_id: str, ip_address: str = None, user_agent: str = None):
        """Update session activity information"""
        try:
            session_key = f"{self.key_prefix}{session_id}"
            session_data = self.redis.get(session_key)
            
            if session_data:
                data = pickle.loads(session_data)
                data['last_activity'] = datetime.utcnow().isoformat()
                
                if ip_address:
                    data['ip_address'] = ip_address
                
                if user_agent:
                    data['user_agent'] = user_agent
                
                # Re-save with updated data
                ttl = self.redis.ttl(session_key)
                if ttl > 0:
                    self.redis.setex(session_key, ttl, pickle.dumps(data))
                
                self.session_stats['updated'] += 1
            
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            self.session_stats['errors'] += 1
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session caching statistics"""
        try:
            # Get total session count
            session_keys = self.redis.keys(f"{self.key_prefix}*")
            total_sessions = len(session_keys)
            
            # Get user session counts
            user_keys = self.redis.keys(f"{self.user_sessions_prefix}*")
            users_with_sessions = len(user_keys)
            
            # Calculate memory usage (approximate)
            memory_usage = 0
            sample_size = min(100, len(session_keys))
            
            if sample_size > 0:
                sample_keys = session_keys[:sample_size]
                for key in sample_keys:
                    try:
                        memory_usage += self.redis.memory_usage(key) or 0
                    except:
                        pass
                
                # Estimate total memory usage
                if sample_size > 0:
                    avg_memory_per_session = memory_usage / sample_size
                    memory_usage = avg_memory_per_session * total_sessions
            
            return {
                'total_sessions': total_sessions,
                'users_with_sessions': users_with_sessions,
                'estimated_memory_usage_bytes': memory_usage,
                'estimated_memory_usage_mb': memory_usage / (1024 * 1024),
                'operations': self.session_stats.copy()
            }
            
        except Exception as e:
            logger.error(f"Error getting session statistics: {e}")
            return {'error': str(e)}
    
    def cleanup_expired_sessions(self):
        """Clean up expired session references"""
        try:
            cleaned_count = 0
            
            # Clean up user session references
            user_keys = self.redis.keys(f"{self.user_sessions_prefix}*")
            
            for user_key in user_keys:
                try:
                    session_ids = self.redis.smembers(user_key)
                    
                    for session_id in session_ids:
                        session_key = f"{self.key_prefix}{session_id.decode()}"
                        
                        # Check if session still exists
                        if not self.redis.exists(session_key):
                            # Remove stale reference
                            self.redis.srem(user_key, session_id)
                            cleaned_count += 1
                    
                    # Remove empty user session sets
                    if self.redis.scard(user_key) == 0:
                        self.redis.delete(user_key)
                        
                except Exception as e:
                    logger.error(f"Error cleaning user key {user_key}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} expired session references")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
            return 0
    
    def get_session_security_info(self, session_id: str) -> Dict[str, Any]:
        """Get security information for a session"""
        try:
            session_key = f"{self.key_prefix}{session_id}"
            session_data = self.redis.get(session_key)
            
            if session_data:
                data = pickle.loads(session_data)
                
                return {
                    'session_id': session_id,
                    'last_activity': data.get('last_activity'),
                    'ip_address': data.get('ip_address'),
                    'user_agent': data.get('user_agent'),
                    'created_at': data.get('created_at'),
                    'user_id': data.get('user_id'),
                    'is_authenticated': 'user_id' in data,
                    'ttl_seconds': self.redis.ttl(session_key)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting session security info: {e}")
            return None


# Global session cache optimizer
session_cache_optimizer = SessionCacheOptimizer()


def init_session_caching(app):
    """Initialize Redis session caching for Flask app"""
    
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        # Create Redis client for sessions
        redis_client = redis.from_url(redis_url, decode_responses=False)
        
        # Test connection
        redis_client.ping()
        
        # Configure session interface
        app.session_interface = RedisSessionInterface(
            redis_client=redis_client,
            key_prefix='session:',
            ttl=app.config.get('PERMANENT_SESSION_LIFETIME', 3600)
        )
        
        # Initialize session cache optimizer
        session_cache_optimizer.redis = redis_client
        
        # Setup session hooks
        @app.before_request
        def before_request():
            """Track session activity"""
            if hasattr(session, 'sid'):
                from flask import request
                session_cache_optimizer.update_session_activity(
                    session.sid,
                    request.remote_addr,
                    request.headers.get('User-Agent')
                )
        
        logger.info(f"Session caching initialized with Redis: {redis_url}")
        
    except Exception as e:
        logger.error(f"Failed to initialize session caching: {e}")
        # Fall back to default session interface
        logger.warning("Falling back to default session interface")


def get_current_session_info():
    """Get information about the current session"""
    if hasattr(session, 'sid'):
        return session_cache_optimizer.get_session_security_info(session.sid)
    return None


def invalidate_all_user_sessions(user_id: int, keep_current: bool = False):
    """Invalidate all sessions for a user"""
    current_session_id = session.get('sid') if keep_current else None
    return session_cache_optimizer.invalidate_user_sessions(user_id, current_session_id)