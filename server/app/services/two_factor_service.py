"""Two-Factor Authentication service."""

from datetime import datetime, timedelta
from flask import current_app
from app.models import User, TwoFactorAuth, TwoFactorSession
from app.extensions import db
from app.services.email_service import send_email


class TwoFactorService:
    """Service for managing two-factor authentication."""
    
    @staticmethod
    def setup_2fa(user_id):
        """Set up 2FA for a user."""
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        
        # Check if 2FA is already set up
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        if two_fa and two_fa.is_enabled:
            return None, "2FA is already enabled for this user"
        
        # Create or update 2FA settings
        if not two_fa:
            two_fa = TwoFactorAuth(user_id=user_id)
            db.session.add(two_fa)
        
        # Generate new secret
        two_fa.generate_secret()
        
        # Generate QR code
        qr_code = two_fa.generate_qr_code()
        
        # Generate backup codes
        backup_codes = two_fa.generate_backup_codes()
        
        db.session.commit()
        
        return {
            'secret': two_fa.secret,
            'qr_code': qr_code,
            'backup_codes': backup_codes,
            'setup_id': two_fa.id
        }, None
    
    @staticmethod
    def verify_setup(user_id, token):
        """Verify 2FA setup with initial token."""
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        if not two_fa:
            return False, "2FA not set up for this user"
        
        if two_fa.is_enabled:
            return False, "2FA is already enabled"
        
        # Verify the token
        if two_fa.verify_token(token):
            two_fa.is_enabled = True
            two_fa.is_verified = True
            two_fa.enabled_at = datetime.utcnow()
            db.session.commit()
            
            # Send confirmation email
            user = User.query.get(user_id)
            if user:
                send_email(
                    user.email,
                    "Two-Factor Authentication Enabled",
                    f"Two-factor authentication has been successfully enabled for your account."
                )
            
            return True, "2FA successfully enabled"
        
        return False, "Invalid token"
    
    @staticmethod
    def verify_token(user_id, token):
        """Verify a 2FA token for login."""
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        if not two_fa or not two_fa.is_enabled:
            return False, "2FA not enabled for this user"
        
        # Try TOTP token first
        if two_fa.verify_token(token):
            return True, "Valid token"
        
        # Try backup code if TOTP fails
        if two_fa.verify_backup_code(token):
            # Check if user is running low on backup codes
            remaining_codes = len(two_fa.backup_codes.split(',')) if two_fa.backup_codes else 0
            if remaining_codes <= 2:
                user = User.query.get(user_id)
                if user:
                    send_email(
                        user.email,
                        "Low on Backup Codes",
                        f"You have only {remaining_codes} backup codes remaining. "
                        "Please generate new codes from your security settings."
                    )
            
            return True, "Valid backup code"
        
        return False, "Invalid token or backup code"
    
    @staticmethod
    def disable_2fa(user_id):
        """Disable 2FA for a user."""
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        if not two_fa:
            return False, "2FA not set up for this user"
        
        two_fa.disable()
        
        # Send notification email
        user = User.query.get(user_id)
        if user:
            send_email(
                user.email,
                "Two-Factor Authentication Disabled",
                "Two-factor authentication has been disabled for your account. "
                "Your account security may be reduced."
            )
        
        return True, "2FA successfully disabled"
    
    @staticmethod
    def regenerate_backup_codes(user_id):
        """Regenerate backup codes for a user."""
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        if not two_fa or not two_fa.is_enabled:
            return None, "2FA not enabled for this user"
        
        # Generate new codes
        backup_codes = two_fa.generate_backup_codes()
        db.session.commit()
        
        return backup_codes, None
    
    @staticmethod
    def create_2fa_session(user_id):
        """Create a 2FA verification session."""
        # Clean up expired sessions
        TwoFactorSession.query.filter(
            TwoFactorSession.expires_at < datetime.utcnow()
        ).delete()
        
        # Create new session
        session = TwoFactorSession.create_session(user_id)
        
        return session.session_token
    
    @staticmethod
    def verify_2fa_session(session_token, verification_token):
        """Verify a 2FA session with token."""
        session = TwoFactorSession.query.filter_by(
            session_token=session_token
        ).first()
        
        if not session:
            return None, "Invalid session"
        
        if session.is_expired():
            return None, "Session expired"
        
        if session.is_verified:
            return None, "Session already verified"
        
        # Verify the token
        success, message = TwoFactorService.verify_token(
            session.user_id, 
            verification_token
        )
        
        if success:
            session.verify()
            return session.user_id, None
        
        return None, message
    
    @staticmethod
    def check_2fa_required(user_id):
        """Check if 2FA is required for a user."""
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        return two_fa and two_fa.is_enabled
    
    @staticmethod
    def get_2fa_status(user_id):
        """Get 2FA status for a user."""
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        if not two_fa:
            return {
                'enabled': False,
                'verified': False,
                'has_backup_codes': False
            }
        
        return {
            'enabled': two_fa.is_enabled,
            'verified': two_fa.is_verified,
            'has_backup_codes': bool(two_fa.backup_codes),
            'enabled_at': two_fa.enabled_at.isoformat() if two_fa.enabled_at else None,
            'last_used_at': two_fa.last_used_at.isoformat() if two_fa.last_used_at else None
        }
    
    @staticmethod
    def enforce_2fa_for_role(role):
        """Check if 2FA should be enforced for a specific role."""
        # Enforce 2FA for admin roles
        enforced_roles = ['super_admin', 'tenant_admin']
        return role in enforced_roles
    
    @staticmethod
    def send_2fa_setup_reminder(user_id):
        """Send reminder to set up 2FA."""
        user = User.query.get(user_id)
        if not user:
            return
        
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        if two_fa and two_fa.is_enabled:
            return  # Already enabled
        
        send_email(
            user.email,
            "Enable Two-Factor Authentication",
            f"Hi {user.first_name},\n\n"
            "For enhanced security, we recommend enabling two-factor authentication "
            "on your account. This adds an extra layer of protection.\n\n"
            "You can enable 2FA in your account security settings."
        )