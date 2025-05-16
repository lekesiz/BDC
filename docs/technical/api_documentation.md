# BDC API Documentation

## Overview

The BDC (Beneficiary Development Center) API provides RESTful endpoints for managing beneficiaries, assessments, appointments, and more. All endpoints require authentication unless otherwise specified.

## Base URL

```
Development: http://localhost:5000/api
Production: https://api.bdc.com/api
```

## Authentication

The API uses JWT (JSON Web Token) based authentication. To authenticate:

1. Obtain a token by calling the login endpoint
2. Include the token in the Authorization header for all subsequent requests

```
Authorization: Bearer <your-jwt-token>
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "Error message",
  "status": 400,
  "details": "Additional error information"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Endpoints

### Authentication

#### POST /api/auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "trainer"
  }
}
```

#### POST /api/auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "role": "trainer"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

#### POST /api/auth/logout
Logout current user.

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### User Management

#### GET /api/users
Get list of users (Admin only).

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `role` (optional): Filter by role

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "role": "trainer",
      "is_active": true
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 10
}
```

#### GET /api/users/{id}
Get specific user details.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "trainer",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### PUT /api/users/{id}
Update user information.

**Request:**
```json
{
  "name": "Jane Doe",
  "role": "admin"
}
```

**Response:**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "name": "Jane Doe",
    "role": "admin"
  }
}
```

### Beneficiary Management

#### GET /api/beneficiaries
Get list of beneficiaries.

**Query Parameters:**
- `page` (optional): Page number
- `per_page` (optional): Items per page
- `trainer_id` (optional): Filter by trainer
- `search` (optional): Search by name or email

**Response:**
```json
{
  "beneficiaries": [
    {
      "id": 1,
      "user_id": 2,
      "user": {
        "name": "Alice Smith",
        "email": "alice@example.com"
      },
      "trainer_id": 1,
      "trainer": {
        "name": "John Doe"
      },
      "assessment_count": 5,
      "last_assessment_date": "2023-06-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 10
}
```

#### GET /api/beneficiaries/{id}
Get specific beneficiary details.

**Response:**
```json
{
  "id": 1,
  "user_id": 2,
  "user": {
    "name": "Alice Smith",
    "email": "alice@example.com"
  },
  "trainer_id": 1,
  "trainer": {
    "name": "John Doe"
  },
  "profile": {
    "phone": "+1234567890",
    "address": "123 Main St",
    "emergency_contact": "Bob Smith"
  },
  "assessments": [...],
  "appointments": [...]
}
```

#### POST /api/beneficiaries
Create a new beneficiary.

**Request:**
```json
{
  "user_id": 2,
  "trainer_id": 1,
  "profile": {
    "phone": "+1234567890",
    "address": "123 Main St"
  }
}
```

**Response:**
```json
{
  "message": "Beneficiary created successfully",
  "beneficiary": {
    "id": 1,
    "user_id": 2,
    "trainer_id": 1
  }
}
```

#### GET /api/beneficiaries/{id}/dashboard
Get beneficiary dashboard data.

**Response:**
```json
{
  "beneficiary": {
    "id": 1,
    "name": "Alice Smith"
  },
  "stats": {
    "total_assessments": 10,
    "completed_assessments": 8,
    "average_score": 85.5,
    "improvement_rate": 15.2
  },
  "recent_assessments": [...],
  "upcoming_appointments": [...],
  "progress_chart": {
    "labels": ["Jan", "Feb", "Mar"],
    "data": [75, 80, 85]
  }
}
```

### Assessment Management

#### GET /api/assessments
Get list of assessments.

**Query Parameters:**
- `beneficiary_id` (optional): Filter by beneficiary
- `trainer_id` (optional): Filter by trainer
- `status` (optional): Filter by status
- `type` (optional): Filter by assessment type

**Response:**
```json
{
  "assessments": [
    {
      "id": 1,
      "title": "Initial Assessment",
      "type": "cognitive",
      "beneficiary_id": 1,
      "trainer_id": 1,
      "status": "completed",
      "score": 85,
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 200,
  "page": 1,
  "per_page": 10
}
```

#### GET /api/assessments/{id}
Get specific assessment details.

**Response:**
```json
{
  "id": 1,
  "title": "Initial Assessment",
  "type": "cognitive",
  "description": "Assessment description",
  "beneficiary": {
    "id": 1,
    "name": "Alice Smith"
  },
  "trainer": {
    "id": 1,
    "name": "John Doe"
  },
  "questions": [...],
  "responses": [...],
  "results": {
    "score": 85,
    "analysis": "AI analysis results",
    "recommendations": [...]
  }
}
```

#### POST /api/assessments
Create a new assessment.

**Request:**
```json
{
  "title": "Monthly Assessment",
  "type": "cognitive",
  "beneficiary_id": 1,
  "questions": [
    {
      "text": "Question 1",
      "type": "multiple_choice",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Assessment created successfully",
  "assessment": {
    "id": 1,
    "title": "Monthly Assessment",
    "status": "draft"
  }
}
```

#### POST /api/assessments/{id}/submit
Submit assessment responses.

**Request:**
```json
{
  "responses": [
    {
      "question_id": 1,
      "answer": "A"
    },
    {
      "question_id": 2,
      "answer": "B"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Assessment submitted successfully",
  "results": {
    "score": 85,
    "correct_answers": 17,
    "total_questions": 20
  }
}
```

### Appointment Management

#### GET /api/appointments
Get list of appointments.

**Query Parameters:**
- `beneficiary_id` (optional): Filter by beneficiary
- `trainer_id` (optional): Filter by trainer
- `status` (optional): Filter by status
- `start_date` (optional): Filter by start date
- `end_date` (optional): Filter by end date

**Response:**
```json
{
  "appointments": [
    {
      "id": 1,
      "title": "Weekly Check-in",
      "beneficiary_id": 1,
      "trainer_id": 1,
      "start_time": "2023-06-01T10:00:00Z",
      "end_time": "2023-06-01T11:00:00Z",
      "status": "scheduled",
      "location": "Room 101"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 10
}
```

#### POST /api/appointments
Create a new appointment.

**Request:**
```json
{
  "title": "Assessment Review",
  "beneficiary_id": 1,
  "start_time": "2023-06-01T10:00:00Z",
  "end_time": "2023-06-01T11:00:00Z",
  "location": "Room 101",
  "notes": "Review recent assessment results"
}
```

**Response:**
```json
{
  "message": "Appointment created successfully",
  "appointment": {
    "id": 1,
    "title": "Assessment Review",
    "status": "scheduled"
  }
}
```

#### PUT /api/appointments/{id}
Update appointment details.

**Request:**
```json
{
  "start_time": "2023-06-01T14:00:00Z",
  "end_time": "2023-06-01T15:00:00Z",
  "location": "Room 202"
}
```

**Response:**
```json
{
  "message": "Appointment updated successfully",
  "appointment": {
    "id": 1,
    "start_time": "2023-06-01T14:00:00Z",
    "end_time": "2023-06-01T15:00:00Z"
  }
}
```

#### DELETE /api/appointments/{id}
Cancel an appointment.

**Response:**
```json
{
  "message": "Appointment cancelled successfully"
}
```

### Document Management

#### GET /api/documents
Get list of documents.

**Query Parameters:**
- `category` (optional): Filter by category
- `beneficiary_id` (optional): Filter by beneficiary
- `shared_with_me` (optional): Show documents shared with current user

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "assessment_report.pdf",
      "category": "reports",
      "size": 1024000,
      "uploaded_by": {
        "id": 1,
        "name": "John Doe"
      },
      "uploaded_at": "2023-01-01T00:00:00Z",
      "shared_with": ["user@example.com"]
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

#### POST /api/documents/upload
Upload a new document.

**Request:** (multipart/form-data)
- `file`: The document file
- `category`: Document category
- `description`: Optional description
- `beneficiary_id`: Optional beneficiary association

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document": {
    "id": 1,
    "filename": "assessment_report.pdf",
    "url": "/api/documents/1/download"
  }
}
```

#### GET /api/documents/{id}/download
Download a document.

**Response:** Binary file stream

#### POST /api/documents/{id}/share
Share a document with other users.

**Request:**
```json
{
  "user_ids": [2, 3, 4],
  "message": "Please review this document"
}
```

**Response:**
```json
{
  "message": "Document shared successfully",
  "shared_with": ["user2@example.com", "user3@example.com", "user4@example.com"]
}
```

### Messaging

#### GET /api/messages
Get list of messages.

**Query Parameters:**
- `unread` (optional): Show only unread messages
- `sender_id` (optional): Filter by sender

**Response:**
```json
{
  "messages": [
    {
      "id": 1,
      "sender": {
        "id": 2,
        "name": "Alice Smith"
      },
      "subject": "Assessment completed",
      "content": "I've completed the assessment...",
      "created_at": "2023-01-01T00:00:00Z",
      "read": false
    }
  ],
  "total": 10,
  "page": 1,
  "per_page": 10
}
```

#### POST /api/messages
Send a new message.

**Request:**
```json
{
  "recipient_id": 2,
  "subject": "Meeting reminder",
  "content": "Don't forget our meeting tomorrow at 10 AM"
}
```

**Response:**
```json
{
  "message": "Message sent successfully",
  "message_id": 1
}
```

#### PUT /api/messages/{id}/read
Mark a message as read.

**Response:**
```json
{
  "message": "Message marked as read"
}
```

### Notifications

#### GET /api/notifications
Get list of notifications.

**Query Parameters:**
- `unread` (optional): Show only unread notifications
- `type` (optional): Filter by notification type

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "type": "appointment_reminder",
      "title": "Appointment in 1 hour",
      "message": "Your appointment with John Doe is in 1 hour",
      "created_at": "2023-01-01T09:00:00Z",
      "read": false
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 10
}
```

#### PUT /api/notifications/{id}/read
Mark a notification as read.

**Response:**
```json
{
  "message": "Notification marked as read"
}
```

#### PUT /api/notifications/read-all
Mark all notifications as read.

**Response:**
```json
{
  "message": "All notifications marked as read",
  "count": 5
}
```

### Reports

#### GET /api/reports/beneficiary/{id}
Generate beneficiary progress report.

**Query Parameters:**
- `start_date` (optional): Report start date
- `end_date` (optional): Report end date
- `format` (optional): Report format (pdf, excel)

**Response:**
```json
{
  "report": {
    "beneficiary": {
      "id": 1,
      "name": "Alice Smith"
    },
    "period": {
      "start": "2023-01-01",
      "end": "2023-06-01"
    },
    "summary": {
      "total_assessments": 10,
      "average_score": 85.5,
      "improvement_rate": 15.2
    },
    "assessments": [...],
    "appointments": [...],
    "recommendations": [...]
  }
}
```

#### GET /api/reports/trainer/{id}
Generate trainer performance report.

**Response:**
```json
{
  "report": {
    "trainer": {
      "id": 1,
      "name": "John Doe"
    },
    "beneficiaries": {
      "total": 10,
      "active": 8
    },
    "assessments": {
      "conducted": 50,
      "average_completion_time": "2.5 hours"
    },
    "appointments": {
      "scheduled": 100,
      "completed": 95,
      "cancelled": 5
    }
  }
}
```

### AI Analysis

#### POST /api/ai/analyze-assessment
Analyze assessment results using AI.

**Request:**
```json
{
  "assessment_id": 1,
  "analysis_type": "comprehensive"
}
```

**Response:**
```json
{
  "analysis": {
    "strengths": [
      "Strong analytical skills",
      "Good problem-solving ability"
    ],
    "areas_for_improvement": [
      "Time management",
      "Communication skills"
    ],
    "recommendations": [
      "Focus on time-bound exercises",
      "Practice public speaking"
    ],
    "predicted_progress": {
      "1_month": 88,
      "3_months": 92,
      "6_months": 95
    }
  }
}
```

#### POST /api/ai/generate-questions
Generate assessment questions using AI.

**Request:**
```json
{
  "topic": "Mathematics",
  "difficulty": "intermediate",
  "count": 10,
  "question_types": ["multiple_choice", "true_false"]
}
```

**Response:**
```json
{
  "questions": [
    {
      "text": "What is the derivative of x²?",
      "type": "multiple_choice",
      "options": ["2x", "x²", "2", "x"],
      "correct_answer": "2x",
      "difficulty": "intermediate"
    }
  ]
}
```

### System Monitoring

#### GET /api/monitoring/health
Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai_service": "available"
  },
  "uptime": 3600,
  "version": "1.0.0"
}
```

#### GET /api/monitoring/metrics
Get system performance metrics.

**Response:**
```json
{
  "metrics": {
    "requests_per_minute": 120,
    "average_response_time": 250,
    "error_rate": 0.01,
    "active_users": 45,
    "cpu_usage": 35,
    "memory_usage": 60
  }
}
```

## WebSocket Events

The application supports real-time communication via WebSocket for certain features.

### Connection
```javascript
const socket = io('http://localhost:5000', {
  auth: {
    token: 'your-jwt-token'
  }
});
```

### Events

#### notification
Receive real-time notifications.
```javascript
socket.on('notification', (data) => {
  console.log('New notification:', data);
});
```

#### message
Receive real-time messages.
```javascript
socket.on('message', (data) => {
  console.log('New message:', data);
});
```

#### assessment_update
Receive assessment status updates.
```javascript
socket.on('assessment_update', (data) => {
  console.log('Assessment update:', data);
});
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- General endpoints: 100 requests per minute
- File uploads: 10 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1623456789
```

## Pagination

List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)

Pagination metadata is included in responses:
```json
{
  "data": [...],
  "total": 500,
  "page": 1,
  "per_page": 10,
  "total_pages": 50
}
```

## Filtering and Sorting

List endpoints support filtering and sorting:
- Filter: Use query parameters specific to each endpoint
- Sort: Use `sort` parameter with format `field:direction` (e.g., `sort=created_at:desc`)

## Versioning

The API uses URL versioning. The current version is v1. Future versions will be accessible at:
```
/api/v2/...
```

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for the API. Allowed origins are configured in the server settings.

## Security

- All API communication should use HTTPS in production
- JWT tokens expire after 24 hours
- Sensitive data is encrypted at rest
- Input validation is performed on all endpoints
- SQL injection protection is implemented

## Support

For API support and questions:
- Email: api-support@bdc.com
- Documentation: https://docs.bdc.com/api
- Status: https://status.bdc.com