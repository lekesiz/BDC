"""Program utility endpoints for categories, levels, etc."""

from flask import jsonify
from flask_jwt_extended import jwt_required

from . import programs_bp


@programs_bp.route('/programs/categories', methods=['GET'])
@jwt_required()
def get_program_categories():
    """Get available program categories."""
    categories = [
        {'value': 'technical', 'label': 'Technical Skills'},
        {'value': 'soft_skills', 'label': 'Soft Skills'},
        {'value': 'leadership', 'label': 'Leadership'},
        {'value': 'management', 'label': 'Management'},
        {'value': 'communication', 'label': 'Communication'},
        {'value': 'industry', 'label': 'Industry-Specific'},
        {'value': 'certification', 'label': 'Certification'},
        {'value': 'language', 'label': 'Language'},
        {'value': 'other', 'label': 'Other'}
    ]
    
    return jsonify(categories), 200


@programs_bp.route('/programs/levels', methods=['GET'])
@jwt_required()
def get_program_levels():
    """Get available program levels."""
    levels = [
        {'value': 'beginner', 'label': 'Beginner'},
        {'value': 'intermediate', 'label': 'Intermediate'},
        {'value': 'advanced', 'label': 'Advanced'},
        {'value': 'expert', 'label': 'Expert'}
    ]
    
    return jsonify(levels), 200