"""Evaluation and test schemas."""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, pre_load
from app.models import Evaluation, Question


class QuestionSchema(Schema):
    """Schema for Question model."""
    id = fields.Integer(dump_only=True)
    evaluation_id = fields.Integer(required=True)
    text = fields.String(required=True)
    type = fields.String(required=True, validate=validate.OneOf([
        'multiple_choice', 'text', 'true_false', 'matching', 'ordering'
    ]))
    options = fields.Dict(allow_none=True)
    correct_answer = fields.Raw(allow_none=True)
    explanation = fields.String(allow_none=True)
    category = fields.String(allow_none=True)
    difficulty = fields.String(validate=validate.OneOf(['easy', 'medium', 'hard']), 
                             dump_default='medium')
    points = fields.Float(dump_default=1.0)
    order = fields.Integer(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class QuestionCreateSchema(Schema):
    """Schema for creating a question."""
    text = fields.String(required=True)
    type = fields.String(required=True, validate=validate.OneOf([
        'multiple_choice', 'text', 'true_false', 'matching', 'ordering'
    ]))
    options = fields.Dict(allow_none=True)
    correct_answer = fields.Raw(allow_none=True)
    explanation = fields.String(allow_none=True)
    category = fields.String(allow_none=True)
    difficulty = fields.String(validate=validate.OneOf(['easy', 'medium', 'hard']), 
                             dump_default='medium')
    points = fields.Float(dump_default=1.0)
    order = fields.Integer(allow_none=True)


class QuestionUpdateSchema(Schema):
    """Schema for updating a question."""
    text = fields.String()
    type = fields.String(validate=validate.OneOf([
        'multiple_choice', 'text', 'true_false', 'matching', 'ordering'
    ]))
    options = fields.Dict(allow_none=True)
    correct_answer = fields.Raw(allow_none=True)
    explanation = fields.String(allow_none=True)
    category = fields.String(allow_none=True)
    difficulty = fields.String(validate=validate.OneOf(['easy', 'medium', 'hard']))
    points = fields.Float()
    order = fields.Integer(allow_none=True)


class EvaluationSchema(Schema):
    """Schema for Evaluation model."""
    id = fields.Integer(dump_only=True)
    tenant_id = fields.Integer(required=True)
    creator_id = fields.Integer(dump_only=True)
    beneficiary_id = fields.Integer(allow_none=True)
    
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    instructions = fields.String(allow_none=True)
    
    type = fields.String(validate=validate.OneOf([
        'assessment', 'quiz', 'survey', 'test'
    ]), dump_default='assessment')
    category = fields.String(allow_none=True)
    
    time_limit = fields.Integer(allow_none=True)
    passing_score = fields.Float(allow_none=True)
    is_randomized = fields.Boolean(dump_default=False)
    allow_resume = fields.Boolean(dump_default=True)
    max_attempts = fields.Integer(dump_default=1)
    show_results = fields.Boolean(dump_default=True)
    
    status = fields.String(validate=validate.OneOf([
        'draft', 'active', 'archived'
    ]), dump_default='draft')
    is_template = fields.Boolean(dump_default=False)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Relationships
    creator = fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'), dump_only=True)
    tenant = fields.Nested('TenantSchema', only=('id', 'name'), dump_only=True)
    questions = fields.Nested(QuestionSchema, many=True, dump_only=True)


class EvaluationCreateSchema(Schema):
    """Schema for creating an evaluation."""
    tenant_id = fields.Integer(required=True)
    beneficiary_id = fields.Integer(allow_none=True)
    
    title = fields.String(required=True)
    description = fields.String(allow_none=True)
    instructions = fields.String(allow_none=True)
    
    type = fields.String(validate=validate.OneOf([
        'assessment', 'quiz', 'survey', 'test'
    ]), dump_default='assessment')
    category = fields.String(allow_none=True)
    
    time_limit = fields.Integer(allow_none=True)
    passing_score = fields.Float(allow_none=True)
    is_randomized = fields.Boolean(dump_default=False)
    allow_resume = fields.Boolean(dump_default=True)
    max_attempts = fields.Integer(dump_default=1)
    show_results = fields.Boolean(dump_default=True)
    
    status = fields.String(validate=validate.OneOf([
        'draft', 'active', 'archived'
    ]), dump_default='draft')
    is_template = fields.Boolean(dump_default=False)
    
    questions = fields.Nested(QuestionCreateSchema, many=True, required=False)


class EvaluationUpdateSchema(Schema):
    """Schema for updating an evaluation."""
    tenant_id = fields.Integer()
    beneficiary_id = fields.Integer(allow_none=True)
    
    title = fields.String()
    description = fields.String(allow_none=True)
    instructions = fields.String(allow_none=True)
    
    type = fields.String(validate=validate.OneOf([
        'assessment', 'quiz', 'survey', 'test'
    ]))
    category = fields.String(allow_none=True)
    
    time_limit = fields.Integer(allow_none=True)
    passing_score = fields.Float(allow_none=True)
    is_randomized = fields.Boolean()
    allow_resume = fields.Boolean()
    max_attempts = fields.Integer()
    show_results = fields.Boolean()
    
    status = fields.String(validate=validate.OneOf([
        'draft', 'active', 'archived'
    ]))
    is_template = fields.Boolean()


class TestSessionSchema(Schema):
    """Schema for TestSession model."""
    id = fields.Integer(dump_only=True)
    evaluation_id = fields.Integer(required=True)
    beneficiary_id = fields.Integer(required=True)
    
    start_time = fields.DateTime(dump_only=True)
    end_time = fields.DateTime(dump_only=True)
    time_spent = fields.Integer(dump_only=True)
    current_question = fields.Integer(dump_only=True)
    status = fields.String(validate=validate.OneOf([
        'in_progress', 'completed', 'abandoned'
    ]), dump_only=True)
    
    score = fields.Float(dump_only=True)
    max_score = fields.Float(dump_only=True)
    passed = fields.Boolean(dump_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Relationships
    evaluation = fields.Nested(EvaluationSchema, only=(
        'id', 'title', 'type', 'time_limit', 'passing_score'
    ), dump_only=True)
    beneficiary = fields.Nested('BeneficiarySchema', only=(
        'id', 'user_id', 'user'
    ), dump_only=True)
    responses = fields.Nested('ResponseSchema', many=True, dump_only=True)


class TestSessionCreateSchema(Schema):
    """Schema for creating a test session."""
    evaluation_id = fields.Integer(required=True)
    beneficiary_id = fields.Integer(required=True)


class ResponseSchema(Schema):
    """Schema for Response model."""
    id = fields.Integer(dump_only=True)
    session_id = fields.Integer(required=True)
    question_id = fields.Integer(required=True)
    
    answer = fields.Raw(allow_none=True)
    is_correct = fields.Boolean(dump_only=True)
    score = fields.Float(dump_only=True)
    
    start_time = fields.DateTime(dump_only=True)
    end_time = fields.DateTime(dump_only=True)
    time_spent = fields.Integer(dump_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Relationships
    question = fields.Nested(QuestionSchema, only=(
        'id', 'text', 'type', 'options', 'explanation', 'points'
    ), dump_only=True)


class ResponseCreateSchema(Schema):
    """Schema for creating a response."""
    session_id = fields.Integer(required=True)
    question_id = fields.Integer(required=True)
    answer = fields.Raw(allow_none=True)
    time_spent = fields.Integer(allow_none=True)


class AIFeedbackSchema(Schema):
    """Schema for AIFeedback model."""
    id = fields.Integer(dump_only=True)
    session_id = fields.Integer(required=True)
    
    summary = fields.String(allow_none=True)
    strengths = fields.List(fields.String(), allow_none=True)
    areas_to_improve = fields.List(fields.String(), allow_none=True)
    recommendations = fields.List(fields.String(), allow_none=True)
    next_steps = fields.List(fields.String(), allow_none=True)
    
    status = fields.String(validate=validate.OneOf([
        'draft', 'approved', 'rejected'
    ]), dump_default='draft')
    approved_by = fields.Integer(allow_none=True, dump_only=True)
    rejected_reason = fields.String(allow_none=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Relationships
    session = fields.Nested(TestSessionSchema, only=(
        'id', 'evaluation_id', 'beneficiary_id', 'score', 'passed'
    ), dump_only=True)
    approver = fields.Nested('UserSchema', only=(
        'id', 'first_name', 'last_name'
    ), dump_only=True)


class AIFeedbackUpdateSchema(Schema):
    """Schema for updating an AI feedback."""
    summary = fields.String(allow_none=True)
    strengths = fields.List(fields.String(), allow_none=True)
    areas_to_improve = fields.List(fields.String(), allow_none=True)
    recommendations = fields.List(fields.String(), allow_none=True)
    next_steps = fields.List(fields.String(), allow_none=True)
    
    status = fields.String(validate=validate.OneOf([
        'draft', 'approved', 'rejected'
    ]))
    rejected_reason = fields.String(allow_none=True)