"""Authentication service module."""

from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from werkzeug.security import generate_password_hash

from app.models import User, TokenBlocklist
from app.extensions import db, jwt


class AuthService:
    """Authentication service."""
    
    @staticmethod
    def login(email, password, remember=False):
        """
        Authenticate a user.
        
        Args:
            email (str): User's email
            password (str): User's password
            remember (bool): Whether to remember the user
        
        Returns:
            dict: Authentication tokens or None if authentication fails
        """
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.verify_password(password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login time
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': 3600  # 1 hour in seconds
        }
    
    @staticmethod
    def register(email, password, first_name, last_name, role='student', tenant_id=None):
        """
        Register a new user.
        
        Args:
            email (str): User's email
            password (str): User's password
            first_name (str): User's first name
            last_name (str): User's last name
            role (str): User's role
            tenant_id (int): User's tenant ID
        
        Returns:
            User: The created user or None if registration fails
        """
        from app.services.email_service import send_welcome_email
        
        user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        db.session.add(user)
        
        if tenant_id:
            from app.models import Tenant
            tenant = Tenant.query.get(tenant_id)
            if tenant:
                user.tenants.append(tenant)
        
        try:
            db.session.commit()
            
            # Send welcome email (non-blocking)
            send_welcome_email(user)
            
            return user
        except Exception as e:
            db.session.rollback()
            return None
    
    @staticmethod
    def refresh_token(refresh_token):
        """
        Refresh an access token.
        
        Args:
            refresh_token (str): Refresh token
        
        Returns:
            dict: New access token or None if refresh fails
        """
        try:
            identity = jwt.get_jwt_identity()
            access_token = create_access_token(identity=identity)
            
            return {
                'access_token': access_token,
                'token_type': 'bearer',
                'expires_in': 3600  # 1 hour in seconds
            }
        except:
            return None
    
    @staticmethod
    def logout(token):
        """
        Revoke a token.
        
        Args:
            token (dict): JWT token
        
        Returns:
            bool: True if successful, False otherwise
        """
        jti = token['jti']
        token_type = token['type']
        user_id = token['sub']
        expires = datetime.fromtimestamp(token['exp'], timezone.utc)
        
        token_entry = TokenBlocklist(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires
        )
        
        try:
            db.session.add(token_entry)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
    
    @staticmethod
    def request_password_reset(email):
        """
        Request a password reset.
        
        Args:
            email (str): User's email
        
        Returns:
            bool: True if successful, False otherwise
        """
        from app.services.email_service import send_password_reset_email
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return False
        
        # Send password reset email
        return send_password_reset_email(user)
    
    @staticmethod
    def reset_password(token, password):
        """
        Reset a user's password.
        
        Args:
            token (str): Password reset token
            password (str): New password
        
        Returns:
            bool: True if successful, False otherwise
        """
        from app.services.email_service import verify_email_token
        
        # Verify token
        data = verify_email_token(token, salt='password-reset-salt', expires_in=3600)
        
        if not data or 'user_id' not in data:
            return False
        
        # Get user
        user = User.query.get(data['user_id'])
        
        if not user:
            return False
        
        # Update password
        user.password = password
        
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change a user's password.
        
        Args:
            user_id (int): User ID
            current_password (str): Current password
            new_password (str): New password
        
        Returns:
            bool: True if successful, False otherwise
        """
        user = User.query.get(user_id)
        
        if not user or not user.verify_password(current_password):
            return False
        
        user.password = new_password
        
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False