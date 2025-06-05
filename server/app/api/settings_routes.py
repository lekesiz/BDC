"""Settings API routes."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.decorators import role_required
from app.extensions import db

from app.utils.logging import logger

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.route('/ai', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def get_ai_settings():
    """Get AI configuration settings."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'user_not_found', 'message': 'User not found'}), 404
        
        # Default AI settings - these would typically come from database or config
        default_settings = {
            'providers': {
                'openai': {
                    'name': 'OpenAI GPT',
                    'enabled': True,
                    'model': 'gpt-3.5-turbo',
                    'apiKey': '',  # Will be masked for security
                    'baseUrl': 'https://api.openai.com/v1',
                    'temperature': 0.7,
                    'maxTokens': 1000,
                    'description': 'OpenAI GPT models for general AI tasks',
                    'supportedModels': [
                        'gpt-3.5-turbo',
                        'gpt-4',
                        'gpt-4-turbo',
                        'gpt-4o'
                    ]
                },
                'anthropic': {
                    'name': 'Anthropic Claude',
                    'enabled': False,
                    'model': 'claude-3-sonnet-20240229',
                    'apiKey': '',
                    'baseUrl': 'https://api.anthropic.com/v1',
                    'temperature': 0.7,
                    'maxTokens': 1000,
                    'description': 'Anthropic Claude models for advanced reasoning',
                    'supportedModels': [
                        'claude-3-haiku-20240307',
                        'claude-3-sonnet-20240229',
                        'claude-3-opus-20240229'
                    ]
                },
                'local': {
                    'name': 'Local LLM',
                    'enabled': False,
                    'model': 'llama2',
                    'apiKey': '',
                    'baseUrl': 'http://localhost:11434/v1',
                    'temperature': 0.7,
                    'maxTokens': 1000,
                    'description': 'Self-hosted local language models',
                    'supportedModels': [
                        'llama2',
                        'mistral',
                        'codellama'
                    ]
                }
            },
            'features': {
                'content_generation': {
                    'enabled': True,
                    'provider': 'openai',
                    'description': 'Generate educational content and materials'
                },
                'evaluation_insights': {
                    'enabled': True,
                    'provider': 'openai',
                    'description': 'AI-powered evaluation analysis and insights'
                },
                'chatbot': {
                    'enabled': True,
                    'provider': 'openai',
                    'description': 'Interactive AI assistant for learners'
                },
                'recommendations': {
                    'enabled': True,
                    'provider': 'openai',
                    'description': 'Personalized learning recommendations'
                }
            },
            'customEndpoints': [
                {
                    'id': 1,
                    'name': 'Custom Translation Service',
                    'url': 'https://api.example.com/translate',
                    'apiKey': '***masked***',
                    'description': 'Custom translation endpoint for multilingual support'
                }
            ],
            'usage': {
                'monthly_tokens': 0,
                'monthly_limit': 1000000,
                'current_month': '2025-06',
                'cost_estimate': 0.00
            }
        }
        
        # In a real implementation, you would fetch actual settings from database
        # For now, return the default configuration
        return jsonify(default_settings), 200
        
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@settings_bp.route('/ai', methods=['PUT'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def update_ai_settings():
    """Update AI configuration settings."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'user_not_found', 'message': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'invalid_data', 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['providers']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': 'missing_field', 'message': f'Missing required field: {field}'}), 400
        
        # In a real implementation, you would:
        # 1. Validate the configuration
        # 2. Save to database
        # 3. Update environment variables or config files
        # 4. Restart services if needed
        
        # For now, just log the update
        current_app.logger.info(f'AI settings updated by user {current_user.email}')
        current_app.logger.info(f'Updated providers: {list(data["providers"].keys())}')
        
        return jsonify({
            'message': 'AI settings updated successfully',
            'updated_at': '2025-06-02T16:48:00Z',
            'updated_by': current_user.email
        }), 200
        
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@settings_bp.route('/ai/test-connection', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def test_ai_connection():
    """Test AI provider connection."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'user_not_found', 'message': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or 'provider' not in data:
            return jsonify({'error': 'invalid_data', 'message': 'Provider is required'}), 400
        
        provider = data['provider']
        
        # Mock connection test - in real implementation, you would:
        # 1. Make actual API call to the provider
        # 2. Test authentication
        # 3. Verify model availability
        # 4. Check rate limits
        
        test_results = {
            'provider': provider,
            'status': 'success',
            'response_time': '234ms',
            'model_available': True,
            'rate_limit_remaining': 1000,
            'tested_at': '2025-06-02T16:48:00Z',
            'message': f'Successfully connected to {provider}'
        }
        
        # Simulate some different test results
        if provider == 'anthropic':
            test_results.update({
                'status': 'warning',
                'message': 'Connected but rate limits are low',
                'rate_limit_remaining': 50
            })
        elif provider == 'local':
            test_results.update({
                'status': 'error',
                'message': 'Local server not responding',
                'model_available': False
            })
        
        return jsonify(test_results), 200
        
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Connection test failed'}), 500


@settings_bp.route('/ai/usage', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def get_ai_usage():
    """Get AI usage statistics."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'user_not_found', 'message': 'User not found'}), 404
        
        # Mock usage data - in real implementation, fetch from usage tracking
        usage_stats = {
            'current_month': '2025-06',
            'total_tokens': 15420,
            'total_requests': 89,
            'cost_estimate': 23.45,
            'monthly_limit': 1000000,
            'usage_by_feature': {
                'content_generation': {
                    'tokens': 8920,
                    'requests': 34,
                    'cost': 13.20
                },
                'evaluation_insights': {
                    'tokens': 4200,
                    'requests': 28,
                    'cost': 6.40
                },
                'chatbot': {
                    'tokens': 1800,
                    'requests': 18,
                    'cost': 2.85
                },
                'recommendations': {
                    'tokens': 500,
                    'requests': 9,
                    'cost': 1.00
                }
            },
            'usage_by_provider': {
                'openai': {
                    'tokens': 14920,
                    'requests': 84,
                    'cost': 22.45
                },
                'anthropic': {
                    'tokens': 500,
                    'requests': 5,
                    'cost': 1.00
                }
            },
            'daily_usage': [
                {'date': '2025-06-01', 'tokens': 1200, 'requests': 8, 'cost': 1.80},
                {'date': '2025-06-02', 'tokens': 2100, 'requests': 12, 'cost': 3.15}
            ]
        }
        
        return jsonify(usage_stats), 200
        
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500