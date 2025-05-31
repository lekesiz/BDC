"""Appointment schemas."""
from marshmallow import Schema, fields, validate


class AppointmentSchema(Schema):
    """Schema for appointment."""
    id = fields.Int(dump_only=True)
    beneficiary_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(missing='')
    scheduled_date = fields.Date(required=True)
    scheduled_time = fields.Time(required=True)
    duration_minutes = fields.Int(missing=30, validate=validate.Range(min=15, max=480))
    location = fields.Str(missing='')
    status = fields.Str(missing='scheduled', validate=validate.OneOf(['scheduled', 'confirmed', 'completed', 'cancelled']))
    notes = fields.Str(missing='')
    created_by_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)