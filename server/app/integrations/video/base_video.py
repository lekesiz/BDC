"""
Base video conferencing integration functionality.
"""

from abc import abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..base import BaseIntegration, IntegrationConfig


class MeetingType(Enum):
    """Video meeting types."""
    INSTANT = "instant"
    SCHEDULED = "scheduled"
    RECURRING = "recurring"
    WEBINAR = "webinar"


class MeetingStatus(Enum):
    """Video meeting status."""
    WAITING = "waiting"
    STARTED = "started"
    ENDED = "ended"
    CANCELLED = "cancelled"


class ParticipantRole(Enum):
    """Participant roles."""
    HOST = "host"
    CO_HOST = "co_host"
    ATTENDEE = "attendee"
    PRESENTER = "presenter"


@dataclass
class Participant:
    """Represents a meeting participant."""
    id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    role: ParticipantRole = ParticipantRole.ATTENDEE
    join_time: Optional[datetime] = None
    leave_time: Optional[datetime] = None
    duration: Optional[int] = None  # in seconds
    camera_on: bool = True
    microphone_on: bool = True


@dataclass
class RecordingInfo:
    """Information about meeting recordings."""
    id: str
    meeting_id: str
    recording_start: datetime
    recording_end: datetime
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    play_url: Optional[str] = None
    file_type: Optional[str] = None
    status: Optional[str] = None


@dataclass
class VideoMeetingInput:
    """Input data for creating/updating video meetings."""
    topic: str
    start_time: Optional[datetime] = None
    duration: int = 60  # in minutes
    timezone: Optional[str] = None
    password: Optional[str] = None
    waiting_room: bool = True
    join_before_host: bool = False
    mute_participants: bool = False
    auto_recording: Optional[str] = None  # "cloud", "local", "none"
    meeting_type: MeetingType = MeetingType.SCHEDULED
    participants: Optional[List[str]] = None  # email addresses
    agenda: Optional[str] = None
    alternative_hosts: Optional[List[str]] = None
    recurrence: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.alternative_hosts is None:
            self.alternative_hosts = []


@dataclass
class VideoMeeting:
    """Represents a video meeting."""
    id: str
    topic: str
    host_id: str
    host_email: Optional[str] = None
    start_time: Optional[datetime] = None
    duration: int = 60
    timezone: Optional[str] = None
    status: MeetingStatus = MeetingStatus.WAITING
    join_url: Optional[str] = None
    start_url: Optional[str] = None
    password: Optional[str] = None
    meeting_type: MeetingType = MeetingType.SCHEDULED
    participants: Optional[List[Participant]] = None
    agenda: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    recordings: Optional[List[RecordingInfo]] = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.settings is None:
            self.settings = {}
        if self.recordings is None:
            self.recordings = []


class BaseVideoIntegration(BaseIntegration):
    """Base class for video conferencing integrations."""
    
    @property
    def integration_type(self) -> str:
        return "video"
    
    @abstractmethod
    async def create_meeting(self, meeting_data: VideoMeetingInput) -> VideoMeeting:
        """Create a new video meeting."""
        pass
    
    @abstractmethod
    async def get_meeting(self, meeting_id: str) -> Optional[VideoMeeting]:
        """Get meeting details by ID."""
        pass
    
    @abstractmethod
    async def update_meeting(self, meeting_id: str, meeting_data: VideoMeetingInput) -> VideoMeeting:
        """Update an existing meeting."""
        pass
    
    @abstractmethod
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting."""
        pass
    
    @abstractmethod
    async def list_meetings(
        self,
        user_id: Optional[str] = None,
        meeting_type: Optional[MeetingType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 30
    ) -> List[VideoMeeting]:
        """List meetings with optional filters."""
        pass
    
    @abstractmethod
    async def start_meeting(self, meeting_id: str) -> bool:
        """Start a meeting."""
        pass
    
    @abstractmethod
    async def end_meeting(self, meeting_id: str) -> bool:
        """End a meeting."""
        pass
    
    @abstractmethod
    async def get_meeting_participants(self, meeting_id: str) -> List[Participant]:
        """Get current participants in a meeting."""
        pass
    
    @abstractmethod
    async def add_participant(self, meeting_id: str, email: str, name: Optional[str] = None) -> bool:
        """Add a participant to a meeting."""
        pass
    
    @abstractmethod
    async def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Remove a participant from a meeting."""
        pass
    
    @abstractmethod
    async def mute_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Mute a participant."""
        pass
    
    @abstractmethod
    async def unmute_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Unmute a participant."""
        pass
    
    @abstractmethod
    async def start_recording(self, meeting_id: str, record_type: str = "cloud") -> bool:
        """Start recording a meeting."""
        pass
    
    @abstractmethod
    async def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording a meeting."""
        pass
    
    @abstractmethod
    async def get_recordings(self, meeting_id: str) -> List[RecordingInfo]:
        """Get recordings for a meeting."""
        pass
    
    @abstractmethod
    async def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording."""
        pass
    
    async def generate_join_url(
        self,
        meeting_id: str,
        participant_name: Optional[str] = None,
        password: Optional[str] = None
    ) -> str:
        """Generate a join URL for a participant."""
        # Default implementation - can be overridden
        meeting = await self.get_meeting(meeting_id)
        if not meeting or not meeting.join_url:
            raise ValueError(f"Meeting {meeting_id} not found or has no join URL")
        
        join_url = meeting.join_url
        
        # Add participant name and password as query parameters if needed
        params = []
        if participant_name:
            params.append(f"uname={participant_name}")
        if password:
            params.append(f"pwd={password}")
        
        if params:
            separator = "&" if "?" in join_url else "?"
            join_url += separator + "&".join(params)
        
        return join_url
    
    async def create_instant_meeting(
        self,
        topic: str,
        host_email: Optional[str] = None
    ) -> VideoMeeting:
        """Create an instant meeting that starts immediately."""
        meeting_data = VideoMeetingInput(
            topic=topic,
            start_time=datetime.now(),
            meeting_type=MeetingType.INSTANT,
            duration=60
        )
        
        return await self.create_meeting(meeting_data)
    
    async def schedule_recurring_meeting(
        self,
        topic: str,
        start_time: datetime,
        duration: int,
        recurrence_pattern: Dict[str, Any],
        participants: Optional[List[str]] = None
    ) -> VideoMeeting:
        """Schedule a recurring meeting."""
        meeting_data = VideoMeetingInput(
            topic=topic,
            start_time=start_time,
            duration=duration,
            meeting_type=MeetingType.RECURRING,
            participants=participants or [],
            recurrence=recurrence_pattern
        )
        
        return await self.create_meeting(meeting_data)
    
    def _parse_recurrence_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Parse recurrence pattern into provider-specific format."""
        # Default implementation - should be overridden by providers
        return pattern
    
    async def get_meeting_analytics(self, meeting_id: str) -> Dict[str, Any]:
        """Get analytics for a meeting."""
        meeting = await self.get_meeting(meeting_id)
        if not meeting:
            return {}
        
        participants = meeting.participants or []
        
        analytics = {
            'meeting_id': meeting_id,
            'topic': meeting.topic,
            'duration_scheduled': meeting.duration,
            'participants_count': len(participants),
            'participants_joined': len([p for p in participants if p.join_time]),
            'average_duration': 0,
            'camera_usage': 0,
            'microphone_usage': 0
        }
        
        if participants:
            joined_participants = [p for p in participants if p.duration]
            if joined_participants:
                analytics['average_duration'] = sum(p.duration for p in joined_participants) / len(joined_participants)
            
            analytics['camera_usage'] = len([p for p in participants if p.camera_on]) / len(participants) * 100
            analytics['microphone_usage'] = len([p for p in participants if p.microphone_on]) / len(participants) * 100
        
        return analytics
    
    async def send_meeting_invitation(
        self,
        meeting_id: str,
        recipients: List[str],
        message: Optional[str] = None
    ) -> bool:
        """Send meeting invitation to participants."""
        # Default implementation - can be overridden
        # This would typically integrate with email service
        meeting = await self.get_meeting(meeting_id)
        if not meeting:
            return False
        
        # Log invitation details
        self.logger.info(f"Sending invitation for meeting {meeting_id} to {len(recipients)} recipients")
        
        return True