"""User profile API endpoints."""

from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.profile import UserProfileSchema, UserProfileUpdateSchema

profile_bp = Blueprint('profile', __name__)
profile_schema = UserProfileSchema()
profile_update_schema = UserProfileUpdateSchema()


@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get the current user's profile."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Check if the user has a profile, create one if not
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    
    return jsonify(profile_schema.dump(profile)), 200


@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update the current user's profile."""
    user_id = get_jwt_identity()
    
    # Validate request data
    try:
        profile_data = profile_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400
    
    # Get or create profile
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
    
    # Update profile fields
    for key, value in profile_data.items():
        setattr(profile, key, value)
    
    db.session.commit()
    
    return jsonify(profile_schema.dump(profile)), 200


@profile_bp.route('/profiles/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    """Get a user's profile by user ID (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if current user has permission to view this profile
    if current_user.role not in ['super_admin', 'tenant_admin'] and current_user_id != user_id:
        return jsonify({"error": "Not authorized to view this profile"}), 403
    
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify(profile_schema.dump(profile)), 200


@profile_bp.route('/profiles/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user_profile(user_id):
    """Update a user's profile by user ID (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if current user has permission to update this profile
    if current_user.role not in ['super_admin', 'tenant_admin'] and current_user_id != user_id:
        return jsonify({"error": "Not authorized to update this profile"}), 403
    
    # Validate request data
    try:
        profile_data = profile_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400
    
    # Get or create profile
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
    
    # Update profile fields
    for key, value in profile_data.items():
        setattr(profile, key, value)
    
    db.session.commit()
    
    return jsonify(profile_schema.dump(profile)), 200


@profile_bp.route('/profile/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Upload a profile avatar."""
    user_id = get_jwt_identity()
    
    if 'avatar' not in request.files:
        return jsonify({"error": "No avatar file provided"}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Check file type
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({"error": "Only PNG and JPG files are allowed"}), 400
    
    # Save file
    import os
    from werkzeug.utils import secure_filename
    import uuid
    
    filename = secure_filename(file.filename)
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', unique_filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    file.save(file_path)
    
    # Update profile with avatar URL
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
    
    # Set the avatar URL
    avatar_url = f"/uploads/avatars/{unique_filename}"
    profile.avatar_url = avatar_url
    db.session.commit()
    
    return jsonify({
        "message": "Avatar uploaded successfully",
        "avatar_url": avatar_url
    }), 201