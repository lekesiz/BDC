"""
Zoom video conferencing integration.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

try:
    import aiohttp
    import jwt
    ZOOM_DEPS_AVAILABLE = True
except ImportError:
    ZOOM_DEPS_AVAILABLE = False

from ..base import OAuth2Integration, IntegrationConfig, ServiceUnavailableError, AuthenticationError
from ..registry import register_integration
from .base_video import (
    BaseVideoIntegration, VideoMeeting, VideoMeetingInput, Participant, RecordingInfo,
    MeetingType, MeetingStatus, ParticipantRole
)

logger = logging.getLogger(__name__)


@register_integration('zoom')
class ZoomIntegration(BaseVideoIntegration, OAuth2Integration):
    """Zoom video conferencing integration."""
    
    BASE_URL = 'https://api.zoom.us/v2'
    AUTH_URL = 'https://zoom.us/oauth/authorize'
    TOKEN_URL = 'https://zoom.us/oauth/token'
    
    SCOPES = [
        'meeting:write',
        'meeting:read',
        'webinar:write',
        'webinar:read',
        'recording:write',
        'recording:read',
        'user:read'
    ]
    
    def __init__(self, config: IntegrationConfig):
        if not ZOOM_DEPS_AVAILABLE:
            raise ImportError("Zoom dependencies not available. Install aiohttp PyJWT")
        
        super().__init__(config)
        self._session = None
        
    @property
    def provider_name(self) -> str:
        return "zoom"
    
    async def get_authorization_url(self, state: str = None) -> str:
        """Get OAuth2 authorization URL for Zoom."""
        params = {
            'response_type': 'code',
            'client_id': self.config.credentials['client_id'],
            'redirect_uri': self.config.credentials['redirect_uri'],
            'scope': ' '.join(self.SCOPES)
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.config.credentials['redirect_uri'],
            'client_id': self.config.credentials['client_id'],
            'client_secret': self.config.credentials['client_secret']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.TOKEN_URL, data=data) as response:
                if response.status != 200:
                    text = await response.text()
                    raise AuthenticationError(f"Token exchange failed: {text}", "video")
                
                token_data = await response.json()
                
                tokens = {
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in'),
                    'scope': token_data.get('scope')
                }
                
                # Update config with tokens
                self.config.credentials.update(tokens)
                
                return tokens
    
    async def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token."""
        if not self.refresh_token:
            return False
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.config.credentials['client_id'],
            'client_secret': self.config.credentials['client_secret']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.TOKEN_URL, data=data) as response:
                    if response.status != 200:
                        return False
                    
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    self.config.credentials['access_token'] = token_data['access_token']
                    
                    if 'refresh_token' in token_data:
                        self.refresh_token = token_data['refresh_token']
                        self.config.credentials['refresh_token'] = token_data['refresh_token']
                    
                    return True
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return False
    
    async def connect(self) -> bool:
        """Connect to Zoom API."""
        try:
            if not self.access_token:
                return False
            
            self._session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Zoom: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Zoom API."""
        if self._session:
            await self._session.close()
            self._session = None
        return True
    
    async def test_connection(self) -> bool:
        """Test Zoom connection."""
        try:
            if not self._session:
                return False
            
            async with self._session.get(f"{self.BASE_URL}/users/me") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def create_meeting(self, meeting_data: VideoMeetingInput) -> VideoMeeting:
        """Create a new Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            zoom_meeting_data = self._convert_to_zoom_meeting(meeting_data)
            
            async with self._session.post(
                f"{self.BASE_URL}/users/me/meetings",
                json=zoom_meeting_data
            ) as response:
                if response.status not in [200, 201]:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to create Zoom meeting: {text}", "video")
                
                result = await response.json()
                return self._convert_from_zoom_meeting(result)
                
        except Exception as e:
            logger.error(f"Failed to create Zoom meeting: {e}")
            raise ServiceUnavailableError(f"Failed to create meeting: {e}", "video")
    
    async def get_meeting(self, meeting_id: str) -> Optional[VideoMeeting]:
        """Get Zoom meeting by ID."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.get(f"{self.BASE_URL}/meetings/{meeting_id}") as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get Zoom meeting: {text}", "video")
                
                result = await response.json()
                return self._convert_from_zoom_meeting(result)
                
        except Exception as e:
            logger.error(f"Failed to get Zoom meeting: {e}")
            raise ServiceUnavailableError(f"Failed to get meeting: {e}", "video")
    
    async def update_meeting(self, meeting_id: str, meeting_data: VideoMeetingInput) -> VideoMeeting:
        """Update Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            zoom_meeting_data = self._convert_to_zoom_meeting(meeting_data)
            
            async with self._session.patch(
                f"{self.BASE_URL}/meetings/{meeting_id}",
                json=zoom_meeting_data
            ) as response:
                if response.status not in [200, 204]:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to update Zoom meeting: {text}", "video")
                
                # Get updated meeting
                return await self.get_meeting(meeting_id)
                
        except Exception as e:
            logger.error(f"Failed to update Zoom meeting: {e}")
            raise ServiceUnavailableError(f"Failed to update meeting: {e}", "video")
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.delete(f"{self.BASE_URL}/meetings/{meeting_id}") as response:
                return response.status in [200, 204, 404]  # 404 means already deleted
        except Exception as e:
            logger.error(f"Failed to delete Zoom meeting: {e}")
            return False
    
    async def list_meetings(
        self,
        user_id: Optional[str] = None,
        meeting_type: Optional[MeetingType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 30
    ) -> List[VideoMeeting]:
        """List Zoom meetings."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            user_endpoint = user_id or 'me'
            params = {'page_size': page_size}
            
            if meeting_type:
                zoom_type = self._convert_to_zoom_meeting_type(meeting_type)
                params['type'] = zoom_type
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.BASE_URL}/users/{user_endpoint}/meetings?{query_string}"
            
            async with self._session.get(url) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to list Zoom meetings: {text}", "video")
                
                data = await response.json()
                meetings = []
                
                for meeting_data in data.get('meetings', []):
                    meeting = self._convert_from_zoom_meeting(meeting_data)
                    
                    # Apply time filters
                    if start_time and meeting.start_time and meeting.start_time < start_time:
                        continue
                    if end_time and meeting.start_time and meeting.start_time > end_time:
                        continue
                    
                    meetings.append(meeting)
                
                return meetings
                
        except Exception as e:
            logger.error(f"Failed to list Zoom meetings: {e}")
            raise ServiceUnavailableError(f"Failed to list meetings: {e}", "video")
    
    async def start_meeting(self, meeting_id: str) -> bool:
        """Start Zoom meeting (Zoom doesn't have explicit start API)."""
        # Zoom meetings start automatically when host joins
        # We can update the status to indicate it should be started
        try:
            async with self._session.patch(
                f"{self.BASE_URL}/meetings/{meeting_id}/status",
                json={'action': 'start'}
            ) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"Failed to start Zoom meeting: {e}")
            return False
    
    async def end_meeting(self, meeting_id: str) -> bool:
        """End Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.patch(
                f"{self.BASE_URL}/meetings/{meeting_id}/status",
                json={'action': 'end'}
            ) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"Failed to end Zoom meeting: {e}")
            return False
    
    async def get_meeting_participants(self, meeting_id: str) -> List[Participant]:
        """Get Zoom meeting participants."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.get(
                f"{self.BASE_URL}/metrics/meetings/{meeting_id}/participants"
            ) as response:
                if response.status == 404:
                    return []
                elif response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get participants: {text}", "video")
                
                data = await response.json()
                participants = []
                
                for participant_data in data.get('participants', []):
                    participant = self._convert_from_zoom_participant(participant_data)
                    participants.append(participant)
                
                return participants
                
        except Exception as e:
            logger.error(f"Failed to get Zoom meeting participants: {e}")
            return []
    
    async def add_participant(self, meeting_id: str, email: str, name: Optional[str] = None) -> bool:
        """Add participant to Zoom meeting."""
        # Zoom doesn't have direct API to add participants during meeting
        # This would typically be done through meeting invite
        return True
    
    async def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Remove participant from Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.patch(
                f"{self.BASE_URL}/meetings/{meeting_id}/events",
                json={
                    'method': 'meeting.participant_left',
                    'participant': {'id': participant_id}
                }
            ) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"Failed to remove participant: {e}")
            return False
    
    async def mute_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Mute participant in Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.patch(
                f"{self.BASE_URL}/meetings/{meeting_id}/events",
                json={
                    'method': 'meeting.participant_audio_muted',
                    'participant': {'id': participant_id}
                }
            ) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"Failed to mute participant: {e}")
            return False
    
    async def unmute_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Unmute participant in Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.patch(
                f"{self.BASE_URL}/meetings/{meeting_id}/events",
                json={
                    'method': 'meeting.participant_audio_unmuted',
                    'participant': {'id': participant_id}
                }
            ) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"Failed to unmute participant: {e}")
            return False
    
    async def start_recording(self, meeting_id: str, record_type: str = "cloud") -> bool:
        """Start recording Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.patch(
                f"{self.BASE_URL}/meetings/{meeting_id}/recordings/status",
                json={
                    'action': 'start',
                    'recording_type': record_type
                }
            ) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    async def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.patch(
                f"{self.BASE_URL}/meetings/{meeting_id}/recordings/status",
                json={'action': 'stop'}
            ) as response:
                return response.status in [200, 204]
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False
    
    async def get_recordings(self, meeting_id: str) -> List[RecordingInfo]:
        """Get recordings for Zoom meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            async with self._session.get(f"{self.BASE_URL}/meetings/{meeting_id}/recordings") as response:
                if response.status == 404:
                    return []
                elif response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get recordings: {text}", "video")
                
                data = await response.json()
                recordings = []
                
                for recording_data in data.get('recording_files', []):
                    recording = self._convert_from_zoom_recording(recording_data, meeting_id)
                    recordings.append(recording)
                
                return recordings
                
        except Exception as e:
            logger.error(f"Failed to get Zoom recordings: {e}")
            return []
    
    async def delete_recording(self, recording_id: str) -> bool:
        """Delete Zoom recording."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Zoom", "video")
        
        try:
            # Note: Zoom API uses meeting ID to delete recordings, not recording ID
            # This is a limitation of Zoom's API structure
            async with self._session.delete(f"{self.BASE_URL}/meetings/{recording_id}/recordings") as response:
                return response.status in [200, 204, 404]
        except Exception as e:
            logger.error(f"Failed to delete recording: {e}")
            return False
    
    def _convert_to_zoom_meeting(self, meeting_data: VideoMeetingInput) -> Dict[str, Any]:
        """Convert VideoMeetingInput to Zoom meeting format."""
        zoom_meeting = {
            'topic': meeting_data.topic,
            'type': self._convert_to_zoom_meeting_type(meeting_data.meeting_type),
            'duration': meeting_data.duration,
            'timezone': meeting_data.timezone or 'UTC',
            'agenda': meeting_data.agenda or '',
            'settings': {
                'waiting_room': meeting_data.waiting_room,
                'join_before_host': meeting_data.join_before_host,
                'mute_upon_entry': meeting_data.mute_participants,
                'auto_recording': meeting_data.auto_recording or 'none'
            }
        }
        
        if meeting_data.start_time:
            zoom_meeting['start_time'] = meeting_data.start_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        if meeting_data.password:
            zoom_meeting['password'] = meeting_data.password
        
        if meeting_data.recurrence:
            zoom_meeting['recurrence'] = self._parse_recurrence_pattern(meeting_data.recurrence)
        
        return zoom_meeting
    
    def _convert_from_zoom_meeting(self, zoom_meeting: Dict[str, Any]) -> VideoMeeting:
        """Convert Zoom meeting to VideoMeeting."""
        # Parse start time
        start_time = None
        if zoom_meeting.get('start_time'):
            try:
                start_time = datetime.fromisoformat(zoom_meeting['start_time'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Parse created time
        created_at = None
        if zoom_meeting.get('created_at'):
            try:
                created_at = datetime.fromisoformat(zoom_meeting['created_at'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Parse status
        status = MeetingStatus.WAITING
        if zoom_meeting.get('status') == 'started':
            status = MeetingStatus.STARTED
        elif zoom_meeting.get('status') == 'ended':
            status = MeetingStatus.ENDED
        
        # Parse meeting type
        meeting_type = self._convert_from_zoom_meeting_type(zoom_meeting.get('type', 2))
        
        return VideoMeeting(
            id=str(zoom_meeting['id']),
            topic=zoom_meeting.get('topic', ''),
            host_id=zoom_meeting.get('host_id', ''),
            host_email=zoom_meeting.get('host_email'),
            start_time=start_time,
            duration=zoom_meeting.get('duration', 60),
            timezone=zoom_meeting.get('timezone'),
            status=status,
            join_url=zoom_meeting.get('join_url'),
            start_url=zoom_meeting.get('start_url'),
            password=zoom_meeting.get('password'),
            meeting_type=meeting_type,
            agenda=zoom_meeting.get('agenda'),
            created_at=created_at,
            settings=zoom_meeting.get('settings', {})
        )
    
    def _convert_from_zoom_participant(self, zoom_participant: Dict[str, Any]) -> Participant:
        """Convert Zoom participant to Participant."""
        # Parse join/leave times
        join_time = None
        if zoom_participant.get('join_time'):
            try:
                join_time = datetime.fromisoformat(zoom_participant['join_time'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        leave_time = None
        if zoom_participant.get('leave_time'):
            try:
                leave_time = datetime.fromisoformat(zoom_participant['leave_time'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        return Participant(
            id=zoom_participant.get('id'),
            email=zoom_participant.get('user_email'),
            name=zoom_participant.get('name'),
            role=ParticipantRole.HOST if zoom_participant.get('user_email') == zoom_participant.get('host_email') else ParticipantRole.ATTENDEE,
            join_time=join_time,
            leave_time=leave_time,
            duration=zoom_participant.get('duration'),
            camera_on=zoom_participant.get('camera', True),
            microphone_on=not zoom_participant.get('audio_muted', False)
        )
    
    def _convert_from_zoom_recording(self, zoom_recording: Dict[str, Any], meeting_id: str) -> RecordingInfo:
        """Convert Zoom recording to RecordingInfo."""
        # Parse times
        recording_start = None
        if zoom_recording.get('recording_start'):
            try:
                recording_start = datetime.fromisoformat(zoom_recording['recording_start'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        recording_end = None
        if zoom_recording.get('recording_end'):
            try:
                recording_end = datetime.fromisoformat(zoom_recording['recording_end'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        return RecordingInfo(
            id=zoom_recording.get('id', ''),
            meeting_id=meeting_id,
            recording_start=recording_start or datetime.now(timezone.utc),
            recording_end=recording_end or datetime.now(timezone.utc),
            file_size=zoom_recording.get('file_size'),
            download_url=zoom_recording.get('download_url'),
            play_url=zoom_recording.get('play_url'),
            file_type=zoom_recording.get('file_type'),
            status=zoom_recording.get('status')
        )
    
    def _convert_to_zoom_meeting_type(self, meeting_type: MeetingType) -> int:
        """Convert MeetingType to Zoom type."""
        mapping = {
            MeetingType.INSTANT: 1,
            MeetingType.SCHEDULED: 2,
            MeetingType.RECURRING: 3,
            MeetingType.WEBINAR: 5
        }
        return mapping.get(meeting_type, 2)
    
    def _convert_from_zoom_meeting_type(self, zoom_type: int) -> MeetingType:
        """Convert Zoom type to MeetingType."""
        mapping = {
            1: MeetingType.INSTANT,
            2: MeetingType.SCHEDULED,
            3: MeetingType.RECURRING,
            8: MeetingType.RECURRING,  # Recurring with fixed time
            5: MeetingType.WEBINAR,
            6: MeetingType.WEBINAR,  # Recurring webinar
        }
        return mapping.get(zoom_type, MeetingType.SCHEDULED)