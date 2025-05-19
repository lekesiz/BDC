"""User profile API endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.profile import UserProfileSchema, UserProfileUpdateSchema

users_profile_bp = Blueprint('users_profile', __name__)
profile_schema = UserProfileSchema()
profile_update_schema = UserProfileUpdateSchema()


@users_profile_bp.route('/users/me/profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Get current user's profile."""
    current_user_id = get_jwt_identity()
    
    # Get user with profile
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get or create profile
    profile = UserProfile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        # Create default profile
        profile = UserProfile(
            user_id=current_user_id,
            bio='',
            phone='',
            address='',
            city='',
            state='',
            country='',
            postal_code='',
            linkedin_url='',
            github_url='',
            website_url='',
            timezone='UTC',
            avatar_url=None
        )
        db.session.add(profile)
        db.session.commit()
    
    # Include user data in profile response
    profile_data = profile_schema.dump(profile)
    profile_data.update({
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'is_active': user.is_active
    })
    
    return jsonify(profile_data), 200


@users_profile_bp.route('/users/me/profile', methods=['PUT', 'PATCH'])
@jwt_required()
def update_my_profile():
    """Update current user's profile."""
    current_user_id = get_jwt_identity()
    
    # Validate request data
    errors = profile_update_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Get or create profile
    profile = UserProfile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        profile = UserProfile(user_id=current_user_id)
        db.session.add(profile)
    
    # Update profile fields
    for key, value in request.json.items():
        if hasattr(profile, key) and key not in ['id', 'user_id', 'created_at', 'updated_at']:
            setattr(profile, key, value)
    
    # Handle user fields if provided
    user = User.query.get(current_user_id)
    if user:
        if 'first_name' in request.json:
            user.first_name = request.json['first_name']
        if 'last_name' in request.json:
            user.last_name = request.json['last_name']
        if 'phone' in request.json:
            profile.phone = request.json['phone']
    
    try:
        db.session.commit()
        
        # Return updated profile
        profile_data = profile_schema.dump(profile)
        profile_data.update({
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active
        })
        
        return jsonify(profile_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500


@users_profile_bp.route('/users/me/profile/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Upload user avatar."""
    current_user_id = get_jwt_identity()
    
    if 'avatar' not in request.files:
        return jsonify({'error': 'No avatar file provided'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not file.filename.lower().split('.')[-1] in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400
    
    # Get user profile
    profile = UserProfile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        profile = UserProfile(user_id=current_user_id)
        db.session.add(profile)
    
    # TODO: Implement actual file upload logic
    # For now, just return a placeholder response
    avatar_url = f'/uploads/avatars/{current_user_id}_{file.filename}'
    profile.avatar_url = avatar_url
    
    try:
        db.session.commit()
        return jsonify({
            'avatar_url': avatar_url,
            'message': 'Avatar uploaded successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to upload avatar'}), 500


@users_profile_bp.route('/users/me/profile/privacy', methods=['GET'])
@jwt_required()
def get_privacy_settings():
    """Get user's privacy settings."""
    current_user_id = get_jwt_identity()
    
    # Get user's privacy preferences
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    privacy_settings = {
        'profile_visibility': getattr(user, 'profile_visibility', 'public'),
        'show_email': getattr(user, 'show_email', False),
        'show_phone': getattr(user, 'show_phone', False),
        'show_social_links': getattr(user, 'show_social_links', True),
        'allow_messages': getattr(user, 'allow_messages', True),
        'allow_notifications': getattr(user, 'allow_notifications', True)
    }
    
    return jsonify(privacy_settings), 200


@users_profile_bp.route('/users/me/profile/privacy', methods=['PUT'])
@jwt_required()
def update_privacy_settings():
    """Update user's privacy settings."""
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update privacy settings
    privacy_fields = [
        'profile_visibility', 'show_email', 'show_phone',
        'show_social_links', 'allow_messages', 'allow_notifications'
    ]
    
    for field in privacy_fields:
        if field in request.json:
            setattr(user, field, request.json[field])
    
    try:
        db.session.commit()
        return jsonify({'message': 'Privacy settings updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update privacy settings'}), 500


@users_profile_bp.route('/users/me/profile/social', methods=['PUT'])
@jwt_required()
def update_social_links():
    """Update user's social media links."""
    current_user_id = get_jwt_identity()
    
    profile = UserProfile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        profile = UserProfile(user_id=current_user_id)
        db.session.add(profile)
    
    # Update social links
    social_fields = ['linkedin_url', 'github_url', 'twitter_url', 'facebook_url', 'website_url']
    
    for field in social_fields:
        if field in request.json:
            setattr(profile, field, request.json[field])
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Social links updated successfully',
            'social_links': {
                field: getattr(profile, field, None) for field in social_fields
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update social links'}), 500


@users_profile_bp.route('/users/me/profile/skills', methods=['GET'])
@jwt_required()
def get_skills():
    """Get user's skills."""
    current_user_id = get_jwt_identity()
    
    profile = UserProfile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({'skills': []}), 200
    
    skills = getattr(profile, 'skills', [])
    return jsonify({'skills': skills}), 200


@users_profile_bp.route('/users/me/profile/skills', methods=['PUT'])
@jwt_required()
def update_skills():
    """Update user's skills."""
    current_user_id = get_jwt_identity()
    
    if 'skills' not in request.json:
        return jsonify({'error': 'Skills field is required'}), 400
    
    skills = request.json['skills']
    if not isinstance(skills, list):
        return jsonify({'error': 'Skills must be a list'}), 400
    
    profile = UserProfile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        profile = UserProfile(user_id=current_user_id)
        db.session.add(profile)
    
    profile.skills = skills
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Skills updated successfully',
            'skills': skills
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update skills'}), 500