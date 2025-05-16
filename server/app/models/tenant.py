"""Tenant model for multi-tenancy support."""
from datetime import datetime
from sqlalchemy.orm import relationship
from app.extensions import db


class Tenant(db.Model):
    """Tenant model."""
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    # Contact information
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Subscription details
    plan = db.Column(db.String(50), default='basic')  # basic, pro, enterprise
    max_users = db.Column(db.Integer, default=10)
    max_beneficiaries = db.Column(db.Integer, default=50)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    activation_date = db.Column(db.DateTime)
    expiration_date = db.Column(db.DateTime)
    
    # Settings
    settings = db.Column(db.JSON, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship('User', secondary='user_tenant', back_populates='tenants')
    folders = relationship('Folder', back_populates='tenant', lazy='dynamic')
    reports = relationship('Report', back_populates='tenant', lazy='dynamic')
    programs = relationship('Program', back_populates='tenant', lazy='dynamic')
    
    def to_dict(self):
        """Convert tenant to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'plan': self.plan,
            'max_users': self.max_users,
            'max_beneficiaries': self.max_beneficiaries,
            'is_active': self.is_active,
            'activation_date': self.activation_date.isoformat() if self.activation_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'settings': self.settings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }