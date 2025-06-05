"""API endpoints for Adaptive Test System."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError

from app.models import AdaptiveTestPool, AdaptiveQuestion, AdaptiveTestSession, AdaptiveTestReport
from app.services.adaptive_test_service import (
    AdaptiveTestService, AdaptiveQuestionService, AdaptiveTestIntegrationService
)
from app.utils.decorators import tenant_required, rate_limit
from app.extensions import db

from app.utils.logging import logger


# Schemas
class AdaptiveTestPoolSchema(Schema):
    """Schema for adaptive test pool."""
    id = fields.Int(dump_only=True)
    tenant_id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    subject = fields.Str(allow_none=True)
    grade_level = fields.Str(allow_none=True)
    total_questions = fields.Int(dump_only=True)
    is_active = fields.Bool(default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class AdaptiveQuestionSchema(Schema):
    """Schema for adaptive question."""
    id = fields.Int(dump_only=True)
    pool_id = fields.Int(required=True)
    text = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf([
        'multiple_choice', 'true_false', 'matching', 'ordering', 'text'
    ]))
    options = fields.Dict(allow_none=True)
    correct_answer = fields.Raw(allow_none=True)
    explanation = fields.Str(allow_none=True)
    
    # IRT parameters
    difficulty = fields.Float(required=True, validate=validate.Range(min=-3, max=3))
    discrimination = fields.Float(default=1.0, validate=validate.Range(min=0.1, max=2.5))
    guessing = fields.Float(default=0.0, validate=validate.Range(min=0, max=0.3))
    
    # Categorization
    difficulty_level = fields.Int(required=True, validate=validate.Range(min=1, max=10))
    topic = fields.Str(allow_none=True)
    subtopic = fields.Str(allow_none=True)
    cognitive_level = fields.Str(allow_none=True, validate=validate.OneOf([
        'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'
    ]))
    
    # Statistics
    usage_count = fields.Int(dump_only=True)
    correct_count = fields.Int(dump_only=True)
    average_response_time = fields.Float(dump_only=True)
    exposure_rate = fields.Float(dump_only=True)
    information_value = fields.Float(dump_only=True)
    
    is_active = fields.Bool(default=True)
    review_status = fields.Str(default='approved', validate=validate.OneOf([
        'draft', 'approved', 'needs_review'
    ]))
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class AdaptiveSessionConfigSchema(Schema):
    """Schema for adaptive session configuration."""
    max_questions = fields.Int(default=20, validate=validate.Range(min=5, max=100))
    max_time = fields.Int(allow_none=True, validate=validate.Range(min=5, max=180))
    standard_error_threshold = fields.Float(default=0.3, validate=validate.Range(min=0.1, max=1.0))
    initial_ability = fields.Float(default=0.0, validate=validate.Range(min=-3, max=3))
    selection_method = fields.Str(default='maximum_information', validate=validate.OneOf([
        'maximum_information', 'closest_difficulty', 'random'
    ]))
    topic_balancing = fields.Bool(default=True)
    exposure_control = fields.Bool(default=True)
    test_id = fields.Int(allow_none=True)


class SubmitResponseSchema(Schema):
    """Schema for submitting response."""
    question_id = fields.Int(required=True)
    answer = fields.Raw(required=True)
    response_time = fields.Float(allow_none=True)


class AdaptiveTestReportSchema(Schema):
    """Schema for adaptive test report."""
    id = fields.Int(dump_only=True)
    session_id = fields.Int(dump_only=True)
    final_ability = fields.Float(dump_only=True)
    ability_percentile = fields.Float(dump_only=True)
    performance_level = fields.Str(dump_only=True)
    topic_strengths = fields.List(fields.Str(), dump_only=True)
    topic_weaknesses = fields.List(fields.Str(), dump_only=True)
    topic_scores = fields.Dict(dump_only=True)
    response_patterns = fields.Dict(dump_only=True)
    recommended_topics = fields.List(fields.Str(), dump_only=True)
    recommended_difficulty = fields.Float(dump_only=True)
    next_steps = fields.List(fields.Str(), dump_only=True)
    total_questions = fields.Int(dump_only=True)
    correct_answers = fields.Int(dump_only=True)
    average_difficulty = fields.Float(dump_only=True)
    response_consistency = fields.Float(dump_only=True)
    generated_at = fields.DateTime(dump_only=True)


# Blueprint
adaptive_test_bp = Blueprint('adaptive_tests', __name__, url_prefix='/api/adaptive-tests')


# Pool endpoints
@adaptive_test_bp.route('/pools', methods=['GET'])
@jwt_required()
@tenant_required()
def get_pools():
    """Get all adaptive test pools."""
    tenant_id = request.args.get('tenant_id', type=int)
    
    pools = AdaptiveTestPool.query.filter_by(tenant_id=tenant_id).all()
    schema = AdaptiveTestPoolSchema(many=True)
    
    return jsonify({
        'pools': schema.dump(pools),
        'total': len(pools)
    }), 200


@adaptive_test_bp.route('/pools', methods=['POST'])
@jwt_required()
@tenant_required()
@rate_limit(limit=10, per=60)
def create_pool():
    """Create a new adaptive test pool."""
    schema = AdaptiveTestPoolSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    
    try:
        pool = AdaptiveTestService.create_question_pool(
            tenant_id=data['tenant_id'],
            data=data
        )
        
        return jsonify({
            'message': 'Pool created successfully',
            'pool': schema.dump(pool)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@adaptive_test_bp.route('/pools/<int:pool_id>', methods=['GET'])
@jwt_required()
@tenant_required()
def get_pool(pool_id):
    """Get a specific adaptive test pool."""
    pool = AdaptiveTestPool.query.get(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
    
    schema = AdaptiveTestPoolSchema()
    return jsonify(schema.dump(pool)), 200


# Question endpoints
@adaptive_test_bp.route('/pools/<int:pool_id>/questions', methods=['GET'])
@jwt_required()
@tenant_required()
def get_pool_questions(pool_id):
    """Get questions in a pool."""
    pool = AdaptiveTestPool.query.get(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
    
    # Filters
    topic = request.args.get('topic')
    difficulty_level = request.args.get('difficulty_level', type=int)
    is_active = request.args.get('is_active', type=lambda x: x.lower() == 'true')
    
    # Query
    query = AdaptiveQuestion.query.filter_by(pool_id=pool_id)
    
    if topic:
        query = query.filter_by(topic=topic)
    if difficulty_level:
        query = query.filter_by(difficulty_level=difficulty_level)
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    questions = query.all()
    schema = AdaptiveQuestionSchema(many=True)
    
    return jsonify({
        'questions': schema.dump(questions),
        'total': len(questions)
    }), 200


@adaptive_test_bp.route('/pools/<int:pool_id>/questions', methods=['POST'])
@jwt_required()
@tenant_required()
@rate_limit(limit=50, per=60)
def add_question(pool_id):
    """Add a question to the pool."""
    pool = AdaptiveTestPool.query.get(pool_id)
    if not pool:
        return jsonify({'error': 'Pool not found'}), 404
    
    schema = AdaptiveQuestionSchema()
    
    try:
        data = schema.load(request.json)
        data['pool_id'] = pool_id
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    
    try:
        question = AdaptiveTestService.add_question_to_pool(pool_id, data)
        
        return jsonify({
            'message': 'Question added successfully',
            'question': schema.dump(question)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@adaptive_test_bp.route('/questions/<int:question_id>/statistics', methods=['GET'])
@jwt_required()
@tenant_required()
def get_question_statistics(question_id):
    """Get detailed statistics for a question."""
    stats = AdaptiveQuestionService.get_question_statistics(question_id)
    if not stats:
        return jsonify({'error': 'Question not found'}), 404
    
    return jsonify(stats), 200


@adaptive_test_bp.route('/questions/<int:question_id>/calibrate', methods=['POST'])
@jwt_required()
@tenant_required()
def calibrate_question(question_id):
    """Calibrate IRT parameters for a question."""
    result = AdaptiveQuestionService.calibrate_irt_parameters(question_id)
    if not result:
        return jsonify({'error': 'Question not found'}), 404
    
    return jsonify({
        'message': 'Calibration completed',
        'result': result
    }), 200


# Session endpoints
@adaptive_test_bp.route('/sessions/start', methods=['POST'])
@jwt_required()
@tenant_required()
@rate_limit(limit=10, per=60)
def start_session():
    """Start a new adaptive test session."""
    data = request.json
    pool_id = data.get('pool_id')
    beneficiary_id = data.get('beneficiary_id')
    
    if not pool_id or not beneficiary_id:
        return jsonify({'error': 'pool_id and beneficiary_id are required'}), 400
    
    # Validate configuration
    config_schema = AdaptiveSessionConfigSchema()
    try:
        config = config_schema.load(data.get('config', {}))
    except ValidationError as e:
        return jsonify({'error': 'Invalid configuration', 'messages': e.messages}), 400
    
    try:
        session = AdaptiveTestService.start_adaptive_session(
            pool_id=pool_id,
            beneficiary_id=beneficiary_id,
            config=config
        )
        
        # Get first question
        first_question = AdaptiveTestService.get_next_question(session.id)
        
        return jsonify({
            'message': 'Session started successfully',
            'session': {
                'id': session.id,
                'pool_id': session.pool_id,
                'beneficiary_id': session.beneficiary_id,
                'max_questions': session.max_questions,
                'questions_answered': session.questions_answered,
                'current_ability': session.current_ability,
                'status': session.status
            },
            'next_question': AdaptiveQuestionSchema().dump(first_question) if first_question else None
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@adaptive_test_bp.route('/sessions/<int:session_id>/next', methods=['GET'])
@jwt_required()
@tenant_required()
def get_next_question(session_id):
    """Get the next question in an adaptive session."""
    session = AdaptiveTestSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if session.status != 'in_progress':
        return jsonify({'error': 'Session is not in progress'}), 400
    
    next_question = AdaptiveTestService.get_next_question(session_id)
    
    if not next_question:
        return jsonify({
            'message': 'No more questions available',
            'session_complete': True,
            'final_ability': session.final_ability,
            'questions_answered': session.questions_answered
        }), 200
    
    schema = AdaptiveQuestionSchema()
    return jsonify({
        'question': schema.dump(next_question),
        'progress': {
            'questions_answered': session.questions_answered,
            'max_questions': session.max_questions,
            'current_ability': session.current_ability,
            'ability_se': session.ability_se
        }
    }), 200


@adaptive_test_bp.route('/sessions/<int:session_id>/submit', methods=['POST'])
@jwt_required()
@tenant_required()
def submit_response(session_id):
    """Submit a response to the current question."""
    session = AdaptiveTestSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if session.status != 'in_progress':
        return jsonify({'error': 'Session is not in progress'}), 400
    
    schema = SubmitResponseSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'messages': e.messages}), 400
    
    try:
        response, new_ability, se = AdaptiveTestService.submit_response(
            session_id=session_id,
            question_id=data['question_id'],
            answer=data['answer'],
            response_time=data.get('response_time')
        )
        
        # Check if session should stop
        session = AdaptiveTestSession.query.get(session_id)
        should_stop, reason = session.should_stop()
        
        # Get next question if continuing
        next_question = None
        if not should_stop:
            next_question = AdaptiveTestService.get_next_question(session_id)
        
        return jsonify({
            'message': 'Response submitted successfully',
            'response': {
                'is_correct': response.is_correct,
                'ability_after': new_ability,
                'se_after': se
            },
            'session': {
                'questions_answered': session.questions_answered,
                'current_ability': session.current_ability,
                'ability_se': session.ability_se,
                'status': session.status,
                'should_stop': should_stop,
                'stop_reason': reason if should_stop else None
            },
            'next_question': AdaptiveQuestionSchema().dump(next_question) if next_question else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@adaptive_test_bp.route('/sessions/<int:session_id>/complete', methods=['POST'])
@jwt_required()
@tenant_required()
def complete_session(session_id):
    """Complete an adaptive test session."""
    try:
        session = AdaptiveTestService.complete_session(session_id)
        
        # Get report
        report = AdaptiveTestReport.query.filter_by(session_id=session_id).first()
        
        return jsonify({
            'message': 'Session completed successfully',
            'session': {
                'id': session.id,
                'final_ability': session.final_ability,
                'final_se': session.final_se,
                'confidence_interval': [
                    session.confidence_interval_lower,
                    session.confidence_interval_upper
                ],
                'questions_answered': session.questions_answered,
                'total_time_seconds': session.total_time_seconds
            },
            'report': AdaptiveTestReportSchema().dump(report) if report else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@adaptive_test_bp.route('/sessions/<int:session_id>/report', methods=['GET'])
@jwt_required()
@tenant_required()
def get_session_report(session_id):
    """Get report for a completed session."""
    session = AdaptiveTestSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if session.status != 'completed':
        return jsonify({'error': 'Session not completed'}), 400
    
    report = AdaptiveTestReport.query.filter_by(session_id=session_id).first()
    if not report:
        # Generate report if not exists
        report = AdaptiveTestService.generate_report(session_id)
    
    schema = AdaptiveTestReportSchema()
    return jsonify(schema.dump(report)), 200


# Integration endpoints
@adaptive_test_bp.route('/integrate/evaluation', methods=['POST'])
@jwt_required()
@tenant_required()
def create_adaptive_evaluation():
    """Create an evaluation that uses adaptive testing."""
    data = request.json
    test_set_id = data.get('test_set_id')
    pool_id = data.get('pool_id')
    
    if not test_set_id or not pool_id:
        return jsonify({'error': 'test_set_id and pool_id are required'}), 400
    
    # Validate configuration
    config_schema = AdaptiveSessionConfigSchema()
    try:
        config = config_schema.load(data.get('config', {}))
    except ValidationError as e:
        return jsonify({'error': 'Invalid configuration', 'messages': e.messages}), 400
    
    try:
        result = AdaptiveTestIntegrationService.create_adaptive_evaluation(
            test_set_id=test_set_id,
            pool_id=pool_id,
            config=config
        )
        
        return jsonify({
            'message': 'Adaptive evaluation created successfully',
            'result': result
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@adaptive_test_bp.route('/integrate/sync', methods=['POST'])
@jwt_required()
@tenant_required()
def sync_to_evaluation():
    """Sync adaptive test results to regular evaluation."""
    data = request.json
    adaptive_session_id = data.get('adaptive_session_id')
    evaluation_id = data.get('evaluation_id')
    
    if not adaptive_session_id or not evaluation_id:
        return jsonify({'error': 'adaptive_session_id and evaluation_id are required'}), 400
    
    try:
        success = AdaptiveTestIntegrationService.sync_adaptive_session_to_evaluation(
            adaptive_session_id=adaptive_session_id,
            evaluation_id=evaluation_id
        )
        
        if success:
            return jsonify({'message': 'Sync completed successfully'}), 200
        else:
            return jsonify({'error': 'Sync failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500