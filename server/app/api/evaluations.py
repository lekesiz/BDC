"""Evaluations API."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from marshmallow import ValidationError

from app.extensions import db
from app.schemas import (
    EvaluationSchema, EvaluationCreateSchema, EvaluationUpdateSchema,
    QuestionSchema, QuestionCreateSchema, QuestionUpdateSchema,
    TestSessionSchema, TestSessionCreateSchema,
    ResponseSchema, ResponseCreateSchema,
    AIFeedbackSchema, AIFeedbackUpdateSchema
)
from app.services import QuestionService
from app.services.evaluation_service_factory import EvaluationServiceFactory
from app.middleware.request_context import auth_required, role_required
from app.utils import cache_response

from app.utils.logging import logger


evaluations_bp = Blueprint('evaluations', __name__)

# Create service instance
evaluation_service = EvaluationServiceFactory.create()

# Additional endpoints can be added here if needed


@evaluations_bp.route('', methods=['GET'])
@jwt_required()
@cache_response(timeout=300, key_prefix='evaluations')
def get_evaluations():
    """Get all evaluations with optional filtering."""
    try:
        # Get query parameters
        tenant_id = request.args.get('tenant_id', type=int)
        creator_id = request.args.get('creator_id', type=int)
        beneficiary_id = request.args.get('beneficiary_id', type=int)
        status = request.args.get('status')
        type = request.args.get('type')
        is_template = request.args.get('is_template', type=lambda v: v.lower() == 'true' if v else None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Apply role-based filtering
        if current_user.role == 'tenant_admin':
            # Tenant admins can only see evaluations from their tenant
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id:
                return jsonify({
                    'error': 'tenant_required',
                    'message': 'Tenant admin must belong to a tenant'
                }), 400
        elif current_user.role == 'trainer':
            # Trainers can only see evaluations they created or those for their beneficiaries
            if not creator_id:
                creator_id = current_user.id
        elif current_user.role == 'student':
            # Students can only see evaluations assigned to them
            from app.models import Beneficiary
            current_app.logger.info(f"Student user ID: {current_user.id}, Email: {current_user.email}")
            beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
            current_app.logger.info(f"Beneficiary found: {beneficiary is not None}")
            if beneficiary:
                current_app.logger.info(f"Beneficiary ID: {beneficiary.id}, User ID: {beneficiary.user_id}")
            beneficiary_id = beneficiary.id if beneficiary else None
            if not beneficiary_id:
                return jsonify({
                    'error': 'beneficiary_required',
                    'message': 'Student must have a beneficiary profile'
                }), 400
        
        # Get evaluations
        result = evaluation_service.get_evaluations(
            tenant_id=tenant_id,
            creator_id=creator_id,
            beneficiary_id=beneficiary_id,
            status=status,
            evaluation_type=type,
            is_template=is_template,
            page=page,
            per_page=per_page
        )
        evaluations = result.items
        total = result.total
        pages = result.pages
        
        # Serialize data
        schema = EvaluationSchema(many=True)
        result = schema.dump(evaluations)
        
        # Return paginated response
        return jsonify({
            'items': result,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get evaluations error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@cache_response(timeout=300, key_prefix='evaluation')
def get_evaluation(id):
    """Get an evaluation by ID."""
    try:
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(id)
        
        if not evaluation:
            return jsonify({
                'error': 'not_found',
                'message': 'Evaluation not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or evaluation.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to access this evaluation'
                }), 403
        elif current_user.role == 'trainer':
            if evaluation.creator_id != current_user.id:
                # Also check if it's for their beneficiary
                can_access = False
                if evaluation.beneficiary_id:
                    from app.models import Beneficiary
                    beneficiary = Beneficiary.query.get(evaluation.beneficiary_id)
                    if beneficiary and beneficiary.trainer_id == current_user.id:
                        can_access = True
                
                if not can_access:
                    return jsonify({
                        'error': 'forbidden',
                        'message': 'You do not have permission to access this evaluation'
                    }), 403
        elif current_user.role == 'student':
            from app.models import Beneficiary
            beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
            beneficiary_id = beneficiary.id if beneficiary else None
            if not beneficiary_id or evaluation.beneficiary_id != beneficiary_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to access this evaluation'
                }), 403
        
        # Get questions - check if we need randomized order
        if current_user.role == 'student':
            # For students, get questions in randomized order if this is part of an active session
            from app.services.evaluation_service import TestSessionService
            
            # Try to find an active session for this student
            from app.models import Beneficiary
            beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
            if beneficiary:
                active_session = TestSession.query.filter_by(
                    test_set_id=evaluation.id,
                    beneficiary_id=beneficiary.id,
                    status='in_progress'
                ).first()
                
                if active_session:
                    questions, answer_mappings = TestSessionService.get_randomized_questions(active_session.id)
                    if questions is None:
                        questions, _, _ = QuestionService.get_questions(evaluation.id, per_page=100)
                        answer_mappings = {}
                else:
                    questions, _, _ = QuestionService.get_questions(evaluation.id, per_page=100)
                    answer_mappings = {}
            else:
                questions, _, _ = QuestionService.get_questions(evaluation.id, per_page=100)
                answer_mappings = {}
        else:
            # For non-students, get regular order
            questions, _, _ = QuestionService.get_questions(evaluation.id, per_page=100)
            answer_mappings = {}
        
        # Serialize data
        schema = EvaluationSchema()
        result = schema.dump(evaluation)
        
        # Add questions to the result
        question_schema = QuestionSchema(many=True)
        serialized_questions = question_schema.dump(questions)
        
        # Apply answer randomization if needed
        if answer_mappings:
            for q_data in serialized_questions:
                q_id = str(q_data['id'])
                if q_id in answer_mappings and q_data.get('options'):
                    # Reorder options based on mapping
                    original_options = q_data['options']
                    mapping = answer_mappings[q_id]
                    
                    # Create new options array
                    new_options = [None] * len(original_options)
                    for original_idx, new_idx in mapping.items():
                        if int(original_idx) < len(original_options):
                            new_options[new_idx] = original_options[int(original_idx)]
                    
                    q_data['options'] = [opt for opt in new_options if opt is not None]
        
        result['questions'] = serialized_questions
        
        # Return evaluation
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get evaluation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def create_evaluation():
    """Create a new evaluation."""
    try:
        # Validate request data
        schema = EvaluationCreateSchema()
        data = schema.load(request.json)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id:
                return jsonify({
                    'error': 'tenant_required',
                    'message': 'Tenant admin must belong to a tenant'
                }), 400
            
            # Override tenant_id with the admin's tenant
            data['tenant_id'] = tenant_id
        elif current_user.role == 'trainer':
            # Trainers can only create evaluations for their tenant and beneficiaries
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id:
                return jsonify({
                    'error': 'tenant_required',
                    'message': 'Trainer must belong to a tenant'
                }), 400
            
            # Override tenant_id with the trainer's tenant
            data['tenant_id'] = tenant_id
            
            # Check if beneficiary is assigned to them
            if data.get('beneficiary_id'):
                from app.models import Beneficiary
                beneficiary = Beneficiary.query.get(data['beneficiary_id'])
                if not beneficiary or beneficiary.trainer_id != current_user.id:
                    return jsonify({
                        'error': 'forbidden',
                        'message': 'You do not have permission to create evaluations for this beneficiary'
                    }), 403
        
        # Create evaluation
        evaluation = evaluation_service.create_evaluation(current_user.id, data)
        
        # Serialize data
        response_schema = EvaluationSchema()
        result = response_schema.dump(evaluation)
        
        # Return created evaluation
        return jsonify(result), 201
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        current_app.logger.exception(f"Create evaluation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def update_evaluation(id):
    """Update an evaluation."""
    try:
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(id)
        
        if not evaluation:
            return jsonify({
                'error': 'not_found',
                'message': 'Evaluation not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or evaluation.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to update this evaluation'
                }), 403
        elif current_user.role == 'trainer':
            if evaluation.creator_id != current_user.id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to update this evaluation'
                }), 403
        
        # Validate request data
        schema = EvaluationUpdateSchema()
        data = schema.load(request.json)
        
        # Update evaluation
        updated_evaluation = evaluation_service.update_evaluation(id, data)
        
        # Serialize data
        response_schema = EvaluationSchema()
        result = response_schema.dump(updated_evaluation)
        
        # Return updated evaluation
        return jsonify(result), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        current_app.logger.exception(f"Update evaluation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def delete_evaluation(id):
    """Delete an evaluation."""
    try:
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(id)
        
        if not evaluation:
            return jsonify({
                'error': 'not_found',
                'message': 'Evaluation not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or evaluation.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to delete this evaluation'
                }), 403
        elif current_user.role == 'trainer':
            if evaluation.creator_id != current_user.id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to delete this evaluation'
                }), 403
        
        # Delete evaluation
        success = evaluation_service.delete_evaluation(id)
        
        if not success:
            return jsonify({
                'error': 'deletion_failed',
                'message': 'Failed to delete evaluation'
            }), 400
        
        # Return success response
        return jsonify({
            'message': 'Evaluation deleted successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Delete evaluation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


# Questions endpoints

@evaluations_bp.route('/<int:evaluation_id>/questions', methods=['GET'])
@jwt_required()
def get_questions(evaluation_id):
    """Get questions for an evaluation."""
    try:
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(evaluation_id)
        
        if not evaluation:
            return jsonify({
                'error': 'not_found',
                'message': 'Evaluation not found'
            }), 404
        
        # Check permissions (same as for getting the evaluation)
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or evaluation.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to access questions for this evaluation'
                }), 403
        elif current_user.role == 'trainer':
            if evaluation.creator_id != current_user.id:
                # Also check if it's for their beneficiary
                can_access = False
                if evaluation.beneficiary_id:
                    from app.models import Beneficiary
                    beneficiary = Beneficiary.query.get(evaluation.beneficiary_id)
                    if beneficiary and beneficiary.trainer_id == current_user.id:
                        can_access = True
                
                if not can_access:
                    return jsonify({
                        'error': 'forbidden',
                        'message': 'You do not have permission to access questions for this evaluation'
                    }), 403
        elif current_user.role == 'student':
            from app.models import Beneficiary
            beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
            beneficiary_id = beneficiary.id if beneficiary else None
            if not beneficiary_id or evaluation.beneficiary_id != beneficiary_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to access questions for this evaluation'
                }), 403
        
        # Get query parameters
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        type = request.args.get('type')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get questions
        questions, total, pages = QuestionService.get_questions(
            evaluation_id=evaluation_id,
            category=category,
            difficulty=difficulty,
            type=type,
            page=page,
            per_page=per_page
        )
        
        # For students, don't include correct answers
        is_student = current_user.role == 'student'
        
        # Serialize data
        schema = QuestionSchema(many=True)
        result = schema.dump(questions)
        
        # Remove correct answers for students
        if is_student:
            for question in result:
                question.pop('correct_answer', None)
        
        # Return paginated response
        return jsonify({
            'items': result,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get questions error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/<int:evaluation_id>/questions', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def create_question(evaluation_id):
    """Create a new question for an evaluation."""
    try:
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(evaluation_id)
        
        if not evaluation:
            return jsonify({
                'error': 'not_found',
                'message': 'Evaluation not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or evaluation.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to create questions for this evaluation'
                }), 403
        elif current_user.role == 'trainer':
            if evaluation.creator_id != current_user.id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to create questions for this evaluation'
                }), 403
        
        # Validate request data
        schema = QuestionCreateSchema()
        data = schema.load(request.json)
        
        # Add evaluation ID to data
        data['evaluation_id'] = evaluation_id
        
        # Create question
        question = QuestionService.create_question(data)
        
        # Serialize data
        response_schema = QuestionSchema()
        result = response_schema.dump(question)
        
        # Return created question
        return jsonify(result), 201
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        current_app.logger.exception(f"Create question error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/questions/<int:question_id>', methods=['PATCH'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def update_question(question_id):
    """Update a question."""
    try:
        # Get question
        question = QuestionService.get_question(question_id)
        
        if not question:
            return jsonify({
                'error': 'not_found',
                'message': 'Question not found'
            }), 404
        
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(question.evaluation_id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or evaluation.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to update this question'
                }), 403
        elif current_user.role == 'trainer':
            if evaluation.creator_id != current_user.id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to update this question'
                }), 403
        
        # Validate request data
        schema = QuestionUpdateSchema()
        data = schema.load(request.json)
        
        # Update question
        updated_question = QuestionService.update_question(question_id, data)
        
        # Serialize data
        response_schema = QuestionSchema()
        result = response_schema.dump(updated_question)
        
        # Return updated question
        return jsonify(result), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        current_app.logger.exception(f"Update question error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def delete_question(question_id):
    """Delete a question."""
    try:
        # Get question
        question = QuestionService.get_question(question_id)
        
        if not question:
            return jsonify({
                'error': 'not_found',
                'message': 'Question not found'
            }), 404
        
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(question.evaluation_id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or evaluation.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to delete this question'
                }), 403
        elif current_user.role == 'trainer':
            if evaluation.creator_id != current_user.id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to delete this question'
                }), 403
        
        # Delete question
        success = QuestionService.delete_question(question_id)
        
        if not success:
            return jsonify({
                'error': 'deletion_failed',
                'message': 'Failed to delete question'
            }), 400
        
        # Return success response
        return jsonify({
            'message': 'Question deleted successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Delete question error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


# Test session endpoints

@evaluations_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get test sessions with optional filtering."""
    try:
        # Get query parameters
        evaluation_id = request.args.get('evaluation_id', type=int)
        beneficiary_id = request.args.get('beneficiary_id', type=int)
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Apply role-based filtering
        if current_user.role == 'tenant_admin':
            # Tenant admins can only see sessions for evaluations from their tenant
            if evaluation_id:
                evaluation = evaluation_service.get_evaluation_by_id(evaluation_id)
                tenant_id = current_user.tenants[0].id if current_user.tenants else None
                if not tenant_id or (evaluation and evaluation.tenant_id != tenant_id):
                    return jsonify({
                        'error': 'forbidden',
                        'message': 'You do not have permission to access sessions for this evaluation'
                    }), 403
            elif beneficiary_id:
                # Check if beneficiary belongs to tenant
                from app.models import Beneficiary
                beneficiary = Beneficiary.query.get(beneficiary_id)
                tenant_id = current_user.tenants[0].id if current_user.tenants else None
                if not tenant_id or (beneficiary and beneficiary.tenant_id != tenant_id):
                    return jsonify({
                        'error': 'forbidden',
                        'message': 'You do not have permission to access sessions for this beneficiary'
                    }), 403
            else:
                # Can't get all sessions, must filter by evaluation or beneficiary
                return jsonify({
                    'error': 'filter_required',
                    'message': 'Must filter by evaluation_id or beneficiary_id'
                }), 400
        elif current_user.role == 'trainer':
            # Trainers can only see sessions for their beneficiaries or evaluations they created
            if evaluation_id:
                evaluation = evaluation_service.get_evaluation_by_id(evaluation_id)
                if evaluation and evaluation.creator_id != current_user.id:
                    return jsonify({
                        'error': 'forbidden',
                        'message': 'You do not have permission to access sessions for this evaluation'
                    }), 403
            elif beneficiary_id:
                # Check if beneficiary is assigned to them
                from app.models import Beneficiary
                beneficiary = Beneficiary.query.get(beneficiary_id)
                if not beneficiary or beneficiary.trainer_id != current_user.id:
                    return jsonify({
                        'error': 'forbidden',
                        'message': 'You do not have permission to access sessions for this beneficiary'
                    }), 403
            else:
                # Can't get all sessions, must filter by evaluation or beneficiary
                return jsonify({
                    'error': 'filter_required',
                    'message': 'Must filter by evaluation_id or beneficiary_id'
                }), 400
        elif current_user.role == 'student':
            # Students can only see their own sessions
            from app.models import Beneficiary
            beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
            beneficiary_id = beneficiary.id if beneficiary else None
            if not beneficiary_id:
                return jsonify({
                    'error': 'beneficiary_required',
                    'message': 'Student must have a beneficiary profile'
                }), 400
        
        # Get sessions
        sessions, total, pages = TestSessionService.get_sessions(
            evaluation_id=evaluation_id,
            beneficiary_id=beneficiary_id,
            status=status,
            page=page,
            per_page=per_page
        )
        
        # Serialize data
        schema = TestSessionSchema(many=True)
        result = schema.dump(sessions)
        
        # Return paginated response
        return jsonify({
            'items': result,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get sessions error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/<int:id>/submit', methods=['POST'])
@jwt_required()
def submit_evaluation(id):
    """Submit responses for an evaluation."""
    try:
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(id)
        
        if not evaluation:
            return jsonify({
                'error': 'not_found',
                'message': 'Evaluation not found'
            }), 404
        
        # Check permissions - only the assigned beneficiary can submit
        if current_user.role == 'student':
            from app.models import Beneficiary
            beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
            beneficiary_id = beneficiary.id if beneficiary else None
            if not beneficiary_id or evaluation.beneficiary_id != beneficiary_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to submit this evaluation'
                }), 403
        else:
            return jsonify({
                'error': 'forbidden',
                'message': 'Only students can submit evaluations'
            }), 403
        
        # Get or create test session
        from app.services import TestSessionService
        session = TestSessionService.get_active_session(evaluation.id, beneficiary_id)
        if not session:
            session = TestSessionService.create_session({
                'evaluation_id': evaluation.id,
                'beneficiary_id': beneficiary_id,
                'status': 'in_progress'
            })
        
        # Save responses
        responses = request.json.get('responses', [])
        from app.services import ResponseService
        for response_data in responses:
            response_data['session_id'] = session.id
            response_data['beneficiary_id'] = beneficiary_id
            ResponseService.create_response(response_data)
        
        # Mark session as completed
        TestSessionService.update_session(session.id, {'status': 'completed'})
        
        # Calculate score
        from app.services import EvaluationScoringService
        score = EvaluationScoringService.calculate_score(session.id)
        TestSessionService.update_session(session.id, {'score': score})
        
        return jsonify({
            'message': 'Evaluation submitted successfully',
            'session_id': session.id,
            'score': score
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Submit evaluation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/<int:id>/results', methods=['GET'])
@jwt_required()
def get_evaluation_results(id):
    """Get results for an evaluation."""
    try:
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(id)
        
        if not evaluation:
            return jsonify({
                'error': 'not_found',
                'message': 'Evaluation not found'
            }), 404
        
        # Check permissions
        beneficiary_id = None
        if current_user.role == 'student':
            from app.models import Beneficiary
            beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
            beneficiary_id = beneficiary.id if beneficiary else None
            if not beneficiary_id or evaluation.beneficiary_id != beneficiary_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to view these results'
                }), 403
        elif current_user.role == 'trainer':
            # Trainers can view results of their evaluations or beneficiaries
            if evaluation.creator_id != current_user.id:
                from app.models import Beneficiary
                beneficiary = Beneficiary.query.get(evaluation.beneficiary_id)
                if not beneficiary or beneficiary.trainer_id != current_user.id:
                    return jsonify({
                        'error': 'forbidden',
                        'message': 'You do not have permission to view these results'
                    }), 403
            beneficiary_id = request.args.get('beneficiary_id', type=int) or evaluation.beneficiary_id
        else:
            beneficiary_id = request.args.get('beneficiary_id', type=int) or evaluation.beneficiary_id
        
        # Get test session
        from app.services import TestSessionService
        session = TestSessionService.get_latest_session(evaluation.id, beneficiary_id)
        
        if not session:
            return jsonify({
                'error': 'not_found',
                'message': 'No completed evaluation session found'
            }), 404
        
        # Get responses
        from app.services import ResponseService
        responses = ResponseService.get_session_responses(session.id)
        
        # Get AI feedback if available
        from app.services import AIFeedbackService
        ai_feedback = AIFeedbackService.get_session_feedback(session.id)
        
        result = {
            'evaluation_id': evaluation.id,
            'evaluation_title': evaluation.title,
            'session_id': session.id,
            'beneficiary_id': beneficiary_id,
            'score': session.score,
            'status': session.status,
            'started_at': session.started_at.isoformat() if session.started_at else None,
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'responses': ResponseSchema(many=True).dump(responses),
            'ai_feedback': AIFeedbackSchema(many=True).dump(ai_feedback) if ai_feedback else []
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get evaluation results error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@evaluations_bp.route('/<int:id>/analyze', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def analyze_evaluation(id):
    """Analyze evaluation results using AI."""
    try:
        # Get evaluation
        evaluation = evaluation_service.get_evaluation_by_id(id)
        
        if not evaluation:
            return jsonify({
                'error': 'not_found',
                'message': 'Evaluation not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or evaluation.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to analyze this evaluation'
                }), 403
        elif current_user.role == 'trainer':
            if evaluation.creator_id != current_user.id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to analyze this evaluation'
                }), 403
        
        # Get session to analyze
        session_id = request.json.get('session_id')
        if not session_id:
            return jsonify({
                'error': 'validation_error',
                'message': 'Session ID is required'
            }), 400
        
        # Perform AI analysis
        from app.services.ai import AIService
        from app.services import ResponseService
        
        # Get responses for the session
        responses = ResponseService.get_session_responses(session_id)
        
        # Prepare data for AI analysis
        response_data = []
        for response in responses:
            question = response.question
            response_data.append({
                'question': question.text,
                'question_type': question.question_type,
                'response': response.answer_text or response.answer_choice,
                'correct_answer': question.correct_answer
            })
        
        # Get AI analysis
        analysis = AIService.analyze_evaluation_responses(
            evaluation_title=evaluation.title,
            responses=response_data
        )
        
        # Save AI feedback
        from app.services import AIFeedbackService
        feedback = AIFeedbackService.create_feedback({
            'session_id': session_id,
            'feedback_type': 'evaluation_analysis',
            'content': analysis.get('summary', ''),
            'recommendations': analysis.get('recommendations', []),
            'strengths': analysis.get('strengths', []),
            'areas_for_improvement': analysis.get('areas_for_improvement', []),
            'confidence_score': analysis.get('confidence_score', 0.0)
        })
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'analysis': analysis,
            'feedback_id': feedback.id if feedback else None
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Analyze evaluation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500