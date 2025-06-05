"""Add missing fields to MessageThread and Message models

This migration adds:
- title and thread_type to MessageThread
- is_edited and edited_at to Message
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add fields to message_threads table
    op.add_column('message_threads', sa.Column('title', sa.String(100), nullable=True))
    op.add_column('message_threads', sa.Column('thread_type', sa.String(50), nullable=True))
    
    # Set default values for existing records
    op.execute("UPDATE message_threads SET thread_type = 'direct' WHERE thread_type IS NULL")
    
    # Add fields to messages table
    op.add_column('messages', sa.Column('is_edited', sa.Boolean(), nullable=True))
    op.add_column('messages', sa.Column('edited_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing records
    op.execute("UPDATE messages SET is_edited = FALSE WHERE is_edited IS NULL")


def downgrade():
    # Remove fields from messages table
    op.drop_column('messages', 'edited_at')
    op.drop_column('messages', 'is_edited')
    
    # Remove fields from message_threads table
    op.drop_column('message_threads', 'thread_type')
    op.drop_column('message_threads', 'title')