"""WebRTC service implementation for direct peer-to-peer video calls."""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from flask_socketio import emit, join_room, leave_room, disconnect

from app.extensions import db
from app.models.video_conference import VideoConference, VideoConferenceParticipant
from app.models.user import User
from app.exceptions import NotFoundException, ValidationException, ForbiddenException

logger = logging.getLogger(__name__)


class WebRTCRoom:
    """WebRTC room management."""
    
    def __init__(self, room_id: str, conference_id: Optional[int] = None):
        self.room_id = room_id
        self.conference_id = conference_id
        self.participants = {}  # participant_id -> participant_info
        self.created_at = datetime.utcnow()
        self.host_id = None
        self.is_recording = False
        self.chat_messages = []
        self.screen_sharing = None  # participant_id who is sharing screen
        
    def add_participant(self, participant_id: str, user_info: Dict[str, Any], socket_id: str):
        """Add participant to room."""
        self.participants[participant_id] = {
            'user_info': user_info,
            'socket_id': socket_id,
            'joined_at': datetime.utcnow(),
            'is_audio_muted': False,
            'is_video_muted': False,
            'is_screen_sharing': False,
            'peer_connections': {}  # other_participant_id -> connection_state
        }
        
        # Set first participant as host if no host exists
        if not self.host_id:
            self.host_id = participant_id
            
        logger.info(f"Participant {participant_id} joined room {self.room_id}")
        
    def remove_participant(self, participant_id: str):
        """Remove participant from room."""
        if participant_id in self.participants:
            participant = self.participants.pop(participant_id)
            
            # If this was the screen sharer, stop screen sharing
            if self.screen_sharing == participant_id:
                self.screen_sharing = None
                
            # If this was the host, assign new host
            if self.host_id == participant_id and self.participants:
                self.host_id = list(self.participants.keys())[0]
                
            logger.info(f"Participant {participant_id} left room {self.room_id}")
            
    def get_participant_list(self) -> List[Dict[str, Any]]:
        """Get list of participants for room."""
        return [
            {
                'participant_id': pid,
                'user_info': info['user_info'],
                'joined_at': info['joined_at'].isoformat(),
                'is_audio_muted': info['is_audio_muted'],
                'is_video_muted': info['is_video_muted'],
                'is_screen_sharing': info['is_screen_sharing'],
                'is_host': pid == self.host_id
            }
            for pid, info in self.participants.items()
        ]
        
    def add_chat_message(self, participant_id: str, message: str):
        """Add chat message to room."""
        chat_message = {
            'id': str(uuid.uuid4()),
            'participant_id': participant_id,
            'user_info': self.participants[participant_id]['user_info'],
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.chat_messages.append(chat_message)
        return chat_message
        
    def is_empty(self) -> bool:
        """Check if room is empty."""
        return len(self.participants) == 0


class WebRTCService:
    """WebRTC service for managing peer-to-peer video calls."""
    
    def __init__(self):
        self.rooms = {}  # room_id -> WebRTCRoom
        self.participant_to_room = {}  # participant_id -> room_id
        self.socket_to_participant = {}  # socket_id -> participant_id
        
    def create_room(self, conference_id: Optional[int] = None) -> str:
        """
        Create a new WebRTC room.
        
        Args:
            conference_id: Optional conference ID to associate with room
            
        Returns:
            str: Room ID
        """
        room_id = str(uuid.uuid4())
        self.rooms[room_id] = WebRTCRoom(room_id, conference_id)
        
        logger.info(f"Created WebRTC room {room_id}")
        return room_id
        
    def join_room(self, room_id: str, user_id: int, socket_id: str) -> Dict[str, Any]:
        """
        Join a WebRTC room.
        
        Args:
            room_id: Room ID to join
            user_id: User ID joining
            socket_id: Socket connection ID
            
        Returns:
            Dict: Room join information
        """
        if room_id not in self.rooms:
            raise NotFoundException(f"Room {room_id} not found")
            
        # Get user info
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
            
        room = self.rooms[room_id]
        participant_id = str(uuid.uuid4())
        
        user_info = {
            'user_id': user_id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'avatar_url': getattr(user, 'avatar_url', None)
        }
        
        # Add participant to room
        room.add_participant(participant_id, user_info, socket_id)
        
        # Track mappings
        self.participant_to_room[participant_id] = room_id
        self.socket_to_participant[socket_id] = participant_id
        
        # Update database if conference exists
        if room.conference_id:
            self._update_conference_participant(room.conference_id, user_id, 'joined')
            
        return {
            'room_id': room_id,
            'participant_id': participant_id,
            'user_info': user_info,
            'is_host': participant_id == room.host_id,
            'participants': room.get_participant_list(),
            'ice_servers': current_app.config.get('WEBRTC_ICE_SERVERS', [
                {'urls': 'stun:stun.l.google.com:19302'},
                {'urls': 'stun:stun1.l.google.com:19302'}
            ])
        }
        
    def leave_room(self, socket_id: str) -> Optional[Dict[str, Any]]:
        """
        Leave a WebRTC room.
        
        Args:
            socket_id: Socket connection ID
            
        Returns:
            Dict: Leave information or None if not in room
        """
        if socket_id not in self.socket_to_participant:
            return None
            
        participant_id = self.socket_to_participant[socket_id]
        room_id = self.participant_to_room.get(participant_id)
        
        if not room_id or room_id not in self.rooms:
            return None
            
        room = self.rooms[room_id]
        participant_info = room.participants.get(participant_id)
        
        if not participant_info:
            return None
            
        # Update database if conference exists
        if room.conference_id:
            user_id = participant_info['user_info']['user_id']
            self._update_conference_participant(room.conference_id, user_id, 'left')
            
        # Remove participant
        room.remove_participant(participant_id)
        
        # Clean up mappings
        del self.socket_to_participant[socket_id]
        del self.participant_to_room[participant_id]
        
        # Clean up empty room
        if room.is_empty():
            del self.rooms[room_id]
            logger.info(f"Cleaned up empty room {room_id}")
            
        return {
            'room_id': room_id,
            'participant_id': participant_id,
            'remaining_participants': room.get_participant_list() if not room.is_empty() else []
        }
        
    def handle_webrtc_signal(self, socket_id: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle WebRTC signaling messages.
        
        Args:
            socket_id: Socket connection ID
            signal_data: Signaling data
            
        Returns:
            Dict: Response data
        """
        if socket_id not in self.socket_to_participant:
            raise ValidationException("Not connected to any room")
            
        participant_id = self.socket_to_participant[socket_id]
        room_id = self.participant_to_room[participant_id]
        room = self.rooms[room_id]
        
        signal_type = signal_data.get('type')
        target_participant = signal_data.get('target_participant')
        
        if signal_type in ['offer', 'answer', 'ice_candidate']:
            # Relay signaling to target participant
            if target_participant in room.participants:
                target_socket = room.participants[target_participant]['socket_id']
                return {
                    'action': 'relay_signal',
                    'target_socket': target_socket,
                    'signal_data': {
                        **signal_data,
                        'from_participant': participant_id
                    }
                }
                
        elif signal_type == 'media_state_change':
            # Update participant media state
            if 'is_audio_muted' in signal_data:
                room.participants[participant_id]['is_audio_muted'] = signal_data['is_audio_muted']
            if 'is_video_muted' in signal_data:
                room.participants[participant_id]['is_video_muted'] = signal_data['is_video_muted']
                
            return {
                'action': 'broadcast_to_room',
                'room_id': room_id,
                'exclude_participant': participant_id,
                'data': {
                    'type': 'participant_media_changed',
                    'participant_id': participant_id,
                    'is_audio_muted': room.participants[participant_id]['is_audio_muted'],
                    'is_video_muted': room.participants[participant_id]['is_video_muted']
                }
            }
            
        elif signal_type == 'screen_share_start':
            # Handle screen sharing start
            if room.screen_sharing and room.screen_sharing != participant_id:
                raise ValidationException("Another participant is already sharing screen")
                
            room.screen_sharing = participant_id
            room.participants[participant_id]['is_screen_sharing'] = True
            
            return {
                'action': 'broadcast_to_room',
                'room_id': room_id,
                'exclude_participant': participant_id,
                'data': {
                    'type': 'screen_share_started',
                    'participant_id': participant_id,
                    'user_info': room.participants[participant_id]['user_info']
                }
            }
            
        elif signal_type == 'screen_share_stop':
            # Handle screen sharing stop
            if room.screen_sharing == participant_id:
                room.screen_sharing = None
                room.participants[participant_id]['is_screen_sharing'] = False
                
                return {
                    'action': 'broadcast_to_room',
                    'room_id': room_id,
                    'exclude_participant': participant_id,
                    'data': {
                        'type': 'screen_share_stopped',
                        'participant_id': participant_id
                    }
                }
                
        return {'action': 'none'}
        
    def send_chat_message(self, socket_id: str, message: str) -> Dict[str, Any]:
        """
        Send chat message in room.
        
        Args:
            socket_id: Socket connection ID
            message: Chat message
            
        Returns:
            Dict: Chat message data
        """
        if socket_id not in self.socket_to_participant:
            raise ValidationException("Not connected to any room")
            
        participant_id = self.socket_to_participant[socket_id]
        room_id = self.participant_to_room[participant_id]
        room = self.rooms[room_id]
        
        chat_message = room.add_chat_message(participant_id, message)
        
        return {
            'action': 'broadcast_to_room',
            'room_id': room_id,
            'data': {
                'type': 'chat_message',
                'message': chat_message
            }
        }
        
    def start_recording(self, socket_id: str) -> Dict[str, Any]:
        """
        Start recording in room.
        
        Args:
            socket_id: Socket connection ID
            
        Returns:
            Dict: Recording start response
        """
        if socket_id not in self.socket_to_participant:
            raise ValidationException("Not connected to any room")
            
        participant_id = self.socket_to_participant[socket_id]
        room_id = self.participant_to_room[participant_id]
        room = self.rooms[room_id]
        
        # Only host can start recording
        if participant_id != room.host_id:
            raise ForbiddenException("Only host can start recording")
            
        if room.is_recording:
            raise ValidationException("Recording is already in progress")
            
        room.is_recording = True
        
        return {
            'action': 'broadcast_to_room',
            'room_id': room_id,
            'data': {
                'type': 'recording_started',
                'started_by': participant_id,
                'user_info': room.participants[participant_id]['user_info']
            }
        }
        
    def stop_recording(self, socket_id: str) -> Dict[str, Any]:
        """
        Stop recording in room.
        
        Args:
            socket_id: Socket connection ID
            
        Returns:
            Dict: Recording stop response
        """
        if socket_id not in self.socket_to_participant:
            raise ValidationException("Not connected to any room")
            
        participant_id = self.socket_to_participant[socket_id]
        room_id = self.participant_to_room[participant_id]
        room = self.rooms[room_id]
        
        # Only host can stop recording
        if participant_id != room.host_id:
            raise ForbiddenException("Only host can stop recording")
            
        if not room.is_recording:
            raise ValidationException("No recording in progress")
            
        room.is_recording = False
        
        return {
            'action': 'broadcast_to_room',
            'room_id': room_id,
            'data': {
                'type': 'recording_stopped',
                'stopped_by': participant_id,
                'user_info': room.participants[participant_id]['user_info']
            }
        }
        
    def get_room_info(self, room_id: str) -> Dict[str, Any]:
        """
        Get room information.
        
        Args:
            room_id: Room ID
            
        Returns:
            Dict: Room information
        """
        if room_id not in self.rooms:
            raise NotFoundException(f"Room {room_id} not found")
            
        room = self.rooms[room_id]
        
        return {
            'room_id': room_id,
            'conference_id': room.conference_id,
            'created_at': room.created_at.isoformat(),
            'host_id': room.host_id,
            'is_recording': room.is_recording,
            'screen_sharing': room.screen_sharing,
            'participant_count': len(room.participants),
            'participants': room.get_participant_list(),
            'chat_message_count': len(room.chat_messages)
        }
        
    def get_participant_info(self, socket_id: str) -> Optional[Dict[str, Any]]:
        """
        Get participant information.
        
        Args:
            socket_id: Socket connection ID
            
        Returns:
            Dict: Participant information or None
        """
        if socket_id not in self.socket_to_participant:
            return None
            
        participant_id = self.socket_to_participant[socket_id]
        room_id = self.participant_to_room[participant_id]
        
        if room_id not in self.rooms:
            return None
            
        room = self.rooms[room_id]
        participant = room.participants.get(participant_id)
        
        if not participant:
            return None
            
        return {
            'participant_id': participant_id,
            'room_id': room_id,
            'user_info': participant['user_info'],
            'joined_at': participant['joined_at'].isoformat(),
            'is_host': participant_id == room.host_id,
            'is_audio_muted': participant['is_audio_muted'],
            'is_video_muted': participant['is_video_muted'],
            'is_screen_sharing': participant['is_screen_sharing']
        }
        
    def _update_conference_participant(self, conference_id: int, user_id: int, action: str):
        """Update conference participant status in database."""
        try:
            participant = VideoConferenceParticipant.query.filter_by(
                conference_id=conference_id,
                user_id=user_id
            ).first()
            
            if participant:
                if action == 'joined':
                    participant.has_joined = True
                    participant.joined_at = datetime.utcnow()
                elif action == 'left':
                    participant.left_at = datetime.utcnow()
                    if participant.joined_at:
                        participant.duration_minutes = int(
                            (participant.left_at - participant.joined_at).total_seconds() / 60
                        )
                        
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Error updating conference participant: {str(e)}")
            db.session.rollback()


# Global WebRTC service instance
webrtc_service = WebRTCService()


def handle_webrtc_events(socketio):
    """Register WebRTC event handlers with SocketIO."""
    
    @socketio.on('webrtc_join_room')
    def on_join_room(data):
        """Handle joining WebRTC room."""
        try:
            room_id = data.get('room_id')
            user_id = data.get('user_id')
            
            if not room_id or not user_id:
                emit('webrtc_error', {'error': 'Missing room_id or user_id'})
                return
                
            join_info = webrtc_service.join_room(room_id, user_id, request.sid)
            
            # Join socket room
            join_room(room_id)
            
            # Send join confirmation to user
            emit('webrtc_joined', join_info)
            
            # Notify other participants
            emit('webrtc_participant_joined', {
                'participant_id': join_info['participant_id'],
                'user_info': join_info['user_info'],
                'is_host': join_info['is_host']
            }, room=room_id, include_self=False)
            
        except Exception as e:
            logger.error(f"Error joining WebRTC room: {str(e)}")
            emit('webrtc_error', {'error': str(e)})
            
    @socketio.on('webrtc_signal')
    def on_webrtc_signal(data):
        """Handle WebRTC signaling."""
        try:
            response = webrtc_service.handle_webrtc_signal(request.sid, data)
            
            if response['action'] == 'relay_signal':
                # Send signal to target participant
                socketio.emit('webrtc_signal', response['signal_data'], 
                            room=response['target_socket'])
                            
            elif response['action'] == 'broadcast_to_room':
                # Broadcast to room excluding sender
                room_id = response['room_id']
                exclude_participant = response.get('exclude_participant')
                
                if exclude_participant:
                    emit('webrtc_event', response['data'], room=room_id, include_self=False)
                else:
                    emit('webrtc_event', response['data'], room=room_id)
                    
        except Exception as e:
            logger.error(f"Error handling WebRTC signal: {str(e)}")
            emit('webrtc_error', {'error': str(e)})
            
    @socketio.on('webrtc_chat_message')
    def on_chat_message(data):
        """Handle chat message."""
        try:
            message = data.get('message', '').strip()
            if not message:
                return
                
            response = webrtc_service.send_chat_message(request.sid, message)
            
            if response['action'] == 'broadcast_to_room':
                emit('webrtc_event', response['data'], room=response['room_id'])
                
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")
            emit('webrtc_error', {'error': str(e)})
            
    @socketio.on('webrtc_start_recording')
    def on_start_recording():
        """Handle start recording."""
        try:
            response = webrtc_service.start_recording(request.sid)
            
            if response['action'] == 'broadcast_to_room':
                emit('webrtc_event', response['data'], room=response['room_id'])
                
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            emit('webrtc_error', {'error': str(e)})
            
    @socketio.on('webrtc_stop_recording')
    def on_stop_recording():
        """Handle stop recording."""
        try:
            response = webrtc_service.stop_recording(request.sid)
            
            if response['action'] == 'broadcast_to_room':
                emit('webrtc_event', response['data'], room=response['room_id'])
                
        except Exception as e:
            logger.error(f"Error stopping recording: {str(e)}")
            emit('webrtc_error', {'error': str(e)})
            
    @socketio.on('disconnect')
    def on_disconnect():
        """Handle client disconnect."""
        try:
            leave_info = webrtc_service.leave_room(request.sid)
            
            if leave_info:
                room_id = leave_info['room_id']
                participant_id = leave_info['participant_id']
                
                # Leave socket room
                leave_room(room_id)
                
                # Notify remaining participants
                if leave_info['remaining_participants']:
                    emit('webrtc_participant_left', {
                        'participant_id': participant_id
                    }, room=room_id)
                    
        except Exception as e:
            logger.error(f"Error handling disconnect: {str(e)}")
    
    return socketio