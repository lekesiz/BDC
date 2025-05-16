from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

from app.utils.logging import logger

class DatabaseOptimizer:
    """Database optimization utilities"""
    
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def analyze_slow_queries(self):
        """Analyze and log slow queries"""
        with self.engine.connect() as conn:
            # PostgreSQL example
            if 'postgresql' in str(self.engine.url):
                result = conn.execute(text("""
                    SELECT query, calls, mean_time, total_time
                    FROM pg_stat_statements
                    WHERE mean_time > 100
                    ORDER BY mean_time DESC
                    LIMIT 20
                """))
                
                slow_queries = []
                for row in result:
                    slow_queries.append({
                        'query': row.query,
                        'calls': row.calls,
                        'mean_time': row.mean_time,
                        'total_time': row.total_time
                    })
                
                return slow_queries
            
            # MySQL example
            elif 'mysql' in str(self.engine.url):
                result = conn.execute(text("""
                    SELECT * FROM mysql.slow_log
                    ORDER BY query_time DESC
                    LIMIT 20
                """))
                
                return list(result)
        
        return []
    
    def create_indexes(self):
        """Create optimized indexes"""
        indexes = [
            # Users table indexes
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
            "CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id)",
            
            # Beneficiaries table indexes
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_user_id ON beneficiaries(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_trainer_id ON beneficiaries(trainer_id)",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_status ON beneficiaries(status)",
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_enrollment_date ON beneficiaries(enrollment_date)",
            
            # Evaluations table indexes
            "CREATE INDEX IF NOT EXISTS idx_evaluations_beneficiary_id ON evaluations(beneficiary_id)",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_test_id ON evaluations(test_id)",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_status ON evaluations(status)",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_created_at ON evaluations(created_at)",
            
            # Appointments table indexes
            "CREATE INDEX IF NOT EXISTS idx_appointments_beneficiary_id ON appointments(beneficiary_id)",
            "CREATE INDEX IF NOT EXISTS idx_appointments_trainer_id ON appointments(trainer_id)",
            "CREATE INDEX IF NOT EXISTS idx_appointments_start_time ON appointments(start_time)",
            "CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)",
            
            # Documents table indexes
            "CREATE INDEX IF NOT EXISTS idx_documents_owner_id ON documents(owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category)",
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at)",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_beneficiaries_trainer_status ON beneficiaries(trainer_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_evaluations_beneficiary_status ON evaluations(beneficiary_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_appointments_trainer_date ON appointments(trainer_id, start_time)",
        ]
        
        with self.engine.connect() as conn:
            for index in indexes:
                try:
                    conn.execute(text(index))
                    conn.commit()
                    logger.info(f"Created index: {index}")
                except Exception as e:
                    logger.error(f"Error creating index: {e}")
    
    def optimize_tables(self):
        """Optimize database tables"""
        tables = [
            'users', 'beneficiaries', 'evaluations', 
            'appointments', 'documents', 'messages'
        ]
        
        with self.engine.connect() as conn:
            for table in tables:
                try:
                    if 'postgresql' in str(self.engine.url):
                        # PostgreSQL VACUUM and ANALYZE
                        conn.execute(text(f"VACUUM ANALYZE {table}"))
                    elif 'mysql' in str(self.engine.url):
                        # MySQL OPTIMIZE TABLE
                        conn.execute(text(f"OPTIMIZE TABLE {table}"))
                    
                    conn.commit()
                    logger.info(f"Optimized table: {table}")
                except Exception as e:
                    logger.error(f"Error optimizing table {table}: {e}")
    
    def partition_large_tables(self):
        """Setup partitioning for large tables"""
        # Example: Partition evaluations table by month
        if 'postgresql' in str(self.engine.url):
            partition_sql = """
            -- Create parent table for partitioning
            CREATE TABLE IF NOT EXISTS evaluations_partitioned (
                LIKE evaluations INCLUDING ALL
            ) PARTITION BY RANGE (created_at);
            
            -- Create monthly partitions
            CREATE TABLE IF NOT EXISTS evaluations_2024_01 
                PARTITION OF evaluations_partitioned
                FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
                
            CREATE TABLE IF NOT EXISTS evaluations_2024_02 
                PARTITION OF evaluations_partitioned
                FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
            
            -- Continue for other months...
            """
            
            with self.engine.connect() as conn:
                try:
                    conn.execute(text(partition_sql))
                    conn.commit()
                    logger.info("Created partitioned tables")
                except Exception as e:
                    logger.error(f"Error creating partitions: {e}")
    
    def configure_connection_pooling(self):
        """Configure database connection pooling"""
        pool_config = {
            'pool_size': 20,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'pool_pre_ping': True
        }
        
        return pool_config
    
    def generate_query_execution_plans(self):
        """Generate execution plans for common queries"""
        queries = [
            """
            SELECT b.*, u.first_name, u.last_name, u.email
            FROM beneficiaries b
            JOIN users u ON b.user_id = u.id
            WHERE b.trainer_id = :trainer_id AND b.status = 'active'
            """,
            """
            SELECT e.*, t.title as test_title
            FROM evaluations e
            JOIN tests t ON e.test_id = t.id
            WHERE e.beneficiary_id = :beneficiary_id
            ORDER BY e.created_at DESC
            LIMIT 10
            """,
            """
            SELECT a.*, b.user_id, u.first_name, u.last_name
            FROM appointments a
            JOIN beneficiaries b ON a.beneficiary_id = b.id
            JOIN users u ON b.user_id = u.id
            WHERE a.trainer_id = :trainer_id 
            AND a.start_time >= :start_date
            AND a.start_time <= :end_date
            ORDER BY a.start_time
            """
        ]
        
        execution_plans = []
        with self.engine.connect() as conn:
            for query in queries:
                if 'postgresql' in str(self.engine.url):
                    plan_query = f"EXPLAIN ANALYZE {query}"
                elif 'mysql' in str(self.engine.url):
                    plan_query = f"EXPLAIN {query}"
                
                try:
                    result = conn.execute(text(plan_query), {
                        'trainer_id': 1,
                        'beneficiary_id': 1,
                        'start_date': '2024-01-01',
                        'end_date': '2024-12-31'
                    })
                    
                    execution_plans.append({
                        'query': query,
                        'plan': list(result)
                    })
                except Exception as e:
                    logger.error(f"Error generating execution plan: {e}")
        
        return execution_plans
    
    def setup_materialized_views(self):
        """Create materialized views for complex queries"""
        if 'postgresql' in str(self.engine.url):
            views = [
                """
                CREATE MATERIALIZED VIEW IF NOT EXISTS beneficiary_progress AS
                SELECT 
                    b.id,
                    b.user_id,
                    COUNT(DISTINCT e.id) as total_evaluations,
                    AVG(e.score) as average_score,
                    MAX(e.created_at) as last_evaluation_date,
                    COUNT(DISTINCT a.id) as total_appointments
                FROM beneficiaries b
                LEFT JOIN evaluations e ON b.id = e.beneficiary_id
                LEFT JOIN appointments a ON b.id = a.beneficiary_id
                GROUP BY b.id, b.user_id
                """,
                """
                CREATE MATERIALIZED VIEW IF NOT EXISTS trainer_statistics AS
                SELECT 
                    t.id as trainer_id,
                    COUNT(DISTINCT b.id) as total_beneficiaries,
                    COUNT(DISTINCT a.id) as total_appointments,
                    AVG(e.score) as average_beneficiary_score
                FROM users t
                LEFT JOIN beneficiaries b ON t.id = b.trainer_id
                LEFT JOIN appointments a ON t.id = a.trainer_id
                LEFT JOIN evaluations e ON b.id = e.beneficiary_id
                WHERE t.role = 'trainer'
                GROUP BY t.id
                """
            ]
            
            with self.engine.connect() as conn:
                for view in views:
                    try:
                        conn.execute(text(view))
                        conn.commit()
                        logger.info(f"Created materialized view")
                    except Exception as e:
                        logger.error(f"Error creating materialized view: {e}")
    
    def update_statistics(self):
        """Update database statistics for query optimizer"""
        with self.engine.connect() as conn:
            if 'postgresql' in str(self.engine.url):
                conn.execute(text("ANALYZE"))
            elif 'mysql' in str(self.engine.url):
                tables = ['users', 'beneficiaries', 'evaluations', 'appointments']
                for table in tables:
                    conn.execute(text(f"ANALYZE TABLE {table}"))
            
            conn.commit()
            logger.info("Updated database statistics")
    
    def configure_query_cache(self):
        """Configure query caching"""
        cache_config = {
            'query_cache_size': '256M',
            'query_cache_type': 'ON',
            'query_cache_limit': '2M'
        }
        
        if 'mysql' in str(self.engine.url):
            with self.engine.connect() as conn:
                for key, value in cache_config.items():
                    try:
                        conn.execute(text(f"SET GLOBAL {key} = '{value}'"))
                        logger.info(f"Set {key} = {value}")
                    except Exception as e:
                        logger.error(f"Error setting {key}: {e}")
        
        return cache_config


if __name__ == "__main__":
    # Example usage
    optimizer = DatabaseOptimizer('postgresql://user:pass@localhost/bdc')
    
    # Run optimizations
    optimizer.create_indexes()
    optimizer.optimize_tables()
    optimizer.update_statistics()
    
    # Analyze slow queries
    slow_queries = optimizer.analyze_slow_queries()
    for query in slow_queries:
        print(f"Slow query: {query['query'][:100]}... (Mean time: {query['mean_time']}ms)")
    
    # Generate execution plans
    plans = optimizer.generate_query_execution_plans()
    for plan in plans:
        print(f"Query: {plan['query'][:100]}...")
        print(f"Plan: {plan['plan']}") 