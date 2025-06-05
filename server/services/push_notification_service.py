"""
Push Notification Service for BDC PWA
Handles web push notifications using VAPID keys and the Web Push Protocol
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pywebpush import webpush, WebPushException
import jwt
from urllib.parse import urlparse

from app.extensions import db
from models.notification import Notification
from models.user import User


logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for managing web push notifications"""
    
    def __init__(self, vapid_private_key: str = None, vapid_public_key: str = None, vapid_claims: dict = None):
        self.vapid_private_key = vapid_private_key
        self.vapid_public_key = vapid_public_key
        self.vapid_claims = vapid_claims or {}
        
        # Default notification settings
        self.default_options = {
            'ttl': 3600,  # Time to live in seconds
            'urgency': 'normal',  # low, normal, high
            'timeout': 30  # Request timeout
        }
    
    def subscribe_user(self, user_id: int, subscription_data: dict) -> bool:
        """
        Subscribe a user to push notifications
        
        Args:
            user_id: User ID
            subscription_data: Push subscription data from browser
            
        Returns:
            bool: Success status
        """
        try:
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return False
            
            # Validate subscription data
            if not self._validate_subscription(subscription_data):
                logger.error("Invalid subscription data")
                return False
            
            # Store subscription in user preferences
            user_preferences = getattr(user, 'push_subscription', {})
            user_preferences.update({
                'endpoint': subscription_data.get('endpoint'),
                'keys': subscription_data.get('keys', {}),
                'subscribed_at': datetime.utcnow().isoformat(),
                'active': True
            })
            
            # Update user model (assuming there's a push_subscription field)
            # This would need to be added to the User model
            setattr(user, 'push_subscription', user_preferences)
            db.session.commit()
            
            logger.info(f"User {user_id} subscribed to push notifications")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe user {user_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def unsubscribe_user(self, user_id: int) -> bool:
        """
        Unsubscribe a user from push notifications
        
        Args:
            user_id: User ID
            
        Returns:
            bool: Success status
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Mark subscription as inactive
            user_preferences = getattr(user, 'push_subscription', {})
            user_preferences['active'] = False
            user_preferences['unsubscribed_at'] = datetime.utcnow().isoformat()
            
            setattr(user, 'push_subscription', user_preferences)
            db.session.commit()
            
            logger.info(f"User {user_id} unsubscribed from push notifications")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe user {user_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def send_notification(
        self, 
        user_id: int, 
        title: str, 
        body: str, 
        data: dict = None,
        options: dict = None
    ) -> bool:
        """
        Send a push notification to a specific user
        
        Args:
            user_id: Target user ID
            title: Notification title
            body: Notification body
            data: Additional notification data
            options: Push notification options
            
        Returns:
            bool: Success status
        """
        try:
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return False
            
            subscription = getattr(user, 'push_subscription', {})
            if not subscription.get('active', False):
                logger.warning(f"User {user_id} not subscribed to push notifications")
                return False
            
            # Prepare notification payload
            payload = {
                'title': title,
                'body': body,
                'icon': '/icons/icon-192x192.png',
                'badge': '/icons/badge-72x72.png',
                'data': data or {},
                'timestamp': datetime.utcnow().isoformat(),
                'actions': [
                    {'action': 'view', 'title': 'View'},
                    {'action': 'dismiss', 'title': 'Dismiss'}
                ]
            }
            
            # Merge options
            push_options = {**self.default_options, **(options or {})}
            
            # Send push notification
            response = webpush(
                subscription_info={
                    'endpoint': subscription['endpoint'],
                    'keys': subscription['keys']
                },
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims,
                **push_options
            )
            
            # Store notification in database
            notification = Notification(
                user_id=user_id,
                title=title,
                message=body,
                type='push',
                data=data,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            db.session.commit()
            
            logger.info(f"Push notification sent to user {user_id}: {title}")
            return True
            
        except WebPushException as e:
            logger.error(f"Web push failed for user {user_id}: {str(e)}")
            
            # Handle subscription expiration
            if e.response and e.response.status_code in [410, 413]:
                self._handle_expired_subscription(user_id)
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def send_bulk_notification(
        self, 
        user_ids: List[int], 
        title: str, 
        body: str, 
        data: dict = None,
        options: dict = None
    ) -> Dict[str, Any]:
        """
        Send push notifications to multiple users
        
        Args:
            user_ids: List of target user IDs
            title: Notification title
            body: Notification body
            data: Additional notification data
            options: Push notification options
            
        Returns:
            dict: Results summary
        """
        results = {
            'total': len(user_ids),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for user_id in user_ids:
            try:
                success = self.send_notification(user_id, title, body, data, options)
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"User {user_id}: {str(e)}")
        
        logger.info(f"Bulk notification sent: {results['sent']}/{results['total']} successful")
        return results
    
    def send_notification_by_role(
        self, 
        role: str, 
        title: str, 
        body: str, 
        data: dict = None,
        options: dict = None
    ) -> Dict[str, Any]:
        """
        Send push notifications to all users with a specific role
        
        Args:
            role: Target user role
            title: Notification title
            body: Notification body
            data: Additional notification data
            options: Push notification options
            
        Returns:
            dict: Results summary
        """
        try:
            # Get users with the specified role who have push subscriptions
            users = User.query.filter(
                User.role == role,
                User.push_subscription.isnot(None)
            ).all()
            
            user_ids = [user.id for user in users if 
                       getattr(user, 'push_subscription', {}).get('active', False)]
            
            return self.send_bulk_notification(user_ids, title, body, data, options)
            
        except Exception as e:
            logger.error(f"Failed to send notification by role {role}: {str(e)}")
            return {
                'total': 0,
                'sent': 0,
                'failed': 0,
                'errors': [str(e)]
            }
    
    def get_user_subscription(self, user_id: int) -> Optional[dict]:
        """Get user's push subscription details"""
        try:
            user = User.query.get(user_id)
            if user:
                return getattr(user, 'push_subscription', None)
            return None
        except Exception as e:
            logger.error(f"Failed to get subscription for user {user_id}: {str(e)}")
            return None
    
    def get_subscription_stats(self) -> Dict[str, int]:
        """Get push notification subscription statistics"""
        try:
            total_users = User.query.count()
            
            # This would need proper database schema to work correctly
            subscribed_users = User.query.filter(
                User.push_subscription.isnot(None)
            ).count()
            
            return {
                'total_users': total_users,
                'subscribed_users': subscribed_users,
                'subscription_rate': round((subscribed_users / total_users) * 100, 2) if total_users > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to get subscription stats: {str(e)}")
            return {'total_users': 0, 'subscribed_users': 0, 'subscription_rate': 0}
    
    def _validate_subscription(self, subscription_data: dict) -> bool:
        """Validate push subscription data format"""
        required_fields = ['endpoint', 'keys']
        if not all(field in subscription_data for field in required_fields):
            return False
        
        keys = subscription_data.get('keys', {})
        required_keys = ['p256dh', 'auth']
        if not all(key in keys for key in required_keys):
            return False
        
        # Validate endpoint URL
        try:
            parsed = urlparse(subscription_data['endpoint'])
            if not parsed.scheme or not parsed.netloc:
                return False
        except Exception:
            return False
        
        return True
    
    def _handle_expired_subscription(self, user_id: int):
        """Handle expired or invalid subscription"""
        try:
            user = User.query.get(user_id)
            if user:
                subscription = getattr(user, 'push_subscription', {})
                subscription['active'] = False
                subscription['expired_at'] = datetime.utcnow().isoformat()
                setattr(user, 'push_subscription', subscription)
                db.session.commit()
                
                logger.info(f"Marked subscription as expired for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to handle expired subscription for user {user_id}: {str(e)}")


# Notification templates for common scenarios
class NotificationTemplates:
    """Pre-defined notification templates for common use cases"""
    
    @staticmethod
    def evaluation_available(beneficiary_name: str, evaluation_title: str) -> dict:
        return {
            'title': 'New Evaluation Available',
            'body': f'A new evaluation "{evaluation_title}" is available for {beneficiary_name}',
            'data': {
                'type': 'evaluation',
                'action': 'view_evaluation',
                'url': '/evaluations'
            }
        }
    
    @staticmethod
    def appointment_reminder(appointment_time: str, participant_name: str) -> dict:
        return {
            'title': 'Appointment Reminder',
            'body': f'You have an appointment with {participant_name} at {appointment_time}',
            'data': {
                'type': 'appointment',
                'action': 'view_calendar',
                'url': '/calendar'
            }
        }
    
    @staticmethod
    def message_received(sender_name: str, message_preview: str) -> dict:
        return {
            'title': f'Message from {sender_name}',
            'body': message_preview[:100] + ('...' if len(message_preview) > 100 else ''),
            'data': {
                'type': 'message',
                'action': 'view_message',
                'url': '/messages'
            }
        }
    
    @staticmethod
    def system_update(version: str, features: List[str]) -> dict:
        return {
            'title': 'App Update Available',
            'body': f'Version {version} is available with new features',
            'data': {
                'type': 'update',
                'action': 'update_app',
                'features': features
            }
        }
    
    @staticmethod
    def document_shared(document_name: str, shared_by: str) -> dict:
        return {
            'title': 'Document Shared',
            'body': f'{shared_by} shared "{document_name}" with you',
            'data': {
                'type': 'document',
                'action': 'view_document',
                'url': '/documents'
            }
        }


# Example usage and configuration
def create_push_service(app_config):
    """Create and configure push notification service"""
    return PushNotificationService(
        vapid_private_key=app_config.get('VAPID_PRIVATE_KEY'),
        vapid_public_key=app_config.get('VAPID_PUBLIC_KEY'),
        vapid_claims={
            'sub': f"mailto:{app_config.get('VAPID_CLAIM_EMAIL', 'admin@bdc.com')}"
        }
    )