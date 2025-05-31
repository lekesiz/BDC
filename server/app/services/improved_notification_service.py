"""Improved notification service with dependency injection."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging

from app.services.interfaces.notification_service_interface import INotificationService
from app.repositories.interfaces.notification_repository_interface import INotificationRepository
from app.extensions import db

logger = logging.getLogger(__name__)


class ImprovedNotificationService(INotificationService):
    """Improved notification service with dependency injection."""
    
    def __init__(self, notification_repository: INotificationRepository, db_session: Optional[Session] = None):
        """Initialize service with dependencies.
        
        Args:
            notification_repository: Notification repository implementation
            db_session: Database session (optional)
        """
        self.notification_repository = notification_repository
        self.db_session = db_session or db.session
    
    def create_notification(self, user_id: int, type: str, title: str, message: str, 
                           data: Optional[Dict[str, Any]] = None, related_id: Optional[int] = None, 
                           related_type: Optional[str] = None, sender_id: Optional[int] = None, 
                           priority: str = 'normal', send_email: bool = False, 
                           tenant_id: Optional[int] = None) -> Optional[Any]:
        """Create a new notification for a user."""
        try:
            notification_data = {
                'user_id': user_id,
                'title': title,
                'message': message,
                'type': type,
                'priority': priority,
                'read': False,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            if sender_id:
                notification_data['sender_id'] = sender_id
            if data:
                notification_data['data'] = data
            if related_id:
                notification_data['related_id'] = related_id
            if related_type:
                notification_data['related_type'] = related_type
            if tenant_id:
                notification_data['tenant_id'] = tenant_id
            
            notification = self.notification_repository.create(**notification_data)
            self.db_session.commit()
            
            # TODO: Implement email sending if send_email is True
            
            logger.info(f"Created notification {notification.id} for user {user_id}")
            return notification
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create notification: {str(e)}")
            return None
    
    def create_bulk_notifications(self, user_ids: List[int], type: str, title: str, message: str,
                                 data: Optional[Dict[str, Any]] = None, related_id: Optional[int] = None,
                                 related_type: Optional[str] = None, sender_id: Optional[int] = None,
                                 priority: str = 'normal', send_email: bool = False,
                                 tenant_id: Optional[int] = None) -> List[Any]:
        """Create notifications for multiple users."""
        notifications = []
        for user_id in user_ids:
            notification = self.create_notification(
                user_id=user_id, type=type, title=title, message=message,
                data=data, related_id=related_id, related_type=related_type,
                sender_id=sender_id, priority=priority, send_email=send_email,
                tenant_id=tenant_id
            )
            if notification:
                notifications.append(notification)
        return notifications
    
    def create_role_notification(self, role: str, type: str, title: str, message: str,
                                data: Optional[Dict[str, Any]] = None, related_id: Optional[int] = None,
                                related_type: Optional[str] = None, sender_id: Optional[int] = None,
                                priority: str = 'normal', send_email: bool = False,
                                tenant_id: Optional[int] = None) -> List[Any]:
        """Create notification for all users with a specific role."""
        try:
            # Get all users with the specified role
            from app.models import User
            query = self.db_session.query(User).filter_by(role=role, is_active=True)
            
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            
            users = query.all()
            user_ids = [user.id for user in users]
            
            return self.create_bulk_notifications(
                user_ids=user_ids, type=type, title=title, message=message,
                data=data, related_id=related_id, related_type=related_type,
                sender_id=sender_id, priority=priority, send_email=send_email,
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.error(f"Failed to create role notification for role {role}: {str(e)}")
            return []
    
    def create_tenant_notification(self, tenant_id: int, type: str, title: str, message: str,
                                  data: Optional[Dict[str, Any]] = None, related_id: Optional[int] = None,
                                  related_type: Optional[str] = None, sender_id: Optional[int] = None,
                                  priority: str = 'normal', send_email: bool = False,
                                  exclude_roles: Optional[List[str]] = None) -> List[Any]:
        """Create notification for all users in a tenant."""
        try:
            # Get all users in the tenant
            from app.models import User
            query = self.db_session.query(User).filter_by(tenant_id=tenant_id, is_active=True)
            
            if exclude_roles:
                query = query.filter(~User.role.in_(exclude_roles))
            
            users = query.all()
            user_ids = [user.id for user in users]
            
            return self.create_bulk_notifications(
                user_ids=user_ids, type=type, title=title, message=message,
                data=data, related_id=related_id, related_type=related_type,
                sender_id=sender_id, priority=priority, send_email=send_email,
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.error(f"Failed to create tenant notification for tenant {tenant_id}: {str(e)}")
            return []
    
    def get_unread_count(self, user_id: int, type: Optional[str] = None) -> int:
        """Get count of unread notifications for a user."""
        try:
            return self.notification_repository.get_unread_count(user_id, type)
        except Exception as e:
            logger.error(f"Failed to get unread count for user {user_id}: {str(e)}")
            return 0
    
    def get_notification(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """Get notification by ID."""
        try:
            notification = self.notification_repository.find_by_id(notification_id)
            if notification:
                return notification.to_dict() if hasattr(notification, 'to_dict') else self._serialize_notification(notification)
            return None
        except Exception as e:
            logger.error(f"Failed to get notification {notification_id}: {str(e)}")
            return None
    
    def get_user_notifications(self, user_id: int, limit: int = 20, offset: int = 0,
                              unread_only: bool = False, type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        try:
            notifications = self.notification_repository.get_user_notifications(
                user_id, limit, offset, unread_only, type
            )
            return [notification.to_dict() if hasattr(notification, 'to_dict') else self._serialize_notification(notification) 
                   for notification in notifications]
        except Exception as e:
            logger.error(f"Failed to get notifications for user {user_id}: {str(e)}")
            return []
    
    def get_unread_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        """Get unread notifications for a user."""
        try:
            notifications = self.notification_repository.find_unread_by_user_id(user_id)
            return [notification.to_dict() if hasattr(notification, 'to_dict') else self._serialize_notification(notification) 
                   for notification in notifications]
        except Exception as e:
            logger.error(f"Failed to get unread notifications for user {user_id}: {str(e)}")
            return []
    
    def get_notifications_by_type(self, user_id: int, notification_type: str) -> List[Dict[str, Any]]:
        """Get notifications by type for a user."""
        try:
            notifications = self.notification_repository.find_by_type(user_id, notification_type)
            return [notification.to_dict() if hasattr(notification, 'to_dict') else self._serialize_notification(notification) 
                   for notification in notifications]
        except Exception as e:
            logger.error(f"Failed to get notifications by type {notification_type} for user {user_id}: {str(e)}")
            return []
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        try:
            success = self.notification_repository.mark_as_read(notification_id, user_id)
            if success:
                self.db_session.commit()
                logger.info(f"Marked notification {notification_id} as read")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to mark notification {notification_id} as read: {str(e)}")
            return False
    
    def mark_multiple_as_read(self, notification_ids: List[int]) -> int:
        """Mark multiple notifications as read."""
        try:
            count = self.notification_repository.mark_multiple_as_read(notification_ids)
            if count > 0:
                self.db_session.commit()
                logger.info(f"Marked {count} notifications as read")
            return count
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to mark multiple notifications as read: {str(e)}")
            return 0
    
    def mark_all_as_read(self, user_id: int, type: Optional[str] = None) -> int:
        """Mark all notifications as read for a user."""
        try:
            count = self.notification_repository.mark_all_as_read(user_id, type)
            if count > 0:
                self.db_session.commit()
                logger.info(f"Marked all notifications as read for user {user_id}")
            return count
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to mark all notifications as read for user {user_id}: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        try:
            success = self.notification_repository.delete(notification_id, user_id)
            if success:
                self.db_session.commit()
                logger.info(f"Deleted notification {notification_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete notification {notification_id}: {str(e)}")
            return False
    
    def delete_multiple_notifications(self, notification_ids: List[int]) -> int:
        """Delete multiple notifications."""
        try:
            count = self.notification_repository.delete_multiple(notification_ids)
            if count > 0:
                self.db_session.commit()
                logger.info(f"Deleted {count} notifications")
            return count
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete multiple notifications: {str(e)}")
            return 0
    
    def delete_old_notifications(self, days: int = 30) -> int:
        """Delete notifications older than specified days."""
        try:
            count = self.notification_repository.delete_old_notifications(days)
            if count > 0:
                self.db_session.commit()
                logger.info(f"Deleted {count} old notifications")
            return count
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete old notifications: {str(e)}")
            return 0
    
    def get_notification_count(self, user_id: int, unread_only: bool = False) -> int:
        """Get notification count for a user."""
        try:
            return self.notification_repository.count_by_user_id(user_id, unread_only)
        except Exception as e:
            logger.error(f"Failed to get notification count for user {user_id}: {str(e)}")
            return 0
    
    def send_bulk_notification(self, user_ids: List[int], title: str, message: str,
                              notification_type: str = 'info', sender_id: Optional[int] = None,
                              **kwargs) -> List[Dict[str, Any]]:
        """Send notification to multiple users."""
        created_notifications = []
        try:
            for user_id in user_ids:
                notification = self.create_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    sender_id=sender_id,
                    **kwargs
                )
                if notification:
                    created_notifications.append(notification)
            
            logger.info(f"Created {len(created_notifications)} bulk notifications")
            return created_notifications
            
        except Exception as e:
            logger.error(f"Failed to send bulk notification: {str(e)}")
            return created_notifications
    
    def create_appointment_notification(self, user_id: int, appointment_id: int,
                                      title: str, message: str) -> Optional[Dict[str, Any]]:
        """Create appointment-related notification."""
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type='appointment',
            related_id=appointment_id,
            related_type='appointment',
            priority='high'
        )
    
    def create_evaluation_notification(self, user_id: int, evaluation_id: int,
                                     title: str, message: str, sender_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Create evaluation-related notification."""
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type='evaluation',
            sender_id=sender_id,
            related_id=evaluation_id,
            related_type='evaluation',
            priority='normal'
        )
    
    def _serialize_notification(self, notification) -> Dict[str, Any]:
        """Serialize notification for API response."""
        return {
            'id': notification.id,
            'user_id': getattr(notification, 'user_id', None),
            'sender_id': getattr(notification, 'sender_id', None),
            'title': getattr(notification, 'title', ''),
            'message': getattr(notification, 'message', ''),
            'type': getattr(notification, 'type', 'info'),
            'link': getattr(notification, 'link', ''),
            'data': getattr(notification, 'data', None),
            'related_id': getattr(notification, 'related_id', None),
            'related_type': getattr(notification, 'related_type', None),
            'priority': getattr(notification, 'priority', 'normal'),
            'tenant_id': getattr(notification, 'tenant_id', None),
            'read': getattr(notification, 'read', False),
            'read_at': getattr(notification, 'read_at', None),
            'created_at': getattr(notification, 'created_at', datetime.now()).isoformat(),
            'updated_at': getattr(notification, 'updated_at', datetime.now()).isoformat()
        }