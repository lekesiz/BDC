"""Google Meet video conference provider implementation."""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base_provider import (
    VideoConferenceProviderInterface,
    ProviderError,
    ProviderConfigurationError,
    ProviderAPIError,
    ProviderAuthenticationError
)

logger = logging.getLogger(__name__)


class GoogleMeetProvider(VideoConferenceProviderInterface):
    """Google Meet video conference provider implementation."""
    
    def __init__(self):
        """Initialize Google Meet provider with configuration."""
        self.client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        self.client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        self.refresh_token = current_app.config.get('GOOGLE_REFRESH_TOKEN')
        self.credentials = None
        
        if not self.validate_configuration():
            raise ProviderConfigurationError("Google Meet provider configuration is invalid")
        
        self._setup_credentials()
    
    def validate_configuration(self) -> bool:
        """Validate Google Meet configuration."""
        required_configs = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
        for config in required_configs:
            if not current_app.config.get(config):
                logger.error(f"Missing Google Meet configuration: {config}")
                return False
        return True
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported Google Meet features."""
        return [
            'create_meeting',
            'update_meeting',
            'delete_meeting',
            'get_meeting_info',
            'add_participants',
            'send_invitation',
            'get_meeting_analytics'
        ]
    
    def _setup_credentials(self):
        """Setup Google OAuth2 credentials."""
        try:
            if self.refresh_token:
                self.credentials = Credentials(
                    token=None,
                    refresh_token=self.refresh_token,
                    id_token=None,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                
                # Refresh the token
                self.credentials.refresh(Request())
            else:
                logger.warning("No Google refresh token provided. Some features may not work.")
                
        except Exception as e:
            logger.error(f"Error setting up Google credentials: {str(e)}")
            raise ProviderAuthenticationError(f"Failed to authenticate with Google: {str(e)}")
    
    def _get_calendar_service(self):
        """Get Google Calendar service."""
        try:
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    raise ProviderAuthenticationError("Invalid Google credentials")
            
            return build('calendar', 'v3', credentials=self.credentials)
            
        except Exception as e:
            logger.error(f"Error getting Google Calendar service: {str(e)}")
            raise ProviderAPIError(f"Failed to get Google Calendar service: {str(e)}")
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Meet meeting."""
        try:
            service = self._get_calendar_service()
            
            # Prepare event data
            event = {
                'summary': meeting_data['title'],
                'description': meeting_data.get('description', ''),
                'start': {
                    'dateTime': meeting_data['start_time'].isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': meeting_data['end_time'].isoformat(),
                    'timeZone': 'UTC',
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet-{datetime.utcnow().timestamp()}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                },
                'attendees': [],
                'guestsCanInviteOthers': True,
                'guestsCanModify': False,
                'guestsCanSeeOtherGuests': True,
            }
            
            # Add attendees if provided
            if 'attendees' in meeting_data:
                for attendee in meeting_data['attendees']:
                    if isinstance(attendee, str):
                        event['attendees'].append({'email': attendee})
                    elif isinstance(attendee, dict) and 'email' in attendee:
                        event['attendees'].append({
                            'email': attendee['email'],
                            'displayName': attendee.get('name', ''),
                            'optional': attendee.get('optional', False)
                        })
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1
            ).execute()
            
            # Extract meeting information
            conference_data = created_event.get('conferenceData', {})
            entry_points = conference_data.get('entryPoints', [])
            
            meeting_url = None
            for entry_point in entry_points:
                if entry_point.get('entryPointType') == 'video':
                    meeting_url = entry_point.get('uri')
                    break
            
            if not meeting_url:
                # Fallback to hangoutLink if available
                meeting_url = created_event.get('hangoutLink')
            
            return {
                'meeting_id': created_event['id'],
                'meeting_url': meeting_url or '',
                'meeting_password': '',  # Google Meet doesn't use passwords
                'provider_data': {
                    'calendar_event_id': created_event['id'],
                    'conference_id': conference_data.get('conferenceId'),
                    'entry_points': entry_points,
                    'created_event': created_event
                }
            }
            
        except HttpError as e:
            logger.error(f"Google API error creating meeting: {str(e)}")
            raise ProviderAPIError(f"Google Meet API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating Google Meet meeting: {str(e)}")
            raise ProviderAPIError(f"Failed to create Google Meet meeting: {str(e)}")
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Google Meet meeting."""
        try:
            service = self._get_calendar_service()
            
            # Get existing event
            existing_event = service.events().get(
                calendarId='primary',
                eventId=meeting_id
            ).execute()
            
            # Update fields
            if 'title' in meeting_data:
                existing_event['summary'] = meeting_data['title']
            if 'description' in meeting_data:
                existing_event['description'] = meeting_data['description']
            if 'start_time' in meeting_data:
                existing_event['start'] = {
                    'dateTime': meeting_data['start_time'].isoformat(),
                    'timeZone': 'UTC',
                }
            if 'end_time' in meeting_data:
                existing_event['end'] = {
                    'dateTime': meeting_data['end_time'].isoformat(),
                    'timeZone': 'UTC',
                }
            
            # Update attendees if provided
            if 'attendees' in meeting_data:
                existing_event['attendees'] = []
                for attendee in meeting_data['attendees']:
                    if isinstance(attendee, str):
                        existing_event['attendees'].append({'email': attendee})
                    elif isinstance(attendee, dict) and 'email' in attendee:
                        existing_event['attendees'].append({
                            'email': attendee['email'],
                            'displayName': attendee.get('name', ''),
                            'optional': attendee.get('optional', False)
                        })
            
            # Update the event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=meeting_id,
                body=existing_event
            ).execute()
            
            return {
                'success': True,
                'provider_data': updated_event,
                'updated_fields': list(meeting_data.keys())
            }
            
        except HttpError as e:
            logger.error(f"Google API error updating meeting: {str(e)}")
            raise ProviderAPIError(f"Google Meet API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating Google Meet meeting: {str(e)}")
            raise ProviderAPIError(f"Failed to update Google Meet meeting: {str(e)}")
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a Google Meet meeting."""
        try:
            service = self._get_calendar_service()
            
            service.events().delete(
                calendarId='primary',
                eventId=meeting_id
            ).execute()
            
            return True
            
        except HttpError as e:
            logger.error(f"Google API error deleting meeting: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error deleting Google Meet meeting: {str(e)}")
            return False
    
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """Get Google Meet meeting information."""
        try:
            service = self._get_calendar_service()
            
            event = service.events().get(
                calendarId='primary',
                eventId=meeting_id
            ).execute()
            
            return {
                'id': event['id'],
                'title': event.get('summary', ''),
                'description': event.get('description', ''),
                'start_time': event.get('start', {}).get('dateTime'),
                'end_time': event.get('end', {}).get('dateTime'),
                'meeting_url': event.get('hangoutLink', ''),
                'attendees': event.get('attendees', []),
                'status': event.get('status', 'confirmed'),
                'created': event.get('created'),
                'updated': event.get('updated')
            }
            
        except HttpError as e:
            logger.error(f"Google API error getting meeting info: {str(e)}")
            raise ProviderAPIError(f"Google Meet API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting Google Meet meeting info: {str(e)}")
            raise ProviderAPIError(f"Failed to get Google Meet meeting info: {str(e)}")
    
    def start_recording(self, meeting_id: str) -> bool:
        """Start recording a Google Meet meeting."""
        # Google Meet recording is controlled by the host during the meeting
        # and cannot be started programmatically via API
        logger.warning("Google Meet recording cannot be started programmatically")
        return False
    
    def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording a Google Meet meeting."""
        # Google Meet recording is controlled by the host during the meeting
        # and cannot be stopped programmatically via API
        logger.warning("Google Meet recording cannot be stopped programmatically")
        return False
    
    def get_recordings(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get recordings for a Google Meet meeting."""
        # Google Meet recordings are saved to Google Drive
        # This would require Drive API integration
        logger.warning("Google Meet recordings retrieval not implemented")
        return []
    
    def add_participants(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """Add participants to a Google Meet meeting."""
        try:
            service = self._get_calendar_service()
            
            # Get existing event
            event = service.events().get(
                calendarId='primary',
                eventId=meeting_id
            ).execute()
            
            # Add new attendees
            existing_attendees = event.get('attendees', [])
            existing_emails = {att.get('email') for att in existing_attendees}
            
            for participant in participants:
                email = participant.get('email')
                if email and email not in existing_emails:
                    existing_attendees.append({
                        'email': email,
                        'displayName': participant.get('name', ''),
                        'optional': participant.get('optional', False)
                    })
            
            # Update event with new attendees
            event['attendees'] = existing_attendees
            service.events().update(
                calendarId='primary',
                eventId=meeting_id,
                body=event,
                sendUpdates='all'  # Send email updates to all attendees
            ).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding participants to Google Meet: {str(e)}")
            return False
    
    def send_invitation(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """Send meeting invitations via Google Calendar."""
        try:
            # Adding participants automatically sends invitations
            return self.add_participants(meeting_id, participants)
            
        except Exception as e:
            logger.error(f"Error sending Google Meet invitations: {str(e)}")
            return False
    
    def get_meeting_analytics(self, meeting_id: str) -> Dict[str, Any]:
        """Get Google Meet meeting analytics."""
        try:
            # Get basic meeting info
            meeting_info = self.get_meeting_info(meeting_id)
            
            analytics = {
                'meeting_id': meeting_id,
                'title': meeting_info.get('title'),
                'scheduled_start': meeting_info.get('start_time'),
                'scheduled_end': meeting_info.get('end_time'),
                'total_invited': len(meeting_info.get('attendees', [])),
                'attendees_summary': []
            }
            
            for attendee in meeting_info.get('attendees', []):
                analytics['attendees_summary'].append({
                    'email': attendee.get('email'),
                    'name': attendee.get('displayName', ''),
                    'response_status': attendee.get('responseStatus', 'needsAction'),
                    'optional': attendee.get('optional', False)
                })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting Google Meet analytics: {str(e)}")
            return {}
    
    def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Remove a participant from a Google Meet meeting."""
        try:
            service = self._get_calendar_service()
            
            # Get existing event
            event = service.events().get(
                calendarId='primary',
                eventId=meeting_id
            ).execute()
            
            # Remove attendee by email (participant_id should be email)
            attendees = event.get('attendees', [])
            updated_attendees = [
                att for att in attendees 
                if att.get('email') != participant_id
            ]
            
            if len(updated_attendees) < len(attendees):
                event['attendees'] = updated_attendees
                service.events().update(
                    calendarId='primary',
                    eventId=meeting_id,
                    body=event,
                    sendUpdates='all'
                ).execute()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing participant from Google Meet: {str(e)}")
            return False
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get current Google Meet meeting participants."""
        try:
            # Google Meet doesn't provide real-time participant data via API
            # Return scheduled attendees instead
            meeting_info = self.get_meeting_info(meeting_id)
            
            participants = []
            for attendee in meeting_info.get('attendees', []):
                participants.append({
                    'email': attendee.get('email'),
                    'name': attendee.get('displayName', ''),
                    'response_status': attendee.get('responseStatus', 'needsAction'),
                    'optional': attendee.get('optional', False)
                })
            
            return participants
            
        except Exception as e:
            logger.error(f"Error getting Google Meet participants: {str(e)}")
            return []