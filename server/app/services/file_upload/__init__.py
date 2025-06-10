"""File Upload Security System for BDC Project.

This module provides a comprehensive file upload security system with:
- Advanced file type detection using python-magic
- Virus scanning integration (ClamAV)
- Image processing and sanitization
- Secure storage with encryption
- CDN/S3 integration
- File versioning and audit trail
"""

from .file_upload_service import FileUploadService
from .file_scanner import FileScanner
from .image_processor import ImageProcessor
from .storage_manager import StorageManager
from .audit_logger import FileAuditLogger
from .config import FileUploadConfig

__all__ = [
    'FileUploadService',
    'FileScanner',
    'ImageProcessor',
    'StorageManager',
    'FileAuditLogger',
    'FileUploadConfig'
]