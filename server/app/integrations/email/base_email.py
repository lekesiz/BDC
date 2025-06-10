"""
Base email service integration functionality.
"""

from abc import abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import base64

from ..base import BaseIntegration, IntegrationConfig


class EmailStatus(Enum):
    """Email status."""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"
    SPAM = "spam"
    UNSUBSCRIBED = "unsubscribed"


class EmailPriority(Enum):
    """Email priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class EmailAttachment:
    """Email attachment."""
    filename: str
    content: bytes
    content_type: str
    content_id: Optional[str] = None
    disposition: str = "attachment"  # "attachment" or "inline"
    
    def get_base64_content(self) -> str:
        """Get base64 encoded content."""
        return base64.b64encode(self.content).decode('utf-8')


@dataclass
class EmailMessage:
    """Email message."""
    to: List[str]
    subject: str
    content: str
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    reply_to: Optional[str] = None
    html_content: Optional[str] = None
    attachments: Optional[List[EmailAttachment]] = None
    headers: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    priority: EmailPriority = EmailPriority.NORMAL
    send_at: Optional[datetime] = None
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.cc is None:
            self.cc = []
        if self.bcc is None:
            self.bcc = []
        if self.attachments is None:
            self.attachments = []
        if self.headers is None:
            self.headers = {}
        if self.tags is None:
            self.tags = []
        if self.template_data is None:
            self.template_data = {}


@dataclass
class EmailTemplate:
    """Email template."""
    id: str
    name: str
    subject: str
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    variables: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = []


@dataclass
class EmailStats:
    """Email statistics."""
    sent: int = 0
    delivered: int = 0
    bounced: int = 0
    opened: int = 0
    clicked: int = 0
    unsubscribed: int = 0
    spam_reports: int = 0
    reputation: Optional[float] = None
    date: Optional[datetime] = None


@dataclass
class EmailEvent:
    """Email event (webhook data)."""
    email: str
    event_type: EmailStatus
    timestamp: datetime
    message_id: Optional[str] = None
    reason: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class BaseEmailIntegration(BaseIntegration):
    """Base class for email service integrations."""
    
    @property
    def integration_type(self) -> str:
        return "email"
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> str:
        """Send an email message and return message ID."""
        pass
    
    @abstractmethod
    async def send_bulk_email(self, messages: List[EmailMessage]) -> List[str]:
        """Send multiple emails and return list of message IDs."""
        pass
    
    @abstractmethod
    async def get_email_status(self, message_id: str) -> Optional[EmailStatus]:
        """Get status of a sent email."""
        pass
    
    @abstractmethod
    async def get_email_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> EmailStats:
        """Get email statistics."""
        pass
    
    @abstractmethod
    async def create_template(self, template: EmailTemplate) -> str:
        """Create an email template and return template ID."""
        pass
    
    @abstractmethod
    async def get_template(self, template_id: str) -> Optional[EmailTemplate]:
        """Get email template by ID."""
        pass
    
    @abstractmethod
    async def update_template(self, template_id: str, template: EmailTemplate) -> bool:
        """Update an email template."""
        pass
    
    @abstractmethod
    async def delete_template(self, template_id: str) -> bool:
        """Delete an email template."""
        pass
    
    @abstractmethod
    async def list_templates(self) -> List[EmailTemplate]:
        """List all email templates."""
        pass
    
    @abstractmethod
    async def send_template_email(
        self,
        template_id: str,
        to: List[str],
        template_data: Dict[str, Any],
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> str:
        """Send email using a template."""
        pass
    
    @abstractmethod
    async def add_to_suppression_list(self, email: str, reason: str = "unsubscribe") -> bool:
        """Add email to suppression list."""
        pass
    
    @abstractmethod
    async def remove_from_suppression_list(self, email: str) -> bool:
        """Remove email from suppression list."""
        pass
    
    @abstractmethod
    async def check_suppression_list(self, email: str) -> bool:
        """Check if email is in suppression list."""
        pass
    
    async def validate_email(self, email: str) -> bool:
        """Validate email address format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def send_simple_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        content: str,
        from_email: Optional[str] = None,
        html_content: Optional[str] = None
    ) -> str:
        """Send a simple email."""
        if isinstance(to, str):
            to = [to]
        
        message = EmailMessage(
            to=to,
            subject=subject,
            content=content,
            from_email=from_email,
            html_content=html_content
        )
        
        return await self.send_email(message)
    
    async def send_notification_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        content: str,
        priority: EmailPriority = EmailPriority.HIGH,
        tags: Optional[List[str]] = None
    ) -> str:
        """Send a notification email with high priority."""
        if isinstance(to, str):
            to = [to]
        
        message = EmailMessage(
            to=to,
            subject=subject,
            content=content,
            priority=priority,
            tags=tags or ["notification"]
        )
        
        return await self.send_email(message)
    
    async def send_password_reset_email(
        self,
        to: str,
        reset_link: str,
        user_name: Optional[str] = None
    ) -> str:
        """Send password reset email."""
        subject = "Password Reset Request"
        
        content = f"""
        Hello{' ' + user_name if user_name else ''},
        
        You have requested to reset your password. Please click the link below to reset your password:
        
        {reset_link}
        
        This link will expire in 24 hours.
        
        If you did not request this password reset, please ignore this email.
        
        Best regards,
        The BDC Team
        """
        
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello{' ' + user_name if user_name else ''},</p>
            <p>You have requested to reset your password. Please click the button below to reset your password:</p>
            <p><a href="{reset_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you did not request this password reset, please ignore this email.</p>
            <p>Best regards,<br>The BDC Team</p>
        </body>
        </html>
        """
        
        message = EmailMessage(
            to=[to],
            subject=subject,
            content=content,
            html_content=html_content,
            tags=["password-reset", "security"],
            priority=EmailPriority.HIGH
        )
        
        return await self.send_email(message)
    
    async def send_welcome_email(
        self,
        to: str,
        user_name: str,
        login_link: Optional[str] = None
    ) -> str:
        """Send welcome email to new user."""
        subject = f"Welcome to BDC, {user_name}!"
        
        content = f"""
        Hello {user_name},
        
        Welcome to BDC! We're excited to have you on board.
        
        {'You can log in to your account here: ' + login_link if login_link else ''}
        
        If you have any questions, please don't hesitate to contact our support team.
        
        Best regards,
        The BDC Team
        """
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to BDC!</h2>
            <p>Hello {user_name},</p>
            <p>Welcome to BDC! We're excited to have you on board.</p>
            {f'<p><a href="{login_link}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login to Your Account</a></p>' if login_link else ''}
            <p>If you have any questions, please don't hesitate to contact our support team.</p>
            <p>Best regards,<br>The BDC Team</p>
        </body>
        </html>
        """
        
        message = EmailMessage(
            to=[to],
            subject=subject,
            content=content,
            html_content=html_content,
            tags=["welcome", "onboarding"],
            priority=EmailPriority.NORMAL
        )
        
        return await self.send_email(message)
    
    async def process_webhook_event(self, payload: Dict[str, Any]) -> List[EmailEvent]:
        """Process webhook event from email service."""
        # Default implementation - should be overridden by providers
        return []
    
    def _sanitize_email_content(self, content: str) -> str:
        """Sanitize email content to prevent issues."""
        # Remove or escape potentially problematic characters
        # This is a basic implementation
        return content.replace('\r\n', '\n').replace('\r', '\n')
    
    def _validate_email_list(self, emails: List[str]) -> List[str]:
        """Validate and filter email list."""
        valid_emails = []
        for email in emails:
            if self.validate_email(email):
                valid_emails.append(email.lower().strip())
            else:
                self.logger.warning(f"Invalid email address: {email}")
        return valid_emails