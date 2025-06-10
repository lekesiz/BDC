"""Add virus scan logs table.

Run this migration with:
flask db upgrade
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Create virus_scan_logs table."""
    
    op.create_table('virus_scan_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # File information
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=100), nullable=True),
        
        # Scan results
        sa.Column('scan_result', sa.String(length=20), nullable=False),
        sa.Column('is_infected', sa.Boolean(), nullable=False, default=False),
        sa.Column('threats_found', sa.Text(), nullable=True),
        sa.Column('scan_details', sa.Text(), nullable=True),
        
        # Performance metrics
        sa.Column('scan_duration', sa.Float(), nullable=True),
        
        # Action taken
        sa.Column('action_taken', sa.String(length=50), nullable=True),
        sa.Column('quarantine_path', sa.String(length=500), nullable=True),
        
        # User information
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_virus_scan_logs_user_id', 'virus_scan_logs', ['user_id'])
    op.create_index('idx_virus_scan_logs_is_infected', 'virus_scan_logs', ['is_infected'])
    op.create_index('idx_virus_scan_logs_created_at', 'virus_scan_logs', ['created_at'])
    op.create_index('idx_virus_scan_logs_file_hash', 'virus_scan_logs', ['file_hash'])


def downgrade():
    """Drop virus_scan_logs table."""
    
    # Drop indexes
    op.drop_index('idx_virus_scan_logs_file_hash', 'virus_scan_logs')
    op.drop_index('idx_virus_scan_logs_created_at', 'virus_scan_logs')
    op.drop_index('idx_virus_scan_logs_is_infected', 'virus_scan_logs')
    op.drop_index('idx_virus_scan_logs_user_id', 'virus_scan_logs')
    
    # Drop table
    op.drop_table('virus_scan_logs')