"""Enhanced file upload security utilities."""

import os
import hashlib
import mimetypes
import magic
from pathlib import Path
from typing import Optional, Tuple, List
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

# Safe file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'zip', 'rar', '7z'
}

# MIME type mapping
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/csv',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/bmp',
    'application/zip',
    'application/x-rar-compressed',
    'application/x-7z-compressed'
}

# Maximum file sizes by type (in bytes)
MAX_FILE_SIZES = {
    'image': 10 * 1024 * 1024,  # 10MB
    'document': 50 * 1024 * 1024,  # 50MB
    'archive': 100 * 1024 * 1024,  # 100MB
    'default': 16 * 1024 * 1024  # 16MB
}


class FileUploadValidator:
    """Validates and secures file uploads."""
    
    def __init__(self, upload_folder: str = None):
        """Initialize the validator."""
        self.upload_folder = upload_folder or current_app.config.get('UPLOAD_FOLDER', 'uploads')
        self.magic = magic.Magic(mime=True)
    
    def validate_file(self, file) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file for security.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"
        
        # Check filename
        filename = file.filename
        if not filename:
            return False, "No filename provided"
        
        # Validate extension
        ext = self._get_file_extension(filename)
        if not ext or ext not in ALLOWED_EXTENSIONS:
            return False, f"File type '{ext}' not allowed"
        
        # Read file content for validation
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Check file size
        file_size = len(file_content)
        max_size = self._get_max_file_size(ext)
        if file_size > max_size:
            return False, f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
        
        # Validate MIME type using magic
        try:
            mime_type = self.magic.from_buffer(file_content)
            if mime_type not in ALLOWED_MIME_TYPES:
                return False, f"Invalid file content. Detected type: {mime_type}"
        except Exception as e:
            return False, f"Could not validate file type: {str(e)}"
        
        # Check for malicious content patterns
        if self._contains_malicious_patterns(file_content):
            return False, "File contains potentially malicious content"
        
        return True, None
    
    def _get_file_extension(self, filename: str) -> Optional[str]:
        """Get file extension safely."""
        if '.' not in filename:
            return None
        return filename.rsplit('.', 1)[1].lower()
    
    def _get_max_file_size(self, extension: str) -> int:
        """Get maximum file size for extension."""
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            return MAX_FILE_SIZES['image']
        elif extension in ['zip', 'rar', '7z']:
            return MAX_FILE_SIZES['archive']
        elif extension in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
            return MAX_FILE_SIZES['document']
        return MAX_FILE_SIZES['default']
    
    def _contains_malicious_patterns(self, content: bytes) -> bool:
        """Check for common malicious patterns."""
        # Check for executable headers
        malicious_headers = [
            b'MZ',  # Windows executable
            b'\x7fELF',  # Linux executable
            b'#!/',  # Shell script
            b'<?php',  # PHP script
            b'<script',  # JavaScript
            b'<%',  # ASP/JSP
        ]
        
        for header in malicious_headers:
            if content[:len(header)] == header:
                return True
        
        # Check for embedded scripts in first 1KB
        sample = content[:1024].lower()
        dangerous_patterns = [
            b'<script',
            b'javascript:',
            b'onerror=',
            b'onclick=',
            b'<iframe',
            b'eval(',
            b'expression(',
        ]
        
        for pattern in dangerous_patterns:
            if pattern in sample:
                return True
        
        return False
    
    def save_file_securely(self, file, subfolder: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Save file securely with validation.
        
        Returns:
            Tuple of (success, saved_path, error_message)
        """
        # Validate file first
        is_valid, error = self.validate_file(file)
        if not is_valid:
            return False, None, error
        
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        ext = self._get_file_extension(original_filename)
        
        # Generate unique filename using UUID
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Create subfolder path
        if subfolder:
            save_path = os.path.join(self.upload_folder, secure_filename(subfolder))
        else:
            save_path = self.upload_folder
        
        # Ensure directory exists
        Path(save_path).mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(save_path, unique_filename)
        
        try:
            # Save file
            file.save(file_path)
            
            # Set secure permissions (readable by owner and group only)
            os.chmod(file_path, 0o640)
            
            # Return relative path for storage
            relative_path = os.path.relpath(file_path, self.upload_folder)
            return True, relative_path, None
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            return False, None, f"Failed to save file: {str(e)}"
    
    def scan_file_for_viruses(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Scan file for viruses (placeholder for actual implementation).
        
        In production, integrate with ClamAV or similar.
        """
        # TODO: Integrate with actual virus scanner
        # Example: pyclamd.scan_file(file_path)
        return True, None
    
    def generate_file_hash(self, file_content: bytes) -> str:
        """Generate SHA-256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()
    
    def cleanup_old_files(self, days: int = 30):
        """Clean up files older than specified days."""
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(self.upload_folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        current_app.logger.info(f"Deleted old file: {file_path}")
                except Exception as e:
                    current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")


# Helper functions for backward compatibility
def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    validator = FileUploadValidator()
    ext = validator._get_file_extension(filename)
    return ext is not None and ext in ALLOWED_EXTENSIONS


def secure_save_file(file, upload_folder: str = None, subfolder: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """Save file securely with validation."""
    validator = FileUploadValidator(upload_folder)
    return validator.save_file_securely(file, subfolder)