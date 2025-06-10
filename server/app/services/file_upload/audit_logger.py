"""File upload audit logging and versioning system."""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import logging

from app.extensions import db
from .config import FileUploadConfig

logger = logging.getLogger(__name__)


class FileUploadAudit(db.Model):
    """Model for file upload audit logs."""
    
    __tablename__ = 'file_upload_audits'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # File information
    file_id = Column(String(100), unique=True, nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    secure_filename = Column(String(255), nullable=False)
    file_category = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=False)
    
    # Storage information
    storage_path = Column(Text)
    s3_url = Column(Text)
    cdn_url = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    
    # Security scan results
    virus_scan_result = Column(Text)
    security_flags = Column(Text)
    
    # Audit information
    action = Column(String(50), nullable=False)  # upload, download, delete, modify
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Additional metadata
    metadata = Column(Text)
    
    # Relationships
    versions = relationship('FileVersion', back_populates='audit_log', 
                          cascade='all, delete-orphan')


class FileVersion(db.Model):
    """Model for file versioning."""
    
    __tablename__ = 'file_versions'
    
    id = Column(Integer, primary_key=True)
    audit_id = Column(Integer, ForeignKey('file_upload_audits.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # Version information
    storage_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False)
    
    # Version metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(50), nullable=False)
    comment = Column(Text)
    
    # Relationship
    audit_log = relationship('FileUploadAudit', back_populates='versions')


class FileAuditLogger:
    """Handles file upload audit logging and versioning."""
    
    def __init__(self, config: FileUploadConfig):
        self.config = config
    
    def log_upload(self, user_id: str, tenant_id: str, file_info: Dict, 
                   request_info: Optional[Dict] = None) -> FileUploadAudit:
        """Log a file upload event."""
        try:
            audit_entry = FileUploadAudit(
                user_id=user_id,
                tenant_id=tenant_id,
                file_id=file_info.get('file_id', file_info.get('secure_filename')),
                original_filename=file_info['original_filename'],
                secure_filename=file_info['secure_filename'],
                file_category=file_info['file_category'],
                file_size=file_info['file_size'],
                mime_type=file_info['mime_type'],
                file_hash=file_info['file_hash'],
                storage_path=file_info.get('local_path'),
                s3_url=file_info.get('s3_url'),
                cdn_url=file_info.get('cdn_url'),
                is_encrypted=file_info.get('encrypted', False),
                virus_scan_result=json.dumps(file_info.get('virus_scan')),
                security_flags=json.dumps(file_info.get('security_flags', [])),
                action='upload',
                ip_address=request_info.get('ip_address') if request_info else None,
                user_agent=request_info.get('user_agent') if request_info else None,
                metadata=json.dumps(file_info.get('metadata', {}))
            )
            
            db.session.add(audit_entry)
            
            # Create initial version
            if self.config.ENABLE_VERSIONING:
                self._create_version(audit_entry, 1, user_id, "Initial upload")
            
            db.session.commit()
            
            logger.info(
                f"File upload logged: {file_info['original_filename']} "
                f"by user {user_id}"
            )
            
            return audit_entry
            
        except Exception as e:
            logger.error(f"Failed to log file upload: {str(e)}")
            db.session.rollback()
            raise
    
    def log_download(self, file_id: str, user_id: str, 
                    request_info: Optional[Dict] = None):
        """Log a file download event."""
        try:
            # Find the original audit entry
            original_audit = FileUploadAudit.query.filter_by(
                file_id=file_id
            ).first()
            
            if not original_audit:
                logger.warning(f"File not found for download logging: {file_id}")
                return
            
            # Create download audit entry
            download_entry = FileUploadAudit(
                user_id=user_id,
                tenant_id=original_audit.tenant_id,
                file_id=f"{file_id}_download_{datetime.utcnow().timestamp()}",
                original_filename=original_audit.original_filename,
                secure_filename=original_audit.secure_filename,
                file_category=original_audit.file_category,
                file_size=original_audit.file_size,
                mime_type=original_audit.mime_type,
                file_hash=original_audit.file_hash,
                action='download',
                ip_address=request_info.get('ip_address') if request_info else None,
                user_agent=request_info.get('user_agent') if request_info else None
            )
            
            db.session.add(download_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log file download: {str(e)}")
            db.session.rollback()
    
    def log_deletion(self, file_id: str, user_id: str, reason: str = None):
        """Log a file deletion event."""
        try:
            # Find the original audit entry
            original_audit = FileUploadAudit.query.filter_by(
                file_id=file_id
            ).first()
            
            if not original_audit:
                logger.warning(f"File not found for deletion logging: {file_id}")
                return
            
            # Create deletion audit entry
            deletion_entry = FileUploadAudit(
                user_id=user_id,
                tenant_id=original_audit.tenant_id,
                file_id=f"{file_id}_delete_{datetime.utcnow().timestamp()}",
                original_filename=original_audit.original_filename,
                secure_filename=original_audit.secure_filename,
                file_category=original_audit.file_category,
                file_size=original_audit.file_size,
                mime_type=original_audit.mime_type,
                file_hash=original_audit.file_hash,
                action='delete',
                metadata=json.dumps({'reason': reason}) if reason else None
            )
            
            db.session.add(deletion_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log file deletion: {str(e)}")
            db.session.rollback()
    
    def add_version(self, file_id: str, new_file_info: Dict, 
                   user_id: str, comment: str = None):
        """Add a new version of a file."""
        try:
            # Find the original audit entry
            original_audit = FileUploadAudit.query.filter_by(
                file_id=file_id
            ).first()
            
            if not original_audit:
                raise ValueError(f"File not found: {file_id}")
            
            # Get current version number
            current_version = db.session.query(
                db.func.max(FileVersion.version_number)
            ).filter_by(
                audit_id=original_audit.id
            ).scalar() or 0
            
            # Check version limit
            if current_version >= self.config.MAX_VERSIONS:
                # Delete oldest version
                oldest_version = FileVersion.query.filter_by(
                    audit_id=original_audit.id
                ).order_by(FileVersion.version_number).first()
                
                if oldest_version:
                    # Delete the file
                    if os.path.exists(oldest_version.storage_path):
                        os.remove(oldest_version.storage_path)
                    db.session.delete(oldest_version)
            
            # Create new version
            new_version = self._create_version(
                original_audit,
                current_version + 1,
                user_id,
                comment,
                new_file_info
            )
            
            # Update main audit entry
            original_audit.file_size = new_file_info['file_size']
            original_audit.file_hash = new_file_info['file_hash']
            original_audit.storage_path = new_file_info.get('local_path')
            
            db.session.commit()
            
            return new_version
            
        except Exception as e:
            logger.error(f"Failed to add file version: {str(e)}")
            db.session.rollback()
            raise
    
    def _create_version(self, audit_entry: FileUploadAudit, version_number: int,
                       user_id: str, comment: str = None, 
                       file_info: Optional[Dict] = None):
        """Create a file version entry."""
        version = FileVersion(
            audit_id=audit_entry.id,
            version_number=version_number,
            storage_path=file_info.get('local_path') if file_info else audit_entry.storage_path,
            file_size=file_info.get('file_size') if file_info else audit_entry.file_size,
            file_hash=file_info.get('file_hash') if file_info else audit_entry.file_hash,
            created_by=user_id,
            comment=comment
        )
        
        db.session.add(version)
        return version
    
    def get_file_history(self, file_id: str) -> Dict:
        """Get complete history of a file."""
        try:
            # Get main audit entry
            main_audit = FileUploadAudit.query.filter_by(
                file_id=file_id
            ).first()
            
            if not main_audit:
                return None
            
            # Get all related audit entries
            all_audits = FileUploadAudit.query.filter(
                FileUploadAudit.secure_filename == main_audit.secure_filename
            ).order_by(FileUploadAudit.timestamp.desc()).all()
            
            # Get versions
            versions = FileVersion.query.filter_by(
                audit_id=main_audit.id
            ).order_by(FileVersion.version_number.desc()).all()
            
            return {
                'file_info': {
                    'file_id': main_audit.file_id,
                    'original_filename': main_audit.original_filename,
                    'current_size': main_audit.file_size,
                    'mime_type': main_audit.mime_type,
                    'uploaded_at': main_audit.timestamp.isoformat(),
                    'uploaded_by': main_audit.user_id
                },
                'audit_trail': [
                    {
                        'action': audit.action,
                        'user_id': audit.user_id,
                        'timestamp': audit.timestamp.isoformat(),
                        'ip_address': audit.ip_address
                    }
                    for audit in all_audits
                ],
                'versions': [
                    {
                        'version': version.version_number,
                        'size': version.file_size,
                        'created_at': version.created_at.isoformat(),
                        'created_by': version.created_by,
                        'comment': version.comment
                    }
                    for version in versions
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get file history: {str(e)}")
            return None
    
    def cleanup_old_audits(self):
        """Clean up old audit logs based on retention policy."""
        try:
            if self.config.AUDIT_LOG_RETENTION_DAYS <= 0:
                return
            
            cutoff_date = datetime.utcnow() - timedelta(
                days=self.config.AUDIT_LOG_RETENTION_DAYS
            )
            
            # Delete old audit entries
            old_audits = FileUploadAudit.query.filter(
                FileUploadAudit.timestamp < cutoff_date,
                FileUploadAudit.action.in_(['download', 'delete'])
            ).all()
            
            for audit in old_audits:
                db.session.delete(audit)
            
            db.session.commit()
            
            logger.info(f"Cleaned up {len(old_audits)} old audit entries")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old audits: {str(e)}")
            db.session.rollback()
    
    def get_user_upload_stats(self, user_id: str, tenant_id: str) -> Dict:
        """Get upload statistics for a user."""
        try:
            # Get upload count
            upload_count = FileUploadAudit.query.filter_by(
                user_id=user_id,
                tenant_id=tenant_id,
                action='upload'
            ).count()
            
            # Get total size
            total_size = db.session.query(
                db.func.sum(FileUploadAudit.file_size)
            ).filter_by(
                user_id=user_id,
                tenant_id=tenant_id,
                action='upload'
            ).scalar() or 0
            
            # Get file categories
            categories = db.session.query(
                FileUploadAudit.file_category,
                db.func.count(FileUploadAudit.id)
            ).filter_by(
                user_id=user_id,
                tenant_id=tenant_id,
                action='upload'
            ).group_by(FileUploadAudit.file_category).all()
            
            return {
                'total_uploads': upload_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'categories': {cat: count for cat, count in categories}
            }
            
        except Exception as e:
            logger.error(f"Failed to get user upload stats: {str(e)}")
            return {
                'total_uploads': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'categories': {}
            }