"""Sensitive data encryption utilities."""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Union
from flask import current_app
import json


class DataEncryption:
    """Handles encryption and decryption of sensitive data."""
    
    def __init__(self, key: Optional[bytes] = None):
        """Initialize encryption with key."""
        if key:
            self.cipher = Fernet(key)
        else:
            self.cipher = self._get_cipher_from_config()
    
    def _get_cipher_from_config(self) -> Fernet:
        """Get cipher from application configuration."""
        # Get key from environment or config
        encryption_key = current_app.config.get('ENCRYPTION_KEY')
        
        if not encryption_key:
            # Generate key from SECRET_KEY
            secret_key = current_app.config.get('SECRET_KEY', '').encode()
            if not secret_key:
                raise ValueError("No encryption key or secret key configured")
            
            # Derive encryption key from secret key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'bdc-encryption-salt',  # Should be random in production
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret_key))
            return Fernet(key)
        
        return Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def encrypt(self, data: Union[str, dict, list]) -> str:
        """
        Encrypt data and return base64 encoded string.
        
        Args:
            data: Data to encrypt (string, dict, or list)
            
        Returns:
            Base64 encoded encrypted string
        """
        # Convert data to bytes
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data).encode()
        elif isinstance(data, str):
            data_bytes = data.encode()
        else:
            data_bytes = str(data).encode()
        
        # Encrypt
        encrypted = self.cipher.encrypt(data_bytes)
        
        # Return base64 encoded string
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str, return_type: type = str) -> Union[str, dict, list]:
        """
        Decrypt base64 encoded data.
        
        Args:
            encrypted_data: Base64 encoded encrypted string
            return_type: Expected return type (str, dict, or list)
            
        Returns:
            Decrypted data in specified type
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            
            # Convert to requested type
            if return_type in (dict, list):
                return json.loads(decrypted_bytes.decode())
            else:
                return decrypted_bytes.decode()
                
        except Exception as e:
            current_app.logger.error(f"Decryption failed: {str(e)}")
            raise ValueError("Failed to decrypt data")
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    def encrypt_field(self, value: Optional[str]) -> Optional[str]:
        """Encrypt a single field value."""
        if value is None:
            return None
        return self.encrypt(value)
    
    def decrypt_field(self, value: Optional[str]) -> Optional[str]:
        """Decrypt a single field value."""
        if value is None:
            return None
        return self.decrypt(value, str)


class SensitiveDataMixin:
    """Mixin for models with sensitive data fields."""
    
    # Override in subclass
    ENCRYPTED_FIELDS = []
    
    def __init__(self, *args, **kwargs):
        """Initialize with encryption support."""
        super().__init__(*args, **kwargs)
        self._encryptor = None
    
    @property
    def encryptor(self):
        """Get encryptor instance."""
        if not self._encryptor:
            self._encryptor = DataEncryption()
        return self._encryptor
    
    def encrypt_sensitive_fields(self):
        """Encrypt all sensitive fields before saving."""
        for field in self.ENCRYPTED_FIELDS:
            if hasattr(self, field):
                value = getattr(self, field)
                if value and not self._is_encrypted(value):
                    setattr(self, field, self.encryptor.encrypt_field(value))
    
    def decrypt_sensitive_fields(self):
        """Decrypt all sensitive fields after loading."""
        for field in self.ENCRYPTED_FIELDS:
            if hasattr(self, field):
                value = getattr(self, field)
                if value and self._is_encrypted(value):
                    try:
                        setattr(self, field, self.encryptor.decrypt_field(value))
                    except:
                        # Log error but don't fail
                        current_app.logger.error(f"Failed to decrypt field: {field}")
    
    def _is_encrypted(self, value: str) -> bool:
        """Check if value appears to be encrypted."""
        if not value:
            return False
        
        # Check if it looks like base64 encoded Fernet token
        try:
            decoded = base64.b64decode(value)
            # Fernet tokens start with specific version byte
            return len(decoded) > 0 and decoded[0:1] == b'\x80'
        except:
            return False
    
    def get_decrypted(self, field: str) -> Optional[str]:
        """Get decrypted value of a field."""
        if field not in self.ENCRYPTED_FIELDS:
            return getattr(self, field, None)
        
        value = getattr(self, field, None)
        if not value:
            return None
        
        if self._is_encrypted(value):
            return self.encryptor.decrypt_field(value)
        return value
    
    def set_encrypted(self, field: str, value: Optional[str]):
        """Set and encrypt a field value."""
        if field not in self.ENCRYPTED_FIELDS:
            setattr(self, field, value)
            return
        
        if value:
            setattr(self, field, self.encryptor.encrypt_field(value))
        else:
            setattr(self, field, None)


# Utility functions
def encrypt_password_reset_token(user_id: int, email: str) -> str:
    """Create encrypted password reset token."""
    encryptor = DataEncryption()
    token_data = {
        'user_id': user_id,
        'email': email,
        'timestamp': int(os.time.time())
    }
    return encryptor.encrypt(token_data)


def decrypt_password_reset_token(token: str, max_age: int = 3600) -> Optional[dict]:
    """Decrypt and validate password reset token."""
    try:
        encryptor = DataEncryption()
        data = encryptor.decrypt(token, dict)
        
        # Check age
        if int(os.time.time()) - data['timestamp'] > max_age:
            return None
        
        return data
    except:
        return None


def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for storage."""
    encryptor = DataEncryption()
    return encryptor.encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> Optional[str]:
    """Decrypt stored API key."""
    try:
        encryptor = DataEncryption()
        return encryptor.decrypt(encrypted_key, str)
    except:
        return None


# Example usage in models
"""
from app.utils.data_encryption import SensitiveDataMixin

class User(db.Model, SensitiveDataMixin):
    ENCRYPTED_FIELDS = ['ssn', 'tax_id', 'bank_account']
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    ssn = db.Column(db.Text)  # Will be encrypted
    tax_id = db.Column(db.Text)  # Will be encrypted
    bank_account = db.Column(db.Text)  # Will be encrypted
    
    def save(self):
        self.encrypt_sensitive_fields()
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        user = cls.query.get(id)
        if user:
            user.decrypt_sensitive_fields()
        return user
"""