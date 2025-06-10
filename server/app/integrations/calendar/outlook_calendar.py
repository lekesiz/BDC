"""
Microsoft Outlook Calendar integration.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from ..base import OAuth2Integration, IntegrationConfig, AuthenticationError, ServiceUnavailableError
from ..registry import register_integration
from .base_calendar import (
    BaseCalendarIntegration, CalendarEvent, CalendarEventInput, Calendar,
    EventStatus, EventVisibility
)

logger = logging.getLogger(__name__)


@register_integration('outlook_calendar')
class OutlookCalendarIntegration(BaseCalendarIntegration, OAuth2Integration):
    """Microsoft Outlook Calendar integration using OAuth2."""
    
    SCOPES = [
        'https://graph.microsoft.com/Calendars.ReadWrite',
        'https://graph.microsoft.com/User.Read'
    ]
    
    BASE_URL = 'https://graph.microsoft.com/v1.0'
    AUTH_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    
    def __init__(self, config: IntegrationConfig):
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp is required for Outlook integration")
        
        super().__init__(config)
        self._session = None
    
    @property
    def provider_name(self) -> str:
        return "outlook"
    
    async def get_authorization_url(self, state: str = None) -> str:
        """Get OAuth2 authorization URL for Microsoft."""
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
                    raise AuthenticationError(f"Token exchange failed: {text}", "calendar")
                
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
                headers={'Authorization': f'Bearer {self.access_token}'}
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Outlook Calendar: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Microsoft Graph API."""
        if self._session:
            await self._session.close()
            self._session = None
        return True
    
    async def test_connection(self) -> bool:
        """Test Outlook Calendar connection."""
        try:
            if not self._session:
                return False
            
            async with self._session.get(f"{self.BASE_URL}/me") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def get_calendars(self) -> List[Calendar]:
        """Get list of Outlook calendars."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Outlook Calendar", "calendar")
        
        try:
            async with self._session.get(f"{self.BASE_URL}/me/calendars") as response:
                if response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get calendars: {text}", "calendar")
                
                data = await response.json()
                calendars = []
                
                for item in data.get('value', []):
                    calendar = Calendar(
                        id=item['id'],
                        name=item['name'],
                        description=item.get('description'),
                        primary=item.get('isDefaultCalendar', False),
                        color=item.get('color')
                    )
                    calendars.append(calendar)
                
                return calendars
        except Exception as e:
            logger.error(f"Failed to get calendars: {e}")
            raise ServiceUnavailableError(f"Failed to get calendars: {e}", "calendar")
    
    async def get_primary_calendar(self) -> Optional[Calendar]:
        """Get the primary Outlook calendar."""
        calendars = await self.get_calendars()
        for calendar in calendars:
            if calendar.primary:
                return calendar
        return calendars[0] if calendars else None
    
    async def create_event(self, calendar_id: str, event_data: CalendarEventInput) -> CalendarEvent:
        """Create a new event in Outlook Calendar."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Outlook Calendar", "calendar")
        
        try:
            event_body = self._convert_to_outlook_event(event_data)
            
            async with self._session.post(
                f"{self.BASE_URL}/me/calendars/{calendar_id}/events",
                json=event_body
            ) as response:
                if response.status not in [200, 201]:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to create event: {text}", "calendar")
                
                result = await response.json()
                return self._convert_from_outlook_event(result)
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise ServiceUnavailableError(f"Failed to create event: {e}", "calendar")
    
    async def get_event(self, calendar_id: str, event_id: str) -> Optional[CalendarEvent]:
        """Get a specific event from Outlook Calendar."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Outlook Calendar", "calendar")
        
        try:
            async with self._session.get(
                f"{self.BASE_URL}/me/calendars/{calendar_id}/events/{event_id}"
            ) as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to get event: {text}", "calendar")
                
                result = await response.json()
                return self._convert_from_outlook_event(result)
        except Exception as e:
            logger.error(f"Failed to get event: {e}")
            raise ServiceUnavailableError(f"Failed to get event: {e}", "calendar")
    
    async def update_event(self, calendar_id: str, event_id: str, event_data: CalendarEventInput) -> CalendarEvent:
        """Update an existing event in Outlook Calendar."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Outlook Calendar", "calendar")
        
        try:
            event_body = self._convert_to_outlook_event(event_data)
            
            async with self._session.patch(
                f"{self.BASE_URL}/me/calendars/{calendar_id}/events/{event_id}",
                json=event_body
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to update event: {text}", "calendar")
                
                result = await response.json()
                return self._convert_from_outlook_event(result)
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            raise ServiceUnavailableError(f"Failed to update event: {e}", "calendar")
    
    async def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete an event from Outlook Calendar."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Outlook Calendar", "calendar")
        
        try:
            async with self._session.delete(
                f"{self.BASE_URL}/me/calendars/{calendar_id}/events/{event_id}"
            ) as response:
                return response.status in [200, 204, 404]  # 404 means already deleted
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False
    
    async def list_events(
        self, 
        calendar_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[CalendarEvent]:
        """List events from Outlook Calendar."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Outlook Calendar", "calendar")
        
        try:
            params = {'$top': max_results}
            
            filter_parts = []
            if start_time:
                filter_parts.append(f"start/dateTime ge '{start_time.isoformat()}'")
            if end_time:
                filter_parts.append(f"end/dateTime le '{end_time.isoformat()}'")
            
            if filter_parts:
                params['$filter'] = ' and '.join(filter_parts)
            
            params['$orderby'] = 'start/dateTime'
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.BASE_URL}/me/calendars/{calendar_id}/events?{query_string}"
            
            async with self._session.get(url) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to list events: {text}", "calendar")
                
                data = await response.json()
                events = []
                
                for item in data.get('value', []):
                    event = self._convert_from_outlook_event(item)
                    events.append(event)
                
                return events
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            raise ServiceUnavailableError(f"Failed to list events: {e}", "calendar")
    
    async def search_events(self, calendar_id: str, query: str) -> List[CalendarEvent]:
        """Search for events in Outlook Calendar."""
        if not self._session:
            raise ServiceUnavailableError("Not connected to Outlook Calendar", "calendar")
        
        try:
            params = {
                '$search': f'"{query}"',
                '$orderby': 'start/dateTime'
            }
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.BASE_URL}/me/calendars/{calendar_id}/events?{query_string}"
            
            async with self._session.get(url) as response:
                if response.status != 200:
                    text = await response.text()
                    raise ServiceUnavailableError(f"Failed to search events: {text}", "calendar")
                
                data = await response.json()
                events = []
                
                for item in data.get('value', []):
                    event = self._convert_from_outlook_event(item)
                    events.append(event)
                
                return events
        except Exception as e:
            logger.error(f"Failed to search events: {e}")
            raise ServiceUnavailableError(f"Failed to search events: {e}", "calendar")
    
    def _convert_to_outlook_event(self, event_data: CalendarEventInput) -> Dict[str, Any]:
        """Convert CalendarEventInput to Outlook event format."""
        event = {
            'subject': event_data.title,
            'body': {
                'contentType': 'text',
                'content': event_data.description or ''
            },
            'location': {
                'displayName': event_data.location or ''
            } if event_data.location else None
        }
        
        # Handle datetime
        if event_data.all_day:
            event['isAllDay'] = True
            event['start'] = {
                'dateTime': event_data.start_time.date().isoformat(),
                'timeZone': event_data.timezone or 'UTC'
            }
            event['end'] = {
                'dateTime': event_data.end_time.date().isoformat(),
                'timeZone': event_data.timezone or 'UTC'
            }
        else:
            event['isAllDay'] = False
            event['start'] = {
                'dateTime': event_data.start_time.isoformat(),
                'timeZone': event_data.timezone or 'UTC'
            }
            event['end'] = {
                'dateTime': event_data.end_time.isoformat(),
                'timeZone': event_data.timezone or 'UTC'
            }
        
        # Handle attendees
        if event_data.attendees:
            event['attendees'] = [
                {
                    'emailAddress': {
                        'address': email,
                        'name': email  # Could be improved with actual names
                    },
                    'type': 'required'
                }
                for email in event_data.attendees
            ]
        
        # Remove None values
        return {k: v for k, v in event.items() if v is not None}
    
    def _convert_from_outlook_event(self, outlook_event: Dict[str, Any]) -> CalendarEvent:
        """Convert Outlook event to CalendarEvent."""
        # Parse start and end times
        start_data = outlook_event.get('start', {})
        end_data = outlook_event.get('end', {})
        
        start_time = datetime.fromisoformat(start_data['dateTime'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_data['dateTime'].replace('Z', '+00:00'))
        
        # Parse attendees
        attendees = []
        for attendee in outlook_event.get('attendees', []):
            email_address = attendee.get('emailAddress', {})
            if email_address.get('address'):
                attendees.append(email_address['address'])
        
        # Parse status
        status = EventStatus.CONFIRMED
        if outlook_event.get('isCancelled'):
            status = EventStatus.CANCELLED
        
        # Parse timestamps
        created_at = None
        if outlook_event.get('createdDateTime'):
            created_at = datetime.fromisoformat(outlook_event['createdDateTime'].replace('Z', '+00:00'))
        
        updated_at = None
        if outlook_event.get('lastModifiedDateTime'):
            updated_at = datetime.fromisoformat(outlook_event['lastModifiedDateTime'].replace('Z', '+00:00'))
        
        return CalendarEvent(
            id=outlook_event['id'],
            title=outlook_event.get('subject', ''),
            start_time=start_time,
            end_time=end_time,
            description=outlook_event.get('body', {}).get('content'),
            location=outlook_event.get('location', {}).get('displayName'),
            attendees=attendees,
            organizer=outlook_event.get('organizer', {}).get('emailAddress', {}).get('address'),
            status=status,
            timezone=start_data.get('timeZone'),
            all_day=outlook_event.get('isAllDay', False),
            created_at=created_at,
            updated_at=updated_at,
            html_link=outlook_event.get('webLink'),
            meeting_link=outlook_event.get('onlineMeeting', {}).get('joinUrl')
        )