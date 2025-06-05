"""
Migration script to add randomization fields to evaluation-related tables.

This migration adds comprehensive randomization support to the BDC system.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = 'add_randomization_fields'
down_revision = None  # Set this to the latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Add randomization fields to evaluation tables."""
    
    # Add randomization fields to evaluations table
    with op.batch_alter_table('evaluations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('randomization_enabled', sa.Boolean(), nullable=True, default=True))
        batch_op.add_column(sa.Column('randomization_strategy', sa.String(length=50), nullable=True, default='simple_random'))
        batch_op.add_column(sa.Column('randomization_config', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('question_order_template', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('anchor_questions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('answer_randomization', sa.Boolean(), nullable=True, default=True))
        batch_op.add_column(sa.Column('blocking_rules', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('time_based_seed', sa.Boolean(), nullable=True, default=False))

    # Add randomization fields to test_sets table
    with op.batch_alter_table('test_sets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('randomization_enabled', sa.Boolean(), nullable=True, default=True))
        batch_op.add_column(sa.Column('randomization_strategy', sa.String(length=50), nullable=True, default='simple_random'))
        batch_op.add_column(sa.Column('randomization_config', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('question_order_template', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('anchor_questions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('answer_randomization', sa.Boolean(), nullable=True, default=True))
        batch_op.add_column(sa.Column('blocking_rules', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('time_based_seed', sa.Boolean(), nullable=True, default=False))

    # Add randomization tracking fields to test_sessions table
    with op.batch_alter_table('test_sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('question_order', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('randomization_seed', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('answer_mappings', sa.JSON(), nullable=True))

    # Update existing records to have default values
    op.execute("UPDATE evaluations SET randomization_enabled = 1 WHERE randomization_enabled IS NULL")
    op.execute("UPDATE evaluations SET randomization_strategy = 'simple_random' WHERE randomization_strategy IS NULL")
    op.execute("UPDATE evaluations SET answer_randomization = 1 WHERE answer_randomization IS NULL")
    op.execute("UPDATE evaluations SET time_based_seed = 0 WHERE time_based_seed IS NULL")

    op.execute("UPDATE test_sets SET randomization_enabled = 1 WHERE randomization_enabled IS NULL")
    op.execute("UPDATE test_sets SET randomization_strategy = 'simple_random' WHERE randomization_strategy IS NULL")
    op.execute("UPDATE test_sets SET answer_randomization = 1 WHERE answer_randomization IS NULL")
    op.execute("UPDATE test_sets SET time_based_seed = 0 WHERE time_based_seed IS NULL")

    # Create indexes for performance
    op.create_index('idx_evaluations_randomization_strategy', 'evaluations', ['randomization_strategy'])
    op.create_index('idx_test_sets_randomization_strategy', 'test_sets', ['randomization_strategy'])
    op.create_index('idx_test_sessions_randomization_seed', 'test_sessions', ['randomization_seed'])


def downgrade():
    """Remove randomization fields from evaluation tables."""
    
    # Remove indexes
    op.drop_index('idx_test_sessions_randomization_seed', table_name='test_sessions')
    op.drop_index('idx_test_sets_randomization_strategy', table_name='test_sets')
    op.drop_index('idx_evaluations_randomization_strategy', table_name='evaluations')

    # Remove fields from test_sessions table
    with op.batch_alter_table('test_sessions', schema=None) as batch_op:
        batch_op.drop_column('answer_mappings')
        batch_op.drop_column('randomization_seed')
        batch_op.drop_column('question_order')

    # Remove fields from test_sets table
    with op.batch_alter_table('test_sets', schema=None) as batch_op:
        batch_op.drop_column('time_based_seed')
        batch_op.drop_column('blocking_rules')
        batch_op.drop_column('answer_randomization')
        batch_op.drop_column('anchor_questions')
        batch_op.drop_column('question_order_template')
        batch_op.drop_column('randomization_config')
        batch_op.drop_column('randomization_strategy')
        batch_op.drop_column('randomization_enabled')

    # Remove fields from evaluations table
    with op.batch_alter_table('evaluations', schema=None) as batch_op:
        batch_op.drop_column('time_based_seed')
        batch_op.drop_column('blocking_rules')
        batch_op.drop_column('answer_randomization')
        batch_op.drop_column('anchor_questions')
        batch_op.drop_column('question_order_template')
        batch_op.drop_column('randomization_config')
        batch_op.drop_column('randomization_strategy')
        batch_op.drop_column('randomization_enabled')