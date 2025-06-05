"""SMS API endpoints."""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.sms_message import SMSMessage, SMSTemplate, SMSCampaign
from app.services.sms_service import SMSService
from app.utils.decorators import require_role, require_permission

from app.utils.logging import logger

sms_bp = Blueprint('sms', __name__, url_prefix='/api/sms')
sms_service = SMSService()


@sms_bp.route('/send', methods=['POST'])
@jwt_required()
@require_permission('sms.send')
def send_sms():
    """Send an SMS message."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'error': 'Phone number and message are required'}), 400
        
        # Send SMS
        success, message_id, response = sms_service.send_sms(
            phone_number=phone_number,
            message=message,
            message_type=data.get('message_type', 'general_notification'),
            user_id=data.get('user_id'),
            related_id=data.get('related_id'),
            related_type=data.get('related_type'),
            tenant_id=data.get('tenant_id'),
            metadata=data.get('metadata'),
            language=data.get('language', 'en')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message_id': message_id,
                'status': 'sent'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': response.get('error', 'Failed to send SMS')
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/send-templated', methods=['POST'])
@jwt_required()
@require_permission('sms.send')
def send_templated_sms():
    """Send an SMS using a template."""
    try:
        data = request.get_json()
        
        # Validate required fields
        phone_number = data.get('phone_number')
        template_id = data.get('template_id')
        
        if not phone_number or not template_id:
            return jsonify({'error': 'Phone number and template ID are required'}), 400
        
        # Send templated SMS
        success, message_id, response = sms_service.send_templated_sms(
            phone_number=phone_number,
            template_id=template_id,
            variables=data.get('variables', {}),
            message_type=data.get('message_type', 'general_notification'),
            user_id=data.get('user_id'),
            related_id=data.get('related_id'),
            related_type=data.get('related_type'),
            tenant_id=data.get('tenant_id'),
            metadata=data.get('metadata'),
            language=data.get('language', 'en')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message_id': message_id,
                'status': 'sent'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': response.get('error', 'Failed to send SMS')
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/send-bulk', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def send_bulk_sms():
    """Send SMS to multiple recipients."""
    try:
        data = request.get_json()
        
        # Validate required fields
        phone_numbers = data.get('phone_numbers', [])
        message = data.get('message')
        
        if not phone_numbers or not message:
            return jsonify({'error': 'Phone numbers and message are required'}), 400
        
        # Send bulk SMS
        result = sms_service.send_bulk_sms(
            phone_numbers=phone_numbers,
            message=message,
            message_type=data.get('message_type', 'general_notification'),
            tenant_id=data.get('tenant_id'),
            metadata=data.get('metadata'),
            language=data.get('language', 'en')
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/schedule', methods=['POST'])
@jwt_required()
@require_permission('sms.schedule')
def schedule_sms():
    """Schedule an SMS for future delivery."""
    try:
        data = request.get_json()
        
        # Validate required fields
        phone_number = data.get('phone_number')
        message = data.get('message')
        scheduled_time_str = data.get('scheduled_time')
        
        if not phone_number or not message or not scheduled_time_str:
            return jsonify({'error': 'Phone number, message, and scheduled time are required'}), 400
        
        # Parse scheduled time
        try:
            scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid scheduled time format'}), 400
        
        # Schedule SMS
        success, message_id = sms_service.schedule_sms(
            phone_number=phone_number,
            message=message,
            scheduled_time=scheduled_time,
            message_type=data.get('message_type', 'general_notification'),
            user_id=data.get('user_id'),
            related_id=data.get('related_id'),
            related_type=data.get('related_type'),
            tenant_id=data.get('tenant_id'),
            metadata=data.get('metadata'),
            language=data.get('language', 'en')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message_id': message_id,
                'status': 'scheduled'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to schedule SMS'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/messages/<int:message_id>/cancel', methods=['POST'])
@jwt_required()
@require_permission('sms.cancel')
def cancel_scheduled_sms(message_id):
    """Cancel a scheduled SMS."""
    try:
        success = sms_service.cancel_scheduled_sms(message_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'SMS cancelled successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to cancel SMS'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/messages/<int:message_id>/status', methods=['GET'])
@jwt_required()
def get_sms_status(message_id):
    """Get the status of an SMS message."""
    try:
        status = sms_service.get_sms_status(message_id)
        
        if status:
            return jsonify(status), 200
        else:
            return jsonify({'error': 'Message not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/history', methods=['GET'])
@jwt_required()
def get_sms_history():
    """Get SMS history with filters."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Parse query parameters
        user_id = request.args.get('user_id', type=int)
        phone_number = request.args.get('phone_number')
        message_type = request.args.get('message_type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Regular users can only see their own messages
        if current_user.role not in ['super_admin', 'tenant_admin']:
            user_id = current_user_id
        
        # Get history
        messages = sms_service.get_sms_history(
            user_id=user_id,
            phone_number=phone_number,
            message_type=message_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'messages': messages,
            'total': len(messages),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def get_sms_stats():
    """Get SMS statistics."""
    try:
        # Parse query parameters
        tenant_id = request.args.get('tenant_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Parse dates
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get stats
        stats = sms_service.get_sms_stats(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/validate-phone', methods=['POST'])
@jwt_required()
def validate_phone_number():
    """Validate a phone number."""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        country_code = data.get('country_code')
        
        if not phone_number:
            return jsonify({'error': 'Phone number is required'}), 400
        
        is_valid, formatted = sms_service.validate_phone_number(phone_number, country_code)
        
        return jsonify({
            'valid': is_valid,
            'formatted_number': formatted
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Template management endpoints

@sms_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_sms_templates():
    """Get SMS templates."""
    try:
        templates = SMSTemplate.query.filter_by(is_active=True).all()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/templates', methods=['POST'])
@jwt_required()
@require_role(['super_admin'])
def create_sms_template():
    """Create a new SMS template."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['template_id', 'name', 'content_en', 'message_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if template ID already exists
        existing = SMSTemplate.query.filter_by(template_id=data['template_id']).first()
        if existing:
            return jsonify({'error': 'Template ID already exists'}), 400
        
        # Create template
        template = SMSTemplate(
            template_id=data['template_id'],
            name=data['name'],
            description=data.get('description'),
            content_en=data['content_en'],
            content_tr=data.get('content_tr'),
            message_type=data['message_type'],
            variables=data.get('variables', []),
            tenant_id=data.get('tenant_id')
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify(template.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
@require_role(['super_admin'])
def update_sms_template(template_id):
    """Update an SMS template."""
    try:
        template = SMSTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'content_en' in data:
            template.content_en = data['content_en']
        if 'content_tr' in data:
            template.content_tr = data['content_tr']
        if 'variables' in data:
            template.variables = data['variables']
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify(template.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Campaign management endpoints

@sms_bp.route('/campaigns', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def get_sms_campaigns():
    """Get SMS campaigns."""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        query = SMSCampaign.query
        
        # Filter by tenant for tenant admins
        if current_user.role == 'tenant_admin':
            query = query.filter_by(tenant_id=current_user.tenant_id)
        
        campaigns = query.order_by(SMSCampaign.created_at.desc()).all()
        
        return jsonify({
            'campaigns': [campaign.to_dict() for campaign in campaigns]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/campaigns', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def create_sms_campaign():
    """Create a new SMS campaign."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Campaign name is required'}), 400
        
        if not data.get('template_id') and not data.get('message_content'):
            return jsonify({'error': 'Either template_id or message_content is required'}), 400
        
        # Parse scheduled time if provided
        scheduled_for = None
        if data.get('scheduled_for'):
            try:
                scheduled_for = datetime.fromisoformat(data['scheduled_for'].replace('Z', '+00:00'))
            except:
                return jsonify({'error': 'Invalid scheduled time format'}), 400
        
        # Create campaign
        campaign_id = sms_service.create_sms_campaign(
            name=data['name'],
            template_id=data.get('template_id'),
            message_content=data.get('message_content'),
            recipient_filters=data.get('recipient_filters'),
            scheduled_for=scheduled_for,
            tenant_id=data.get('tenant_id'),
            created_by=current_user_id
        )
        
        if campaign_id:
            return jsonify({
                'success': True,
                'campaign_id': campaign_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create campaign'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/campaigns/<int:campaign_id>/execute', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def execute_sms_campaign(campaign_id):
    """Execute an SMS campaign."""
    try:
        success = sms_service.execute_sms_campaign(campaign_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Campaign execution started'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to execute campaign'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sms_bp.route('/campaigns/<int:campaign_id>/status', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def get_campaign_status(campaign_id):
    """Get campaign status and statistics."""
    try:
        status = sms_service.get_campaign_status(campaign_id)
        
        if status:
            return jsonify(status), 200
        else:
            return jsonify({'error': 'Campaign not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500