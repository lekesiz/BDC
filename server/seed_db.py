"""Seed database with initial data."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Tenant, UserRole
from werkzeug.security import generate_password_hash


def create_default_tenant():
    """Create default tenant."""
    tenant = Tenant(
        name="BDC Demo",
        slug="demo",
        email="demo@bdc.com",
        plan="pro",
        max_users=50,
        max_beneficiaries=200,
        is_active=True
    )
    db.session.add(tenant)
    db.session.commit()
    return tenant


def create_default_users(tenant):
    """Create default users."""
    users = [
        {
            'email': 'admin@bdc.com',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': UserRole.SUPER_ADMIN
        },
        {
            'email': 'tenant@bdc.com',
            'password': 'Tenant123!',
            'first_name': 'Tenant',
            'last_name': 'Admin',
            'role': UserRole.TENANT_ADMIN
        },
        {
            'email': 'trainer@bdc.com',
            'password': 'Trainer123!',
            'first_name': 'Trainer',
            'last_name': 'User',
            'role': UserRole.TRAINER
        },
        {
            'email': 'student@bdc.com',
            'password': 'Student123!',
            'first_name': 'Student',
            'last_name': 'User',
            'role': UserRole.STUDENT
        }
    ]
    
    created_users = []
    for user_data in users:
        user = User(
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'].value if hasattr(user_data['role'], 'value') else user_data['role'],
            is_active=True
        )
        user.tenants.append(tenant)
        db.session.add(user)
        created_users.append(user)
    
    db.session.commit()
    return created_users


def init_db():
    """Initialize database with seed data."""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("Database already contains data. Skipping seed.")
            return
        
        # Create default tenant
        tenant = create_default_tenant()
        print(f"Created tenant: {tenant.name}")
        
        # Create default users
        users = create_default_users(tenant)
        for user in users:
            print(f"Created user: {user.email} with role: {user.role}")
        
        print("\nDatabase seeded successfully!")
        print("\nDefault credentials:")
        print("Super Admin: admin@bdc.com / Admin123!")
        print("Tenant Admin: tenant@bdc.com / Tenant123!")
        print("Trainer: trainer@bdc.com / Trainer123!")
        print("Student: student@bdc.com / Student123!")


if __name__ == '__main__':
    init_db()