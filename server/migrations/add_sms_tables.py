"""Add SMS messaging tables migration."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_sms_tables'
down_revision = 'bb34e53f771c'
branch_labels = None
depends_on = None


def upgrade():
    """Create SMS related tables."""
    
    # Create sms_templates table
    op.create_table('sms_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_en', sa.Text(), nullable=False),
        sa.Column('content_tr', sa.Text(), nullable=True),
        sa.Column('message_type', sa.String(50), nullable=False),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_id')
    )
    
    # Create sms_campaigns table
    op.create_table('sms_campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_id', sa.String(100), nullable=True),
        sa.Column('message_content', sa.Text(), nullable=True),
        sa.Column('recipient_count', sa.Integer(), default=0),
        sa.Column('recipient_filters', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),
        sa.Column('scheduled_for', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('messages_sent', sa.Integer(), default=0),
        sa.Column('messages_delivered', sa.Integer(), default=0),
        sa.Column('messages_failed', sa.Integer(), default=0),
        sa.Column('total_cost', sa.Float(), default=0.0),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create sms_messages table
    op.create_table('sms_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('recipient_phone', sa.String(20), nullable=False),
        sa.Column('recipient_name', sa.String(100), nullable=True),
        sa.Column('message_type', sa.String(50), nullable=False, default='general_notification'),
        sa.Column('template_id', sa.String(100), nullable=True),
        sa.Column('message_content', sa.Text(), nullable=False),
        sa.Column('language', sa.String(5), nullable=False, default='en'),
        sa.Column('provider', sa.String(50), nullable=False, default='twilio'),
        sa.Column('provider_message_id', sa.String(100), nullable=True),
        sa.Column('provider_response', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('failed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('cost_amount', sa.Float(), nullable=True),
        sa.Column('cost_currency', sa.String(3), nullable=True, default='USD'),
        sa.Column('scheduled_for', sa.DateTime(), nullable=True),
        sa.Column('related_id', sa.Integer(), nullable=True),
        sa.Column('related_type', sa.String(50), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_sms_user_status', 'sms_messages', ['user_id', 'status'])
    op.create_index('idx_sms_phone_status', 'sms_messages', ['recipient_phone', 'status'])
    op.create_index('idx_sms_scheduled', 'sms_messages', ['scheduled_for', 'status'])
    op.create_index('idx_sms_created_at', 'sms_messages', ['created_at'])
    op.create_index('idx_sms_provider_id', 'sms_messages', ['provider_message_id'])


def downgrade():
    """Drop SMS related tables."""
    
    # Drop indexes
    op.drop_index('idx_sms_provider_id', 'sms_messages')
    op.drop_index('idx_sms_created_at', 'sms_messages')
    op.drop_index('idx_sms_scheduled', 'sms_messages')
    op.drop_index('idx_sms_phone_status', 'sms_messages')
    op.drop_index('idx_sms_user_status', 'sms_messages')
    
    # Drop tables
    op.drop_table('sms_messages')
    op.drop_table('sms_campaigns')
    op.drop_table('sms_templates')