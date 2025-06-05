"""Add missing unique constraints to database tables."""

from alembic import op
import sqlalchemy as sa

revision = 'add_unique_constraints'
down_revision = 'add_database_indexes'
branch_labels = None
depends_on = None

def upgrade():
    """Add unique constraints to prevent duplicate data."""
    
    # User model unique constraints
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_unique_constraint('uq_users_username', 'users', ['username'])
    
    # Beneficiary model unique constraints
    op.create_unique_constraint('uq_beneficiaries_email', 'beneficiaries', ['email'])
    op.create_unique_constraint('uq_beneficiaries_social_security', 'beneficiaries', ['social_security_number'])
    
    # Tenant model unique constraints (if exists)
    try:
        op.create_unique_constraint('uq_tenants_name', 'tenants', ['name'])
        op.create_unique_constraint('uq_tenants_subdomain', 'tenants', ['subdomain'])
    except:
        pass  # Table might not exist
    
    # Program model unique constraints
    op.create_unique_constraint('uq_programs_code_tenant', 'programs', ['code', 'tenant_id'])
    
    # Document model unique constraints
    # Ensure no duplicate documents with same hash
    op.create_unique_constraint('uq_documents_file_hash', 'documents', ['file_hash'])
    
    # Two-factor auth unique constraint
    try:
        op.create_unique_constraint('uq_two_factor_user', 'two_factor_auth', ['user_id'])
    except:
        pass
    
    # User preferences unique constraint
    try:
        op.create_unique_constraint('uq_user_preferences_user', 'user_preferences', ['user_id'])
    except:
        pass
    
    # Composite unique constraints for many-to-many tables
    try:
        # User-Tenant association
        op.create_unique_constraint('uq_user_tenant', 'user_tenant', ['user_id', 'tenant_id'])
        
        # Program enrollments
        op.create_unique_constraint('uq_program_enrollment', 'program_enrollments', 
                                  ['program_id', 'beneficiary_id'])
        
        # Document permissions
        op.create_unique_constraint('uq_document_permission', 'document_permissions',
                                  ['document_id', 'user_id'])
    except:
        pass
    
    # Add check constraints for data integrity
    
    # Ensure positive values
    op.create_check_constraint('ck_programs_duration_positive', 'programs', 
                              'duration_weeks > 0')
    
    op.create_check_constraint('ck_evaluations_score_range', 'evaluations',
                              'score >= 0 AND score <= 100')
    
    # Ensure valid status values
    op.create_check_constraint('ck_appointments_status', 'appointments',
                              "status IN ('scheduled', 'completed', 'cancelled', 'no_show')")
    
    op.create_check_constraint('ck_programs_status', 'programs',
                              "status IN ('draft', 'active', 'completed', 'archived')")
    
    op.create_check_constraint('ck_evaluations_status', 'evaluations',
                              "status IN ('pending', 'in_progress', 'completed', 'expired')")
    
    # Ensure valid email format (basic check)
    op.create_check_constraint('ck_users_email_format', 'users',
                              "email LIKE '%@%.%'")
    
    op.create_check_constraint('ck_beneficiaries_email_format', 'beneficiaries',
                              "email LIKE '%@%.%'")
    
    # Ensure dates are logical
    op.create_check_constraint('ck_programs_dates', 'programs',
                              'end_date > start_date')
    
    op.create_check_constraint('ck_appointments_dates', 'appointments',
                              'end_time > start_time')


def downgrade():
    """Remove unique constraints."""
    
    # Drop check constraints
    op.drop_constraint('ck_appointments_dates', 'appointments')
    op.drop_constraint('ck_programs_dates', 'programs')
    op.drop_constraint('ck_beneficiaries_email_format', 'beneficiaries')
    op.drop_constraint('ck_users_email_format', 'users')
    op.drop_constraint('ck_evaluations_status', 'evaluations')
    op.drop_constraint('ck_programs_status', 'programs')
    op.drop_constraint('ck_appointments_status', 'appointments')
    op.drop_constraint('ck_evaluations_score_range', 'evaluations')
    op.drop_constraint('ck_programs_duration_positive', 'programs')
    
    # Drop composite unique constraints
    try:
        op.drop_constraint('uq_document_permission', 'document_permissions')
        op.drop_constraint('uq_program_enrollment', 'program_enrollments')
        op.drop_constraint('uq_user_tenant', 'user_tenant')
    except:
        pass
    
    # Drop single column unique constraints
    try:
        op.drop_constraint('uq_user_preferences_user', 'user_preferences')
        op.drop_constraint('uq_two_factor_user', 'two_factor_auth')
    except:
        pass
    
    op.drop_constraint('uq_documents_file_hash', 'documents')
    op.drop_constraint('uq_programs_code_tenant', 'programs')
    
    try:
        op.drop_constraint('uq_tenants_subdomain', 'tenants')
        op.drop_constraint('uq_tenants_name', 'tenants')
    except:
        pass
    
    op.drop_constraint('uq_beneficiaries_social_security', 'beneficiaries')
    op.drop_constraint('uq_beneficiaries_email', 'beneficiaries')
    op.drop_constraint('uq_users_username', 'users')
    op.drop_constraint('uq_users_email', 'users')