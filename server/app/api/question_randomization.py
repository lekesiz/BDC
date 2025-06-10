"""
Question Randomization API endpoints.

Provides endpoints for configuring and managing question randomization.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, current_user
from marshmallow import ValidationError, Schema, fields

from app.extensions import db
from app.models import TestSet, Question, TestSession, Beneficiary
from app.services.question_randomization_service import (
    question_randomization_service,
    RandomizationStrategy,
    QuestionOrderTemplate
)
from app.middleware.request_context import role_required
from app.utils import cache_response
from app.utils.logger import get_logger

from app.utils.logging import logger

logger = get_logger(__name__)

randomization_bp = Blueprint('randomization', __name__)


class RandomizationConfigSchema(Schema):
    """Schema for randomization configuration."""
    
    strategy = fields.Str(required=True, validate=fields.validate.OneOf([
        'simple_random', 'stratified', 'deterministic', 'adaptive', 'template_based', 'balanced'
    ]))
    template = fields.Str(allow_none=True, validate=fields.validate.OneOf([
        'easy_to_hard', 'hard_to_easy', 'mixed_difficulty', 'topic_grouped', 
        'alternating_difficulty', 'cognitive_progression'
    ]))
    anchor_positions = fields.Dict(keys=fields.Str(), values=fields.Int(), load_default=dict)
    time_based_seed = fields.Bool(load_default=False)
    time_window = fields.Str(validate=fields.validate.OneOf(['daily', 'weekly', 'monthly', 'hourly']), load_default='daily')
    strata_key = fields.Str(validate=fields.validate.OneOf(['difficulty', 'topic', 'both']), load_default='difficulty')
    randomness_factor = fields.Float(validate=fields.validate.Range(min=0.0, max=1.0), load_default=0.2)
    blocking_rules = fields.List(fields.Dict(), load_default=list)
    enable_answer_randomization = fields.Bool(load_default=True)
    preserve_answer_positions = fields.List(fields.Int(), load_default=list)
    prevent_repetition = fields.Bool(load_default=True)
    lookback_sessions = fields.Int(validate=fields.validate.Range(min=1, max=10), load_default=3)
    min_gap_between_exposure = fields.Int(validate=fields.validate.Range(min=1, max=20), load_default=5)


class QuestionOrderRequestSchema(Schema):
    """Schema for question ordering requests."""
    
    test_set_id = fields.Int(required=True)
    beneficiary_id = fields.Int(required=True)
    config = fields.Nested(RandomizationConfigSchema, load_default=dict)
    session_id = fields.Int(allow_none=True)


class ExposureAnalysisSchema(Schema):
    """Schema for exposure analysis requests."""
    
    question_ids = fields.List(fields.Int(), required=True)
    time_period = fields.Int(validate=fields.validate.Range(min=1, max=90), load_default=30)  # days


@randomization_bp.route('/strategies', methods=['GET'])
@jwt_required()
def get_randomization_strategies():
    """Get available randomization strategies."""
    strategies = [
        {
            'value': 'simple_random',
            'label': 'Simple Random',
            'description': 'Random shuffle of all questions'
        },
        {
            'value': 'stratified',
            'label': 'Stratified Random',
            'description': 'Balanced randomization by difficulty and/or topic'
        },
        {
            'value': 'deterministic',
            'label': 'Deterministic Pseudo-Random',
            'description': 'Reproducible randomization using seeds'
        },
        {
            'value': 'adaptive',
            'label': 'Adaptive Randomization',
            'description': 'Personalized based on user history and performance'
        },
        {
            'value': 'template_based',
            'label': 'Template-Based',
            'description': 'Predefined ordering patterns'
        },
        {
            'value': 'balanced',
            'label': 'Balanced Distribution',
            'description': 'Ensures variety in question characteristics'
        }
    ]
    
    templates = [
        {
            'value': 'easy_to_hard',
            'label': 'Easy to Hard',
            'description': 'Questions ordered by increasing difficulty'
        },
        {
            'value': 'hard_to_easy',
            'label': 'Hard to Easy',
            'description': 'Questions ordered by decreasing difficulty'
        },
        {
            'value': 'mixed_difficulty',
            'label': 'Mixed Difficulty',
            'description': 'Evenly distributed difficulty levels'
        },
        {
            'value': 'topic_grouped',
            'label': 'Topic Grouped',
            'description': 'Questions grouped by topic or category'
        },
        {
            'value': 'alternating_difficulty',
            'label': 'Alternating Difficulty',
            'description': 'Alternating pattern of difficulty levels'
        },
        {
            'value': 'cognitive_progression',
            'label': 'Cognitive Progression',
            'description': 'Ordered by cognitive complexity (Bloom\'s taxonomy)'
        }
    ]
    
    return jsonify({
        'strategies': strategies,
        'templates': templates
    }), 200


@randomization_bp.route('/test-sets/<int:test_set_id>/config', methods=['GET'])
@jwt_required()
@cache_response(timeout=300, key_prefix='randomization_config')
def get_test_randomization_config(test_set_id):
    """Get randomization configuration for a test set."""
    try:
        # Get test set
        test_set = TestSet.query.get(test_set_id)
        
        if not test_set:
            return jsonify({
                'error': 'not_found',
                'message': 'Test set not found'
            }), 404
        
        # Check permissions
        if not _check_test_access(test_set):
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to access this test set'
            }), 403
        
        config = {
            'randomization_enabled': test_set.randomization_enabled,
            'randomization_strategy': test_set.randomization_strategy,
            'randomization_config': test_set.randomization_config or {},
            'question_order_template': test_set.question_order_template,
            'anchor_questions': test_set.anchor_questions or {},
            'answer_randomization': test_set.answer_randomization,
            'blocking_rules': test_set.blocking_rules or [],
            'time_based_seed': test_set.time_based_seed
        }
        
        return jsonify(config), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get randomization config error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@randomization_bp.route('/test-sets/<int:test_set_id>/config', methods=['PUT'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def update_test_randomization_config(test_set_id):
    """Update randomization configuration for a test set."""
    try:
        # Get test set
        test_set = TestSet.query.get(test_set_id)
        
        if not test_set:
            return jsonify({
                'error': 'not_found',
                'message': 'Test set not found'
            }), 404
        
        # Check permissions
        if not _check_test_modify_access(test_set):
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to modify this test set'
            }), 403
        
        # Validate request data
        schema = RandomizationConfigSchema()
        try:
            config = schema.load(request.json)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Invalid configuration',
                'errors': e.messages
            }), 400
        
        # Update test set configuration
        test_set.randomization_enabled = request.json.get('randomization_enabled', True)
        test_set.randomization_strategy = config['strategy']
        test_set.randomization_config = {
            'strata_key': config.get('strata_key'),
            'time_window': config.get('time_window'),
            'randomness_factor': config.get('randomness_factor'),
            'lookback_sessions': config.get('lookback_sessions'),
            'min_gap_between_exposure': config.get('min_gap_between_exposure')
        }
        test_set.question_order_template = config.get('template')
        test_set.anchor_questions = config.get('anchor_positions', {})
        test_set.answer_randomization = config.get('enable_answer_randomization', True)
        test_set.blocking_rules = config.get('blocking_rules', [])
        test_set.time_based_seed = config.get('time_based_seed', False)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Randomization configuration updated successfully',
            'config': {
                'randomization_enabled': test_set.randomization_enabled,
                'randomization_strategy': test_set.randomization_strategy,
                'randomization_config': test_set.randomization_config,
                'question_order_template': test_set.question_order_template,
                'anchor_questions': test_set.anchor_questions,
                'answer_randomization': test_set.answer_randomization,
                'blocking_rules': test_set.blocking_rules,
                'time_based_seed': test_set.time_based_seed
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Update randomization config error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@randomization_bp.route('/questions/order', methods=['POST'])
@jwt_required()
def generate_question_order():
    """Generate randomized question order for a test session."""
    try:
        # Validate request
        schema = QuestionOrderRequestSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Invalid request data',
                'errors': e.messages
            }), 400
        
        test_set_id = data['test_set_id']
        beneficiary_id = data['beneficiary_id']
        config = data['config']
        session_id = data.get('session_id')
        
        # Get test set
        test_set = TestSet.query.get(test_set_id)
        if not test_set:
            return jsonify({
                'error': 'not_found',
                'message': 'Test set not found'
            }), 404
        
        # Check permissions
        if not _check_test_access(test_set):
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to access this test set'
            }), 403
        
        # Get questions
        questions = Question.query.filter_by(test_set_id=test_set_id).all()
        
        if not questions:
            return jsonify({
                'error': 'no_questions',
                'message': 'No questions found for this test set'
            }), 400
        
        # Apply repetition prevention if enabled
        if config.get('prevent_repetition', True):
            questions = question_randomization_service.prevent_question_repetition(
                questions,
                beneficiary_id,
                config.get('lookback_sessions', 3),
                config.get('min_gap_between_exposure', 5)
            )
        
        # Merge test set config with request config
        final_config = test_set.randomization_config or {}
        final_config.update(config)
        
        # Add test set specific settings
        if test_set.anchor_questions:
            final_config['anchor_positions'] = test_set.anchor_questions
        if test_set.blocking_rules:
            final_config['blocking_rules'] = test_set.blocking_rules
        if test_set.question_order_template:
            final_config['template'] = test_set.question_order_template
        
        # Determine strategy
        if test_set.randomization_enabled:
            try:
                strategy = RandomizationStrategy(test_set.randomization_strategy)
            except ValueError:
                strategy = RandomizationStrategy.SIMPLE_RANDOM
        else:
            strategy = RandomizationStrategy.SIMPLE_RANDOM
        
        # Randomize questions
        randomized_questions = question_randomization_service.randomize_questions(
            questions,
            strategy,
            beneficiary_id,
            session_id,
            final_config
        )
        
        # Generate answer randomization if enabled
        answer_mappings = {}
        randomized_options = {}
        
        if test_set.answer_randomization:
            for question in randomized_questions:
                if question.type == 'multiple_choice' and question.options:
                    randomization_result = question_randomization_service.randomize_multiple_choice_answers(
                        question,
                        preserve_position=config.get('preserve_answer_positions', [])
                    )
                    answer_mappings[question.id] = randomization_result['mapping']
                    randomized_options[question.id] = randomization_result['options']
        
        # Track exposure
        for question in randomized_questions:
            question_randomization_service.track_question_exposure(
                question.id,
                beneficiary_id,
                session_id or 0
            )
        
        # Prepare response
        question_order = [q.id for q in randomized_questions]
        
        # Serialize questions with randomized options
        serialized_questions = []
        for question in randomized_questions:
            q_dict = question.to_dict()
            
            # Replace options with randomized ones if available
            if question.id in randomized_options:
                q_dict['options'] = randomized_options[question.id]
            
            # Remove correct answer for students
            if current_user.role == 'student':
                q_dict.pop('correct_answer', None)
            
            serialized_questions.append(q_dict)
        
        return jsonify({
            'questions': serialized_questions,
            'question_order': question_order,
            'answer_mappings': answer_mappings,
            'randomization_seed': question_randomization_service.apply_time_based_seed(
                config.get('time_window', 'daily')
            ) if test_set.time_based_seed else None,
            'strategy_used': strategy.value,
            'total_questions': len(randomized_questions)
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Generate question order error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@randomization_bp.route('/questions/exposure', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def analyze_question_exposure():
    """Analyze question exposure rates."""
    try:
        # Validate request
        schema = ExposureAnalysisSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Invalid request data',
                'errors': e.messages
            }), 400
        
        question_ids = data['question_ids']
        time_period = data['time_period']
        
        # Get exposure rates
        exposure_rates = question_randomization_service.get_exposure_rates(question_ids)
        
        # Get detailed statistics
        questions = Question.query.filter(Question.id.in_(question_ids)).all()
        
        analysis = {
            'time_period_days': time_period,
            'questions': []
        }
        
        for question in questions:
            exposure_rate = exposure_rates.get(question.id, 0.0)
            
            question_analysis = {
                'id': question.id,
                'text': question.text[:100] + '...' if len(question.text) > 100 else question.text,
                'difficulty': question.difficulty,
                'category': question.category,
                'exposure_rate': round(exposure_rate, 4),
                'exposure_level': _categorize_exposure(exposure_rate)
            }
            
            analysis['questions'].append(question_analysis)
        
        # Sort by exposure rate
        analysis['questions'].sort(key=lambda x: x['exposure_rate'], reverse=True)
        
        # Add summary statistics
        exposure_values = [q['exposure_rate'] for q in analysis['questions']]
        if exposure_values:
            analysis['summary'] = {
                'total_questions': len(exposure_values),
                'avg_exposure': round(sum(exposure_values) / len(exposure_values), 4),
                'max_exposure': max(exposure_values),
                'min_exposure': min(exposure_values),
                'overexposed_count': len([x for x in exposure_values if x > 0.3]),
                'underexposed_count': len([x for x in exposure_values if x < 0.1])
            }
        else:
            analysis['summary'] = {
                'total_questions': 0,
                'avg_exposure': 0,
                'max_exposure': 0,
                'min_exposure': 0,
                'overexposed_count': 0,
                'underexposed_count': 0
            }
        
        return jsonify(analysis), 200
        
    except Exception as e:
        current_app.logger.exception(f"Analyze question exposure error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@randomization_bp.route('/test-sets/<int:test_set_id>/preview', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def preview_randomization():
    """Preview question randomization without affecting exposure tracking."""
    try:
        # Get test set
        test_set = TestSet.query.get(test_set_id)
        
        if not test_set:
            return jsonify({
                'error': 'not_found',
                'message': 'Test set not found'
            }), 404
        
        # Check permissions
        if not _check_test_access(test_set):
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to access this test set'
            }), 403
        
        # Get questions
        questions = Question.query.filter_by(test_set_id=test_set_id).all()
        
        if not questions:
            return jsonify({
                'error': 'no_questions',
                'message': 'No questions found for this test set'
            }), 400
        
        # Get configuration from request or use test set defaults
        config = request.json or {}
        
        # Merge test set config
        final_config = test_set.randomization_config or {}
        final_config.update(config)
        
        if test_set.anchor_questions:
            final_config['anchor_positions'] = test_set.anchor_questions
        if test_set.blocking_rules:
            final_config['blocking_rules'] = test_set.blocking_rules
        if test_set.question_order_template:
            final_config['template'] = test_set.question_order_template
        
        # Determine strategy
        try:
            strategy = RandomizationStrategy(test_set.randomization_strategy)
        except ValueError:
            strategy = RandomizationStrategy.SIMPLE_RANDOM
        
        # Generate multiple previews
        previews = []
        for i in range(3):  # Generate 3 different previews
            randomized_questions = question_randomization_service.randomize_questions(
                questions.copy(),
                strategy,
                beneficiary_id=None,  # No beneficiary for preview
                session_id=None,
                config=final_config
            )
            
            preview = {
                'preview_id': i + 1,
                'question_order': [q.id for q in randomized_questions],
                'questions': [
                    {
                        'id': q.id,
                        'text': q.text[:100] + '...' if len(q.text) > 100 else q.text,
                        'difficulty': q.difficulty,
                        'category': q.category,
                        'type': q.type,
                        'position': idx + 1
                    }
                    for idx, q in enumerate(randomized_questions)
                ]
            }
            
            previews.append(preview)
        
        return jsonify({
            'strategy': strategy.value,
            'config': final_config,
            'total_questions': len(questions),
            'previews': previews
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Preview randomization error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


# Helper functions

def _check_test_access(test_set):
    """Check if current user can access the test set."""
    if current_user.role == 'super_admin':
        return True
    elif current_user.role == 'tenant_admin':
        tenant_id = current_user.tenants[0].id if current_user.tenants else None
        return tenant_id and test_set.tenant_id == tenant_id
    elif current_user.role == 'trainer':
        return test_set.creator_id == current_user.id
    elif current_user.role == 'student':
        # Students can access if assigned to them
        beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
        return beneficiary and test_set.beneficiary_id == beneficiary.id
    return False


def _check_test_modify_access(test_set):
    """Check if current user can modify the test set."""
    if current_user.role == 'super_admin':
        return True
    elif current_user.role == 'tenant_admin':
        tenant_id = current_user.tenants[0].id if current_user.tenants else None
        return tenant_id and test_set.tenant_id == tenant_id
    elif current_user.role == 'trainer':
        return test_set.creator_id == current_user.id
    return False


def _categorize_exposure(exposure_rate):
    """Categorize exposure rate."""
    if exposure_rate > 0.5:
        return 'very_high'
    elif exposure_rate > 0.3:
        return 'high'
    elif exposure_rate > 0.1:
        return 'moderate'
    elif exposure_rate > 0.05:
        return 'low'
    else:
        return 'very_low'