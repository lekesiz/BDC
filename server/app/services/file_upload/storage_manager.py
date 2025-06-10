"""Secure storage manager with encryption and S3/CDN support."""

import os
import uuid
import shutil
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import boto3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

from .config import FileUploadConfig
from .exceptions import StorageException, EncryptionException

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages secure file storage with encryption and cloud integration."""
    
    def __init__(self, config: FileUploadConfig):
        self.config = config
        self._init_encryption()
        self._init_s3_client()
        
    def _init_encryption(self):
        """Initialize encryption system."""
        if self.config.ENABLE_ENCRYPTION:
            if not self.config.ENCRYPTION_KEY:
                raise EncryptionException("Encryption enabled but no key provided")
            
            # Derive encryption key from the provided key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'stable_salt',  # In production, use a proper salt
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(self.config.ENCRYPTION_KEY.encode())
            )
            self.cipher_suite = Fernet(key)
        else:
            self.cipher_suite = None
    
    def _init_s3_client(self):
        """Initialize S3 client if configured."""
        if self.config.S3_BUCKET:
            try:
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.config.S3_REGION,
                    aws_access_key_id=self.config.S3_ACCESS_KEY,
                    aws_secret_access_key=self.config.S3_SECRET_KEY
                )
            except Exception as e:
                logger.warning(f"Failed to initialize S3 client: {str(e)}")
                self.s3_client = None
        else:
            self.s3_client = None
    
    def store_file(self, file_path: str, file_category: str, 
                   user_id: str, metadata: Optional[Dict] = None) -> Dict[str, any]:
        """
        Store file securely with optional encryption and cloud upload.
        
        Args:
            file_path: Path to file to store
            file_category: Category of file (image, document, etc.)
            user_id: ID of user uploading the file
            metadata: Optional metadata to store with file
            
        Returns:
            Dictionary with storage information
        """
        try:
            # Generate secure filename
            secure_filename = self._generate_secure_filename(file_path)
            
            # Create storage path
            storage_path = self._create_storage_path(
                file_category, user_id, secure_filename
            )
            
            # Encrypt file if enabled
            if self.config.ENABLE_ENCRYPTION:
                encrypted_path = self._encrypt_file(file_path)
                shutil.move(encrypted_path, storage_path)
            else:
                shutil.copy2(file_path, storage_path)
            
            # Upload to S3 if configured
            s3_url = None
            if self.s3_client and self.config.S3_BUCKET:
                s3_url = self._upload_to_s3(storage_path, file_category, user_id)
            
            # Generate CDN URL if available
            cdn_url = None
            if s3_url and self.config.CDN_URL:
                cdn_url = self._generate_cdn_url(s3_url)
            
            return {
                'local_path': storage_path,
                'secure_filename': secure_filename,
                'original_filename': os.path.basename(file_path),
                's3_url': s3_url,
                'cdn_url': cdn_url,
                'encrypted': self.config.ENABLE_ENCRYPTION,
                'storage_date': datetime.utcnow().isoformat(),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error storing file: {str(e)}")
            raise StorageException(f"Failed to store file: {str(e)}")
    
    def retrieve_file(self, storage_path: str, decrypt: bool = True) -> str:
        """
        Retrieve file from storage with optional decryption.
        
        Args:
            storage_path: Path to stored file
            decrypt: Whether to decrypt the file
            
        Returns:
            Path to retrieved file
        """
        try:
            if not os.path.exists(storage_path):
                # Try to download from S3
                if self.s3_client:
                    temp_path = self._download_from_s3(storage_path)
                    if temp_path:
                        storage_path = temp_path
                    else:
                        raise StorageException("File not found in local or cloud storage")
                else:
                    raise StorageException("File not found in local storage")
            
            # Decrypt if needed
            if decrypt and self.config.ENABLE_ENCRYPTION:
                return self._decrypt_file(storage_path)
            
            return storage_path
            
        except Exception as e:
            logger.error(f"Error retrieving file: {str(e)}")
            raise StorageException(f"Failed to retrieve file: {str(e)}")
    
    def delete_file(self, storage_path: str, delete_from_s3: bool = True):
        """Delete file from storage."""
        try:
            # Delete from local storage
            if os.path.exists(storage_path):
                os.remove(storage_path)
            
            # Delete from S3 if configured
            if delete_from_s3 and self.s3_client and self.config.S3_BUCKET:
                self._delete_from_s3(storage_path)
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise StorageException(f"Failed to delete file: {str(e)}")
    
    def _generate_secure_filename(self, original_path: str) -> str:
        """Generate a secure filename."""
        ext = Path(original_path).suffix.lower()
        return f"{uuid.uuid4().hex}{ext}"
    
    def _create_storage_path(self, category: str, user_id: str, filename: str) -> str:
        """Create storage path with proper directory structure."""
        # Create directory structure: category/user_id/year/month/filename
        now = datetime.utcnow()
        path_components = [
            self.config.UPLOAD_FOLDER,
            category,
            user_id,
            str(now.year),
            str(now.month).zfill(2),
            filename
        ]
        
        storage_path = os.path.join(*path_components)
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        return storage_path
    
    def _encrypt_file(self, file_path: str) -> str:
        """Encrypt a file and return path to encrypted file."""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.cipher_suite.encrypt(file_data)
            
            encrypted_path = f"{file_path}.enc"
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            return encrypted_path
            
        except Exception as e:
            raise EncryptionException(f"Failed to encrypt file: {str(e)}")
    
    def _decrypt_file(self, encrypted_path: str) -> str:
        """Decrypt a file and return path to decrypted file."""
        try:
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            decrypted_path = encrypted_path.replace('.enc', '')
            with open(decrypted_path, 'wb') as f:
                f.write(decrypted_data)
            
            return decrypted_path
            
        except Exception as e:
            raise EncryptionException(f"Failed to decrypt file: {str(e)}")
    
    def _upload_to_s3(self, file_path: str, category: str, user_id: str) -> Optional[str]:
        """Upload file to S3."""
        try:
            # Generate S3 key
            filename = os.path.basename(file_path)
            s3_key = f"{category}/{user_id}/{filename}"
            
            # Upload file
            self.s3_client.upload_file(
                file_path,
                self.config.S3_BUCKET,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'ContentDisposition': f'inline; filename="{filename}"'
                }
            )
            
            # Generate URL
            s3_url = f"https://{self.config.S3_BUCKET}.s3.{self.config.S3_REGION}.amazonaws.com/{s3_key}"
            
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            return None
    
    def _download_from_s3(self, s3_key: str) -> Optional[str]:
        """Download file from S3."""
        try:
            temp_path = os.path.join(self.config.TEMP_FOLDER, os.path.basename(s3_key))
            
            self.s3_client.download_file(
                self.config.S3_BUCKET,
                s3_key,
                temp_path
            )
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to download from S3: {str(e)}")
            return None
    
    def _delete_from_s3(self, file_path: str):
        """Delete file from S3."""
        try:
            # Extract S3 key from file path
            filename = os.path.basename(file_path)
            # You might need to adjust this based on your S3 structure
            s3_key = filename
            
            self.s3_client.delete_object(
                Bucket=self.config.S3_BUCKET,
                Key=s3_key
            )
            
        except Exception as e:
            logger.error(f"Failed to delete from S3: {str(e)}")
    
    def _generate_cdn_url(self, s3_url: str) -> str:
        """Generate CDN URL from S3 URL."""
        # Extract key from S3 URL
        s3_key = s3_url.split('.com/')[-1]
        return f"{self.config.CDN_URL}/{s3_key}"
    
    def create_signed_url(self, file_key: str, expiration: int = 3600) -> str:
        """
        Create a signed URL for temporary file access.
        
        Args:
            file_key: S3 key or file identifier
            expiration: URL expiration time in seconds
            
        Returns:
            Signed URL
        """
        try:
            if self.s3_client:
                return self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.config.S3_BUCKET,
                        'Key': file_key
                    },
                    ExpiresIn=expiration
                )
            else:
                # Generate local temporary URL
                # In production, implement proper temporary URL system
                return f"/api/files/temp/{file_key}?expires={expiration}"
                
        except Exception as e:
            logger.error(f"Failed to create signed URL: {str(e)}")
            raise StorageException(f"Failed to create signed URL: {str(e)}")