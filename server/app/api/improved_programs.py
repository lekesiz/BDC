"""Improved programs API with dependency injection."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.core.improved_container import get_program_service
from app.services.interfaces.program_service_interface import IProgramService

improved_programs_bp = Blueprint('improved_programs', __name__)


@improved_programs_bp.route('/programs', methods=['POST'])
@jwt_required()
def create_program():
    """Create a new program endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'description', 'trainer_id']
        for field in required_fields:
            if field not in json_data:
                return jsonify({
                    'error': 'validation_error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Get current user
        current_user_id = get_jwt_identity()
        
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Create program
        result = program_service.create_program(
            name=json_data['name'],
            description=json_data['description'],
            trainer_id=json_data['trainer_id'],
            tenant_id=json_data.get('tenant_id'),
            **{k: v for k, v in json_data.items() if k not in ['name', 'description', 'trainer_id', 'tenant_id']}
        )
        
        if not result:
            return jsonify({
                'error': 'creation_failed',
                'message': 'Failed to create program'
            }), 500
        
        return jsonify(result), 201
    
    except Exception as e:
        current_app.logger.exception(f"Program creation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>', methods=['GET'])
@jwt_required()
def get_program(program_id):
    """Get program by ID endpoint with improved architecture."""
    try:
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Get program
        program = program_service.get_program(program_id)
        
        if not program:
            return jsonify({
                'error': 'not_found',
                'message': 'Program not found'
            }), 404
        
        return jsonify(program), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get program error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs', methods=['GET'])
@jwt_required()
def get_programs():
    """Get programs endpoint with improved architecture."""
    try:
        # Get query parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        trainer_id = request.args.get('trainer_id', type=int)
        tenant_id = request.args.get('tenant_id', type=int)
        category = request.args.get('category')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Get programs based on filters
        if trainer_id:
            programs = program_service.get_programs_by_trainer(trainer_id)
        elif tenant_id:
            programs = program_service.get_programs_by_tenant(tenant_id)
        elif category:
            programs = program_service.get_programs_by_category(category)
        elif active_only:
            programs = program_service.get_active_programs()
        else:
            programs = program_service.get_all_programs(limit=limit, offset=offset)
        
        return jsonify({
            'programs': programs,
            'count': len(programs)
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get programs error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>', methods=['PUT'])
@jwt_required()
def update_program(program_id):
    """Update program endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Update program
        result = program_service.update_program(program_id, **json_data)
        
        if not result:
            return jsonify({
                'error': 'update_failed',
                'message': 'Failed to update program or program not found'
            }), 404
        
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Update program error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>', methods=['DELETE'])
@jwt_required()
def delete_program(program_id):
    """Delete program endpoint with improved architecture."""
    try:
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Delete program
        success = program_service.delete_program(program_id)
        
        if not success:
            return jsonify({
                'error': 'delete_failed',
                'message': 'Failed to delete program or program not found'
            }), 404
        
        return jsonify({
            'message': 'Program deleted successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Delete program error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>/activate', methods=['POST'])
@jwt_required()
def activate_program(program_id):
    """Activate program endpoint with improved architecture."""
    try:
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Activate program
        success = program_service.activate_program(program_id)
        
        if not success:
            return jsonify({
                'error': 'activation_failed',
                'message': 'Failed to activate program or program not found'
            }), 404
        
        return jsonify({
            'message': 'Program activated successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Activate program error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_program(program_id):
    """Deactivate program endpoint with improved architecture."""
    try:
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Deactivate program
        success = program_service.deactivate_program(program_id)
        
        if not success:
            return jsonify({
                'error': 'deactivation_failed',
                'message': 'Failed to deactivate program or program not found'
            }), 404
        
        return jsonify({
            'message': 'Program deactivated successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Deactivate program error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_beneficiary(program_id):
    """Enroll beneficiary in program endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data or 'beneficiary_id' not in json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Beneficiary ID is required'
            }), 400
        
        beneficiary_id = json_data['beneficiary_id']
        
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Enroll beneficiary
        success = program_service.enroll_beneficiary(program_id, beneficiary_id)
        
        if not success:
            return jsonify({
                'error': 'enrollment_failed',
                'message': 'Failed to enroll beneficiary or already enrolled'
            }), 400
        
        return jsonify({
            'message': 'Beneficiary enrolled successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Enroll beneficiary error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>/unenroll', methods=['POST'])
@jwt_required()
def unenroll_beneficiary(program_id):
    """Unenroll beneficiary from program endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data or 'beneficiary_id' not in json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Beneficiary ID is required'
            }), 400
        
        beneficiary_id = json_data['beneficiary_id']
        
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Unenroll beneficiary
        success = program_service.unenroll_beneficiary(program_id, beneficiary_id)
        
        if not success:
            return jsonify({
                'error': 'unenrollment_failed',
                'message': 'Failed to unenroll beneficiary or not enrolled'
            }), 400
        
        return jsonify({
            'message': 'Beneficiary unenrolled successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Unenroll beneficiary error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>/enrollments', methods=['GET'])
@jwt_required()
def get_program_enrollments(program_id):
    """Get program enrollments endpoint with improved architecture."""
    try:
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Get enrollments
        enrollments = program_service.get_program_enrollments(program_id)
        
        return jsonify({
            'enrollments': enrollments,
            'count': len(enrollments)
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get program enrollments error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@improved_programs_bp.route('/programs/<int:program_id>/statistics', methods=['GET'])
@jwt_required()
def get_program_statistics(program_id):
    """Get program statistics endpoint with improved architecture."""
    try:
        # Get program service through dependency injection
        program_service: IProgramService = get_program_service()
        
        # Get statistics
        statistics = program_service.get_program_statistics(program_id)
        
        if not statistics:
            return jsonify({
                'error': 'not_found',
                'message': 'Program not found'
            }), 404
        
        return jsonify(statistics), 200
    
    except Exception as e:
        current_app.logger.exception(f"Get program statistics error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500