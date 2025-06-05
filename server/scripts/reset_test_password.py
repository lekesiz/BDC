#!/usr/bin/env python
"""Reset test user password."""

from app import create_app
from app.models import User
from app.extensions import db
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)

with app.app_context():
    # Reset admin password
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if admin:
        admin.password = 'admin123'
        db.session.commit()
        print(f"Reset password for {admin.email} to: admin123")
    
    # Reset tenant admin password  
    tenant_admin = User.query.filter_by(email='tenant@bdc.com').first()
    if tenant_admin:
        tenant_admin.password = 'admin123'
        db.session.commit()
        print(f"Reset password for {tenant_admin.email} to: admin123")