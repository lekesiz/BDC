"""Microsoft Teams video conference provider implementation."""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app

from .base_provider import (
    VideoConferenceProviderInterface,
    ProviderError,
    ProviderConfigurationError,
    ProviderAPIError,
    ProviderAuthenticationError,
    ProviderRateLimitError
)

logger = logging.getLogger(__name__)


class MicrosoftTeamsProvider(VideoConferenceProviderInterface):
    """Microsoft Teams video conference provider implementation."""
    
    def __init__(self):
        """Initialize Microsoft Teams provider with configuration."""
        self.client_id = current_app.config.get('TEAMS_CLIENT_ID')
        self.client_secret = current_app.config.get('TEAMS_CLIENT_SECRET')
        self.tenant_id = current_app.config.get('TEAMS_TENANT_ID')
        self.base_url = 'https://graph.microsoft.com/v1.0'
        self._access_token = None
        self._token_expires_at = None
        
        if not self.validate_configuration():
            raise ProviderConfigurationError("Microsoft Teams provider configuration is invalid")
    
    def validate_configuration(self) -> bool:
        """Validate Microsoft Teams configuration."""
        required_configs = ['TEAMS_CLIENT_ID', 'TEAMS_CLIENT_SECRET', 'TEAMS_TENANT_ID']
        for config in required_configs:
            if not current_app.config.get(config):
                logger.error(f"Missing Teams configuration: {config}")
                return False
        return True
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported Microsoft Teams features."""
        return [
            'create_meeting',
            'update_meeting',
            'delete_meeting',
            'get_meeting_info',
            'add_participants',
            'send_invitation',
            'get_meeting_analytics',
            'get_meeting_participants'
        ]
    
    def _get_access_token(self) -> str:
        """Get or refresh access token for Microsoft Graph API."""
        try:
            # Check if we have a valid token
            if self._access_token and self._token_expires_at:
                if datetime.utcnow() < self._token_expires_at - timedelta(minutes=5):
                    return self._access_token
            
            # Get new token using client credentials flow
            token_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data['access_token']
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
            
            return self._access_token
            
        except Exception as e:
            logger.error(f"Error getting Teams access token: {str(e)}")
            raise ProviderAuthenticationError(f"Failed to authenticate with Microsoft Teams: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Microsoft Graph API."""
        access_token = self._get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ProviderAPIError(f"Unsupported HTTP method: {method}")
            
            # Handle rate limiting
            if response.status_code == 429:
                raise ProviderRateLimitError("Microsoft Graph API rate limit exceeded")
            
            response.raise_for_status()
            return response.json() if response.content else {}
        
        except requests.exceptions.Timeout:
            raise ProviderAPIError("Microsoft Graph API request timed out")
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', str(e))
                except:
                    error_message = str(e)
            else:
                error_message = str(e)
            
            logger.error(f"Teams API request failed: {error_message}")
            raise ProviderAPIError(f"Microsoft Teams API error: {error_message}")
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Microsoft Teams meeting."""
        try:
            # Create online meeting
            teams_data = {
                'subject': meeting_data['title'],
                'startDateTime': meeting_data['start_time'].isoformat() + 'Z',
                'endDateTime': meeting_data['end_time'].isoformat() + 'Z',
                'participants': {
                    'attendees': []
                }
            }
            
            # Add attendees if provided
            if 'attendees' in meeting_data:
                for attendee in meeting_data['attendees']:
                    if isinstance(attendee, str):
                        teams_data['participants']['attendees'].append({
                            'upn': attendee
                        })
                    elif isinstance(attendee, dict) and 'email' in attendee:
                        teams_data['participants']['attendees'].append({
                            'upn': attendee['email']
                        })
            
            # Add meeting settings
            teams_data['allowedPresenters'] = 'everyone'
            teams_data['allowMeetingChat'] = 'enabled'
            teams_data['allowTeamworkReactions'] = True
            
            if meeting_data.get('require_authentication'):
                teams_data['lobbyBypassSettings'] = {
                    'scope': 'organization',
                    'isDialInBypassEnabled': False
                }
            else:
                teams_data['lobbyBypassSettings'] = {
                    'scope': 'everyone',
                    'isDialInBypassEnabled': True
                }
            
            # Create the meeting
            result = self._make_request('POST', '/me/onlineMeetings', teams_data)
            
            return {
                'meeting_id': result['id'],
                'meeting_url': result['joinWebUrl'],
                'meeting_password': '',  # Teams doesn't use passwords
                'provider_data': {
                    'teams_meeting_id': result['id'],
                    'join_web_url': result['joinWebUrl'],
                    'audio_conferencing': result.get('audioConferencing', {}),
                    'chat_info': result.get('chatInfo', {}),
                    'settings': result.get('lobbyBypassSettings', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating Teams meeting: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            raise ProviderAPIError(f"Failed to create Teams meeting: {str(e)}")
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Microsoft Teams meeting."""
        try:
            teams_data = {}
            
            if 'title' in meeting_data:
                teams_data['subject'] = meeting_data['title']
            if 'start_time' in meeting_data:
                teams_data['startDateTime'] = meeting_data['start_time'].isoformat() + 'Z'
            if 'end_time' in meeting_data:
                teams_data['endDateTime'] = meeting_data['end_time'].isoformat() + 'Z'
            
            # Update settings if provided
            if 'require_authentication' in meeting_data:
                if meeting_data['require_authentication']:
                    teams_data['lobbyBypassSettings'] = {
                        'scope': 'organization',
                        'isDialInBypassEnabled': False
                    }
                else:
                    teams_data['lobbyBypassSettings'] = {
                        'scope': 'everyone',
                        'isDialInBypassEnabled': True
                    }
            
            result = self._make_request('PATCH', f'/me/onlineMeetings/{meeting_id}', teams_data)
            
            return {
                'success': True,
                'provider_data': result,
                'updated_fields': list(teams_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Error updating Teams meeting: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            raise ProviderAPIError(f"Failed to update Teams meeting: {str(e)}")
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a Microsoft Teams meeting."""
        try:
            self._make_request('DELETE', f'/me/onlineMeetings/{meeting_id}')
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Teams meeting: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            return False
    
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """Get Microsoft Teams meeting information."""
        try:
            return self._make_request('GET', f'/me/onlineMeetings/{meeting_id}')
            
        except Exception as e:
            logger.error(f"Error getting Teams meeting info: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            raise ProviderAPIError(f"Failed to get Teams meeting info: {str(e)}")
    
    def start_recording(self, meeting_id: str) -> bool:
        """Start recording a Microsoft Teams meeting."""
        try:
            # Teams recording is typically controlled by the meeting organizer
            # and may require additional permissions
            logger.warning("Teams recording control via API requires additional setup")
            return False
            
        except Exception as e:
            logger.error(f"Error starting Teams recording: {str(e)}")
            return False
    
    def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording a Microsoft Teams meeting."""
        try:
            # Teams recording is typically controlled by the meeting organizer
            # and may require additional permissions
            logger.warning("Teams recording control via API requires additional setup")
            return False
            
        except Exception as e:
            logger.error(f"Error stopping Teams recording: {str(e)}")
            return False
    
    def get_recordings(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get recordings for a Microsoft Teams meeting."""
        try:
            # Teams recordings are typically stored in SharePoint/OneDrive
            # This would require additional API calls to get recording files
            logger.warning("Teams recordings retrieval requires SharePoint/OneDrive integration")
            return []
            
        except Exception as e:
            logger.error(f"Error getting Teams recordings: {str(e)}")
            return []
    
    def add_participants(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """Add participants to a Microsoft Teams meeting."""
        try:
            # Get current meeting info
            meeting_info = self.get_meeting_info(meeting_id)
            
            # Extract current attendees
            current_attendees = meeting_info.get('participants', {}).get('attendees', [])
            
            # Add new participants
            for participant in participants:
                email = participant.get('email')
                if email:
                    # Check if participant already exists
                    exists = any(att.get('upn') == email for att in current_attendees)
                    if not exists:
                        current_attendees.append({'upn': email})
            
            # Update meeting with new attendees
            update_data = {
                'participants': {
                    'attendees': current_attendees
                }
            }
            
            self._make_request('PATCH', f'/me/onlineMeetings/{meeting_id}', update_data)
            return True
            
        except Exception as e:
            logger.error(f"Error adding participants to Teams meeting: {str(e)}")
            return False
    
    def send_invitation(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """Send meeting invitations via Microsoft Teams."""
        try:
            # Get meeting info to include in invitation
            meeting_info = self.get_meeting_info(meeting_id)
            
            # Create calendar event for each participant
            for participant in participants:
                email = participant.get('email')
                if not email:
                    continue
                
                # Create calendar event with Teams meeting
                event_data = {
                    'subject': meeting_info.get('subject', ''),
                    'start': {
                        'dateTime': meeting_info.get('startDateTime'),
                        'timeZone': 'UTC'
                    },
                    'end': {
                        'dateTime': meeting_info.get('endDateTime'),
                        'timeZone': 'UTC'
                    },
                    'attendees': [
                        {
                            'emailAddress': {
                                'address': email,
                                'name': participant.get('name', '')
                            }
                        }
                    ],
                    'onlineMeetingUrl': meeting_info.get('joinWebUrl'),
                    'isOnlineMeeting': True,
                    'onlineMeetingProvider': 'teamsForBusiness'
                }
                
                try:
                    self._make_request('POST', '/me/events', event_data)
                except Exception as e:
                    logger.warning(f"Failed to send invitation to {email}: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending Teams invitations: {str(e)}")
            return False
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get current Microsoft Teams meeting participants."""
        try:
            # Get meeting attendees from the meeting info
            meeting_info = self.get_meeting_info(meeting_id)
            attendees = meeting_info.get('participants', {}).get('attendees', [])
            
            participants = []
            for attendee in attendees:
                participants.append({
                    'email': attendee.get('upn'),
                    'identity': attendee.get('identity', {}),
                    'role': attendee.get('role', 'attendee')
                })
            
            return participants
            
        except Exception as e:
            logger.error(f"Error getting Teams meeting participants: {str(e)}")
            return []
    
    def get_meeting_analytics(self, meeting_id: str) -> Dict[str, Any]:
        """Get Microsoft Teams meeting analytics."""
        try:
            meeting_info = self.get_meeting_info(meeting_id)
            participants = self.get_meeting_participants(meeting_id)
            
            analytics = {
                'meeting_id': meeting_id,
                'subject': meeting_info.get('subject'),
                'start_time': meeting_info.get('startDateTime'),
                'end_time': meeting_info.get('endDateTime'),
                'join_web_url': meeting_info.get('joinWebUrl'),
                'total_participants': len(participants),
                'participants_summary': []
            }
            
            for participant in participants:
                analytics['participants_summary'].append({
                    'email': participant.get('email'),
                    'role': participant.get('role', 'attendee')
                })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting Teams meeting analytics: {str(e)}")
            return {}
    
    def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Remove a participant from a Microsoft Teams meeting."""
        try:
            # Get current meeting info
            meeting_info = self.get_meeting_info(meeting_id)
            current_attendees = meeting_info.get('participants', {}).get('attendees', [])
            
            # Remove participant by email (participant_id should be email)
            updated_attendees = [
                att for att in current_attendees 
                if att.get('upn') != participant_id
            ]
            
            if len(updated_attendees) < len(current_attendees):
                # Update meeting with removed participant
                update_data = {
                    'participants': {
                        'attendees': updated_attendees
                    }
                }
                
                self._make_request('PATCH', f'/me/onlineMeetings/{meeting_id}', update_data)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing participant from Teams meeting: {str(e)}")
            return False