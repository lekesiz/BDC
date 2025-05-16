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
from app.services import (
    EvaluationService, QuestionService, TestSessionService, 
    ResponseService, AIFeedbackService
)
from app.middleware.request_context import auth_required, role_required
from app.utils import cache_response


evaluations_bp = Blueprint('evaluations', __name__)

# Import additional endpoints
from app.api.evaluations_endpoints import register_additional_routes
register_additional_routes(evaluations_bp)


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
            beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
            beneficiary_id = beneficiary.id if beneficiary else None
            if not beneficiary_id:
                return jsonify({
                    'error': 'beneficiary_required',
                    'message': 'Student must have a beneficiary profile'
                }), 400
        
        # Get evaluations
        evaluations, total, pages = EvaluationService.get_evaluations(
            tenant_id=tenant_id,
            creator_id=creator_id,
            beneficiary_id=beneficiary_id,
            status=status,
            type=type,
            is_template=is_template,
            page=page,
            per_page=per_page
        )
        
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
        evaluation = EvaluationService.get_evaluation(id)
        
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
        
        # Get questions
        questions, _, _ = QuestionService.get_questions(evaluation.id, per_page=100)
        
        # Serialize data
        schema = EvaluationSchema()
        result = schema.dump(evaluation)
        
        # Add questions to the result
        question_schema = QuestionSchema(many=True)
        result['questions'] = question_schema.dump(questions)
        
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
        evaluation = EvaluationService.create_evaluation(current_user.id, data)
        
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
        evaluation = EvaluationService.get_evaluation(id)
        
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
        updated_evaluation = EvaluationService.update_evaluation(id, data)
        
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
        evaluation = EvaluationService.get_evaluation(id)
        
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
        success = EvaluationService.delete_evaluation(id)
        
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
        evaluation = EvaluationService.get_evaluation(evaluation_id)
        
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
        evaluation = EvaluationService.get_evaluation(evaluation_id)
        
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
        evaluation = EvaluationService.get_evaluation(question.evaluation_id)
        
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
        evaluation = EvaluationService.get_evaluation(question.evaluation_id)
        
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
                evaluation = EvaluationService.get_evaluation(evaluation_id)
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
                evaluation = EvaluationService.get_evaluation(evaluation_id)
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