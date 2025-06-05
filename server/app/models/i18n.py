"""Internationalization models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.extensions import db


class Language(db.Model):
    """Language configuration model."""
    __tablename__ = 'languages'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)  # 'en', 'tr', 'ar', etc.
    name = Column(String(100), nullable=False)  # 'English', 'Turkish', etc.
    native_name = Column(String(100), nullable=False)  # 'English', 'Türkçe', 'العربية', etc.
    direction = Column(String(3), default='ltr')  # 'ltr' or 'rtl'
    region = Column(String(10), nullable=True)  # 'en-US', 'tr-TR', etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Metadata
    flag_icon = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'native_name': self.native_name,
            'direction': self.direction,
            'region': self.region,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'flag_icon': self.flag_icon,
            'sort_order': self.sort_order,
            'is_rtl': self.direction == 'rtl'
        }


class MultilingualContent(db.Model):
    """Model for storing multilingual content versions."""
    __tablename__ = 'multilingual_content'
    
    id = Column(Integer, primary_key=True)
    
    # Content identification
    entity_type = Column(String(50), nullable=False)  # 'program', 'document', 'notification', etc.
    entity_id = Column(String(255), nullable=False)  # ID of the source entity
    field_name = Column(String(100), nullable=False)  # 'title', 'description', 'content', etc.
    
    # Language and content
    language_code = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default='text')  # 'text', 'html', 'markdown'
    
    # Translation metadata
    is_original = Column(Boolean, default=False)  # True for source language
    translation_status = Column(String(20), default='draft')  # 'draft', 'translated', 'reviewed', 'published'
    translation_method = Column(String(20), nullable=True)  # 'manual', 'ai', 'mixed'
    quality_score = Column(db.Float, nullable=True)
    
    # Version control
    version = Column(Integer, default=1)
    is_current = Column(Boolean, default=True)
    parent_version_id = Column(Integer, ForeignKey('multilingual_content.id'), nullable=True)
    
    # User tracking
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    translated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    translated_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    language = relationship('Language', foreign_keys=[language_code], primaryjoin="MultilingualContent.language_code == Language.code")
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])
    translator = relationship('User', foreign_keys=[translated_by])
    reviewer = relationship('User', foreign_keys=[reviewed_by])
    parent_version = relationship('MultilingualContent', remote_side=[id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_entity_field_lang', 'entity_type', 'entity_id', 'field_name', 'language_code'),
        Index('idx_entity_current', 'entity_type', 'entity_id', 'is_current'),
        Index('idx_translation_status', 'translation_status'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'field_name': self.field_name,
            'language_code': self.language_code,
            'content': self.content,
            'content_type': self.content_type,
            'is_original': self.is_original,
            'translation_status': self.translation_status,
            'translation_method': self.translation_method,
            'quality_score': self.quality_score,
            'version': self.version,
            'is_current': self.is_current,
            'parent_version_id': self.parent_version_id,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'translated_by': self.translated_by,
            'reviewed_by': self.reviewed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'translated_at': self.translated_at.isoformat() if self.translated_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }


class TranslationProject(db.Model):
    """Model for managing translation projects and workflows."""
    __tablename__ = 'translation_projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Project configuration
    source_language = Column(String(10), nullable=False)
    target_languages = Column(Text, nullable=False)  # JSON array of language codes
    
    # Project scope
    entity_types = Column(Text, nullable=True)  # JSON array of entity types to translate
    entity_ids = Column(Text, nullable=True)  # JSON array of specific entity IDs
    field_names = Column(Text, nullable=True)  # JSON array of field names to translate
    
    # Workflow settings
    require_review = Column(Boolean, default=True)
    auto_approve_ai = Column(Boolean, default=False)
    quality_threshold = Column(db.Float, default=0.8)
    
    # Status and progress
    status = Column(String(20), default='draft')  # 'draft', 'active', 'completed', 'paused', 'cancelled'
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    progress_percentage = Column(db.Float, default=0.0)
    
    # Deadlines
    start_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    
    # User assignments
    project_manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_translators = Column(Text, nullable=True)  # JSON array of user IDs
    assigned_reviewers = Column(Text, nullable=True)  # JSON array of user IDs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project_manager = relationship('User', foreign_keys=[project_manager_id])
    
    def to_dict(self):
        """Convert to dictionary."""
        import json
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source_language': self.source_language,
            'target_languages': json.loads(self.target_languages) if self.target_languages else [],
            'entity_types': json.loads(self.entity_types) if self.entity_types else [],
            'entity_ids': json.loads(self.entity_ids) if self.entity_ids else [],
            'field_names': json.loads(self.field_names) if self.field_names else [],
            'require_review': self.require_review,
            'auto_approve_ai': self.auto_approve_ai,
            'quality_threshold': self.quality_threshold,
            'status': self.status,
            'total_items': self.total_items,
            'completed_items': self.completed_items,
            'progress_percentage': self.progress_percentage,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'project_manager_id': self.project_manager_id,
            'assigned_translators': json.loads(self.assigned_translators) if self.assigned_translators else [],
            'assigned_reviewers': json.loads(self.assigned_reviewers) if self.assigned_reviewers else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TranslationWorkflow(db.Model):
    """Model for tracking translation workflow states."""
    __tablename__ = 'translation_workflows'
    
    id = Column(Integer, primary_key=True)
    
    # Content reference
    content_id = Column(Integer, ForeignKey('multilingual_content.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('translation_projects.id'), nullable=True)
    
    # Workflow state
    current_state = Column(String(30), default='pending_translation')  # State machine states
    previous_state = Column(String(30), nullable=True)
    
    # Assignment
    assigned_translator = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_reviewer = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Deadlines
    translation_deadline = Column(DateTime, nullable=True)
    review_deadline = Column(DateTime, nullable=True)
    
    # Progress tracking
    translation_started_at = Column(DateTime, nullable=True)
    translation_completed_at = Column(DateTime, nullable=True)
    review_started_at = Column(DateTime, nullable=True)
    review_completed_at = Column(DateTime, nullable=True)
    
    # Quality and comments
    translation_quality = Column(db.Float, nullable=True)
    review_quality = Column(db.Float, nullable=True)
    translator_notes = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content = relationship('MultilingualContent', back_populates='workflows')
    project = relationship('TranslationProject')
    translator = relationship('User', foreign_keys=[assigned_translator])
    reviewer = relationship('User', foreign_keys=[assigned_reviewer])
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'project_id': self.project_id,
            'current_state': self.current_state,
            'previous_state': self.previous_state,
            'assigned_translator': self.assigned_translator,
            'assigned_reviewer': self.assigned_reviewer,
            'translation_deadline': self.translation_deadline.isoformat() if self.translation_deadline else None,
            'review_deadline': self.review_deadline.isoformat() if self.review_deadline else None,
            'translation_started_at': self.translation_started_at.isoformat() if self.translation_started_at else None,
            'translation_completed_at': self.translation_completed_at.isoformat() if self.translation_completed_at else None,
            'review_started_at': self.review_started_at.isoformat() if self.review_started_at else None,
            'review_completed_at': self.review_completed_at.isoformat() if self.review_completed_at else None,
            'translation_quality': self.translation_quality,
            'review_quality': self.review_quality,
            'translator_notes': self.translator_notes,
            'reviewer_notes': self.reviewer_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UserLanguagePreference(db.Model):
    """Model for storing user language preferences."""
    __tablename__ = 'user_language_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Language preferences
    primary_language = Column(String(10), nullable=False, default='en')
    secondary_languages = Column(Text, nullable=True)  # JSON array of language codes
    
    # Auto-detection preferences
    enable_auto_detection = Column(Boolean, default=True)
    detect_from_browser = Column(Boolean, default=True)
    detect_from_content = Column(Boolean, default=False)
    detect_from_location = Column(Boolean, default=False)
    
    # Content preferences
    fallback_language = Column(String(10), default='en')
    show_original_content = Column(Boolean, default=False)
    auto_translate_content = Column(Boolean, default=True)
    
    # Translation preferences for user as translator
    translation_specialties = Column(Text, nullable=True)  # JSON array of domains
    available_for_translation = Column(Boolean, default=False)
    translation_language_pairs = Column(Text, nullable=True)  # JSON array of {source, target} pairs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='language_preferences')
    
    def to_dict(self):
        """Convert to dictionary."""
        import json
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'primary_language': self.primary_language,
            'secondary_languages': json.loads(self.secondary_languages) if self.secondary_languages else [],
            'enable_auto_detection': self.enable_auto_detection,
            'detect_from_browser': self.detect_from_browser,
            'detect_from_content': self.detect_from_content,
            'detect_from_location': self.detect_from_location,
            'fallback_language': self.fallback_language,
            'show_original_content': self.show_original_content,
            'auto_translate_content': self.auto_translate_content,
            'translation_specialties': json.loads(self.translation_specialties) if self.translation_specialties else [],
            'available_for_translation': self.available_for_translation,
            'translation_language_pairs': json.loads(self.translation_language_pairs) if self.translation_language_pairs else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Add relationship to MultilingualContent
MultilingualContent.workflows = relationship('TranslationWorkflow', back_populates='content')