"""
Database Performance Optimization - Index Creation
Run this migration to add performance indexes to the database
"""

from app import create_app, db
from sqlalchemy import text

def create_performance_indexes():
    """Create database indexes for performance optimization"""
    
    app = create_app()
    
    with app.app_context():
        indexes = [
            # User indexes
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);",
            
            # Beneficiary indexes
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_status ON beneficiaries(status);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_created_at ON beneficiaries(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_date_of_birth ON beneficiaries(date_of_birth);",
            
            # Program indexes
            "CREATE INDEX IF NOT EXISTS idx_programs_status ON programs(status);",
            "CREATE INDEX IF NOT EXISTS idx_programs_start_date ON programs(start_date);",
            "CREATE INDEX IF NOT EXISTS idx_programs_end_date ON programs(end_date);",
            "CREATE INDEX IF NOT EXISTS idx_programs_created_at ON programs(created_at);",
            
            # Appointment indexes
            "CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_beneficiary_id ON appointments(beneficiary_id);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_appointments_user_date ON appointments(user_id, appointment_date);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_beneficiary_date ON appointments(beneficiary_id, appointment_date);",
            
            # Document indexes
            "CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);",
            
            # Evaluation indexes
            "CREATE INDEX IF NOT EXISTS idx_evaluations_user_id ON evaluations(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_beneficiary_id ON evaluations(beneficiary_id);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_status ON evaluations(status);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_created_at ON evaluations(created_at);",
            
            # Notification indexes
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);",
            
            # Composite index for unread notifications
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = false;",
            
            # Activity/Audit log indexes
            "CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_activities_timestamp ON user_activities(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_user_activities_action ON user_activities(action);",
        ]
        
        # Execute index creation
        for index_sql in indexes:
            try:
                db.session.execute(text(index_sql))
                print(f"✅ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                print(f"❌ Error creating index: {e}")
        
        db.session.commit()
        
        # Analyze tables for query optimization
        tables = ['users', 'beneficiaries', 'programs', 'appointments', 
                 'documents', 'evaluations', 'notifications', 'user_activities']
        
        for table in tables:
            try:
                db.session.execute(text(f"ANALYZE {table};"))
                print(f"✅ Analyzed table: {table}")
            except Exception as e:
                print(f"❌ Error analyzing table {table}: {e}")
        
        db.session.commit()
        
        print("\n✅ Database performance indexes created successfully!")

if __name__ == '__main__':
    create_performance_indexes()