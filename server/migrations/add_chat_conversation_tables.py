"""Add chat conversation tables migration

This migration adds tables for the AI chat functionality including:
- chat_conversations: Main conversation table
- chat_messages: Individual messages within conversations
- chat_rate_limits: Rate limiting per user
- conversation_templates: Pre-defined conversation templates
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = 'add_chat_conversation_tables'
down_revision = None  # Update with your latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Create chat conversation tables."""
    
    # Create enum types
    op.execute("CREATE TYPE conversationstatus AS ENUM ('active', 'closed', 'archived', 'flagged')")
    op.execute("CREATE TYPE messagerole AS ENUM ('user', 'assistant', 'system')")
    
    # Create chat_conversations table
    op.create_table('chat_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('beneficiary_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True, default='en'),
        sa.Column('status', postgresql.ENUM('active', 'closed', 'archived', 'flagged', name='conversationstatus'), nullable=True, default='active'),
        sa.Column('context_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column('model', sa.String(length=50), nullable=True, default='gpt-4'),
        sa.Column('temperature', sa.Float(), nullable=True, default=0.7),
        sa.Column('max_tokens', sa.Integer(), nullable=True, default=1000),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('key_topics', sa.JSON(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), nullable=True, default=False),
        sa.Column('flag_reason', sa.Text(), nullable=True),
        sa.Column('flagged_by', sa.Integer(), nullable=True),
        sa.Column('flagged_at', sa.DateTime(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True, default=0),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['beneficiary_id'], ['beneficiaries.id'], ),
        sa.ForeignKeyConstraint(['flagged_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_conversations_beneficiary_id'), 'chat_conversations', ['beneficiary_id'], unique=False)
    op.create_index(op.f('ix_chat_conversations_context_type'), 'chat_conversations', ['context_type'], unique=False)
    op.create_index(op.f('ix_chat_conversations_status'), 'chat_conversations', ['status'], unique=False)
    op.create_index(op.f('ix_chat_conversations_tenant_id'), 'chat_conversations', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_chat_conversations_user_id'), 'chat_conversations', ['user_id'], unique=False)
    
    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', 'system', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('is_error', sa.Boolean(), nullable=True, default=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['conversation_id'], ['chat_conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_conversation_id'), 'chat_messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_created_at'), 'chat_messages', ['created_at'], unique=False)
    
    # Create chat_rate_limits table
    op.create_table('chat_rate_limits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('daily_message_count', sa.Integer(), nullable=True, default=0),
        sa.Column('daily_token_count', sa.Integer(), nullable=True, default=0),
        sa.Column('daily_reset_at', sa.DateTime(), nullable=True),
        sa.Column('monthly_message_count', sa.Integer(), nullable=True, default=0),
        sa.Column('monthly_token_count', sa.Integer(), nullable=True, default=0),
        sa.Column('monthly_reset_at', sa.DateTime(), nullable=True),
        sa.Column('max_daily_messages', sa.Integer(), nullable=True),
        sa.Column('max_daily_tokens', sa.Integer(), nullable=True),
        sa.Column('max_monthly_messages', sa.Integer(), nullable=True),
        sa.Column('max_monthly_tokens', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create conversation_templates table
    op.create_table('conversation_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True, default='en'),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('welcome_message', sa.Text(), nullable=False),
        sa.Column('suggested_questions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('priority', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_templates_category'), 'conversation_templates', ['category'], unique=False)
    op.create_index(op.f('ix_conversation_templates_is_active'), 'conversation_templates', ['is_active'], unique=False)
    op.create_index(op.f('ix_conversation_templates_language'), 'conversation_templates', ['language'], unique=False)
    op.create_index(op.f('ix_conversation_templates_tenant_id'), 'conversation_templates', ['tenant_id'], unique=False)


def downgrade():
    """Drop chat conversation tables."""
    
    # Drop tables
    op.drop_index(op.f('ix_conversation_templates_tenant_id'), table_name='conversation_templates')
    op.drop_index(op.f('ix_conversation_templates_language'), table_name='conversation_templates')
    op.drop_index(op.f('ix_conversation_templates_is_active'), table_name='conversation_templates')
    op.drop_index(op.f('ix_conversation_templates_category'), table_name='conversation_templates')
    op.drop_table('conversation_templates')
    
    op.drop_table('chat_rate_limits')
    
    op.drop_index(op.f('ix_chat_messages_created_at'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_conversation_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    
    op.drop_index(op.f('ix_chat_conversations_user_id'), table_name='chat_conversations')
    op.drop_index(op.f('ix_chat_conversations_tenant_id'), table_name='chat_conversations')
    op.drop_index(op.f('ix_chat_conversations_status'), table_name='chat_conversations')
    op.drop_index(op.f('ix_chat_conversations_context_type'), table_name='chat_conversations')
    op.drop_index(op.f('ix_chat_conversations_beneficiary_id'), table_name='chat_conversations')
    op.drop_table('chat_conversations')
    
    # Drop enum types
    op.execute('DROP TYPE conversationstatus')
    op.execute('DROP TYPE messagerole')