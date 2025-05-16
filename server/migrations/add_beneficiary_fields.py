"""Add additional fields to beneficiary model"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add columns to beneficiaries table
    op.add_column('beneficiaries', sa.Column('state', sa.String(100), nullable=True))
    op.add_column('beneficiaries', sa.Column('nationality', sa.String(100), nullable=True))
    op.add_column('beneficiaries', sa.Column('native_language', sa.String(100), nullable=True))
    op.add_column('beneficiaries', sa.Column('category', sa.String(100), nullable=True))
    op.add_column('beneficiaries', sa.Column('bio', sa.Text, nullable=True))
    op.add_column('beneficiaries', sa.Column('goals', sa.Text, nullable=True))
    op.add_column('beneficiaries', sa.Column('notes', sa.Text, nullable=True))
    op.add_column('beneficiaries', sa.Column('referral_source', sa.String(200), nullable=True))
    op.add_column('beneficiaries', sa.Column('custom_fields', sa.JSON, nullable=True))

def downgrade():
    # Remove columns from beneficiaries table
    op.drop_column('beneficiaries', 'state')
    op.drop_column('beneficiaries', 'nationality')
    op.drop_column('beneficiaries', 'native_language')
    op.drop_column('beneficiaries', 'category')
    op.drop_column('beneficiaries', 'bio')
    op.drop_column('beneficiaries', 'goals')
    op.drop_column('beneficiaries', 'notes')
    op.drop_column('beneficiaries', 'referral_source')
    op.drop_column('beneficiaries', 'custom_fields')