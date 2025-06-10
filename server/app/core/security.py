"""Security utilities for password hashing and token generation."""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app


class SecurityManager:
    """Manages security operations like password hashing and token generation."""
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = 'HS256'):
        """Initialize security manager."""
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def hash_password(self, password: str) -> str:
        """Hash password using werkzeug security."""
        return generate_password_hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(password_hash, password)
    
    def generate_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Generate JWT token."""
        payload = payload.copy()
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload['iat'] = datetime.utcnow()
        
        secret_key = self.secret_key or current_app.config.get('SECRET_KEY')
        if not secret_key:
            raise ValueError("SECRET_KEY must be set in environment variables")
        return jwt.encode(payload, secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify JWT token."""
        try:
            secret_key = self.secret_key or current_app.config.get('SECRET_KEY')
            if not secret_key:
                raise ValueError("SECRET_KEY must be set in environment variables")
            payload = jwt.decode(token, secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def generate_random_token(self, length: int = 32) -> str:
        """Generate random token for password reset, etc."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_access_token(self, user_id: int, **kwargs) -> str:
        """Generate access token for user."""
        payload = {
            'user_id': user_id,
            'type': 'access',
            **kwargs
        }
        return self.generate_token(payload, expires_in=3600)  # 1 hour
    
    def generate_refresh_token(self, user_id: int, **kwargs) -> str:
        """Generate refresh token for user."""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            **kwargs
        }
        return self.generate_token(payload, expires_in=86400 * 30)  # 30 days
    
    def verify_token_type(self, token: str, expected_type: str) -> Optional[Dict[str, Any]]:
        """Verify token and check if it's of expected type."""
        payload = self.decode_token(token)
        if payload and payload.get('type') == expected_type:
            return payload
        return None