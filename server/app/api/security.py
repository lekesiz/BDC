"""Security management API endpoints."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db, redis_client
from app.security.threat_detection import ThreatDetectionEngine
from app.security.audit_logger import AuditLogger
from app.config.security import SecurityConfig
from app.utils.decorators import admin_required
from datetime import datetime, timedelta
import ipaddress

security_bp = Blueprint('security', __name__, url_prefix='/api/security')

# Initialize services
threat_detector = ThreatDetectionEngine(redis_client)
audit_logger = AuditLogger()


@security_bp.route('/threat-summary', methods=['GET'])
@jwt_required()
@admin_required
def get_threat_summary():
    """Get current threat summary and statistics."""
    try:
        # Get optional IP filter
        ip_filter = request.args.get('ip')
        
        # Get threat summary
        summary = threat_detector.get_threat_summary(ip_filter)
        
        # Add additional statistics
        if redis_client:
            # Get blacklisted IPs count
            blacklist_keys = redis_client.keys('blacklist:*')
            summary['blacklisted_ips_count'] = len(blacklist_keys)
            
            # Get recent failed logins
            failed_login_keys = redis_client.keys('failed_login:*')
            summary['active_failed_login_ips'] = len(failed_login_keys)
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting threat summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve threat summary'
        }), 500


@security_bp.route('/blacklist', methods=['GET'])
@jwt_required()
@admin_required
def get_blacklist():
    """Get current IP blacklist."""
    try:
        blacklist = []
        
        if redis_client:
            # Get all blacklisted IPs
            for key in redis_client.keys('blacklist:*'):
                ip = key.decode('utf-8').replace('blacklist:', '')
                ttl = redis_client.ttl(key)
                blacklist.append({
                    'ip': ip,
                    'expires_in': ttl,
                    'expires_at': (datetime.utcnow() + timedelta(seconds=ttl)).isoformat() if ttl > 0 else None
                })
        
        return jsonify({
            'success': True,
            'data': {
                'blacklist': blacklist,
                'total': len(blacklist)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting blacklist: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve blacklist'
        }), 500


@security_bp.route('/blacklist', methods=['POST'])
@jwt_required()
@admin_required
def add_to_blacklist():
    """Add IP to blacklist."""
    try:
        data = request.get_json()
        ip = data.get('ip')
        duration = data.get('duration', 3600)  # Default 1 hour
        reason = data.get('reason', 'Manual blacklist')
        
        # Validate IP
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid IP address'
            }), 400
        
        # Add to blacklist
        if redis_client:
            redis_client.setex(f"blacklist:{ip}", duration, 1)
        
        # Log the action
        audit_logger.log_security_event(
            event_type='manual_blacklist',
            severity='high',
            description=f'IP manually blacklisted: {reason}',
            source_ip=ip,
            user_id=get_jwt_identity(),
            details={'duration': duration, 'reason': reason}
        )
        
        return jsonify({
            'success': True,
            'message': f'IP {ip} added to blacklist for {duration} seconds'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error adding to blacklist: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to add IP to blacklist'
        }), 500


@security_bp.route('/blacklist/<ip>', methods=['DELETE'])
@jwt_required()
@admin_required
def remove_from_blacklist(ip):
    """Remove IP from blacklist."""
    try:
        # Remove from blacklist
        if redis_client:
            result = redis_client.delete(f"blacklist:{ip}")
        
        if result:
            # Log the action
            audit_logger.log_security_event(
                event_type='blacklist_removed',
                severity='medium',
                description=f'IP removed from blacklist',
                source_ip=ip,
                user_id=get_jwt_identity()
            )
            
            return jsonify({
                'success': True,
                'message': f'IP {ip} removed from blacklist'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'IP not found in blacklist'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error removing from blacklist: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to remove IP from blacklist'
        }), 500


@security_bp.route('/whitelist', methods=['GET'])
@jwt_required()
@admin_required
def get_whitelist():
    """Get current IP whitelist configuration."""
    try:
        config = SecurityConfig()
        
        return jsonify({
            'success': True,
            'data': {
                'enabled': config.ENABLE_IP_WHITELIST,
                'whitelist': config.IP_WHITELIST,
                'admin_whitelist': config.ADMIN_IP_WHITELIST
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting whitelist: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve whitelist'
        }), 500


@security_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@admin_required
def get_audit_logs():
    """Get security audit logs."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        severity = request.args.get('severity')
        event_type = request.args.get('event_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # This would typically query from a database
        # For now, return a sample response
        logs = []
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs,
                'page': page,
                'per_page': per_page,
                'total': len(logs)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting audit logs: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve audit logs'
        }), 500


@security_bp.route('/security-config', methods=['GET'])
@jwt_required()
@admin_required
def get_security_config():
    """Get current security configuration."""
    try:
        config = SecurityConfig.get_security_config()
        
        # Remove sensitive information
        if 'admin_whitelist' in config.get('ip_whitelist', {}):
            config['ip_whitelist']['admin_whitelist'] = ['***.***.***.***' for _ in config['ip_whitelist']['admin_whitelist']]
        
        return jsonify({
            'success': True,
            'data': config
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting security config: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve security configuration'
        }), 500


@security_bp.route('/failed-logins', methods=['GET'])
@jwt_required()
@admin_required
def get_failed_logins():
    """Get recent failed login attempts."""
    try:
        failed_logins = []
        
        if redis_client:
            # Get all failed login keys
            for key in redis_client.keys('failed_login:*'):
                ip = key.decode('utf-8').replace('failed_login:', '')
                count = int(redis_client.get(key) or 0)
                ttl = redis_client.ttl(key)
                
                failed_logins.append({
                    'ip': ip,
                    'attempts': count,
                    'expires_in': ttl,
                    'threat_level': 'high' if count >= 5 else 'medium' if count >= 3 else 'low'
                })
        
        # Sort by attempts (descending)
        failed_logins.sort(key=lambda x: x['attempts'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'failed_logins': failed_logins,
                'total': len(failed_logins)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting failed logins: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve failed login attempts'
        }), 500


@security_bp.route('/security-alerts', methods=['GET'])
@jwt_required()
@admin_required
def get_security_alerts():
    """Get recent security alerts."""
    try:
        # This would typically query from a monitoring system
        # For now, return sample alerts based on current threat data
        alerts = []
        
        # Check for high-risk IPs
        summary = threat_detector.get_threat_summary()
        for ip in summary.get('high_risk_ips', []):
            alerts.append({
                'type': 'high_risk_ip',
                'severity': 'high',
                'message': f'High risk IP detected: {ip}',
                'timestamp': datetime.utcnow().isoformat(),
                'details': {'ip': ip}
            })
        
        # Check for multiple failed login IPs
        if redis_client:
            for key in redis_client.keys('failed_login:*'):
                count = int(redis_client.get(key) or 0)
                if count >= 5:
                    ip = key.decode('utf-8').replace('failed_login:', '')
                    alerts.append({
                        'type': 'brute_force',
                        'severity': 'high',
                        'message': f'Possible brute force attack from {ip}',
                        'timestamp': datetime.utcnow().isoformat(),
                        'details': {'ip': ip, 'attempts': count}
                    })
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'total': len(alerts)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting security alerts: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve security alerts'
        }), 500