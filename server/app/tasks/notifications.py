"""Notification-related Celery tasks."""

from celery import shared_task
from datetime import datetime, timedelta
from app.models import Appointment, User, Notification
from app.services import NotificationService, EmailService
from app.extensions import db
from flask import current_app


@shared_task(bind=True)
def send_appointment_reminders(self):
    """Send reminders for upcoming appointments."""
    try:
        # Get appointments happening in the next 24 hours
        tomorrow = datetime.utcnow() + timedelta(days=1)
        upcoming_appointments = Appointment.query.filter(
            Appointment.scheduled_at >= datetime.utcnow(),
            Appointment.scheduled_at <= tomorrow,
            Appointment.reminder_sent == False,
            Appointment.status == 'scheduled'
        ).all()
        
        count = 0
        for appointment in upcoming_appointments:
            try:
                # Get beneficiary user
                if appointment.beneficiary and appointment.beneficiary.user:
                    user = appointment.beneficiary.user
                    
                    # Calculate time until appointment
                    time_until = appointment.scheduled_at - datetime.utcnow()
                    hours_until = int(time_until.total_seconds() / 3600)
                    
                    # Create notification
                    NotificationService.create_notification(
                        user_id=user.id,
                        title='Appointment Reminder',
                        message=f'You have an appointment in {hours_until} hours with {appointment.trainer.first_name} {appointment.trainer.last_name}',
                        type='appointment',
                        related_id=appointment.id,
                        related_type='appointment',
                        priority='high'
                    )
                    
                    # Send email reminder
                    EmailService.send_appointment_reminder(
                        to_email=user.email,
                        appointment=appointment
                    )
                    
                    # Mark reminder as sent
                    appointment.reminder_sent = True
                    count += 1
                    
            except Exception as e:
                current_app.logger.error(f"Error sending reminder for appointment {appointment.id}: {str(e)}")
                continue
        
        db.session.commit()
        return f"Sent {count} appointment reminders"
        
    except Exception as e:
        current_app.logger.error(f"Error in send_appointment_reminders task: {str(e)}")
        raise


@shared_task(bind=True)
def send_bulk_notification(self, notification_data):
    """Send a notification to multiple users."""
    try:
        user_ids = notification_data.get('user_ids', [])
        title = notification_data.get('title')
        message = notification_data.get('message')
        type = notification_data.get('type', 'system')
        priority = notification_data.get('priority', 'normal')
        
        count = 0
        for user_id in user_ids:
            try:
                NotificationService.create_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    type=type,
                    priority=priority
                )
                count += 1
            except Exception as e:
                current_app.logger.error(f"Error sending notification to user {user_id}: {str(e)}")
                continue
        
        return f"Sent {count} notifications"
        
    except Exception as e:
        current_app.logger.error(f"Error in send_bulk_notification task: {str(e)}")
        raise


@shared_task(bind=True)
def send_role_based_notification(self, notification_data):
    """Send a notification to all users with a specific role."""
    try:
        role = notification_data.get('role')
        tenant_id = notification_data.get('tenant_id')
        title = notification_data.get('title')
        message = notification_data.get('message')
        type = notification_data.get('type', 'system')
        priority = notification_data.get('priority', 'normal')
        
        # Get users with the specified role
        query = User.query.filter_by(role=role, is_active=True)
        if tenant_id:
            query = query.filter(User.tenants.any(id=tenant_id))
        
        users = query.all()
        
        count = 0
        for user in users:
            try:
                NotificationService.create_notification(
                    user_id=user.id,
                    title=title,
                    message=message,
                    type=type,
                    priority=priority,
                    tenant_id=tenant_id
                )
                count += 1
            except Exception as e:
                current_app.logger.error(f"Error sending notification to user {user.id}: {str(e)}")
                continue
        
        return f"Sent {count} notifications to {role} users"
        
    except Exception as e:
        current_app.logger.error(f"Error in send_role_based_notification task: {str(e)}")
        raise