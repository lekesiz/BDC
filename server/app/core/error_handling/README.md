# Comprehensive Error Handling System

A robust, production-ready error handling system for the BDC project that provides centralized error management, fault tolerance patterns, monitoring, and user-friendly error messages.

## Features

- **Centralized Error Management**: Unified error classification, logging, and handling
- **Circuit Breaker Pattern**: Fault tolerance for external services and dependencies
- **Retry Mechanisms**: Configurable retry strategies with exponential backoff and jitter
- **Error Monitoring & Alerting**: Real-time error tracking with intelligent alerting
- **User-Friendly Messages**: Localized, actionable error messages for end users
- **Error Recovery**: Automatic recovery strategies and fallback mechanisms
- **Flask Middleware Integration**: Seamless integration with Flask applications
- **Configuration Management**: Flexible configuration from multiple sources

## Quick Start

### Basic Setup

```python
from flask import Flask
from app.core.error_handling import (
    ErrorHandlingMiddleware,
    error_manager,
    error_monitor,
    config_manager
)

app = Flask(__name__)

# Load configuration
config_manager.load_from_environment()

# Initialize error handling middleware
error_middleware = ErrorHandlingMiddleware(app)

# Example route with error handling
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    try:
        user = user_service.get_user(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        # Error is automatically handled by middleware
        raise
```

### Using Decorators

```python
from app.core.error_handling import circuit_breaker, retry, with_recovery

# Circuit breaker for external API calls
@circuit_breaker(
    name="external_api",
    failure_threshold=5,
    recovery_timeout=60
)
def call_external_api(data):
    response = requests.post("https://api.example.com/data", json=data)
    response.raise_for_status()
    return response.json()

# Retry with exponential backoff
@retry(
    max_attempts=3,
    base_delay=1.0,
    backoff_strategy="exponential"
)
def unstable_operation():
    # This operation might fail transiently
    if random.random() < 0.3:
        raise ConnectionError("Network error")
    return "Success"

# Error recovery with fallback
@with_recovery(cache_key="user_data", fallback_value={})
def get_user_data(user_id):
    return database.get_user(user_id)
```

## Components

### 1. Error Manager

Centralized error classification and logging:

```python
from app.core.error_handling import error_manager, ErrorCategory, ErrorSeverity

# Automatic error handling
try:
    risky_operation()
except Exception as e:
    error_context = error_manager.handle_error(
        e,
        context={"operation": "data_processing"},
        user_id="user123",
        request_id="req456"
    )
    print(f"Error ID: {error_context.error_id}")

# Custom error classification
def custom_classifier(exception):
    if isinstance(exception, CustomBusinessError):
        return ErrorCategory.BUSINESS_LOGIC, ErrorSeverity.HIGH
    return None

error_manager.register_error_classifier(custom_classifier)

# Get error statistics
stats = error_manager.get_error_statistics(hours=24)
print(f"Total errors: {stats['total_errors']}")
```

### 2. Circuit Breaker

Fault tolerance for external dependencies:

```python
from app.core.error_handling import CircuitBreaker, CircuitBreakerConfig

# Configure circuit breaker
config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60,
    success_threshold=3
)

breaker = CircuitBreaker("payment_service", config)

# Use circuit breaker
try:
    result = breaker.call(payment_service.process_payment, payment_data)
except CircuitBreakerError:
    # Handle when circuit is open
    return fallback_payment_processing(payment_data)

# Get circuit breaker stats
stats = breaker.get_stats()
print(f"Circuit state: {stats.state}")
print(f"Failure count: {stats.failure_count}")
```

### 3. Retry Manager

Intelligent retry mechanisms:

```python
from app.core.error_handling import (
    retry_manager, RetryConfig, BackoffStrategy, JitterType
)

# Configure retry behavior
config = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=60.0,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    jitter_type=JitterType.EQUAL,
    retryable_exceptions=(ConnectionError, TimeoutError),
    non_retryable_exceptions=(ValueError, AuthenticationError)
)

# Retry a function
try:
    result = retry_manager.retry(
        unreliable_function,
        config,
        operation_name="data_sync",
        arg1="value1",
        arg2="value2"
    )
except RetryExhaustedError as e:
    print(f"All retry attempts failed: {e}")

# Get retry statistics
stats = retry_manager.get_operation_stats("data_sync")
print(f"Average attempts: {stats.average_attempts_per_operation}")
```

### 4. Error Monitoring

Real-time error tracking and alerting:

```python
from app.core.error_handling import (
    error_monitor, AlertRule, AlertLevel, AlertChannel
)

# Custom alert rule
def high_error_rate_condition(metrics):
    return metrics.get('error_rate_per_minute', 0) > 20

alert_rule = AlertRule(
    name="critical_error_rate",
    description="Critical error rate exceeded",
    condition=high_error_rate_condition,
    level=AlertLevel.CRITICAL,
    channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
    cooldown_minutes=5
)

error_monitor.add_alert_rule(alert_rule)

# Custom alert handler
def slack_alert_handler(alert):
    slack_client.send_message(
        channel="#alerts",
        message=f"🚨 {alert.message}"
    )

error_monitor.register_alert_handler(AlertChannel.SLACK, slack_alert_handler)

# Get monitoring data
metrics = error_monitor.get_current_metrics()
trends = error_monitor.get_error_trends(hours=6)
alerts = error_monitor.get_alert_history(hours=1)
```

### 5. User-Friendly Messages

Localized error messages for users:

```python
from app.core.error_handling import error_message_mapper, UserMessage, MessageType

# Get user-friendly message
user_message = error_message_mapper.map_exception_to_message(
    ValidationError("Invalid email format"),
    locale="es"  # Spanish
)

print(user_message.message)  # "Por favor ingrese una dirección de correo electrónico válida."

# Custom message mapping
custom_message = UserMessage(
    code="CUSTOM_ERROR",
    message="Something went wrong with your request.",
    message_type=MessageType.ERROR,
    suggested_actions=[
        "Please check your input and try again",
        "Contact support if the problem persists"
    ],
    support_info="Error code: CUSTOM_ERROR"
)

error_message_mapper.add_message_mapping("en", "CUSTOM_ERROR", custom_message)

# Load messages from file
error_message_mapper.load_messages_from_file("custom_messages.json", "en")
```

### 6. Error Recovery

Automatic error recovery strategies:

```python
from app.core.error_handling import (
    error_recovery, FallbackRecoveryHandler, CacheFallbackHandler
)

# Register custom recovery handler
fallback_handler = FallbackRecoveryHandler(
    name="user_service_fallback",
    fallback_function=lambda user_id: {"id": user_id, "name": "Guest User"}
)

error_recovery.register_handler(fallback_handler)

# Use recovery with decorator
@with_recovery(cache_key="user_profile", fallback_value=None)
def get_user_profile(user_id):
    return external_service.get_profile(user_id)

# Manual recovery attempt
try:
    result = error_recovery.attempt_recovery(
        exception=ServiceUnavailableError(),
        original_function=get_user_data,
        user_id=123
    )
except RecoveryError:
    # All recovery strategies failed
    return default_response
```

## Configuration

### Environment Variables

```bash
# Global settings
ERROR_HANDLING_ENABLED=true
ERROR_HANDLING_DEBUG_MODE=false
ERROR_HANDLING_LOG_LEVEL=INFO

# Circuit breaker settings
ERROR_HANDLING_CB_FAILURE_THRESHOLD=5
ERROR_HANDLING_CB_RECOVERY_TIMEOUT=60
ERROR_HANDLING_CB_SUCCESS_THRESHOLD=3

# Retry settings
ERROR_HANDLING_RETRY_MAX_ATTEMPTS=3
ERROR_HANDLING_RETRY_BASE_DELAY=1.0
ERROR_HANDLING_RETRY_BACKOFF_STRATEGY=exponential

# Monitoring settings
ERROR_HANDLING_MONITORING_ENABLED=true
ERROR_HANDLING_MONITORING_ERROR_RATE_THRESHOLD=10.0

# Alert settings
ERROR_HANDLING_ALERT_ENABLED=true
ERROR_HANDLING_ALERT_EMAIL_ENABLED=true
ERROR_HANDLING_ALERT_EMAIL_RECIPIENTS=admin@example.com,ops@example.com

# User messages settings
ERROR_HANDLING_MESSAGES_DEFAULT_LOCALE=en
ERROR_HANDLING_MESSAGES_INCLUDE_TECHNICAL_DETAILS=false
```

### Configuration Files

**config.json:**
```json
{
  "enabled": true,
  "circuit_breaker": {
    "failure_threshold": 5,
    "recovery_timeout": 60,
    "success_threshold": 3
  },
  "retry": {
    "max_attempts": 3,
    "base_delay": 1.0,
    "backoff_strategy": "exponential"
  },
  "monitoring": {
    "enabled": true,
    "error_rate_threshold": 10.0
  },
  "alerts": {
    "enabled": true,
    "channels": ["log", "email"],
    "email_recipients": ["admin@example.com"]
  }
}
```

**config.yaml:**
```yaml
enabled: true
circuit_breaker:
  failure_threshold: 5
  recovery_timeout: 60
  success_threshold: 3
retry:
  max_attempts: 3
  base_delay: 1.0
  backoff_strategy: exponential
monitoring:
  enabled: true
  error_rate_threshold: 10.0
alerts:
  enabled: true
  channels: [log, email]
  email_recipients: [admin@example.com]
```

### Loading Configuration

```python
from app.core.error_handling import config_manager

# Load from multiple sources (order matters)
config_manager.load_default_config() \
    .load_from_file('config.yaml') \
    .load_from_environment() \
    .load_from_dict({'custom_setting': 'value'})

# Validate configuration
issues = config_manager.validate_config()
if issues:
    print("Configuration issues:", issues)

# Get specific configurations
cb_config = config_manager.get_circuit_breaker_config()
retry_config = config_manager.get_retry_config()
```

## Advanced Usage

### Custom Error Handlers

```python
from app.core.error_handling import error_manager

def database_error_handler(exception, error_context):
    # Custom handling for database errors
    if isinstance(exception, DatabaseConnectionError):
        # Switch to read-only mode
        app.config['READ_ONLY_MODE'] = True
        send_urgent_alert("Database connection lost")

error_manager.register_error_handler(DatabaseConnectionError, database_error_handler)
```

### Custom Alert Channels

```python
from app.core.error_handling import error_monitor, AlertChannel

def teams_alert_handler(alert):
    teams_client.send_card({
        "title": f"Alert: {alert.rule_name}",
        "text": alert.message,
        "themeColor": "FF0000" if alert.level == AlertLevel.CRITICAL else "FFA500"
    })

error_monitor.register_alert_handler(AlertChannel.WEBHOOK, teams_alert_handler)
```

### Async Support

```python
import asyncio
from app.core.error_handling import retry_manager

@retry(max_attempts=3, base_delay=1.0)
async def async_operation():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com/data') as response:
            return await response.json()

# Use with asyncio
result = await async_operation()
```

## Best Practices

1. **Use Circuit Breakers for External Dependencies**:
   ```python
   @circuit_breaker(name="payment_api", failure_threshold=3)
   def process_payment(amount):
       return payment_api.charge(amount)
   ```

2. **Configure Appropriate Retry Strategies**:
   ```python
   # For network operations
   @retry(max_attempts=5, backoff_strategy="exponential")
   def network_call():
       pass
   
   # For database operations
   @retry(max_attempts=3, backoff_strategy="linear", base_delay=0.5)
   def database_operation():
       pass
   ```

3. **Provide Meaningful Fallbacks**:
   ```python
   @with_fallback(fallback_value={"status": "unavailable"})
   def get_service_status():
       return external_service.get_status()
   ```

4. **Monitor Critical Operations**:
   ```python
   # Add monitoring to critical business operations
   try:
       result = critical_business_operation()
   except Exception as e:
       error_context = error_manager.handle_error(
           e,
           context={"operation": "critical_business_op", "impact": "high"}
       )
       raise
   ```

5. **Use Localized Error Messages**:
   ```python
   # Always provide locale when handling user-facing errors
   user_message = error_message_mapper.map_exception_to_message(
       exception,
       locale=request.headers.get('Accept-Language', 'en')
   )
   ```

## Error Handling Patterns

### Database Operations
```python
@circuit_breaker(name="database", failure_threshold=3)
@retry(max_attempts=3, retryable_exceptions=(DatabaseConnectionError,))
@with_fallback(fallback_value=None)
def get_user_by_id(user_id):
    return db.session.query(User).filter_by(id=user_id).first()
```

### External API Calls
```python
@circuit_breaker(name="external_api", failure_threshold=5, recovery_timeout=120)
@retry(max_attempts=3, base_delay=2.0, retryable_exceptions=(ConnectionError, TimeoutError))
def call_external_service(data):
    response = requests.post(EXTERNAL_API_URL, json=data, timeout=30)
    response.raise_for_status()
    return response.json()
```

### File Operations
```python
@retry(max_attempts=3, retryable_exceptions=(IOError, OSError))
def save_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
```

## Monitoring and Observability

### Metrics Available
- Total error count by category and severity
- Error rate per minute
- Circuit breaker states and failure counts
- Retry attempt statistics
- Recovery success/failure rates
- Alert history and frequency

### Dashboard Integration
```python
# Export metrics for external monitoring systems
metrics_data = error_monitor.export_metrics('json')

# Get performance data
circuit_stats = circuit_breaker_manager.get_all_stats()
retry_stats = retry_manager.get_all_stats()
recovery_stats = error_recovery.get_recovery_stats()
```

## Troubleshooting

### Common Issues

1. **Circuit Breaker Not Opening**: Check failure threshold and exception types
2. **Retries Not Working**: Verify retryable_exceptions configuration
3. **Alerts Not Firing**: Check alert rule conditions and cooldown periods
4. **Messages Not Localized**: Ensure locale is properly detected and messages are loaded

### Debug Mode
```python
# Enable debug mode for detailed logging
config_manager.load_from_dict({'debug_mode': True, 'log_level': 'DEBUG'})
```

### Testing Error Handling
```python
import pytest
from app.core.error_handling import error_manager, CircuitBreaker

def test_error_classification():
    try:
        raise ValidationError("Invalid input")
    except Exception as e:
        context = error_manager.handle_error(e)
        assert context.category == ErrorCategory.VALIDATION
        assert context.severity == ErrorSeverity.LOW

def test_circuit_breaker():
    breaker = CircuitBreaker("test_service")
    
    # Simulate failures
    for _ in range(6):
        try:
            breaker.call(lambda: exec('raise ConnectionError()'))
        except:
            pass
    
    assert breaker.is_open
```

## Contributing

When extending the error handling system:

1. Add new exception types to the appropriate category
2. Create custom recovery handlers for specific scenarios
3. Add localized error messages for new error types
4. Update configuration schema for new settings
5. Add comprehensive tests for new functionality

## Support

For issues and questions:
- Check the logs for detailed error information
- Use the error_id from responses to trace specific errors
- Monitor error trends to identify systemic issues
- Contact the development team with error context and reproduction steps