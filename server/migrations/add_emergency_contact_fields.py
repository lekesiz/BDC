"""Add emergency contact fields to beneficiaries table

This migration adds emergency contact information fields to the beneficiaries table
to allow storing emergency contact details for each beneficiary.
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add emergency contact fields to beneficiaries table
    op.add_column('beneficiaries', sa.Column('emergency_contact_name', sa.String(200), nullable=True))
    op.add_column('beneficiaries', sa.Column('emergency_contact_relationship', sa.String(100), nullable=True))
    op.add_column('beneficiaries', sa.Column('emergency_contact_phone', sa.String(20), nullable=True))
    op.add_column('beneficiaries', sa.Column('emergency_contact_email', sa.String(100), nullable=True))
    op.add_column('beneficiaries', sa.Column('emergency_contact_address', sa.Text(), nullable=True))


def downgrade():
    # Remove emergency contact fields from beneficiaries table
    op.drop_column('beneficiaries', 'emergency_contact_address')
    op.drop_column('beneficiaries', 'emergency_contact_email')
    op.drop_column('beneficiaries', 'emergency_contact_phone')
    op.drop_column('beneficiaries', 'emergency_contact_relationship')
    op.drop_column('beneficiaries', 'emergency_contact_name')