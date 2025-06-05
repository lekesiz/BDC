"""Test API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.extensions import db
from app.models.test import Test, TestSet, Question
from app.models.user import User

from app.utils.logging import logger

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/tests', methods=['GET'])
@jwt_required()
def get_tests():
    """Get all tests accessible by the current user."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', None)
    status = request.args.get('status', None)
    
    # Base query
    query = Test.query
    
    # Filter by user role
    if user.role == 'student':
        # Students can't see tests directly
        return jsonify({'tests': [], 'total': 0, 'pages': 0}), 200
    elif user.role == 'trainer':
        # Trainers can see tests created by them or published tests
        query = query.filter(or_(
            Test.created_by == user_id,
            Test.status == 'published'
        ))
    
    # Apply filters
    if search:
        query = query.filter(Test.title.contains(search))
    
    if status:
        query = query.filter_by(status=status)
    
    # Filter active tests
    query = query.filter_by(is_active=True)
    
    # Order by created date
    query = query.order_by(Test.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Serialize tests
    tests = [test.to_dict() for test in pagination.items]
    
    return jsonify({
        'tests': tests,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@tests_bp.route('/tests', methods=['POST'])
@jwt_required()
def create_test():
    """Create a new test."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Check permissions
    if user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Not authorized to create tests'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'type', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create test
    test = Test(
        title=data['title'],
        description=data.get('description', ''),
        type=data['type'],
        category=data['category'],
        tenant_id=getattr(user, 'tenant_id', 1),  # Default to 1 if not set
        created_by=user_id,
        duration=data.get('duration'),
        passing_score=data.get('passing_score', 70.0),
        total_points=data.get('total_points', 100.0),
        status=data.get('status', 'draft')
    )
    
    db.session.add(test)
    db.session.commit()
    
    return jsonify(test.to_dict()), 201


@tests_bp.route('/tests/sessions', methods=['GET'])
@jwt_required()
def get_test_sessions():
    """Get test sessions for current user."""
    from app.models.test import TestSession
    from app.models.evaluation import Evaluation
    
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', None)
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Base query
    query = TestSession.query
    
    # Filter by user role
    if user.role == 'student':
        # Students see their own test sessions
        from app.models.beneficiary import Beneficiary
        beneficiary = Beneficiary.query.filter_by(user_id=user_id).first()
        if beneficiary:
            query = query.filter_by(beneficiary_id=beneficiary.id)
        else:
            # Return empty if no beneficiary record
            return jsonify({'sessions': [], 'total': 0, 'pages': 0}), 200
    elif user.role == 'trainer':
        # Trainers see test sessions of their beneficiaries
        from app.models.beneficiary import Beneficiary
        trainer_beneficiaries = Beneficiary.query.filter_by(trainer_id=user_id).all()
        beneficiary_ids = [b.id for b in trainer_beneficiaries]
        query = query.filter(TestSession.beneficiary_id.in_(beneficiary_ids))
    # Admins see all test sessions within their tenant
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    # Apply sorting
    if hasattr(TestSession, sort):
        sort_field = getattr(TestSession, sort)
        if order == 'desc':
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Include evaluation info in response
    sessions = []
    for session in pagination.items:
        session_dict = session.to_dict()
        
        # Try to get test info through evaluation
        if hasattr(session, 'evaluation_id') and session.evaluation_id:
            evaluation = Evaluation.query.get(session.evaluation_id)
            if evaluation:
                session_dict['evaluation'] = {
                    'id': evaluation.id,
                    'title': evaluation.title,
                    'description': evaluation.description
                }
        
        sessions.append(session_dict)
    
    return jsonify({
        'sessions': sessions,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@tests_bp.route('/tests/<int:test_id>', methods=['GET'])
@jwt_required()
def get_test(test_id):
    """Get a specific test."""
    user_id = get_jwt_identity()
    test = Test.query.get_or_404(test_id)
    
    # Check permissions
    user = User.query.get_or_404(user_id)
    if user.role == 'student':
        return jsonify({'error': 'Not authorized to view this test'}), 403
    elif user.role == 'trainer' and test.created_by != user_id and test.status != 'published':
        return jsonify({'error': 'Not authorized to view this test'}), 403
    
    return jsonify(test.to_dict()), 200

@tests_bp.route('/tests/<int:test_id>', methods=['PUT'])
@jwt_required()
def update_test(test_id):
    """Update a test."""
    user_id = get_jwt_identity()
    test = Test.query.get_or_404(test_id)
    
    # Check permissions
    user = User.query.get_or_404(user_id)
    if user.role not in ['super_admin', 'tenant_admin'] and test.created_by != user_id:
        return jsonify({'error': 'Not authorized to update this test'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        test.title = data['title']
    if 'description' in data:
        test.description = data['description']
    if 'type' in data:
        test.type = data['type']
    if 'category' in data:
        test.category = data['category']
    if 'duration' in data:
        test.duration = data['duration']
    if 'passing_score' in data:
        test.passing_score = data['passing_score']
    if 'total_points' in data:
        test.total_points = data['total_points']
    if 'status' in data:
        test.status = data['status']
    
    db.session.commit()
    
    return jsonify(test.to_dict()), 200

@tests_bp.route('/tests/<int:test_id>', methods=['DELETE'])
@jwt_required()
def delete_test(test_id):
    """Delete a test (soft delete)."""
    user_id = get_jwt_identity()
    test = Test.query.get_or_404(test_id)
    
    # Check permissions
    user = User.query.get_or_404(user_id)
    if user.role not in ['super_admin', 'tenant_admin'] and test.created_by != user_id:
        return jsonify({'error': 'Not authorized to delete this test'}), 403
    
    # Soft delete
    test.is_active = False
    test.status = 'archived'
    db.session.commit()
    
    return jsonify({'message': 'Test deleted successfully'}), 200

# Test types endpoint
@tests_bp.route('/tests/types', methods=['GET'])
@jwt_required()
def get_test_types():
    """Get available test types."""
    test_types = [
        {'value': 'questionnaire', 'label': 'Questionnaire'},
        {'value': 'assessment', 'label': 'Assessment'},
        {'value': 'skill_test', 'label': 'Skill Test'},
        {'value': 'evaluation', 'label': 'Evaluation'},
        {'value': 'survey', 'label': 'Survey'}
    ]
    
    return jsonify({'types': test_types}), 200

# Test categories endpoint
@tests_bp.route('/tests/categories', methods=['GET'])
@jwt_required()
def get_test_categories():
    """Get available test categories."""
    categories = [
        {'value': 'technical', 'label': 'Technical Skills'},
        {'value': 'soft_skills', 'label': 'Soft Skills'},
        {'value': 'leadership', 'label': 'Leadership'},
        {'value': 'communication', 'label': 'Communication'},
        {'value': 'problem_solving', 'label': 'Problem Solving'},
        {'value': 'general', 'label': 'General Knowledge'}
    ]
    
    return jsonify({'categories': categories}), 200