"""
Real-time Analytics Dashboard Service

Provides real-time data processing and dashboard visualization capabilities
with WebSocket support for live updates.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import numpy as np
import pandas as pd
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.models.evaluation import Evaluation
from app.models.user_activity import UserActivity
from app.extensions import db, socketio


@dataclass
class MetricData:
    """Real-time metric data structure"""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    timestamp: datetime
    trend: str  # 'up', 'down', 'stable'


@dataclass
class ChartData:
    """Chart data structure for dashboard"""
    chart_type: str  # 'line', 'bar', 'pie', 'gauge'
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Dict[str, Any] = None


class RealTimeAnalyticsDashboard:
    """
    Real-time analytics dashboard service providing live metrics,
    charts, and WebSocket-based updates.
    """
    
    def __init__(self):
        self.metrics_cache = {}
        self.active_connections = set()
        self.update_interval = 30  # seconds
        self.data_history = defaultdict(lambda: deque(maxlen=100))
        
    async def start_real_time_monitoring(self):
        """Start real-time monitoring and WebSocket updates"""
        while True:
            try:
                # Collect current metrics
                metrics = await self.collect_all_metrics()
                
                # Update cache and history
                self.update_metrics_cache(metrics)
                
                # Broadcast to connected clients
                await self.broadcast_metrics(metrics)
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Error in real-time monitoring: {str(e)}")
                await asyncio.sleep(self.update_interval)
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all real-time metrics"""
        return {
            'user_metrics': await self.get_user_metrics(),
            'appointment_metrics': await self.get_appointment_metrics(),
            'evaluation_metrics': await self.get_evaluation_metrics(),
            'system_metrics': await self.get_system_metrics(),
            'engagement_metrics': await self.get_engagement_metrics(),
            'performance_metrics': await self.get_performance_metrics()
        }
    
    async def get_user_metrics(self) -> Dict[str, MetricData]:
        """Get real-time user metrics"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        with db.session() as session:
            # Active users (last hour)
            active_users_current = session.query(User).filter(
                User.last_login >= hour_ago
            ).count()
            
            active_users_previous = session.query(User).filter(
                and_(User.last_login >= day_ago - timedelta(hours=1),
                     User.last_login < day_ago)
            ).count()
            
            # New registrations (last hour)
            new_users_current = session.query(User).filter(
                User.created_at >= hour_ago
            ).count()
            
            new_users_previous = session.query(User).filter(
                and_(User.created_at >= day_ago - timedelta(hours=1),
                     User.created_at < day_ago)
            ).count()
            
            # Total users
            total_users = session.query(User).count()
            
        return {
            'active_users': MetricData(
                metric_name='Active Users',
                current_value=active_users_current,
                previous_value=active_users_previous,
                change_percentage=self.calculate_change_percentage(
                    active_users_current, active_users_previous
                ),
                timestamp=now,
                trend=self.determine_trend(active_users_current, active_users_previous)
            ),
            'new_registrations': MetricData(
                metric_name='New Registrations',
                current_value=new_users_current,
                previous_value=new_users_previous,
                change_percentage=self.calculate_change_percentage(
                    new_users_current, new_users_previous
                ),
                timestamp=now,
                trend=self.determine_trend(new_users_current, new_users_previous)
            ),
            'total_users': MetricData(
                metric_name='Total Users',
                current_value=total_users,
                previous_value=total_users,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            )
        }
    
    async def get_appointment_metrics(self) -> Dict[str, MetricData]:
        """Get real-time appointment metrics"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        with db.session() as session:
            # Appointments scheduled (last hour)
            scheduled_current = session.query(Appointment).filter(
                Appointment.created_at >= hour_ago
            ).count()
            
            scheduled_previous = session.query(Appointment).filter(
                and_(Appointment.created_at >= day_ago - timedelta(hours=1),
                     Appointment.created_at < day_ago)
            ).count()
            
            # Completed appointments (last hour)
            completed_current = session.query(Appointment).filter(
                and_(Appointment.updated_at >= hour_ago,
                     Appointment.status == 'completed')
            ).count()
            
            completed_previous = session.query(Appointment).filter(
                and_(Appointment.updated_at >= day_ago - timedelta(hours=1),
                     Appointment.updated_at < day_ago,
                     Appointment.status == 'completed')
            ).count()
            
            # Cancelled appointments (last hour)
            cancelled_current = session.query(Appointment).filter(
                and_(Appointment.updated_at >= hour_ago,
                     Appointment.status == 'cancelled')
            ).count()
            
        return {
            'appointments_scheduled': MetricData(
                metric_name='Appointments Scheduled',
                current_value=scheduled_current,
                previous_value=scheduled_previous,
                change_percentage=self.calculate_change_percentage(
                    scheduled_current, scheduled_previous
                ),
                timestamp=now,
                trend=self.determine_trend(scheduled_current, scheduled_previous)
            ),
            'appointments_completed': MetricData(
                metric_name='Appointments Completed',
                current_value=completed_current,
                previous_value=completed_previous,
                change_percentage=self.calculate_change_percentage(
                    completed_current, completed_previous
                ),
                timestamp=now,
                trend=self.determine_trend(completed_current, completed_previous)
            ),
            'appointments_cancelled': MetricData(
                metric_name='Appointments Cancelled',
                current_value=cancelled_current,
                previous_value=0,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            )
        }
    
    async def get_evaluation_metrics(self) -> Dict[str, MetricData]:
        """Get real-time evaluation metrics"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        with db.session() as session:
            # Evaluations submitted (last hour)
            submitted_current = session.query(Evaluation).filter(
                Evaluation.submitted_at >= hour_ago
            ).count()
            
            # Average score (last hour)
            avg_score_result = session.query(
                func.avg(Evaluation.score)
            ).filter(
                Evaluation.submitted_at >= hour_ago
            ).scalar()
            
            avg_score = float(avg_score_result) if avg_score_result else 0.0
            
        return {
            'evaluations_submitted': MetricData(
                metric_name='Evaluations Submitted',
                current_value=submitted_current,
                previous_value=0,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            ),
            'average_score': MetricData(
                metric_name='Average Score',
                current_value=avg_score,
                previous_value=avg_score,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            )
        }
    
    async def get_system_metrics(self) -> Dict[str, MetricData]:
        """Get real-time system metrics"""
        now = datetime.utcnow()
        
        # Database connection count (simulated)
        db_connections = 15
        
        # Memory usage (simulated)
        memory_usage = 67.5
        
        # CPU usage (simulated)
        cpu_usage = 23.8
        
        return {
            'database_connections': MetricData(
                metric_name='Database Connections',
                current_value=db_connections,
                previous_value=db_connections,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            ),
            'memory_usage': MetricData(
                metric_name='Memory Usage (%)',
                current_value=memory_usage,
                previous_value=memory_usage,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            ),
            'cpu_usage': MetricData(
                metric_name='CPU Usage (%)',
                current_value=cpu_usage,
                previous_value=cpu_usage,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            )
        }
    
    async def get_engagement_metrics(self) -> Dict[str, MetricData]:
        """Get real-time engagement metrics"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        with db.session() as session:
            # Page views (simulated)
            page_views = session.query(UserActivity).filter(
                and_(UserActivity.timestamp >= hour_ago,
                     UserActivity.activity_type == 'page_view')
            ).count()
            
            # Session duration (simulated average)
            avg_session_duration = 1250.0  # seconds
            
        return {
            'page_views': MetricData(
                metric_name='Page Views',
                current_value=page_views,
                previous_value=0,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            ),
            'avg_session_duration': MetricData(
                metric_name='Avg Session Duration (sec)',
                current_value=avg_session_duration,
                previous_value=avg_session_duration,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            )
        }
    
    async def get_performance_metrics(self) -> Dict[str, MetricData]:
        """Get real-time performance metrics"""
        now = datetime.utcnow()
        
        # Response time (simulated)
        avg_response_time = 127.5  # milliseconds
        
        # Error rate (simulated)
        error_rate = 0.8  # percentage
        
        # Throughput (simulated)
        throughput = 45.2  # requests per second
        
        return {
            'avg_response_time': MetricData(
                metric_name='Avg Response Time (ms)',
                current_value=avg_response_time,
                previous_value=avg_response_time,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            ),
            'error_rate': MetricData(
                metric_name='Error Rate (%)',
                current_value=error_rate,
                previous_value=error_rate,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            ),
            'throughput': MetricData(
                metric_name='Throughput (req/sec)',
                current_value=throughput,
                previous_value=throughput,
                change_percentage=0.0,
                timestamp=now,
                trend='stable'
            )
        }
    
    def update_metrics_cache(self, metrics: Dict[str, Any]):
        """Update metrics cache and history"""
        timestamp = datetime.utcnow()
        
        for category, category_metrics in metrics.items():
            if category not in self.metrics_cache:
                self.metrics_cache[category] = {}
                
            for metric_name, metric_data in category_metrics.items():
                # Update cache
                self.metrics_cache[category][metric_name] = metric_data
                
                # Update history
                history_key = f"{category}.{metric_name}"
                self.data_history[history_key].append({
                    'timestamp': timestamp.isoformat(),
                    'value': metric_data.current_value
                })
    
    async def broadcast_metrics(self, metrics: Dict[str, Any]):
        """Broadcast metrics to connected WebSocket clients"""
        if not self.active_connections:
            return
            
        # Convert metrics to serializable format
        serializable_metrics = {}
        for category, category_metrics in metrics.items():
            serializable_metrics[category] = {}
            for metric_name, metric_data in category_metrics.items():
                serializable_metrics[category][metric_name] = asdict(metric_data)
                # Convert datetime to ISO string
                serializable_metrics[category][metric_name]['timestamp'] = \
                    metric_data.timestamp.isoformat()
        
        # Broadcast to all connected clients
        socketio.emit('analytics_update', serializable_metrics, room='analytics')
    
    def get_chart_data(self, chart_type: str, metric_name: str, 
                      time_range: str = '1h') -> ChartData:
        """Generate chart data for specified metric"""
        
        if chart_type == 'line':
            return self.generate_line_chart(metric_name, time_range)
        elif chart_type == 'bar':
            return self.generate_bar_chart(metric_name, time_range)
        elif chart_type == 'pie':
            return self.generate_pie_chart(metric_name)
        elif chart_type == 'gauge':
            return self.generate_gauge_chart(metric_name)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
    def generate_line_chart(self, metric_name: str, time_range: str) -> ChartData:
        """Generate line chart data"""
        history = list(self.data_history[metric_name])
        
        # Filter by time range
        now = datetime.utcnow()
        if time_range == '1h':
            cutoff = now - timedelta(hours=1)
        elif time_range == '24h':
            cutoff = now - timedelta(days=1)
        elif time_range == '7d':
            cutoff = now - timedelta(days=7)
        else:
            cutoff = now - timedelta(hours=1)
        
        filtered_history = [
            point for point in history
            if datetime.fromisoformat(point['timestamp']) >= cutoff
        ]
        
        labels = [point['timestamp'] for point in filtered_history]
        values = [point['value'] for point in filtered_history]
        
        return ChartData(
            chart_type='line',
            title=f'{metric_name} Over Time',
            labels=labels,
            datasets=[{
                'label': metric_name,
                'data': values,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.4
            }],
            options={
                'responsive': True,
                'scales': {
                    'x': {'type': 'time'},
                    'y': {'beginAtZero': True}
                }
            }
        )
    
    def generate_bar_chart(self, metric_name: str, time_range: str) -> ChartData:
        """Generate bar chart data"""
        # Aggregate data by hour for bar chart
        history = list(self.data_history[metric_name])
        
        hourly_data = defaultdict(float)
        for point in history[-24:]:  # Last 24 points
            hour = datetime.fromisoformat(point['timestamp']).strftime('%H:00')
            hourly_data[hour] += point['value']
        
        labels = list(hourly_data.keys())
        values = list(hourly_data.values())
        
        return ChartData(
            chart_type='bar',
            title=f'{metric_name} by Hour',
            labels=labels,
            datasets=[{
                'label': metric_name,
                'data': values,
                'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        )
    
    def generate_pie_chart(self, metric_name: str) -> ChartData:
        """Generate pie chart data"""
        # Sample pie chart data
        labels = ['Category A', 'Category B', 'Category C', 'Category D']
        values = [30, 25, 25, 20]
        colors = [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 205, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)'
        ]
        
        return ChartData(
            chart_type='pie',
            title=f'{metric_name} Distribution',
            labels=labels,
            datasets=[{
                'data': values,
                'backgroundColor': colors,
                'borderWidth': 1
            }]
        )
    
    def generate_gauge_chart(self, metric_name: str) -> ChartData:
        """Generate gauge chart data"""
        # Get current value from cache
        current_value = 75.0  # Default value
        
        for category in self.metrics_cache.values():
            for name, metric in category.items():
                if name == metric_name:
                    current_value = metric.current_value
                    break
        
        return ChartData(
            chart_type='gauge',
            title=f'{metric_name} Gauge',
            labels=[],
            datasets=[{
                'value': current_value,
                'min': 0,
                'max': 100,
                'threshold': 80
            }]
        )
    
    def calculate_change_percentage(self, current: float, previous: float) -> float:
        """Calculate percentage change between current and previous values"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100.0
    
    def determine_trend(self, current: float, previous: float) -> str:
        """Determine trend direction"""
        if current > previous:
            return 'up'
        elif current < previous:
            return 'down'
        else:
            return 'stable'
    
    def add_client_connection(self, client_id: str):
        """Add client to active connections"""
        self.active_connections.add(client_id)
    
    def remove_client_connection(self, client_id: str):
        """Remove client from active connections"""
        self.active_connections.discard(client_id)
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary with key metrics"""
        summary = {
            'total_metrics': sum(len(category) for category in self.metrics_cache.values()),
            'active_connections': len(self.active_connections),
            'last_update': datetime.utcnow().isoformat(),
            'key_metrics': {}
        }
        
        # Extract key metrics
        for category, metrics in self.metrics_cache.items():
            summary['key_metrics'][category] = {}
            for name, metric in metrics.items():
                summary['key_metrics'][category][name] = {
                    'value': metric.current_value,
                    'trend': metric.trend,
                    'change': metric.change_percentage
                }
        
        return summary


# WebSocket event handlers
@socketio.on('connect', namespace='/analytics')
def handle_analytics_connect():
    """Handle client connection to analytics namespace"""
    from flask_socketio import join_room
    
    dashboard = RealTimeAnalyticsDashboard()
    dashboard.add_client_connection(str(id(dashboard)))
    join_room('analytics')
    
    # Send initial data
    socketio.emit('analytics_connected', {
        'status': 'connected',
        'message': 'Connected to real-time analytics'
    })


@socketio.on('disconnect', namespace='/analytics')
def handle_analytics_disconnect():
    """Handle client disconnection from analytics namespace"""
    dashboard = RealTimeAnalyticsDashboard()
    dashboard.remove_client_connection(str(id(dashboard)))


@socketio.on('request_chart_data', namespace='/analytics')
def handle_chart_data_request(data):
    """Handle chart data request"""
    dashboard = RealTimeAnalyticsDashboard()
    
    chart_type = data.get('chart_type', 'line')
    metric_name = data.get('metric_name', 'active_users')
    time_range = data.get('time_range', '1h')
    
    try:
        chart_data = dashboard.get_chart_data(chart_type, metric_name, time_range)
        socketio.emit('chart_data_response', {
            'success': True,
            'data': asdict(chart_data)
        })
    except Exception as e:
        socketio.emit('chart_data_response', {
            'success': False,
            'error': str(e)
        })


# Initialize dashboard instance
dashboard_instance = RealTimeAnalyticsDashboard()