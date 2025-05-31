"""Interface for Notification service operations."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.notification import Notification


class INotificationService(ABC):
    """Interface defining operations for Notification service."""
    
    @abstractmethod
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
        """Create a new notification for a user."""
        pass
    
    @abstractmethod
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
        """Create notifications for multiple users."""
        pass
    
    @abstractmethod
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
        """Create notification for all users with a specific role."""
        pass
    
    @abstractmethod
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
        """Create notification for all users in a tenant."""
        pass
    
    @abstractmethod
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        pass
    
    @abstractmethod
    def mark_all_as_read(self, user_id: int, type: Optional[str] = None) -> int:
        """Mark all notifications as read for a user."""
        pass
    
    @abstractmethod
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        pass
    
    @abstractmethod
    def get_user_notifications(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
        type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        pass
    
    @abstractmethod
    def get_unread_count(self, user_id: int, type: Optional[str] = None) -> int:
        """Get count of unread notifications for a user."""
        pass