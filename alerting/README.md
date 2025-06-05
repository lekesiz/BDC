# BDC Real-time Alert System

## Overview

The BDC Alert System provides comprehensive real-time alerting capabilities for critical system events, security incidents, performance issues, and operational notifications across multiple channels including Slack, email, webhooks, Microsoft Teams, and Discord.

## 🚨 Features

### Multi-Channel Support
- **Slack Integration**: Webhook and bot token support with rich formatting
- **Email Notifications**: HTML and text email alerts to admin teams
- **Webhook Endpoints**: Custom webhook integration for external systems
- **Microsoft Teams**: Native Teams webhook support
- **Discord**: Discord webhook integration with embeds

### Intelligent Alert Management
- **Rate Limiting**: Configurable rate limits per severity level
- **Alert Correlation**: Request correlation IDs for tracking
- **Severity Levels**: Critical, High, Medium, Low with appropriate routing
- **Event Types**: Security, Performance, System, Manual, Custom categories
- **Automatic Retry**: Resilient delivery with fallback channels

### Advanced Features
- **Alert History**: Complete audit trail with filtering and pagination
- **Dashboard Integration**: React-based admin interface
- **API Management**: Full REST API for alert management
- **Health Monitoring**: System health checks and metrics
- **Performance Monitoring**: Response time and error rate alerting

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                BDC Alert System Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │Application  │    │   Security  │    │Performance  │     │
│  │   Events    │    │   Events    │    │   Events    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                    │                    │        │
│         └────────────────────┼────────────────────┘        │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │   Alert Service   │                   │
│                    │  (Rate Limiting,  │                   │
│                    │   Correlation)    │                   │
│                    └─────────┬─────────┘                   │
│                              │                             │
│         ┌────────────────────┼────────────────────┐        │
│         │                    │                    │        │
│  ┌──────▼──────┐    ┌────────▼────────┐    ┌──────▼──────┐ │
│  │    Slack    │    │     Email       │    │   Webhook   │ │
│  │   Channel   │    │    Channel      │    │   Channel   │ │
│  └─────────────┘    └─────────────────┘    └─────────────┘ │
│         │                    │                    │        │
│  ┌──────▼──────┐    ┌────────▼────────┐    ┌──────▼──────┐ │
│  │    Teams    │    │    Discord      │    │   Custom    │ │
│  │   Channel   │    │    Channel      │    │  Webhooks   │ │
│  └─────────────┘    └─────────────────┘    └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
alerting/
├── server/app/
│   ├── services/
│   │   └── alert_service.py           # Core alert service
│   ├── middleware/
│   │   └── alert_middleware.py        # Flask middleware for auto-alerts
│   └── api/routes/
│       └── alerts.py                  # Alert API endpoints
├── client/src/components/admin/
│   └── AlertManagement.jsx            # React admin interface
├── scripts/
│   └── test-alert-system.sh           # Alert system testing script
└── README.md                          # This file
```

## 🚀 Quick Start

### 1. Environment Configuration

Add alert configuration to your `.env` file:

```bash
# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token

# Email Configuration
ADMIN_EMAILS=admin@yourcompany.com,alerts@yourcompany.com

# Webhook Endpoints
ALERT_WEBHOOK_URL=https://your-webhook-endpoint.com/alerts
ALERT_API_KEY=your-webhook-api-key

# Microsoft Teams
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR-TEAMS-WEBHOOK

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
```

### 2. Basic Usage

#### Send Critical Alert
```python
from app.services.alert_service import send_critical_alert

send_critical_alert(
    title="Database Connection Failed",
    message="Unable to connect to PostgreSQL database",
    source="database",
    metadata={"error_code": "DB001", "retry_count": 3}
)
```

#### Send Security Alert
```python
from app.services.alert_service import send_security_alert

send_security_alert(
    title="Suspicious Login Attempt",
    message="Multiple failed login attempts from IP 192.168.1.100",
    metadata={"ip_address": "192.168.1.100", "attempt_count": 5}
)
```

#### Performance Monitoring Decorator
```python
from app.middleware.alert_middleware import monitor_performance

@monitor_performance(warning_threshold=2.0, critical_threshold=5.0)
def slow_function():
    # Will alert if function takes longer than thresholds
    time.sleep(3)
```

### 3. Testing the System

```bash
# Test entire alert system
./scripts/test-alert-system.sh

# Test specific components
./scripts/test-alert-system.sh health
./scripts/test-alert-system.sh test-alert
./scripts/test-alert-system.sh webhook
```

## 📊 API Endpoints

### Alert Management
- `GET /api/alerts/stats` - Get alert statistics
- `GET /api/alerts/history` - Get alert history with filtering
- `GET /api/alerts/config` - Get alert system configuration
- `GET /api/alerts/health` - Check alert system health

### Sending Alerts
- `POST /api/alerts/test` - Send test alert
- `POST /api/alerts/send` - Send manual alert
- `POST /api/alerts/webhook` - Webhook endpoint for external systems

### Example API Usage

#### Get Alert Statistics
```bash
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/alerts/stats
```

#### Send Test Alert
```bash
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Alert",
       "message": "This is a test alert",
       "severity": "medium"
     }' \
     http://localhost:5000/api/alerts/test
```

#### Webhook Alert
```bash
curl -X POST \
     -H "Authorization: Bearer demo-key" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "External Alert",
       "message": "Alert from external system",
       "severity": "high",
       "source": "monitoring"
     }' \
     http://localhost:5000/api/alerts/webhook
```

## 🎯 Alert Configuration

### Severity Levels

| Severity | Description | Default Rate Limit | Channels |
|----------|-------------|-------------------|----------|
| **Critical** | System failures, security breaches | 50/hour | All channels |
| **High** | Important issues requiring attention | 30/hour | All channels |
| **Medium** | Warnings and operational notices | 20/hour | Slack, Email |
| **Low** | Informational messages | 10/hour | Slack only |

### Rate Limiting

Rate limits are configurable per severity level to prevent alert flooding:

```python
rate_limit_config = {
    AlertSeverity.CRITICAL: {"max_alerts": 50, "window_minutes": 60},
    AlertSeverity.HIGH: {"max_alerts": 30, "window_minutes": 60},
    AlertSeverity.MEDIUM: {"max_alerts": 20, "window_minutes": 60},
    AlertSeverity.LOW: {"max_alerts": 10, "window_minutes": 60}
}
```

### Channel Configuration

#### Slack Configuration
```bash
# Webhook URL (recommended)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX

# Bot Token (alternative)
SLACK_BOT_TOKEN=xoxb-000000000000-000000000000-XXXXXXXXXXXXXXXXXXXXXXXX
```

#### Email Configuration
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=alerts@yourcompany.com
MAIL_PASSWORD=your-app-password
ADMIN_EMAILS=admin1@company.com,admin2@company.com
```

#### Teams Configuration
```bash
# Get webhook URL from Teams channel connector
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

## 🛠️ Advanced Usage

### Custom Alert Decorators

#### Alert on Exception
```python
from app.middleware.alert_middleware import alert_on_exception, AlertSeverity

@alert_on_exception(AlertSeverity.CRITICAL)
def critical_function():
    # Will send critical alert if exception occurs
    if some_condition:
        raise Exception("Critical error occurred")
```

#### Conditional Alerts
```python
from app.middleware.alert_middleware import alert_on_condition

@alert_on_condition(
    condition_func=lambda result: result['status'] == 'failed',
    title="Process Failed",
    message="Background process returned failed status",
    severity=AlertSeverity.HIGH
)
def background_process():
    return {'status': 'failed', 'error': 'Database timeout'}
```

### Custom Alert Channels

Extend the alert service to support additional channels:

```python
class CustomAlertChannel:
    def send_alert(self, event: AlertEvent) -> bool:
        # Implement custom sending logic
        return True

# Register custom channel
alert_service.register_channel('custom', CustomAlertChannel())
```

### Alert Correlation

Use correlation IDs to track related alerts:

```python
correlation_id = f"batch_job_{job_id}"

send_critical_alert(
    title="Batch Job Failed",
    message=f"Batch job {job_id} failed with error",
    correlation_id=correlation_id,
    metadata={"job_id": job_id, "stage": "processing"}
)
```

## 📱 Admin Dashboard

Access the alert management dashboard at `/admin/alerts`:

### Features
- **Overview**: Real-time alert statistics and system health
- **Alert History**: Searchable history with filtering options
- **Send Alerts**: Test and manual alert sending interface
- **Configuration**: View current alert system settings

### Dashboard Capabilities
- View alert trends and patterns
- Filter alerts by severity, source, and date
- Send test alerts to verify channel configuration
- Export alert data for analysis
- Monitor alert system health and performance

## 🔧 Troubleshooting

### Common Issues

#### Slack Alerts Not Working
```bash
# Check webhook URL configuration
curl -X POST $SLACK_WEBHOOK_URL \
     -H 'Content-Type: application/json' \
     -d '{"text": "Test message"}'

# Verify webhook URL in environment
echo $SLACK_WEBHOOK_URL
```

#### Email Alerts Failing
```bash
# Test SMTP connection
python -c "
import smtplib
server = smtplib.SMTP('$MAIL_SERVER', $MAIL_PORT)
server.starttls()
server.login('$MAIL_USERNAME', '$MAIL_PASSWORD')
print('SMTP connection successful')
server.quit()
"
```

#### High Alert Volume
```bash
# Check rate limiting statistics
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/alerts/stats
```

### Debug Mode

Enable debug logging for alert system:

```bash
# In environment
ALERT_DEBUG=true
LOG_LEVEL=DEBUG

# Check alert service logs
docker logs bdc-backend | grep -i alert
```

### Testing Channels

Test individual channels:

```bash
# Test all channels
./scripts/test-alert-system.sh full

# Test specific functionality
./scripts/test-alert-system.sh webhook
./scripts/test-alert-system.sh test-alert
```

## 📈 Monitoring and Metrics

### Alert Metrics

The system automatically tracks:
- Alert count by severity and time
- Channel success/failure rates
- Rate limiting statistics
- Response times per channel
- Error rates and patterns

### Integration with Monitoring Stack

Alert metrics are exported to:
- **Prometheus**: Alert count and rate metrics
- **Grafana**: Alert dashboard and visualizations
- **ELK Stack**: Alert logs and analytics

### Health Monitoring

```bash
# Check alert system health
curl http://localhost:5000/api/alerts/health

# Get detailed statistics
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/alerts/stats
```

## 🔒 Security Considerations

### Authentication
- All admin endpoints require JWT authentication
- Webhook endpoints use API key authentication
- Rate limiting prevents abuse

### Data Protection
- Alert content is sanitized before sending
- Sensitive data can be filtered from alerts
- Audit trail for all alert operations

### Network Security
- HTTPS required for webhook endpoints
- Webhook signature validation (configurable)
- IP allowlisting for webhook sources

## 🚀 Production Deployment

### Environment Variables Checklist
- [ ] `SLACK_WEBHOOK_URL` or `SLACK_BOT_TOKEN`
- [ ] `ADMIN_EMAILS` (comma-separated)
- [ ] `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`
- [ ] `ALERT_WEBHOOK_URL` and `ALERT_API_KEY`
- [ ] `TEAMS_WEBHOOK_URL` (if using Teams)
- [ ] `DISCORD_WEBHOOK_URL` (if using Discord)

### Performance Tuning
- Adjust rate limits based on alert volume
- Configure appropriate timeouts for channels
- Use async processing for high-volume alerts
- Monitor memory usage and connection pools

### Monitoring Setup
- Set up alerts for alert system failures
- Monitor channel health and response times
- Track alert volume and patterns
- Configure dashboards for alert analytics

## 📞 Support

### Health Check Endpoint
```bash
curl http://localhost:5000/api/alerts/health
```

### Log Analysis
```bash
# Backend alert logs
docker logs bdc-backend | grep -i alert

# Check alert service status
docker exec bdc-backend python -c "
from app.services.alert_service import alert_service
print(f'Enabled channels: {[c.value for c in alert_service.enabled_channels]}')
print(f'Recent alerts: {len(alert_service.alert_history)}')
"
```

### Common Commands
```bash
# Test entire system
./scripts/test-alert-system.sh

# Get alert statistics
./scripts/test-alert-system.sh stats

# Test webhook only
./scripts/test-alert-system.sh webhook

# Check configuration
./scripts/test-alert-system.sh config
```