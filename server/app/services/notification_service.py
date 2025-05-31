"""Notification service module with dependency injection support."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from flask import current_app

from app.extensions import db
from app.realtime import emit_to_user, user_is_online, emit_to_role, emit_to_tenant
from app.services.email_service import send_notification_email
from app.services.interfaces.notification_service_interface import INotificationService
from app.models.notification import Notification
from app.repositories.interfaces.notification_repository_interface import INotificationRepository


class NotificationService(INotificationService):
    """Notification service for managing user notifications with dependency injection."""
    
    def __init__(self, notification_repository: INotificationRepository):
        """Initialize notification service with repository dependency."""
        self._notification_repository = notification_repository
    
    def create_notification(
        self, 
        user_id: int, 
        type: str, 
        title: str, 
        message: str, 
        data: Optional[Dict[str, Any]] = None, 
        related_id: Optional[int] = None, 
        related_type: Optional[str] = None, 
        sender_id: Optional[int] = None, 
        priority: str = 'normal', 
        send_email: bool = False, 
        tenant_id: Optional[int] = None
    ) -> Optional[Notification]:
        """
        Create a new notification.
        
        Args:
            user_id (int): The recipient user ID
            type (str): Notification type (e.g., 'appointment', 'message', 'system')
            title (str): Notification title
            message (str): Notification message
            data (dict): Additional data for the notification
            related_id (int): ID of the related entity (e.g., appointment ID)
            related_type (str): Type of the related entity (e.g., 'appointment')
            sender_id (int): The sender user ID (if applicable)
            priority (str): Notification priority ('low', 'normal', 'high', 'urgent')
            send_email (bool): Whether to send an email
            tenant_id (int): The tenant ID (if applicable)
            
        Returns:
            Notification: The created notification or None if creation fails
        """
        try:
            # Create notification using repository
            notification = self._notification_repository.create(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                data=data,
                related_id=related_id,
                related_type=related_type,
                sender_id=sender_id,
                priority=priority,
                tenant_id=tenant_id
            )
            
            if notification:
                # Send real-time notification if user is online
                if user_is_online(user_id):
                    emit_to_user(user_id, 'notification', notification.to_dict())
                
                # Send email if requested
                if send_email:
                    from app.models.user import User
                    user = User.query.get(user_id)
                    
                    if user and user.email:
                        send_notification_email(
                            user=user,
                            notification={
                                'subject': title,
                                'message': message
                            }
                        )
            
            return notification
            
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {str(e)}")
            return None
    
    def create_bulk_notifications(
        self,
        user_ids: List[int],
        type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        sender_id: Optional[int] = None,
        priority: str = 'normal',
        send_email: bool = False,
        tenant_id: Optional[int] = None
    ) -> List[Notification]:
        """
        Create notifications for multiple users.
        
        Args:
            user_ids (list): List of recipient user IDs
            type (str): Notification type
            title (str): Notification title
            message (str): Notification message
            data (dict): Additional data for the notification
            related_id (int): ID of the related entity
            related_type (str): Type of the related entity
            sender_id (int): The sender user ID
            priority (str): Notification priority
            send_email (bool): Whether to send emails
            tenant_id (int): The tenant ID
            
        Returns:
            list: List of created notifications
        """
        notifications = []
        
        for user_id in user_ids:
            notification = self.create_notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                data=data,
                related_id=related_id,
                related_type=related_type,
                sender_id=sender_id,
                priority=priority,
                send_email=send_email,
                tenant_id=tenant_id
            )
            
            if notification:
                notifications.append(notification)
        
        return notifications
    
    def create_role_notification(
        self,
        role: str,
        type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        sender_id: Optional[int] = None,
        priority: str = 'normal',
        send_email: bool = False,
        tenant_id: Optional[int] = None
    ) -> List[Notification]:
        """
        Create notification for users with a specific role.
        
        Args:
            role (str): User role (e.g., 'super_admin', 'tenant_admin', 'trainer')
            type (str): Notification type
            title (str): Notification title
            message (str): Notification message
            data (dict): Additional data for the notification
            related_id (int): ID of the related entity
            related_type (str): Type of the related entity
            sender_id (int): The sender user ID
            priority (str): Notification priority
            send_email (bool): Whether to send emails
            tenant_id (int): The tenant ID
            
        Returns:
            list: List of created notifications
        """
        try:
            # Get users with the specified role
            from app.models.user import User, user_tenant
            
            users = User.query.filter_by(role=role, is_active=True)
            
            if tenant_id:
                users = users.join(user_tenant).filter(user_tenant.c.tenant_id == tenant_id)
            
            user_ids = [user.id for user in users]
            
            # Create notifications
            notifications = self.create_bulk_notifications(
                user_ids=user_ids,
                type=type,
                title=title,
                message=message,
                data=data,
                related_id=related_id,
                related_type=related_type,
                sender_id=sender_id,
                priority=priority,
                send_email=send_email,
                tenant_id=tenant_id
            )
            
            # Also emit to role channel for real-time updates
            emit_to_role(role, 'notification', {
                'type': type,
                'title': title,
                'message': message,
                'data': data,
                'related_id': related_id,
                'related_type': related_type,
                'sender_id': sender_id,
                'priority': priority,
                'tenant_id': tenant_id,
                'created_at': datetime.now(timezone.utc).isoformat()
            })
            
            return notifications
            
        except Exception as e:
            current_app.logger.error(f"Error creating role notification: {str(e)}")
            return []
    
    def create_tenant_notification(
        self,
        tenant_id: int,
        type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        sender_id: Optional[int] = None,
        priority: str = 'normal',
        send_email: bool = False,
        exclude_roles: Optional[List[str]] = None
    ) -> List[Notification]:
        """
        Create notification for all users in a tenant.
        
        Args:
            tenant_id (int): The tenant ID
            type (str): Notification type
            title (str): Notification title
            message (str): Notification message
            data (dict): Additional data for the notification
            related_id (int): ID of the related entity
            related_type (str): Type of the related entity
            sender_id (int): The sender user ID
            priority (str): Notification priority
            send_email (bool): Whether to send emails
            exclude_roles (list): List of roles to exclude
            
        Returns:
            list: List of created notifications
        """
        try:
            # Get users in the tenant
            from app.models.user import User, user_tenant
            
            query = User.query.join(user_tenant).filter(
                user_tenant.c.tenant_id == tenant_id,
                User.is_active == True
            )
            
            if exclude_roles:
                query = query.filter(User.role.notin_(exclude_roles))
            
            user_ids = [user.id for user in query]
            
            # Create notifications
            notifications = self.create_bulk_notifications(
                user_ids=user_ids,
                type=type,
                title=title,
                message=message,
                data=data,
                related_id=related_id,
                related_type=related_type,
                sender_id=sender_id,
                priority=priority,
                send_email=send_email,
                tenant_id=tenant_id
            )
            
            # Also emit to tenant channel for real-time updates
            emit_to_tenant(tenant_id, 'notification', {
                'type': type,
                'title': title,
                'message': message,
                'data': data,
                'related_id': related_id,
                'related_type': related_type,
                'sender_id': sender_id,
                'priority': priority,
                'tenant_id': tenant_id,
                'created_at': datetime.now(timezone.utc).isoformat()
            })
            
            return notifications
            
        except Exception as e:
            current_app.logger.error(f"Error creating tenant notification: {str(e)}")
            return []
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id (int): The notification ID
            user_id (int): The user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self._notification_repository.mark_as_read(notification_id, user_id)
        except Exception as e:
            current_app.logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    def mark_all_as_read(self, user_id: int, type: Optional[str] = None) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id (int): The user ID
            type (str): Notification type to filter by
            
        Returns:
            int: Number of notifications updated
        """
        try:
            return self._notification_repository.mark_all_as_read(user_id, type)
        except Exception as e:
            current_app.logger.error(f"Error marking all notifications as read: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id (int): The notification ID
            user_id (int): The user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self._notification_repository.delete(notification_id, user_id)
        except Exception as e:
            current_app.logger.error(f"Error deleting notification: {str(e)}")
            return False
    
    def get_user_notifications(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
        type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.
        
        Args:
            user_id (int): The user ID
            limit (int): Maximum number of notifications to return
            offset (int): Offset for pagination
            unread_only (bool): Whether to return only unread notifications
            type (str): Notification type to filter by
            
        Returns:
            list: List of notifications
        """
        try:
            notifications = self._notification_repository.get_user_notifications(
                user_id, limit, offset, unread_only, type
            )
            return [notification.to_dict() for notification in notifications]
        except Exception as e:
            current_app.logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    def get_unread_count(self, user_id: int, type: Optional[str] = None) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id (int): The user ID
            type (str): Notification type to filter by
            
        Returns:
            int: Number of unread notifications
        """
        try:
            return self._notification_repository.get_unread_count(user_id, type)
        except Exception as e:
            current_app.logger.error(f"Error getting unread count: {str(e)}")
            return 0