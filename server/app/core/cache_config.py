"""Cache configuration and strategies."""
from typing import Dict, Any, Optional
from datetime import timedelta


class CacheConfig:
    """Cache configuration for different resources."""
    
    # Default TTL values (in seconds)
    DEFAULT_TTL = 300  # 5 minutes
    SHORT_TTL = 60     # 1 minute
    MEDIUM_TTL = 300   # 5 minutes
    LONG_TTL = 900     # 15 minutes
    VERY_LONG_TTL = 3600  # 1 hour
    
    # Resource-specific TTL configurations
    RESOURCE_TTL = {
        # User-related
        'user_list': MEDIUM_TTL,
        'user_detail': LONG_TTL,
        'user_profile': LONG_TTL,
        'user_stats': VERY_LONG_TTL,
        
        # Beneficiary-related
        'beneficiary_list': MEDIUM_TTL,
        'beneficiary_detail': LONG_TTL,
        'beneficiary_stats': VERY_LONG_TTL,
        'beneficiary_documents': MEDIUM_TTL,
        'beneficiary_appointments': SHORT_TTL,  # More dynamic
        
        # Program-related
        'program_list': LONG_TTL,
        'program_detail': LONG_TTL,
        'program_enrollments': MEDIUM_TTL,
        
        # Evaluation-related
        'evaluation_list': MEDIUM_TTL,
        'evaluation_detail': LONG_TTL,
        'evaluation_results': VERY_LONG_TTL,
        
        # Static/Reference data
        'tenant_info': VERY_LONG_TTL,
        'system_settings': VERY_LONG_TTL,
        'reference_data': VERY_LONG_TTL,
        
        # Reports and analytics
        'analytics_dashboard': LONG_TTL,
        'reports': VERY_LONG_TTL,
        'statistics': LONG_TTL,
    }
    
    # Cache invalidation rules
    INVALIDATION_RULES = {
        'user': {
            'on_update': ['user_detail', 'user_profile', 'user_list'],
            'on_delete': ['user_detail', 'user_profile', 'user_list', 'user_stats'],
        },
        'beneficiary': {
            'on_update': ['beneficiary_detail', 'beneficiary_list'],
            'on_delete': ['beneficiary_detail', 'beneficiary_list', 'beneficiary_stats'],
            'on_document_add': ['beneficiary_documents'],
            'on_appointment_change': ['beneficiary_appointments'],
        },
        'program': {
            'on_update': ['program_detail', 'program_list'],
            'on_enrollment': ['program_enrollments', 'beneficiary_detail'],
        },
        'evaluation': {
            'on_complete': ['evaluation_detail', 'evaluation_results', 'beneficiary_detail'],
        }
    }
    
    @classmethod
    def get_ttl(cls, resource_type: str) -> int:
        """Get TTL for a resource type."""
        return cls.RESOURCE_TTL.get(resource_type, cls.DEFAULT_TTL)
    
    @classmethod
    def get_invalidation_rules(cls, entity_type: str, action: str) -> list:
        """Get cache keys to invalidate for an entity action."""
        rules = cls.INVALIDATION_RULES.get(entity_type, {})
        return rules.get(action, [])
    
    @classmethod
    def should_cache(cls, endpoint: str, method: str = 'GET') -> bool:
        """Determine if an endpoint should be cached."""
        # Only cache GET requests by default
        if method != 'GET':
            return False
        
        # Don't cache certain endpoints
        no_cache_patterns = [
            '/auth/',  # Authentication endpoints
            '/realtime/',  # Real-time data
            '/stream/',  # Streaming endpoints
            '/admin/',  # Admin endpoints (always fresh)
        ]
        
        for pattern in no_cache_patterns:
            if pattern in endpoint:
                return False
        
        return True


class CacheStrategy:
    """Different caching strategies."""
    
    @staticmethod
    def cache_aside(cache_manager, key: str, ttl: int, fetch_func, *args, **kwargs):
        """Cache-aside (lazy loading) pattern."""
        # Try cache first
        cached_value = cache_manager.get(key)
        if cached_value is not None:
            return cached_value
        
        # Fetch from source
        value = fetch_func(*args, **kwargs)
        
        # Store in cache
        if value is not None:
            cache_manager.set(key, value, ttl)
        
        return value
    
    @staticmethod
    def write_through(cache_manager, key: str, ttl: int, value: Any, persist_func, *args, **kwargs):
        """Write-through caching pattern."""
        # Write to persistent store first
        result = persist_func(value, *args, **kwargs)
        
        # If successful, update cache
        if result:
            cache_manager.set(key, value, ttl)
        
        return result
    
    @staticmethod
    def write_behind(cache_manager, key: str, ttl: int, value: Any, queue_func):
        """Write-behind (write-back) caching pattern."""
        # Update cache immediately
        cache_manager.set(key, value, ttl)
        
        # Queue write to persistent store
        queue_func(key, value)
        
        return True
    
    @staticmethod
    def refresh_ahead(cache_manager, key: str, ttl: int, refresh_threshold: float, fetch_func, *args, **kwargs):
        """Refresh-ahead caching pattern."""
        # Get from cache with TTL info
        cached_value = cache_manager.get(key)
        remaining_ttl = cache_manager.ttl(key)  # Would need to implement this
        
        # If cache is about to expire, refresh it asynchronously
        if cached_value and remaining_ttl and remaining_ttl < (ttl * refresh_threshold):
            # Queue background refresh
            # In production, use Celery or similar
            # celery_app.send_task('refresh_cache', args=[key, fetch_func, args, kwargs])
            pass
        
        # Return cached value or fetch new
        if cached_value is not None:
            return cached_value
        
        value = fetch_func(*args, **kwargs)
        cache_manager.set(key, value, ttl)
        return value


# Cache warming configuration
CACHE_WARM_ENDPOINTS = [
    # Critical endpoints to pre-warm on startup
    {
        'endpoint': '/api/v2/cached/statistics/beneficiaries',
        'method': 'GET',
        'params': {},
        'ttl': CacheConfig.VERY_LONG_TTL
    },
    {
        'endpoint': '/api/v2/cached/statistics/users',
        'method': 'GET',
        'params': {},
        'ttl': CacheConfig.VERY_LONG_TTL
    },
    # Add more endpoints to warm
]


def warm_cache(app, cache_manager):
    """Warm cache with critical data on startup."""
    with app.test_client() as client:
        for config in CACHE_WARM_ENDPOINTS:
            try:
                # Make request to endpoint
                response = client.get(
                    config['endpoint'],
                    query_string=config['params']
                )
                
                if response.status_code == 200:
                    app.logger.info(f"Cache warmed for {config['endpoint']}")
                else:
                    app.logger.warning(f"Failed to warm cache for {config['endpoint']}")
                    
            except Exception as e:
                app.logger.error(f"Error warming cache for {config['endpoint']}: {e}")