"""
Encryption and cryptographic services for data protection.
"""

import os
import base64
import hashlib
import secrets
from typing import Optional, Tuple, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import bcrypt
import argon2

class EncryptionService:
    """Comprehensive encryption service for data protection."""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize encryption service with master key."""
        if master_key:
            self.fernet = Fernet(master_key.encode() if isinstance(master_key, str) else master_key)
        else:
            # Generate a new key if none provided
            self.fernet = Fernet(Fernet.generate_key())
        
        # Initialize Argon2 for password hashing
        self.argon2 = argon2.PasswordHasher(
            time_cost=2,      # Number of iterations
            memory_cost=65536,  # Memory usage in KB (64MB)
            parallelism=1,    # Number of parallel threads
            hash_len=32,      # Hash length
            salt_len=16       # Salt length
        )
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt data using Fernet symmetric encryption."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self.fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet symmetric encryption."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using Argon2."""
        try:
            return self.argon2.hash(password)
        except Exception as e:
            raise ValueError(f"Password hashing failed: {str(e)}")
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against Argon2 hash."""
        try:
            self.argon2.verify(hashed, password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def hash_password_bcrypt(password: str, rounds: int = 12) -> str:
        """Hash password using bcrypt (alternative/legacy method)."""
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password_bcrypt(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure random token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        """Generate cryptographically secure salt."""
        return os.urandom(length)
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Encrypt a file."""
        if output_path is None:
            output_path = file_path + '.encrypted'
        
        try:
            with open(file_path, 'rb') as infile:
                data = infile.read()
            
            encrypted_data = self.fernet.encrypt(data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(encrypted_data)
            
            return output_path
        except Exception as e:
            raise ValueError(f"File encryption failed: {str(e)}")
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """Decrypt a file."""
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        try:
            with open(encrypted_file_path, 'rb') as infile:
                encrypted_data = infile.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(decrypted_data)
            
            return output_path
        except Exception as e:
            raise ValueError(f"File decryption failed: {str(e)}")
    
    @staticmethod
    def hash_data(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """Hash data using specified algorithm."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data).hexdigest()
        elif algorithm == 'blake2b':
            return hashlib.blake2b(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    def encrypt_sensitive_field(self, value: str, field_name: str = "") -> str:
        """Encrypt sensitive database field with additional context."""
        # Add field name as additional authenticated data if needed
        return self.encrypt_data(value)
    
    def decrypt_sensitive_field(self, encrypted_value: str, field_name: str = "") -> str:
        """Decrypt sensitive database field with additional context."""
        return self.decrypt_data(encrypted_value)
    
    @staticmethod
    def generate_rsa_keypair(key_size: int = 2048) -> Tuple[bytes, bytes]:
        """Generate RSA key pair for asymmetric encryption."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def encrypt_with_rsa_public_key(data: bytes, public_key_pem: bytes) -> bytes:
        """Encrypt data with RSA public key."""
        public_key = serialization.load_pem_public_key(public_key_pem)
        
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted
    
    @staticmethod
    def decrypt_with_rsa_private_key(encrypted_data: bytes, private_key_pem: bytes) -> bytes:
        """Decrypt data with RSA private key."""
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        
        decrypted = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted
    
    @staticmethod
    def constant_time_compare(val1: str, val2: str) -> bool:
        """Constant-time string comparison to prevent timing attacks."""
        return secrets.compare_digest(val1, val2)
    
    def rotate_encryption_key(self, old_key: str, new_key: str, encrypted_data: str) -> str:
        """Rotate encryption key for existing encrypted data."""
        # Decrypt with old key
        old_fernet = Fernet(old_key.encode() if isinstance(old_key, str) else old_key)
        decrypted_data = old_fernet.decrypt(
            base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        )
        
        # Encrypt with new key
        new_fernet = Fernet(new_key.encode() if isinstance(new_key, str) else new_key)
        new_encrypted = new_fernet.encrypt(decrypted_data)
        
        return base64.urlsafe_b64encode(new_encrypted).decode('utf-8')