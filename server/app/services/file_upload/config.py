"""Configuration for file upload security system."""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class FileUploadConfig:
    """Configuration for file upload system."""
    
    # File size limits (in bytes)
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    MAX_DOCUMENT_SIZE: int = 50 * 1024 * 1024  # 50 MB
    
    # Allowed file types with MIME types
    ALLOWED_FILE_TYPES: Dict[str, List[str]] = field(default_factory=lambda: {
        'image': [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
            'image/svg+xml'
        ],
        'document': [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'text/csv'
        ],
        'video': [
            'video/mp4',
            'video/mpeg',
            'video/quicktime',
            'video/webm'
        ],
        'audio': [
            'audio/mpeg',
            'audio/wav',
            'audio/ogg',
            'audio/webm'
        ]
    })
    
    # File extension whitelist
    ALLOWED_EXTENSIONS: List[str] = field(default_factory=lambda: [
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv',
        '.mp4', '.mpeg', '.mov', '.webm',
        '.mp3', '.wav', '.ogg'
    ])
    
    # Dangerous file extensions to block
    BLOCKED_EXTENSIONS: List[str] = field(default_factory=lambda: [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.app', '.dmg', '.pkg', '.deb', '.rpm', '.msi',
        '.php', '.py', '.rb', '.sh', '.ps1', '.psm1', '.ps1xml', '.psc1',
        '.gadget', '.inf', '.ins', '.inx', '.isu', '.job', '.jse', '.lnk',
        '.msc', '.msh', '.msh1', '.msh2', '.mshxml', '.msh1xml', '.msh2xml',
        '.reg', '.rgs', '.sct', '.shb', '.shs', '.u3p', '.vb', '.vbe',
        '.vbscript', '.ws', '.wsf', '.wsh', '.dll', '.so'
    ])
    
    # Storage paths
    UPLOAD_FOLDER: str = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
    TEMP_FOLDER: str = os.environ.get('TEMP_FOLDER', '/tmp/upload_temp')
    QUARANTINE_FOLDER: str = os.environ.get('QUARANTINE_FOLDER', '/tmp/quarantine')
    
    # S3/CDN Configuration
    S3_BUCKET: Optional[str] = os.environ.get('S3_BUCKET')
    S3_REGION: str = os.environ.get('S3_REGION', 'us-east-1')
    S3_ACCESS_KEY: Optional[str] = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY: Optional[str] = os.environ.get('S3_SECRET_KEY')
    CDN_URL: Optional[str] = os.environ.get('CDN_URL')
    
    # ClamAV Configuration
    CLAMAV_HOST: str = os.environ.get('CLAMAV_HOST', 'localhost')
    CLAMAV_PORT: int = int(os.environ.get('CLAMAV_PORT', '3310'))
    ENABLE_VIRUS_SCAN: bool = os.environ.get('ENABLE_VIRUS_SCAN', 'True').lower() == 'true'
    
    # Encryption Configuration
    ENABLE_ENCRYPTION: bool = os.environ.get('ENABLE_ENCRYPTION', 'True').lower() == 'true'
    ENCRYPTION_KEY: Optional[str] = os.environ.get('FILE_ENCRYPTION_KEY')
    
    # Image Processing Configuration
    MAX_IMAGE_DIMENSION: int = 4096
    THUMBNAIL_SIZES: Dict[str, tuple] = field(default_factory=lambda: {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (800, 800)
    })
    
    # Security Configuration
    ENABLE_MAGIC_VALIDATION: bool = True
    STRIP_EXIF_DATA: bool = True
    SANITIZE_FILENAMES: bool = True
    GENERATE_SECURE_NAMES: bool = True
    
    # Versioning Configuration
    ENABLE_VERSIONING: bool = True
    MAX_VERSIONS: int = 10
    
    # Audit Configuration
    ENABLE_AUDIT_LOG: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90
    
    def __post_init__(self):
        """Create necessary directories after initialization."""
        for folder in [self.UPLOAD_FOLDER, self.TEMP_FOLDER, self.QUARANTINE_FOLDER]:
            os.makedirs(folder, exist_ok=True)