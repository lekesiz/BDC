"""
Example usage of the validation system in API endpoints.
"""

from flask import Blueprint, request, jsonify, g
from .decorators import (
    validate_json, validate_query, validate_files,
    validate_business_rule, sanitize_output, rate_limit
)
from .schemas import (
    LoginSchema, RegisterSchema, BeneficiaryCreateSchema,
    AppointmentCreateSchema, PaginationSchema, SearchSchema
)
from app.models import User, Beneficiary, Appointment
from app.services import AuthService, BeneficiaryService

# Create example blueprint
api = Blueprint('validated_api', __name__, url_prefix='/api/v2')


# Authentication examples
@api.route('/auth/login', methods=['POST'])
@validate_json(LoginSchema)
@rate_limit(max_requests=5, window=300)  # 5 attempts per 5 minutes
def login():
    """Login endpoint with validation."""
    data = g.validated_data
    
    # Validated data is safe to use
    user = AuthService.authenticate(
        email=data['email'],
        password=data['password']
    )
    
    if not user:
        return jsonify({
            'error': 'Invalid credentials',
            'status': 'error'
        }), 401
    
    token = AuthService.generate_token(user)
    
    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'status': 'success'
    })


@api.route('/auth/register', methods=['POST'])
@validate_json(RegisterSchema)
@validate_business_rule('user', action='registration')
def register():
    """Registration endpoint with validation."""
    data = g.validated_data
    
    # Create user with validated data
    user = AuthService.register_user(data)
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict(),
        'status': 'success'
    }), 201


# Beneficiary examples
@api.route('/beneficiaries', methods=['GET'])
@validate_query(PaginationSchema)
@sanitize_output(remove_fields=['national_id', 'medical_conditions'])
def list_beneficiaries():
    """List beneficiaries with pagination and sanitization."""
    filters = g.validated_data
    
    beneficiaries = BeneficiaryService.get_paginated(
        page=filters['page'],
        per_page=filters['per_page'],
        sort_by=filters['sort_by'],
        sort_order=filters['sort_order']
    )
    
    return jsonify({
        'beneficiaries': [b.to_dict() for b in beneficiaries.items],
        'total': beneficiaries.total,
        'pages': beneficiaries.pages,
        'current_page': beneficiaries.page,
        'status': 'success'
    })


@api.route('/beneficiaries', methods=['POST'])
@validate_json(BeneficiaryCreateSchema)
@validate_business_rule('beneficiary', action='registration')
def create_beneficiary():
    """Create beneficiary with validation."""
    data = g.validated_data
    
    beneficiary = BeneficiaryService.create(data)
    
    return jsonify({
        'beneficiary': beneficiary.to_dict(),
        'message': 'Beneficiary created successfully',
        'status': 'success'
    }), 201


# Appointment examples
@api.route('/appointments', methods=['POST'])
@validate_json(AppointmentCreateSchema)
@validate_business_rule('appointment', action='booking')
def create_appointment():
    """Create appointment with business rule validation."""
    data = g.validated_data
    
    appointment = Appointment(**data)
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({
        'appointment': appointment.to_dict(),
        'message': 'Appointment scheduled successfully',
        'status': 'success'
    }), 201


# File upload example
@api.route('/documents', methods=['POST'])
@validate_files(
    max_size=50 * 1024 * 1024,  # 50MB
    allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png']
)
def upload_document():
    """Upload document with file validation."""
    file = request.files['file']
    file_info = g.file_info
    
    # Additional form data validation
    title = request.form.get('title', file_info['filename'])
    description = request.form.get('description', '')
    
    # Save file using validated info
    document = DocumentService.save_file(
        file=file,
        title=title,
        description=description,
        file_info=file_info
    )
    
    return jsonify({
        'document': document.to_dict(),
        'message': 'Document uploaded successfully',
        'status': 'success'
    }), 201


# Search example
@api.route('/search', methods=['POST'])
@validate_json(SearchSchema)
@rate_limit(max_requests=30, window=60)  # 30 searches per minute
def search():
    """Global search with validation and rate limiting."""
    data = g.validated_data
    
    results = SearchService.search(
        query=data['query'],
        search_type=data.get('search_type', 'all'),
        filters=data.get('filters', {}),
        page=data['page'],
        per_page=data['per_page']
    )
    
    return jsonify({
        'results': results['items'],
        'total': results['total'],
        'page': data['page'],
        'status': 'success'
    })


# Complex validation example
@api.route('/programs/<int:program_id>/enroll', methods=['POST'])
@validate_json(schema=None)  # Basic JSON validation
@validate_business_rule('beneficiary', action='enrollment')
def enroll_in_program(program_id):
    """Enroll beneficiary in program with complex validation."""
    data = request.get_json()
    data['program_id'] = program_id
    
    # Business rule validation will check prerequisites, capacity, etc.
    enrollment = ProgramService.enroll_beneficiary(
        beneficiary_id=data['beneficiary_id'],
        program_id=program_id
    )
    
    return jsonify({
        'enrollment': enrollment.to_dict(),
        'message': 'Successfully enrolled in program',
        'status': 'success'
    }), 201


# Example with custom validation
@api.route('/reports/generate', methods=['POST'])
def generate_report():
    """Generate report with custom validation."""
    from .schemas import ReportGenerationSchema
    from .decorators import validate_request
    
    # Apply validation with custom rules
    @validate_request(
        schema=ReportGenerationSchema,
        custom_validators=[
            lambda data: _validate_report_permissions(data),
            lambda data: _validate_data_availability(data)
        ]
    )
    def _generate():
        data = g.validated_data
        
        report = ReportService.generate(
            report_type=data['report_type'],
            date_from=data['date_from'],
            date_to=data['date_to'],
            filters=data
        )
        
        return jsonify({
            'report_id': report.id,
            'download_url': report.download_url,
            'status': 'success'
        })
    
    return _generate()


def _validate_report_permissions(data):
    """Custom validator for report permissions."""
    user = g.current_user
    
    if not user.has_permission('generate_reports'):
        raise ValueError('You do not have permission to generate reports')
    
    # Check if user can access requested beneficiaries
    if 'beneficiary_ids' in data:
        accessible_ids = user.get_accessible_beneficiary_ids()
        for bid in data['beneficiary_ids']:
            if bid not in accessible_ids:
                raise ValueError(f'You do not have access to beneficiary {bid}')


def _validate_data_availability(data):
    """Custom validator for data availability."""
    # Check if data exists for the requested period
    if data['report_type'] == 'attendance':
        # Example: Check if attendance data exists
        has_data = Attendance.query.filter(
            Attendance.date >= data['date_from'],
            Attendance.date <= data['date_to']
        ).first()
        
        if not has_data:
            raise ValueError('No attendance data available for the selected period')


# Error handling example
@api.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle validation errors consistently."""
    return jsonify({
        'error': 'Validation failed',
        'errors': error.messages,
        'status': 'error'
    }), 400


@api.errorhandler(ValueError)
def handle_value_error(error):
    """Handle business rule violations."""
    return jsonify({
        'error': str(error),
        'status': 'error'
    }), 400


# Middleware registration example
def register_validation_middleware(app):
    """Register validation middleware with the Flask app."""
    from .validation_middleware import validation_middleware
    
    # Initialize middleware
    validation_middleware.init_app(app)
    
    # Configure middleware settings
    app.config['VALIDATION_ERROR_STATUS'] = 400
    app.config['VALIDATION_SQL_CHECK'] = True
    app.config['VALIDATION_MAX_JSON_SIZE'] = 10 * 1024 * 1024  # 10MB
    
    # Register custom validators
    from .schema_validator import SchemaValidator
    validator = SchemaValidator()
    
    # Add custom field validators
    validator.register_validator('tenant_code', validate_tenant_code)
    validator.register_validator('currency', validate_currency)
    
    return app


def validate_tenant_code(value):
    """Custom validator for tenant codes."""
    if not re.match(r'^[A-Z]{3}\d{4}$', value):
        raise ValidationError('Tenant code must be 3 uppercase letters followed by 4 digits')
    return value


def validate_currency(value):
    """Custom validator for currency codes."""
    valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
    if value not in valid_currencies:
        raise ValidationError(f'Currency must be one of: {", ".join(valid_currencies)}')
    return value