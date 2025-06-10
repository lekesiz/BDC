"""Source content model for AI question generation."""

from datetime import datetime
from app.extensions import db


class SourceContent(db.Model):
    """Model for storing source content used in AI question generation."""
    __tablename__ = 'source_content'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), default='text')  # text, pdf, document, etc.
    source_url = db.Column(db.String(500))
    
    # Metadata
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    language = db.Column(db.String(10), default='en')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    question_generation_requests = db.relationship(
        'QuestionGenerationRequest', 
        back_populates='source_content',
        lazy='dynamic'
    )
    
    def to_dict(self):
        """Convert source content to dictionary."""
        return {
            'id': self.id,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'content_type': self.content_type,
            'source_url': self.source_url,
            'title': self.title,
            'description': self.description,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }