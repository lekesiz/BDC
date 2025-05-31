"""Wrapper for NotificationService to provide static method compatibility."""

from flask import g
from typing import List, Optional, Dict, Any
from app.models.notification import Notification


class NotificationService:
    """Static wrapper for notification service to maintain backward compatibility."""
    
    @staticmethod
    def _get_service():
        """Get notification service instance from DI container."""
        if not hasattr(g, '_notification_service'):
            # Import here to avoid circular dependencies
            from app.repositories.notification_repository import NotificationRepository
            from app.services.notification_service import NotificationService as RealNotificationService
            from app.extensions import db
            
            # Create repository and service instances
            repository = NotificationRepository(db.session)
            g._notification_service = RealNotificationService(repository)
        return g._notification_service
    
    @classmethod
    def create_notification(
        cls,
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
        """Create a new notification."""
        service = cls._get_service()
        return service.create_notification(
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
    
    @classmethod
    def create_bulk_notifications(
        cls,
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
        """Create notifications for multiple users."""
        service = cls._get_service()
        return service.create_bulk_notifications(
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
    
    @classmethod
    def create_role_notification(
        cls,
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
        """Create notification for users with a specific role."""
        service = cls._get_service()
        return service.create_role_notification(
            role=role,
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
    
    @classmethod
    def mark_as_read(cls, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        service = cls._get_service()
        return service.mark_as_read(notification_id, user_id)
    
    @classmethod
    def mark_all_as_read(cls, user_id: int, type: Optional[str] = None) -> int:
        """Mark all notifications as read for a user."""
        service = cls._get_service()
        return service.mark_all_as_read(user_id, type)
    
    @classmethod
    def delete_notification(cls, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        service = cls._get_service()
        return service.delete_notification(notification_id, user_id)
    
    @classmethod
    def get_user_notifications(
        cls,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
        type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        service = cls._get_service()
        return service.get_user_notifications(
            user_id=user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
            type=type
        )
    
    @classmethod
    def get_unread_count(cls, user_id: int, type: Optional[str] = None) -> int:
        """Get count of unread notifications for a user."""
        service = cls._get_service()
        return service.get_unread_count(user_id, type)