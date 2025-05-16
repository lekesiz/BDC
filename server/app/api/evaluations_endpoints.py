"""Additional evaluation API endpoints."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from marshmallow import ValidationError
from datetime import datetime

from app.extensions import db
from app.schemas import (
    EvaluationSchema, EvaluationCreateSchema, EvaluationUpdateSchema,
    TestSessionSchema, TestSessionCreateSchema,
    ResponseSchema, ResponseCreateSchema
)
from app.services import (
    EvaluationService, TestSessionService, ResponseService
)
from app.middleware.request_context import auth_required, role_required
from app.utils import cache_response


# Add these routes to the existing evaluations blueprint
def register_additional_routes(evaluations_bp):
    """Register additional evaluation routes."""
    
    @evaluations_bp.route('/sessions', methods=['POST'])
    @jwt_required()
    def create_test_session():
        """Create a new test session."""
        try:
            # Get request data
            schema = TestSessionCreateSchema()
            data = schema.load(request.json)
            
            # Get current user
            user_id = get_jwt_identity()
            
            # Create session
            session = TestSessionService.create_session(
                test_id=data['test_id'],
                user_id=user_id,
                scheduled_date=data.get('scheduled_date')
            )
            
            # Serialize response
            response_schema = TestSessionSchema()
            result = response_schema.dump(session)
            
            return jsonify(result), 201
            
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Validation failed',
                'errors': e.messages
            }), 400
            
        except Exception as e:
            current_app.logger.exception(f"Create test session error: {str(e)}")
            return jsonify({
                'error': 'server_error',
                'message': 'An unexpected error occurred'
            }), 500
    
    
    
    
    @evaluations_bp.route('/sessions/<int:session_id>/complete', methods=['POST'])
    @jwt_required()
    def complete_test_session(session_id):
        """Complete a test session."""
        try:
            # Get current user
            user_id = get_jwt_identity()
            
            # Get session
            session = TestSessionService.get_session(session_id)
            if not session:
                return jsonify({
                    'error': 'not_found',
                    'message': 'Test session not found'
                }), 404
            
            # Check permissions
            if session.user_id != user_id and current_user.role not in ['trainer', 'admin', 'super_admin']:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to complete this session'
                }), 403
            
            # Complete session
            completed_session = TestSessionService.complete_session(session_id)
            
            if not completed_session:
                return jsonify({
                    'error': 'completion_failed',
                    'message': 'Failed to complete session'
                }), 400
            
            # Serialize response
            response_schema = TestSessionSchema()
            result = response_schema.dump(completed_session)
            
            return jsonify({
                'message': 'Session completed successfully',
                'session': result
            }), 200
            
        except Exception as e:
            current_app.logger.exception(f"Complete test session error: {str(e)}")
            return jsonify({
                'error': 'server_error',
                'message': 'An unexpected error occurred'
            }), 500
    
    
    @evaluations_bp.route('/responses', methods=['POST'])
    @jwt_required()
    def submit_response():
        """Submit a response to a question."""
        try:
            # Get request data
            schema = ResponseCreateSchema()
            data = schema.load(request.json)
            
            # Get current user
            user_id = get_jwt_identity()
            
            # Verify session access
            session = TestSessionService.get_session(data['session_id'])
            if not session:
                return jsonify({
                    'error': 'not_found',
                    'message': 'Test session not found'
                }), 404
            
            if session.user_id != user_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to submit responses to this session'
                }), 403
            
            # Submit response
            response = ResponseService.submit_response(
                session_id=data['session_id'],
                question_id=data['question_id'],
                answer=data['answer'],
                user_id=user_id
            )
            
            # Serialize response
            response_schema = ResponseSchema()
            result = response_schema.dump(response)
            
            return jsonify(result), 201
            
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Validation failed',
                'errors': e.messages
            }), 400
            
        except Exception as e:
            current_app.logger.exception(f"Submit response error: {str(e)}")
            return jsonify({
                'error': 'server_error',
                'message': 'An unexpected error occurred'
            }), 500
    
    
    @evaluations_bp.route('/sessions/<int:session_id>/submit', methods=['POST'])
    @jwt_required()
    def submit_all_responses(session_id):
        """Submit all responses for a test session at once."""
        try:
            # Get current user
            user_id = get_jwt_identity()
            
            # Get session
            session = TestSessionService.get_session(session_id)
            if not session:
                return jsonify({
                    'error': 'not_found',
                    'message': 'Test session not found'
                }), 404
            
            # Check permissions
            if session.user_id != user_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to submit responses to this session'
                }), 403
            
            # Get responses from request
            data = request.json
            if 'responses' not in data or not isinstance(data['responses'], list):
                return jsonify({
                    'error': 'invalid_data',
                    'message': 'Responses must be provided as a list'
                }), 400
            
            # Submit all responses
            submitted_responses = []
            for response_data in data['responses']:
                response = ResponseService.submit_response(
                    session_id=session_id,
                    question_id=response_data['question_id'],
                    answer=response_data['answer'],
                    user_id=user_id
                )
                submitted_responses.append(response)
            
            # Complete session if requested
            if data.get('complete_session', False):
                TestSessionService.complete_session(session_id)
            
            # Serialize responses
            response_schema = ResponseSchema(many=True)
            result = response_schema.dump(submitted_responses)
            
            return jsonify({
                'message': f'{len(submitted_responses)} responses submitted successfully',
                'responses': result
            }), 201
            
        except Exception as e:
            current_app.logger.exception(f"Submit all responses error: {str(e)}")
            return jsonify({
                'error': 'server_error',
                'message': 'An unexpected error occurred'
            }), 500