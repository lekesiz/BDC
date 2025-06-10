"""
Email service integrations for BDC project.

Supports SendGrid and Mailgun email services.
"""

from .base_email import BaseEmailIntegration, EmailMessage, EmailAttachment, EmailTemplate, EmailStats
from .sendgrid_integration import SendGridIntegration
from .mailgun_integration import MailgunIntegration

__all__ = [
    'BaseEmailIntegration',
    'EmailMessage',
    'EmailAttachment',
    'EmailTemplate',
    'EmailStats',
    'SendGridIntegration',
    'MailgunIntegration'
]