"""Add performance optimization indexes

Revision ID: performance_indexes_20250110
Revises: 
Create Date: 2025-01-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'performance_indexes_20250110'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add performance optimization indexes."""
    
    # Beneficiaries table - composite indexes for common queries
    op.create_index(
        'idx_beneficiaries_trainer_active_created',
        'beneficiaries',
        ['trainer_id', 'is_active', 'created_at'],
        postgresql_where=sa.text('is_active = true')
    )
    
    op.create_index(
        'idx_beneficiaries_tenant_status',
        'beneficiaries',
        ['tenant_id', 'status', 'created_at']
    )
    
    # Appointments table - for calendar and scheduling queries
    op.create_index(
        'idx_appointments_trainer_time_status',
        'appointments',
        ['trainer_id', 'start_time', 'status']
    )
    
    op.create_index(
        'idx_appointments_beneficiary_time_status',
        'appointments',
        ['beneficiary_id', 'start_time', 'status']
    )
    
    op.create_index(
        'idx_appointments_date_range',
        'appointments',
        ['start_time', 'end_time'],
        postgresql_where=sa.text("status != 'cancelled'")
    )
    
    # Evaluations table - for progress tracking and reporting
    op.create_index(
        'idx_evaluations_beneficiary_created_status',
        'evaluations',
        ['beneficiary_id', 'created_at', 'status']
    )
    
    op.create_index(
        'idx_evaluations_trainer_date',
        'evaluations',
        ['created_by', 'created_at', 'type']
    )
    
    # Documents table - for document management
    op.create_index(
        'idx_documents_beneficiary_type_created',
        'documents',
        ['beneficiary_id', 'document_type', 'created_at'],
        postgresql_where=sa.text('is_archived = false')
    )
    
    op.create_index(
        'idx_documents_uploaded_by_date',
        'documents',
        ['uploaded_by', 'created_at']
    )
    
    # Users table - for authentication and user queries
    op.create_index(
        'idx_users_email_active',
        'users',
        ['email', 'is_active'],
        unique=False  # email already has unique constraint
    )
    
    op.create_index(
        'idx_users_tenant_role',
        'users',
        ['tenant_id', 'role', 'is_active']
    )
    
    # Programs table - for program management
    op.create_index(
        'idx_programs_status_dates',
        'programs',
        ['status', 'start_date', 'end_date']
    )
    
    op.create_index(
        'idx_programs_tenant_active',
        'programs',
        ['tenant_id', 'is_active', 'created_at']
    )
    
    # Program enrollments - for student progress
    op.create_index(
        'idx_program_enrollments_beneficiary_status',
        'program_enrollments',
        ['beneficiary_id', 'status', 'enrolled_at']
    )
    
    op.create_index(
        'idx_program_enrollments_program_active',
        'program_enrollments',
        ['program_id', 'is_active'],
        postgresql_where=sa.text('is_active = true')
    )
    
    # Notifications table - for unread notifications
    op.create_index(
        'idx_notifications_user_unread',
        'notifications',
        ['user_id', 'created_at'],
        postgresql_where=sa.text('is_read = false')
    )
    
    # User activities - for activity tracking
    op.create_index(
        'idx_user_activities_user_date',
        'user_activities',
        ['user_id', 'created_at', 'activity_type']
    )
    
    # Sessions table - for active session management
    op.create_index(
        'idx_sessions_user_active',
        'sessions',
        ['user_id', 'expires_at'],
        postgresql_where=sa.text('is_active = true')
    )
    
    # Full-text search indexes for PostgreSQL
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        # Create GIN indexes for full-text search
        op.execute("""
            CREATE INDEX idx_beneficiaries_search 
            ON beneficiaries 
            USING gin(to_tsvector('english', 
                coalesce(notes, '') || ' ' || 
                coalesce(goals, '') || ' ' || 
                coalesce(bio, '')
            ))
        """)
        
        op.execute("""
            CREATE INDEX idx_programs_search 
            ON programs 
            USING gin(to_tsvector('english', 
                coalesce(name, '') || ' ' || 
                coalesce(description, '')
            ))
        """)
        
        op.execute("""
            CREATE INDEX idx_documents_search 
            ON documents 
            USING gin(to_tsvector('english', 
                coalesce(title, '') || ' ' || 
                coalesce(description, '')
            ))
        """)


def downgrade():
    """Remove performance optimization indexes."""
    
    # Drop indexes in reverse order
    op.drop_index('idx_documents_search', 'documents')
    op.drop_index('idx_programs_search', 'programs')
    op.drop_index('idx_beneficiaries_search', 'beneficiaries')
    
    op.drop_index('idx_sessions_user_active', 'sessions')
    op.drop_index('idx_user_activities_user_date', 'user_activities')
    op.drop_index('idx_notifications_user_unread', 'notifications')
    op.drop_index('idx_program_enrollments_program_active', 'program_enrollments')
    op.drop_index('idx_program_enrollments_beneficiary_status', 'program_enrollments')
    op.drop_index('idx_programs_tenant_active', 'programs')
    op.drop_index('idx_programs_status_dates', 'programs')
    op.drop_index('idx_users_tenant_role', 'users')
    op.drop_index('idx_users_email_active', 'users')
    op.drop_index('idx_documents_uploaded_by_date', 'documents')
    op.drop_index('idx_documents_beneficiary_type_created', 'documents')
    op.drop_index('idx_evaluations_trainer_date', 'evaluations')
    op.drop_index('idx_evaluations_beneficiary_created_status', 'evaluations')
    op.drop_index('idx_appointments_date_range', 'appointments')
    op.drop_index('idx_appointments_beneficiary_time_status', 'appointments')
    op.drop_index('idx_appointments_trainer_time_status', 'appointments')
    op.drop_index('idx_beneficiaries_tenant_status', 'beneficiaries')
    op.drop_index('idx_beneficiaries_trainer_active_created', 'beneficiaries')