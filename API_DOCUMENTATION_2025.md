# BDC API Documentation - Version 2025.06
*Last Updated: June 3, 2025*

## Overview
The BDC (Beneficiary Development Center) API is a RESTful API that provides endpoints for managing beneficiaries, programs, evaluations, documents, and other training-related resources.

## Base URL
- Development: `http://localhost:5001/api`
- Production: `https://api.bdc.com/api`

## Authentication
All API endpoints require JWT authentication unless otherwise specified.

### Authentication Flow
1. Login with credentials to obtain access and refresh tokens
2. Include the access token in the Authorization header: `Authorization: Bearer <token>`
3. Refresh the token when it expires using the refresh endpoint

### Authentication Endpoints

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "trainer",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Logout
```http
POST /auth/logout
Authorization: Bearer <access_token>

Response:
{
  "message": "Successfully logged out"
}
```

## User Roles
- **super_admin**: Full system access
- **tenant_admin**: Tenant-level administration
- **trainer**: Can manage assigned beneficiaries
- **student**: Basic access to own data

## API Endpoints

### 1. Beneficiaries Management

#### List Beneficiaries
```http
GET /beneficiaries?page=1&per_page=10&tenant_id=1&trainer_id=1&status=active&query=john
Authorization: Bearer <token>
Roles: super_admin, tenant_admin, trainer

Response:
{
  "items": [
    {
      "id": 1,
      "user_id": 2,
      "trainer_id": 3,
      "tenant_id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "gender": "male",
      "birth_date": "1990-01-01",
      "address": "123 Main St",
      "city": "New York",
      "country": "USA",
      "profession": "Software Developer",
      "company": "Tech Corp",
      "emergency_contact_name": "Jane Doe",
      "emergency_contact_relationship": "Spouse",
      "emergency_contact_phone": "+1234567891",
      "emergency_contact_email": "jane@example.com",
      "emergency_contact_address": "123 Main St, New York",
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 50,
  "pages": 5
}
```

#### Create Beneficiary
```http
POST /beneficiaries
Authorization: Bearer <token>
Roles: super_admin, tenant_admin, trainer
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Smith",
  "tenant_id": 1,
  "trainer_id": 3,
  "phone": "+1234567890",
  "gender": "male",
  "birth_date": "1990-01-01",
  "address": "456 Oak St",
  "city": "Boston",
  "country": "USA",
  "profession": "Designer",
  "company": "Design Studio",
  "emergency_contact_name": "Mary Smith",
  "emergency_contact_relationship": "Mother",
  "emergency_contact_phone": "+1234567892",
  "emergency_contact_email": "mary@example.com",
  "emergency_contact_address": "789 Pine St, Boston"
}

Response:
{
  "message": "Beneficiary created successfully",
  "beneficiary": {
    "id": 2,
    "user_id": 5,
    ...
  }
}
```

#### Get Beneficiary Details
```http
GET /beneficiaries/{id}
Authorization: Bearer <token>
Roles: super_admin, tenant_admin, trainer, student (own data)

Response:
{
  "id": 1,
  "user": {
    "id": 2,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "trainer": {
    "id": 3,
    "first_name": "Alice",
    "last_name": "Johnson"
  },
  // All beneficiary fields including emergency contacts
}
```

#### Update Beneficiary
```http
PUT /beneficiaries/{id}
Authorization: Bearer <token>
Roles: super_admin, tenant_admin, trainer
Content-Type: application/json

{
  "phone": "+1234567899",
  "address": "789 New Street",
  "emergency_contact_name": "Updated Contact",
  "emergency_contact_phone": "+9876543210"
}

Response:
{
  "message": "Beneficiary updated successfully",
  "beneficiary": { ... }
}
```

### 2. Programs Management

#### List Programs
```http
GET /programs?page=1&per_page=10&tenant_id=1&status=active
Authorization: Bearer <token>

Response:
{
  "items": [
    {
      "id": 1,
      "name": "Web Development Bootcamp",
      "description": "Full-stack web development training",
      "tenant_id": 1,
      "duration_weeks": 12,
      "status": "active",
      "start_date": "2025-07-01",
      "end_date": "2025-09-30",
      "max_participants": 25,
      "enrolled_count": 18
    }
  ],
  "pagination": { ... }
}
```

#### Create Program
```http
POST /programs
Authorization: Bearer <token>
Roles: super_admin, tenant_admin
Content-Type: application/json

{
  "name": "Data Science Fundamentals",
  "description": "Introduction to data science and machine learning",
  "duration_weeks": 8,
  "start_date": "2025-08-01",
  "end_date": "2025-09-30",
  "max_participants": 20,
  "category": "technology",
  "level": "beginner",
  "prerequisites": "Basic programming knowledge"
}
```

#### Program Modules
```http
GET /programs/{id}/modules
POST /programs/{id}/modules
PUT /programs/{program_id}/modules/{module_id}
DELETE /programs/{program_id}/modules/{module_id}
PUT /programs/{id}/modules/reorder
```

### 3. Evaluations/Tests

#### List Evaluations
```http
GET /evaluations?beneficiary_id=1&status=pending
Authorization: Bearer <token>
```

#### Submit Evaluation
```http
POST /evaluations/{id}/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "responses": [
    {
      "question_id": 1,
      "answer": "Option A"
    },
    {
      "question_id": 2,
      "answer": "True"
    },
    {
      "question_id": 3,
      "answer": "This is my essay response..."
    }
  ],
  "time_spent": 1800
}

Response:
{
  "message": "Evaluation submitted successfully",
  "submission_id": 123,
  "score": 85,
  "status": "completed"
}
```

#### Get Evaluation Results
```http
GET /evaluations/{id}/results
Authorization: Bearer <token>

Response:
{
  "evaluation_id": 1,
  "beneficiary_id": 2,
  "score": 85,
  "max_score": 100,
  "percentage": 85.0,
  "status": "completed",
  "submitted_at": "2025-06-03T10:30:00Z",
  "time_spent": 1800,
  "questions_answered": 20,
  "correct_answers": 17,
  "feedback": "Great performance! Areas for improvement..."
}
```

#### Analyze Evaluation with AI
```http
POST /evaluations/{id}/analyze
Authorization: Bearer <token>

Response:
{
  "analysis": {
    "strengths": ["Strong understanding of concepts", "Good problem-solving skills"],
    "weaknesses": ["Need to work on time management", "Review chapter 3"],
    "recommendations": ["Practice more mock tests", "Focus on weak areas"],
    "predicted_improvement": 10
  }
}
```

### 4. Documents Management

#### List Documents
```http
GET /documents?beneficiary_id=1&category=certificates
Authorization: Bearer <token>
```

#### Upload Document
```http
POST /documents
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- file: [binary]
- title: "Certificate of Completion"
- description: "Web Development Bootcamp Certificate"
- beneficiary_id: 1
- category: "certificates"
- version_control_enabled: true
```

#### Get Document
```http
GET /documents/{id}
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "title": "Certificate of Completion",
  "description": "Web Development Bootcamp Certificate",
  "filename": "certificate_john_doe.pdf",
  "file_size": 245632,
  "mime_type": "application/pdf",
  "category": "certificates",
  "current_version": 1,
  "version_control_enabled": true,
  "download_count": 5,
  "created_at": "2025-06-01T10:00:00Z"
}
```

#### Update Document
```http
PUT /documents/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Certificate Title",
  "description": "Updated description",
  "category": "achievements"
}
```

#### Download Document
```http
GET /documents/{id}/download
Authorization: Bearer <token>

Response: Binary file data
```

#### Share Document
```http
POST /documents/{id}/share
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_ids": [2, 3, 4],
  "message": "Please review this document",
  "expires_at": "2025-07-01T00:00:00Z"
}
```

### 5. Document Versioning

#### List Document Versions
```http
GET /documents/{id}/versions
Authorization: Bearer <token>

Response:
{
  "versions": [
    {
      "id": 1,
      "version_number": 1,
      "created_at": "2025-06-01T10:00:00Z",
      "created_by": "John Doe",
      "change_notes": "Initial version",
      "file_size": 245632,
      "is_current": false
    },
    {
      "id": 2,
      "version_number": 2,
      "created_at": "2025-06-02T14:00:00Z",
      "created_by": "John Doe",
      "change_notes": "Updated content",
      "file_size": 248901,
      "is_current": true
    }
  ]
}
```

#### Create New Version
```http
POST /documents/{id}/versions
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- file: [binary]
- change_notes: "Updated section 3 with new requirements"
```

#### Restore Version
```http
POST /documents/{id}/versions/{version_id}/restore
Authorization: Bearer <token>
```

#### Compare Versions
```http
POST /documents/{id}/versions/compare
Authorization: Bearer <token>
Content-Type: application/json

{
  "version1_id": 1,
  "version2_id": 2
}
```

### 6. Calendar & Appointments

#### List Appointments
```http
GET /appointments?beneficiary_id=1&start_date=2025-06-01&end_date=2025-06-30
Authorization: Bearer <token>
```

#### Create Appointment
```http
POST /appointments
Authorization: Bearer <token>
Content-Type: application/json

{
  "beneficiary_id": 1,
  "title": "Career Counseling Session",
  "description": "Monthly progress review",
  "start_time": "2025-06-15T10:00:00Z",
  "end_time": "2025-06-15T11:00:00Z",
  "location": "Online - Zoom",
  "reminder_enabled": true,
  "reminder_minutes": 15
}
```

### 7. Messaging System

#### List Message Threads
```http
GET /messages/threads
Authorization: Bearer <token>

Response:
{
  "threads": [
    {
      "id": 1,
      "title": "Project Discussion",
      "thread_type": "direct",
      "participants": [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Smith"}
      ],
      "last_message": {
        "content": "Thanks for the update",
        "sent_at": "2025-06-03T09:00:00Z",
        "sender": "Jane Smith"
      },
      "unread_count": 2
    }
  ]
}
```

#### Send Message
```http
POST /messages/threads/{thread_id}/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Hello, I have a question about the assignment",
  "attachments": []
}
```

### 8. Notifications

#### List Notifications
```http
GET /notifications?is_read=false
Authorization: Bearer <token>
```

#### Mark Notification as Read
```http
PUT /notifications/{id}/read
Authorization: Bearer <token>
```

#### Mark All as Read
```http
PUT /notifications/mark-all-read
Authorization: Bearer <token>
```

### 9. Reports & Analytics

#### Generate Report
```http
POST /reports/generate
Authorization: Bearer <token>
Roles: super_admin, tenant_admin, trainer
Content-Type: application/json

{
  "report_type": "beneficiary_progress",
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-06-30"
  },
  "filters": {
    "tenant_id": 1,
    "program_id": 5
  },
  "format": "pdf"
}

Response:
{
  "report_id": "rpt_123456",
  "status": "processing",
  "estimated_time": 30
}
```

#### Download Report
```http
GET /reports/{report_id}/download
Authorization: Bearer <token>
```

### 10. AI Features

#### Get AI Insights
```http
GET /ai/insights?beneficiary_id=1
Authorization: Bearer <token>

Response:
{
  "performance_trends": {
    "overall_progress": 78,
    "improvement_rate": 12,
    "strengths": ["Communication", "Problem-solving"],
    "areas_for_improvement": ["Time management", "Technical skills"]
  },
  "predictions": {
    "completion_probability": 0.85,
    "estimated_completion_date": "2025-08-15"
  }
}
```

#### Generate AI Content
```http
POST /ai/content/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_type": "quiz",
  "topic": "JavaScript Fundamentals",
  "difficulty": "intermediate",
  "num_questions": 10
}
```

## WebSocket Events

### Connection
```javascript
const socket = io('http://localhost:5001', {
  auth: {
    token: 'your-jwt-token'
  }
});
```

### Real-time Events

#### Message Events
- `message_sent` - New message in a thread
- `typing` - User is typing
- `mark_read` - Messages marked as read

#### Program Events
- `program_created` - New program created
- `program_updated` - Program details updated
- `program_deleted` - Program deleted

#### Notification Events
- `new_notification` - New notification received

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    // Optional additional error details
  }
}
```

### Common Error Codes
- `validation_error` - Invalid request data
- `unauthorized` - Missing or invalid authentication
- `forbidden` - Insufficient permissions
- `not_found` - Resource not found
- `conflict` - Resource conflict (e.g., duplicate email)
- `server_error` - Internal server error

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `500` - Internal Server Error

## Rate Limiting

API requests are rate-limited to prevent abuse:
- Authenticated requests: 1000 per hour
- Unauthenticated requests: 100 per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1623456789
```

## Pagination

List endpoints support pagination with these parameters:
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10, max: 100)

Pagination metadata is included in responses:
```json
{
  "items": [...],
  "page": 1,
  "per_page": 10,
  "total": 100,
  "pages": 10
}
```

## Filtering and Sorting

Most list endpoints support filtering and sorting:
- `sort_by` - Field to sort by
- `sort_dir` - Sort direction (`asc` or `desc`)
- Various filter parameters specific to each endpoint

## Versioning

The API uses URL versioning. The current version is v1, accessible at `/api/v1/`.
Future versions will be available at `/api/v2/`, etc.

## Testing

### Using cURL
```bash
# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bdc.com","password":"Admin123!"}'

# Get beneficiaries
curl -X GET http://localhost:5001/api/beneficiaries \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Postman
1. Import the OpenAPI specification
2. Set the base URL
3. Configure authentication
4. Start making requests

## Background Tasks

The system uses Celery for background tasks:
- Email notifications
- Report generation
- Data cleanup
- Scheduled reminders

Background task status can be checked via:
```http
GET /tasks/{task_id}/status
```

## Security Considerations

1. **HTTPS Only**: All production API calls must use HTTPS
2. **JWT Expiration**: Access tokens expire after 15 minutes
3. **CORS**: Configured for specific allowed origins
4. **Input Validation**: All inputs are validated and sanitized
5. **SQL Injection Protection**: Using parameterized queries
6. **XSS Protection**: Output encoding for user-generated content

## Changelog

### Version 2025.06 (June 3, 2025)
- Added emergency contact fields to beneficiaries
- Implemented document versioning system
- Added test submission and results endpoints
- Enhanced real-time messaging with WebSocket
- Added AI analysis endpoints for evaluations
- Implemented background task scheduler with Celery
- Added comprehensive CRUD operations for documents
- Fixed model-API field mismatches

### Version 2025.05 (May 31, 2025)
- Initial API documentation
- Basic CRUD operations for main entities
- Authentication and authorization system
- WebSocket support for real-time features

---

For questions or support, contact: support@bdc.com