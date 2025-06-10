"""Main file upload service orchestrating all security features."""

import os
import tempfile
import re
from typing import Optional, Dict, List, BinaryIO
from werkzeug.datastructures import FileStorage
from flask import current_app
import logging

from .config import FileUploadConfig
from .file_scanner import FileScanner
from .image_processor import ImageProcessor
from .storage_manager import StorageManager
from .audit_logger import FileAuditLogger
from .exceptions import (
    FileUploadException,
    FileSizeExceededException,
    FileTypeNotAllowedException
)

logger = logging.getLogger(__name__)


class FileUploadService:
    """Main service for secure file uploads."""
    
    def __init__(self, config: Optional[FileUploadConfig] = None):
        self.config = config or FileUploadConfig()
        self.scanner = FileScanner(self.config)
        self.image_processor = ImageProcessor(self.config)
        self.storage_manager = StorageManager(self.config)
        self.audit_logger = FileAuditLogger(self.config)
        
    def upload_file(self, file: FileStorage, user_id: str, tenant_id: str,
                   category: Optional[str] = None,
                   metadata: Optional[Dict] = None,
                   request_info: Optional[Dict] = None) -> Dict[str, any]:
        """
        Upload a file with comprehensive security checks.
        
        Args:
            file: Werkzeug FileStorage object
            user_id: ID of user uploading the file
            tenant_id: Tenant ID for multi-tenancy
            category: Optional file category override
            metadata: Optional metadata to store with file
            request_info: Request information (IP, user agent)
            
        Returns:
            Dictionary with upload results and file information
        """
        temp_path = None
        processed_path = None
        
        try:
            # Validate file object
            if not file or not file.filename:
                raise FileUploadException("No file provided")
            
            # Sanitize filename
            original_filename = self._sanitize_filename(file.filename)
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.config.MAX_FILE_SIZE:
                raise FileSizeExceededException(
                    f"File size {file_size} exceeds maximum {self.config.MAX_FILE_SIZE}"
                )
            
            # Save to temporary location
            temp_path = self._save_temp_file(file)
            
            # Scan file for security threats
            scan_results = self.scanner.scan_file(temp_path)
            
            # Process based on file category
            file_category = scan_results['file_category']
            if category and category in self.config.ALLOWED_FILE_TYPES:
                file_category = category
            
            # Process image files
            if file_category == 'image':
                processed_path = temp_path + '_processed'
                processing_results = self.image_processor.process_image(
                    temp_path, processed_path
                )
                scan_results.update(processing_results)
                upload_path = processed_path
            else:
                upload_path = temp_path
            
            # Store file securely
            storage_results = self.storage_manager.store_file(
                upload_path,
                file_category,
                user_id,
                metadata
            )
            
            # Combine all results
            file_info = {
                **scan_results,
                **storage_results,
                'original_filename': original_filename,
                'file_category': file_category,
                'user_id': user_id,
                'tenant_id': tenant_id
            }
            
            # Log upload in audit trail
            audit_entry = self.audit_logger.log_upload(
                user_id, tenant_id, file_info, request_info
            )
            
            # Add audit ID to results
            file_info['file_id'] = str(audit_entry.id)
            file_info['audit_id'] = audit_entry.id
            
            return {
                'success': True,
                'file_info': file_info,
                'message': 'File uploaded successfully'
            }
            
        except FileUploadException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {str(e)}")
            raise FileUploadException(f"Upload failed: {str(e)}")
        finally:
            # Cleanup temporary files
            for path in [temp_path, processed_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
    
    def download_file(self, file_id: str, user_id: str,
                     request_info: Optional[Dict] = None) -> Dict[str, any]:
        """
        Download a file with audit logging.
        
        Args:
            file_id: ID of file to download
            user_id: ID of user downloading the file
            request_info: Request information for audit
            
        Returns:
            Dictionary with file information and path
        """
        try:
            # Get file information from audit log
            file_history = self.audit_logger.get_file_history(file_id)
            if not file_history:
                raise FileUploadException("File not found")
            
            # Get storage path
            storage_path = file_history['file_info'].get('storage_path')
            if not storage_path:
                raise FileUploadException("File storage path not found")
            
            # Retrieve file
            file_path = self.storage_manager.retrieve_file(storage_path)
            
            # Log download
            self.audit_logger.log_download(file_id, user_id, request_info)
            
            return {
                'success': True,
                'file_path': file_path,
                'file_info': file_history['file_info']
            }
            
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            raise FileUploadException(f"Download failed: {str(e)}")
    
    def delete_file(self, file_id: str, user_id: str, reason: Optional[str] = None):
        """
        Delete a file with audit logging.
        
        Args:
            file_id: ID of file to delete
            user_id: ID of user deleting the file
            reason: Optional reason for deletion
        """
        try:
            # Get file information
            file_history = self.audit_logger.get_file_history(file_id)
            if not file_history:
                raise FileUploadException("File not found")
            
            # Get storage path
            storage_path = file_history['file_info'].get('storage_path')
            if storage_path:
                self.storage_manager.delete_file(storage_path)
            
            # Log deletion
            self.audit_logger.log_deletion(file_id, user_id, reason)
            
            return {
                'success': True,
                'message': 'File deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            raise FileUploadException(f"Deletion failed: {str(e)}")
    
    def update_file(self, file_id: str, file: FileStorage, user_id: str,
                   comment: Optional[str] = None) -> Dict[str, any]:
        """
        Update a file (create new version).
        
        Args:
            file_id: ID of file to update
            file: New file content
            user_id: ID of user updating the file
            comment: Optional version comment
            
        Returns:
            Dictionary with update results
        """
        try:
            # Upload new version
            upload_result = self.upload_file(
                file, user_id, 
                self._get_tenant_id_from_file(file_id)
            )
            
            # Add as new version
            new_version = self.audit_logger.add_version(
                file_id,
                upload_result['file_info'],
                user_id,
                comment
            )
            
            return {
                'success': True,
                'version': new_version.version_number,
                'file_info': upload_result['file_info']
            }
            
        except Exception as e:
            logger.error(f"Error updating file {file_id}: {str(e)}")
            raise FileUploadException(f"Update failed: {str(e)}")
    
    def get_file_history(self, file_id: str) -> Dict[str, any]:
        """Get complete history and versions of a file."""
        return self.audit_logger.get_file_history(file_id)
    
    def get_user_stats(self, user_id: str, tenant_id: str) -> Dict[str, any]:
        """Get upload statistics for a user."""
        return self.audit_logger.get_user_upload_stats(user_id, tenant_id)
    
    def create_signed_url(self, file_id: str, expiration: int = 3600) -> str:
        """
        Create a signed URL for temporary file access.
        
        Args:
            file_id: ID of file
            expiration: URL expiration in seconds
            
        Returns:
            Signed URL
        """
        # Get file information
        file_history = self.audit_logger.get_file_history(file_id)
        if not file_history:
            raise FileUploadException("File not found")
        
        # Get S3 key or local path
        file_key = file_history['file_info'].get('secure_filename')
        
        return self.storage_manager.create_signed_url(file_key, expiration)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security."""
        if not self.config.SANITIZE_FILENAMES:
            return filename
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove special characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Replace spaces
        filename = filename.replace(' ', '_')
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 100:
            name = name[:100]
        
        return name + ext
    
    def _save_temp_file(self, file: FileStorage) -> str:
        """Save uploaded file to temporary location."""
        fd, temp_path = tempfile.mkstemp(dir=self.config.TEMP_FOLDER)
        try:
            os.close(fd)
            file.save(temp_path)
            return temp_path
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise FileUploadException(f"Failed to save temporary file: {str(e)}")
    
    def _get_tenant_id_from_file(self, file_id: str) -> str:
        """Get tenant ID from file audit record."""
        from .audit_logger import FileUploadAudit
        audit = FileUploadAudit.query.filter_by(file_id=file_id).first()
        return audit.tenant_id if audit else 'default'
    
    def cleanup_temp_files(self):
        """Clean up old temporary files."""
        try:
            # Clean files older than 1 hour
            import time
            current_time = time.time()
            
            for filename in os.listdir(self.config.TEMP_FOLDER):
                file_path = os.path.join(self.config.TEMP_FOLDER, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > 3600:  # 1 hour
                        os.remove(file_path)
                        
        except Exception as e:
            logger.error(f"Error cleaning temp files: {str(e)}")
    
    def cleanup_old_audits(self):
        """Clean up old audit logs."""
        self.audit_logger.cleanup_old_audits()