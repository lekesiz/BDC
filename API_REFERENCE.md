# BDC Platform - API Reference

## Overview

The BDC Platform API is a RESTful service that provides comprehensive functionality for managing beneficiaries, programs, evaluations, and educational resources. This document provides detailed information about all available API endpoints.

## Base URL

```
Production: https://api.bdc-platform.com
Development: http://localhost:5001/api
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

## Content Type

All requests and responses use JSON:

```http
Content-Type: application/json
```

## Rate Limiting

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

## Error Responses

Standard error response format:

```json
{
  "error": "Error message",
  "message": "Detailed error description",
  "code": "ERROR_CODE",
  "status": 400
}
```

---

# API Endpoints

## Authentication

### Login

```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "refresh_token": "eyJ0eXAiOiJKV1Q...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "trainer"
  }
}
```

### Register

```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "student"
}
```

### Refresh Token

```http
POST /api/auth/refresh
```

**Headers:**
```http
Authorization: Bearer <refresh-token>
```

### Logout

```http
POST /api/auth/logout
```

### Forgot Password

```http
POST /api/auth/forgot-password
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

### Reset Password

```http
POST /api/auth/reset-password
```

**Request Body:**
```json
{
  "token": "reset-token",
  "new_password": "NewSecurePass123!"
}
```

---

## Users

### List Users

```http
GET /api/users
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20)
- `search` (string): Search by name or email
- `role` (string): Filter by role
- `tenant_id` (uuid): Filter by tenant

**Response:**
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "trainer",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

### Get User

```http
GET /api/users/:id
```

### Create User

```http
POST /api/users
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "first_name": "New",
  "last_name": "User",
  "role": "trainer",
  "tenant_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Update User

```http
PUT /api/users/:id
```

**Request Body:**
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "is_active": true
}
```

### Delete User

```http
DELETE /api/users/:id
```

---

## Beneficiaries

### List Beneficiaries

```http
GET /api/beneficiaries
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `search` (string): Search by name, email, or phone
- `status` (string): Filter by status
- `program_id` (uuid): Filter by program enrollment

**Response:**
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "first_name": "Alice",
      "last_name": "Johnson",
      "email": "alice@example.com",
      "phone": "+1234567890",
      "date_of_birth": "1990-01-01",
      "status": "active",
      "enrollment_count": 3,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "pages": 3
  }
}
```

### Get Beneficiary

```http
GET /api/beneficiaries/:id
```

**Response includes:**
- Basic information
- Enrollment history
- Evaluation results
- Document list
- Progress metrics

### Create Beneficiary

```http
POST /api/beneficiaries
```

**Request Body:**
```json
{
  "first_name": "New",
  "last_name": "Beneficiary",
  "email": "beneficiary@example.com",
  "phone": "+1234567890",
  "date_of_birth": "1995-05-15",
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  },
  "emergency_contact": {
    "name": "Emergency Contact",
    "phone": "+0987654321",
    "relationship": "Parent"
  }
}
```

### Update Beneficiary

```http
PUT /api/beneficiaries/:id
```

### Delete Beneficiary

```http
DELETE /api/beneficiaries/:id
```

### Beneficiary Documents

```http
GET /api/beneficiaries/:id/documents
POST /api/beneficiaries/:id/documents
DELETE /api/beneficiaries/:id/documents/:documentId
```

### Beneficiary Evaluations

```http
GET /api/beneficiaries/:id/evaluations
```

### Beneficiary Progress

```http
GET /api/beneficiaries/:id/progress
```

---

## Programs

### List Programs

```http
GET /api/programs
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `search` (string): Search by name or description
- `status` (string): active, completed, upcoming
- `category` (string): Filter by category

### Get Program

```http
GET /api/programs/:id
```

### Create Program

```http
POST /api/programs
```

**Request Body:**
```json
{
  "name": "Advanced Training Program",
  "description": "Comprehensive training program",
  "category": "professional_development",
  "start_date": "2024-03-01",
  "end_date": "2024-06-30",
  "capacity": 30,
  "requirements": ["Basic knowledge", "Commitment"],
  "modules": [
    {
      "name": "Module 1",
      "description": "Introduction",
      "duration_hours": 10,
      "order": 1
    }
  ]
}
```

### Update Program

```http
PUT /api/programs/:id
```

### Delete Program

```http
DELETE /api/programs/:id
```

### Program Enrollment

```http
POST /api/programs/:id/enroll
```

**Request Body:**
```json
{
  "beneficiary_id": "123e4567-e89b-12d3-a456-426614174000",
  "start_date": "2024-03-01"
}
```

### Program Sessions

```http
GET /api/programs/:id/sessions
POST /api/programs/:id/sessions
PUT /api/programs/:id/sessions/:sessionId
DELETE /api/programs/:id/sessions/:sessionId
```

---

## Evaluations

### List Evaluations

```http
GET /api/evaluations
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `type` (string): quiz, assignment, exam
- `program_id` (uuid): Filter by program
- `status` (string): draft, published, completed

### Get Evaluation

```http
GET /api/evaluations/:id
```

### Create Evaluation

```http
POST /api/evaluations
```

**Request Body:**
```json
{
  "name": "Midterm Exam",
  "description": "Program midterm evaluation",
  "type": "exam",
  "program_id": "123e4567-e89b-12d3-a456-426614174000",
  "duration_minutes": 120,
  "passing_score": 70,
  "questions": [
    {
      "type": "multiple_choice",
      "question": "What is...?",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "B",
      "points": 10
    }
  ]
}
```

### Submit Evaluation

```http
POST /api/evaluations/:id/submit
```

**Request Body:**
```json
{
  "beneficiary_id": "123e4567-e89b-12d3-a456-426614174000",
  "answers": [
    {
      "question_id": "q1",
      "answer": "B"
    }
  ],
  "started_at": "2024-01-01T10:00:00Z",
  "submitted_at": "2024-01-01T11:30:00Z"
}
```

---

## Documents

### List Documents

```http
GET /api/documents
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `type` (string): Filter by document type
- `folder_id` (uuid): Filter by folder

### Upload Document

```http
POST /api/documents
```

**Request Body (multipart/form-data):**
- `file`: Document file
- `name`: Document name
- `description`: Document description
- `folder_id`: Target folder ID
- `tags`: Comma-separated tags

### Get Document

```http
GET /api/documents/:id
```

### Download Document

```http
GET /api/documents/:id/download
```

### Delete Document

```http
DELETE /api/documents/:id
```

---

## Appointments

### List Appointments

```http
GET /api/appointments
```

**Query Parameters:**
- `start_date` (date): Filter by start date
- `end_date` (date): Filter by end date
- `trainer_id` (uuid): Filter by trainer
- `beneficiary_id` (uuid): Filter by beneficiary
- `status` (string): scheduled, completed, cancelled

### Create Appointment

```http
POST /api/appointments
```

**Request Body:**
```json
{
  "title": "Training Session",
  "description": "One-on-one training",
  "trainer_id": "123e4567-e89b-12d3-a456-426614174000",
  "beneficiary_id": "123e4567-e89b-12d3-a456-426614174000",
  "start_time": "2024-03-01T10:00:00Z",
  "end_time": "2024-03-01T11:00:00Z",
  "location": "Room 101",
  "meeting_link": "https://meet.example.com/abc123"
}
```

### Update Appointment

```http
PUT /api/appointments/:id
```

### Cancel Appointment

```http
POST /api/appointments/:id/cancel
```

**Request Body:**
```json
{
  "reason": "Scheduling conflict"
}
```

---

## Notifications

### List Notifications

```http
GET /api/notifications
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `unread_only` (boolean): Show only unread
- `type` (string): Filter by notification type

### Mark as Read

```http
PUT /api/notifications/:id/read
```

### Mark All as Read

```http
PUT /api/notifications/read-all
```

### Delete Notification

```http
DELETE /api/notifications/:id
```

---

## Analytics

### Dashboard Statistics

```http
GET /api/v2/analytics/dashboard
```

**Query Parameters:**
- `period` (string): today, week, month, year
- `tenant_id` (uuid): Filter by tenant

**Response:**
```json
{
  "beneficiaries": {
    "total": 500,
    "active": 450,
    "new_this_month": 25
  },
  "programs": {
    "total": 20,
    "active": 15,
    "completion_rate": 85.5
  },
  "evaluations": {
    "total": 100,
    "completed": 850,
    "average_score": 78.3
  },
  "engagement": {
    "daily_active_users": 120,
    "average_session_duration": "45m"
  }
}
```

### Trend Analysis

```http
GET /api/v2/analytics/trends
```

**Query Parameters:**
- `metric` (string): beneficiaries, programs, evaluations
- `period` (string): day, week, month
- `start_date` (date): Start date
- `end_date` (date): End date

### Export Analytics

```http
POST /api/v2/analytics/export
```

**Request Body:**
```json
{
  "metrics": ["beneficiaries", "programs", "evaluations"],
  "period": "month",
  "format": "excel",
  "email": "user@example.com"
}
```

---

## Reports

### List Report Templates

```http
GET /api/v2/reports/templates
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `category` (string): Filter by category
- `tags` (string): Filter by tags

### Create Report Template

```http
POST /api/v2/reports/templates
```

**Request Body:**
```json
{
  "name": "Monthly Progress Report",
  "description": "Monthly beneficiary progress report",
  "category": "progress",
  "template_content": "...",
  "parameters": [
    {
      "name": "month",
      "type": "date",
      "required": true
    }
  ],
  "output_formats": ["pdf", "excel"]
}
```

### Generate Report

```http
POST /api/v2/reports/generate
```

**Request Body:**
```json
{
  "template_id": "123e4567-e89b-12d3-a456-426614174000",
  "parameters": {
    "month": "2024-01",
    "include_charts": true
  },
  "output_format": "pdf",
  "delivery": {
    "method": "email",
    "recipients": ["user@example.com"]
  }
}
```

### Report History

```http
GET /api/v2/reports/history
```

### Download Report

```http
GET /api/v2/reports/history/:id/download
```

### Schedule Report

```http
POST /api/v2/reports/schedules
```

**Request Body:**
```json
{
  "template_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Weekly Progress Report",
  "cron_expression": "0 9 * * MON",
  "parameters": {
    "period": "week"
  },
  "output_format": "pdf",
  "recipients": ["manager@example.com"]
}
```

---

## Global Search

### Search All Entities

```http
GET /api/v2/search/global
```

**Query Parameters:**
- `q` (string): Search query (required)
- `types` (array): Entity types to search
- `limit` (integer): Results per type (default: 5)
- `page` (integer): Page number

**Response:**
```json
{
  "results": {
    "beneficiaries": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "type": "beneficiary",
        "title": "John Doe",
        "description": "john.doe@example.com",
        "url": "/beneficiaries/123e4567-e89b-12d3-a456-426614174000",
        "relevance": 0.95
      }
    ],
    "programs": [...],
    "documents": [...]
  },
  "total": 25,
  "query": "john"
}
```

### Search Suggestions

```http
GET /api/v2/search/suggestions
```

**Query Parameters:**
- `q` (string): Partial search query
- `limit` (integer): Number of suggestions (default: 10)

---

## Bulk Operations

### Execute Bulk Operation

```http
POST /api/v2/bulk/operations
```

**Request Body:**
```json
{
  "entity_type": "beneficiaries",
  "operation": "update",
  "entity_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "234e5678-e89b-12d3-a456-426614174001"
  ],
  "data": {
    "status": "active"
  }
}
```

**Supported Operations:**
- `create`: Bulk create entities
- `update`: Bulk update entities
- `delete`: Bulk delete entities
- `assign`: Bulk assign to programs
- `export`: Bulk export data
- `import`: Bulk import data

### Check Operation Status

```http
GET /api/v2/bulk/operations/:id/status
```

**Response:**
```json
{
  "id": "op_123456",
  "status": "in_progress",
  "progress": {
    "total": 100,
    "processed": 45,
    "succeeded": 43,
    "failed": 2
  },
  "errors": [
    {
      "entity_id": "...",
      "error": "Validation failed"
    }
  ]
}
```

---

## Health & Monitoring

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### Detailed Health Check

```http
GET /api/v2/health
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 2
    },
    "storage": {
      "status": "healthy",
      "available_space_gb": 450
    }
  },
  "metrics": {
    "uptime_seconds": 86400,
    "request_count": 10000,
    "error_rate": 0.01
  }
}
```

---

## WebSocket Events

### Connection

```javascript
const socket = io('wss://api.bdc-platform.com', {
  auth: {
    token: 'your-jwt-token'
  }
});
```

### Events

#### Join Room

```javascript
socket.emit('join', {
  room: 'beneficiary_123',
  user_id: 'user_456'
});
```

#### Real-time Updates

```javascript
// Listen for updates
socket.on('beneficiary_updated', (data) => {
  console.log('Beneficiary updated:', data);
});

socket.on('notification', (data) => {
  console.log('New notification:', data);
});

socket.on('evaluation_submitted', (data) => {
  console.log('Evaluation submitted:', data);
});
```

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication endpoints**: 10 requests per minute
- **Public endpoints**: 100 requests per hour
- **Authenticated endpoints**: 1000 requests per hour
- **Bulk operations**: 10 requests per hour

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

---

## Pagination

Standard pagination parameters:

- `page`: Page number (starts at 1)
- `per_page`: Items per page (max: 100)

Pagination response:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Changelog

### Version 2.0 (Current)
- Added bulk operations endpoints
- Added global search functionality
- Enhanced analytics endpoints
- Added report generation and scheduling
- Improved error responses

### Version 1.0
- Initial API release
- Basic CRUD operations
- Authentication and authorization
- File upload support

---

*Generated: January 2025*
*API Version: 2.0*