"""
Enhanced Flask Application Factory with Performance Optimization
Integrates all performance optimization components into the BDC application.
"""

import os
from flask import Flask
from flask_cors import CORS

# Import all extensions
from app.extensions import db, jwt, mail, migrate, limiter, cache, socketio

# Import performance optimization components
from app.core.performance_init import init_performance_optimization
from app.core.session_cache import init_session_caching
from app.core.cdn_config import init_cdn_configuration

# Import API blueprints
from app.api.auth import auth_bp
from app.api.beneficiaries_dashboard import beneficiaries_bp
from app.api.appointments import appointments_bp
from app.api.evaluations import evaluations_bp
from app.api.documents import documents_bp
from app.api.notifications import notifications_bp
from app.api.performance_monitoring import performance_bp
from app.api.ai_question_generation import ai_question_generation_bp
from app.api.i18n import i18n_bp
from app.api.gamification import gamification_bp
from app.api.security import security_bp

# Import i18n middleware
from app.middleware.i18n_middleware import (
    i18n_middleware, content_localization_middleware, rtl_support_middleware
)

from app.utils.logging import logger


def create_app(config_name='default'):
    """
    Enhanced application factory with comprehensive performance optimization.
    
    Args:
        config_name: Configuration environment ('development', 'testing', 'production')
    
    Returns:
        Flask application instance with all optimizations enabled
    """
    
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:5173']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Initialize SocketIO
    socketio.init_app(app, 
                     cors_allowed_origins=app.config.get('CORS_ORIGINS', ['http://localhost:5173']),
                     async_mode='threading')
    
    # Initialize i18n middleware
    try:
        logger.info("🌐 Initializing internationalization middleware...")
        i18n_middleware.init_app(app)
        content_localization_middleware.init_app(app)
        rtl_support_middleware.init_app(app)
        logger.info("✅ I18n middleware initialization completed successfully!")
    except Exception as e:
        logger.error(f"❌ I18n middleware initialization failed: {e}")
    
    # Initialize security middleware
    try:
        logger.info("🔒 Initializing enhanced security features...")
        
        # 1. Initialize threat detection middleware
        from app.middleware.threat_detection_middleware import threat_detection_middleware
        threat_detection_middleware.init_app(app)
        
        # 2. Apply IP whitelist middleware if enabled
        if app.config.get('ENABLE_IP_WHITELIST', False):
            from app.middleware.ip_whitelist import IPWhitelistMiddleware
            app.wsgi_app = IPWhitelistMiddleware(app.wsgi_app)
            logger.info("✅ IP whitelist middleware enabled")
        
        logger.info("✅ Enhanced security features initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Security middleware initialization failed: {e}")
    
    # CRITICAL: Initialize Performance Optimization
    try:
        logger.info("🚀 Initializing comprehensive performance optimization...")
        
        # 1. Core performance optimization
        init_performance_optimization(app)
        
        # 2. Session caching with Redis
        init_session_caching(app)
        
        # 3. CDN configuration for static assets
        init_cdn_configuration(app)
        
        logger.info("✅ Performance optimization initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Performance optimization initialization failed: {e}")
        # Continue without performance optimizations in case of failure
    
    # Register API blueprints
    api_blueprints = [
        (auth_bp, '/api/auth'),
        (beneficiaries_bp, '/api/beneficiaries'),
        (appointments_bp, '/api/appointments'),
        (evaluations_bp, '/api/evaluations'),
        (documents_bp, '/api/documents'),
        (notifications_bp, '/api/notifications'),
        (performance_bp, '/api/performance'),  # Performance monitoring API
        (ai_question_generation_bp, None),  # AI Question Generation API (has its own prefix)
        (i18n_bp, None),  # I18n API (has its own prefix)
        (gamification_bp, None),  # Gamification API (has its own prefix)
        (security_bp, None)  # Security API (has its own prefix)
    ]
    
    for blueprint, url_prefix in api_blueprints:
        try:
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            logger.info(f"✅ Registered blueprint: {blueprint.name}")
        except Exception as e:
            logger.error(f"❌ Failed to register blueprint {blueprint.name}: {e}")
    
    # Application hooks for performance monitoring
    @app.before_first_request
    def initialize_performance_monitoring():
        """Initialize performance monitoring on first request"""
        logger.info("🔍 Starting performance monitoring...")
        
        # Set memory baseline
        try:
            from app.core.memory_optimizer import memory_optimizer
            memory_optimizer.monitor.set_memory_baseline()
            logger.info("✅ Memory baseline established")
        except Exception as e:
            logger.error(f"❌ Memory baseline setup failed: {e}")
        
        # Run initial database optimizations
        try:
            from app.core.database_performance import db_performance_optimizer
            with app.app_context():
                result = db_performance_optimizer.create_performance_indexes()
                logger.info(f"✅ Database indexes optimized: {result}")
        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
    
    @app.before_request
    def before_request():
        """Performance tracking for each request"""
        import time
        from flask import g
        
        g.request_start_time = time.time()
        g.request_id = os.urandom(16).hex()
    
    @app.after_request
    def after_request(response):
        """Performance logging after each request"""
        import time
        from flask import g, request
        
        if hasattr(g, 'request_start_time'):
            request_time = time.time() - g.request_start_time
            
            # Log slow requests
            if request_time > 2.0:  # Requests slower than 2 seconds
                logger.warning(f"Slow request detected: {request.endpoint} "
                             f"({request_time:.3f}s) - {request.method} {request.path}")
        
        # Add performance headers
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        response.headers['X-Response-Time'] = f"{getattr(g, 'request_start_time', 0):.3f}s"
        
        return response
    
    @app.teardown_appcontext
    def cleanup_db(error):
        """Database cleanup on request teardown"""
        if error:
            logger.error(f"Request error during teardown: {error}")
            db.session.rollback()
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Basic health check endpoint"""
        return {
            'status': 'healthy',
            'timestamp': '2024-01-01T00:00:00Z',
            'version': app.config.get('APP_VERSION', '1.0.0'),
            'performance_optimization': 'enabled'
        }
    
    # Performance dashboard endpoint
    @app.route('/performance')
    def performance_dashboard():
        """Redirect to performance monitoring dashboard"""
        from flask import redirect, url_for
        return redirect(url_for('performance.performance_dashboard'))
    
    # Error handlers with performance considerations
    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"404 error: {error}")
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        db.session.rollback()
        
        # Check if this is a performance-related error
        try:
            from app.core.memory_optimizer import memory_optimizer
            memory_usage = memory_optimizer.monitor.get_memory_usage()
            
            if memory_usage.get('percent', 0) > 90:
                logger.critical(f"High memory usage detected during error: {memory_usage}")
                # Force garbage collection
                memory_optimizer.monitor.force_garbage_collection()
        except Exception:
            pass
        
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(429)
    def rate_limit_handler(error):
        logger.warning(f"Rate limit exceeded: {error}")
        return {
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }, 429
    
    # CLI commands for performance management
    @app.cli.command('optimize-db')
    def optimize_database():
        """CLI command to optimize database performance"""
        logger.info("🔧 Running database optimization...")
        
        try:
            from app.core.database_performance import db_performance_optimizer
            
            with app.app_context():
                # Create/update indexes
                result = db_performance_optimizer.create_performance_indexes()
                logger.info(f"✅ Database optimization completed: {result}")
                
                # Update table statistics
                db_performance_optimizer.optimize_table_statistics()
                logger.info("✅ Table statistics updated")
                
        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
    
    @app.cli.command('clear-cache')
    def clear_cache():
        """CLI command to clear all caches"""
        logger.info("🧹 Clearing all caches...")
        
        try:
            from app.core.query_cache import query_cache_manager
            from app.core.database_performance import db_performance_optimizer
            
            # Clear query cache
            query_cache_manager.clear_cache()
            logger.info("✅ Query cache cleared")
            
            # Clear database performance cache
            db_performance_optimizer.clear_query_cache()
            logger.info("✅ Database cache cleared")
            
            # Clear Flask cache
            cache.clear()
            logger.info("✅ Flask cache cleared")
            
        except Exception as e:
            logger.error(f"❌ Cache clearing failed: {e}")
    
    @app.cli.command('performance-report')
    def performance_report():
        """CLI command to generate performance report"""
        logger.info("📊 Generating performance report...")
        
        try:
            from app.core.performance_init import generate_performance_report
            
            with app.app_context():
                report = generate_performance_report()
                
                logger.info("\n" + "="*80)
                logger.info("PERFORMANCE OPTIMIZATION REPORT")
                logger.info("="*80)
                
                # System health
                health = report.get('health_check', {})
                logger.info(f"\n🏥 SYSTEM HEALTH: {health.get('overall_status', 'unknown').upper()}")
                
                # Database performance
                db_perf = report.get('database_performance', {})
                if 'performance_stats' in db_perf:
                    stats = db_perf['performance_stats']
                    logger.info(f"\n📊 DATABASE PERFORMANCE:")
                    logger.info(f"   - Total queries: {stats.get('total_queries', 0)}")
                    logger.info(f"   - Average query time: {stats.get('average_query_time', 0):.3f}s")
                    logger.info(f"   - Slow queries: {stats.get('slow_queries', 0)}")
                
                # Cache performance
                cache_perf = report.get('cache_performance', {})
                if 'hit_rate_percentage' in cache_perf:
                    logger.info(f"\n🎯 CACHE PERFORMANCE:")
                    logger.info(f"   - Hit rate: {cache_perf['hit_rate_percentage']:.1f}%")
                    logger.info(f"   - Total requests: {cache_perf.get('total_requests', 0)}")
                
                # Memory usage
                memory = report.get('memory_usage', {})
                if 'memory_usage' in memory:
                    mem_info = memory['memory_usage']
                    logger.info(f"\n💾 MEMORY USAGE:")
                    logger.info(f"   - Current: {mem_info.get('rss_mb', 0):.1f} MB")
                    logger.info(f"   - Peak: {mem_info.get('peak_rss_mb', 0):.1f} MB")
                    logger.info(f"   - Percentage: {mem_info.get('percent', 0):.1f}%")
                
                # Recommendations
                recommendations = report.get('recommendations', [])
                if recommendations:
                    logger.info(f"\n💡 RECOMMENDATIONS:")
                    for rec in recommendations[:5]:  # Top 5 recommendations
                        priority = rec.get('priority', 'unknown').upper()
                        category = rec.get('category', 'unknown').upper()
                        description = rec.get('recommendation', 'No description')
                        logger.info(f"   - [{priority}] {category}: {description}")
                
                logger.info("\n" + "="*80)
                logger.info("✅ Performance report generated successfully")
                
        except Exception as e:
            logger.error(f"❌ Performance report generation failed: {e}")
    
    # Final initialization log
    logger.info(f"🎉 BDC Application created successfully with comprehensive performance optimization!")
    logger.info(f"📈 Performance monitoring available at: /api/performance/dashboard")
    logger.info(f"🏥 Health check available at: /health")
    
    return app


# Export the application factory
__all__ = ['create_app']