"""Notification repository implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.notification_repository_interface import INotificationRepository
from app.models import Notification
from app.extensions import db


class NotificationRepository(BaseRepository[Notification], INotificationRepository):
    """Notification repository implementation."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize notification repository."""
        super().__init__(Notification, db_session)
    
    def get_user_notifications(self, user_id: int, limit: int = 10, offset: int = 0, 
                              unread_only: bool = False, type_filter: Optional[str] = None) -> List[Notification]:
        """Get user notifications with filtering options."""
        query = self.db_session.query(Notification).filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(read=False)
        
        if type_filter:
            query = query.filter_by(type=type_filter)
        
        query = query.order_by(desc(Notification.created_at))
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def find_by_user_id(self, user_id: int, limit: Optional[int] = None,
                       offset: Optional[int] = None, unread_only: bool = False) -> List[Notification]:
        """Find notifications by user ID."""
        return self.get_user_notifications(
            user_id, 
            limit=limit or 10, 
            offset=offset or 0, 
            unread_only=unread_only
        )
    
    def find_unread_by_user_id(self, user_id: int) -> List[Notification]:
        """Find unread notifications by user ID."""
        return self.db_session.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.read == False
            )
        ).order_by(desc(Notification.created_at)).all()
    
    def find_by_type(self, user_id: int, notification_type: str) -> List[Notification]:
        """Find notifications by type for a user."""
        return self.db_session.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.type == notification_type
            )
        ).order_by(desc(Notification.created_at)).all()
    
    def find_by_priority(self, user_id: int, priority: str) -> List[Notification]:
        """Find notifications by priority for a user."""
        return self.db_session.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.priority == priority
            )
        ).order_by(desc(Notification.created_at)).all()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read."""
        try:
            notification = self.find_by_id(notification_id)
            if not notification or notification.user_id != user_id:
                return False
            
            notification.read = True
            notification.read_at = datetime.utcnow()
            notification.updated_at = datetime.utcnow()
            self.db_session.flush()
            return True
        except Exception:
            return False
    
    def mark_multiple_as_read(self, notification_ids: List[int]) -> int:
        """Mark multiple notifications as read."""
        try:
            now = datetime.utcnow()
            count = self.db_session.query(Notification).filter(
                Notification.id.in_(notification_ids)
            ).update({
                'read': True,
                'read_at': now,
                'updated_at': now
            }, synchronize_session=False)
            
            self.db_session.flush()
            return count
        except Exception:
            return 0
    
    def mark_all_as_read(self, user_id: int, type_filter: Optional[str] = None) -> int:
        """Mark all user notifications as read."""
        try:
            now = datetime.utcnow()
            query = self.db_session.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.read == False
                )
            )
            
            if type_filter:
                query = query.filter(Notification.type == type_filter)
            
            count = query.update({
                'read': True,
                'read_at': now,
                'updated_at': now
            }, synchronize_session=False)
            
            self.db_session.flush()
            return count
        except Exception:
            return 0
    
    def delete_multiple(self, notification_ids: List[int]) -> int:
        """Delete multiple notifications."""
        try:
            count = self.db_session.query(Notification).filter(
                Notification.id.in_(notification_ids)
            ).delete(synchronize_session=False)
            
            self.db_session.flush()
            return count
        except Exception:
            return 0
    
    def delete_old_notifications(self, days: int = 30) -> int:
        """Delete notifications older than specified days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            count = self.db_session.query(Notification).filter(
                Notification.created_at < cutoff_date
            ).delete(synchronize_session=False)
            
            self.db_session.flush()
            return count
        except Exception:
            return 0
    
    def get_unread_count(self, user_id: int, type_filter: Optional[str] = None) -> int:
        """Get count of unread notifications."""
        query = self.db_session.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.read == False
            )
        )
        
        if type_filter:
            query = query.filter(Notification.type == type_filter)
        
        return query.count()
    
    def count_by_user_id(self, user_id: int, unread_only: bool = False) -> int:
        """Count notifications for a user."""
        if unread_only:
            return self.get_unread_count(user_id)
        
        return self.db_session.query(Notification).filter_by(user_id=user_id).count()
    
    def create(self, **kwargs) -> Notification:
        """Create a new notification."""
        notification = Notification(**kwargs)
        self.db_session.add(notification)
        self.db_session.flush()
        return notification
    
    def update(self, notification_id: int, **kwargs) -> Optional[Notification]:
        """Update notification by ID."""
        notification = self.find_by_id(notification_id)
        if not notification:
            return None
        
        for key, value in kwargs.items():
            if hasattr(notification, key):
                setattr(notification, key, value)
        
        notification.updated_at = datetime.utcnow()
        self.db_session.flush()
        return notification
    
    def delete(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        notification = self.find_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return False
        
        self.db_session.delete(notification)
        self.db_session.flush()
        return True
    
    def save(self, notification: Notification) -> Notification:
        """Save notification instance."""
        self.db_session.add(notification)
        self.db_session.flush()
        return notification
    
    def find_all(self, limit: int = None, offset: int = None) -> List[Notification]:
        """Find all notifications with optional pagination."""
        query = self.db_session.query(Notification).order_by(desc(Notification.created_at))
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def count(self) -> int:
        """Count total notifications."""
        return self.db_session.query(Notification).count()