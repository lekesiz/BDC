"""Email verification service."""

import logging
from flask import current_app, url_for
from app.models.user import User
from app.models.email_verification import EmailVerificationToken
from app.services.email_service import EmailService
from app.extensions import db
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Service for handling email verification."""
    
    @staticmethod
    def send_verification_email(user):
        """Send verification email to user."""
        try:
            # Check if user already verified
            if user.email_verified:
                logger.info(f"User {user.email} already verified")
                return True, "Email already verified"
            
            # Create verification token
            token = EmailVerificationToken.create_for_user(user)
            
            # Generate verification URL
            verification_url = url_for(
                'auth.verify_email',
                token=token.token,
                _external=True
            )
            
            # Prepare email content
            subject = "Verify Your Email - BDC Platform"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">Welcome to BDC Platform!</h2>
                        
                        <p>Hi {user.first_name},</p>
                        
                        <p>Thank you for registering with BDC Platform. To complete your registration and access all features, please verify your email address.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}" 
                               style="background-color: #3498db; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Verify Email Address
                            </a>
                        </div>
                        
                        <p>Or copy and paste this link in your browser:</p>
                        <p style="word-break: break-all; color: #3498db;">
                            {verification_url}
                        </p>
                        
                        <p style="color: #7f8c8d; font-size: 14px;">
                            This link will expire in 24 hours. If you didn't create an account, 
                            you can safely ignore this email.
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                        
                        <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                            © 2024 BDC Platform. All rights reserved.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
            Welcome to BDC Platform!
            
            Hi {user.first_name},
            
            Thank you for registering with BDC Platform. To complete your registration 
            and access all features, please verify your email address by clicking the 
            link below:
            
            {verification_url}
            
            This link will expire in 24 hours. If you didn't create an account, 
            you can safely ignore this email.
            
            Best regards,
            BDC Platform Team
            """
            
            # Send email
            email_service = EmailService()
            success = email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            if success:
                logger.info(f"Verification email sent to {user.email}")
                return True, "Verification email sent successfully"
            else:
                logger.error(f"Failed to send verification email to {user.email}")
                return False, "Failed to send verification email"
                
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False, f"Error sending verification email: {str(e)}"
    
    @staticmethod
    def verify_email(token_string):
        """Verify email using token."""
        try:
            # Verify token and get user
            user, error = EmailVerificationToken.verify_token(token_string)
            
            if error:
                return False, error
            
            # Mark user as verified
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Email verified for user {user.email}")
            return True, "Email verified successfully"
            
        except Exception as e:
            logger.error(f"Error verifying email: {str(e)}")
            db.session.rollback()
            return False, f"Error verifying email: {str(e)}"
    
    @staticmethod
    def resend_verification_email(user):
        """Resend verification email."""
        try:
            # Check if already verified
            if user.email_verified:
                return False, "Email already verified"
            
            # Check for recent tokens
            recent_token = EmailVerificationToken.query.filter_by(
                user_id=user.id,
                is_used=False
            ).filter(
                EmailVerificationToken.expires_at > datetime.utcnow()
            ).first()
            
            if recent_token:
                # Calculate time until next resend allowed (5 minutes between resends)
                time_since_created = datetime.utcnow() - recent_token.created_at
                if time_since_created.total_seconds() < 300:  # 5 minutes
                    wait_time = 300 - int(time_since_created.total_seconds())
                    return False, f"Please wait {wait_time} seconds before requesting another email"
            
            # Send new verification email
            return EmailVerificationService.send_verification_email(user)
            
        except Exception as e:
            logger.error(f"Error resending verification email: {str(e)}")
            return False, f"Error resending verification email: {str(e)}"
    
    @staticmethod
    def check_verification_required(user):
        """Check if email verification is required for user."""
        # Skip verification for certain roles or environments
        if current_app.config.get('SKIP_EMAIL_VERIFICATION', False):
            return False
        
        # Super admins might not need verification
        if user.role == 'super_admin':
            return False
        
        return not user.email_verified
    
    @staticmethod
    def cleanup_expired_tokens():
        """Clean up expired verification tokens."""
        try:
            expired_tokens = EmailVerificationToken.query.filter(
                EmailVerificationToken.expires_at < datetime.utcnow()
            ).all()
            
            count = len(expired_tokens)
            for token in expired_tokens:
                db.session.delete(token)
            
            db.session.commit()
            logger.info(f"Cleaned up {count} expired verification tokens")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")
            db.session.rollback()
            return 0