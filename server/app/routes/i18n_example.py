"""
Example routes showing i18n implementation
Demonstrates how to use translations in API endpoints
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.i18n import translate, Messages, localized_response, get_available_languages, set_user_language
from app.models import User, Beneficiary
from app.extensions import db
from app.utils.decorators import validate_json

i18n_bp = Blueprint('i18n', __name__, url_prefix='/api/i18n')


@i18n_bp.route('/languages', methods=['GET'])
@localized_response
def get_languages():
    """Get available languages"""
    languages = get_available_languages()
    return jsonify({
        'languages': languages,
        'message': translate('api.success.generic')
    }), 200


@i18n_bp.route('/language', methods=['POST'])
@jwt_required()
@validate_json({
    'language': {'type': 'string', 'required': True}
})
@localized_response
def set_language():
    """Set user's preferred language"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'error': translate('api.error.not_found'),
            'message': translate('api.user.not_found')
        }), 404
    
    language = request.json.get('language')
    
    if set_user_language(user, language):
        return jsonify({
            'message': translate('api.settings.updated'),
            'language': language
        }), 200
    else:
        return jsonify({
            'error': translate('api.error.validation'),
            'message': translate('api.settings.invalid_value')
        }), 400


@i18n_bp.route('/beneficiaries', methods=['POST'])
@jwt_required()
@validate_json({
    'first_name': {'type': 'string', 'required': True},
    'last_name': {'type': 'string', 'required': True},
    'email': {'type': 'string', 'required': True},
    'phone': {'type': 'string', 'required': True}
})
@localized_response
def create_beneficiary_i18n():
    """Example of creating a beneficiary with i18n responses"""
    data = request.get_json()
    
    # Validation with translated messages
    errors = []
    
    if not data.get('first_name'):
        errors.append(Messages.FIELD_REQUIRED('first_name'))
    
    if not data.get('last_name'):
        errors.append(Messages.FIELD_REQUIRED('last_name'))
    
    if not data.get('email'):
        errors.append(Messages.FIELD_REQUIRED('email'))
    elif '@' not in data.get('email', ''):
        errors.append(Messages.INVALID_EMAIL())
    
    if errors:
        return jsonify({
            'error': Messages.ERROR_VALIDATION(),
            'errors': errors
        }), 400
    
    # Check if email already exists
    existing = Beneficiary.query.filter_by(email=data['email']).first()
    if existing:
        return jsonify({
            'error': Messages.ERROR_VALIDATION(),
            'message': translate('api.validation.unique', field='email')
        }), 400
    
    try:
        # Create beneficiary
        beneficiary = Beneficiary(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            date_of_birth=data.get('date_of_birth'),
            address=data.get('address', {}),
            emergency_contact=data.get('emergency_contact', {}),
            status='active'
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        return jsonify({
            'message': translate('api.beneficiary.created'),
            'beneficiary': {
                'id': beneficiary.id,
                'first_name': beneficiary.first_name,
                'last_name': beneficiary.last_name,
                'email': beneficiary.email,
                'status': beneficiary.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': Messages.ERROR_SERVER(),
            'message': str(e)
        }), 500


@i18n_bp.route('/test-messages', methods=['GET'])
@localized_response
def test_messages():
    """Test various message translations"""
    return jsonify({
        'success_messages': {
            'created': Messages.SUCCESS_CREATED(),
            'updated': Messages.SUCCESS_UPDATED(),
            'deleted': Messages.SUCCESS_DELETED()
        },
        'error_messages': {
            'not_found': Messages.ERROR_NOT_FOUND(),
            'unauthorized': Messages.ERROR_UNAUTHORIZED(),
            'validation': Messages.ERROR_VALIDATION()
        },
        'auth_messages': {
            'login_success': Messages.AUTH_LOGIN_SUCCESS(),
            'login_failed': Messages.AUTH_LOGIN_FAILED(),
            'token_expired': Messages.AUTH_TOKEN_EXPIRED()
        },
        'validation_messages': {
            'email_required': Messages.FIELD_REQUIRED('email'),
            'min_length': Messages.MIN_LENGTH('password', 8),
            'max_length': Messages.MAX_LENGTH('name', 50)
        },
        'custom_translations': {
            'welcome': translate('email.subject.welcome'),
            'greeting': translate('email.greeting.formal', name='John Doe'),
            'date_today': translate('dates.relative.today')
        }
    }), 200


@i18n_bp.route('/test-pluralization', methods=['GET'])
@localized_response
def test_pluralization():
    """Test pluralization in translations"""
    from app.i18n import pluralize
    
    counts = [0, 1, 2, 5, 10]
    results = {}
    
    for count in counts:
        results[f'days_{count}'] = translate('dates.relative.days_ago', count=count)
    
    return jsonify({
        'pluralization_examples': results,
        'message': translate('api.success.generic')
    }), 200


# Example error handler with i18n
@i18n_bp.errorhandler(404)
@localized_response
def not_found_error(error):
    """Handle 404 errors with translated message"""
    return jsonify({
        'error': Messages.ERROR_NOT_FOUND(),
        'message': translate('api.error.not_found')
    }), 404


@i18n_bp.errorhandler(500)
@localized_response
def internal_error(error):
    """Handle 500 errors with translated message"""
    return jsonify({
        'error': Messages.ERROR_SERVER(),
        'message': translate('api.error.server')
    }), 500