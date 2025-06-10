"""Two-Factor Authentication service."""

import logging
from typing import Optional, Tuple, List, Dict
from datetime import datetime, timedelta
from flask import current_app, url_for
from app.models.user import User
from app.models.two_factor_auth import TwoFactorAuth, TwoFactorSession
from app.services.email_service import EmailService
from app.extensions import db
import pyotp
import secrets

logger = logging.getLogger(__name__)


class TwoFactorService:
    """Service for handling two-factor authentication."""
    
    @staticmethod
    def setup_2fa(user: User) -> Tuple[bool, Dict]:
        """Initialize 2FA setup for a user."""
        try:
            # Check if 2FA already exists
            two_fa = TwoFactorAuth.query.filter_by(user_id=user.id).first()
            
            if two_fa and two_fa.is_enabled:
                return False, {"error": "2FA is already enabled for this user"}
            
            # Create or update 2FA settings
            if not two_fa:
                two_fa = TwoFactorAuth(user_id=user.id)
                db.session.add(two_fa)
            
            # Generate new secret
            two_fa.generate_secret()
            
            # Generate QR code
            qr_code = two_fa.generate_qr_code(
                app_name=current_app.config.get('APP_NAME', 'BDC Platform')
            )
            
            # Generate backup codes
            backup_codes = two_fa.generate_backup_codes()
            
            db.session.commit()
            
            return True, {
                "secret": two_fa.secret,
                "qr_code": f"data:image/png;base64,{qr_code}",
                "backup_codes": backup_codes,
                "manual_entry_key": two_fa.secret
            }
            
        except Exception as e:
            logger.error(f"Error setting up 2FA: {str(e)}")
            db.session.rollback()
            return False, {"error": f"Failed to setup 2FA: {str(e)}"}
    
    @staticmethod
    def verify_2fa_setup(user: User, token: str) -> Tuple[bool, str]:
        """Verify 2FA setup with initial token."""
        try:
            two_fa = TwoFactorAuth.query.filter_by(user_id=user.id).first()
            
            if not two_fa:
                return False, "2FA not initialized"
            
            if two_fa.is_enabled:
                return False, "2FA is already enabled"
            
            # Verify the token
            if two_fa.verify_token(token):
                two_fa.is_enabled = True
                two_fa.is_verified = True
                two_fa.enabled_at = datetime.utcnow()
                db.session.commit()
                
                # Send confirmation email
                TwoFactorService._send_2fa_enabled_email(user)
                
                return True, "2FA enabled successfully"
            else:
                return False, "Invalid verification code"
                
        except Exception as e:
            logger.error(f"Error verifying 2FA setup: {str(e)}")
            db.session.rollback()
            return False, f"Error verifying 2FA: {str(e)}"
    
    @staticmethod
    def verify_2fa_login(user: User, token: str) -> Tuple[bool, Optional[str]]:
        """Verify 2FA token during login."""
        try:
            two_fa = TwoFactorAuth.query.filter_by(
                user_id=user.id,
                is_enabled=True
            ).first()
            
            if not two_fa:
                return False, "2FA not enabled for this user"
            
            # Try TOTP token first
            if two_fa.verify_token(token):
                return True, None
            
            # Try backup code if TOTP fails
            if two_fa.verify_backup_code(token):
                # Check remaining backup codes
                remaining = len(two_fa.backup_codes.split(',')) if two_fa.backup_codes else 0
                if remaining < 3:
                    TwoFactorService._send_low_backup_codes_warning(user, remaining)
                return True, None
            
            return False, "Invalid 2FA code"
            
        except Exception as e:
            logger.error(f"Error verifying 2FA login: {str(e)}")
            return False, f"Error verifying 2FA: {str(e)}"
    
    @staticmethod
    def disable_2fa(user: User, password: str) -> Tuple[bool, str]:
        """Disable 2FA for a user."""
        try:
            # Verify password
            if not user.check_password(password):
                return False, "Invalid password"
            
            two_fa = TwoFactorAuth.query.filter_by(user_id=user.id).first()
            
            if not two_fa or not two_fa.is_enabled:
                return False, "2FA is not enabled"
            
            # Disable 2FA
            two_fa.disable()
            
            # Send confirmation email
            TwoFactorService._send_2fa_disabled_email(user)
            
            return True, "2FA disabled successfully"
            
        except Exception as e:
            logger.error(f"Error disabling 2FA: {str(e)}")
            db.session.rollback()
            return False, f"Error disabling 2FA: {str(e)}"
    
    @staticmethod
    def regenerate_backup_codes(user: User) -> Tuple[bool, Optional[List[str]]]:
        """Regenerate backup codes for a user."""
        try:
            two_fa = TwoFactorAuth.query.filter_by(
                user_id=user.id,
                is_enabled=True
            ).first()
            
            if not two_fa:
                return False, None
            
            # Generate new backup codes
            backup_codes = two_fa.generate_backup_codes()
            db.session.commit()
            
            # Send email notification
            TwoFactorService._send_backup_codes_regenerated_email(user)
            
            return True, backup_codes
            
        except Exception as e:
            logger.error(f"Error regenerating backup codes: {str(e)}")
            db.session.rollback()
            return False, None
    
    @staticmethod
    def create_2fa_session(user: User) -> Optional[str]:
        """Create a 2FA session for step-up authentication."""
        try:
            # Clean up expired sessions
            TwoFactorSession.query.filter(
                TwoFactorSession.expires_at < datetime.utcnow()
            ).delete()
            
            # Create new session
            session = TwoFactorSession.create_session(user.id)
            
            return session.session_token
            
        except Exception as e:
            logger.error(f"Error creating 2FA session: {str(e)}")
            return None
    
    @staticmethod
    def verify_2fa_session(session_token: str, otp_code: str) -> Tuple[bool, Optional[User]]:
        """Verify a 2FA session."""
        try:
            # Find session
            session = TwoFactorSession.query.filter_by(
                session_token=session_token
            ).first()
            
            if not session:
                return False, None
            
            if session.is_expired():
                db.session.delete(session)
                db.session.commit()
                return False, None
            
            if session.is_verified:
                return True, session.user
            
            # Verify OTP
            two_fa = TwoFactorAuth.query.filter_by(
                user_id=session.user_id,
                is_enabled=True
            ).first()
            
            if not two_fa:
                return False, None
            
            # Verify token
            if two_fa.verify_token(otp_code) or two_fa.verify_backup_code(otp_code):
                session.verify()
                return True, session.user
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error verifying 2FA session: {str(e)}")
            return False, None
    
    @staticmethod
    def get_2fa_status(user: User) -> Dict:
        """Get 2FA status for a user."""
        try:
            two_fa = TwoFactorAuth.query.filter_by(user_id=user.id).first()
            
            if not two_fa:
                return {
                    "enabled": False,
                    "configured": False
                }
            
            backup_code_count = 0
            if two_fa.backup_codes:
                backup_code_count = len(two_fa.backup_codes.split(','))
            
            return {
                "enabled": two_fa.is_enabled,
                "configured": True,
                "verified": two_fa.is_verified,
                "backup_codes_remaining": backup_code_count,
                "last_used": two_fa.last_used_at.isoformat() if two_fa.last_used_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting 2FA status: {str(e)}")
            return {
                "enabled": False,
                "configured": False,
                "error": str(e)
            }
    
    @staticmethod
    def _send_2fa_enabled_email(user: User):
        """Send email notification when 2FA is enabled."""
        try:
            subject = "Two-Factor Authentication Enabled - BDC Platform"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">Two-Factor Authentication Enabled</h2>
                        
                        <p>Hi {user.first_name},</p>
                        
                        <p>Two-factor authentication has been successfully enabled for your account.</p>
                        
                        <p><strong>What this means:</strong></p>
                        <ul>
                            <li>You'll need your phone to log in</li>
                            <li>Your account is now more secure</li>
                            <li>Keep your backup codes safe</li>
                        </ul>
                        
                        <p style="color: #e74c3c;">
                            <strong>Important:</strong> If you didn't enable 2FA, please contact us immediately.
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            This is a security notification from BDC Platform.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            Two-Factor Authentication Enabled
            
            Hi {user.first_name},
            
            Two-factor authentication has been successfully enabled for your account.
            
            What this means:
            - You'll need your phone to log in
            - Your account is now more secure
            - Keep your backup codes safe
            
            Important: If you didn't enable 2FA, please contact us immediately.
            
            This is a security notification from BDC Platform.
            """
            
            email_service = EmailService()
            email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
        except Exception as e:
            logger.error(f"Error sending 2FA enabled email: {str(e)}")
    
    @staticmethod
    def _send_2fa_disabled_email(user: User):
        """Send email notification when 2FA is disabled."""
        try:
            subject = "Two-Factor Authentication Disabled - BDC Platform"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #e74c3c;">Two-Factor Authentication Disabled</h2>
                        
                        <p>Hi {user.first_name},</p>
                        
                        <p>Two-factor authentication has been disabled for your account.</p>
                        
                        <p style="color: #e74c3c;">
                            <strong>Warning:</strong> Your account is now less secure. 
                            We recommend re-enabling 2FA as soon as possible.
                        </p>
                        
                        <p>If you didn't disable 2FA, please:</p>
                        <ol>
                            <li>Change your password immediately</li>
                            <li>Re-enable 2FA</li>
                            <li>Contact our support team</li>
                        </ol>
                        
                        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            This is a security notification from BDC Platform.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            email_service = EmailService()
            email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_body=html_body,
                text_body="2FA has been disabled for your account. If this wasn't you, please contact support immediately."
            )
            
        except Exception as e:
            logger.error(f"Error sending 2FA disabled email: {str(e)}")
    
    @staticmethod
    def _send_low_backup_codes_warning(user: User, remaining: int):
        """Send warning when backup codes are running low."""
        try:
            subject = "Low Backup Codes Warning - BDC Platform"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #f39c12;">Low Backup Codes Warning</h2>
                        
                        <p>Hi {user.first_name},</p>
                        
                        <p>You have only <strong>{remaining}</strong> backup codes remaining.</p>
                        
                        <p>We recommend generating new backup codes to ensure you don't get locked out of your account.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{url_for('auth.two_factor_settings', _external=True)}" 
                               style="background-color: #3498db; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Generate New Backup Codes
                            </a>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            This is a security notification from BDC Platform.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            email_service = EmailService()
            email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_body=html_body,
                text_body=f"You have only {remaining} backup codes remaining. Please generate new ones."
            )
            
        except Exception as e:
            logger.error(f"Error sending low backup codes warning: {str(e)}")
    
    @staticmethod
    def _send_backup_codes_regenerated_email(user: User):
        """Send notification when backup codes are regenerated."""
        try:
            subject = "Backup Codes Regenerated - BDC Platform"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">Backup Codes Regenerated</h2>
                        
                        <p>Hi {user.first_name},</p>
                        
                        <p>Your two-factor authentication backup codes have been regenerated.</p>
                        
                        <p><strong>Important:</strong></p>
                        <ul>
                            <li>Your old backup codes are no longer valid</li>
                            <li>Store your new codes in a safe place</li>
                            <li>Each code can only be used once</li>
                        </ul>
                        
                        <p style="color: #e74c3c;">
                            If you didn't request new backup codes, please contact us immediately.
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            This is a security notification from BDC Platform.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            email_service = EmailService()
            email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_body=html_body,
                text_body="Your 2FA backup codes have been regenerated. If this wasn't you, contact support immediately."
            )
            
        except Exception as e:
            logger.error(f"Error sending backup codes regenerated email: {str(e)}")