"""Beneficiary schemas."""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, pre_load
from app.models import Beneficiary


class BeneficiaryBaseSchema(Schema):
    """Base schema for Beneficiary model."""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    trainer_id = fields.Integer(allow_none=True)
    tenant_id = fields.Integer(required=True)
    
    # Personal information
    gender = fields.String(validate=validate.OneOf(['male', 'female', 'other']), allow_none=True)
    birth_date = fields.Date(allow_none=True)
    phone = fields.String(allow_none=True)
    address = fields.String(allow_none=True)
    city = fields.String(allow_none=True)
    postal_code = fields.String(allow_none=True)
    country = fields.String(allow_none=True)
    
    # Emergency contact information
    emergency_contact_name = fields.String(allow_none=True)
    emergency_contact_relationship = fields.String(allow_none=True)
    emergency_contact_phone = fields.String(allow_none=True)
    emergency_contact_email = fields.Email(allow_none=True)
    emergency_contact_address = fields.String(allow_none=True)
    
    # Professional information
    profession = fields.String(allow_none=True)
    company = fields.String(allow_none=True)
    company_size = fields.String(validate=validate.OneOf([
        'small', 'medium', 'large', 'enterprise'
    ]), allow_none=True)
    years_of_experience = fields.Integer(allow_none=True)
    education_level = fields.String(allow_none=True)
    
    # Status
    status = fields.String(validate=validate.OneOf(['active', 'inactive', 'archived']), 
                         dump_default='active')
    is_active = fields.Boolean(dump_default=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Computed fields
    first_name = fields.String(dump_only=True)
    last_name = fields.String(dump_only=True)
    evaluation_count = fields.Integer(dump_only=True)
    completed_evaluation_count = fields.Integer(dump_only=True)
    session_count = fields.Integer(dump_only=True)
    trainer_count = fields.Integer(dump_only=True)


class BeneficiarySchema(BeneficiaryBaseSchema):
    """Schema for Beneficiary model."""
    # Add relationships
    user = fields.Nested('UserSchema', only=('id', 'email', 'first_name', 'last_name'), dump_only=True)
    trainer = fields.Nested('UserSchema', only=('id', 'email', 'first_name', 'last_name'), dump_only=True)
    tenant = fields.Nested('TenantSchema', only=('id', 'name'), dump_only=True)


class BeneficiaryCreateSchema(Schema):
    """Schema for creating a beneficiary with user information."""
    # User information
    email = fields.Email(required=True)
    password = fields.String(required=False, load_only=True,
                           validate=validate.Length(min=8, error="Password must be at least 8 characters long"))
    confirm_password = fields.String(required=False, load_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    
    # Beneficiary information
    trainer_id = fields.Integer(allow_none=True)
    tenant_id = fields.Integer(required=False)
    gender = fields.String(validate=validate.OneOf(['male', 'female', 'other']), allow_none=True)
    birth_date = fields.Date(allow_none=True)
    phone = fields.String(allow_none=True)
    address = fields.String(allow_none=True)
    city = fields.String(allow_none=True)
    postal_code = fields.String(allow_none=True)
    zip_code = fields.String(allow_none=True)  # Alias for postal_code
    state = fields.String(allow_none=True)
    country = fields.String(allow_none=True)
    profession = fields.String(allow_none=True)
    occupation = fields.String(allow_none=True)  # Alias for profession
    company = fields.String(allow_none=True)
    organization = fields.String(allow_none=True)  # Alias for company
    company_size = fields.String(validate=validate.OneOf([
        'small', 'medium', 'large', 'enterprise'
    ]), allow_none=True)
    years_of_experience = fields.Integer(allow_none=True)
    education_level = fields.String(allow_none=True)
    nationality = fields.String(allow_none=True)
    native_language = fields.String(allow_none=True)
    category = fields.String(allow_none=True)
    status = fields.String(allow_none=True)
    bio = fields.String(allow_none=True)
    goals = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
    referral_source = fields.String(allow_none=True)
    custom_fields = fields.Dict(allow_none=True)
    
    # Emergency contact information
    emergency_contact_name = fields.String(allow_none=True)
    emergency_contact_relationship = fields.String(allow_none=True)
    emergency_contact_phone = fields.String(allow_none=True)
    emergency_contact_email = fields.Email(allow_none=True)
    emergency_contact_address = fields.String(allow_none=True)
    
    @validates('confirm_password')
    def validate_confirm_password(self, value):
        """Validate that passwords match if password is provided."""
        password = self.context.get('password')
        if password and value != password:
            raise ValidationError('Passwords do not match')
    
    @validates('email')
    def validate_email(self, value):
        """Validate that email is not already in use by a beneficiary."""
        from app.models import User, Beneficiary
        user = User.query.filter_by(email=value).first()
        if user:
            # Check if this user already has a beneficiary profile
            beneficiary = Beneficiary.query.filter_by(user_id=user.id).first()
            if beneficiary:
                raise ValidationError('This email is already associated with a beneficiary account')
    
    @pre_load
    def preprocess_data(self, data, **kwargs):
        """Preprocess the data before validation."""
        # Map frontend field names to backend field names
        field_mapping = {
            'zip_code': 'postal_code',
            'occupation': 'profession',
            'organization': 'company'
        }
        
        for frontend_field, backend_field in field_mapping.items():
            if frontend_field in data and backend_field not in data:
                data[backend_field] = data[frontend_field]
        
        # Convert empty strings to None for optional fields
        for key, value in data.items():
            if value == '':
                data[key] = None
                
        # Convert date formats if needed
        if 'birth_date' in data and data['birth_date']:
            # The frontend sends YYYY-MM-DD format which is correct for Date field
            pass
        
        return data


class BeneficiaryUpdateSchema(Schema):
    """Schema for updating a beneficiary."""
    trainer_id = fields.Integer(allow_none=True)
    
    # User information
    email = fields.Email(allow_none=True)
    first_name = fields.String(allow_none=True)
    last_name = fields.String(allow_none=True)
    
    # Personal information
    gender = fields.String(validate=validate.OneOf(['male', 'female', 'other']), allow_none=True)
    birth_date = fields.Date(allow_none=True)
    phone = fields.String(allow_none=True)
    address = fields.String(allow_none=True)
    city = fields.String(allow_none=True)
    postal_code = fields.String(allow_none=True)
    zip_code = fields.String(allow_none=True)  # Alias for postal_code  
    state = fields.String(allow_none=True)
    country = fields.String(allow_none=True)
    nationality = fields.String(allow_none=True)
    native_language = fields.String(allow_none=True)
    
    # Professional information
    profession = fields.String(allow_none=True)
    occupation = fields.String(allow_none=True)  # Alias for profession
    company = fields.String(allow_none=True)
    organization = fields.String(allow_none=True)  # Alias for company
    company_size = fields.String(validate=validate.OneOf([
        'small', 'medium', 'large', 'enterprise'
    ]), allow_none=True)
    years_of_experience = fields.Integer(allow_none=True)
    education_level = fields.String(allow_none=True)
    
    # Additional information
    category = fields.String(allow_none=True)
    bio = fields.String(allow_none=True)
    goals = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
    referral_source = fields.String(allow_none=True)
    custom_fields = fields.Dict(allow_none=True)
    
    # Emergency contact information
    emergency_contact_name = fields.String(allow_none=True)
    emergency_contact_relationship = fields.String(allow_none=True)
    emergency_contact_phone = fields.String(allow_none=True)
    emergency_contact_email = fields.Email(allow_none=True)
    emergency_contact_address = fields.String(allow_none=True)
    
    # Status
    status = fields.String(validate=validate.OneOf(['active', 'inactive', 'archived']))
    is_active = fields.Boolean()
    
    @validates('email')
    def validate_email(self, value):
        """Validate that email is not already in use by another user."""
        from app.models import User
        if value:
            # Check if this email is already in use by another user
            # We need to exclude the current user from the check
            from flask_jwt_extended import get_jwt_identity
            current_user_id = get_jwt_identity()
            user = User.query.filter_by(email=value).first()
            if user and user.id != current_user_id:
                raise ValidationError('This email is already in use')
    
    @pre_load
    def preprocess_data(self, data, **kwargs):
        """Preprocess the data before validation."""
        # Map frontend field names to backend field names
        field_mapping = {
            'zip_code': 'postal_code',
            'occupation': 'profession',
            'organization': 'company'
        }
        
        for frontend_field, backend_field in field_mapping.items():
            if frontend_field in data and backend_field not in data:
                data[backend_field] = data[frontend_field]
        
        # Convert empty strings to None for optional fields
        for key, value in data.items():
            if value == '':
                data[key] = None
                
        # Convert date formats if needed
        if 'birth_date' in data and data['birth_date']:
            # The frontend sends YYYY-MM-DD format which is correct for Date field
            pass
        
        return data


class NoteSchema(Schema):
    """Schema for Note model."""
    id = fields.Integer(dump_only=True)
    beneficiary_id = fields.Integer(required=True)
    user_id = fields.Integer(dump_only=True)
    content = fields.String(required=True)
    type = fields.String(validate=validate.OneOf(['general', 'private', 'assessment', 'follow_up']), 
                       dump_default='general')
    is_private = fields.Boolean(dump_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Add relationships
    user = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'), dump_only=True)


class NoteCreateSchema(Schema):
    """Schema for creating a note."""
    beneficiary_id = fields.Integer(required=True)
    content = fields.String(required=True)
    type = fields.String(validate=validate.OneOf(['general', 'private', 'assessment', 'follow_up']), 
                       dump_default='general')
    is_private = fields.Boolean(dump_default=False)


class NoteUpdateSchema(Schema):
    """Schema for updating a note."""
    content = fields.String()
    type = fields.String(validate=validate.OneOf(['general', 'private', 'assessment', 'follow_up']))
    is_private = fields.Boolean()


class AppointmentSchema(Schema):
    """Schema for Appointment model."""
    id = fields.Integer(dump_only=True)
    beneficiary_id = fields.Integer(required=True)
    user_id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    location = fields.String(dump_default='Online')
    status = fields.String(validate=validate.OneOf(['scheduled', 'completed', 'cancelled']), 
                         dump_default='scheduled')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Add relationships
    beneficiary = fields.Nested('BeneficiarySchema', only=('id', 'user'), dump_only=True)
    user = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'), dump_only=True)


class AppointmentCreateSchema(Schema):
    """Schema for creating an appointment."""
    beneficiary_id = fields.Integer(required=True)
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    location = fields.String(dump_default='Online')
    
    @validates('end_time')
    def validate_end_time(self, value):
        """Validate that end_time is after start_time."""
        if value <= self.start_time:
            raise ValidationError('End time must be after start time')


class AppointmentUpdateSchema(Schema):
    """Schema for updating an appointment."""
    title = fields.String()
    description = fields.String(allow_none=True)
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    location = fields.String()
    status = fields.String(validate=validate.OneOf(['scheduled', 'completed', 'cancelled']))
    
    @validates('end_time')
    def validate_end_time(self, value):
        """Validate that end_time is after start_time."""
        if 'start_time' in self.data and value <= self.data['start_time']:
            raise ValidationError('End time must be after start time')


class DocumentSchema(Schema):
    """Schema for Document model."""
    id = fields.Integer(dump_only=True)
    beneficiary_id = fields.Integer(required=True)
    user_id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    file_path = fields.String(dump_only=True)
    file_type = fields.String(dump_only=True)
    file_size = fields.Integer(dump_only=True)
    is_private = fields.Boolean(dump_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Add relationships
    beneficiary = fields.Nested('BeneficiarySchema', only=('id', 'user'), dump_only=True)
    user = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'), dump_only=True)


class DocumentCreateSchema(Schema):
    """Schema for creating a document."""
    beneficiary_id = fields.Integer(required=True)
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    is_private = fields.Boolean(dump_default=False)
    # file field is handled separately in the controller


class DocumentUpdateSchema(Schema):
    """Schema for updating a document."""
    title = fields.String()
    description = fields.String(allow_none=True)
    is_private = fields.Boolean()