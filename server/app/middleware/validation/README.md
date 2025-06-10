# BDC Input Validation and Sanitization System

A comprehensive validation and sanitization middleware system for the BDC project, providing robust protection against common security vulnerabilities.

## Features

### 1. **Schema-Based Validation**
- Uses Marshmallow for declarative schema validation
- Type checking and format validation
- Custom field validators
- Nested schema support
- Automatic error message enhancement

### 2. **Security Protection**
- **XSS Prevention**: HTML sanitization and dangerous content detection
- **SQL Injection Prevention**: Pattern matching and parameterized query enforcement
- **Command Injection Prevention**: Shell command pattern detection
- **Path Traversal Prevention**: Filename sanitization
- **File Upload Security**: MIME type validation, size limits, content scanning

### 3. **Input Sanitization**
- String sanitization with configurable rules
- HTML cleaning with allowed tags/attributes
- URL validation and sanitization
- Email normalization
- Unicode normalization
- Filename security

### 4. **Business Logic Validation**
- Beneficiary registration rules
- Appointment scheduling conflicts
- Program enrollment prerequisites
- Evaluation submission deadlines
- User role change authorization

### 5. **Specialized Validators**
- Email validation with deliverability checks
- Password strength validation
- Phone number validation (international)
- Credit card validation (Luhn algorithm)
- Date/time validation with business hours
- JSON structure validation

## Installation

The validation system is integrated into the BDC server. No additional installation required.

## Usage

### Basic Request Validation

```python
from app.middleware.validation import validate_json
from app.middleware.validation.schemas import LoginSchema

@app.route('/api/login', methods=['POST'])
@validate_json(LoginSchema)
def login():
    # Access validated data via g.validated_data
    data = g.validated_data
    # data is guaranteed to be valid according to LoginSchema
```

### Query Parameter Validation

```python
from app.middleware.validation import validate_query
from app.middleware.validation.schemas import PaginationSchema

@app.route('/api/users')
@validate_query(PaginationSchema)
def list_users():
    filters = g.validated_data
    # filters contains validated pagination parameters
```

### File Upload Validation

```python
from app.middleware.validation import validate_files

@app.route('/api/upload', methods=['POST'])
@validate_files(max_size=10*1024*1024, allowed_extensions=['pdf', 'doc'])
def upload_document():
    file = request.files['file']
    file_info = g.file_info  # Contains validated file metadata
```

### Business Rule Validation

```python
from app.middleware.validation import validate_business_rule

@app.route('/api/appointments', methods=['POST'])
@validate_json(AppointmentCreateSchema)
@validate_business_rule('appointment', action='booking')
def create_appointment():
    # Both schema and business rules are validated
    data = g.validated_data
```

### Custom Validators

```python
def validate_custom_rule(data):
    if data.get('field') == 'invalid_value':
        raise ValueError('Custom validation failed')

@app.route('/api/custom', methods=['POST'])
@validate_request(
    schema=CustomSchema,
    custom_validators=[validate_custom_rule]
)
def custom_endpoint():
    data = g.validated_data
```

## Schema Examples

### Creating a Validation Schema

```python
from marshmallow import Schema, fields, validate, validates_schema
from app.middleware.validation.schema_validator import SecureFields

class UserRegistrationSchema(Schema):
    # Use secure field definitions
    email = SecureFields.email(required=True)
    password = SecureFields.password(required=True)
    first_name = SecureFields.name(required=True)
    last_name = SecureFields.name(required=True)
    phone = SecureFields.phone(required=False)
    
    # Custom field with validation
    age = fields.Integer(
        required=True,
        validate=validate.Range(min=18, max=100)
    )
    
    # Enum field
    role = fields.String(
        validate=validate.OneOf(['student', 'trainer', 'admin'])
    )
    
    # Cross-field validation
    @validates_schema
    def validate_data(self, data, **kwargs):
        if data.get('role') == 'admin' and data.get('age') < 21:
            raise ValidationError('Admins must be at least 21 years old')
```

## Security Features

### XSS Prevention

```python
from app.middleware.validation.sanitizers import InputSanitizer

sanitizer = InputSanitizer()

# Basic string sanitization
clean_text = sanitizer.sanitize_string(user_input)

# HTML sanitization with allowed tags
clean_html = sanitizer.sanitize_html(
    html_content,
    allowed_tags=['p', 'strong', 'em', 'a'],
    allowed_attributes={'a': ['href', 'title']}
)
```

### SQL Injection Prevention

```python
from app.middleware.validation.validators import SQLValidator

validator = SQLValidator()

# Check for SQL injection patterns
try:
    validator.validate(user_input)
except ValueError:
    # SQL injection attempt detected
    pass
```

### File Upload Security

```python
from app.middleware.validation.validators import FileValidator

validator = FileValidator(
    allowed_extensions=['pdf', 'doc', 'docx'],
    allowed_mimetypes=['application/pdf', 'application/msword'],
    max_size=10 * 1024 * 1024,  # 10MB
    check_content=True  # Scan file headers
)

file_info = validator.validate(uploaded_file)
```

## Business Validators

### Beneficiary Registration

```python
from app.middleware.validation.business_validators import BeneficiaryValidator

# Validates age, unique identifiers, emergency contacts
BeneficiaryValidator.validate_registration(beneficiary_data)
```

### Appointment Scheduling

```python
from app.middleware.validation.business_validators import AppointmentValidator

# Checks business hours, conflicts, advance booking rules
AppointmentValidator.validate_booking(appointment_data)
```

### Program Enrollment

```python
from app.middleware.validation.business_validators import ProgramValidator

# Validates prerequisites, capacity, eligibility
BeneficiaryValidator.validate_program_enrollment(beneficiary_id, program_id)
```

## Configuration

### Middleware Initialization

```python
from app.middleware.validation import ValidationMiddleware

# Initialize with Flask app
validation_middleware = ValidationMiddleware(app)

# Or initialize later
validation_middleware = ValidationMiddleware()
validation_middleware.init_app(app)
```

### Custom Configuration

```python
# Configure validation settings
app.config['VALIDATION_ERROR_STATUS'] = 400
app.config['VALIDATION_SQL_CHECK'] = True
app.config['VALIDATION_MAX_JSON_SIZE'] = 10 * 1024 * 1024
app.config['VALIDATION_RATE_LIMIT_BACKEND'] = 'redis'
```

## Error Handling

### Validation Errors

Validation errors return a consistent JSON format:

```json
{
    "error": "Validation failed",
    "errors": {
        "email": ["Invalid email format"],
        "password": ["Password must be at least 12 characters long"]
    },
    "status": "error"
}
```

### Business Rule Violations

```json
{
    "error": "Appointment must be booked at least 24 hours in advance",
    "status": "error"
}
```

## Best Practices

1. **Always validate user input** - Never trust data from clients
2. **Use appropriate validators** - Choose the right validator for each data type
3. **Combine validators** - Use both schema and business rule validation
4. **Sanitize output** - Use `@sanitize_output` decorator for sensitive data
5. **Rate limit endpoints** - Prevent abuse with `@rate_limit` decorator
6. **Log validation failures** - Monitor for potential attacks
7. **Keep schemas DRY** - Reuse common field definitions
8. **Test edge cases** - Include validation tests in your test suite

## Testing

### Unit Testing Validators

```python
import pytest
from app.middleware.validation.validators import EmailValidator

def test_email_validation():
    validator = EmailValidator()
    
    # Valid email
    assert validator.validate('user@example.com') == 'user@example.com'
    
    # Invalid email
    with pytest.raises(ValueError):
        validator.validate('invalid-email')
    
    # Blocked domain
    with pytest.raises(ValueError):
        validator.validate('user@tempmail.com')
```

### Integration Testing

```python
def test_api_validation(client):
    # Missing required field
    response = client.post('/api/login', json={})
    assert response.status_code == 400
    assert 'email' in response.json['errors']
    
    # Invalid data type
    response = client.post('/api/login', json={
        'email': 'invalid-email',
        'password': '123'  # Too short
    })
    assert response.status_code == 400
    assert 'email' in response.json['errors']
    assert 'password' in response.json['errors']
```

## Performance Considerations

1. **Caching** - Validation schemas are cached for performance
2. **Lazy Loading** - Validators are loaded on-demand
3. **Efficient Patterns** - Regex patterns are pre-compiled
4. **Batch Validation** - Multiple fields validated in single pass
5. **Early Termination** - Validation stops on first critical error

## Security Considerations

1. **Defense in Depth** - Multiple layers of validation
2. **Whitelist Approach** - Only allow known-good patterns
3. **Context-Aware** - Different rules for different contexts
4. **Audit Logging** - All validation failures are logged
5. **Rate Limiting** - Prevent validation DoS attacks

## Troubleshooting

### Common Issues

1. **"Validation failed" with no details**
   - Check if schema is properly defined
   - Ensure field names match

2. **"SQL injection detected" false positives**
   - Use `validate_sql=False` for fields that need SQL keywords
   - Consider using parameterized queries instead

3. **File upload fails**
   - Check MIME type matches extension
   - Verify file size limits
   - Ensure file content is not malicious

4. **Business rule validation fails**
   - Check prerequisites are met
   - Verify user permissions
   - Ensure data consistency

## Contributing

When adding new validators:

1. Extend appropriate base class
2. Add comprehensive tests
3. Document validation rules
4. Consider performance impact
5. Update this README

## License

This validation system is part of the BDC project and follows the same license terms.