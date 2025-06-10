# BDC Platform - Technical Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Installation & Setup](#installation--setup)
5. [API Documentation](#api-documentation)
6. [Frontend Architecture](#frontend-architecture)
7. [Backend Architecture](#backend-architecture)
8. [Database Schema](#database-schema)
9. [Security](#security)
10. [Performance Optimization](#performance-optimization)
11. [Deployment](#deployment)
12. [Testing](#testing)
13. [Monitoring & Logging](#monitoring--logging)
14. [Troubleshooting](#troubleshooting)

---

## Project Overview

BDC (Beneficiary Data Center) is a comprehensive platform designed for managing beneficiaries, programs, evaluations, and educational resources. The platform provides multi-tenant support, real-time analytics, and advanced reporting capabilities.

### Key Features

- **Multi-tenant Architecture**: Isolated data and resources per organization
- **Real-time Collaboration**: WebSocket-based live updates
- **Progressive Web App**: Offline functionality and mobile support
- **Advanced Analytics**: Real-time dashboards and insights
- **AI Integration**: Intelligent content generation and recommendations
- **Comprehensive Security**: JWT authentication, threat detection, audit logging
- **Performance Optimized**: Caching, compression, and database optimization

---

## Architecture

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Frontend      │────▶│   Backend API   │────▶│   Database     │
│   (React SPA)   │     │   (Flask)       │     │   (PostgreSQL) │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Static CDN    │     │   Redis Cache   │     │   File Storage │
│                 │     │                 │     │   (S3/Local)   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Component Architecture

- **Frontend**: React SPA with Material-UI and Tailwind CSS
- **Backend**: Flask REST API with SQLAlchemy ORM
- **Database**: PostgreSQL with Redis caching
- **Real-time**: Socket.IO for WebSocket communication
- **Storage**: Local filesystem or S3-compatible storage
- **CDN**: CloudFlare or custom CDN for static assets

---

## Technology Stack

### Frontend

- **Framework**: React 18.2.0
- **Build Tool**: Vite 6.3.5
- **Styling**: 
  - Material-UI 5.x
  - Tailwind CSS 3.x
  - Emotion for CSS-in-JS
- **State Management**: React Context API
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **WebSocket**: Socket.IO Client
- **Charts**: Recharts, Chart.js
- **Forms**: React Hook Form
- **Testing**: Vitest, React Testing Library

### Backend

- **Framework**: Flask 3.0.0
- **ORM**: SQLAlchemy 2.0.25
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow 3.x
- **WebSocket**: Flask-SocketIO
- **Caching**: Flask-Caching with Redis
- **Task Queue**: Celery (optional)
- **Testing**: Pytest

### Infrastructure

- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Web Server**: Gunicorn/uWSGI
- **Reverse Proxy**: Nginx
- **Container**: Docker
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (optional)

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd BDC
```

#### 2. Backend Setup

```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db upgrade
flask seed-data  # Optional: Load sample data
```

#### 3. Frontend Setup

```bash
cd client
npm install

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

### Docker Setup

```bash
# Quick start with Docker
cp .env.production.template .env
./scripts/docker-deploy.sh

# With monitoring stack
./scripts/docker-deploy.sh --monitoring

# Development mode
./scripts/docker-deploy.sh --mode development
```

---

## API Documentation

### Authentication

All API endpoints require JWT authentication except public endpoints.

```http
Authorization: Bearer <jwt-token>
```

### Base URL

```
http://localhost:5001/api
```

### Core Endpoints

#### Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

#### Users

- `GET /api/users` - List users (admin only)
- `GET /api/users/:id` - Get user details
- `POST /api/users` - Create user (admin only)
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user (admin only)

#### Beneficiaries

- `GET /api/beneficiaries` - List beneficiaries
- `GET /api/beneficiaries/:id` - Get beneficiary details
- `POST /api/beneficiaries` - Create beneficiary
- `PUT /api/beneficiaries/:id` - Update beneficiary
- `DELETE /api/beneficiaries/:id` - Delete beneficiary

#### Programs

- `GET /api/programs` - List programs
- `GET /api/programs/:id` - Get program details
- `POST /api/programs` - Create program
- `PUT /api/programs/:id` - Update program
- `DELETE /api/programs/:id` - Delete program
- `POST /api/programs/:id/enroll` - Enroll beneficiary

#### Evaluations

- `GET /api/evaluations` - List evaluations
- `GET /api/evaluations/:id` - Get evaluation details
- `POST /api/evaluations` - Create evaluation
- `PUT /api/evaluations/:id` - Update evaluation
- `POST /api/evaluations/:id/submit` - Submit evaluation

### V2 API Endpoints

#### Bulk Operations

- `POST /api/v2/bulk/operations` - Execute bulk operations
- `GET /api/v2/bulk/operations/:id/status` - Check operation status

#### Global Search

- `GET /api/v2/search/global` - Search across all entities
- `GET /api/v2/search/suggestions` - Get search suggestions

#### Analytics

- `GET /api/v2/analytics/dashboard` - Dashboard statistics
- `GET /api/v2/analytics/trends` - Trend analysis
- `GET /api/v2/analytics/export` - Export analytics data

#### Reports

- `GET /api/v2/reports/templates` - List report templates
- `POST /api/v2/reports/generate` - Generate report
- `GET /api/v2/reports/schedules` - List scheduled reports
- `POST /api/v2/reports/schedules` - Create report schedule

---

## Frontend Architecture

### Directory Structure

```
client/
├── src/
│   ├── components/       # Reusable components
│   │   ├── common/      # Common components
│   │   ├── layout/      # Layout components
│   │   ├── ui/          # UI primitives
│   │   └── specific/    # Feature-specific components
│   ├── contexts/        # React contexts
│   ├── hooks/           # Custom hooks
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── utils/           # Utilities
│   ├── i18n/           # Internationalization
│   └── styles/         # Global styles
├── public/             # Static assets
└── tests/              # Test files
```

### Key Components

#### Layout System

- `DashboardLayout` - Main application layout
- `Sidebar` - Navigation sidebar
- `Header` - Top navigation bar
- `Footer` - Application footer

#### Core Features

- `BeneficiariesPage` - Beneficiary management
- `ProgramsListPage` - Program management
- `EvaluationsPage` - Evaluation management
- `ReportsDashboard` - Reporting interface
- `AnalyticsDashboard` - Analytics visualization

#### UI Components

- `DataTable` - Advanced data grid
- `Form` - Dynamic form builder
- `Chart` - Data visualization
- `Modal` - Dialog system
- `Toast` - Notification system

### State Management

- **Auth Context**: User authentication state
- **Theme Context**: Application theming
- **Socket Context**: WebSocket connections
- **Notification Context**: Real-time notifications

### Routing

Routes are defined in `SimpleRouteRenderer.jsx` with role-based access control:

- Public routes: Login, Register, Forgot Password
- Protected routes: Require authentication
- Role-based routes: Admin, Trainer, Student specific

---

## Backend Architecture

### Directory Structure

```
server/
├── app/
│   ├── api/             # API endpoints
│   │   ├── v1/         # Version 1 endpoints
│   │   └── v2/         # Version 2 endpoints
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Marshmallow schemas
│   ├── services/       # Business logic
│   ├── middleware/     # Custom middleware
│   ├── utils/          # Utilities
│   └── core/           # Core functionality
├── migrations/         # Database migrations
├── tests/             # Test files
└── config.py          # Configuration
```

### Key Services

#### Authentication Service

- JWT token generation and validation
- Password hashing with bcrypt
- Two-factor authentication support
- Session management

#### Beneficiary Service

- CRUD operations
- Document management
- Progress tracking
- Evaluation history

#### Report Service

- Template-based generation
- Multiple format support (PDF, Excel, CSV)
- Scheduled reports
- Email delivery

#### Analytics Service

- Real-time data aggregation
- Trend analysis
- Performance metrics
- Export functionality

### Middleware

- **CORS**: Cross-origin resource sharing
- **Rate Limiting**: API throttling
- **Authentication**: JWT validation
- **Error Handling**: Global exception handling
- **Logging**: Request/response logging
- **Compression**: Response compression

---

## Database Schema

### Core Tables

#### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL,
    tenant_id UUID REFERENCES tenants(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### beneficiaries

```sql
CREATE TABLE beneficiaries (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    date_of_birth DATE,
    tenant_id UUID REFERENCES tenants(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### programs

```sql
CREATE TABLE programs (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    capacity INTEGER,
    tenant_id UUID REFERENCES tenants(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Relationships

- Users belong to Tenants (multi-tenancy)
- Beneficiaries belong to Tenants
- Programs have many Enrollments
- Enrollments link Beneficiaries to Programs
- Evaluations belong to Programs and Beneficiaries

### Indexes

Performance indexes are automatically created for:
- Foreign keys
- Frequently queried columns
- Search fields
- Date ranges

---

## Security

### Authentication & Authorization

- **JWT Authentication**: Stateless token-based auth
- **Role-Based Access Control (RBAC)**: Fine-grained permissions
- **Two-Factor Authentication**: Optional 2FA support
- **Session Management**: Secure session handling

### Security Features

#### Input Validation

- Marshmallow schemas for request validation
- SQL injection prevention with parameterized queries
- XSS protection with content sanitization

#### API Security

- Rate limiting per user/IP
- CORS configuration
- API versioning
- Request signing for sensitive operations

#### Data Protection

- Password hashing with bcrypt
- Encryption at rest for sensitive data
- TLS/SSL for data in transit
- PII data masking

#### Audit & Compliance

- Comprehensive audit logging
- User activity tracking
- Data retention policies
- GDPR compliance features

---

## Performance Optimization

### Frontend Optimization

#### Build Optimization

- Code splitting with React.lazy
- Tree shaking for smaller bundles
- Compression (Gzip/Brotli)
- Asset optimization

#### Runtime Optimization

- Virtual scrolling for large lists
- Debounced search inputs
- Memoization with React.memo
- Lazy loading images

### Backend Optimization

#### Database Optimization

- Query optimization with indexes
- Connection pooling
- Query result caching
- Batch operations

#### Caching Strategy

- Redis for session storage
- Query result caching
- Static asset caching
- CDN integration

#### Performance Monitoring

- Request timing
- Database query analysis
- Memory usage tracking
- Real-time metrics dashboard

---

## Deployment

### Docker Deployment

#### Quick Start

```bash
# Production deployment
./scripts/docker-deploy.sh

# With monitoring
./scripts/docker-deploy.sh --monitoring

# Development mode
./scripts/docker-deploy.sh --mode development
```

#### Docker Compose Services

- **postgres**: PostgreSQL database
- **redis**: Redis cache
- **backend**: Flask API
- **frontend**: Nginx + React
- **prometheus**: Metrics collection (optional)
- **grafana**: Monitoring dashboard (optional)

### Manual Deployment

#### Backend Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

#### Frontend Deployment

```bash
# Build production bundle
npm run build

# Serve with Nginx
cp -r dist/* /var/www/html/
```

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/bdc
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# External Services
OPENAI_API_KEY=your-openai-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password

# Storage
UPLOAD_FOLDER=/uploads
MAX_CONTENT_LENGTH=16777216

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## Testing

### Frontend Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test Button.test.jsx

# Run in watch mode
npm run test:watch
```

### Backend Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_auth.py

# Run integration tests
pytest tests/integration/
```

### E2E Testing

```bash
# Run Cypress tests
npm run cypress:open

# Run headless
npm run cypress:run
```

---

## Monitoring & Logging

### Application Monitoring

#### Metrics Collection

- Prometheus metrics endpoint: `/metrics`
- Custom metrics for business logic
- System metrics (CPU, memory, disk)

#### Dashboards

- Grafana dashboards for visualization
- Real-time performance monitoring
- Alert configuration

### Logging

#### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

#### Log Aggregation

- Centralized logging with ELK stack
- Structured JSON logging
- Log rotation and retention

### Health Checks

- `/health` - Basic health check
- `/api/v2/health` - Detailed health status
- Database connectivity check
- Redis connectivity check
- External service checks

---

## Troubleshooting

### Common Issues

#### Frontend Issues

**Problem**: Blank page or React errors
```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Problem**: API connection errors
```bash
# Check backend is running
curl http://localhost:5001/health

# Check CORS configuration
# Ensure frontend URL is in CORS_ORIGINS
```

#### Backend Issues

**Problem**: Database connection errors
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
flask db current
```

**Problem**: Redis connection errors
```bash
# Check Redis is running
redis-cli ping

# Verify Redis URL
python -c "import redis; r = redis.from_url('redis://localhost:6379'); print(r.ping())"
```

### Performance Issues

#### Slow API Responses

1. Check database query performance
2. Enable query logging
3. Review slow query log
4. Add appropriate indexes

#### High Memory Usage

1. Check for memory leaks
2. Review caching strategy
3. Optimize query results
4. Implement pagination

### Debugging Tips

#### Frontend Debugging

- Use React DevTools
- Enable source maps
- Check network tab for API calls
- Review console errors

#### Backend Debugging

- Enable Flask debug mode (development only)
- Use Flask-DebugToolbar
- Check application logs
- Use pdb for breakpoints

---

## Appendix

### Useful Commands

```bash
# Database
flask db init        # Initialize migrations
flask db migrate     # Create migration
flask db upgrade     # Apply migrations
flask db downgrade   # Rollback migration

# Cache
flask clear-cache    # Clear all caches
redis-cli FLUSHALL   # Clear Redis (careful!)

# Performance
flask optimize-db    # Optimize database
flask performance-report  # Generate report

# Docker
docker-compose logs -f backend  # View backend logs
docker-compose exec backend flask shell  # Flask shell
docker-compose down -v  # Stop and remove volumes
```

### Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

*Last Updated: January 2025*
*Version: 1.0.0*