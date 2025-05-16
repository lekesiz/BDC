"""Document schemas."""

from marshmallow import Schema, fields, validate


class DocumentSchema(Schema):
    """Schema for Document model."""
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String()
    file_path = fields.String(dump_only=True)
    file_type = fields.String(dump_only=True)
    file_size = fields.Integer(dump_only=True)
    document_type = fields.String(validate=validate.OneOf(['general', 'report', 'certificate', 'assessment', 'other']))
    is_active = fields.Boolean()
    upload_by = fields.Integer(dump_only=True)
    uploader_name = fields.String(dump_only=True)
    beneficiary_id = fields.Integer()
    evaluation_id = fields.Integer()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class DocumentCreateSchema(Schema):
    """Schema for creating a document."""
    title = fields.String(required=True)
    description = fields.String()
    document_type = fields.String(validate=validate.OneOf(['general', 'report', 'certificate', 'assessment', 'other']))
    beneficiary_id = fields.Integer()
    evaluation_id = fields.Integer()
    # Note: file handling is done separately with request.files


class DocumentUpdateSchema(Schema):
    """Schema for updating a document."""
    title = fields.String()
    description = fields.String()
    document_type = fields.String(validate=validate.OneOf(['general', 'report', 'certificate', 'assessment', 'other']))
    is_active = fields.Boolean()
    beneficiary_id = fields.Integer()
    evaluation_id = fields.Integer()


class DocumentFilterSchema(Schema):
    """Schema for filtering documents."""
    document_type = fields.String()
    beneficiary_id = fields.Integer()
    evaluation_id = fields.Integer()
    upload_by = fields.Integer()
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    search = fields.String()