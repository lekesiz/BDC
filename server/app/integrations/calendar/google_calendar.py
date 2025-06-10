"""
Google Calendar integration.
"""

import asyncio
from datetime import datetime, timezone
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

from ..base import OAuth2Integration, IntegrationConfig, AuthenticationError, ServiceUnavailableError
from ..registry import register_integration
from .base_calendar import (
    BaseCalendarIntegration, CalendarEvent, CalendarEventInput, Calendar,
    EventStatus, EventVisibility
)

logger = logging.getLogger(__name__)


@register_integration('google_calendar')
class GoogleCalendarIntegration(BaseCalendarIntegration, OAuth2Integration):
    """Google Calendar integration using OAuth2."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, config: IntegrationConfig):
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google Calendar dependencies not available. Install google-api-python-client google-auth-oauthlib")
        
        super().__init__(config)
        self._service = None
        self._credentials = None
    
    @property
    def provider_name(self) -> str:
        return "google"
    
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
        """Connect to Google Calendar API."""
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
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._service = await loop.run_in_executor(
                None, 
                lambda: build('calendar', 'v3', credentials=self._credentials)
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Google Calendar: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Google Calendar."""
        self._service = None
        self._credentials = None
        return True
    
    async def test_connection(self) -> bool:
        """Test Google Calendar connection."""
        try:
            if not self._service:
                return False
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._service.calendarList().list(maxResults=1).execute()
            )
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def get_calendars(self) -> List[Calendar]:
        """Get list of Google calendars."""
        if not self._service:
            raise ServiceUnavailableError("Not connected to Google Calendar", "calendar")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.calendarList().list().execute()
            )
            
            calendars = []
            for item in result.get('items', []):
                calendar = Calendar(
                    id=item['id'],
                    name=item['summary'],
                    description=item.get('description'),
                    timezone=item.get('timeZone'),
                    primary=item.get('primary', False),
                    access_role=item.get('accessRole'),
                    color=item.get('colorId')
                )
                calendars.append(calendar)
            
            return calendars
        except HttpError as e:
            logger.error(f"Failed to get calendars: {e}")
            raise ServiceUnavailableError(f"Failed to get calendars: {e}", "calendar")
    
    async def get_primary_calendar(self) -> Optional[Calendar]:
        """Get the primary Google calendar."""
        calendars = await self.get_calendars()
        for calendar in calendars:
            if calendar.primary:
                return calendar
        return None
    
    async def create_event(self, calendar_id: str, event_data: CalendarEventInput) -> CalendarEvent:
        """Create a new event in Google Calendar."""
        if not self._service:
            raise ServiceUnavailableError("Not connected to Google Calendar", "calendar")
        
        try:
            event_body = self._convert_to_google_event(event_data)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.events().insert(calendarId=calendar_id, body=event_body).execute()
            )
            
            return self._convert_from_google_event(result)
        except HttpError as e:
            logger.error(f"Failed to create event: {e}")
            raise ServiceUnavailableError(f"Failed to create event: {e}", "calendar")
    
    async def get_event(self, calendar_id: str, event_id: str) -> Optional[CalendarEvent]:
        """Get a specific event from Google Calendar."""
        if not self._service:
            raise ServiceUnavailableError("Not connected to Google Calendar", "calendar")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )
            
            return self._convert_from_google_event(result)
        except HttpError as e:
            if e.resp.status == 404:
                return None
            logger.error(f"Failed to get event: {e}")
            raise ServiceUnavailableError(f"Failed to get event: {e}", "calendar")
    
    async def update_event(self, calendar_id: str, event_id: str, event_data: CalendarEventInput) -> CalendarEvent:
        """Update an existing event in Google Calendar."""
        if not self._service:
            raise ServiceUnavailableError("Not connected to Google Calendar", "calendar")
        
        try:
            event_body = self._convert_to_google_event(event_data)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.events().update(
                    calendarId=calendar_id, 
                    eventId=event_id, 
                    body=event_body
                ).execute()
            )
            
            return self._convert_from_google_event(result)
        except HttpError as e:
            logger.error(f"Failed to update event: {e}")
            raise ServiceUnavailableError(f"Failed to update event: {e}", "calendar")
    
    async def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete an event from Google Calendar."""
        if not self._service:
            raise ServiceUnavailableError("Not connected to Google Calendar", "calendar")
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            )
            return True
        except HttpError as e:
            if e.resp.status == 404:
                return True  # Already deleted
            logger.error(f"Failed to delete event: {e}")
            return False
    
    async def list_events(
        self, 
        calendar_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[CalendarEvent]:
        """List events from Google Calendar."""
        if not self._service:
            raise ServiceUnavailableError("Not connected to Google Calendar", "calendar")
        
        try:
            params = {
                'calendarId': calendar_id,
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if start_time:
                params['timeMin'] = start_time.isoformat()
            if end_time:
                params['timeMax'] = end_time.isoformat()
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.events().list(**params).execute()
            )
            
            events = []
            for item in result.get('items', []):
                event = self._convert_from_google_event(item)
                events.append(event)
            
            return events
        except HttpError as e:
            logger.error(f"Failed to list events: {e}")
            raise ServiceUnavailableError(f"Failed to list events: {e}", "calendar")
    
    async def search_events(self, calendar_id: str, query: str) -> List[CalendarEvent]:
        """Search for events in Google Calendar."""
        if not self._service:
            raise ServiceUnavailableError("Not connected to Google Calendar", "calendar")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.events().list(
                    calendarId=calendar_id,
                    q=query,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
            )
            
            events = []
            for item in result.get('items', []):
                event = self._convert_from_google_event(item)
                events.append(event)
            
            return events
        except HttpError as e:
            logger.error(f"Failed to search events: {e}")
            raise ServiceUnavailableError(f"Failed to search events: {e}", "calendar")
    
    def _convert_to_google_event(self, event_data: CalendarEventInput) -> Dict[str, Any]:
        """Convert CalendarEventInput to Google Calendar event format."""
        event = {
            'summary': event_data.title,
            'description': event_data.description,
            'location': event_data.location,
        }
        
        # Handle datetime
        if event_data.all_day:
            event['start'] = {'date': event_data.start_time.date().isoformat()}
            event['end'] = {'date': event_data.end_time.date().isoformat()}
        else:
            start_dt = event_data.start_time
            end_dt = event_data.end_time
            
            if event_data.timezone:
                event['start'] = {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': event_data.timezone
                }
                event['end'] = {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': event_data.timezone
                }
            else:
                event['start'] = {'dateTime': start_dt.isoformat()}
                event['end'] = {'dateTime': end_dt.isoformat()}
        
        # Handle attendees
        if event_data.attendees:
            event['attendees'] = [{'email': email} for email in event_data.attendees]
        
        # Handle reminders
        if event_data.reminders:
            event['reminders'] = {
                'useDefault': False,
                'overrides': event_data.reminders
            }
        
        # Handle recurrence
        if event_data.recurrence:
            event['recurrence'] = [self._build_recurrence_rule(event_data.recurrence)]
        
        # Handle visibility
        if event_data.visibility != EventVisibility.DEFAULT:
            event['visibility'] = event_data.visibility.value
        
        return event
    
    def _convert_from_google_event(self, google_event: Dict[str, Any]) -> CalendarEvent:
        """Convert Google Calendar event to CalendarEvent."""
        # Parse start and end times
        start_data = google_event.get('start', {})
        end_data = google_event.get('end', {})
        
        all_day = 'date' in start_data
        
        if all_day:
            start_time = datetime.fromisoformat(start_data['date'])
            end_time = datetime.fromisoformat(end_data['date'])
        else:
            start_time = datetime.fromisoformat(start_data['dateTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_data['dateTime'].replace('Z', '+00:00'))
        
        # Parse attendees
        attendees = []
        for attendee in google_event.get('attendees', []):
            attendees.append(attendee.get('email'))
        
        # Parse status
        status = EventStatus.CONFIRMED
        if google_event.get('status') == 'cancelled':
            status = EventStatus.CANCELLED
        elif google_event.get('status') == 'tentative':
            status = EventStatus.TENTATIVE
        
        # Parse visibility
        visibility = EventVisibility.DEFAULT
        if google_event.get('visibility'):
            try:
                visibility = EventVisibility(google_event['visibility'])
            except ValueError:
                pass
        
        # Parse timestamps
        created_at = None
        if google_event.get('created'):
            created_at = datetime.fromisoformat(google_event['created'].replace('Z', '+00:00'))
        
        updated_at = None
        if google_event.get('updated'):
            updated_at = datetime.fromisoformat(google_event['updated'].replace('Z', '+00:00'))
        
        return CalendarEvent(
            id=google_event['id'],
            title=google_event.get('summary', ''),
            start_time=start_time,
            end_time=end_time,
            description=google_event.get('description'),
            location=google_event.get('location'),
            attendees=attendees,
            organizer=google_event.get('organizer', {}).get('email'),
            status=status,
            visibility=visibility,
            timezone=start_data.get('timeZone'),
            all_day=all_day,
            created_at=created_at,
            updated_at=updated_at,
            html_link=google_event.get('htmlLink'),
            meeting_link=google_event.get('hangoutLink'),
            recurrence=google_event.get('recurrence')
        )