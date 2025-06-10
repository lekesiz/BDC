"""User model module."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.extensions import db

# User roles
class UserRole:
    SUPER_ADMIN = 'super_admin'
    TENANT_ADMIN = 'tenant_admin'
    TRAINER = 'trainer'
    STUDENT = 'student'
    TRAINEE = 'trainee'  # Frontend uyumluluğu için eklendi
    
    ROLES = [SUPER_ADMIN, TENANT_ADMIN, TRAINER, STUDENT, TRAINEE]

# User-Tenant association table
user_tenant = Table(
    'user_tenant',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('tenant_id', Integer, ForeignKey('tenants.id'), primary_key=True)
)

class User(db.Model):
    """User model."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=True)
    password_hash = Column(String(256), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional profile fields
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Email verification fields
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)
    organization = Column(String(255), nullable=True)
    bio = Column(db.Text, nullable=True)
    profile_picture = Column(String(255), nullable=True)
    
    # Preference fields
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=False)
    sms_notifications = Column(Boolean, default=False)
    language = Column(String(10), default='en')
    theme = Column(String(20), default='light')
    
    # Foreign key to tenant
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    tenants = relationship('Tenant', secondary=user_tenant, back_populates='users', lazy='select')
    folders = relationship('Folder', back_populates='owner', lazy='select')
    reports = relationship('Report', back_populates='created_by', lazy='select')
    programs_created = relationship('Program', back_populates='created_by', lazy='select')
    training_sessions = relationship('TrainingSession', back_populates='trainer', lazy='select')
    
    @property
    def full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def password(self):
        """Password getter (not allowed)."""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_profile=False):
        """Return a dict representation of the user."""
        user_dict = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'tenant_id': self.tenant_id,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        # Include profile data if requested
        if include_profile:
            user_dict.update({
                'phone': self.phone,
                'address': self.address,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code,
                'country': self.country,
                'organization': self.organization,
                'bio': self.bio,
                'profile_picture': self.profile_picture
            })
            
        return user_dict
    
    def __repr__(self):
        """String representation of the user."""
        return f'<User {self.email}>'



class TokenBlocklist(db.Model):
    """Token blocklist for JWT tokens."""
    __tablename__ = 'token_blocklist'
    
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False, index=True)
    token_type = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    revoked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    def to_dict(self):
        """Return a dict representation of the token blocklist entry."""
        return {
            'id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_id': self.user_id,
            'revoked_at': self.revoked_at.isoformat(),
            'expires_at': self.expires_at.isoformat()
        }