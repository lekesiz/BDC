"""Simple seed database script."""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime


def init_db():
    """Initialize database with seed data."""
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create default tenant
        tenant_exists = db.session.execute(
            db.text("SELECT COUNT(*) FROM tenants")
        ).scalar()
        
        if tenant_exists:
            print("Database already contains data. Skipping seed.")
            return
        
        # Insert tenant
        db.session.execute(
            db.text("""
                INSERT INTO tenants (name, slug, email, plan, max_users, max_beneficiaries, is_active, created_at, updated_at)
                VALUES (:name, :slug, :email, :plan, :max_users, :max_beneficiaries, :is_active, :created_at, :updated_at)
            """),
            {
                'name': 'BDC Demo',
                'slug': 'demo',
                'email': 'demo@bdc.com',
                'plan': 'pro',
                'max_users': 50,
                'max_beneficiaries': 200,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        )
        db.session.commit()
        
        # Get tenant ID
        tenant_id = db.session.execute(
            db.text("SELECT id FROM tenants WHERE slug = 'demo'")
        ).scalar()
        
        # Create users
        users = [
            {
                'email': 'admin@bdc.com',
                'password': 'Admin123!',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'super_admin'
            },
            {
                'email': 'tenant@bdc.com',
                'password': 'Tenant123!',
                'first_name': 'Tenant',
                'last_name': 'Admin',
                'role': 'tenant_admin'
            },
            {
                'email': 'trainer@bdc.com',
                'password': 'Trainer123!',
                'first_name': 'Trainer',
                'last_name': 'User',
                'role': 'trainer'
            },
            {
                'email': 'student@bdc.com',
                'password': 'Student123!',
                'first_name': 'Student',
                'last_name': 'User',
                'role': 'student'
            }
        ]
        
        for user_data in users:
            # Insert user
            db.session.execute(
                db.text("""
                    INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, created_at, updated_at)
                    VALUES (:email, :password_hash, :first_name, :last_name, :role, :is_active, :created_at, :updated_at)
                """),
                {
                    'email': user_data['email'],
                    'password_hash': generate_password_hash(user_data['password']),
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'is_active': True,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            )
            db.session.commit()
            
            # Get user ID
            user_id = db.session.execute(
                db.text("SELECT id FROM users WHERE email = :email"),
                {'email': user_data['email']}
            ).scalar()
            
            # Associate user with tenant
            db.session.execute(
                db.text("""
                    INSERT INTO user_tenant (user_id, tenant_id)
                    VALUES (:user_id, :tenant_id)
                """),
                {
                    'user_id': user_id,
                    'tenant_id': tenant_id
                }
            )
            db.session.commit()
            
            print(f"Created user: {user_data['email']} with role: {user_data['role']}")
        
        print("\nDatabase seeded successfully!")
        print("\nDefault credentials:")
        print("Super Admin: admin@bdc.com / Admin123!")
        print("Tenant Admin: tenant@bdc.com / Tenant123!")
        print("Trainer: trainer@bdc.com / Trainer123!")
        print("Student: student@bdc.com / Student123!")


if __name__ == '__main__':
    init_db()