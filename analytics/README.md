# BDC Automated Log Analytics

## Overview

The BDC Automated Log Analytics system provides intelligent analysis of application logs using machine learning techniques to detect patterns, anomalies, and trends. It automatically identifies issues, generates insights, and provides actionable recommendations for system optimization and security enhancement.

## 🧠 Features

### Intelligent Pattern Detection
- **Error Pattern Analysis**: Groups similar errors using TF-IDF and DBSCAN clustering
- **Performance Trend Analysis**: Monitors response times and database performance
- **Security Incident Detection**: Identifies authentication failures and suspicious activities
- **Usage Pattern Analysis**: Tracks user activity and API usage patterns
- **Anomaly Detection**: Uses statistical methods and topic modeling to find unusual patterns

### Machine Learning Capabilities
- **TF-IDF Vectorization**: Text analysis for error message similarity
- **DBSCAN Clustering**: Groups similar log entries automatically
- **Latent Dirichlet Allocation**: Topic modeling for pattern discovery
- **Statistical Anomaly Detection**: Z-score based outlier detection
- **Time Series Analysis**: Trend detection and forecasting

### Real-time Analytics
- **Background Processing**: Continuous analysis every 5 minutes
- **Automated Alerting**: Integration with alert system for critical findings
- **Correlation Tracking**: Links related log entries across services
- **Performance Monitoring**: Real-time response time and error rate tracking

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                BDC Log Analytics Architecture               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    ELK      │    │   Flask     │    │   Redis     │     │
│  │   Stack     │    │Application  │    │   Cache     │     │
│  │(Log Storage)│    │   Logs      │    │ (Results)   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                    │                    │        │
│         └────────────────────┼────────────────────┘        │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │  Log Analytics    │                   │
│                    │     Service       │                   │
│                    │ (ML Processing)   │                   │
│                    └─────────┬─────────┘                   │
│                              │                             │
│         ┌────────────────────┼────────────────────┐        │
│         │                    │                    │        │
│  ┌──────▼──────┐    ┌────────▼────────┐    ┌──────▼──────┐ │
│  │ Pattern     │    │   Anomaly       │    │   Alert     │ │
│  │ Detection   │    │  Detection      │    │  Service    │ │
│  └─────────────┘    └─────────────────┘    └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
analytics/
├── server/app/
│   ├── services/
│   │   └── log_analytics_service.py    # Core analytics engine
│   └── api/routes/
│       └── analytics.py                # Analytics API endpoints
├── client/src/components/admin/
│   └── LogAnalytics.jsx               # React analytics dashboard
└── README.md                          # This file
```

## 🚀 Quick Start

### 1. Environment Configuration

Add to your `.env` file:

```bash
# Log Analytics
LOG_ANALYTICS_ENABLED=true
LOG_ANALYSIS_INTERVAL=300
LOG_RETENTION_DAYS=30
MIN_PATTERN_FREQUENCY=5
ANOMALY_THRESHOLD=2.0

# Machine Learning
ML_ERROR_CLUSTERING_ENABLED=true
ML_TOPIC_MODELING_ENABLED=true
ML_ANOMALY_DETECTION_ENABLED=true

# Performance Thresholds
ANALYTICS_RESPONSE_TIME_WARNING=2000
ANALYTICS_RESPONSE_TIME_CRITICAL=5000
ANALYTICS_ERROR_RATE_WARNING=0.1
ANALYTICS_ERROR_RATE_CRITICAL=0.2

# Security Analytics
SECURITY_ANALYTICS_ENABLED=true
BRUTE_FORCE_THRESHOLD=10
SUSPICIOUS_ACTIVITY_THRESHOLD=5
```

### 2. Access Analytics Dashboard

- **Analytics Dashboard**: http://localhost:5173/admin/analytics
- **API Endpoints**: http://localhost:5000/api/analytics/*

### 3. Dependencies

The analytics service requires:
- **Elasticsearch**: For log storage and querying
- **Redis**: For caching analysis results
- **Scikit-learn**: For machine learning algorithms
- **Pandas/NumPy**: For data processing

## 📊 Analysis Types

### 1. Error Pattern Analysis

Automatically groups similar errors and identifies recurring issues:

```python
# Triggered automatically every 5 minutes
results = log_analytics_service.analyze_error_patterns(time_window=3600)

# Manual analysis via API
GET /api/analytics/logs/patterns?type=error_pattern&hours=1
```

**Features:**
- TF-IDF vectorization of error messages
- DBSCAN clustering for grouping similar errors
- Frequency analysis and impact assessment
- Automated recommendations for error resolution

### 2. Performance Trend Analysis

Monitors system performance metrics and identifies bottlenecks:

```python
# Analyze response times and database performance
results = log_analytics_service.analyze_performance_trends(time_window=3600)
```

**Metrics Tracked:**
- API response times (avg, p95, p99)
- Database query performance
- Cache hit/miss rates
- Error rates by endpoint

### 3. Security Incident Detection

Identifies potential security threats and suspicious activities:

```python
# Detect authentication failures and security incidents
results = log_analytics_service.analyze_security_incidents(time_window=3600)
```

**Security Indicators:**
- Failed authentication attempts
- Brute force attack patterns
- Suspicious IP activities
- Privilege escalation attempts
- Data access anomalies

### 4. Usage Pattern Analysis

Analyzes user behavior and API usage patterns:

```python
# Analyze user activity and API usage
results = log_analytics_service.analyze_usage_patterns(time_window=86400)
```

**Pattern Types:**
- User activity trends
- API endpoint usage
- Peak traffic times
- Geographic access patterns

### 5. Anomaly Detection

Uses statistical methods to detect unusual patterns:

```python
# Detect volume and pattern anomalies
results = log_analytics_service.detect_anomalies(time_window=3600)
```

**Anomaly Types:**
- Log volume spikes/drops
- Unusual error patterns
- Performance degradation
- Security anomalies

## 🔧 API Endpoints

### Get Insights

```bash
GET /api/analytics/logs/insights?hours=24&min_severity=medium

Response:
{
  "success": true,
  "data": {
    "insights": [...],
    "summary": {
      "total_insights": 15,
      "severity_distribution": {...}
    }
  }
}
```

### Search Logs

```bash
POST /api/analytics/logs/search
{
  "query": "database error",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T23:59:59Z",
  "log_levels": ["ERROR", "CRITICAL"],
  "max_results": 1000
}
```

### Get Trends

```bash
GET /api/analytics/logs/trends?days=7&granularity=hour

Response:
{
  "success": true,
  "data": {
    "trends": [...],
    "summary": {
      "total_logs": 50000,
      "error_rate": 2.5
    }
  }
}
```

### Export Logs

```bash
POST /api/analytics/logs/export
{
  "format": "csv",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T23:59:59Z"
}
```

### Run Pattern Analysis

```bash
GET /api/analytics/logs/patterns?type=security_incident&hours=1
```

## 🎯 Dashboard Features

### Insights Tab
- **Real-time Insights**: Latest analysis results with severity indicators
- **Filtering**: By time window, severity, and analysis type
- **Recommendations**: Actionable suggestions for each insight
- **Confidence Scores**: ML model confidence for each analysis

### Trends Tab
- **Interactive Charts**: Line charts and bar charts for trend visualization
- **Time Range Selection**: Hourly or daily granularity
- **Log Level Distribution**: Visual breakdown by severity
- **Performance Metrics**: Response time and error rate trends

### Search Tab
- **Advanced Search**: Query logs with multiple filters
- **Export Options**: JSON and CSV export formats
- **Real-time Results**: Live search with syntax highlighting
- **Correlation Tracking**: Link related log entries

### Pattern Analysis Tab
- **On-demand Analysis**: Trigger specific analysis types
- **Interactive Results**: Drill down into analysis details
- **Historical Comparisons**: Compare current vs. historical patterns

## 🔬 Machine Learning Models

### TF-IDF Vectorizer
```python
tfidf_vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 3)
)
```

**Purpose**: Convert log messages to numerical vectors for similarity analysis

### DBSCAN Clustering
```python
clustering_model = DBSCAN(
    eps=0.3, 
    min_samples=5
)
```

**Purpose**: Group similar error messages automatically

### Latent Dirichlet Allocation
```python
topic_model = LatentDirichletAllocation(
    n_components=10, 
    random_state=42
)
```

**Purpose**: Discover hidden topics in log messages

### Statistical Anomaly Detection
```python
# Z-score based anomaly detection
z_score = abs(value - mean) / std_dev
is_anomaly = z_score > threshold  # Default: 2.0
```

**Purpose**: Identify statistical outliers in log patterns

## 📈 Performance Monitoring

### Response Time Analysis

The system automatically monitors:
- API endpoint response times
- Database query performance
- External service call latency
- Cache operation times

**Thresholds:**
- **Warning**: > 2 seconds average response time
- **Critical**: > 5 seconds average response time

### Error Rate Monitoring

Tracks error rates across:
- HTTP status codes (4xx, 5xx)
- Application errors by component
- Database connection errors
- Authentication failures

**Thresholds:**
- **Warning**: > 10% error rate
- **Critical**: > 20% error rate

## 🔒 Security Analytics

### Authentication Analysis

Monitors for:
- Failed login attempts
- Brute force attack patterns
- Suspicious IP addresses
- Account lockout events

**Detection Logic:**
```python
# Brute force detection
if failed_attempts_from_ip > BRUTE_FORCE_THRESHOLD:
    trigger_security_alert("Potential brute force attack")
```

### Suspicious Activity Detection

Identifies:
- Unusual access patterns
- Privilege escalation attempts
- Data exfiltration indicators
- Malicious request patterns

**Security Indicators:**
- SQL injection attempts
- XSS attack patterns
- Command injection tries
- Unusual user agent strings

## 🚨 Automated Alerting

### Alert Integration

Analysis results automatically trigger alerts for:
- **Critical Errors**: Recurring error patterns
- **Performance Issues**: Slow response times
- **Security Incidents**: Attack patterns
- **System Anomalies**: Unusual behavior

### Alert Severity Mapping

```python
# Severity determination logic
if error_count > 50 or critical_errors > 0:
    severity = AlertSeverity.CRITICAL
elif error_count > 20:
    severity = AlertSeverity.HIGH
elif error_count > 10:
    severity = AlertSeverity.MEDIUM
else:
    severity = AlertSeverity.LOW
```

### Recommendation Engine

Generates actionable recommendations based on analysis:

```python
def generate_recommendations(analysis_result):
    recommendations = []
    
    if 'database' in error_pattern:
        recommendations.append("Check database connectivity")
        recommendations.append("Review query performance")
    
    if 'timeout' in error_pattern:
        recommendations.append("Increase timeout values")
        recommendations.append("Check for blocking operations")
    
    return recommendations
```

## 🔧 Configuration

### Analysis Intervals

```bash
# Background analysis frequency
LOG_ANALYSIS_INTERVAL=300  # 5 minutes

# Data retention
LOG_RETENTION_DAYS=30

# Pattern detection sensitivity
MIN_PATTERN_FREQUENCY=5
ANOMALY_THRESHOLD=2.0
```

### Machine Learning Tuning

```bash
# Enable/disable ML features
ML_ERROR_CLUSTERING_ENABLED=true
ML_TOPIC_MODELING_ENABLED=true
ML_ANOMALY_DETECTION_ENABLED=true

# Clustering parameters
DBSCAN_EPS=0.3
DBSCAN_MIN_SAMPLES=5

# Topic modeling
LDA_TOPICS=10
LDA_RANDOM_STATE=42
```

### Performance Thresholds

```bash
# Response time thresholds (milliseconds)
ANALYTICS_RESPONSE_TIME_WARNING=2000
ANALYTICS_RESPONSE_TIME_CRITICAL=5000

# Error rate thresholds (percentage)
ANALYTICS_ERROR_RATE_WARNING=0.1
ANALYTICS_ERROR_RATE_CRITICAL=0.2
```

## 🛠️ Troubleshooting

### Common Issues

#### Analytics Service Not Starting

```bash
# Check dependencies
pip install elasticsearch redis scikit-learn pandas numpy

# Check connections
curl http://localhost:9200/_cluster/health
redis-cli ping
```

#### No Analysis Results

```bash
# Check if logs are being indexed
curl "http://localhost:9200/bdc-*/_search?size=1"

# Check analysis status
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/analytics/status
```

#### Performance Issues

```bash
# Reduce analysis frequency
export LOG_ANALYSIS_INTERVAL=600  # 10 minutes

# Limit log processing
export MAX_LOGS_PER_ANALYSIS=10000

# Disable expensive ML features
export ML_TOPIC_MODELING_ENABLED=false
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export LOG_ANALYTICS_DEBUG=true

# Check service logs
docker logs bdc-backend | grep -i analytics
```

## 📊 Metrics and KPIs

### Analysis Metrics

- **Patterns Detected**: Number of patterns found per analysis
- **Anomalies Found**: Count of anomalies detected
- **Analysis Latency**: Time taken for each analysis type
- **Accuracy Scores**: ML model confidence scores

### System Health Metrics

- **Analysis Success Rate**: Percentage of successful analyses
- **Processing Time**: Average time per log entry
- **Memory Usage**: Analytics service memory consumption
- **Cache Hit Rate**: Redis cache effectiveness

### Business Impact Metrics

- **MTTR Reduction**: Mean time to resolution improvement
- **Issue Prevention**: Proactive issue identification
- **Security Incident Response**: Faster threat detection
- **Performance Optimization**: System efficiency gains

## 🚀 Production Deployment

### Resource Requirements

```yaml
# Minimum requirements
CPU: 2 cores
Memory: 4GB RAM
Storage: 10GB (for ML models and cache)

# Recommended for production
CPU: 4 cores
Memory: 8GB RAM
Storage: 50GB
```

### Scaling Considerations

- **Horizontal Scaling**: Multiple analytics workers
- **Data Partitioning**: Time-based log partitioning
- **Cache Strategy**: Distributed Redis cluster
- **ML Model Updates**: Periodic model retraining

### Monitoring Setup

```bash
# Analytics service health
curl http://localhost:5000/api/analytics/status

# Elasticsearch health
curl http://localhost:9200/_cluster/health

# Redis health
redis-cli info memory
```

## 📞 Support

### Health Check Commands

```bash
# Service status
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/analytics/status

# Recent insights
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:5000/api/analytics/logs/insights?hours=1"

# Run manual analysis
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:5000/api/analytics/logs/patterns?type=error_pattern"
```

### Log Analysis

```bash
# Check analytics service logs
docker logs bdc-backend | grep "log_analytics"

# Monitor analysis performance
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:5000/api/analytics/logs/trends?days=1"
```