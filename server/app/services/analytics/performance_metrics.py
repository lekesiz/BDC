"""
Performance Metrics and KPI Tracking Service

Comprehensive performance monitoring and KPI tracking system
for business metrics, operational metrics, and system performance.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sqlalchemy import func, and_, or_, case, text
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.models.evaluation import Evaluation
from app.models.user_activity import UserActivity
from app.extensions import db


class MetricType(Enum):
    """Types of metrics"""
    BUSINESS = "business"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    USER_EXPERIENCE = "user_experience"


class TrendDirection(Enum):
    """Trend direction for metrics"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


@dataclass
class KPIMetric:
    """KPI metric data structure"""
    name: str
    current_value: float
    previous_value: float
    target_value: float
    unit: str
    metric_type: MetricType
    trend: TrendDirection
    change_percentage: float
    status: str  # 'on_track', 'at_risk', 'critical'
    timestamp: datetime


@dataclass
class PerformanceDashboard:
    """Performance dashboard data structure"""
    business_metrics: List[KPIMetric]
    operational_metrics: List[KPIMetric]
    technical_metrics: List[KPIMetric]
    user_experience_metrics: List[KPIMetric]
    overall_health_score: float
    alerts: List[Dict[str, Any]]


@dataclass
class MetricAlert:
    """Metric alert data structure"""
    metric_name: str
    alert_level: str  # 'warning', 'critical'
    current_value: float
    threshold: float
    message: str
    timestamp: datetime


class PerformanceMetricsService:
    """
    Service for tracking and analyzing performance metrics and KPIs
    across all aspects of the BDC platform.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metric_cache = {}
        self.cache_duration = timedelta(minutes=15)
        self.last_cache_update = {}
        
        # Define KPI targets
        self.kpi_targets = {
            'user_retention_rate': 85.0,
            'appointment_completion_rate': 90.0,
            'evaluation_score_average': 80.0,
            'system_uptime': 99.9,
            'response_time_avg': 200.0,  # milliseconds
            'user_satisfaction_score': 4.5,  # out of 5
            'monthly_active_users': 1000,
            'conversion_rate': 15.0,
            'support_ticket_resolution_time': 24.0,  # hours
            'error_rate': 1.0  # percentage
        }
        
        # Define alert thresholds
        self.alert_thresholds = {
            'warning': {
                'user_retention_rate': 80.0,
                'appointment_completion_rate': 85.0,
                'system_uptime': 99.0,
                'response_time_avg': 300.0,
                'error_rate': 2.0
            },
            'critical': {
                'user_retention_rate': 70.0,
                'appointment_completion_rate': 75.0,
                'system_uptime': 95.0,
                'response_time_avg': 500.0,
                'error_rate': 5.0
            }
        }
    
    async def get_performance_dashboard(self) -> PerformanceDashboard:
        """Get comprehensive performance dashboard"""
        try:
            # Collect all metrics
            business_metrics = await self.get_business_metrics()
            operational_metrics = await self.get_operational_metrics()
            technical_metrics = await self.get_technical_metrics()
            user_experience_metrics = await self.get_user_experience_metrics()
            
            # Calculate overall health score
            all_metrics = business_metrics + operational_metrics + technical_metrics + user_experience_metrics
            health_score = self.calculate_overall_health_score(all_metrics)
            
            # Generate alerts
            alerts = self.generate_alerts(all_metrics)
            
            return PerformanceDashboard(
                business_metrics=business_metrics,
                operational_metrics=operational_metrics,
                technical_metrics=technical_metrics,
                user_experience_metrics=user_experience_metrics,
                overall_health_score=health_score,
                alerts=alerts
            )
            
        except Exception as e:
            self.logger.error(f"Error getting performance dashboard: {str(e)}")
            raise
    
    async def get_business_metrics(self) -> List[KPIMetric]:
        """Get business-related KPI metrics"""
        try:
            cache_key = "business_metrics"
            if self.is_cache_valid(cache_key):
                return self.metric_cache[cache_key]
            
            with db.session() as session:
                now = datetime.utcnow()
                current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
                last_month_end = current_month_start - timedelta(seconds=1)
                
                metrics = []
                
                # Monthly Active Users (MAU)
                current_mau = session.query(func.count(func.distinct(UserActivity.user_id))).filter(
                    UserActivity.timestamp >= current_month_start
                ).scalar() or 0
                
                previous_mau = session.query(func.count(func.distinct(UserActivity.user_id))).filter(
                    and_(UserActivity.timestamp >= last_month_start,
                         UserActivity.timestamp <= last_month_end)
                ).scalar() or 0
                
                metrics.append(self.create_kpi_metric(
                    name="Monthly Active Users",
                    current_value=current_mau,
                    previous_value=previous_mau,
                    target_value=self.kpi_targets['monthly_active_users'],
                    unit="users",
                    metric_type=MetricType.BUSINESS
                ))
                
                # User Retention Rate (30-day)
                thirty_days_ago = now - timedelta(days=30)
                sixty_days_ago = now - timedelta(days=60)
                
                # Users who were active 30-60 days ago
                cohort_users = session.query(func.distinct(UserActivity.user_id)).filter(
                    and_(UserActivity.timestamp >= sixty_days_ago,
                         UserActivity.timestamp < thirty_days_ago)
                ).subquery()
                
                # How many of those were also active in the last 30 days
                retained_users = session.query(func.count(func.distinct(UserActivity.user_id))).filter(
                    and_(UserActivity.user_id.in_(cohort_users),
                         UserActivity.timestamp >= thirty_days_ago)
                ).scalar() or 0
                
                total_cohort_users = session.query(func.count()).select_from(cohort_users).scalar() or 0
                retention_rate = (retained_users / total_cohort_users * 100) if total_cohort_users > 0 else 0
                
                # Previous period retention for comparison
                previous_retention_rate = retention_rate * 0.95  # Simulated previous value
                
                metrics.append(self.create_kpi_metric(
                    name="User Retention Rate",
                    current_value=retention_rate,
                    previous_value=previous_retention_rate,
                    target_value=self.kpi_targets['user_retention_rate'],
                    unit="%",
                    metric_type=MetricType.BUSINESS
                ))
                
                # Conversion Rate (appointments scheduled / new users)
                new_users_current = session.query(User).filter(
                    User.created_at >= current_month_start
                ).count()
                
                appointments_by_new_users = session.query(Appointment).join(User).filter(
                    and_(User.created_at >= current_month_start,
                         Appointment.created_at >= current_month_start)
                ).count()
                
                conversion_rate = (appointments_by_new_users / new_users_current * 100) if new_users_current > 0 else 0
                previous_conversion_rate = conversion_rate * 0.9  # Simulated
                
                metrics.append(self.create_kpi_metric(
                    name="Conversion Rate",
                    current_value=conversion_rate,
                    previous_value=previous_conversion_rate,
                    target_value=self.kpi_targets['conversion_rate'],
                    unit="%",
                    metric_type=MetricType.BUSINESS
                ))
                
                # Revenue per User (simulated)
                total_revenue = new_users_current * 50  # $50 per user (simulated)
                revenue_per_user = total_revenue / new_users_current if new_users_current > 0 else 0
                previous_revenue_per_user = revenue_per_user * 0.95  # Simulated
                
                metrics.append(self.create_kpi_metric(
                    name="Revenue per User",
                    current_value=revenue_per_user,
                    previous_value=previous_revenue_per_user,
                    target_value=60.0,
                    unit="$",
                    metric_type=MetricType.BUSINESS
                ))
                
                # Cache results
                self.metric_cache[cache_key] = metrics
                self.last_cache_update[cache_key] = now
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error getting business metrics: {str(e)}")
            raise
    
    async def get_operational_metrics(self) -> List[KPIMetric]:
        """Get operational KPI metrics"""
        try:
            cache_key = "operational_metrics"
            if self.is_cache_valid(cache_key):
                return self.metric_cache[cache_key]
            
            with db.session() as session:
                now = datetime.utcnow()
                current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
                last_month_end = current_month_start - timedelta(seconds=1)
                
                metrics = []
                
                # Appointment Completion Rate
                current_appointments = session.query(Appointment).filter(
                    Appointment.created_at >= current_month_start
                ).count()
                
                completed_appointments = session.query(Appointment).filter(
                    and_(Appointment.created_at >= current_month_start,
                         Appointment.status == 'completed')
                ).count()
                
                completion_rate = (completed_appointments / current_appointments * 100) if current_appointments > 0 else 0
                
                # Previous month comparison
                previous_appointments = session.query(Appointment).filter(
                    and_(Appointment.created_at >= last_month_start,
                         Appointment.created_at <= last_month_end)
                ).count()
                
                previous_completed = session.query(Appointment).filter(
                    and_(Appointment.created_at >= last_month_start,
                         Appointment.created_at <= last_month_end,
                         Appointment.status == 'completed')
                ).count()
                
                previous_completion_rate = (previous_completed / previous_appointments * 100) if previous_appointments > 0 else 0
                
                metrics.append(self.create_kpi_metric(
                    name="Appointment Completion Rate",
                    current_value=completion_rate,
                    previous_value=previous_completion_rate,
                    target_value=self.kpi_targets['appointment_completion_rate'],
                    unit="%",
                    metric_type=MetricType.OPERATIONAL
                ))
                
                # No-show Rate
                noshow_appointments = session.query(Appointment).filter(
                    and_(Appointment.created_at >= current_month_start,
                         Appointment.status == 'no_show')
                ).count()
                
                noshow_rate = (noshow_appointments / current_appointments * 100) if current_appointments > 0 else 0
                
                previous_noshow = session.query(Appointment).filter(
                    and_(Appointment.created_at >= last_month_start,
                         Appointment.created_at <= last_month_end,
                         Appointment.status == 'no_show')
                ).count()
                
                previous_noshow_rate = (previous_noshow / previous_appointments * 100) if previous_appointments > 0 else 0
                
                metrics.append(self.create_kpi_metric(
                    name="No-show Rate",
                    current_value=noshow_rate,
                    previous_value=previous_noshow_rate,
                    target_value=5.0,  # Target: less than 5%
                    unit="%",
                    metric_type=MetricType.OPERATIONAL
                ))
                
                # Average Evaluation Score
                current_evaluations = session.query(Evaluation).filter(
                    Evaluation.created_at >= current_month_start
                ).all()
                
                if current_evaluations:
                    avg_score = np.mean([e.score for e in current_evaluations if e.score])
                else:
                    avg_score = 0
                
                previous_evaluations = session.query(Evaluation).filter(
                    and_(Evaluation.created_at >= last_month_start,
                         Evaluation.created_at <= last_month_end)
                ).all()
                
                if previous_evaluations:
                    previous_avg_score = np.mean([e.score for e in previous_evaluations if e.score])
                else:
                    previous_avg_score = 0
                
                metrics.append(self.create_kpi_metric(
                    name="Average Evaluation Score",
                    current_value=avg_score,
                    previous_value=previous_avg_score,
                    target_value=self.kpi_targets['evaluation_score_average'],
                    unit="points",
                    metric_type=MetricType.OPERATIONAL
                ))
                
                # Staff Utilization Rate (simulated)
                staff_utilization = 78.5  # Simulated percentage
                previous_staff_utilization = 75.2
                
                metrics.append(self.create_kpi_metric(
                    name="Staff Utilization Rate",
                    current_value=staff_utilization,
                    previous_value=previous_staff_utilization,
                    target_value=80.0,
                    unit="%",
                    metric_type=MetricType.OPERATIONAL
                ))
                
                # Cache results
                self.metric_cache[cache_key] = metrics
                self.last_cache_update[cache_key] = now
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error getting operational metrics: {str(e)}")
            raise
    
    async def get_technical_metrics(self) -> List[KPIMetric]:
        """Get technical performance metrics"""
        try:
            cache_key = "technical_metrics"
            if self.is_cache_valid(cache_key):
                return self.metric_cache[cache_key]
            
            now = datetime.utcnow()
            metrics = []
            
            # System Uptime (simulated)
            uptime = 99.95
            previous_uptime = 99.87
            
            metrics.append(self.create_kpi_metric(
                name="System Uptime",
                current_value=uptime,
                previous_value=previous_uptime,
                target_value=self.kpi_targets['system_uptime'],
                unit="%",
                metric_type=MetricType.TECHNICAL
            ))
            
            # Average Response Time (simulated)
            avg_response_time = 185.5  # milliseconds
            previous_response_time = 202.3
            
            metrics.append(self.create_kpi_metric(
                name="Average Response Time",
                current_value=avg_response_time,
                previous_value=previous_response_time,
                target_value=self.kpi_targets['response_time_avg'],
                unit="ms",
                metric_type=MetricType.TECHNICAL
            ))
            
            # Error Rate (simulated)
            error_rate = 0.8  # percentage
            previous_error_rate = 1.2
            
            metrics.append(self.create_kpi_metric(
                name="Error Rate",
                current_value=error_rate,
                previous_value=previous_error_rate,
                target_value=self.kpi_targets['error_rate'],
                unit="%",
                metric_type=MetricType.TECHNICAL
            ))
            
            # Database Performance (simulated)
            db_response_time = 45.2  # milliseconds
            previous_db_response_time = 48.7
            
            metrics.append(self.create_kpi_metric(
                name="Database Response Time",
                current_value=db_response_time,
                previous_value=previous_db_response_time,
                target_value=50.0,
                unit="ms",
                metric_type=MetricType.TECHNICAL
            ))
            
            # Memory Usage (simulated)
            memory_usage = 67.8  # percentage
            previous_memory_usage = 71.2
            
            metrics.append(self.create_kpi_metric(
                name="Memory Usage",
                current_value=memory_usage,
                previous_value=previous_memory_usage,
                target_value=80.0,
                unit="%",
                metric_type=MetricType.TECHNICAL
            ))
            
            # Cache results
            self.metric_cache[cache_key] = metrics
            self.last_cache_update[cache_key] = now
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting technical metrics: {str(e)}")
            raise
    
    async def get_user_experience_metrics(self) -> List[KPIMetric]:
        """Get user experience metrics"""
        try:
            cache_key = "user_experience_metrics"
            if self.is_cache_valid(cache_key):
                return self.metric_cache[cache_key]
            
            now = datetime.utcnow()
            metrics = []
            
            # User Satisfaction Score (simulated - would come from surveys)
            satisfaction_score = 4.3  # out of 5
            previous_satisfaction = 4.1
            
            metrics.append(self.create_kpi_metric(
                name="User Satisfaction Score",
                current_value=satisfaction_score,
                previous_value=previous_satisfaction,
                target_value=self.kpi_targets['user_satisfaction_score'],
                unit="/5",
                metric_type=MetricType.USER_EXPERIENCE
            ))
            
            # Page Load Time (simulated)
            page_load_time = 2.1  # seconds
            previous_page_load_time = 2.4
            
            metrics.append(self.create_kpi_metric(
                name="Page Load Time",
                current_value=page_load_time,
                previous_value=previous_page_load_time,
                target_value=3.0,
                unit="sec",
                metric_type=MetricType.USER_EXPERIENCE
            ))
            
            # Support Ticket Resolution Time (simulated)
            resolution_time = 18.5  # hours
            previous_resolution_time = 22.3
            
            metrics.append(self.create_kpi_metric(
                name="Support Ticket Resolution Time",
                current_value=resolution_time,
                previous_value=previous_resolution_time,
                target_value=self.kpi_targets['support_ticket_resolution_time'],
                unit="hours",
                metric_type=MetricType.USER_EXPERIENCE
            ))
            
            # Feature Adoption Rate (simulated)
            feature_adoption = 72.5  # percentage
            previous_feature_adoption = 68.9
            
            metrics.append(self.create_kpi_metric(
                name="Feature Adoption Rate",
                current_value=feature_adoption,
                previous_value=previous_feature_adoption,
                target_value=75.0,
                unit="%",
                metric_type=MetricType.USER_EXPERIENCE
            ))
            
            # Cache results
            self.metric_cache[cache_key] = metrics
            self.last_cache_update[cache_key] = now
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting user experience metrics: {str(e)}")
            raise
    
    def create_kpi_metric(self, name: str, current_value: float, previous_value: float,
                         target_value: float, unit: str, metric_type: MetricType) -> KPIMetric:
        """Create a KPI metric with calculated trend and status"""
        
        # Calculate change percentage
        if previous_value != 0:
            change_percentage = ((current_value - previous_value) / previous_value) * 100
        else:
            change_percentage = 100.0 if current_value > 0 else 0.0
        
        # Determine trend
        if abs(change_percentage) < 1:  # Less than 1% change
            trend = TrendDirection.STABLE
        elif change_percentage > 0:
            trend = TrendDirection.UP
        else:
            trend = TrendDirection.DOWN
        
        # Determine status based on target achievement
        if current_value >= target_value * 0.95:  # Within 5% of target
            status = "on_track"
        elif current_value >= target_value * 0.85:  # Within 15% of target
            status = "at_risk"
        else:
            status = "critical"
        
        # For metrics where lower is better (like error rate, response time)
        lower_is_better_metrics = ["Error Rate", "Average Response Time", "Database Response Time", 
                                 "Page Load Time", "Support Ticket Resolution Time", "No-show Rate"]
        
        if name in lower_is_better_metrics:
            if current_value <= target_value * 1.05:  # Within 5% of target (lower)
                status = "on_track"
            elif current_value <= target_value * 1.15:  # Within 15% of target (lower)
                status = "at_risk"
            else:
                status = "critical"
        
        return KPIMetric(
            name=name,
            current_value=current_value,
            previous_value=previous_value,
            target_value=target_value,
            unit=unit,
            metric_type=metric_type,
            trend=trend,
            change_percentage=change_percentage,
            status=status,
            timestamp=datetime.utcnow()
        )
    
    def calculate_overall_health_score(self, metrics: List[KPIMetric]) -> float:
        """Calculate overall health score based on all metrics"""
        if not metrics:
            return 0.0
        
        status_scores = {
            "on_track": 100,
            "at_risk": 60,
            "critical": 20
        }
        
        total_score = sum(status_scores.get(metric.status, 0) for metric in metrics)
        return total_score / len(metrics)
    
    def generate_alerts(self, metrics: List[KPIMetric]) -> List[Dict[str, Any]]:
        """Generate alerts based on metric thresholds"""
        alerts = []
        
        for metric in metrics:
            metric_key = metric.name.lower().replace(" ", "_").replace("-", "_")
            
            # Check critical thresholds
            if metric_key in self.alert_thresholds['critical']:
                threshold = self.alert_thresholds['critical'][metric_key]
                
                # For metrics where lower is better
                lower_is_better = metric_key in ['error_rate', 'response_time_avg', 'no_show_rate']
                
                if (lower_is_better and metric.current_value >= threshold) or \
                   (not lower_is_better and metric.current_value <= threshold):
                    alerts.append({
                        'level': 'critical',
                        'metric': metric.name,
                        'current_value': metric.current_value,
                        'threshold': threshold,
                        'message': f"{metric.name} is critically {'high' if lower_is_better else 'low'}: {metric.current_value}{metric.unit}",
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    continue
            
            # Check warning thresholds
            if metric_key in self.alert_thresholds['warning']:
                threshold = self.alert_thresholds['warning'][metric_key]
                lower_is_better = metric_key in ['error_rate', 'response_time_avg', 'no_show_rate']
                
                if (lower_is_better and metric.current_value >= threshold) or \
                   (not lower_is_better and metric.current_value <= threshold):
                    alerts.append({
                        'level': 'warning',
                        'metric': metric.name,
                        'current_value': metric.current_value,
                        'threshold': threshold,
                        'message': f"{metric.name} is approaching threshold: {metric.current_value}{metric.unit}",
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        return alerts
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.last_cache_update:
            return False
        
        return (datetime.utcnow() - self.last_cache_update[cache_key]) < self.cache_duration
    
    async def get_metric_history(self, metric_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric"""
        try:
            # This would typically fetch from a time-series database
            # For now, generating simulated historical data
            
            history = []
            base_value = 75.0  # Base value for simulation
            
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=days-i-1)
                
                # Add some variation to simulate realistic data
                variation = np.random.normal(0, 5)
                trend = i * 0.1  # Small upward trend
                seasonal = 10 * np.sin(2 * np.pi * i / 7)  # Weekly seasonality
                
                value = base_value + variation + trend + seasonal
                
                history.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': max(0, round(value, 2)),
                    'metric_name': metric_name
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting metric history: {str(e)}")
            return []
    
    async def get_comparative_analysis(self, metrics: List[str], 
                                     period: str = 'monthly') -> Dict[str, Any]:
        """Get comparative analysis of metrics over time"""
        try:
            analysis = {
                'period': period,
                'metrics': {},
                'correlations': {},
                'insights': []
            }
            
            for metric_name in metrics:
                history = await self.get_metric_history(metric_name, 30)
                
                if history:
                    values = [point['value'] for point in history]
                    
                    analysis['metrics'][metric_name] = {
                        'current': values[-1],
                        'average': np.mean(values),
                        'trend': 'increasing' if values[-1] > values[0] else 'decreasing',
                        'volatility': np.std(values),
                        'min': min(values),
                        'max': max(values)
                    }
            
            # Generate insights
            analysis['insights'] = self.generate_metric_insights(analysis['metrics'])
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting comparative analysis: {str(e)}")
            return {}
    
    def generate_metric_insights(self, metrics: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate insights based on metric analysis"""
        insights = []
        
        for metric_name, data in metrics.items():
            if data['trend'] == 'increasing' and data['volatility'] < 5:
                insights.append(f"{metric_name} shows steady improvement with low volatility")
            elif data['volatility'] > 15:
                insights.append(f"{metric_name} shows high volatility - investigate underlying causes")
            elif data['current'] < data['average'] * 0.9:
                insights.append(f"{metric_name} is currently below historical average - attention needed")
        
        return insights
    
    async def export_metrics_report(self, start_date: datetime, 
                                  end_date: datetime) -> Dict[str, Any]:
        """Export comprehensive metrics report"""
        try:
            dashboard = await self.get_performance_dashboard()
            
            report = {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'executive_summary': {
                    'overall_health_score': dashboard.overall_health_score,
                    'total_metrics_tracked': (
                        len(dashboard.business_metrics) +
                        len(dashboard.operational_metrics) +
                        len(dashboard.technical_metrics) +
                        len(dashboard.user_experience_metrics)
                    ),
                    'critical_alerts': len([a for a in dashboard.alerts if a['level'] == 'critical']),
                    'warning_alerts': len([a for a in dashboard.alerts if a['level'] == 'warning'])
                },
                'metrics_by_category': {
                    'business': [asdict(m) for m in dashboard.business_metrics],
                    'operational': [asdict(m) for m in dashboard.operational_metrics],
                    'technical': [asdict(m) for m in dashboard.technical_metrics],
                    'user_experience': [asdict(m) for m in dashboard.user_experience_metrics]
                },
                'alerts': dashboard.alerts,
                'recommendations': self.generate_recommendations(dashboard),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics report: {str(e)}")
            raise
    
    def generate_recommendations(self, dashboard: PerformanceDashboard) -> List[str]:
        """Generate recommendations based on dashboard data"""
        recommendations = []
        
        # Check for critical metrics
        all_metrics = (dashboard.business_metrics + dashboard.operational_metrics + 
                      dashboard.technical_metrics + dashboard.user_experience_metrics)
        
        critical_metrics = [m for m in all_metrics if m.status == 'critical']
        at_risk_metrics = [m for m in all_metrics if m.status == 'at_risk']
        
        if critical_metrics:
            recommendations.append(f"Immediate attention required for {len(critical_metrics)} critical metrics")
        
        if at_risk_metrics:
            recommendations.append(f"Monitor {len(at_risk_metrics)} at-risk metrics closely")
        
        if dashboard.overall_health_score < 70:
            recommendations.append("Overall system health is below acceptable levels - implement improvement plan")
        
        # Specific recommendations based on metric types
        for metric in critical_metrics:
            if metric.metric_type == MetricType.TECHNICAL:
                recommendations.append(f"Technical issue detected: {metric.name} - escalate to engineering team")
            elif metric.metric_type == MetricType.BUSINESS:
                recommendations.append(f"Business impact: {metric.name} - review business processes")
            elif metric.metric_type == MetricType.OPERATIONAL:
                recommendations.append(f"Operational efficiency: {metric.name} - optimize workflows")
        
        return recommendations


# Initialize service instance
performance_metrics_service = PerformanceMetricsService()