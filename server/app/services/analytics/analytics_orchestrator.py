"""
Analytics Orchestrator

Central orchestration service that coordinates all analytics components,
manages workflows, and provides unified access to analytics capabilities.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json

from .real_time_dashboard import RealTimeAnalyticsDashboard, dashboard_instance
from .predictive_analytics import PredictiveAnalyticsService, predictive_analytics_service
from .user_behavior_analytics import UserBehaviorAnalytics, user_behavior_analytics
from .performance_metrics import PerformanceMetricsService, performance_metrics_service
from .report_generator import CustomReportGenerator, custom_report_generator
from .data_export import DataExportService, data_export_service


class AnalyticsWorkflowType(Enum):
    """Types of analytics workflows"""
    REAL_TIME_MONITORING = "real_time_monitoring"
    DAILY_INSIGHTS = "daily_insights"
    WEEKLY_REPORTS = "weekly_reports"
    MONTHLY_ANALYTICS = "monthly_analytics"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    USER_BEHAVIOR_ANALYSIS = "user_behavior_analysis"
    PERFORMANCE_MONITORING = "performance_monitoring"
    CUSTOM_WORKFLOW = "custom_workflow"


@dataclass
class AnalyticsWorkflow:
    """Analytics workflow configuration"""
    workflow_id: str
    name: str
    description: str
    workflow_type: AnalyticsWorkflowType
    components: List[str]
    schedule: Optional[str] = None
    parameters: Dict[str, Any] = None
    active: bool = True


@dataclass
class WorkflowExecution:
    """Workflow execution result"""
    execution_id: str
    workflow_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str  # 'running', 'completed', 'failed'
    results: Dict[str, Any]
    errors: List[str]


@dataclass
class AnalyticsInsight:
    """Analytics insight structure"""
    insight_id: str
    category: str
    title: str
    description: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    confidence: float
    recommendations: List[str]
    data_sources: List[str]
    generated_at: datetime


class AnalyticsOrchestrator:
    """
    Central orchestration service for all analytics components.
    Manages workflows, coordinates services, and provides unified access.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Analytics service instances
        self.dashboard = dashboard_instance
        self.predictive_service = predictive_analytics_service
        self.behavior_analytics = user_behavior_analytics
        self.performance_service = performance_metrics_service
        self.report_generator = custom_report_generator
        self.data_export = data_export_service
        
        # Workflow management
        self.workflows = {}
        self.workflow_executions = {}
        self.running_workflows = set()
        
        # Insights storage
        self.insights = {}
        self.insight_history = []
        
        # Initialize default workflows
        self.initialize_default_workflows()
    
    def initialize_default_workflows(self):
        """Initialize default analytics workflows"""
        
        # Real-time monitoring workflow
        self.workflows['real_time_monitoring'] = AnalyticsWorkflow(
            workflow_id='real_time_monitoring',
            name='Real-time Monitoring',
            description='Continuous real-time monitoring and alerting',
            workflow_type=AnalyticsWorkflowType.REAL_TIME_MONITORING,
            components=['dashboard', 'performance_metrics'],
            schedule='continuous',
            parameters={'update_interval': 30}
        )
        
        # Daily insights workflow
        self.workflows['daily_insights'] = AnalyticsWorkflow(
            workflow_id='daily_insights',
            name='Daily Insights',
            description='Daily analytics insights and recommendations',
            workflow_type=AnalyticsWorkflowType.DAILY_INSIGHTS,
            components=['performance_metrics', 'user_behavior', 'predictive_analytics'],
            schedule='daily',
            parameters={'report_format': 'json'}
        )
        
        # Weekly reports workflow
        self.workflows['weekly_reports'] = AnalyticsWorkflow(
            workflow_id='weekly_reports',
            name='Weekly Reports',
            description='Comprehensive weekly analytics reports',
            workflow_type=AnalyticsWorkflowType.WEEKLY_REPORTS,
            components=['report_generator', 'data_export'],
            schedule='weekly',
            parameters={'template': 'operational_analytics', 'format': 'pdf'}
        )
        
        # Monthly analytics workflow
        self.workflows['monthly_analytics'] = AnalyticsWorkflow(
            workflow_id='monthly_analytics',
            name='Monthly Analytics',
            description='Monthly comprehensive analytics and strategic insights',
            workflow_type=AnalyticsWorkflowType.MONTHLY_ANALYTICS,
            components=['user_behavior', 'predictive_analytics', 'report_generator'],
            schedule='monthly',
            parameters={'include_forecasts': True, 'cohort_analysis': True}
        )
    
    async def start_orchestrator(self):
        """Start the analytics orchestrator"""
        try:
            self.logger.info("Starting Analytics Orchestrator")
            
            # Initialize all services
            await self.initialize_services()
            
            # Start scheduled workflows
            await self.start_scheduled_workflows()
            
            # Start real-time monitoring
            asyncio.create_task(self.run_continuous_monitoring())
            
            self.logger.info("Analytics Orchestrator started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting orchestrator: {str(e)}")
            raise
    
    async def initialize_services(self):
        """Initialize all analytics services"""
        try:
            # Initialize predictive models
            await self.predictive_service.initialize_models()
            
            # Initialize dashboard
            # Dashboard initialization handled in dashboard service
            
            self.logger.info("All analytics services initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing services: {str(e)}")
            raise
    
    async def start_scheduled_workflows(self):
        """Start scheduled workflow execution"""
        try:
            for workflow in self.workflows.values():
                if workflow.schedule and workflow.active:
                    if workflow.schedule == 'continuous':
                        asyncio.create_task(self.run_continuous_workflow(workflow))
                    else:
                        asyncio.create_task(self.schedule_workflow(workflow))
            
            self.logger.info("Scheduled workflows started")
            
        except Exception as e:
            self.logger.error(f"Error starting scheduled workflows: {str(e)}")
            raise
    
    async def run_continuous_monitoring(self):
        """Run continuous real-time monitoring"""
        while True:
            try:
                # Check for alerts and critical conditions
                alerts = await self.check_system_alerts()
                
                if alerts:
                    await self.handle_alerts(alerts)
                
                # Sleep before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def execute_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> WorkflowExecution:
        """Execute a specific workflow"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            execution_id = f"{workflow_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Merge parameters
            final_parameters = workflow.parameters.copy() if workflow.parameters else {}
            if parameters:
                final_parameters.update(parameters)
            
            # Create execution record
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                started_at=datetime.utcnow(),
                completed_at=None,
                status='running',
                results={},
                errors=[]
            )
            
            self.workflow_executions[execution_id] = execution
            self.running_workflows.add(workflow_id)
            
            self.logger.info(f"Starting workflow execution: {execution_id}")
            
            # Execute workflow components
            results = {}
            for component in workflow.components:
                try:
                    component_result = await self.execute_component(component, final_parameters)
                    results[component] = component_result
                except Exception as e:
                    error_msg = f"Error in component {component}: {str(e)}"
                    execution.errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Update execution status
            execution.completed_at = datetime.utcnow()
            execution.status = 'completed' if not execution.errors else 'failed'
            execution.results = results
            
            self.running_workflows.discard(workflow_id)
            
            # Generate insights from results
            insights = await self.generate_workflow_insights(workflow, results)
            execution.results['insights'] = insights
            
            self.logger.info(f"Workflow execution completed: {execution_id}")
            
            return execution
            
        except Exception as e:
            self.logger.error(f"Error executing workflow: {str(e)}")
            
            # Update execution with error
            if 'execution' in locals():
                execution.completed_at = datetime.utcnow()
                execution.status = 'failed'
                execution.errors.append(str(e))
                self.running_workflows.discard(workflow_id)
            
            raise
    
    async def execute_component(self, component: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific analytics component"""
        try:
            if component == 'dashboard':
                return await self.execute_dashboard_component(parameters)
            elif component == 'performance_metrics':
                return await self.execute_performance_component(parameters)
            elif component == 'user_behavior':
                return await self.execute_user_behavior_component(parameters)
            elif component == 'predictive_analytics':
                return await self.execute_predictive_component(parameters)
            elif component == 'report_generator':
                return await self.execute_report_component(parameters)
            elif component == 'data_export':
                return await self.execute_export_component(parameters)
            else:
                raise ValueError(f"Unknown component: {component}")
                
        except Exception as e:
            self.logger.error(f"Error executing component {component}: {str(e)}")
            raise
    
    async def execute_dashboard_component(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute dashboard analytics component"""
        metrics = await self.dashboard.collect_all_metrics()
        summary = self.dashboard.get_dashboard_summary()
        
        return {
            'component': 'dashboard',
            'metrics': metrics,
            'summary': summary,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def execute_performance_component(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute performance metrics component"""
        dashboard = await self.performance_service.get_performance_dashboard()
        
        return {
            'component': 'performance_metrics',
            'dashboard': asdict(dashboard),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def execute_user_behavior_component(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute user behavior analytics component"""
        engagement_metrics = await self.behavior_analytics.calculate_engagement_metrics()
        behavioral_segments = await self.behavior_analytics.segment_users_by_behavior()
        feature_usage = await self.behavior_analytics.analyze_feature_usage()
        
        return {
            'component': 'user_behavior',
            'engagement_summary': {
                'total_users': len(engagement_metrics),
                'avg_engagement_score': sum(m.engagement_score for m in engagement_metrics) / len(engagement_metrics) if engagement_metrics else 0
            },
            'behavioral_segments': [asdict(s) for s in behavioral_segments],
            'feature_usage': feature_usage,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def execute_predictive_component(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute predictive analytics component"""
        # Retrain models if needed
        await self.predictive_service.retrain_models_if_needed()
        
        # Get model performance
        model_performance = await self.predictive_service.get_model_performance()
        
        # Generate sample predictions (would be based on actual data)
        sample_predictions = {
            'churn_predictions': 'Generated for high-risk users',
            'capacity_forecast': 'Generated for next 7 days',
            'appointment_noshow_predictions': 'Generated for upcoming appointments'
        }
        
        return {
            'component': 'predictive_analytics',
            'model_performance': {name: asdict(perf) for name, perf in model_performance.items()},
            'predictions': sample_predictions,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def execute_report_component(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation component"""
        template_id = parameters.get('template', 'executive_summary')
        
        report = await self.report_generator.generate_report(template_id, parameters)
        
        return {
            'component': 'report_generator',
            'report': asdict(report),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def execute_export_component(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data export component"""
        from .data_export import ExportRequest, ExportFormat
        
        # Create export request
        export_request = ExportRequest(
            export_id=f"workflow_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            data_sources=parameters.get('data_sources', ['users', 'appointments']),
            filters=parameters.get('filters', {}),
            format=ExportFormat(parameters.get('format', 'json')),
            include_metadata=parameters.get('include_metadata', True)
        )
        
        export_result = await self.data_export.export_data(export_request)
        
        return {
            'component': 'data_export',
            'export_result': asdict(export_result),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def generate_workflow_insights(self, workflow: AnalyticsWorkflow, 
                                       results: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate insights from workflow results"""
        insights = []
        
        try:
            # Generate insights based on workflow type
            if workflow.workflow_type == AnalyticsWorkflowType.DAILY_INSIGHTS:
                insights.extend(await self.generate_daily_insights(results))
            elif workflow.workflow_type == AnalyticsWorkflowType.PERFORMANCE_MONITORING:
                insights.extend(await self.generate_performance_insights(results))
            elif workflow.workflow_type == AnalyticsWorkflowType.USER_BEHAVIOR_ANALYSIS:
                insights.extend(await self.generate_behavior_insights(results))
            
            # Store insights
            for insight in insights:
                self.insights[insight.insight_id] = insight
                self.insight_history.append(insight)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating workflow insights: {str(e)}")
            return []
    
    async def generate_daily_insights(self, results: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate daily insights from workflow results"""
        insights = []
        
        # Performance insights
        if 'performance_metrics' in results:
            performance_data = results['performance_metrics']['dashboard']
            health_score = performance_data.get('overall_health_score', 0)
            
            if health_score < 70:
                insights.append(AnalyticsInsight(
                    insight_id=f"daily_health_{datetime.utcnow().strftime('%Y%m%d')}",
                    category='Performance',
                    title='System Health Below Threshold',
                    description=f'Overall system health score is {health_score:.1f}%, below acceptable threshold',
                    priority='high',
                    confidence=0.9,
                    recommendations=[
                        'Review critical alerts and address immediately',
                        'Investigate performance bottlenecks',
                        'Consider scaling resources if needed'
                    ],
                    data_sources=['performance_metrics'],
                    generated_at=datetime.utcnow()
                ))
        
        # User behavior insights
        if 'user_behavior' in results:
            behavior_data = results['user_behavior']
            avg_engagement = behavior_data['engagement_summary'].get('avg_engagement_score', 0)
            
            if avg_engagement > 75:
                insights.append(AnalyticsInsight(
                    insight_id=f"daily_engagement_{datetime.utcnow().strftime('%Y%m%d')}",
                    category='User Engagement',
                    title='High User Engagement Detected',
                    description=f'Average user engagement score is {avg_engagement:.1f}%, indicating strong platform adoption',
                    priority='medium',
                    confidence=0.8,
                    recommendations=[
                        'Leverage high engagement for user testimonials',
                        'Consider expanding successful features',
                        'Plan capacity for continued growth'
                    ],
                    data_sources=['user_behavior'],
                    generated_at=datetime.utcnow()
                ))
        
        return insights
    
    async def generate_performance_insights(self, results: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate performance-specific insights"""
        insights = []
        
        if 'performance_metrics' in results:
            performance_data = results['performance_metrics']['dashboard']
            alerts = performance_data.get('alerts', [])
            
            critical_alerts = [a for a in alerts if a['level'] == 'critical']
            
            if critical_alerts:
                insights.append(AnalyticsInsight(
                    insight_id=f"perf_critical_{datetime.utcnow().strftime('%Y%m%d_%H%M')}",
                    category='Performance',
                    title='Critical Performance Issues Detected',
                    description=f'{len(critical_alerts)} critical performance alerts require immediate attention',
                    priority='critical',
                    confidence=1.0,
                    recommendations=[
                        'Address critical alerts immediately',
                        'Escalate to technical team',
                        'Monitor system closely for resolution'
                    ],
                    data_sources=['performance_metrics'],
                    generated_at=datetime.utcnow()
                ))
        
        return insights
    
    async def generate_behavior_insights(self, results: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate user behavior insights"""
        insights = []
        
        if 'user_behavior' in results:
            behavior_data = results['user_behavior']
            segments = behavior_data.get('behavioral_segments', [])
            
            # Find at-risk segment
            at_risk_segments = [s for s in segments if 'at risk' in s.get('segment_name', '').lower()]
            
            if at_risk_segments and at_risk_segments[0].get('user_count', 0) > 100:
                insights.append(AnalyticsInsight(
                    insight_id=f"behavior_atrisk_{datetime.utcnow().strftime('%Y%m%d')}",
                    category='User Behavior',
                    title='High Number of At-Risk Users',
                    description=f'{at_risk_segments[0]["user_count"]} users identified as at-risk for churn',
                    priority='high',
                    confidence=0.85,
                    recommendations=[
                        'Implement targeted re-engagement campaigns',
                        'Provide personalized support to at-risk users',
                        'Analyze common factors contributing to risk'
                    ],
                    data_sources=['user_behavior'],
                    generated_at=datetime.utcnow()
                ))
        
        return insights
    
    async def check_system_alerts(self) -> List[Dict[str, Any]]:
        """Check for system-wide alerts"""
        try:
            dashboard = await self.performance_service.get_performance_dashboard()
            return dashboard.alerts
            
        except Exception as e:
            self.logger.error(f"Error checking system alerts: {str(e)}")
            return []
    
    async def handle_alerts(self, alerts: List[Dict[str, Any]]):
        """Handle system alerts"""
        try:
            critical_alerts = [a for a in alerts if a['level'] == 'critical']
            
            if critical_alerts:
                self.logger.warning(f"Critical alerts detected: {len(critical_alerts)}")
                
                # Generate alert insight
                alert_insight = AnalyticsInsight(
                    insight_id=f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    category='System Alert',
                    title='Critical System Alerts',
                    description=f'{len(critical_alerts)} critical alerts require immediate attention',
                    priority='critical',
                    confidence=1.0,
                    recommendations=['Address critical issues immediately', 'Check system status'],
                    data_sources=['performance_monitoring'],
                    generated_at=datetime.utcnow()
                )
                
                self.insights[alert_insight.insight_id] = alert_insight
                self.insight_history.append(alert_insight)
            
        except Exception as e:
            self.logger.error(f"Error handling alerts: {str(e)}")
    
    async def run_continuous_workflow(self, workflow: AnalyticsWorkflow):
        """Run a continuous workflow"""
        while workflow.active:
            try:
                await self.execute_workflow(workflow.workflow_id)
                
                # Sleep based on update interval
                interval = workflow.parameters.get('update_interval', 300)  # 5 minutes default
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in continuous workflow {workflow.workflow_id}: {str(e)}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def schedule_workflow(self, workflow: AnalyticsWorkflow):
        """Schedule a workflow for periodic execution"""
        while workflow.active:
            try:
                now = datetime.utcnow()
                
                # Calculate next execution time based on schedule
                if workflow.schedule == 'daily':
                    next_execution = now.replace(hour=6, minute=0, second=0, microsecond=0)
                    if next_execution <= now:
                        next_execution += timedelta(days=1)
                elif workflow.schedule == 'weekly':
                    # Execute on Mondays at 6 AM
                    days_until_monday = (7 - now.weekday()) % 7
                    next_execution = (now + timedelta(days=days_until_monday)).replace(
                        hour=6, minute=0, second=0, microsecond=0
                    )
                elif workflow.schedule == 'monthly':
                    # Execute on the 1st of each month at 6 AM
                    if now.day == 1 and now.hour < 6:
                        next_execution = now.replace(hour=6, minute=0, second=0, microsecond=0)
                    else:
                        next_month = now.replace(day=1) + timedelta(days=32)
                        next_execution = next_month.replace(day=1, hour=6, minute=0, second=0, microsecond=0)
                else:
                    # Default to daily
                    next_execution = now + timedelta(days=1)
                
                # Wait until next execution time
                sleep_duration = (next_execution - now).total_seconds()
                if sleep_duration > 0:
                    await asyncio.sleep(sleep_duration)
                
                # Execute workflow
                await self.execute_workflow(workflow.workflow_id)
                
            except Exception as e:
                self.logger.error(f"Error in scheduled workflow {workflow.workflow_id}: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    # Public API methods
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            # Get dashboard summary
            dashboard_summary = self.dashboard.get_dashboard_summary()
            
            # Get performance summary
            performance_dashboard = await self.performance_service.get_performance_dashboard()
            
            # Get recent insights
            recent_insights = sorted(self.insight_history, key=lambda x: x.generated_at, reverse=True)[:10]
            
            # Get workflow status
            workflow_status = {
                'total_workflows': len(self.workflows),
                'active_workflows': len([w for w in self.workflows.values() if w.active]),
                'running_workflows': len(self.running_workflows)
            }
            
            return {
                'dashboard_summary': dashboard_summary,
                'performance_health_score': performance_dashboard.overall_health_score,
                'recent_insights': [asdict(insight) for insight in recent_insights],
                'workflow_status': workflow_status,
                'alerts': performance_dashboard.alerts,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analytics summary: {str(e)}")
            raise
    
    async def create_custom_workflow(self, workflow_config: Dict[str, Any]) -> AnalyticsWorkflow:
        """Create a custom analytics workflow"""
        try:
            workflow = AnalyticsWorkflow(
                workflow_id=workflow_config['workflow_id'],
                name=workflow_config['name'],
                description=workflow_config.get('description', ''),
                workflow_type=AnalyticsWorkflowType(workflow_config.get('workflow_type', 'custom_workflow')),
                components=workflow_config['components'],
                schedule=workflow_config.get('schedule'),
                parameters=workflow_config.get('parameters', {}),
                active=workflow_config.get('active', True)
            )
            
            self.workflows[workflow.workflow_id] = workflow
            
            # Start workflow if it has a schedule
            if workflow.schedule and workflow.active:
                if workflow.schedule == 'continuous':
                    asyncio.create_task(self.run_continuous_workflow(workflow))
                else:
                    asyncio.create_task(self.schedule_workflow(workflow))
            
            return workflow
            
        except Exception as e:
            self.logger.error(f"Error creating custom workflow: {str(e)}")
            raise
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        # Get recent executions
        recent_executions = [
            asdict(execution) for execution_id, execution in self.workflow_executions.items()
            if execution.workflow_id == workflow_id
        ]
        recent_executions.sort(key=lambda x: x['started_at'], reverse=True)
        
        return {
            'workflow': asdict(workflow),
            'is_running': workflow_id in self.running_workflows,
            'recent_executions': recent_executions[:5],  # Last 5 executions
            'total_executions': len([e for e in self.workflow_executions.values() if e.workflow_id == workflow_id])
        }
    
    async def get_insights(self, category: Optional[str] = None, 
                         priority: Optional[str] = None, 
                         limit: int = 50) -> List[AnalyticsInsight]:
        """Get analytics insights with optional filtering"""
        insights = list(self.insights.values())
        
        # Apply filters
        if category:
            insights = [i for i in insights if i.category.lower() == category.lower()]
        
        if priority:
            insights = [i for i in insights if i.priority.lower() == priority.lower()]
        
        # Sort by generated date (most recent first)
        insights.sort(key=lambda x: x.generated_at, reverse=True)
        
        return insights[:limit]


# Initialize orchestrator instance
analytics_orchestrator = AnalyticsOrchestrator()