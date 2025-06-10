"""Users API."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import time

from app.extensions import db, logger, limiter
from app.schemas import UserSchema, UserCreateSchema, UserUpdateSchema, UserProfileSchema
from app.models import User
from app.middleware.request_context import admin_required, role_required
from app.middleware.i18n_middleware import i18n_response

from app.utils.logging import logger


users_bp = Blueprint('users', __name__)


@users_bp.route('/me', methods=['GET'])
@jwt_required()
@i18n_response
def get_current_user():
    """Get current authenticated user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': '$t:api.user.not_found'
            }), 404
        
        # Serialize user data
        schema = UserProfileSchema()
        user_data = schema.dump(user)
        
        return jsonify(user_data), 200
    
    except Exception as e:
        logger.exception(f"Get current user error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@users_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
@i18n_response
def get_users():
    """Get all users (admin only)."""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get filters
        role = request.args.get('role')
        status = request.args.get('status')
        search = request.args.get('search')
        
        # Build query
        query = User.query
        
        # Apply filters
        if role:
            query = query.filter_by(role=role)
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(
                db.or_(
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        # Get current user's tenant_id for filtering
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Filter by tenant for tenant admins
        if current_user.role == 'tenant_admin':
            query = query.filter_by(tenant_id=current_user.tenant_id)
        
        # Paginate
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Serialize data
        schema = UserSchema(many=True)
        users = schema.dump(paginated.items)
        
        return jsonify({
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200
    
    except Exception as e:
        logger.exception(f"Get users error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@i18n_response
def get_user(user_id):
    """Get a specific user."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': '$t:api.user.not_found'
            }), 404
        
        # Check permissions
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Allow users to see their own profile
        if current_user_id != user_id:
            # Check admin permissions
            if current_user.role not in ['super_admin', 'tenant_admin']:
                return jsonify({
                    'error': 'forbidden',
                    'message': '$t:api.error.forbidden'
                }), 403
            
            # Tenant admins can only see users in their tenant
            if current_user.role == 'tenant_admin' and user.tenant_id != current_user.tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': '$t:api.error.forbidden'
                }), 403
        
        # Serialize user data
        schema = UserSchema()
        user_data = schema.dump(user)
        
        return jsonify(user_data), 200
    
    except Exception as e:
        logger.exception(f"Get user error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@users_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
@i18n_response
def create_user():
    """Create a new user (admin only)."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': '$t:api.validation.request_empty'
            }), 400
        
        # Validate request data
        schema = UserCreateSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': '$t:api.error.validation',
                'errors': e.messages
            }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'error': 'conflict',
                'message': '$t:api.user.email_exists'
            }), 409
        
        # Get current user for tenant assignment
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Set tenant_id for tenant admins
        if current_user.role == 'tenant_admin':
            data['tenant_id'] = current_user.tenant_id
        
        # Create user
        user = User(**data)
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Serialize user data
        schema = UserSchema()
        user_data = schema.dump(user)
        
        return jsonify({
            'message': '$t:api.user.created',
            'user': user_data
        }), 201
    
    except Exception as e:
        logger.exception(f"Create user error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@i18n_response
def update_user(user_id):
    """Update a user."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': '$t:api.user.not_found'
            }), 404
        
        # Check permissions
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Allow users to update their own profile
        if current_user_id != user_id:
            # Check admin permissions
            if current_user.role not in ['super_admin', 'tenant_admin']:
                return jsonify({
                    'error': 'forbidden',
                    'message': '$t:api.error.forbidden'
                }), 403
            
            # Tenant admins can only update users in their tenant
            if current_user.role == 'tenant_admin' and user.tenant_id != current_user.tenant_id:
                return jsonify({
                    'error': 'forbidden',
                    'message': '$t:api.error.forbidden'
                }), 403
        
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': '$t:api.validation.request_empty'
            }), 400
        
        # Validate request data
        schema = UserUpdateSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': '$t:api.error.validation',
                'errors': e.messages
            }), 400
        
        # Check if email is being changed and already exists
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({
                    'error': 'conflict',
                    'message': '$t:api.user.email_exists'
                }), 409
        
        # Update user fields
        for key, value in data.items():
            if key != 'password':  # Handle password separately
                setattr(user, key, value)
        
        # Update password if provided
        if 'password' in data:
            user.set_password(data['password'])
        
        user.updated_at = db.func.now()
        db.session.commit()
        
        # Serialize user data
        schema = UserSchema()
        user_data = schema.dump(user)
        
        return jsonify({
            'message': '$t:api.user.updated',
            'user': user_data
        }), 200
    
    except Exception as e:
        logger.exception(f"Update user error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
@i18n_response
def delete_user(user_id):
    """Delete a user (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': '$t:api.user.not_found'
            }), 404
        
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Prevent self-deletion
        if current_user_id == user_id:
            return jsonify({
                'error': 'forbidden',
                'message': '$t:api.user.cannot_delete_self'
            }), 403
        
        # Tenant admins can only delete users in their tenant
        if current_user.role == 'tenant_admin' and user.tenant_id != current_user.tenant_id:
            return jsonify({
                'error': 'forbidden',
                'message': '$t:api.error.forbidden'
            }), 403
        
        # Soft delete
        user.status = 'deleted'
        user.deleted_at = db.func.now()
        db.session.commit()
        
        return jsonify({
            'message': '$t:api.user.deleted'
        }), 200
    
    except Exception as e:
        logger.exception(f"Delete user error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@users_bp.route('/<int:user_id>/activate', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
@i18n_response
def activate_user(user_id):
    """Activate a user (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': '$t:api.user.not_found'
            }), 404
        
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Tenant admins can only activate users in their tenant
        if current_user.role == 'tenant_admin' and user.tenant_id != current_user.tenant_id:
            return jsonify({
                'error': 'forbidden',
                'message': '$t:api.error.forbidden'
            }), 403
        
        # Activate user
        user.status = 'active'
        user.updated_at = db.func.now()
        db.session.commit()
        
        return jsonify({
            'message': '$t:api.user.activated'
        }), 200
    
    except Exception as e:
        logger.exception(f"Activate user error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@users_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
@i18n_response
def deactivate_user(user_id):
    """Deactivate a user (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': '$t:api.user.not_found'
            }), 404
        
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Prevent self-deactivation
        if current_user_id == user_id:
            return jsonify({
                'error': 'forbidden',
                'message': '$t:api.user.cannot_deactivate_self'
            }), 403
        
        # Tenant admins can only deactivate users in their tenant
        if current_user.role == 'tenant_admin' and user.tenant_id != current_user.tenant_id:
            return jsonify({
                'error': 'forbidden',
                'message': '$t:api.error.forbidden'
            }), 403
        
        # Deactivate user
        user.status = 'inactive'
        user.updated_at = db.func.now()
        db.session.commit()
        
        return jsonify({
            'message': '$t:api.user.deactivated'
        }), 200
    
    except Exception as e:
        logger.exception(f"Deactivate user error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@users_bp.route('/<int:user_id>/change-role', methods=['POST'])
@jwt_required()
@role_required(['super_admin'])
@i18n_response
def change_user_role(user_id):
    """Change user role (super admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': '$t:api.user.not_found'
            }), 404
        
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data or 'role' not in json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': '$t:api.validation.field_required',
                'field': 'role'
            }), 400
        
        new_role = json_data['role']
        
        # Validate role
        valid_roles = ['super_admin', 'tenant_admin', 'trainer', 'trainee']
        if new_role not in valid_roles:
            return jsonify({
                'error': 'validation_error',
                'message': '$t:api.validation.invalid_role'
            }), 400
        
        # Update role
        user.role = new_role
        user.updated_at = db.func.now()
        db.session.commit()
        
        return jsonify({
            'message': '$t:api.user.role_changed'
        }), 200
    
    except Exception as e:
        logger.exception(f"Change user role error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500