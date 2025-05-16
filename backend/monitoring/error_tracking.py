"""
Error tracking system for BDC application
"""
import os
import json
import time
import logging
import traceback
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import threading
from functools import wraps

from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
import redis
from sqlalchemy import func

from backend.app.models.monitoring import ErrorLog, ErrorMetrics
from backend.app.utils.security import sanitize_sensitive_data


logger = logging.getLogger(__name__)


class ErrorTracker:
    """Central error tracking system"""
    
    def __init__(self, app: Optional[Flask] = None, 
                 db: Optional[SQLAlchemy] = None,
                 redis_client: Optional[redis.Redis] = None):
        self.app = app
        self.db = db
        self.redis_client = redis_client
        self.error_counts = defaultdict(int)
        self.error_history = []
        self.error_patterns = defaultdict(list)
        self.alert_thresholds = {
            'critical': {'count': 5, 'window': 300},  # 5 errors in 5 minutes
            'warning': {'count': 20, 'window': 3600},  # 20 errors in 1 hour
        }
        self._lock = threading.Lock()
        
        if app:
            self.init_app(app, db, redis_client)
    
    def init_app(self, app: Flask, db: SQLAlchemy, redis_client: redis.Redis):
        """Initialize error tracking with Flask app"""
        self.app = app
        self.db = db
        self.redis_client = redis_client
        
        # Register error handlers
        app.register_error_handler(Exception, self.handle_exception)
        app.register_error_handler(404, self.handle_404)
        app.register_error_handler(500, self.handle_500)
        
        # Add before_request and teardown handlers
        app.before_request(self.before_request)
        app.teardown_appcontext(self.teardown_request)
    
    def before_request(self):
        """Initialize request tracking"""
        g.request_start_time = time.time()
        g.request_id = self._generate_request_id()
    
    def teardown_request(self, exception=None):
        """Clean up after request"""
        if exception:
            self.track_error(exception)
    
    def handle_exception(self, error):
        """Global exception handler"""
        self.track_error(error)
        
        # Log the error
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        
        # Return appropriate response
        if self.app.debug:
            # In debug mode, show full traceback
            return {
                'error': str(error),
                'type': type(error).__name__,
                'traceback': traceback.format_exc(),
                'request_id': getattr(g, 'request_id', None)
            }, 500
        else:
            # In production, show generic error
            return {
                'error': 'Internal server error',
                'request_id': getattr(g, 'request_id', None)
            }, 500
    
    def handle_404(self, error):
        """Handle 404 errors"""
        self.track_error(error, severity='warning')
        return {
            'error': 'Resource not found',
            'path': request.path,
            'request_id': getattr(g, 'request_id', None)
        }, 404
    
    def handle_500(self, error):
        """Handle 500 errors"""
        self.track_error(error, severity='critical')
        return {
            'error': 'Internal server error',
            'request_id': getattr(g, 'request_id', None)
        }, 500
    
    def track_error(self, error: Exception, severity: str = 'error', 
                   context: Optional[Dict[str, Any]] = None):
        """Track an error occurrence"""
        try:
            with self._lock:
                # Extract error information
                error_type = type(error).__name__
                error_message = str(error)
                error_traceback = traceback.format_exc()
                
                # Sanitize sensitive data
                error_message = sanitize_sensitive_data(error_message)
                
                # Get request context
                request_context = self._get_request_context()
                
                # Combine contexts
                full_context = {
                    **request_context,
                    **(context or {})
                }
                
                # Create error record
                error_record = {
                    'timestamp': datetime.utcnow(),
                    'error_type': error_type,
                    'error_message': error_message,
                    'traceback': error_traceback,
                    'severity': severity,
                    'context': full_context,
                    'request_id': getattr(g, 'request_id', None),
                    'user_id': self._get_current_user_id()
                }
                
                # Store in database
                if self.db:
                    self._store_error_db(error_record)
                
                # Store in Redis for real-time analysis
                if self.redis_client:
                    self._store_error_redis(error_record)
                
                # Update in-memory metrics
                self._update_error_metrics(error_record)
                
                # Check for alert conditions
                self._check_alerts(error_record)
                
                # Log the error
                logger.error(
                    f"Error tracked: {error_type} - {error_message}",
                    extra={'error_record': error_record}
                )
                
        except Exception as e:
            # Don't let error tracking errors break the app
            logger.error(f"Error in error tracking: {str(e)}", exc_info=True)
    
    def _store_error_db(self, error_record: Dict[str, Any]):
        """Store error in database"""
        try:
            error_log = ErrorLog(
                timestamp=error_record['timestamp'],
                error_type=error_record['error_type'],
                error_message=error_record['error_message'],
                traceback=error_record['traceback'],
                severity=error_record['severity'],
                context=json.dumps(error_record['context']),
                request_id=error_record['request_id'],
                user_id=error_record['user_id']
            )
            
            self.db.session.add(error_log)
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to store error in database: {str(e)}")
            self.db.session.rollback()
    
    def _store_error_redis(self, error_record: Dict[str, Any]):
        """Store error in Redis for real-time analysis"""
        try:
            # Convert datetime to string
            error_record_copy = error_record.copy()
            error_record_copy['timestamp'] = error_record_copy['timestamp'].isoformat()
            
            # Store in sorted set by timestamp
            key = f"errors:{error_record['severity']}"
            score = error_record['timestamp'].timestamp()
            value = json.dumps(error_record_copy)
            
            self.redis_client.zadd(key, {value: score})
            
            # Expire old entries (keep last 7 days)
            self.redis_client.expire(key, 7 * 86400)
            
            # Update error counters
            counter_key = f"error_count:{error_record['error_type']}"
            self.redis_client.incr(counter_key)
            self.redis_client.expire(counter_key, 3600)  # 1 hour expiry
            
        except Exception as e:
            logger.error(f"Failed to store error in Redis: {str(e)}")
    
    def _update_error_metrics(self, error_record: Dict[str, Any]):
        """Update in-memory error metrics"""
        error_type = error_record['error_type']
        
        # Update counts
        self.error_counts[error_type] += 1
        
        # Update history (keep last 1000 errors)
        self.error_history.append(error_record)
        if len(self.error_history) > 1000:
            self.error_history.pop(0)
        
        # Update patterns
        self.error_patterns[error_type].append(error_record['timestamp'])
    
    def _check_alerts(self, error_record: Dict[str, Any]):
        """Check if error conditions warrant an alert"""
        error_type = error_record['error_type']
        severity = error_record['severity']
        
        # Check against thresholds
        for alert_level, threshold in self.alert_thresholds.items():
            if severity in ['critical', 'error'] or alert_level == 'warning':
                # Count recent errors
                recent_errors = self._count_recent_errors(
                    error_type,
                    threshold['window']
                )
                
                if recent_errors >= threshold['count']:
                    self._send_alert(
                        alert_level,
                        error_type,
                        recent_errors,
                        threshold
                    )
    
    def _count_recent_errors(self, error_type: str, window_seconds: int) -> int:
        """Count errors within time window"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=window_seconds)
        
        if error_type in self.error_patterns:
            recent_timestamps = [
                ts for ts in self.error_patterns[error_type]
                if ts > cutoff_time
            ]
            return len(recent_timestamps)
        
        return 0
    
    def _send_alert(self, alert_level: str, error_type: str, 
                   error_count: int, threshold: Dict[str, Any]):
        """Send alert for error condition"""
        alert_message = (
            f"Alert Level: {alert_level.upper()}\n"
            f"Error Type: {error_type}\n"
            f"Count: {error_count} errors in {threshold['window']} seconds\n"
            f"Threshold: {threshold['count']} errors"
        )
        
        logger.warning(f"Error alert triggered: {alert_message}")
        
        # Send alerts via multiple channels
        if self.app and hasattr(self.app, 'alarm_system'):
            # Use the alarm system for notifications
            self.app.alarm_system._send_email_notification({
                'subject': f"BDC Error Alert: {alert_level.upper()}",
                'message': alert_message,
                'error_type': error_type,
                'error_count': error_count,
                'threshold': threshold
            })
            
            # Send to Slack if critical
            if alert_level in ['critical', 'error']:
                self.app.alarm_system._send_slack_notification({
                    'text': alert_message,
                    'color': 'danger' if alert_level == 'critical' else 'warning',
                    'fields': [
                        {'title': 'Error Type', 'value': error_type, 'short': True},
                        {'title': 'Error Count', 'value': str(error_count), 'short': True}
                    ]
                })
        
        if self.redis_client:
            alert_key = f"alert:{alert_level}:{error_type}"
            self.redis_client.setex(
                alert_key,
                threshold['window'],
                json.dumps({
                    'message': alert_message,
                    'timestamp': datetime.utcnow().isoformat(),
                    'count': error_count
                })
            )
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Get current request context"""
        context = {}
        
        if request:
            context.update({
                'url': request.url,
                'method': request.method,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'referrer': request.headers.get('Referer'),
                'request_id': getattr(g, 'request_id', None)
            })
            
            # Add request data (sanitized)
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if request.is_json:
                        context['request_data'] = sanitize_sensitive_data(
                            request.get_json()
                        )
                    else:
                        context['request_data'] = sanitize_sensitive_data(
                            dict(request.form)
                        )
                except Exception:
                    context['request_data'] = 'Unable to parse request data'
        
        return context
    
    def _get_current_user_id(self) -> Optional[int]:
        """Get current user ID if available"""
        # This would depend on your authentication implementation
        # For example, with Flask-JWT-Extended:
        try:
            from flask_jwt_extended import get_jwt_identity
            return get_jwt_identity()
        except Exception:
            return None
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        summary = {
            'total_errors': 0,
            'errors_by_type': defaultdict(int),
            'errors_by_severity': defaultdict(int),
            'error_timeline': [],
            'top_errors': []
        }
        
        # Analyze recent errors
        for error in self.error_history:
            if error['timestamp'] > cutoff_time:
                summary['total_errors'] += 1
                summary['errors_by_type'][error['error_type']] += 1
                summary['errors_by_severity'][error['severity']] += 1
        
        # Create timeline
        timeline_buckets = defaultdict(int)
        bucket_size = 3600  # 1 hour buckets
        
        for error in self.error_history:
            if error['timestamp'] > cutoff_time:
                bucket = int(error['timestamp'].timestamp() / bucket_size)
                timeline_buckets[bucket] += 1
        
        summary['error_timeline'] = [
            {
                'timestamp': datetime.fromtimestamp(bucket * bucket_size),
                'count': count
            }
            for bucket, count in sorted(timeline_buckets.items())
        ]
        
        # Top errors
        summary['top_errors'] = sorted(
            summary['errors_by_type'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return summary
    
    def get_error_details(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific error"""
        if self.db:
            error = ErrorLog.query.filter_by(id=error_id).first()
            if error:
                return {
                    'id': error.id,
                    'timestamp': error.timestamp,
                    'error_type': error.error_type,
                    'error_message': error.error_message,
                    'traceback': error.traceback,
                    'severity': error.severity,
                    'context': json.loads(error.context),
                    'request_id': error.request_id,
                    'user_id': error.user_id
                }
        
        return None
    
    def get_error_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyze error trends over time"""
        if not self.db:
            return {}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query error counts by day and type
        daily_errors = self.db.session.query(
            func.date(ErrorLog.timestamp).label('date'),
            ErrorLog.error_type,
            func.count(ErrorLog.id).label('count')
        ).filter(
            ErrorLog.timestamp >= cutoff_date
        ).group_by(
            func.date(ErrorLog.timestamp),
            ErrorLog.error_type
        ).all()
        
        # Process results
        trends = defaultdict(lambda: defaultdict(int))
        
        for record in daily_errors:
            date_str = record.date.isoformat()
            trends[date_str][record.error_type] = record.count
        
        return dict(trends)
    
    def cleanup_old_errors(self, days: int = 30):
        """Clean up old error records"""
        if self.db:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old error logs
            deleted = ErrorLog.query.filter(
                ErrorLog.timestamp < cutoff_date
            ).delete()
            
            self.db.session.commit()
            
            logger.info(f"Cleaned up {deleted} old error records")
            
            return deleted
        
        return 0


def error_handler(severity: str = 'error'):
    """Decorator for error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get error tracker from app context
                from flask import current_app
                if hasattr(current_app, 'error_tracker'):
                    current_app.error_tracker.track_error(
                        e,
                        severity=severity,
                        context={
                            'function': func.__name__,
                            'args': str(args)[:200],
                            'kwargs': str(kwargs)[:200]
                        }
                    )
                raise
        return wrapper
    return decorator


class ErrorMetricsCollector:
    """Collect and process error metrics"""
    
    def __init__(self, error_tracker: ErrorTracker):
        self.error_tracker = error_tracker
        self.metrics = defaultdict(lambda: defaultdict(int))
    
    def collect_metrics(self):
        """Collect current error metrics"""
        # Get summary from error tracker
        summary = self.error_tracker.get_error_summary(hours=1)
        
        # Update metrics
        self.metrics['errors']['total'] = summary['total_errors']
        
        for error_type, count in summary['errors_by_type'].items():
            self.metrics['errors'][f'type_{error_type}'] = count
        
        for severity, count in summary['errors_by_severity'].items():
            self.metrics['errors'][f'severity_{severity}'] = count
        
        # Calculate error rate
        if hasattr(self.error_tracker, 'app'):
            request_count = self._get_request_count()
            if request_count > 0:
                self.metrics['rates']['error_rate'] = (
                    summary['total_errors'] / request_count
                )
        
        return dict(self.metrics)
    
    def _get_request_count(self) -> int:
        """Get total request count for time period"""
        # This would integrate with your request tracking
        # For now, return a placeholder
        return 1000
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        for category, metrics in self.metrics.items():
            for metric_name, value in metrics.items():
                prometheus_name = f"bdc_{category}_{metric_name}"
                lines.append(f"# TYPE {prometheus_name} gauge")
                lines.append(f"{prometheus_name} {value}")
        
        return '\n'.join(lines)


def init_error_tracking(app: Flask, db: SQLAlchemy, redis_client: redis.Redis):
    """Initialize error tracking for the application"""
    error_tracker = ErrorTracker(app, db, redis_client)
    app.error_tracker = error_tracker
    
    # Create metrics collector
    metrics_collector = ErrorMetricsCollector(error_tracker)
    app.error_metrics_collector = metrics_collector
    
    # Register cleanup task
    @app.cli.command()
    def cleanup_errors():
        """Clean up old error records"""
        count = error_tracker.cleanup_old_errors()
        print(f"Cleaned up {count} old error records")
    
    return error_tracker