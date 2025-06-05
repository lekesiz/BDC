# BDC Project Documentation
*Consolidated Documentation - January 2025*

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Setup & Installation](#setup--installation)
4. [API Documentation](#api-documentation)
5. [Security](#security)
6. [Performance](#performance)
7. [Deployment](#deployment)
8. [Development Guidelines](#development-guidelines)

---

## Project Overview

BDC (Bilan de Compétence) is a comprehensive skills assessment and career development platform.

### Key Features
- Multi-tenant architecture
- Role-based access control (Super Admin, Tenant Admin, Trainer, Student)
- Real-time notifications
- AI-powered evaluations
- Document management
- Appointment scheduling
- Progress tracking

### Technology Stack
- **Backend**: Flask 3.0, SQLAlchemy 2.0, PostgreSQL 15
- **Frontend**: React 18, Vite, Tailwind CSS
- **Infrastructure**: Docker, Redis, Nginx
- **Security**: JWT, Argon2, TLS

---

## Architecture

### Clean Architecture Pattern
```
app/
├── api/           # API endpoints (Presentation layer)
├── services/      # Business logic (Application layer)
├── repositories/  # Data access (Infrastructure layer)
├── models/        # Domain models
├── utils/         # Cross-cutting concerns
└── core/          # Core infrastructure
```

### Dependency Injection
All services use dependency injection pattern via `app/container.py`.

### Multi-tenancy
Row-level security implemented via `app/utils/multi_tenancy.py`.

---

## Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd BDC

# Setup environment
cp .env.example .env
# Edit .env with your values

# Start with Docker
docker-compose up -d

# Or start locally
cd server && pip install -r requirements.txt
cd ../client && npm install
```

### Database Setup
```bash
# Run migrations
cd server
flask db upgrade

# Seed initial data
python seed_db.py
```

---

## API Documentation

### Authentication
All API endpoints require JWT authentication except `/api/auth/login`.

```bash
# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Response
{
  "access_token": "...",
  "refresh_token": "...",
  "user": {...}
}
```

### Main Endpoints

#### Users
- `GET /api/users` - List users
- `GET /api/users/:id` - Get user
- `POST /api/users` - Create user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

#### Beneficiaries
- `GET /api/beneficiaries` - List beneficiaries
- `GET /api/beneficiaries/:id` - Get beneficiary
- `POST /api/beneficiaries` - Create beneficiary
- `PUT /api/beneficiaries/:id` - Update beneficiary

#### Programs
- `GET /api/programs` - List programs
- `GET /api/programs/:id` - Get program details
- `POST /api/programs` - Create program
- `POST /api/programs/:id/enroll` - Enroll beneficiary

#### Evaluations
- `GET /api/evaluations` - List evaluations
- `POST /api/evaluations` - Create evaluation
- `GET /api/evaluations/:id/results` - Get results

### Rate Limiting
- Default: 200 requests/hour
- Authentication: 5 requests/minute
- File uploads: 10 requests/hour

---

## Security

### Authentication & Authorization
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- Multi-tenant isolation

### Data Protection
- Password hashing: Argon2
- Sensitive data encryption: Fernet
- File upload validation: MIME type & content checking

### Security Headers
- Content Security Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security

### Rate Limiting
Implemented via Flask-Limiter with Redis backend.

---

## Performance

### Database Optimization
- Indexes on all foreign keys
- Composite indexes for common queries
- Connection pooling
- Query optimization

### Caching
- Redis for session management
- API response caching
- Static asset caching

### Frontend Optimization
- Code splitting with React.lazy
- Bundle optimization
- Image lazy loading
- Service Worker for offline support

---

## Deployment

### Docker Deployment
```bash
# Production deployment
./scripts/docker-deploy.sh

# With monitoring
./scripts/docker-deploy.sh --monitoring
```

### Environment Variables
See `.env.example` for all required variables.

### SSL/TLS
- Use Let's Encrypt for certificates
- Configure in nginx/conf.d/

### Monitoring
- Prometheus metrics at /metrics
- Grafana dashboards
- Health check at /api/health

---

## Development Guidelines

### Code Style
- Python: PEP 8
- JavaScript: ESLint + Prettier
- Git: Conventional Commits

### Testing
```bash
# Backend tests
cd server && pytest

# Frontend tests
cd client && npm test

# E2E tests
npm run test:e2e
```

### Error Handling
Use standardized error handler from `app/utils/error_handler.py`.

### Logging
- Development: Console
- Production: Structured JSON logs
- Use appropriate log levels

### API Versioning
- Current: /api/v2/
- Legacy: /api/v1/ (deprecated)

### Security Best Practices
1. Never commit secrets
2. Use environment variables
3. Validate all inputs
4. Implement proper CORS
5. Keep dependencies updated

---

## Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check PostgreSQL
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Redis Connection
```bash
# Check Redis
docker-compose logs redis

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

#### Frontend Build
```bash
# Clear cache
rm -rf node_modules/.vite
npm run build
```

### Support
- GitHub Issues: <repository-url>/issues
- Documentation: /docs
- API Docs: /api/docs

---

*Last updated: January 2025*