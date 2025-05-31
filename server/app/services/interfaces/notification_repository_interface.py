"""Interface for notification repository operations."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from app.models.notification import Notification


class INotificationRepository(ABC):
    """Interface for notification repository."""
    
    @abstractmethod
    def create(self, **kwargs) -> Notification:
        """Create a new notification."""
        pass
    
    @abstractmethod
    def find_by_id(self, notification_id: int) -> Optional[Notification]:
        """Find notification by ID."""
        pass
    
    @abstractmethod
    def get_user_notifications(self, user_id: int, limit: int = 10, offset: int = 0, 
                              unread_only: bool = False, type_filter: Optional[str] = None) -> List[Notification]:
        """Get user notifications with filtering options."""
        pass
    
    @abstractmethod
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read."""
        pass
    
    @abstractmethod
    def mark_all_as_read(self, user_id: int, type_filter: Optional[str] = None) -> int:
        """Mark all user notifications as read."""
        pass
    
    @abstractmethod
    def delete(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        pass
    
    @abstractmethod
    def get_unread_count(self, user_id: int, type_filter: Optional[str] = None) -> int:
        """Get count of unread notifications."""
        pass