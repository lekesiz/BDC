import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations

logger = logging.getLogger(__name__)

class MigrationManager:
    """Database migration management"""
    
    def __init__(self, database_url, alembic_ini_path=None):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        
        # Setup Alembic configuration
        if alembic_ini_path:
            self.alembic_cfg = Config(alembic_ini_path)
        else:
            self.alembic_cfg = Config()
            self.alembic_cfg.set_main_option("script_location", "alembic")
            self.alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    def init_migrations(self):
        """Initialize migration environment"""
        try:
            command.init(self.alembic_cfg, "alembic")
            logger.info("Initialized migration environment")
        except Exception as e:
            logger.error(f"Error initializing migrations: {e}")
    
    def create_migration(self, message):
        """Create a new migration"""
        try:
            command.revision(self.alembic_cfg, autogenerate=True, message=message)
            logger.info(f"Created migration: {message}")
        except Exception as e:
            logger.error(f"Error creating migration: {e}")
    
    def run_migrations(self):
        """Run pending migrations"""
        try:
            command.upgrade(self.alembic_cfg, "head")
            logger.info("Migrations completed successfully")
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            raise
    
    def rollback_migration(self, steps=1):
        """Rollback migrations"""
        try:
            command.downgrade(self.alembic_cfg, f"-{steps}")
            logger.info(f"Rolled back {steps} migration(s)")
        except Exception as e:
            logger.error(f"Error rolling back migrations: {e}")
    
    def get_current_revision(self):
        """Get current database revision"""
        with self.engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
    
    def get_migration_history(self):
        """Get migration history"""
        try:
            history = command.history(self.alembic_cfg)
            return history
        except Exception as e:
            logger.error(f"Error getting migration history: {e}")
            return []
    
    def validate_migrations(self):
        """Validate migration files"""
        issues = []
        
        # Check for naming conventions
        migration_dir = self.alembic_cfg.get_main_option("script_location")
        if os.path.exists(migration_dir):
            for filename in os.listdir(os.path.join(migration_dir, "versions")):
                if filename.endswith(".py") and not filename.startswith("_"):
                    # Check naming pattern (timestamp_description.py)
                    if not filename[0:14].isdigit():
                        issues.append(f"Invalid migration filename: {filename}")
        
        return issues
    
    def backup_before_migration(self, backup_path):
        """Create database backup before migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_path, f"backup_{timestamp}.sql")
        
        if 'postgresql' in self.database_url:
            db_name = self.database_url.split('/')[-1]
            cmd = f"pg_dump {db_name} > {backup_file}"
        elif 'mysql' in self.database_url:
            db_name = self.database_url.split('/')[-1]
            cmd = f"mysqldump {db_name} > {backup_file}"
        else:
            logger.warning("Backup not supported for this database type")
            return None
        
        try:
            os.system(cmd)
            logger.info(f"Created backup: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def apply_data_migrations(self):
        """Apply data-only migrations"""
        data_migrations = [
            self._migrate_user_roles,
            self._migrate_beneficiary_statuses,
            self._normalize_phone_numbers,
            self._update_timestamps
        ]
        
        for migration in data_migrations:
            try:
                migration()
            except Exception as e:
                logger.error(f"Error in data migration {migration.__name__}: {e}")
    
    def _migrate_user_roles(self):
        """Migrate user roles to new format"""
        with self.engine.connect() as conn:
            # Example: Convert old role names to new ones
            conn.execute(text("""
                UPDATE users 
                SET role = CASE 
                    WHEN role = 'admin' THEN 'super_admin'
                    WHEN role = 'teacher' THEN 'trainer'
                    WHEN role = 'student' THEN 'beneficiary'
                    ELSE role
                END
            """))
            conn.commit()
            logger.info("Migrated user roles")
    
    def _migrate_beneficiary_statuses(self):
        """Migrate beneficiary statuses"""
        with self.engine.connect() as conn:
            # Example: Standardize status values
            conn.execute(text("""
                UPDATE beneficiaries 
                SET status = CASE 
                    WHEN status IN ('active', 'enrolled') THEN 'active'
                    WHEN status IN ('inactive', 'paused') THEN 'inactive'
                    WHEN status IN ('completed', 'graduated') THEN 'completed'
                    ELSE status
                END
            """))
            conn.commit()
            logger.info("Migrated beneficiary statuses")
    
    def _normalize_phone_numbers(self):
        """Normalize phone number formats"""
        with self.engine.connect() as conn:
            # Example: Standardize phone number format
            conn.execute(text("""
                UPDATE beneficiaries 
                SET phone = REGEXP_REPLACE(phone, '[^0-9+]', '', 'g')
                WHERE phone IS NOT NULL
            """))
            conn.commit()
            logger.info("Normalized phone numbers")
    
    def _update_timestamps(self):
        """Update missing timestamps"""
        with self.engine.connect() as conn:
            # Set created_at for records missing it
            tables = ['users', 'beneficiaries', 'evaluations', 'appointments']
            for table in tables:
                conn.execute(text(f"""
                    UPDATE {table} 
                    SET created_at = NOW() 
                    WHERE created_at IS NULL
                """))
            conn.commit()
            logger.info("Updated missing timestamps")
    
    def check_migration_conflicts(self):
        """Check for potential migration conflicts"""
        conflicts = []
        
        # Check for duplicate migration names
        migration_dir = os.path.join(
            self.alembic_cfg.get_main_option("script_location"), 
            "versions"
        )
        
        if os.path.exists(migration_dir):
            migrations = {}
            for filename in os.listdir(migration_dir):
                if filename.endswith(".py"):
                    # Extract migration description
                    parts = filename.split("_", 1)
                    if len(parts) > 1:
                        desc = parts[1].replace(".py", "")
                        if desc in migrations:
                            conflicts.append(f"Duplicate migration: {desc}")
                        migrations[desc] = filename
        
        return conflicts
    
    def generate_migration_report(self):
        """Generate migration status report"""
        report = {
            'current_revision': self.get_current_revision(),
            'pending_migrations': [],
            'applied_migrations': [],
            'conflicts': self.check_migration_conflicts(),
            'validation_issues': self.validate_migrations()
        }
        
        # Get pending migrations
        try:
            # This would need actual implementation to compare
            # current revision with available migrations
            pass
        except Exception as e:
            logger.error(f"Error generating report: {e}")
        
        return report


class MigrationScript:
    """Base class for custom migration scripts"""
    
    def __init__(self, engine):
        self.engine = engine
        self.connection = None
        self.op = None
    
    def upgrade(self):
        """Upgrade migration logic"""
        raise NotImplementedError
    
    def downgrade(self):
        """Downgrade migration logic"""
        raise NotImplementedError
    
    def execute(self, direction='upgrade'):
        """Execute migration"""
        with self.engine.connect() as connection:
            self.connection = connection
            self.op = Operations(MigrationContext.configure(connection))
            
            if direction == 'upgrade':
                self.upgrade()
            else:
                self.downgrade()
            
            connection.commit()


# Example custom migration
class AddIndexesMigration(MigrationScript):
    """Migration to add performance indexes"""
    
    def upgrade(self):
        # Add indexes
        self.op.create_index(
            'idx_beneficiaries_trainer_status',
            'beneficiaries',
            ['trainer_id', 'status']
        )
        
        self.op.create_index(
            'idx_evaluations_beneficiary_created',
            'evaluations',
            ['beneficiary_id', 'created_at']
        )
    
    def downgrade(self):
        # Remove indexes
        self.op.drop_index('idx_beneficiaries_trainer_status')
        self.op.drop_index('idx_evaluations_beneficiary_created')


if __name__ == "__main__":
    # Example usage
    manager = MigrationManager('postgresql://user:pass@localhost/bdc')
    
    # Initialize migrations
    manager.init_migrations()
    
    # Create a new migration
    manager.create_migration("add_user_preferences_table")
    
    # Run migrations
    manager.run_migrations()
    
    # Get status
    print(f"Current revision: {manager.get_current_revision()}")
    
    # Generate report
    report = manager.generate_migration_report()
    print(f"Migration report: {report}")