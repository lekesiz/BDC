"""Zoom video conference provider implementation."""

import json
import jwt
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


class ZoomProvider(VideoConferenceProviderInterface):
    """Zoom video conference provider implementation."""
    
    def __init__(self):
        """Initialize Zoom provider with configuration."""
        self.api_key = current_app.config.get('ZOOM_API_KEY')
        self.api_secret = current_app.config.get('ZOOM_API_SECRET')
        self.account_id = current_app.config.get('ZOOM_ACCOUNT_ID')
        self.base_url = 'https://api.zoom.us/v2'
        self._access_token = None
        self._token_expires_at = None
        
        if not self.validate_configuration():
            raise ProviderConfigurationError("Zoom provider configuration is invalid")
    
    def validate_configuration(self) -> bool:
        """Validate Zoom configuration."""
        required_configs = ['ZOOM_API_KEY', 'ZOOM_API_SECRET', 'ZOOM_ACCOUNT_ID']
        for config in required_configs:
            if not current_app.config.get(config):
                logger.error(f"Missing Zoom configuration: {config}")
                return False
        return True
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported Zoom features."""
        return [
            'create_meeting',
            'update_meeting',
            'delete_meeting',
            'get_meeting_info',
            'start_recording',
            'stop_recording',
            'get_recordings',
            'add_participants',
            'remove_participant',
            'get_meeting_participants',
            'send_invitation',
            'get_meeting_analytics'
        ]
    
    def _get_access_token(self) -> str:
        """Get or refresh access token for Zoom API."""
        try:
            # Check if we have a valid token
            if self._access_token and self._token_expires_at:
                if datetime.utcnow() < self._token_expires_at - timedelta(minutes=5):
                    return self._access_token
            
            # Generate JWT for OAuth
            payload = {
                'iss': self.api_key,
                'exp': datetime.utcnow() + timedelta(hours=1),
                'iat': datetime.utcnow(),
                'aud': 'zoom',
                'appKey': self.api_key,
                'tokenExp': (datetime.utcnow() + timedelta(hours=1)).timestamp(),
                'alg': 'HS256'
            }
            
            token = jwt.encode(payload, self.api_secret, algorithm='HS256')
            
            # Use OAuth 2.0 with JWT
            oauth_url = 'https://zoom.us/oauth/token'
            headers = {
                'Authorization': f'Basic {self.api_key}:{self.api_secret}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'account_credentials',
                'account_id': self.account_id
            }
            
            response = requests.post(oauth_url, headers=headers, data=data)
            response.raise_for_status()
            
            oauth_data = response.json()
            self._access_token = oauth_data['access_token']
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=oauth_data['expires_in'])
            
            return self._access_token
            
        except Exception as e:
            logger.error(f"Error getting Zoom access token: {str(e)}")
            raise ProviderAuthenticationError(f"Failed to authenticate with Zoom: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Zoom API."""
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
                raise ProviderRateLimitError("Zoom API rate limit exceeded")
            
            response.raise_for_status()
            return response.json() if response.content else {}
        
        except requests.exceptions.Timeout:
            raise ProviderAPIError("Zoom API request timed out")
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', str(e))
                except:
                    error_message = str(e)
            else:
                error_message = str(e)
            
            logger.error(f"Zoom API request failed: {error_message}")
            raise ProviderAPIError(f"Zoom API error: {error_message}")
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Zoom meeting."""
        try:
            zoom_data = {
                'topic': meeting_data['title'],
                'type': 2,  # Scheduled meeting
                'start_time': meeting_data['start_time'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                'duration': meeting_data.get('duration_minutes', 60),
                'timezone': 'UTC',
                'agenda': meeting_data.get('description', ''),
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'cn_meeting': False,
                    'in_meeting': False,
                    'join_before_host': meeting_data.get('join_before_host', False),
                    'mute_upon_entry': True,
                    'watermark': False,
                    'use_pmi': False,
                    'approval_type': 2,  # Automatically approve
                    'audio': 'both',
                    'auto_recording': 'cloud' if meeting_data.get('auto_record') else 'none',
                    'enforce_login': meeting_data.get('require_authentication', False),
                    'enforce_login_domains': '',
                    'alternative_hosts': '',
                    'close_registration': False,
                    'show_share_button': True,
                    'allow_multiple_devices': True,
                    'registrants_confirmation_email': True,
                    'waiting_room': meeting_data.get('waiting_room_enabled', True),
                    'registrants_email_notification': True,
                    'meeting_authentication': meeting_data.get('require_authentication', False),
                    'encryption_type': 'enhanced_encryption'
                }
            }
            
            # Add password if specified
            if meeting_data.get('meeting_password'):
                zoom_data['password'] = meeting_data['meeting_password']
            
            # Add recurrence if specified
            if meeting_data.get('recurrence'):
                zoom_data['recurrence'] = meeting_data['recurrence']
            
            result = self._make_request('POST', '/users/me/meetings', zoom_data)
            
            return {
                'meeting_id': str(result['id']),
                'meeting_url': result['join_url'],
                'start_url': result['start_url'],
                'meeting_password': result.get('password', ''),
                'provider_data': {
                    'zoom_meeting_id': result['id'],
                    'uuid': result.get('uuid'),
                    'host_id': result.get('host_id'),
                    'settings': result.get('settings', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating Zoom meeting: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            raise ProviderAPIError(f"Failed to create Zoom meeting: {str(e)}")
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Zoom meeting."""
        try:
            zoom_data = {}
            
            if 'title' in meeting_data:
                zoom_data['topic'] = meeting_data['title']
            if 'start_time' in meeting_data:
                zoom_data['start_time'] = meeting_data['start_time'].strftime('%Y-%m-%dT%H:%M:%SZ')
            if 'duration_minutes' in meeting_data:
                zoom_data['duration'] = meeting_data['duration_minutes']
            if 'description' in meeting_data:
                zoom_data['agenda'] = meeting_data['description']
            
            # Update settings if provided
            if any(key in meeting_data for key in ['waiting_room_enabled', 'require_authentication', 'auto_record']):
                settings = {}
                if 'waiting_room_enabled' in meeting_data:
                    settings['waiting_room'] = meeting_data['waiting_room_enabled']
                if 'require_authentication' in meeting_data:
                    settings['enforce_login'] = meeting_data['require_authentication']
                if 'auto_record' in meeting_data:
                    settings['auto_recording'] = 'cloud' if meeting_data['auto_record'] else 'none'
                zoom_data['settings'] = settings
            
            result = self._make_request('PATCH', f'/meetings/{meeting_id}', zoom_data)
            
            return {
                'success': True,
                'provider_data': result,
                'updated_fields': list(zoom_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Error updating Zoom meeting: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            raise ProviderAPIError(f"Failed to update Zoom meeting: {str(e)}")
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a Zoom meeting."""
        try:
            self._make_request('DELETE', f'/meetings/{meeting_id}')
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Zoom meeting: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            return False
    
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """Get Zoom meeting information."""
        try:
            return self._make_request('GET', f'/meetings/{meeting_id}')
            
        except Exception as e:
            logger.error(f"Error getting Zoom meeting info: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            raise ProviderAPIError(f"Failed to get Zoom meeting info: {str(e)}")
    
    def start_recording(self, meeting_id: str) -> bool:
        """Start recording a Zoom meeting."""
        try:
            self._make_request('PATCH', f'/meetings/{meeting_id}/recordings/status', {
                'action': 'start'
            })
            return True
            
        except Exception as e:
            logger.error(f"Error starting Zoom recording: {str(e)}")
            return False
    
    def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording a Zoom meeting."""
        try:
            self._make_request('PATCH', f'/meetings/{meeting_id}/recordings/status', {
                'action': 'stop'
            })
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Zoom recording: {str(e)}")
            return False
    
    def get_recordings(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get recordings for a Zoom meeting."""
        try:
            result = self._make_request('GET', f'/meetings/{meeting_id}/recordings')
            recordings = []
            
            for recording_file in result.get('recording_files', []):
                recordings.append({
                    'id': recording_file.get('id'),
                    'meeting_id': recording_file.get('meeting_id'),
                    'recording_start': recording_file.get('recording_start'),
                    'recording_end': recording_file.get('recording_end'),
                    'file_type': recording_file.get('file_type'),
                    'file_size': recording_file.get('file_size'),
                    'download_url': recording_file.get('download_url'),
                    'play_url': recording_file.get('play_url'),
                    'recording_type': recording_file.get('recording_type'),
                    'status': recording_file.get('status')
                })
            
            return recordings
            
        except Exception as e:
            logger.error(f"Error getting Zoom recordings: {str(e)}")
            return []
    
    def add_participants(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """Add participants to a Zoom meeting."""
        try:
            # Zoom doesn't have a direct API to add participants to a scheduled meeting
            # This would typically be handled through meeting invitations
            return self.send_invitation(meeting_id, participants)
            
        except Exception as e:
            logger.error(f"Error adding participants to Zoom meeting: {str(e)}")
            return False
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get current Zoom meeting participants."""
        try:
            # Get live meeting participants
            result = self._make_request('GET', f'/meetings/{meeting_id}/participants')
            participants = []
            
            for participant in result.get('participants', []):
                participants.append({
                    'id': participant.get('id'),
                    'user_id': participant.get('user_id'),
                    'name': participant.get('name'),
                    'user_email': participant.get('user_email'),
                    'join_time': participant.get('join_time'),
                    'leave_time': participant.get('leave_time'),
                    'duration': participant.get('duration'),
                    'status': participant.get('status')
                })
            
            return participants
            
        except Exception as e:
            logger.error(f"Error getting Zoom meeting participants: {str(e)}")
            return []
    
    def send_invitation(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """Send meeting invitations via Zoom."""
        try:
            # Get meeting info to include in invitation
            meeting_info = self.get_meeting_info(meeting_id)
            
            for participant in participants:
                email = participant.get('email')
                if not email:
                    continue
                
                # Zoom automatically sends invitations when you add registrants
                # or when the meeting is created with attendees
                registrant_data = {
                    'email': email,
                    'first_name': participant.get('first_name', ''),
                    'last_name': participant.get('last_name', ''),
                }
                
                try:
                    self._make_request('POST', f'/meetings/{meeting_id}/registrants', registrant_data)
                except Exception as e:
                    logger.warning(f"Failed to register participant {email}: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending Zoom invitations: {str(e)}")
            return False
    
    def get_meeting_analytics(self, meeting_id: str) -> Dict[str, Any]:
        """Get Zoom meeting analytics."""
        try:
            # Get meeting details
            meeting_info = self.get_meeting_info(meeting_id)
            participants = self.get_meeting_participants(meeting_id)
            
            analytics = {
                'meeting_id': meeting_id,
                'total_participants': len(participants),
                'duration_minutes': meeting_info.get('duration', 0),
                'start_time': meeting_info.get('start_time'),
                'timezone': meeting_info.get('timezone'),
                'participants_summary': []
            }
            
            for participant in participants:
                analytics['participants_summary'].append({
                    'name': participant.get('name'),
                    'email': participant.get('user_email'),
                    'join_time': participant.get('join_time'),
                    'leave_time': participant.get('leave_time'),
                    'duration': participant.get('duration')
                })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting Zoom meeting analytics: {str(e)}")
            return {}
    
    def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Remove a participant from a Zoom meeting."""
        try:
            # Zoom doesn't have a direct API to remove participants from a live meeting
            # This would need to be handled through the Zoom client or by the host
            logger.warning("Remove participant not directly supported by Zoom API")
            return False
            
        except Exception as e:
            logger.error(f"Error removing participant from Zoom meeting: {str(e)}")
            return False