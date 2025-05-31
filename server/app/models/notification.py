"""Notification model module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.extensions import db


class Notification(db.Model):
    """Notification model for user notifications."""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default='info')  # 'appointment', 'message', 'system', etc.
    link = Column(String(255), nullable=True)
    
    # Additional data
    data = Column(JSON, nullable=True)  # JSON data for the notification
    related_id = Column(Integer, nullable=True)  # ID of the related entity
    related_type = Column(String(50), nullable=True)  # Type of the related entity
    priority = Column(String(20), nullable=False, default='normal')  # 'low', 'normal', 'high', 'urgent'
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # Status
    read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='notifications')
    sender = relationship('User', foreign_keys=[sender_id], backref='sent_notifications')
    tenant = relationship('Tenant', backref='notifications')
    
    def to_dict(self):
        """Return a dict representation of the notification."""
        sender_info = None
        if self.sender:
            sender_info = {
                'id': self.sender.id,
                'name': f"{self.sender.first_name} {self.sender.last_name}",
                'email': self.sender.email
            }
            
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sender_id': self.sender_id,
            'sender': sender_info,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'link': self.link,
            'data': self.data,
            'related_id': self.related_id,
            'related_type': self.related_type,
            'priority': self.priority,
            'tenant_id': self.tenant_id,
            'read': self.read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def mark_as_read(self):
        """Mark the notification as read."""
        self.read = True
        self.read_at = datetime.utcnow()
        # Note: db.session.commit() should be called by the service layer, not the model
    
    def __repr__(self):
        """String representation of the notification."""
        return f'<Notification {self.id}: {self.title}>'


class MessageThread(db.Model):
    """Message thread model for conversations."""
    __tablename__ = 'message_threads'
    
    id = Column(Integer, primary_key=True)
    subject = Column(String(100), nullable=True)
    
    # Status
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship('Message', backref='thread', lazy='dynamic')
    participants = relationship('ThreadParticipant', backref='thread', lazy='dynamic')
    
    def to_dict(self):
        """Return a dict representation of the message thread."""
        return {
            'id': self.id,
            'subject': self.subject,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the message thread."""
        return f'<MessageThread {self.id}: {self.subject}>'


class ThreadParticipant(db.Model):
    """Thread participant model for message threads."""
    __tablename__ = 'thread_participants'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey('message_threads.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Status
    is_muted = Column(Boolean, default=False)
    last_read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='thread_participations')
    
    def to_dict(self):
        """Return a dict representation of the thread participant."""
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'user_id': self.user_id,
            'is_muted': self.is_muted,
            'last_read_at': self.last_read_at.isoformat() if self.last_read_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Message(db.Model):
    """Message model for user-to-user messages."""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey('message_threads.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    content = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = relationship('User', backref='sent_messages')
    read_receipts = relationship('ReadReceipt', backref='message', lazy='dynamic')
    
    def to_dict(self):
        """Return a dict representation of the message."""
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'sender_id': self.sender_id,
            'content': self.content,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the message."""
        return f'<Message {self.id} from {self.sender_id}>'


class ReadReceipt(db.Model):
    """Read receipt model for tracking message reads."""
    __tablename__ = 'read_receipts'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    read_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='read_receipts')
    
    def to_dict(self):
        """Return a dict representation of the read receipt."""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'read_at': self.read_at.isoformat()
        }