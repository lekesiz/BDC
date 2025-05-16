from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.folder import Folder
from app.models.tenant import Tenant
from app.models.user import User
from sqlalchemy.exc import SQLAlchemyError

folders_bp = Blueprint('folders', __name__)

@folders_bp.route('/folders', methods=['POST'])
@jwt_required()
def create_folder():
    """Create a new folder."""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validate input
        if not data or 'name' not in data:
            return jsonify({'error': 'Folder name is required'}), 400
            
        # Get user and tenant
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Create the folder
        folder = Folder(
            name=data['name'],
            parent_id=data.get('parent_id'),
            tenant_id=user.tenant_id,
            owner_id=user_id
        )
        
        # If parent folder specified, validate it exists and user has access
        if folder.parent_id:
            parent_folder = Folder.query.filter_by(
                id=folder.parent_id,
                tenant_id=user.tenant_id
            ).first()
            if not parent_folder:
                return jsonify({'error': 'Parent folder not found'}), 404
        
        db.session.add(folder)
        db.session.commit()
        
        return jsonify({
            'id': folder.id,
            'name': folder.name,
            'parent_id': folder.parent_id,
            'owner_id': folder.owner_id,
            'created_at': folder.created_at.isoformat() if folder.created_at else None,
            'updated_at': folder.updated_at.isoformat() if folder.updated_at else None
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@folders_bp.route('/folders/<int:folder_id>', methods=['GET'])
@jwt_required()
def get_folder(folder_id):
    """Get folder details with path."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Get the folder
        folder = Folder.query.filter_by(
            id=folder_id,
            tenant_id=user.tenant_id
        ).first()
        
        if not folder:
            return jsonify({'error': 'Folder not found'}), 404
            
        # Build path
        path = []
        current_folder = folder.parent
        while current_folder:
            path.insert(0, {
                'id': current_folder.id,
                'name': current_folder.name
            })
            current_folder = current_folder.parent
            
        return jsonify({
            'id': folder.id,
            'name': folder.name,
            'parent_id': folder.parent_id,
            'owner_id': folder.owner_id,
            'path': path
        }), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500