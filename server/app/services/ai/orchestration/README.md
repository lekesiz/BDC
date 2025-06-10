# AI Pipeline Orchestration System

A comprehensive AI pipeline orchestration system for the BDC project that provides advanced workflow management, task coordination, model versioning, human-in-the-loop capabilities, intelligent caching, and comprehensive monitoring.

## Features

### 🔧 Pipeline Definition and Configuration
- **Flexible Pipeline Configuration**: Define pipelines using YAML, JSON, or Python dictionaries
- **Task Dependencies**: Support for complex task dependency graphs with automatic execution ordering
- **Multiple Task Types**: Built-in support for text generation, classification, extraction, validation, and custom tasks
- **Dynamic Parameter Injection**: Pass data between tasks and inject global parameters

### ⚡ Task Orchestration with Celery
- **Distributed Task Execution**: Leverage Celery for scalable, distributed task processing
- **Parallel and Sequential Execution**: Execute tasks in parallel within stages while respecting dependencies
- **Retry Logic**: Configurable retry policies with exponential backoff
- **Timeout Management**: Per-task timeout configuration with graceful handling
- **Task Result Tracking**: Comprehensive tracking of task status and results

### 📦 Model Versioning and Management
- **Model Registry**: Centralized registry for AI models with version tracking
- **Checksum Verification**: Automatic integrity checking with SHA256 checksums
- **Metadata Management**: Rich metadata support including performance metrics and tags
- **Version Comparison**: Compare different model versions with detailed diff reports
- **Default Version Management**: Set and manage default versions for each model

### 👥 Human-in-the-Loop Workflow
- **Review Request Management**: Create, assign, and track human review requests
- **Reviewer Profiles**: Manage reviewer capabilities, availability, and workload
- **Priority-based Assignment**: Intelligent assignment based on specialization and workload
- **Timeout and Escalation**: Configurable timeouts with escalation policies
- **Review History**: Complete audit trail of human review activities

### 💾 Result Caching and Optimization
- **Multi-level Caching**: Local and Redis-based caching with intelligent eviction
- **Cache Strategies**: Support for LRU, LFU, TTL, and adaptive caching strategies
- **Compression**: Multiple compression options (JSON, GZIP, Pickle) for storage efficiency
- **Cache Analytics**: Detailed statistics including hit rates and performance metrics
- **Automatic Optimization**: Background cleanup and optimization processes

### 📊 Monitoring and Logging
- **Real-time Metrics**: Track execution times, success rates, throughput, and error rates
- **Custom Alerts**: Configurable alert rules with multiple severity levels
- **System Health**: Comprehensive system health monitoring and reporting
- **Execution History**: Detailed logs of all pipeline executions
- **Performance Analytics**: Percentile-based performance analysis

## Quick Start

### 1. Installation and Setup

```python
from app.services.ai.orchestration import (
    PipelineOrchestrator, Pipeline, PipelineConfig,
    OrchestrationConfig
)
import redis
from celery import Celery

# Initialize configuration
config = OrchestrationConfig.from_env()

# Setup Redis and Celery
redis_client = redis.Redis(host=config.redis_host, port=config.redis_port)
celery_app = Celery('bdc_orchestration', broker=config.celery_broker_url)

# Initialize orchestrator
orchestrator = PipelineOrchestrator(
    celery_app=celery_app,
    redis_client=redis_client
)
```

### 2. Define a Pipeline

```python
# Using dictionary configuration
pipeline_config = {
    "name": "document_analysis",
    "description": "Analyze and extract information from documents",
    "version": "1.0.0",
    "tasks": [
        {
            "name": "extract_text",
            "type": "extraction",
            "model": "gpt-4",
            "parameters": {
                "schema": {
                    "title": "string",
                    "content": "string",
                    "entities": "list"
                }
            },
            "timeout": 300,
            "cache_enabled": True
        },
        {
            "name": "classify_document",
            "type": "classification",
            "model": "bert-base-uncased",
            "parameters": {
                "categories": ["legal", "financial", "technical"]
            },
            "dependencies": ["extract_text"],
            "timeout": 120
        }
    ],
    "cache_ttl": 3600,
    "enable_monitoring": True
}

# Create and register pipeline
pipeline = Pipeline(pipeline_config)
pipeline_id = orchestrator.register_pipeline(pipeline, "document_analysis")
```

### 3. Execute Pipeline

```python
# Prepare input data
input_data = {
    "document": {
        "content": "Your document content here...",
        "metadata": {"source": "upload", "user_id": "123"}
    }
}

# Execute pipeline asynchronously
execution_id = await orchestrator.execute_pipeline(
    pipeline_id="document_analysis",
    input_data=input_data
)

# Monitor execution
status = orchestrator.get_execution_status(execution_id)
print(f"Pipeline status: {status['status']}")
```

### 4. Model Version Management

```python
# Register a new model version
version_manager = orchestrator.version_manager

model_version = version_manager.register_model(
    model_name="custom_classifier",
    version="v2.1.0",
    model_path="/path/to/model",
    metadata={
        "description": "Enhanced classification model",
        "accuracy": 0.95,
        "training_data": "dataset_v2.1"
    },
    tags=["classification", "production"],
    set_as_default=True
)

# Get model for use
model_info = version_manager.get_model_version("custom_classifier", "v2.1.0")
```

### 5. Human-in-the-Loop

```python
# Register reviewers
from app.services.ai.orchestration.human_loop import ReviewerProfile

reviewer = ReviewerProfile(
    id="expert_001",
    name="Dr. Jane Smith",
    email="jane@example.com",
    specializations=["legal", "compliance"],
    max_concurrent_reviews=5
)

hitl_manager = orchestrator.human_loop_manager
hitl_manager.register_reviewer(reviewer)

# Create review request
review_id = hitl_manager.create_review(
    task_name="legal_validation",
    task_type="validation",
    input_data={"document": "contract.pdf", "extracted_terms": [...]},
    priority="high"
)
```

### 6. Monitoring and Alerts

```python
# Setup custom alert rules
from app.services.ai.orchestration.monitoring import AlertRule, AlertSeverity

alert_rule = AlertRule(
    name="High Error Rate Alert",
    metric_name="error_rate",
    operator=">",
    threshold=0.1,  # 10%
    severity=AlertSeverity.WARNING,
    message_template="Pipeline {pipeline} error rate: {current_value:.2%}"
)

monitor = orchestrator.monitor
monitor.add_alert_rule("document_analysis", alert_rule)

# Get system health
health = monitor.get_system_health()
print(f"System success rate: {health['overall_success_rate']:.2%}")
```

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_WORKER_CONCURRENCY=4

# Model Registry
MODEL_REGISTRY_PATH=/var/lib/bdc/models

# Cache Configuration
CACHE_DEFAULT_TTL=3600
CACHE_MAX_SIZE=1000000
CACHE_STRATEGY=lru

# Monitoring
MONITORING_ENABLED=true
METRICS_RETENTION_DAYS=7

# Human-in-the-Loop
HITL_DEFAULT_TIMEOUT_HOURS=24

# Execution
MAX_PARALLEL_TASKS=5
DEFAULT_TASK_TIMEOUT=300
```

### Pipeline Configuration Examples

#### YAML Configuration
```yaml
name: content_generation
description: Generate and refine content
version: 1.0.0
tasks:
  - name: generate_draft
    type: text_generation
    model: gpt-4
    parameters:
      max_tokens: 2000
      temperature: 0.7
    timeout: 300
    cache_enabled: true
  
  - name: refine_content
    type: text_generation
    model: gpt-4
    parameters:
      prompt_template: "Refine: {generate_draft_output.text}"
      temperature: 0.5
    dependencies: [generate_draft]
    timeout: 300

global_parameters:
  output_mapping:
    final_content: refine_content_output.text
cache_ttl: 1800
enable_monitoring: true
```

## Advanced Features

### Custom Task Handlers

```python
def custom_analysis_task(task_config, input_data, context):
    """Custom task implementation."""
    # Your custom logic here
    result = perform_analysis(input_data)
    
    return {
        "analysis_result": result,
        "confidence": 0.95,
        "metadata": {"processing_time": 123}
    }

# Register custom handler
orchestrator.task_manager.task.register_task_handler(
    "custom_analysis", 
    custom_analysis_task
)
```

### Pipeline Callbacks

```python
def on_pipeline_complete(execution):
    """Handle pipeline completion."""
    print(f"Pipeline {execution.pipeline_name} completed: {execution.status}")
    
    if execution.status == "completed":
        # Send notification, update database, etc.
        send_completion_notification(execution)

def on_pipeline_error(execution):
    """Handle pipeline errors."""
    print(f"Pipeline {execution.pipeline_name} failed: {execution.error}")
    
    # Log error, send alert, etc.
    log_pipeline_error(execution)

# Register callbacks
orchestrator.add_completion_callback(on_pipeline_complete)
orchestrator.add_error_callback(on_pipeline_error)
```

### Cache Optimization

```python
# Custom cache key generation
def generate_cache_key(pipeline_name, input_data):
    import hashlib
    key_data = f"{pipeline_name}:{input_data.get('key_field')}"
    return hashlib.md5(key_data.encode()).hexdigest()

# Cache with custom TTL and tags
cache = orchestrator.cache
cache.set(
    key=generate_cache_key("analysis", input_data),
    value=result,
    ttl=7200,  # 2 hours
    tags=["analysis", "high_priority"]
)

# Bulk cache operations
cache.delete_by_tags(["expired", "low_priority"])
```

## Monitoring and Analytics

### Metrics Available
- **Execution Metrics**: Count, success rate, execution times, throughput
- **Performance Metrics**: Min/max/average execution times, percentiles
- **Error Metrics**: Error rate, failure patterns, retry statistics
- **Resource Metrics**: Cache hit rates, model usage, reviewer workload

### Alert Types
- **Performance Alerts**: Long execution times, low throughput
- **Error Alerts**: High error rates, specific failure patterns
- **Resource Alerts**: Cache misses, model unavailability
- **Business Alerts**: SLA violations, review timeouts

### Health Checks
- System uptime and availability
- Pipeline health status
- Model availability and performance
- Cache efficiency metrics
- Human reviewer availability

## Production Deployment

### Docker Configuration

```dockerfile
# Dockerfile for orchestration service
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Environment setup
ENV PYTHONPATH=/app
ENV CELERY_WORKER_CONCURRENCY=4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import redis; redis.Redis(host='redis').ping()"

CMD ["celery", "worker", "-A", "app.services.ai.orchestration.tasks", "--loglevel=info"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  celery-worker:
    build: .
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - CELERY_BROKER_URL=redis://redis:6379/1
    volumes:
      - ./models:/var/lib/bdc/models
  
  orchestrator:
    build: .
    depends_on:
      - redis
      - celery-worker
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
```

### Scaling Considerations

1. **Horizontal Scaling**: Add more Celery workers for increased throughput
2. **Redis Clustering**: Use Redis cluster for high availability
3. **Model Registry**: Use distributed storage for model files
4. **Monitoring**: Implement distributed tracing and metrics collection
5. **Load Balancing**: Distribute pipeline executions across workers

## Troubleshooting

### Common Issues

1. **Task Timeouts**: Increase timeout values or optimize task implementation
2. **Memory Issues**: Enable result compression and limit concurrent tasks
3. **Cache Misses**: Review cache key generation and TTL settings
4. **Alert Noise**: Adjust alert thresholds and cooldown periods

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed monitoring
orchestrator.monitor.monitoring_active = True

# Check task execution details
status = orchestrator.get_execution_status(execution_id)
print(json.dumps(status, indent=2))
```

### Performance Optimization

1. **Cache Strategy**: Choose appropriate caching strategy for your workload
2. **Task Batching**: Group related tasks for efficiency
3. **Model Optimization**: Use appropriate model versions for tasks
4. **Resource Monitoring**: Monitor CPU, memory, and I/O usage

## Contributing

To contribute to the orchestration system:

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure backward compatibility
5. Test with real-world scenarios

## License

This orchestration system is part of the BDC project and follows the project's licensing terms.