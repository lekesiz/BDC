"""Add missing database indexes for foreign keys and common queries."""

from alembic import op
import sqlalchemy as sa

revision = 'add_database_indexes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add indexes for foreign keys and common query patterns."""
    
    # User model indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    
    # Beneficiary model indexes
    op.create_index('idx_beneficiaries_tenant_id', 'beneficiaries', ['tenant_id'])
    op.create_index('idx_beneficiaries_created_by_id', 'beneficiaries', ['created_by_id'])
    op.create_index('idx_beneficiaries_assigned_to_id', 'beneficiaries', ['assigned_to_id'])
    op.create_index('idx_beneficiaries_email', 'beneficiaries', ['email'])
    
    # Program model indexes
    op.create_index('idx_programs_tenant_id', 'programs', ['tenant_id'])
    op.create_index('idx_programs_created_by_id', 'programs', ['created_by_id'])
    op.create_index('idx_programs_status', 'programs', ['status'])
    
    # Evaluation model indexes
    op.create_index('idx_evaluations_tenant_id', 'evaluations', ['tenant_id'])
    op.create_index('idx_evaluations_beneficiary_id', 'evaluations', ['beneficiary_id'])
    op.create_index('idx_evaluations_program_id', 'evaluations', ['program_id'])
    op.create_index('idx_evaluations_evaluator_id', 'evaluations', ['evaluator_id'])
    op.create_index('idx_evaluations_status', 'evaluations', ['status'])
    
    # Document model indexes
    op.create_index('idx_documents_tenant_id', 'documents', ['tenant_id'])
    op.create_index('idx_documents_uploaded_by_id', 'documents', ['uploaded_by_id'])
    op.create_index('idx_documents_beneficiary_id', 'documents', ['beneficiary_id'])
    op.create_index('idx_documents_folder_id', 'documents', ['folder_id'])
    
    # Appointment model indexes
    op.create_index('idx_appointments_tenant_id', 'appointments', ['tenant_id'])
    op.create_index('idx_appointments_trainer_id', 'appointments', ['trainer_id'])
    op.create_index('idx_appointments_beneficiary_id', 'appointments', ['beneficiary_id'])
    op.create_index('idx_appointments_status', 'appointments', ['status'])
    op.create_index('idx_appointments_date', 'appointments', ['date'])
    
    # Notification model indexes
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])
    
    # Composite indexes for common queries
    op.create_index('idx_users_email_password', 'users', ['email', 'password_hash'])
    op.create_index('idx_appointments_date_status', 'appointments', ['date', 'status'])
    op.create_index('idx_evaluations_beneficiary_status', 'evaluations', ['beneficiary_id', 'status'])
    

def downgrade():
    """Remove indexes."""
    
    # Drop composite indexes
    op.drop_index('idx_evaluations_beneficiary_status', 'evaluations')
    op.drop_index('idx_appointments_date_status', 'appointments')
    op.drop_index('idx_users_email_password', 'users')
    
    # Drop notification indexes
    op.drop_index('idx_notifications_created_at', 'notifications')
    op.drop_index('idx_notifications_is_read', 'notifications')
    op.drop_index('idx_notifications_user_id', 'notifications')
    
    # Drop appointment indexes
    op.drop_index('idx_appointments_date', 'appointments')
    op.drop_index('idx_appointments_status', 'appointments')
    op.drop_index('idx_appointments_beneficiary_id', 'appointments')
    op.drop_index('idx_appointments_trainer_id', 'appointments')
    op.drop_index('idx_appointments_tenant_id', 'appointments')
    
    # Drop document indexes
    op.drop_index('idx_documents_folder_id', 'documents')
    op.drop_index('idx_documents_beneficiary_id', 'documents')
    op.drop_index('idx_documents_uploaded_by_id', 'documents')
    op.drop_index('idx_documents_tenant_id', 'documents')
    
    # Drop evaluation indexes
    op.drop_index('idx_evaluations_status', 'evaluations')
    op.drop_index('idx_evaluations_evaluator_id', 'evaluations')
    op.drop_index('idx_evaluations_program_id', 'evaluations')
    op.drop_index('idx_evaluations_beneficiary_id', 'evaluations')
    op.drop_index('idx_evaluations_tenant_id', 'evaluations')
    
    # Drop program indexes
    op.drop_index('idx_programs_status', 'programs')
    op.drop_index('idx_programs_created_by_id', 'programs')
    op.drop_index('idx_programs_tenant_id', 'programs')
    
    # Drop beneficiary indexes
    op.drop_index('idx_beneficiaries_email', 'beneficiaries')
    op.drop_index('idx_beneficiaries_assigned_to_id', 'beneficiaries')
    op.drop_index('idx_beneficiaries_created_by_id', 'beneficiaries')
    op.drop_index('idx_beneficiaries_tenant_id', 'beneficiaries')
    
    # Drop user indexes
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_role', 'users')
    op.drop_index('idx_users_tenant_id', 'users')
    op.drop_index('idx_users_username', 'users')
    op.drop_index('idx_users_email', 'users')