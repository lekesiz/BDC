"""Database management and migration system."""

import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from flask import Flask, current_app
from sqlalchemy.exc import SQLAlchemyError


class MigrationStatus(Enum):
    """Migration execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    status: MigrationStatus
    message: str
    error: Optional[Exception] = None


class IDatabaseMigration(ABC):
    """Interface for database migrations."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get migration name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get migration version."""
        pass
    
    @abstractmethod
    def execute(self) -> MigrationResult:
        """Execute the migration."""
        pass
    
    @abstractmethod
    def rollback(self) -> MigrationResult:
        """Rollback the migration."""
        pass
    
    @abstractmethod
    def can_execute(self) -> bool:
        """Check if migration can be executed."""
        pass


class DatabaseInitializer:
    """Handles database initialization with proper separation of concerns."""
    
    def __init__(self):
        """Initialize database initializer."""
        self._logger = logging.getLogger(__name__)
    
    def initialize_database(self, app: Flask, create_tables: bool = True, 
                          create_test_data: bool = False) -> bool:
        """Initialize database with optional test data creation.
        
        Args:
            app: Flask application instance
            create_tables: Whether to create database tables
            create_test_data: Whether to create test users and data
            
        Returns:
            True if initialization was successful
        """
        try:
            with app.app_context():
                if create_tables:
                    self._create_tables()
                
                if create_test_data:
                    self._create_test_data()
            
            self._logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Database initialization failed: {e}")
            return False
    
    def _create_tables(self) -> None:
        """Create database tables."""
        from app.extensions import db
        
        try:
            db.create_all()
            self._logger.info("Database tables created")
        except SQLAlchemyError as e:
            self._logger.error(f"Failed to create tables: {e}")
            raise
    
    def _create_test_data(self) -> None:
        """Create test data for development/testing."""
        try:
            self._create_default_tenant()
            self._create_test_users()
            self._logger.info("Test data created successfully")
        except Exception as e:
            self._logger.error(f"Failed to create test data: {e}")
            raise
    
    def _create_default_tenant(self) -> None:
        """Create default tenant if needed."""
        from app.models.tenant import Tenant
        from app.extensions import db
        
        tenant = Tenant.query.first()
        if not tenant:
            tenant = Tenant(
                name='Default',
                slug='default',
                email='admin@default.com',
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            self._logger.info("Created default tenant")
    
    def _create_test_users(self) -> None:
        """Create test users."""
        from app.models.user import User
        from app.models.tenant import Tenant
        from app.extensions import db
        
        tenant = Tenant.query.first()
        if not tenant:
            self._logger.error("No tenant available for user creation")
            return
        
        # Define test users
        test_users = [
            {
                'email': 'admin@bdc.com',
                'username': 'admin',
                'password': 'Admin123!',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'super_admin'
            },
            {
                'email': 'tenant@bdc.com',
                'username': 'tenant',
                'password': 'Tenant123!',
                'first_name': 'Tenant',
                'last_name': 'Admin',
                'role': 'tenant_admin'
            },
            {
                'email': 'trainer@bdc.com',
                'username': 'trainer',
                'password': 'Trainer123!',
                'first_name': 'Trainer',
                'last_name': 'User',
                'role': 'trainer'
            },
            {
                'email': 'student@bdc.com',
                'username': 'student',
                'password': 'Student123!',
                'first_name': 'Student',
                'last_name': 'User',
                'role': 'student'
            }
        ]
        
        # Create or update test users
        for user_data in test_users:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=True,
                    tenant_id=tenant.id
                )
                db.session.add(user)
                self._logger.info(f"Created user: {user_data['email']}")
            
            # Reset password for testing
            user.password = user_data['password']
            
            # Add tenant relationship if needed
            if hasattr(user, 'tenants') and tenant not in user.tenants:
                user.tenants.append(tenant)
        
        db.session.commit()
        total_users = User.query.count()
        self._logger.info(f"Total users in database: {total_users}")


class DefaultTenantMigration(IDatabaseMigration):
    """Migration to create default tenant."""
    
    def get_name(self) -> str:
        return "create_default_tenant"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def execute(self) -> MigrationResult:
        """Execute the migration."""
        try:
            from app.models.tenant import Tenant
            from app.extensions import db
            
            # Check if default tenant already exists
            existing_tenant = Tenant.query.filter_by(slug='default').first()
            if existing_tenant:
                return MigrationResult(
                    status=MigrationStatus.SKIPPED,
                    message="Default tenant already exists"
                )
            
            # Create default tenant
            tenant = Tenant(
                name='Default',
                slug='default',
                email='admin@default.com',
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            
            return MigrationResult(
                status=MigrationStatus.SUCCESS,
                message="Default tenant created successfully"
            )
            
        except Exception as e:
            return MigrationResult(
                status=MigrationStatus.FAILED,
                message=f"Failed to create default tenant: {e}",
                error=e
            )
    
    def rollback(self) -> MigrationResult:
        """Rollback the migration."""
        try:
            from app.models.tenant import Tenant
            from app.extensions import db
            
            tenant = Tenant.query.filter_by(slug='default').first()
            if tenant:
                db.session.delete(tenant)
                db.session.commit()
            
            return MigrationResult(
                status=MigrationStatus.SUCCESS,
                message="Default tenant removed successfully"
            )
            
        except Exception as e:
            return MigrationResult(
                status=MigrationStatus.FAILED,
                message=f"Failed to remove default tenant: {e}",
                error=e
            )
    
    def can_execute(self) -> bool:
        """Check if migration can be executed."""
        try:
            from app.models.tenant import Tenant
            return Tenant.query.filter_by(slug='default').first() is None
        except Exception:
            return True


class AdminUserMigration(IDatabaseMigration):
    """Migration to create admin user."""
    
    def get_name(self) -> str:
        return "create_admin_user"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def execute(self) -> MigrationResult:
        """Execute the migration."""
        try:
            from app.models.user import User
            from app.models.tenant import Tenant
            from app.extensions import db
            
            # Check if admin user already exists
            existing_user = User.query.filter_by(email='admin@bdc.com').first()
            if existing_user:
                return MigrationResult(
                    status=MigrationStatus.SKIPPED,
                    message="Admin user already exists"
                )
            
            # Get default tenant
            tenant = Tenant.query.filter_by(slug='default').first()
            if not tenant:
                return MigrationResult(
                    status=MigrationStatus.FAILED,
                    message="Default tenant not found, run create_default_tenant migration first"
                )
            
            # Create admin user
            admin_user = User(
                email='admin@bdc.com',
                username='admin',
                first_name='Admin',
                last_name='User',
                role='super_admin',
                is_active=True,
                tenant_id=tenant.id
            )
            admin_user.password = 'Admin123!'
            
            db.session.add(admin_user)
            db.session.commit()
            
            return MigrationResult(
                status=MigrationStatus.SUCCESS,
                message="Admin user created successfully"
            )
            
        except Exception as e:
            return MigrationResult(
                status=MigrationStatus.FAILED,
                message=f"Failed to create admin user: {e}",
                error=e
            )
    
    def rollback(self) -> MigrationResult:
        """Rollback the migration."""
        try:
            from app.models.user import User
            from app.extensions import db
            
            user = User.query.filter_by(email='admin@bdc.com').first()
            if user:
                db.session.delete(user)
                db.session.commit()
            
            return MigrationResult(
                status=MigrationStatus.SUCCESS,
                message="Admin user removed successfully"
            )
            
        except Exception as e:
            return MigrationResult(
                status=MigrationStatus.FAILED,
                message=f"Failed to remove admin user: {e}",
                error=e
            )
    
    def can_execute(self) -> bool:
        """Check if migration can be executed."""
        try:
            from app.models.user import User
            return User.query.filter_by(email='admin@bdc.com').first() is None
        except Exception:
            return True


class DatabaseMigrationManager:
    """Manages database migrations."""
    
    def __init__(self):
        """Initialize migration manager."""
        self._migrations: Dict[str, IDatabaseMigration] = {}
        self._logger = logging.getLogger(__name__)
        
        # Register default migrations
        self._register_default_migrations()
    
    def _register_default_migrations(self) -> None:
        """Register default migrations."""
        self.register_migration(DefaultTenantMigration())
        self.register_migration(AdminUserMigration())
    
    def register_migration(self, migration: IDatabaseMigration) -> None:
        """Register a migration."""
        name = migration.get_name()
        self._migrations[name] = migration
        self._logger.debug(f"Registered migration: {name}")
    
    def run_migration(self, migration_name: str) -> MigrationResult:
        """Run a specific migration."""
        if migration_name not in self._migrations:
            return MigrationResult(
                status=MigrationStatus.FAILED,
                message=f"Migration {migration_name} not found"
            )
        
        migration = self._migrations[migration_name]
        
        if not migration.can_execute():
            return MigrationResult(
                status=MigrationStatus.SKIPPED,
                message=f"Migration {migration_name} cannot be executed"
            )
        
        self._logger.info(f"Running migration: {migration_name}")
        result = migration.execute()
        
        if result.status == MigrationStatus.SUCCESS:
            self._logger.info(f"Migration {migration_name} completed: {result.message}")
        else:
            self._logger.error(f"Migration {migration_name} failed: {result.message}")
        
        return result
    
    def run_all_migrations(self) -> List[MigrationResult]:
        """Run all registered migrations."""
        results = []
        
        self._logger.info("Running all migrations")
        
        for migration_name in self._migrations.keys():
            result = self.run_migration(migration_name)
            results.append(result)
        
        successful = sum(1 for r in results if r.status == MigrationStatus.SUCCESS)
        skipped = sum(1 for r in results if r.status == MigrationStatus.SKIPPED)
        failed = sum(1 for r in results if r.status == MigrationStatus.FAILED)
        
        self._logger.info(f"Migration summary: {successful} successful, {skipped} skipped, {failed} failed")
        
        return results
    
    def get_available_migrations(self) -> List[str]:
        """Get list of available migrations."""
        return list(self._migrations.keys())


# Global instances
database_initializer = DatabaseInitializer()
migration_manager = DatabaseMigrationManager()