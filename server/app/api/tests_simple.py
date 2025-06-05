"""Simple Tests API for frontend compatibility."""

from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, current_user

from app.extensions import db
from app.models.test import Test, Question

from app.utils.logging import logger

tests_simple_bp = Blueprint('tests_simple', __name__)

@tests_simple_bp.route('', methods=['GET'])
@jwt_required()
def get_tests():
    """Get all tests for evaluations page."""
    try:
        # Get all tests from the database
        tests = Test.query.filter_by(is_active=True).order_by(Test.created_at.desc()).all()
        
        # Transform tests to match frontend expectations
        result = []
        for test in tests:
            # Get questions count - using test_set_id since that's the field in Question model
            question_count = 0  # Default to 0 for now since tests != test_sets
            
            test_data = {
                'id': test.id,
                'title': test.title,
                'description': test.description or 'No description available',
                'type': test.type,
                'category': test.category or 'general',
                'status': test.status,
                'time_limit': test.duration,  # Map duration to time_limit
                'passing_score': test.passing_score or 70.0,
                'questions': {'length': question_count},  # Frontend expects questions.length
                'created_at': test.created_at.isoformat() if test.created_at else None,
                'updated_at': test.updated_at.isoformat() if test.updated_at else None
            }
            result.append(test_data)
        
        return jsonify({
            'items': result,
            'total': len(result),
            'page': 1,
            'per_page': len(result),
            'pages': 1
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get tests error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500

@tests_simple_bp.route('/<int:test_id>', methods=['GET'])
@jwt_required()
def get_test(test_id):
    """Get a specific test by ID."""
    try:
        test = Test.query.get_or_404(test_id)
        
        # Get questions for this test - no direct relation, use empty list for now
        questions = []
        
        test_data = {
            'id': test.id,
            'title': test.title,
            'description': test.description or 'No description available',
            'type': test.type,
            'category': test.category or 'general',
            'status': test.status,
            'time_limit': test.duration,
            'passing_score': test.passing_score or 70.0,
            'questions': [],
            'created_at': test.created_at.isoformat() if test.created_at else None,
            'updated_at': test.updated_at.isoformat() if test.updated_at else None
        }
        
        return jsonify(test_data), 200
        
    except Exception as e:
        current_app.logger.exception(f"Get test error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500