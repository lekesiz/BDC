"""Chat conversation models for AI chatbot."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
import enum

from app.extensions import db


class ConversationStatus(enum.Enum):
    """Conversation status enum."""
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"
    FLAGGED = "flagged"  # For moderation


class MessageRole(enum.Enum):
    """Message role enum."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatConversation(db.Model):
    """Chat conversation model for storing chat sessions."""
    __tablename__ = 'chat_conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # Conversation metadata
    title = Column(String(200), nullable=True)
    language = Column(String(10), default='en')  # 'en' or 'tr'
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    
    # Context and purpose
    context_type = Column(String(50), nullable=True)  # 'education', 'appointment', 'progress', 'general'
    related_entity_type = Column(String(50), nullable=True)  # 'appointment', 'assessment', 'program'
    related_entity_id = Column(Integer, nullable=True)
    
    # AI settings for this conversation
    model = Column(String(50), default='gpt-4')
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    
    # Summary and insights
    summary = Column(Text, nullable=True)
    key_topics = Column(JSON, nullable=True)  # List of identified topics
    sentiment_score = Column(Float, nullable=True)  # Overall sentiment
    
    # Moderation
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)
    flagged_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    flagged_at = Column(DateTime, nullable=True)
    
    # Rate limiting
    message_count = Column(Integer, default=0)
    last_message_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='chat_conversations')
    beneficiary = relationship('Beneficiary', backref='chat_conversations')
    tenant = relationship('Tenant', backref='chat_conversations')
    messages = relationship('ChatMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    flagger = relationship('User', foreign_keys=[flagged_by])
    
    def to_dict(self, include_messages=False):
        """Convert conversation to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'beneficiary_id': self.beneficiary_id,
            'tenant_id': self.tenant_id,
            'title': self.title,
            'language': self.language,
            'status': self.status.value if self.status else None,
            'context_type': self.context_type,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'summary': self.summary,
            'key_topics': self.key_topics,
            'sentiment_score': self.sentiment_score,
            'is_flagged': self.is_flagged,
            'flag_reason': self.flag_reason,
            'flagged_by': self.flagged_by,
            'flagged_at': self.flagged_at.isoformat() if self.flagged_at else None,
            'message_count': self.message_count,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
        }
        
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages.order_by(ChatMessage.created_at)]
            
        return data
    
    def __repr__(self):
        return f'<ChatConversation {self.id}: {self.title or "Untitled"}>'


class ChatMessage(db.Model):
    """Individual chat message model."""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('chat_conversations.id'), nullable=False)
    
    # Message content
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Token usage
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    # Additional metadata
    extra_data = Column(JSON, nullable=True)  # Store function calls, tool uses, etc.
    
    # Error tracking
    is_error = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role.value if self.role else None,
            'content': self.content,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'extra_data': self.extra_data,
            'is_error': self.is_error,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.role.value if self.role else "Unknown"}>'


class ChatRateLimit(db.Model):
    """Rate limiting for chat conversations per user."""
    __tablename__ = 'chat_rate_limits'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Daily limits
    daily_message_count = Column(Integer, default=0)
    daily_token_count = Column(Integer, default=0)
    daily_reset_at = Column(DateTime, nullable=True)
    
    # Monthly limits
    monthly_message_count = Column(Integer, default=0)
    monthly_token_count = Column(Integer, default=0)
    monthly_reset_at = Column(DateTime, nullable=True)
    
    # Custom limits (can override defaults)
    max_daily_messages = Column(Integer, nullable=True)
    max_daily_tokens = Column(Integer, nullable=True)
    max_monthly_messages = Column(Integer, nullable=True)
    max_monthly_tokens = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='chat_rate_limit', uselist=False)
    
    def to_dict(self):
        """Convert rate limit to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'daily_message_count': self.daily_message_count,
            'daily_token_count': self.daily_token_count,
            'daily_reset_at': self.daily_reset_at.isoformat() if self.daily_reset_at else None,
            'monthly_message_count': self.monthly_message_count,
            'monthly_token_count': self.monthly_token_count,
            'monthly_reset_at': self.monthly_reset_at.isoformat() if self.monthly_reset_at else None,
            'max_daily_messages': self.max_daily_messages,
            'max_daily_tokens': self.max_daily_tokens,
            'max_monthly_messages': self.max_monthly_messages,
            'max_monthly_tokens': self.max_monthly_tokens,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ChatRateLimit {self.id}: User {self.user_id}>'


class ConversationTemplate(db.Model):
    """Pre-defined conversation templates for common scenarios."""
    __tablename__ = 'conversation_templates'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # Template info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # 'education', 'appointment', 'onboarding'
    language = Column(String(10), default='en')
    
    # Initial messages
    system_prompt = Column(Text, nullable=False)
    welcome_message = Column(Text, nullable=False)
    suggested_questions = Column(JSON, nullable=True)  # List of suggested user questions
    
    # Settings
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # For ordering
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='conversation_templates')
    
    def to_dict(self):
        """Convert template to dictionary."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'language': self.language,
            'system_prompt': self.system_prompt,
            'welcome_message': self.welcome_message,
            'suggested_questions': self.suggested_questions,
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ConversationTemplate {self.id}: {self.name}>'