"""Users API."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import time

from app.extensions import db, logger, limiter
from app.schemas import UserSchema, UserCreateSchema, UserUpdateSchema, UserProfileSchema
from app.models import User
from app.middleware.request_context import admin_required, role_required


users_bp = Blueprint('users', __name__)


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': 'User not found'
            }), 404
        
        # Serialize user data
        schema = UserProfileSchema()
        user_data = schema.dump(user)
        
        return jsonify(user_data), 200
    
    except Exception as e:
        logger.exception(f"Get current user error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def get_users():
    """Get all users."""
    try:
        # Get query parameters with both naming conventions for compatibility
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', request.args.get('limit', 10, type=int))
        role = request.args.get('role')
        # Dikkat: is_active parametresini parse ederken None kontrolü yapıyoruz
        is_active_param = request.args.get('is_active')
        if is_active_param is not None:
            is_active = is_active_param.lower() == 'true'
        else:
            is_active = None
        
        # status parametresi (frontend'den geliyor olabilir)
        status = request.args.get('status')
        tenant_id = request.args.get('tenant_id', type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_direction = request.args.get('sort_direction', 'desc')
        
        # Build query
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        # is_active filtresi - varsayılan olarak sadece aktif kullanıcıları göster
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        elif status:
            # Frontend'den status parametresi gelirse
            if status == 'active':
                query = query.filter_by(is_active=True)
            elif status == 'inactive':
                query = query.filter_by(is_active=False)
        else:
            # Hiçbir filtre yoksa varsayılan olarak sadece aktif kullanıcıları göster
            query = query.filter_by(is_active=True)
            
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        # Apply sorting
        sort_attr = getattr(User, sort_by, None)
        if sort_attr:
            if sort_direction.lower() == 'desc':
                query = query.order_by(sort_attr.desc())
            else:
                query = query.order_by(sort_attr.asc())
        
        # Paginate query
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Serialize data
        schema = UserSchema(many=True)
        users = schema.dump(pagination.items)
        
        # Return paginated response
        return jsonify({
            'items': users,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'filters': {
                'is_active': is_active,
                'status': status,
                'role': role,
                'show_inactive': is_active is False or status == 'inactive'
            }
        }), 200
    
    except Exception as e:
        logger.exception(f"Get users error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/profile-picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    """Upload profile picture."""
    try:
        from werkzeug.utils import secure_filename
        import os
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Check if the post request has the file part
        if 'profile_picture' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['profile_picture']
        
        # If user does not select file, browser also submits an empty part
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Get allowed extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
        if file and allowed_file(file.filename):
            # Create secure filename
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename = f"{user_id}_{timestamp}_{filename}"
            
            # Save file
            upload_folder = current_app.config['UPLOAD_FOLDER']
            profile_pictures_folder = os.path.join(upload_folder, 'profile_pictures')
            
            # Create directory if it doesn't exist
            if not os.path.exists(profile_pictures_folder):
                os.makedirs(profile_pictures_folder)
            
            file_path = os.path.join(profile_pictures_folder, filename)
            file.save(file_path)
            
            # Update user's profile picture URL
            user.profile_picture = f'/uploads/profile_pictures/{filename}'
            db.session.commit()
            
            return jsonify({
                'message': 'Profile picture uploaded successfully',
                'profile_picture': user.profile_picture
            }), 200
        else:
            return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg, gif'}), 400
    
    except Exception as e:
        logger.exception(f"Upload profile picture error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': 'User not found'
            }), 404
        
        # Serialize data
        schema = UserSchema()
        user_data = schema.dump(user)
        
        return jsonify(user_data), 200
    
    except Exception as e:
        logger.exception(f"Get user error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def create_user():
    """Create a new user."""
    try:
        # Get request data
        data = request.get_json()
        
        # Validate data
        schema = UserCreateSchema()
        validated_data = schema.load(data)
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=validated_data['email']).first()
        if existing_user:
            return jsonify({
                'error': 'already_exists',
                'message': 'User with this email already exists'
            }), 409
        
        # Remove confirm_password and any non-model fields before creating user
        validated_data.pop('confirm_password', None)
        validated_data.pop('status', None)  # Frontend'in gönderdiği fazladan alan
        
        # Create new user with only valid model fields
        user_data = {
            'email': validated_data['email'],
            'password': validated_data['password'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'role': validated_data['role'],
            'phone': validated_data.get('phone'),
            'organization': validated_data.get('organization'),
            'tenant_id': validated_data.get('tenant_id'),
            'is_active': True
        }
        
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        
        # Serialize response
        response_schema = UserSchema()
        user_data = response_schema.dump(user)
        
        return jsonify({
            'message': 'User created successfully',
            'user': user_data
        }), 201
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Invalid data provided',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        logger.exception(f"Create user error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': f'Error: {str(e)}'  # Debug için detaylı hata mesajı
        }), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update a user."""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Get user to update
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': 'User not found'
            }), 404
        
        # Check permissions
        if current_user.role not in ['super_admin', 'tenant_admin'] and current_user_id != user_id:
            return jsonify({
                'error': 'forbidden',
                'message': 'You do not have permission to update this user'
            }), 403
        
        # Get request data
        data = request.get_json()
        
        # Validate data with user_id context for email validation
        schema = UserUpdateSchema(context={'user_id': user_id})
        validated_data = schema.load(data)
        
        # Handle special fields
        if 'status' in validated_data:
            # Map frontend status to backend is_active
            user.is_active = validated_data.pop('status') == 'active'
        
        if 'password' in validated_data:
            # Update password using the property setter
            user.password = validated_data.pop('password')
        
        # Update other fields
        for key, value in validated_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        
        # Serialize response
        response_schema = UserSchema()
        user_data = response_schema.dump(user)
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user_data
        }), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Invalid data provided',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        logger.exception(f"Update user error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def delete_user(user_id):
    """Delete a user."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': 'User not found'
            }), 404
        
        # Soft delete the user (sadece pasif yap)
        user.is_active = False
        db.session.commit()
        
        # Gerçek silme için (opsiyonel - query param ile kontrol edilebilir):
        # if request.args.get('hard_delete', 'false').lower() == 'true':
        #     db.session.delete(user)
        #     db.session.commit()
        
        return jsonify({
            'message': 'User deactivated successfully'  # Daha açıklayıcı mesaj
        }), 200
    
    except Exception as e:
        logger.exception(f"Delete user error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/<int:user_id>/profile', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """Get user profile."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'not_found',
                'message': 'User not found'
            }), 404
        
        # Serialize data with profile schema
        schema = UserProfileSchema()
        profile_data = schema.dump(user)
        
        return jsonify(profile_data), 200
    
    except Exception as e:
        logger.exception(f"Get user profile error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500

