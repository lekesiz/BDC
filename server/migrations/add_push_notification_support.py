"""
Add push notification support to BDC
Adds push subscription and notification preferences to User model
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import json


# revision identifiers
revision = 'add_push_notifications'
down_revision = 'previous_migration'  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Add push notification support"""
    
    # Add push subscription column to users table
    op.add_column('users', sa.Column(
        'push_subscription', 
        postgresql.JSON(),
        nullable=True,
        comment='Web push subscription data'
    ))
    
    # Add notification preferences column to users table
    op.add_column('users', sa.Column(
        'notification_preferences', 
        postgresql.JSON(),
        nullable=True,
        default=json.dumps({
            'evaluations': True,
            'appointments': True,
            'messages': True,
            'updates': False,
            'reminders': True
        }),
        comment='User notification preferences'
    ))
    
    # Create push_notification_logs table for tracking
    op.create_table(
        'push_notification_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('notification_id', sa.Integer(), sa.ForeignKey('notifications.id'), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSON(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='sent'),  # sent, failed, expired
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('endpoint_hash', sa.String(64), nullable=True),  # Hash of endpoint for privacy
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes for performance
    op.create_index('idx_push_logs_user_id', 'push_notification_logs', ['user_id'])
    op.create_index('idx_push_logs_status', 'push_notification_logs', ['status'])
    op.create_index('idx_push_logs_sent_at', 'push_notification_logs', ['sent_at'])
    op.create_index('idx_users_push_subscription', 'users', ['push_subscription'], postgresql_using='gin')
    
    # Create push_notification_templates table
    op.create_table(
        'push_notification_templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('title_template', sa.String(255), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('data_template', postgresql.JSON(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),  # evaluation, appointment, message, etc.
        sa.Column('parameters', postgresql.JSON(), nullable=True),  # Required parameters
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Insert default templates
    templates_data = [
        {
            'name': 'evaluation_available',
            'title_template': 'New Evaluation Available',
            'body_template': 'A new evaluation "{evaluation_title}" is available for {beneficiary_name}',
            'data_template': json.dumps({
                'type': 'evaluation',
                'action': 'view_evaluation',
                'url': '/evaluations'
            }),
            'category': 'evaluation',
            'parameters': json.dumps(['evaluation_title', 'beneficiary_name'])
        },
        {
            'name': 'appointment_reminder',
            'title_template': 'Appointment Reminder',
            'body_template': 'You have an appointment with {participant_name} at {appointment_time}',
            'data_template': json.dumps({
                'type': 'appointment',
                'action': 'view_calendar',
                'url': '/calendar'
            }),
            'category': 'appointment',
            'parameters': json.dumps(['appointment_time', 'participant_name'])
        },
        {
            'name': 'message_received',
            'title_template': 'Message from {sender_name}',
            'body_template': '{message_preview}',
            'data_template': json.dumps({
                'type': 'message',
                'action': 'view_message',
                'url': '/messages'
            }),
            'category': 'message',
            'parameters': json.dumps(['sender_name', 'message_preview'])
        },
        {
            'name': 'system_update',
            'title_template': 'App Update Available',
            'body_template': 'Version {version} is available with new features',
            'data_template': json.dumps({
                'type': 'update',
                'action': 'update_app'
            }),
            'category': 'system',
            'parameters': json.dumps(['version', 'features'])
        },
        {
            'name': 'document_shared',
            'title_template': 'Document Shared',
            'body_template': '{shared_by} shared "{document_name}" with you',
            'data_template': json.dumps({
                'type': 'document',
                'action': 'view_document',
                'url': '/documents'
            }),
            'category': 'document',
            'parameters': json.dumps(['document_name', 'shared_by'])
        }
    ]
    
    # Insert templates
    templates_table = sa.table(
        'push_notification_templates',
        sa.column('name', sa.String),
        sa.column('title_template', sa.String),
        sa.column('body_template', sa.Text),
        sa.column('data_template', postgresql.JSON),
        sa.column('category', sa.String),
        sa.column('parameters', postgresql.JSON),
        sa.column('active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    for template in templates_data:
        op.execute(
            templates_table.insert().values(
                name=template['name'],
                title_template=template['title_template'],
                body_template=template['body_template'],
                data_template=template['data_template'],
                category=template['category'],
                parameters=template['parameters'],
                active=True,
                created_at=sa.func.now(),
                updated_at=sa.func.now()
            )
        )
    
    # Add type column to notifications table if it doesn't exist
    try:
        op.add_column('notifications', sa.Column(
            'type', 
            sa.String(50), 
            nullable=True, 
            default='general'
        ))
    except Exception:
        # Column might already exist
        pass
    
    # Add data column to notifications table if it doesn't exist
    try:
        op.add_column('notifications', sa.Column(
            'data', 
            postgresql.JSON(), 
            nullable=True
        ))
    except Exception:
        # Column might already exist
        pass


def downgrade():
    """Remove push notification support"""
    
    # Drop tables
    op.drop_table('push_notification_templates')
    op.drop_table('push_notification_logs')
    
    # Drop indexes
    try:
        op.drop_index('idx_users_push_subscription')
        op.drop_index('idx_push_logs_sent_at')
        op.drop_index('idx_push_logs_status')
        op.drop_index('idx_push_logs_user_id')
    except Exception:
        pass
    
    # Remove columns from users table
    try:
        op.drop_column('users', 'notification_preferences')
        op.drop_column('users', 'push_subscription')
    except Exception:
        pass
    
    # Remove columns from notifications table (optional, might want to keep)
    # op.drop_column('notifications', 'data')
    # op.drop_column('notifications', 'type')