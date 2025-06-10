# BDC Platform - Developer Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Coding Standards](#coding-standards)
4. [Frontend Development](#frontend-development)
5. [Backend Development](#backend-development)
6. [Database Development](#database-development)
7. [API Development](#api-development)
8. [Testing Guide](#testing-guide)
9. [Security Best Practices](#security-best-practices)
10. [Performance Guidelines](#performance-guidelines)
11. [Git Workflow](#git-workflow)
12. [Debugging Guide](#debugging-guide)
13. [Contributing](#contributing)

---

## Development Environment Setup

### Prerequisites

```bash
# Required Software
- Git 2.30+
- Python 3.11+
- Node.js 18+ & npm 9+
- PostgreSQL 15+
- Redis 7+
- Docker 20+ (optional)
- VS Code or PyCharm (recommended)
```

### Initial Setup

#### 1. Clone Repository

```bash
git clone git@github.com:your-org/bdc-platform.git
cd bdc-platform
```

#### 2. Backend Setup

```bash
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Setup pre-commit hooks
pre-commit install

# Create environment file
cp .env.example .env
# Edit .env with your local settings

# Initialize database
createdb bdc_development
flask db upgrade
flask seed-db  # Load sample data
```

#### 3. Frontend Setup

```bash
cd ../client

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with your local settings

# Start development server
npm run dev
```

### VS Code Configuration

`.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.pythonPath": "${workspaceFolder}/server/venv/bin/python",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact"
  ],
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

### Docker Development

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Run with specific services
docker-compose -f docker-compose.dev.yml up backend frontend

# Execute commands in container
docker-compose exec backend flask shell
docker-compose exec backend pytest
```

---

## Project Structure

### Overall Structure

```
bdc-platform/
├── client/                 # Frontend React application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── contexts/     # React contexts
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API services
│   │   ├── utils/        # Utilities
│   │   └── styles/       # Global styles
│   ├── public/           # Static assets
│   └── tests/            # Frontend tests
├── server/               # Backend Flask application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Marshmallow schemas
│   │   ├── services/    # Business logic
│   │   ├── middleware/  # Custom middleware
│   │   └── utils/       # Utilities
│   ├── migrations/      # Database migrations
│   └── tests/           # Backend tests
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── docker/              # Docker configurations
```

### Frontend Structure

```
src/
├── components/
│   ├── common/          # Shared components
│   │   ├── Button/
│   │   ├── Modal/
│   │   └── Table/
│   ├── layout/          # Layout components
│   │   ├── Header/
│   │   ├── Sidebar/
│   │   └── Footer/
│   └── features/        # Feature-specific components
│       ├── beneficiaries/
│       ├── programs/
│       └── reports/
├── pages/              # Route pages
├── hooks/              # Custom React hooks
├── services/           # API communication
├── utils/              # Helper functions
└── styles/             # CSS/SCSS files
```

### Backend Structure

```
app/
├── api/
│   ├── v1/            # Version 1 endpoints
│   └── v2/            # Version 2 endpoints
├── models/            # SQLAlchemy models
│   ├── user.py
│   ├── beneficiary.py
│   └── program.py
├── schemas/           # Marshmallow schemas
├── services/          # Business logic
│   ├── auth_service.py
│   ├── report_service.py
│   └── analytics_service.py
├── middleware/        # Flask middleware
└── core/              # Core functionality
```

---

## Coding Standards

### Python (Backend)

#### Style Guide

Follow PEP 8 with these additions:

```python
# File header
"""
Module description goes here.
Explains what this module does and why it exists.
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ExampleService:
    """
    Service class for handling example operations.
    
    Attributes:
        config: Application configuration
        db: Database session
    """
    
    def __init__(self, config: Dict, db: Any):
        self.config = config
        self.db = db
    
    def process_data(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Process incoming data.
        
        Args:
            data: List of data items to process
            
        Returns:
            Processed results dictionary
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
            
        # Process logic here
        return {"status": "success", "count": len(data)}
```

#### Naming Conventions

```python
# Classes: PascalCase
class UserService:
    pass

# Functions/Methods: snake_case
def calculate_total_score(scores: List[int]) -> int:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Private methods: prefix with underscore
def _internal_helper(self) -> None:
    pass
```

### JavaScript/React (Frontend)

#### Style Guide

Follow Airbnb JavaScript Style Guide:

```javascript
// File header
/**
 * Component description
 * @module components/ExampleComponent
 */

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useTranslation } from 'react-i18next';

/**
 * ExampleComponent displays example data
 * @component
 * @param {Object} props - Component props
 * @param {string} props.title - Component title
 * @param {Array} props.items - List of items to display
 */
const ExampleComponent = ({ title, items = [] }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Effect logic
  }, []);

  const handleItemClick = (item) => {
    // Handle click logic
  };

  return (
    <div className="example-component">
      <h2>{title}</h2>
      {loading ? (
        <p>{t('common.loading')}</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.id} onClick={() => handleItemClick(item)}>
              {item.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

ExampleComponent.propTypes = {
  title: PropTypes.string.isRequired,
  items: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
    })
  ),
};

export default ExampleComponent;
```

#### Naming Conventions

```javascript
// Components: PascalCase
const UserProfile = () => {};

// Functions: camelCase
const calculateTotalScore = (scores) => {};

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;

// CSS classes: kebab-case
className="user-profile-container"

// Files: PascalCase for components, camelCase for utilities
UserProfile.jsx
userHelpers.js
```

### CSS/SCSS

```scss
// BEM Naming Convention
.block {
  &__element {
    &--modifier {
      // Styles
    }
  }
}

// Example
.user-card {
  &__header {
    &--highlighted {
      background-color: yellow;
    }
  }
  
  &__body {
    padding: 1rem;
  }
}

// Variables
$primary-color: #007bff;
$spacing-unit: 8px;

// Mixins
@mixin button-style($bg-color) {
  background-color: $bg-color;
  padding: $spacing-unit * 2;
  border-radius: 4px;
}
```

---

## Frontend Development

### Component Development

#### Creating a New Component

```bash
# Generate component structure
npm run generate:component MyComponent
```

Manual creation:

```javascript
// src/components/MyComponent/MyComponent.jsx
import React from 'react';
import PropTypes from 'prop-types';
import './MyComponent.scss';

const MyComponent = ({ prop1, prop2 }) => {
  return (
    <div className="my-component">
      {/* Component content */}
    </div>
  );
};

MyComponent.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.number,
};

MyComponent.defaultProps = {
  prop2: 0,
};

export default MyComponent;
```

```javascript
// src/components/MyComponent/index.js
export { default } from './MyComponent';
```

```scss
// src/components/MyComponent/MyComponent.scss
.my-component {
  // Styles
}
```

### State Management

#### Using Context API

```javascript
// contexts/ExampleContext.jsx
import React, { createContext, useContext, useState } from 'react';

const ExampleContext = createContext();

export const useExample = () => {
  const context = useContext(ExampleContext);
  if (!context) {
    throw new Error('useExample must be used within ExampleProvider');
  }
  return context;
};

export const ExampleProvider = ({ children }) => {
  const [state, setState] = useState({
    data: [],
    loading: false,
  });

  const fetchData = async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const response = await api.get('/data');
      setState(prev => ({ ...prev, data: response.data, loading: false }));
    } catch (error) {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  const value = {
    ...state,
    fetchData,
  };

  return (
    <ExampleContext.Provider value={value}>
      {children}
    </ExampleContext.Provider>
  );
};
```

### Custom Hooks

```javascript
// hooks/useDebounce.js
import { useState, useEffect } from 'react';

export const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};
```

### API Service Layer

```javascript
// services/beneficiaryService.js
import api from '@/lib/api';

class BeneficiaryService {
  async getAll(params = {}) {
    const response = await api.get('/api/beneficiaries', { params });
    return response.data;
  }

  async getById(id) {
    const response = await api.get(`/api/beneficiaries/${id}`);
    return response.data;
  }

  async create(data) {
    const response = await api.post('/api/beneficiaries', data);
    return response.data;
  }

  async update(id, data) {
    const response = await api.put(`/api/beneficiaries/${id}`, data);
    return response.data;
  }

  async delete(id) {
    const response = await api.delete(`/api/beneficiaries/${id}`);
    return response.data;
  }
}

export default new BeneficiaryService();
```

---

## Backend Development

### Creating Models

```python
# app/models/example.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db
from app.models.base import BaseModel

class Example(BaseModel):
    """Example model demonstrating best practices."""
    
    __tablename__ = 'examples'
    
    # Columns
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000))
    status = Column(String(50), default='active')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='examples')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_example_user_status', 'user_id', 'status'),
    )
    
    def __repr__(self):
        return f'<Example {self.name}>'
    
    @property
    def is_active(self):
        """Check if example is active."""
        return self.status == 'active'
    
    @classmethod
    def get_active_by_user(cls, user_id):
        """Get all active examples for a user."""
        return cls.query.filter_by(
            user_id=user_id,
            status='active'
        ).all()
```

### Creating Schemas

```python
# app/schemas/example.py
from marshmallow import Schema, fields, validate, validates, ValidationError
from app.schemas.base import BaseSchema

class ExampleSchema(BaseSchema):
    """Schema for Example model."""
    
    # Fields
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255)
    )
    description = fields.String(
        validate=validate.Length(max=1000),
        allow_none=True
    )
    status = fields.String(
        validate=validate.OneOf(['active', 'inactive', 'pending']),
        load_default='active'
    )
    user_id = fields.Integer(required=True)
    
    # Nested fields
    user = fields.Nested('UserSchema', only=['id', 'name', 'email'], dump_only=True)
    
    @validates('name')
    def validate_name(self, value):
        """Custom validation for name field."""
        if value and value.lower() in ['admin', 'system']:
            raise ValidationError('Reserved name')
        return value
    
    class Meta:
        # Include timestamps from BaseSchema
        fields = ('id', 'name', 'description', 'status', 'user_id', 'user', 
                 'created_at', 'updated_at')
```

### Creating Services

```python
# app/services/example_service.py
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.example import Example
from app.schemas.example import ExampleSchema
from app.core.exceptions import NotFoundError, ValidationError

class ExampleService:
    """Service layer for Example operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.schema = ExampleSchema()
    
    def get_all(self, filters: Dict = None) -> List[Example]:
        """Get all examples with optional filters."""
        query = self.db.query(Example)
        
        if filters:
            if filters.get('status'):
                query = query.filter_by(status=filters['status'])
            if filters.get('user_id'):
                query = query.filter_by(user_id=filters['user_id'])
        
        return query.all()
    
    def get_by_id(self, example_id: int) -> Example:
        """Get example by ID."""
        example = self.db.query(Example).get(example_id)
        if not example:
            raise NotFoundError(f'Example {example_id} not found')
        return example
    
    def create(self, data: Dict) -> Example:
        """Create new example."""
        # Validate data
        validated_data = self.schema.load(data)
        
        # Create instance
        example = Example(**validated_data)
        
        # Save to database
        self.db.add(example)
        self.db.commit()
        self.db.refresh(example)
        
        return example
    
    def update(self, example_id: int, data: Dict) -> Example:
        """Update existing example."""
        example = self.get_by_id(example_id)
        
        # Validate data
        validated_data = self.schema.load(data, partial=True)
        
        # Update fields
        for key, value in validated_data.items():
            setattr(example, key, value)
        
        # Save changes
        self.db.commit()
        self.db.refresh(example)
        
        return example
    
    def delete(self, example_id: int) -> bool:
        """Delete example."""
        example = self.get_by_id(example_id)
        
        self.db.delete(example)
        self.db.commit()
        
        return True
```

### Creating API Endpoints

```python
# app/api/v2/example.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.services.example_service import ExampleService
from app.schemas.example import ExampleSchema
from app.core.decorators import validate_request
from app.core.pagination import paginate

example_bp = Blueprint('example', __name__, url_prefix='/api/v2/examples')
example_schema = ExampleSchema()
examples_schema = ExampleSchema(many=True)

@example_bp.route('', methods=['GET'])
@jwt_required()
def get_examples():
    """Get all examples with pagination."""
    service = ExampleService(db.session)
    
    # Get filters from query params
    filters = {
        'status': request.args.get('status'),
        'user_id': request.args.get('user_id', type=int)
    }
    
    # Get examples
    examples = service.get_all(filters)
    
    # Paginate results
    return paginate(examples, examples_schema)

@example_bp.route('/<int:example_id>', methods=['GET'])
@jwt_required()
def get_example(example_id):
    """Get single example."""
    service = ExampleService(db.session)
    example = service.get_by_id(example_id)
    
    return jsonify(example_schema.dump(example))

@example_bp.route('', methods=['POST'])
@jwt_required()
@validate_request(ExampleSchema)
def create_example(validated_data):
    """Create new example."""
    service = ExampleService(db.session)
    
    # Add current user
    validated_data['user_id'] = get_jwt_identity()
    
    # Create example
    example = service.create(validated_data)
    
    return jsonify(example_schema.dump(example)), 201

@example_bp.route('/<int:example_id>', methods=['PUT'])
@jwt_required()
@validate_request(ExampleSchema, partial=True)
def update_example(example_id, validated_data):
    """Update example."""
    service = ExampleService(db.session)
    example = service.update(example_id, validated_data)
    
    return jsonify(example_schema.dump(example))

@example_bp.route('/<int:example_id>', methods=['DELETE'])
@jwt_required()
def delete_example(example_id):
    """Delete example."""
    service = ExampleService(db.session)
    service.delete(example_id)
    
    return '', 204
```

---

## Database Development

### Creating Migrations

```bash
# Create new migration
flask db migrate -m "Add example table"

# Review migration file
# Edit if necessary in migrations/versions/

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Migration Best Practices

```python
"""Add example table

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create table
    op.create_table('examples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_example_name', 'examples', ['name'])
    op.create_index('idx_example_user_status', 'examples', ['user_id', 'status'])

def downgrade():
    # Drop indexes
    op.drop_index('idx_example_user_status', table_name='examples')
    op.drop_index('idx_example_name', table_name='examples')
    
    # Drop table
    op.drop_table('examples')
```

### Database Performance

```python
# Optimize queries
from sqlalchemy.orm import joinedload, selectinload

# Eager loading
examples = db.session.query(Example)\
    .options(joinedload(Example.user))\
    .filter_by(status='active')\
    .all()

# Select specific columns
from sqlalchemy.orm import load_only

examples = db.session.query(Example)\
    .options(load_only(Example.id, Example.name))\
    .all()

# Use indexes effectively
class Example(BaseModel):
    __table_args__ = (
        db.Index('idx_created_at_desc', sa.desc('created_at')),
        db.Index('idx_composite', 'user_id', 'status', 'created_at'),
    )
```

---

## API Development

### RESTful Design

```python
# RESTful URL patterns
GET    /api/v2/resources          # List all resources
GET    /api/v2/resources/:id      # Get specific resource
POST   /api/v2/resources          # Create new resource
PUT    /api/v2/resources/:id      # Update resource
PATCH  /api/v2/resources/:id      # Partial update
DELETE /api/v2/resources/:id      # Delete resource

# Nested resources
GET    /api/v2/users/:id/resources
POST   /api/v2/users/:id/resources

# Actions
POST   /api/v2/resources/:id/activate
POST   /api/v2/resources/:id/archive
```

### API Versioning

```python
# URL versioning
/api/v1/resources
/api/v2/resources

# Header versioning
Accept: application/vnd.bdc.v2+json

# Implementation
from flask import Blueprint

# Version 1
v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Version 2
v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')
```

### Error Handling

```python
# app/core/exceptions.py
class APIException(Exception):
    """Base API exception."""
    status_code = 500
    message = 'Internal server error'
    
    def __init__(self, message=None, status_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self):
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'status': self.status_code
        }

class NotFoundError(APIException):
    status_code = 404
    message = 'Resource not found'

class ValidationError(APIException):
    status_code = 422
    message = 'Validation failed'

class UnauthorizedError(APIException):
    status_code = 401
    message = 'Unauthorized'

# Error handler
@app.errorhandler(APIException)
def handle_api_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
```

---

## Testing Guide

### Frontend Testing

#### Component Testing

```javascript
// MyComponent.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  const defaultProps = {
    title: 'Test Title',
    onSubmit: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<MyComponent {...defaultProps} />);
    
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('handles form submission', async () => {
    const user = userEvent.setup();
    render(<MyComponent {...defaultProps} />);
    
    const input = screen.getByLabelText('Name');
    const submitButton = screen.getByRole('button', { name: 'Submit' });
    
    await user.type(input, 'John Doe');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(defaultProps.onSubmit).toHaveBeenCalledWith({
        name: 'John Doe'
      });
    });
  });

  it('shows validation errors', async () => {
    const user = userEvent.setup();
    render(<MyComponent {...defaultProps} />);
    
    const submitButton = screen.getByRole('button', { name: 'Submit' });
    await user.click(submitButton);
    
    expect(screen.getByText('Name is required')).toBeInTheDocument();
  });
});
```

#### Integration Testing

```javascript
// integration.test.js
import { render, screen, waitFor } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import App from './App';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.json({
        data: [
          { id: 1, name: 'John Doe' },
          { id: 2, name: 'Jane Smith' }
        ]
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('loads and displays users', async () => {
  render(<App />);
  
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });
});
```

### Backend Testing

#### Unit Testing

```python
# tests/unit/test_example_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.example_service import ExampleService
from app.models.example import Example
from app.core.exceptions import NotFoundError

class TestExampleService:
    
    @pytest.fixture
    def service(self):
        mock_db = Mock()
        return ExampleService(mock_db)
    
    @pytest.fixture
    def example_data(self):
        return {
            'name': 'Test Example',
            'description': 'Test description',
            'status': 'active',
            'user_id': 1
        }
    
    def test_create_example(self, service, example_data):
        # Mock the schema validation
        with patch.object(service.schema, 'load', return_value=example_data):
            # Call service method
            result = service.create(example_data)
            
            # Assertions
            assert service.db.add.called
            assert service.db.commit.called
            assert service.db.refresh.called
    
    def test_get_by_id_not_found(self, service):
        # Mock query
        service.db.query.return_value.get.return_value = None
        
        # Should raise NotFoundError
        with pytest.raises(NotFoundError):
            service.get_by_id(999)
    
    def test_update_example(self, service, example_data):
        # Create mock example
        mock_example = Mock(spec=Example)
        mock_example.id = 1
        
        # Mock get_by_id
        with patch.object(service, 'get_by_id', return_value=mock_example):
            with patch.object(service.schema, 'load', return_value={'name': 'Updated'}):
                # Call update
                result = service.update(1, {'name': 'Updated'})
                
                # Assertions
                assert mock_example.name == 'Updated'
                assert service.db.commit.called
```

#### Integration Testing

```python
# tests/integration/test_example_api.py
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.example import Example

@pytest.fixture
def client():
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    # Create test user
    user = User(email='test@example.com', password='password')
    db.session.add(user)
    db.session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password'
    })
    
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_create_example(client, auth_headers):
    response = client.post('/api/v2/examples', 
        headers=auth_headers,
        json={
            'name': 'Test Example',
            'description': 'Test description'
        }
    )
    
    assert response.status_code == 201
    assert response.json['name'] == 'Test Example'

def test_get_examples(client, auth_headers):
    # Create test data
    example = Example(name='Test', user_id=1)
    db.session.add(example)
    db.session.commit()
    
    # Get examples
    response = client.get('/api/v2/examples', headers=auth_headers)
    
    assert response.status_code == 200
    assert len(response.json['data']) == 1
```

---

## Security Best Practices

### Authentication & Authorization

```python
# Secure password hashing
from werkzeug.security import generate_password_hash, check_password_hash

class User(BaseModel):
    password_hash = Column(String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Role-based access control
from functools import wraps
from flask_jwt_extended import get_jwt_identity

def require_role(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@example_bp.route('/admin', methods=['GET'])
@jwt_required()
@require_role(['admin', 'super_admin'])
def admin_endpoint():
    return jsonify({'message': 'Admin access granted'})
```

### Input Validation

```python
# SQL injection prevention
# Always use parameterized queries
user = db.session.query(User).filter_by(email=email).first()  # Good
user = db.session.execute(f"SELECT * FROM users WHERE email = '{email}'")  # Bad

# XSS prevention
from markupsafe import escape

@app.template_filter('sanitize')
def sanitize_html(text):
    return escape(text)

# File upload validation
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(file):
    if not file:
        raise ValidationError('No file provided')
    
    if not allowed_file(file.filename):
        raise ValidationError('Invalid file type')
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise ValidationError('File too large')
```

### Data Protection

```python
# Encrypt sensitive data
from cryptography.fernet import Fernet

class EncryptedField:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, value):
        if value is None:
            return None
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt(self, value):
        if value is None:
            return None
        return self.cipher.decrypt(value.encode()).decode()

# Audit logging
class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    details = Column(JSON)
    
    @classmethod
    def log(cls, action, resource_type=None, resource_id=None, details=None):
        log = cls(
            user_id=get_jwt_identity(),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=details
        )
        db.session.add(log)
        db.session.commit()
```

---

## Performance Guidelines

### Frontend Performance

```javascript
// Code splitting
const HeavyComponent = lazy(() => import('./HeavyComponent'));

// Memoization
const ExpensiveComponent = memo(({ data }) => {
  const processedData = useMemo(() => {
    return heavyProcessing(data);
  }, [data]);
  
  return <div>{processedData}</div>;
});

// Debouncing
const SearchInput = () => {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);
  
  useEffect(() => {
    if (debouncedQuery) {
      searchAPI(debouncedQuery);
    }
  }, [debouncedQuery]);
  
  return <input value={query} onChange={e => setQuery(e.target.value)} />;
};

// Virtual scrolling
import { FixedSizeList } from 'react-window';

const VirtualList = ({ items }) => (
  <FixedSizeList
    height={600}
    itemCount={items.length}
    itemSize={50}
    width="100%"
  >
    {({ index, style }) => (
      <div style={style}>{items[index].name}</div>
    )}
  </FixedSizeList>
);
```

### Backend Performance

```python
# Query optimization
from sqlalchemy.orm import joinedload, selectinload, contains_eager

# N+1 query problem solution
# Bad
users = User.query.all()
for user in users:
    print(user.posts)  # N queries

# Good
users = User.query.options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # 1 query

# Caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300, key_prefix='all_users')
def get_all_users():
    return User.query.all()

# Database connection pooling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

# Async operations
from concurrent.futures import ThreadPoolExecutor
import asyncio

executor = ThreadPoolExecutor(max_workers=4)

async def process_batch(items):
    loop = asyncio.get_event_loop()
    tasks = []
    
    for item in items:
        task = loop.run_in_executor(executor, process_item, item)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

---

## Git Workflow

### Branch Strategy

```bash
main
├── develop
│   ├── feature/JIRA-123-user-authentication
│   ├── feature/JIRA-456-payment-integration
│   └── feature/JIRA-789-reporting-module
├── release/v1.2.0
└── hotfix/JIRA-999-critical-bug
```

### Commit Messages

```bash
# Format
<type>(<scope>): <subject>

<body>

<footer>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation only
style:    Code style changes
refactor: Code refactoring
perf:     Performance improvement
test:     Adding tests
chore:    Maintenance tasks

# Examples
feat(auth): implement two-factor authentication

- Add TOTP support
- Create QR code generation endpoint
- Update user model with 2FA fields

Closes JIRA-123

fix(api): resolve race condition in token refresh

The token refresh endpoint was vulnerable to race conditions
when multiple requests were made simultaneously. This fix
implements a mutex lock to ensure thread safety.

Fixes #456
```

### Pull Request Process

1. **Create feature branch**
```bash
git checkout -b feature/JIRA-123-feature-name
```

2. **Make changes and commit**
```bash
git add .
git commit -m "feat(module): implement feature"
```

3. **Push and create PR**
```bash
git push origin feature/JIRA-123-feature-name
```

4. **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
```

---

## Debugging Guide

### Frontend Debugging

```javascript
// React Developer Tools
// Install browser extension

// Debug component renders
const MyComponent = () => {
  console.log('MyComponent rendered');
  
  useEffect(() => {
    console.log('MyComponent mounted');
    return () => console.log('MyComponent unmounted');
  }, []);
  
  return <div>Content</div>;
};

// Performance profiling
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
}

<Profiler id="MyComponent" onRender={onRenderCallback}>
  <MyComponent />
</Profiler>

// Network debugging
window.addEventListener('fetch', (event) => {
  console.log('Fetching:', event.request.url);
});
```

### Backend Debugging

```python
# Flask Debug Mode
app.config['DEBUG'] = True  # Development only!

# Logging
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.debug(f"{request.method} {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Body: {request.get_data()}")

# SQL query logging
app.config['SQLALCHEMY_ECHO'] = True

# Python debugger
import pdb

def problematic_function():
    # Set breakpoint
    pdb.set_trace()
    
    # Your code here
    result = complex_calculation()
    return result

# Flask Debug Toolbar
from flask_debugtoolbar import DebugToolbarExtension

app.config['DEBUG_TB_ENABLED'] = app.debug
toolbar = DebugToolbarExtension(app)

# Custom error pages
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', error=error), 500
```

---

## Contributing

### Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Run tests
6. Submit a pull request

### Code Review Checklist

- [ ] Code follows project style guide
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Performance impact considered
- [ ] Backward compatibility maintained
- [ ] Database migrations included if needed
- [ ] API documentation updated if needed

### Release Process

1. **Version Bump**
```bash
# Update version in:
# - package.json
# - setup.py
# - __version__.py
```

2. **Update Changelog**
```markdown
## [1.2.0] - 2024-01-15

### Added
- New feature X
- Enhancement Y

### Fixed
- Bug fix Z

### Changed
- Updated dependency A
```

3. **Create Release**
```bash
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

---

*Last Updated: January 2025*
*Version: 1.0.0*