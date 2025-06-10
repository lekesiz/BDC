"""File scanner with magic byte detection and virus scanning."""

import os
import hashlib
import magic
import socket
from typing import Optional, Tuple, Dict
from pathlib import Path
import logging

from .config import FileUploadConfig
from .exceptions import (
    FileTypeNotAllowedException,
    VirusDetectedException,
    FileScanException
)

logger = logging.getLogger(__name__)


class FileScanner:
    """Scans files for security threats and validates file types."""
    
    def __init__(self, config: FileUploadConfig):
        self.config = config
        self.mime = magic.Magic(mime=True)
        self.file_magic = magic.Magic()
        
    def scan_file(self, file_path: str) -> Dict[str, any]:
        """
        Perform comprehensive file scanning.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            Dictionary with scan results
            
        Raises:
            FileTypeNotAllowedException: If file type is not allowed
            VirusDetectedException: If virus is detected
            FileScanException: For other scanning errors
        """
        try:
            # Check file exists
            if not os.path.exists(file_path):
                raise FileScanException(f"File not found: {file_path}")
            
            # Get file info
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            
            # Check file size
            if file_size > self.config.MAX_FILE_SIZE:
                raise FileScanException(
                    f"File size {file_size} exceeds maximum allowed size {self.config.MAX_FILE_SIZE}"
                )
            
            # Detect MIME type using magic bytes
            mime_type = self._detect_mime_type(file_path)
            file_description = self._get_file_description(file_path)
            
            # Validate file type
            file_category = self._validate_file_type(file_path, mime_type)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Scan for viruses if enabled
            virus_scan_result = None
            if self.config.ENABLE_VIRUS_SCAN:
                virus_scan_result = self._scan_for_virus(file_path)
            
            return {
                'file_path': file_path,
                'file_size': file_size,
                'mime_type': mime_type,
                'file_description': file_description,
                'file_category': file_category,
                'file_hash': file_hash,
                'virus_scan': virus_scan_result,
                'is_safe': True
            }
            
        except (FileTypeNotAllowedException, VirusDetectedException):
            raise
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {str(e)}")
            raise FileScanException(f"File scan failed: {str(e)}")
    
    def _detect_mime_type(self, file_path: str) -> str:
        """Detect MIME type using python-magic."""
        try:
            return self.mime.from_file(file_path)
        except Exception as e:
            logger.error(f"Error detecting MIME type: {str(e)}")
            raise FileScanException(f"Failed to detect MIME type: {str(e)}")
    
    def _get_file_description(self, file_path: str) -> str:
        """Get detailed file description using magic."""
        try:
            return self.file_magic.from_file(file_path)
        except Exception as e:
            logger.error(f"Error getting file description: {str(e)}")
            return "Unknown file type"
    
    def _validate_file_type(self, file_path: str, mime_type: str) -> str:
        """
        Validate file type against allowed types.
        
        Returns:
            File category (image, document, video, audio)
        """
        # Check extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext in self.config.BLOCKED_EXTENSIONS:
            raise FileTypeNotAllowedException(
                f"File extension {file_ext} is blocked for security reasons"
            )
        
        # Check MIME type
        file_category = None
        for category, allowed_mimes in self.config.ALLOWED_FILE_TYPES.items():
            if mime_type in allowed_mimes:
                file_category = category
                break
        
        if not file_category:
            raise FileTypeNotAllowedException(
                f"File type {mime_type} is not allowed"
            )
        
        # Additional validation for specific file types
        if file_category == 'image':
            self._validate_image_file(file_path, mime_type)
        
        return file_category
    
    def _validate_image_file(self, file_path: str, mime_type: str):
        """Additional validation for image files."""
        # Check for embedded scripts in SVG files
        if mime_type == 'image/svg+xml':
            with open(file_path, 'rb') as f:
                content = f.read()
                dangerous_patterns = [
                    b'<script',
                    b'javascript:',
                    b'onerror=',
                    b'onclick=',
                    b'onload='
                ]
                for pattern in dangerous_patterns:
                    if pattern in content.lower():
                        raise FileTypeNotAllowedException(
                            "SVG file contains potentially dangerous content"
                        )
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _scan_for_virus(self, file_path: str) -> Dict[str, any]:
        """
        Scan file for viruses using ClamAV.
        
        Returns:
            Dictionary with scan results
        """
        try:
            # Connect to ClamAV daemon
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.config.CLAMAV_HOST, self.config.CLAMAV_PORT))
                
                # Send INSTREAM command
                sock.send(b'zINSTREAM\0')
                
                # Send file in chunks
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(2048)
                        if not chunk:
                            break
                        
                        # Send chunk size and data
                        size = len(chunk)
                        sock.send(size.to_bytes(4, byteorder='big'))
                        sock.send(chunk)
                
                # Send zero-length chunk to indicate end
                sock.send(b'\0\0\0\0')
                
                # Receive response
                response = sock.recv(1024).decode('utf-8').strip()
                
                # Parse response
                if 'FOUND' in response:
                    virus_name = response.split(':')[1].strip()
                    raise VirusDetectedException(
                        f"Virus detected: {virus_name}"
                    )
                
                return {
                    'scanned': True,
                    'clean': True,
                    'response': response
                }
                
        except socket.error as e:
            logger.warning(f"ClamAV connection failed: {str(e)}")
            return {
                'scanned': False,
                'error': 'ClamAV service unavailable',
                'clean': None
            }
        except VirusDetectedException:
            raise
        except Exception as e:
            logger.error(f"Virus scan error: {str(e)}")
            return {
                'scanned': False,
                'error': str(e),
                'clean': None
            }
    
    def quarantine_file(self, file_path: str, reason: str):
        """Move infected or suspicious file to quarantine."""
        try:
            filename = os.path.basename(file_path)
            quarantine_path = os.path.join(
                self.config.QUARANTINE_FOLDER,
                f"{hashlib.md5(file_path.encode()).hexdigest()}_{filename}"
            )
            
            os.rename(file_path, quarantine_path)
            
            # Log quarantine action
            logger.warning(
                f"File quarantined: {file_path} -> {quarantine_path}. "
                f"Reason: {reason}"
            )
            
            return quarantine_path
            
        except Exception as e:
            logger.error(f"Failed to quarantine file: {str(e)}")
            # If quarantine fails, delete the file
            try:
                os.remove(file_path)
            except:
                pass
            raise FileScanException(f"Failed to quarantine file: {str(e)}")