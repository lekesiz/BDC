# BDC Clean Project Structure

## 🎯 Project Overview
BDC (Bilan de Compétence) - A clean, maintainable competency assessment platform

## 📁 Clean Directory Structure

```
BDC/
├── client/                     # React Frontend Application
│   ├── public/                 # Static assets
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── contexts/          # React contexts (Auth, Theme, etc.)
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # API client and utilities
│   │   ├── pages/             # Page components
│   │   ├── services/          # Frontend services
│   │   ├── styles/            # Global styles
│   │   ├── utils/             # Utility functions
│   │   ├── App.jsx            # Main App component
│   │   └── main.jsx           # Entry point
│   ├── tests/                 # Frontend tests
│   └── package.json
│
├── server/                    # Flask Backend Application
│   ├── app/
│   │   ├── api/              # API endpoints (one per resource)
│   │   ├── core/             # Core business logic
│   │   ├── models/           # Database models
│   │   ├── repositories/     # Data access layer
│   │   ├── schemas/          # Marshmallow schemas
│   │   ├── services/         # Business services
│   │   ├── utils/            # Utilities
│   │   └── __init__.py       # App factory
│   ├── config/               # Configuration files
│   ├── migrations/           # Database migrations
│   ├── tests/                # Consolidated backend tests
│   │   └── consolidated/     # Domain-focused test files
│   ├── requirements.txt      # Python dependencies
│   ├── run_local.py         # Development runner
│   └── wsgi.py              # Production entry point
│
├── docker/                   # Docker configurations
│   ├── docker-compose.yml    # Base configuration
│   ├── docker-compose.dev.yml # Development overrides
│   └── docker-compose.prod.yml # Production configuration
│
├── scripts/                  # Utility scripts
├── docs/                     # Documentation
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # Project documentation
```

## 🔧 Key Improvements

### 1. **Single Implementation Policy**
- One service per domain (no duplicates)
- One API endpoint per resource
- One configuration system
- One test file per domain

### 2. **Clear Separation of Concerns**
```
API Layer → Service Layer → Repository Layer → Database
     ↓            ↓              ↓
  Schemas    Business Logic   Data Access
```

### 3. **Simplified Entry Points**
- **Development**: `python run_local.py`
- **Production**: `gunicorn wsgi:app`
- **Docker**: `docker-compose up`

### 4. **Consolidated Testing**
From 283 test files to 5 domain-focused files:
- `test_auth.py` - Authentication & authorization
- `test_users.py` - User management
- `test_beneficiaries.py` - Beneficiary operations
- `test_programs.py` - Program management
- `test_evaluations.py` - Evaluations & assessments

### 5. **Clean Service Architecture**
```python
# Each service follows this pattern:
class ServiceName:
    def __init__(self, repository: RepositoryInterface):
        self.repository = repository
    
    def business_method(self):
        # Business logic here
        pass
```

## 🚀 Quick Start

### Local Development
```bash
# Backend
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_local.py

# Frontend
cd client
npm install
npm run dev
```

### Docker Development
```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up
```

### Production Deployment
```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d
```

## 📊 Cleanup Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total Files | 500+ | ~200 | 60% reduction |
| Test Files | 283 | 5 | 98% reduction |
| Service Duplicates | 60+ | 15 | 75% reduction |
| API Endpoints | 40+ | 20 | 50% reduction |
| Entry Points | 6 | 2 | 67% reduction |

## 🔒 Security

- Environment-based configuration
- No hardcoded credentials
- JWT authentication
- Role-based access control
- Input validation
- Rate limiting

## 🧪 Testing Strategy

### Unit Tests
- Service layer testing
- Model validation
- Utility function tests

### Integration Tests
- API endpoint testing
- Database operations
- External service mocking

### Run Tests
```bash
cd server
pytest tests/consolidated/
```

## 📝 API Documentation

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh token

### Users
- `GET /api/users` - List users
- `GET /api/users/:id` - Get user
- `POST /api/users` - Create user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Beneficiaries
- `GET /api/beneficiaries` - List beneficiaries
- `GET /api/beneficiaries/:id` - Get beneficiary
- `POST /api/beneficiaries` - Create beneficiary
- `PUT /api/beneficiaries/:id` - Update beneficiary
- `DELETE /api/beneficiaries/:id` - Delete beneficiary

### Programs
- `GET /api/programs` - List programs
- `GET /api/programs/:id` - Get program
- `POST /api/programs` - Create program
- `PUT /api/programs/:id` - Update program
- `DELETE /api/programs/:id` - Delete program

### Evaluations
- `GET /api/evaluations` - List evaluations
- `GET /api/evaluations/:id` - Get evaluation
- `POST /api/evaluations` - Create evaluation
- `PUT /api/evaluations/:id` - Update evaluation
- `DELETE /api/evaluations/:id` - Delete evaluation

## 🔄 Development Workflow

1. **Feature Development**
   - Create feature branch
   - Implement in appropriate layer
   - Write/update tests
   - Update documentation

2. **Code Review**
   - Check for duplicates
   - Verify single responsibility
   - Ensure proper error handling
   - Validate security practices

3. **Deployment**
   - Run tests
   - Build Docker images
   - Deploy to staging
   - Verify functionality
   - Deploy to production

## 🛠 Maintenance

### Adding New Features
1. Define API endpoint in `app/api/`
2. Create service in `app/services/`
3. Add repository if needed in `app/repositories/`
4. Define models in `app/models/`
5. Create schemas in `app/schemas/`
6. Write tests in `tests/consolidated/`

### Updating Dependencies
```bash
# Backend
pip-compile requirements.in

# Frontend
npm update
```

### Database Migrations
```bash
flask db migrate -m "Description"
flask db upgrade
```

## 📈 Performance

- Optimized database queries
- Redis caching
- Async task processing
- Connection pooling
- Response compression

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Follow clean architecture principles
4. Write tests
5. Submit pull request

---

**Remember**: Keep it simple, keep it clean, avoid duplicates!