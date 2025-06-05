"""Document version service for managing document versions."""

import os
import shutil
import hashlib
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.document import Document
from app.models.document_version import DocumentVersion, DocumentComparison
from app.services.notification_service import NotificationService


class DocumentVersionService:
    """Service for document version management."""
    
    @staticmethod
    def create_version(document_id, file, user_id, change_notes=None):
        """Create a new version of a document."""
        try:
            # Get the document
            document = Document.query.get(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Check if versioning is enabled
            if not document.version_control_enabled:
                raise ValueError("Version control is not enabled for this document")
            
            # Calculate file hash
            file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            file.seek(0)  # Reset file pointer
            
            # Check if content has changed
            if document.file_hash == file_hash:
                raise ValueError("File content has not changed")
            
            # Update current version to not current
            DocumentVersion.query.filter_by(
                document_id=document_id,
                is_current=True
            ).update({'is_current': False})
            
            # Create new version
            new_version_number = document.current_version + 1
            
            # Generate versioned filename
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            versioned_filename = f"{name}_v{new_version_number}{ext}"
            
            # Create version directory if not exists
            version_dir = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'versions',
                str(document_id)
            )
            os.makedirs(version_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(version_dir, versioned_filename)
            file.save(file_path)
            
            # Create version record
            version = DocumentVersion(
                document_id=document_id,
                version_number=new_version_number,
                file_path=file_path,
                filename=filename,
                file_size=len(file_content),
                mime_type=file.content_type,
                file_hash=file_hash,
                title=document.title,
                description=document.description,
                change_notes=change_notes,
                created_by=user_id,
                is_current=True
            )
            
            db.session.add(version)
            
            # Update document
            document.current_version = new_version_number
            document.file_path = file_path
            document.file_hash = file_hash
            document.file_size = len(file_content)
            document.filename = filename
            document.mime_type = file.content_type
            document.updated_at = datetime.utcnow()
            
            # Clean up old versions if exceeds max
            if document.max_versions > 0:
                old_versions = DocumentVersion.query.filter_by(
                    document_id=document_id
                ).order_by(DocumentVersion.version_number.desc()).offset(
                    document.max_versions
                ).all()
                
                for old_version in old_versions:
                    # Delete file
                    if os.path.exists(old_version.file_path):
                        os.remove(old_version.file_path)
                    # Mark as archived
                    old_version.is_archived = True
            
            db.session.commit()
            
            # Send notification to document owner
            if document.upload_by != user_id:
                NotificationService.create_notification(
                    user_id=document.upload_by,
                    title='Document Updated',
                    message=f'A new version of "{document.title}" has been uploaded',
                    type='document',
                    related_id=document.id,
                    related_type='document'
                )
            
            return version
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating document version: {str(e)}")
            raise
    
    @staticmethod
    def get_versions(document_id, include_archived=False):
        """Get all versions of a document."""
        query = DocumentVersion.query.filter_by(document_id=document_id)
        
        if not include_archived:
            query = query.filter_by(is_archived=False)
        
        return query.order_by(DocumentVersion.version_number.desc()).all()
    
    @staticmethod
    def get_version(version_id):
        """Get a specific version."""
        return DocumentVersion.query.get(version_id)
    
    @staticmethod
    def restore_version(document_id, version_id, user_id):
        """Restore a previous version of a document."""
        try:
            # Get the document and version
            document = Document.query.get(document_id)
            version = DocumentVersion.query.get(version_id)
            
            if not document or not version:
                raise ValueError("Document or version not found")
            
            if version.document_id != document_id:
                raise ValueError("Version does not belong to this document")
            
            # Create a new version from the old one
            new_version_number = document.current_version + 1
            
            # Copy the old file to new location
            name, ext = os.path.splitext(version.filename)
            versioned_filename = f"{name}_v{new_version_number}{ext}"
            
            version_dir = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'versions',
                str(document_id)
            )
            new_file_path = os.path.join(version_dir, versioned_filename)
            
            shutil.copy2(version.file_path, new_file_path)
            
            # Update current version to not current
            DocumentVersion.query.filter_by(
                document_id=document_id,
                is_current=True
            ).update({'is_current': False})
            
            # Create new version record
            new_version = DocumentVersion(
                document_id=document_id,
                version_number=new_version_number,
                file_path=new_file_path,
                filename=version.filename,
                file_size=version.file_size,
                mime_type=version.mime_type,
                file_hash=version.file_hash,
                title=version.title,
                description=version.description,
                change_notes=f"Restored from version {version.version_number}",
                created_by=user_id,
                is_current=True
            )
            
            db.session.add(new_version)
            
            # Update document
            document.current_version = new_version_number
            document.file_path = new_file_path
            document.file_hash = version.file_hash
            document.file_size = version.file_size
            document.filename = version.filename
            document.mime_type = version.mime_type
            document.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return new_version
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error restoring document version: {str(e)}")
            raise
    
    @staticmethod
    def compare_versions(document_id, version1_id, version2_id, user_id):
        """Compare two versions of a document."""
        try:
            version1 = DocumentVersion.query.get(version1_id)
            version2 = DocumentVersion.query.get(version2_id)
            
            if not version1 or not version2:
                raise ValueError("One or both versions not found")
            
            if version1.document_id != document_id or version2.document_id != document_id:
                raise ValueError("Versions do not belong to the same document")
            
            # Calculate similarity (simplified - in real implementation, use proper diff algorithms)
            similarity_score = 100.0
            differences = {
                'file_size_diff': version2.file_size - version1.file_size,
                'time_diff': (version2.created_at - version1.created_at).total_seconds(),
                'hash_changed': version1.file_hash != version2.file_hash
            }
            
            if version1.file_hash != version2.file_hash:
                similarity_score = 0.0  # Different files
            
            # Save comparison
            comparison = DocumentComparison(
                document_id=document_id,
                version1_id=version1_id,
                version2_id=version2_id,
                similarity_score=similarity_score,
                differences=differences,
                comparison_type='binary',
                compared_by=user_id
            )
            
            db.session.add(comparison)
            db.session.commit()
            
            return comparison
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error comparing document versions: {str(e)}")
            raise
    
    @staticmethod
    def enable_versioning(document_id, max_versions=10):
        """Enable version control for a document."""
        try:
            document = Document.query.get(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Enable versioning
            document.version_control_enabled = True
            document.max_versions = max_versions
            
            # Create initial version from current document
            version = DocumentVersion(
                document_id=document_id,
                version_number=1,
                file_path=document.file_path,
                filename=document.filename or os.path.basename(document.file_path),
                file_size=document.file_size,
                mime_type=document.mime_type,
                file_hash=document.file_hash,
                title=document.title,
                description=document.description,
                change_notes="Initial version",
                created_by=document.upload_by,
                is_current=True
            )
            
            db.session.add(version)
            db.session.commit()
            
            return version
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error enabling document versioning: {str(e)}")
            raise