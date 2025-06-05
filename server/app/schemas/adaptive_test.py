"""Schemas for Adaptive Test System."""

from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow.decorators import post_dump


class AdaptiveTestPoolSchema(Schema):
    """Schema for adaptive test pool."""
    id = fields.Int(dump_only=True)
    tenant_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    subject = fields.Str(allow_none=True, validate=validate.Length(max=100))
    grade_level = fields.Str(allow_none=True, validate=validate.Length(max=50))
    total_questions = fields.Int(dump_only=True)
    is_active = fields.Bool(default=True)
    created_at = fields.DateTime(dump_only=True, format='iso')
    updated_at = fields.DateTime(dump_only=True, format='iso')
    
    # Nested fields
    questions = fields.Nested('AdaptiveQuestionSchema', many=True, dump_only=True)
    statistics = fields.Method('get_statistics', dump_only=True)
    
    def get_statistics(self, obj):
        """Get pool statistics."""
        if hasattr(obj, 'questions'):
            questions = obj.questions
            if questions:
                return {
                    'total_questions': len(questions),
                    'active_questions': sum(1 for q in questions if q.is_active),
                    'average_difficulty': sum(q.difficulty for q in questions) / len(questions),
                    'topics': list(set(q.topic for q in questions if q.topic))
                }
        return None


class IRTParametersSchema(Schema):
    """Schema for IRT parameters."""
    difficulty = fields.Float(
        required=True, 
        validate=validate.Range(min=-3, max=3),
        metadata={'description': 'Difficulty parameter (b) in IRT model'}
    )
    discrimination = fields.Float(
        default=1.0, 
        validate=validate.Range(min=0.1, max=2.5),
        metadata={'description': 'Discrimination parameter (a) in IRT model'}
    )
    guessing = fields.Float(
        default=0.0, 
        validate=validate.Range(min=0, max=0.3),
        metadata={'description': 'Guessing parameter (c) in IRT model'}
    )
    
    @validates('guessing')
    def validate_guessing(self, value):
        """Validate guessing parameter based on question type."""
        # Could add logic to enforce higher guessing for multiple choice
        if value > 0.25:  # For most questions, guessing should be < 0.25
            raise ValidationError("Guessing parameter too high for reliable assessment")


class AdaptiveQuestionSchema(Schema):
    """Schema for adaptive question."""
    id = fields.Int(dump_only=True)
    pool_id = fields.Int(required=True)
    
    # Question content
    text = fields.Str(required=True, validate=validate.Length(min=5))
    type = fields.Str(
        required=True, 
        validate=validate.OneOf([
            'multiple_choice', 'true_false', 'matching', 'ordering', 'text'
        ])
    )
    options = fields.Dict(allow_none=True)
    correct_answer = fields.Raw(allow_none=True)
    explanation = fields.Str(allow_none=True)
    
    # IRT parameters (nested)
    irt_parameters = fields.Nested(IRTParametersSchema, required=True)
    
    # Legacy flat fields for backward compatibility
    difficulty = fields.Float(dump_only=True)
    discrimination = fields.Float(dump_only=True)
    guessing = fields.Float(dump_only=True)
    
    # Categorization
    difficulty_level = fields.Int(
        required=True, 
        validate=validate.Range(min=1, max=10),
        metadata={'description': 'Difficulty level on 1-10 scale'}
    )
    topic = fields.Str(allow_none=True, validate=validate.Length(max=100))
    subtopic = fields.Str(allow_none=True, validate=validate.Length(max=100))
    cognitive_level = fields.Str(
        allow_none=True,
        validate=validate.OneOf([
            'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'
        ])
    )
    
    # Statistics
    usage_count = fields.Int(dump_only=True)
    correct_count = fields.Int(dump_only=True)
    average_response_time = fields.Float(dump_only=True)
    exposure_rate = fields.Float(dump_only=True)
    information_value = fields.Float(dump_only=True)
    
    # Status
    is_active = fields.Bool(default=True)
    review_status = fields.Str(
        default='approved',
        validate=validate.OneOf(['draft', 'approved', 'needs_review'])
    )
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True, format='iso')
    updated_at = fields.DateTime(dump_only=True, format='iso')
    
    # Computed fields
    success_rate = fields.Method('get_success_rate', dump_only=True)
    
    @post_dump
    def flatten_irt_parameters(self, data, **kwargs):
        """Flatten IRT parameters for backward compatibility."""
        if 'irt_parameters' in data and data['irt_parameters']:
            data['difficulty'] = data['irt_parameters']['difficulty']
            data['discrimination'] = data['irt_parameters']['discrimination']
            data['guessing'] = data['irt_parameters']['guessing']
        return data
    
    def get_success_rate(self, obj):
        """Calculate success rate."""
        if obj.usage_count > 0:
            return round(obj.correct_count / obj.usage_count * 100, 2)
        return None


class AdaptiveSessionConfigSchema(Schema):
    """Schema for adaptive session configuration."""
    max_questions = fields.Int(
        default=20,
        validate=validate.Range(min=5, max=100),
        metadata={'description': 'Maximum number of questions'}
    )
    max_time = fields.Int(
        allow_none=True,
        validate=validate.Range(min=5, max=180),
        metadata={'description': 'Maximum time in minutes'}
    )
    standard_error_threshold = fields.Float(
        default=0.3,
        validate=validate.Range(min=0.1, max=1.0),
        metadata={'description': 'SE threshold for stopping'}
    )
    initial_ability = fields.Float(
        default=0.0,
        validate=validate.Range(min=-3, max=3),
        metadata={'description': 'Starting ability estimate'}
    )
    selection_method = fields.Str(
        default='maximum_information',
        validate=validate.OneOf([
            'maximum_information', 'closest_difficulty', 'random'
        ])
    )
    topic_balancing = fields.Bool(
        default=True,
        metadata={'description': 'Enable topic coverage balancing'}
    )
    exposure_control = fields.Bool(
        default=True,
        metadata={'description': 'Enable question exposure control'}
    )
    test_id = fields.Int(
        allow_none=True,
        metadata={'description': 'Link to regular test/evaluation'}
    )


class AdaptiveTestSessionSchema(Schema):
    """Schema for adaptive test session."""
    id = fields.Int(dump_only=True)
    pool_id = fields.Int(required=True)
    beneficiary_id = fields.Int(required=True)
    test_id = fields.Int(allow_none=True)
    
    # Configuration
    config = fields.Nested(AdaptiveSessionConfigSchema, dump_only=True)
    
    # Progress
    questions_answered = fields.Int(dump_only=True)
    current_ability = fields.Float(dump_only=True)
    ability_se = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    
    # Results
    final_ability = fields.Float(dump_only=True)
    final_se = fields.Float(dump_only=True)
    confidence_interval = fields.Method('get_confidence_interval', dump_only=True)
    
    # Timing
    start_time = fields.DateTime(dump_only=True, format='iso')
    end_time = fields.DateTime(dump_only=True, format='iso')
    total_time_seconds = fields.Int(dump_only=True)
    
    # Metadata
    ability_history = fields.List(fields.Float(), dump_only=True)
    topic_coverage = fields.Dict(dump_only=True)
    
    def get_confidence_interval(self, obj):
        """Get confidence interval."""
        if obj.confidence_interval_lower and obj.confidence_interval_upper:
            return {
                'lower': obj.confidence_interval_lower,
                'upper': obj.confidence_interval_upper,
                'level': '95%'
            }
        return None


class SubmitResponseSchema(Schema):
    """Schema for submitting response."""
    question_id = fields.Int(required=True)
    answer = fields.Raw(required=True)
    response_time = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0),
        metadata={'description': 'Response time in seconds'}
    )


class AdaptiveResponseSchema(Schema):
    """Schema for adaptive response."""
    id = fields.Int(dump_only=True)
    session_id = fields.Int(dump_only=True)
    question_id = fields.Int(dump_only=True)
    
    # Response data
    answer = fields.Raw(dump_only=True)
    is_correct = fields.Bool(dump_only=True)
    response_time = fields.Float(dump_only=True)
    
    # Ability tracking
    ability_before = fields.Float(dump_only=True)
    ability_after = fields.Float(dump_only=True)
    se_after = fields.Float(dump_only=True)
    ability_change = fields.Method('get_ability_change', dump_only=True)
    
    # Question info
    question_difficulty = fields.Float(dump_only=True)
    question_number = fields.Int(dump_only=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True, format='iso')
    answered_at = fields.DateTime(dump_only=True, format='iso')
    
    def get_ability_change(self, obj):
        """Calculate ability change."""
        return round(obj.ability_after - obj.ability_before, 3)


class TopicScoreSchema(Schema):
    """Schema for topic performance score."""
    topic = fields.Str(required=True)
    score = fields.Float(required=True)
    total_questions = fields.Int(required=True)
    correct_answers = fields.Int(required=True)
    average_difficulty = fields.Float(required=True)
    performance_level = fields.Method('get_performance_level')
    
    def get_performance_level(self, obj):
        """Determine performance level for topic."""
        score = obj.get('score', 0)
        if score >= 90:
            return 'Excellent'
        elif score >= 80:
            return 'Good'
        elif score >= 70:
            return 'Satisfactory'
        elif score >= 60:
            return 'Needs Improvement'
        else:
            return 'Requires Focus'


class AdaptiveTestReportSchema(Schema):
    """Schema for adaptive test report."""
    id = fields.Int(dump_only=True)
    session_id = fields.Int(dump_only=True)
    
    # Overall performance
    final_ability = fields.Float(dump_only=True)
    ability_percentile = fields.Float(dump_only=True)
    performance_level = fields.Str(dump_only=True)
    
    # Topic analysis
    topic_strengths = fields.List(fields.Str(), dump_only=True)
    topic_weaknesses = fields.List(fields.Str(), dump_only=True)
    topic_scores = fields.Dict(dump_only=True)
    
    # Insights
    learning_profile = fields.Dict(dump_only=True)
    response_patterns = fields.Dict(dump_only=True)
    
    # Recommendations
    recommended_topics = fields.List(fields.Str(), dump_only=True)
    recommended_difficulty = fields.Float(dump_only=True)
    next_steps = fields.List(fields.Str(), dump_only=True)
    
    # Statistics
    total_questions = fields.Int(dump_only=True)
    correct_answers = fields.Int(dump_only=True)
    accuracy_rate = fields.Method('get_accuracy_rate', dump_only=True)
    average_difficulty = fields.Float(dump_only=True)
    response_consistency = fields.Float(dump_only=True)
    
    # Timestamp
    generated_at = fields.DateTime(dump_only=True, format='iso')
    
    # Formatted report sections
    summary = fields.Method('get_summary', dump_only=True)
    
    def get_accuracy_rate(self, obj):
        """Calculate accuracy rate."""
        if obj.total_questions > 0:
            return round(obj.correct_answers / obj.total_questions * 100, 2)
        return 0
    
    def get_summary(self, obj):
        """Generate summary text."""
        return {
            'performance': f"Achieved {obj.performance_level} level with {obj.ability_percentile}th percentile",
            'strengths': f"Strong in: {', '.join(obj.topic_strengths[:3])}" if obj.topic_strengths else "Building foundational skills",
            'focus_areas': f"Focus on: {', '.join(obj.topic_weaknesses[:3])}" if obj.topic_weaknesses else "Maintain current progress",
            'accuracy': f"{self.get_accuracy_rate(obj)}% accuracy across {obj.total_questions} questions"
        }


class QuestionStatisticsSchema(Schema):
    """Schema for question statistics."""
    question_id = fields.Int(required=True)
    usage_count = fields.Int(required=True)
    correct_rate = fields.Float(required=True)
    average_response_time = fields.Float(required=True)
    exposure_rate = fields.Float(required=True)
    discrimination_index = fields.Float(required=True)
    
    # IRT parameters
    irt_parameters = fields.Nested(IRTParametersSchema, required=True)
    
    # Information curve
    information_curve = fields.List(
        fields.Dict(keys=fields.Str(), values=fields.Float()),
        required=True
    )
    
    # Performance by ability level
    performance_by_ability = fields.Method('get_performance_by_ability', dump_only=True)
    
    def get_performance_by_ability(self, obj):
        """Analyze performance across ability levels."""
        # This would be calculated from actual response data
        return {
            'low_ability': {'range': [-3, -1], 'success_rate': 0.2},
            'medium_ability': {'range': [-1, 1], 'success_rate': 0.5},
            'high_ability': {'range': [1, 3], 'success_rate': 0.8}
        }


class CalibrationResultSchema(Schema):
    """Schema for IRT calibration results."""
    difficulty = fields.Float(required=True)
    discrimination = fields.Float(required=True)
    guessing = fields.Float(required=True)
    status = fields.Str(required=True)
    sample_size = fields.Int()
    fit_statistics = fields.Dict()
    recommendations = fields.List(fields.Str())