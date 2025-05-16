# BDC Code Documentation

## Project Structure

```
BDC/
├── backend/                 # Flask backend application
│   ├── app/                # Main application package
│   │   ├── api/           # API endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Marshmallow schemas
│   │   ├── services/      # Business logic services
│   │   ├── utils/         # Utility functions
│   │   └── extensions.py  # Flask extensions
│   ├── config/            # Configuration files
│   ├── database/          # Database utilities
│   ├── migrations/        # Alembic migrations
│   ├── monitoring/        # Monitoring and logging
│   ├── tests/            # Test suites
│   └── requirements.txt   # Python dependencies
└── client/                 # React frontend application
    ├── src/
    │   ├── components/    # Reusable components
    │   ├── pages/        # Page components
    │   ├── hooks/        # Custom React hooks
    │   ├── contexts/     # React contexts
    │   ├── services/     # API services
    │   ├── utils/        # Utility functions
    │   └── styles/       # Global styles
    ├── public/           # Static assets
    └── package.json      # Node dependencies
```

## Backend Architecture

### Flask Application Structure

The backend follows a modular architecture with clear separation of concerns:

1. **API Layer** (`app/api/`): RESTful endpoints organized by resource
2. **Model Layer** (`app/models/`): SQLAlchemy ORM models
3. **Schema Layer** (`app/schemas/`): Marshmallow serialization schemas
4. **Service Layer** (`app/services/`): Business logic implementation
5. **Utility Layer** (`app/utils/`): Helper functions and utilities

### Key Components

#### Application Factory Pattern

```python
# app/__init__.py
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
```

#### Database Models

Models use SQLAlchemy ORM with mixins for common functionality:

```python
# app/models/mixins.py
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# app/models/user.py
class User(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
```

#### API Endpoints

Endpoints use Flask-RESTful for consistent API structure:

```python
# app/api/auth.py
class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {'error': 'Invalid credentials'}, 401
        
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token, 'user': user.to_dict()}, 200
```

#### Service Layer

Services contain business logic separated from API endpoints:

```python
# app/services/assessment_service.py
class AssessmentService:
    @staticmethod
    def create_assessment(title, beneficiary_id, trainer_id, questions):
        assessment = Assessment(
            title=title,
            beneficiary_id=beneficiary_id,
            trainer_id=trainer_id
        )
        db.session.add(assessment)
        
        for question_data in questions:
            question = Question(**question_data, assessment_id=assessment.id)
            db.session.add(question)
        
        db.session.commit()
        return assessment
    
    @staticmethod
    def analyze_results(assessment_id):
        # AI analysis logic
        return analysis_results
```

#### Middleware and Decorators

Custom decorators for common functionality:

```python
# app/utils/decorators.py
def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if current_user.role != role:
                return {'error': 'Insufficient permissions'}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@require_role('admin')
def admin_only_endpoint():
    return {'message': 'Admin access granted'}
```

### Error Handling

Centralized error handling with custom exceptions:

```python
# app/utils/exceptions.py
class AppException(Exception):
    status_code = 400
    
    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code:
            self.status_code = status_code

# app/error_handlers.py
@app.errorhandler(AppException)
def handle_app_exception(e):
    return {'error': e.message}, e.status_code

@app.errorhandler(404)
def handle_not_found(e):
    return {'error': 'Resource not found'}, 404
```

### Configuration Management

Environment-based configuration:

```python
# config/config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bdc_dev.db'
    
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

## Frontend Architecture

### React Application Structure

The frontend uses React with modern patterns and best practices:

1. **Component Architecture**: Functional components with hooks
2. **State Management**: Context API for global state
3. **Routing**: React Router for navigation
4. **API Integration**: Axios for HTTP requests
5. **Styling**: Tailwind CSS for UI design

### Key Components

#### App Root

```javascript
// src/App.jsx
function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="beneficiaries" element={<Beneficiaries />} />
              // More routes...
            </Route>
          </Routes>
        </BrowserRouter>
      </NotificationProvider>
    </AuthProvider>
  );
}
```

#### Authentication Context

```javascript
// src/contexts/AuthContext.jsx
const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user } = response.data;
    
    localStorage.setItem('token', access_token);
    setUser(user);
    
    return user;
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };
  
  useEffect(() => {
    // Check for existing session
    const token = localStorage.getItem('token');
    if (token) {
      // Validate token and load user
    }
    setLoading(false);
  }, []);
  
  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

#### API Service

```javascript
// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### Custom Hooks

```javascript
// src/hooks/useApi.js
export function useApi(apiFunc) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const request = async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiFunc(...args);
      setData(response.data);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return { data, loading, error, request };
}

// Usage
function BeneficiaryList() {
  const { data: beneficiaries, loading, error, request: loadBeneficiaries } = 
    useApi(api.get);
  
  useEffect(() => {
    loadBeneficiaries('/beneficiaries');
  }, []);
  
  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;
  
  return (
    <div>
      {beneficiaries?.map(beneficiary => (
        <BeneficiaryCard key={beneficiary.id} {...beneficiary} />
      ))}
    </div>
  );
}
```

#### Component Patterns

```javascript
// src/components/common/DataTable.jsx
function DataTable({ columns, data, onRowClick, loading }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} className="px-6 py-3 text-left">
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td colSpan={columns.length}>
                <Spinner />
              </td>
            </tr>
          ) : (
            data.map((row) => (
              <tr
                key={row.id}
                onClick={() => onRowClick?.(row)}
                className="hover:bg-gray-50 cursor-pointer"
              >
                {columns.map((column) => (
                  <td key={column.key} className="px-6 py-4">
                    {column.render ? column.render(row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
```

### State Management

Using React Context for global state:

```javascript
// src/contexts/AppContext.jsx
const AppContext = createContext();

export function AppProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [theme, setTheme] = useState('light');
  
  const addNotification = (notification) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { ...notification, id }]);
    
    // Auto-remove after timeout
    setTimeout(() => {
      removeNotification(id);
    }, notification.timeout || 5000);
  };
  
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };
  
  return (
    <AppContext.Provider value={{
      notifications,
      addNotification,
      removeNotification,
      theme,
      setTheme,
    }}>
      {children}
    </AppContext.Provider>
  );
}
```

## Testing Strategies

### Backend Testing

#### Unit Tests

```python
# tests/test_models.py
import pytest
from app.models import User

def test_user_password_hashing():
    user = User(email='test@example.com')
    user.set_password('password123')
    
    assert user.password_hash != 'password123'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')
```

#### Integration Tests

```python
# tests/test_api.py
def test_login_endpoint(client):
    # Create test user
    user = UserFactory(email='test@example.com', password='password123')
    
    # Test login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
```

### Frontend Testing

#### Component Tests

```javascript
// tests/components/Button.test.jsx
import { render, fireEvent } from '@testing-library/react';
import Button from '@/components/common/Button';

test('renders button with text', () => {
  const { getByText } = render(<Button>Click me</Button>);
  expect(getByText('Click me')).toBeInTheDocument();
});

test('calls onClick handler', () => {
  const handleClick = jest.fn();
  const { getByText } = render(
    <Button onClick={handleClick}>Click me</Button>
  );
  
  fireEvent.click(getByText('Click me'));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

#### E2E Tests

```javascript
// cypress/e2e/auth.cy.js
describe('Authentication Flow', () => {
  it('allows user to login', () => {
    cy.visit('/login');
    cy.get('[data-testid=email-input]').type('test@example.com');
    cy.get('[data-testid=password-input]').type('password123');
    cy.get('[data-testid=login-button]').click();
    
    cy.url().should('eq', '/dashboard');
    cy.contains('Welcome back').should('be.visible');
  });
});
```

## Deployment

### Docker Configuration

```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

```dockerfile
# client/Dockerfile
FROM node:16-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Backend Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      
      - name: Run Frontend Tests
        run: |
          cd client
          npm ci
          npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Server
        run: |
          # Deployment scripts
```

## Performance Optimization

### Backend Optimization

1. **Database Query Optimization**
   - Use eager loading to avoid N+1 queries
   - Add appropriate indexes
   - Use query optimization techniques

```python
# Eager loading example
beneficiaries = Beneficiary.query.options(
    joinedload(Beneficiary.user),
    joinedload(Beneficiary.trainer)
).filter_by(trainer_id=trainer_id).all()
```

2. **Caching Strategy**
   - Redis caching for frequently accessed data
   - Cache invalidation on updates

```python
# app/utils/cache.py
def cache_key_wrapper(prefix):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{prefix}:{':'.join(map(str, args))}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = f(*args, **kwargs)
            redis_client.setex(
                cache_key,
                300,  # 5 minutes
                json.dumps(result)
            )
            return result
        return decorated_function
    return decorator
```

### Frontend Optimization

1. **Code Splitting**

```javascript
// Lazy loading components
const BeneficiaryDashboard = lazy(() => 
  import('./pages/BeneficiaryDashboard')
);

// Usage with Suspense
<Suspense fallback={<Spinner />}>
  <BeneficiaryDashboard />
</Suspense>
```

2. **Memoization**

```javascript
// Memoize expensive calculations
const MemoizedChart = memo(({ data }) => {
  const processedData = useMemo(() => 
    processDataForChart(data), [data]
  );
  
  return <Chart data={processedData} />;
});
```

## Security Best Practices

### Backend Security

1. **Input Validation**

```python
# app/schemas/user.py
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8)
    )
    role = fields.Str(
        validate=validate.OneOf(['admin', 'trainer', 'student'])
    )
```

2. **SQL Injection Prevention**
   - Use ORM queries
   - Parameterized queries when using raw SQL

3. **Authentication & Authorization**
   - JWT tokens with expiration
   - Role-based access control
   - Secure password hashing

### Frontend Security

1. **XSS Prevention**
   - React automatically escapes values
   - Use dangerouslySetInnerHTML cautiously

2. **CSRF Protection**
   - Include CSRF tokens in forms
   - Validate origin headers

3. **Secure Storage**
   - Don't store sensitive data in localStorage
   - Use httpOnly cookies for tokens

## Monitoring and Logging

### Application Monitoring

```python
# app/monitoring/metrics.py
from prometheus_client import Counter, Histogram

request_count = Counter(
    'app_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'app_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Usage in middleware
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    request_count.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    request_duration.labels(
        method=request.method,
        endpoint=request.endpoint
    ).observe(duration)
    return response
```

### Logging Configuration

```python
# app/utils/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not app.debug:
        file_handler = RotatingFileHandler(
            'logs/bdc.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('BDC startup')
```

## API Versioning

Supporting multiple API versions:

```python
# app/api/__init__.py
from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)
api_v2 = Blueprint('api_v2', __name__)

# app/__init__.py
app.register_blueprint(api_v1, url_prefix='/api/v1')
app.register_blueprint(api_v2, url_prefix='/api/v2')
```

## Troubleshooting Guide

### Common Issues

1. **Database Connection Errors**
   - Check database URL configuration
   - Verify database server is running
   - Check network connectivity

2. **JWT Token Errors**
   - Verify token expiration
   - Check token format
   - Ensure secret key is configured

3. **CORS Issues**
   - Configure allowed origins
   - Check request headers
   - Verify API endpoint configuration

### Debug Mode

Enable debug mode for development:

```python
# Development only
app.config['DEBUG'] = True
app.config['SQLALCHEMY_ECHO'] = True  # Log SQL queries
```

```javascript
// Enable React dev tools
if (process.env.NODE_ENV === 'development') {
  console.log('Development mode enabled');
  // Additional debug configuration
}
```

## Contributing Guidelines

1. **Code Style**
   - Follow PEP 8 for Python
   - Use ESLint configuration for JavaScript
   - Write meaningful commit messages

2. **Pull Request Process**
   - Create feature branch
   - Write tests for new features
   - Update documentation
   - Request code review

3. **Code Review Checklist**
   - Code follows style guidelines
   - Tests pass and coverage adequate
   - Documentation updated
   - No security vulnerabilities

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Security Guidelines](https://owasp.org/)