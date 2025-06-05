"""
Alert API Routes
Provides endpoints for managing and monitoring alerts
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
import json

from app.services.alert_service import (
    alert_service, 
    AlertSeverity, 
    AlertChannel,
    send_critical_alert,
    send_security_alert,
    send_performance_alert
)
from app.middleware.auth_middleware import require_role
from app.utils.logger import get_logger
from app.security.audit_logger import audit_logger

from app.utils.logging import logger

logger = get_logger(__name__)

# Create blueprint
alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

@alerts_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def get_alert_stats():
    """Get alert statistics and metrics"""
    try:
        stats = alert_service.get_alert_stats()
        
        # Add system health info
        stats['system_health'] = {
            'alert_service_enabled': True,
            'enabled_channels': [c.value for c in alert_service.enabled_channels],
            'total_channels_configured': len(alert_service.enabled_channels)
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting alert stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get alert statistics'
        }), 500

@alerts_bp.route('/test', methods=['POST'])
@jwt_required()
@require_role(['super_admin'])
def send_test_alert():
    """Send a test alert to verify alert system functionality"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validate request
        severity_str = data.get('severity', 'low').lower()
        try:
            severity = AlertSeverity(severity_str)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'Invalid severity. Must be one of: {[s.value for s in AlertSeverity]}'
            }), 400
        
        channels_str = data.get('channels', [])
        channels = []
        for channel_str in channels_str:
            try:
                channels.append(AlertChannel(channel_str.lower()))
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid channel: {channel_str}. Must be one of: {[c.value for c in AlertChannel]}'
                }), 400
        
        # Create test alert
        title = data.get('title', 'Test Alert from BDC System')
        message = data.get('message', f'This is a test alert sent by {user_id} to verify the alert system is working correctly.')
        
        alert_event = alert_service.create_alert(
            title=title,
            message=message,
            severity=severity,
            source='admin-panel',
            event_type='test',
            metadata={
                'test_alert': True,
                'sent_by': user_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'test_data': data.get('metadata', {})
            }
        )
        
        # Send to specific channels if requested
        if channels:
            success = alert_service.send_alert(alert_event, channels)
        else:
            success = True  # Alert was already sent by create_alert
        
        # Log the test
        audit_logger.log_security_event(
            event_type="TEST_ALERT_SENT",
            user_id=user_id,
            ip_address=request.remote_addr,
            metadata={
                "alert_id": alert_event.id,
                "severity": severity.value,
                "channels": [c.value for c in channels] if channels else "all",
                "success": success
            },
            risk_level="low"
        )
        
        return jsonify({
            'success': True,
            'message': 'Test alert sent successfully',
            'data': {
                'alert_id': alert_event.id,
                'severity': severity.value,
                'channels_sent': [c.value for c in (channels or alert_service.enabled_channels)],
                'timestamp': alert_event.timestamp.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error sending test alert: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send test alert'
        }), 500

@alerts_bp.route('/send', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def send_manual_alert():
    """Send a manual alert"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['title', 'message', 'severity', 'event_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate severity
        try:
            severity = AlertSeverity(data['severity'].lower())
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'Invalid severity. Must be one of: {[s.value for s in AlertSeverity]}'
            }), 400
        
        # Create and send alert
        alert_event = alert_service.create_alert(
            title=data['title'],
            message=data['message'],
            severity=severity,
            source=data.get('source', 'manual'),
            event_type=data['event_type'],
            metadata={
                'manual_alert': True,
                'sent_by': user_id,
                'admin_notes': data.get('notes', ''),
                **data.get('metadata', {})
            },
            affected_users=data.get('affected_users', []),
            correlation_id=data.get('correlation_id')
        )
        
        # Log the manual alert
        audit_logger.log_security_event(
            event_type="MANUAL_ALERT_SENT",
            user_id=user_id,
            ip_address=request.remote_addr,
            metadata={
                "alert_id": alert_event.id,
                "title": data['title'],
                "severity": severity.value,
                "event_type": data['event_type']
            },
            risk_level="low"
        )
        
        return jsonify({
            'success': True,
            'message': 'Alert sent successfully',
            'data': {
                'alert_id': alert_event.id,
                'timestamp': alert_event.timestamp.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error sending manual alert: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send alert'
        }), 500

@alerts_bp.route('/history', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def get_alert_history():
    """Get alert history with pagination and filtering"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)  # Max 100 per page
        severity_filter = request.args.get('severity')
        event_type_filter = request.args.get('event_type')
        source_filter = request.args.get('source')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Filter alerts
        filtered_alerts = alert_service.alert_history.copy()
        
        if severity_filter:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.severity.value == severity_filter.lower()
            ]
        
        if event_type_filter:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.event_type == event_type_filter
            ]
        
        if source_filter:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.source == source_filter
            ]
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                filtered_alerts = [
                    alert for alert in filtered_alerts
                    if alert.timestamp >= start_dt
                ]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid start_date format. Use ISO format.'
                }), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                filtered_alerts = [
                    alert for alert in filtered_alerts
                    if alert.timestamp <= end_dt
                ]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid end_date format. Use ISO format.'
                }), 400
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Paginate
        total = len(filtered_alerts)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_alerts = filtered_alerts[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': [alert.to_dict() for alert in page_alerts],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page,
                    'has_next': end_idx < total,
                    'has_prev': page > 1
                },
                'filters': {
                    'severity': severity_filter,
                    'event_type': event_type_filter,
                    'source': source_filter,
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting alert history: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get alert history'
        }), 500

@alerts_bp.route('/config', methods=['GET'])
@jwt_required()
@require_role(['super_admin'])
def get_alert_config():
    """Get current alert system configuration"""
    try:
        config = {
            'enabled_channels': [c.value for c in alert_service.enabled_channels],
            'rate_limits': {
                severity.value: {
                    'max_alerts': config['max_alerts'],
                    'window_minutes': config['window_minutes']
                }
                for severity, config in alert_service.rate_limit_config.items()
            },
            'email_config': {
                'server': alert_service.email_config.get('server'),
                'port': alert_service.email_config.get('port'),
                'use_tls': alert_service.email_config.get('use_tls'),
                'from_email': alert_service.email_config.get('from_email'),
                'admin_emails': alert_service.email_config.get('admin_emails', [])
            },
            'webhook_config': {
                'primary_configured': bool(alert_service.webhook_urls.get('primary')),
                'backup_configured': bool(alert_service.webhook_urls.get('backup')),
                'teams_configured': bool(alert_service.webhook_urls.get('teams')),
                'discord_configured': bool(alert_service.webhook_urls.get('discord'))
            },
            'slack_config': {
                'webhook_configured': bool(alert_service.slack_webhook),
                'token_configured': bool(alert_service.slack_token)
            }
        }
        
        return jsonify({
            'success': True,
            'data': config
        })
        
    except Exception as e:
        logger.error(f"Error getting alert config: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get alert configuration'
        }), 500

@alerts_bp.route('/webhook', methods=['POST'])
def webhook_receiver():
    """
    Webhook endpoint for receiving alerts from external systems
    This can be used by monitoring tools to send alerts to BDC
    """
    try:
        # Verify webhook token if configured
        webhook_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        expected_token = alert_service.webhook_urls.get('token')
        
        if expected_token and webhook_token != expected_token:
            return jsonify({
                'success': False,
                'message': 'Invalid webhook token'
            }), 401
        
        data = request.get_json()
        
        # Validate webhook payload
        required_fields = ['title', 'message', 'severity', 'source']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate severity
        try:
            severity = AlertSeverity(data['severity'].lower())
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'Invalid severity. Must be one of: {[s.value for s in AlertSeverity]}'
            }), 400
        
        # Create alert from webhook
        alert_event = alert_service.create_alert(
            title=data['title'],
            message=data['message'],
            severity=severity,
            source=data['source'],
            event_type=data.get('event_type', 'webhook'),
            metadata={
                'webhook_alert': True,
                'webhook_source': request.remote_addr,
                'webhook_timestamp': datetime.now(timezone.utc).isoformat(),
                **data.get('metadata', {})
            },
            correlation_id=data.get('correlation_id')
        )
        
        return jsonify({
            'success': True,
            'message': 'Webhook alert processed successfully',
            'data': {
                'alert_id': alert_event.id,
                'timestamp': alert_event.timestamp.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook alert: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to process webhook alert'
        }), 500

@alerts_bp.route('/health', methods=['GET'])
def alert_system_health():
    """Check alert system health status"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'enabled_channels': [c.value for c in alert_service.enabled_channels],
            'total_channels': len(alert_service.enabled_channels),
            'recent_alerts': len([
                alert for alert in alert_service.alert_history
                if (datetime.now(timezone.utc) - alert.timestamp).total_seconds() < 3600
            ])
        }
        
        # Check channel health
        channel_status = {}
        
        if AlertChannel.EMAIL in alert_service.enabled_channels:
            channel_status['email'] = {
                'configured': bool(alert_service.email_config.get('username')),
                'server': alert_service.email_config.get('server')
            }
        
        if AlertChannel.SLACK in alert_service.enabled_channels:
            channel_status['slack'] = {
                'webhook_configured': bool(alert_service.slack_webhook),
                'token_configured': bool(alert_service.slack_token)
            }
        
        if AlertChannel.WEBHOOK in alert_service.enabled_channels:
            channel_status['webhook'] = {
                'primary_configured': bool(alert_service.webhook_urls.get('primary'))
            }
        
        health_status['channels'] = channel_status
        
        return jsonify({
            'success': True,
            'data': health_status
        })
        
    except Exception as e:
        logger.error(f"Error checking alert system health: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to check alert system health'
        }), 500

# Register error handlers for this blueprint
@alerts_bp.errorhandler(404)
def handle_not_found(error):
    return jsonify({
        'success': False,
        'message': 'Alert endpoint not found'
    }), 404

@alerts_bp.errorhandler(500)
def handle_internal_error(error):
    logger.error(f"Internal error in alerts API: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Internal server error in alert system'
    }), 500