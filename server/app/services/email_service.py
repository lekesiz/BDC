"""Email service module."""

import os
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import SignatureExpired, BadTimeSignature

from app.extensions import mail


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
        current_app.logger.error(f"Email sending error: {str(e)}")
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