# Advanced Analytics System for BDC Project

This comprehensive analytics system provides real-time monitoring, predictive analytics, user behavior analysis, performance tracking, custom reporting, and data visualization capabilities.

## System Overview

The analytics system consists of six main components:

1. **Real-time Analytics Dashboard** - Live metrics and WebSocket updates
2. **Predictive Analytics** - ML-based predictions and forecasting
3. **User Behavior Analytics** - Cohort analysis and behavioral insights
4. **Performance Metrics** - KPI tracking and system monitoring
5. **Custom Report Generator** - Automated report generation
6. **Data Export & Visualization** - Multi-format exports and charts

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Analytics Orchestrator                       │
│  (Central coordination and workflow management)             │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Real-time   │ │ Predictive  │ │ User        │
│ Dashboard   │ │ Analytics   │ │ Behavior    │
└─────────────┘ └─────────────┘ └─────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Performance │ │ Report      │ │ Data Export │
│ Metrics     │ │ Generator   │ │ & Viz       │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Components

### 1. Real-time Analytics Dashboard (`real_time_dashboard.py`)

Provides live monitoring capabilities with WebSocket integration.

**Features:**
- Real-time metric collection and broadcasting
- Interactive charts and visualizations
- Live updates every 30 seconds (configurable)
- WebSocket support for instant updates
- Metric caching and history tracking

**Key Classes:**
- `RealTimeAnalyticsDashboard` - Main service class
- `MetricData` - Real-time metric structure
- `ChartData` - Chart configuration and data

**Usage Example:**
```python
from app.services.analytics import RealTimeAnalyticsDashboard

dashboard = RealTimeAnalyticsDashboard()

# Start real-time monitoring
await dashboard.start_real_time_monitoring()

# Get current metrics
metrics = await dashboard.collect_all_metrics()

# Generate chart data
chart_data = dashboard.get_chart_data('line', 'active_users', '24h')
```

### 2. Predictive Analytics (`predictive_analytics.py`)

Machine learning-based prediction system for business insights.

**Features:**
- Appointment no-show prediction
- User churn prediction
- Evaluation outcome forecasting
- Capacity planning and forecasting
- Model performance tracking and auto-retraining

**Key Classes:**
- `PredictiveAnalyticsService` - Main ML service
- `PredictionResult` - Prediction output structure
- `ModelPerformance` - Model metrics tracking

**Available Models:**
- **Appointment No-show Model**: RandomForestClassifier
- **User Churn Model**: GradientBoostingRegressor
- **Evaluation Outcome Model**: LinearRegression
- **Engagement Prediction Model**: RandomForestClassifier
- **Capacity Forecasting Model**: GradientBoostingRegressor

**Usage Example:**
```python
from app.services.analytics import PredictiveAnalyticsService

predictor = PredictiveAnalyticsService()

# Initialize models
await predictor.initialize_models()

# Predict appointment no-show
result = await predictor.predict_appointment_noshow(appointment_id=123)
print(f"No-show probability: {result.confidence:.2%}")

# Predict user churn
churn_result = await predictor.predict_user_churn(user_id=456)
print(f"Churn risk: {churn_result.prediction['probability']:.2%}")

# Forecast capacity needs
forecasts = await predictor.forecast_capacity_needs(forecast_days=7)
```

### 3. User Behavior Analytics (`user_behavior_analytics.py`)

Comprehensive user behavior analysis and segmentation.

**Features:**
- Cohort analysis and retention tracking
- User journey mapping
- Engagement metrics calculation
- Behavioral segmentation
- Feature usage analysis
- Temporal pattern analysis

**Key Classes:**
- `UserBehaviorAnalytics` - Main behavior analysis service
- `CohortData` - Cohort analysis results
- `UserJourney` - User journey tracking
- `EngagementMetrics` - User engagement scoring
- `BehavioralSegment` - User segmentation results

**Usage Example:**
```python
from app.services.analytics import UserBehaviorAnalytics

behavior_analytics = UserBehaviorAnalytics()

# Perform cohort analysis
cohorts = await behavior_analytics.perform_cohort_analysis(
    period_type='monthly',
    months_back=12
)

# Analyze user journeys
journeys = await behavior_analytics.analyze_user_journeys(limit=100)

# Calculate engagement metrics
engagement = await behavior_analytics.calculate_engagement_metrics()

# Segment users by behavior
segments = await behavior_analytics.segment_users_by_behavior()
```

### 4. Performance Metrics (`performance_metrics.py`)

KPI tracking and performance monitoring system.

**Features:**
- Business metrics tracking
- Operational metrics monitoring
- Technical performance metrics
- User experience metrics
- Alert generation and threshold monitoring
- Historical trend analysis

**Key Classes:**
- `PerformanceMetricsService` - Main metrics service
- `KPIMetric` - Individual metric structure
- `PerformanceDashboard` - Complete dashboard data
- `MetricAlert` - Alert configuration

**Tracked Metrics:**
- **Business**: MAU, retention rate, conversion rate, revenue per user
- **Operational**: Appointment completion rate, evaluation scores, staff utilization
- **Technical**: System uptime, response time, error rate, resource usage
- **User Experience**: Satisfaction score, page load time, support resolution time

**Usage Example:**
```python
from app.services.analytics import PerformanceMetricsService

performance_service = PerformanceMetricsService()

# Get performance dashboard
dashboard = await performance_service.get_performance_dashboard()

# Get specific metric history
history = await performance_service.get_metric_history('user_retention_rate', days=30)

# Export metrics report
report = await performance_service.export_metrics_report(
    start_date=datetime.utcnow() - timedelta(days=30),
    end_date=datetime.utcnow()
)
```

### 5. Custom Report Generator (`report_generator.py`)

Automated report generation with customizable templates.

**Features:**
- Multiple report templates (Executive, Operational, User Behavior, Performance)
- Multiple output formats (PDF, HTML, JSON, Excel, CSV)
- Automated insights generation
- Scheduled report generation
- Custom template creation

**Key Classes:**
- `CustomReportGenerator` - Main report service
- `ReportTemplate` - Template configuration
- `GeneratedReport` - Report output structure
- `ReportSchedule` - Scheduling configuration

**Available Templates:**
- **Executive Summary**: High-level KPIs and trends
- **Operational Analytics**: Detailed operational metrics
- **User Behavior Analysis**: Comprehensive behavior insights
- **Performance Metrics**: Technical and business performance

**Usage Example:**
```python
from app.services.analytics import CustomReportGenerator
from app.services.analytics.report_generator import ReportFormat

report_generator = CustomReportGenerator()

# Generate executive summary
report = await report_generator.generate_report(
    template_id='executive_summary',
    parameters={'period': 'monthly', 'include_charts': True},
    output_format=ReportFormat.PDF
)

# Generate custom report
custom_report = await report_generator.generate_report(
    template_id='user_behavior',
    parameters={'cohort_type': 'weekly', 'include_predictions': True}
)
```

### 6. Data Export & Visualization (`data_export.py`)

Multi-format data export and advanced visualization capabilities.

**Features:**
- Multiple export formats (CSV, JSON, Excel, Parquet, XML, YAML)
- Advanced data transformations and cleaning
- Interactive visualizations with Plotly
- Batch export capabilities
- Data quality scoring

**Key Classes:**
- `DataExportService` - Main export service
- `ExportRequest` - Export configuration
- `VisualizationConfig` - Chart configuration
- `ExportResult` - Export output details

**Supported Visualizations:**
- Line charts, bar charts, pie charts
- Scatter plots, heatmaps, histograms
- Box plots, area charts, gauge charts
- Treemaps and custom visualizations

**Usage Example:**
```python
from app.services.analytics import DataExportService
from app.services.analytics.data_export import ExportRequest, ExportFormat, VisualizationConfig, VisualizationType

export_service = DataExportService()

# Create export request
export_request = ExportRequest(
    export_id='monthly_user_export',
    data_sources=['users', 'appointments'],
    filters={'start_date': '2024-01-01', 'end_date': '2024-01-31'},
    format=ExportFormat.EXCEL,
    include_metadata=True
)

# Export data
result = await export_service.export_data(export_request)

# Create visualization
viz_config = VisualizationConfig(
    chart_type=VisualizationType.LINE_CHART,
    title='User Registration Trends',
    data_source='users',
    x_axis='registration_month',
    y_axis='count',
    filters={'start_date': '2024-01-01'},
    styling={'color': 'blue'},
    interactive=True
)

chart_path = await export_service.create_visualization(viz_config)
```

### 7. Analytics Orchestrator (`analytics_orchestrator.py`)

Central coordination service that manages all analytics components.

**Features:**
- Workflow orchestration and scheduling
- Service coordination and initialization
- Automated insight generation
- Alert handling and monitoring
- Custom workflow creation

**Key Classes:**
- `AnalyticsOrchestrator` - Main orchestration service
- `AnalyticsWorkflow` - Workflow configuration
- `WorkflowExecution` - Execution tracking
- `AnalyticsInsight` - Automated insights

**Default Workflows:**
- **Real-time Monitoring**: Continuous system monitoring
- **Daily Insights**: Daily analytics and recommendations
- **Weekly Reports**: Comprehensive weekly reports
- **Monthly Analytics**: Strategic monthly analysis

**Usage Example:**
```python
from app.services.analytics import AnalyticsOrchestrator

orchestrator = AnalyticsOrchestrator()

# Start orchestrator
await orchestrator.start_orchestrator()

# Get analytics summary
summary = await orchestrator.get_analytics_summary()

# Execute specific workflow
execution = await orchestrator.execute_workflow('daily_insights')

# Get insights
insights = await orchestrator.get_insights(category='Performance', priority='high')

# Create custom workflow
custom_workflow = await orchestrator.create_custom_workflow({
    'workflow_id': 'custom_analysis',
    'name': 'Custom Analysis',
    'components': ['user_behavior', 'predictive_analytics'],
    'schedule': 'weekly',
    'parameters': {'include_forecasts': True}
})
```

## Installation and Setup

### Prerequisites

```bash
pip install numpy pandas scikit-learn matplotlib seaborn plotly jinja2 sqlalchemy flask-socketio
```

### Database Models

The analytics system integrates with existing BDC models:
- `User` - User information and registration data
- `Beneficiary` - Beneficiary details and demographics
- `Appointment` - Appointment scheduling and status
- `Evaluation` - Assessment scores and results
- `UserActivity` - User interaction tracking

### Configuration

1. **Initialize Services**:
```python
from app.services.analytics import analytics_orchestrator

# Start the orchestrator (includes all services)
await analytics_orchestrator.start_orchestrator()
```

2. **WebSocket Integration**:
```python
# Add to your Flask app
from app.services.analytics.real_time_dashboard import socketio

socketio.init_app(app, cors_allowed_origins="*")
```

3. **Scheduled Tasks**:
```python
# Add to your Celery configuration
from app.services.analytics import analytics_orchestrator

@celery.task
def run_daily_analytics():
    asyncio.run(analytics_orchestrator.execute_workflow('daily_insights'))
```

## API Integration

### Flask Routes Example

```python
from flask import Blueprint, jsonify, request
from app.services.analytics import analytics_orchestrator

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/summary')
async def get_analytics_summary():
    summary = await analytics_orchestrator.get_analytics_summary()
    return jsonify(summary)

@analytics_bp.route('/analytics/insights')
async def get_insights():
    category = request.args.get('category')
    priority = request.args.get('priority')
    insights = await analytics_orchestrator.get_insights(category, priority)
    return jsonify([asdict(insight) for insight in insights])

@analytics_bp.route('/analytics/reports', methods=['POST'])
async def generate_report():
    data = request.get_json()
    report = await custom_report_generator.generate_report(
        template_id=data['template_id'],
        parameters=data.get('parameters', {}),
        output_format=ReportFormat(data.get('format', 'json'))
    )
    return jsonify(asdict(report))

@analytics_bp.route('/analytics/export', methods=['POST'])
async def export_data():
    data = request.get_json()
    export_request = ExportRequest(**data)
    result = await data_export_service.export_data(export_request)
    return jsonify(asdict(result))
```

### WebSocket Events

```javascript
// Connect to analytics namespace
const socket = io('/analytics');

// Listen for real-time updates
socket.on('analytics_update', (metrics) => {
    console.log('Received metrics:', metrics);
    updateDashboard(metrics);
});

// Request chart data
socket.emit('request_chart_data', {
    chart_type: 'line',
    metric_name: 'active_users',
    time_range: '24h'
});

// Handle chart data response
socket.on('chart_data_response', (response) => {
    if (response.success) {
        renderChart(response.data);
    }
});
```

## Performance Considerations

1. **Caching**: Metrics are cached for 15 minutes to reduce database load
2. **Batch Processing**: Large data exports are processed in batches
3. **Async Operations**: All heavy computations are asynchronous
4. **Memory Management**: DataFrames are optimized for memory efficiency
5. **Model Management**: ML models are retrained automatically when needed

## Monitoring and Alerts

The system includes comprehensive monitoring:

- **Health Checks**: Continuous service health monitoring
- **Performance Alerts**: Automated threshold-based alerting
- **Error Tracking**: Comprehensive error logging and tracking
- **Resource Monitoring**: Memory and CPU usage tracking

## Customization and Extension

### Adding New Metrics

```python
# Extend PerformanceMetricsService
class CustomMetricsService(PerformanceMetricsService):
    async def get_custom_metrics(self):
        # Add your custom metric logic
        return custom_metrics
```

### Creating Custom Reports

```python
# Add new report template
custom_template = ReportTemplate(
    template_id='custom_template',
    name='Custom Report',
    description='Custom analytics report',
    report_type=ReportType.CUSTOM,
    sections=['custom_section'],
    parameters={'custom_param': True},
    default_format=ReportFormat.HTML
)

report_generator.templates['custom_template'] = custom_template
```

### Adding New Visualizations

```python
# Extend DataExportService
class CustomVisualizationService(DataExportService):
    def create_custom_chart(self, df, config):
        # Add your custom visualization logic
        return custom_figure
```

## Best Practices

1. **Data Quality**: Always validate and clean data before analysis
2. **Performance**: Use appropriate sampling for large datasets
3. **Security**: Ensure sensitive data is properly anonymized
4. **Scalability**: Design for horizontal scaling from the start
5. **Documentation**: Keep analytics insights well-documented
6. **Testing**: Implement comprehensive testing for analytics components

## Troubleshooting

### Common Issues

1. **Memory Issues**: Reduce dataset size or increase memory allocation
2. **Slow Queries**: Add database indexes for analytics queries
3. **Model Performance**: Retrain models with more recent data
4. **WebSocket Disconnections**: Implement reconnection logic
5. **Export Failures**: Check file permissions and disk space

### Debugging

```python
# Enable debug logging
import logging
logging.getLogger('app.services.analytics').setLevel(logging.DEBUG)

# Check service status
status = await analytics_orchestrator.get_workflow_status('daily_insights')
print(status)

# Validate data quality
export_result = await data_export_service.export_data(export_request)
print(export_result.metadata['quality_metrics'])
```

## Future Enhancements

1. **Real-time ML**: Implement streaming ML for real-time predictions
2. **Advanced Visualizations**: Add more interactive chart types
3. **AI Insights**: Integrate natural language insights generation
4. **External Integrations**: Connect with external analytics platforms
5. **Mobile Dashboard**: Create mobile-optimized analytics interface
6. **Advanced Forecasting**: Implement time series forecasting models

This analytics system provides a comprehensive foundation for data-driven decision making in the BDC project, with the flexibility to grow and adapt to changing requirements.