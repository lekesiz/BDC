"""
Enhanced Database Performance Optimization - Comprehensive Index Creation
Run this migration to add comprehensive performance indexes to the database
"""

from app import create_app, db
from sqlalchemy import text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_performance_indexes():
    """Create comprehensive database indexes for performance optimization"""
    
    app = create_app()
    
    with app.app_context():
        # Enhanced comprehensive indexes
        indexes = [
            # User indexes - Critical for authentication and user management
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);",
            "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);",
            
            # Composite indexes for user queries
            "CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);",
            "CREATE INDEX IF NOT EXISTS idx_users_tenant_role ON users(tenant_id, role);",
            "CREATE INDEX IF NOT EXISTS idx_users_active_created ON users(is_active, created_at);",
            
            # Beneficiary indexes - Critical for student management
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_trainer_id ON beneficiaries(trainer_id);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_tenant_id ON beneficiaries(tenant_id);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_status ON beneficiaries(status);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_is_active ON beneficiaries(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_created_at ON beneficiaries(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_birth_date ON beneficiaries(birth_date);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_category ON beneficiaries(category);",
            
            # Composite indexes for beneficiary queries
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_trainer_status ON beneficiaries(trainer_id, status);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_tenant_status ON beneficiaries(tenant_id, status);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_status_created ON beneficiaries(status, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_active_trainer ON beneficiaries(is_active, trainer_id);",
            
            # Appointment indexes - Critical for scheduling
            "CREATE INDEX IF NOT EXISTS idx_appointments_beneficiary_id ON appointments(beneficiary_id);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_trainer_id ON appointments(trainer_id);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_start_time ON appointments(start_time);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_end_time ON appointments(end_time);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_series_id ON appointments(series_id);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_is_recurring ON appointments(is_recurring);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_created_at ON appointments(created_at);",
            
            # Composite indexes for appointment queries
            "CREATE INDEX IF NOT EXISTS idx_appointments_beneficiary_start ON appointments(beneficiary_id, start_time);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_trainer_start ON appointments(trainer_id, start_time);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_status_start ON appointments(status, start_time);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_start_end ON appointments(start_time, end_time);",
            "CREATE INDEX IF NOT EXISTS idx_appointments_trainer_status ON appointments(trainer_id, status);",
            
            # Program indexes - For training program management
            "CREATE INDEX IF NOT EXISTS idx_programs_status ON programs(status);",
            "CREATE INDEX IF NOT EXISTS idx_programs_created_by ON programs(created_by);",
            "CREATE INDEX IF NOT EXISTS idx_programs_created_at ON programs(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_programs_start_date ON programs(start_date);",
            "CREATE INDEX IF NOT EXISTS idx_programs_end_date ON programs(end_date);",
            
            # Program enrollment indexes
            "CREATE INDEX IF NOT EXISTS idx_program_enrollments_program_id ON program_enrollments(program_id);",
            "CREATE INDEX IF NOT EXISTS idx_program_enrollments_beneficiary_id ON program_enrollments(beneficiary_id);",
            "CREATE INDEX IF NOT EXISTS idx_program_enrollments_status ON program_enrollments(status);",
            "CREATE INDEX IF NOT EXISTS idx_program_enrollments_enrolled_at ON program_enrollments(enrolled_at);",
            
            # Document indexes - For file management
            "CREATE INDEX IF NOT EXISTS idx_documents_beneficiary_id ON documents(beneficiary_id);",
            "CREATE INDEX IF NOT EXISTS idx_documents_created_by ON documents(created_by);",
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);",
            "CREATE INDEX IF NOT EXISTS idx_documents_file_name ON documents(file_name);",
            
            # Composite indexes for document queries
            "CREATE INDEX IF NOT EXISTS idx_documents_beneficiary_created ON documents(beneficiary_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_documents_type_created ON documents(file_type, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_documents_creator_created ON documents(created_by, created_at);",
            
            # Evaluation indexes - For assessment management
            "CREATE INDEX IF NOT EXISTS idx_evaluations_beneficiary_id ON evaluations(beneficiary_id);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_created_by ON evaluations(created_by);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_status ON evaluations(status);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_created_at ON evaluations(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_completed_at ON evaluations(completed_at);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_due_date ON evaluations(due_date);",
            
            # Composite indexes for evaluation queries
            "CREATE INDEX IF NOT EXISTS idx_evaluations_beneficiary_status ON evaluations(beneficiary_id, status);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_beneficiary_created ON evaluations(beneficiary_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_status_created ON evaluations(status, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_status_due ON evaluations(status, due_date);",
            
            # Notification indexes - For messaging system
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_notification_type ON notifications(notification_type);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);",
            
            # Composite indexes for notification queries
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_created ON notifications(user_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_type_created ON notifications(notification_type, created_at);",
            
            # Partial index for unread notifications (more efficient)
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, created_at) WHERE is_read = false;",
            
            # User Activity indexes - For audit trail
            "CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_activities_timestamp ON user_activities(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_user_activities_action ON user_activities(action);",
            "CREATE INDEX IF NOT EXISTS idx_user_activities_ip_address ON user_activities(ip_address);",
            
            # Composite indexes for activity queries
            "CREATE INDEX IF NOT EXISTS idx_user_activities_user_timestamp ON user_activities(user_id, timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_user_activities_action_timestamp ON user_activities(action, timestamp);",
            
            # Test and Assessment indexes
            "CREATE INDEX IF NOT EXISTS idx_tests_created_by ON tests(created_by);",
            "CREATE INDEX IF NOT EXISTS idx_tests_status ON tests(status);",
            "CREATE INDEX IF NOT EXISTS idx_tests_created_at ON tests(created_at);",
            
            "CREATE INDEX IF NOT EXISTS idx_test_sessions_beneficiary_id ON test_sessions(beneficiary_id);",
            "CREATE INDEX IF NOT EXISTS idx_test_sessions_test_id ON test_sessions(test_id);",
            "CREATE INDEX IF NOT EXISTS idx_test_sessions_status ON test_sessions(status);",
            "CREATE INDEX IF NOT EXISTS idx_test_sessions_started_at ON test_sessions(started_at);",
            "CREATE INDEX IF NOT EXISTS idx_test_sessions_completed_at ON test_sessions(completed_at);",
            
            # Message and Chat indexes
            "CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);",
            "CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);",
            "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages(is_read);",
            
            "CREATE INDEX IF NOT EXISTS idx_message_threads_created_by ON message_threads(created_by);",
            "CREATE INDEX IF NOT EXISTS idx_message_threads_created_at ON message_threads(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_message_threads_last_activity ON message_threads(last_activity);",
            
            # Report indexes
            "CREATE INDEX IF NOT EXISTS idx_reports_created_by ON reports(created_by);",
            "CREATE INDEX IF NOT EXISTS idx_reports_report_type ON reports(report_type);",
            "CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);",
            "CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_reports_generated_at ON reports(generated_at);",
            
            # Token blacklist indexes
            "CREATE INDEX IF NOT EXISTS idx_token_blocklist_jti ON token_blocklist(jti);",
            "CREATE INDEX IF NOT EXISTS idx_token_blocklist_token_type ON token_blocklist(token_type);",
            "CREATE INDEX IF NOT EXISTS idx_token_blocklist_created_at ON token_blocklist(created_at);",
            
            # Folder indexes
            "CREATE INDEX IF NOT EXISTS idx_folders_owner_id ON folders(owner_id);",
            "CREATE INDEX IF NOT EXISTS idx_folders_parent_id ON folders(parent_id);",
            "CREATE INDEX IF NOT EXISTS idx_folders_created_at ON folders(created_at);",
            
            # Training session indexes
            "CREATE INDEX IF NOT EXISTS idx_training_sessions_program_id ON training_sessions(program_id);",
            "CREATE INDEX IF NOT EXISTS idx_training_sessions_trainer_id ON training_sessions(trainer_id);",
            "CREATE INDEX IF NOT EXISTS idx_training_sessions_scheduled_at ON training_sessions(scheduled_at);",
            "CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON training_sessions(status);",
            
            # Session attendance indexes
            "CREATE INDEX IF NOT EXISTS idx_session_attendance_session_id ON session_attendance(session_id);",
            "CREATE INDEX IF NOT EXISTS idx_session_attendance_beneficiary_id ON session_attendance(beneficiary_id);",
            "CREATE INDEX IF NOT EXISTS idx_session_attendance_attended ON session_attendance(attended);",
            "CREATE INDEX IF NOT EXISTS idx_session_attendance_attendance_date ON session_attendance(attendance_date);",
        ]
        
        # Get database dialect for dialect-specific optimizations
        dialect = db.engine.dialect.name
        logger.info(f"Database dialect detected: {dialect}")
        
        # Execute index creation with progress tracking
        created_count = 0
        error_count = 0
        
        for index_sql in indexes:
            try:
                # Extract index name for logging
                index_name = "unknown"
                if "idx_" in index_sql:
                    index_name = index_sql.split("idx_")[1].split(" ")[0]
                
                # Execute index creation
                db.session.execute(text(index_sql))
                logger.info(f"✅ Created index: idx_{index_name}")
                created_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error creating index: {e}")
                error_count += 1
        
        db.session.commit()
        
        # Create partial indexes for PostgreSQL
        if dialect == 'postgresql':
            partial_indexes = [
                # Partial indexes for better performance on filtered queries
                "CREATE INDEX IF NOT EXISTS idx_users_active_recent ON users(created_at) WHERE is_active = true;",
                "CREATE INDEX IF NOT EXISTS idx_beneficiaries_active_recent ON beneficiaries(created_at) WHERE is_active = true;",
                "CREATE INDEX IF NOT EXISTS idx_appointments_upcoming ON appointments(start_time) WHERE status = 'scheduled' AND start_time > NOW();",
                "CREATE INDEX IF NOT EXISTS idx_evaluations_pending ON evaluations(due_date) WHERE status = 'pending';",
                "CREATE INDEX IF NOT EXISTS idx_notifications_urgent ON notifications(created_at) WHERE priority = 'high' AND is_read = false;",
            ]
            
            for index_sql in partial_indexes:
                try:
                    db.session.execute(text(index_sql))
                    index_name = index_sql.split("idx_")[1].split(" ")[0]
                    logger.info(f"✅ Created partial index: idx_{index_name}")
                    created_count += 1
                except Exception as e:
                    logger.error(f"❌ Error creating partial index: {e}")
                    error_count += 1
            
            db.session.commit()
        
        # Update table statistics for query optimizer
        tables = [
            'users', 'beneficiaries', 'appointments', 'programs', 'program_enrollments',
            'documents', 'evaluations', 'notifications', 'user_activities', 'tests',
            'test_sessions', 'messages', 'message_threads', 'reports', 'folders',
            'training_sessions', 'session_attendance', 'token_blocklist'
        ]
        
        analyzed_count = 0
        for table in tables:
            try:
                if dialect == 'postgresql':
                    db.session.execute(text(f"ANALYZE {table};"))
                elif dialect == 'sqlite':
                    db.session.execute(text(f"ANALYZE {table};"))
                elif dialect == 'mysql':
                    db.session.execute(text(f"ANALYZE TABLE {table};"))
                
                logger.info(f"✅ Analyzed table: {table}")
                analyzed_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error analyzing table {table}: {e}")
        
        db.session.commit()
        
        # Create database-specific optimizations
        if dialect == 'postgresql':
            try:
                # Enable auto-vacuum for better performance
                db.session.execute(text("VACUUM ANALYZE;"))
                logger.info("✅ Executed VACUUM ANALYZE")
            except Exception as e:
                logger.error(f"❌ Error executing VACUUM ANALYZE: {e}")
        
        # Final summary
        logger.info(f"\n🎉 Database performance optimization completed!")
        logger.info(f"📊 Summary:")
        logger.info(f"   - Indexes created: {created_count}")
        logger.info(f"   - Tables analyzed: {analyzed_count}")
        logger.info(f"   - Errors encountered: {error_count}")
        logger.info(f"   - Database dialect: {dialect}")
        
        return {
            'indexes_created': created_count,
            'tables_analyzed': analyzed_count,
            'errors': error_count,
            'dialect': dialect
        }


def check_existing_indexes():
    """Check which indexes already exist"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        
        existing_indexes = {}
        for table in tables:
            try:
                indexes = inspector.get_indexes(table)
                existing_indexes[table] = [idx['name'] for idx in indexes]
                logger.info(f"Table {table}: {len(indexes)} existing indexes")
            except Exception as e:
                logger.error(f"Error checking indexes for table {table}: {e}")
        
        return existing_indexes


def analyze_index_usage():
    """Analyze index usage statistics (PostgreSQL only)"""
    app = create_app()
    
    with app.app_context():
        if db.engine.dialect.name != 'postgresql':
            logger.warning("Index usage analysis only available for PostgreSQL")
            return None
        
        try:
            # Query to get index usage statistics
            usage_query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC;
            """
            
            result = db.session.execute(text(usage_query))
            usage_stats = []
            
            for row in result:
                usage_stats.append({
                    'schema': row.schemaname,
                    'table': row.tablename,
                    'index': row.indexname,
                    'scans': row.idx_scan,
                    'tuples_read': row.idx_tup_read,
                    'tuples_fetched': row.idx_tup_fetch,
                    'size': row.index_size
                })
            
            logger.info(f"Analyzed usage for {len(usage_stats)} indexes")
            return usage_stats
            
        except Exception as e:
            logger.error(f"Error analyzing index usage: {e}")
            return None

if __name__ == '__main__':
    create_performance_indexes()