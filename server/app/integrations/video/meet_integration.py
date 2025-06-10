"""
Google Meet video conferencing integration.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import logging

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from ..base import OAuth2Integration, IntegrationConfig, ServiceUnavailableError, AuthenticationError
from ..registry import register_integration
from .base_video import (
    BaseVideoIntegration, VideoMeeting, VideoMeetingInput, Participant, RecordingInfo,
    MeetingType, MeetingStatus, ParticipantRole
)

logger = logging.getLogger(__name__)


@register_integration('google_meet')
class MeetIntegration(BaseVideoIntegration, OAuth2Integration):
    """Google Meet video conferencing integration."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, config: IntegrationConfig):
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google Meet dependencies not available. Install google-api-python-client google-auth-oauthlib")
        
        super().__init__(config)
        self._calendar_service = None
        self._credentials = None
        
    @property
    def provider_name(self) -> str:
        return "meet"
    
    async def get_authorization_url(self, state: str = None) -> str:
        """Get OAuth2 authorization URL for Google."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.config.credentials['client_id'],
                    "client_secret": self.config.credentials['client_secret'],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.config.credentials['redirect_uri']]
                }
            },
            scopes=self.SCOPES,
            state=state
        )
        flow.redirect_uri = self.config.credentials['redirect_uri']
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return auth_url
    
    async def exchange_code_for_tokens(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.config.credentials['client_id'],
                    "client_secret": self.config.credentials['client_secret'],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.config.credentials['redirect_uri']]
                }
            },
            scopes=self.SCOPES,
            state=state
        )
        flow.redirect_uri = self.config.credentials['redirect_uri']
        
        # Exchange code for tokens
        flow.fetch_token(code=code)
        
        tokens = {
            'access_token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'expires_at': flow.credentials.expiry.timestamp() if flow.credentials.expiry else None
        }
        
        # Update config with tokens
        self.config.credentials.update(tokens)
        
        return tokens
    
    async def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token."""
        if not self.refresh_token:
            return False
        
        try:
            credentials = Credentials(
                token=self.access_token,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.config.credentials['client_id'],
                client_secret=self.config.credentials['client_secret']
            )
            
            request = Request()
            credentials.refresh(request)
            
            self.access_token = credentials.token
            self.config.credentials['access_token'] = credentials.token
            
            return True
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return False
    
    async def connect(self) -> bool:
        """Connect to Google Calendar API (Meet uses Calendar API)."""
        try:
            if not self.access_token:
                return False
            
            self._credentials = Credentials(
                token=self.access_token,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.config.credentials['client_id'],
                client_secret=self.config.credentials['client_secret']
            )
            
            # Build Calendar service (Meet meetings are calendar events)
            import asyncio
            loop = asyncio.get_event_loop()
            self._calendar_service = await loop.run_in_executor(
                None,
                lambda: build('calendar', 'v3', credentials=self._credentials)
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Google Meet: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Google services."""
        self._calendar_service = None
        self._credentials = None
        return True
    
    async def test_connection(self) -> bool:
        """Test Google Meet connection."""
        try:
            if not self._calendar_service:
                return False
            
            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._calendar_service.calendarList().list(maxResults=1).execute()
            )
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def create_meeting(self, meeting_data: VideoMeetingInput) -> VideoMeeting:
        """Create a new Google Meet meeting (via Calendar event)."""
        if not self._calendar_service:
            raise ServiceUnavailableError("Not connected to Google Meet", "video")
        
        try:
            calendar_event = self._convert_to_calendar_event(meeting_data)
            
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().insert(
                    calendarId='primary',
                    body=calendar_event,
                    conferenceDataVersion=1
                ).execute()
            )
            
            return self._convert_from_calendar_event(result)
            
        except HttpError as e:
            logger.error(f"Failed to create Google Meet meeting: {e}")
            raise ServiceUnavailableError(f"Failed to create meeting: {e}", "video")
    
    async def get_meeting(self, meeting_id: str) -> Optional[VideoMeeting]:
        """Get Google Meet meeting by calendar event ID."""
        if not self._calendar_service:
            raise ServiceUnavailableError("Not connected to Google Meet", "video")
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().get(
                    calendarId='primary',
                    eventId=meeting_id
                ).execute()
            )
            
            return self._convert_from_calendar_event(result)
            
        except HttpError as e:
            if e.resp.status == 404:
                return None
            logger.error(f"Failed to get Google Meet meeting: {e}")
            raise ServiceUnavailableError(f"Failed to get meeting: {e}", "video")
    
    async def update_meeting(self, meeting_id: str, meeting_data: VideoMeetingInput) -> VideoMeeting:
        """Update Google Meet meeting."""
        if not self._calendar_service:
            raise ServiceUnavailableError("Not connected to Google Meet", "video")
        
        try:
            calendar_event = self._convert_to_calendar_event(meeting_data)
            
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().update(
                    calendarId='primary',
                    eventId=meeting_id,
                    body=calendar_event,
                    conferenceDataVersion=1
                ).execute()
            )
            
            return self._convert_from_calendar_event(result)
            
        except HttpError as e:
            logger.error(f"Failed to update Google Meet meeting: {e}")
            raise ServiceUnavailableError(f"Failed to update meeting: {e}", "video")
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete Google Meet meeting."""
        if not self._calendar_service:
            raise ServiceUnavailableError("Not connected to Google Meet", "video")
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().delete(
                    calendarId='primary',
                    eventId=meeting_id
                ).execute()
            )
            return True
        except HttpError as e:
            if e.resp.status == 404:
                return True  # Already deleted
            logger.error(f"Failed to delete Google Meet meeting: {e}")
            return False
    
    async def list_meetings(
        self,
        user_id: Optional[str] = None,
        meeting_type: Optional[MeetingType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 30
    ) -> List[VideoMeeting]:
        """List Google Meet meetings (calendar events with conferenceData)."""
        if not self._calendar_service:
            raise ServiceUnavailableError("Not connected to Google Meet", "video")
        
        try:
            params = {
                'calendarId': 'primary',
                'maxResults': page_size,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if start_time:
                params['timeMin'] = start_time.isoformat()
            if end_time:
                params['timeMax'] = end_time.isoformat()
            
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().list(**params).execute()
            )
            
            meetings = []
            for event in result.get('items', []):
                # Only include events with Google Meet conferenceData
                if event.get('conferenceData', {}).get('conferenceId'):
                    meeting = self._convert_from_calendar_event(event)
                    
                    # Apply meeting type filter
                    if meeting_type and meeting.meeting_type != meeting_type:
                        continue
                    
                    meetings.append(meeting)
            
            return meetings
            
        except HttpError as e:
            logger.error(f"Failed to list Google Meet meetings: {e}")
            raise ServiceUnavailableError(f"Failed to list meetings: {e}", "video")
    
    async def start_meeting(self, meeting_id: str) -> bool:
        """Start Google Meet meeting (Google Meet starts automatically)."""
        # Google Meet meetings start automatically when participants join
        return True
    
    async def end_meeting(self, meeting_id: str) -> bool:
        """End Google Meet meeting (Google Meet ends automatically)."""
        # Google Meet meetings end automatically when all participants leave
        return True
    
    async def get_meeting_participants(self, meeting_id: str) -> List[Participant]:
        """Get Google Meet meeting participants."""
        # Google Meet doesn't provide real-time participant API through Calendar
        # Would need Google Meet API or Admin SDK for this
        return []
    
    async def add_participant(self, meeting_id: str, email: str, name: Optional[str] = None) -> bool:
        """Add participant to Google Meet meeting."""
        if not self._calendar_service:
            raise ServiceUnavailableError("Not connected to Google Meet", "video")
        
        try:
            # Get current event
            import asyncio
            loop = asyncio.get_event_loop()
            event = await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().get(
                    calendarId='primary',
                    eventId=meeting_id
                ).execute()
            )
            
            # Add attendee
            attendees = event.get('attendees', [])
            attendees.append({'email': email, 'displayName': name})
            event['attendees'] = attendees
            
            # Update event
            await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().update(
                    calendarId='primary',
                    eventId=meeting_id,
                    body=event
                ).execute()
            )
            
            return True
            
        except HttpError as e:
            logger.error(f"Failed to add participant: {e}")
            return False
    
    async def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Remove participant from Google Meet meeting."""
        if not self._calendar_service:
            raise ServiceUnavailableError("Not connected to Google Meet", "video")
        
        try:
            # Get current event
            import asyncio
            loop = asyncio.get_event_loop()
            event = await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().get(
                    calendarId='primary',
                    eventId=meeting_id
                ).execute()
            )
            
            # Remove attendee by email (using participant_id as email)
            attendees = event.get('attendees', [])
            attendees = [a for a in attendees if a.get('email') != participant_id]
            event['attendees'] = attendees
            
            # Update event
            await loop.run_in_executor(
                None,
                lambda: self._calendar_service.events().update(
                    calendarId='primary',
                    eventId=meeting_id,
                    body=event
                ).execute()
            )
            
            return True
            
        except HttpError as e:
            logger.error(f"Failed to remove participant: {e}")
            return False
    
    async def mute_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Mute participant in Google Meet meeting."""
        # Google Meet doesn't support muting participants via API
        return False
    
    async def unmute_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Unmute participant in Google Meet meeting."""
        # Google Meet doesn't support unmuting participants via API
        return False
    
    async def start_recording(self, meeting_id: str, record_type: str = "cloud") -> bool:
        """Start recording Google Meet meeting."""
        # Google Meet recording is controlled by meeting participants
        # No API for programmatic recording control
        return False
    
    async def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording Google Meet meeting."""
        # Google Meet recording is controlled by meeting participants
        return False
    
    async def get_recordings(self, meeting_id: str) -> List[RecordingInfo]:
        """Get recordings for Google Meet meeting."""
        # Google Meet recordings are stored in Google Drive
        # Would need Drive API to locate recordings
        return []
    
    async def delete_recording(self, recording_id: str) -> bool:
        """Delete Google Meet recording."""
        # Google Meet recordings are stored in Google Drive
        return False
    
    def _convert_to_calendar_event(self, meeting_data: VideoMeetingInput) -> Dict[str, Any]:
        """Convert VideoMeetingInput to Google Calendar event with Meet."""
        event = {
            'summary': meeting_data.topic,
            'description': meeting_data.agenda or '',
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{datetime.now().timestamp()}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        }
        
        # Set time
        if meeting_data.start_time:
            start_time = meeting_data.start_time
            end_time = start_time + timedelta(minutes=meeting_data.duration)
            
            if meeting_data.timezone:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': meeting_data.timezone
                }
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': meeting_data.timezone
                }
            else:
                event['start'] = {'dateTime': start_time.isoformat()}
                event['end'] = {'dateTime': end_time.isoformat()}
        
        # Add participants as attendees
        if meeting_data.participants:
            event['attendees'] = [{'email': email} for email in meeting_data.participants]
        
        # Add settings
        if meeting_data.auto_recording:
            # Google Meet doesn't support auto-recording via API
            pass
        
        return event
    
    def _convert_from_calendar_event(self, calendar_event: Dict[str, Any]) -> VideoMeeting:
        """Convert Google Calendar event to VideoMeeting."""
        # Parse start and end times
        start_data = calendar_event.get('start', {})
        end_data = calendar_event.get('end', {})
        
        start_time = None
        end_time = None
        
        if 'dateTime' in start_data:
            start_time = datetime.fromisoformat(start_data['dateTime'].replace('Z', '+00:00'))
        elif 'date' in start_data:
            start_time = datetime.fromisoformat(start_data['date'])
        
        if 'dateTime' in end_data:
            end_time = datetime.fromisoformat(end_data['dateTime'].replace('Z', '+00:00'))
        elif 'date' in end_data:
            end_time = datetime.fromisoformat(end_data['date'])
        
        # Calculate duration
        duration = 60  # default
        if start_time and end_time:
            duration = int((end_time - start_time).total_seconds() / 60)
        
        # Parse conference data
        conference_data = calendar_event.get('conferenceData', {})
        join_url = None
        meeting_id = None
        
        if conference_data:
            meeting_id = conference_data.get('conferenceId')
            for entry_point in conference_data.get('entryPoints', []):
                if entry_point.get('entryPointType') == 'video':
                    join_url = entry_point.get('uri')
                    break
        
        # Parse attendees
        participants = []
        for attendee in calendar_event.get('attendees', []):
            if attendee.get('email'):
                participant = Participant(
                    email=attendee['email'],
                    name=attendee.get('displayName'),
                    role=ParticipantRole.ATTENDEE
                )
                participants.append(participant)
        
        # Parse timestamps
        created_at = None
        if calendar_event.get('created'):
            created_at = datetime.fromisoformat(calendar_event['created'].replace('Z', '+00:00'))
        
        updated_at = None
        if calendar_event.get('updated'):
            updated_at = datetime.fromisoformat(calendar_event['updated'].replace('Z', '+00:00'))
        
        return VideoMeeting(
            id=calendar_event['id'],
            topic=calendar_event.get('summary', ''),
            host_id=calendar_event.get('creator', {}).get('email', ''),
            host_email=calendar_event.get('creator', {}).get('email'),
            start_time=start_time,
            duration=duration,
            timezone=start_data.get('timeZone'),
            status=MeetingStatus.WAITING,  # Default status
            join_url=join_url,
            meeting_type=MeetingType.SCHEDULED,
            participants=participants,
            agenda=calendar_event.get('description'),
            created_at=created_at,
            updated_at=updated_at,
            settings={}
        )