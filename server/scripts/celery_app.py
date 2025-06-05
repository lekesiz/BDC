"""Celery application configuration."""

from celery import Celery
from flask import Flask
from app.config import Config
import os

def make_celery(app=None):
    """Create a Celery instance."""
    if app is None:
        # Create a minimal Flask app for Celery workers
        app = Flask(__name__)
        app.config.from_object(Config)
    
    # Configure Celery
    celery = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    
    # Update task base name to be consistent with app's name
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Configure Celery settings
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone=app.config.get('CELERY_TIMEZONE', 'UTC'),
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )
    
    # Configure beat schedule for periodic tasks
    celery.conf.beat_schedule = {
        # Send appointment reminders every 15 minutes
        'send-appointment-reminders': {
            'task': 'app.tasks.notifications.send_appointment_reminders',
            'schedule': 900.0,  # 15 minutes in seconds
        },
        # Check for overdue evaluations daily
        'check-overdue-evaluations': {
            'task': 'app.tasks.evaluations.check_overdue_evaluations',
            'schedule': 86400.0,  # 24 hours in seconds
        },
        # Clean up old notifications weekly
        'cleanup-old-notifications': {
            'task': 'app.tasks.maintenance.cleanup_old_notifications',
            'schedule': 604800.0,  # 1 week in seconds
        },
        # Generate weekly reports
        'generate-weekly-reports': {
            'task': 'app.tasks.reports.generate_weekly_reports',
            'schedule': {
                'type': 'crontab',
                'hour': 9,
                'minute': 0,
                'day_of_week': 1,  # Monday
            },
        },
        # SMS Tasks
        # Send SMS appointment reminders every 30 minutes
        'send-sms-appointment-reminders': {
            'task': 'app.tasks.sms.send_appointment_reminders',
            'schedule': 1800.0,  # 30 minutes in seconds
        },
        # Update SMS delivery status every hour
        'update-sms-delivery-status': {
            'task': 'app.tasks.sms.update_sms_delivery_status',
            'schedule': 3600.0,  # 1 hour in seconds
        },
        # Clean up old SMS records monthly
        'cleanup-old-sms-records': {
            'task': 'app.tasks.sms.cleanup_old_sms_records',
            'schedule': {
                'type': 'crontab',
                'hour': 2,
                'minute': 0,
                'day_of_month': 1,  # First day of each month
            },
        },
    }
    
    return celery

# Create the celery app
celery_app = make_celery()