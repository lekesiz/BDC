"""Refactored Google Calendar service with dependency injection and improved testability."""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.models.integration import UserIntegration
from app.exceptions import (
    NotFoundException,
    ValidationException,
    ExternalServiceException
)


# Protocol for mockable dependencies
class CalendarAPIProtocol(Protocol):
    """Protocol for Google Calendar API operations."""
    
    def build_service(self, credentials: Credentials) -> Resource:
        """Build the Google Calendar service."""
        ...


@dataclass
class CalendarEvent:
    """Data class for calendar event information."""
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = None
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


class GoogleCalendarAPI:
    """Concrete implementation of Google Calendar API operations."""
    
    API_SERVICE_NAME = 'calendar'
    API_VERSION = 'v3'
    
    def build_service(self, credentials: Credentials) -> Resource:
        """Build the Google Calendar service."""
        return build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)


class CalendarServiceRefactored:
    """
    Refactored Google Calendar service with dependency injection.
    
    This service handles OAuth2 authentication and calendar event management
    for Google Calendar integration.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    PROVIDER_NAME = 'google_calendar'
    
    def __init__(
        self,
        db_session: Session,
        client_secrets_path: str,
        redirect_uri: str,
        calendar_api: Optional[CalendarAPIProtocol] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Calendar Service.
        
        Args:
            db_session: SQLAlchemy database session
            client_secrets_path: Path to Google OAuth2 client secrets file
            redirect_uri: OAuth2 redirect URI
            calendar_api: Calendar API implementation (defaults to GoogleCalendarAPI)
            logger: Logger instance (defaults to module logger)
        """
        self.db = db_session
        self.client_secrets_path = client_secrets_path
        self.redirect_uri = redirect_uri
        self.calendar_api = calendar_api or GoogleCalendarAPI()
        self.logger = logger or logging.getLogger(__name__)
    
    def get_authorization_url(self, user_id: int) -> Dict[str, str]:
        """
        Generate OAuth2 authorization URL for Google Calendar access.
        
        Args:
            user_id: ID of the user requesting authorization
            
        Returns:
            Dict containing 'url' key with the authorization URL
            
        Raises:
            ValidationException: If client secrets file is not found
            ExternalServiceException: If URL generation fails
        """
        try:
            # Validate client secrets file exists
            if not os.path.exists(self.client_secrets_path):
                raise ValidationException(f"Client secrets file not found at {self.client_secrets_path}")
            
            # Create OAuth2 flow
            flow = Flow.from_client_secrets_file(
                self.client_secrets_path,
                scopes=self.SCOPES
            )
            flow.redirect_uri = self.redirect_uri
            
            # Generate authorization URL with offline access
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Store state for later validation
            integration = self._get_or_create_integration(user_id)
            integration.status = 'pending'
            integration.data = json.dumps({'state': state})
            integration.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return {'url': authorization_url}
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error generating authorization URL: {str(e)}")
            raise ExternalServiceException("Failed to generate authorization URL")
    
    def handle_oauth_callback(self, user_id: int, code: str, state: str) -> Dict[str, Any]:
        """
        Handle OAuth2 callback and exchange code for credentials.
        
        Args:
            user_id: ID of the user
            code: Authorization code from OAuth callback
            state: State token for CSRF protection
            
        Returns:
            Dict with success status and message
            
        Raises:
            NotFoundException: If integration not found
            ValidationException: If state mismatch or invalid code
            ExternalServiceException: If token exchange fails
        """
        try:
            # Get stored state for validation
            integration = self._get_integration(user_id)
            if not integration:
                raise NotFoundException(f"No integration found for user {user_id}")
            
            stored_data = json.loads(integration.data or '{}')
            stored_state = stored_data.get('state')
            
            if stored_state != state:
                raise ValidationException("Invalid state token")
            
            # Create flow and exchange code for credentials
            flow = Flow.from_client_secrets_file(
                self.client_secrets_path,
                scopes=self.SCOPES,
                state=state
            )
            flow.redirect_uri = self.redirect_uri
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Store credentials
            self._store_credentials(integration, credentials)
            
            return {
                'success': True,
                'message': 'Google Calendar connected successfully'
            }
            
        except (NotFoundException, ValidationException):
            raise
        except Exception as e:
            self.logger.error(f"Error handling OAuth callback: {str(e)}")
            raise ExternalServiceException("Failed to complete authorization")
    
    def create_event(self, user_id: int, event: CalendarEvent) -> Dict[str, str]:
        """
        Create a calendar event in Google Calendar.
        
        Args:
            user_id: ID of the user
            event: CalendarEvent object with event details
            
        Returns:
            Dict containing 'event_id' of the created event
            
        Raises:
            NotFoundException: If user has no active integration
            ValidationException: If event data is invalid
            ExternalServiceException: If event creation fails
        """
        try:
            # Validate event data
            self._validate_event(event)
            
            # Get credentials and build service
            credentials = self._get_credentials(user_id)
            if not credentials:
                raise NotFoundException("Google Calendar not connected")
            
            service = self.calendar_api.build_service(credentials)
            
            # Build event body
            event_body = self._build_event_body(event)
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()
            
            return {'event_id': created_event.get('id')}
            
        except (NotFoundException, ValidationException):
            raise
        except HttpError as e:
            self.logger.error(f"Google Calendar API error: {str(e)}")
            raise ExternalServiceException(f"Failed to create calendar event: {e.reason}")
        except Exception as e:
            self.logger.error(f"Error creating calendar event: {str(e)}")
            raise ExternalServiceException("Failed to create calendar event")
    
    def update_event(self, user_id: int, event_id: str, event: CalendarEvent) -> Dict[str, str]:
        """
        Update an existing calendar event.
        
        Args:
            user_id: ID of the user
            event_id: Google Calendar event ID
            event: CalendarEvent object with updated details
            
        Returns:
            Dict with success message
            
        Raises:
            NotFoundException: If user has no active integration or event not found
            ValidationException: If event data is invalid
            ExternalServiceException: If event update fails
        """
        try:
            # Validate event data
            self._validate_event(event)
            
            # Get credentials and build service
            credentials = self._get_credentials(user_id)
            if not credentials:
                raise NotFoundException("Google Calendar not connected")
            
            service = self.calendar_api.build_service(credentials)
            
            # Get existing event
            try:
                existing_event = service.events().get(
                    calendarId='primary',
                    eventId=event_id
                ).execute()
            except HttpError as e:
                if e.resp.status == 404:
                    raise NotFoundException(f"Calendar event {event_id} not found")
                raise
            
            # Update event body
            updated_body = self._build_event_body(event)
            
            # Preserve some fields from existing event
            updated_body['id'] = existing_event['id']
            updated_body['etag'] = existing_event.get('etag')
            
            # Update the event
            service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=updated_body
            ).execute()
            
            return {'message': 'Event updated successfully'}
            
        except (NotFoundException, ValidationException):
            raise
        except HttpError as e:
            self.logger.error(f"Google Calendar API error: {str(e)}")
            raise ExternalServiceException(f"Failed to update calendar event: {e.reason}")
        except Exception as e:
            self.logger.error(f"Error updating calendar event: {str(e)}")
            raise ExternalServiceException("Failed to update calendar event")
    
    def delete_event(self, user_id: int, event_id: str) -> Dict[str, str]:
        """
        Delete a calendar event from Google Calendar.
        
        Args:
            user_id: ID of the user
            event_id: Google Calendar event ID
            
        Returns:
            Dict with success message
            
        Raises:
            NotFoundException: If user has no active integration
            ExternalServiceException: If event deletion fails
        """
        try:
            # Get credentials and build service
            credentials = self._get_credentials(user_id)
            if not credentials:
                raise NotFoundException("Google Calendar not connected")
            
            service = self.calendar_api.build_service(credentials)
            
            # Delete the event
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return {'message': 'Event deleted successfully'}
            
        except NotFoundException:
            raise
        except HttpError as e:
            # Ignore 404 errors (event already deleted)
            if e.resp.status != 404:
                self.logger.error(f"Google Calendar API error: {str(e)}")
                raise ExternalServiceException(f"Failed to delete calendar event: {e.reason}")
            return {'message': 'Event already deleted'}
        except Exception as e:
            self.logger.error(f"Error deleting calendar event: {str(e)}")
            raise ExternalServiceException("Failed to delete calendar event")
    
    def get_events(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Retrieve calendar events from Google Calendar.
        
        Args:
            user_id: ID of the user
            start_time: Start of time range (defaults to now)
            end_time: End of time range
            max_results: Maximum number of events to return
            
        Returns:
            Dict containing 'events' list with event details
            
        Raises:
            NotFoundException: If user has no active integration
            ExternalServiceException: If event retrieval fails
        """
        try:
            # Get credentials and build service
            credentials = self._get_credentials(user_id)
            if not credentials:
                raise NotFoundException("Google Calendar not connected")
            
            service = self.calendar_api.build_service(credentials)
            
            # Build query parameters
            params = {
                'calendarId': 'primary',
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if start_time:
                params['timeMin'] = start_time.isoformat() + 'Z'
            
            if end_time:
                params['timeMax'] = end_time.isoformat() + 'Z'
            
            # Get events
            events_result = service.events().list(**params).execute()
            events = events_result.get('items', [])
            
            # Transform events to standardized format
            transformed_events = [
                self._transform_event(event) for event in events
            ]
            
            return {'events': transformed_events}
            
        except NotFoundException:
            raise
        except HttpError as e:
            self.logger.error(f"Google Calendar API error: {str(e)}")
            raise ExternalServiceException(f"Failed to retrieve calendar events: {e.reason}")
        except Exception as e:
            self.logger.error(f"Error retrieving calendar events: {str(e)}")
            raise ExternalServiceException("Failed to retrieve calendar events")
    
    def is_connected(self, user_id: int) -> bool:
        """
        Check if user has active Google Calendar integration.
        
        Args:
            user_id: ID of the user
            
        Returns:
            True if connected, False otherwise
        """
        integration = self._get_integration(user_id)
        return integration is not None and integration.status == 'active'
    
    def disconnect(self, user_id: int) -> Dict[str, str]:
        """
        Disconnect user's Google Calendar integration.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict with success message
            
        Raises:
            NotFoundException: If no integration found
        """
        integration = self._get_integration(user_id)
        if not integration:
            raise NotFoundException("Google Calendar integration not found")
        
        # Update integration status
        integration.status = 'disconnected'
        integration.data = None
        integration.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {'message': 'Google Calendar disconnected successfully'}
    
    # Private helper methods
    
    def _get_integration(self, user_id: int) -> Optional[UserIntegration]:
        """Get user's calendar integration."""
        return self.db.query(UserIntegration).filter_by(
            user_id=user_id,
            provider=self.PROVIDER_NAME
        ).first()
    
    def _get_or_create_integration(self, user_id: int) -> UserIntegration:
        """Get or create user's calendar integration."""
        integration = self._get_integration(user_id)
        
        if not integration:
            integration = UserIntegration(
                user_id=user_id,
                provider=self.PROVIDER_NAME,
                status='pending',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(integration)
            self.db.flush()
        
        return integration
    
    def _get_credentials(self, user_id: int) -> Optional[Credentials]:
        """Get OAuth2 credentials for user."""
        integration = self._get_integration(user_id)
        
        if not integration or integration.status != 'active':
            return None
        
        try:
            data = json.loads(integration.data or '{}')
            
            credentials = Credentials(
                token=data.get('token'),
                refresh_token=data.get('refresh_token'),
                token_uri=data.get('token_uri'),
                client_id=data.get('client_id'),
                client_secret=data.get('client_secret'),
                scopes=data.get('scopes')
            )
            
            if data.get('expiry'):
                credentials.expiry = datetime.fromisoformat(data.get('expiry'))
            
            # TODO: Implement token refresh logic here if needed
            # if credentials.expired and credentials.refresh_token:
            #     credentials.refresh(Request())
            #     self._store_credentials(integration, credentials)
            
            return credentials
            
        except Exception as e:
            self.logger.error(f"Error loading credentials: {str(e)}")
            return None
    
    def _store_credentials(self, integration: UserIntegration, credentials: Credentials) -> None:
        """Store OAuth2 credentials in database."""
        integration.status = 'active'
        integration.data = json.dumps({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        })
        integration.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    def _validate_event(self, event: CalendarEvent) -> None:
        """Validate calendar event data."""
        if not event.title:
            raise ValidationException("Event title is required")
        
        if event.start_time >= event.end_time:
            raise ValidationException("Start time must be before end time")
        
        if event.start_time < datetime.utcnow():
            raise ValidationException("Cannot create events in the past")
    
    def _build_event_body(self, event: CalendarEvent) -> Dict[str, Any]:
        """Build Google Calendar event body from CalendarEvent."""
        body = {
            'summary': event.title,
            'description': event.description or '',
            'start': {
                'dateTime': event.start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event.end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [{'email': email} for email in event.attendees],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        if event.location:
            body['location'] = event.location
        
        return body
    
    def _transform_event(self, google_event: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Google Calendar event to standardized format."""
        # Extract start and end times
        start = google_event.get('start', {})
        end = google_event.get('end', {})
        
        start_time = start.get('dateTime') or start.get('date')
        end_time = end.get('dateTime') or end.get('date')
        
        # Extract attendees
        attendees = [
            attendee.get('email')
            for attendee in google_event.get('attendees', [])
            if attendee.get('email')
        ]
        
        return {
            'id': google_event.get('id'),
            'title': google_event.get('summary', ''),
            'description': google_event.get('description'),
            'location': google_event.get('location'),
            'start_time': start_time,
            'end_time': end_time,
            'attendees': attendees,
            'status': google_event.get('status'),
            'html_link': google_event.get('htmlLink')
        }