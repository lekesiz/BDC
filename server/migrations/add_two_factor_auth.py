"""Add two-factor authentication tables

This migration adds tables and fields for two-factor authentication support.
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Create two_factor_auth table
    op.create_table('two_factor_auth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('secret', sa.String(32), nullable=False),
        sa.Column('backup_codes', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), default=False),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('enabled_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create two_factor_sessions table
    op.create_table('two_factor_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(64), nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token')
    )
    
    # Create indexes
    op.create_index('idx_two_factor_auth_user_id', 'two_factor_auth', ['user_id'])
    op.create_index('idx_two_factor_sessions_user_id', 'two_factor_sessions', ['user_id'])
    op.create_index('idx_two_factor_sessions_token', 'two_factor_sessions', ['session_token'])
    op.create_index('idx_two_factor_sessions_expires', 'two_factor_sessions', ['expires_at'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_two_factor_sessions_expires', 'two_factor_sessions')
    op.drop_index('idx_two_factor_sessions_token', 'two_factor_sessions')
    op.drop_index('idx_two_factor_sessions_user_id', 'two_factor_sessions')
    op.drop_index('idx_two_factor_auth_user_id', 'two_factor_auth')
    
    # Drop tables
    op.drop_table('two_factor_sessions')
    op.drop_table('two_factor_auth')