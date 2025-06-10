"""
Performance Optimization Initialization
Centralized initialization for all performance optimization components.
"""

import redis
from flask import Flask

from app.core.database_performance import db_performance_optimizer
from app.core.query_cache import init_query_cache
from app.core.memory_optimizer import init_memory_optimization
from app.middleware.performance_middleware import init_performance_middleware
from app.api.performance_monitoring import register_performance_monitoring
from app.utils.logging import logger


def init_performance_optimization(app: Flask):
    """Initialize comprehensive performance optimization for the BDC application"""
    
    logger.info("Initializing performance optimization...")
    
    # 1. Initialize database performance optimization
    try:
        db_performance_optimizer.init_app(app)
        logger.info("✅ Database performance optimization initialized")
    except Exception as e:
        logger.error(f"❌ Database performance initialization failed: {e}")
    
    # 2. Initialize query caching with Redis
    try:
        init_query_cache(app)
        logger.info("✅ Query caching initialized")
    except Exception as e:
        logger.error(f"❌ Query cache initialization failed: {e}")
    
    # 3. Initialize memory optimization
    try:
        init_memory_optimization(app)
        logger.info("✅ Memory optimization initialized")
    except Exception as e:
        logger.error(f"❌ Memory optimization initialization failed: {e}")
    
    # 4. Initialize performance middleware
    try:
        init_performance_middleware(app)
        logger.info("✅ Performance middleware initialized")
    except Exception as e:
        logger.error(f"❌ Performance middleware initialization failed: {e}")
    
    # 5. Register performance monitoring API
    try:
        register_performance_monitoring(app)
        logger.info("✅ Performance monitoring API registered")
    except Exception as e:
        logger.error(f"❌ Performance monitoring registration failed: {e}")
    
    # 6. Initialize Celery optimization (if Celery is configured)
    try:
        from app.core.celery_optimizer import init_celery_optimization
        from celery_app import celery
        
        if celery:
            init_celery_optimization(celery)
            logger.info("✅ Celery optimization initialized")
    except ImportError:
        logger.warning("⚠️ Celery not configured, skipping Celery optimization")
    except Exception as e:
        logger.error(f"❌ Celery optimization initialization failed: {e}")
    
    # 7. Setup performance monitoring hooks
    try:
        _setup_performance_hooks(app)
        logger.info("✅ Performance monitoring hooks configured")
    except Exception as e:
        logger.error(f"❌ Performance hooks setup failed: {e}")
    
    # 8. Run initial optimizations
    try:
        _run_initial_optimizations(app)
        logger.info("✅ Initial performance optimizations completed")
    except Exception as e:
        logger.error(f"❌ Initial optimizations failed: {e}")
    
    logger.info("🎉 Performance optimization initialization completed!")


def _setup_performance_hooks(app: Flask):
    """Setup application-level performance monitoring hooks"""
    
    # Note: before_first_request is deprecated in Flask 2.3+
    # We'll initialize during app creation instead
    
    @app.teardown_appcontext
    def teardown_db(error):
        """Database cleanup on request teardown"""
        if error:
            logger.error(f"Request error: {error}")
            # Force rollback on error
            from app.extensions import db
            db.session.rollback()
    
    @app.teardown_request
    def teardown_request(error):
        """Request cleanup"""
        if error:
            logger.error(f"Request teardown error: {error}")


def _run_initial_optimizations(app: Flask):
    """Run initial performance optimizations"""
    
    with app.app_context():
        # 1. Create/update database indexes
        try:
            logger.info("Creating performance indexes...")
            result = db_performance_optimizer.create_performance_indexes()
            logger.info(f"Index optimization result: {result}")
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
        
        # 2. Update table statistics
        try:
            logger.info("Updating table statistics...")
            db_performance_optimizer.optimize_table_statistics()
        except Exception as e:
            logger.error(f"Table statistics update failed: {e}")
        
        # 3. Initialize object pools
        try:
            from app.core.memory_optimizer import memory_optimizer
            logger.info("Initializing object pools...")
            # Pools are automatically initialized in memory_optimizer
        except Exception as e:
            logger.error(f"Object pool initialization failed: {e}")


def _warm_critical_caches():
    """Warm up critical application caches"""
    
    from app.core.query_cache import query_cache_manager
    
    # Define critical queries to warm up
    warm_queries = [
        {
            'query': lambda: _get_active_users_count(),
            'cache_key': 'stats:active_users_count',
            'ttl': 3600  # 1 hour
        },
        {
            'query': lambda: _get_beneficiaries_count(),
            'cache_key': 'stats:beneficiaries_count',
            'ttl': 3600  # 1 hour
        },
        {
            'query': lambda: _get_system_status(),
            'cache_key': 'system:status',
            'ttl': 300   # 5 minutes
        }
    ]
    
    try:
        query_cache_manager.warm_cache(warm_queries)
        logger.info("Critical caches warmed successfully")
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")


def _get_active_users_count():
    """Get count of active users for cache warming"""
    try:
        from app.models import User
        from app.extensions import db
        
        count = db.session.query(User).filter(User.is_active == True).count()
        return {'count': count, 'timestamp': '2024-01-01T00:00:00Z'}  # Placeholder
    except Exception:
        return {'count': 0, 'timestamp': '2024-01-01T00:00:00Z'}


def _get_beneficiaries_count():
    """Get count of beneficiaries for cache warming"""
    try:
        from app.models import Beneficiary
        from app.extensions import db
        
        count = db.session.query(Beneficiary).filter(Beneficiary.is_active == True).count()
        return {'count': count, 'timestamp': '2024-01-01T00:00:00Z'}  # Placeholder
    except Exception:
        return {'count': 0, 'timestamp': '2024-01-01T00:00:00Z'}


def _get_system_status():
    """Get system status for cache warming"""
    try:
        import psutil
        
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'status': 'healthy',
            'timestamp': '2024-01-01T00:00:00Z'  # Placeholder
        }
    except Exception:
        return {
            'status': 'unknown',
            'timestamp': '2024-01-01T00:00:00Z'
        }


def check_performance_health():
    """Check the health of all performance optimization components"""
    
    health_report = {
        'overall_status': 'healthy',
        'components': {}
    }
    
    # Check database performance
    try:
        db_stats = db_performance_optimizer.get_database_statistics()
        health_report['components']['database'] = {
            'status': 'healthy',
            'metrics': db_stats
        }
    except Exception as e:
        health_report['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_report['overall_status'] = 'degraded'
    
    # Check cache performance
    try:
        from app.core.query_cache import query_cache_manager
        cache_stats = query_cache_manager.get_cache_statistics()
        health_report['components']['cache'] = {
            'status': 'healthy',
            'metrics': cache_stats
        }
    except Exception as e:
        health_report['components']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_report['overall_status'] = 'degraded'
    
    # Check memory optimization
    try:
        from app.core.memory_optimizer import memory_optimizer
        memory_report = memory_optimizer.get_memory_report()
        
        # Check if memory usage is too high
        memory_percent = memory_report.get('memory_usage', {}).get('percent', 0)
        memory_status = 'healthy'
        if memory_percent > 90:
            memory_status = 'critical'
            health_report['overall_status'] = 'critical'
        elif memory_percent > 80:
            memory_status = 'warning'
            if health_report['overall_status'] == 'healthy':
                health_report['overall_status'] = 'degraded'
        
        health_report['components']['memory'] = {
            'status': memory_status,
            'metrics': memory_report
        }
    except Exception as e:
        health_report['components']['memory'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_report['overall_status'] = 'degraded'
    
    return health_report


def generate_performance_report():
    """Generate a comprehensive performance report"""
    
    try:
        # Collect all performance data
        report = {
            'timestamp': '2024-01-01T00:00:00Z',  # Will be replaced with actual timestamp
            'health_check': check_performance_health(),
            'database_performance': {},
            'cache_performance': {},
            'memory_usage': {},
            'api_performance': {},
            'recommendations': []
        }
        
        # Database performance
        try:
            report['database_performance'] = db_performance_optimizer.get_database_statistics()
        except Exception as e:
            report['database_performance'] = {'error': str(e)}
        
        # Cache performance
        try:
            from app.core.query_cache import query_cache_manager
            report['cache_performance'] = query_cache_manager.get_cache_statistics()
        except Exception as e:
            report['cache_performance'] = {'error': str(e)}
        
        # Memory usage
        try:
            from app.core.memory_optimizer import memory_optimizer
            report['memory_usage'] = memory_optimizer.get_memory_report()
        except Exception as e:
            report['memory_usage'] = {'error': str(e)}
        
        # API performance
        try:
            from app.middleware.performance_middleware import performance_monitoring_middleware
            report['api_performance'] = performance_monitoring_middleware.get_metrics()
        except Exception as e:
            report['api_performance'] = {'error': str(e)}
        
        # Generate recommendations
        report['recommendations'] = _generate_recommendations(report)
        
        return report
        
    except Exception as e:
        logger.error(f"Performance report generation failed: {e}")
        return {'error': str(e)}


def _generate_recommendations(report):
    """Generate performance optimization recommendations"""
    
    recommendations = []
    
    try:
        # Database recommendations
        db_stats = report.get('database_performance', {})
        if isinstance(db_stats, dict) and 'performance_stats' in db_stats:
            avg_query_time = db_stats['performance_stats'].get('average_query_time', 0)
            if avg_query_time > 1.0:  # More than 1 second average
                recommendations.append({
                    'category': 'database',
                    'priority': 'high',
                    'recommendation': 'Average query time is high, consider optimizing slow queries and adding indexes'
                })
        
        # Cache recommendations
        cache_stats = report.get('cache_performance', {})
        if isinstance(cache_stats, dict) and 'hit_rate_percentage' in cache_stats:
            hit_rate = cache_stats['hit_rate_percentage']
            if hit_rate < 70:
                recommendations.append({
                    'category': 'cache',
                    'priority': 'medium',
                    'recommendation': f'Cache hit rate is low ({hit_rate:.1f}%), consider increasing cache TTL or warming more data'
                })
        
        # Memory recommendations
        memory_stats = report.get('memory_usage', {})
        if isinstance(memory_stats, dict) and 'memory_usage' in memory_stats:
            memory_percent = memory_stats['memory_usage'].get('percent', 0)
            if memory_percent > 85:
                recommendations.append({
                    'category': 'memory',
                    'priority': 'high',
                    'recommendation': f'Memory usage is high ({memory_percent:.1f}%), consider scaling up or optimizing memory usage'
                })
        
        # API recommendations
        api_stats = report.get('api_performance', {})
        if isinstance(api_stats, dict) and 'slow_request_rate_percentage' in api_stats:
            slow_rate = api_stats['slow_request_rate_percentage']
            if slow_rate > 5:
                recommendations.append({
                    'category': 'api',
                    'priority': 'medium',
                    'recommendation': f'High slow request rate ({slow_rate:.1f}%), consider optimizing slow endpoints'
                })
    
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        recommendations.append({
            'category': 'system',
            'priority': 'low',
            'recommendation': 'Unable to analyze performance metrics for recommendations'
        })
    
    return recommendations