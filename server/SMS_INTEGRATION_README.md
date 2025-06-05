# SMS Integration Service

A comprehensive SMS integration service for the BDC platform with support for multiple providers, templates, campaigns, and advanced features.

## Features

### Core Features
- **Multiple SMS Provider Support**: Twilio (primary) with automatic fallback to AWS SNS
- **SMS Types**: Appointment reminders, assessment notifications, password reset codes, 2FA codes, general notifications
- **Template System**: Multi-language support (Turkish and English) with variable substitution
- **Bulk SMS**: Send to multiple recipients with validation
- **SMS Scheduling**: Schedule messages for future delivery
- **Delivery Tracking**: Real-time status updates and delivery confirmations
- **Rate Limiting**: Prevent abuse with configurable limits
- **Phone Validation**: International phone number validation and formatting
- **Cost Tracking**: Monitor SMS costs and generate reports

### Advanced Features
- **SMS Campaigns**: Create and manage bulk SMS campaigns with filters
- **Automatic Retries**: Failed messages are retried with exponential backoff
- **Webhook Support**: Receive delivery status updates from providers
- **Analytics**: Comprehensive statistics and reporting
- **Multi-tenant**: Full tenant isolation and management

## Configuration

1. Copy the example environment file:
```bash
cp .env.sms.example .env
```

2. Configure your SMS providers in the `.env` file:
```env
# Twilio (Primary Provider)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# AWS SNS (Fallback Provider)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# SMS Settings
DEFAULT_COUNTRY_CODE=US
SMS_RATE_LIMIT=100
SMS_RETENTION_DAYS=90
```

3. Run migrations to create SMS tables:
```bash
flask db upgrade
```

## API Endpoints

### Sending SMS

#### Send Single SMS
```http
POST /api/sms/send
Authorization: Bearer {token}
Content-Type: application/json

{
  "phone_number": "+1234567890",
  "message": "Your appointment is tomorrow at 2 PM",
  "message_type": "appointment_reminder",
  "language": "en"
}
```

#### Send Templated SMS
```http
POST /api/sms/send-templated
Authorization: Bearer {token}
Content-Type: application/json

{
  "phone_number": "+1234567890",
  "template_id": "appointment_reminder",
  "variables": {
    "date": "March 15, 2024",
    "time": "2:00 PM",
    "trainer_name": "John Doe",
    "location": "Training Room A"
  },
  "language": "en"
}
```

#### Send Bulk SMS
```http
POST /api/sms/send-bulk
Authorization: Bearer {token}
Content-Type: application/json

{
  "phone_numbers": ["+1234567890", "+0987654321"],
  "message": "Important announcement: Training session rescheduled",
  "message_type": "general_notification"
}
```

#### Schedule SMS
```http
POST /api/sms/schedule
Authorization: Bearer {token}
Content-Type: application/json

{
  "phone_number": "+1234567890",
  "message": "Reminder: Your assessment is due tomorrow",
  "scheduled_time": "2024-03-15T10:00:00Z",
  "message_type": "assessment_notification"
}
```

### SMS Management

#### Get SMS Status
```http
GET /api/sms/messages/{message_id}/status
Authorization: Bearer {token}
```

#### Get SMS History
```http
GET /api/sms/history?user_id=123&status=delivered&limit=50
Authorization: Bearer {token}
```

#### Get SMS Statistics
```http
GET /api/sms/stats?start_date=2024-01-01&end_date=2024-03-31
Authorization: Bearer {token}
```

#### Validate Phone Number
```http
POST /api/sms/validate-phone
Authorization: Bearer {token}
Content-Type: application/json

{
  "phone_number": "234-567-8900",
  "country_code": "US"
}
```

### Template Management

#### List Templates
```http
GET /api/sms/templates
Authorization: Bearer {token}
```

#### Create Template
```http
POST /api/sms/templates
Authorization: Bearer {token}
Content-Type: application/json

{
  "template_id": "welcome_message",
  "name": "Welcome Message",
  "content_en": "Welcome {{name}}! Your account has been created.",
  "content_tr": "Hoş geldiniz {{name}}! Hesabınız oluşturuldu.",
  "message_type": "welcome_message",
  "variables": ["name"]
}
```

### Campaign Management

#### Create Campaign
```http
POST /api/sms/campaigns
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "March Training Reminder",
  "template_id": "training_reminder",
  "recipient_filters": {
    "roles": ["beneficiary"],
    "tenant_id": 1
  },
  "scheduled_for": "2024-03-10T09:00:00Z"
}
```

#### Execute Campaign
```http
POST /api/sms/campaigns/{campaign_id}/execute
Authorization: Bearer {token}
```

#### Get Campaign Status
```http
GET /api/sms/campaigns/{campaign_id}/status
Authorization: Bearer {token}
```

## Usage Examples

### Python SDK Usage

```python
from app.services.sms_service import SMSService

sms_service = SMSService()

# Send appointment reminder
success, message_id = sms_service.send_appointment_reminder(
    appointment_id=123,
    phone_number="+1234567890",
    user_id=456,
    language="en"
)

# Send password reset code
success, message_id = sms_service.send_password_reset_code(
    phone_number="+1234567890",
    reset_code="123456",
    user_id=456,
    language="en"
)

# Send 2FA code
success, message_id = sms_service.send_2fa_code(
    phone_number="+1234567890",
    auth_code="987654",
    user_id=456,
    language="en"
)

# Validate phone number
is_valid, formatted = sms_service.validate_phone_number(
    phone_number="234-567-8900",
    country_code="US"
)
```

### Celery Tasks

The following tasks run automatically:
- **Send SMS appointment reminders**: Every 30 minutes
- **Update SMS delivery status**: Every hour
- **Clean up old SMS records**: Monthly (configurable retention period)

## Default Templates

The system comes with pre-configured templates:

### Appointment Reminder
- **ID**: `appointment_reminder`
- **Variables**: `date`, `time`, `trainer_name`, `location`
- **Languages**: English, Turkish

### Assessment Notification
- **ID**: `assessment_notification`
- **Variables**: `assessment_name`, `due_date`
- **Languages**: English, Turkish

### Password Reset
- **ID**: `password_reset`
- **Variables**: `code`
- **Languages**: English, Turkish

### 2FA Verification
- **ID**: `2fa_code`
- **Variables**: `code`
- **Languages**: English, Turkish

## Rate Limiting

SMS sending is rate-limited to prevent abuse:
- Default: 100 SMS per hour per user
- Configurable via `SMS_RATE_LIMIT` environment variable
- Admin users have higher limits

## Cost Tracking

The system tracks SMS costs:
- Cost per message stored in database
- Monthly cost reports available
- Cost breakdown by provider, message type, and tenant

## Security

- Phone numbers are validated before sending
- Rate limiting prevents abuse
- Sensitive codes (password reset, 2FA) expire after set time
- All SMS content is logged for audit purposes
- Provider credentials are stored securely in environment variables

## Monitoring

Monitor SMS service health:
- Check delivery rates: `/api/sms/stats`
- Failed message alerts via logging
- Cost threshold alerts (configurable)
- Provider availability monitoring

## Troubleshooting

### Common Issues

1. **SMS not sending**
   - Check provider credentials
   - Verify phone number format (must be E.164)
   - Check rate limits
   - Review logs for provider errors

2. **Invalid phone numbers**
   - Ensure correct country code
   - Remove formatting characters
   - Use the validation endpoint

3. **Template not found**
   - Verify template ID exists
   - Check template is active
   - Ensure correct tenant context

## Database Schema

### sms_messages
- Stores all SMS messages sent
- Tracks delivery status and costs
- Links to users and related entities

### sms_templates
- Reusable message templates
- Multi-language support
- Variable substitution

### sms_campaigns
- Bulk SMS campaign management
- Recipient filtering
- Execution tracking

## Future Enhancements

- WhatsApp Business API integration
- Rich media messaging (MMS)
- Two-way SMS conversations
- Advanced analytics dashboard
- A/B testing for templates
- Delivery time optimization