"""Chat API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.models import User, ChatConversation, ConversationStatus
from app.services.ai_chat_service import ai_chat_service
from app.utils.decorators import require_permission
from app.extensions import db

bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """Create a new chat conversation."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Extract parameters
    beneficiary_id = data.get('beneficiary_id')
    context_type = data.get('context_type', 'general')
    related_entity_type = data.get('related_entity_type')
    related_entity_id = data.get('related_entity_id')
    language = data.get('language')
    initial_message = data.get('message')
    
    # Validate context type
    valid_contexts = ['education', 'appointment', 'progress', 'assessment', 'general']
    if context_type not in valid_contexts:
        return jsonify({'error': 'Invalid context type'}), 400
    
    # Create conversation
    result = ai_chat_service.create_conversation(
        user_id=current_user_id,
        beneficiary_id=beneficiary_id,
        context_type=context_type,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        language=language,
        initial_message=initial_message
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 201


@bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """Send a message in an existing conversation."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    message = data.get('message')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Send message
    result = ai_chat_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user_id,
        message=message
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 200


@bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get user's conversation history."""
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    beneficiary_id = request.args.get('beneficiary_id', type=int)
    status = request.args.get('status')
    context_type = request.args.get('context_type')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Convert status string to enum if provided
    if status:
        try:
            status = ConversationStatus[status.upper()]
        except KeyError:
            return jsonify({'error': 'Invalid status'}), 400
    
    # Get conversations
    result = ai_chat_service.get_conversation_history(
        user_id=current_user_id,
        beneficiary_id=beneficiary_id,
        status=status,
        context_type=context_type,
        limit=limit,
        offset=offset
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 200


@bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """Get a specific conversation with messages."""
    current_user_id = get_jwt_identity()
    
    # Get conversation
    conversation = ChatConversation.query.filter_by(
        id=conversation_id,
        user_id=current_user_id
    ).first()
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    return jsonify({
        'conversation': conversation.to_dict(include_messages=True)
    }), 200


@bp.route('/conversations/<int:conversation_id>/close', methods=['POST'])
@jwt_required()
def close_conversation(conversation_id):
    """Close a conversation."""
    current_user_id = get_jwt_identity()
    
    # Get conversation
    conversation = ChatConversation.query.filter_by(
        id=conversation_id,
        user_id=current_user_id
    ).first()
    
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    if conversation.status != ConversationStatus.ACTIVE:
        return jsonify({'error': 'Conversation is not active'}), 400
    
    # Close conversation
    conversation.status = ConversationStatus.CLOSED
    conversation.closed_at = db.func.current_timestamp()
    db.session.commit()
    
    return jsonify({
        'message': 'Conversation closed successfully',
        'conversation': conversation.to_dict()
    }), 200


@bp.route('/conversations/<int:conversation_id>/export', methods=['GET'])
@jwt_required()
def export_conversation(conversation_id):
    """Export a conversation."""
    current_user_id = get_jwt_identity()
    format = request.args.get('format', 'json')
    
    if format not in ['json', 'text']:
        return jsonify({'error': 'Invalid export format'}), 400
    
    # Export conversation
    result = ai_chat_service.export_conversation(
        conversation_id=conversation_id,
        user_id=current_user_id,
        format=format
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    # Return appropriate response based on format
    if format == 'json':
        return jsonify(result), 200
    else:
        # For text format, return as plain text
        response = make_response(result['data'])
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Content-Disposition'] = f'attachment; filename=conversation_{conversation_id}.txt'
        return response


@bp.route('/rate-limits', methods=['GET'])
@jwt_required()
def get_rate_limits():
    """Get user's chat rate limits."""
    current_user_id = get_jwt_identity()
    
    # Get rate limit info
    from app.models import ChatRateLimit
    rate_limit = ChatRateLimit.query.filter_by(user_id=current_user_id).first()
    
    if not rate_limit:
        # Return default limits
        return jsonify({
            'daily_message_count': 0,
            'daily_token_count': 0,
            'monthly_message_count': 0,
            'monthly_token_count': 0,
            'max_daily_messages': ai_chat_service.DEFAULT_DAILY_MESSAGES,
            'max_daily_tokens': ai_chat_service.DEFAULT_DAILY_TOKENS,
            'max_monthly_messages': ai_chat_service.DEFAULT_MONTHLY_MESSAGES,
            'max_monthly_tokens': ai_chat_service.DEFAULT_MONTHLY_TOKENS
        }), 200
    
    return jsonify(rate_limit.to_dict()), 200


# Admin endpoints
@bp.route('/conversations/<int:conversation_id>/flag', methods=['POST'])
@jwt_required()
@require_permission('manage_conversations')
def flag_conversation(conversation_id):
    """Flag a conversation for moderation."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    reason = data.get('reason')
    if not reason:
        return jsonify({'error': 'Reason is required'}), 400
    
    # Flag conversation
    result = ai_chat_service.flag_conversation(
        conversation_id=conversation_id,
        admin_id=current_user_id,
        reason=reason
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 200


@bp.route('/analytics', methods=['GET'])
@jwt_required()
@require_permission('view_analytics')
def get_analytics():
    """Get chat analytics."""
    # Get query parameters
    tenant_id = request.args.get('tenant_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Parse dates if provided
    from datetime import datetime
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    
    # Get analytics
    result = ai_chat_service.get_conversation_analytics(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 200


@bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """Get available conversation templates."""
    current_user = User.query.get(get_jwt_identity())
    tenant_id = current_user.tenants[0].id if current_user.tenants else None
    
    # Get query parameters
    category = request.args.get('category')
    language = request.args.get('language', 'en')
    
    # Query templates
    from app.models import ConversationTemplate
    query = ConversationTemplate.query.filter_by(is_active=True)
    
    # Filter by tenant or global templates
    if tenant_id:
        query = query.filter(
            or_(
                ConversationTemplate.tenant_id == tenant_id,
                ConversationTemplate.tenant_id.is_(None)
            )
        )
    else:
        query = query.filter(ConversationTemplate.tenant_id.is_(None))
    
    if category:
        query = query.filter_by(category=category)
    if language:
        query = query.filter_by(language=language)
    
    templates = query.order_by(ConversationTemplate.priority.desc()).all()
    
    return jsonify({
        'templates': [template.to_dict() for template in templates]
    }), 200


@bp.route('/templates', methods=['POST'])
@jwt_required()
@require_permission('manage_templates')
def create_template():
    """Create a new conversation template."""
    data = request.get_json()
    current_user = User.query.get(get_jwt_identity())
    
    # Validate required fields
    required_fields = ['name', 'category', 'system_prompt', 'welcome_message']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Create template
    from app.models import ConversationTemplate
    template = ConversationTemplate(
        tenant_id=current_user.tenants[0].id if current_user.tenants else None,
        name=data['name'],
        description=data.get('description'),
        category=data['category'],
        language=data.get('language', 'en'),
        system_prompt=data['system_prompt'],
        welcome_message=data['welcome_message'],
        suggested_questions=data.get('suggested_questions', []),
        is_active=data.get('is_active', True),
        priority=data.get('priority', 0)
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({
        'message': 'Template created successfully',
        'template': template.to_dict()
    }), 201


@bp.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
@require_permission('manage_templates')
def update_template(template_id):
    """Update a conversation template."""
    data = request.get_json()
    
    # Get template
    from app.models import ConversationTemplate
    template = ConversationTemplate.query.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Update fields
    updateable_fields = [
        'name', 'description', 'category', 'language',
        'system_prompt', 'welcome_message', 'suggested_questions',
        'is_active', 'priority'
    ]
    
    for field in updateable_fields:
        if field in data:
            setattr(template, field, data[field])
    
    template.updated_at = db.func.current_timestamp()
    db.session.commit()
    
    return jsonify({
        'message': 'Template updated successfully',
        'template': template.to_dict()
    }), 200


@bp.route('/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
@require_permission('manage_templates')
def delete_template(template_id):
    """Delete a conversation template."""
    # Get template
    from app.models import ConversationTemplate
    template = ConversationTemplate.query.get(template_id)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Soft delete by deactivating
    template.is_active = False
    db.session.commit()
    
    return jsonify({
        'message': 'Template deleted successfully'
    }), 200


# Error handlers
@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# Import make_response for export functionality
from flask import make_response

from app.utils.logging import logger