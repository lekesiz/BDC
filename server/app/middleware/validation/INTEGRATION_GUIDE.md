# Integration Guide for BDC Validation System

This guide provides step-by-step instructions for integrating the validation system into existing and new API endpoints.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Integration Steps](#integration-steps)
3. [Migrating Existing Endpoints](#migrating-existing-endpoints)
4. [Common Patterns](#common-patterns)
5. [Performance Optimization](#performance-optimization)
6. [Security Best Practices](#security-best-practices)

## Quick Start

### 1. Initialize the Validation Middleware

In your `app.py` or application factory:

```python
from app.middleware.validation import ValidationMiddleware

def create_app():
    app = Flask(__name__)
    
    # Initialize validation middleware
    validation_middleware = ValidationMiddleware(app)
    
    # Or if using application factory pattern
    validation_middleware = ValidationMiddleware()
    validation_middleware.init_app(app)
    
    return app
```

### 2. Create Your First Validated Endpoint

```python
from flask import Blueprint, jsonify, g
from app.middleware.validation.decorators import validate_json
from app.middleware.validation.schemas import LoginSchema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@validate_json(LoginSchema)
def login():
    # Access validated data
    data = g.validated_data
    
    # Your business logic here
    user = authenticate_user(data['email'], data['password'])
    
    return jsonify({'token': generate_token(user)})
```

## Integration Steps

### Step 1: Analyze Current Endpoints

Identify endpoints that need validation:

```python
# Before
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # Manual validation
    if not data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    # ... more validation
```

### Step 2: Create Validation Schema

```python
# app/middleware/validation/schemas/user_schemas.py
from marshmallow import Schema, fields, validate
from app.middleware.validation.schema_validator import SecureFields

class UserCreateSchema(Schema):
    email = SecureFields.email(required=True)
    password = SecureFields.password(required=True)
    first_name = SecureFields.name(required=True)
    last_name = SecureFields.name(required=True)
    role = fields.String(
        missing='user',
        validate=validate.OneOf(['user', 'admin'])
    )
```

### Step 3: Apply Validation Decorator

```python
# After
from app.middleware.validation.decorators import validate_json
from app.middleware.validation.schemas import UserCreateSchema

@app.route('/api/users', methods=['POST'])
@validate_json(UserCreateSchema)
def create_user():
    data = g.validated_data  # Already validated!
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
```

### Step 4: Add Business Rule Validation

```python
from app.middleware.validation.decorators import validate_business_rule

@app.route('/api/users', methods=['POST'])
@validate_json(UserCreateSchema)
@validate_business_rule('user', action='registration')
def create_user():
    # Both schema and business rules validated
    data = g.validated_data
    # ...
```

## Migrating Existing Endpoints

### Migration Checklist

- [ ] Identify all input sources (JSON, query params, forms, files)
- [ ] Document current validation rules
- [ ] Create appropriate schemas
- [ ] Replace manual validation with decorators
- [ ] Test thoroughly
- [ ] Update API documentation

### Example Migration

#### Before Migration

```python
@app.route('/api/beneficiaries', methods=['POST'])
@login_required
def create_beneficiary():
    data = request.get_json()
    
    # Manual validation
    errors = {}
    
    if not data.get('first_name'):
        errors['first_name'] = 'First name is required'
    
    if not data.get('email'):
        errors['email'] = 'Email is required'
    elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
        errors['email'] = 'Invalid email format'
    
    if 'date_of_birth' in data:
        try:
            dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
            age = (datetime.now() - dob).days // 365
            if age < 18:
                errors['date_of_birth'] = 'Must be 18 or older'
        except ValueError:
            errors['date_of_birth'] = 'Invalid date format'
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Create beneficiary
    beneficiary = Beneficiary(**data)
    db.session.add(beneficiary)
    db.session.commit()
    
    return jsonify(beneficiary.to_dict()), 201
```

#### After Migration

```python
from app.middleware.validation.decorators import validate_json, validate_business_rule
from app.middleware.validation.schemas import BeneficiaryCreateSchema

@app.route('/api/beneficiaries', methods=['POST'])
@login_required
@validate_json(BeneficiaryCreateSchema)
@validate_business_rule('beneficiary', action='registration')
def create_beneficiary():
    # All validation handled by decorators
    data = g.validated_data
    
    beneficiary = Beneficiary(**data)
    db.session.add(beneficiary)
    db.session.commit()
    
    return jsonify(beneficiary.to_dict()), 201
```

## Common Patterns

### 1. Pagination with Query Validation

```python
from app.middleware.validation.decorators import validate_query
from app.middleware.validation.schemas import PaginationSchema

@app.route('/api/users')
@validate_query(PaginationSchema)
def list_users():
    params = g.validated_data
    
    users = User.query.paginate(
        page=params['page'],
        per_page=params['per_page'],
        error_out=False
    )
    
    return jsonify({
        'users': [u.to_dict() for u in users.items],
        'total': users.total,
        'pages': users.pages
    })
```

### 2. File Upload with Validation

```python
from app.middleware.validation.decorators import validate_files

@app.route('/api/documents', methods=['POST'])
@validate_files(
    max_size=10*1024*1024,
    allowed_extensions=['pdf', 'doc', 'docx']
)
def upload_document():
    file = request.files['file']
    file_info = g.file_info
    
    # Save file securely
    document = save_document(file, file_info)
    
    return jsonify(document.to_dict()), 201
```

### 3. Complex Validation with Multiple Sources

```python
@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    # Validate JSON body
    body_schema = ReportGenerationSchema()
    body_data = body_schema.load(request.get_json())
    
    # Validate query parameters
    query_schema = ReportFiltersSchema()
    query_data = query_schema.load(request.args)
    
    # Combine and validate
    combined_data = {**body_data, **query_data}
    
    # Generate report
    report = generate_report(combined_data)
    return jsonify(report.to_dict())
```

### 4. Conditional Validation

```python
def create_conditional_schema(user_role):
    """Create schema based on user role."""
    
    class ConditionalSchema(Schema):
        name = fields.String(required=True)
        
        if user_role == 'admin':
            # Admin-only fields
            priority = fields.String(
                required=True,
                validate=validate.OneOf(['low', 'medium', 'high'])
            )
            assigned_to = fields.Integer()
    
    return ConditionalSchema

@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    # Get schema based on user role
    schema_class = create_conditional_schema(g.current_user.role)
    
    # Validate with dynamic schema
    schema = schema_class()
    data = schema.load(request.get_json())
    
    # Create task
    task = Task(**data)
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201
```

## Performance Optimization

### 1. Schema Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_schema(schema_name):
    """Cache schema instances for performance."""
    schema_map = {
        'user_create': UserCreateSchema,
        'user_update': UserUpdateSchema,
        # ... more schemas
    }
    return schema_map[schema_name]()
```

### 2. Lazy Validation

```python
from app.middleware.validation.decorators import validate_request

@app.route('/api/bulk-upload', methods=['POST'])
@validate_request(
    schema=None,  # Skip schema validation
    validate_sql=False,  # Skip SQL validation for performance
    custom_validators=[validate_bulk_data]  # Custom fast validation
)
def bulk_upload():
    # Process large dataset with minimal validation overhead
    pass
```

### 3. Batch Validation

```python
def validate_bulk_items(items, schema_class):
    """Validate multiple items efficiently."""
    schema = schema_class(many=True)
    
    try:
        validated_items = schema.load(items)
        return validated_items, None
    except ValidationError as e:
        return None, e.messages
```

## Security Best Practices

### 1. Always Validate User Input

```python
# Bad - No validation
@app.route('/api/search')
def search():
    query = request.args.get('q')
    results = db.session.execute(f"SELECT * FROM users WHERE name LIKE '%{query}%'")
    
# Good - With validation
@app.route('/api/search')
@validate_query(SearchSchema)
def search():
    params = g.validated_data
    query = params['query']
    results = User.query.filter(User.name.contains(query)).all()
```

### 2. Sanitize Output

```python
from app.middleware.validation.decorators import sanitize_output

@app.route('/api/users/<int:user_id>')
@sanitize_output(
    remove_fields=['password_hash', 'reset_token', 'api_key'],
    fields_to_sanitize=['bio', 'notes']
)
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
```

### 3. Rate Limiting

```python
from app.middleware.validation.decorators import rate_limit

@app.route('/api/password-reset', methods=['POST'])
@rate_limit(max_requests=3, window=3600)  # 3 attempts per hour
@validate_json(PasswordResetSchema)
def request_password_reset():
    # Protected from brute force attacks
    pass
```

### 4. Input Length Limits

```python
class SecureSchema(Schema):
    # Limit input lengths to prevent DoS
    comment = fields.String(
        required=True,
        validate=validate.Length(min=1, max=1000)
    )
    
    tags = fields.List(
        fields.String(validate=validate.Length(max=50)),
        validate=validate.Length(max=10)  # Max 10 tags
    )
```

### 5. Content-Type Validation

```python
@app.before_request
def validate_content_type():
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.data and not request.is_json:
            # For JSON APIs, enforce JSON content type
            if not request.path.startswith('/api/upload'):
                abort(400, 'Content-Type must be application/json')
```

## Testing Integration

### Unit Tests

```python
def test_user_creation_validation(client):
    # Test missing required field
    response = client.post('/api/users', json={})
    assert response.status_code == 400
    assert 'email' in response.json['errors']
    
    # Test invalid email
    response = client.post('/api/users', json={
        'email': 'invalid-email',
        'password': 'ValidPass123!',
        'first_name': 'John',
        'last_name': 'Doe'
    })
    assert response.status_code == 400
    assert 'email' in response.json['errors']
    
    # Test successful validation
    response = client.post('/api/users', json={
        'email': 'john@example.com',
        'password': 'ValidPass123!',
        'first_name': 'John',
        'last_name': 'Doe'
    })
    assert response.status_code == 201
```

### Integration Tests

```python
def test_full_validation_flow(client, mock_db):
    # Test complete validation pipeline
    with patch('app.services.EmailService.send_verification'):
        response = client.post('/api/register', json={
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'terms_accepted': True
        })
    
    assert response.status_code == 201
    assert 'user' in response.json
    
    # Verify user was created with sanitized data
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None
    assert user.first_name == 'New'
```

## Monitoring and Logging

### Validation Metrics

```python
from app.utils.metrics import validation_counter, validation_timer

@validation_timer.time()
def validate_with_metrics(schema, data):
    """Track validation performance."""
    try:
        result = schema.load(data)
        validation_counter.labels(status='success').inc()
        return result
    except ValidationError as e:
        validation_counter.labels(status='failure').inc()
        raise
```

### Audit Logging

```python
@app.after_request
def log_validation_failures(response):
    if response.status_code == 400 and 'validation' in str(response.data):
        logger.warning(
            'Validation failure',
            extra={
                'endpoint': request.endpoint,
                'method': request.method,
                'ip': request.remote_addr,
                'user_id': getattr(g, 'current_user', {}).get('id'),
                'errors': response.json.get('errors')
            }
        )
    return response
```

## Troubleshooting

### Common Issues and Solutions

1. **Schema not found**
   ```python
   # Ensure schema is imported
   from app.middleware.validation.schemas import YourSchema
   ```

2. **Validation too strict**
   ```python
   # Use partial validation for updates
   @validate_json(UserUpdateSchema, partial=True)
   ```

3. **Custom validation needed**
   ```python
   # Add custom validators
   @validate_request(
       schema=BaseSchema,
       custom_validators=[your_custom_validator]
   )
   ```

4. **Performance issues**
   ```python
   # Disable expensive validations for bulk operations
   @validate_request(validate_sql=False)
   ```

## Next Steps

1. Review all API endpoints and identify validation needs
2. Create schemas for all input data
3. Implement business rule validators
4. Add comprehensive tests
5. Monitor validation metrics
6. Document validation rules in API documentation