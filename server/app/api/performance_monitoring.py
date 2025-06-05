"""
Performance Monitoring API Endpoints
Provides comprehensive performance monitoring, metrics collection, and alerting.
"""

import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.core.database_performance import db_performance_optimizer
from app.core.query_cache import query_cache_manager
from app.core.memory_optimizer import memory_optimizer
from app.core.celery_optimizer import celery_optimizer
from app.middleware.performance_middleware import performance_monitoring_middleware
from app.services.optimization.db_indexing import db_indexing_strategy
from app.utils.logging import logger

# Create blueprint
performance_bp = Blueprint('performance', __name__, url_prefix='/api/performance')


@performance_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def performance_dashboard():
    """Get comprehensive performance dashboard data"""
    try:
        # Collect all performance metrics
        dashboard_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_overview': _get_system_overview(),
            'database_performance': _get_database_performance(),
            'cache_performance': _get_cache_performance(),
            'memory_usage': _get_memory_usage(),
            'api_performance': _get_api_performance(),
            'celery_performance': _get_celery_performance(),
            'alerts': _get_performance_alerts()
        }
        
        return jsonify({
            'status': 'success',
            'data': dashboard_data
        })
    
    except Exception as e:
        logger.error(f"Performance dashboard error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/system', methods=['GET'])
@jwt_required()
def system_metrics():
    """Get system-level performance metrics"""
    try:
        system_data = _get_system_overview()
        return jsonify({
            'status': 'success',
            'data': system_data
        })
    
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/database', methods=['GET'])
@jwt_required()
def database_metrics():
    """Get database performance metrics"""
    try:
        db_data = _get_database_performance()
        return jsonify({
            'status': 'success',
            'data': db_data
        })
    
    except Exception as e:
        logger.error(f"Database metrics error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/database/slow-queries', methods=['GET'])
@jwt_required()
def slow_queries():
    """Get slow query analysis"""
    try:
        slow_queries_data = {
            'slow_queries': db_performance_optimizer.slow_queries,
            'slow_query_threshold': db_performance_optimizer.slow_query_threshold,
            'total_slow_queries': db_performance_optimizer.performance_stats['slow_queries']
        }
        
        return jsonify({
            'status': 'success',
            'data': slow_queries_data
        })
    
    except Exception as e:
        logger.error(f"Slow queries error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/database/analyze-query', methods=['POST'])
@jwt_required()
def analyze_query():
    """Analyze a specific query for performance"""
    try:
        data = request.get_json()
        query_sql = data.get('query')
        
        if not query_sql:
            return jsonify({
                'status': 'error',
                'message': 'Query SQL is required'
            }), 400
        
        analysis = db_performance_optimizer.analyze_query_performance(query_sql)
        
        return jsonify({
            'status': 'success',
            'data': analysis
        })
    
    except Exception as e:
        logger.error(f"Query analysis error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/cache', methods=['GET'])
@jwt_required()
def cache_metrics():
    """Get cache performance metrics"""
    try:
        cache_data = _get_cache_performance()
        return jsonify({
            'status': 'success',
            'data': cache_data
        })
    
    except Exception as e:
        logger.error(f"Cache metrics error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
def clear_cache():
    """Clear application cache"""
    try:
        # Clear query cache
        query_cache_manager.clear_cache()
        
        # Clear database performance cache
        db_performance_optimizer.clear_query_cache()
        
        return jsonify({
            'status': 'success',
            'message': 'Cache cleared successfully'
        })
    
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/memory', methods=['GET'])
@jwt_required()
def memory_metrics():
    """Get memory usage metrics"""
    try:
        memory_data = _get_memory_usage()
        return jsonify({
            'status': 'success',
            'data': memory_data
        })
    
    except Exception as e:
        logger.error(f"Memory metrics error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/memory/optimize', methods=['POST'])
@jwt_required()
def optimize_memory():
    """Trigger memory optimization"""
    try:
        optimization_result = memory_optimizer.optimize_memory()
        return jsonify({
            'status': 'success',
            'data': optimization_result
        })
    
    except Exception as e:
        logger.error(f"Memory optimization error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/api', methods=['GET'])
@jwt_required()
def api_metrics():
    """Get API performance metrics"""
    try:
        api_data = _get_api_performance()
        return jsonify({
            'status': 'success',
            'data': api_data
        })
    
    except Exception as e:
        logger.error(f"API metrics error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/celery', methods=['GET'])
@jwt_required()
def celery_metrics():
    """Get Celery task performance metrics"""
    try:
        celery_data = _get_celery_performance()
        return jsonify({
            'status': 'success',
            'data': celery_data
        })
    
    except Exception as e:
        logger.error(f"Celery metrics error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/indexes/optimize', methods=['POST'])
@jwt_required()
def optimize_indexes():
    """Optimize database indexes"""
    try:
        optimization_result = db_performance_optimizer.create_performance_indexes()
        return jsonify({
            'status': 'success',
            'data': optimization_result
        })
    
    except Exception as e:
        logger.error(f"Index optimization error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/alerts', methods=['GET'])
@jwt_required()
def performance_alerts():
    """Get performance alerts"""
    try:
        alerts = _get_performance_alerts()
        return jsonify({
            'status': 'success',
            'data': {'alerts': alerts}
        })
    
    except Exception as e:
        logger.error(f"Performance alerts error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@performance_bp.route('/health-check', methods=['GET'])
def health_check():
    """Comprehensive system health check"""
    try:
        health_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'checks': []
        }
        
        # Database health
        try:
            from app.extensions import db
            db.session.execute('SELECT 1')
            health_data['checks'].append({
                'component': 'database',
                'status': 'healthy',
                'message': 'Database connection successful'
            })
        except Exception as e:
            health_data['status'] = 'unhealthy'
            health_data['checks'].append({
                'component': 'database',
                'status': 'unhealthy',
                'message': f'Database connection failed: {e}'
            })
        
        # Cache health
        try:
            if query_cache_manager.redis_client:
                query_cache_manager.redis_client.ping()
                health_data['checks'].append({
                    'component': 'cache',
                    'status': 'healthy',
                    'message': 'Cache connection successful'
                })
            else:
                health_data['checks'].append({
                    'component': 'cache',
                    'status': 'warning',
                    'message': 'Cache not configured'
                })
        except Exception as e:
            health_data['checks'].append({
                'component': 'cache',
                'status': 'unhealthy',
                'message': f'Cache connection failed: {e}'
            })
        
        # Memory health
        memory_usage = memory_optimizer.monitor.get_memory_usage()
        memory_percent = memory_usage.get('percent', 0)
        
        if memory_percent > 90:
            health_data['status'] = 'unhealthy'
            health_data['checks'].append({
                'component': 'memory',
                'status': 'critical',
                'message': f'Memory usage critical: {memory_percent:.1f}%'
            })
        elif memory_percent > 80:
            health_data['checks'].append({
                'component': 'memory',
                'status': 'warning',
                'message': f'Memory usage high: {memory_percent:.1f}%'
            })
        else:
            health_data['checks'].append({
                'component': 'memory',
                'status': 'healthy',
                'message': f'Memory usage normal: {memory_percent:.1f}%'
            })
        
        return jsonify(health_data), 200 if health_data['status'] == 'healthy' else 503
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Helper functions
def _get_system_overview() -> Dict[str, Any]:
    """Get system-level metrics"""
    try:
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network I/O
        network = psutil.net_io_counters()
        
        # Load average (Unix systems)
        try:
            load_avg = psutil.getloadavg()
        except AttributeError:
            load_avg = [0, 0, 0]  # Windows doesn't have load average
        
        return {
            'cpu_percent': cpu_percent,
            'memory': {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': disk.total / (1024**3),
                'free_gb': disk.free / (1024**3),
                'used_gb': disk.used / (1024**3),
                'percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'load_average': {
                '1min': load_avg[0],
                '5min': load_avg[1],
                '15min': load_avg[2]
            }
        }
    
    except Exception as e:
        logger.error(f"System overview error: {e}")
        return {}


def _get_database_performance() -> Dict[str, Any]:
    """Get database performance metrics"""
    try:
        db_stats = db_performance_optimizer.get_database_statistics()
        return {
            'connection_pool': db_stats.get('connection_pool_info', {}),
            'query_stats': db_stats.get('performance_stats', {}),
            'slow_queries_count': len(db_performance_optimizer.slow_queries),
            'cache_hit_rate': db_stats.get('cache_hit_rate', 0)
        }
    
    except Exception as e:
        logger.error(f"Database performance error: {e}")
        return {}


def _get_cache_performance() -> Dict[str, Any]:
    """Get cache performance metrics"""
    try:
        cache_stats = query_cache_manager.get_cache_statistics()
        return cache_stats
    
    except Exception as e:
        logger.error(f"Cache performance error: {e}")
        return {}


def _get_memory_usage() -> Dict[str, Any]:
    """Get memory usage metrics"""
    try:
        memory_report = memory_optimizer.get_memory_report()
        return memory_report
    
    except Exception as e:
        logger.error(f"Memory usage error: {e}")
        return {}


def _get_api_performance() -> Dict[str, Any]:
    """Get API performance metrics"""
    try:
        api_stats = performance_monitoring_middleware.get_metrics()
        return api_stats
    
    except Exception as e:
        logger.error(f"API performance error: {e}")
        return {}


def _get_celery_performance() -> Dict[str, Any]:
    """Get Celery performance metrics"""
    try:
        celery_stats = celery_optimizer.get_optimization_stats()
        return celery_stats
    
    except Exception as e:
        logger.error(f"Celery performance error: {e}")
        return {}


def _get_performance_alerts() -> List[Dict[str, Any]]:
    """Generate performance alerts based on metrics"""
    alerts = []
    
    try:
        # Memory alerts
        memory_usage = memory_optimizer.monitor.get_memory_usage()
        memory_percent = memory_usage.get('percent', 0)
        
        if memory_percent > 90:
            alerts.append({
                'severity': 'critical',
                'component': 'memory',
                'message': f'Memory usage critical: {memory_percent:.1f}%',
                'timestamp': datetime.utcnow().isoformat(),
                'value': memory_percent,
                'threshold': 90
            })
        elif memory_percent > 80:
            alerts.append({
                'severity': 'warning',
                'component': 'memory',
                'message': f'Memory usage high: {memory_percent:.1f}%',
                'timestamp': datetime.utcnow().isoformat(),
                'value': memory_percent,
                'threshold': 80
            })
        
        # CPU alerts
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            alerts.append({
                'severity': 'critical',
                'component': 'cpu',
                'message': f'CPU usage critical: {cpu_percent:.1f}%',
                'timestamp': datetime.utcnow().isoformat(),
                'value': cpu_percent,
                'threshold': 90
            })
        elif cpu_percent > 80:
            alerts.append({
                'severity': 'warning',
                'component': 'cpu',
                'message': f'CPU usage high: {cpu_percent:.1f}%',
                'timestamp': datetime.utcnow().isoformat(),
                'value': cpu_percent,
                'threshold': 80
            })
        
        # Slow query alerts
        slow_query_count = len(db_performance_optimizer.slow_queries)
        if slow_query_count > 10:
            alerts.append({
                'severity': 'warning',
                'component': 'database',
                'message': f'High number of slow queries: {slow_query_count}',
                'timestamp': datetime.utcnow().isoformat(),
                'value': slow_query_count,
                'threshold': 10
            })
        
        # Cache hit rate alerts
        cache_stats = query_cache_manager.get_cache_statistics()
        hit_rate = cache_stats.get('hit_rate_percentage', 0)
        if hit_rate < 50:
            alerts.append({
                'severity': 'warning',
                'component': 'cache',
                'message': f'Low cache hit rate: {hit_rate:.1f}%',
                'timestamp': datetime.utcnow().isoformat(),
                'value': hit_rate,
                'threshold': 50
            })
        
        # API performance alerts
        api_stats = performance_monitoring_middleware.get_metrics()
        slow_request_rate = api_stats.get('slow_request_rate_percentage', 0)
        if slow_request_rate > 10:
            alerts.append({
                'severity': 'warning',
                'component': 'api',
                'message': f'High slow request rate: {slow_request_rate:.1f}%',
                'timestamp': datetime.utcnow().isoformat(),
                'value': slow_request_rate,
                'threshold': 10
            })
    
    except Exception as e:
        logger.error(f"Performance alerts error: {e}")
    
    return alerts


# Register blueprint
def register_performance_monitoring(app):
    """Register performance monitoring blueprint"""
    app.register_bluelogger.info(performance_bp)
    logger.info("Performance monitoring API registered")