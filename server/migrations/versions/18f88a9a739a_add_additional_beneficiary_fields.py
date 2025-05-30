"""Add additional beneficiary fields

Revision ID: 18f88a9a739a
Revises: bb34e53f771c
Create Date: 2025-05-16 03:05:27.997323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18f88a9a739a'
down_revision = 'bb34e53f771c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('beneficiaries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('state', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('nationality', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('native_language', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('bio', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('goals', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('referral_source', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('custom_fields', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('beneficiaries', schema=None) as batch_op:
        batch_op.drop_column('custom_fields')
        batch_op.drop_column('referral_source')
        batch_op.drop_column('goals')
        batch_op.drop_column('bio')
        batch_op.drop_column('category')
        batch_op.drop_column('native_language')
        batch_op.drop_column('nationality')
        batch_op.drop_column('state')

    # ### end Alembic commands ###
