"""
Health Check API Endpoints
Provides comprehensive health monitoring and system status endpoints.
"""

from flask import Blueprint, jsonify, request, current_app
from app.services.health_monitor import health_monitor
from app.core.auth import requires_permission
from flask_jwt_extended import jwt_required
import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api/v2/health')

@health_bp.route('/', methods=['GET'])
def basic_health():
    """
    Basic health check endpoint
    Returns minimal health status for load balancers and monitoring systems
    """
    try:
        health_data = health_monitor.get_basic_health()
        
        # Return appropriate HTTP status code
        status_code = 200 if health_data['status'] == 'healthy' else 503
        
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Basic health check failed: {str(e)}")
        return jsonify({
            'status': 'critical',
            'error': 'Health check failed',
            'message': str(e)
        }), 503

@health_bp.route('/detailed', methods=['GET'])
@jwt_required()
@requires_permission('system.health.view')
def detailed_health():
    """
    Detailed health check endpoint with comprehensive metrics
    Requires authentication and appropriate permissions
    """
    try:
        health_data = health_monitor.get_detailed_health()
        
        # Return appropriate HTTP status code
        status_code = 200 if health_data['status'] in ['healthy', 'warning'] else 503
        
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            'status': 'critical',
            'error': 'Detailed health check failed',
            'message': str(e)
        }), 503

@health_bp.route('/metrics', methods=['GET'])
@jwt_required()
@requires_permission('system.metrics.view')
def health_metrics():
    """
    Get health metrics history and current system metrics
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        
        # Get historical data
        history = health_monitor.get_health_history(hours)
        
        # Get current detailed health
        current_health = health_monitor.get_detailed_health()
        
        return jsonify({
            'current': current_health,
            'history': history,
            'thresholds': health_monitor.get_alert_thresholds(),
            'timeframe_hours': hours
        })
        
    except Exception as e:
        logger.error(f"Health metrics retrieval failed: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve health metrics',
            'message': str(e)
        }), 500

@health_bp.route('/alerts', methods=['GET'])
@jwt_required()
@requires_permission('system.alerts.view')
def get_alerts():
    """
    Get current active alerts and alert configuration
    """
    try:
        health_data = health_monitor.get_detailed_health()
        alerts = health_data.get('alerts', [])
        
        return jsonify({
            'active_alerts': alerts,
            'alert_count': len(alerts),
            'thresholds': health_monitor.get_alert_thresholds(),
            'timestamp': health_data['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Alert retrieval failed: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve alerts',
            'message': str(e)
        }), 500

@health_bp.route('/alerts/thresholds', methods=['PUT'])
@jwt_required()
@requires_permission('system.alerts.configure')
def update_alert_thresholds():
    """
    Update alert thresholds for system metrics
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        updated_thresholds = {}
        for metric, threshold in data.items():
            if isinstance(threshold, (int, float)) and threshold > 0:
                health_monitor.set_alert_threshold(metric, float(threshold))
                updated_thresholds[metric] = float(threshold)
            else:
                return jsonify({
                    'error': f'Invalid threshold value for {metric}. Must be a positive number.'
                }), 400
        
        return jsonify({
            'message': 'Alert thresholds updated successfully',
            'updated_thresholds': updated_thresholds,
            'all_thresholds': health_monitor.get_alert_thresholds()
        })
        
    except Exception as e:
        logger.error(f"Alert threshold update failed: {str(e)}")
        return jsonify({
            'error': 'Failed to update alert thresholds',
            'message': str(e)
        }), 500

@health_bp.route('/services', methods=['GET'])
@jwt_required()
@requires_permission('system.services.view')
def service_status():
    """
    Get detailed status of all monitored services
    """
    try:
        health_data = health_monitor.get_detailed_health()
        services = health_data.get('services', {})
        
        # Calculate service statistics
        total_services = len(services)
        healthy_services = sum(1 for s in services.values() if s.get('status') == 'healthy')
        warning_services = sum(1 for s in services.values() if s.get('status') == 'warning')
        critical_services = sum(1 for s in services.values() if s.get('status') == 'critical')
        
        return jsonify({
            'services': services,
            'summary': {
                'total': total_services,
                'healthy': healthy_services,
                'warning': warning_services,
                'critical': critical_services,
                'health_percentage': round((healthy_services / total_services) * 100, 1) if total_services > 0 else 0
            },
            'timestamp': health_data['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Service status retrieval failed: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve service status',
            'message': str(e)
        }), 500

@health_bp.route('/system', methods=['GET'])
@jwt_required()
@requires_permission('system.metrics.view')
def system_metrics():
    """
    Get detailed system metrics (CPU, memory, disk, network)
    """
    try:
        health_data = health_monitor.get_detailed_health()
        system_data = health_data.get('system', {})
        
        return jsonify({
            'system_metrics': system_data,
            'timestamp': health_data['timestamp'],
            'overall_status': health_data['status']
        })
        
    except Exception as e:
        logger.error(f"System metrics retrieval failed: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve system metrics',
            'message': str(e)
        }), 500

@health_bp.route('/performance', methods=['GET'])
@jwt_required()
@requires_permission('system.performance.view')
def performance_metrics():
    """
    Get application performance metrics
    """
    try:
        health_data = health_monitor.get_detailed_health()
        performance_data = health_data.get('performance', {})
        application_data = health_data.get('application', {})
        
        return jsonify({
            'performance_metrics': performance_data,
            'application_metrics': application_data,
            'timestamp': health_data['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Performance metrics retrieval failed: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve performance metrics',
            'message': str(e)
        }), 500

@health_bp.route('/environment', methods=['GET'])
@jwt_required()
@requires_permission('system.info.view')
def environment_info():
    """
    Get environment and system information
    """
    try:
        health_data = health_monitor.get_detailed_health()
        environment_data = health_data.get('environment', {})
        
        return jsonify({
            'environment': environment_data,
            'timestamp': health_data['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Environment info retrieval failed: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve environment information',
            'message': str(e)
        }), 500

@health_bp.route('/readiness', methods=['GET'])
def readiness_check():
    """
    Kubernetes/Docker readiness probe endpoint
    Checks if the application is ready to serve traffic
    """
    try:
        # Check critical dependencies
        db_status = health_monitor._check_database()
        redis_status = health_monitor._check_redis()
        
        if db_status.get('healthy') and redis_status.get('healthy'):
            return jsonify({
                'status': 'ready',
                'timestamp': health_monitor.get_basic_health()['timestamp']
            }), 200
        else:
            return jsonify({
                'status': 'not_ready',
                'database': db_status,
                'redis': redis_status
            }), 503
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'not_ready',
            'error': str(e)
        }), 503

@health_bp.route('/liveness', methods=['GET'])
def liveness_check():
    """
    Kubernetes/Docker liveness probe endpoint
    Simple check if the application is alive
    """
    try:
        return jsonify({
            'status': 'alive',
            'timestamp': health_monitor.get_basic_health()['timestamp']
        }), 200
        
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        return jsonify({
            'status': 'dead',
            'error': str(e)
        }), 503

# Error handlers
@health_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Insufficient permissions',
        'message': 'You do not have permission to access this health endpoint'
    }), 403

@health_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Authentication required',
        'message': 'Please authenticate to access health endpoints'
    }), 401