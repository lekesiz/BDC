"""
Notification utilities for BDC application
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from flask import current_app
import requests

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str, 
               html_body: Optional[str] = None,
               from_email: Optional[str] = None,
               attachments: Optional[List[Dict[str, Any]]] = None):
    """Send email notification"""
    try:
        # Get email configuration
        smtp_host = current_app.config.get('SMTP_HOST', 'localhost')
        smtp_port = current_app.config.get('SMTP_PORT', 587)
        smtp_user = current_app.config.get('SMTP_USER')
        smtp_password = current_app.config.get('SMTP_PASSWORD')
        smtp_use_tls = current_app.config.get('SMTP_USE_TLS', True)
        
        from_email = from_email or current_app.config.get('MAIL_FROM', 'noreply@bdc.com')
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to
        
        # Add text part
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                # TODO: Implement attachment handling
                pass
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_use_tls:
                server.starttls()
            
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {to}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return False


def send_slack_message(webhook_url: str, message: Dict[str, Any]):
    """Send message to Slack webhook"""
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()
        logger.info("Slack message sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send Slack message: {str(e)}")
        return False


def send_sms(to: str, message: str):
    """Send SMS notification using Twilio"""
    try:
        # Get Twilio configuration
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        from_number = current_app.config.get('TWILIO_FROM_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            logger.warning("Twilio credentials not configured")
            return False
        
        from twilio.rest import Client
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        
        logger.info(f"SMS sent successfully to {to}: {message.sid}")
        return True
        
    except ImportError:
        logger.warning("Twilio library not installed")
        return False
    except Exception as e:
        logger.error(f"Failed to send SMS to {to}: {str(e)}")
        return False


def send_push_notification(user_id: int, title: str, body: str, 
                          data: Optional[Dict[str, Any]] = None):
    """Send push notification to user device"""
    try:
        # Get push notification service configuration
        fcm_server_key = current_app.config.get('FCM_SERVER_KEY')
        
        if not fcm_server_key:
            logger.warning("FCM server key not configured")
            return False
        
        # Get user's device tokens from database
        # TODO: Implement device token retrieval
        device_tokens = []
        
        if not device_tokens:
            logger.warning(f"No device tokens found for user {user_id}")
            return False
        
        # Send via Firebase Cloud Messaging
        headers = {
            'Authorization': f'key={fcm_server_key}',
            'Content-Type': 'application/json'
        }
        
        for token in device_tokens:
            payload = {
                'to': token,
                'notification': {
                    'title': title,
                    'body': body
                }
            }
            
            if data:
                payload['data'] = data
            
            response = requests.post(
                'https://fcm.googleapis.com/fcm/send',
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Push notification sent to user {user_id}")
            else:
                logger.error(f"Failed to send push notification: {response.text}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send push notification: {str(e)}")
        return False


def send_notification(user_id: int, notification_type: str, 
                     subject: str, message: str,
                     data: Optional[Dict[str, Any]] = None,
                     channels: Optional[List[str]] = None):
    """Send notification through multiple channels"""
    
    # Default channels if not specified
    if channels is None:
        channels = ['email', 'push']
    
    results = {}
    
    # Get user notification preferences
    # TODO: Load from user preferences
    user_email = None
    user_phone = None
    
    if 'email' in channels and user_email:
        results['email'] = send_email(
            to=user_email,
            subject=subject,
            body=message
        )
    
    if 'sms' in channels and user_phone:
        results['sms'] = send_sms(
            to=user_phone,
            message=f"{subject}: {message[:100]}"
        )
    
    if 'push' in channels:
        results['push'] = send_push_notification(
            user_id=user_id,
            title=subject,
            body=message,
            data=data
        )
    
    # Store notification in database
    try:
        from app.models import Notification
        from app.extensions import db
        
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=subject,
            message=message,
            data=data,
            channels=channels,
            results=results
        )
        
        db.session.add(notification)
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Failed to store notification in database: {str(e)}")
    
    return results


def send_bulk_notification(user_ids: List[int], notification_type: str,
                          subject: str, message: str,
                          data: Optional[Dict[str, Any]] = None,
                          channels: Optional[List[str]] = None):
    """Send notification to multiple users"""
    results = {}
    
    for user_id in user_ids:
        results[user_id] = send_notification(
            user_id=user_id,
            notification_type=notification_type,
            subject=subject,
            message=message,
            data=data,
            channels=channels
        )
    
    return results


def schedule_notification(user_id: int, notification_type: str,
                         subject: str, message: str,
                         scheduled_at: datetime,
                         data: Optional[Dict[str, Any]] = None,
                         channels: Optional[List[str]] = None):
    """Schedule a notification for future delivery"""
    try:
        from app.models import ScheduledNotification
        from app.extensions import db
        
        scheduled = ScheduledNotification(
            user_id=user_id,
            type=notification_type,
            title=subject,
            message=message,
            scheduled_at=scheduled_at,
            data=data,
            channels=channels
        )
        
        db.session.add(scheduled)
        db.session.commit()
        
        logger.info(f"Notification scheduled for user {user_id} at {scheduled_at}")
        return scheduled.id
        
    except Exception as e:
        logger.error(f"Failed to schedule notification: {str(e)}")
        return None