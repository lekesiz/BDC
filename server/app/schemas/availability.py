"""Availability schemas for validation."""

from marshmallow import Schema, fields, validate, ValidationError


class AvailabilitySchema(Schema):
    """Schema for availability."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    date = fields.Date(required=True)
    time_slot = fields.Str(required=True, validate=validate.Regexp(
        r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    ))  # Format: HH:MM-HH:MM
    is_available = fields.Bool(default=True)
    is_recurring = fields.Bool(default=False)
    recurrence_pattern = fields.Str(
        validate=validate.OneOf(['daily', 'weekly', 'monthly']),
        allow_none=True
    )
    recurrence_end_date = fields.Date(allow_none=True)
    notes = fields.Str(validate=validate.Length(max=500), allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested objects
    user = fields.Nested('UserSchema', only=['id', 'first_name', 'last_name', 'email'], dump_only=True)


class AvailabilityCreateSchema(Schema):
    """Schema for creating availability."""
    date = fields.Date(required=True)
    time_slot = fields.Str(required=True, validate=validate.Regexp(
        r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    ))
    is_available = fields.Bool(default=True)
    is_recurring = fields.Bool(default=False)
    recurrence_pattern = fields.Str(
        validate=validate.OneOf(['daily', 'weekly', 'monthly']),
        allow_none=True
    )
    recurrence_end_date = fields.Date(allow_none=True)
    notes = fields.Str(validate=validate.Length(max=500), allow_none=True)
    
    def validate_recurrence(self, data):
        """Validate recurrence settings."""
        if data.get('is_recurring'):
            if not data.get('recurrence_pattern'):
                raise ValidationError('Recurrence pattern is required when is_recurring is True')
            if not data.get('recurrence_end_date'):
                raise ValidationError('Recurrence end date is required when is_recurring is True')
        return data


class AvailabilityUpdateSchema(Schema):
    """Schema for updating availability."""
    date = fields.Date()
    time_slot = fields.Str(validate=validate.Regexp(
        r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    ))
    is_available = fields.Bool()
    is_recurring = fields.Bool()
    recurrence_pattern = fields.Str(
        validate=validate.OneOf(['daily', 'weekly', 'monthly']),
        allow_none=True
    )
    recurrence_end_date = fields.Date(allow_none=True)
    notes = fields.Str(validate=validate.Length(max=500), allow_none=True)


class BulkAvailabilityCreateSchema(Schema):
    """Schema for creating multiple availability slots."""
    slots = fields.List(fields.Nested(AvailabilityCreateSchema), required=True, validate=validate.Length(min=1, max=100))


class AvailabilityCheckSchema(Schema):
    """Schema for checking availability."""
    user_id = fields.Int()
    date = fields.Date(required=True)
    time_slot = fields.Str(required=True, validate=validate.Regexp(
        r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]-([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    ))