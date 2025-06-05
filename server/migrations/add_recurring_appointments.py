"""Add recurring appointments tables migration."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_recurring_appointments'
down_revision = 'add_two_factor_auth'
branch_labels = None
depends_on = None


def upgrade():
    """Create recurring appointments tables."""
    
    # Create recurring_patterns table
    op.create_table('recurring_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('frequency', sa.String(20), nullable=False),
        sa.Column('interval', sa.Integer(), default=1),
        sa.Column('days_of_week', sa.JSON(), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('week_of_month', sa.Integer(), nullable=True),
        sa.Column('day_of_week_month', sa.Integer(), nullable=True),
        sa.Column('end_type', sa.String(20), default='never'),
        sa.Column('occurrences', sa.Integer(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('exceptions', sa.JSON(), default=list),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create appointment_series table
    op.create_table('appointment_series',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('beneficiary_id', sa.Integer(), nullable=False),
        sa.Column('trainer_id', sa.Integer(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, default=60),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('pattern_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['beneficiary_id'], ['beneficiaries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trainer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pattern_id'], ['recurring_patterns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add recurring fields to appointments table
    op.add_column('appointments', sa.Column('series_id', sa.Integer(), nullable=True))
    op.add_column('appointments', sa.Column('is_recurring', sa.Boolean(), default=False))
    op.add_column('appointments', sa.Column('reminder_sent', sa.Boolean(), default=False))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_appointments_series_id',
        'appointments', 'appointment_series',
        ['series_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create indexes
    op.create_index('idx_appointment_series_beneficiary', 'appointment_series', ['beneficiary_id'])
    op.create_index('idx_appointment_series_trainer', 'appointment_series', ['trainer_id'])
    op.create_index('idx_appointment_series_active', 'appointment_series', ['is_active'])
    op.create_index('idx_appointments_series', 'appointments', ['series_id'])
    op.create_index('idx_appointments_recurring', 'appointments', ['is_recurring'])


def downgrade():
    """Drop recurring appointments tables."""
    
    # Drop indexes
    op.drop_index('idx_appointments_recurring', 'appointments')
    op.drop_index('idx_appointments_series', 'appointments')
    op.drop_index('idx_appointment_series_active', 'appointment_series')
    op.drop_index('idx_appointment_series_trainer', 'appointment_series')
    op.drop_index('idx_appointment_series_beneficiary', 'appointment_series')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_appointments_series_id', 'appointments', type_='foreignkey')
    
    # Drop columns from appointments table
    op.drop_column('appointments', 'reminder_sent')
    op.drop_column('appointments', 'is_recurring')
    op.drop_column('appointments', 'series_id')
    
    # Drop tables
    op.drop_table('appointment_series')
    op.drop_table('recurring_patterns')