"""WebRTC provider implementation for direct peer-to-peer video calls."""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import current_app

from .base_provider import (
    VideoConferenceProviderInterface,
    ProviderError,
    ProviderConfigurationError,
    ProviderAPIError
)

logger = logging.getLogger(__name__)


class WebRTCProvider(VideoConferenceProviderInterface):
    """WebRTC provider implementation for direct peer-to-peer video calls."""
    
    def __init__(self):
        """Initialize WebRTC provider with configuration."""
        self.ice_servers = current_app.config.get('WEBRTC_ICE_SERVERS', [
            {'urls': 'stun:stun.l.google.com:19302'},
            {'urls': 'stun:stun1.l.google.com:19302'}
        ])
        self.frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
        self.max_participants = current_app.config.get('WEBRTC_MAX_PARTICIPANTS', 10)
        self.recording_enabled = current_app.config.get('WEBRTC_RECORDING_ENABLED', True)
        
        # Store active rooms in memory (in production, use Redis or similar)
        self.active_rooms = {}
    
    def validate_configuration(self) -> bool:
        """Validate WebRTC configuration."""
        # WebRTC provider has minimal configuration requirements
        return True
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported WebRTC features."""
        features = [
            'create_meeting',
            'update_meeting',
            'delete_meeting',
            'get_meeting_info',
            'add_participants',
            'remove_participant',
            'get_meeting_participants'
        ]
        
        if self.recording_enabled:
            features.extend(['start_recording', 'stop_recording', 'get_recordings'])
        
        return features
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a WebRTC meeting room."""
        try:
            # Generate unique room ID
            room_id = str(uuid.uuid4())
            
            # Generate optional room password
            room_password = meeting_data.get('meeting_password', '')
            if not room_password and meeting_data.get('require_authentication'):
                room_password = str(uuid.uuid4())[:8]
            
            # Create room configuration
            room_config = {
                'id': room_id,
                'title': meeting_data['title'],
                'description': meeting_data.get('description', ''),
                'start_time': meeting_data['start_time'].isoformat(),
                'end_time': meeting_data['end_time'].isoformat(),
                'password': room_password,
                'max_participants': min(
                    meeting_data.get('max_participants', self.max_participants),
                    self.max_participants
                ),
                'settings': {
                    'require_authentication': meeting_data.get('require_authentication', False),
                    'waiting_room_enabled': meeting_data.get('waiting_room_enabled', True),
                    'allow_recording': meeting_data.get('allow_recording', self.recording_enabled),
                    'auto_record': meeting_data.get('auto_record', False),
                    'allow_screen_sharing': meeting_data.get('allow_screen_sharing', True),
                    'allow_chat': meeting_data.get('allow_chat', True),
                    'mute_on_entry': meeting_data.get('mute_on_entry', True)
                },
                'ice_servers': self.ice_servers,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'scheduled',
                'participants': [],
                'recordings': []
            }
            
            # Store room configuration
            self.active_rooms[room_id] = room_config
            
            # Generate meeting URL
            meeting_url = f"{self.frontend_url}/webrtc/{room_id}"
            if room_password:
                meeting_url += f"?password={room_password}"
            
            return {
                'meeting_id': room_id,
                'meeting_url': meeting_url,
                'meeting_password': room_password,
                'provider_data': {
                    'webrtc_room_id': room_id,
                    'room_config': room_config,
                    'ice_servers': self.ice_servers,
                    'frontend_url': self.frontend_url
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating WebRTC meeting: {str(e)}")
            raise ProviderAPIError(f"Failed to create WebRTC meeting: {str(e)}")
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a WebRTC meeting."""
        try:
            if meeting_id not in self.active_rooms:
                raise ProviderAPIError(f"WebRTC room {meeting_id} not found")
            
            room_config = self.active_rooms[meeting_id]
            updated_fields = []
            
            # Update basic meeting info
            if 'title' in meeting_data:
                room_config['title'] = meeting_data['title']
                updated_fields.append('title')
            
            if 'description' in meeting_data:
                room_config['description'] = meeting_data['description']
                updated_fields.append('description')
            
            if 'start_time' in meeting_data:
                room_config['start_time'] = meeting_data['start_time'].isoformat()
                updated_fields.append('start_time')
            
            if 'end_time' in meeting_data:
                room_config['end_time'] = meeting_data['end_time'].isoformat()
                updated_fields.append('end_time')
            
            # Update settings
            settings_updated = False
            if 'require_authentication' in meeting_data:
                room_config['settings']['require_authentication'] = meeting_data['require_authentication']
                settings_updated = True
            
            if 'waiting_room_enabled' in meeting_data:
                room_config['settings']['waiting_room_enabled'] = meeting_data['waiting_room_enabled']
                settings_updated = True
            
            if 'allow_recording' in meeting_data:
                room_config['settings']['allow_recording'] = meeting_data['allow_recording']
                settings_updated = True
            
            if 'auto_record' in meeting_data:
                room_config['settings']['auto_record'] = meeting_data['auto_record']
                settings_updated = True
            
            if settings_updated:
                updated_fields.append('settings')
            
            room_config['updated_at'] = datetime.utcnow().isoformat()
            
            return {
                'success': True,
                'provider_data': room_config,
                'updated_fields': updated_fields
            }
            
        except Exception as e:
            logger.error(f"Error updating WebRTC meeting: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            raise ProviderAPIError(f"Failed to update WebRTC meeting: {str(e)}")
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a WebRTC meeting."""
        try:
            if meeting_id in self.active_rooms:
                # Update status to cancelled before deletion
                self.active_rooms[meeting_id]['status'] = 'cancelled'
                
                # In a real implementation, you might want to notify active participants
                # before actually deleting the room
                
                # Delete the room
                del self.active_rooms[meeting_id]
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting WebRTC meeting: {str(e)}")
            return False
    
    def get_meeting_info(self, meeting_id: str) -> Dict[str, Any]:
        """Get WebRTC meeting information."""
        try:
            if meeting_id not in self.active_rooms:
                raise ProviderAPIError(f"WebRTC room {meeting_id} not found")
            
            return self.active_rooms[meeting_id]
            
        except Exception as e:
            logger.error(f"Error getting WebRTC meeting info: {str(e)}")
            if isinstance(e, ProviderError):
                raise
            raise ProviderAPIError(f"Failed to get WebRTC meeting info: {str(e)}")
    
    def start_recording(self, meeting_id: str) -> bool:
        """Start recording a WebRTC meeting."""
        try:
            if meeting_id not in self.active_rooms:
                return False
            
            room_config = self.active_rooms[meeting_id]
            
            if not room_config['settings']['allow_recording']:
                logger.warning(f"Recording not allowed for room {meeting_id}")
                return False
            
            # Create recording entry
            recording_id = str(uuid.uuid4())
            recording = {
                'id': recording_id,
                'room_id': meeting_id,
                'started_at': datetime.utcnow().isoformat(),
                'status': 'recording',
                'file_path': None  # Will be set when recording is saved
            }
            
            room_config['recordings'].append(recording)
            room_config['current_recording'] = recording_id
            
            logger.info(f"Started recording for WebRTC room {meeting_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting WebRTC recording: {str(e)}")
            return False
    
    def stop_recording(self, meeting_id: str) -> bool:
        """Stop recording a WebRTC meeting."""
        try:
            if meeting_id not in self.active_rooms:
                return False
            
            room_config = self.active_rooms[meeting_id]
            current_recording_id = room_config.get('current_recording')
            
            if not current_recording_id:
                logger.warning(f"No active recording for room {meeting_id}")
                return False
            
            # Find and update recording
            for recording in room_config['recordings']:
                if recording['id'] == current_recording_id:
                    recording['ended_at'] = datetime.utcnow().isoformat()
                    recording['status'] = 'completed'
                    break
            
            room_config['current_recording'] = None
            
            logger.info(f"Stopped recording for WebRTC room {meeting_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping WebRTC recording: {str(e)}")
            return False
    
    def get_recordings(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get recordings for a WebRTC meeting."""
        try:
            if meeting_id not in self.active_rooms:
                return []
            
            room_config = self.active_rooms[meeting_id]
            return room_config.get('recordings', [])
            
        except Exception as e:
            logger.error(f"Error getting WebRTC recordings: {str(e)}")
            return []
    
    def add_participants(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """Add participants to a WebRTC meeting."""
        try:
            if meeting_id not in self.active_rooms:
                return False
            
            room_config = self.active_rooms[meeting_id]
            current_participants = room_config.get('participants', [])
            
            # Check room capacity
            total_participants = len(current_participants) + len(participants)
            if total_participants > room_config['max_participants']:
                logger.warning(f"Room {meeting_id} capacity exceeded")
                return False
            
            # Add new participants
            for participant in participants:
                participant_entry = {
                    'id': str(uuid.uuid4()),
                    'email': participant.get('email'),
                    'name': participant.get('name', ''),
                    'role': participant.get('role', 'participant'),
                    'invited_at': datetime.utcnow().isoformat(),
                    'joined_at': None,
                    'left_at': None,
                    'status': 'invited'
                }
                current_participants.append(participant_entry)
            
            room_config['participants'] = current_participants
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding participants to WebRTC meeting: {str(e)}")
            return False
    
    def remove_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Remove a participant from a WebRTC meeting."""
        try:
            if meeting_id not in self.active_rooms:
                return False
            
            room_config = self.active_rooms[meeting_id]
            participants = room_config.get('participants', [])
            
            # Remove participant by ID or email
            updated_participants = []
            participant_removed = False
            
            for participant in participants:
                if (participant.get('id') == participant_id or 
                    participant.get('email') == participant_id):
                    participant['left_at'] = datetime.utcnow().isoformat()
                    participant['status'] = 'left'
                    participant_removed = True
                else:
                    updated_participants.append(participant)
            
            if participant_removed:
                room_config['participants'] = updated_participants
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing participant from WebRTC meeting: {str(e)}")
            return False
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get current WebRTC meeting participants."""
        try:
            if meeting_id not in self.active_rooms:
                return []
            
            room_config = self.active_rooms[meeting_id]
            return room_config.get('participants', [])
            
        except Exception as e:
            logger.error(f"Error getting WebRTC meeting participants: {str(e)}")
            return []
    
    def send_invitation(self, meeting_id: str, participants: List[Dict[str, Any]]) -> bool:
        """Send meeting invitations for WebRTC meeting."""
        try:
            # For WebRTC, invitations are typically handled by the application
            # This method would integrate with the notification/email service
            
            if meeting_id not in self.active_rooms:
                return False
            
            room_config = self.active_rooms[meeting_id]
            meeting_url = f"{self.frontend_url}/webrtc/{meeting_id}"
            
            if room_config.get('password'):
                meeting_url += f"?password={room_config['password']}"
            
            # Add participants and mark as invited
            self.add_participants(meeting_id, participants)
            
            # In a real implementation, you would send emails/notifications here
            logger.info(f"Invitations prepared for WebRTC room {meeting_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending WebRTC invitations: {str(e)}")
            return False
    
    def get_meeting_analytics(self, meeting_id: str) -> Dict[str, Any]:
        """Get WebRTC meeting analytics."""
        try:
            if meeting_id not in self.active_rooms:
                return {}
            
            room_config = self.active_rooms[meeting_id]
            participants = room_config.get('participants', [])
            
            # Calculate analytics
            total_invited = len(participants)
            total_joined = len([p for p in participants if p.get('joined_at')])
            currently_active = len([p for p in participants if p.get('joined_at') and not p.get('left_at')])
            
            analytics = {
                'meeting_id': meeting_id,
                'title': room_config.get('title'),
                'start_time': room_config.get('start_time'),
                'end_time': room_config.get('end_time'),
                'status': room_config.get('status'),
                'total_invited': total_invited,
                'total_joined': total_joined,
                'currently_active': currently_active,
                'join_rate': (total_joined / total_invited * 100) if total_invited > 0 else 0,
                'recordings_count': len(room_config.get('recordings', [])),
                'max_participants': room_config.get('max_participants'),
                'settings': room_config.get('settings', {}),
                'participants_summary': participants
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting WebRTC meeting analytics: {str(e)}")
            return {}
    
    def get_active_rooms(self) -> List[Dict[str, Any]]:
        """Get list of all active WebRTC rooms."""
        try:
            active_rooms = []
            
            for room_id, room_config in self.active_rooms.items():
                if room_config['status'] in ['scheduled', 'active']:
                    active_rooms.append({
                        'room_id': room_id,
                        'title': room_config.get('title'),
                        'participant_count': len([
                            p for p in room_config.get('participants', [])
                            if p.get('joined_at') and not p.get('left_at')
                        ]),
                        'status': room_config['status'],
                        'created_at': room_config.get('created_at')
                    })
            
            return active_rooms
            
        except Exception as e:
            logger.error(f"Error getting active WebRTC rooms: {str(e)}")
            return []
    
    def cleanup_expired_rooms(self) -> int:
        """Clean up expired or inactive rooms."""
        try:
            cleaned_count = 0
            current_time = datetime.utcnow()
            
            expired_rooms = []
            
            for room_id, room_config in self.active_rooms.items():
                # Check if room has ended
                end_time_str = room_config.get('end_time')
                if end_time_str:
                    end_time = datetime.fromisoformat(end_time_str.replace('Z', ''))
                    if current_time > end_time:
                        expired_rooms.append(room_id)
                
                # Check if room is cancelled
                elif room_config.get('status') == 'cancelled':
                    expired_rooms.append(room_id)
            
            # Remove expired rooms
            for room_id in expired_rooms:
                del self.active_rooms[room_id]
                cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired WebRTC rooms")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up WebRTC rooms: {str(e)}")
            return 0