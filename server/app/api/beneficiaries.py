"""Beneficiaries API."""

from flask import Blueprint, request, jsonify, current_app, send_from_directory, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from marshmallow import ValidationError
import os
from werkzeug.utils import secure_filename
from io import BytesIO

from app.extensions import db
from app.schemas import (
    BeneficiarySchema, BeneficiaryCreateSchema, BeneficiaryUpdateSchema,
    NoteSchema, NoteCreateSchema, NoteUpdateSchema,
    AppointmentSchema, AppointmentCreateSchema, AppointmentUpdateSchema,
    DocumentSchema, DocumentCreateSchema, DocumentUpdateSchema,
    EvaluationSchema
)
from app.services import (
    BeneficiaryService, NoteService, AppointmentService, DocumentService
)
from app.models import Beneficiary, Evaluation, TestSession, Document, Note
from app.middleware.request_context import auth_required, role_required
from app.utils import cache_response


beneficiaries_bp = Blueprint('beneficiaries', __name__)


@beneficiaries_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
@cache_response(timeout=300, key_prefix='beneficiaries')
def get_beneficiaries():
    """Get all beneficiaries with optional filtering."""
    try:
        # Get query parameters
        tenant_id = request.args.get('tenant_id', type=int)
        trainer_id = request.args.get('trainer_id', type=int)
        status = request.args.get('status')
        query = request.args.get('query')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by')
        sort_dir = request.args.get('sort_dir')
        
        # Apply role-based filtering
        if current_user.role == 'tenant_admin':
            # Tenant admins can only see beneficiaries from their tenant
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id:
                return jsonify({
                    'error': 'tenant_required',
                    'message': 'Tenant admin must belong to a tenant'
                }), 400
        elif current_user.role == 'trainer':
            # Trainers can only see their assigned beneficiaries
            trainer_id = current_user.id
        
        # Get beneficiaries
        beneficiaries, total, pages = BeneficiaryService.get_beneficiaries(
            tenant_id=tenant_id,
            trainer_id=trainer_id,
            status=status,
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
        
        # Serialize data
        schema = BeneficiarySchema(many=True)
        result = schema.dump(beneficiaries)
        
        # Return paginated response
        return jsonify({
            'items': result,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get beneficiaries error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@cache_response(timeout=300, key_prefix='beneficiary')
def get_beneficiary(id):
    """Get a beneficiary by ID."""
    try:
        # Get beneficiary
        beneficiary = BeneficiaryService.get_beneficiary(id)
        
        if not beneficiary:
            return jsonify({
                'error': 'not_found',
                'message': 'Beneficiary not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'trainer' and beneficiary.trainer_id != current_user.id:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to access this beneficiary'
            }), 403
        
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to access this beneficiary'
                }), 403
        
        if current_user.role == 'student' and current_user.id != beneficiary.user_id:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to access this beneficiary'
            }), 403
        
        # Serialize data
        schema = BeneficiarySchema()
        result = schema.dump(beneficiary)
        
        # Return beneficiary
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get beneficiary error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_beneficiary_details(id):
    """Update a beneficiary."""
    try:
        # Get beneficiary
        beneficiary = BeneficiaryService.get_beneficiary(id)
        
        if not beneficiary:
            return jsonify({
                'error': 'not_found',
                'message': 'Beneficiary not found'
            }), 404
        
        # Check permissions
        current_user_id = get_jwt_identity()
        
        if current_user.role == 'student' and current_user.id != beneficiary.user_id:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to update this beneficiary'
            }), 403
        
        if current_user.role == 'trainer' and beneficiary.trainer_id != current_user.id:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to update this beneficiary'
            }), 403
        
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to update this beneficiary'
                }), 403
        
        # Get request data
        data = request.get_json()
        
        # Validate request data
        update_schema = BeneficiaryUpdateSchema()
        validated_data = update_schema.load(data)
        
        # Update beneficiary
        updated_beneficiary = BeneficiaryService.update_beneficiary(id, validated_data)
        
        if not updated_beneficiary:
            return jsonify({
                'error': 'update_failed',
                'message': 'Failed to update beneficiary'
            }), 400
        
        # Serialize data
        schema = BeneficiarySchema()
        result = schema.dump(updated_beneficiary)
        
        # Return updated beneficiary
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Update beneficiary error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def create_beneficiary():
    """Create a new beneficiary."""
    try:
        # Validate request data
        request_data = request.json.copy()
        
        # If no password provided, generate a random one
        if not request_data.get('password'):
            import secrets
            request_data['password'] = secrets.token_urlsafe(16)
            request_data['confirm_password'] = request_data['password']
        
        schema = BeneficiaryCreateSchema(context={'password': request_data.get('password')})
        data = schema.load(request_data)
        
        # Handle tenant_id
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id:
                return jsonify({
                    'error': 'tenant_required',
                    'message': 'Tenant admin must belong to a tenant'
                }), 400
            
            # Override tenant_id with the admin's tenant
            data['tenant_id'] = tenant_id
        elif current_user.role == 'super_admin':
            # For super admin, use the provided tenant_id or the user's tenant
            if not data.get('tenant_id'):
                tenant_id = current_user.tenants[0].id if current_user.tenants else None
                if not tenant_id:
                    # Get the first tenant if no tenant specified
                    from app.models import Tenant
                    first_tenant = Tenant.query.first()
                    if first_tenant:
                        data['tenant_id'] = first_tenant.id
                    else:
                        return jsonify({
                            'error': 'tenant_required',
                            'message': 'No tenant exists in the system'
                        }), 400
                else:
                    data['tenant_id'] = tenant_id
        
        # Extract user data
        user_data = {
            'email': data.pop('email'),
            'password': data.pop('password'),
            'first_name': data.pop('first_name'),
            'last_name': data.pop('last_name')
        }
        
        # Create beneficiary
        beneficiary = BeneficiaryService.create_beneficiary(user_data, data)
        
        if not beneficiary:
            return jsonify({
                'error': 'creation_failed',
                'message': 'Failed to create beneficiary'
            }), 400
        
        # Serialize data
        response_schema = BeneficiarySchema()
        result = response_schema.dump(beneficiary)
        
        # Return created beneficiary
        return jsonify(result), 201
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        current_app.logger.exception(f"Create beneficiary error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def update_beneficiary(id):
    """Update a beneficiary."""
    try:
        # Get beneficiary
        beneficiary = BeneficiaryService.get_beneficiary(id)
        
        if not beneficiary:
            return jsonify({
                'error': 'not_found',
                'message': 'Beneficiary not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'trainer' and beneficiary.trainer_id != current_user.id:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to update this beneficiary'
            }), 403
        
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to update this beneficiary'
                }), 403
        
        # Validate request data
        schema = BeneficiaryUpdateSchema()
        data = schema.load(request.json)
        
        # Update beneficiary
        updated_beneficiary = BeneficiaryService.update_beneficiary(id, data)
        
        if not updated_beneficiary:
            return jsonify({
                'error': 'update_failed',
                'message': 'Failed to update beneficiary'
            }), 400
        
        # Serialize data
        response_schema = BeneficiarySchema()
        result = response_schema.dump(updated_beneficiary)
        
        # Return updated beneficiary
        return jsonify(result), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        current_app.logger.exception(f"Update beneficiary error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def delete_beneficiary(id):
    """Delete a beneficiary."""
    try:
        # Get beneficiary
        beneficiary = BeneficiaryService.get_beneficiary(id)
        
        if not beneficiary:
            return jsonify({
                'error': 'not_found',
                'message': 'Beneficiary not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to delete this beneficiary'
                }), 403
        
        # Delete beneficiary
        success = BeneficiaryService.delete_beneficiary(id)
        
        if not success:
            return jsonify({
                'error': 'deletion_failed',
                'message': 'Failed to delete beneficiary'
            }), 400
        
        # Return success response
        return jsonify({
            'message': 'Beneficiary deleted successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Delete beneficiary error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/<int:id>/trainers', methods=['GET'])
@jwt_required()
def get_beneficiary_trainers(id):
    """Get trainers assigned to a beneficiary."""
    try:
        # Get beneficiary
        beneficiary = BeneficiaryService.get_beneficiary(id)
        
        if not beneficiary:
            return jsonify({
                'error': 'not_found',
                'message': 'Beneficiary not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to view this beneficiary'
                }), 403
        
        # Get trainer information
        if beneficiary.trainer:
            trainers = [{
                'id': beneficiary.trainer.id,
                'email': beneficiary.trainer.email,
                'first_name': beneficiary.trainer.first_name,
                'last_name': beneficiary.trainer.last_name,
                'role': beneficiary.trainer.role
            }]
        else:
            trainers = []
        
        return jsonify(trainers), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get beneficiary trainers error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/<int:id>/assign-trainer', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def assign_trainer(id):
    """Assign a trainer to a beneficiary."""
    try:
        # Get beneficiary
        beneficiary = BeneficiaryService.get_beneficiary(id)
        
        if not beneficiary:
            return jsonify({
                'error': 'not_found',
                'message': 'Beneficiary not found'
            }), 404
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to assign a trainer to this beneficiary'
                }), 403
        
        # Validate request data
        trainer_id = request.json.get('trainer_id')
        
        if trainer_id is None:
            return jsonify({
                'error': 'validation_error',
                'message': 'Trainer ID is required'
            }), 400
        
        # Assign trainer
        updated_beneficiary = BeneficiaryService.assign_trainer(id, trainer_id)
        
        if not updated_beneficiary:
            return jsonify({
                'error': 'assign_failed',
                'message': 'Failed to assign trainer'
            }), 400
        
        # Serialize data
        schema = BeneficiarySchema()
        result = schema.dump(updated_beneficiary)
        
        # Return updated beneficiary
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Assign trainer error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


# Evaluations endpoints
@beneficiaries_bp.route('/<int:id>/evaluations', methods=['GET'])
@jwt_required()
def get_beneficiary_evaluations(id):
    """Get evaluations for a beneficiary."""
    try:
        beneficiary = Beneficiary.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden'}), 403
        
        evaluations = Evaluation.query.filter_by(beneficiary_id=id).all()
        schema = EvaluationSchema(many=True)
        
        return jsonify({
            'evaluations': schema.dump(evaluations),
            'total': len(evaluations),
            'completed': sum(1 for e in evaluations if e.status == 'completed')
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get evaluations error: {str(e)}")
        return jsonify({'error': 'server_error'}), 500


# Sessions endpoints
@beneficiaries_bp.route('/<int:id>/sessions', methods=['GET'])
@jwt_required()
def get_beneficiary_sessions(id):
    """Get sessions for a beneficiary."""
    try:
        beneficiary = Beneficiary.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden'}), 403
        
        sessions = TestSession.query.filter_by(beneficiary_id=id).all()
        
        return jsonify({
            'sessions': [{
                'id': s.id,
                'evaluation_id': s.evaluation_id,
                'start_time': s.start_time.isoformat() if s.start_time else None,
                'end_time': s.end_time.isoformat() if s.end_time else None,
                'status': s.status,
                'score': s.score,
                'duration': s.duration,
                'created_at': s.created_at.isoformat()
            } for s in sessions],
            'total': len(sessions)
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get sessions error: {str(e)}")
        return jsonify({'error': 'server_error'}), 500


# Progress endpoints
@beneficiaries_bp.route('/<int:id>/progress', methods=['GET'])
@jwt_required()
def get_beneficiary_progress(id):
    """Get progress overview for a beneficiary."""
    try:
        beneficiary = Beneficiary.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden'}), 403
        
        # Calculate progress metrics
        evaluations = Evaluation.query.filter_by(beneficiary_id=id).all()
        sessions = TestSession.query.filter_by(beneficiary_id=id).all()
        
        completed_evaluations = [e for e in evaluations if e.status == 'completed']
        avg_score = sum(s.score for s in sessions if s.score) / len(sessions) if sessions else 0
        
        return jsonify({
            'overview': {
                'total_evaluations': len(evaluations),
                'completed_evaluations': len(completed_evaluations),
                'in_progress_evaluations': len([e for e in evaluations if e.status == 'in_progress']),
                'total_sessions': len(sessions),
                'average_score': round(avg_score, 2),
                'completion_rate': round(len(completed_evaluations) / len(evaluations) * 100, 2) if evaluations else 0
            },
            'recent_activity': [{
                'type': 'evaluation',
                'title': e.title,
                'date': e.created_at.isoformat(),
                'status': e.status
            } for e in evaluations[:5]]
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get progress error: {str(e)}")
        return jsonify({'error': 'server_error'}), 500


# Skills endpoints  
@beneficiaries_bp.route('/<int:id>/skills', methods=['GET'])
@jwt_required()
def get_beneficiary_skills(id):
    """Get skills assessment for a beneficiary."""
    try:
        beneficiary = Beneficiary.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden'}), 403
        
        # Mock skills data for now
        skills = [
            {'name': 'Communication', 'level': 75, 'trend': 'up'},
            {'name': 'Problem Solving', 'level': 85, 'trend': 'stable'},
            {'name': 'Leadership', 'level': 60, 'trend': 'up'},
            {'name': 'Teamwork', 'level': 90, 'trend': 'stable'},
            {'name': 'Time Management', 'level': 70, 'trend': 'down'}
        ]
        
        return jsonify({
            'skills': skills,
            'last_assessment': '2024-01-15',
            'next_assessment': '2024-02-15'
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get skills error: {str(e)}")
        return jsonify({'error': 'server_error'}), 500


# Documents endpoints
@beneficiaries_bp.route('/<int:id>/documents', methods=['GET'])
@jwt_required()
def get_beneficiary_documents(id):
    """Get documents for a beneficiary."""
    try:
        beneficiary = Beneficiary.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden'}), 403
        
        documents = Document.query.filter_by(beneficiary_id=id).all()
        schema = DocumentSchema(many=True)
        
        return jsonify({
            'documents': schema.dump(documents),
            'total': len(documents)
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get documents error: {str(e)}")
        return jsonify({'error': 'server_error'}), 500


# Profile picture endpoint
@beneficiaries_bp.route('/<int:id>/profile-picture', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def upload_profile_picture(id):
    """Upload profile picture for a beneficiary."""
    try:
        beneficiary = Beneficiary.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden'}), 403
        
        if 'profile_picture' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['profile_picture']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_pictures')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        filename = secure_filename(f"beneficiary_{id}_{file.filename}")
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Update beneficiary's user profile picture path
        beneficiary.user.profile_picture = f"profile_pictures/{filename}"
        db.session.commit()
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'path': f"profile_pictures/{filename}"
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Upload profile picture error: {str(e)}")
        return jsonify({'error': 'server_error'}), 500


# Comparison endpoint
@beneficiaries_bp.route('/<int:id>/comparison', methods=['GET'])
@jwt_required()
def get_beneficiary_comparison(id):
    """Get comparison data for a beneficiary."""
    try:
        beneficiary = Beneficiary.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden'}), 403
        
        # Mock comparison data
        return jsonify({
            'comparison': {
                'average_score': {
                    'beneficiary': 85,
                    'cohort': 78,
                    'benchmark': 82
                },
                'completion_rate': {
                    'beneficiary': 90,
                    'cohort': 85,
                    'benchmark': 88
                },
                'skills': {
                    'communication': {'beneficiary': 75, 'cohort': 72},
                    'leadership': {'beneficiary': 85, 'cohort': 80},
                    'problem_solving': {'beneficiary': 90, 'cohort': 83}
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get comparison error: {str(e)}")
        return jsonify({'error': 'server_error'}), 500


# Report generation endpoint
@beneficiaries_bp.route('/<int:id>/report', methods=['GET'])
@jwt_required()
def generate_beneficiary_report(id):
    """Generate a report for a beneficiary."""
    try:
        beneficiary = Beneficiary.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if not tenant_id or beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden'}), 403
        
        # Mock PDF report generation
        from io import BytesIO
        pdf_buffer = BytesIO()
        pdf_buffer.write(b"Mock PDF Report Content")
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'beneficiary_report_{id}.pdf'
        )
        
    except Exception as e:
        current_app.logger.exception(f"Generate report error: {str(e)}")
        return jsonify({'error': 'server_error'}), 500


# Notes endpoints

@beneficiaries_bp.route('/<int:beneficiary_id>/notes', methods=['GET'])
@jwt_required()
def get_notes(beneficiary_id):
    """Get notes for a beneficiary."""
    try:
        # Get beneficiary
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        
        if not beneficiary:
            return jsonify({
                'error': 'not_found',
                'message': 'Beneficiary not found'
            }), 404
        
        # Check permissions
        can_access = False
        if current_user.role in ['super_admin']:
            can_access = True
        elif current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            can_access = tenant_id and beneficiary.tenant_id == tenant_id
        elif current_user.role == 'trainer':
            can_access = beneficiary.trainer_id == current_user.id
        elif current_user.role == 'student':
            can_access = beneficiary.user_id == current_user.id
        
        if not can_access:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to access notes for this beneficiary'
            }), 403
        
        # Get query parameters
        user_id = request.args.get('user_id', type=int)
        note_type = request.args.get('type')
        is_private = request.args.get('is_private', type=lambda v: v.lower() == 'true' if v else None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Students can only see their own non-private notes
        if current_user.role == 'student':
            is_private = False
        
        # Get notes
        notes, total, pages = NoteService.get_notes(
            beneficiary_id=beneficiary_id,
            user_id=user_id,
            type=note_type,
            is_private=is_private,
            page=page,
            per_page=per_page
        )
        
        # Serialize data
        schema = NoteSchema(many=True)
        result = schema.dump(notes)
        
        # Return paginated response
        return jsonify({
            'items': result,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get notes error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/notes', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def create_note(beneficiary_id):
    """Create a new note for a beneficiary."""
    try:
        # Get beneficiary
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        
        if not beneficiary:
            return jsonify({
                'error': 'not_found',
                'message': 'Beneficiary not found'
            }), 404
        
        # Check permissions
        can_access = False
        if current_user.role in ['super_admin']:
            can_access = True
        elif current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            can_access = tenant_id and beneficiary.tenant_id == tenant_id
        elif current_user.role == 'trainer':
            can_access = beneficiary.trainer_id == current_user.id
        
        if not can_access:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to create notes for this beneficiary'
            }), 403
        
        # Validate request data
        schema = NoteCreateSchema()
        data = schema.load(request.json)
        
        # Ensure beneficiary_id matches
        data['beneficiary_id'] = beneficiary_id
        
        # Create note
        note = NoteService.create_note(current_user.id, data)
        
        if not note:
            return jsonify({
                'error': 'creation_failed',
                'message': 'Failed to create note'
            }), 400
        
        # Serialize data
        response_schema = NoteSchema()
        result = response_schema.dump(note)
        
        # Return created note
        return jsonify(result), 201
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        current_app.logger.exception(f"Create note error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/notes/<int:note_id>', methods=['PATCH'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def update_note(note_id):
    """Update a note."""
    try:
        # Get note
        note = NoteService.get_note(note_id)
        
        if not note:
            return jsonify({
                'error': 'not_found',
                'message': 'Note not found'
            }), 404
        
        # Check permissions
        can_update = False
        if current_user.role in ['super_admin']:
            can_update = True
        elif current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            beneficiary = BeneficiaryService.get_beneficiary(note.beneficiary_id)
            can_update = tenant_id and beneficiary and beneficiary.tenant_id == tenant_id
        elif current_user.role == 'trainer':
            beneficiary = BeneficiaryService.get_beneficiary(note.beneficiary_id)
            can_update = beneficiary and beneficiary.trainer_id == current_user.id
        
        # Owner check (user who created the note)
        is_owner = note.user_id == current_user.id
        
        if not (can_update or is_owner):
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to update this note'
            }), 403
        
        # Validate request data
        schema = NoteUpdateSchema()
        data = schema.load(request.json)
        
        # Update note
        updated_note = NoteService.update_note(note_id, data)
        
        if not updated_note:
            return jsonify({
                'error': 'update_failed',
                'message': 'Failed to update note'
            }), 400
        
        # Serialize data
        response_schema = NoteSchema()
        result = response_schema.dump(updated_note)
        
        # Return updated note
        return jsonify(result), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        current_app.logger.exception(f"Update note error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@beneficiaries_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def delete_note(note_id):
    """Delete a note."""
    try:
        # Get note
        note = NoteService.get_note(note_id)
        
        if not note:
            return jsonify({
                'error': 'not_found',
                'message': 'Note not found'
            }), 404
        
        # Check permissions
        can_delete = False
        if current_user.role in ['super_admin']:
            can_delete = True
        elif current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            beneficiary = BeneficiaryService.get_beneficiary(note.beneficiary_id)
            can_delete = tenant_id and beneficiary and beneficiary.tenant_id == tenant_id
        elif current_user.role == 'trainer':
            beneficiary = BeneficiaryService.get_beneficiary(note.beneficiary_id)
            can_delete = beneficiary and beneficiary.trainer_id == current_user.id
        
        # Owner check (user who created the note)
        is_owner = note.user_id == current_user.id
        
        if not (can_delete or is_owner):
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to delete this note'
            }), 403
        
        # Delete note
        success = NoteService.delete_note(note_id)
        
        if not success:
            return jsonify({
                'error': 'deletion_failed',
                'message': 'Failed to delete note'
            }), 400
        
        # Return success response
        return jsonify({
            'message': 'Note deleted successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Delete note error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500