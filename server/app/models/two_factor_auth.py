"""Two-Factor Authentication models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import pyotp
import qrcode
import io
import base64
from app.extensions import db


class TwoFactorAuth(db.Model):
    """Two-Factor Authentication settings for users."""
    __tablename__ = 'two_factor_auth'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # TOTP Secret
    secret = Column(String(32), nullable=False)
    
    # Backup codes (stored as comma-separated encrypted values)
    backup_codes = Column(Text, nullable=True)
    
    # Status
    is_enabled = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    enabled_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='two_factor_auth', uselist=False)
    
    def generate_secret(self):
        """Generate a new TOTP secret."""
        self.secret = pyotp.random_base32()
        return self.secret
    
    def get_totp_uri(self, app_name='BDC'):
        """Get the TOTP URI for QR code generation."""
        if not self.user:
            raise ValueError("User not associated with 2FA settings")
        
        totp = pyotp.TOTP(self.secret)
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name=app_name
        )
    
    def generate_qr_code(self, app_name='BDC'):
        """Generate QR code for TOTP setup."""
        uri = self.get_totp_uri(app_name)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for easy embedding
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_token(self, token):
        """Verify a TOTP token."""
        totp = pyotp.TOTP(self.secret)
        # Allow for time drift (valid_window=1 means +/- 30 seconds)
        is_valid = totp.verify(token, valid_window=1)
        
        if is_valid:
            self.last_used_at = datetime.utcnow()
            db.session.commit()
        
        return is_valid
    
    def generate_backup_codes(self, count=10):
        """Generate backup codes."""
        import secrets
        codes = []
        
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_hex(4).upper()
            codes.append(code)
        
        # Store hashed versions
        from werkzeug.security import generate_password_hash
        hashed_codes = [generate_password_hash(code) for code in codes]
        self.backup_codes = ','.join(hashed_codes)
        
        return codes  # Return plain codes to show user once
    
    def verify_backup_code(self, code):
        """Verify and consume a backup code."""
        if not self.backup_codes:
            return False
        
        from werkzeug.security import check_password_hash
        
        codes = self.backup_codes.split(',')
        remaining_codes = []
        code_valid = False
        
        for hashed_code in codes:
            if not code_valid and check_password_hash(hashed_code, code.upper()):
                code_valid = True
                # Don't add this code back (consume it)
            else:
                remaining_codes.append(hashed_code)
        
        if code_valid:
            self.backup_codes = ','.join(remaining_codes) if remaining_codes else None
            self.last_used_at = datetime.utcnow()
            db.session.commit()
        
        return code_valid
    
    def disable(self):
        """Disable 2FA for the user."""
        self.is_enabled = False
        self.is_verified = False
        self.backup_codes = None
        self.enabled_at = None
        db.session.commit()
    
    def to_dict(self):
        """Return a dict representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'is_enabled': self.is_enabled,
            'is_verified': self.is_verified,
            'enabled_at': self.enabled_at.isoformat() if self.enabled_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'has_backup_codes': bool(self.backup_codes)
        }


class TwoFactorSession(db.Model):
    """Track 2FA verification sessions."""
    __tablename__ = 'two_factor_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_token = Column(String(64), unique=True, nullable=False)
    
    # Track verification status
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Expiration
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='two_factor_sessions')
    
    @staticmethod
    def create_session(user_id, duration_minutes=5):
        """Create a new 2FA session."""
        import secrets
        from datetime import timedelta
        
        session = TwoFactorSession(
            user_id=user_id,
            session_token=secrets.token_urlsafe(48),
            expires_at=datetime.utcnow() + timedelta(minutes=duration_minutes)
        )
        db.session.add(session)
        db.session.commit()
        
        return session
    
    def is_expired(self):
        """Check if the session has expired."""
        return datetime.utcnow() > self.expires_at
    
    def verify(self):
        """Mark the session as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        db.session.commit()