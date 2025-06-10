"""Email service module."""

import os
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import SignatureExpired, BadTimeSignature

from app.extensions import mail
import logging

logger = logging.getLogger(__name__)


def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body=None, sender=None, attachments=None):
    """
    Send an email.
    
    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        text_body (str): Email body in plain text
        html_body (str): Email body in HTML
        sender (str): Sender email address
        attachments (list): List of attachments (tuples of filename, media_type, data)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        app = current_app._get_current_object()
        sender = sender or app.config['MAIL_DEFAULT_SENDER']
        
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        
        if html_body:
            msg.html = html_body
        
        if attachments:
            for attachment in attachments:
                filename, media_type, data = attachment
                msg.attach(filename, media_type, data)
        
        # Send email asynchronously
        Thread(target=send_async_email, args=(app, msg)).start()
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


class EmailService:
    """Email service class for sending various types of emails."""
    
    @staticmethod
    def send_email(to_email, subject, html_body=None, text_body=None, attachments=None):
        """Send an email using the configured mail service."""
        try:
            recipients = [to_email] if isinstance(to_email, str) else to_email
            
            # Use the global send_email function
            return send_email(
                subject=subject,
                recipients=recipients,
                text_body=text_body or "",
                html_body=html_body,
                attachments=attachments
            )
        except Exception as e:
            logger.error(f"EmailService.send_email failed: {str(e)}")
            return False


def generate_email_token(data, salt=None, expires_in=3600):
    """
    Generate a secure token for email verification, password reset, etc.
    
    Args:
        data: Data to encode in the token
        salt (str): Secret salt for the token
        expires_in (int): Token expiration time in seconds
        
    Returns:
        str: Secure token
    """
    salt = salt or current_app.config.get('SECRET_KEY', 'email-salt')
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(data, salt=salt)


def verify_email_token(token, salt=None, expires_in=3600):
    """
    Verify a secure token.
    
    Args:
        token (str): Token to verify
        salt (str): Secret salt used for the token
        expires_in (int): Token expiration time in seconds
        
    Returns:
        dict: Decoded data or None if verification fails
    """
    salt = salt or current_app.config.get('SECRET_KEY', 'email-salt')
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    try:
        data = serializer.loads(token, salt=salt, max_age=expires_in)
        return data
    except (SignatureExpired, BadTimeSignature):
        return None


def send_password_reset_email(user):
    """
    Send a password reset email to a user.
    
    Args:
        user: User to send the email to
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Generate a secure token
    token = generate_email_token({'user_id': user.id}, salt='password-reset-salt', expires_in=3600)
    
    # Build the password reset link
    reset_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
    reset_url = f"{reset_url}/reset-password?token={token}"
    
    # Prepare email content
    subject = "Reset Your Password"
    
    text_body = f"""
    Dear {user.first_name} {user.last_name},
    
    To reset your password, please click on the following link:
    
    {reset_url}
    
    If you did not request a password reset, please ignore this email.
    
    The link will expire in 1 hour.
    
    Best regards,
    BDC Team
    """
    
    html_body = f"""
    <p>Dear {user.first_name} {user.last_name},</p>
    <p>To reset your password, please click on the following link:</p>
    <p><a href="{reset_url}">Reset Your Password</a></p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>The link will expire in 1 hour.</p>
    <p>Best regards,<br>BDC Team</p>
    """
    
    # Send the email
    return send_email(
        subject=subject,
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )


def send_welcome_email(user):
    """
    Send a welcome email to a new user.
    
    Args:
        user: User to send the email to
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Prepare email content
    subject = "Welcome to BDC"
    
    text_body = f"""
    Dear {user.first_name} {user.last_name},
    
    Welcome to BDC! We're excited to have you on board.
    
    Your account has been created successfully.
    
    Best regards,
    BDC Team
    """
    
    html_body = f"""
    <p>Dear {user.first_name} {user.last_name},</p>
    <p>Welcome to BDC! We're excited to have you on board.</p>
    <p>Your account has been created successfully.</p>
    <p>Best regards,<br>BDC Team</p>
    """
    
    # Send the email
    return send_email(
        subject=subject,
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )


def send_notification_email(user, notification):
    """
    Send a notification email to a user.
    
    Args:
        user: User to send the email to
        notification: Notification details
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Prepare email content
    subject = notification.get('subject', 'New Notification')
    
    text_body = f"""
    Dear {user.first_name} {user.last_name},
    
    {notification.get('message', 'You have a new notification.')}
    
    Best regards,
    BDC Team
    """
    
    html_body = f"""
    <p>Dear {user.first_name} {user.last_name},</p>
    <p>{notification.get('message', 'You have a new notification.')}</p>
    <p>Best regards,<br>BDC Team</p>
    """
    
    # Send the email
    return send_email(
        subject=subject,
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )


class EmailService:
    """Email service for sending various types of emails."""
    
    @staticmethod
    def send_recurring_appointment_created(email, data):
        """Send email when a recurring appointment series is created."""
        subject = f"Recurring Appointment Created: {data['title']}"
        
        text_body = f"""
Dear {data['beneficiary_name']},

A recurring appointment series has been created for you:

Title: {data['title']}
Trainer: {data['trainer_name']}
Frequency: {data['frequency'].capitalize()}
Starting: {data['start_date']}
Number of appointments: {data['appointment_count']}

Please log in to your account to view the full schedule.

Best regards,
BDC Team
        """
        
        html_body = f"""
<h2>Recurring Appointment Created</h2>
<p>Dear {data['beneficiary_name']},</p>
<p>A recurring appointment series has been created for you:</p>
<ul>
    <li><strong>Title:</strong> {data['title']}</li>
    <li><strong>Trainer:</strong> {data['trainer_name']}</li>
    <li><strong>Frequency:</strong> {data['frequency'].capitalize()}</li>
    <li><strong>Starting:</strong> {data['start_date']}</li>
    <li><strong>Number of appointments:</strong> {data['appointment_count']}</li>
</ul>
<p>Please log in to your account to view the full schedule.</p>
<p>Best regards,<br>BDC Team</p>
        """
        
        return send_email(
            subject=subject,
            recipients=[email],
            text_body=text_body,
            html_body=html_body
        )
    
    @staticmethod
    def send_recurring_appointment_cancelled(email, data):
        """Send email when a recurring appointment series is cancelled."""
        subject = f"Recurring Appointments Cancelled: {data['title']}"
        
        text_body = f"""
Dear {data['beneficiary_name']},

Your recurring appointment series has been cancelled:

Title: {data['title']}
Number of cancelled appointments: {data['cancelled_count']}
Reason: {data['reason']}

If you have any questions, please contact your trainer.

Best regards,
BDC Team
        """
        
        html_body = f"""
<h2>Recurring Appointments Cancelled</h2>
<p>Dear {data['beneficiary_name']},</p>
<p>Your recurring appointment series has been cancelled:</p>
<ul>
    <li><strong>Title:</strong> {data['title']}</li>
    <li><strong>Number of cancelled appointments:</strong> {data['cancelled_count']}</li>
    <li><strong>Reason:</strong> {data['reason']}</li>
</ul>
<p>If you have any questions, please contact your trainer.</p>
<p>Best regards,<br>BDC Team</p>
        """
        
        return send_email(
            subject=subject,
            recipients=[email],
            text_body=text_body,
            html_body=html_body
        )