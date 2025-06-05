"""AI Question Generation models module."""

from datetime import datetime
import json
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Boolean, 
    ForeignKey, JSON, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.extensions import db


class ContentType(db.Model):
    """Content types for question generation."""
    __tablename__ = 'content_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    supported_formats = Column(JSON, default=list)  # ['pdf', 'docx', 'txt', 'mp4', 'mp3', 'url']
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'supported_formats': self.supported_formats,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# SourceContent class temporarily disabled due to metadata conflict


class QuestionType(db.Model):
    """Question types for AI generation."""
    __tablename__ = 'question_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Generation configuration
    generation_prompt_template = Column(Text, nullable=True)
    validation_rules = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'validation_rules': self.validation_rules,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class BloomsTaxonomy(db.Model):
    """Bloom's taxonomy levels for question categorization."""
    __tablename__ = 'blooms_taxonomy'
    
    id = Column(Integer, primary_key=True)
    level = Column(String(20), nullable=False, unique=True)  # remember, understand, apply, analyze, evaluate, create
    order = Column(Integer, nullable=False)  # 1-6
    description = Column(Text, nullable=True)
    keywords = Column(JSON, default=list)  # Action verbs associated with this level
    
    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'order': self.order,
            'description': self.description,
            'keywords': self.keywords
        }


class LearningObjective(db.Model):
    """Learning objectives for question alignment."""
    __tablename__ = 'learning_objectives'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    blooms_level_id = Column(Integer, ForeignKey('blooms_taxonomy.id'), nullable=True)
    
    # Metadata
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='learning_objectives')
    creator = relationship('User', backref='created_learning_objectives')
    blooms_level = relationship('BloomsTaxonomy', backref='learning_objectives')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'creator_id': self.creator_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'blooms_level_id': self.blooms_level_id,
            'tags': self.tags,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class QuestionGenerationRequest(db.Model):
    """Request for AI question generation."""
    __tablename__ = 'question_generation_requests'
    
    id = Column(Integer, primary_key=True)
    request_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    source_content_id = Column(Integer, ForeignKey('source_content.id'), nullable=False)
    
    # Generation parameters
    question_count = Column(Integer, default=10)
    question_types = Column(JSON, default=list)  # List of question type IDs
    difficulty_range = Column(JSON, default=[1, 10])  # [min, max] difficulty
    blooms_levels = Column(JSON, default=list)  # List of Bloom's taxonomy level IDs
    learning_objectives = Column(JSON, default=list)  # List of learning objective IDs
    
    # Customization options
    language = Column(String(10), default='en')
    topic_focus = Column(JSON, default=list)  # Specific topics to focus on
    avoid_topics = Column(JSON, default=list)  # Topics to avoid
    custom_instructions = Column(Text, nullable=True)
    
    # Processing status
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    error_message = Column(Text, nullable=True)
    
    # AI model information
    ai_model = Column(String(50), default='gpt-4')
    model_parameters = Column(JSON, default=dict)
    total_tokens_used = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)
    
    # Results
    questions_generated = Column(Integer, default=0)
    questions_approved = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    tenant = relationship('Tenant', backref='question_generation_requests')
    creator = relationship('User', backref='question_generation_requests')
    source_content = relationship('SourceContent', backref='generation_requests')
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'tenant_id': self.tenant_id,
            'creator_id': self.creator_id,
            'source_content_id': self.source_content_id,
            'question_count': self.question_count,
            'question_types': self.question_types,
            'difficulty_range': self.difficulty_range,
            'blooms_levels': self.blooms_levels,
            'learning_objectives': self.learning_objectives,
            'language': self.language,
            'topic_focus': self.topic_focus,
            'avoid_topics': self.avoid_topics,
            'custom_instructions': self.custom_instructions,
            'status': self.status,
            'progress': self.progress,
            'error_message': self.error_message,
            'ai_model': self.ai_model,
            'model_parameters': self.model_parameters,
            'total_tokens_used': self.total_tokens_used,
            'cost_estimate': self.cost_estimate,
            'questions_generated': self.questions_generated,
            'questions_approved': self.questions_approved,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class GeneratedQuestion(db.Model):
    """AI-generated questions."""
    __tablename__ = 'generated_questions'
    
    id = Column(Integer, primary_key=True)
    generation_request_id = Column(Integer, ForeignKey('question_generation_requests.id'), nullable=False)
    question_type_id = Column(Integer, ForeignKey('question_types.id'), nullable=False)
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_options = Column(JSON, nullable=True)  # For multiple choice, matching, etc.
    correct_answer = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    
    # Metadata
    difficulty_level = Column(Float, nullable=False)  # 1-10 scale
    blooms_level_id = Column(Integer, ForeignKey('blooms_taxonomy.id'), nullable=True)
    learning_objective_id = Column(Integer, ForeignKey('learning_objectives.id'), nullable=True)
    keywords = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    
    # Quality metrics
    quality_score = Column(Float, nullable=True)  # AI-generated quality score
    clarity_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    uniqueness_score = Column(Float, nullable=True)
    
    # Approval workflow
    status = Column(String(20), default='pending')  # pending, approved, rejected, needs_review
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    review_notes = Column(Text, nullable=True)
    review_date = Column(DateTime, nullable=True)
    
    # Usage tracking
    times_used = Column(Integer, default=0)
    performance_data = Column(JSON, default=dict)  # Average scores, completion rates, etc.
    
    # AI generation details
    generation_prompt = Column(Text, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    tokens_used = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    generation_request = relationship('QuestionGenerationRequest', backref='generated_questions')
    question_type = relationship('QuestionType', backref='generated_questions')
    blooms_level = relationship('BloomsTaxonomy', backref='generated_questions')
    learning_objective = relationship('LearningObjective', backref='generated_questions')
    reviewer = relationship('User', backref='reviewed_questions')
    
    # Indexes
    __table_args__ = (
        Index('idx_generated_questions_status', 'status'),
        Index('idx_generated_questions_difficulty', 'difficulty_level'),
        Index('idx_generated_questions_quality', 'quality_score'),
        Index('idx_generated_questions_request', 'generation_request_id'),
    )
    
    def to_dict(self, include_sensitive=False):
        result = {
            'id': self.id,
            'generation_request_id': self.generation_request_id,
            'question_type_id': self.question_type_id,
            'question_text': self.question_text,
            'question_options': self.question_options,
            'explanation': self.explanation,
            'difficulty_level': self.difficulty_level,
            'blooms_level_id': self.blooms_level_id,
            'learning_objective_id': self.learning_objective_id,
            'keywords': self.keywords,
            'topics': self.topics,
            'quality_score': self.quality_score,
            'clarity_score': self.clarity_score,
            'relevance_score': self.relevance_score,
            'uniqueness_score': self.uniqueness_score,
            'status': self.status,
            'reviewed_by': self.reviewed_by,
            'review_notes': self.review_notes,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'times_used': self.times_used,
            'performance_data': self.performance_data,
            'ai_confidence': self.ai_confidence,
            'tokens_used': self.tokens_used,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            result['correct_answer'] = self.correct_answer
            result['generation_prompt'] = self.generation_prompt
            
        return result


class QuestionDuplicate(db.Model):
    """Track potential duplicate questions."""
    __tablename__ = 'question_duplicates'
    
    id = Column(Integer, primary_key=True)
    question1_id = Column(Integer, ForeignKey('generated_questions.id'), nullable=False)
    question2_id = Column(Integer, ForeignKey('generated_questions.id'), nullable=False)
    
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    similarity_type = Column(String(20), nullable=False)  # text, semantic, concept
    detection_method = Column(String(50), nullable=False)  # ai, text_similarity, keyword_overlap
    
    status = Column(String(20), default='pending')  # pending, confirmed, dismissed
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    question1 = relationship('GeneratedQuestion', foreign_keys=[question1_id])
    question2 = relationship('GeneratedQuestion', foreign_keys=[question2_id])
    reviewer = relationship('User', backref='reviewed_duplicates')
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('question1_id', 'question2_id', name='unique_question_pair'),
        Index('idx_question_duplicates_similarity', 'similarity_score'),
        Index('idx_question_duplicates_status', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'question1_id': self.question1_id,
            'question2_id': self.question2_id,
            'similarity_score': self.similarity_score,
            'similarity_type': self.similarity_type,
            'detection_method': self.detection_method,
            'status': self.status,
            'reviewed_by': self.reviewed_by,
            'resolution_notes': self.resolution_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class QuestionBank(db.Model):
    """Question banks for organizing generated questions."""
    __tablename__ = 'question_banks'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Configuration
    auto_add_criteria = Column(JSON, default=dict)  # Criteria for auto-adding questions
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Statistics
    total_questions = Column(Integer, default=0)
    approved_questions = Column(Integer, default=0)
    avg_difficulty = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='question_banks')
    creator = relationship('User', backref='created_question_banks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'creator_id': self.creator_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'auto_add_criteria': self.auto_add_criteria,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'total_questions': self.total_questions,
            'approved_questions': self.approved_questions,
            'avg_difficulty': self.avg_difficulty,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class QuestionBankQuestion(db.Model):
    """Association between question banks and questions."""
    __tablename__ = 'question_bank_questions'
    
    id = Column(Integer, primary_key=True)
    question_bank_id = Column(Integer, ForeignKey('question_banks.id'), nullable=False)
    generated_question_id = Column(Integer, ForeignKey('generated_questions.id'), nullable=False)
    
    added_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    order = Column(Integer, nullable=True)
    tags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question_bank = relationship('QuestionBank', backref='bank_questions')
    generated_question = relationship('GeneratedQuestion', backref='bank_associations')
    added_by_user = relationship('User', backref='added_bank_questions')
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('question_bank_id', 'generated_question_id', name='unique_bank_question'),
        Index('idx_question_bank_questions_order', 'order'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_bank_id': self.question_bank_id,
            'generated_question_id': self.generated_question_id,
            'added_by': self.added_by,
            'order': self.order,
            'tags': self.tags,
            'created_at': self.created_at.isoformat()
        }


class GenerationAnalytics(db.Model):
    """Analytics for question generation performance."""
    __tablename__ = 'generation_analytics'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Generation metrics
    requests_created = Column(Integer, default=0)
    requests_completed = Column(Integer, default=0)
    requests_failed = Column(Integer, default=0)
    questions_generated = Column(Integer, default=0)
    questions_approved = Column(Integer, default=0)
    questions_rejected = Column(Integer, default=0)
    
    # Quality metrics
    avg_quality_score = Column(Float, nullable=True)
    avg_ai_confidence = Column(Float, nullable=True)
    duplicate_rate = Column(Float, nullable=True)
    
    # Performance metrics
    avg_generation_time = Column(Float, nullable=True)  # in seconds
    total_tokens_used = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Usage metrics
    questions_used_in_tests = Column(Integer, default=0)
    avg_question_performance = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='generation_analytics')
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'date', name='unique_tenant_date'),
        Index('idx_generation_analytics_date', 'date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'date': self.date.isoformat(),
            'requests_created': self.requests_created,
            'requests_completed': self.requests_completed,
            'requests_failed': self.requests_failed,
            'questions_generated': self.questions_generated,
            'questions_approved': self.questions_approved,
            'questions_rejected': self.questions_rejected,
            'avg_quality_score': self.avg_quality_score,
            'avg_ai_confidence': self.avg_ai_confidence,
            'duplicate_rate': self.duplicate_rate,
            'avg_generation_time': self.avg_generation_time,
            'total_tokens_used': self.total_tokens_used,
            'total_cost': self.total_cost,
            'questions_used_in_tests': self.questions_used_in_tests,
            'avg_question_performance': self.avg_question_performance,
            'created_at': self.created_at.isoformat()
        }