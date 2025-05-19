"""Assessment schemas for validation."""

from marshmallow import Schema, fields, validate, ValidationError, validates_schema


class AssessmentQuestionSchema(Schema):
    """Schema for assessment question."""
    id = fields.Int(dump_only=True)
    section_id = fields.Int(required=True)
    question_text = fields.Str(required=True, validate=validate.Length(min=1))
    question_type = fields.Str(required=True, validate=validate.OneOf([
        'multiple_choice', 'multiple_select', 'true_false', 
        'short_answer', 'essay', 'code', 'file_upload'
    ]))
    points = fields.Int(validate=validate.Range(min=0))
    correct_answer = fields.Raw(allow_none=True)
    answer_options = fields.List(fields.Dict(), allow_none=True)
    order_index = fields.Int(default=0)
    is_required = fields.Bool(default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates_schema
    def validate_question(self, data, **kwargs):
        """Validate question based on type."""
        question_type = data.get('question_type')
        
        if question_type in ['multiple_choice', 'multiple_select']:
            if not data.get('answer_options'):
                raise ValidationError('Answer options are required for multiple choice questions')
            if len(data.get('answer_options', [])) < 2:
                raise ValidationError('At least 2 answer options are required')
        
        if question_type == 'true_false':
            if data.get('answer_options') and len(data.get('answer_options')) != 2:
                raise ValidationError('True/False questions must have exactly 2 options')


class AssessmentSectionSchema(Schema):
    """Schema for assessment section."""
    id = fields.Int(dump_only=True)
    template_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    order_index = fields.Int(default=0)
    points = fields.Int(default=0, validate=validate.Range(min=0))
    questions = fields.List(fields.Nested(AssessmentQuestionSchema))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class AssessmentTemplateSchema(Schema):
    """Schema for assessment template."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    category = fields.Str(required=True, validate=validate.OneOf([
        'technical', 'soft_skills', 'language', 'general', 'compliance', 'custom'
    ]))
    difficulty_level = fields.Str(validate=validate.OneOf(['easy', 'medium', 'hard']))
    time_limit = fields.Int(validate=validate.Range(min=1, max=360))  # in minutes
    total_points = fields.Int(validate=validate.Range(min=0))
    passing_score = fields.Int(validate=validate.Range(min=0, max=100))
    instructions = fields.Str()
    is_active = fields.Bool(default=True)
    tenant_id = fields.Int(dump_only=True)
    created_by = fields.Int(dump_only=True)
    sections = fields.List(fields.Nested(AssessmentSectionSchema))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested relationships
    creator = fields.Nested('UserSchema', only=['id', 'first_name', 'last_name'], dump_only=True)
    
    @validates_schema
    def validate_scoring(self, data, **kwargs):
        """Validate scoring settings."""
        if data.get('passing_score') and data.get('total_points'):
            if data['passing_score'] > data['total_points']:
                raise ValidationError('Passing score cannot be greater than total points')


class AssessmentTemplateCreateSchema(Schema):
    """Schema for creating assessment template."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    category = fields.Str(required=True, validate=validate.OneOf([
        'technical', 'soft_skills', 'language', 'general', 'compliance', 'custom'
    ]))
    difficulty_level = fields.Str(validate=validate.OneOf(['easy', 'medium', 'hard']))
    time_limit = fields.Int(validate=validate.Range(min=1, max=360))
    total_points = fields.Int(validate=validate.Range(min=0))
    passing_score = fields.Int(validate=validate.Range(min=0, max=100))
    instructions = fields.Str()
    is_active = fields.Bool(default=True)
    sections = fields.List(fields.Nested(AssessmentSectionSchema), required=True)


class AssessmentTemplateUpdateSchema(Schema):
    """Schema for updating assessment template."""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    category = fields.Str(validate=validate.OneOf([
        'technical', 'soft_skills', 'language', 'general', 'compliance', 'custom'
    ]))
    difficulty_level = fields.Str(validate=validate.OneOf(['easy', 'medium', 'hard']))
    time_limit = fields.Int(validate=validate.Range(min=1, max=360))
    total_points = fields.Int(validate=validate.Range(min=0))
    passing_score = fields.Int(validate=validate.Range(min=0, max=100))
    instructions = fields.Str()
    is_active = fields.Bool()
    sections = fields.List(fields.Nested(AssessmentSectionSchema))


class AssessmentResponseSchema(Schema):
    """Schema for assessment response."""
    id = fields.Int(dump_only=True)
    assessment_id = fields.Int(required=True)
    question_id = fields.Int(required=True)
    answer = fields.Raw()
    is_correct = fields.Bool()
    points_earned = fields.Float(validate=validate.Range(min=0))
    feedback = fields.Str()
    time_spent = fields.Int(validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested relationships
    question = fields.Nested(AssessmentQuestionSchema, dump_only=True)


class AssessmentSchema(Schema):
    """Schema for assessment instance."""
    id = fields.Int(dump_only=True)
    template_id = fields.Int(required=True)
    beneficiary_id = fields.Int(required=True)
    assigned_by = fields.Int(dump_only=True)
    status = fields.Str(validate=validate.OneOf([
        'assigned', 'in_progress', 'completed', 'graded'
    ]))
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    submit_time = fields.DateTime()
    score = fields.Float(validate=validate.Range(min=0))
    passed = fields.Bool()
    feedback = fields.Str()
    graded_by = fields.Int()
    graded_at = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested relationships
    template = fields.Nested(AssessmentTemplateSchema, dump_only=True)
    beneficiary = fields.Nested('BeneficiarySchema', only=['id', 'first_name', 'last_name'], dump_only=True)
    assigner = fields.Nested('UserSchema', only=['id', 'first_name', 'last_name'], dump_only=True)
    grader = fields.Nested('UserSchema', only=['id', 'first_name', 'last_name'], dump_only=True)
    responses = fields.List(fields.Nested(AssessmentResponseSchema), dump_only=True)


class AssessmentCreateSchema(Schema):
    """Schema for creating assessment."""
    template_id = fields.Int(required=True)
    beneficiary_id = fields.Int(required=True)
    scheduled_date = fields.DateTime()
    notes = fields.Str()


class AssessmentUpdateSchema(Schema):
    """Schema for updating assessment."""
    status = fields.Str(validate=validate.OneOf([
        'assigned', 'in_progress', 'completed', 'graded'
    ]))
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    submit_time = fields.DateTime()
    score = fields.Float(validate=validate.Range(min=0))
    passed = fields.Bool()
    feedback = fields.Str()


class AssessmentGradeSchema(Schema):
    """Schema for grading assessment."""
    score = fields.Float(required=True, validate=validate.Range(min=0))
    passed = fields.Bool(required=True)
    feedback = fields.Str()
    question_feedbacks = fields.Dict(
        keys=fields.Int(),  # question_id
        values=fields.Dict(
            score=fields.Float(required=True),
            feedback=fields.Str()
        )
    )