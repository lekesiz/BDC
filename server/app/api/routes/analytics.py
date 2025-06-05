"""
Log Analytics API Routes
Provides endpoints for accessing log analysis results and insights
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
import json

from app.services.log_analytics_service import (
    log_analytics_service,
    AnalysisType,
    LogLevel
)
from app.middleware.auth_middleware import require_role
from app.utils.logger import get_logger
from app.security.audit_logger import audit_logger

from app.utils.logging import logger

logger = get_logger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/logs/insights', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def get_log_insights():
    """Get recent log analysis insights"""
    try:
        # Get query parameters
        hours = int(request.args.get('hours', 24))
        analysis_types = request.args.getlist('types')
        min_severity = request.args.get('min_severity', 'low')
        
        # Validate parameters
        if hours > 168:  # Max 1 week
            hours = 168
        
        # Map severity levels
        severity_map = {
            'low': 1,
            'medium': 2, 
            'high': 3,
            'critical': 4
        }
        min_severity_level = severity_map.get(min_severity, 1)
        
        # Get cached analysis results
        analysis_history = log_analytics_service.get_analysis_history(limit=100)
        
        # Filter results
        filtered_results = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        for entry in analysis_history:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if entry_time < cutoff_time:
                continue
            
            for result in entry['results']:
                # Filter by analysis type
                if analysis_types and result['analysis_type'] not in analysis_types:
                    continue
                
                # Filter by severity
                result_severity = severity_map.get(result['severity'], 1)
                if result_severity < min_severity_level:
                    continue
                
                filtered_results.append({
                    **result,
                    'analysis_timestamp': entry['timestamp']
                })
        
        # Sort by timestamp (newest first)
        filtered_results.sort(
            key=lambda x: x['analysis_timestamp'], 
            reverse=True
        )
        
        # Group by analysis type
        grouped_results = {}
        for result in filtered_results:
            analysis_type = result['analysis_type']
            if analysis_type not in grouped_results:
                grouped_results[analysis_type] = []
            grouped_results[analysis_type].append(result)
        
        return jsonify({
            'success': True,
            'data': {
                'insights': filtered_results[:50],  # Limit to 50 most recent
                'grouped_insights': grouped_results,
                'summary': {
                    'total_insights': len(filtered_results),
                    'time_range_hours': hours,
                    'analysis_types': list(grouped_results.keys()),
                    'severity_distribution': _get_severity_distribution(filtered_results)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting log insights: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get log insights'
        }), 500

@analytics_bp.route('/logs/patterns', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def analyze_log_patterns():
    """Analyze log patterns for a specific time period"""
    try:
        # Get query parameters
        hours = int(request.args.get('hours', 1))
        analysis_type = request.args.get('type', 'error_pattern')
        
        # Validate parameters
        if hours > 24:  # Max 24 hours for on-demand analysis
            hours = 24
        
        user_id = get_jwt_identity()
        
        # Run specific analysis based on type
        if analysis_type == 'error_pattern':
            results = log_analytics_service.analyze_error_patterns(hours * 3600)
        elif analysis_type == 'performance_trend':
            results = log_analytics_service.analyze_performance_trends(hours * 3600)
        elif analysis_type == 'security_incident':
            results = log_analytics_service.analyze_security_incidents(hours * 3600)
        elif analysis_type == 'usage_pattern':
            results = log_analytics_service.analyze_usage_patterns(hours * 3600)
        elif analysis_type == 'anomaly_detection':
            results = log_analytics_service.detect_anomalies(hours * 3600)
        else:
            return jsonify({
                'success': False,
                'message': f'Invalid analysis type: {analysis_type}'
            }), 400
        
        # Convert results to dict format
        results_data = [result.to_dict() for result in results]
        
        # Log the analysis request
        audit_logger.log_security_event(
            event_type="LOG_ANALYSIS_REQUEST",
            user_id=user_id,
            ip_address=request.remote_addr,
            metadata={
                "analysis_type": analysis_type,
                "time_window_hours": hours,
                "results_count": len(results)
            },
            risk_level="low"
        )
        
        return jsonify({
            'success': True,
            'data': {
                'analysis_type': analysis_type,
                'time_window_hours': hours,
                'results': results_data,
                'summary': {
                    'total_patterns': len(results),
                    'high_severity_count': len([r for r in results if r.severity.value in ['high', 'critical']]),
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing log patterns: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to analyze log patterns'
        }), 500

@analytics_bp.route('/logs/search', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def search_logs():
    """Search logs with advanced filtering"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Parse search parameters
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        log_levels = data.get('log_levels', [])
        sources = data.get('sources', [])
        search_query = data.get('query', '')
        max_results = min(int(data.get('max_results', 1000)), 5000)  # Max 5000 results
        
        # Validate and parse timestamps
        try:
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            else:
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            
            if end_time_str:
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            else:
                end_time = datetime.now(timezone.utc)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid timestamp format. Use ISO format.'
            }), 400
        
        # Convert log levels
        log_level_objects = []
        for level_str in log_levels:
            try:
                log_level_objects.append(LogLevel(level_str.upper()))
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Invalid log level: {level_str}'
                }), 400
        
        # Get logs from the service
        logs = log_analytics_service.get_logs(
            start_time=start_time,
            end_time=end_time,
            log_levels=log_level_objects if log_level_objects else None,
            sources=sources if sources else None,
            max_logs=max_results
        )
        
        # Filter by search query if provided
        if search_query:
            filtered_logs = []
            query_lower = search_query.lower()
            for log in logs:
                if (query_lower in log.message.lower() or 
                    (log.correlation_id and query_lower in log.correlation_id.lower()) or
                    (log.user_id and query_lower in str(log.user_id).lower())):
                    filtered_logs.append(log)
            logs = filtered_logs
        
        # Convert to dict format
        logs_data = [log.to_dict() for log in logs]
        
        # Generate statistics
        level_counts = {}
        source_counts = {}
        hourly_counts = {}
        
        for log in logs:
            # Count by level
            level = log.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
            
            # Count by source
            source = log.source
            source_counts[source] = source_counts.get(source, 0) + 1
            
            # Count by hour
            hour = log.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        # Log the search request
        audit_logger.log_security_event(
            event_type="LOG_SEARCH_REQUEST",
            user_id=user_id,
            ip_address=request.remote_addr,
            metadata={
                "search_query": search_query,
                "time_range": f"{start_time.isoformat()} to {end_time.isoformat()}",
                "results_count": len(logs),
                "log_levels": log_levels,
                "sources": sources
            },
            risk_level="low"
        )
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs_data,
                'statistics': {
                    'total_logs': len(logs),
                    'level_distribution': level_counts,
                    'source_distribution': source_counts,
                    'hourly_distribution': hourly_counts,
                    'time_range': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat()
                    }
                },
                'search_parameters': {
                    'query': search_query,
                    'log_levels': log_levels,
                    'sources': sources,
                    'max_results': max_results
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching logs: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to search logs'
        }), 500

@analytics_bp.route('/logs/trends', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def get_log_trends():
    """Get log trends and statistics"""
    try:
        # Get query parameters
        days = int(request.args.get('days', 7))
        granularity = request.args.get('granularity', 'hour')  # hour, day
        
        # Validate parameters
        if days > 30:  # Max 30 days
            days = 30
        
        if granularity not in ['hour', 'day']:
            granularity = 'hour'
        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        # Get logs for the time period
        logs = log_analytics_service.get_logs(
            start_time=start_time,
            end_time=end_time,
            max_logs=50000  # Higher limit for trend analysis
        )
        
        # Generate trends based on granularity
        if granularity == 'hour':
            time_format = '%Y-%m-%d %H:00'
            time_delta = timedelta(hours=1)
        else:  # day
            time_format = '%Y-%m-%d'
            time_delta = timedelta(days=1)
        
        # Initialize time buckets
        trends = {}
        current_time = start_time
        while current_time <= end_time:
            time_key = current_time.strftime(time_format)
            trends[time_key] = {
                'timestamp': time_key,
                'total': 0,
                'error': 0,
                'warning': 0,
                'info': 0,
                'debug': 0,
                'critical': 0
            }
            current_time += time_delta
        
        # Populate trends with log data
        for log in logs:
            time_key = log.timestamp.strftime(time_format)
            if time_key in trends:
                trends[time_key]['total'] += 1
                level_key = log.level.value.lower()
                if level_key in trends[time_key]:
                    trends[time_key][level_key] += 1
        
        # Convert to list and sort by timestamp
        trends_list = list(trends.values())
        trends_list.sort(key=lambda x: x['timestamp'])
        
        # Calculate summary statistics
        total_logs = len(logs)
        error_logs = len([log for log in logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]])
        warning_logs = len([log for log in logs if log.level == LogLevel.WARNING])
        
        error_rate = (error_logs / total_logs * 100) if total_logs > 0 else 0
        warning_rate = (warning_logs / total_logs * 100) if total_logs > 0 else 0
        
        # Get unique sources and users
        unique_sources = len(set(log.source for log in logs))
        unique_users = len(set(log.user_id for log in logs if log.user_id))
        
        return jsonify({
            'success': True,
            'data': {
                'trends': trends_list,
                'summary': {
                    'total_logs': total_logs,
                    'error_count': error_logs,
                    'warning_count': warning_logs,
                    'error_rate': round(error_rate, 2),
                    'warning_rate': round(warning_rate, 2),
                    'unique_sources': unique_sources,
                    'unique_users': unique_users,
                    'time_range': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat(),
                        'days': days,
                        'granularity': granularity
                    }
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting log trends: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get log trends'
        }), 500

@analytics_bp.route('/logs/export', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def export_logs():
    """Export logs in various formats"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Parse export parameters
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        format_type = data.get('format', 'json')  # json, csv
        log_levels = data.get('log_levels', [])
        sources = data.get('sources', [])
        max_results = min(int(data.get('max_results', 10000)), 50000)  # Max 50k for export
        
        # Validate format
        if format_type not in ['json', 'csv']:
            return jsonify({
                'success': False,
                'message': 'Invalid format. Use json or csv.'
            }), 400
        
        # Parse timestamps
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Invalid timestamp format. Use ISO format.'
            }), 400
        
        # Convert log levels
        log_level_objects = []
        for level_str in log_levels:
            try:
                log_level_objects.append(LogLevel(level_str.upper()))
            except ValueError:
                pass
        
        # Get logs
        logs = log_analytics_service.get_logs(
            start_time=start_time,
            end_time=end_time,
            log_levels=log_level_objects if log_level_objects else None,
            sources=sources if sources else None,
            max_logs=max_results
        )
        
        # Log the export request
        audit_logger.log_security_event(
            event_type="LOG_EXPORT_REQUEST",
            user_id=user_id,
            ip_address=request.remote_addr,
            metadata={
                "format": format_type,
                "time_range": f"{start_time.isoformat()} to {end_time.isoformat()}",
                "exported_count": len(logs),
                "log_levels": log_levels,
                "sources": sources
            },
            risk_level="medium"  # Log exports are more sensitive
        )
        
        # Format data based on requested format
        if format_type == 'json':
            export_data = [log.to_dict() for log in logs]
            return jsonify({
                'success': True,
                'data': {
                    'logs': export_data,
                    'export_info': {
                        'format': format_type,
                        'count': len(logs),
                        'exported_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            })
        
        elif format_type == 'csv':
            # Convert logs to CSV format
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'timestamp', 'level', 'source', 'message', 
                'correlation_id', 'user_id', 'request_id'
            ])
            
            # Write data
            for log in logs:
                writer.writerow([
                    log.timestamp.isoformat(),
                    log.level.value,
                    log.source,
                    log.message,
                    log.correlation_id or '',
                    log.user_id or '',
                    log.request_id or ''
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return jsonify({
                'success': True,
                'data': {
                    'csv_content': csv_content,
                    'export_info': {
                        'format': format_type,
                        'count': len(logs),
                        'exported_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            })
        
    except Exception as e:
        logger.error(f"Error exporting logs: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to export logs'
        }), 500

@analytics_bp.route('/status', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def get_analytics_status():
    """Get log analytics service status"""
    try:
        # Check service status
        status = {
            'enabled': log_analytics_service.enabled,
            'elasticsearch_connected': bool(log_analytics_service.es_client),
            'redis_connected': bool(log_analytics_service.redis_client),
            'background_analysis_running': log_analytics_service.running,
            'analysis_interval_seconds': log_analytics_service.analysis_interval,
            'cache_duration_seconds': log_analytics_service.cache_duration
        }
        
        # Test connections
        if log_analytics_service.es_client:
            try:
                status['elasticsearch_health'] = log_analytics_service.es_client.ping()
            except:
                status['elasticsearch_health'] = False
        
        if log_analytics_service.redis_client:
            try:
                log_analytics_service.redis_client.ping()
                status['redis_health'] = True
            except:
                status['redis_health'] = False
        
        # Get recent analysis count
        recent_analysis = log_analytics_service.get_analysis_history(limit=10)
        status['recent_analysis_count'] = len(recent_analysis)
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get analytics status'
        }), 500

def _get_severity_distribution(results: list) -> dict:
    """Get distribution of severities in results"""
    distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    
    for result in results:
        severity = result.get('severity', 'low')
        if severity in distribution:
            distribution[severity] += 1
    
    return distribution

# Register error handlers for this blueprint
@analytics_bp.errorhandler(404)
def handle_not_found(error):
    return jsonify({
        'success': False,
        'message': 'Analytics endpoint not found'
    }), 404

@analytics_bp.errorhandler(500)
def handle_internal_error(error):
    logger.error(f"Internal error in analytics API: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Internal server error in analytics system'
    }), 500