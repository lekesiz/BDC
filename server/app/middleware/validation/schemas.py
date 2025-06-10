"""
Enhanced validation schemas for the BDC project using Marshmallow.
"""

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, post_load
from marshmallow.fields import Nested, List, Dict
from datetime import datetime, date
from .schema_validator import SecureFields


# Base schemas with common fields
class BaseSchema(Schema):
    """Base schema with common fields."""
    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        ordered = True
        unknown = 'exclude'


class PaginationSchema(Schema):
    """Schema for pagination parameters."""
    page = fields.Integer(
        missing=1,
        validate=validate.Range(min=1),
        error_messages={'invalid': 'Page must be a positive integer'}
    )
    per_page = fields.Integer(
        missing=20,
        validate=validate.Range(min=1, max=100),
        error_messages={'invalid': 'Items per page must be between 1 and 100'}
    )
    sort_by = fields.String(
        missing='created_at',
        validate=validate.Length(max=50)
    )
    sort_order = fields.String(
        missing='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )


# Authentication schemas
class LoginSchema(Schema):
    """Enhanced login schema."""
    email = SecureFields.email(required=True)
    password = fields.String(required=True, load_only=True)
    remember_me = fields.Boolean(missing=False)
    two_factor_code = fields.String(
        validate=validate.Regexp(r'^\d{6}$', error='Invalid 2FA code format')
    )


class RegisterSchema(Schema):
    """Enhanced registration schema."""
    email = SecureFields.email(required=True)
    password = SecureFields.password(required=True)
    confirm_password = fields.String(required=True, load_only=True)
    first_name = SecureFields.name(required=True, max_length=50)
    last_name = SecureFields.name(required=True, max_length=50)
    phone = SecureFields.phone(required=False)
    role = fields.String(
        missing='student',
        validate=validate.OneOf(['student', 'trainer', 'admin'])
    )
    terms_accepted = fields.Boolean(
        required=True,
        validate=validate.Equal(True, error='You must accept the terms and conditions')
    )
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', field_name='confirm_password')


class PasswordResetRequestSchema(Schema):
    """Password reset request schema."""
    email = SecureFields.email(required=True)


class PasswordResetSchema(Schema):
    """Password reset schema."""
    token = fields.String(required=True, validate=validate.Length(min=32))
    password = SecureFields.password(required=True)
    confirm_password = fields.String(required=True, load_only=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', field_name='confirm_password')


# User schemas
class UserProfileSchema(BaseSchema):
    """User profile schema."""
    email = SecureFields.email(dump_only=True)
    username = fields.String(
        validate=[
            validate.Length(min=3, max=30),
            validate.Regexp(
                r'^[a-zA-Z0-9_\-\.]+$',
                error='Username can only contain letters, numbers, underscore, hyphen, or dot'
            )
        ]
    )
    first_name = SecureFields.name(required=True, max_length=50)
    last_name = SecureFields.name(required=True, max_length=50)
    phone = SecureFields.phone()
    bio = SecureFields.safe_string(max_length=500, allow_special=True)
    avatar_url = SecureFields.url()
    timezone = fields.String(validate=validate.Length(max=50))
    language = fields.String(
        validate=validate.OneOf(['en', 'es', 'fr', 'ar', 'de', 'ru', 'tr'])
    )
    notification_preferences = fields.Dict()


class UserSettingsSchema(Schema):
    """User settings schema."""
    email_notifications = fields.Boolean()
    sms_notifications = fields.Boolean()
    push_notifications = fields.Boolean()
    newsletter_subscription = fields.Boolean()
    privacy_settings = fields.Dict()
    theme = fields.String(validate=validate.OneOf(['light', 'dark', 'auto']))
    language = fields.String(
        validate=validate.OneOf(['en', 'es', 'fr', 'ar', 'de', 'ru', 'tr'])
    )


# Beneficiary schemas
class BeneficiaryCreateSchema(Schema):
    """Beneficiary creation schema."""
    first_name = SecureFields.name(required=True, max_length=50)
    last_name = SecureFields.name(required=True, max_length=50)
    email = SecureFields.email(required=True)
    phone = SecureFields.phone(required=True)
    date_of_birth = fields.Date(required=True)
    gender = fields.String(
        validate=validate.OneOf(['male', 'female', 'other', 'prefer_not_to_say'])
    )
    address = SecureFields.safe_string(max_length=255, allow_special=True)
    city = SecureFields.name(max_length=100)
    state = SecureFields.name(max_length=100)
    postal_code = fields.String(validate=validate.Regexp(r'^[\w\s\-]+$'))
    country = SecureFields.name(max_length=100)
    emergency_contact_name = SecureFields.name(max_length=100)
    emergency_contact_phone = SecureFields.phone()
    emergency_contact_relationship = SecureFields.safe_string(max_length=50)
    medical_conditions = fields.String(validate=validate.Length(max=1000))
    medications = fields.String(validate=validate.Length(max=500))
    allergies = fields.String(validate=validate.Length(max=500))
    notes = fields.String(validate=validate.Length(max=2000))
    
    @validates('date_of_birth')
    def validate_age(self, value):
        age = (date.today() - value).days // 365
        if age < 16:
            raise ValidationError('Beneficiary must be at least 16 years old')
        if age > 100:
            raise ValidationError('Invalid date of birth')


class BeneficiaryUpdateSchema(BeneficiaryCreateSchema):
    """Beneficiary update schema (all fields optional)."""
    class Meta:
        fields = BeneficiaryCreateSchema.Meta.fields
        partial = True


# Program schemas
class ProgramCreateSchema(Schema):
    """Program creation schema."""
    name = SecureFields.safe_string(required=True, max_length=100)
    description = SecureFields.safe_string(max_length=1000, allow_special=True)
    category = fields.String(
        required=True,
        validate=validate.OneOf(['education', 'health', 'employment', 'social', 'other'])
    )
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    max_participants = SecureFields.positive_integer()
    min_age = fields.Integer(validate=validate.Range(min=0, max=100))
    max_age = fields.Integer(validate=validate.Range(min=0, max=100))
    location = SecureFields.safe_string(max_length=255)
    is_online = fields.Boolean(missing=False)
    sessions_per_week = fields.Integer(
        validate=validate.Range(min=1, max=7)
    )
    duration_per_session = fields.Integer(
        validate=validate.Range(min=15, max=480)
    )
    prerequisites = fields.List(fields.Integer())
    materials_needed = fields.String(validate=validate.Length(max=500))
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise ValidationError('End date must be after start date')
            
            duration_days = (data['end_date'] - data['start_date']).days
            if duration_days < 7:
                raise ValidationError('Program must be at least 7 days long')
            if duration_days > 365:
                raise ValidationError('Program cannot exceed 1 year')
    
    @validates_schema
    def validate_age_range(self, data, **kwargs):
        if data.get('min_age') and data.get('max_age'):
            if data['min_age'] > data['max_age']:
                raise ValidationError('Minimum age cannot be greater than maximum age')


# Appointment schemas
class AppointmentCreateSchema(Schema):
    """Appointment creation schema."""
    beneficiary_id = SecureFields.positive_integer(required=True)
    trainer_id = SecureFields.positive_integer(required=True)
    appointment_datetime = fields.DateTime(required=True)
    duration_minutes = fields.Integer(
        required=True,
        validate=validate.Range(min=15, max=240)
    )
    appointment_type = fields.String(
        required=True,
        validate=validate.OneOf(['consultation', 'assessment', 'training', 'follow_up'])
    )
    location = SecureFields.safe_string(max_length=255)
    is_virtual = fields.Boolean(missing=False)
    notes = SecureFields.safe_string(max_length=1000, allow_special=True)
    reminder_sent = fields.Boolean(missing=False)
    
    @validates('appointment_datetime')
    def validate_datetime(self, value):
        if value <= datetime.now():
            raise ValidationError('Appointment must be in the future')
        
        if value.hour < 8 or value.hour >= 18:
            raise ValidationError('Appointment must be during business hours (8 AM - 6 PM)')
        
        if value.weekday() >= 5:
            raise ValidationError('Appointments are only available on weekdays')
    
    @validates('duration_minutes')
    def validate_duration(self, value):
        if value % 15 != 0:
            raise ValidationError('Duration must be in 15-minute increments')


class AppointmentUpdateSchema(AppointmentCreateSchema):
    """Appointment update schema."""
    status = fields.String(
        validate=validate.OneOf(['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'])
    )
    cancellation_reason = SecureFields.safe_string(max_length=255)
    
    class Meta:
        partial = True


# Evaluation schemas
class EvaluationCreateSchema(Schema):
    """Evaluation creation schema."""
    name = SecureFields.safe_string(required=True, max_length=100)
    description = SecureFields.safe_string(max_length=500, allow_special=True)
    evaluation_type = fields.String(
        required=True,
        validate=validate.OneOf(['assessment', 'test', 'survey', 'feedback'])
    )
    program_id = SecureFields.positive_integer()
    beneficiary_id = SecureFields.positive_integer(required=True)
    evaluator_id = SecureFields.positive_integer(required=True)
    due_date = fields.DateTime()
    questions = fields.List(fields.Dict(), validate=validate.Length(min=1))
    total_points = fields.Integer(validate=validate.Range(min=0))
    passing_score = fields.Integer(validate=validate.Range(min=0))
    time_limit_minutes = fields.Integer(validate=validate.Range(min=1, max=480))
    
    @validates_schema
    def validate_scores(self, data, **kwargs):
        if data.get('passing_score') and data.get('total_points'):
            if data['passing_score'] > data['total_points']:
                raise ValidationError('Passing score cannot exceed total points')


class EvaluationSubmissionSchema(Schema):
    """Evaluation submission schema."""
    evaluation_id = SecureFields.positive_integer(required=True)
    answers = fields.Dict(required=True)
    time_taken_minutes = fields.Integer(
        validate=validate.Range(min=1, max=480)
    )
    submitted_at = fields.DateTime(dump_only=True)
    score = fields.Float(validate=validate.Range(min=0, max=100))
    feedback = SecureFields.safe_string(max_length=1000, allow_special=True)
    attachments = fields.List(fields.Dict())


# Document schemas
class DocumentUploadSchema(Schema):
    """Document upload schema."""
    title = SecureFields.safe_string(required=True, max_length=255)
    description = SecureFields.safe_string(max_length=500, allow_special=True)
    category = fields.String(
        validate=validate.OneOf(['report', 'certificate', 'assessment', 'other'])
    )
    tags = fields.List(
        SecureFields.safe_string(max_length=50),
        validate=validate.Length(max=10)
    )
    access_level = fields.String(
        missing='private',
        validate=validate.OneOf(['private', 'shared', 'public'])
    )
    allowed_users = fields.List(fields.Integer())


# Message schemas
class MessageSchema(Schema):
    """Message/Chat schema."""
    recipient_id = SecureFields.positive_integer(required=True)
    subject = SecureFields.safe_string(max_length=200)
    content = SecureFields.safe_string(required=True, max_length=5000, allow_special=True)
    parent_message_id = fields.Integer()
    attachments = fields.List(fields.Dict())
    is_urgent = fields.Boolean(missing=False)
    
    @validates('content')
    def validate_content(self, value):
        if len(value.strip()) < 1:
            raise ValidationError('Message content cannot be empty')


# Report schemas
class ReportGenerationSchema(Schema):
    """Report generation schema."""
    report_type = fields.String(
        required=True,
        validate=validate.OneOf(['progress', 'attendance', 'evaluation', 'custom'])
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    beneficiary_ids = fields.List(fields.Integer())
    program_ids = fields.List(fields.Integer())
    include_charts = fields.Boolean(missing=True)
    include_recommendations = fields.Boolean(missing=False)
    format = fields.String(
        missing='pdf',
        validate=validate.OneOf(['pdf', 'excel', 'csv'])
    )
    
    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data.get('date_to') and data.get('date_from'):
            if data['date_to'] < data['date_from']:
                raise ValidationError('End date must be after start date')
            
            # Limit report range to 1 year
            days_diff = (data['date_to'] - data['date_from']).days
            if days_diff > 365:
                raise ValidationError('Report range cannot exceed 1 year')


# Search schemas
class SearchSchema(Schema):
    """General search schema."""
    query = SecureFields.safe_string(
        required=True,
        max_length=200,
        error_messages={'required': 'Search query is required'}
    )
    search_type = fields.String(
        validate=validate.OneOf(['all', 'users', 'beneficiaries', 'programs', 'documents'])
    )
    filters = fields.Dict()
    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))
    
    @validates('query')
    def validate_query(self, value):
        if len(value.strip()) < 2:
            raise ValidationError('Search query must be at least 2 characters')


# File upload schema
class FileUploadSchema(Schema):
    """File upload validation schema."""
    file = fields.Field(required=True)
    title = SecureFields.safe_string(max_length=255)
    description = SecureFields.safe_string(max_length=500)
    category = fields.String(
        validate=validate.OneOf(['document', 'image', 'report', 'other'])
    )
    
    @validates('file')
    def validate_file(self, value):
        if not hasattr(value, 'filename'):
            raise ValidationError('Invalid file object')
        
        if not value.filename:
            raise ValidationError('File must have a filename')
        
        # Additional validation would be done by FileValidator