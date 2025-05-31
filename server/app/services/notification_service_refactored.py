"""Refactored notification service with dependency injection and improved architecture."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any, Protocol
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.notification import Notification
from app.models.user import User, user_tenant


class NotificationType(Enum):
    """Enum for notification types."""
    APPOINTMENT = "appointment"
    MESSAGE = "message"
    SYSTEM = "system"
    ALERT = "alert"
    REMINDER = "reminder"
    UPDATE = "update"
    INFO = "info"


class NotificationPriority(Enum):
    """Enum for notification priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class IEmailService(Protocol):
    """Protocol for email service interface."""
    def send_notification_email(self, user_email: str, subject: str, message: str) -> bool:
        """Send notification email."""
        ...


class IRealtimeService(Protocol):
    """Protocol for realtime service interface."""
    def emit_to_user(self, user_id: int, event: str, data: Dict[str, Any]) -> None:
        """Emit event to specific user."""
        ...
    
    def emit_to_role(self, role: str, event: str, data: Dict[str, Any]) -> None:
        """Emit event to all users with specific role."""
        ...
    
    def emit_to_tenant(self, tenant_id: int, event: str, data: Dict[str, Any]) -> None:
        """Emit event to all users in tenant."""
        ...
    
    def user_is_online(self, user_id: int) -> bool:
        """Check if user is online."""
        ...


class NotificationServiceRefactored:
    """Refactored notification service with dependency injection and improved testability."""
    
    def __init__(
        self,
        db_session: Session,
        email_service: Optional[IEmailService] = None,
        realtime_service: Optional[IRealtimeService] = None
    ):
        """
        Initialize notification service with dependencies.
        
        Args:
            db_session: SQLAlchemy database session
            email_service: Optional email service for sending notifications
            realtime_service: Optional realtime service for pushing notifications
        """
        self.db = db_session
        self.email_service = email_service
        self.realtime_service = realtime_service
    
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
        priority: str = NotificationPriority.NORMAL.value,
        send_email: bool = False,
        tenant_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new notification.
        
        Args:
            user_id: The recipient user ID
            type: Notification type
            title: Notification title
            message: Notification message
            data: Additional data for the notification
            related_id: ID of the related entity (e.g., appointment ID)
            related_type: Type of the related entity (e.g., 'appointment')
            sender_id: The sender user ID (if applicable)
            priority: Notification priority
            send_email: Whether to send an email
            tenant_id: The tenant ID (if applicable)
            
        Returns:
            Dict containing the created notification data
            
        Raises:
            ValueError: If user_id is invalid or type/priority is not valid
            Exception: If database operation fails
        """
        # Validate inputs
        self._validate_notification_type(type)
        self._validate_notification_priority(priority)
        
        # Verify user exists
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        try:
            # Create notification
            notification = Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                data=data,
                related_id=related_id,
                related_type=related_type,
                sender_id=sender_id,
                priority=priority,
                tenant_id=tenant_id,
                read=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            # Send real-time notification if service available
            if self.realtime_service and self.realtime_service.user_is_online(user_id):
                self.realtime_service.emit_to_user(
                    user_id,
                    'notification',
                    self._serialize_notification(notification)
                )
            
            # Send email if requested and service available
            if send_email and self.email_service and user.email:
                self.email_service.send_notification_email(
                    user_email=user.email,
                    subject=title,
                    message=message
                )
            
            return self._serialize_notification(notification)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create notification: {str(e)}")
    
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
        priority: str = NotificationPriority.NORMAL.value,
        send_email: bool = False,
        tenant_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Create notifications for multiple users.
        
        Args:
            user_ids: List of recipient user IDs
            type: Notification type
            title: Notification title
            message: Notification message
            data: Additional data for the notification
            related_id: ID of the related entity
            related_type: Type of the related entity
            sender_id: The sender user ID
            priority: Notification priority
            send_email: Whether to send emails
            tenant_id: The tenant ID
            
        Returns:
            List of created notification dictionaries
        """
        notifications = []
        
        for user_id in user_ids:
            try:
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
                notifications.append(notification)
            except Exception:
                # Continue creating notifications for other users
                # Log error if logger is available
                continue
        
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
        priority: str = NotificationPriority.NORMAL.value,
        send_email: bool = False,
        tenant_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Create notification for users with a specific role.
        
        Args:
            role: User role (e.g., 'super_admin', 'tenant_admin', 'trainer')
            type: Notification type
            title: Notification title
            message: Notification message
            data: Additional data for the notification
            related_id: ID of the related entity
            related_type: Type of the related entity
            sender_id: The sender user ID
            priority: Notification priority
            send_email: Whether to send emails
            tenant_id: The tenant ID
            
        Returns:
            List of created notification dictionaries
        """
        try:
            # Get users with the specified role
            query = self.db.query(User).filter(
                User.role == role,
                User.is_active == True
            )
            
            if tenant_id:
                query = query.join(user_tenant).filter(
                    user_tenant.c.tenant_id == tenant_id
                )
            
            users = query.all()
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
            
            # Emit to role channel if realtime service available
            if self.realtime_service:
                self.realtime_service.emit_to_role(role, 'notification', {
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
            raise Exception(f"Failed to create role notification: {str(e)}")
    
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
        priority: str = NotificationPriority.NORMAL.value,
        send_email: bool = False,
        exclude_roles: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create notification for all users in a tenant.
        
        Args:
            tenant_id: The tenant ID
            type: Notification type
            title: Notification title
            message: Notification message
            data: Additional data for the notification
            related_id: ID of the related entity
            related_type: Type of the related entity
            sender_id: The sender user ID
            priority: Notification priority
            send_email: Whether to send emails
            exclude_roles: List of roles to exclude
            
        Returns:
            List of created notification dictionaries
        """
        try:
            # Get users in the tenant
            query = self.db.query(User).join(user_tenant).filter(
                user_tenant.c.tenant_id == tenant_id,
                User.is_active == True
            )
            
            if exclude_roles:
                query = query.filter(User.role.notin_(exclude_roles))
            
            users = query.all()
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
            
            # Emit to tenant channel if realtime service available
            if self.realtime_service:
                self.realtime_service.emit_to_tenant(tenant_id, 'notification', {
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
            raise Exception(f"Failed to create tenant notification: {str(e)}")
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: The notification ID
            user_id: The user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if not notification:
                return False
            
            notification.read = True
            notification.read_at = datetime.now(timezone.utc)
            notification.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def mark_all_as_read(self, user_id: int, type: Optional[str] = None) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: The user ID
            type: Optional notification type to filter by
            
        Returns:
            Number of notifications updated
        """
        try:
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.read == False
            )
            
            if type:
                query = query.filter(Notification.type == type)
            
            count = query.update({
                'read': True,
                'read_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            })
            
            self.db.commit()
            return count
            
        except Exception:
            self.db.rollback()
            return 0
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: The notification ID
            user_id: The user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if not notification:
                return False
            
            self.db.delete(notification)
            self.db.commit()
            return True
            
        except Exception:
            self.db.rollback()
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
            user_id: The user ID
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            unread_only: Whether to return only unread notifications
            type: Optional notification type to filter by
            
        Returns:
            List of notification dictionaries
        """
        try:
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id
            )
            
            if unread_only:
                query = query.filter(Notification.read == False)
            
            if type:
                query = query.filter(Notification.type == type)
            
            notifications = query.order_by(
                Notification.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            return [self._serialize_notification(n) for n in notifications]
            
        except Exception:
            return []
    
    def get_unread_count(self, user_id: int, type: Optional[str] = None) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id: The user ID
            type: Optional notification type to filter by
            
        Returns:
            Number of unread notifications
        """
        try:
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.read == False
            )
            
            if type:
                query = query.filter(Notification.type == type)
            
            return query.count()
            
        except Exception:
            return 0
    
    def _validate_notification_type(self, type: str) -> None:
        """Validate notification type."""
        valid_types = [t.value for t in NotificationType]
        if type not in valid_types:
            raise ValueError(f"Invalid notification type: {type}. Must be one of {valid_types}")
    
    def _validate_notification_priority(self, priority: str) -> None:
        """Validate notification priority."""
        valid_priorities = [p.value for p in NotificationPriority]
        if priority not in valid_priorities:
            raise ValueError(f"Invalid notification priority: {priority}. Must be one of {valid_priorities}")
    
    def _serialize_notification(self, notification: Notification) -> Dict[str, Any]:
        """
        Serialize notification to dictionary.
        
        Args:
            notification: Notification model instance
            
        Returns:
            Dictionary representation of notification
        """
        sender_info = None
        if notification.sender_id:
            sender = self.db.query(User).filter_by(id=notification.sender_id).first()
            if sender:
                sender_info = {
                    'id': sender.id,
                    'name': f"{sender.first_name} {sender.last_name}",
                    'email': sender.email
                }
        
        return {
            'id': notification.id,
            'user_id': notification.user_id,
            'sender_id': notification.sender_id,
            'sender': sender_info,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'link': notification.link,
            'data': notification.data,
            'related_id': notification.related_id,
            'related_type': notification.related_type,
            'priority': notification.priority,
            'tenant_id': notification.tenant_id,
            'read': notification.read,
            'read_at': notification.read_at.isoformat() if notification.read_at else None,
            'created_at': notification.created_at.isoformat(),
            'updated_at': notification.updated_at.isoformat()
        }