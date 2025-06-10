"""
Real-time Reporting Service

Provides real-time reporting capabilities with live data feeds:
- WebSocket connections for live updates
- Event-driven data refreshing
- Streaming data processing
- Real-time dashboard updates
- Live chart animations
- Performance optimization for high-frequency updates
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from sqlalchemy.orm import Session
from sqlalchemy import event, text
import socketio
import redis
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import queue
import weakref

from app.core.database_manager import DatabaseManager
from .report_builder_service import ReportBuilderService
from .dashboard_service import DashboardService
from .visualization_service import VisualizationService


class RealtimeReportingService:
    """Service for real-time reporting and live data feeds"""

    def __init__(self, socketio_server=None, redis_client=None):
        self.socketio = socketio_server
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.report_builder = ReportBuilderService()
        self.dashboard_service = DashboardService()
        self.visualization_service = VisualizationService()
        
        # Active subscriptions
        self.active_subscriptions: Dict[str, Dict] = {}
        self.client_subscriptions: Dict[str, Set[str]] = {}  # client_id -> subscription_ids
        
        # Update queues and workers
        self.update_queue = queue.Queue()
        self.worker_pool = ThreadPoolExecutor(max_workers=5)
        self.update_workers_running = False
        
        # Performance settings
        self.max_update_frequency = 1.0  # Maximum 1 update per second per subscription
        self.batch_update_interval = 0.5  # Batch updates every 500ms
        self.max_clients_per_subscription = 1000
        
        # Data change tracking
        self.last_update_times: Dict[str, float] = {}
        self.pending_updates: Dict[str, Dict] = {}
        
        # Start background workers
        self._start_update_workers()

    def subscribe_to_report(self, client_id: str, subscription_config: Dict[str, Any]) -> Dict[str, Any]:
        """Subscribe a client to real-time report updates"""
        
        subscription_id = subscription_config.get('id') or f"sub_{client_id}_{int(time.time())}"
        
        # Validate subscription configuration
        validation_result = self._validate_subscription_config(subscription_config)
        if not validation_result['is_valid']:
            return {
                'success': False,
                'errors': validation_result['errors']
            }
        
        # Check subscription limits
        if len(self.active_subscriptions) >= 10000:  # Global limit
            return {
                'success': False,
                'error': 'Maximum number of active subscriptions reached'
            }
        
        # Create subscription
        subscription = {
            'id': subscription_id,
            'client_id': client_id,
            'type': subscription_config.get('type', 'report'),  # report, dashboard, widget
            'config': subscription_config,
            'last_update': 0,
            'update_frequency': subscription_config.get('update_frequency', 5.0),  # seconds
            'auto_refresh': subscription_config.get('auto_refresh', True),
            'filters': subscription_config.get('filters', []),
            'created_at': time.time(),
            'update_count': 0,
            'error_count': 0,
            'last_error': None
        }
        
        # Store subscription
        self.active_subscriptions[subscription_id] = subscription
        
        # Track client subscriptions
        if client_id not in self.client_subscriptions:
            self.client_subscriptions[client_id] = set()
        self.client_subscriptions[client_id].add(subscription_id)
        
        # Send initial data
        try:
            initial_data = self._fetch_subscription_data(subscription)
            if initial_data['success']:
                self._emit_to_client(client_id, 'report_data', {
                    'subscription_id': subscription_id,
                    'type': 'initial',
                    'data': initial_data['data'],
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                subscription['last_error'] = initial_data.get('error')
                subscription['error_count'] += 1
        except Exception as e:
            subscription['last_error'] = str(e)
            subscription['error_count'] += 1
        
        # Start monitoring for this subscription type
        self._start_monitoring(subscription)
        
        return {
            'success': True,
            'subscription_id': subscription_id,
            'update_frequency': subscription['update_frequency']
        }

    def unsubscribe_from_report(self, client_id: str, subscription_id: str) -> bool:
        """Unsubscribe a client from real-time updates"""
        
        if subscription_id not in self.active_subscriptions:
            return False
        
        subscription = self.active_subscriptions[subscription_id]
        
        # Verify client ownership
        if subscription['client_id'] != client_id:
            return False
        
        # Remove subscription
        del self.active_subscriptions[subscription_id]
        
        # Update client tracking
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(subscription_id)
            if not self.client_subscriptions[client_id]:
                del self.client_subscriptions[client_id]
        
        # Clean up monitoring
        self._stop_monitoring(subscription_id)
        
        return True

    def disconnect_client(self, client_id: str):
        """Handle client disconnection"""
        
        if client_id not in self.client_subscriptions:
            return
        
        # Remove all subscriptions for this client
        subscription_ids = list(self.client_subscriptions[client_id])
        for subscription_id in subscription_ids:
            if subscription_id in self.active_subscriptions:
                del self.active_subscriptions[subscription_id]
                self._stop_monitoring(subscription_id)
        
        # Remove client tracking
        del self.client_subscriptions[client_id]

    def trigger_manual_update(self, subscription_id: str) -> Dict[str, Any]:
        """Manually trigger an update for a subscription"""
        
        if subscription_id not in self.active_subscriptions:
            return {
                'success': False,
                'error': 'Subscription not found'
            }
        
        subscription = self.active_subscriptions[subscription_id]
        
        try:
            # Fetch fresh data
            result = self._fetch_subscription_data(subscription)
            
            if result['success']:
                # Send update to client
                self._emit_to_client(subscription['client_id'], 'report_data', {
                    'subscription_id': subscription_id,
                    'type': 'manual_update',
                    'data': result['data'],
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                subscription['update_count'] += 1
                subscription['last_update'] = time.time()
                
                return {
                    'success': True,
                    'data': result['data']
                }
            else:
                subscription['error_count'] += 1
                subscription['last_error'] = result.get('error')
                
                return {
                    'success': False,
                    'error': result.get('error')
                }
                
        except Exception as e:
            subscription['error_count'] += 1
            subscription['last_error'] = str(e)
            
            return {
                'success': False,
                'error': str(e)
            }

    def get_subscription_status(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a subscription"""
        
        if subscription_id not in self.active_subscriptions:
            return None
        
        subscription = self.active_subscriptions[subscription_id]
        
        return {
            'id': subscription_id,
            'client_id': subscription['client_id'],
            'type': subscription['type'],
            'active': True,
            'update_frequency': subscription['update_frequency'],
            'auto_refresh': subscription['auto_refresh'],
            'created_at': datetime.fromtimestamp(subscription['created_at']).isoformat(),
            'last_update': datetime.fromtimestamp(subscription['last_update']).isoformat() if subscription['last_update'] > 0 else None,
            'update_count': subscription['update_count'],
            'error_count': subscription['error_count'],
            'last_error': subscription['last_error'],
            'next_update': self._get_next_update_time(subscription)
        }

    def get_active_subscriptions(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of active subscriptions"""
        
        subscriptions = []
        
        for subscription_id, subscription in self.active_subscriptions.items():
            if client_id is None or subscription['client_id'] == client_id:
                status = self.get_subscription_status(subscription_id)
                if status:
                    subscriptions.append(status)
        
        return subscriptions

    def update_subscription_config(self, subscription_id: str, 
                                 config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update subscription configuration"""
        
        if subscription_id not in self.active_subscriptions:
            return {
                'success': False,
                'error': 'Subscription not found'
            }
        
        subscription = self.active_subscriptions[subscription_id]
        
        # Update allowed fields
        allowed_updates = ['update_frequency', 'auto_refresh', 'filters']
        for key, value in config_updates.items():
            if key in allowed_updates:
                if key == 'update_frequency':
                    # Enforce minimum update frequency
                    value = max(value, 1.0)
                subscription[key] = value
                # Also update in config
                subscription['config'][key] = value
        
        return {
            'success': True,
            'subscription': self.get_subscription_status(subscription_id)
        }

    def _fetch_subscription_data(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data for a subscription"""
        
        subscription_type = subscription['type']
        config = subscription['config']
        
        try:
            if subscription_type == 'report':
                # Fetch report data
                report_config = config.get('report_config', {})
                
                # Apply real-time filters
                if subscription.get('filters'):
                    report_config = report_config.copy()
                    existing_filters = report_config.get('filters', [])
                    report_config['filters'] = existing_filters + subscription['filters']
                
                result = self.report_builder.execute_report(
                    report_config,
                    limit=config.get('limit', 1000)
                )
                
                return {
                    'success': True,
                    'data': {
                        'type': 'report',
                        'report_data': result,
                        'config': report_config
                    }
                }
                
            elif subscription_type == 'dashboard':
                # Fetch dashboard data
                dashboard_id = config.get('dashboard_id')
                if not dashboard_id:
                    return {
                        'success': False,
                        'error': 'Dashboard ID required for dashboard subscription'
                    }
                
                dashboard = self.dashboard_service.get_dashboard(dashboard_id)
                
                return {
                    'success': True,
                    'data': {
                        'type': 'dashboard',
                        'dashboard_data': dashboard,
                        'widgets': dashboard.get('widgets', [])
                    }
                }
                
            elif subscription_type == 'widget':
                # Fetch specific widget data
                widget_config = config.get('widget_config', {})
                
                widget_data = self.dashboard_service.load_widget_data(widget_config)
                
                return {
                    'success': True,
                    'data': {
                        'type': 'widget',
                        'widget_data': widget_data
                    }
                }
                
            elif subscription_type == 'chart':
                # Fetch chart data
                chart_config = config.get('chart_config', {})
                data_config = config.get('data_config', {})
                
                # Get data
                report_result = self.report_builder.execute_report(data_config)
                
                # Create chart
                chart_result = self.visualization_service.create_chart(
                    report_result['data'], 
                    chart_config
                )
                
                return {
                    'success': True,
                    'data': {
                        'type': 'chart',
                        'chart_data': chart_result,
                        'report_data': report_result
                    }
                }
                
            else:
                return {
                    'success': False,
                    'error': f'Unsupported subscription type: {subscription_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _validate_subscription_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate subscription configuration"""
        
        errors = []
        warnings = []
        
        subscription_type = config.get('type', 'report')
        if subscription_type not in ['report', 'dashboard', 'widget', 'chart']:
            errors.append(f'Invalid subscription type: {subscription_type}')
        
        update_frequency = config.get('update_frequency', 5.0)
        if update_frequency < 1.0:
            errors.append('Update frequency must be at least 1 second')
        elif update_frequency < 5.0:
            warnings.append('High update frequency may impact performance')
        
        if subscription_type == 'report':
            if not config.get('report_config'):
                errors.append('Report configuration required for report subscription')
        
        elif subscription_type == 'dashboard':
            if not config.get('dashboard_id'):
                errors.append('Dashboard ID required for dashboard subscription')
        
        elif subscription_type == 'widget':
            if not config.get('widget_config'):
                errors.append('Widget configuration required for widget subscription')
        
        elif subscription_type == 'chart':
            if not config.get('chart_config') or not config.get('data_config'):
                errors.append('Chart and data configuration required for chart subscription')
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _start_monitoring(self, subscription: Dict[str, Any]):
        """Start monitoring for data changes for a subscription"""
        
        # For now, we'll use polling-based monitoring
        # In a production environment, you might want to use database triggers,
        # message queues, or other event-driven mechanisms
        
        if subscription['auto_refresh']:
            # Schedule periodic updates
            self._schedule_update(subscription['id'])

    def _stop_monitoring(self, subscription_id: str):
        """Stop monitoring for a subscription"""
        
        # Remove from pending updates
        if subscription_id in self.pending_updates:
            del self.pending_updates[subscription_id]
        
        # Remove from last update times
        if subscription_id in self.last_update_times:
            del self.last_update_times[subscription_id]

    def _schedule_update(self, subscription_id: str):
        """Schedule an update for a subscription"""
        
        if subscription_id not in self.active_subscriptions:
            return
        
        subscription = self.active_subscriptions[subscription_id]
        
        # Check if enough time has passed
        current_time = time.time()
        last_update = self.last_update_times.get(subscription_id, 0)
        
        if current_time - last_update >= subscription['update_frequency']:
            # Queue update
            self.update_queue.put({
                'subscription_id': subscription_id,
                'timestamp': current_time
            })
            
            self.last_update_times[subscription_id] = current_time

    def _start_update_workers(self):
        """Start background workers for processing updates"""
        
        if self.update_workers_running:
            return
        
        self.update_workers_running = True
        
        # Start update processor
        self.worker_pool.submit(self._process_updates)
        
        # Start scheduler
        self.worker_pool.submit(self._schedule_periodic_updates)

    def _stop_update_workers(self):
        """Stop background workers"""
        
        self.update_workers_running = False

    def _process_updates(self):
        """Process queued updates"""
        
        while self.update_workers_running:
            try:
                # Get update from queue (with timeout)
                update = self.update_queue.get(timeout=1.0)
                
                subscription_id = update['subscription_id']
                
                if subscription_id not in self.active_subscriptions:
                    continue
                
                subscription = self.active_subscriptions[subscription_id]
                
                # Fetch fresh data
                result = self._fetch_subscription_data(subscription)
                
                if result['success']:
                    # Send update to client
                    self._emit_to_client(subscription['client_id'], 'report_data', {
                        'subscription_id': subscription_id,
                        'type': 'auto_update',
                        'data': result['data'],
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                    subscription['update_count'] += 1
                    subscription['last_update'] = time.time()
                    subscription['last_error'] = None
                else:
                    subscription['error_count'] += 1
                    subscription['last_error'] = result.get('error')
                    
                    # Send error to client
                    self._emit_to_client(subscription['client_id'], 'report_error', {
                        'subscription_id': subscription_id,
                        'error': result.get('error'),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
            except queue.Empty:
                continue
            except Exception as e:
                # Log error but continue processing
                print(f"Error processing update: {e}")

    def _schedule_periodic_updates(self):
        """Periodically check which subscriptions need updates"""
        
        while self.update_workers_running:
            try:
                current_time = time.time()
                
                for subscription_id, subscription in list(self.active_subscriptions.items()):
                    if not subscription.get('auto_refresh', True):
                        continue
                    
                    last_update = subscription.get('last_update', 0)
                    update_frequency = subscription.get('update_frequency', 5.0)
                    
                    if current_time - last_update >= update_frequency:
                        self._schedule_update(subscription_id)
                
                # Sleep before next check
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Error in periodic scheduler: {e}")
                time.sleep(5.0)  # Sleep longer on error

    def _emit_to_client(self, client_id: str, event: str, data: Dict[str, Any]):
        """Emit data to a specific client"""
        
        if self.socketio:
            try:
                self.socketio.emit(event, data, room=client_id)
            except Exception as e:
                print(f"Error emitting to client {client_id}: {e}")

    def _get_next_update_time(self, subscription: Dict[str, Any]) -> Optional[str]:
        """Calculate next update time for a subscription"""
        
        if not subscription.get('auto_refresh', True):
            return None
        
        last_update = subscription.get('last_update', 0)
        update_frequency = subscription.get('update_frequency', 5.0)
        
        if last_update == 0:
            next_update = time.time()
        else:
            next_update = last_update + update_frequency
        
        return datetime.fromtimestamp(next_update).isoformat()

    def get_system_stats(self) -> Dict[str, Any]:
        """Get real-time system statistics"""
        
        return {
            'active_subscriptions': len(self.active_subscriptions),
            'connected_clients': len(self.client_subscriptions),
            'update_queue_size': self.update_queue.qsize(),
            'total_updates_processed': sum(
                sub.get('update_count', 0) 
                for sub in self.active_subscriptions.values()
            ),
            'total_errors': sum(
                sub.get('error_count', 0) 
                for sub in self.active_subscriptions.values()
            ),
            'subscriptions_by_type': self._get_subscriptions_by_type(),
            'workers_running': self.update_workers_running,
            'average_update_frequency': self._get_average_update_frequency()
        }

    def _get_subscriptions_by_type(self) -> Dict[str, int]:
        """Get subscription count by type"""
        
        type_counts = {}
        for subscription in self.active_subscriptions.values():
            sub_type = subscription.get('type', 'unknown')
            type_counts[sub_type] = type_counts.get(sub_type, 0) + 1
        
        return type_counts

    def _get_average_update_frequency(self) -> float:
        """Get average update frequency across all subscriptions"""
        
        if not self.active_subscriptions:
            return 0.0
        
        total_frequency = sum(
            sub.get('update_frequency', 5.0) 
            for sub in self.active_subscriptions.values()
        )
        
        return total_frequency / len(self.active_subscriptions)

    def broadcast_system_notification(self, message: str, 
                                    notification_type: str = 'info',
                                    target_clients: List[str] = None):
        """Broadcast a system notification to clients"""
        
        notification = {
            'type': 'system_notification',
            'message': message,
            'notification_type': notification_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if target_clients:
            for client_id in target_clients:
                self._emit_to_client(client_id, 'system_notification', notification)
        else:
            # Broadcast to all connected clients
            if self.socketio:
                self.socketio.emit('system_notification', notification)

    def shutdown(self):
        """Shutdown the real-time service"""
        
        # Stop workers
        self._stop_update_workers()
        
        # Clear subscriptions
        self.active_subscriptions.clear()
        self.client_subscriptions.clear()
        
        # Shutdown worker pool
        self.worker_pool.shutdown(wait=True)