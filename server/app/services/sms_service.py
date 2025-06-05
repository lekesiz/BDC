"""SMS service implementation with multiple provider support."""

import re
import phonenumbers
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from flask import current_app
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
import boto3
from botocore.exceptions import ClientError

from app.extensions import db, redis_client
from app.models.sms_message import SMSMessage, SMSTemplate, SMSCampaign, SMSStatus, SMSType, SMSProvider
from app.models.user import User
from app.models.appointment import Appointment
from app.models.assessment import Assessment
from app.services.interfaces.sms_service_interface import ISMSService
from app.tasks.sms import send_scheduled_sms, process_bulk_sms
from app.utils.decorators import rate_limit


class SMSService(ISMSService):
    """SMS service implementation with Twilio as primary provider."""
    
    def __init__(self):
        """Initialize SMS service with provider clients."""
        self._init_providers()
        self._init_templates()
    
    def _init_providers(self):
        """Initialize SMS provider clients."""
        self.providers = {}
        
        # Initialize Twilio
        twilio_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        twilio_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        if twilio_sid and twilio_token:
            self.providers['twilio'] = {
                'client': TwilioClient(twilio_sid, twilio_token),
                'from_number': current_app.config.get('TWILIO_PHONE_NUMBER'),
                'priority': 1
            }
        
        # Initialize AWS SNS as fallback
        aws_access_key = current_app.config.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = current_app.config.get('AWS_SECRET_ACCESS_KEY')
        if aws_access_key and aws_secret_key:
            self.providers['aws_sns'] = {
                'client': boto3.client(
                    'sns',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=current_app.config.get('AWS_REGION', 'us-east-1')
                ),
                'priority': 2
            }
    
    def _init_templates(self):
        """Initialize default SMS templates if they don't exist."""
        default_templates = [
            {
                'template_id': 'appointment_reminder',
                'name': 'Appointment Reminder',
                'message_type': SMSType.APPOINTMENT_REMINDER.value,
                'content_en': 'Reminder: You have an appointment on {{date}} at {{time}} with {{trainer_name}}. Location: {{location}}',
                'content_tr': 'Hatırlatma: {{date}} tarihinde saat {{time}} de {{trainer_name}} ile randevunuz var. Yer: {{location}}',
                'variables': ['date', 'time', 'trainer_name', 'location']
            },
            {
                'template_id': 'assessment_notification',
                'name': 'Assessment Notification',
                'message_type': SMSType.ASSESSMENT_NOTIFICATION.value,
                'content_en': 'You have a new assessment to complete: {{assessment_name}}. Please complete it by {{due_date}}.',
                'content_tr': 'Tamamlamanız gereken yeni bir değerlendirme var: {{assessment_name}}. Lütfen {{due_date}} tarihine kadar tamamlayın.',
                'variables': ['assessment_name', 'due_date']
            },
            {
                'template_id': 'password_reset',
                'name': 'Password Reset Code',
                'message_type': SMSType.PASSWORD_RESET.value,
                'content_en': 'Your password reset code is: {{code}}. This code will expire in 15 minutes.',
                'content_tr': 'Şifre sıfırlama kodunuz: {{code}}. Bu kod 15 dakika içinde geçerliliğini yitirecek.',
                'variables': ['code']
            },
            {
                'template_id': '2fa_code',
                'name': '2FA Verification Code',
                'message_type': SMSType.TWO_FACTOR_AUTH.value,
                'content_en': 'Your verification code is: {{code}}. Do not share this code with anyone.',
                'content_tr': 'Doğrulama kodunuz: {{code}}. Bu kodu kimseyle paylaşmayın.',
                'variables': ['code']
            }
        ]
        
        for template_data in default_templates:
            existing = SMSTemplate.query.filter_by(template_id=template_data['template_id']).first()
            if not existing:
                template = SMSTemplate(**template_data)
                db.session.add(template)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error initializing SMS templates: {str(e)}")
    
    @rate_limit("sms", max_calls=100, time_window=3600)  # 100 SMS per hour
    def send_sms(
        self,
        phone_number: str,
        message: str,
        message_type: str = 'general_notification',
        user_id: Optional[int] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        tenant_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Send an SMS message."""
        try:
            # Validate phone number
            is_valid, formatted_number = self.validate_phone_number(phone_number)
            if not is_valid:
                return False, None, {'error': 'Invalid phone number'}
            
            # Create SMS record
            sms_message = SMSMessage(
                user_id=user_id,
                recipient_phone=formatted_number,
                message_type=message_type,
                message_content=message,
                language=language,
                related_id=related_id,
                related_type=related_type,
                tenant_id=tenant_id,
                metadata=metadata,
                status=SMSStatus.QUEUED.value
            )
            
            if user_id:
                user = User.query.get(user_id)
                if user:
                    sms_message.recipient_name = f"{user.first_name} {user.last_name}"
            
            db.session.add(sms_message)
            db.session.commit()
            
            # Try sending with primary provider
            success, provider_response = self._send_with_provider(
                formatted_number, 
                message, 
                'twilio'
            )
            
            if success:
                sms_message.mark_as_sent(
                    provider_message_id=provider_response.get('message_id'),
                    provider_response=provider_response
                )
                sms_message.provider = SMSProvider.TWILIO.value
                
                # Track cost if available
                if 'price' in provider_response:
                    sms_message.cost_amount = float(provider_response['price'])
                    sms_message.cost_currency = provider_response.get('price_unit', 'USD')
            else:
                # Try fallback provider
                if 'aws_sns' in self.providers:
                    success, provider_response = self._send_with_provider(
                        formatted_number, 
                        message, 
                        'aws_sns'
                    )
                    
                    if success:
                        sms_message.mark_as_sent(
                            provider_message_id=provider_response.get('message_id'),
                            provider_response=provider_response
                        )
                        sms_message.provider = SMSProvider.AWS_SNS.value
                    else:
                        sms_message.mark_as_failed(str(provider_response))
                else:
                    sms_message.mark_as_failed(str(provider_response))
            
            db.session.commit()
            
            return success, str(sms_message.id), provider_response
            
        except Exception as e:
            current_app.logger.error(f"Error sending SMS: {str(e)}")
            return False, None, {'error': str(e)}
    
    def _send_with_provider(self, phone_number: str, message: str, provider_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Send SMS with specific provider."""
        if provider_name not in self.providers:
            return False, {'error': 'Provider not configured'}
        
        provider = self.providers[provider_name]
        
        try:
            if provider_name == 'twilio':
                response = provider['client'].messages.create(
                    body=message,
                    from_=provider['from_number'],
                    to=phone_number
                )
                return True, {
                    'message_id': response.sid,
                    'status': response.status,
                    'price': response.price,
                    'price_unit': response.price_unit
                }
            
            elif provider_name == 'aws_sns':
                response = provider['client'].publish(
                    PhoneNumber=phone_number,
                    Message=message
                )
                return True, {
                    'message_id': response['MessageId'],
                    'status': 'sent'
                }
            
        except TwilioException as e:
            current_app.logger.error(f"Twilio error: {str(e)}")
            return False, {'error': str(e)}
        except ClientError as e:
            current_app.logger.error(f"AWS SNS error: {str(e)}")
            return False, {'error': str(e)}
        except Exception as e:
            current_app.logger.error(f"Provider error: {str(e)}")
            return False, {'error': str(e)}
        
        return False, {'error': 'Unknown provider'}
    
    def send_templated_sms(
        self,
        phone_number: str,
        template_id: str,
        variables: Optional[Dict[str, Any]] = None,
        message_type: str = 'general_notification',
        user_id: Optional[int] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        tenant_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Send an SMS using a template."""
        try:
            # Get template
            template = SMSTemplate.query.filter_by(
                template_id=template_id,
                is_active=True
            ).first()
            
            if not template:
                return False, None, {'error': 'Template not found'}
            
            # Render template
            message = template.render(variables, language)
            
            # Send SMS
            return self.send_sms(
                phone_number=phone_number,
                message=message,
                message_type=template.message_type,
                user_id=user_id,
                related_id=related_id,
                related_type=related_type,
                tenant_id=tenant_id,
                metadata={
                    'template_id': template_id,
                    'variables': variables,
                    **(metadata or {})
                },
                language=language
            )
            
        except Exception as e:
            current_app.logger.error(f"Error sending templated SMS: {str(e)}")
            return False, None, {'error': str(e)}
    
    def send_bulk_sms(
        self,
        phone_numbers: List[str],
        message: str,
        message_type: str = 'general_notification',
        tenant_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """Send SMS to multiple recipients."""
        try:
            # Validate all phone numbers
            valid_numbers = []
            invalid_numbers = []
            
            for phone in phone_numbers:
                is_valid, formatted = self.validate_phone_number(phone)
                if is_valid:
                    valid_numbers.append(formatted)
                else:
                    invalid_numbers.append(phone)
            
            if not valid_numbers:
                return {
                    'success': 0,
                    'failed': len(invalid_numbers),
                    'invalid_numbers': invalid_numbers
                }
            
            # Queue bulk SMS task
            from app.tasks.sms import process_bulk_sms
            task = process_bulk_sms.delay(
                valid_numbers,
                message,
                message_type,
                tenant_id,
                metadata,
                language
            )
            
            return {
                'task_id': task.id,
                'total': len(phone_numbers),
                'queued': len(valid_numbers),
                'invalid': len(invalid_numbers),
                'invalid_numbers': invalid_numbers
            }
            
        except Exception as e:
            current_app.logger.error(f"Error sending bulk SMS: {str(e)}")
            return {
                'error': str(e),
                'success': 0,
                'failed': len(phone_numbers)
            }
    
    def schedule_sms(
        self,
        phone_number: str,
        message: str,
        scheduled_time: datetime,
        message_type: str = 'general_notification',
        user_id: Optional[int] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        tenant_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[int]]:
        """Schedule an SMS for future delivery."""
        try:
            # Validate phone number
            is_valid, formatted_number = self.validate_phone_number(phone_number)
            if not is_valid:
                return False, None
            
            # Ensure scheduled time is in the future
            if scheduled_time <= datetime.utcnow():
                return False, None
            
            # Create SMS record
            sms_message = SMSMessage(
                user_id=user_id,
                recipient_phone=formatted_number,
                message_type=message_type,
                message_content=message,
                language=language,
                related_id=related_id,
                related_type=related_type,
                tenant_id=tenant_id,
                metadata=metadata,
                status=SMSStatus.PENDING.value,
                scheduled_for=scheduled_time
            )
            
            if user_id:
                user = User.query.get(user_id)
                if user:
                    sms_message.recipient_name = f"{user.first_name} {user.last_name}"
            
            db.session.add(sms_message)
            db.session.commit()
            
            # Schedule task
            from app.tasks.sms import send_scheduled_sms
            send_scheduled_sms.apply_async(
                args=[sms_message.id],
                eta=scheduled_time
            )
            
            return True, sms_message.id
            
        except Exception as e:
            current_app.logger.error(f"Error scheduling SMS: {str(e)}")
            return False, None
    
    def cancel_scheduled_sms(self, message_id: int) -> bool:
        """Cancel a scheduled SMS."""
        try:
            sms_message = SMSMessage.query.get(message_id)
            if not sms_message:
                return False
            
            if sms_message.status != SMSStatus.PENDING.value:
                return False
            
            sms_message.status = SMSStatus.CANCELLED.value
            db.session.commit()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error cancelling SMS: {str(e)}")
            return False
    
    def get_sms_status(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get the status of an SMS message."""
        try:
            sms_message = SMSMessage.query.get(message_id)
            if not sms_message:
                return None
            
            # Update status from provider if needed
            if sms_message.provider_message_id and sms_message.status == SMSStatus.SENT.value:
                self._update_delivery_status(sms_message)
            
            return sms_message.to_dict()
            
        except Exception as e:
            current_app.logger.error(f"Error getting SMS status: {str(e)}")
            return None
    
    def _update_delivery_status(self, sms_message: SMSMessage):
        """Update delivery status from provider."""
        try:
            if sms_message.provider == SMSProvider.TWILIO.value and 'twilio' in self.providers:
                client = self.providers['twilio']['client']
                message = client.messages(sms_message.provider_message_id).fetch()
                
                if message.status == 'delivered':
                    sms_message.mark_as_delivered()
                elif message.status in ['failed', 'undelivered']:
                    sms_message.mark_as_failed(message.error_message)
                
                db.session.commit()
                
        except Exception as e:
            current_app.logger.error(f"Error updating delivery status: {str(e)}")
    
    def get_sms_history(
        self,
        user_id: Optional[int] = None,
        phone_number: Optional[str] = None,
        message_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get SMS history with filters."""
        try:
            query = SMSMessage.query
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            if phone_number:
                query = query.filter_by(recipient_phone=phone_number)
            if message_type:
                query = query.filter_by(message_type=message_type)
            if status:
                query = query.filter_by(status=status)
            if start_date:
                query = query.filter(SMSMessage.created_at >= start_date)
            if end_date:
                query = query.filter(SMSMessage.created_at <= end_date)
            
            messages = query.order_by(SMSMessage.created_at.desc())\
                          .limit(limit)\
                          .offset(offset)\
                          .all()
            
            return [msg.to_dict() for msg in messages]
            
        except Exception as e:
            current_app.logger.error(f"Error getting SMS history: {str(e)}")
            return []
    
    def get_sms_stats(
        self,
        tenant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get SMS statistics."""
        try:
            query = db.session.query(SMSMessage)
            
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            if start_date:
                query = query.filter(SMSMessage.created_at >= start_date)
            if end_date:
                query = query.filter(SMSMessage.created_at <= end_date)
            
            # Get counts by status
            status_counts = {}
            for status in SMSStatus:
                count = query.filter_by(status=status.value).count()
                status_counts[status.value] = count
            
            # Get counts by type
            type_counts = {}
            for sms_type in SMSType:
                count = query.filter_by(message_type=sms_type.value).count()
                type_counts[sms_type.value] = count
            
            # Calculate costs
            total_cost = db.session.query(
                db.func.sum(SMSMessage.cost_amount)
            ).filter(
                SMSMessage.cost_amount.isnot(None)
            ).scalar() or 0.0
            
            # Get provider breakdown
            provider_counts = {}
            for provider in SMSProvider:
                count = query.filter_by(provider=provider.value).count()
                provider_counts[provider.value] = count
            
            return {
                'total_messages': query.count(),
                'status_breakdown': status_counts,
                'type_breakdown': type_counts,
                'provider_breakdown': provider_counts,
                'total_cost': total_cost,
                'cost_currency': 'USD',
                'date_range': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting SMS stats: {str(e)}")
            return {}
    
    def validate_phone_number(self, phone_number: str, country_code: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Validate and format a phone number."""
        try:
            # Remove common formatting characters
            cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
            
            # Default country code
            default_country = country_code or current_app.config.get('DEFAULT_COUNTRY_CODE', 'US')
            
            # Parse phone number
            parsed = phonenumbers.parse(cleaned, default_country)
            
            # Validate
            if not phonenumbers.is_valid_number(parsed):
                return False, None
            
            # Format in E164
            formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            
            return True, formatted
            
        except phonenumbers.phonenumberutil.NumberParseException:
            return False, None
        except Exception as e:
            current_app.logger.error(f"Error validating phone number: {str(e)}")
            return False, None
    
    def send_appointment_reminder(
        self,
        appointment_id: int,
        phone_number: str,
        user_id: Optional[int] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str]]:
        """Send appointment reminder SMS."""
        try:
            appointment = Appointment.query.get(appointment_id)
            if not appointment:
                return False, None
            
            # Format date and time
            date_str = appointment.start_time.strftime('%B %d, %Y')
            time_str = appointment.start_time.strftime('%I:%M %p')
            
            # Get trainer name
            trainer_name = "your trainer"
            if appointment.trainer:
                trainer_name = f"{appointment.trainer.first_name} {appointment.trainer.last_name}"
            
            # Send templated SMS
            success, message_id, response = self.send_templated_sms(
                phone_number=phone_number,
                template_id='appointment_reminder',
                variables={
                    'date': date_str,
                    'time': time_str,
                    'trainer_name': trainer_name,
                    'location': appointment.location or 'TBD'
                },
                message_type=SMSType.APPOINTMENT_REMINDER.value,
                user_id=user_id,
                related_id=appointment_id,
                related_type='appointment',
                tenant_id=appointment.tenant_id,
                language=language
            )
            
            return success, message_id
            
        except Exception as e:
            current_app.logger.error(f"Error sending appointment reminder: {str(e)}")
            return False, None
    
    def send_assessment_notification(
        self,
        assessment_id: int,
        phone_number: str,
        user_id: Optional[int] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str]]:
        """Send assessment notification SMS."""
        try:
            assessment = Assessment.query.get(assessment_id)
            if not assessment:
                return False, None
            
            # Format due date
            due_date_str = "soon"
            if hasattr(assessment, 'due_date') and assessment.due_date:
                due_date_str = assessment.due_date.strftime('%B %d, %Y')
            
            # Send templated SMS
            success, message_id, response = self.send_templated_sms(
                phone_number=phone_number,
                template_id='assessment_notification',
                variables={
                    'assessment_name': assessment.title,
                    'due_date': due_date_str
                },
                message_type=SMSType.ASSESSMENT_NOTIFICATION.value,
                user_id=user_id,
                related_id=assessment_id,
                related_type='assessment',
                language=language
            )
            
            return success, message_id
            
        except Exception as e:
            current_app.logger.error(f"Error sending assessment notification: {str(e)}")
            return False, None
    
    def send_password_reset_code(
        self,
        phone_number: str,
        reset_code: str,
        user_id: Optional[int] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str]]:
        """Send password reset code via SMS."""
        try:
            # Store reset code in Redis with expiration
            if user_id:
                redis_key = f"password_reset:{user_id}"
                redis_client.setex(redis_key, 900, reset_code)  # 15 minutes
            
            # Send templated SMS
            success, message_id, response = self.send_templated_sms(
                phone_number=phone_number,
                template_id='password_reset',
                variables={'code': reset_code},
                message_type=SMSType.PASSWORD_RESET.value,
                user_id=user_id,
                language=language
            )
            
            return success, message_id
            
        except Exception as e:
            current_app.logger.error(f"Error sending password reset code: {str(e)}")
            return False, None
    
    def send_2fa_code(
        self,
        phone_number: str,
        auth_code: str,
        user_id: Optional[int] = None,
        language: str = 'en'
    ) -> Tuple[bool, Optional[str]]:
        """Send 2FA verification code via SMS."""
        try:
            # Store auth code in Redis with expiration
            if user_id:
                redis_key = f"2fa_code:{user_id}"
                redis_client.setex(redis_key, 300, auth_code)  # 5 minutes
            
            # Send templated SMS
            success, message_id, response = self.send_templated_sms(
                phone_number=phone_number,
                template_id='2fa_code',
                variables={'code': auth_code},
                message_type=SMSType.TWO_FACTOR_AUTH.value,
                user_id=user_id,
                language=language
            )
            
            return success, message_id
            
        except Exception as e:
            current_app.logger.error(f"Error sending 2FA code: {str(e)}")
            return False, None
    
    def create_sms_campaign(
        self,
        name: str,
        template_id: Optional[str] = None,
        message_content: Optional[str] = None,
        recipient_filters: Optional[Dict[str, Any]] = None,
        scheduled_for: Optional[datetime] = None,
        tenant_id: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> Optional[int]:
        """Create an SMS campaign."""
        try:
            campaign = SMSCampaign(
                name=name,
                template_id=template_id,
                message_content=message_content,
                recipient_filters=recipient_filters,
                scheduled_for=scheduled_for,
                tenant_id=tenant_id,
                created_by=created_by,
                status='draft' if not scheduled_for else 'scheduled'
            )
            
            # Calculate recipient count based on filters
            if recipient_filters:
                query = User.query.filter_by(is_active=True)
                
                if 'roles' in recipient_filters:
                    query = query.filter(User.role.in_(recipient_filters['roles']))
                if 'tenant_id' in recipient_filters:
                    query = query.join(User.tenants).filter_by(id=recipient_filters['tenant_id'])
                
                campaign.recipient_count = query.count()
            
            db.session.add(campaign)
            db.session.commit()
            
            return campaign.id
            
        except Exception as e:
            current_app.logger.error(f"Error creating SMS campaign: {str(e)}")
            db.session.rollback()
            return None
    
    def execute_sms_campaign(self, campaign_id: int) -> bool:
        """Execute an SMS campaign."""
        try:
            campaign = SMSCampaign.query.get(campaign_id)
            if not campaign:
                return False
            
            if campaign.status not in ['draft', 'scheduled']:
                return False
            
            # Update campaign status
            campaign.status = 'running'
            campaign.started_at = datetime.utcnow()
            db.session.commit()
            
            # Queue campaign execution
            from app.tasks.sms import execute_sms_campaign
            execute_sms_campaign.delay(campaign_id)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error executing SMS campaign: {str(e)}")
            return False
    
    def get_campaign_status(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """Get campaign status and statistics."""
        try:
            campaign = SMSCampaign.query.get(campaign_id)
            if not campaign:
                return None
            
            return campaign.to_dict()
            
        except Exception as e:
            current_app.logger.error(f"Error getting campaign status: {str(e)}")
            return None