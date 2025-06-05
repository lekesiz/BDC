"""Add document versioning tables and fields

This migration adds:
- DocumentVersion table for version history
- DocumentComparison table for version comparisons
- Additional fields to Document table for versioning support
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    # Create document_versions table
    op.create_table('document_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('change_notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('is_current', sa.Boolean(), default=True),
        sa.Column('is_archived', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create document_comparisons table
    op.create_table('document_comparisons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version1_id', sa.Integer(), nullable=False),
        sa.Column('version2_id', sa.Integer(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('differences', sa.JSON(), nullable=True),
        sa.Column('comparison_type', sa.String(50), nullable=True),
        sa.Column('compared_by', sa.Integer(), nullable=True),
        sa.Column('compared_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['compared_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['version1_id'], ['document_versions.id'], ),
        sa.ForeignKeyConstraint(['version2_id'], ['document_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add versioning fields to documents table
    op.add_column('documents', sa.Column('current_version', sa.Integer(), default=1))
    op.add_column('documents', sa.Column('version_control_enabled', sa.Boolean(), default=False))
    op.add_column('documents', sa.Column('max_versions', sa.Integer(), default=10))
    op.add_column('documents', sa.Column('tags', sa.JSON(), nullable=True))
    op.add_column('documents', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('documents', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('filename', sa.String(255), nullable=True))
    op.add_column('documents', sa.Column('mime_type', sa.String(100), nullable=True))
    op.add_column('documents', sa.Column('file_hash', sa.String(64), nullable=True))
    op.add_column('documents', sa.Column('download_count', sa.Integer(), default=0))
    op.add_column('documents', sa.Column('last_accessed_at', sa.DateTime(), nullable=True))
    
    # Add foreign key for tenant_id
    op.create_foreign_key(None, 'documents', 'tenants', ['tenant_id'], ['id'])
    
    # Create indexes
    op.create_index('idx_document_versions_document_id', 'document_versions', ['document_id'])
    op.create_index('idx_document_versions_version_number', 'document_versions', ['document_id', 'version_number'])
    op.create_index('idx_document_comparisons_document_id', 'document_comparisons', ['document_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_document_comparisons_document_id', 'document_comparisons')
    op.drop_index('idx_document_versions_version_number', 'document_versions')
    op.drop_index('idx_document_versions_document_id', 'document_versions')
    
    # Drop foreign key
    op.drop_constraint(None, 'documents', type_='foreignkey')
    
    # Remove columns from documents table
    op.drop_column('documents', 'last_accessed_at')
    op.drop_column('documents', 'download_count')
    op.drop_column('documents', 'file_hash')
    op.drop_column('documents', 'mime_type')
    op.drop_column('documents', 'filename')
    op.drop_column('documents', 'tenant_id')
    op.drop_column('documents', 'category')
    op.drop_column('documents', 'tags')
    op.drop_column('documents', 'max_versions')
    op.drop_column('documents', 'version_control_enabled')
    op.drop_column('documents', 'current_version')
    
    # Drop tables
    op.drop_table('document_comparisons')
    op.drop_table('document_versions')