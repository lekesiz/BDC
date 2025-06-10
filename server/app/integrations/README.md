# BDC Third-Party Integrations System

A comprehensive third-party integrations system for the BDC project, providing unified interfaces for calendar services, payment processors, video conferencing, email services, storage providers, and authentication providers.

## Features

### Supported Integrations

#### Calendar Services
- **Google Calendar** - Full OAuth2 integration with event management and availability checking
- **Microsoft Outlook Calendar** - Complete Outlook calendar integration via Microsoft Graph API
- **iCal/WebDAV** - Support for standard CalDAV calendar services

#### Payment Processors
- **Stripe** - Complete payment processing with customers, payment methods, and webhooks
- **PayPal** - PayPal integration for payment processing and order management

#### Video Conferencing
- **Zoom** - Full Zoom meeting management with recording and participant controls
- **Microsoft Teams** - Teams meeting integration via Microsoft Graph API
- **Google Meet** - Google Meet integration through Calendar API

#### Email Services
- **SendGrid** - Complete email sending with templates and analytics
- **Mailgun** - Email delivery service with template support

#### Storage Providers
- **AWS S3** - Amazon S3 cloud storage integration
- **Azure Storage** - Microsoft Azure Blob Storage
- **Google Cloud Storage** - Google Cloud Platform storage

#### Authentication Providers
- **Google OAuth** - Google authentication and user management
- **Microsoft Azure AD** - Microsoft identity platform integration
- **GitHub** - GitHub OAuth integration

## Architecture

### Base Components

#### BaseIntegration
All integrations inherit from `BaseIntegration` which provides:
- Common authentication patterns (OAuth2, API Key)
- Configuration management
- Error handling and retry logic
- Webhook processing
- Status monitoring

#### Integration Registry
Central registry for managing integration classes and instances:
- Dynamic integration discovery
- Instance lifecycle management
- Type-based filtering

#### Configuration Manager
Handles integration configuration:
- Environment variable loading
- File-based configuration
- Runtime configuration updates
- Credential management

## Quick Start

### Installation

```bash
# Install base dependencies
pip install aiohttp

# Install integration-specific dependencies
pip install stripe sendgrid google-api-python-client google-auth-oauthlib
pip install icalendar caldav PyJWT
```

### Environment Configuration

```bash
# Calendar integrations
export GOOGLE_CALENDAR_CLIENT_ID="your_client_id"
export GOOGLE_CALENDAR_CLIENT_SECRET="your_client_secret"
export GOOGLE_CALENDAR_REDIRECT_URI="http://localhost/callback"

export OUTLOOK_CLIENT_ID="your_client_id"
export OUTLOOK_CLIENT_SECRET="your_client_secret"
export OUTLOOK_REDIRECT_URI="http://localhost/callback"

# Payment processors
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

export PAYPAL_CLIENT_ID="your_client_id"
export PAYPAL_CLIENT_SECRET="your_client_secret"
export PAYPAL_ENVIRONMENT="sandbox"

# Video conferencing
export ZOOM_CLIENT_ID="your_client_id"
export ZOOM_CLIENT_SECRET="your_client_secret"
export ZOOM_REDIRECT_URI="http://localhost/callback"

# Email services
export SENDGRID_API_KEY="SG...."
export MAILGUN_API_KEY="key-..."
export MAILGUN_DOMAIN="your-domain.com"

# Storage providers
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
export AWS_S3_BUCKET="your-bucket"

# Authentication providers
export GOOGLE_OAUTH_CLIENT_ID="your_client_id"
export GOOGLE_OAUTH_CLIENT_SECRET="your_client_secret"
```

### Basic Usage

```python
from app.integrations import IntegrationManager
from app.integrations.calendar import GoogleCalendarIntegration, CalendarEventInput
from app.integrations.email import SendGridIntegration
from datetime import datetime, timedelta

# Initialize integration manager
manager = IntegrationManager()

# Calendar example
config = manager.get_config('google_calendar')
calendar = GoogleCalendarIntegration(config)

await calendar.connect()

# Create a meeting
meeting_data = CalendarEventInput(
    title="Team Meeting",
    start_time=datetime.now() + timedelta(hours=1),
    end_time=datetime.now() + timedelta(hours=2),
    attendees=["team@company.com"]
)

event = await calendar.create_event("primary", meeting_data)
print(f"Created event: {event.title}")

# Email example
email_config = manager.get_config('sendgrid')
email = SendGridIntegration(email_config)

await email.connect()

message_id = await email.send_welcome_email(
    "user@example.com",
    "John Doe",
    "https://app.company.com/login"
)
print(f"Sent welcome email: {message_id}")
```

### Advanced Usage

#### Using the Registry

```python
from app.integrations.registry import integration_registry
from app.integrations.config import IntegrationManager

manager = IntegrationManager()

# Create all available integrations
for config_name in manager.list_enabled_configs():
    config = manager.get_config(config_name)
    if config:
        integration = integration_registry.create_integration(config_name, config)
        await integration.connect()

# Get integrations by type
calendar_integrations = integration_registry.get_integrations_by_type("calendar")
payment_integrations = integration_registry.get_integrations_by_type("payment")
```

#### OAuth2 Flow

```python
# Step 1: Get authorization URL
auth_url = await integration.get_authorization_url(state="random_state")
# Redirect user to auth_url

# Step 2: Exchange code for tokens (after callback)
tokens = await integration.exchange_code_for_tokens(code, state)

# Step 3: Connect with tokens
await integration.connect()
```

#### Webhook Handling

```python
from flask import Flask, request
app = Flask(__name__)

@app.route('/webhooks/stripe', methods=['POST'])
async def stripe_webhook():
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    
    # Validate signature
    if await stripe_integration.validate_webhook_signature(
        payload, signature, webhook_secret
    ):
        webhook_data = request.get_json()
        result = await stripe_integration.handle_webhook(webhook_data)
        return {'status': 'success'}
    
    return {'error': 'Invalid signature'}, 400
```

## Integration Details

### Calendar Integrations

#### Google Calendar
- Full OAuth2 support
- Event CRUD operations
- Availability checking
- Calendar sharing
- Recurring events
- Attendee management

```python
# Create recurring meeting
recurrence = {
    'FREQ': 'WEEKLY',
    'BYDAY': 'MO',
    'COUNT': 10
}

event_data = CalendarEventInput(
    title="Weekly Standup",
    start_time=datetime.now(),
    end_time=datetime.now() + timedelta(hours=1),
    recurrence=recurrence
)

event = await calendar.create_event("primary", event_data)
```

#### Microsoft Outlook
- Microsoft Graph API integration
- Enterprise calendar features
- Exchange compatibility
- Advanced filtering

#### iCal/WebDAV
- Standards-based integration
- Self-hosted calendar support
- Cross-platform compatibility

### Payment Processing

#### Stripe Integration
- Customer management
- Payment methods
- Payment intents
- Subscriptions
- Webhooks
- Refunds

```python
from decimal import Decimal

# Create customer and payment
customer = await stripe.create_customer(
    email="customer@example.com",
    name="John Doe"
)

payment_intent = await stripe.create_payment_intent(
    amount=Decimal('29.99'),
    currency='usd',
    customer_id=customer.id,
    description="Service payment"
)

# Confirm payment
confirmed = await stripe.confirm_payment_intent(
    payment_intent.id,
    payment_method_id="pm_card_visa"
)
```

#### PayPal Integration
- Order management
- Payment capture
- Refund processing
- Webhook support

### Video Conferencing

#### Zoom Integration
- Meeting scheduling
- Instant meetings
- Recording management
- Participant controls
- Webinar support

```python
# Schedule meeting with recording
meeting_data = VideoMeetingInput(
    topic="Client Consultation",
    start_time=datetime.now() + timedelta(days=1),
    duration=60,
    auto_recording="cloud",
    waiting_room=True
)

meeting = await zoom.create_meeting(meeting_data)
print(f"Join URL: {meeting.join_url}")

# Start recording
await zoom.start_recording(meeting.id)
```

#### Microsoft Teams
- Online meeting creation
- Calendar integration
- Enterprise features

#### Google Meet
- Calendar-based meetings
- Automatic meeting links
- Google Workspace integration

### Email Services

#### SendGrid Integration
- Transactional emails
- Email templates
- Analytics and tracking
- Suppression management
- A/B testing

```python
# Create and use template
template = EmailTemplate(
    name="welcome_email",
    subject="Welcome {{name}}!",
    html_content="<h1>Hello {{name}}</h1><p>Welcome to our service!</p>"
)

template_id = await sendgrid.create_template(template)

# Send templated email
await sendgrid.send_template_email(
    template_id,
    ["user@example.com"],
    {"name": "John"}
)
```

#### Mailgun Integration
- Reliable delivery
- Email validation
- Route management
- Analytics

## Testing

### Running Tests

```python
from app.integrations.testing import run_integration_tests

# Run all tests
results = await run_integration_tests()

# Run specific test suite
from app.integrations.testing import IntegrationTester
tester = IntegrationTester()
calendar_results = await tester.run_test_suite('calendar')
```

### Test Coverage

The testing system includes:
- Connection tests for all integrations
- CRUD operation tests
- Authentication flow tests
- Error handling tests
- Performance tests
- Integration compatibility tests

## Security Considerations

### Credential Management
- Environment variable configuration
- Encrypted storage support
- Token rotation
- Webhook signature validation

### Rate Limiting
- Automatic rate limit handling
- Backoff strategies
- Request queuing

### Error Handling
- Comprehensive error types
- Retry mechanisms
- Circuit breaker patterns
- Graceful degradation

## Monitoring and Logging

### Health Checks
Each integration provides health check endpoints:

```python
status = await integration.get_status()
# Returns:
# {
#   'name': 'google_calendar',
#   'type': 'calendar',
#   'provider': 'google',
#   'status': 'connected',
#   'enabled': True,
#   'last_error': None
# }
```

### Metrics
- Request counts and latencies
- Error rates
- Success rates
- Integration availability

### Logging
Structured logging with integration-specific contexts:

```python
import logging
logger = logging.getLogger('app.integrations.calendar.google')
```

## Extending the System

### Adding New Integrations

1. Create integration class inheriting from appropriate base:

```python
from app.integrations.base import BaseIntegration
from app.integrations.registry import register_integration

@register_integration('new_service')
class NewServiceIntegration(BaseIntegration):
    @property
    def integration_type(self) -> str:
        return "custom"
    
    @property
    def provider_name(self) -> str:
        return "new_service"
    
    async def connect(self) -> bool:
        # Implementation
        pass
```

2. Add configuration support in `config.py`
3. Add tests in `testing.py`
4. Update documentation

### Custom Integration Types

Create custom base classes for new integration categories:

```python
from app.integrations.base import BaseIntegration

class BaseSMSIntegration(BaseIntegration):
    @property
    def integration_type(self) -> str:
        return "sms"
    
    @abstractmethod
    async def send_sms(self, to: str, message: str) -> str:
        pass
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check credentials in environment variables
   - Verify OAuth redirect URIs
   - Ensure proper scopes are requested

2. **Rate Limiting**
   - Monitor API usage
   - Implement proper backoff
   - Consider caching strategies

3. **Webhook Issues**
   - Verify endpoint accessibility
   - Check signature validation
   - Monitor webhook logs

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('app.integrations').setLevel(logging.DEBUG)
```

### Health Monitoring

```python
from app.integrations.config import IntegrationManager

manager = IntegrationManager()
status = manager.get_integration_status()

for name, integration_status in status.items():
    if integration_status['status'] != 'connected':
        print(f"Integration {name} is not healthy: {integration_status}")
```

## Performance Optimization

### Connection Pooling
- Reuse HTTP connections
- Connection timeout management
- Pool size optimization

### Caching
- Response caching for read operations
- Token caching
- Configuration caching

### Async Operations
- Concurrent request processing
- Background task queuing
- Streaming for large datasets

## Contributing

1. Follow the existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Ensure security best practices
5. Add monitoring and logging

## License

This integration system is part of the BDC project and follows the same licensing terms.