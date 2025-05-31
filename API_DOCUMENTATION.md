# BDC API Documentation

## Overview
The BDC API provides RESTful endpoints for managing beneficiaries, programs, evaluations, and related resources. All API requests must include proper authentication headers.

## Base URL
```
Production: https://api.yourdomain.com
Development: http://localhost:5001
```

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Common Headers
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <jwt_token>
X-API-Version: 1.0
```

## Error Responses
All errors follow a consistent format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": "Specific field error"
    }
  },
  "status": 400
}
```

## Rate Limiting
- Default: 1000 requests per hour
- Authentication endpoints: 5 requests per minute
- File uploads: 10 requests per hour

## API Endpoints

### Authentication

#### Login
```http
POST /api/auth/login
```
Request:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember": true
}
```
Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "trainer",
    "full_name": "John Doe"
  }
}
```

#### Register
```http
POST /api/auth/register
```
Request:
```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "full_name": "Jane Smith",
  "role": "student"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
```
Headers:
```http
Authorization: Bearer <refresh_token>
```
Response:
```json
{
  "access_token": "new_access_token"
}
```

#### Logout
```http
POST /api/auth/logout
```
Headers:
```http
Authorization: Bearer <access_token>
```

### Users

#### List Users
```http
GET /api/users
```
Query Parameters:
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20)
- `search` (string): Search by name or email
- `role` (string): Filter by role
- `tenant_id` (int): Filter by tenant

Response:
```json
{
  "items": [
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "trainer",
      "tenant_id": 1,
      "created_at": "2024-01-15T10:00:00Z",
      "last_login": "2024-03-20T15:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8
}
```

#### Get User
```http
GET /api/users/{id}
```
Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "trainer",
  "tenant": {
    "id": 1,
    "name": "Acme Corp"
  },
  "permissions": ["view_beneficiaries", "create_evaluations"],
  "profile": {
    "phone": "+1234567890",
    "address": "123 Main St",
    "bio": "Experienced trainer"
  }
}
```

#### Create User
```http
POST /api/users
```
Request:
```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "full_name": "New User",
  "role": "trainer",
  "tenant_id": 1
}
```

#### Update User
```http
PUT /api/users/{id}
```
Request:
```json
{
  "full_name": "Updated Name",
  "email": "updated@example.com",
  "role": "admin"
}
```

#### Delete User
```http
DELETE /api/users/{id}
```

### Beneficiaries

#### List Beneficiaries
```http
GET /api/beneficiaries
```
Query Parameters:
- `page` (int): Page number
- `per_page` (int): Items per page
- `search` (string): Search by name or email
- `trainer_id` (int): Filter by trainer
- `program_id` (int): Filter by program
- `status` (string): Filter by status

Response:
```json
{
  "items": [
    {
      "id": 1,
      "full_name": "Jane Student",
      "email": "jane@example.com",
      "status": "active",
      "trainer": {
        "id": 5,
        "full_name": "John Trainer"
      },
      "programs": ["Web Development", "Data Science"],
      "progress": {
        "completed_evaluations": 5,
        "total_evaluations": 10,
        "average_score": 85
      }
    }
  ],
  "total": 250,
  "page": 1,
  "per_page": 20
}
```

#### Get Beneficiary
```http
GET /api/beneficiaries/{id}
```
Response:
```json
{
  "id": 1,
  "full_name": "Jane Student",
  "email": "jane@example.com",
  "phone": "+1234567890",
  "address": "456 Oak St",
  "date_of_birth": "1995-05-15",
  "status": "active",
  "trainer": {
    "id": 5,
    "full_name": "John Trainer",
    "email": "john@example.com"
  },
  "emergency_contact": {
    "name": "Emergency Contact",
    "phone": "+0987654321",
    "relationship": "Parent"
  },
  "programs": [
    {
      "id": 1,
      "name": "Web Development",
      "status": "in_progress",
      "start_date": "2024-01-01",
      "end_date": "2024-06-30"
    }
  ],
  "evaluations": [
    {
      "id": 1,
      "title": "HTML Basics",
      "score": 90,
      "completed_at": "2024-02-15T10:00:00Z"
    }
  ]
}
```

#### Create Beneficiary
```http
POST /api/beneficiaries
```
Request:
```json
{
  "full_name": "New Student",
  "email": "newstudent@example.com",
  "phone": "+1234567890",
  "date_of_birth": "2000-01-01",
  "trainer_id": 5,
  "program_ids": [1, 2]
}
```

#### Update Beneficiary
```http
PUT /api/beneficiaries/{id}
```
Request:
```json
{
  "full_name": "Updated Name",
  "status": "inactive",
  "trainer_id": 6
}
```

#### Assign Trainer
```http
POST /api/beneficiaries/{id}/assign-trainer
```
Request:
```json
{
  "trainer_id": 5
}
```

### Programs

#### List Programs
```http
GET /api/programs
```
Query Parameters:
- `status` (string): active, inactive, completed
- `category` (string): Filter by category
- `trainer_id` (int): Filter by trainer

Response:
```json
{
  "items": [
    {
      "id": 1,
      "name": "Web Development Bootcamp",
      "description": "Learn modern web development",
      "category": "Technology",
      "duration_weeks": 12,
      "status": "active",
      "capacity": 30,
      "enrolled": 25,
      "start_date": "2024-01-01",
      "end_date": "2024-03-31",
      "trainers": [
        {
          "id": 5,
          "full_name": "John Trainer"
        }
      ]
    }
  ],
  "total": 15
}
```

#### Get Program
```http
GET /api/programs/{id}
```
Response:
```json
{
  "id": 1,
  "name": "Web Development Bootcamp",
  "description": "Comprehensive web development training",
  "category": "Technology",
  "duration_weeks": 12,
  "status": "active",
  "capacity": 30,
  "enrolled": 25,
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "schedule": {
    "days": ["Monday", "Wednesday", "Friday"],
    "time": "09:00-12:00"
  },
  "curriculum": [
    {
      "week": 1,
      "topic": "HTML & CSS Basics",
      "objectives": ["Understand HTML structure", "Apply CSS styling"]
    }
  ],
  "trainers": [
    {
      "id": 5,
      "full_name": "John Trainer",
      "specialization": "Frontend Development"
    }
  ],
  "participants": [
    {
      "id": 1,
      "full_name": "Jane Student",
      "progress": 45
    }
  ]
}
```

#### Get Program Students
```http
GET /api/programs/{id}/students
```
Returns a simplified list of students (beneficiaries) enrolled in a specific program.

Response:
```json
[
  {
    "id": 1,
    "full_name": "Jane Student",
    "email": "jane@example.com"
  },
  {
    "id": 2,
    "full_name": "John Student",
    "email": "john@example.com"
  }
]
```

#### Create Program
```http
POST /api/programs
```
Request:
```json
{
  "name": "Data Science Fundamentals",
  "description": "Introduction to data science",
  "category": "Data Science",
  "duration_weeks": 8,
  "capacity": 20,
  "start_date": "2024-04-01",
  "end_date": "2024-05-31",
  "trainer_ids": [5, 6]
}
```

#### Enroll Beneficiary
```http
POST /api/programs/{id}/enroll
```
Request:
```json
{
  "beneficiary_id": 1
}
```

### Evaluations

#### List Evaluations
```http
GET /api/evaluations
```
Query Parameters:
- `beneficiary_id` (int): Filter by beneficiary
- `trainer_id` (int): Filter by trainer
- `program_id` (int): Filter by program
- `status` (string): pending, completed, graded
- `type` (string): quiz, assignment, project

Response:
```json
{
  "items": [
    {
      "id": 1,
      "title": "HTML Basics Quiz",
      "type": "quiz",
      "status": "completed",
      "score": 85,
      "max_score": 100,
      "beneficiary": {
        "id": 1,
        "full_name": "Jane Student"
      },
      "trainer": {
        "id": 5,
        "full_name": "John Trainer"
      },
      "created_at": "2024-02-01T10:00:00Z",
      "completed_at": "2024-02-05T14:30:00Z"
    }
  ],
  "total": 50
}
```

#### Get Evaluation
```http
GET /api/evaluations/{id}
```
Response:
```json
{
  "id": 1,
  "title": "HTML Basics Quiz",
  "description": "Test your HTML knowledge",
  "type": "quiz",
  "status": "completed",
  "questions": [
    {
      "id": 1,
      "question": "What does HTML stand for?",
      "type": "multiple_choice",
      "options": [
        "Hyper Text Markup Language",
        "High Tech Modern Language",
        "Home Tool Markup Language",
        "Hyperlink Text Management Language"
      ],
      "correct_answer": 0,
      "user_answer": 0,
      "points": 10
    }
  ],
  "score": 85,
  "max_score": 100,
  "feedback": "Great job! Review the CSS section.",
  "time_limit_minutes": 60,
  "time_taken_minutes": 45
}
```

#### Create Evaluation
```http
POST /api/evaluations
```
Request:
```json
{
  "title": "JavaScript Functions",
  "description": "Test on JavaScript functions",
  "type": "assignment",
  "beneficiary_id": 1,
  "program_id": 1,
  "questions": [
    {
      "question": "Write a function that returns the sum of two numbers",
      "type": "code",
      "points": 20
    }
  ],
  "max_score": 100,
  "time_limit_minutes": 90
}
```

#### Submit Evaluation
```http
POST /api/evaluations/{id}/submit
```
Request:
```json
{
  "answers": [
    {
      "question_id": 1,
      "answer": "function sum(a, b) { return a + b; }"
    }
  ],
  "time_taken_minutes": 45
}
```

#### Grade Evaluation
```http
POST /api/evaluations/{id}/grade
```
Request:
```json
{
  "scores": [
    {
      "question_id": 1,
      "score": 18,
      "feedback": "Good implementation, but missing input validation"
    }
  ],
  "overall_feedback": "Well done overall",
  "final_score": 85
}
```

### Documents

#### List Documents
```http
GET /api/documents
```
Query Parameters:
- `category` (string): Filter by category
- `owner_id` (int): Filter by owner
- `shared_with_me` (boolean): Show shared documents

Response:
```json
{
  "items": [
    {
      "id": 1,
      "name": "Course Material.pdf",
      "type": "application/pdf",
      "size": 2457600,
      "category": "course_material",
      "owner": {
        "id": 5,
        "full_name": "John Trainer"
      },
      "created_at": "2024-02-01T10:00:00Z",
      "shared_with": ["jane@example.com"],
      "download_url": "/api/documents/1/download"
    }
  ],
  "total": 25
}
```

#### Upload Document
```http
POST /api/documents
```
Request (multipart/form-data):
```
file: <binary>
name: "Course Material"
category: "course_material"
description: "Week 1 materials"
```

#### Download Document
```http
GET /api/documents/{id}/download
```
Response: Binary file data

#### Share Document
```http
POST /api/documents/{id}/share
```
Request:
```json
{
  "user_ids": [1, 2, 3],
  "permissions": ["view", "download"]
}
```

### Calendar & Appointments

#### Get Calendar Events
```http
GET /api/calendar/events
```
Query Parameters:
- `start_date` (date): Start of date range
- `end_date` (date): End of date range
- `type` (string): appointment, class, deadline

Response:
```json
{
  "events": [
    {
      "id": 1,
      "title": "1-on-1 with Jane Student",
      "type": "appointment",
      "start": "2024-03-25T10:00:00Z",
      "end": "2024-03-25T11:00:00Z",
      "attendees": [
        {
          "id": 1,
          "full_name": "Jane Student",
          "email": "jane@example.com"
        }
      ],
      "location": "Room 101",
      "description": "Weekly progress check"
    }
  ]
}
```

#### Create Appointment
```http
POST /api/calendar/appointments
```
Request:
```json
{
  "title": "Progress Review",
  "beneficiary_id": 1,
  "start": "2024-03-25T10:00:00Z",
  "end": "2024-03-25T11:00:00Z",
  "location": "Online",
  "description": "Monthly progress review",
  "recurring": {
    "frequency": "weekly",
    "until": "2024-06-30"
  }
}
```

#### Get Availability
```http
GET /api/calendar/availability
```
Query Parameters:
- `trainer_id` (int): Trainer to check
- `date` (date): Date to check
- `duration_minutes` (int): Required duration

Response:
```json
{
  "available_slots": [
    {
      "start": "2024-03-25T09:00:00Z",
      "end": "2024-03-25T10:00:00Z"
    },
    {
      "start": "2024-03-25T14:00:00Z",
      "end": "2024-03-25T17:00:00Z"
    }
  ]
}
```

### Messages

#### Send Message
```http
POST /api/messages
```
Request:
```json
{
  "recipient_id": 1,
  "subject": "Assignment Feedback",
  "content": "Great work on the assignment!",
  "attachments": [1, 2]
}
```

#### List Messages
```http
GET /api/messages
```
Query Parameters:
- `folder` (string): inbox, sent, archived
- `unread` (boolean): Filter unread messages
- `search` (string): Search in subject/content

Response:
```json
{
  "items": [
    {
      "id": 1,
      "subject": "Assignment Feedback",
      "content": "Great work on the assignment!",
      "sender": {
        "id": 5,
        "full_name": "John Trainer"
      },
      "recipient": {
        "id": 1,
        "full_name": "Jane Student"
      },
      "read": false,
      "created_at": "2024-03-20T15:30:00Z"
    }
  ],
  "total": 10,
  "unread_count": 3
}
```

### Reports & Analytics

#### Get Dashboard Stats
```http
GET /api/dashboard/stats
```
Response:
```json
{
  "total_beneficiaries": 250,
  "active_programs": 15,
  "completed_evaluations": 1200,
  "average_score": 82.5,
  "monthly_trends": {
    "beneficiaries": [220, 230, 240, 250],
    "evaluations": [280, 300, 320, 350]
  },
  "program_performance": [
    {
      "program": "Web Development",
      "completion_rate": 85,
      "average_score": 88
    }
  ]
}
```

#### Generate Report
```http
POST /api/reports/generate
```
Request:
```json
{
  "type": "beneficiary_progress",
  "format": "pdf",
  "filters": {
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-03-31"
    },
    "program_id": 1
  }
}
```
Response:
```json
{
  "report_id": "abc123",
  "status": "processing",
  "download_url": "/api/reports/abc123/download"
}
```

#### Download Report
```http
GET /api/reports/{report_id}/download
```
Response: Binary file data (PDF/Excel)

### Settings

#### Get User Settings
```http
GET /api/settings
```
Response:
```json
{
  "theme": "light",
  "language": "en",
  "notifications": {
    "email": true,
    "push": false,
    "sms": false
  },
  "timezone": "America/New_York",
  "date_format": "MM/DD/YYYY"
}
```

#### Update Settings
```http
PUT /api/settings
```
Request:
```json
{
  "theme": "dark",
  "notifications": {
    "email": false
  }
}
```

## Webhooks

### Available Events
- `user.created`
- `user.updated`
- `beneficiary.enrolled`
- `evaluation.completed`
- `program.started`
- `program.completed`

### Webhook Payload
```json
{
  "event": "evaluation.completed",
  "timestamp": "2024-03-20T15:30:00Z",
  "data": {
    "evaluation_id": 1,
    "beneficiary_id": 1,
    "score": 85
  }
}
```

### Register Webhook
```http
POST /api/webhooks
```
Request:
```json
{
  "url": "https://yourapp.com/webhook",
  "events": ["evaluation.completed", "program.completed"],
  "secret": "your_webhook_secret"
}
```

## Code Examples

### JavaScript (Axios)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.yourdomain.com',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
async function login(email, password) {
  const response = await api.post('/api/auth/login', {
    email,
    password
  });
  
  localStorage.setItem('access_token', response.data.access_token);
  return response.data;
}

// Get beneficiaries
async function getBeneficiaries(page = 1) {
  const response = await api.get('/api/beneficiaries', {
    params: { page, per_page: 20 }
  });
  return response.data;
}
```

### Python (Requests)
```python
import requests

class BDCClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.session = requests.Session()
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
    
    def login(self, email, password):
        response = self.session.post(
            f'{self.base_url}/api/auth/login',
            json={'email': email, 'password': password}
        )
        data = response.json()
        self.session.headers['Authorization'] = f"Bearer {data['access_token']}"
        return data
    
    def get_beneficiaries(self, page=1):
        response = self.session.get(
            f'{self.base_url}/api/beneficiaries',
            params={'page': page, 'per_page': 20}
        )
        return response.json()

# Usage
client = BDCClient('https://api.yourdomain.com')
client.login('user@example.com', 'password')
beneficiaries = client.get_beneficiaries()
```

### cURL
```bash
# Login
curl -X POST https://api.yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Get beneficiaries with auth
curl -X GET https://api.yourdomain.com/api/beneficiaries \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json"

# Create beneficiary
curl -X POST https://api.yourdomain.com/api/beneficiaries \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"New Student","email":"student@example.com"}'
```

## Postman Collection
A complete Postman collection is available at: `https://api.yourdomain.com/postman-collection.json`

## API Versioning
The API uses URL versioning. The current version is v1. Future versions will be available at:
- v2: `/api/v2/...`
- v3: `/api/v3/...`

## Support
For API support, contact:
- Email: api-support@yourdomain.com
- Documentation: https://docs.yourdomain.com
- Status Page: https://status.yourdomain.com

---

Last Updated: May 17, 2025
API Version: 1.0