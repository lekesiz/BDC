"""Assessment API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.middleware.request_context import role_required

assessment_bp = Blueprint('assessment', __name__)


@assessment_bp.route('/assessment/templates', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def get_assessment_templates():
    """Get assessment templates for the current user's organization."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Mock data for now - can be replaced with actual database model later
    templates = [
        {
            'id': 1,
            'name': 'Basic Skills Assessment',
            'description': 'General assessment for basic skills',
            'category': 'general',
            'sections': [
                {
                    'name': 'Communication',
                    'questions': [
                        {
                            'id': 1,
                            'question': 'How well can the participant communicate verbally?',
                            'type': 'scale',
                            'scale_max': 5
                        }
                    ]
                }
            ],
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        },
        {
            'id': 2,
            'name': 'Technical Skills Assessment',
            'description': 'Assessment for technical and computer skills',
            'category': 'technical',
            'sections': [
                {
                    'name': 'Computer Skills',
                    'questions': [
                        {
                            'id': 2,
                            'question': 'Can the participant use basic computer applications?',
                            'type': 'boolean'
                        }
                    ]
                }
            ],
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
    ]
    
    return jsonify({
        'templates': templates,
        'total': len(templates)
    }), 200


@assessment_bp.route('/assessment/templates', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def create_assessment_template():
    """Create a new assessment template."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'description', 'category', 'sections']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Mock creation - replace with actual database logic
    new_template = {
        'id': 3,  # Would be auto-generated in real implementation
        'name': data['name'],
        'description': data['description'],
        'category': data['category'],
        'sections': data['sections'],
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }
    
    return jsonify(new_template), 201


@assessment_bp.route('/assessment/templates/<int:template_id>', methods=['GET'])
@jwt_required()
def get_assessment_template(template_id):
    """Get a specific assessment template."""
    # Mock data - replace with actual database query
    if template_id == 1:
        template = {
            'id': 1,
            'name': 'Basic Skills Assessment',
            'description': 'General assessment for basic skills',
            'category': 'general',
            'sections': [
                {
                    'name': 'Communication',
                    'questions': [
                        {
                            'id': 1,
                            'question': 'How well can the participant communicate verbally?',
                            'type': 'scale',
                            'scale_max': 5
                        }
                    ]
                }
            ],
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
        return jsonify(template), 200
    
    return jsonify({'error': 'Template not found'}), 404


@assessment_bp.route('/assessment/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def update_assessment_template(template_id):
    """Update an assessment template."""
    data = request.get_json()
    
    # Mock update - replace with actual database logic
    if template_id != 1:
        return jsonify({'error': 'Template not found'}), 404
    
    updated_template = {
        'id': template_id,
        'name': data.get('name', 'Basic Skills Assessment'),
        'description': data.get('description', 'General assessment for basic skills'),
        'category': data.get('category', 'general'),
        'sections': data.get('sections', []),
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }
    
    return jsonify(updated_template), 200


@assessment_bp.route('/assessment/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def delete_assessment_template(template_id):
    """Delete an assessment template."""
    # Mock deletion - replace with actual database logic
    if template_id != 1:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify({'message': 'Template deleted successfully'}), 200