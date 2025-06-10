"""Add email verification fields to users table and create verification tokens table.

Run this migration with:
flask db upgrade
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Add email verification fields and table."""
    
    # Add columns to users table
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True, default=False))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
    
    # Set default value for existing users (assume they are verified)
    op.execute("UPDATE users SET email_verified = true WHERE email_verified IS NULL")
    
    # Make email_verified not nullable after setting defaults
    op.alter_column('users', 'email_verified', nullable=False)
    
    # Create email_verification_tokens table
    op.create_table('email_verification_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('token', sa.String(length=100), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_email_verification_tokens_token', 'email_verification_tokens', ['token'], unique=True)
    op.create_index('idx_email_verification_tokens_user_id', 'email_verification_tokens', ['user_id'])
    op.create_index('idx_email_verification_tokens_expires_at', 'email_verification_tokens', ['expires_at'])


def downgrade():
    """Remove email verification fields and table."""
    
    # Drop indexes
    op.drop_index('idx_email_verification_tokens_expires_at', 'email_verification_tokens')
    op.drop_index('idx_email_verification_tokens_user_id', 'email_verification_tokens')
    op.drop_index('idx_email_verification_tokens_token', 'email_verification_tokens')
    
    # Drop table
    op.drop_table('email_verification_tokens')
    
    # Remove columns from users table
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'email_verified')