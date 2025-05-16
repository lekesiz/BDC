"""Users API."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db, logger
from app.schemas import UserSchema, UserCreateSchema, UserUpdateSchema, UserProfileSchema
from app.models import User
from app.middleware.request_context import admin_required, role_required


users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def get_users():
    """Get all users."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role = request.args.get('role')
        
        # Build query
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        # Paginate query
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Serialize data
        schema = UserSchema(many=True)
        users = schema.dump(pagination.items)
        
        # Return paginated response
        return jsonify({
            'items': users,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
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
        
        # Allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename to avoid collisions
            unique_filename = f"user_{user_id}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_path = os.path.join('app', 'static', 'uploads', 'profile_pictures')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Generate URL
            url = f"/static/uploads/profile_pictures/{unique_filename}"
            
            # Update user's profile picture
            user.profile_picture = url
            db.session.commit()
            
            return jsonify({'url': url}), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    """Get a user by ID."""
    try:
        # Get user identity
        current_user_id = get_jwt_identity()
        
        # Check if user is requesting their own data or has admin role
        user = User.query.get_or_404(id)
        
        if id != current_user_id:
            current_user = User.query.get(current_user_id)
            if current_user.role not in ['super_admin', 'tenant_admin']:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to access this resource'
                }), 403
        
        # Serialize data
        schema = UserSchema()
        user_data = schema.dump(user)
        
        # Return user data
        return jsonify(user_data), 200
    
    except Exception as e:
        logger.exception(f"Get user error: {str(e)}")
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
        
        # Allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename to avoid collisions
            unique_filename = f"user_{user_id}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_path = os.path.join('app', 'static', 'uploads', 'profile_pictures')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Generate URL
            url = f"/static/uploads/profile_pictures/{unique_filename}"
            
            # Update user's profile picture
            user.profile_picture = url
            db.session.commit()
            
            return jsonify({'url': url}), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """Create a new user."""
    try:
        # Validate request data
        schema = UserCreateSchema()
        data = schema.load(request.json)
        
        # Create user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role']
        )
        user.password = data['password']
        
        # Add user to tenant if tenant_id provided
        if 'tenant_id' in data:
            from app.models import Tenant
            tenant = Tenant.query.get_or_404(data['tenant_id'])
            user.tenants.append(tenant)
        
        # Save user
        db.session.add(user)
        db.session.commit()
        
        # Serialize data
        user_data = schema.dump(user)
        
        # Return created user
        return jsonify(user_data), 201
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Create user error: {str(e)}")
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
        
        # Allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename to avoid collisions
            unique_filename = f"user_{user_id}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_path = os.path.join('app', 'static', 'uploads', 'profile_pictures')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Generate URL
            url = f"/static/uploads/profile_pictures/{unique_filename}"
            
            # Update user's profile picture
            user.profile_picture = url
            db.session.commit()
            
            return jsonify({'url': url}), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
def update_user(id):
    """Update a user."""
    try:
        # Get user identity
        current_user_id = get_jwt_identity()
        
        # Check if user is updating their own data or has admin role
        user = User.query.get_or_404(id)
        
        if id != current_user_id:
            current_user = User.query.get(current_user_id)
            if current_user.role not in ['super_admin', 'tenant_admin']:
                return jsonify({
                    'error': 'forbidden',
                    'message': 'You do not have permission to update this user'
                }), 403
        
        # Validate request data
        schema = UserUpdateSchema(context={'user_id': id})
        data = schema.load(request.json)
        
        # Update user
        for key, value in data.items():
            setattr(user, key, value)
        
        # Save user
        db.session.commit()
        
        # Serialize data
        response_schema = UserSchema()
        user_data = response_schema.dump(user)
        
        # Return updated user
        return jsonify(user_data), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Update user error: {str(e)}")
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
        
        # Allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename to avoid collisions
            unique_filename = f"user_{user_id}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_path = os.path.join('app', 'static', 'uploads', 'profile_pictures')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Generate URL
            url = f"/static/uploads/profile_pictures/{unique_filename}"
            
            # Update user's profile picture
            user.profile_picture = url
            db.session.commit()
            
            return jsonify({'url': url}), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(id):
    """Delete a user."""
    try:
        # Check if user exists
        user = User.query.get_or_404(id)
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        # Return success response
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Delete user error: {str(e)}")
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
        
        # Allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename to avoid collisions
            unique_filename = f"user_{user_id}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_path = os.path.join('app', 'static', 'uploads', 'profile_pictures')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Generate URL
            url = f"/static/uploads/profile_pictures/{unique_filename}"
            
            # Update user's profile picture
            user.profile_picture = url
            db.session.commit()
            
            return jsonify({'url': url}), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the current user."""
    try:
        # Get user identity
        user_id = get_jwt_identity()
        
        # Get user
        user = User.query.get_or_404(user_id)
        
        # Serialize data
        schema = UserSchema()
        user_data = schema.dump(user)
        
        # Return user data
        return jsonify(user_data), 200
    
    except Exception as e:
        logger.exception(f"Get current user error: {str(e)}")
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
        
        # Allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename to avoid collisions
            unique_filename = f"user_{user_id}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_path = os.path.join('app', 'static', 'uploads', 'profile_pictures')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Generate URL
            url = f"/static/uploads/profile_pictures/{unique_filename}"
            
            # Update user's profile picture
            user.profile_picture = url
            db.session.commit()
            
            return jsonify({'url': url}), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/me/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    """Update user profile."""
    try:
        # Get user identity
        user_id = get_jwt_identity()
        
        # Get user
        user = User.query.get_or_404(user_id)
        
        # Validate request data
        schema = UserProfileSchema()
        data = schema.load(request.json)
        
        # Update user
        for key, value in data.items():
            setattr(user, key, value)
        
        # Save user
        db.session.commit()
        
        # Serialize data
        response_schema = UserSchema()
        user_data = response_schema.dump(user)
        
        # Return updated user
        return jsonify(user_data), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Update profile error: {str(e)}")
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
        
        # Allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        
        def allowed_file(filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename to avoid collisions
            unique_filename = f"user_{user_id}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_path = os.path.join('app', 'static', 'uploads', 'profile_pictures')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Generate URL
            url = f"/static/uploads/profile_pictures/{unique_filename}"
            
            # Update user's profile picture
            user.profile_picture = url
            db.session.commit()
            
            return jsonify({'url': url}), 200
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500