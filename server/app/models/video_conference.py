"""Video Conference models module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.extensions import db


class VideoConferenceProvider(PyEnum):
    """Video conference provider enum."""
    ZOOM = "zoom"
    GOOGLE_MEET = "google_meet"
    MICROSOFT_TEAMS = "microsoft_teams"
    WEBRTC = "webrtc"


class VideoConferenceStatus(PyEnum):
    """Video conference status enum."""
    SCHEDULED = "scheduled"
    STARTED = "started"
    ENDED = "ended"
    CANCELLED = "cancelled"


class RecordingStatus(PyEnum):
    """Recording status enum."""
    NOT_STARTED = "not_started"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoConference(db.Model):
    """Video Conference model."""
    __tablename__ = 'video_conferences'
    
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id', ondelete='CASCADE'), nullable=False)
    host_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Conference details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    provider = Column(Enum(VideoConferenceProvider), nullable=False, default=VideoConferenceProvider.ZOOM)
    status = Column(Enum(VideoConferenceStatus), nullable=False, default=VideoConferenceStatus.SCHEDULED)
    
    # Meeting identifiers
    meeting_id = Column(String(255), nullable=True)  # Provider-specific meeting ID
    meeting_url = Column(String(500), nullable=True)  # Join URL
    meeting_password = Column(String(100), nullable=True)  # Meeting password
    
    # Scheduling
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=True)  # Planned duration
    actual_duration_minutes = Column(Integer, nullable=True)  # Actual duration
    
    # Meeting settings
    waiting_room_enabled = Column(Boolean, default=True)
    require_authentication = Column(Boolean, default=False)
    allow_recording = Column(Boolean, default=True)
    auto_record = Column(Boolean, default=False)
    
    # Provider-specific settings
    provider_settings = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    appointment = relationship('Appointment', backref='video_conference', lazy='select')
    host = relationship('User', backref='hosted_conferences', lazy='select')
    participants = relationship('VideoConferenceParticipant', back_populates='conference', cascade='all, delete-orphan')
    recordings = relationship('VideoConferenceRecording', back_populates='conference', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Return a dict representation of the video conference."""
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'host_id': self.host_id,
            'title': self.title,
            'description': self.description,
            'provider': self.provider.value,
            'status': self.status.value,
            'meeting_id': self.meeting_id,
            'meeting_url': self.meeting_url,
            'meeting_password': self.meeting_password,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'actual_duration_minutes': self.actual_duration_minutes,
            'waiting_room_enabled': self.waiting_room_enabled,
            'require_authentication': self.require_authentication,
            'allow_recording': self.allow_recording,
            'auto_record': self.auto_record,
            'provider_settings': self.provider_settings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'host': {
                'id': self.host.id,
                'first_name': self.host.first_name,
                'last_name': self.host.last_name,
                'email': self.host.email
            } if self.host else None,
            'participants': [p.to_dict() for p in self.participants],
            'recordings': [r.to_dict() for r in self.recordings]
        }
    
    def __repr__(self):
        """String representation of the video conference."""
        return f'<VideoConference {self.id} {self.title}>'


class VideoConferenceParticipant(db.Model):
    """Video Conference Participant model."""
    __tablename__ = 'video_conference_participants'
    
    id = Column(Integer, primary_key=True)
    conference_id = Column(Integer, ForeignKey('video_conferences.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)  # Nullable for guest participants
    
    # Participant details
    email = Column(String(255), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False, default='participant')  # 'host', 'co_host', 'participant'
    
    # Join details
    joined_at = Column(DateTime, nullable=True)
    left_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Status
    invitation_sent = Column(Boolean, default=False)
    invitation_sent_at = Column(DateTime, nullable=True)
    has_joined = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship('VideoConference', back_populates='participants')
    user = relationship('User', backref='conference_participations', lazy='select')
    
    def to_dict(self):
        """Return a dict representation of the participant."""
        return {
            'id': self.id,
            'conference_id': self.conference_id,
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'left_at': self.left_at.isoformat() if self.left_at else None,
            'duration_minutes': self.duration_minutes,
            'invitation_sent': self.invitation_sent,
            'invitation_sent_at': self.invitation_sent_at.isoformat() if self.invitation_sent_at else None,
            'has_joined': self.has_joined,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user': {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email
            } if self.user else None
        }
    
    def __repr__(self):
        """String representation of the participant."""
        return f'<VideoConferenceParticipant {self.id} {self.name}>'


class VideoConferenceRecording(db.Model):
    """Video Conference Recording model."""
    __tablename__ = 'video_conference_recordings'
    
    id = Column(Integer, primary_key=True)
    conference_id = Column(Integer, ForeignKey('video_conferences.id', ondelete='CASCADE'), nullable=False)
    
    # Recording details
    title = Column(String(200), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Storage details
    storage_provider = Column(String(50), nullable=True)  # 'local', 's3', 'provider'
    storage_path = Column(String(500), nullable=True)  # Local path or cloud URL
    download_url = Column(String(500), nullable=True)  # Download URL
    
    # Provider details
    provider_recording_id = Column(String(255), nullable=True)  # Provider-specific recording ID
    provider_download_url = Column(String(500), nullable=True)  # Provider download URL
    
    # Status and processing
    status = Column(Enum(RecordingStatus), nullable=False, default=RecordingStatus.NOT_STARTED)
    processing_progress = Column(Integer, default=0)  # 0-100%
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Access control
    is_public = Column(Boolean, default=False)
    password_protected = Column(Boolean, default=False)
    access_password = Column(String(100), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Transcription
    has_transcription = Column(Boolean, default=False)
    transcription_text = Column(Text, nullable=True)
    transcription_file_path = Column(String(500), nullable=True)
    
    # Relationships
    conference = relationship('VideoConference', back_populates='recordings')
    
    def to_dict(self):
        """Return a dict representation of the recording."""
        return {
            'id': self.id,
            'conference_id': self.conference_id,
            'title': self.title,
            'file_name': self.file_name,
            'file_size_bytes': self.file_size_bytes,
            'duration_minutes': self.duration_minutes,
            'storage_provider': self.storage_provider,
            'storage_path': self.storage_path,
            'download_url': self.download_url,
            'provider_recording_id': self.provider_recording_id,
            'provider_download_url': self.provider_download_url,
            'status': self.status.value,
            'processing_progress': self.processing_progress,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_public': self.is_public,
            'password_protected': self.password_protected,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'has_transcription': self.has_transcription
        }
    
    def __repr__(self):
        """String representation of the recording."""
        return f'<VideoConferenceRecording {self.id} {self.title}>'


class VideoConferenceInvitation(db.Model):
    """Video Conference Invitation model."""
    __tablename__ = 'video_conference_invitations'
    
    id = Column(Integer, primary_key=True)
    conference_id = Column(Integer, ForeignKey('video_conferences.id', ondelete='CASCADE'), nullable=False)
    
    # Invitation details
    email = Column(String(255), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False, default='participant')
    
    # Status
    status = Column(String(20), nullable=False, default='pending')  # 'pending', 'sent', 'delivered', 'failed'
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Invitation content
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=True)
    
    # Delivery method
    delivery_method = Column(String(20), nullable=False, default='email')  # 'email', 'sms', 'both'
    phone_number = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship('VideoConference', backref='invitations', lazy='select')
    
    def to_dict(self):
        """Return a dict representation of the invitation."""
        return {
            'id': self.id,
            'conference_id': self.conference_id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'subject': self.subject,
            'message': self.message,
            'delivery_method': self.delivery_method,
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the invitation."""
        return f'<VideoConferenceInvitation {self.id} {self.email}>'


class VideoConferenceAnalytics(db.Model):
    """Video Conference Analytics model."""
    __tablename__ = 'video_conference_analytics'
    
    id = Column(Integer, primary_key=True)
    conference_id = Column(Integer, ForeignKey('video_conferences.id', ondelete='CASCADE'), nullable=False)
    
    # Attendance metrics
    total_participants = Column(Integer, default=0)
    max_concurrent_participants = Column(Integer, default=0)
    average_duration_minutes = Column(Integer, default=0)
    
    # Engagement metrics
    total_chat_messages = Column(Integer, default=0)
    screen_share_duration_minutes = Column(Integer, default=0)
    questions_asked = Column(Integer, default=0)
    
    # Quality metrics
    average_audio_quality = Column(Integer, default=0)  # 1-5 scale
    average_video_quality = Column(Integer, default=0)  # 1-5 scale
    connection_issues_count = Column(Integer, default=0)
    
    # Technical metrics
    bandwidth_usage_mb = Column(Integer, default=0)
    cpu_usage_percent = Column(Integer, default=0)
    memory_usage_mb = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = relationship('VideoConference', backref='analytics', lazy='select')
    
    def to_dict(self):
        """Return a dict representation of the analytics."""
        return {
            'id': self.id,
            'conference_id': self.conference_id,
            'total_participants': self.total_participants,
            'max_concurrent_participants': self.max_concurrent_participants,
            'average_duration_minutes': self.average_duration_minutes,
            'total_chat_messages': self.total_chat_messages,
            'screen_share_duration_minutes': self.screen_share_duration_minutes,
            'questions_asked': self.questions_asked,
            'average_audio_quality': self.average_audio_quality,
            'average_video_quality': self.average_video_quality,
            'connection_issues_count': self.connection_issues_count,
            'bandwidth_usage_mb': self.bandwidth_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the analytics."""
        return f'<VideoConferenceAnalytics {self.id} Conference:{self.conference_id}>'