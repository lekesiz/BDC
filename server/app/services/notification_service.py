"""Notification service module."""

from datetime import datetime, timezone
from flask import current_app

from app.extensions import db
from app.realtime import emit_to_user, user_is_online, emit_to_role, emit_to_tenant
from app.services.email_service import send_notification_email


class NotificationService:
    """Notification service for managing user notifications."""
    
    @staticmethod
    def create_notification(user_id, type, title, message, data=None, related_id=None, related_type=None, 
                         sender_id=None, priority='normal', send_email=False, tenant_id=None):
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
            from app.models.notification import Notification
            
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
                tenant_id=tenant_id
            )
            
            db.session.add(notification)
            db.session.commit()
            
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
            db.session.rollback()
            return None
    
    @staticmethod
    def create_bulk_notifications(user_ids, type, title, message, data=None, related_id=None, 
                               related_type=None, sender_id=None, priority='normal', 
                               send_email=False, tenant_id=None):
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
            notification = NotificationService.create_notification(
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
    
    @staticmethod
    def create_role_notification(role, type, title, message, data=None, related_id=None, 
                              related_type=None, sender_id=None, priority='normal', 
                              send_email=False, tenant_id=None):
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
            from app.models.user import User
            users = User.query.filter_by(role=role, is_active=True)
            
            if tenant_id:
                from app.models.user import user_tenant
                users = users.join(user_tenant).filter(user_tenant.c.tenant_id == tenant_id)
            
            user_ids = [user.id for user in users]
            
            # Create notifications
            notifications = NotificationService.create_bulk_notifications(
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
    
    @staticmethod
    def create_tenant_notification(tenant_id, type, title, message, data=None, related_id=None, 
                                related_type=None, sender_id=None, priority='normal', 
                                send_email=False, exclude_roles=None):
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
            notifications = NotificationService.create_bulk_notifications(
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
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """
        Mark a notification as read.
        
        Args:
            notification_id (int): The notification ID
            user_id (int): The user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from app.models.notification import Notification
            
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                return False
            
            notification.read = True
            notification.read_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error marking notification as read: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def mark_all_as_read(user_id, type=None):
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id (int): The user ID
            type (str): Notification type to filter by
            
        Returns:
            int: Number of notifications updated
        """
        try:
            from app.models.notification import Notification
            
            query = Notification.query.filter_by(
                user_id=user_id,
                read=False
            )
            
            if type:
                query = query.filter_by(type=type)
            
            count = query.update({
                'read': True,
                'read_at': datetime.now(timezone.utc)
            })
            
            db.session.commit()
            
            return count
            
        except Exception as e:
            current_app.logger.error(f"Error marking all notifications as read: {str(e)}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def delete_notification(notification_id, user_id):
        """
        Delete a notification.
        
        Args:
            notification_id (int): The notification ID
            user_id (int): The user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from app.models.notification import Notification
            
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                return False
            
            db.session.delete(notification)
            db.session.commit()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error deleting notification: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_user_notifications(user_id, limit=20, offset=0, unread_only=False, type=None):
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
            from app.models.notification import Notification
            
            query = Notification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(read=False)
            
            if type:
                query = query.filter_by(type=type)
            
            notifications = query.order_by(
                Notification.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            return [notification.to_dict() for notification in notifications]
            
        except Exception as e:
            current_app.logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    @staticmethod
    def get_unread_count(user_id, type=None):
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id (int): The user ID
            type (str): Notification type to filter by
            
        Returns:
            int: Number of unread notifications
        """
        try:
            from app.models.notification import Notification
            
            query = Notification.query.filter_by(
                user_id=user_id,
                read=False
            )
            
            if type:
                query = query.filter_by(type=type)
            
            return query.count()
            
        except Exception as e:
            current_app.logger.error(f"Error getting unread count: {str(e)}")
            return 0