"""
SendGrid email integration.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

from ..base import APIKeyIntegration, IntegrationConfig, ServiceUnavailableError
from ..registry import register_integration
from .base_email import (
    BaseEmailIntegration, EmailMessage, EmailAttachment, EmailTemplate, EmailStats,
    EmailStatus, EmailEvent, EmailPriority
)

logger = logging.getLogger(__name__)


@register_integration('sendgrid')
class SendGridIntegration(BaseEmailIntegration, APIKeyIntegration):
    """SendGrid email service integration."""
    
    def __init__(self, config: IntegrationConfig):
        if not SENDGRID_AVAILABLE:
            raise ImportError("SendGrid library not available. Install sendgrid")
        
        super().__init__(config)
        self._client = None
        
    @property
    def provider_name(self) -> str:
        return "sendgrid"
    
    async def connect(self) -> bool:
        """Initialize SendGrid client."""
        try:
            if not self.api_key:
                return False
            
            self._client = sendgrid.SendGridAPIClient(api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SendGrid: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Clear SendGrid client."""
        self._client = None
        return True
    
    async def test_connection(self) -> bool:
        """Test SendGrid connection."""
        try:
            if not self._client:
                return False
            
            # Test with API key validation
            response = self._client.api_keys.get()
            return response.status_code == 200
        except Exception as e:
            logger.error(f"SendGrid connection test failed: {e}")
            return False
    
    async def send_email(self, message: EmailMessage) -> str:
        """Send email via SendGrid."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            sg_mail = self._convert_to_sendgrid_mail(message)
            response = self._client.send(sg_mail)
            
            if response.status_code in [200, 202]:
                # Extract message ID from headers
                message_id = response.headers.get('X-Message-Id', '')
                return message_id
            else:
                raise ServiceUnavailableError(f"SendGrid send failed: {response.status_code}", "email")
                
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {e}")
            raise ServiceUnavailableError(f"Failed to send email: {e}", "email")
    
    async def send_bulk_email(self, messages: List[EmailMessage]) -> List[str]:
        """Send multiple emails via SendGrid."""
        message_ids = []
        for message in messages:
            try:
                message_id = await self.send_email(message)
                message_ids.append(message_id)
            except Exception as e:
                logger.error(f"Failed to send bulk email: {e}")
                message_ids.append("")
        return message_ids
    
    async def get_email_status(self, message_id: str) -> Optional[EmailStatus]:
        """Get email status from SendGrid."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            # SendGrid doesn't have direct message status API
            # Would need to use Event Webhook or Activity API
            return None
        except Exception as e:
            logger.error(f"Failed to get email status: {e}")
            return None
    
    async def get_email_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> EmailStats:
        """Get email statistics from SendGrid."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['end_date'] = end_date.strftime('%Y-%m-%d')
            if tags:
                params['tags'] = tags
            
            response = self._client.stats.get(query_params=params)
            
            if response.status_code == 200:
                data = response.body
                # Parse SendGrid stats format
                return self._parse_sendgrid_stats(data)
            else:
                return EmailStats()
                
        except Exception as e:
            logger.error(f"Failed to get email stats: {e}")
            return EmailStats()
    
    async def create_template(self, template: EmailTemplate) -> str:
        """Create email template in SendGrid."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            template_data = {
                'name': template.name,
                'generation': 'dynamic'
            }
            
            response = self._client.templates.post(request_body=template_data)
            
            if response.status_code in [200, 201]:
                template_id = response.body.get('id')
                
                # Create version
                version_data = {
                    'template_id': template_id,
                    'active': 1,
                    'name': template.name,
                    'subject': template.subject,
                    'html_content': template.html_content or '',
                    'plain_content': template.text_content or ''
                }
                
                version_response = self._client.templates._(template_id).versions.post(
                    request_body=version_data
                )
                
                if version_response.status_code in [200, 201]:
                    return template_id
                else:
                    raise ServiceUnavailableError("Failed to create template version", "email")
            else:
                raise ServiceUnavailableError("Failed to create template", "email")
                
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise ServiceUnavailableError(f"Failed to create template: {e}", "email")
    
    async def get_template(self, template_id: str) -> Optional[EmailTemplate]:
        """Get email template from SendGrid."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            response = self._client.templates._(template_id).get()
            
            if response.status_code == 200:
                template_data = response.body
                return self._convert_from_sendgrid_template(template_data)
            elif response.status_code == 404:
                return None
            else:
                raise ServiceUnavailableError("Failed to get template", "email")
                
        except Exception as e:
            logger.error(f"Failed to get template: {e}")
            return None
    
    async def update_template(self, template_id: str, template: EmailTemplate) -> bool:
        """Update email template in SendGrid."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            # Update template metadata
            template_data = {
                'name': template.name
            }
            
            response = self._client.templates._(template_id).patch(request_body=template_data)
            
            if response.status_code == 200:
                # Update active version
                version_data = {
                    'subject': template.subject,
                    'html_content': template.html_content or '',
                    'plain_content': template.text_content or ''
                }
                
                # Get active version ID
                versions_response = self._client.templates._(template_id).versions.get()
                if versions_response.status_code == 200:
                    versions = versions_response.body.get('versions', [])
                    active_version = next((v for v in versions if v.get('active') == 1), None)
                    
                    if active_version:
                        version_id = active_version['id']
                        version_response = self._client.templates._(template_id).versions._(version_id).patch(
                            request_body=version_data
                        )
                        return version_response.status_code == 200
                
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to update template: {e}")
            return False
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete email template from SendGrid."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            response = self._client.templates._(template_id).delete()
            return response.status_code in [200, 204, 404]
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False
    
    async def list_templates(self) -> List[EmailTemplate]:
        """List email templates from SendGrid."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            response = self._client.templates.get()
            
            if response.status_code == 200:
                templates_data = response.body.get('templates', [])
                templates = []
                
                for template_data in templates_data:
                    template = self._convert_from_sendgrid_template(template_data)
                    templates.append(template)
                
                return templates
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            return []
    
    async def send_template_email(
        self,
        template_id: str,
        to: List[str],
        template_data: Dict[str, Any],
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> str:
        """Send email using SendGrid template."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            mail = Mail()
            
            # Set from
            if from_email:
                mail.from_email = Email(from_email, from_name)
            
            # Set template
            mail.template_id = template_id
            
            # Add recipients with template data
            for email in to:
                personalization = mail.personalizations[0] if mail.personalizations else mail.add_personalization()
                personalization.add_to(Email(email))
                
                # Add template data
                for key, value in template_data.items():
                    personalization.add_dynamic_template_data(key, value)
            
            response = self._client.send(mail)
            
            if response.status_code in [200, 202]:
                message_id = response.headers.get('X-Message-Id', '')
                return message_id
            else:
                raise ServiceUnavailableError(f"Template send failed: {response.status_code}", "email")
                
        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            raise ServiceUnavailableError(f"Failed to send template email: {e}", "email")
    
    async def add_to_suppression_list(self, email: str, reason: str = "unsubscribe") -> bool:
        """Add email to SendGrid suppression list."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            # Add to global unsubscribes
            data = {'emails': [email]}
            response = self._client.asm.suppressions.global_.post(request_body=data)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Failed to add to suppression list: {e}")
            return False
    
    async def remove_from_suppression_list(self, email: str) -> bool:
        """Remove email from SendGrid suppression list."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            response = self._client.asm.suppressions.global_._(email).delete()
            return response.status_code in [200, 204, 404]
        except Exception as e:
            logger.error(f"Failed to remove from suppression list: {e}")
            return False
    
    async def check_suppression_list(self, email: str) -> bool:
        """Check if email is in SendGrid suppression list."""
        if not self._client:
            raise ServiceUnavailableError("Not connected to SendGrid", "email")
        
        try:
            response = self._client.asm.suppressions.global_._(email).get()
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to check suppression list: {e}")
            return False
    
    def _convert_to_sendgrid_mail(self, message: EmailMessage) -> Mail:
        """Convert EmailMessage to SendGrid Mail object."""
        mail = Mail()
        
        # Set from
        if message.from_email:
            mail.from_email = Email(message.from_email, message.from_name)
        
        # Set subject
        mail.subject = message.subject
        
        # Set content
        if message.html_content:
            mail.add_content(Content("text/html", message.html_content))
        mail.add_content(Content("text/plain", message.content))
        
        # Add recipients
        for email in message.to:
            mail.add_to(To(email))
        
        # Add CC
        for email in message.cc:
            mail.add_cc(Email(email))
        
        # Add BCC
        for email in message.bcc:
            mail.add_bcc(Email(email))
        
        # Set reply-to
        if message.reply_to:
            mail.reply_to = Email(message.reply_to)
        
        # Add attachments
        for attachment in message.attachments:
            sg_attachment = Attachment()
            sg_attachment.file_content = FileContent(attachment.get_base64_content())
            sg_attachment.file_type = FileType(attachment.content_type)
            sg_attachment.file_name = FileName(attachment.filename)
            sg_attachment.disposition = Disposition(attachment.disposition)
            if attachment.content_id:
                sg_attachment.content_id = attachment.content_id
            mail.add_attachment(sg_attachment)
        
        # Add headers
        for key, value in message.headers.items():
            mail.add_header(key, value)
        
        # Add categories (tags)
        for tag in message.tags:
            mail.add_category(tag)
        
        # Set send time
        if message.send_at:
            mail.send_at = int(message.send_at.timestamp())
        
        return mail
    
    def _convert_from_sendgrid_template(self, template_data: Dict[str, Any]) -> EmailTemplate:
        """Convert SendGrid template to EmailTemplate."""
        # Get active version data
        versions = template_data.get('versions', [])
        active_version = next((v for v in versions if v.get('active') == 1), {})
        
        return EmailTemplate(
            id=template_data.get('id', ''),
            name=template_data.get('name', ''),
            subject=active_version.get('subject', ''),
            html_content=active_version.get('html_content'),
            text_content=active_version.get('plain_content'),
            created_at=datetime.fromisoformat(template_data.get('created_at', '').replace('Z', '+00:00')) if template_data.get('created_at') else None,
            updated_at=datetime.fromisoformat(template_data.get('updated_at', '').replace('Z', '+00:00')) if template_data.get('updated_at') else None
        )
    
    def _parse_sendgrid_stats(self, data: List[Dict[str, Any]]) -> EmailStats:
        """Parse SendGrid statistics data."""
        stats = EmailStats()
        
        for stat_data in data:
            metrics = stat_data.get('stats', [{}])[0].get('metrics', {})
            
            stats.sent += metrics.get('requests', 0)
            stats.delivered += metrics.get('delivered', 0)
            stats.bounced += metrics.get('bounces', 0)
            stats.opened += metrics.get('unique_opens', 0)
            stats.clicked += metrics.get('unique_clicks', 0)
            stats.unsubscribed += metrics.get('unsubscribes', 0)
            stats.spam_reports += metrics.get('spam_reports', 0)
        
        return stats
    
    async def process_webhook_event(self, payload: Dict[str, Any]) -> List[EmailEvent]:
        """Process SendGrid webhook event."""
        events = []
        
        # SendGrid sends array of events
        if isinstance(payload, list):
            for event_data in payload:
                event = self._parse_sendgrid_event(event_data)
                if event:
                    events.append(event)
        else:
            event = self._parse_sendgrid_event(payload)
            if event:
                events.append(event)
        
        return events
    
    def _parse_sendgrid_event(self, event_data: Dict[str, Any]) -> Optional[EmailEvent]:
        """Parse individual SendGrid event."""
        try:
            event_type_map = {
                'processed': EmailStatus.QUEUED,
                'delivered': EmailStatus.DELIVERED,
                'open': EmailStatus.OPENED,
                'click': EmailStatus.CLICKED,
                'bounce': EmailStatus.BOUNCED,
                'dropped': EmailStatus.FAILED,
                'spamreport': EmailStatus.SPAM,
                'unsubscribe': EmailStatus.UNSUBSCRIBED
            }
            
            event_type = event_type_map.get(event_data.get('event'))
            if not event_type:
                return None
            
            return EmailEvent(
                email=event_data.get('email', ''),
                event_type=event_type,
                timestamp=datetime.fromtimestamp(event_data.get('timestamp', 0), timezone.utc),
                message_id=event_data.get('sg_message_id'),
                reason=event_data.get('reason'),
                url=event_data.get('url'),
                user_agent=event_data.get('useragent'),
                ip_address=event_data.get('ip')
            )
        except Exception as e:
            logger.error(f"Failed to parse SendGrid event: {e}")
            return None