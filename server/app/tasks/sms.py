"""SMS tasks for asynchronous processing."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import shared_task
from flask import current_app

from app.extensions import db
from app.models.sms_message import SMSMessage, SMSCampaign, SMSStatus
from app.models.user import User


@shared_task
def send_scheduled_sms(message_id: int):
    """Send a scheduled SMS message."""
    try:
        from app.services.sms_service import SMSService
        
        sms_message = SMSMessage.query.get(message_id)
        if not sms_message:
            current_app.logger.error(f"SMS message {message_id} not found")
            return False
        
        if sms_message.status != SMSStatus.PENDING.value:
            current_app.logger.warning(f"SMS message {message_id} is not pending")
            return False
        
        # Initialize SMS service
        sms_service = SMSService()
        
        # Send the SMS
        success, _, response = sms_service.send_sms(
            phone_number=sms_message.recipient_phone,
            message=sms_message.message_content,
            message_type=sms_message.message_type,
            user_id=sms_message.user_id,
            related_id=sms_message.related_id,
            related_type=sms_message.related_type,
            tenant_id=sms_message.tenant_id,
            metadata=sms_message.metadata,
            language=sms_message.language
        )
        
        return success
        
    except Exception as e:
        current_app.logger.error(f"Error sending scheduled SMS: {str(e)}")
        return False


@shared_task
def process_bulk_sms(
    phone_numbers: List[str],
    message: str,
    message_type: str,
    tenant_id: Optional[int],
    metadata: Optional[Dict[str, Any]],
    language: str
):
    """Process bulk SMS sending."""
    try:
        from app.services.sms_service import SMSService
        
        sms_service = SMSService()
        results = {
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        for phone_number in phone_numbers:
            success, message_id, response = sms_service.send_sms(
                phone_number=phone_number,
                message=message,
                message_type=message_type,
                tenant_id=tenant_id,
                metadata=metadata,
                language=language
            )
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'phone': phone_number,
                'success': success,
                'message_id': message_id,
                'error': response.get('error') if not success else None
            })
        
        return results
        
    except Exception as e:
        current_app.logger.error(f"Error processing bulk SMS: {str(e)}")
        return {
            'success': 0,
            'failed': len(phone_numbers),
            'error': str(e)
        }


@shared_task
def execute_sms_campaign(campaign_id: int):
    """Execute an SMS campaign."""
    try:
        from app.services.sms_service import SMSService
        
        campaign = SMSCampaign.query.get(campaign_id)
        if not campaign:
            current_app.logger.error(f"Campaign {campaign_id} not found")
            return False
        
        sms_service = SMSService()
        
        # Get recipients based on filters
        recipients = []
        if campaign.recipient_filters:
            query = User.query.filter_by(is_active=True)
            
            if 'roles' in campaign.recipient_filters:
                query = query.filter(User.role.in_(campaign.recipient_filters['roles']))
            if 'tenant_id' in campaign.recipient_filters:
                query = query.join(User.tenants).filter_by(id=campaign.recipient_filters['tenant_id'])
            
            # Get users with phone numbers
            users = query.filter(User.phone.isnot(None)).all()
            recipients = [(user.id, user.phone) for user in users]
        
        # Get message content
        message_content = campaign.message_content
        if campaign.template_id:
            from app.models.sms_message import SMSTemplate
            template = SMSTemplate.query.filter_by(template_id=campaign.template_id).first()
            if template:
                message_content = template.get_content('en')  # Default to English
        
        # Send messages
        for user_id, phone_number in recipients:
            try:
                success, message_id, _ = sms_service.send_sms(
                    phone_number=phone_number,
                    message=message_content,
                    user_id=user_id,
                    tenant_id=campaign.tenant_id,
                    metadata={
                        'campaign_id': campaign_id,
                        'campaign_name': campaign.name
                    }
                )
                
                if success:
                    campaign.messages_sent += 1
                    # Get the SMS message to check cost
                    sms_msg = SMSMessage.query.get(message_id)
                    if sms_msg and sms_msg.cost_amount:
                        campaign.total_cost += sms_msg.cost_amount
                else:
                    campaign.messages_failed += 1
                    
            except Exception as e:
                current_app.logger.error(f"Error sending campaign SMS to {phone_number}: {str(e)}")
                campaign.messages_failed += 1
        
        # Update campaign status
        campaign.status = 'completed'
        campaign.completed_at = datetime.utcnow()
        db.session.commit()
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error executing SMS campaign: {str(e)}")
        
        # Mark campaign as failed
        campaign = SMSCampaign.query.get(campaign_id)
        if campaign:
            campaign.status = 'failed'
            db.session.commit()
        
        return False


@shared_task
def update_sms_delivery_status():
    """Update delivery status for sent messages."""
    try:
        from app.services.sms_service import SMSService
        
        sms_service = SMSService()
        
        # Get messages that are sent but not yet delivered/failed
        pending_messages = SMSMessage.query.filter_by(
            status=SMSStatus.SENT.value
        ).filter(
            SMSMessage.sent_at > datetime.utcnow() - timedelta(hours=24)  # Check messages from last 24 hours
        ).all()
        
        for message in pending_messages:
            if message.provider_message_id:
                sms_service._update_delivery_status(message)
        
        return len(pending_messages)
        
    except Exception as e:
        current_app.logger.error(f"Error updating SMS delivery status: {str(e)}")
        return 0


@shared_task
def send_appointment_reminders():
    """Send appointment reminders for upcoming appointments."""
    try:
        from datetime import timedelta
        from app.models.appointment import Appointment
        from app.services.sms_service import SMSService
        
        sms_service = SMSService()
        
        # Get appointments happening in the next 24 hours
        tomorrow = datetime.utcnow() + timedelta(days=1)
        today = datetime.utcnow()
        
        appointments = Appointment.query.filter(
            Appointment.start_time >= today,
            Appointment.start_time <= tomorrow,
            Appointment.status == 'scheduled'
        ).all()
        
        sent_count = 0
        for appointment in appointments:
            # Check if reminder already sent
            existing_reminder = SMSMessage.query.filter_by(
                related_id=appointment.id,
                related_type='appointment',
                message_type='appointment_reminder'
            ).first()
            
            if existing_reminder:
                continue
            
            # Get beneficiary phone number
            if appointment.beneficiary and appointment.beneficiary.phone:
                success, _ = sms_service.send_appointment_reminder(
                    appointment_id=appointment.id,
                    phone_number=appointment.beneficiary.phone,
                    user_id=appointment.beneficiary_id,
                    language='en'
                )
                
                if success:
                    sent_count += 1
        
        return sent_count
        
    except Exception as e:
        current_app.logger.error(f"Error sending appointment reminders: {str(e)}")
        return 0


@shared_task
def cleanup_old_sms_records(days_to_keep: int = 90):
    """Clean up old SMS records."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old SMS messages
        deleted_count = SMSMessage.query.filter(
            SMSMessage.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        current_app.logger.info(f"Deleted {deleted_count} old SMS records")
        return deleted_count
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up SMS records: {str(e)}")
        db.session.rollback()
        return 0