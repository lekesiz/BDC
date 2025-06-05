# BDC Distributed Tracing with Jaeger

## Overview

The BDC Distributed Tracing system provides comprehensive observability across the entire application stack using Jaeger and OpenTelemetry. This enables end-to-end request tracing, performance monitoring, and debugging across microservices.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                BDC Distributed Tracing                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   React     │    │   Flask     │    │  Database   │     │
│  │  Frontend   │    │  Backend    │    │  Queries    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                    │                    │        │
│         │                    │                    │        │
│  ┌──────▼──────┐    ┌────────▼────────┐    ┌──────▼──────┐ │
│  │OpenTelemetry│    │OpenTelemetry    │    │SQLAlchemy   │ │
│  │Web SDK      │    │Python SDK       │    │Tracing      │ │
│  └─────────────┘    └─────────────────┘    └─────────────┘ │
│         │                    │                    │        │
│         └────────────────────┼────────────────────┘        │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │  OTLP Collector   │                   │
│                    │  (Aggregation)    │                   │
│                    └─────────┬─────────┘                   │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │     Jaeger        │                   │
│                    │   (Storage &      │                   │
│                    │   Visualization)  │                   │
│                    └───────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
tracing/
├── jaeger/
│   └── config/
│       ├── ui-config.json             # Jaeger UI configuration
│       └── sampling_strategies.json   # Sampling strategies
├── otel/
│   └── config/
│       └── otel-collector-config.yml  # OpenTelemetry Collector config
├── server/app/
│   ├── services/
│   │   └── tracing_service.py         # Backend tracing service
│   └── middleware/
│       └── tracing_middleware.py      # Flask tracing middleware
├── client/src/
│   ├── services/
│   │   └── tracing.js                 # Frontend tracing service
│   └── hooks/
│       └── useTracing.js              # React tracing hooks
├── scripts/
│   └── deploy-jaeger-tracing.sh       # Deployment script
└── README.md                          # This file
```

## 🚀 Quick Start

### 1. Deploy Tracing Stack

```bash
# Basic Jaeger deployment
./scripts/deploy-jaeger-tracing.sh

# With ELK integration for log correlation
./scripts/deploy-jaeger-tracing.sh --with-elk

# Full observability stack
./scripts/deploy-jaeger-tracing.sh --with-elk --with-monitoring
```

### 2. Access Jaeger UI

- **Jaeger UI**: http://localhost:16686
- **OTLP gRPC**: localhost:4317
- **OTLP HTTP**: localhost:4318

### 3. Environment Configuration

Add to your `.env` file:

```bash
# Distributed Tracing
TRACING_ENABLED=true
TRACING_SAMPLE_RATE=1.0
OTEL_SERVICE_NAME=bdc-backend
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# Frontend Tracing
VITE_TRACING_ENABLED=true
VITE_TRACING_SAMPLE_RATE=0.1
VITE_OTEL_ENDPOINT=http://localhost:4318/v1/traces
```

## 💻 Backend Integration

### Basic Usage

```python
from app.services.tracing_service import trace_function, trace_database_operation

@trace_function("user_authentication")
def authenticate_user(email, password):
    # Function automatically traced
    return user

@trace_database_operation("select", "users")
def get_user_by_email(email):
    # Database query automatically traced
    return db.session.query(User).filter_by(email=email).first()
```

### Manual Span Creation

```python
from app.services.tracing_service import tracing_service

def complex_operation():
    with tracing_service.trace_operation("complex_business_logic") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("operation.type", "business_logic")
        
        # Your business logic here
        result = process_data()
        
        span.set_attribute("result.count", len(result))
        return result
```

### Correlation ID Management

```python
from app.services.tracing_service import get_correlation_id, set_correlation_id

# Get current correlation ID
correlation_id = get_correlation_id()

# Set correlation ID (automatically propagated)
set_correlation_id("custom_correlation_id")
```

### Flask Middleware Integration

The tracing middleware automatically:
- Creates spans for HTTP requests
- Extracts/injects correlation IDs
- Adds user context to spans
- Records performance metrics
- Handles error propagation

## 🌐 Frontend Integration

### React Hooks

```javascript
import { useTracing, usePageTracing, useApiTracing } from '../hooks/useTracing';

function MyComponent() {
  const { trace, traceAsync, traceAction } = useTracing('MyComponent');
  const { traceApiCall } = useApiTracing();
  
  // Trace page load
  usePageTracing('dashboard');
  
  const handleClick = () => {
    traceAction('button_click', {
      buttonId: 'submit-btn',
      buttonText: 'Submit'
    });
  };
  
  const fetchData = async () => {
    return traceApiCall('GET', '/api/users', null, {
      operation: 'fetch_users'
    });
  };
  
  const processData = () => {
    return trace('data_processing', () => {
      // Your processing logic
      return processedData;
    });
  };
}
```

### Manual Tracing

```javascript
import tracingService, { traceOperation, traceError } from '../services/tracing';

// Trace operation
const result = await traceOperation(
  'user_action',
  async (span) => {
    span.setAttributes({
      'action.type': 'form_submit',
      'form.name': 'user_registration'
    });
    
    return await submitForm(formData);
  }
);

// Trace errors
try {
  await riskyOperation();
} catch (error) {
  traceError(error, {
    component: 'UserForm',
    operation: 'submit'
  });
  throw error;
}
```

## 📊 Sampling Strategies

### Intelligent Sampling

The system uses intelligent sampling to balance observability with performance:

```json
{
  "per_service_strategies": [
    {
      "service": "bdc-backend",
      "type": "probabilistic",
      "param": 1.0,
      "operation_strategies": [
        {
          "operation": "GET /health",
          "param": 0.1
        },
        {
          "operation": "POST /api/auth/login",
          "param": 1.0
        },
        {
          "operation": "database_query",
          "param": 0.8
        }
      ]
    }
  ]
}
```

### Sampling Rules

- **Health checks**: 1% sampling (reduce noise)
- **Authentication**: 100% sampling (critical path)
- **Database queries**: 80% sampling (performance monitoring)
- **API endpoints**: 50% sampling (general monitoring)
- **Errors**: 100% sampling (always trace errors)
- **Slow operations**: 100% sampling (performance issues)

## 🔗 Correlation and Context Propagation

### Request Correlation

Each request gets a unique correlation ID that follows the request through:

1. **Frontend** → generates correlation ID
2. **API Gateway** → extracts and forwards
3. **Backend Services** → propagates through all operations
4. **Database** → includes in query spans
5. **External APIs** → injects in outgoing requests

### Context Propagation

```javascript
// Frontend: Inject headers
const headers = tracingService.injectHeaders({
  'Content-Type': 'application/json'
});

fetch('/api/users', { headers });
```

```python
# Backend: Extract context
headers = dict(request.headers)
context = tracing_service.extract_headers(headers)

# Propagate to external service
external_headers = tracing_service.inject_headers()
requests.get('https://external-api.com', headers=external_headers)
```

## 🎯 Trace Analysis

### Finding Traces

1. **By Service**: Filter by `bdc-backend`, `bdc-frontend`
2. **By Operation**: Search for specific endpoints or functions
3. **By User**: Filter by `user.id` tag
4. **By Correlation ID**: Direct lookup by correlation ID
5. **By Error**: Filter traces with errors

### Key Metrics

- **Request Duration**: End-to-end response time
- **Database Time**: Time spent in database operations
- **External API Time**: Time spent calling external services
- **Queue Time**: Time spent waiting
- **Error Rate**: Percentage of failed operations

### Performance Analysis

```bash
# Find slow traces
curl "http://localhost:16686/api/traces?service=bdc-backend&minDuration=5s"

# Find error traces
curl "http://localhost:16686/api/traces?service=bdc-backend&tags={\"error\":\"true\"}"

# Find user activity
curl "http://localhost:16686/api/traces?service=bdc-backend&tags={\"user.id\":\"123\"}"
```

## 🔧 Advanced Configuration

### Custom Instrumentations

```python
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Custom Flask instrumentation
FlaskInstrumentor().instrument_app(app, 
    request_hook=custom_request_hook,
    response_hook=custom_response_hook
)

def custom_request_hook(span, environ):
    span.set_attribute("custom.request_id", generate_request_id())

def custom_response_hook(span, status, response_headers):
    span.set_attribute("custom.response_size", len(response_headers))
```

### Performance Monitoring

```python
from app.middleware.tracing_middleware import monitor_performance

@monitor_performance(warning_threshold=2.0, critical_threshold=5.0)
def slow_operation():
    # Will alert and trace if operation is slow
    time.sleep(3)
```

### Error Correlation

Errors are automatically correlated with:
- Request traces
- User context
- System state
- Previous operations

## 🔍 Integration with Other Systems

### ELK Stack Integration

Traces are correlated with logs using:
- **Correlation ID**: Links traces to log entries
- **Request ID**: Connects related log messages
- **User ID**: Associates with user activity

```bash
# Find logs for a trace
curl "http://localhost:5601/api/console/proxy?path=_search&method=GET" \
  -d '{"query":{"match":{"correlation_id":"trace_correlation_id"}}}'
```

### Grafana Integration

Jaeger can be added as a data source in Grafana:

```yaml
datasources:
  - name: Jaeger
    type: jaeger
    url: http://jaeger:16686
    access: proxy
```

### Alerting Integration

```python
from app.services.alert_service import send_performance_alert

def trace_with_alerting(operation_name):
    with tracing_service.trace_operation(operation_name) as span:
        start_time = time.time()
        
        try:
            result = operation()
            duration = time.time() - start_time
            
            if duration > 5.0:
                send_performance_alert(
                    title=f"Slow operation: {operation_name}",
                    message=f"Operation took {duration:.2f}s",
                    correlation_id=get_correlation_id()
                )
            
            return result
        except Exception as e:
            span.record_exception(e)
            raise
```

## 📈 Monitoring and Metrics

### Jaeger Metrics

Jaeger exposes metrics on port 14269:

```bash
# Jaeger internal metrics
curl http://localhost:14269/metrics

# Trace count by service
curl "http://localhost:16686/api/traces?service=bdc-backend&lookback=1h" | jq '.data | length'
```

### Custom Metrics

```python
from app.services.tracing_service import tracing_service

# Record custom metrics
tracing_service.record_request_metrics(
    method="POST",
    endpoint="/api/users",
    status_code=201,
    duration=0.5
)

tracing_service.record_database_metrics(
    operation="insert",
    table="users", 
    duration=0.1,
    success=True
)
```

## 🛠️ Troubleshooting

### Common Issues

#### No Traces Appearing

```bash
# Check if tracing is enabled
echo $TRACING_ENABLED

# Check Jaeger health
curl http://localhost:16686/api/services

# Check OTLP endpoint
curl -X POST -H "Content-Type: application/json" \
  -d '{"resourceSpans":[]}' \
  http://localhost:4318/v1/traces
```

#### High Memory Usage

```bash
# Reduce sampling rate
export TRACING_SAMPLE_RATE=0.1

# Limit trace retention
export JAEGER_MEMORY_MAX_TRACES=10000

# Check memory usage
docker stats bdc-jaeger
```

#### Slow Performance

```bash
# Enable batch processing
export OTEL_BSP_MAX_QUEUE_SIZE=2048
export OTEL_BSP_EXPORT_BATCH_SIZE=512

# Reduce sampling for high-volume operations
# Edit sampling_strategies.json
```

### Debug Mode

```bash
# Enable debug logging
export OTEL_LOG_LEVEL=debug
export JAEGER_LOG_LEVEL=debug

# Check collector logs
docker logs bdc-otel-collector

# Check Jaeger logs
docker logs bdc-jaeger
```

## 🚀 Production Deployment

### Environment Checklist

- [ ] `TRACING_ENABLED=true`
- [ ] `OTEL_SERVICE_NAME` set for each service
- [ ] `OTEL_EXPORTER_OTLP_ENDPOINT` configured
- [ ] Sampling rates appropriate for traffic volume
- [ ] Resource limits set for Jaeger and OTLP collector
- [ ] Storage configured (for non-memory storage)

### Performance Tuning

```bash
# Jaeger configuration
JAEGER_MEMORY_MAX_TRACES=100000
JAEGER_STORAGE_TYPE=elasticsearch  # For production

# OTLP Collector configuration  
OTEL_MEMORY_LIMIT=1G
OTEL_CPU_LIMIT=1.0

# Sampling configuration
TRACING_SAMPLE_RATE=0.1  # 10% sampling for production
```

### Scaling Considerations

- **High Traffic**: Use probabilistic sampling
- **Critical Services**: Higher sampling rates
- **Background Jobs**: Lower sampling rates
- **Storage**: Use Elasticsearch or Cassandra for production
- **Retention**: Configure appropriate data retention policies

## 📞 Support

### Health Checks

```bash
# Jaeger health
curl http://localhost:14269/

# OTLP Collector health
curl http://localhost:13133/

# Service discovery
curl http://localhost:16686/api/services
```

### Useful Queries

```bash
# All services
curl "http://localhost:16686/api/services"

# Recent traces
curl "http://localhost:16686/api/traces?service=bdc-backend&lookback=1h"

# Error traces
curl "http://localhost:16686/api/traces?service=bdc-backend&tags={\"error\":\"true\"}"

# Slow traces
curl "http://localhost:16686/api/traces?service=bdc-backend&minDuration=5s"
```

### Integration Testing

```bash
# Test trace generation
./scripts/test-tracing.sh

# Generate sample traces
curl -X POST http://localhost:5000/api/test/trace
```