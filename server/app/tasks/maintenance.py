"""Maintenance-related Celery tasks."""

from celery import shared_task
from datetime import datetime, timedelta
from app.models import Notification, Document, AuditLog, TestSession
from app.extensions import db
from flask import current_app
import os


@shared_task(bind=True)
def cleanup_old_notifications(self):
    """Clean up old read notifications."""
    try:
        # Delete read notifications older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_notifications = Notification.query.filter(
            Notification.read == True,
            Notification.created_at < cutoff_date
        ).all()
        
        count = len(old_notifications)
        for notification in old_notifications:
            db.session.delete(notification)
        
        db.session.commit()
        return f"Deleted {count} old notifications"
        
    except Exception as e:
        current_app.logger.error(f"Error in cleanup_old_notifications task: {str(e)}")
        raise


@shared_task(bind=True)
def cleanup_orphaned_documents(self):
    """Clean up orphaned document files."""
    try:
        # Get all document records
        documents = Document.query.all()
        db_files = {doc.file_path for doc in documents if doc.file_path}
        
        # Get upload directory
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_dir):
            return "Upload directory does not exist"
        
        # Find orphaned files
        orphaned_count = 0
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in db_files:
                    try:
                        os.remove(file_path)
                        orphaned_count += 1
                    except Exception as e:
                        current_app.logger.error(f"Error deleting orphaned file {file_path}: {str(e)}")
        
        return f"Deleted {orphaned_count} orphaned files"
        
    except Exception as e:
        current_app.logger.error(f"Error in cleanup_orphaned_documents task: {str(e)}")
        raise


@shared_task(bind=True)
def cleanup_old_audit_logs(self):
    """Clean up old audit log entries."""
    try:
        # Keep audit logs for 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Delete old audit logs
        deleted = AuditLog.query.filter(
            AuditLog.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        return f"Deleted {deleted} old audit log entries"
        
    except Exception as e:
        current_app.logger.error(f"Error in cleanup_old_audit_logs task: {str(e)}")
        raise


@shared_task(bind=True)
def cleanup_abandoned_test_sessions(self):
    """Clean up abandoned test sessions."""
    try:
        # Consider sessions abandoned if not completed within 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        abandoned_sessions = TestSession.query.filter(
            TestSession.status == 'in_progress',
            TestSession.started_at < cutoff_date
        ).all()
        
        count = len(abandoned_sessions)
        for session in abandoned_sessions:
            session.status = 'abandoned'
        
        db.session.commit()
        return f"Marked {count} test sessions as abandoned"
        
    except Exception as e:
        current_app.logger.error(f"Error in cleanup_abandoned_test_sessions task: {str(e)}")
        raise


@shared_task(bind=True)
def optimize_database(self):
    """Run database optimization tasks."""
    try:
        # Run VACUUM on PostgreSQL or OPTIMIZE on MySQL
        db_engine = db.engine.name
        
        if db_engine == 'postgresql':
            db.session.execute('VACUUM ANALYZE')
        elif db_engine == 'mysql':
            # Get all tables
            tables = db.session.execute("SHOW TABLES").fetchall()
            for table in tables:
                table_name = table[0]
                db.session.execute(f"OPTIMIZE TABLE {table_name}")
        
        return f"Database optimization completed for {db_engine}"
        
    except Exception as e:
        current_app.logger.error(f"Error in optimize_database task: {str(e)}")
        raise


@shared_task(bind=True)
def check_storage_usage(self):
    """Check storage usage and send alerts if needed."""
    try:
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        # Calculate total size
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except:
                    pass
        
        # Convert to MB
        total_size_mb = total_size / (1024 * 1024)
        
        # Check threshold (default 10GB)
        threshold_mb = current_app.config.get('STORAGE_ALERT_THRESHOLD_MB', 10240)
        
        if total_size_mb > threshold_mb:
            # Send alert to admins
            from app.models import User
            from app.services import NotificationService
            
            admins = User.query.filter_by(role='super_admin', is_active=True).all()
            for admin in admins:
                NotificationService.create_notification(
                    user_id=admin.id,
                    title='Storage Usage Alert',
                    message=f'Storage usage has exceeded {threshold_mb}MB. Current usage: {total_size_mb:.2f}MB',
                    type='system',
                    priority='urgent'
                )
        
        return f"Storage check complete: {total_size_mb:.2f}MB used, {file_count} files"
        
    except Exception as e:
        current_app.logger.error(f"Error in check_storage_usage task: {str(e)}")
        raise