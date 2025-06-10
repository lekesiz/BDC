"""
Microsoft Teams video conferencing integration.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from ..base import OAuth2Integration, IntegrationConfig, ServiceUnavailableError, AuthenticationError
from ..registry import register_integration
from .base_video import (
    BaseVideoIntegration, VideoMeeting, VideoMeetingInput, Participant, RecordingInfo,
    MeetingType, MeetingStatus, ParticipantRole
)

logger = logging.getLogger(__name__)


@register_integration('microsoft_teams')
class TeamsIntegration(BaseVideoIntegration, OAuth2Integration):
    """Microsoft Teams video conferencing integration."""
    
    BASE_URL = 'https://graph.microsoft.com/v1.0'
    AUTH_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    
    SCOPES = [
        'https://graph.microsoft.com/OnlineMeetings.ReadWrite',
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/Calendars.ReadWrite'
    ]
    
    def __init__(self, config: IntegrationConfig):
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp is required for Teams integration")
        
        super().__init__(config)
        self._session = None
        
    @property
    def provider_name(self) -> str:
        return "teams"
    
    async def get_authorization_url(self, state: str = None) -> str:
        """Get OAuth2 authorization URL for Teams."""
        params = {
            'client_id': self.config.credentials['client_id'],
            'response_type': 'code',
            'redirect_uri': self.config.credentials['redirect_uri'],
            'scope': ' '.join(self.SCOPES),
            'response_mode': 'query'
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        data = {
            'client_id': self.config.credentials['client_id'],
            'client_secret': self.config.credentials['client_secret'],
            'code': code,
            'redirect_uri': self.config.credentials['redirect_uri'],
            'grant_type': 'authorization_code'
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
            'client_id': self.config.credentials['client_id'],
            'client_secret': self.config.credentials['client_secret'],
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
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
        """Connect to Microsoft Graph API."""
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
            logger.error(f"Failed to connect to Teams: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Microsoft Graph API."""
        if self._session:
            await self._session.close()
            self._session = None
        return True
    
    async def test_connection(self) -> bool:
        """Test Teams connection."""
        try:
            if not self._session:
                return False
            
            async with self._session.get(f"{self.BASE_URL}/me") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def create_meeting(self, meeting_data: VideoMeetingInput) -> VideoMeeting:
        """Create a new Teams meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Teams", "video")
        
        try:
            teams_meeting_data = self._convert_to_teams_meeting(meeting_data)
            
            async with self._session.post(
                f"{self.BASE_URL}/me/onlineMeetings",
                json=teams_meeting_data
            ) as response:
                if response.status not in [200, 201]:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to create Teams meeting: {text}", "video")
                
                result = await response.json()
                return self._convert_from_teams_meeting(result)
                
        except Exception as e:
            logger.error(f"Failed to create Teams meeting: {e}")
            raise ServiceUnavailableError(f"Failed to create meeting: {e}", "video")
    
    async def get_meeting(self, meeting_id: str) -> Optional[VideoMeeting]:
        """Get Teams meeting by ID."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Teams", "video")
        
        try:
            async with self._session.get(f"{self.BASE_URL}/me/onlineMeetings/{meeting_id}") as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get Teams meeting: {text}", "video")
                
                result = await response.json()
                return self._convert_from_teams_meeting(result)
                
        except Exception as e:
            logger.error(f"Failed to get Teams meeting: {e}")
            raise ServiceUnavailableError(f"Failed to get meeting: {e}", "video")
    
    async def update_meeting(self, meeting_id: str, meeting_data: VideoMeetingInput) -> VideoMeeting:
        """Update Teams meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Teams", "video")
        
        try:
            teams_meeting_data = self._convert_to_teams_meeting(meeting_data, update=True)
            
            async with self._session.patch(
                f"{self.BASE_URL}/me/onlineMeetings/{meeting_id}",
                json=teams_meeting_data
            ) as response:
                if response.status not in [200, 204]:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to update Teams meeting: {text}", "video")
                
                # Get updated meeting
                return await self.get_meeting(meeting_id)
                
        except Exception as e:
            logger.error(f"Failed to update Teams meeting: {e}")
            raise ServiceUnavailableError(f"Failed to update meeting: {e}", "video")
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete Teams meeting."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Teams", "video")
        
        try:
            async with self._session.delete(f"{self.BASE_URL}/me/onlineMeetings/{meeting_id}") as response:
                return response.status in [200, 204, 404]  # 404 means already deleted
        except Exception as e:
            logger.error(f"Failed to delete Teams meeting: {e}")
            return False
    
    async def list_meetings(
        self,
        user_id: Optional[str] = None,
        meeting_type: Optional[MeetingType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 30
    ) -> List[VideoMeeting]:
        """List Teams meetings."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Teams", "video")
        
        try:
            user_endpoint = user_id or 'me'
            params = {'$top': page_size}
            
            # Teams doesn't have direct filtering, so we'll get all and filter
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.BASE_URL}/users/{user_endpoint}/onlineMeetings?{query_string}"
            
            async with self._session.get(url) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to list Teams meetings: {text}", "video")
                
                data = await response.json()
                meetings = []
                
                for meeting_data in data.get('value', []):
                    meeting = self._convert_from_teams_meeting(meeting_data)
                    
                    # Apply filters
                    if meeting_type and meeting.meeting_type != meeting_type:
                        continue
                    if start_time and meeting.start_time and meeting.start_time < start_time:
                        continue
                    if end_time and meeting.start_time and meeting.start_time > end_time:
                        continue
                    
                    meetings.append(meeting)
                
                return meetings
                
        except Exception as e:
            logger.error(f"Failed to list Teams meetings: {e}")
            raise ServiceUnavailableError(f"Failed to list meetings: {e}", "video")
    
    async def start_meeting(self, meeting_id: str) -> bool:
        """Start Teams meeting (Teams doesn't have explicit start API)."""
        # Teams meetings start automatically when participants join
        return True
    
    async def end_meeting(self, meeting_id: str) -> bool:
        """End Teams meeting (Teams doesn't have explicit end API)."""
        # Teams meetings end automatically when all participants leave
        return True
    
    async def get_meeting_participants(self, meeting_id: str) -> List[Participant]:
        """Get Teams meeting participants."""
        # Teams doesn't provide real-time participant API
        # Would need to use Teams activity reports or presence API
        return []
    
    async def add_participant(self, meeting_id: str, email: str, name: Optional[str] = None) -> bool:
        """Add participant to Teams meeting."""
        # Teams handles participants through invitations
        return True
    
    async def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Remove participant from Teams meeting."""
        # Teams doesn't support removing participants via API
        return False
    
    async def mute_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Mute participant in Teams meeting."""
        # Teams doesn't support muting participants via API
        return False
    
    async def unmute_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Unmute participant in Teams meeting."""
        # Teams doesn't support unmuting participants via API
        return False
    
    async def start_recording(self, meeting_id: str, record_type: str = "cloud") -> bool:
        """Start recording Teams meeting."""
        # Teams recording is controlled by meeting participants
        # No API for programmatic recording control
        return False
    
    async def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording Teams meeting."""
        # Teams recording is controlled by meeting participants
        return False
    
    async def get_recordings(self, meeting_id: str) -> List[RecordingInfo]:
        """Get recordings for Teams meeting."""
        # Teams recordings are available through SharePoint/OneDrive
        # Would need additional Graph API calls to locate recordings
        return []
    
    async def delete_recording(self, recording_id: str) -> bool:
        """Delete Teams recording."""
        # Teams recordings are stored in SharePoint/OneDrive
        return False
    
    def _convert_to_teams_meeting(self, meeting_data: VideoMeetingInput, update: bool = False) -> Dict[str, Any]:
        """Convert VideoMeetingInput to Teams meeting format."""
        teams_meeting = {
            'subject': meeting_data.topic
        }
        
        if meeting_data.start_time:
            teams_meeting['startDateTime'] = meeting_data.start_time.isoformat() + 'Z'
            end_time = meeting_data.start_time + timedelta(minutes=meeting_data.duration)
            teams_meeting['endDateTime'] = end_time.isoformat() + 'Z'
        
        # Teams meeting settings
        if not update:  # Only set on creation
            teams_meeting['participantAccessPolicy'] = {
                'enabledForGuestsAndAnonymous': True,
                'enabledForExternalUsers': True
            }
            
            teams_meeting['audioConferencing'] = {
                'tollFreeNumber': None,
                'tollNumber': None,
                'conferenceId': None
            }
        
        return teams_meeting
    
    def _convert_from_teams_meeting(self, teams_meeting: Dict[str, Any]) -> VideoMeeting:
        """Convert Teams meeting to VideoMeeting."""
        # Parse times
        start_time = None
        if teams_meeting.get('startDateTime'):
            try:
                start_time = datetime.fromisoformat(teams_meeting['startDateTime'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        end_time = None
        if teams_meeting.get('endDateTime'):
            try:
                end_time = datetime.fromisoformat(teams_meeting['endDateTime'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Calculate duration
        duration = 60  # default
        if start_time and end_time:
            duration = int((end_time - start_time).total_seconds() / 60)
        
        created_at = None
        if teams_meeting.get('creationDateTime'):
            try:
                created_at = datetime.fromisoformat(teams_meeting['creationDateTime'].replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Extract join URL
        join_url = None
        if teams_meeting.get('joinWebUrl'):
            join_url = teams_meeting['joinWebUrl']
        elif teams_meeting.get('joinInformation', {}).get('content'):
            # Parse join URL from content
            content = teams_meeting['joinInformation']['content']
            # Simple extraction - would need more robust parsing
            if 'https://teams.microsoft.com/' in content:
                start_idx = content.find('https://teams.microsoft.com/')
                end_idx = content.find(' ', start_idx)
                if end_idx == -1:
                    end_idx = content.find('\n', start_idx)
                if end_idx == -1:
                    end_idx = len(content)
                join_url = content[start_idx:end_idx]
        
        return VideoMeeting(
            id=teams_meeting.get('id', ''),
            topic=teams_meeting.get('subject', ''),
            host_id=teams_meeting.get('organizer', {}).get('identity', {}).get('user', {}).get('id', ''),
            host_email=teams_meeting.get('organizer', {}).get('identity', {}).get('user', {}).get('email'),
            start_time=start_time,
            duration=duration,
            status=MeetingStatus.WAITING,  # Teams doesn't provide status
            join_url=join_url,
            meeting_type=MeetingType.SCHEDULED,
            created_at=created_at,
            settings={}
        )