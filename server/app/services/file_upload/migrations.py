"""Database migration for file upload audit tables.

Run this migration to create the necessary tables:
    alembic revision -m "Add file upload audit tables"
    
Then copy the upgrade() and downgrade() functions to the generated migration file.
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Create file upload audit tables."""
    
    # Create file_upload_audits table
    op.create_table(
        'file_upload_audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('file_id', sa.String(100), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('secure_filename', sa.String(255), nullable=False),
        sa.Column('file_category', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False),
        sa.Column('storage_path', sa.Text()),
        sa.Column('s3_url', sa.Text()),
        sa.Column('cdn_url', sa.Text()),
        sa.Column('is_encrypted', sa.Boolean(), default=False),
        sa.Column('virus_scan_result', sa.Text()),
        sa.Column('security_flags', sa.Text()),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text()),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('metadata', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_file_upload_audits_user_id', 'file_upload_audits', ['user_id'])
    op.create_index('idx_file_upload_audits_tenant_id', 'file_upload_audits', ['tenant_id'])
    op.create_index('idx_file_upload_audits_file_id', 'file_upload_audits', ['file_id'], unique=True)
    op.create_index('idx_file_upload_audits_timestamp', 'file_upload_audits', ['timestamp'])
    
    # Create file_versions table
    op.create_table(
        'file_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=False),
        sa.Column('comment', sa.Text()),
        sa.ForeignKeyConstraint(['audit_id'], ['file_upload_audits.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Drop file upload audit tables."""
    op.drop_table('file_versions')
    op.drop_table('file_upload_audits')