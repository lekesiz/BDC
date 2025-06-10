"""Create push notification tables.

Revision ID: push_notifications
Revises: virus_scan_log
Create Date: 2025-06-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'push_notifications'
down_revision = 'virus_scan_log'
branch_labels = None
depends_on = None


def upgrade():
    # Create push_notification_devices table
    op.create_table('push_notification_devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_token', sa.String(length=255), nullable=False),
        sa.Column('device_type', sa.String(length=20), nullable=False),
        sa.Column('device_name', sa.String(length=100), nullable=True),
        sa.Column('device_model', sa.String(length=100), nullable=True),
        sa.Column('device_os', sa.String(length=50), nullable=True),
        sa.Column('app_version', sa.String(length=20), nullable=True),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('provider_data', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('failed_attempts', sa.Integer(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_token')
    )
    
    # Create indexes for push_notification_devices
    op.create_index('idx_push_devices_user_active', 'push_notification_devices', ['user_id', 'is_active'], unique=False)
    op.create_index('idx_push_devices_token', 'push_notification_devices', ['device_token'], unique=False)
    
    # Create push_notification_logs table
    op.create_table('push_notification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('device_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('data', sa.Text(), nullable=True),
        sa.Column('notification_type', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('provider', sa.String(length=20), nullable=True),
        sa.Column('provider_message_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['push_notification_devices.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for push_notification_logs
    op.create_index('idx_push_logs_user_created', 'push_notification_logs', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_push_logs_status', 'push_notification_logs', ['status'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('idx_push_logs_status', table_name='push_notification_logs')
    op.drop_index('idx_push_logs_user_created', table_name='push_notification_logs')
    op.drop_index('idx_push_devices_token', table_name='push_notification_devices')
    op.drop_index('idx_push_devices_user_active', table_name='push_notification_devices')
    
    # Drop tables
    op.drop_table('push_notification_logs')
    op.drop_table('push_notification_devices')