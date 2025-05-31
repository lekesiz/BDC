"""Permission and Role models."""
from datetime import datetime

from app.extensions import db


# Association table for many-to-many relationship between roles and permissions
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Permission(db.Model):
    """Model for permissions."""
    
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    resource = db.Column(db.String(50))  # e.g., 'users', 'beneficiaries'
    action = db.Column(db.String(50))    # e.g., 'create', 'read', 'update', 'delete'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """String representation."""
        return f'<Permission {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'action': self.action
        }


class Role(db.Model):
    """Model for roles."""
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_system = db.Column(db.Boolean, default=False)  # System roles can't be deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('Permission', secondary=role_permissions, 
                                lazy='subquery',
                                backref=db.backref('roles', lazy=True))
    
    def __repr__(self):
        """String representation."""
        return f'<Role {self.name}>'
    
    def has_permission(self, permission_name):
        """Check if role has a specific permission."""
        return any(p.name == permission_name for p in self.permissions)
    
    def add_permission(self, permission):
        """Add a permission to this role."""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission):
        """Remove a permission from this role."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_system': self.is_system,
            'permissions': [p.to_dict() for p in self.permissions]
        }