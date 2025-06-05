# AI Chat Service Documentation

## Overview

The AI Chat Service provides intelligent conversational assistance to beneficiaries through an OpenAI-powered chatbot. It supports context-aware conversations, multiple languages, and integrates with existing services like appointments, assessments, and programs.

## Features

### Core Features
- **Intelligent Conversations**: Powered by OpenAI's GPT models
- **Context-Aware**: Different conversation types (education, appointment, progress, assessment, general)
- **Multi-Language Support**: Turkish and English with automatic language detection
- **Conversation History**: Full chat history stored in database
- **Rate Limiting**: Per-user limits on messages and tokens
- **Export Functionality**: Export conversations in JSON or text format
- **Admin Moderation**: Flag and review conversations
- **Integration**: Works with appointments, assessments, and program services

### Technical Features
- **Token Tracking**: Monitor OpenAI API usage
- **Conversation Summarization**: Automatic summarization of long conversations
- **Template System**: Pre-defined conversation starters
- **Analytics**: Track usage patterns and metrics
- **Function Calling**: AI can interact with system functions

## Architecture

### Models

#### ChatConversation
Main conversation entity storing:
- User and beneficiary associations
- Conversation metadata (title, language, status)
- Context information (type, related entities)
- AI model settings
- Summary and sentiment analysis
- Moderation flags

#### ChatMessage
Individual messages within conversations:
- Role (user, assistant, system)
- Content
- Token usage
- Metadata for function calls
- Error tracking

#### ChatRateLimit
Rate limiting per user:
- Daily/monthly message counts
- Daily/monthly token counts
- Custom limits per user

#### ConversationTemplate
Pre-defined conversation templates:
- System prompts
- Welcome messages
- Suggested questions
- Language-specific content

### Service Layer

The `AIChatService` handles:
- Conversation creation and management
- Message generation using OpenAI
- Context building and enhancement
- Function calling for system integration
- Rate limit enforcement
- Analytics and reporting

## API Endpoints

### User Endpoints

#### Create Conversation
```
POST /api/chat/conversations
{
    "beneficiary_id": 123,
    "context_type": "education",
    "language": "en",
    "message": "Hello, I need help with my program"
}
```

#### Send Message
```
POST /api/chat/conversations/{id}/messages
{
    "message": "Can you explain the next module?"
}
```

#### Get Conversations
```
GET /api/chat/conversations?status=active&context_type=education
```

#### Get Conversation Details
```
GET /api/chat/conversations/{id}
```

#### Close Conversation
```
POST /api/chat/conversations/{id}/close
```

#### Export Conversation
```
GET /api/chat/conversations/{id}/export?format=json
```

#### Get Rate Limits
```
GET /api/chat/rate-limits
```

### Admin Endpoints

#### Flag Conversation
```
POST /api/chat/conversations/{id}/flag
{
    "reason": "Inappropriate content"
}
```

#### Get Analytics
```
GET /api/chat/analytics?tenant_id=1&start_date=2025-01-01
```

#### Manage Templates
```
GET /api/chat/templates
POST /api/chat/templates
PUT /api/chat/templates/{id}
DELETE /api/chat/templates/{id}
```

## Context Types

### General
Default context for general inquiries about the center and its services.

### Education
Focused on educational support, study strategies, and program-related questions.

### Appointment
Handles appointment scheduling, checking availability, and managing bookings.

### Progress
Tracks beneficiary progress, achievements, and provides improvement suggestions.

### Assessment
Supports assessment preparation, requirements understanding, and performance guidance.

## Rate Limiting

Default limits per user:
- **Daily**: 100 messages, 50,000 tokens
- **Monthly**: 1,000 messages, 500,000 tokens

Custom limits can be set per user through the `ChatRateLimit` model.

## Function Calling

The AI can call system functions based on context:

### Appointment Context
- `check_availability`: Check available appointment slots
- `book_appointment`: Book an appointment

### Progress Context
- `get_progress_report`: Get beneficiary's progress report

### Education Context
- `get_program_info`: Get information about programs

## Language Support

- **Automatic Detection**: Language is auto-detected from user messages
- **Supported Languages**: English (en) and Turkish (tr)
- **Template Localization**: Separate templates for each language
- **Response Localization**: AI responds in the detected/selected language

## Moderation and Safety

- **Flagging System**: Admins can flag conversations for review
- **Status Tracking**: Conversations can be active, closed, archived, or flagged
- **Audit Trail**: All flags include admin ID and timestamp
- **User Notifications**: Users are notified when conversations are flagged

## Integration Points

### Appointment Service
- Check availability
- Book appointments
- Manage scheduling

### Program Service
- Get program information
- Track enrollment
- Monitor progress

### Assessment Service
- Access assessment details
- Track performance
- Provide preparation guidance

### Notification Service
- Send moderation notifications
- Alert users of important updates

## Configuration

### Environment Variables
```
OPENAI_API_KEY=your_api_key
OPENAI_ORGANIZATION=your_org_id
AI_MODEL=gpt-4
```

### Model Settings
- **Model**: gpt-4, gpt-4-turbo, or gpt-3.5-turbo
- **Temperature**: 0.7 (default)
- **Max Tokens**: Varies by model (800-1500)

## Database Schema

### Migrations
Run the migration to create chat tables:
```bash
alembic upgrade head
```

### Initialization
Initialize default templates:
```bash
python scripts/init_chat_templates.py
```

## Usage Examples

### Creating a Conversation
```python
from app.services.ai_chat_service import ai_chat_service

result = ai_chat_service.create_conversation(
    user_id=1,
    beneficiary_id=10,
    context_type='education',
    language='en',
    initial_message="What programs are available?"
)
```

### Sending a Message
```python
response = ai_chat_service.send_message(
    conversation_id=1,
    user_id=1,
    message="Tell me more about the Python course"
)
```

### Getting Analytics
```python
analytics = ai_chat_service.get_conversation_analytics(
    tenant_id=1,
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)
```

## Best Practices

1. **Context Selection**: Choose appropriate context types for better responses
2. **Language Consistency**: Maintain language consistency within conversations
3. **Rate Limit Monitoring**: Monitor usage to avoid hitting limits
4. **Template Customization**: Create tenant-specific templates for better UX
5. **Regular Moderation**: Review flagged conversations promptly
6. **Analytics Review**: Monitor analytics for usage patterns and improvements

## Error Handling

The service handles various error scenarios:
- **Rate Limit Exceeded**: Returns appropriate error message
- **OpenAI API Errors**: Fallback error messages in user's language
- **Invalid Context**: Validates context types before processing
- **Missing Conversations**: 404 errors for non-existent conversations

## Security Considerations

1. **Authentication**: All endpoints require JWT authentication
2. **Authorization**: Users can only access their own conversations
3. **Data Privacy**: Conversations are user-specific and isolated
4. **Admin Access**: Special permissions required for moderation
5. **Input Validation**: All inputs are validated before processing

## Future Enhancements

Potential improvements:
- Voice message support
- File attachment handling
- Real-time streaming responses
- Advanced analytics dashboard
- Custom AI model fine-tuning
- Integration with more services
- Conversation threading
- Automated moderation using AI